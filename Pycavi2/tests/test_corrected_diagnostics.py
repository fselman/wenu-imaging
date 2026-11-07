"""Corrected ASDF -> existing diagnostics -> read-only viewer; no native commands."""
from copy import deepcopy
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Pycavi2/tests'),str(ROOT/'Pycavi2/pycavi/pycavi')]
from corrected_diagnostic_fixture import make
import pycavi_measurement_display as measurements
import pycavi_residual_qc as residual
import pycavi_roi_ratio_qc as ratio
import test_pair_qc as raw_fixture
spec=importlib.util.spec_from_file_location('corrected_viewer',ROOT/'tools/view-pair-qc.py')
viewer=importlib.util.module_from_spec(spec);spec.loader.exec_module(viewer)
WORK=Path(tempfile.gettempdir())


class CorrectedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=Path(tempfile.mkdtemp(prefix='corrected-diagnostic-fixture-',dir=WORK)).resolve()
        cls.fixture=make(cls.base)
    def setUp(self):self.work=Path(tempfile.mkdtemp(prefix='corrected-inspection-',dir=WORK)).resolve()
    def diagnostics(self):
        line=self.work/'line';line.mkdir()
        product=residual.publish(self.fixture['source'],line,assessment_id='diag',created_at='2026-11-05T00:00:00Z',
            source_revision='c'*40,minimum=300.,maximum=800.)
        ratios=self.work/'ratio';ratios.mkdir()
        r=ratio.publish(product['path'],ratios,assessment_id='ratio',created_at='2026-11-05T00:00:00Z',source_revision='c'*40,
            minimum=300.,maximum=800.,numerator_suffix='R0',denominator_suffix='R2')
        return product,r
    def test_lossless_corrected_projection_and_separate_raw_channels(self):
        source=measurements.read_source(self.fixture['source'])
        self.assertEqual((source['kind'],source['stage']),('preparation',measurements.CORRECTED))
        self.assertEqual(len(source['signals']),100)
        self.assertEqual(source['signals'][0]['signal_adu'],205.5)
        self.assertEqual(source['signals'][0]['spatial_variance_adu2'],13.)
        self.assertEqual(source['signals'][0]['raw_pair_diagnostic']['signal1_adu'],5000.)
        self.assertEqual(source['signals'][0]['processing_stage'],measurements.CORRECTED)
        self.assertEqual([r['input_index'] for r in source['signals'][::5]],list(range(10,30)))
        self.assertEqual(len(source['bias']),5)
        self.assertFalse(list(self.base.glob('*.fits')))
    def test_analytical_corrected_lines_and_ratios(self):
        p,r=self.diagnostics();line=residual.read_product(p['path']);ratios=ratio.read_product(r['path'])
        self.assertEqual(line['source_kind'],'preparation');self.assertEqual(line['measurement_stage'],measurements.CORRECTED)
        self.assertEqual(len(line['rows']),100);self.assertEqual(len(line['fits']),5)
        for fit in line['fits']:
            self.assertAlmostEqual(fit['slope_adu_per_s'],100.)
            self.assertAlmostEqual(fit['intercept_adu'],5.5);self.assertEqual(fit['n'],10)
        self.assertEqual(line['rows'][0]['signal_adu'],205.5)
        self.assertTrue(all(abs(row['residual_adu'])<1e-10 for row in line['rows']))
        self.assertEqual(len(ratios['rows']),20);self.assertEqual(ratios['source_kind'],'preparation')
        self.assertEqual(ratios['normalization']['reference_ratio'],1.)
        self.assertTrue(all(row['normalized_ratio']==1. for row in ratios['rows']))
    def test_relocation_reader_no_refit_or_original_native_images(self):
        p,r=self.diagnostics();moved=self.work/'moved';shutil.copytree(self.work/'ratio',moved)
        original_line,original_ratio=residual.analyze,ratio.compute
        try:
            residual.analyze=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No refitting in reader'))
            ratio.compute=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No ratio computation in reader'))
            value=ratio.read_product(moved/'roi-ratio.asdf');self.assertEqual(len(value['rows']),20)
        finally:residual.analyze=original_line;ratio.compute=original_ratio
    def test_stage_tamper_and_mixed_mosaic_refused(self):
        p,_=self.diagnostics();tree=residual.qc.read_record(p['path']).as_dict()
        tree['extensions']['line_residual_diagnostic']['measurement_stage']=measurements.RAW
        bad=self.work/'bad';bad.mkdir();shutil.copytree(self.work/'line/inputs',bad/'inputs')
        path=residual.qc.write_record(residual.qc.QcRecord(residual.qc.encoded(tree)),bad,qc_root=bad)
        with self.assertRaises(ValueError):residual.read_product(path)
        rawdir=self.work/'raw';rawdir.mkdir();run,_,_=raw_fixture.fixture(rawdir)
        records=self.work/'raw-records';records.mkdir()
        raw_fixture.bridge.publish(run,records,assessment_id='raw',created_at='2026-11-05T00:00:00Z',serializer_revision='c'*40)
        with self.assertRaisesRegex(ValueError,'Cannot mix'):
            viewer.build(self.fixture['detectors'],self.fixture['processing'],[self.fixture['source'],records/'pairs.asdf'])
    def test_preparation_index_requires_outer_guards(self):
        batch=self.work/'batch';batch.mkdir()
        (batch/'index.json').write_text(json.dumps(dict(status='complete_for_owner_inspection',measurement_stage=measurements.CORRECTED,products=[])))
        (batch/'overall-execution.json').write_text(json.dumps(dict(status='complete_for_owner_inspection',products=[],
            detectors_total=32,detectors_processed=31,preservation=dict(images=False))))
        with self.assertRaises(ValueError):measurements.preparation_products(batch)
    def test_saved_diagnostics_viewer_and_frozen_sources(self):
        p,r=self.diagnostics()
        for directory,product in [('line',p),('ratio',r)]:
            item=dict(product,path=Path(product['path']).name)
            (self.work/directory/'index.json').write_text(json.dumps(dict(status='complete',source_preservation=True,products=[item])))
        old_line,old_ratio=residual.analyze,ratio.compute
        try:
            residual.analyze=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Viewer refit forbidden'))
            ratio.compute=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Viewer ratio math forbidden'))
            payload,frozen=viewer.build(self.fixture['detectors'],self.fixture['processing'],[self.fixture['source']],
                diagnostics=self.work/'line/index.json',ratios=self.work/'ratio/index.json')
        finally:residual.analyze=old_line;ratio.compute=old_ratio
        panel=payload['panels'][0]
        self.assertEqual(payload['measurement_stage'],measurements.CORRECTED)
        self.assertEqual(panel['signals'][0]['signal_adu'],205.5)
        self.assertEqual(panel['pairs'][0]['signal1_adu'],5000.)
        self.assertEqual(panel['diagnostics']['rows'][0]['signal_adu'],205.5)
        self.assertEqual(panel['ratio']['rows'][0]['normalized_ratio'],1.)
        viewer.unchanged(frozen)
        (WORK/'corrected-viewer-test.html').write_text(viewer.render(payload))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);a=p.parse_args();WORK=a.work.resolve(strict=True)
    attempts=[]
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            attempts.append(event);raise RuntimeError('Offline diagnostic checks')
    sys.addaudithook(offline)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CorrectedTests))
    (WORK/'corrected-diagnostic-results.json').write_text(json.dumps(dict(tests=result.testsRun,successful=result.wasSuccessful(),network_attempts=attempts))+'\n')
    raise SystemExit(not result.wasSuccessful())
