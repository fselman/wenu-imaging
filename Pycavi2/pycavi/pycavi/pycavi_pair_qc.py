"""Native raw-pair tables -> shared ASDF QC. No pixel reads or estimators (#233)."""
from __future__ import annotations
from copy import deepcopy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import tomllib
try:
    from . import pycavi_qc as qc
except ImportError:
    import pycavi_qc as qc

PAIR_COLUMNS = ['schema_version', 'detector', 'amplifier', 'configuration_detector', 'roi', 'active_xmin', 'active_xmax', 'active_ymin', 'active_ymax', 'raw_xmin', 'raw_xmax', 'raw_ymin', 'raw_ymax', 'bias1_asset', 'bias1_hdu', 'bias2_asset', 'bias2_hdu', 'bpm_supplied', 'bpm_binary_supplied', 'reject_bits', 'saturation_raw_adu', 'pair_time_tolerance_s', 'pair_id', 'first_asset', 'first_input_index', 'first_hdu', 'first_seconds', 'second_asset', 'second_input_index', 'second_hdu', 'second_seconds', 'region_pixels', 'bpm_excluded', 'nonfinite_excluded', 'saturated', 'valid_pixels', 'levels_available', 'flat1_mean_adu', 'flat2_mean_adu', 'bias1_mean_adu', 'bias2_mean_adu', 'signal_available', 'signal1_adu', 'signal2_adu', 'mean_signal_adu', 'variance_available', 'flat_difference_variance_adu2', 'bias_difference_variance_adu2', 'single_flat_variance_adu2', 'single_bias_variance_adu2', 'mismatch_available', 'fractional_mismatch', 'matched_ron_available', 'matched_ron_adu', 'matched_ron_mad_available', 'matched_ron_mad_adu', 'gain_state', 'point_gain_e_per_adu']
BIAS_COLUMNS = ['schema_version', 'detector', 'amplifier', 'configuration_detector', 'roi', 'active_xmin', 'active_xmax', 'active_ymin', 'active_ymax', 'raw_xmin', 'raw_xmax', 'raw_ymin', 'raw_ymax', 'bias1_asset', 'bias1_hdu', 'bias2_asset', 'bias2_hdu', 'bpm_supplied', 'bpm_binary_supplied', 'reject_bits', 'saturation_raw_adu', 'pair_time_tolerance_s', 'region_pixels', 'bpm_excluded', 'nonfinite_excluded', 'saturated', 'valid_pixels', 'level_available', 'difference_mean_adu', 'difference_median_adu', 'stdev_available', 'difference_stdev_adu', 'mad_available', 'difference_mad_adu', 'ron_available', 'ron_adu', 'ron_mad_available', 'ron_mad_adu']
TEXT = {'detector','amplifier','roi','bias1_asset','bias2_asset','pair_id','first_asset','second_asset','gain_state'}
PAIR_OPTIONAL = {
    **{k:'levels_available' for k in ('flat1_mean_adu','flat2_mean_adu','bias1_mean_adu','bias2_mean_adu')},
    **{k:'signal_available' for k in ('signal1_adu','signal2_adu','mean_signal_adu')},
    **{k:'variance_available' for k in ('flat_difference_variance_adu2','bias_difference_variance_adu2',
                                     'single_flat_variance_adu2','single_bias_variance_adu2')},
    'fractional_mismatch':'mismatch_available','matched_ron_adu':'matched_ron_available',
    'matched_ron_mad_adu':'matched_ron_mad_available','point_gain_e_per_adu':'gain_state',
}
BIAS_OPTIONAL = {'difference_mean_adu':'level_available','difference_median_adu':'level_available',
                 'difference_stdev_adu':'stdev_available','difference_mad_adu':'mad_available',
                 'ron_adu':'ron_available','ron_mad_adu':'ron_mad_available'}
FLOAT = {'saturation_raw_adu','pair_time_tolerance_s','first_seconds','second_seconds',
         *PAIR_OPTIONAL,*BIAS_OPTIONAL}
COUNTS = ('region_pixels','bpm_excluded','nonfinite_excluded','saturated','valid_pixels')
STATES = {'arithmetic_available','too_few_pixels','nonpositive_signal','nonpositive_variance','bias_evidence_unavailable'}
KINDS = {'pairs':(PAIR_COLUMNS,PAIR_OPTIONAL),'bias-ron':(BIAS_COLUMNS,BIAS_OPTIONAL)}


def canonical(value):
    return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def small(path):
    path=Path(path)
    qc.require(not path.is_symlink() and path.is_file() and path.stat().st_size<=qc.MAX_RECORD_BYTES,'Missing/oversized metadata: '+str(path))
    return path.read_bytes()


