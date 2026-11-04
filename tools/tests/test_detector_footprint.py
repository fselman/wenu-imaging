"""Geometry regression tests: independent landmarks, PAF agreement and refusals."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('footprint',ROOT/'tools/detector-footprint.py')
viewer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)

class Footprints(unittest.TestCase):
    def read(self,instrument):
        return viewer.load(ROOT/f'config/detectors/{instrument}-1x1.toml',
                           ROOT/f'config/processing/{instrument}-characterization.toml')

    def test_exact_native_paf_source_fingerprints(self):
        for instrument in ('omegacam','wfi'):
            _,processing,_=self.read(instrument)
            native=ROOT/processing['source_paf']
            self.assertEqual(processing['source_paf_sha256'],
                             hashlib.sha256(native.read_bytes()).hexdigest())

    def test_ocam_identity_reflection_and_raw_coordinates(self):
        g,p,t=self.read('omegacam')
        self.assertEqual(len(g['detector']),32)
        self.assertEqual(len(p['roi']),160)
        d={d['id']:d for d in g['detector']}
        self.assertEqual(d['ESO_CCD_#65']['native_paf_chip'],1)
        self.assertEqual(d['ESO_CCD_#96']['native_paf_chip'],32)
        self.assertEqual(d['ESO_CCD_#96']['mosaic_column'],8)
        self.assertEqual(d['ESO_CCD_#65']['illuminated'],[49,2096,1,4100])
        self.assertEqual(d['ESO_CCD_#96']['illuminated'],[49,2096,101,4200])
        r={r['id']:r for r in p['roi']}
        self.assertEqual(r['CCD65.near_readout']['ymin'],129)
        self.assertEqual(r['CCD96.near_readout']['ymin'],3452)
        self.assertEqual(t['ESO_CCD_#96']['retained'],[51,2094,105,4195])

    def test_wfi_identity_not_hdu_and_exceptional_output(self):
        g,p,t=self.read('wfi')
        ds=g['detector'];self.assertEqual(len(ds),8)
        self.assertEqual(ds[4]['id'],'WIN1.CHIP8.OUT1')
        self.assertEqual(ds[7]['id'],'WIN1.CHIP5.OUT2')
        self.assertEqual(ds[7]['mosaic_column'],1)
        self.assertEqual(ds[4]['mosaic_column'],4)
        self.assertEqual(ds[7]['amplifier'],'R')
        self.assertEqual(ds[7]['amplifier_corner'],'lower-left')
        self.assertEqual(ds[4]['amplifier_corner'],'lower-right')
        self.assertEqual(ds[0]['amplifier_corner'],'upper-left')
        self.assertEqual(ds[0]['illuminated'],[49,2094,31,4128])
        self.assertEqual(ds[7]['illuminated'],[49,2094,1,4098])
        self.assertEqual(t[ds[4]['id']]['retained'],[49,2092,2,4098])

    def test_all_processing_crops_and_samples_match_native_paf(self):
        for instrument in ('wfi','omegacam'):
            g,p,trims=self.read(instrument)
            paf=(ROOT/p['source_paf']).read_text()
            def val(key):return int(re.findall(r'^'+re.escape(key)+r'\s+(\d+);',paf,re.M)[0])
            for d in g['detector']:
                chip=d['native_paf_chip'];t=trims[d['id']]
                self.assertEqual(t['retained'],[val(f'MEF.CROP.{k}.CHIP{chip}') for k in ('X.MIN','X.MAX','Y.MIN','Y.MAX')])
                for scan in ('prescan','overscan'):
                    self.assertEqual(t[scan+'_sample'][:2],[val(f'MEF.{scan.upper()}.X.{k}.CHIP{chip}') for k in ('MIN','MAX')])
            document=viewer.render(g,p,trims)
            self.assertEqual(document.count('class="tile"'),len(g['detector']))
            self.assertNotIn('src="http',document)

    def test_refuse_cross_instrument_and_outside_roi(self):
        with self.assertRaisesRegex(ValueError,'Instrument mismatch'):
            viewer.load(ROOT/'config/detectors/wfi-1x1.toml',ROOT/'config/processing/omegacam-characterization.toml')
        source=(ROOT/'config/processing/wfi-characterization.toml').read_text()
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'bad.toml';path.write_text(source.replace('xmax = 640','xmax = 99999',1))
            with self.assertRaisesRegex(ValueError,'outside footprint'):
                viewer.load(ROOT/'config/detectors/wfi-1x1.toml',path)

if __name__=='__main__': unittest.main()
