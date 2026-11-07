"""Same-exposure ROI ratio/ASDF contracts. No image reads, line fitting or plotting."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parent))
import test_pair_qc as fixtures
import pycavi_residual_qc as residual
import pycavi_roi_ratio_qc as storage
from pycavi_roi_ratio import compute
WORK=Path(tempfile.gettempdir())


def samples(levels):
    rows=[]
    for i,(near,far) in enumerate(levels):
        for roi,signal in (('near',near),('far',far)):
            rows.append(dict(detector='D',amplifier='L',roi=roi,input_index=i,asset=f'F{i}.fits',
                hdu=1,pair_id=f'P{i//2}',pair_member=i%2+1,exposure_seconds=float(i+1),signal_adu=signal))
    return rows


class RatioTests(unittest.TestCase):
    def setUp(self):self.work=Path(tempfile.mkdtemp(prefix='ratio-asdf-',dir=WORK))
    def prepare(self):
        run,_,_=fixtures.fixture(self.work);pairs=self.work/'pairs';pairs.mkdir()
        fixtures.bridge.publish(run,pairs,assessment_id='pair',created_at='2026-11-04T00:00:00Z',serializer_revision='1'*40)
        source=self.work/'residual';source.mkdir()
        residual.publish(pairs/'pairs.asdf',source,assessment_id='residual',created_at='2026-11-04T00:00:00Z',source_revision='2'*40)
        target=self.work/'ratio';target.mkdir()
        value=storage.publish(source/'line-residuals.asdf',target,assessment_id='ratio',
            created_at='2026-11-04T00:00:00Z',source_revision='3'*40,minimum=900,maximum=1100,
            numerator_suffix='R0',denominator_suffix='R1')
        return source,target,value
    def test_known_ratios_and_reference_members(self):
        data=compute(samples([(1200,1000),(18000,16000),(27000,24000)]),numerator_roi='near',denominator_roi='far')
        self.assertEqual(data['normalization']['count'],2)
        self.assertEqual(data['normalization']['reference_ratio'],1.125)
        self.assertAlmostEqual(data['rows'][0]['normalized_ratio'],1.2/1.125)
        self.assertAlmostEqual(data['rows'][0]['ratio_departure_percent'],100*(1.2/1.125-1))
        self.assertEqual([r['reference_included'] for r in data['rows']],[False,True,True])
    def test_common_multiplier_cancels_and_inputs_unchanged(self):
        rows=samples([(18000,15000),(24000,20000),(36000,30000)]);before=deepcopy(rows)
        data=compute(rows,numerator_roi='near',denominator_roi='far')
        self.assertEqual(rows,before)
        for r in data['rows']:self.assertAlmostEqual(r['raw_ratio'],1.2)
        self.assertAlmostEqual(data['rows'][2]['normalized_ratio'],1.)
        self.assertEqual([r['pair_member'] for r in data['rows']],[1,2,1])
    def test_missing_nonpositive_and_no_reference(self):
        data=compute(samples([(None,100),(100,0),(100,-1),(1000,500)]),numerator_roi='near',denominator_roi='far')
        self.assertEqual(data['normalization']['count'],0)
        self.assertEqual(data['rows'][-1]['raw_ratio'],2.)
        self.assertTrue(all(r['normalized_ratio'] is None for r in data['rows']))
    def test_matching_refuses_duplicate_missing_and_different_time(self):
        base=samples([(18000,16000),(27000,24000)])
        for rows in (base+[deepcopy(base[0])],base[:-1]):
            with self.assertRaises(ValueError):compute(rows,numerator_roi='near',denominator_roi='far')
        altered=deepcopy(base);altered[1]['exposure_seconds']=99
        with self.assertRaises(ValueError):compute(altered,numerator_roi='near',denominator_roi='far')
        with self.assertRaises(ValueError):compute(base,numerator_roi='near',denominator_roi='far',minimum=9,maximum=1)
    def test_roundtrip_relocation_and_source_unchanged(self):
        source,target,result=self.prepare();before={str(p):p.read_bytes() for p in source.rglob('*.asdf')}
        value=storage.read_product(result['path'],expected_digest=result['digest'])
        self.assertEqual(len(value['rows']),4)
        self.assertTrue(all(r['normalized_ratio']==1 for r in value['rows']))
        self.assertEqual(value['measurement_stage'],'raw_pair_bias_subtracted_without_overscan')
        moved=self.work/'moved';shutil.move(str(target),moved)
        self.assertEqual(storage.read_product(moved/'roi-ratio.asdf'),value)
        self.assertEqual(before,{str(p):p.read_bytes() for p in source.rglob('*.asdf')})
    def test_digest_conflict_and_broken_link_refused(self):
        source,target,result=self.prepare()
        for kwargs in (dict(expected_digest='0'*64),dict(expected_residual_digest='0'*64)):
            with self.assertRaises(ValueError):storage.read_product(result['path'],**kwargs)
        with self.assertRaises(ValueError):storage.publish(source/'line-residuals.asdf',target,
            assessment_id='again',created_at='2026-11-04T00:00:00Z',source_revision='3'*40)
        (target/'inputs/line-residuals.asdf').unlink()
        with self.assertRaises((ValueError,OSError)):storage.read_product(result['path'])
    def test_reader_does_not_recompute(self):
        _,_,result=self.prepare();old=storage.compute
        try:
            storage.compute=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('ratio computation forbidden'))
            self.assertEqual(len(storage.read_product(result['path'])['rows']),4)
        finally:storage.compute=old
    def test_command_saves_index_without_fits_or_plots(self):
        source,_,_=self.prepare();index=self.work/'source-index.json'
        # A portable source index with one detector, mirroring the real completed index.
        path=source/'line-residuals.asdf';record=storage.qc.read_record(path)
        index.write_text(json.dumps(dict(status='complete',source_preservation=True,detectors=1,
            products=[dict(detector='ESO_CCD_#65',path=str(path.relative_to(self.work)),digest=record.digest)])))
        target=self.work/'command';target.mkdir()
        argv=[sys.executable,'-B',str(fixtures.ROOT/'tools/compute-roi-ratios.py'),
            '--source-index',str(index),'--run',str(target),'--source-revision','3'*40,
            '--reference-min','900','--reference-max','1100','--numerator-suffix','R0','--denominator-suffix','R1']
        process=subprocess.run(argv,capture_output=True,text=True)
        self.assertEqual(process.returncode,0,process.stdout+process.stderr)
        saved=json.loads((target/'index.json').read_text())
        self.assertEqual((saved['status'],saved['rows']),('complete',4))
        self.assertFalse(saved['line_fits_recomputed']);self.assertFalse(saved['plotting_performed'])


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);a=p.parse_args();WORK=a.work.resolve(strict=True);attempts=[]
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            attempts.append(event);raise RuntimeError('Offline ratio test')
        if event=='open' and args and isinstance(args[0],(str,bytes)) and str(args[0]).lower().endswith('.fits'):
            raise RuntimeError('FITS reads forbidden')
    sys.addaudithook(offline)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RatioTests))
    (WORK/'roi-ratio-results.json').write_text(json.dumps(dict(tests=result.testsRun,successful=result.wasSuccessful(),network_attempts=attempts),indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() and not attempts else 1)
