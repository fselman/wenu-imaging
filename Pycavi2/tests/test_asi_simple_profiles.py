"""Focused simple-input contracts; tiny synthetic FITS only, no reduction calls."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import asi_preparation_profiles as prep
from astropy.io import fits

CONFIG = Path(__file__).resolve().parents[1]/"config/preparation"
EVIDENCE = Path(tempfile.mkdtemp(prefix="asi-simple-profile-controls-"))


class SimpleTests(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix=self._testMethodName+"-",dir=EVIDENCE))
        self.root=self.work/"raw"; self.root.mkdir()
        self.inputs=[]
        for name in ("bath_observatory.toml","zwo_asi1600mm_pro.toml","bath_directories.toml"):
            p=self.work/name; p.write_bytes((CONFIG/name).read_bytes()); self.inputs.append(p)

    def bundle(self):
        return prep.load_bundle(*self.inputs)

    def frame(self,relative="Science/frame.fits",changes=None,extra=()):
        # Tiny opaque payload: preserve unsigned endpoint encodings with a padded primary image.
        values={"SIMPLE":True,"BITPIX":16,"NAXIS":2,"NAXIS1":4,"NAXIS2":3,
                "BSCALE":1,"BZERO":32768,"INSTRUME":"ZWO CCD ASI1600MM Pro",
                "FRAME":"Light","IMAGETYP":"Light Frame","FILTER":"Blue",
                "EXPTIME":32.0,"GAIN":139.0,"OFFSET":10.0,"CCD-TEMP":-5.0,
                "XBINNING":1,"YBINNING":1,"DATE-OBS":"2022-02-05T20:01:02.003",
                "TELESCOP":"SynScan","APTDIA":200.0,"FOCALLEN":1600.0}
        values.update(changes or {})
        h=fits.Header()
        for k,v in values.items():
            if v is not None: h[k]=v
        for k,v in extra: h.append((k,v))
        payload=struct.pack(">hhh",-32768,-1,32767)+b"\0"*(2880-6)
        p=self.root/relative;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(h.tostring().encode("ascii")+payload)
        return p

    def inventory(self):
        return prep.inventory(self.root,self.bundle())

    def plan(self):
        value=self.inventory();p=self.work/"dataset.toml"
        p.write_text(prep.toml_text(value))
        self.assertEqual(tomllib.loads(p.read_text()),value)
        return p,prep.sha(p.read_bytes())

    def test_roles_both_orders_and_flat_subtypes(self):
        # Directory semantics: flat/filter ordering and dome/sky/generic distinctions.
        for directory,kind in [("Flats","FLAT"),("DomeFlats","FLAT,DOME"),("SkyFlats","FLAT,SKY")]:
            for relative in (directory+"/Blue/frame.fits","Blue/"+directory+"/frame.fits"):
                self.frame(relative,{"FRAME":"Flat","IMAGETYP":"Flat Frame"})
        self.frame("Flats/SkyFlats/Blue/extra.fits",{"FRAME":"Flat","IMAGETYP":"Flat Frame"})
        result=self.inventory();self.assertEqual(result["errors"],[])
        self.assertEqual(result["summary"]["roles"],{"FLAT":2,"FLAT,DOME":2,"FLAT,SKY":3})

    def test_header_filter_without_filter_directory(self):
        # Header-first filters: use existing labels in science and flat role-only paths.
        self.frame("Science/a.fits",{"FILTER":"Luminance"})
        self.frame("SkyFlats/b.fits",{"FILTER":"Red","FRAME":"Flat","IMAGETYP":"Flat Frame"})
        rows=self.inventory();self.assertEqual(rows["errors"],[])
        self.assertEqual({r["filter"] for r in rows["entries"]},{"Red","Luminance"})
        self.assertTrue(all("FILTER" not in r["additions"] for r in rows["entries"]))

    def test_filter_fallback_and_unknown(self):
        # Missing filters: directory proposal or explicit unknown without guessing.
        self.frame("Blue/Science/a.fits",{"FILTER":None})
        self.frame("Science/b.fits",{"FILTER":None})
        rows=self.inventory();self.assertEqual(rows["errors"],[])
        byfile={r["file"]:r for r in rows["entries"]}
        self.assertEqual(byfile["Blue/Science/a.fits"]["additions"]["FILTER"],"Blue")
        self.assertIn("filter_unknown",byfile["Science/b.fits"]["warnings"])
        self.assertNotIn("FILTER",byfile["Science/b.fits"]["additions"])

    def test_filter_mismatch_for_all_roles(self):
        # Directory/header cross-check: mismatch blocks science, flats, bias and dark alike.
        for directory,frame in [("Science","Light"),("Flats","Flat"),("Bias","Bias"),("Darks","Dark")]:
            self.frame(directory+"/Blue/a.fits",{"FILTER":"Red","FRAME":frame,"IMAGETYP":frame+" Frame"})
        result=self.inventory();self.assertEqual(len(result["errors"]),4)
        self.assertTrue(all("FILTER conflict" in r["error"] for r in result["errors"]))

    def test_directory_conflicts_and_header_contradictions(self):
        # Ambiguity refusal: incompatible role/filter directories and inconsistent frame labels.
        for path,changes in [("Bias/Darks/a.fits",{}),("Science/Blue/Red/a.fits",{}),
                             ("DomeFlats/SkyFlats/a.fits",{}),
                             ("Science/a.fits",{"FRAME":"Bias"})]:
            self.frame(path,changes)
        self.assertEqual(len(self.inventory()["errors"]),4)

    def test_discovered_settings_and_missing_values(self):
        # Discovery: retain variable exposures/settings and unknown mode without fixed expectations.
        self.frame("Science/a.fits")
        self.frame("Science/b.fits",{"EXPTIME":45.5,"GAIN":100.0,"OFFSET":5.0,"CCD-TEMP":-10.0})
        self.frame("Science/c.fits",{"EXPTIME":None,"GAIN":None,"OFFSET":None,"CCD-TEMP":None})
        result=self.inventory();self.assertEqual(result["errors"],[])
        self.assertEqual(set(result["summary"]["settings"]["EXPTIME"]),{"32.0","45.5","<unknown>"})
        self.assertTrue(all("detector_mode" in r["missing_metadata"] for r in result["entries"]))
        self.assertTrue(all("ADCBITS" not in r["additions"] for r in result["entries"]))

    def test_copy_cards_filter_payload_and_manifest(self):
        # Actual copy integrity: inserted filter/provenance, preserved old cards and decoded endpoints.
        source=self.frame("Blue/SkyFlats/a.fits",{"FILTER":None,"FRAME":"Flat","IMAGETYP":"Flat Frame",
                         "CHECKSUM":"0000000000000000","DATASUM":"0"})
        original=source.read_bytes();plan,digest=self.plan();out=self.work/"prepared"
        prep.apply_plan(plan,digest,out,False,self.bundle())
        product=out/source.relative_to(self.root)
        self.assertEqual(source.read_bytes(),original)
        old,old_end=prep.raw_header(source);new,new_end=prep.raw_header(product)
        self.assertEqual(original[len(old):],product.read_bytes()[len(new):])
        cards=[old[i:i+80] for i in range(0,old_end,80) if old[i:i+8] not in (b"CHECKSUM",b"DATASUM ")]
        self.assertEqual(new[:80*len(cards)],b"".join(cards))
        h=fits.getheader(product)
        self.assertEqual(h["FILTER"],"Blue");self.assertEqual(h.count("FILTER"),1)
        self.assertEqual(h["ESO DPR TYPE"],"FLAT,SKY")
        self.assertEqual(h["TELESCOP"],"SynScan")
        self.assertEqual(h["WENU PROV TELESCOPE"],"BPO StellaLyra RC 8-inch")
        self.assertEqual(h["WENU PROV SENSOR"],"Panasonic MN34230ALJ")
        self.assertNotIn("ADCBITS",h);self.assertNotIn("CHECKSUM",h)
        with fits.open(product,memmap=False) as hdus:
            self.assertEqual(hdus[0].section[0,:3].tolist(),[0,32767,65535])
        manifest=json.loads((out/"preparation-manifest.json").read_text())
        self.assertEqual(manifest["products"][0]["source_sha256"],hashlib.sha256(original).hexdigest())
        self.assertTrue((out/"PREPARATION_COMPLETE").is_file())

    def test_flat_light_acknowledgement_and_existing_dpr(self):
        # Flat declaration: retain Light labels and matching DPR; require explicit acknowledgement.
        self.frame("Blue/DomeFlats/a.fits",extra=[("HIERARCH ESO DPR TYPE","FLAT,DOME")])
        plan,digest=self.plan();out=self.work/"prepared"
        with self.assertRaises(ValueError):prep.apply_plan(plan,digest,out,False,self.bundle())
        self.assertFalse(out.exists())
        prep.apply_plan(plan,digest,out,True,self.bundle())
        h=fits.getheader(out/"Blue/DomeFlats/a.fits")
        self.assertEqual(h["IMAGETYP"],"Light Frame");self.assertEqual(h.count("ESO DPR TYPE"),1)

    def test_stale_config_plan_source_and_incomplete_marker(self):
        # Plan binding/failure: changed inputs or reviewed TOML refuse output; interrupted copies remain incomplete.
        self.frame();plan,digest=self.plan();out=self.work/"prepared"
        original=self.inputs[2].read_bytes();self.inputs[2].write_bytes(original+b"# changed\n")
        with self.assertRaises(ValueError):prep.apply_plan(plan,digest,out,False,self.bundle())
        self.assertFalse(out.exists());self.inputs[2].write_bytes(original)
        plan.write_text(plan.read_text()+"# changed\n")
        with self.assertRaises(ValueError):prep.apply_plan(plan,digest,out,False,self.bundle())
        self.frame(changes={"EXPTIME":99.0})
        with self.assertRaises(ValueError):
            prep.apply_plan(plan,prep.sha(plan.read_bytes()),out,False,self.bundle())
        self.assertFalse(out.exists())
        plan,digest=self.plan()
        with mock.patch.object(prep,"copy_prepared",side_effect=OSError("injected copy failure")):
            with self.assertRaises(OSError):prep.apply_plan(plan,digest,out,False,self.bundle())
        self.assertTrue((out/"PREPARATION_INCOMPLETE").is_file())
        self.assertFalse((out/"PREPARATION_COMPLETE").exists())
        # Mid-copy input edits must also prevent publication of a completion marker.
        original_copy=prep.copy_prepared
        def change_config(*args,**kwargs):
            result=original_copy(*args,**kwargs)
            self.inputs[2].write_bytes(self.inputs[2].read_bytes()+b"# concurrent edit\n")
            return result
        out2=self.work/"changed-config-output"
        with mock.patch.object(prep,"copy_prepared",side_effect=change_config):
            with self.assertRaises(ValueError):prep.apply_plan(plan,digest,out2,False,self.bundle())
        self.assertTrue((out2/"PREPARATION_INCOMPLETE").is_file())
        self.assertFalse((out2/"PREPARATION_COMPLETE").exists())

    def test_stable_telescope_and_profile_date(self):
        # Stable equipment: observation/profile dates stay separate, including missing DATE-OBS.
        self.frame("Science/a.fits",{"DATE-OBS":"2022-01-08T22:04:06.108"})
        self.frame("Science/b.fits",{"DATE-OBS":"2022-02-06T19:06:04.613"})
        self.frame("Science/c.fits",{"DATE-OBS":None})
        result=self.inventory();self.assertEqual(result["errors"],[])
        self.assertEqual({r["additions"]["WENU PROV TELESCOPE"] for r in result["entries"]},
                         {"BPO StellaLyra RC 8-inch"})
        self.assertEqual(result["profile"]["observatory"]["settings"]["profile_date"],"2026-10-31")
        row=next(r for r in result["entries"] if r["file"]=="Science/c.fits")
        self.assertIn("DATE-OBS",row["missing_metadata"])
        plan,digest=self.plan();out=self.work/"prepared"
        prep.apply_plan(plan,digest,out,False,self.bundle())
        for r in result["entries"]:
            hdr=fits.getheader(out/r["file"])
            self.assertEqual(hdr["WENU PROV TELESCOPE"],"BPO StellaLyra RC 8-inch")
            if "DATE-OBS" in r["reported"]:
                self.assertEqual(hdr["DATE-OBS"],r["reported"]["DATE-OBS"])
            else:
                self.assertNotIn("DATE-OBS",hdr)
        self.inputs[0].write_text(self.inputs[0].read_text().replace('2026-10-31','2026-10-30'))
        self.assertEqual({r["additions"]["WENU PROV TELESCOPE"] for r in self.inventory()["entries"]},
                         {"BPO StellaLyra RC 8-inch"})

    def test_camera_telescope_bad_header_and_link_controls(self):
        # Ingestion refusal: camera/geometry conflicts, malformed cards, duplicates, symlinks and extra HDUs.
        for name,changes,extra in [("a.fits",{"INSTRUME":"Other"},()),("b.fits",{"FOCALLEN":910.0},()),
                                  ("c.fits",{},[("FILTER","Blue")])]:
            self.frame("Science/"+name,changes,extra)
        malformed=self.frame("Science/malformed.fits")
        with malformed.open("r+b") as f:f.seek(100);f.write(b"X")
        extra=self.frame("Science/extra.fits")
        with extra.open("ab") as f:f.write(b"\0"*2880)
        (self.root/"link.fits").symlink_to(extra)
        self.assertEqual(len(self.inventory()["errors"]),6)

    def test_input_validation_and_explicit_filter_alias(self):
        # Inputs stay declarative: reject unknown keys/ambiguous names; permit explicit filter aliases.
        original=self.inputs[2].read_text()
        self.inputs[2].write_text(original.replace('dark = ["Darks"]','dark = ["Bias"]'))
        with self.assertRaises(ValueError):self.bundle()
        self.inputs[2].write_text(original+'\nB = "Blue"\n')
        self.frame("B/Science/a.fits")
        self.assertEqual(self.inventory()["errors"],[])
        self.inputs[0].write_text(self.inputs[0].read_text()+'\nBADKEY = 1\n')
        with self.assertRaises(ValueError):self.bundle()

    def test_cli_generated_toml_roundtrip_and_output_guard(self):
        # CLI integration: generate/reload dataset TOML and prepare via the public helper entry point.
        self.frame();helper=Path(__file__).resolve().parents[1]/"tools/prepare_zwo_asi.py"
        common=["--observatory",str(self.inputs[0]),"--camera",str(self.inputs[1]),"--directories",str(self.inputs[2])]
        plan=self.work/"cli-dataset.toml";out=self.work/"prepared"
        subprocess.run([sys.executable,"-B",str(helper),"preflight",*common,"--root",str(self.root),"--report",str(plan)],check=True)
        value=tomllib.loads(plan.read_text());self.assertEqual(value,self.inventory())
        subprocess.run([sys.executable,"-B",str(helper),"apply",*common,"--plan",str(plan),
                        "--expected-plan-sha256",prep.sha(plan.read_bytes()),"--output",str(out)],check=True)
        self.assertTrue((out/"PREPARATION_COMPLETE").is_file())
        self.assertEqual(prep.main(["plan",*common,"--root",str(self.root),"--report",str(self.root/"bad.toml")]),2)


if __name__=="__main__":
    # Evidence retention: keep synthetic fixtures and actual output trees for inspection.
    print("RETAINED EVIDENCE:",EVIDENCE,flush=True)
    unittest.main(verbosity=2)
