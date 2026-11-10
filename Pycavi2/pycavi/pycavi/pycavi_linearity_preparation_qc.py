"""Native corrected ROI transports -> shared QC ASDF, without pixel math.

The recipe publishes only after its external source-preservation checks. This
adapter freezes the existing direct-site/master graph and stores native values,
configuration, populations and ordered correction traces. No fit/plot backend.
"""
from copy import deepcopy
import csv
import io
import json
import math
from pathlib import Path
import shutil
try:
    from . import pycavi_qc as qc, pycavi_pair_qc as pair, pycavi_sample_qc as sample
    from . import pycavi_linearity_recipe as recipe
except ImportError:
    import pycavi_qc as qc
    import pycavi_pair_qc as pair
    import pycavi_sample_qc as sample
    import pycavi_linearity_recipe as recipe

STAGE='scan_corrected_master_bias_subtracted'
FIELDS='schema_version pair_row valid_pixels first_mean_adu second_mean_adu first_spatial_variance_adu2 second_spatial_variance_adu2 difference_mean_adu difference_variance_adu2 half_difference_variance_adu2'.split()
TRACES='role input_index master_accepted raw_row correction_adu'.split()


def table(data, columns):
    text=data.decode('utf-8');qc.require(text.endswith('\n'),'Truncated native table')
    r=csv.DictReader(io.StringIO(text),delimiter='\t',quoting=csv.QUOTE_NONE)
    qc.require(r.fieldnames==columns,'Unknown native table columns')
    rows=list(r);qc.require(all(None not in row and None not in row.values() for row in rows),'Malformed native table')
    return rows


def natural(value):
    qc.require(type(value) is str and value.isascii() and value.isdigit(),'Invalid native count/index')
    return int(value)


def corrected(data, raw):
    output=[]
    for i,row in enumerate(table(data,FIELDS)):
        v={k:natural(row[k]) for k in FIELDS[:3]}
        qc.require(v['schema_version']==1 and v['pair_row']==i and i<len(raw),'Wrong corrected row identity')
        qc.require(v['valid_pixels']==raw[i]['valid_pixels'],'Corrected/raw population differs')
        for key in FIELDS[3:]:
            v[key]=float(row[key]) if row[key] else None
            qc.require(v[key] is None or math.isfinite(v[key]),'Nonfinite corrected value')
            needed=v['valid_pixels']>=(2 if 'variance' in key else 1)
            qc.require((v[key] is not None)==needed,'Incorrect native availability')
            if v[key] is not None and 'variance' in key:qc.require(v[key]>=0,'Negative variance')
        output.append(v)
    qc.require(len(output)==len(raw),'Incomplete corrected table')
    return output


def traces(data, frames, height, role):
    expected={r['index']:r for r in frames};groups={i:[] for i in expected}
    qc.require(len(expected)==len(frames),'Duplicate trace frame identity')
    for row in table(data,TRACES):
        index=natural(row['input_index']);y=natural(row['raw_row'])
        qc.require(row['role']==role and index in groups,'Unexpected trace frame')
        decision=int(row['master_accepted']);value=float(row['correction_adu'])
        qc.require(decision==(-1 if role=='flat' else expected[index]['accepted']) and math.isfinite(value),
                   'Trace membership/value mismatch')
        qc.require(y==len(groups[index])+1 and y<=height,'Trace row order/coverage differs')
        groups[index].append(value)
    qc.require(all(len(v)==height for v in groups.values()),'Incomplete scan trace')
    return [dict(role=role,input_index=r['index'],asset=r['asset'],hdu=r['hdu'],
                 master_accepted=None if role=='flat' else r['accepted'],
                 raw_row_start=1,correction_adu=groups[r['index']]) for r in frames]


