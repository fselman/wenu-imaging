"""Independent ASDF reader: complete mapped QC and median policy provenance."""
import argparse,json
from pathlib import Path
import asdf
import numpy as np
from bias_qc_fits_contract import verify
p=argparse.ArgumentParser();p.add_argument('--expected',type=Path,required=True);p.add_argument('--schema',type=Path,required=True)
a=p.parse_args();e=json.loads(a.expected.read_text());schema=a.schema.read_bytes();schema_id=json.loads(schema)['id'];records={}
# Read into ordinary JSON-compatible objects without relying on open ASDF handles.
def clean(v):
    if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [clean(x) for x in v]
    if isinstance(v,np.ndarray):return v.tolist()
    return v
with asdf.config_context() as c:
    c.add_resource_mapping({schema_id:schema})
    for label,path in e['products'].items():
        with asdf.open(Path(path).with_suffix('.asdf'),custom_schema=schema_id,lazy_load=False,strict_extension_check=True) as f:
            f.validate();q=f.tree['qc'];records[label]=clean(q)
            assert q['provenance']['producer']['source_revision']==e['revision']
            for i,d in enumerate(q['characterization']['detectors']):
                assert d['median_even_handling']==('lower' if label=='lower' else 'average')
                verify(e['headers'][label][i],q,d)
                if label in e['master']:
                    m={v['name']:v for v in d['measurements']}
                    for key,wanted in e['master'][label][i].items():
                        assert np.isclose(m['master.'+key]['value'],wanted,rtol=1e-12,atol=1e-12),(label,i,key,m['master.'+key]['value'],wanted)
                assert all(v['status']=='used' for r in q['inputs'] for v in r['participation_by_detector'])
base=records['default']
for label in ('average','lower'):
    other=records[label]
    assert base['inputs']==other['inputs']
    assert base['embedded_input_records']==other['embedded_input_records']
    for d,b in zip(base['characterization']['detectors'],other['characterization']['detectors']):
        bmap={m['name']:m for m in b['measurements']}
        for m in d['measurements']:
            if m['name'].startswith(('raw_difference.','read_noise','ron_clip.')):assert m==bmap[m['name']]
print('PASS: schema, mapped FITS/ASDF QC, actual median mode, exact input QC and raw-pair RON across modes')
