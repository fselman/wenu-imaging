"""Independent retained ASDF6 reader for synthetic native recipe acceptance."""
import argparse
import json
from pathlib import Path
import asdf
from bias_qc_fits_contract import verify as verify_fits_qc

p=argparse.ArgumentParser();p.add_argument('--file',type=Path,required=True)
p.add_argument('--schema',type=Path,required=True);p.add_argument('--expected',type=Path,required=True)
a=p.parse_args();expected=json.loads(a.expected.read_text());schema=a.schema.read_bytes();schema_id=json.loads(schema)['id']
# Local canonical schema registration; no network/schema installation (#249).
with asdf.config_context() as config:
    config.add_resource_mapping({schema_id:schema})
    with asdf.open(a.file,custom_schema=schema_id,lazy_load=False,strict_extension_check=True) as f:
        f.validate();q=f.tree['qc'];ds=q['characterization']['detectors']
        assert q['file']['location']==expected['fits']
        assert q['file']['filename']==Path(expected['fits']).name
        assert q['provenance']['log_path']==str(Path(expected['fits']).with_suffix('.log'))
        assert q['provenance']['product_sequence']==1 and q['record']['schema_version']=='2.0.0'
        assert len(q['inputs'])==len(q['embedded_input_records'])==4 and len(ds)==2
        assert [d['detector_id'] for d in ds]==['F1_CCD_A','F1_CCD_B']
        assert [d['configuration_detector'] for d in ds]==[0,1]
        assert [d['output_hdu'] for d in ds]==[1,2]
        assert [r['file']['location'] for r in q['embedded_input_records']]==expected['raw']
        assert [r['original_index'] for r in q['embedded_input_records']]==list(range(4))
        assert json.loads(q['provenance']['configuration']['snapshot'])==expected['configuration']
        for dindex,d in enumerate(ds):
            verify_fits_qc(expected['fits_qc_headers'][dindex],q,d)
            measurements={m['name']:m for m in d['measurements']}
            assert measurements['recipe.mad_requested']['value']==int(expected['measured'])
            assert measurements['recipe.ron_pair_requested']['value']==int(expected['measured'])
            assert measurements['variance']['value'] is None
            ref=expected['reference_qc'][dindex]
            for prefix in ('master','master_unmasked','raw_difference'):
                for suffix,field,flag,scale in (('mean','mean','level_available',1),('median','median','level_available',1),('stdev','stdev','stdev_available',1),('scaled_mad','mad','mad_available',1.4826)):
                    v=measurements[prefix+'.'+suffix]
                    if ref[prefix][flag]: assert v['value']==ref[prefix][field]*scale
                    else: assert v['value'] is None
            for name,field,flag in (('read_noise','stdev_adu','stdev_available'),('read_noise.mad','mad_adu','mad_available')):
                if ref['ron'][flag]: assert measurements[name]['value']==ref['ron'][field]
                else: assert measurements[name]['value'] is None
            if ref['ron']['pair_set']:
                assert measurements['read_noise']['sources']==['raw-000000','raw-000003']
            if ref['high_offset']['available']:
                assert measurements['pixels.hot']['value']==ref['high_offset']['count']
                if ref['high_offset']['count']:
                    assert list(zip(measurements['pixels.hot.x']['value'],measurements['pixels.hot.y']['value']))==[tuple(p) for p in ref['high_offset']['locations']]
            else: assert measurements['pixels.hot']['value'] is None
            for i,record in enumerate(q['embedded_input_records']):
                binding=record['detectors'][dindex]
                assert binding['detector_id']==d['detector_id']
                assert binding['source_hdu']==expected['hdus'][dindex][i]
                m={v['name']:v for v in binding['measurements']}
                ref=expected['reference_qc'][dindex]['inputs'][i]
                for stage,old in (('raw_active','raw_active'),('corrected_active','corrected_active'),('prescan','prescan'),('overscan','overscan')):
                    for suffix,field,flag,scale in (('mean','mean','level_available',1),('median','median','level_available',1),('stdev','stdev','stdev_available',1),('scaled_mad','mad','mad_available',1.4826)):
                        v=m[stage+'.'+suffix]
                        if ref[old][flag]: assert v['value']==ref[old][field]*scale
                        else: assert v['value'] is None
                assert m['scan_correction.median']['value']==ref['scan_correction']['median']
                assert m['scan_correction.stdev']['value']==ref['scan_correction']['stdev']
                used=q['inputs'][i]['participation_by_detector'][dindex]
                assert used['status']==('used' if ref['accepted'] else 'rejected')
                assert m['raw_active.mean']['sources']==[record['record_id']]
        if expected['measured']:
            assert len(q['calibrations'])==1 and q['calibrations'][0]['role']=='bpm'
            assert [(b['detector_id'],b['source_hdu']) for b in q['calibrations'][0]['detector_bindings']]==[('F1_CCD_A',1),('F1_CCD_B',2)]
        else: assert q['calibrations']==[]
print('PASS: native recipe ASDF schema, exact supplied QC and per-input detector bindings')
