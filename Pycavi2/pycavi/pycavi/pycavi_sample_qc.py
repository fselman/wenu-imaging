"""Corrected singleton native transports -> common ASDF, without FITS reads or fitting."""
from copy import deepcopy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import runpy
try:
    from . import pycavi_qc as qc
    from . import pycavi_pair_qc as pair
except ImportError:
    import pycavi_qc as qc
    import pycavi_pair_qc as pair

ROOT=Path(__file__).resolve().parents[3]
COLUMNS='schema_version detector amplifier configuration_detector source_roi active_x active_y raw_x raw_y asset input_index hdu pair_id seconds admission_state signal_adu noise_state'.split()
TEXT={'detector','amplifier','source_roi','asset','pair_id','admission_state','noise_state'}
UNITS={k:('ADU' if k=='signal_adu' else 's' if k=='seconds' else 'pixel' if k in ('active_x','active_y','raw_x','raw_y') else None if k in TEXT else '1') for k in COLUMNS}
GUARDS={'shared_images','frozen_metadata','products','checkout','installed_files','native_source','qc_source','private_qc_runtime'}


def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':'))
def small(path):return pair.small(path)


def parse(data):
    text=data.decode('utf-8');qc.require(text.endswith('\n'),'Truncated sample table')
    reader=csv.reader(io.StringIO(text,newline=''),delimiter='\t',quoting=csv.QUOTE_NONE)
    qc.require(next(reader,None)==COLUMNS,'Unknown sample columns')
    rows=[]
    for values in reader:
        qc.require(len(values)==len(COLUMNS),'Malformed sample row');row={}
        for key,value in zip(COLUMNS,values):
            if key in TEXT:
                qc.require(bool(value),'Empty sample identity');row[key]=pair.unescape(value)
            elif key in ('seconds','signal_adu'):
                qc.require(bool(value) or key=='signal_adu','Missing exposure')
                row[key]=float(value) if value else None
                qc.require(row[key] is None or math.isfinite(row[key]),'Nonfinite sample')
            else:
                qc.require(re.fullmatch('[0-9]+',value) is not None,'Invalid sample integer');row[key]=int(value)
        qc.require(row['schema_version']==1 and row['seconds']>0 and row['noise_state']=='unavailable','Invalid schema/time/noise state')
        qc.require(row['admission_state'] in ('admitted','not_admitted') and
                   (row['signal_adu'] is not None)==(row['admission_state']=='admitted'),'Contradictory availability')
        rows.append(row)
    qc.require(bool(rows),'Empty sample table')
    return dict(schema_version=1,kind='corrected_samples',columns=COLUMNS,units=UNITS,rows=rows,
                native_tsv_text=text,native_tsv_sha256=sha(data))


def parse_population(data):
    columns='input_index outside_selected_sites bpm_excluded sample_excluded nonfinite saturated admitted'.split()
    text=data.decode('utf-8');reader=csv.reader(io.StringIO(text),delimiter='\t',quoting=csv.QUOTE_NONE)
    qc.require(text.endswith('\n') and next(reader,None)==columns,'Unknown population schema')
    rows=[]
    for values in reader:
        qc.require(len(values)==len(columns) and all(re.fullmatch('[0-9]+',v) is not None for v in values),'Invalid population row')
        rows.append(dict(zip(columns,map(int,values))))
    return dict(schema_version=1,columns=columns,rows=rows,native_tsv_text=text,native_tsv_sha256=sha(data))


def validate_grid(table,entry):
    points=entry['population'];frames=entry['selection']['flat'];rows=table['rows']
    qc.require(len(points)==5 and len(frames)==20 and len(rows)==100,'Require approved five-site20-frame population')
    for f,frame in enumerate(frames):
        times=set()
        for i,site in enumerate(points):
            r=rows[f*5+i]
            qc.require(r['detector']==entry['detector']==site['detector'] and r['amplifier']==site['amplifier']
                and r['configuration_detector']==site['configuration_detector']==entry['configuration_detector']
                and r['source_roi']==site['source_roi'] and [r['active_x'],r['active_y']]==site['active_pixel']
                and [r['raw_x'],r['raw_y']]==site['raw_pixel'],'Physical site mismatch')
            qc.require(r['asset']==frame['asset'] and r['input_index']==frame['index'] and r['hdu']==frame['hdu']
                and r['pair_id']==frame['pair'],'Original frame identity/order mismatch');times.add(r['seconds'])
        qc.require(len(times)==1,'Exposure differs within frame')


