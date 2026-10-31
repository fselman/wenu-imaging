"""Read-only ESO preflight contracts using tiny synthetic mosaic files."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from astropy.io import fits
from astropy.io.fits.hdu.image import _ImageBaseHDU

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pycavi"))
from pycavi_preflight import preflight_files,load_eso_adapter,Limits

EVIDENCE=Path(tempfile.mkdtemp(prefix="eso-preflight-controls-"))


class EsoTests(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix=self._testMethodName+"-",dir=EVIDENCE))

    def frame(self,instrument="WFI",kind="OBJECT",changes=None,extensions=None,missing_gain=False):
        # Synthetic MEF: instrument-configured identities, tiny arrays and explicit reported metadata.
        adapter=load_eso_adapter(instrument)
        h=fits.Header()
        values={"INSTRUME":instrument,"OBJECT":"field","EXPTIME":20.0,
                "DATE-OBS":"2026-10-31T01:02:03","TELESCOP":"VST" if instrument=="OMEGACAM" else "ESO-2.2",
                "ORIGIN":"ESO","ESO INS FILT1 NAME":"r_SDSS","ESO DPR TYPE":kind,
                "ESO DPR CATG":"SCIENCE" if kind=="OBJECT" else "CALIB","ESO DPR TECH":"IMAGE",
                "ESO DET READ MODE":"normal","ESO DET WIN1 BINX":1,"ESO DET WIN1 BINY":1}
        values.update(changes or {})
        for k,v in values.items():
            if v is not None:h[("HIERARCH "+k) if len(k)>8 else k]=v
        hdus=[fits.PrimaryHDU(header=h)]
        for name in extensions if extensions is not None else adapter["detectors"]:
            eh=fits.Header()
            if not missing_gain:eh["HIERARCH "+adapter["detectors"].get(name,"ESO DET OUT1 CONAD")]=2.1
            hdus.append(fits.ImageHDU(np.arange(6,dtype=np.int16).reshape(2,3),header=eh,name=name))
        path=self.work/(instrument+str(len(list(self.work.glob('*.fits'))))+".fits")
        fits.HDUList(hdus).writeto(path)
        return path

    def inspect(self,*paths,**kwargs):
        return preflight_files(paths,invocation_base=self.work,**kwargs)

    def test_complete_native_instruments_need_no_preparation(self):
        # Complete correct ESO metadata: all existing detectors map with no additions or copies.
        for instrument,count in [("OMEGACAM",32),("WFI",8)]:
            p=self.frame(instrument);r=self.inspect(p)
            self.assertEqual(r["summary"]["blocked"],0)
            row=r["observations"][0]
            self.assertEqual(row["readiness"]["status"],"passed")
            self.assertEqual(len(row["images"]),count)
            self.assertEqual(row["proposed_additions"],{})
            self.assertFalse(row["preparation_required"])
            self.assertEqual(row["attributes"]["filter"]["source"]["keyword"],"ESO INS FILT1 NAME")
            self.assertEqual(row["attributes"]["exposure_s"]["unit"],"s")

    def test_wfi_screen_and_omegacam_dome_are_preserved(self):
        # Existing instrument conventions: preserve DPR spelling; normalize configured role separately.
        for instrument,kind in [("WFI","FLAT,SCREEN"),("OMEGACAM","FLAT,DOME")]:
            p=self.frame(instrument,kind);before=hashlib.sha256(p.read_bytes()).hexdigest()
            row=self.inspect(p)["observations"][0]
            self.assertEqual(row["readiness"]["status"],"passed")
            self.assertEqual(row["attributes"]["dpr_type"]["value"],kind)
            self.assertEqual(row["attributes"]["exposure_role"]["value"],"dome_flat")
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),before)

    def test_shuffled_detectors_keep_identity_and_order(self):
        # Detector identity: shuffled HDUs retain header IDs and file order, never HDU-number mapping.
        names=list(reversed(load_eso_adapter("WFI")["detectors"]))
        row=self.inspect(self.frame(extensions=names))["observations"][0]
        self.assertEqual([r["detector_id"] for r in row["images"]],names)
        self.assertEqual([r["hdu"] for r in row["images"]],list(range(1,9)))
        self.assertTrue(all(r["gain"]["value"]==2.1 for r in row["images"]))

    def test_unknown_mode_gain_and_partial_coverage(self):
        # Unknowns remain explicit: no physical gain/default read mode or full-reduction claim.
        p=self.frame(changes={"ESO DET READ MODE":None,"GAIN":139.0},
                     extensions=["WIN1.CHIP1.OUT1"],missing_gain=True)
        row=self.inspect(p)["observations"][0]
        self.assertEqual(row["readiness"]["status"],"passed-with-warnings")
        self.assertIn("read_mode",row["unknown"])
        self.assertIsNone(row["images"][0]["gain"]["value"])
        self.assertEqual(row["readiness"]["scientific"],"not-assessed")
        self.assertEqual(row["readiness"]["calibration"],"not-assessed")

    def test_missing_classification_and_filter(self):
        # Required metadata: missing DPR or science filter blocks rather than creating raw cards.
        for changes in [{"ESO DPR TYPE":None},{"ESO DPR CATG":None},
                        {"ESO DPR TECH":None},{"ESO INS FILT1 NAME":None}]:
            r=self.inspect(self.frame(changes=changes))
            self.assertEqual(r["summary"]["blocked"],1)
            self.assertFalse(r["observations"][0]["preparation_required"])

    def test_conflicting_filters_and_extension_metadata(self):
        # Conflicts: generic/native filter mismatch and repeated extension exposure disagreement block.
        p=self.frame(changes={"FILTER":"Blue"})
        self.assertEqual(self.inspect(p)["summary"]["blocked"],1)
        p=self.frame()
        with fits.open(p,mode="update") as hdus:hdus[1].header["EXPTIME"]=99.0
        self.assertEqual(self.inspect(p)["summary"]["blocked"],1)
        p=self.frame()
        with fits.open(p,mode="update") as hdus:hdus[1].header["FILTER"]="Blue"
        self.assertEqual(self.inspect(p)["summary"]["blocked"],1)

    def test_bad_detector_identity_and_invalid_metadata(self):
        # Ingestion errors: unknown/duplicate identities, negative exposure and invalid binning.
        for names,changes in [(["UNKNOWN"],{}),(["WIN1.CHIP1.OUT1"]*2,{}),
                              (None,{"EXPTIME":-1.0}),(None,{"ESO DET WIN1 BINX":0})]:
            self.assertEqual(self.inspect(self.frame(extensions=names,changes=changes))["summary"]["blocked"],1)

    def test_no_arrays_no_writes_and_source_base(self):
        # Header-only contract: forbid array reads and verify exact file bytes/metadata and caller cwd.
        p=self.frame();p.chmod(0o444)
        before=(p.stat().st_mtime_ns,p.stat().st_mode,hashlib.sha256(p.read_bytes()).hexdigest())
        cwd=Path.cwd();original_open=Path.open
        def read_only(path,mode="r",*args,**kwargs):
            if path.resolve()==p and any(c in mode for c in "wax+"):
                raise AssertionError("raw write attempted")
            return original_open(path,mode,*args,**kwargs)
        with patch.object(_ImageBaseHDU,"_get_scaled_image_data",side_effect=AssertionError("pixel read")), \
                patch.object(Path,"open",read_only):
            r=self.inspect(p.name)
        self.assertEqual(r["summary"]["blocked"],0)
        self.assertEqual(before,(p.stat().st_mtime_ns,p.stat().st_mode,hashlib.sha256(p.read_bytes()).hexdigest()))
        self.assertEqual(Path.cwd(),cwd)
        self.assertEqual(r["observations"][0]["path"],str(p))

    def test_limits_fifo_missing_and_duplicate_inputs(self):
        # Bounded I/O: HDU budgets, nonregular/missing files and duplicate assets are explicit errors.
        p=self.frame()
        self.assertEqual(self.inspect(p,limits=Limits(hdus=1))["summary"]["blocked"],1)
        fifo=self.work/"pipe.fits";os.mkfifo(fifo)
        self.assertEqual(self.inspect(fifo)["summary"]["blocked"],1)
        self.assertEqual(self.inspect(self.work/"missing.fits")["summary"]["blocked"],1)
        self.assertEqual(self.inspect(p,p)["summary"]["blocked"],1)

    def test_cli_report_and_existing_report_protection(self):
        # Public CLI: emit the same read-only assessment; never overwrite an existing report/source.
        p=self.frame();raw=self.work/"raw";raw.mkdir();p=p.rename(raw/p.name)
        report=self.work/"report.json"
        helper=Path(__file__).resolve().parents[1]/"pycavi/pycavi_preflight.py"
        command=[sys.executable,"-B",str(helper),str(p),"--report",str(report)]
        subprocess.run(command,check=True)
        result=json.loads(report.read_text());self.assertEqual(result["summary"]["blocked"],0)
        before=report.read_bytes()
        self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
        self.assertEqual(report.read_bytes(),before)
        public=helper.with_name("pycavi_project.py");report2=self.work/"public.json"
        self.assertIn("preflight",subprocess.check_output([sys.executable,"-B",str(public),"--help"],text=True))
        subprocess.run([sys.executable,"-B",str(public),"preflight",str(p),"--report",str(report2)],check=True)
        self.assertEqual(json.loads(report2.read_text()),result)
        rejected=subprocess.run([sys.executable,"-B",str(public),"preflight",str(p),
                                 "--report",str(raw/"forbidden.json")],capture_output=True)
        self.assertNotEqual(rejected.returncode,0)
        self.assertFalse((raw/"forbidden.json").exists())


if __name__=="__main__":
    print("RETAINED EVIDENCE:",EVIDENCE,flush=True)
    unittest.main(verbosity=2)
