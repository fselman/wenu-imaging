"""Independent ASDF reader: no native estimator or writer implementation import."""
import argparse
import json
import math
from pathlib import Path
import asdf
from bias_qc_fits_contract import verify

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--file', type=Path, required=True)
p.add_argument('--schema', type=Path, required=True)
p.add_argument('--expected', type=Path, required=True)
a = p.parse_args()
e = json.loads(a.expected.read_text())
schema = a.schema.read_bytes()
with asdf.config_context() as config:
    config.add_resource_mapping({json.loads(schema)['id']: schema})
    with asdf.open(a.file, custom_schema=json.loads(schema)['id'], lazy_load=False,
                   strict_extension_check=True) as f:
        f.validate()
        q = f.tree['qc']
        assert q['provenance']['producer']['source_revision'] == e['revision']
        recipe = q['provenance']['recipe_configuration']
        assert recipe['path'] == e['recipe_path'] and recipe['snapshot'] == e['recipe_snapshot']
        snapshot = json.loads(q['provenance']['configuration']['snapshot'])
        for k, v in e['policy'].items():
            assert snapshot[k] == v, (k, snapshot.get(k), v)
        assert q['extensions'].get('bpm_registry') == e['registry']
        for d, wanted in zip(q['characterization']['detectors'], e['detectors']):
            assert d['detector_id'] == wanted['id']
            verify(wanted['header'], q, d)
            ms = {m['name']: m for m in d['measurements']}
            if not e['enabled']:
                assert 'read_noise.clipped' not in ms
                continue
            for k, value in wanted['clipped'].items():
                actual = ms[k]
                assert actual['status'] == 'measured', (k, actual)
                assert math.isclose(actual['value'], value, rel_tol=2e-12, abs_tol=1e-12), (k, actual['value'], value)
            assert ms['read_noise.clipped']['definition']['region']['clipping'] == 'median_centered_monotone_sigma'
            assert ms['read_noise']['definition']['region']['clipping'] == 'none'
            assert ms['read_noise.clipped']['sources'] == ms['read_noise']['sources']
        assert len(q['characterization']['detectors']) == len(e['detectors'])
print('PASS: independent clipped oracle, native ASDF schema/policy, exact FITS mapping and raw-pair provenance')
