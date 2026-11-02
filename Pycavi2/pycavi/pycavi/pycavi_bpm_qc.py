"""Native BPM values -> common ASDF QC; no FITS image processing here.

JSON is a bounded, versioned internal transport. QcRecipe and write_record own
the shared schema/ASDF lifecycle. File bytes are hashed, never pixel-parsed.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

try:
    from . import pycavi_qc as qc
except ImportError:
    import pycavi_qc as qc


class BpmQcRecipe(qc.QcRecipe):
    METRICS = {
        'exposure.time': 's', 'reference.level': 'ADU', 'reference.fraction': '1',
        'pixels.saturated': 'count', 'pixels.margin_excluded': 'count',
        'pixels.sample_excluded': 'count', 'pixels.nonfinite': 'count',
        'pixels.reference': 'count', 'reasons.histogram': 'count',
        'fit.coverage_histogram': 'count', 'pairs.usable': 'count',
        'pairs.distinct_times': 'count', 'pairs.distinct_levels': 'count',
        'signal.span_fraction': '1',
    }

    def __init__(self, **kwargs):
        qc.require(kwargs['operation'] == 'cal.bpm', 'BPM operation mismatch')
        super().__init__(**kwargs)

    def add_measurement(self, detector_id, **measurement):
        qc.require(self.METRICS.get(measurement['name']) == measurement['unit'],
                   'Unknown BPM quantity or unit')
        super().add_measurement(detector_id, **measurement)


def _integer(v):
    return type(v) is int and v >= 0


def _number(v):
    return type(v) in (int, float) and math.isfinite(v)


def _digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_handoff(path):
    path = Path(path).resolve(strict=True)
    qc.require(path.stat().st_size <= qc.MAX_RECORD_BYTES, 'Oversized BPM transport')
    t = json.loads(path.read_text())
    qc.encoded(t)
    expected = {'status', 'handoff_version', 'operation', 'output', 'created_at',
                'source_revision', 'detector_id', 'configuration_detector', 'prior_registry',
                'exposure_key', 'exposure_hdu', 'readout_id', 'bin_x', 'bin_y', 'output_mode', 'shape', 'mode', 'mask_encoding',
                'prior_active_only', 'binary_good_value', 'reject_bits', 'parameters', 'coverage',
                'rois', 'configuration', 'inputs', 'calibrations', 'reason_histogram', 'fit_histogram'}
    qc.require(type(t) is dict and set(t) == expected and t['status'] == 'complete' and
               t['handoff_version'] == 1 and t['operation'] == 'cal.bpm', 'Unknown BPM transport')
    qc.timestamp(t['created_at'])
    qc.require(qc.text(t['detector_id']) and qc.text(t['exposure_key']) and
               _integer(t['exposure_hdu']) and _integer(t['configuration_detector']), 'Invalid binding')
    qc.require(qc.text(t['readout_id']) and _integer(t['bin_x']) and t['bin_x']>0 and
               _integer(t['bin_y']) and t['bin_y']>0, 'Invalid readout/binning')
    qc.require(type(t['source_revision']) is str and len(t['source_revision']) == 40 and
               all(c in '0123456789abcdef' for c in t['source_revision']), 'Invalid source revision')
    qc.require(type(t['output_mode']) is int and t['output_mode'] in (1, 2) and
               type(t['mode']) is int and t['mode'] in (1, 2) and
               type(t['mask_encoding']) is int and t['mask_encoding'] in (1, 2, 3) and
               type(t['prior_active_only']) is int and t['prior_active_only'] in (0, 1) and
               type(t['binary_good_value']) is int and t['binary_good_value'] in (0, 1) and
               _integer(t['reject_bits']) and t['reject_bits'] <= 255,
               'Invalid mask/acquisition mode')
    qc.require(t['output_mode'] != 2 or t['mask_encoding'] != 3, 'Combined binary reasons unavailable')
    qc.require(t['output_mode'] != 2 or t['mask_encoding'] != 2 or t['prior_registry'] == 'WENU_BPM_V1',
               'Combined reason registry mismatch')
    qc.require(type(t['shape']) is list and len(t['shape']) == 2 and
               all(_integer(v) and 0 < v <= 40000 for v in t['shape']), 'Invalid output shape')
    n = t['shape'][0]*t['shape'][1]
    qc.require(type(t['rois']) is list and all(type(z) is list and len(z) == 4 and
               all(type(v) is int for v in z) and 1 <= z[0] <= z[1] <= t['shape'][1] and
               1 <= z[2] <= z[3] <= t['shape'][0] for z in t['rois']), 'Invalid ROI geometry')
    for key, size in [('reason_histogram', 256), ('fit_histogram', 3)]:
        qc.require(type(t[key]) is list and len(t[key]) == size and
                   all(_integer(v) for v in t[key]) and sum(t[key]) == n, 'Invalid native histogram')
    qc.require(type(t['inputs']) is list and len(t['inputs']) >= 2, 'Missing flat inputs')
    for item in t['inputs']:
        qc.require(set(item) == {'file', 'integration_seconds', 'pair_id', 'included', 'saturated',
                   'margin_excluded', 'sample_excluded', 'nonfinite', 'reference_samples',
                   'reference_fraction', 'reference_level'}, 'Unknown native frame fields')
        qc.require(type(item['included']) is int and item['included'] in (0, 1) and _number(item['integration_seconds']) and
                   item['integration_seconds'] > 0 and _integer(item['pair_id']), 'Invalid acquisition metadata')
        qc.require(all(_integer(item[k]) for k in ('saturated', 'margin_excluded',
                   'sample_excluded', 'nonfinite', 'reference_samples')), 'Invalid native counts')
        qc.require(sum(item[k] for k in ('saturated', 'margin_excluded', 'sample_excluded', 'nonfinite')) <= n,
                   'Exclusion counts exceed active plane')
        qc.require(item['reference_samples'] <= n, 'Reference count exceeds active plane')
        for key in ('reference_level', 'reference_fraction'):
            qc.require(_number(item[key]) if item['included'] else item[key] is None,
                       'Missing native measurement availability')
    qc.require(type(t['calibrations']) is list and
               [c['role'] for c in t['calibrations']].count('bias') == 1 and
               all(c['role'] in ('bias', 'bpm') for c in t['calibrations']), 'Invalid selected calibrations')
    qc.require(type(t['parameters']) is dict and set(t['parameters']) == {
        'saturation_raw', 'upper_fraction', 'minimum_span_fraction', 'maximum_pair_difference',
        'response_low', 'response_high', 'proportional'} and
        all(_number(v) for v in t['parameters'].values()), 'Invalid native parameters')
    qc.require(t['parameters']['saturation_raw'] > 0 and 0 < t['parameters']['upper_fraction'] <= 1 and
               0 <= t['parameters']['minimum_span_fraction'] <= 1 and
               t['parameters']['maximum_pair_difference'] >= 0 and
               t['parameters']['response_low'] < t['parameters']['response_high'] and
               type(t['parameters']['proportional']) is int and t['parameters']['proportional'] in (0, 1),
               'Invalid parameter bounds')
    for ref in [i['file'] for i in t['inputs']] + [c['file'] for c in t['calibrations']]:
        qc.require(set(ref) == {'path', 'hdu', 'asset_id'} and qc.text(ref['asset_id']) and
                   _integer(ref['hdu']) and qc.text(ref['path']) and Path(ref['path']).is_absolute(),
                   'Invalid explicit file reference')
    qc.require(qc.text(t['output']) and Path(t['output']).is_absolute(), 'Explicit output required')
    qc.require(set(t['coverage']) == {'usable_pairs', 'distinct_times', 'paired_levels', 'span_fraction'} and
               all(_integer(t['coverage'][k]) for k in ('usable_pairs', 'distinct_times', 'paired_levels')) and
               _number(t['coverage']['span_fraction']), 'Invalid coverage summary')
    return t


def publish_handoff(path, directory, *, configuration_record, assessment_id):
    """Prepare all common records, publish immutable leaves then the product.

    Conflicts fail before writes. Later I/O errors can retain completed files;
    they never authorize overwriting or a false complete-command report.
    """
    t = load_handoff(path)
    directory = Path(directory).resolve(strict=True)
    qc.require(directory.is_dir() and qc.text(assessment_id), 'Explicit assessment/destination required')
    config = Path(configuration_record).resolve(strict=True)
    qc.require(config.stat().st_size <= qc.MAX_RECORD_BYTES and
               json.loads(config.read_text()) == t['configuration'], 'Configuration snapshot mismatch')
    refs = [i['file'] for i in t['inputs']] + [c['file'] for c in t['calibrations']]
    locations = [Path(r['path']).resolve(strict=True) for r in refs] + [Path(t['output']).resolve(strict=True)]
    qc.require(all(p.is_file() for p in locations), 'Missing input/product file')
    names = [qc.qc_filename(p.name) for p in locations]
    qc.require(len(names) == len(set(names)) and len({r['asset_id'] for r in refs}) == len(refs),
               'QC basename or input identity collision')
    qc.require(str(locations[-1]) not in {r['asset_id'] for r in refs}, 'Product/input identity collision')
    qc.require(all(not (directory/n).exists() and not (directory/n).is_symlink() for n in names),
               'Existing QC destination; no overwrite')
    fingerprints = {str(p): _digest(p) for p in [*locations, config]}
    detector = t['detector_id']
    producer = dict(name='mefpp_m5', version='M5', source_revision=t['source_revision'])
    configuration_id = str(config)

    def builder(index, kind, ref):
        p = locations[index]
        return BpmQcRecipe(file=dict(id=ref['asset_id'], filename=p.name, location=str(p), kind=kind,
            sha256=fingerprints[str(p)], observed_at=None,
            context=dict(readout_id=t['readout_id'], bin_x=t['bin_x'], bin_y=t['bin_y']),
            selectors=[dict(detector_id=detector, hdu_index=ref['hdu'],
                            configuration_detector=t['configuration_detector'])]),
            assessment_id=f'{assessment_id}:{index}', created_at=t['created_at'], producer=producer,
            operation='cal.bpm', configuration_id=configuration_id)

    def source(ref):
        return dict(file_id=ref['asset_id'], detector_id=detector, hdu_index=ref['hdu'])

    def add(b, name, value, unit, sources, *, stage, samples, method, region):
        b.add_measurement(detector, name=name, value=value, unit=unit,
            definition=dict(stage=stage, method=method, region=region, sample_count=samples), sources=sources)

    leaves = []
    population = t['shape'][0]*t['shape'][1]
    for index, item in enumerate(t['inputs']):
        b = builder(index, 'raw', item['file'])
        origins = [source(item['file'])]
        add(b, 'exposure.time', item['integration_seconds'], 's', origins, stage='acquisition', samples=1,
            method='explicit_header_card', region=dict(kind='header', keyword=t['exposure_key'], hdu=t['exposure_hdu']))
        for key, metric in [('saturated', 'pixels.saturated'), ('margin_excluded', 'pixels.margin_excluded'),
                            ('sample_excluded', 'pixels.sample_excluded'), ('nonfinite', 'pixels.nonfinite'),
                            ('reference_samples', 'pixels.reference')]:
            add(b, metric, item[key], 'count', origins, stage='active_sample_admission', samples=population,
                method='native_pixel_count', region=dict(kind='active', shape=t['shape']))
        for key, metric, unit in [('reference_level', 'reference.level', 'ADU'),
                                  ('reference_fraction', 'reference.fraction', '1')]:
            if item['included']:
                add(b, metric, item[key], unit, origins, stage='corrected_active_reference',
                    samples=item['reference_samples'], method='legacy_pixel_median',
                    region=dict(kind='active_roi_union', rois=t['rois']))
            else:
                b.add_unavailable(detector, name=metric, unit=unit, stage='corrected_active_reference',
                                  reason='no_usable_reference_samples', sources=origins)
        b.add_extension('bpm_frame', dict(pair_id=item['pair_id'], included=bool(item['included']),
            parameters=deepcopy(t['parameters']), detector_scan_bpm='not_applicable_electronic_reads'))
        leaves.append(b.seal())
    for index, binding in enumerate(t['calibrations'], len(leaves)):
        b = builder(index, 'product', binding['file'])
        b.add_extension('calibration_binding', dict(role=binding['role'],
            scope='selected_binding_only_not_generation_or_reassessment'))
        leaves.append(b.seal())
    output_ref = dict(asset_id=str(locations[-1]), hdu=0)
    parent = builder(len(locations)-1, 'product', output_ref)
    for index, leaf in enumerate(leaves):
        used = index >= len(t['inputs']) or bool(t['inputs'][index]['included'])
        parent.add_input(leaf, qc_path=names[index], participation='used' if used else 'rejected',
                         reason=None if used else 'no_usable_reference_samples')
    origins = [source(i['file']) for i in t['inputs'] if i['included']]
    add(parent, 'reasons.histogram', t['reason_histogram'], 'count', origins,
        stage='response_classification', samples=population, method='native_byte_reason_histogram',
        region=dict(kind='active', shape=t['shape']))
    add(parent, 'fit.coverage_histogram', t['fit_histogram'], 'count', origins,
        stage='response_fitting', samples=population, method='native_fit_state_count',
        region=dict(kind='active', shape=t['shape']))
    for key, metric in [('usable_pairs', 'pairs.usable'), ('distinct_times', 'pairs.distinct_times'),
                        ('paired_levels', 'pairs.distinct_levels'), ('span_fraction', 'signal.span_fraction')]:
        add(parent, metric, t['coverage'][key], '1' if key == 'span_fraction' else 'count', origins,
            stage='acquisition_admission', samples=len(origins), method='native_admission_summary',
            region=dict(kind='active_roi_union', rois=t['rois']))
    parent.add_extension('bpm', dict(parameters=deepcopy(t['parameters']),
        acquisition_mode=t['mode'], output_mode=t['output_mode'], reason_registry='WENU_BPM_V1',
        prior_encoding=t['mask_encoding'], prior_registry=t['prior_registry'],
        prior_active_only=bool(t['prior_active_only']), binary_good_value=t['binary_good_value'],
        reject_bits=t['reject_bits'], configuration_sha256=fingerprints[str(config)],
        fits_planes=dict(reasons=0, coverage=1, sample_count=2, new_reasons=3, selection=4),
        scope='BPM_only; gain_RON_linearity_shutter_not_measured'))
    product = parent.seal()
    for record in leaves:
        qc.write_record(record, directory, qc_root=directory)
    destination = qc.write_record(product, directory, qc_root=directory)
    for _ in qc.traverse_records(destination, qc_root=directory):
        pass
    qc.require(all(_digest(Path(p)) == h for p, h in fingerprints.items()), 'Files changed during QC assembly')
    return destination
