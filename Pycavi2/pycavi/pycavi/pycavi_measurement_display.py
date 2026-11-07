"""Lossless saved-measurement reader for raw-pair and corrected preparation ASDF.

Only selects stored values and identities. No averaging, variance conversion,
image loading, native transport loading, regression or physical model.
"""
from copy import deepcopy
import json
from pathlib import Path
import pycavi_pair_qc as pairs
from pycavi_pair_display import exposure_rows
qc=pairs.qc
RAW='raw_pair_bias_subtracted_without_overscan'
CORRECTED='scan_corrected_master_bias_subtracted'


def preparation_rows(value):
    qc.require(value['measurement_stage']==CORRECTED,'Unexpected preparation stage')
    lookup={}
    for i,pair in enumerate(value['rows']):
        raw=pair['raw']
        for member,prefix in ((1,'first'),(2,'second')):
            key=(raw['roi'],raw[prefix+'_input_index'],member)
            qc.require(key not in lookup,'Duplicate corrected exposure identity')
            lookup[key]=(i,raw,pair['corrected'],prefix)
    rows=[]
    for source in value['exposure_rows']:
        row=deepcopy(source);key=(row['roi'],row['input_index'],row['pair_member'])
        qc.require(key in lookup,'Missing corrected pair source')
        i,raw,corrected,prefix=lookup[key]
        qc.require(row['asset']==raw[prefix+'_asset'] and row['hdu']==raw[prefix+'_hdu'] and
            row['pair_id']==raw['pair_id'] and row['exposure_seconds']==raw[prefix+'_seconds'] and
            row['signal_adu']==corrected[prefix+'_mean_adu'] and
            row['spatial_variance_adu2']==corrected[prefix+'_spatial_variance_adu2'] and
            row['valid_pixels']==corrected['valid_pixels'],'Corrected exposure/source mismatch')
        row.update(source_row_index=i,processing_stage=CORRECTED,population='pair_common_accepted_pixels',
            raw_pair_diagnostic=deepcopy(raw))
        for key in ('active_xmin','active_xmax','active_ymin','active_ymax',
                    'raw_xmin','raw_xmax','raw_ymin','raw_ymax','configuration_detector',
                    'bpm_excluded','nonfinite_excluded','saturated'):
            row[key]=raw[key]
        rows.append(row)
    qc.require(len(rows)==len(lookup),'Incomplete corrected exposure projection')
    return rows


def read_source(path,record=None):
    """Return stored signals and diagnostics; raw diagnostic channels stay raw."""
    path=Path(path).resolve(strict=True);record=record or qc.read_record(path);tree=record.as_dict()
    if tree['provenance']['operation']=='linearity.prepare':
        import pycavi_linearity_preparation_qc as preparation
        value=preparation.read_product(path,expected_digest=record.digest)
        raw_bias=value['raw_bias_diagnostics'][0]['table']['rows']
        qc.require(all(pairs.canonical(d['table']['rows'])==pairs.canonical(raw_bias)
                       for d in value['raw_bias_diagnostics']),'Raw bias-only diagnostics differ across pairs')
        context=tree['extensions']['linearity_preparation_context']
        return dict(record=record,kind='preparation',stage=CORRECTED,signals=preparation_rows(value),
            pairs=[deepcopy(r['raw']) for r in value['rows']],bias=deepcopy(raw_bias),
            provenance=dict(measurement_stage=CORRECTED,raw_diagnostic_stage=RAW,
                selection=deepcopy(context['selection']),native_receipt=dict(directory=context['native_directory'],
                operation='linearity.prepare'),serializer=deepcopy(tree['provenance']['producer'])))
    table=pairs.table_from_record(record)
    qc.require(table['kind']=='pairs','Measurement source must be pairs or preparation ASDF')
    return dict(record=record,kind='pairs',stage=RAW,signals=exposure_rows(table['rows']),
        pairs=deepcopy(table['rows']),provenance=deepcopy(tree['extensions']['raw_pair_provenance']))


def preparation_products(batch):
    """Admit completed all32 index, including the explicitly reused CCD65 product."""
    batch=Path(batch).resolve(strict=True);paths=[batch/'index.json',batch/'overall-execution.json']
    frozen={str(p):pairs.sha(pairs.small(p)) for p in paths}
    index,receipt=[json.loads(pairs.small(p)) for p in paths]
    qc.require(index['status']==receipt['status']=='complete_for_owner_inspection' and
        index['measurement_stage']==CORRECTED and index['products']==receipt['products'] and
        receipt['detectors_total']==32 and receipt['detectors_processed']==31 and
        len(receipt['preservation'])==11 and all(v is True for v in receipt['preservation'].values()),
        'Require completed preserved corrected preparation batch')
    products=[];seen=set()
    for item in index['products']:
        detector=item['detector'];qc.require(detector not in seen,'Duplicate preparation detector');seen.add(detector)
        path=Path(item['path']).resolve(strict=True)
        qc.require(path.name=='linearity-preparation.asdf' and
            tuple(item[k] for k in ('pairs','exposures','sites','trace_frames'))==(50,100,100,30) and
            item['noise_state']=='unavailable','Incomplete preparation product')
        if detector=='ESO_CCD_#65':
            qc.require(item['reused'] is True and receipt['reused_detector']==detector,'Invalid reused detector')
        else:qc.require(item['reused'] is False and path.is_relative_to(batch/detector.replace('ESO_CCD_#','CCD')),
                        'New preparation path escapes detector directory')
        record=qc.read_record(path)
        qc.require(record.digest==item['digest'] and record.as_dict()['file']['selectors']==
            [dict(detector_id=detector,table_name='linearity_preparation')],'Preparation index digest/identity differs')
        products.append(path)
    qc.require(len(products)==32 and seen=={f'ESO_CCD_#{i}' for i in range(65,97)},'Incomplete preparation cohort')
    qc.require(all(pairs.sha(pairs.small(Path(p)))==d for p,d in frozen.items()),'Preparation index changed')
    return products,frozen
