"""Save/read same-exposure ROI ratios through unchanged common ASDF QC."""
import csv
from pathlib import Path
import shutil
import pycavi_residual_qc as residual
from pycavi_roi_ratio import compute
qc=residual.qc;pairs=residual.pairs
UNITS=dict(exposure_seconds='s',signal_adu='ADU',numerator_signal_adu='ADU',denominator_signal_adu='ADU',
    raw_ratio='1',normalized_ratio='1',ratio_departure_percent='percent',reference_ratio='1')


def publish(source,directory,*,assessment_id,created_at,source_revision,minimum=15000.,maximum=35000.,
            numerator_suffix='near_readout',denominator_suffix='parallel_far'):
    source=Path(source).resolve(strict=True);directory=Path(directory).resolve(strict=True)
    qc.require(not any(directory.iterdir()),'Fresh empty ratio directory required')
    qc.timestamp(created_at)
    qc.require(residual.re.fullmatch('[0-9a-f]{40}',source_revision) is not None,'Exact ratio revision required')
    frozen=residual.source_graph(source);record=qc.read_record(source)
    saved=residual.read_product(source)
    samples=saved['rows'];detector=samples[0]['detector']
    def roi(suffix):
        choices={r['roi'] for r in samples if r['roi'].endswith('.'+suffix)}
        qc.require(len(choices)==1,'Missing/ambiguous ratio ROI: '+suffix)
        return choices.pop()
    value=compute(samples,numerator_roi=roi(numerator_suffix),denominator_roi=roi(denominator_suffix),
                  minimum=minimum,maximum=maximum)
    imported=directory/'inputs';imported.mkdir()
    for name in frozen:
        path=Path(name);target=imported/path.relative_to(source.parent)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
    transport=directory/'roi-ratio.tsv'
    columns=[k for k in value['rows'][0] if k not in ('numerator','denominator')]
    with transport.open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns,delimiter='\t',extrasaction='ignore')
        writer.writeheader();writer.writerows(value['rows'])
    value.update(schema_version=1,units=UNITS,source_residual_digest=record.digest,
        source_residual_sha256=frozen[str(source)],source_pair_digest=saved['source_pair_digest'],
        measurement_stage=saved['measurement_stage'],transport_sha256=pairs.sha(transport.read_bytes()))
    builder=qc.QcRecipe(file=dict(id=str(transport),filename=transport.name,location=str(transport),kind='product',
        sha256=value['transport_sha256'],observed_at=None,
        selectors=[dict(detector_id=detector,table_name='roi_ratio')],context=dict(amplifier=samples[0]['amplifier'])),
        assessment_id=assessment_id,created_at=created_at,
        producer=dict(name='pycavi_roi_ratio',version='1',source_revision=source_revision),
        operation='diagnostic.same_exposure_roi_ratio',
        configuration_id='sha256:'+pairs.sha(pairs.canonical(value['configuration']).encode()))
    builder.add_input(record,qc_path='inputs/'+source.name,participation='used')
    builder.add_extension('roi_ratio_diagnostic',value)
    result=builder.seal();path=qc.write_record(result,directory,qc_root=directory)
    qc.require(pairs.canonical(read_product(path))==pairs.canonical(value),'Ratio ASDF roundtrip differs')
    residual.unchanged(frozen)
    return dict(path=str(path),digest=result.digest,detector=detector,rows=len(value['rows']),
                inputs_sha256=frozen,roundtrip_exact=True)


def read_product(path,*,expected_digest=None,expected_residual_digest=None):
    path=Path(path).resolve(strict=True);record=qc.read_record(path);tree=record.as_dict()
    list(qc.traverse_records(path,qc_root=path.parent))
    qc.require(expected_digest is None or record.digest==expected_digest,'Ratio product digest changed')
    value=tree['extensions'].get('roi_ratio_diagnostic')
    qc.require(value and value['schema_version']==1 and value['units']==UNITS,'Unknown ratio schema/units')
    qc.require(len(tree['inputs'])==1,'Ratio requires one frozen residual source')
    source=path.parent/tree['inputs'][0]['qc']['path'];source_record=qc.read_record(source)
    qc.require(source_record.digest==value['source_residual_digest'] and
        (expected_residual_digest is None or source_record.digest==expected_residual_digest),'Ratio source digest differs')
    qc.require(pairs.sha(pairs.small(source))==value['source_residual_sha256'],'Ratio source bytes changed')
    original=residual.read_product(source)
    qc.require(value['source_pair_digest']==original['source_pair_digest'] and
        value['measurement_stage']==original['measurement_stage'],'Ratio source stage/lineage differs')
    qc.require(tree['provenance']['configuration_id']=='sha256:'+pairs.sha(pairs.canonical(value['configuration']).encode()),'Ratio configuration differs')
    from pycavi_roi_ratio import KEYS
    originals={tuple(r[k] for k in KEYS)+(r['roi'],):r for r in original['rows']}
    config=value['configuration'];norm=value['normalization']
    qc.require(config['method']=='same_exposure_ratio_v1' and
        config['reference_method']=='arithmetic_mean_of_individual_ratios' and
        config['numerator_roi']!=config['denominator_roi'] and
        config['uncertainty_state']=='unavailable' and config['physical_correction_fitted'] is False,
        'Unknown ratio method/configuration')
    lo,hi=config['reference_signal_min_adu'],config['reference_signal_max_adu']
    qc.require(residual.finite(lo) and residual.finite(hi) and lo<=hi,'Invalid ratio interval')
    seen=set();members=[]
    for row in value['rows']:
        key=tuple(row[k] for k in KEYS);qc.require(key not in seen,'Duplicate stored ratio exposure');seen.add(key)
        for label in ('numerator','denominator'):
            sample=row[label];expected=originals.get(key+(sample['roi'],))
            qc.require(expected is not None and pairs.canonical(sample)==pairs.canonical(expected),'Ratio sample/source identity differs')
        n,d=row['numerator'],row['denominator']
        qc.require(n['roi']==config['numerator_roi'] and d['roi']==config['denominator_roi'] and
            all(row[k]==n[k]==d[k] for k in (*KEYS,'detector','amplifier','exposure_seconds')) and
            row['signal_adu']==row['numerator_signal_adu']==n['signal_adu'] and
            row['denominator_signal_adu']==d['signal_adu'] and row['roi']=='ratio',
            'Ratio row metadata/ROI/source values differ')
        qc.require(type(row['reference_included']) is bool,'Ratio membership must be boolean')
        if row['reference_included']:members.append({k:row[k] for k in KEYS})
        qc.require(all(row[k] is None or residual.finite(row[k]) for k in
            ('raw_ratio','normalized_ratio','ratio_departure_percent')),'Invalid saved ratio values')
    qc.require(len(seen)==len([r for r in original['rows'] if r['roi']==value['configuration']['numerator_roi']]),'Ratio exposure coverage differs')
    qc.require(norm['members']==members and norm['count']==len(members),'Ratio reference membership differs')
    qc.require(norm['reference_ratio'] is None or
        (residual.finite(norm['reference_ratio']) and norm['reference_ratio']>0),'Invalid ratio reference')
    return value
