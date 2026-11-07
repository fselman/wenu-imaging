"""Direct display controls with injected common records; optional real ASDF check.

Default controls do NOT claim ASDF decoding or target performance. --asdf adds
the retained-runtime fixture/independent deep-reader equivalence check.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'Pycavi2/tests'), str(ROOT/'Pycavi2/pycavi/pycavi')]
import pycavi_viewer_data as direct
import pycavi_residual_qc as residual
import pycavi_roi_ratio_qc as ratio
import test_pair_qc as raw_fixture
import test_pair_qc_viewer as profiles
spec = importlib.util.spec_from_file_location('direct_viewer', ROOT/'tools/view-pair-qc.py')
viewer = importlib.util.module_from_spec(spec); spec.loader.exec_module(viewer)
WORK = Path(tempfile.gettempdir())
ASDF = False
qc = direct.qc


def fixture(work, detector='ESO_CCD_#65'):
    """Primitive saved records injected at read_record; no ASDF installation."""
    _, raw, bias = raw_fixture.fixture(work)
    for row in raw+bias:
        row['detector'] = detector
    raw[0].update(signal1_adu=5000., signal2_adu=5002., mean_signal_adu=5001.)
    value = dict(schema_version=1, measurement_stage=direct.STAGE, detector=detector,
        units=direct.PREPARATION_UNITS, noise_state='unavailable', covariance=None,
        fit_state='not_performed', rows=[], exposure_rows=[],
        raw_bias_diagnostics=[dict(table=dict(rows=bias))])
    leaves = {}
    for row in raw:
        corrected = dict(first_mean_adu=100.*row['first_seconds']+5.5,
            second_mean_adu=100.*row['second_seconds']+5.5,
            first_spatial_variance_adu2=13., second_spatial_variance_adu2=13., valid_pixels=row['valid_pixels'])
        value['rows'].append(dict(raw=row, corrected=corrected))
        for member, prefix in ((1, 'first'), (2, 'second')):
            asset = row[prefix+'_asset']
            if asset not in leaves:
                leaves[asset] = qc.QcRecipe(file=dict(id=asset, filename=asset, location=asset, kind='raw',
                    sha256=None, observed_at=None, selectors=[dict(detector_id=detector,hdu_index=row[prefix+'_hdu'])], context={}),
                    assessment_id=detector+asset, created_at='2026-11-06T00:00:00Z',
                    producer=dict(name='fixture',version='1',source_revision='a'*40), operation='fixture',
                    configuration_id='fixture').seal()
            value['exposure_rows'].append(dict(detector=detector, amplifier='L', roi=row['roi'],
                input_index=row[prefix+'_input_index'], asset=asset, hdu=row[prefix+'_hdu'],
                pair_id=row['pair_id'], pair_member=member, exposure_seconds=row[prefix+'_seconds'],
                signal_adu=corrected[prefix+'_mean_adu'], spatial_variance_adu2=13.,
                valid_pixels=row['valid_pixels'], measurement_stage=direct.STAGE))
    value['exposure_rows'].sort(key=lambda r:(r['input_index'],r['roi']))
    records = {}
    def save(name, operation, table, extensions, parent=None, metrics=False):
        path = work/(name+'.asdf')
        extension = next(iter(extensions.values()))
        builder = qc.QcRecipe(file=dict(id=detector+name,filename=name+'.tsv',location=name+'.tsv',kind='product',
            sha256=extension.get('transport_sha256','f'*64),observed_at=None,
            selectors=[dict(detector_id=detector,table_name=table)],context={}),
            assessment_id=detector+name,created_at='2026-11-06T00:00:00Z',
            producer=dict(name='fixture',version='1',source_revision='a'*40),operation=operation,
            configuration_id='sha256:'+direct.pairs.sha(direct.pairs.canonical(extension.get('configuration',{})).encode()))
        if parent:builder.add_input(records[parent],qc_path=parent.name,participation='used')
        if metrics:
            for asset, leaf in leaves.items():builder.add_input(leaf,qc_path=asset+'.asdf',participation='used')
            for i,row in enumerate(value['exposure_rows']):
                for field,unit in [('signal_adu','ADU'),('spatial_variance_adu2','ADU2')]:
                    builder.add_measurement(detector,name=f'exposure.{i}.{field}',value=row[field],unit=unit,
                        definition=dict(stage=direct.STAGE,method='fixture',region=dict(roi=row['roi']),sample_count=row['valid_pixels']),
                        sources=[dict(file_id=row['asset'],detector_id=detector,hdu_index=row['hdu'])])
        for key, val in extensions.items():builder.add_extension(key,val)
        record = builder.seal(); records[path] = record
        # Bytes are only fingerprint inputs. read_record is explicitly injected.
        path.write_bytes(record._encoded)
        return path
    source = save('linearity-preparation','linearity.prepare','linearity_preparation',
        dict(linearity_preparation=value,linearity_preparation_context=dict(selection={},native_directory='unavailable')),metrics=True)
    signals = direct.measurements.preparation_rows(value)
    line = dict(schema_version=1,units=direct.LINE_UNITS,measurement_stage=direct.STAGE,source_kind='preparation',
        source_pair_digest=records[source].digest,source_measurement_digest=records[source].digest,
        source_pair_sha256=direct.pairs.sha(source.read_bytes()),transport_sha256='e'*64,
        configuration=dict(minimum_signal_adu=300.,maximum_signal_adu=800.),
        rows=[dict(row,line_prediction_adu=row['signal_adu'],residual_adu=0.,residual_percent=0.,
                   count_rate_adu_per_s=100.,fit_included=True) for row in signals],
        fits=[dict(roi=roi,status='available',reason=None,n=4,intercept_adu=5.5,slope_adu_per_s=100.,
                   time_center_s=3.5,signal_center_adu=355.5) for roi in ('CCD65.R0','CCD65.R1')])
    line_path = save('line-residuals','diagnostic.unweighted_line_residuals','line_residuals',
                     dict(line_residual_diagnostic=line),parent=source)
    config = dict(method='same_exposure_ratio_v1',numerator_roi='CCD65.R0',denominator_roi='CCD65.R1',
        reference_method='arithmetic_mean_of_individual_ratios',reference_signal_min_adu=300.,reference_signal_max_adu=800.,
        uncertainty_state='unavailable',physical_correction_fitted=False)
    rows = []
    originals = {(r['input_index'],r['roi']):r for r in line['rows']}
    for index in sorted({r['input_index'] for r in signals}):
        n,d = [deepcopy(originals[index,roi]) for roi in ('CCD65.R0','CCD65.R1')]
        rows.append(dict(roi='ratio',detector=detector,amplifier='L',**{k:n[k] for k in direct.KEYS},
            exposure_seconds=n['exposure_seconds'],signal_adu=n['signal_adu'],numerator_signal_adu=n['signal_adu'],
            denominator_signal_adu=d['signal_adu'],numerator=n,denominator=d,raw_ratio=1.,normalized_ratio=1.,
            ratio_departure_percent=0.,reference_included=True))
    ratios = dict(schema_version=1,units=direct.RATIO_UNITS,configuration=config,rows=rows,
        normalization=dict(reference_ratio=1.,count=len(rows),members=[{k:r[k] for k in direct.KEYS} for r in rows]),
        source_residual_digest=records[line_path].digest,source_residual_sha256=direct.pairs.sha(line_path.read_bytes()),
        source_pair_digest=records[source].digest,measurement_stage=direct.STAGE,source_kind='preparation',transport_sha256='d'*64)
    ratio_path = save('roi-ratio','diagnostic.same_exposure_roi_ratio','roi_ratio',dict(roi_ratio_diagnostic=ratios),parent=line_path)
    return records,source,line_path,ratio_path,value,line,ratios


class DirectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK);self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name).resolve()
        self.records,self.source,self.line,self.ratio,self.saved,self.lines,self.ratios = fixture(self.work)
        self.events = [];self.reader = direct.DisplayReader(self.events.append)
        self.loader = self.enterContext(patch.object(qc,'read_record',side_effect=lambda p:self.records[Path(p)]))
        # No graph readers, transport replay or scientific computations may run.
        for module,name in [(qc,'traverse_records'),(residual,'source_graph'),(residual,'read_product'),
                            (ratio,'read_product'),(residual,'analyze'),(ratio,'compute')]:
            self.enterContext(patch.object(module,name,side_effect=AssertionError('Forbidden deep/scientific call')))
    def load(self):
        m = self.reader.preparation(self.source)
        line,identity = self.reader.line(self.line,m,self.records[self.line].digest)
        ratios,_ = self.reader.ratio(self.ratio,m,line,identity,self.records[self.ratio].digest)
        return m,line,ratios
    def mutate(self,path,change):
        tree=self.records[path].as_dict();change(tree)
        self.records[path]=qc.QcRecord(qc.encoded(tree))
    def test_exact_saved_values_three_reads_and_progress(self):
        m,line,ratios=self.load()
        self.assertEqual(m['signals'],direct.measurements.preparation_rows(self.saved))
        self.assertEqual(line,self.lines);self.assertEqual(ratios,self.ratios)
        self.assertEqual(m['signals'][0]['signal_adu'],205.5)
        self.assertEqual(m['signals'][0]['raw_pair_diagnostic']['signal1_adu'],5000.)
        self.assertEqual(self.loader.call_count,3)
        self.assertEqual(len(self.reader.timings),3);self.assertEqual(len(self.events),9)
        self.assertIn('Reading preparation',self.events[0]);self.assertTrue(any('3 ASDF' in e for e in self.events))
        self.assertIn('4 rows',self.events[-1])
        viewer.unchanged(self.reader.inputs)
    def test_index_digest_and_duplicate_load_refused(self):
        with self.assertRaisesRegex(ValueError,'index digest'):
            self.reader.preparation(self.source,dict(digest='0'*64))
        self.reader.preparation(self.source)
        with self.assertRaisesRegex(ValueError,'more than once'):self.reader.preparation(self.source)
    def test_preparation_stage_unit_and_common_value_mismatch_refused(self):
        original=self.records[self.source]
        for field,val in [('measurement_stage','raw'),('units',{})]:
            self.records[self.source]=original
            self.mutate(self.source,lambda t:t['extensions']['linearity_preparation'].__setitem__(field,val))
            with self.assertRaises(ValueError):direct.DisplayReader().preparation(self.source)
        self.records[self.source]=original
        self.mutate(self.source,lambda t:t['characterization']['detectors'][0]['measurements'][0].__setitem__('value',0.))
        with self.assertRaisesRegex(ValueError,'Common/saved'):direct.DisplayReader().preparation(self.source)
    def test_line_source_units_stage_and_row_mismatch_refused(self):
        m=self.reader.preparation(self.source);original=self.records[self.line]
        for key,val in [('source_pair_digest','0'*64),('units',{}),('measurement_stage','raw')]:
            self.records[self.line]=original
            self.mutate(self.line,lambda t:t['extensions']['line_residual_diagnostic'].__setitem__(key,val))
            with self.assertRaises(ValueError):direct.DisplayReader().line(self.line,m,self.records[self.line].digest)
        self.records[self.line]=original
        self.mutate(self.line,lambda t:t['extensions']['line_residual_diagnostic']['rows'][0].__setitem__('signal_adu',0.))
        with self.assertRaisesRegex(ValueError,'Original samples'):direct.DisplayReader().line(self.line,m,self.records[self.line].digest)
    def test_ratio_link_and_sample_mismatch_refused(self):
        m=self.reader.preparation(self.source);line,identity=self.reader.line(self.line,m,self.records[self.line].digest)
        original=self.records[self.ratio]
        self.mutate(self.ratio,lambda t:t['inputs'][0]['qc'].__setitem__('assessment_id','wrong'))
        with self.assertRaisesRegex(ValueError,'immediate source'):direct.DisplayReader().ratio(self.ratio,m,line,identity,self.records[self.ratio].digest)
        self.records[self.ratio]=original
        self.mutate(self.ratio,lambda t:t['extensions']['roi_ratio_diagnostic']['rows'][0]['numerator'].__setitem__('asset','wrong'))
        with self.assertRaisesRegex(ValueError,'sample/source'):direct.DisplayReader().ratio(self.ratio,m,line,identity,self.records[self.ratio].digest)
    def test_mosaic_uses_direct_reader_and_retains_ui_payload(self):
        setup=profiles.ViewerTests();setup.setUp();self.addCleanup(__import__('shutil').rmtree,setup.work)
        for name,path in [('lines',self.line),('ratios',self.ratio)]:
            (self.work/(name+'.json')).write_text(json.dumps(dict(status='complete',source_preservation=True,
                products=[dict(detector='ESO_CCD_#65',path=path.name,digest=self.records[path].digest)])))
        payload,frozen=viewer.build(setup.detectors,setup.processing,[self.source],
            diagnostics=self.work/'lines.json',ratios=self.work/'ratios.json',reader=self.reader)
        self.assertEqual(payload['panels'][0]['diagnostics'],self.lines)
        self.assertEqual(payload['validation']['asdf_products_decoded'],3)
        self.assertEqual(self.loader.call_count,3);viewer.unchanged(frozen)
        html=viewer.render(payload);self.assertNotIn('__QC_PAYLOAD__',html)
        (WORK/'direct-viewer-test.html').write_text(html)
    def test_32_detectors_need_exactly_96_selected_reads(self):
        self.records.clear()
        for i in range(32):
            work=self.work/f'CCD{i+65}';work.mkdir()
            records,source,line,ratio_path,*_=fixture(work,f'ESO_CCD_#{i+65}')
            self.records.update(records)
            m=self.reader.preparation(source)
            lines,identity=self.reader.line(line,m,records[line].digest)
            self.reader.ratio(ratio_path,m,lines,identity,records[ratio_path].digest)
        self.assertEqual(self.loader.call_count,96)
        self.assertEqual(len(self.reader.inputs),96)
    def test_preparation_admission_has_zero_product_reads_and_requires_guards(self):
        batch=self.work/'batch';batch.mkdir();products=[]
        for i in range(65,97):
            folder=batch/f'CCD{i}';folder.mkdir();path=folder/'linearity-preparation.asdf';path.touch()
            products.append(dict(detector=f'ESO_CCD_#{i}',path=str(path),digest='a'*64,pairs=50,exposures=100,
                sites=100,trace_frames=30,noise_state='unavailable',reused=i==65))
        index=dict(status='complete_for_owner_inspection',measurement_stage=direct.STAGE,products=products)
        receipt=dict(index,detectors_total=32,detectors_processed=31,reused_detector='ESO_CCD_#65',
            preservation={str(i):True for i in range(11)})
        (batch/'index.json').write_text(json.dumps(index));(batch/'overall-execution.json').write_text(json.dumps(receipt))
        paths,expected=self.reader.admit_preparation(batch)
        self.assertEqual(len(paths),32);self.assertEqual(len(expected),32);self.loader.assert_not_called()
        receipt['preservation']['0']=False;(batch/'overall-execution.json').write_text(json.dumps(receipt))
        with self.assertRaises(ValueError):direct.DisplayReader().admit_preparation(batch)


class AsdfTests(unittest.TestCase):
    def test_real_asdf_matches_independent_deep_readers(self):
        # Real ASDF fixture and independent reference; only on an existing runtime.
        from corrected_diagnostic_fixture import make
        work=Path(tempfile.mkdtemp(prefix='direct-asdf-',dir=WORK)).resolve()
        saved=make(work)
        line_dir=work/'line';line_dir.mkdir();ratio_dir=work/'ratio';ratio_dir.mkdir()
        p=residual.publish(saved['source'],line_dir,assessment_id='direct-line',created_at='2026-11-06T00:00:00Z',
            source_revision='c'*40,minimum=300.,maximum=800.)
        r=ratio.publish(p['path'],ratio_dir,assessment_id='direct-ratio',created_at='2026-11-06T00:00:00Z',
            source_revision='c'*40,minimum=300.,maximum=800.,numerator_suffix='R0',denominator_suffix='R2')
        reference=direct.measurements.read_source(saved['source'])
        expected_line=residual.read_product(p['path']);expected_ratio=ratio.read_product(r['path'])
        reader=direct.DisplayReader()
        with ExitStack() as stack:
            read=stack.enter_context(patch.object(qc,'read_record',wraps=qc.read_record))
            for mod,name in [(qc,'traverse_records'),(residual,'source_graph'),(residual,'read_product'),
                             (ratio,'read_product'),(residual,'analyze'),(ratio,'compute')]:
                stack.enter_context(patch.object(mod,name,side_effect=AssertionError('Forbidden deep/scientific call')))
            m=reader.preparation(saved['source']);line,identity=reader.line(p['path'],m,p['digest'])
            ratios,_=reader.ratio(r['path'],m,line,identity,r['digest'])
        self.assertEqual(read.call_count,3)
        for key in ('signals','pairs','bias','provenance'):self.assertEqual(m[key],reference[key])
        self.assertEqual(direct.pairs.canonical(line),direct.pairs.canonical(expected_line))
        self.assertEqual(direct.pairs.canonical(ratios),direct.pairs.canonical(expected_ratio))
        viewer.unchanged(reader.inputs)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--asdf',action='store_true',help='Also exercise the existing ASDF runtime')
    args=parser.parse_args();WORK=args.work.resolve(strict=True);ASDF=args.asdf
    # Injected-record reader, refusal, bounded-load and actual plot-payload controls.
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(DirectTests)
    if ASDF:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(AsdfTests))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    (WORK/'direct-viewer-results.json').write_text(json.dumps(dict(tests=result.testsRun,
        successful=result.wasSuccessful(),real_asdf_exercised=ASDF,browser_painting_verified=False))+'\n')
    raise SystemExit(not result.wasSuccessful())
