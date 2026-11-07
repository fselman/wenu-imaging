"""Native product-QC structural checks; optional real external-libasdf write/read.

No installation, image recipe, observational FITS read or Pycavi code is used.
Without --prefix only the real C structural validator is compiled/executed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
WORK=PROBE=ARGS=None
BASENAME='CMDP.2026-11-06T15:00:00.123Z.001'
NEGATIVES=['duplicate-input','duplicate-index','duplicate-detector','duplicate-output-hdu','missing-binding',
 'reordered-binding','negative-source-hdu','bad-acceptance','missing-rejection-reason','nonfinite-value',
 'applied-without-bpm','unknown-mask','unknown-source','wrong-input-origin','unavailable-has-value','measured-no-samples','invalid-time',
 'duplicate-measurement','fractional-count','outside-log','bad-sha','invalid-region']

class ValidationTests(unittest.TestCase):
    def test_valid_and_integer_count_metadata(self):
        for mode in ('good','integer-count','with-bpm'):
            r=subprocess.run([str(PROBE),'validate',mode,str(WORK)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
    def test_invalid_identities_bindings_states_values_and_references(self):
        for mode in NEGATIVES:
            with self.subTest(mode=mode):
                r=subprocess.run([str(PROBE),'validate',mode,str(WORK)],capture_output=True,text=True)
                self.assertEqual(r.returncode,1,r.stderr);self.assertTrue(r.stderr.strip())

class WriterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='native-qc-',dir=WORK);self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve();self.fits=self.base/(BASENAME+'.fits');self.asdf=self.base/(BASENAME+'.asdf')
        # Metadata-only file sentinels: FITS pixel validity is outside this writer.
        self.fits.write_bytes(b'untouched final FITS metadata fixture')
        for i in range(3):(self.base/f'raw-{i}.fits').write_bytes(b'untouched raw metadata fixture')
        (self.base/'bpm.fits').write_bytes(b'untouched BPM metadata fixture')
        self.frozen={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.base.glob('*.fits')}
    def run_writer(self,mode='good',output=None):
        r=subprocess.run([str(PROBE),'write',mode,str(self.base),str(output or self.asdf)],capture_output=True,text=True)
        self.assertEqual(self.frozen,{str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in self.frozen})
        self.assertFalse(list(self.base.glob('*.tmp-*')))
        return r
    def verify(self,integer=False,bpm=False):
        argv=[str(ARGS.asdf_python),'-B',str(ARGS.verifier or ROOT/'mefpp2/tests/product_qc_verify.py'),str(self.asdf),
              '--schema',str(ROOT/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json')]
        if integer:argv.append('--integer-count')
        if bpm:argv.append('--with-bpm')
        r=subprocess.run(argv,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_real_native_asdf_schema_and_exact_values(self):
        r=self.run_writer();self.assertEqual(r.returncode,0,r.stderr);self.verify()
    def test_calibration_bindings_and_mask_context(self):
        r=self.run_writer('with-bpm');self.assertEqual(r.returncode,0,r.stderr);self.verify(bpm=True)
    def test_integer_count_serialization(self):
        r=self.run_writer('integer-count');self.assertEqual(r.returncode,0,r.stderr);self.verify(True)
    def test_invalid_metadata_cannot_publish(self):
        r=self.run_writer('unknown-source');self.assertEqual(r.returncode,1)
        self.assertFalse(self.asdf.exists())
    def test_existing_asdf_never_overwritten(self):
        self.asdf.write_bytes(b'protected earlier ASDF')
        r=self.run_writer();self.assertEqual(r.returncode,1)
        self.assertEqual(self.asdf.read_bytes(),b'protected earlier ASDF')
    def test_dangling_asdf_link_never_replaced(self):
        self.asdf.symlink_to(self.base/'missing')
        r=self.run_writer();self.assertEqual(r.returncode,1);self.assertTrue(self.asdf.is_symlink())
    def test_wrong_asdf_basename_refused(self):
        wrong=self.base/'wrong.asdf';r=self.run_writer(output=wrong)
        self.assertEqual(r.returncode,1);self.assertFalse(wrong.exists())
    def test_missing_final_fits_cannot_publish(self):
        self.fits.unlink();del self.frozen[str(self.fits)]
        r=self.run_writer();self.assertEqual(r.returncode,1);self.assertFalse(self.asdf.exists())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--cc',type=Path,required=True)
    p.add_argument('--sdkroot',type=Path);p.add_argument('--prefix',type=Path)
    p.add_argument('--asdf-python',type=Path);p.add_argument('--source-root',type=Path,default=ROOT)
    p.add_argument('--reuse-probe',type=Path,help='Use a retained compiled probe without rebuilding')
    p.add_argument('--verifier',type=Path,help='Use a separately exported corrected verifier')
    ARGS=p.parse_args();ROOT=ARGS.source_root.resolve(strict=True);WORK=ARGS.work.resolve(strict=True)
    if sys.platform=='darwin' and ARGS.sdkroot is None:p.error('Darwin requires explicit --sdkroot')
    if (ARGS.prefix is None)!=(ARGS.asdf_python is None):p.error('Supply --prefix and --asdf-python together')
    PROBE=ARGS.reuse_probe.resolve(strict=True) if ARGS.reuse_probe else WORK/'product-qc-probe'
    if ARGS.verifier:ARGS.verifier=ARGS.verifier.resolve(strict=True)
    common=ROOT/'mefpp2/ins/mef/common'
    argv=[str(ARGS.cc),'-std=c17','-Wall','-Wextra','-Werror','-pedantic-errors','-I'+str(common)]
    sdkroot=None
    if ARGS.sdkroot:
        sdkroot=ARGS.sdkroot.resolve(strict=True)
        if not (sdkroot/'usr/include/time.h').is_file():p.error('SDK has no time.h')
        argv+=['-isysroot',str(sdkroot)]
    argv+=[str(common/'mef_product_qc_validate.c'),str(ROOT/'mefpp2/tests/product_qc_probe.c')]
    if ARGS.prefix:
        prefix=ARGS.prefix.resolve(strict=True)
        if not (prefix/'include/asdf/file.h').is_file():p.error('Retained libasdf headers are missing; do not install')
        argv+=['-isystem',str(prefix/'include'),str(common/'mef_product_qc_asdf.c'),
               '-L'+str(prefix/'lib'),'-Wl,-rpath,'+str(prefix/'lib'),'-lasdf']
    else:argv+=['-DMEF_QC_VALIDATE_ONLY=1']
    argv+=['-lm','-o',str(PROBE)]
    # Strict C17 build of the real validator and optional real ASDF writer.
    if ARGS.reuse_probe:
        print('REUSED PROBE:',PROBE,flush=True)
    else:
        print('BUILD:',json.dumps(argv),flush=True);subprocess.run(argv,check=True)
    # Structural metadata/refusal controls, with no file or numerical computation.
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ValidationTests)
    # Real libasdf publication and independent Python ASDF/schema/exact-value checks.
    if ARGS.prefix:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(WriterTests))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    (WORK/'product-qc-results.json').write_text(json.dumps(dict(tests=result.testsRun,successful=result.wasSuccessful(),
        metadata_cases=len(NEGATIVES)+3,real_asdf_exercised=bool(ARGS.prefix),build_argv=None if ARGS.reuse_probe else argv,sdkroot=str(sdkroot),
        compiled_now=not bool(ARGS.reuse_probe),reused_probe=str(PROBE) if ARGS.reuse_probe else None,
        observations_opened=False,image_recipe_executed=False,pycavi_used=False))+'\n')
    raise SystemExit(not result.wasSuccessful())