def unescape(value):
    # Decode only the documented native exporter escapes. No Python eval/codecs.
    result=[]; i=0
    while i<len(value):
        if value[i]!='\\': result.append(value[i]);i+=1;continue
        i+=1;qc.require(i<len(value),'Truncated native text escape')
        char=value[i];i+=1
        if char in {'\\','t','n','r'}:result.append({'\\':'\\','t':'\t','n':'\n','r':'\r'}[char])
        else:
            qc.require(char=='x' and re.fullmatch('[0-9a-fA-F]{2}',value[i:i+2]) is not None,
                       'Unknown native text escape')
            result.append(chr(int(value[i:i+2],16)));i+=2
    return ''.join(result)


def unit(column):
    if column.endswith('_adu2'):return 'ADU2'
    if column.endswith('_adu') and column!='point_gain_e_per_adu':return 'ADU'
    if column=='point_gain_e_per_adu':return 'electron/ADU'
    if column.endswith('_seconds') or column=='pair_time_tolerance_s':return 's'
    if column in COUNTS:return 'count'
    if column=='fractional_mismatch':return '1'
    if column in TEXT:return None
    if '_xmin' in column or '_xmax' in column or '_ymin' in column or '_ymax' in column:return 'pixel'
    return '1'


def parse_table(data,kind):
    columns,optional=KINDS[kind]
    text=data.decode('utf-8')
    qc.require(text.endswith('\n'),'Truncated native TSV')
    reader=csv.reader(io.StringIO(text,newline=''),delimiter='\t',quoting=csv.QUOTE_NONE)
    qc.require(next(reader,None)==columns,'Unknown/reordered native TSV schema')
    rows=[]
    for fields in reader:
        qc.require(len(fields)==len(columns),'Malformed native TSV row')
        raw=dict(zip(columns,fields))
        row={}
        for key,value in zip(columns,fields):
            if key in TEXT:
                qc.require(bool(value) or (key in ('bias1_asset','bias2_asset') and raw.get('gain_state')=='bias_evidence_unavailable'),'Empty native identity/state');row[key]=unescape(value)
            elif key in FLOAT:
                qc.require(bool(value) or key in optional,'Missing required numeric value')
                row[key]=float(value) if value else None
                qc.require(row[key] is None or math.isfinite(row[key]),'Nonfinite native numeric value')
            else:
                qc.require(re.fullmatch('[0-9]+',value) is not None,'Invalid native integer')
                row[key]=int(value)
        qc.require(row['schema_version']==1,'Unknown native table version')
        for key in columns:
            if key.endswith('_available') or key in ('bpm_supplied','bpm_binary_supplied'):
                qc.require(row[key] in (0,1),'Invalid native availability/mask flag')
        if kind=='pairs':qc.require(row['gain_state'] in STATES,'Unknown native gain state')
        for key,flag in optional.items():
            available=row[flag]=='arithmetic_available' if flag=='gain_state' else row[flag]==1
            qc.require((row[key] is not None)==available,'Native value/availability mismatch: '+key)
        qc.require(row['region_pixels']>0 and sum(row[k] for k in COUNTS[1:])==row['region_pixels'],
                   'Native population accounting mismatch')
        for prefix in ('active','raw'):
            bounds=[row[prefix+'_'+k] for k in ('xmin','xmax','ymin','ymax')]
            qc.require(1<=bounds[0]<=bounds[1] and 1<=bounds[2]<=bounds[3] and
                       (bounds[1]-bounds[0]+1)*(bounds[3]-bounds[2]+1)==row['region_pixels'],
                       'Invalid native ROI bounds')
        qc.require(row['saturation_raw_adu']>0 and row['pair_time_tolerance_s']>=0,'Invalid native settings')
        rows.append(row)
    qc.require(bool(rows),'Empty native table')
    return dict(table_schema_version=1,kind=kind,columns=columns,units={k:unit(k) for k in columns},
                rows=rows,native_tsv_text=text,native_tsv_sha256=sha(data),
                stage='raw_uncorrected',correction='none',gain_acceptance='arithmetic_only_not_instrument_acceptance',
                uncertainty=dict(status='unavailable',reason='native_raw_pair_pass_does_not_estimate_uncertainty_or_covariance'))