def admit_entry(batch,entry,result,report,frozen):
    directory=Path(entry['directory']);qc.require(directory==batch/entry['detector'].replace('ESO_CCD_#','CCD'),'Unexpected native directory')
    data={}
    for name in ('samples.tsv','population.tsv','configuration.json','command.complete'):
        path=directory/'native'/name;data[name]=small(path);frozen[str(path)]=data[name]
        qc.require(sha(data[name])==result['outputs'][str(path)]['sha256'],'Native output changed')
    qc.require(data['command.complete']==b'corrected_samples_complete_noise_unavailable\n','Invalid native completion marker')
    # Reuse the exact completed extraction's admission code; never execute main.
    controller=ROOT/'Pycavi2/tools/run_ocam_linearity_samples.py'
    qc.require(small(batch/'run.py')==small(controller),'Extraction controller differs from serializer admission source')
    functions=runpy.run_path(str(controller))
    counts=functions['admit_tables'](directory/'native',entry,entry['selection'],entry['population'],entry['active_pixels'])
    qc.require(all(counts[k]==result[k] for k in ('rows','admitted','not_admitted','noise_state')),'Native counts differ from completed receipt')
    table=parse(data['samples.tsv']);validate_grid(table,entry)
    master=Path(entry['master']['qc_product']);records=list(qc.traverse_records(master,qc_root=master.parent,max_records=12))
    qc.require(len(records)==12 and records[0].digest==entry['master']['recipe']['qc_record_digest'],'Master QC chain differs')
    # Every original master sidecar has a fingerprint in the extraction receipt.
    for path in master.parent.glob('*.asdf'):
        raw=small(path);qc.require(str(path) in report['metadata_inputs'] and sha(raw)==report['metadata_inputs'][str(path)]['sha256'],'Master sidecar changed')
        frozen[str(path)]=raw
    return dict(entry=entry,result=result,table=table,population=parse_population(data['population.tsv']),master_records=records,
                native_configuration=json.loads(data['configuration.json']))


def admit_batch(batch):
    batch=Path(batch).resolve(strict=True);frozen={}
    for path in (batch/'overall-execution.json',batch/'plan.json',batch/'run.py',batch/'singleton-sites/manifest.json'):
        frozen[str(path)]=small(path)
    report=json.loads(frozen[str(batch/'overall-execution.json')]);plan=json.loads(frozen[str(batch/'plan.json')])
    qc.require(report['status']=='complete_for_owner_inspection' and report['source_preservation'] is True
        and set(report['preservation'])==GUARDS and all(report['preservation'].values())
        and report['detectors_processed']==32 and report['rows']==3200,'Incomplete preserved sample batch')
    qc.require(len(report['inputs'])==53 and report['inputs']==report['after_inputs'] and set(plan['images'])==set(report['inputs']),'Recorded image preservation differs')
    qc.require(plan['controller_revision']==report['controller_revision'] and plan['native_revision']==report['native_revision'],'Revision mismatch')
    for path in (batch/'plan.json',batch/'run.py',batch/'singleton-sites/manifest.json'):
        qc.require(sha(frozen[str(path)])==report['metadata_inputs'][str(path)]['sha256'],'Frozen extraction metadata changed')
    ids={f'ESO_CCD_#{n}' for n in range(65,97)};entries=plan['entries'];results=report['results']
    qc.require(len(entries)==len(results)==32 and {e['detector'] for e in entries}=={e['detector'] for e in results}==ids,'Wrong detector cohort')
    indexed={r['detector']:r for r in results}
    states=[admit_entry(batch,e,indexed[e['detector']],report,frozen) for e in entries]
    return dict(batch=batch,report=report,plan=plan,states=states,frozen=frozen,sampling=json.loads(frozen[str(batch/'singleton-sites/manifest.json')])['sampling'])


def sources(row,entry):
    s=entry['selection'];m=entry['master']
    result = [dict(file_id=row['asset'],detector_id=row['detector'],hdu_index=row['hdu']),
              dict(file_id=m['product'],detector_id=row['detector'],hdu_index=m['hdu'])]
    if s['bpm'].get('encoding') != 'omitted':
        result.append(dict(file_id=s['bpm']['asset'],detector_id=row['detector'],hdu_index=s['bpm']['hdu']))
    return result



def signal_definition(row,index):
    return dict(stage='scan_corrected_master_bias_subtracted',method='native_singleton_sample_v1',
        region=dict(coordinates='FITS-1-based-pixels',active=[row['active_x'],row['active_y']],
                    raw=[row['raw_x'],row['raw_y']],source_roi=row['source_roi'],table_row=index,
                    original_input_index=row['input_index']),sample_count=1)


