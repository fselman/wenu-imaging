"""Compile/exercise native output rules in a special synthetic directory.

Only the new C path helper is exercised; no mefpp image recipe, FITS/ASDF
writer, Pycavi, runtime installation or observational processing is involved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
STAMP = '2026-11-06T15:00:00.123Z'
WORK = None
PROBE = None

class PathsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.caller = self.base/'orchestration'; self.caller.mkdir()
        self.raw = self.base/'raw'; self.raw.mkdir()
        (self.raw/'untouched.fits').write_bytes(b'input sentinel; no image reads')
        self.products = self.base/'products with spaces'; self.products.mkdir()
    def run_path(self, directory=None, output=None, product_class='CMDP', stamp=STAMP, sequence=1):
        before = {str(p.relative_to(self.base)):hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.base.rglob('*') if p.is_file()}
        result = subprocess.run([str(PROBE),str(self.caller),str(directory) if directory is not None else '-',
            str(output) if output is not None else '-',product_class,stamp,str(sequence)],
            cwd=self.caller,capture_output=True,text=True)
        after = {str(p.relative_to(self.base)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.base.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        self.assertFalse(list(self.caller.iterdir()))
        return result
    def test_generated_calibration_and_science_names(self):
        for kind in ('CMDP','SMDP'):
            r=self.run_path(directory=self.products,product_class=kind)
            self.assertEqual(r.returncode,0,r.stderr)
            directory,fits,asdf,log=r.stdout.splitlines()
            self.assertEqual(directory,str(self.products))
            stem=self.products/(kind+'.'+STAMP+'.001')
            self.assertEqual((fits,asdf,log),tuple(str(stem)+s for s in ('.fits','.asdf','.log')))
    def test_complete_output_extracts_directory_and_preserves_basename(self):
        output=self.products/'custom.name.with.dots.fits'
        r=self.run_path(output=output)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout.splitlines(),[str(self.products),str(output),
            str(self.products/'custom.name.with.dots.asdf'),str(self.products/'custom.name.with.dots.log')])
    def test_both_options_fail_even_for_the_same_directory(self):
        r=self.run_path(directory=self.products,output=self.products/'same.fits')
        self.assertEqual(r.returncode,1)
        self.assertIn('not both',r.stderr)
    def test_neither_option_fails(self):
        r=self.run_path();self.assertEqual(r.returncode,1)
        self.assertIn('Supply',r.stderr)
    def test_relative_output_resolves_against_invocation(self):
        r=self.run_path(output='../products with spaces/relative.fits')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout.splitlines()[1],str(self.products/'relative.fits'))
    def test_selected_bias_subdirectory_must_exist(self):
        bias=self.products/'cal'/'bias'
        self.assertEqual(self.run_path(directory=bias).returncode,1)
        bias.mkdir(parents=True)
        r=self.run_path(directory=bias)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout.splitlines()[0],str(bias))
    def test_existing_fits_asdf_log_and_dangling_link_refused(self):
        for suffix in ('.fits','.asdf','.log'):
            path=self.products/('CMDP.'+STAMP+'.001'+suffix)
            path.write_bytes(b'protected product')
            self.assertEqual(self.run_path(directory=self.products).returncode,1)
            path.unlink()
        path=self.products/'custom.asdf';path.symlink_to(self.products/'absent')
        self.assertEqual(self.run_path(output=self.products/'custom.fits').returncode,1)
        self.assertTrue(path.is_symlink())
    def test_invalid_timestamp_suffix_class_and_sequence_refused(self):
        for stamp in ('2026-02-30T00:00:00.000Z','2026-11-06T25:00:00.000Z','2026-11-06'):
            self.assertEqual(self.run_path(directory=self.products,stamp=stamp).returncode,1)
        self.assertEqual(self.run_path(directory=self.products,sequence=0).returncode,1)
        self.assertEqual(self.run_path(directory=self.products,product_class='OTHER').returncode,1)
        self.assertEqual(self.run_path(output=self.products/'wrong.fit').returncode,1)
    def test_sequence_is_not_limited_to_three_digits(self):
        r=self.run_path(directory=self.products,sequence=1000)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue(r.stdout.splitlines()[1].endswith('.1000.fits'))
    def test_fixed_clock_fraction_and_calendar_rollover(self):
        from datetime import datetime, timezone
        for text,microseconds,expected in (
            ('2026-11-06T12:34:12',340000,'2026-11-06T12:34:12.340Z'),
            ('2026-12-31T23:59:59',999999,'2026-12-31T23:59:59.999Z'),
            ('2027-01-01T00:00:00',0,'2027-01-01T00:00:00.000Z'),
            ('2028-02-29T00:00:00',123456,'2028-02-29T00:00:00.123Z')):
            seconds=int(datetime.fromisoformat(text).replace(tzinfo=timezone.utc).timestamp())
            r=subprocess.run([str(PROBE),'--format',str(seconds),str(microseconds)],
                             cwd=self.caller,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.strip(),expected)
        r=subprocess.run([str(PROBE),'--format','0','1000000'],capture_output=True,text=True)
        self.assertEqual(r.returncode,1)
    def test_clock_capture_format(self):
        r=subprocess.run([str(PROBE),'--capture'],cwd=self.caller,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertRegex(r.stdout.strip(),r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--cc',type=Path,required=True)
    args=parser.parse_args();WORK=args.work.resolve(strict=True)
    PROBE=WORK/'product-paths-probe'
    common=ROOT/'mefpp2/ins/mef/common'
    # Strict C17 build of the real product path helper and its driver.
    argv=[str(args.cc),'-std=c17','-Wall','-Wextra','-Werror','-pedantic-errors','-I'+str(common),
          str(common/'mef_product_paths.c'),str(ROOT/'mefpp2/tests/product_paths_probe.c'),'-o',str(PROBE)]
    subprocess.run(argv,check=True)
    # Native output-rule controls; each checks unchanged synthetic raw/caller files.
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PathsTests))
    (WORK/'product-paths-results.json').write_text(json.dumps(dict(tests=result.testsRun,
        successful=result.wasSuccessful(),compiler=str(args.cc),build_argv=argv,
        image_recipe_executed=False,observations_opened=False,asdf_writer_exercised=False))+'\n')
    raise SystemExit(not result.wasSuccessful())