def table_from_record(record):
    tree=record.as_dict()
    value=tree['extensions']['raw_pair_table']
    qc.require(value['kind'] in KINDS,'Unknown saved table kind')
    decoded=parse_table(value['native_tsv_text'].encode('utf-8'),value['kind'])
    qc.require(canonical(decoded)==canonical(value),'Saved typed values/units differ from native text')
    qc.require(tree['file']['sha256']==value['native_tsv_sha256'] and
               tree['file']['selectors']==[dict(detector_id=value['rows'][0]['detector'],table_name=value['kind'])],
               'Saved table product identity differs')
    measurements={m['name']:m for m in tree['characterization']['detectors'][0]['measurements']}
    for index,row in enumerate(value['rows']):
        fields=list(KINDS[value['kind']][1])+list(COUNTS)
        for field in fields:
            measurement=measurements[f"{value['kind']}.{index}.{field}"]
            qc.require(canonical(measurement['value'])==canonical(row[field]) and measurement['unit']==unit(field)
                       and measurement['status']==('unavailable' if row[field] is None else 'measured'),
                       'Common measurement differs from saved native table')
    return value


def admit(run):
    """Freeze only small completed-run evidence; never open any observation file."""
    run=Path(run).resolve(strict=True)
    paths=[run/'execution.json',run/'selection.toml',run/'selected-rois.toml',run/'plan.tsv',
           *(run/'native'/name for name in ('pairs.tsv','bias-ron.tsv','configuration.json','command.complete'))]
    frozen={str(p):small(p) for p in paths}
    receipt=json.loads(frozen[str(run/'execution.json')])
    qc.require(receipt['status']=='complete_for_owner_inspection' and receipt['mode']=='raw_pair_measurements'
               and receipt['native_exit_status']==0
               and receipt['source_preservation'] is True and receipt['detectors_processed']==1,
               'Require completed preserved native run')
    qc.require(frozen[str(run/'native/command.complete')]==b'raw_pair_tables_complete\n','Invalid native marker')
    outputs={r['path']:r for r in receipt['outputs']}
    qc.require(len(outputs)==len(receipt['outputs']),'Duplicate output fingerprint')
    for p in paths[4:]:
        qc.require(str(p) in outputs and outputs[str(p)]['sha256']==sha(frozen[str(p)])
                   and outputs[str(p)]['size']==len(frozen[str(p)]),'Native output fingerprint mismatch')
    fingerprints={r['path']:r for r in receipt['inputs']}
    qc.require(len(fingerprints)==len(receipt['inputs']),'Duplicate frozen source fingerprint')
    qc.require(any(r['sha256']==sha(frozen[str(run/'selection.toml')]) for r in receipt['inputs']),
               'Selection is not the frozen measurement input')
    selection=tomllib.loads(frozen[str(run/'selection.toml')].decode('utf-8'))
    rois=tomllib.loads(frozen[str(run/'selected-rois.toml')].decode('utf-8'))['roi']
    tables={kind:parse_table(frozen[str(run/'native'/(kind+'.tsv'))],kind) for kind in KINDS}
    qc.require(re.fullmatch('[0-9a-f]{40}',receipt['source_revision']) is not None,'Invalid native revision')
    detector=receipt['detector'];amplifier=receipt['amplifier']
    qc.require(selection['detector']==detector and len(rois)==receipt['roi_count'],'Selected detector/ROI mismatch')
    roi_by_id={r['id']:r for r in rois}
    qc.require(len(roi_by_id)==len(rois) and all(r['detector']==detector and r['amplifier']==amplifier for r in rois),
               'Duplicate/mismatched ROI configuration')
    refs=[dict(r,role='flat') for r in selection['flat']]+[dict(r,role='bias') for r in selection['bias']]
    if selection['bpm']['encoding']!='omitted':refs.append(dict(selection['bpm'],role='bpm'))
    assets={r['asset']:r for r in refs}
    qc.require(len(assets)==len(refs) and len(selection['bias'])==2,'Aliased source assets')
    for ref in refs:
        qc.require(Path(ref['path']).is_absolute() and ref['path'] in fingerprints,'Missing frozen input identity')
        qc.require(re.fullmatch('[0-9a-f]{64}',fingerprints[ref['path']]['sha256']) is not None,'Invalid frozen input hash')
    groups={}
    for ref in selection['flat']:groups.setdefault(ref['pair'],[]).append(ref)
    qc.require(all(len(v)==2 for v in groups.values()),'Pair membership mismatch')
    expected=[(pair,r['id']) for pair in groups for r in rois]
    qc.require([(r['pair_id'],r['roi']) for r in tables['pairs']['rows']]==expected,'Pair/ROI acquisition order mismatch')
    qc.require([r['roi'] for r in tables['bias-ron']['rows']]==list(roi_by_id),'Bias ROI order mismatch')
    slot=tables['pairs']['rows'][0]['configuration_detector']
    bias_rois={r['roi']:r for r in tables['bias-ron']['rows']}
    for kind,table in tables.items():
        qc.require(receipt['output_rows'][kind+'.tsv']==len(table['rows']),'Output row receipt mismatch')
        for row in table['rows']:
            qc.require(row['detector']==detector and row['amplifier']==amplifier
                       and row['configuration_detector']==slot,'Table detector/output/slot mismatch')
            qc.require(all(row['raw_'+k]==bias_rois[row['roi']]['raw_'+k]
                           for k in ('xmin','xmax','ymin','ymax')),'Inconsistent raw ROI coordinates')
            r=roi_by_id[row['roi']]
            qc.require([row['active_'+k] for k in ('xmin','xmax','ymin','ymax')]==[r[k] for k in ('xmin','xmax','ymin','ymax')],
                       'Table ROI differs from selection')
            qc.require(row['saturation_raw_adu']==selection['raw_saturation_adu'] and
                       row['pair_time_tolerance_s']==selection['pair_time_tolerance_s'] and
                       row['reject_bits']==selection['reject_bits'] and
                       row['bpm_supplied']==int(selection['bpm']['encoding']!='omitted') and
                       row['bpm_binary_supplied']==int(selection['bpm']['encoding']=='binary'),'Native settings differ')
            for i,ref in enumerate(selection['bias'],1):
                qc.require(row[f'bias{i}_asset']==ref['asset'] and row[f'bias{i}_hdu']==ref['hdu'],'Bias binding mismatch')
            if kind=='pairs':
                for prefix,ref in zip(('first','second'),groups[row['pair_id']]):
                    qc.require(row[prefix+'_asset']==ref['asset'] and row[prefix+'_hdu']==ref['hdu'] and
                               row[prefix+'_input_index']==ref['index'] and row[prefix+'_seconds']>0,'Flat binding mismatch')
                qc.require(abs(row['first_seconds']-row['second_seconds'])<=selection['pair_time_tolerance_s'],
                           'Pair exposure tolerance differs')
    # Retain optional explicit structural-copy lineage from the outer run. No source FITS opened.
    lineage=run.parent/'lineage.json'
    if lineage.is_file():
        frozen[str(lineage)]=small(lineage);origin=json.loads(frozen[str(lineage)])
        qc.require(origin['native_revision']==receipt['source_revision'] and
                   origin['derived_selection_sha256']==sha(frozen[str(run/'selection.toml')]) and
                   origin['derived_bpm_sha256']==fingerprints[selection['bpm']['path']]['sha256'],
                   'Structural BPM lineage differs from completed native inputs')
    return dict(run=run,receipt=receipt,selection=selection,rois=rois,refs=refs,assets=assets,
                fingerprints=fingerprints,tables=tables,frozen=frozen,
                configuration=json.loads(frozen[str(run/'native/configuration.json')]))