def table_from_record(record):
    tree=record.as_dict();table=tree['extensions']['corrected_sample_table'];entry=tree['extensions']['corrected_sample_origin']['entry']
    qc.require(canonical(parse(table['native_tsv_text'].encode('utf-8')))==canonical(table),'Typed sample/native transport mismatch')
    qc.require(tree['file']['sha256']==table['native_tsv_sha256'],'Product digest differs from transport')
    validate_grid(table,entry)
    population=tree['extensions']['corrected_sample_population']
    qc.require(canonical(parse_population(population['native_tsv_text'].encode()))==canonical(population),'Typed population/native mismatch')
    qc.require(len(population['rows'])==20,'Incomplete frame population')
    for f,p in enumerate(population['rows']):
        qc.require(p['input_index']==entry['selection']['flat'][f]['index'] and p['outside_selected_sites']==entry['active_pixels']-5
            and p['sample_excluded']==0 and p['admitted']==sum(r['signal_adu'] is not None for r in table['rows'][f*5:f*5+5])
            and sum(v for k,v in p.items() if k not in ('input_index','outside_selected_sites'))==5,'Population/sample mismatch')
    origin=tree['extensions']['corrected_sample_origin']
    qc.require(origin['noise_state']=='unavailable' and origin['covariance'] is None and origin['fit_state']=='not_performed'
        and origin['fit_interval'] is None and origin['correction_coefficients'] is None and origin['scientific_acceptance'] is False,'Unreviewed fit/noise state')
    qc.require(tree['file']['selectors']==[dict(detector_id=entry['detector'],table_name='corrected_samples')]
        and tree['provenance']['operation']=='sample.corrected_linearity'
        and tree['provenance']['producer']['source_revision']==origin['native_revision'],'Wrong product selector/operation/revision')
    metrics=tree['characterization']['detectors'][0]['measurements']
    qc.require(len(metrics)==len(table['rows']),'Unexpected sample measurement count')
    for i,(row,m) in enumerate(zip(table['rows'],metrics)):
        qc.require(m['name']==f'sample.{i}.signal_adu' and m['unit']=='ADU' and m['sources']==sources(row,entry),'Sample measurement origin/unit mismatch')
        if row['signal_adu'] is None:
            qc.require(m['value'] is None and m['status']=='unavailable' and m['reason']=='native_not_admitted'
                and m['definition']==dict(method=None,stage='scan_corrected_master_bias_subtracted',region=None,sample_count=None),'Missing sample became measured')
        else:
            qc.require(m['value']==row['signal_adu'] and m['status']=='measured' and m['definition']==signal_definition(row,i),'Sample measurement changed')
    return table


def publish_entry(state,directory,*,assessment_id,created_at,serializer_revision,origin):
    directory=Path(directory);qc.require(directory.is_dir() and not any(directory.iterdir()),'Fresh per-detector output required')
    e=state['entry'];table=state['table'];detector=e['detector'];slot=e['configuration_detector'];selection=e['selection']
    masterdir=directory/'master';masterdir.mkdir()
    for record in reversed(state['master_records']):
        destination=qc.write_record(record,masterdir,qc_root=directory)
        qc.require(qc.read_record(destination).digest==record.digest,'Master QC semantic copy changed')
    producer=dict(name='mefpp_sample_extract',version='singleton-native-v1',source_revision=origin['native_revision'])
    config_id='sha256:'+sha(canonical(state['native_configuration']).encode())
    inputsdir=directory/'inputs';inputsdir.mkdir();leaves=[]
    bindings=[dict(frame,role='raw_flat') for frame in selection['flat']]
    if selection['bpm'].get('encoding') != 'omitted':
        bindings.append(dict(selection['bpm'],role='bpm'))
    for i,binding in enumerate(bindings):
        builder=qc.QcRecipe(file=dict(id=binding['asset'],filename=Path(binding['path']).name,location=binding['path'],
            kind='raw' if binding['role']=='raw_flat' else 'product',sha256=origin['image_fingerprints'][binding['path']]['sha256'],
            observed_at=None,selectors=[dict(detector_id=detector,hdu_index=binding['hdu'],configuration_detector=slot)],
            context=dict(readout_id=selection['readout_id'],bin_x=selection['bin_x'],bin_y=selection['bin_y'])),
            assessment_id=f'{assessment_id}:input:{i}',created_at=created_at,producer=producer,
            operation='sample.corrected_linearity',configuration_id=config_id)
        builder.add_extension('corrected_sample_input',dict(binding=binding,scope='binding_from_completed_extraction_not_new_frame_reassessment',
            fingerprint=origin['image_fingerprints'][binding['path']],current_FITS_opened=False))
        leaf=builder.seal();destination=qc.write_record(leaf,inputsdir,qc_root=directory);leaves.append((leaf,destination.relative_to(directory).as_posix()))
    product=Path(e['directory'])/'native/samples.tsv'
    builder=qc.QcRecipe(file=dict(id=str(product),filename='samples.tsv',location=str(product),kind='product',
        sha256=table['native_tsv_sha256'],observed_at=None,selectors=[dict(detector_id=detector,table_name='corrected_samples')],
        context=dict(amplifier=e['population'][0]['amplifier'])),assessment_id=assessment_id+':product',created_at=created_at,
        producer=producer,operation='sample.corrected_linearity',configuration_id=config_id)
    for leaf,path in leaves:builder.add_input(leaf,qc_path=path,participation='used')
    master=state['master_records'][0]
    builder.add_input(master,qc_path='master/'+qc.qc_filename(master.as_dict()['file']['filename']),participation='used')
    for i,row in enumerate(table['rows']):
        if row['signal_adu'] is None:
            builder.add_unavailable(detector,name=f'sample.{i}.signal_adu',unit='ADU',stage='scan_corrected_master_bias_subtracted',
                reason='native_not_admitted',sources=sources(row,e))
        else:
            builder.add_measurement(detector,name=f'sample.{i}.signal_adu',value=row['signal_adu'],unit='ADU',sources=sources(row,e),definition=signal_definition(row,i))
    builder.add_extension('corrected_sample_table',table)
    builder.add_extension('corrected_sample_population',state['population'])
    # Keep the binding/sampling contract, not the large duplicated old recipe logs.
    entry={k:deepcopy(e[k]) for k in ('detector','configuration_detector','selection','population','active_pixels','directory')}
    entry['master']={k:deepcopy(e['master'][k]) for k in ('product','qc_product','hdu')}
    builder.add_extension('corrected_sample_origin',dict(entry=entry,native_configuration=state['native_configuration'],
        batch_receipt=origin['batch_receipt'],native_revision=origin['native_revision'],controller_revision=origin['controller_revision'],
        master_fingerprint=origin['image_fingerprints'][e['master']['product']],master_qc_digest=master.digest,
        original65_historical_FITS_hash_available=False if detector=='ESO_CCD_#65' else True,
        source_scope='fingerprints_recorded_at_completed_extraction_no_current_FITS_reread',
        sampling_policy=origin['sampling_policy'],serializer_revision=serializer_revision,noise_state='unavailable',covariance=None,fit_state='not_performed',fit_interval=None,
        correction_coefficients=None,scientific_acceptance=False))
    record=builder.seal();destination=qc.write_record(record,directory,qc_root=directory)
    stored=qc.read_record(destination);qc.require(stored.digest==record.digest,'Product roundtrip differs')
    qc.require(canonical(table_from_record(stored))==canonical(table),'Typed table roundtrip differs')
    count=len(list(qc.traverse_records(destination,qc_root=directory,max_records=34)))
    qc.require(count==len(bindings)+len(state['master_records'])+1,'Incomplete sample/master QC tree')
    return dict(path=str(destination),digest=stored.digest,rows=len(table['rows']),records=count)


