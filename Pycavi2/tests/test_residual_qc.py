"""Saved-data computation/ASDF contracts; no FITS, native tools, plotting or network."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parent))
import test_pair_qc as fixture
import pycavi_residual_qc as storage
from pycavi_residuals import analyze
WORK=Path(tempfile.gettempdir())


def sample(t,s,roi='R0'):
    return dict(roi=roi,exposure_seconds=t,signal_adu=s,asset='source.fits')


class ResidualTests(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix='residual-asdf-',dir=WORK))
    def prepare(self):
        run,_,_=fixture.fixture(self.work)
        source=self.work/'original';source.mkdir()
        fixture.bridge.publish(run,source,assessment_id='source',created_at='2026-11-04T00:00:00Z',serializer_revision='2'*40)
        target=self.work/'diagnostic';target.mkdir()
        result=storage.publish(source/'pairs.asdf',target,assessment_id='diag',
            created_at='2026-11-04T00:00:00Z',source_revision='3'*40)
        return source,target,result
    def test_analytic_solution_and_shutter_absorption(self):
        result=analyze([sample(1,3),sample(2,4),sample(3,8)])
        self.assertEqual(result['fits'][0]['slope_adu_per_s'],2.5)
        self.assertEqual(result['fits'][0]['intercept_adu'],0.)
        self.assertEqual([r['residual_adu'] for r in result['rows']],[.5,-1.,.5])
        shifted=analyze([sample(t,10*(t+.2)) for t in (1,2,10)])
        self.assertAlmostEqual(shifted['fits'][0]['intercept_adu'],2.)
        self.assertAlmostEqual(shifted['rows'][0]['count_rate_adu_per_s'],12.)
        self.assertAlmostEqual(shifted['rows'][-1]['count_rate_adu_per_s'],10.2)
    def test_interval_retains_outside_points_and_input_identity(self):
        rows=[sample(1,3),sample(2,4),sample(3,8)];before=deepcopy(rows)
        result=analyze(rows,minimum=3,maximum=4)
        self.assertEqual(rows,before)
        self.assertEqual([r['fit_included'] for r in result['rows']],[True,True,False])
        self.assertEqual(result['rows'][2]['residual_adu'],3.)
        self.assertEqual(result['rows'][2]['asset'],'source.fits')
    def test_null_signed_zero_negative_and_rank(self):
        result=analyze([sample(0,0),sample(1,-2),sample(2,None)])
        self.assertIsNone(result['rows'][0]['count_rate_adu_per_s'])
        self.assertIsNone(result['rows'][1]['residual_percent'])
        self.assertIsNone(result['rows'][2]['residual_adu'])
        self.assertEqual(result['rows'][1]['count_rate_adu_per_s'],-2.)
        for rows,reason in (([sample(1,1)],'fewer_than_two_points'),
                            ([sample(1,1),sample(1,2)],'no_exposure_time_span')):
            self.assertEqual(analyze(rows)['fits'][0]['reason'],reason)
        self.assertEqual(analyze([sample(1,-0.0)])['rows'][0]['signal_adu'].hex(),(-0.0).hex())
    def test_independent_rois_large_origin_invalid_interval(self):
        result=analyze([sample(1e12+i,3+2*i) for i in range(3)]+[sample(1,100,'R1'),sample(2,200,'R1')])
        self.assertEqual([f['slope_adu_per_s'] for f in result['fits']],[2.,100.])
        result=analyze([sample(1,2),sample(2,4)],minimum=9,maximum=1)
        self.assertEqual(result['fits'][0]['reason'],'invalid_fit_interval')
        self.assertTrue(all(r['residual_adu'] is None for r in result['rows']))
    def test_roundtrip_relocation_and_source_preservation(self):
        source,target,result=self.prepare()
        before={str(p):p.read_bytes() for p in source.glob('*.asdf')}
        value=storage.read_product(result['path'],expected_digest=result['digest'])
        self.assertEqual(len(value['rows']),8)
        self.assertEqual(len(value['fits']),2)
        self.assertEqual(value['units']['residual_percent'],'percent')
        self.assertTrue((target/'line-residuals.tsv').is_file())
        moved=self.work/'moved';shutil.move(str(target),moved)
        self.assertEqual(storage.read_product(moved/'line-residuals.asdf'),value)
        self.assertEqual(before,{str(p):p.read_bytes() for p in source.glob('*.asdf')})
    def test_source_digest_and_conflicts_refused(self):
        source,target,result=self.prepare()
        with self.assertRaises(ValueError):storage.read_product(result['path'],expected_source_digest='0'*64)
        with self.assertRaises(ValueError):storage.read_product(result['path'],expected_digest='0'*64)
        with self.assertRaises(ValueError):storage.publish(source/'pairs.asdf',target,
            assessment_id='again',created_at='2026-11-04T00:00:00Z',source_revision='3'*40)
    def test_read_does_not_recompute(self):
        _,_,result=self.prepare()
        original=storage.analyze
        try:
            storage.analyze=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('refit forbidden'))
            self.assertEqual(len(storage.read_product(result['path'])['rows']),8)
        finally:storage.analyze=original
    def test_recipe_index_and_no_overwrite(self):
        source,_,_=self.prepare()
        target=self.work/'recipe';target.mkdir()
        argv=[sys.executable,'-B',str(fixture.ROOT/'tools/compute-pair-residuals.py'),
              '--pairs-asdf',str(source/'pairs.asdf'),'--run',str(target),'--source-revision','3'*40]
        result=subprocess.run(argv,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        index=target/'index.json';original=index.read_bytes();report=json.loads(original)
        self.assertEqual((report['status'],report['detectors'],report['rows'],report['fits']),('complete',1,8,2))
        product=report['products'][0]
        self.assertEqual(len(storage.read_product(target/product['path'],expected_digest=product['digest'])['rows']),8)
        self.assertFalse(report['plotting_performed'])
        self.assertFalse(list(target.rglob('*.png'))+list(target.rglob('*.html')))
        self.assertFalse(report['raw_FITS_opened'])
        self.assertNotEqual(subprocess.run(argv,capture_output=True).returncode,0)
        self.assertEqual(index.read_bytes(),original)

    def test_broken_frozen_reference_refused(self):
        _,target,result=self.prepare()
        (target/'inputs/pairs.asdf').unlink()
        with self.assertRaises((ValueError,OSError)):storage.read_product(result['path'])


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args();WORK=args.work.resolve(strict=True);attempts=[]
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            attempts.append(event);raise RuntimeError('Offline residual test')
        if event=='open' and args and isinstance(args[0],(str,bytes)) and str(args[0]).lower().endswith('.fits'):
            raise RuntimeError('FITS reads forbidden')
    sys.addaudithook(offline)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ResidualTests))
    (WORK/'residual-qc-results.json').write_text(json.dumps(dict(tests=result.testsRun,
        successful=result.wasSuccessful(),network_attempts=attempts),indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() and not attempts else 1)
