"""Offline QC viewer controls from supplied ASDF transports; no pixel measurements (#235)."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parent))
import test_pair_qc as fixtures
ROOT=fixtures.ROOT
spec=importlib.util.spec_from_file_location('viewer',ROOT/'tools/view-pair-qc.py')
viewer=importlib.util.module_from_spec(spec);spec.loader.exec_module(viewer)
WORK=Path(tempfile.gettempdir())


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix='qc-viewer-',dir=WORK))
        self.run,self.pairs,self.bias=fixtures.fixture(self.work)
        geometry,policy,_=viewer.footprint.load(ROOT/'config/detectors/omegacam-1x1.toml',ROOT/'config/processing/omegacam-characterization.toml')
        self.geometry=geometry;self.policy=policy
        # This legacy raw-table fixture describes display geometry only.
        # Its deliberately shifted crop is not a numerical preparation profile.
        self.policy.pop("linearity_preparation_schema_version",None)
        self.policy.pop("linearity_preparation",None)
        # Use two exact supplied-transport ROI rectangles in the first detector.
        self.policy['roi']=[r for r in self.policy['roi'] if r['detector']!='ESO_CCD_#65']+[
            dict(id='CCD65.R0',detector='ESO_CCD_#65',amplifier='L',xmin=1,xmax=2,ymin=1,ymax=2),
            dict(id='CCD65.R1',detector='ESO_CCD_#65',amplifier='L',xmin=3,xmax=4,ymin=1,ymax=2)]
        next(t for t in self.policy['trim'] if t['detector']=='ESO_CCD_#65')['retained']=[6,2049,6,4096]
        self.detectors=self.work/'detectors.toml';self.processing=self.work/'processing.toml'
        self.write_profiles()
        self.records=self.work/'records';self.records.mkdir()
    def write_profiles(self):
        def text(values):
            result=''
            for key,value in values.items():
                if isinstance(value,list) and value and isinstance(value[0],dict):continue
                result+=key+' = '+json.dumps(value)+'\n'
            for key,value in values.items():
                if isinstance(value,list) and value and isinstance(value[0],dict):
                    for record in value:result+='\n[['+key+']]\n'+text(record)
            return result
        self.detectors.write_text(text(self.geometry));self.processing.write_text(text(self.policy))
    def publish(self):
        return viewer.bridge.publish(self.run,self.records,assessment_id='viewer-test',created_at='2026-11-04T00:00:00Z',serializer_revision='2'*40)
    def build(self,products=None,diagnostics=None,ratios=None):
        return viewer.build(self.detectors,self.processing,products or [self.records/'pairs.asdf'],diagnostics=diagnostics,ratios=ratios)
    def test_full_precision_missing_and_geometry(self):
        self.publish();payload,frozen=self.build()
        self.assertEqual(payload['panels'][0]['pairs'],self.pairs)
        signals=payload['panels'][0]['signals']
        self.assertEqual(len(signals),8)
        self.assertEqual([r['input_index'] for r in signals],[10,10,11,11,12,12,13,13])
        self.assertEqual([r['asset'] for r in signals[::2]],['F0.fits','F1.fits','F2.fits','F3.fits'])
        self.assertEqual(signals[0]['signal_adu'],999.1234567890124)
        self.assertEqual(signals[-1]['signal_adu'],1001.1234567890124)
        self.assertEqual(len(payload['panels']),32)
        self.assertEqual(sum(p['status']=='missing' for p in payload['panels']),31)
        self.assertEqual(payload['panels'][0]['bias'],self.bias)
        self.assertEqual([p['geometry'] for p in payload['panels']],self.geometry['detector'])
        self.assertIn('pairs.asdf',payload['panels'][0]['sources']['pairs']['path'])
        viewer.unchanged(frozen)
        # Retain an explicit incomplete-data fixture for browser interaction checks.
        html=viewer.render(payload)
        self.assertNotIn('QcResiduals.analyze',html)
        self.assertIn('id="residual-x"',html)
        self.assertNotIn('__QC_RESIDUAL_SCRIPT__',html)
        (WORK/'viewer-test.html').write_text(html)
        saved=self.work/'computed';saved.mkdir()
        product=saved/'CCD65';product.mkdir()
        result=viewer.residual_qc.publish(self.records/'pairs.asdf',product,assessment_id='residual',created_at='2026-11-04T00:00:00Z',source_revision='3'*40)
        result['path']='CCD65/line-residuals.asdf'
        index=saved/'index.json';index.write_text(json.dumps(dict(status='complete',source_preservation=True,products=[result])))
        original=viewer.residual_qc.analyze
        try:
            viewer.residual_qc.analyze=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('display must not refit'))
            rendered,_=self.build(diagnostics=index)
        finally:viewer.residual_qc.analyze=original
        diagnostic=rendered['panels'][0]['diagnostics']
        self.assertEqual(len(diagnostic['rows']),8)
        self.assertAlmostEqual(diagnostic['rows'][0]['residual_adu'],-1.)
        (WORK/'viewer-saved-diagnostic.html').write_text(viewer.render(rendered))
        ratios=self.work/'ratios';ratios.mkdir()
        output=ratios/'CCD65';output.mkdir()
        ratio=viewer.ratio_qc.publish(product/'line-residuals.asdf',output,
            assessment_id='ratio',created_at='2026-11-04T00:00:00Z',source_revision='4'*40,
            numerator_suffix='R0',denominator_suffix='R1',minimum=900.,maximum=1100.)
        ratio['path']='CCD65/roi-ratio.asdf'
        ratio_index=ratios/'index.json'
        ratio_index.write_text(json.dumps(dict(status='complete',source_preservation=True,products=[ratio])))
        original_ratio=viewer.ratio_qc.compute
        try:
            viewer.ratio_qc.compute=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('display must not divide/normalize'))
            viewer.residual_qc.analyze=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('display must not refit'))
            rendered,frozen=self.build(diagnostics=index,ratios=ratio_index)
        finally:
            viewer.ratio_qc.compute=original_ratio;viewer.residual_qc.analyze=original
        self.assertEqual(len(rendered['panels'][0]['ratio']['rows']),4)
        viewer.unchanged(frozen)
        (WORK/'viewer-ratio-test.html').write_text(viewer.render(rendered))
        bad=json.loads(ratio_index.read_text());bad['products'][0]['digest']='0'*64
        ratio_index.write_text(json.dumps(bad))
        with self.assertRaises(ValueError):self.build(diagnostics=index,ratios=ratio_index)

    def test_exposure_projection_preserves_members_nulls_and_signed_values(self):
        original=copy.deepcopy(self.pairs)
        rows=copy.deepcopy(self.pairs)
        rows[0]['signal1_adu']=None
        rows[0]['signal2_adu']=-0.0
        rows[2]['signal1_adu']=-3.25
        rows[2]['second_seconds']=5.125
        result=viewer.exposure_rows(rows)
        self.assertEqual(len(result),2*len(rows))
        self.assertEqual([r['input_index'] for r in result],[10,10,11,11,12,12,13,13])
        self.assertIsNone(result[0]['signal_adu'])
        self.assertEqual(result[2]['signal_adu'],-3.25)
        self.assertEqual(result[4]['exposure_seconds'],5.125)
        self.assertEqual(result[6]['signal_adu'].hex(),(-0.0).hex())
        for r in result:
            source=rows[r['source_row_index']]
            self.assertEqual({k:r[k] for k in source},source)
            self.assertEqual(r['population'],'pair_common_accepted_pixels')
            self.assertEqual(r['processing_stage'],'raw_pair_bias_subtracted_without_overscan')
        result[0]['asset']='display-only-change'
        self.assertEqual(self.pairs,original)
        self.assertEqual(rows[0]['first_asset'],'F0.fits')

    def test_saved_diagnostic_digest_mismatch_refused(self):
        self.publish()
        saved=self.work/'computed';saved.mkdir()
        directory=saved/'CCD65';directory.mkdir()
        result=viewer.residual_qc.publish(self.records/'pairs.asdf',directory,
            assessment_id='diag',created_at='2026-11-04T00:00:00Z',source_revision='3'*40)
        result.update(path='CCD65/line-residuals.asdf',digest='0'*64)
        index=saved/'index.json';index.write_text(json.dumps(dict(status='complete',source_preservation=True,products=[result])))
        with self.assertRaises(ValueError):self.build(diagnostics=index)
    def test_unavailable_stays_null(self):
        row=self.pairs[0];row['point_gain_e_per_adu']=None;row['gain_state']='nonpositive_variance'
        path=self.run/'native/pairs.tsv';path.write_text('\t'.join(fixtures.bridge.PAIR_COLUMNS)+'\n'+'\n'.join(fixtures.row_text(fixtures.bridge.PAIR_COLUMNS,r) for r in self.pairs)+'\n')
        receipt=json.loads((self.run/'execution.json').read_text())
        for output in receipt['outputs']:
            if output['path']==str(path):output.update(sha256=viewer.bridge.sha(path.read_bytes()),size=path.stat().st_size)
        (self.run/'execution.json').write_text(json.dumps(receipt))
        self.publish();payload,_=self.build()
        self.assertIsNone(payload['panels'][0]['pairs'][0]['point_gain_e_per_adu'])
        self.assertIn('null',viewer.render(payload))
    def test_duplicate_and_unknown_detector_refused(self):
        self.publish()
        with self.assertRaises(Exception):self.build([self.records/'pairs.asdf']*2)
        self.geometry['detector']=self.geometry['detector'][1:]
        self.policy['trim']=[t for t in self.policy['trim'] if t['detector']!='ESO_CCD_#65']
        self.policy['roi']=[r for r in self.policy['roi'] if r['detector']!='ESO_CCD_#65']
        self.write_profiles()
        with self.assertRaises(Exception):self.build()
    def test_roi_and_native_slot_mismatch_refused(self):
        self.publish();saved=copy.deepcopy(self.policy)
        next(r for r in self.policy['roi'] if r['id']=='CCD65.R0')['xmax']=3
        self.write_profiles()
        with self.assertRaises(Exception):self.build()
        self.policy=saved;self.geometry['detector'][0]['native_paf_chip']=32;self.write_profiles()
        with self.assertRaises(Exception):self.build()
    def test_broken_leaf_and_changed_inputs_refused(self):
        self.publish();payload,frozen=self.build()
        leaf=next(p for p in self.records.glob('*.asdf') if p.name not in ('pairs.asdf','bias-ron.asdf'))
        leaf.unlink()
        with self.assertRaises(Exception):self.build()
        with self.assertRaises(Exception):viewer.unchanged(frozen)
    def test_script_escaping_and_offline_template(self):
        self.publish();payload,_=self.build();payload['authority']='</script><script>alert(1)</script>'
        html=viewer.render(payload)
        self.assertNotIn(payload['authority'],html)
        self.assertIn('\\u003c/script>',html)
        self.assertNotIn('src="http',html);self.assertNotIn('fetch(',html)
        self.assertIn('data-roi',html);self.assertIn('data-row',html)
    def test_failed_batch_refused(self):
        batch=self.work/'failed-batch';batch.mkdir()
        for name,data in (('batch.json',{'entries':[]}),('execution.json',{'status':'failed'}),('shared-verification.json',{})):
            (batch/name).write_text(json.dumps(data))
        with self.assertRaises(Exception):viewer.batch_products(batch)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args();WORK=args.work.resolve(strict=True);attempts=[]
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            attempts.append(event);raise RuntimeError('Offline viewer test')
        if event=='open' and args and isinstance(args[0],(str,bytes)) and str(args[0]).lower().endswith('.fits'):
            raise RuntimeError('Raw FITS access forbidden')
    sys.addaudithook(offline)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ViewerTests))
    (WORK/'pair-viewer-results.json').write_text(json.dumps(dict(tests=result.testsRun,successful=result.wasSuccessful(),network_attempts=attempts),indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() and not attempts else 1)