def publish(run,directory,*,assessment_id,created_at,serializer_revision):
    qc.timestamp(created_at)
    qc.require(re.fullmatch('[0-9a-f]{40}',serializer_revision) is not None,'Exact serializer revision required')
    state=admit(run);run=state['run'];directory=Path(directory).resolve(strict=True)
    qc.require(directory.is_dir() and not any(directory.iterdir()),'Fresh empty QC directory required')
    qc._asdf()
    detector=state['receipt']['detector'];slot=state['tables']['pairs']['rows'][0]['configuration_detector']
    producer=dict(name='mefpp_pair_measure',version='raw-pair-plan-v1',source_revision=state['receipt']['source_revision'])
    config_id='sha256:'+sha(state['frozen'][str(run/'native/configuration.json')])
    records=[];leaves={}
    # No per-frame statistical claim is invented from pair statistics.
    for index,ref in enumerate(state['refs']):
        builder=qc.QcRecipe(file=dict(id=ref['asset'],filename=Path(ref['path']).name,location=ref['path'],
            kind='product' if ref['role']=='bpm' else 'raw',sha256=state['fingerprints'][ref['path']]['sha256'],
            observed_at=None,selectors=[dict(detector_id=detector,hdu_index=ref['hdu'],configuration_detector=slot)],
            context=dict(readout_id=state['selection']['readout_id'],bin_x=state['selection']['bin_x'],bin_y=state['selection']['bin_y'])),
            assessment_id=f'{assessment_id}:input:{index}',created_at=created_at,producer=producer,
            operation='measure.raw_pairs',configuration_id=config_id)
        builder.add_extension('raw_pair_input',dict(binding=ref,frozen_fingerprint=state['fingerprints'][ref['path']],
            scope='selected_binding_from_completed_measurement_not_individual_frame_reassessment'))
        leaf=builder.seal();leaves[ref['asset']]=leaf;records.append(leaf)
    for kind,table in state['tables'].items():
        product=run/'native'/(kind+'.tsv')
        builder=qc.QcRecipe(file=dict(id=str(product),filename=product.name,location=str(product),kind='product',
            sha256=table['native_tsv_sha256'],observed_at=None,
            selectors=[dict(detector_id=detector,table_name=kind)],context=dict(amplifier=state['receipt']['amplifier'])),
            assessment_id=f'{assessment_id}:product:{kind}',created_at=created_at,producer=producer,
            operation='measure.raw_pairs' if kind=='pairs' else 'measure.raw_bias_ron',configuration_id=config_id)
        used=state['refs'] if kind=='pairs' else [r for r in state['refs'] if r['role']!='flat']
        for ref in used:
            leaf=leaves[ref['asset']]
            builder.add_input(leaf,qc_path=qc.qc_filename(leaf.as_dict()['file']['filename']),participation='used')
        optional=KINDS[kind][1]
        for index,row in enumerate(table['rows']):
            sources=[dict(file_id=r['asset'],detector_id=detector,hdu_index=r['hdu']) for r in used
                     if r['role']!='flat' or r['asset'] in (row.get('first_asset'),row.get('second_asset'))]
            region=dict(coordinates='FITS-1-based-inclusive',roi=row['roi'],table_row=index,
                retained_active=[row['active_'+k] for k in ('xmin','xmax','ymin','ymax')],
                raw=[row['raw_'+k] for k in ('xmin','xmax','ymin','ymax')],correction='none')
            metrics=list(optional)+list(COUNTS)
            for field in metrics:
                name=f'{kind}.{index}.{field}'
                if row[field] is None:
                    reason=row['gain_state'] if field=='point_gain_e_per_adu' else 'native_availability_flag_zero'
                    builder.add_unavailable(detector,name=name,unit=unit(field),stage='raw_uncorrected',reason=reason,sources=sources)
                else:
                    builder.add_measurement(detector,name=name,value=row[field],unit=unit(field),sources=sources,
                        definition=dict(stage='raw_uncorrected',method='native_tsv_v1:'+field,region=region,
                                        sample_count=row['region_pixels'] if field in COUNTS else row['valid_pixels']))
        builder.add_extension('raw_pair_table',table)
        builder.add_extension('raw_pair_provenance',dict(
            native_receipt=state['receipt'],native_configuration=state['configuration'],selection=state['selection'],
            selected_rois=state['rois'],plan_text=state['frozen'][str(run/'plan.tsv')].decode('utf-8'),
            metadata_sha256={p:sha(data) for p,data in state['frozen'].items()},
            structural_bpm_lineage=json.loads(state['frozen'][str(run.parent/'lineage.json')]) if str(run.parent/'lineage.json') in state['frozen'] else None,
            serializer=dict(name='pycavi_pair_qc',source_revision=serializer_revision),
            frozen_input_scope='recorded_at_native_measurement_no_current_FITS_reread'))
        records.append(builder.seal())
    names=[qc.qc_filename(r.as_dict()['file']['filename']) for r in records]
    qc.require(len(set(names))==len(names),'Input/product QC basename collision')
    for record in records:
        destination=qc.write_record(record,directory,qc_root=directory)
        qc.require(qc.read_record(destination).digest==record.digest,'Common ASDF roundtrip differs')
    products={}
    for record in records[-2:]:
        destination=directory/qc.qc_filename(record.as_dict()['file']['filename'])
        stored=qc.read_record(destination);value=table_from_record(stored)
        qc.require(value['native_tsv_text'].encode('utf-8')==state['frozen'][str(run/'native'/(value['kind']+'.tsv'))],
                   'Full-precision native TSV roundtrip differs')
        qc.require(len(list(qc.traverse_records(destination,qc_root=directory)))==len(stored.as_dict()['inputs'])+1,
                   'Frozen QC tree incomplete')
        products[value['kind']]=dict(path=str(destination),digest=stored.digest,rows=len(value['rows']))
    qc.require(all(small(Path(p))==data for p,data in state['frozen'].items()),'Completed-run metadata changed')
    return dict(status='complete',products=products,records=len(records),roundtrip_exact=True,
                metadata_preservation=True,raw_FITS_opened=False,pixels_remeasured=False,
                serializer_revision=serializer_revision,native_revision=state['receipt']['source_revision'])
