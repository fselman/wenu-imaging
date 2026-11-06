"""Independent ASDF/schema and exact metadata checks; no Pycavi or FITS processing."""
import argparse
import json
import math
from pathlib import Path
import asdf

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('file',type=Path);p.add_argument('--schema',type=Path,required=True)
    p.add_argument('--integer-count',action='store_true');p.add_argument('--with-bpm',action='store_true');a=p.parse_args()
    # Independent ASDF/schema readback of a native-created product record.
    with asdf.open(a.file,custom_schema=a.schema.resolve().as_uri(),lazy_load=False,
                   strict_extension_check=True) as f:
        f.validate();q=f.tree['qc']
        assert q['record']['schema_version']=='2.0.0'
        assert q['provenance']['recipe_start']=='2026-11-06T15:00:00.123Z'
        assert q['provenance']['product_sequence']==1
        assert q['provenance']['producer']['source_revision']=='a'*40
        assert q['file']['filename']==a.file.with_suffix('.fits').name
        assert q['file']['sha256'] is None and q['file']['integrity']=='not_content_verified'
        assert json.loads(q['provenance']['configuration']['snapshot'])=={'MEF.NCHIPS':{'type':'int','value':2}}
        ds=q['characterization']['detectors'];assert [d['detector_id'] for d in ds]==['CCD-A','CCD-B']
        assert [d['configuration_detector'] for d in ds]==[7,2]
        assert [d['output_hdu'] for d in ds]==[1,2]
        assert [r['original_index'] for r in q['embedded_input_records']]==[10,20,30]
        assert [r['record_id'] for r in q['embedded_input_records']]==['raw-0000','raw-0001','raw-0002']
        # Exact scalar/profile values, explicit unavailable state and internal sources.
        for i,d in enumerate(ds):
            values={m['name']:m for m in d['measurements']}
            master=values['master.mean']['value']
            assert master==([12.0,23.75] if a.integer_count else [12.5,23.75])[i]
            if a.integer_count and i==0:assert type(master) is int
            assert values['ron.stdev_adu']['value']==[math.pi,math.e][i]
            assert values['ron.stdev_adu']['sources']==['raw-0000','raw-0002']
            assert values['variance']['value'] is None and values['variance']['status']=='unavailable'
            assert values['variance']['reason']=='legacy_variance_unavailable'
            profile=values['synthetic_profile']['value']
            assert profile==[-0.0,0.33333333333333331,123456.78901234567]
            assert math.copysign(1.,profile[0])==-1.
        # Input membership remains detector-specific, with per-file HDU mapping.
        records={r['record_id']:r for r in q['embedded_input_records']}
        for j,row in enumerate(q['inputs']):
            assert row['index']==j and row['original_index']==10+j*10
            assert row['record_id']==row['file_id']==f'raw-{j:04d}'
            decision={x['detector_id']:x for x in row['participation_by_detector']}
            assert decision['CCD-A']['status']==('rejected' if j==1 else 'used')
            assert decision['CCD-B']['status']=='used'
            for i,d in enumerate(records[row['record_id']]['detectors']):
                assert d['source_hdu']==(i+1 if j%2 else 2-i)
                m=d['measurements'][0]
                assert m['value']==[[125.5,126.25,127.125],[225.5,226.25,227.125]][i][j]
                assert m['sources']==[row['record_id']]
                assert m['definition']['stage']=='raw_before_correction'
        if a.with_bpm:
            assert len(q['calibrations'])==1
            c=q['calibrations'][0]
            assert c['record_id']=='bpm-0000' and c['role']=='bpm' and c['qc_location'] is None
            assert [(b['detector_id'],b['source_hdu']) for b in c['detector_bindings']]==[('CCD-A',5),('CCD-B',3)]
            for d in ds:
                region=d['measurements'][0]['definition']['region']
                assert region['detector_bpm']=='applied' and region['mask_record_id']==c['record_id']
        else:assert q['calibrations']==[]
        assert q['extensions']['input_reference_policy']=='embedded_record_id'
    print('PASS: native ASDF/schema, exact QC, embedded inputs and detector-specific membership')
