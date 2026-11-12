"""Resolve detector/processing TOMLs for native linearity preparation (#236).

No FITS reads, correction, PAF fallback or physical-model defaults. The returned
JSON-primitive snapshot freezes both input texts and their SHA256 identities.
"""
from copy import deepcopy
import hashlib
import math
from pathlib import Path
import tomllib


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rectangle(value, width, height, label):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(v) is int for v in value), label + ': integer rectangle required')
    x1, x2, y1, y2 = value
    require(1 <= x1 <= x2 <= width and 1 <= y1 <= y2 <= height,
            label + ': rectangle outside raw/active image')
    return list(value)


def contained(inner, outer):
    return (outer[0] <= inner[0] <= inner[1] <= outer[1] and
            outer[2] <= inner[2] <= inner[3] <= outer[3])


CONTROL_FIELDS = {
    'raw_saturation_adu', 'reject_bits', 'mask_encoding', 'binary_good_value',
    'pair_time_tolerance_s', 'with_mad', 'bias_mean_min_adu', 'bias_mean_max_adu',
    'bias_stack_kappa', 'bias_min_frames', 'high_offset_sigma',
}


def resolve(detector_text, processing_text, *, detector_id=None):
    """Validate explicit schemas/values; keep reference and applied regions apart."""
    require(type(detector_text) is str and type(processing_text) is str,
            'Explicit UTF-8 TOML text required')
    d, p = tomllib.loads(detector_text), tomllib.loads(processing_text)
    embedded = 'bpm_linearity_recipe_schema_version' in p and 'detector_toml' in p
    if embedded:
        selected = {row['detector_id'] for row in p['detectors']}
        if detector_id is not None:
            require(detector_id in selected, 'Detector missing from the recipe')
            selected = {detector_id}
        catalogued = {row['id'] for row in d['detector'] if row.get('enabled', True) is True}
        require(selected and selected <= catalogued, 'Unknown or disabled detector selection')
        p = {**p['preparation'], 'trim': d['trim']}
    require(type(d.get('footprint_schema_version')) is int and d['footprint_schema_version'] == 1,
            'Unsupported detector geometry schema')
    require(type(p.get('processing_footprint_schema_version')) is int and
            p['processing_footprint_schema_version'] == 1 and
            type(p.get('linearity_preparation_schema_version')) is int and
            p['linearity_preparation_schema_version'] == 1, 'Missing/unsupported numerical preparation schema')
    require(isinstance(d.get('instrument'), str) and d['instrument'] and
            p.get('instrument') == d['instrument'], 'Instrument mismatch')
    require(d.get('binning') == [1, 1] and all(type(v) is int for v in d['binning']),
            'Only explicit 1x1 geometry is admitted')
    require(type(p.get('roi_schema_version')) is int and p['roi_schema_version'] == 1 and p.get('roi_coordinates') == 'retained-active',
            'Unknown ROI schema/coordinates')
    for key in ('use_prescan', 'use_overscan'):
        require(type(p.get(key)) is int and p[key] in (0, 1), 'Explicit integer scan switch required: ' + key)
    for key in ('scan_reject_low', 'scan_reject_high'):
        require(type(p.get(key)) is int and p[key] >= 0, 'Explicit nonnegative rejection count required: ' + key)
    controls = p.get('linearity_preparation')
    require(isinstance(controls, dict) and set(controls) == CONTROL_FIELDS,
            'Missing/unknown linearity preparation controls')
    for key in ('raw_saturation_adu', 'pair_time_tolerance_s', 'bias_mean_min_adu',
                'bias_mean_max_adu', 'bias_stack_kappa', 'high_offset_sigma'):
        require(type(controls[key]) in (int, float) and math.isfinite(controls[key]),
                'Finite numerical control required: ' + key)
    require(controls['raw_saturation_adu'] > 0 and controls['pair_time_tolerance_s'] >= 0 and
            controls['bias_mean_min_adu'] < controls['bias_mean_max_adu'] and
            controls['bias_stack_kappa'] > 0 and controls['high_offset_sigma'] > 0,
            'Invalid preparation range/scale')
    require(type(controls['reject_bits']) is int and 0 <= controls['reject_bits'] <= 255 and
            type(controls['binary_good_value']) is int and controls['binary_good_value'] in (0, 1) and
            controls['mask_encoding'] in ('binary', 'reason8', 'omitted') and
            type(controls['bias_min_frames']) is int and controls['bias_min_frames'] >= 3 and
            type(controls['with_mad']) is bool, 'Invalid typed mask/bias/QC controls')
    detectors, trims, rois = d.get('detector'), p.get('trim'), p.get('roi')
    require(isinstance(detectors, list) and detectors and isinstance(trims, list) and
            isinstance(rois, list) and rois, 'Detector, processing and ROI entries required')
    if embedded:
        # A recipe supplies measurement regions only for its selected detectors.
        detectors = [row for row in detectors if row['id'] in selected]
        trims = [row for row in trims if row['detector'] in selected]
        rois = [row for row in rois if row['detector'] in selected]
    require(all(isinstance(v, dict) and {'id','amplifier','raw_size','illuminated','prescan','overscan','native_paf_chip'} <= set(v)
                for v in detectors), 'Incomplete detector entry')
    require(all(isinstance(v, dict) and {'detector','retained','prescan_sample','overscan_sample'} <= set(v)
                for v in trims), 'Incomplete processing entry')
    require(all(isinstance(v, dict) and {'id','detector','amplifier','xmin','xmax','ymin','ymax'} <= set(v)
                for v in rois), 'Incomplete ROI entry')
    ids = [v['id'] for v in detectors]
    require(all(type(v) is str and v for v in ids) and len(set(ids)) == len(ids), 'Duplicate/invalid detector ID')
    require(len(trims) == len(ids) and {v['detector'] for v in trims} == set(ids),
            'Each detector requires exactly one processing entry')
    by_id = {v['detector']: v for v in trims}
    slots = [v['native_paf_chip'] for v in detectors]
    require(all(type(v) is int and v >= 1 for v in slots) and len(set(slots)) == len(slots)
            and (embedded or sorted(slots) == list(range(1, len(detectors)+1))),
            'Require unique explicit native configuration slots')
    names = set()
    for r in rois:
        require(type(r['id']) is str and r['id'] and r['id'] not in names and
                r['detector'] in by_id, 'Duplicate ROI or unknown detector')
        names.add(r['id'])
    entries = []
    for detector in detectors:
        name = detector['id']; t = by_id[name]; size = detector['raw_size']
        require(type(detector.get('amplifier')) is str and detector['amplifier'] and
                isinstance(size, list) and len(size) == 2 and
                all(type(v) is int and 1 < v <= 100000 for v in size), 'Invalid detector size/amplifier')
        w, h = size
        full = {key: rectangle(detector[key], w, h, name + ' ' + key)
                for key in ('illuminated', 'prescan', 'overscan')}
        crop = rectangle(t['retained'], w, h, name + ' retained')
        require(crop[0] < crop[1] and crop[2] < crop[3] and contained(crop, full['illuminated']),
                'Retained region must lie in illuminated region')
        samples = {}
        for key in ('prescan', 'overscan'):
            sample = rectangle(t[key + '_sample'], w, h, name + ' ' + key + ' sample')
            require(contained(sample, full[key]), 'Scan sample outside declared full band')
            if p['use_' + key]:
                require(sample[2:] == [1, h], 'Enabled scan must cover every raw row')
                require(sample[1] < crop[0] or sample[0] > crop[1], 'Scan overlaps retained signal')
            samples[key] = sample
        if p['use_prescan'] and p['use_overscan']:
            require(samples['prescan'][1] < samples['overscan'][0] or
                    samples['overscan'][1] < samples['prescan'][0], 'Overlapping enabled scan bands')
        count = sum(samples[key][1] - samples[key][0] + 1 for key in samples if p['use_' + key])
        rejected = p['scan_reject_low'] + p['scan_reject_high']
        require((count > rejected) if count else rejected == 0, 'Insufficient scan samples')
        selected = [deepcopy(r) for r in rois if r['detector'] == name]
        require(bool(selected), 'Each detector requires an explicit ROI')
        for r in selected:
            require(r['amplifier'] == detector['amplifier'], 'ROI amplifier mismatch')
            rectangle([r[k] for k in ('xmin', 'xmax', 'ymin', 'ymax')],
                      crop[1] - crop[0] + 1, crop[3] - crop[2] + 1, r['id'])
        entries.append(dict(detector_id=name, amplifier_id=detector['amplifier'],
            configuration_detector=detector['native_paf_chip']-1,
            raw_size=list(size), full_regions=full, retained=crop, samples=samples,
            scan_samples=count, scan_kept=count-rejected, rois=selected,
            native_settings=dict(prescan=samples['prescan'][:2], overscan=samples['overscan'][:2],
                trim=list(crop), use_prescan=p['use_prescan'], use_overscan=p['use_overscan'],
                rejection=[p['scan_reject_low'], p['scan_reject_high']],
                minimum_frames=controls['bias_min_frames'], kappa=controls['bias_stack_kappa'])))
    return dict(schema_version=1, operation='linearity.prepare', instrument=d['instrument'],
        binning=[1, 1], controls=deepcopy(controls), detectors=entries,
        sources={key: dict(text=text, sha256=hashlib.sha256(text.encode('utf-8')).hexdigest())
                 for key, text in [('detector_toml', detector_text), ('processing_toml', processing_text)]})


def resolve_files(detectors, processing):
    # Path identities are descriptive; hashes/text define the frozen inputs.
    result = resolve(Path(detectors).read_bytes().decode('utf-8'),
                     Path(processing).read_bytes().decode('utf-8'))
    result['source_paths'] = dict(detector_toml=str(Path(detectors).resolve()),
                                  processing_toml=str(Path(processing).resolve()))
    return result
