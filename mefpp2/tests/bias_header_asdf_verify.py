"""Independent retained ASDF reader: selected final-product header provenance."""
import argparse,json
from pathlib import Path
import asdf
p=argparse.ArgumentParser()
p.add_argument('--file',type=Path,required=True)
p.add_argument('--schema',type=Path,required=True)
p.add_argument('--expected',type=Path,required=True)
a=p.parse_args();expected=json.loads(a.expected.read_text())
schema=a.schema.read_bytes()
with asdf.config_context() as config:
    config.add_resource_mapping({json.loads(schema)['id']:schema})
    with asdf.open(a.file,custom_schema=json.loads(schema)['id'],lazy_load=False,strict_extension_check=True) as f:
        f.validate();q=f.tree['qc']
        assert q['provenance']['producer']['source_revision']==expected['revision']
        c=q['provenance']['recipe_configuration']
        assert c['path']==expected['recipe_path']
        assert c['snapshot']==expected['recipe_text'] and c['format']=='bias-recipe-toml/1'
        cards=q['provenance']['fits_headers']
        assert len(cards)==len(expected['cards'])
        for actual,wanted in zip(cards,expected['cards']):
            for key,value in wanted.items():
                assert actual[key]==value,(key,actual,wanted)
            if wanted['value'] is not None:
                assert type(actual['value']) is type(wanted['value']),(actual,wanted)
            if wanted['status']=='missing':
                assert actual['fits_value'] is None and actual['card'] is None
        ds=q['characterization']['detectors']
        assert [d['detector_id'] for d in ds]==expected['detectors']
        assert [d['output_hdu'] for d in ds]==list(range(1,len(ds)+1))
        assert [d['configuration_detector'] for d in ds]==expected['configuration_indices']
        for record in q['embedded_input_records']:
            assert [d['source_hdu'] for d in record['detectors']]==expected['source_hdus']
        assert all(m['name'] not in ('JD','MJD') for d in ds for m in d['measurements'])
print('PASS: selected header cards, typed values, missing states, recipe snapshot and source/output mapping')