def read_product(path):
    path=Path(path).resolve(strict=True)
    records=list(qc.traverse_records(path,qc_root=path.parent,max_records=34))
    tree = records[0].as_dict()
    origin = tree['extensions']['corrected_sample_origin']
    masters = [r for r in records if r.digest == origin['master_qc_digest']]
    qc.require(len(masters)==1 and len(records)==1+len(tree['inputs'])+len(masters[0].as_dict()['inputs']),
               'Incomplete corrected sample QC graph')
    return table_from_record(records[0])


def publish_batch(batch,directory,*,assessment_id,created_at,serializer_revision):
    qc.timestamp(created_at);qc.require(re.fullmatch('[0-9a-f]{40}',serializer_revision) is not None,'Exact serializer revision required')
    directory=Path(directory).resolve(strict=True);qc.require(directory.is_dir() and not any(directory.iterdir()),'Fresh output directory required')
    state=admit_batch(batch);qc._asdf();products=[]
    origin=dict(native_revision=state['report']['native_revision'],controller_revision=state['report']['controller_revision'],
        image_fingerprints=state['report']['inputs'],sampling_policy={k:v for k,v in state['sampling'].items() if k!='sites'},batch_receipt=dict(path=str(state['batch']/'overall-execution.json'),
        sha256=sha(state['frozen'][str(state['batch']/'overall-execution.json')]),preservation=state['report']['preservation']))
    for child in state['states']:
        name=child['entry']['detector'].replace('ESO_CCD_#','CCD');target=directory/name;target.mkdir()
        print('Persisting corrected samples:',name,flush=True)
        products.append(publish_entry(child,target,assessment_id=assessment_id+':'+name,created_at=created_at,
                                      serializer_revision=serializer_revision,origin=origin))
    qc.require(all(small(p)==value for p,value in state['frozen'].items()),'Saved native/master evidence changed during persistence')
    return dict(status='complete',products=products,rows=sum(p['rows'] for p in products),records=sum(p['records'] for p in products),
        raw_FITS_opened=False,pixels_remeasured=False,fitted=False,roundtrip_exact=True,metadata_preservation=True,
        inputs_sha256={p:sha(v) for p,v in state['frozen'].items()},native_revision=origin['native_revision'],serializer_revision=serializer_revision)
