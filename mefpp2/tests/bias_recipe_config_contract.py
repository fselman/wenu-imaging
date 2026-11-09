"""Native recipe TOML selector controls; no FITS pixels, ASDF or observations."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import unittest

ARGS=None
BASE='''bias_recipe_schema_version = 1
settings = "settings.toml"
[bias]
mad = true
ron_pair = [0, 1]
high_sigma = 5.0
readout_id = "test-readout"
bin_x = 1
bin_y = 1
input_bpm = "omitted"
amplifier_id = "whole-detector"
[provenance]
primary = ["MJD-OBS", "DATE-OBS", "TIMESYS", "PRODCATG"]
detector = ["EXTNAME", "HIERARCH ESO DET CHIP ID"]
[[detector]]
id = "A"
configuration_detector = 0
hdus = [1]
expected_extname = "RAW_A"
[[detector]]
id = "B"
configuration_detector = 1
hdus = [2, 2, 2, 2]
'''
class ConfigTests(unittest.TestCase):
    serial=0
    def invoke(self,text=BASE,selection=None,extra=(),success=True):
        ConfigTests.serial+=1
        path=ARGS.work/f'case-{self.serial}.toml';path.write_text(text)
        command=[str(ARGS.probe),'cal','bias','--config',str(path),
                 '--bias','inputs.list','--output-dir','products',*extra]
        if selection is not None:command+=['--detectors',selection]
        result=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode==0,success,result.stderr)
        return result.stdout.splitlines()
    def ids(self,args):
        return [args[i+1] for i,s in enumerate(args) if s=='--detector-id']
    def test_default_and_explicit_all(self):
        self.assertEqual(self.ids(self.invoke()),['A','B'])
        self.assertEqual(self.ids(self.invoke(selection='all')),['A','B'])
        self.assertEqual(self.ids(self.invoke(BASE.replace('mad = true','detectors = "all"\nmad = true'))),['A','B'])
    def test_mad_defaults_off_and_explicit_opt_in(self):
        for setting, expected in (('', 'no'), ('mad = false', 'no'), ('mad = true', 'yes')):
            out = self.invoke(BASE.replace('mad = true', setting))
            self.assertEqual(out[out.index('--mad')+1], expected)
    def test_qc_profiles(self):
        self.assertNotIn('--qc', self.invoke())
        for profile in ('legacy', 'full'):
            out = self.invoke(extra=('--qc', profile))
            self.assertEqual(out[out.index('--qc')+1], profile)
            text = BASE.replace('mad = true', 'qc = "'+profile+'"\nmad = true')
            out = self.invoke(text)
            self.assertEqual(out[out.index('--qc')+1], profile)
            out = self.invoke(text, extra=('--qc', 'full'))
            self.assertEqual(out.count('--qc'), 1)
            self.assertEqual(out[out.index('--qc')+1], 'full')
        for value in ('"off"', 'true', '1'):
            self.invoke(BASE.replace('mad = true', 'qc = '+value+'\nmad = true'), success=False)
        self.invoke(extra=('--qc', 'off'), success=False)
        self.invoke(extra=('--qc', 'full', '--qc', 'legacy'), success=False)

    def test_median_even_handling(self):
        self.assertIn("MEDIAN_EVEN=default",self.invoke())
        for mode in ("average","lower"):
            self.assertIn("MEDIAN_EVEN="+mode,self.invoke(BASE.replace("mad = true",'median_even_handling = "'+mode+'"\nmad = true')))
        for value in ('"upper"','true','1'):
            self.invoke(BASE.replace("mad = true","median_even_handling = "+value+"\nmad = true"),success=False)
        self.invoke(BASE.replace('id = "A"','median_even_handling = "lower"\nid = "A"'),success=False)
    def test_subset_and_catalogue_order(self):
        out=self.invoke(selection='B')
        self.assertEqual(self.ids(out),['B'])
        self.assertEqual(out[out.index('--reference-detector')+1],'B')
        self.assertEqual(self.ids(self.invoke(selection='B,A')),['A','B'])
        self.assertEqual(self.ids(self.invoke(BASE.replace('mad = true','detectors = ["B"]\nmad = true'))),['B'])
    def test_primary_or_single_extension(self):
        for hdu in (0,1):
            one=BASE[:BASE.index('[[detector]]\nid = "B"')].replace('hdus = [1]',f'hdus = [{hdu}]')
            one=one.replace('expected_extname = "RAW_A"','')
            out=self.invoke(one)
            self.assertEqual(self.ids(out),['A'])
            self.assertEqual(out[out.index('--hdu')+1],str(hdu))
            self.assertEqual(out[out.index('--raw-expected-extname')+1],'omitted')
    def test_no_unknown_duplicate_or_empty_selection(self):
        for selection in ('C','A,A','A,','',',A','A,,B'):
            self.invoke(selection=selection,success=False)
        for setting in ('[]','["A","A"]','["C"]','"A"','false'):
            self.invoke(BASE.replace('mad = true',f'detectors = {setting}\nmad = true'),success=False)
    def test_invalid_bindings_and_unknown_fields(self):
        for text in (
            BASE.replace('id = "B"','id = "A"'),
            BASE.replace('configuration_detector = 1','configuration_detector = 0'),
            BASE.replace('hdus = [1]','hdus = [-1]'),
            BASE.replace('hdus = [1]','hdus = [1.0]'),
            BASE.replace('hdus = [1]','hdus = []'),
            BASE.replace('bin_x = 1','bin_x = "1"'),
            BASE.replace('bin_x = 1','bim_x = 1'),
            BASE.replace('mad = true','mad = "yes"'),
            BASE.replace('mad = true','reference_detector = "C"\nmad = true'),
            BASE.replace('settings.toml','absent.toml'),
        ):
            self.invoke(text,success=False)
        self.invoke(extra=('--mad','no'),success=False)
    def test_header_selection_limits(self):
        self.invoke(BASE.replace('"MJD-OBS", "DATE-OBS", "TIMESYS", "PRODCATG"',
                                 '"MJD-OBS", "HIERARCH MJD-OBS"'),success=False)
        for key in ('COMMENT','HISTORY','CONTINUE','END','bad-key'):
            self.invoke(BASE.replace('"MJD-OBS"',json.dumps(key)),success=False)
        keys=', '.join(json.dumps('KEY'+str(i)) for i in range(17))
        self.invoke(BASE.replace('"MJD-OBS", "DATE-OBS", "TIMESYS", "PRODCATG"',keys),success=False)
    def test_paths_and_bpm_inheritance(self):
        (ARGS.work/'mask.fits').write_bytes(b'synthetic path sentinel only')
        text=BASE.replace('input_bpm = "omitted"','input_bpm = "mask.fits"\nbpm_good_value = 1\nbpm_coordinates = "active"')
        text=text.replace('hdus = [1]','hdus = [1]\nbpm_hdu = 1').replace('hdus = [2, 2, 2, 2]','hdus = [2]\nbpm_hdu = 2')
        out=self.invoke(text)
        self.assertEqual(out[out.index('--config')+1],str((ARGS.work/'settings.toml').resolve()))
        self.assertEqual(out[out.index('--input-bpm')+1],str((ARGS.work/'mask.fits').resolve()))
    def test_legacy_configuration_is_not_reinterpreted(self):
        out=self.invoke('schema_version=1\n[native]\n"MEF.NCHIPS"=1\n')
        self.assertNotIn('--detector-id',out)
        self.invoke('schema_version=1\n[native]\n"MEF.NCHIPS"=1\n',selection='all',success=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--probe',type=Path,required=True)
    ARGS=p.parse_args();ARGS.work=ARGS.work.resolve();ARGS.work.mkdir()
    (ARGS.work/'settings.toml').write_text('# native settings sentinel\n')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ConfigTests))
    (ARGS.work/'results.json').write_text(json.dumps({'successful':result.wasSuccessful(),'tests':result.testsRun,'observations_opened':False})+'\n')
    raise SystemExit(not result.wasSuccessful())
