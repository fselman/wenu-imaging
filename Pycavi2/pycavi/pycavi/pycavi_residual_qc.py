"""Persist/read diagnostic curves through the common QC ASDF lifecycle."""
from copy import deepcopy
import csv
import re
from pathlib import Path
import shutil
import pycavi_pair_qc as pairs
from pycavi_pair_display import exposure_rows
from pycavi_residuals import analyze, finite

qc=pairs.qc
UNITS=dict(exposure_seconds='s',signal_adu='ADU',line_prediction_adu='ADU',
    residual_adu='ADU',residual_percent='percent',count_rate_adu_per_s='ADU/s',
    intercept_adu='ADU',slope_adu_per_s='ADU/s',time_center_s='s',signal_center_adu='ADU',
    exposure_range_s='s',signal_range_adu='ADU',n='count',fit_included='1')


def source_graph(path):
    path=Path(path).resolve(strict=True);root=path.parent;paths={}
    def visit(current):
        qc.require(current.is_relative_to(root) and not current.is_symlink(),'Source QC escapes its root')
        name=str(current)
        if name in paths:return
        paths[name]=pairs.sha(pairs.small(current))
        record=qc.read_record(current)
        for member in record.as_dict()['inputs']:
            visit((current.parent/member['qc']['path']).resolve(strict=True))
    list(qc.traverse_records(path,qc_root=root));visit(path)
    return paths


def unchanged(inputs):
    qc.require(all(pairs.sha(pairs.small(Path(p)))==digest for p,digest in inputs.items()),
               'Diagnostic input changed')


def publish(path,directory,*,assessment_id,created_at,source_revision,minimum=None,maximum=None):
    path=Path(path).resolve(strict=True);directory=Path(directory).resolve(strict=True)
    qc.require(not any(directory.iterdir()),'Fresh empty diagnostic directory required')
    qc.timestamp(created_at)
    qc.require(re.fullmatch('[0-9a-f]{40}',source_revision) is not None,'Exact computation revision required')
    frozen=source_graph(path);original=qc.read_record(path)
    table=pairs.table_from_record(original)
    qc.require(table['kind']=='pairs','Pair-ASDF source required')
    samples=exposure_rows(table['rows'])
    detector=samples[0]['detector']
    qc.require(all(r['detector']==detector for r in samples),'Mixed diagnostic detectors')
    result=analyze(samples,minimum=minimum,maximum=maximum)
    # Preserve the existing local QC graph and its original relative references.
    imported=directory/'inputs';imported.mkdir()
    for name in frozen:
        source=Path(name);target=imported/source.relative_to(path.parent)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    transport=directory/'line-residuals.tsv'
    with transport.open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(result['rows'][0]),delimiter='\t')
        writer.writeheader();writer.writerows(result['rows'])
    extension=dict(schema_version=1,**result,units=UNITS,
        source_pair_digest=original.digest,source_pair_sha256=frozen[str(path)],
        measurement_stage='raw_pair_bias_subtracted_without_overscan',
        transport_sha256=pairs.sha(transport.read_bytes()))
    builder=qc.QcRecipe(file=dict(id=str(transport),filename=transport.name,location=str(transport),
        kind='product',sha256=extension['transport_sha256'],observed_at=None,
        selectors=[dict(detector_id=detector,table_name='line_residuals')],
        context=dict(amplifier=samples[0]['amplifier'])),
        assessment_id=assessment_id,created_at=created_at,
        producer=dict(name='pycavi_residuals',version='1',source_revision=source_revision),
        operation='diagnostic.unweighted_line_residuals',
        configuration_id='sha256:'+pairs.sha(pairs.canonical(result['configuration']).encode('utf-8')))
    builder.add_input(original,qc_path='inputs/'+path.name,participation='used')
    builder.add_extension('line_residual_diagnostic',extension)
    record=builder.seal();destination=qc.write_record(record,directory,qc_root=directory)
    saved=read_product(destination,expected_source_digest=original.digest)
    qc.require(pairs.canonical(saved)==pairs.canonical(extension),'Diagnostic ASDF roundtrip differs')
    unchanged(frozen)
    return dict(path=str(destination),digest=record.digest,detector=detector,
        rows=len(samples),fits=len(result['fits']),inputs_sha256=frozen,roundtrip_exact=True)


def read_product(path,*,expected_source_digest=None,expected_digest=None):
    """Validate saved values and lineage without repeating any fit or residual arithmetic."""
    path=Path(path).resolve(strict=True);record=qc.read_record(path)
    list(qc.traverse_records(path,qc_root=path.parent))
    tree=record.as_dict()
    qc.require(expected_digest is None or record.digest==expected_digest,'Diagnostic record digest changed')
    value=tree['extensions'].get('line_residual_diagnostic')
    qc.require(value and value['schema_version']==1 and value['units']==UNITS,'Unknown diagnostic schema/units')
    qc.require(len(tree['inputs'])==1,'Diagnostic needs one frozen pair source')
    member=tree['inputs'][0];origin_path=path.parent/member['qc']['path'];origin=qc.read_record(origin_path)
    qc.require(pairs.sha(pairs.small(origin_path))==value['source_pair_sha256'],'Source pair bytes changed')
    qc.require(origin.digest==value['source_pair_digest'] and
        (expected_source_digest is None or origin.digest==expected_source_digest),'Wrong source pair digest')
    qc.require(tree['provenance']['configuration_id']=='sha256:'+pairs.sha(pairs.canonical(value['configuration']).encode('utf-8')),
               'Diagnostic configuration differs')
    original=exposure_rows(pairs.table_from_record(origin)['rows'])
    qc.require(len(original)==len(value['rows']),'Diagnostic population differs')
    for source,row in zip(original,value['rows']):
        qc.require(pairs.canonical(source)==pairs.canonical({k:row[k] for k in source}),'Original samples changed in diagnostic')
        qc.require(type(row['fit_included']) is bool and all(row[k] is None or finite(row[k])
            for k in ('line_prediction_adu','residual_adu','residual_percent','count_rate_adu_per_s')),
            'Invalid saved diagnostic values')
    qc.require(len(value['fits'])==len({r['roi'] for r in original}) and
        {f['roi'] for f in value['fits']}=={r['roi'] for r in original},'ROI fit coverage differs')
    for fit in value['fits']:
        qc.require(fit['status'] in ('available','unavailable') and type(fit['n']) is int and fit['n']>=0, 'Invalid fit status/count')
        if fit['status']=='available':
            qc.require(fit['reason'] is None and fit['n']>=2 and
                all(finite(fit[k]) for k in ('intercept_adu','slope_adu_per_s','time_center_s','signal_center_adu')), 'Invalid saved line')
        else:qc.require(type(fit['reason']) is str and fit['intercept_adu'] is None and fit['slope_adu_per_s'] is None, 'Invalid unavailable fit')
    qc.require(tree['file']['selectors']==[dict(detector_id=original[0]['detector'],table_name='line_residuals')], 'Diagnostic identity/selector differs')
    qc.require(tree['file']['sha256']==value['transport_sha256'],'Derived table fingerprint differs')
    for fit in value['fits']:
        qc.require(fit['status'] in ('available','unavailable') and type(fit['n']) is int and fit['n']>=0, 'Invalid fit summary')
        qc.require(all(fit[k] is None or finite(fit[k]) for k in ('intercept_adu','slope_adu_per_s','time_center_s','signal_center_adu')), 'Invalid saved coefficients')
    return deepcopy(value)
