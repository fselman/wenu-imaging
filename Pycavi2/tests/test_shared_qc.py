"""Metadata-only shared QC/ASDF contracts. No pixel estimators or native tools."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2]
WORK = Path(tempfile.gettempdir())
MODULE = SOURCE / 'Pycavi2/pycavi/pycavi/pycavi_qc.py'
spec = importlib.util.spec_from_file_location('shared_qc_candidate', MODULE)
qc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = qc
spec.loader.exec_module(qc)


class SharedQcTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='shared-qc-', dir=WORK))
        print('QC CASE:', self._testMethodName, '|', self.work, flush=True)
        self.records = self.work / 'QC with spaces'; self.records.mkdir()
        self.assets = self.work / 'assets'; self.assets.mkdir()
        self.producer = dict(name='synthetic-QC-fixture', version='1', source_revision='fixture-v1')

    def file(self, name, kind='raw'):
        path = self.assets / name
        if not path.exists():
            path.write_bytes(b'synthetic identity fixture; not a numerical FITS test\n')
        return dict(id='asset:' + name, filename=name, location=str(path), kind=kind,
                    sha256=None, observed_at='2026-11-02T00:00:00Z',
                    context=dict(instrument='synthetic', readout='fixture'),
                    selectors=[dict(detector_id=d, hdu_index=i + 1, configuration_detector=i)
                               for i, d in enumerate(('A', 'B'))])

    def builder(self, name, kind='raw', adapter=qc.BiasQcRecipe, operation='cal.bias'):
        return adapter(file=self.file(name, kind), assessment_id='assessment:' + name,
                       created_at='2026-11-02T01:00:00Z', producer=self.producer,
                       operation=operation, configuration_id='fixture:configuration-v1')

    def measure(self, builder, file, detector, value, name='bias.level', sources=None):
        builder.add_measurement(detector, name=name, value=value, unit='ADU',
            definition=dict(method='fixture_supplied', stage='fixture_stage',
                            region=dict(coordinates='FITS-1-based', bounds=[1, 2, 1, 2]), sample_count=4),
            sources=sources if sources is not None else [dict(file_id='asset:' + file,
                detector_id=detector, hdu_index=1 if detector == 'A' else 2)])

    def leaf(self, name):
        builder = self.builder(name)
        self.measure(builder, name, 'A', 10)
        self.measure(builder, name, 'B', 20)
        builder.add_unavailable('A', name='pixels.hot', unit='count', stage='definition_pending',
                                reason='hot-pixel definition not yet selected')
        builder.summarize_detectors('bias.level')
        return builder.seal()

    def parent(self, first, second, name='master.fits'):
        builder = self.builder(name, 'product')
        builder.add_input(first, qc_path=qc.qc_filename(first.as_dict()['file']['filename']), participation='used')
        builder.add_input(second, qc_path=qc.qc_filename(second.as_dict()['file']['filename']),
                          participation='rejected', reason='fixture: recipe-specific rejection')
        self.measure(builder, name, 'A', 12)
        self.measure(builder, name, 'B', 18)
        pair = [dict(file_id=leaf.as_dict()['file']['id'], detector_id='A', hdu_index=1)
                for leaf in (first, second)]
        self.measure(builder, name, 'A', 2.5, name='read_noise', sources=pair)
        builder.summarize_detectors('bias.level')
        return builder.seal()

    def test_sidecar_naming_and_explicit_conflicts(self):
        self.assertEqual(qc.qc_filename('raw001.fits'), 'raw001.asdf')
        self.assertEqual(qc.qc_filename('raw001.FITS'), 'raw001.asdf')
        for name in ('x.fits.fz', 'x.fits.gz', '../x.fits', 'x.txt', '.fits'):
            with self.assertRaises(qc.QcError): qc.qc_filename(name)
        record = self.leaf('raw001.fits'); path = qc.write_record(record, self.records)
        before = path.read_bytes()
        with self.assertRaises(qc.QcError): qc.write_record(record, self.records)
        revised = record.as_dict(); revised['record']['assessment_id'] += ':new-assessment'
        with self.assertRaises(qc.QcError): qc.write_record(qc.QcRecord(qc.encoded(revised)), self.records)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(self.records.glob('.qc-*')))

    def test_immutable_record_and_original_participation(self):
        # Named recipe extensions obey the same owned/immutable lifecycle.
        builder = self.builder('extension.fits')
        extension = {'locations': [[3, 2]]}
        builder.add_extension('bias', extension)
        extension['locations'][0][0] = 99
        with self.assertRaises(qc.QcError): builder.add_extension('bias', {})
        record = builder.seal()
        self.assertEqual(record.as_dict()['extensions']['bias']['locations'], [[3, 2]])
        with self.assertRaises(qc.QcError): builder.add_extension('late', {})
        first, second = self.leaf('raw1.fits'), self.leaf('raw2.fits')
        digest = second.digest
        parent = self.parent(first, second)
        altered = second.as_dict(); altered['file']['filename'] = 'changed.fits'
        self.assertEqual(second.digest, digest)
        self.assertEqual(second.as_dict()['inputs'], [])
        self.assertEqual(parent.as_dict()['inputs'][1]['participation']['status'], 'rejected')
        self.assertEqual([i['index'] for i in parent.as_dict()['inputs']], [0, 1])

    def test_raw_product_roundtrip_and_relocation(self):
        first, second = self.leaf('raw1.fits'), self.leaf('raw2.fits')
        for record in (first, second): qc.write_record(record, self.records)
        parent = self.parent(first, second)
        path = qc.write_record(parent, self.records)
        self.assertIn(b'#ASDF_STANDARD 1.6.0', path.read_bytes()[:150])
        self.assertEqual(qc.read_record(path).as_dict(), parent.as_dict())
        measurements = qc.read_record(self.records / 'raw1.asdf').as_dict()['characterization']
        self.assertEqual([s['value'] for s in measurements['summaries']], [15, 15])
        self.assertEqual(measurements['detectors'][0]['measurements'][1]['value'], None)
        self.assertEqual(measurements['detectors'][0]['measurements'][1]['status'], 'unavailable')
        original = {str(p): p.read_bytes() for p in self.assets.iterdir()}
        moved = self.work / 'moved QC'; shutil.copytree(self.records, moved)
        records = list(qc.traverse_records(moved / 'master.asdf', qc_root=moved))
        self.assertEqual({r.digest for r in records}, {first.digest, second.digest, parent.digest})
        self.assertEqual(original, {str(p): p.read_bytes() for p in self.assets.iterdir()})

    def test_shared_inputs_reused_and_traversal_bounded(self):
        first, second = self.leaf('raw1.fits'), self.leaf('raw2.fits')
        for record in (first, second): qc.write_record(record, self.records)
        one = self.parent(first, second, 'master1.fits'); qc.write_record(one, self.records)
        two = self.parent(first, second, 'master2.fits'); qc.write_record(two, self.records)
        joint = self.builder('higher.fits', 'product')
        joint.add_input(one, qc_path='master1.asdf', participation='used')
        joint.add_input(two, qc_path='master2.asdf', participation='used')
        root = qc.write_record(joint.seal(), self.records)
        self.assertEqual(len(list(qc.traverse_records(root, qc_root=self.records))), 5)
        with self.assertRaises(qc.QcError): list(qc.traverse_records(root, qc_root=self.records, max_records=1))

    def test_broken_frozen_reference_and_no_incomplete_parent(self):
        first, second = self.leaf('raw1.fits'), self.leaf('raw2.fits')
        parent = self.parent(first, second)
        with self.assertRaises((qc.QcError, OSError)): qc.write_record(parent, self.records)
        self.assertFalse((self.records / 'master.asdf').exists())
        qc.write_record(first, self.records); qc.write_record(second, self.records)
        root = qc.write_record(parent, self.records)
        # Deliberately corrupt only private synthetic QC evidence, not image inputs.
        (self.records / 'raw1.asdf').unlink()
        changed = first.as_dict(); changed['record']['assessment_id'] = 'different-assessment'
        qc.write_record(qc.QcRecord(qc.encoded(changed)), self.records)
        with self.assertRaises(qc.QcError): list(qc.traverse_records(root, qc_root=self.records))

    def test_bias_units_pair_origin_and_finite_values(self):
        builder = self.builder('raw.fits')
        with self.assertRaises(qc.QcError):
            builder.add_measurement('A', name='read_noise', value=3, unit='electron', definition={}, sources=[])
        with self.assertRaises(qc.QcError):
            self.measure(builder, 'raw.fits', 'A', 3, name='read_noise')
        bad = self.builder('bad.fits'); self.measure(bad, 'bad.fits', 'A', float('nan'))
        with self.assertRaises(qc.QcError): bad.seal()
        bad = self.builder('unknown.fits'); self.measure(bad, 'unknown.fits', 'A', 1,
            sources=[dict(file_id='not-an-input', detector_id='A', hdu_index=1)])
        with self.assertRaises(qc.QcError): bad.seal()

    def test_missing_values_not_zero_and_profiles_preserved(self):
        builder = self.builder('raw.fits')
        for detector in ('A', 'B'):
            builder.add_unavailable(detector, name='overscan.rms', unit='ADU', stage='definition_pending',
                                    reason='RMS estimator/region not selected')
        builder.summarize_detectors('overscan.rms')
        self.measure(builder, 'raw.fits', 'A', [1, 2, 3], name='profile.rows')
        tree = builder.seal().as_dict()['characterization']
        self.assertEqual([s['value'] for s in tree['summaries']], [None, None])
        self.assertEqual(tree['summaries'][0]['unit'], 'ADU')
        self.assertEqual(tree['detectors'][0]['measurements'][1]['value'], [1, 2, 3])

    def test_same_common_structure_for_another_recipe(self):
        raw = self.leaf('raw.fits'); qc.write_record(raw, self.records)
        builder = self.builder('flat.fits', 'product', adapter=qc.QcRecipe, operation='cal.domeff')
        builder.add_input(raw, qc_path='raw.asdf', participation='used')
        self.measure(builder, 'flat.fits', 'A', 12000, name='illumination.level')
        product = builder.seal()
        path = qc.write_record(product, self.records)
        self.assertEqual(set(qc.read_record(path).as_dict()), set(raw.as_dict()))
        self.assertEqual(product.as_dict()['provenance']['operation'], 'cal.domeff')

    def test_source_mapping_and_reference_root_checked(self):
        first, second = self.leaf('raw1.fits'), self.leaf('raw2.fits')
        for record in (first, second): qc.write_record(record, self.records)
        parent = self.parent(first, second).as_dict()
        for m in parent['characterization']['detectors'][0]['measurements']:
            if m['name'] == 'read_noise': m['sources'][0]['hdu_index'] = 99
        with self.assertRaises(qc.QcError): qc.write_record(qc.QcRecord(qc.encoded(parent)), self.records)
        self.assertFalse((self.records / 'master.asdf').exists())
        outside = self.work / 'outside'; outside.mkdir(); qc.write_record(first, outside)
        builder = self.builder('outside-parent.fits', 'product')
        builder.add_input(first, qc_path='../outside/raw1.asdf', participation='used')
        with self.assertRaises(qc.QcError): qc.write_record(builder.seal(), self.records)

    def test_unknown_schema_rejected_and_offline_reference(self):
        import asdf
        raw = self.leaf('raw.fits')
        bad = raw.as_dict(); bad['record']['schema_version'] = '999'
        with self.assertRaises(qc.QcError): qc.QcRecord(qc.encoded(bad))
        builder = self.builder('master.fits', 'product')
        for path in ('https://example.invalid/raw.asdf', '/raw.asdf'):
            with self.assertRaises(qc.QcError): builder.add_input(raw, qc_path=path, participation='used')
        bad = raw.as_dict(); bad['file']['unknown_field'] = 'not in schema'
        with self.assertRaises(asdf.exceptions.ValidationError):
            qc.write_record(qc.QcRecord(qc.encoded(bad)), self.records)
        self.assertFalse((self.records / 'raw.asdf').exists())
        self.assertFalse(list(self.records.glob('.qc-*')))
        with asdf.AsdfFile({'qc': bad}, version='1.6.0') as af:
            af.write_to(self.records / 'malformed.asdf')
        with self.assertRaises(asdf.exceptions.ValidationError): qc.read_record(self.records / 'malformed.asdf')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    WORK = args.work.resolve(strict=True)
    attempts = []
    def offline(event, arguments):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'):
            attempts.append(event)
            raise RuntimeError('Network attempt in offline QC contract: ' + event)
    sys.addaudithook(offline)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SharedQcTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    (WORK / 'qc-contract-results.json').write_text(json.dumps(dict(
        tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        successful=result.wasSuccessful(), network_attempts=attempts,
        scope='shared metadata/ASDF only; no numerical QC estimator or native recipe'), indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() and not attempts else 1)

