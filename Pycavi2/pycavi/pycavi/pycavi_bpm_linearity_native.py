"""Explicit BPM command construction and native-QC verification; no pixel math."""
import hashlib
import json
from pathlib import Path
import subprocess
try:
    from . import pycavi_native_product_qc as native_qc
    from . import pycavi_linearity_recipe as preparation
except ImportError:
    import pycavi_native_product_qc as native_qc
    import pycavi_linearity_recipe as preparation
require = preparation.require


def bpm_request(plan, entry, destination, started, *, deferred_directories=None):
    d, detector = entry['dependencies'], entry['detector']
    selection, policy = d['selection'], plan['bpm']
    controls = Path(plan['layout']['orchestration'])/entry['key']/'bpm'
    work = Path(plan['layout']['work'])/entry['key']/'bpm'
    logs = Path(plan['layout']['logs'])/entry['key']/'bpm'
    products = destination/'bpm'
    for path in (controls, work, logs, products):
        if path == controls or deferred_directories is None:
            path.mkdir(parents=True)
        else:
            deferred_directories.append(str(path))
    (controls/'native.toml').write_text(d['configuration'])
    pairs, lines = {}, []
    for row in selection['flat']:
        pair = pairs.setdefault(row['pair'], len(pairs))
        require(not any(c in row['path'] for c in '\t\r\n\0'), 'Invalid flat path transport')
        lines.append(f'{row["path"]}\t{row["hdu"]}\t{pair}\n')
    (controls/'flats.tsv').write_text(''.join(lines))
    (controls/'rois.tsv').write_text(''.join(' '.join(map(str, row))+'\n' for row in entry['reference_rois']))
    # Native product companions remain together; process console logs use logs root.
    stem = f'CMDP.{started}.001'
    fits, sidecar, log = (products/(stem+suffix) for suffix in ('.fits', '.asdf', '.log'))
    bpm = selection['bpm']
    controls_policy = plan['resolved']['controls']
    argv = [plan['native']['bpm'], 'cal', 'bpm', '--config', str(controls/'native.toml'),
        '--flats', str(controls/'flats.tsv'), '--detector-id', detector['detector_id'],
        '--config-detector', str(detector['configuration_detector']), '--readout-id', selection['readout_id'],
        '--bin-x', str(selection['bin_x']), '--bin-y', str(selection['bin_y']),
        '--master-bias', d['master']['product'], '--bias-hdu', str(d['master']['hdu']),
        '--input-bpm', bpm.get('path', 'omitted') if bpm['encoding'] != 'omitted' else 'omitted',
        '--bpm-encoding', bpm['encoding'], '--reject-bits', str(controls_policy['reject_bits']),
        '--acquisition', policy['acquisition'], '--exposure-key', selection['header_keys']['exposure'],
        '--exposure-hdu', str(selection['exposure_hdu']), '--saturation', str(controls_policy['raw_saturation_adu']),
        '--upper-fraction', str(policy['upper_fraction']), '--minimum-span', str(policy['minimum_span_fraction']),
        '--maximum-pair-difference', str(policy['maximum_pair_difference']), '--roi-file', str(controls/'rois.tsv'),
        '--mad', 'yes' if controls_policy['with_mad'] else 'no', '--output-mode', policy['output_mode'],
        '--created-at', started[:19]+'Z', '--output', str(fits), '--native-asdf', str(sidecar),
        '--work-dir', str(work), '--log-path', str(log), '--config-record', str(work/'configuration.json')]
    if bpm['encoding'] != 'omitted':
        argv += ['--bpm-hdu', str(bpm['hdu']), '--bpm-coordinates', 'active']
    if bpm['encoding'] == 'binary':
        argv += ['--bpm-good-value', str(bpm['good_value'])]
    elif bpm['encoding'] == 'reason8':
        argv += ['--bpm-registry', bpm['registry']]
    return argv, fits, sidecar, log, logs


def characterize_bpm(plan, entry, destination, started, inputs):
    d = entry['dependencies']
    products = destination/'bpm'
    argv, fits, sidecar, log, logs = bpm_request(plan, entry, destination, started)
    receipt = dict(status='failed', argv=argv, batch_preservation=inputs.reference)
    try:
        for name in d['baseline']:
            inputs.observe(name)
        with (logs/'command.log').open('x') as stream:
            subprocess.run(argv, cwd=plan['layout']['orchestration'], stdout=stream,
                           stderr=subprocess.STDOUT, check=True)
        for name in d['baseline']:
            inputs.observe(name)
        verify_bpm(sidecar, plan, entry, fits)
        receipt.update(status='complete_pending_batch_preservation', files={
            str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (fits, sidecar, log)})
        return dict(fits=str(fits), asdf=str(sidecar), log=str(log), sha256=receipt['files'],
                    original_flat_indices=[row['index'] for row in d['selection']['flat']])
    except Exception as error:
        receipt['error'] = repr(error)
        raise
    finally:
        (products/'execution.json').write_text(json.dumps(receipt, indent=2)+'\n')


def verify_bpm(path, plan, entry, fits):
    q = native_qc.read(path)
    d, detector = entry['dependencies'], entry['detector']
    require(q['file']['location'] == str(fits) and q['provenance']['operation'] == 'cal.bpm' and
            q['extensions']['record_scope'] == 'one_final_primary_image_product' and
            q['provenance']['producer']['source_revision'] == plan['source_revision'] and
            json.loads(q['provenance']['configuration']['snapshot']) == d['master_snapshot'], 'BPM product context differs')
    saved = q['characterization']['detectors']
    require(len(saved) == 1 and saved[0]['detector_id'] == detector['detector_id'] and
            saved[0]['configuration_detector'] == detector['configuration_detector'], 'BPM detector mapping differs')
    require(len(q['embedded_input_records']) == len(d['selection']['flat']), 'BPM input count differs')
    for index, (record, row) in enumerate(zip(q['embedded_input_records'], d['selection']['flat'])):
        require(record['original_index'] == index and record['file']['location'] == row['path'] and
                record['detectors'][0]['source_hdu'] == row['hdu'], 'BPM ordered source path/HDU differs')
    context = json.loads(q['extensions']['operation_context']['snapshot'])
    policy = plan['bpm']
    require(context['mode'] == {'quick': 2, 'provisional': 1}[policy['acquisition']] and
            context['output_mode'] == {'new': 1, 'combined': 2}[policy['output_mode']] and
            context['rois'] == entry['reference_rois'], 'BPM acquisition/reference/output settings differ')
    for field in ('upper_fraction', 'minimum_span_fraction', 'maximum_pair_difference'):
        require(context['parameters'][field] == policy[field], 'BPM admission parameter differs')
    references = {row['role']: row['file'] for row in context['calibrations']}
    expected = [('bias', d['master']['product'], d['master']['hdu'])]
    if d['selection']['bpm']['encoding'] != 'omitted':
        expected.append(('bpm', d['selection']['bpm']['path'], d['selection']['bpm']['hdu']))
    for role, path, hdu in expected:
        require(references[role]['path'] == path and references[role]['hdu'] == hdu, 'BPM calibration binding differs')
    metrics = {m['name']: m for m in saved[0]['measurements']}
    require(metrics['reason_histogram']['value'] == context['reason_histogram'] and
            metrics['fit_histogram']['value'] == context['fit_histogram'], 'BPM common/context histograms differ')