def collect(native, resolved, selection, biases, expected_samples, master_snapshot, *, master_reference, transports=None, input_bpm_policy="archived", bpm_response_limits=None):
    """Read native transport only. No raw FITS or source remeasurement."""
    native=Path(native);frozen={};texts={}
    def read(path):
        name=str(path.relative_to(native))
        if transports is None:data=pair.small(path)
        else:
            qc.require(name in transports,'Missing frozen native transport')
            data=transports[name]['text'].encode('utf-8')
            qc.require(pair.sha(data)==transports[name]['sha256'],'Frozen native transport changed')
        frozen[str(path.resolve())]=pair.sha(data)
        texts[name]=dict(text=data.decode('utf-8'),sha256=pair.sha(data))
        return data
    qc.require(read(native/'command.complete')==b'linearity_preparation_complete_noise_unavailable\n','Missing native completion')
    master_rows=table(read(native/'master-reference.tsv'),['path','hdu','asset'])
    qc.require(len(master_rows)==1 and pair.unescape(master_rows[0]['path'])==master_reference['product'] and
               natural(master_rows[0]['hdu'])==master_reference['hdu'],'Native master path/HDU differs from frozen dependency')
    snapshot=json.loads(read(native/'configuration.json'))
    qc.require(snapshot==recipe.bpm_configuration_snapshot(master_snapshot, bpm_response_limits),'Native configuration differs from verified master/TOML transport')
    recipe.native_configuration(resolved, snapshot)
    detector=next(d for d in resolved['detectors'] if d['detector_id']==selection['detector'])
    height=detector['raw_size'][1];groups=traces(read(native/'bias-traces.tsv'),biases,height,'bias')
    paths=sorted(native.glob('pair-*')) if transports is None else [native/f'pair-{i:04d}' for i in range(len(selection['flat'])//2)]
    qc.require([p.name for p in paths]==[f'pair-{i:04d}' for i in range(len(selection['flat'])//2)],'Incomplete native pair set')
    rows=[];samples=[];exposures=[];raw_bias=[];seen=set()
    lookup={r['asset']:r for r in selection['flat']};known_rois={r['id'] for r in detector['rois']}
    for group in paths:
        raw=pair.parse_table(read(group/'pairs.tsv'),'pairs')['rows']
        c=corrected(read(group/'corrected.tsv'),raw)
        qc.require(len(raw)==len(known_rois) and {r['roi'] for r in raw}==known_rois,'ROI coverage differs')
        members=[]
        for prefix in ('first','second'):
            row=raw[0];r=lookup[row[prefix+'_asset']]
            qc.require(r['index']==row[prefix+'_input_index'] and r['hdu']==row[prefix+'_hdu'] and
                       r['pair']==row['pair_id'],'Original source binding differs')
            qc.require(r['index'] not in seen,'Duplicate pair member');seen.add(r['index']);members.append(r)
        groups+=traces(read(group/'flat-traces.tsv'),members,height,'flat')
        samples+=sample.parse(read(group/'samples.tsv'))['rows']
        # Preserve counters as evidence without pretending singleton and pair
        # populations are identical. Their selections have different definitions.
        population=sample.parse_population(read(group/'population.tsv'))
        bias=pair.parse_table(read(group/'bias-ron.tsv'),'bias-ron')
        raw_bias.append(dict(pair_directory=group.name,table=bias,population=population))
        for index,(r,v) in enumerate(zip(raw,c)):
            qc.require(r['detector']==detector['detector_id'] and r['amplifier']==detector['amplifier_id'] and
                       r['configuration_detector']==detector['configuration_detector'],'Native detector mismatch')
            qc.require(all(r[k]==raw[0][k] for k in ('first_asset','second_asset','pair_id','first_seconds','second_seconds')),
                       'ROI pair identities/times differ')
            rows.append(dict(raw=r,corrected=v))
            for prefix,member in [('first',1),('second',2)]:
                exposures.append(dict(detector=r['detector'],amplifier=r['amplifier'],roi=r['roi'],
                    input_index=r[prefix+'_input_index'],asset=r[prefix+'_asset'],hdu=r[prefix+'_hdu'],
                    pair_id=r['pair_id'],pair_member=member,exposure_seconds=r[prefix+'_seconds'],
                    signal_adu=v[prefix+'_mean_adu'],spatial_variance_adu2=v[prefix+'_spatial_variance_adu2'],
                    valid_pixels=v['valid_pixels'],measurement_stage=STAGE,
                    source_pair_directory=group.name,source_pair_row=index))
    qc.require(len(seen)==len(selection['flat']),'Flat coverage differs')
    def key(r):return (r['asset'],r['input_index'],r['hdu'],r['source_roi'],r['active_x'],r['active_y'])
    expected=expected_samples['rows'];saved={key(r):r for r in samples}
    qc.require(len(saved)==len(samples)==len(expected),'Duplicate/incomplete direct-site replay')
    qc.require(input_bpm_policy in ('archived', 'omitted'), 'Unknown input BPM comparison policy')
    replayed=deepcopy(expected)
    comparison=None
    if input_bpm_policy=='archived':
        qc.require(all(saved.get(key(r))==r for r in expected),'Corrected direct-site replay differs from preserved archive')
    else:
        qc.require(selection['bpm']['encoding']=='omitted' and set(saved)=={key(r) for r in expected},
                   'Omitted-mask direct-site identity cohort differs')
        newly_admitted=0
        for old in expected:
            current=saved[key(old)]
            if old['signal_adu'] is not None:
                qc.require(current==old, 'Previously admitted direct-site value changed')
            else:
                qc.require(set(current)==set(old) and all(current[k]==old[k] for k in old
                           if k not in ('signal_adu', 'admission_state')),
                           'Omitted-mask direct-site metadata changed')
                newly_admitted+=current['signal_adu'] is not None
        replayed=[deepcopy(saved[key(r)]) for r in expected]
        comparison=dict(input_bpm_policy='omitted', exact_replay=replayed==expected,
            previously_admitted=sum(r['signal_adu'] is not None for r in expected),
            newly_admitted=newly_admitted, historical_archive_changed=False)

    # Stable acquisition/ROI order, independent of the native pair processing order.
    order={r['index']:i for i,r in enumerate(selection['flat'])};roi_order={r['id']:i for i,r in enumerate(detector['rois'])}
    exposures.sort(key=lambda r:(order[r['input_index']],roi_order[r['roi']]))
    if transports is None:
        qc.require(all(pair.sha(pair.small(Path(p)))==digest for p,digest in frozen.items()),'Native evidence changed during reading')
    else:qc.require(set(texts)==set(transports),'Unexpected frozen native transport')
    result=dict(schema_version=1,measurement_stage=STAGE,detector=detector['detector_id'],
        rows=rows,exposure_rows=exposures,scan_traces=groups,direct_site_replay=replayed,
        raw_bias_diagnostics=raw_bias,native_sha256=frozen,native_transports=texts,noise_state='unavailable',
        covariance=None,fit_state='not_performed',scientific_acceptance=False,
        units=dict(signal='ADU',variance='ADU2',trace='ADU',exposure='s',coordinates='FITS-1-based-inclusive'))
    if comparison is not None:
        result['historical_sample_comparison']=comparison
    return result


def graph(path):
    path=Path(path).resolve(strict=True);root=path.parent;files={}
    def visit(current):
        qc.require(current.is_relative_to(root) and not current.is_symlink(),'Source QC escapes archive')
        if current in files:return
        files[current]=pair.sha(pair.small(current));r=qc.read_record(current)
        for member in r.as_dict()['inputs']:visit((current.parent/member['qc']['path']).resolve(strict=True))
    list(qc.traverse_records(path,qc_root=root));visit(path);return files


def publish(native, source_samples, directory, *, resolved, selection, biases, master_snapshot,
            assessment_id,created_at,source_revision,dependency_evidence=None):
    """Publish one detector through the existing common owner/writer/reader."""
    directory=Path(directory).resolve(strict=True);qc.require(not any(directory.iterdir()),'Fresh empty ASDF directory required')
    source_samples=Path(source_samples).resolve(strict=True);frozen=graph(source_samples)
    source=qc.read_record(source_samples);expected=sample.table_from_record(source)
    origin=source.as_dict()['extensions']['corrected_sample_origin']
    qc.require(origin['native_configuration']==master_snapshot,'Preserved sample/master configuration differs')
    qc.require(origin['entry']['selection']['flat']==selection['flat'] and
               all(origin['entry']['selection']['bpm'][k]==selection['bpm'][k] for k in ('path','hdu','asset')),
               'Preserved sample source cohort differs')
    records=[qc.read_record(p) for p in frozen]
    masters=[r for r in records if r.digest==origin['master_qc_digest']]
    qc.require(len(masters)==1,'Missing preserved master QC')
    by_id={r.as_dict()['file']['id']:r for r in records}
    raw_members={m['file_id']:m for m in masters[0].as_dict()['inputs']
                 if by_id[m['file_id']].as_dict()['file']['kind']=='raw'}
    qc.require({b['path'] for b in biases}==set(raw_members) and len(biases)==len(raw_members),'Bias dependency cohort differs')
    for b in biases:
        m=raw_members[b['path']];leaf=by_id[b['path']].as_dict()
        qc.require((m['participation']['status']=='used')==bool(b['accepted']) and
                   leaf['file']['selectors'][0]['hdu_index']==b['hdu'],'Bias membership/HDU differs from preserved master')
    value=collect(native,resolved,selection,biases,expected,master_snapshot,master_reference=origin['entry']['master'])
    target=directory/'inputs';target.mkdir()
    for p,digest in frozen.items():
        out=target/p.relative_to(source_samples.parent);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
        qc.require(pair.sha(pair.small(out))==digest,'Frozen graph copy changed')
    producer=dict(name='wenu-imaging.linearity.prepare',version='1',source_revision=source_revision)
    transport=directory/'linearity-preparation.tsv'
    columns=['detector','roi','input_index','asset','hdu','pair_id','pair_member','exposure_seconds',
             'signal_adu','spatial_variance_adu2','valid_pixels']
    stream=io.StringIO(newline='');writer=csv.writer(stream,delimiter='\t',lineterminator='\n')
    writer.writerow(columns)
    for row in value['exposure_rows']:writer.writerow([row[k] for k in columns])
    payload=stream.getvalue().encode('utf-8')
    with transport.open('xb') as output:output.write(payload)
    configuration_id='sha256:'+pair.sha(recipe.canonical(resolved).encode())
    builder=qc.QcRecipe(file=dict(id='linearity-preparation:'+assessment_id,filename='linearity-preparation.tsv',
        location=str(transport),kind='product',sha256=pair.sha(payload),observed_at=None,
        selectors=[dict(detector_id=value['detector'],table_name='linearity_preparation')],context=dict(stage=STAGE)),
        assessment_id=assessment_id,created_at=created_at,producer=producer,
        operation='linearity.prepare',configuration_id=configuration_id)
    builder.add_input(source,qc_path='inputs/'+source_samples.name,participation='used')
    # Common measurements name immediate input identities. Reuse the frozen
    # leaves explicitly while preserving the complete existing sample graph.
    flat_ids={r['asset'] for r in selection['flat']}
    for p in frozen:
        record=qc.read_record(p)
        if record.as_dict()['file']['id'] in flat_ids:
            builder.add_input(record,qc_path='inputs/'+p.relative_to(source_samples.parent).as_posix(),participation='used')
    for i,row in enumerate(value['exposure_rows']):
        sources=[dict(file_id=row['asset'],detector_id=row['detector'],hdu_index=row['hdu'])]
        definition=dict(stage=STAGE,method='native_corrected_common_population',
            region=dict(roi=row['roi'],source_pair_directory=row['source_pair_directory'],source_pair_row=row['source_pair_row']),
            sample_count=row['valid_pixels'])
        for field,unit in [('signal_adu','ADU'),('spatial_variance_adu2','ADU2')]:
            if row[field] is None:builder.add_unavailable(row['detector'],name=f'exposure.{i}.{field}',unit=unit,
                stage=STAGE,reason='native_population_insufficient',sources=sources)
            else:builder.add_measurement(row['detector'],name=f'exposure.{i}.{field}',value=row[field],unit=unit,
                definition=definition,sources=sources)
    builder.add_extension('linearity_preparation',value)
    builder.add_extension('linearity_configuration',resolved)
    builder.add_extension('linearity_preparation_context',dict(native_directory=str(Path(native).resolve()),
        selection=selection,biases=biases,master_snapshot=master_snapshot,
        exposure_transport=dict(text=payload.decode('utf-8'),sha256=pair.sha(payload))))
    builder.add_extension('linearity_dependency_evidence',dependency_evidence or {})
    builder.add_extension('linearity_source_graph',dict(record_digest=source.digest,
        sha256={str(p.relative_to(source_samples.parent)):v for p,v in frozen.items()}))
    record=builder.seal();path=qc.write_record(record,directory,qc_root=directory)
    qc.require(read_product(path)==value,'Preparation ASDF roundtrip differs')
    qc.require(all(pair.sha(pair.small(p))==v for p,v in frozen.items()),'Source sample/master graph changed')
    return dict(path=str(path),digest=record.digest,detector=value['detector'],
        pairs=len(value['rows']),exposures=len(value['exposure_rows']),sites=len(value['direct_site_replay']),
        trace_frames=len(value['scan_traces']),noise_state='unavailable')


def read_product(path, *, expected_digest=None):
    """Read saved measurements only; no estimator, native command or raw FITS."""
    path=Path(path).resolve(strict=True);record=qc.read_record(path);tree=record.as_dict()
    qc.require(expected_digest is None or record.digest==expected_digest,'Unexpected preparation record digest')
    records=list(qc.traverse_records(path,qc_root=path.parent));v=tree['extensions']['linearity_preparation']
    qc.require(tree['provenance']['operation']=='linearity.prepare' and v['measurement_stage']==STAGE and
        v['noise_state']=='unavailable' and v['covariance'] is None and v['fit_state']=='not_performed', 'Invalid preparation/model state')
    context=tree['extensions']['linearity_preparation_context'];transport=context['exposure_transport']
    qc.require(tree['file']['sha256']==transport['sha256']==pair.sha(transport['text'].encode()),'Preparation transport digest differs')
    resolved=tree['extensions']['linearity_configuration']
    qc.require(tree['provenance']['configuration_id']=='sha256:'+pair.sha(recipe.canonical(resolved).encode()),'Configuration digest differs')
    source=[r for r in records if r.digest==tree['extensions']['linearity_source_graph']['record_digest']]
    qc.require(len(source)==1,'Missing direct-site/master source graph')
    expected=sample.table_from_record(source[0]);qc.require(v['direct_site_replay']==expected['rows'],'Stored direct-site replay differs')
    source_origin=source[0].as_dict()['extensions']['corrected_sample_origin']
    decoded=collect(context['native_directory'],resolved,context['selection'],context['biases'],expected,
                    context['master_snapshot'],master_reference=source_origin['entry']['master'],transports=v['native_transports'])
    qc.require(recipe.canonical(decoded)==recipe.canonical(v),'Stored/transport preparation values differ')
    for name,digest in tree['extensions']['linearity_source_graph']['sha256'].items():
        source_path=(path.parent/'inputs'/name).resolve(strict=True)
        qc.require(source_path.is_relative_to((path.parent/'inputs').resolve()) and
                   pair.sha(pair.small(source_path))==digest,'Frozen sample/master evidence changed')
    metrics=tree['characterization']['detectors'][0]['measurements']
    qc.require(len(metrics)==2*len(v['exposure_rows']),'Incomplete common measurements')
    for i,row in enumerate(v['exposure_rows']):
        for offset,field in enumerate(('signal_adu','spatial_variance_adu2')):
            qc.require(metrics[2*i+offset]['name']==f'exposure.{i}.{field}' and metrics[2*i+offset]['value']==row[field],
                       'Common/saved preparation values differ')
    return v


def modelling_inputs(path, *, require_noise=True):
    value=read_product(path)
    if require_noise:raise ValueError('Preparation is complete but a reviewed absolute noise/covariance model is unavailable')
    return dict(pixel_observations=deepcopy(value['direct_site_replay']),
                roi_diagnostics=deepcopy(value['exposure_rows']),noise_state='unavailable',covariance=None)
