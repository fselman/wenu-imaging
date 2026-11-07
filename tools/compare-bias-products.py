#!/usr/bin/env python3
"""Read-only comparison of bias pixels, scalar QC and ASDF provenance.

Run with the Astropy interpreter; --asdf-python selects the independent ASDF
reader. Products must use the expanded bias-scalar/1 FITS mapping and the same
ordered raw inputs. A subset product may be compared with a larger reference.
The optional --allow-clipped-ron-additions mode permits only the documented
clipped-RON and explicit binary-policy additions to an older reference.
Only exact own-product source identities are normalized; scientific values,
definitions, raw/calibration references and input measurements remain strict.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SELF_SOURCES = {
    'ESO MPP QC ' + group + ' SRC1'
    for group in ('BPM ACTIVE', 'BPM GOOD', 'HOT DEGEN', 'HOT K',
                  'HOT N', 'HOT THR', 'MAST', 'REQ MAD',
                  'REQ PAIR', 'UMAS', 'VAR')
}
IDENTITY_KEYS = SELF_SOURCES | {'ESO MPP QC ASDF', 'ESO MPP QC PROD'}

CLIPPED_ADDITIONS = {
    'read_noise.clipped', 'ron_clip.mean', 'ron_clip.median', 'ron_clip.stdev',
    'ron_clip.retained', 'ron_clip.rejected_low', 'ron_clip.rejected_high',
    'ron_clip.bpm_excluded', 'ron_clip.nonfinite_excluded', 'ron_clip.iterations',
    'ron_clip.converged', 'ron_clip.sigma_low', 'ron_clip.sigma_high',
    'ron_clip.max_iterations', 'bpm.encoding', 'bpm.bad_when_nonzero',
}
ADDITION_GROUPS = ('RON CLIP', 'RCL MEAN', 'RCL MED', 'RCL STD', 'RCL NVAL',
                   'RCL NLO', 'RCL NHI', 'RCL NBPM', 'RCL NNF', 'RCL ITER',
                   'RCL CONV', 'RCL KLO', 'RCL KHI', 'RCL LIMIT', 'BPM ENC', 'BPM BADNZ')


def compare_headers(actual, retained, allow_additions):
    missing = retained.keys() - actual.keys()
    extra = actual.keys() - retained.keys()
    assert not missing, ('Missing retained QC cards', sorted(missing))
    if allow_additions:
        for key in extra:
            assert any(key == 'ESO MPP QC ' + group or
                       key.startswith('ESO MPP QC ' + group + ' ')
                       for group in ADDITION_GROUPS), ('Unexpected QC addition', key)
        assert extra, 'Expected documented clipping/policy additions'
    else:
        assert not extra, ('Unexpected QC additions', sorted(extra))
    for key in retained.keys() - IDENTITY_KEYS:
        assert actual[key] == retained[key], (key, actual[key], retained[key])
    return len(retained) - len(IDENTITY_KEYS), len(extra)


# This runs in the explicitly selected ASDF environment, not the FITS reader's.
ASDF_READER = r'''
import json, sys, struct, math
from pathlib import Path
import asdf
import numpy as np
e = json.load(sys.stdin)
sys.path.insert(0, str(Path(e['root'])/'mefpp2/tests'))
from bias_qc_fits_contract import verify
schema = Path(e['schema']).read_bytes()
schema_id = json.loads(schema)['id']

def equal(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.array_equal(a, b)
    return a == b

def measurements(values, own_product):
    result = {}
    for m in values:
        assert m['name'] not in result
        row = dict(m)
        row['sources'] = [
            '<own-product>' if s == own_product else s for s in m['sources']
        ]
        result[m['name']] = row
    return result

with asdf.config_context() as config:
    config.add_resource_mapping({schema_id: schema})
    with asdf.open(Path(e['fits']).with_suffix('.asdf'),
                   custom_schema=schema_id, lazy_load=False,
                   strict_extension_check=True) as new, \
         asdf.open(Path(e['reference_fits']).with_suffix('.asdf'),
                   custom_schema=schema_id, lazy_load=False,
                   strict_extension_check=True) as old:
        new.validate()
        old.validate()
        q, r = new.tree['qc'], old.tree['qc']
        assert q['file']['location'] == e['fits']
        assert r['file']['location'] == e['reference_fits']
        saved = q['provenance']['recipe_configuration']
        assert saved['path'] == e['config_path']
        assert saved['snapshot'] == e['config_text']
        assert saved['format'] == 'bias-recipe-toml/1'
        actual_cards = q['provenance']['fits_headers']
        assert len(actual_cards) == len(e['cards'])
        for actual, expected in zip(actual_cards, e['cards']):
            for key, value in expected.items():
                assert actual[key] == value, (key, actual, expected)
            if expected['value'] is not None:
                assert type(actual['value']) is type(expected['value'])
            if expected['status'] == 'missing':
                assert actual['fits_value'] is None

        if e['allow_clipped_additions']:
            current_settings = json.loads(q['provenance']['configuration']['snapshot'])
            old_settings = json.loads(r['provenance']['configuration']['snapshot'])
            expected_policy = {
                'BPM.ENCODING': {'type': 'string', 'value': 'binary'},
                'BPM.BAD_WHEN': {'type': 'string', 'value': 'zero'},
                'QC.RON.CLIP.ENABLED': {'type': 'int', 'value': 1},
                'QC.RON.CLIP.LOW': {'type': 'float64-bits', 'value': struct.pack('>d',5.0).hex()},
                'QC.RON.CLIP.HIGH': {'type': 'float64-bits', 'value': struct.pack('>d',5.0).hex()},
                'QC.RON.CLIP.MAX_ITERATIONS': {'type': 'int', 'value': 10},
            }
            assert not (old_settings.keys() & expected_policy.keys())
            assert current_settings.keys() == old_settings.keys() | expected_policy.keys()
            assert all(equal(current_settings[k],v) for k,v in old_settings.items())
            assert all(equal(current_settings[k],v) for k,v in expected_policy.items())

        detectors = q['characterization']['detectors']
        retained = {d['detector_id']: d
                    for d in r['characterization']['detectors']}
        assert [d['detector_id'] for d in detectors] == e['ids']
        assert [d['output_hdu'] for d in detectors] == list(range(1, len(detectors)+1))
        assert [d['configuration_detector'] for d in detectors] == e['indices']
        assert len(q['inputs']) == len(q['embedded_input_records']) == len(r['inputs'])
        assert [v['record_id'] for v in q['embedded_input_records']] == [
            v['record_id'] for v in r['embedded_input_records']]
        for index, detector in enumerate(detectors):
            identity = detector['detector_id']
            a = measurements(detector['measurements'], e['fits'])
            b = measurements(retained[identity]['measurements'], e['reference_fits'])
            if e['allow_clipped_additions']:
                assert not (b.keys() & set(e['allowed_measurements']))
                assert a.keys() == b.keys() | set(e['allowed_measurements']), identity
                def measured(name):
                    m = a[name]
                    assert m['status'] == 'measured', (identity,name,m['reason'])
                    return m['value']
                assert measured('bpm.encoding') == 1 and measured('bpm.bad_when_nonzero') == 0
                assert measured('bpm.good_value') == 1
                assert measured('ron_clip.sigma_low') == measured('ron_clip.sigma_high') == 5
                assert measured('ron_clip.max_iterations') == 10
                assert measured('ron_clip.converged') == 1
                assert 1 <= measured('ron_clip.iterations') <= 10
                assert measured('ron_clip.retained') >= 2
                assert math.isclose(measured('read_noise.clipped'), measured('ron_clip.stdev')/math.sqrt(2), rel_tol=1e-14)
                assert a['read_noise.clipped']['sources'] == a['read_noise']['sources']
                assert measured('ron_clip.retained') + measured('ron_clip.bpm_excluded') + measured('ron_clip.nonfinite_excluded') + measured('ron_clip.rejected_low') + measured('ron_clip.rejected_high') == measured('raw_difference.region_pixels')
                for name in ('ron_clip.sigma_low','ron_clip.sigma_high','ron_clip.max_iterations','bpm.encoding','bpm.bad_when_nonzero'):
                    assert a[name]['sources'] == ['<own-product>'], (identity,name)
                assert a['read_noise.clipped']['definition']['region']['clipping'] == 'median_centered_monotone_sigma'
            else:
                assert a.keys() == b.keys(), identity
            for name in b:
                assert equal(a[name], b[name]), (identity, name)
            verify(e['qc_headers'][index], q, detector)

        old_inputs = {v['record_id']: v for v in r['embedded_input_records']}
        for index, record in enumerate(q['embedded_input_records']):
            assert [d['detector_id'] for d in record['detectors']] == e['ids']
            previous = old_inputs[record['record_id']]
            assert record['file']['location'] == previous['file']['location']
            assert record['original_index'] == previous['original_index'] == index
            bindings = {d['detector_id']: d for d in previous['detectors']}
            for binding, configured in zip(record['detectors'], e['hdus']):
                other = bindings[binding['detector_id']]
                assert binding['source_hdu'] == configured[index if len(configured)>1 else 0]
                assert binding['source_hdu'] == other['source_hdu']
                assert equal(binding['measurements'], other['measurements'])
print('PASS: ASDF schema, exact recipe snapshot and selected FITS cards.')
print('PASS: product/input QC matches reference; complete FITS/ASDF mapping.')
'''


def signature(path):
    s = path.stat()
    return s.st_size, s.st_mtime_ns, s.st_ino


def qc(header, product):
    rows = [c for c in header.cards if c.keyword.startswith('ESO MPP QC ')]
    values = {c.keyword: c.value for c in rows}
    assert len(rows) == len(values), 'Duplicate QC keyword'
    assert values['ESO MPP QC ASDF'] == product.with_suffix('.asdf').name
    assert values['ESO MPP QC PROD'] == product.name
    for key in SELF_SOURCES:
        assert values[key] == product.name, (key, values[key], product.name)
    return values


def main():
    global ROOT
    p = argparse.ArgumentParser(description=__doc__)
    for key in ('product', 'reference', 'config', 'asdf-python'):
        p.add_argument('--'+key, type=Path, required=True)
    p.add_argument('--allow-clipped-ron-additions', action='store_true')
    p.add_argument('--source-root', type=Path, help='Matching source tree containing the schema and FITS mapping registry')
    a = p.parse_args()
    if a.source_root is not None:
        ROOT = a.source_root.resolve(strict=True)
    from astropy.io import fits
    # Keep invoked interpreter path: resolving a venv symlink loses its identity.
    a.asdf_python = a.asdf_python.absolute()
    assert a.asdf_python.is_file() and os.access(a.asdf_python, os.X_OK)
    current, reference, configuration = (v.absolute() for v in
                                        (a.product, a.reference, a.config))
    schema = ROOT/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json'
    paths = [current, reference, current.with_suffix('.asdf'),
             reference.with_suffix('.asdf'), configuration, schema]
    before = {str(v): signature(v) for v in paths}
    config_text = configuration.read_text()
    config = tomllib.loads(config_text)
    catalogue = {d['id']: d for d in config['detector']}
    assert len(catalogue) == len(config['detector']), 'Duplicate catalogue ID'
    cards, qc_headers = [], []

    def capture(header, keys, hdu, identity):
        for key in keys:
            key = key.removeprefix('HIERARCH ').upper()
            matches = [c for c in header.cards if c.keyword == key]
            assert len(matches) <= 1, ('Duplicate keyword', key)
            row = dict(keyword=key, hdu=hdu, detector_id=identity,
                       role='primary' if identity is None else 'detector',
                       source_file=str(current))
            if not matches:
                row.update(status='missing', value_type='missing',
                           value=None, comment=None, card=None)
            else:
                card = matches[0]
                value = card.value
                if value is fits.card.UNDEFINED:
                    value = None
                kind = ('undefined' if value is None else
                        'boolean' if isinstance(value, bool) else
                        'integer' if isinstance(value, int) else
                        'real' if isinstance(value, float) else 'string')
                row.update(status='present', value_type=kind, value=value,
                           comment=card.comment, card=card.image)
            cards.append(row)

    with fits.open(current, memmap=False) as new, fits.open(reference, memmap=False) as old:
        assert len(new) > 1
        assert new[0].header['PRODCATG'] == 'CALIB.MASTER_BIAS'
        ids = [h.header['EXTNAME'] for h in new[1:]]
        assert len(ids) == len(set(ids)), 'Duplicate product detector'
        lookup = {h.header['EXTNAME']: h for h in old[1:]}
        assert len(lookup) == len(old)-1, 'Duplicate reference detector'
        capture(new[0].header, config.get('provenance', {}).get('primary', []), 0, None)
        print('CCD             pixels       QC cards', flush=True)
        for index, identity in enumerate(ids, 1):
            assert identity in catalogue and identity in lookup, identity
            actual, retained = new[index], lookup[identity]
            assert actual.data.dtype == retained.data.dtype, identity
            assert actual.data.shape == retained.data.shape, identity
            assert actual.data.tobytes() == retained.data.tobytes(), identity
            actual_qc, retained_qc = qc(actual.header, current), qc(retained.header, reference)
            common_count, added_count = compare_headers(actual_qc, retained_qc, a.allow_clipped_ron_additions)
            qc_headers.append(actual_qc)
            capture(actual.header, config.get('provenance', {}).get('detector', []), index, identity)
            print(f'{identity:16} MATCH        {common_count} MATCH; {added_count} added cards', flush=True)
    expected = dict(allow_clipped_additions=a.allow_clipped_ron_additions,
                    allowed_measurements=sorted(CLIPPED_ADDITIONS), fits=str(current), reference_fits=str(reference),
                    config_path=str(configuration), config_text=config_text,
                    cards=cards, ids=ids, qc_headers=qc_headers, root=str(ROOT),
                    schema=str(schema),
                    indices=[catalogue[v]['configuration_detector'] for v in ids],
                    hdus=[catalogue[v]['hdus'] for v in ids])
    r = subprocess.run([str(a.asdf_python), '-B', '-c', ASDF_READER],
                       input=json.dumps(expected), text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1'),
                       timeout=120)
    assert before == {str(v): signature(v) for v in paths}, 'Checked files changed'
    assert r.returncode == 0, 'Independent ASDF verification failed'
    print('PASS: checked files unchanged; no raw input files read.')


if __name__ == '__main__':
    main()
