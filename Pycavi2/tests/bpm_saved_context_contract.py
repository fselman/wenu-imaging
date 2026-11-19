"""BPM effective-snapshot checks and read-only verification of retained products."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct
import sys
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_bpm_linearity_native as bpm


def typed(value):
    return dict(type='float32-bits', value=struct.pack('>f', value).hex())


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.original = {'MEF.BPM.LGAINTHR': typed(0.5), 'MEF.BPM.HGAINTHR': typed(1.5),
                         'UNCHANGED': dict(type='int', value=7)}
        self.limits = dict(response_low=0.6, response_high=1.4)
        self.plan = dict(source_revision='a'*40, bpm=dict(acquisition='quick', output_mode='new',
            upper_fraction=0.85, minimum_span_fraction=0.15, maximum_pair_difference=0.02,
            **self.limits))
        self.entry = dict(detector=dict(detector_id='CCD1', configuration_detector=0),
            reference_rois=[[1, 2, 1, 2]], dependencies=dict(master_snapshot=deepcopy(self.original),
                bpm_response_limits=self.limits, master=dict(product='/cal/bias.fits', hdu=1),
                selection=dict(flat=[dict(path='/raw/flat.fits', hdu=2)], bpm=dict(encoding='omitted'))))
        effective = {**self.original, 'MEF.BPM.LGAINTHR': typed(0.6), 'MEF.BPM.HGAINTHR': typed(1.4)}
        context = dict(mode=2, output_mode=1, rois=self.entry['reference_rois'],
            parameters={k: struct.unpack('>f', struct.pack('>f', v))[0] if k in self.limits else v
                        for k, v in self.plan['bpm'].items() if isinstance(v, float)},
            calibrations=[dict(role='bias', file=dict(path='/cal/bias.fits', hdu=1))],
            reason_histogram=[0], fit_histogram=[1])
        self.q = dict(file=dict(location='/out/bpm.fits'), provenance=dict(operation='cal.bpm',
            producer=dict(source_revision='a'*40), configuration=dict(snapshot=json.dumps(effective))),
            extensions=dict(record_scope='one_final_primary_image_product',
                            operation_context=dict(snapshot=json.dumps(context))),
            characterization=dict(detectors=[dict(detector_id='CCD1', configuration_detector=0,
                measurements=[dict(name=k, value=context[k]) for k in ('reason_histogram', 'fit_histogram')])]),
            embedded_input_records=[dict(original_index=0, file=dict(location='/raw/flat.fits'),
                                         detectors=[dict(source_hdu=2)])])

    def verify(self):
        with patch.object(bpm.native_qc, 'read', return_value=self.q):
            bpm.verify_bpm('unused.asdf', self.plan, self.entry, Path('/out/bpm.fits'))

    def test_declared_current_limits_preserve_original_master(self):
        self.verify()
        self.assertEqual(self.entry['dependencies']['master_snapshot'], self.original)

    def test_unrelated_configuration_change_is_rejected(self):
        snapshot = json.loads(self.q['provenance']['configuration']['snapshot'])
        snapshot['UNCHANGED']['value'] = 8
        self.q['provenance']['configuration']['snapshot'] = json.dumps(snapshot)
        with self.assertRaisesRegex(ValueError, 'effective configuration'):
            self.verify()

    def test_undeclared_response_change_is_rejected(self):
        snapshot = json.loads(self.q['provenance']['configuration']['snapshot'])
        snapshot['MEF.BPM.HGAINTHR'] = typed(1.6)
        self.q['provenance']['configuration']['snapshot'] = json.dumps(snapshot)
        with self.assertRaisesRegex(ValueError, 'effective configuration'):
            self.verify()

    def test_historical_snapshot_without_override_remains_exact(self):
        self.entry['dependencies'].pop('bpm_response_limits')
        self.plan['bpm'].pop('response_low')
        self.plan['bpm'].pop('response_high')
        self.q['provenance']['configuration']['snapshot'] = json.dumps(self.original)
        self.verify()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_retained(candidate):
    """Check completed synthetic output; never execute a reduction or read raw FITS."""
    import pycavi_linearity_native_archive as archive
    import pycavi_bpm_linearity_assembly as assembly
    revision = 'cec96261942c8856ca48565d889cfed3b588e9e1'
    labels = ('top-level-help-check', 'native-toml-recipe-checks', 'recipe-file-identity-checks',
              'shared-cube-bpm-kernel-checks', 'shared-cube-qc-true-checks', 'shared-cube-qc-false-checks')
    assert all((candidate/(label+'.log')).is_file() for label in labels)
    receipts = list((candidate/'reduced').glob(
        'combined-characterization-*/reduced/cal/bpm-linearity/combined/native-recipe.toml'))
    created = [(p, tomllib.loads(p.read_text())) for p in receipts]
    created = [(p, r) for p, r in created if r['final_mef_state']=='assembled'
               and all(not d['bpm_skipped'] for d in r['detectors'])]
    assert len(created)==1, 'Expected one retained completed creation case'
    receipt_path, receipt = created[0]
    run = receipt_path.parent
    assert receipt['status']=='complete' and receipt['input_preservation'] is True
    assert receipt['source_revision']==revision and receipt['qc'] is True
    for key in ('fits', 'asdf'):
        assert digest(Path(receipt[key]))==receipt[key+'_sha256']
    bindings_path = Path(receipt['bindings'])
    assert digest(bindings_path)==receipt['bindings_sha256']
    bindings = tomllib.loads(bindings_path.read_text())
    author_path = Path(bindings['recipe'])
    author = tomllib.loads(author_path.read_text())
    executable = Path(author['native_recipe']['executable'])
    expected = [d['sha256'] for d in bindings['dependencies'] if d['path']==str(executable)]
    assert expected==[digest(executable)], 'Retained native executable changed'
    frozen = [p for p in run.rglob('*') if p.is_file()]
    frozen += [receipt_path, bindings_path, author_path, executable,
               *[candidate/(label+'.log') for label in labels]]
    before = {str(p): digest(p) for p in frozen}

    def offline(event, values):
        if event.startswith('subprocess.') or event=='os.system' or event.startswith('socket.'):
            raise AssertionError('Saved-product recheck attempted execution/network access')
        if event=='open' and isinstance(values[0], (str, bytes)):
            name = Path(values[0].decode() if isinstance(values[0], bytes) else values[0])
            if name.suffix.lower() in ('.fits', '.fit', '.fts'):
                assert name.resolve().is_relative_to(run), 'Recheck attempted to open an input image'
    sys.addaudithook(offline)
    for detector in receipt['detectors']:
        for key in ('fits', 'asdf', 'prepared'):
            assert digest(Path(detector[key]))==detector[key+'_sha256']
        saved = bpm.native_qc.read(detector['prepared'])
        evidence = {item['name']: item['text'] for item in saved['extensions']['native_evidence']}
        context = json.loads(evidence['preparation-context.json'])
        resolved = context['resolved']
        definition = next(d for d in resolved['detectors'] if d['detector_id']==detector['detector_id'])
        selected = next(d for d in author['detectors'] if d['detector_id']==detector['detector_id'])
        rois = {r['id']: r for r in definition['rois']}
        references = [[rois[k][v] for v in ('xmin','xmax','ymin','ymax')]
                      for k in selected['reference_rois']]
        entry = dict(dependencies=context, detector=definition, reference_rois=references)
        bpm.verify_bpm(detector['asdf'], dict(source_revision=revision, bpm=author['bpm']),
                       entry, Path(detector['fits']))
        value = archive.read_product(detector['prepared'])
        assert len(value['exposure_rows'])==100 and len(value['direct_site_replay'])==100
        assert value['historical_sample_comparison']['previously_admitted']==80
        assert value['historical_sample_comparison']['newly_admitted']==20
        assert value['input_bpm_policy']=='omitted' and value['exposure_rows'][0]['signal_adu']==205.5
        assert detector['image_loads']==31 and detector['corrections']==30
        q = bpm.native_qc.read(detector['asdf'])
        policy = json.loads(q['extensions']['operation_context']['snapshot'])
        assert policy['suitability']['coverage_passed'] is False
        assert policy['suitability']['scientific_acceptance'] is False
        from astropy.io import fits
        import numpy as np
        with fits.open(receipt['fits']) as product:
            assert len(product)==6
            expected_planes = dict(COVERAGE=1, NSAMPLE=20, NEWFLAGS=0, SELECTION=1)
            for plane in product[1:]:
                assert plane.data.shape==(2,6)
                assert np.all(plane.data==expected_planes.get(plane.header['EXTNAME'],0))
    assembly.read_product(receipt['asdf'])
    assert before=={str(p): digest(Path(p)) for p in before}
    print('PASS: retained BPM effective settings, exact saved planes, ASDF mappings and measurements')
    print('PASS: original products unchanged; no raw FITS access, native execution or refitting')
    print('RETAINED RECEIPT:', receipt_path)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, help='Recheck a retained cec9626 Mac candidate without processing')
    args, remaining = parser.parse_known_args()
    if args.candidate:
        assert not remaining
        verify_retained(args.candidate.resolve(strict=True))
    else:
        unittest.main(argv=[sys.argv[0], *remaining])
