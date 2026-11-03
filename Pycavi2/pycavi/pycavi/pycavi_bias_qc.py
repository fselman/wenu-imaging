"""Map a complete native bias handoff to the common ASDF QC creation path.

No FITS image is opened or processed here. Numerical values come from Eclipse;
JSON is an internal versioned transport, never the saved QC representation.
Run explicitly with the qualified ASDF Python, not through an installed Pycavi.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

try:
    from . import pycavi_qc as qc
except ImportError:  # Explicit source-file invocation; no installed-package fallback.
    import pycavi_qc as qc

SAMPLE_KEYS = {'region_pixels', 'bpm_excluded', 'nonfinite_excluded', 'valid_pixels',
               'zone', 'bpm_supplied', 'level_available', 'stdev_available',
               'mad_available', 'mean', 'median', 'stdev', 'mad'}
STAGES = {'raw_active': 'raw_before_correction', 'corrected_active': 'overscan_corrected_trimmed',
          'prescan': 'raw_prescan_empty_reads', 'overscan': 'raw_overscan_empty_reads',
          'master': 'median_stacked_master', 'master_unmasked': 'median_stacked_master_unmasked',
          'raw_difference': 'raw_pair_difference_before_any_correction'}


def _integer(value):
    return type(value) is int and value >= 0


def _flag(value):
    return type(value) is int and value in (0, 1)


def _sample(sample, *, scan=False):
    qc.require(type(sample) is dict and set(sample) == SAMPLE_KEYS, 'Unknown native sample fields')
    qc.require(all(_integer(sample[k]) for k in ('region_pixels', 'bpm_excluded',
               'nonfinite_excluded', 'valid_pixels')), 'Invalid native sample counts')
    qc.require(sample['region_pixels'] == sum(sample[k] for k in
               ('bpm_excluded', 'nonfinite_excluded', 'valid_pixels')), 'Native sample counts do not partition region')
    qc.require(all(_flag(sample[k]) for k in ('bpm_supplied', 'level_available',
               'stdev_available', 'mad_available')), 'Invalid native availability flags')
    qc.require(sample['level_available'] == int(sample['valid_pixels'] > 0) and
               sample['stdev_available'] == int(sample['valid_pixels'] > 1) and
               sample['mad_available'] <= sample['level_available'], 'Contradictory native availability')
    qc.require(all(type(sample[k]) in (int, float) and math.isfinite(sample[k]) for k in
               ('mean', 'median', 'stdev', 'mad')), 'Nonfinite native measurement')
    qc.require(sample['stdev'] >= 0 and sample['mad'] >= 0, 'Negative native spread')
    zone = sample['zone']
    qc.require(type(zone) is list and len(zone) == 4 and all(_integer(x) for x in zone), 'Invalid native ROI')
    if sample['region_pixels']:
        qc.require(zone[0] >= 1 and zone[2] >= 1 and zone[1] >= zone[0] and zone[3] >= zone[2] and
                   (zone[1]-zone[0]+1)*(zone[3]-zone[2]+1) == sample['region_pixels'], 'Native ROI/count mismatch')
    if scan:
        qc.require(not sample['bpm_supplied'] and not sample['bpm_excluded'], 'Detector BPM cannot apply to electronic scan reads')


def load_handoff(path):
    path = Path(path).resolve(strict=True)
    qc.require(path.is_file() and path.stat().st_size <= qc.MAX_RECORD_BYTES, 'Invalid/oversized native handoff')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            qc.require(key not in result, 'Duplicate native JSON key')
            result[key] = value
        return result
    try:
        tree = json.loads(path.read_text(), object_pairs_hook=unique)
        qc.require(tree['status'] == 'complete' and tree['handoff_version'] == 1, 'Require a complete version-1 native handoff')
        qc.require(type(tree['configuration']) is dict, 'Missing effective native configuration')
        qc.require(type(tree['inputs']) is list and len(tree['inputs']) >= 3, 'Missing native bias inputs')
        qc.require(qc.text(tree['detector_id']) and qc.text(tree['readout_id']), 'Missing detector/readout')
        qc.require(all(_integer(tree[k]) for k in ('configuration_detector', 'input_hdu', 'output_hdu')) and
                   tree['bin_x'] > 0 and tree['bin_y'] > 0, 'Invalid native mapping')
        qc.require(set(tree['producer']) == {'name', 'version', 'source_revision'} and
                   all(qc.text(v) for v in tree['producer'].values()), 'Missing native producer')
        bpm = tree['bpm']
        qc.require(_flag(bpm['selected']), 'Invalid BPM selection')
        if bpm['selected']:
            qc.require(Path(bpm['path']).is_absolute() and _integer(bpm['hdu']) and
                       _flag(bpm['good_value']) and _flag(bpm['active_only']), 'Invalid explicit BPM binding')
        for member in tree['inputs']:
            qc.require(Path(member['path']).is_absolute() and _flag(member['accepted']), 'Invalid input path/participation')
            profile = member['scan_correction']
            qc.require(_integer(profile['rows']) and profile['rows'] >= 2 and
                all(type(profile[k]) in (int,float) and math.isfinite(profile[k]) for k in ('median','stdev')) and
                profile['stdev'] >= 0 and _flag(profile['prescan_used']) and _flag(profile['overscan_used']) and
                type(profile['rejection']) is list and len(profile['rejection']) == 2 and
                all(_integer(x) for x in profile['rejection']), 'Invalid native scan correction profile')
            for stage in ('raw_active', 'corrected_active', 'prescan', 'overscan'):
                _sample(member[stage], scan=stage in ('prescan', 'overscan'))
                if stage in ('raw_active', 'corrected_active'):
                    qc.require(member[stage]['bpm_supplied'] == bpm['selected'], 'BPM selection/measurement mismatch')
        for stage in ('master', 'master_unmasked', 'raw_difference'):
            _sample(tree[stage])
        qc.require(tree['master']['bpm_supplied'] == bpm['selected'] and
                   not tree['master_unmasked']['bpm_supplied'], 'Master mask mismatch')
        ron = tree['ron']
        qc.require(all(_flag(ron[k]) for k in ('pair_set', 'stdev_available', 'mad_available')), 'Invalid RON flags')
        if ron['pair_set']:
            qc.require(_integer(ron['first']) and _integer(ron['second']) and
                       ron['first'] != ron['second'] and max(ron['first'], ron['second']) < len(tree['inputs']), 'Invalid raw RON pair')
            qc.require(tree['inputs'][ron['first']]['path'] != tree['inputs'][ron['second']]['path'], 'RON needs two distinct files')
            qc.require(ron['stdev_available'] == tree['raw_difference']['stdev_available'] and
                       ron['mad_available'] == tree['raw_difference']['mad_available'], 'RON availability mismatch')
        else:
            qc.require(not ron['stdev_available'] and not ron['mad_available'], 'RON without explicit pair')
        qc.require(all(type(ron[k]) in (int, float) and math.isfinite(ron[k]) and ron[k] >= 0
                       for k in ('stdev_adu', 'mad_adu')), 'Invalid RON values')
        high = tree['high_offset']
        qc.require(_flag(high['available']) and _flag(high['degenerate']) and _integer(high['count']) and
                   type(high['locations']) is list and high['count'] == len(high['locations']), 'Invalid high-offset diagnostics')
        qc.require(type(high['sigma']) in (int, float) and math.isfinite(high['sigma']) and high['sigma'] > 0 and
                   type(high['threshold']) in (int, float) and math.isfinite(high['threshold']), 'Invalid high-offset threshold')
        locations = high['locations']
        bounds = tree['master']['zone']
        qc.require(all(type(p) is list and len(p) == 2 and all(_integer(v) for v in p) and
                       bounds[0] <= p[0] <= bounds[1] and bounds[2] <= p[1] <= bounds[3] for p in locations), 'High-offset locations outside master')
        qc.require(len({tuple(p) for p in locations}) == len(locations), 'Duplicate high-offset location')
        qc.require(high['available'] == tree['master']['mad_available'] and
                   (high['available'] or (not high['count'] and not high['degenerate'])), 'High-offset availability mismatch')
        qc.require(Path(tree['output']).is_absolute() and Path(tree['configuration_record']).is_absolute(), 'Explicit absolute product/configuration paths required')
        qc.encoded(tree)  # Reject nonfinite values anywhere, including extensions.
    except (KeyError, TypeError, ValueError) as error:
        raise qc.QcError('Invalid native bias handoff: ' + str(error)) from error
    return tree


def _source(path, tree, hdu):
    return dict(file_id=path, detector_id=tree['detector_id'], hdu_index=hdu)


def _mask(tree, sample, stage):
    if stage in ('prescan', 'overscan'):
        return dict(status='not_applicable', reason='electronic_empty_reads_not_detector_pixels')
    if not sample['bpm_supplied']:
        return dict(status='omitted' if not tree['bpm']['selected'] else 'unmasked_diagnostic')
    return dict(status='applied', **deepcopy(tree['bpm']))


def _add_sample(builder, tree, stage, sample, sources):
    detector = tree['detector_id']
    region = dict(coordinates='FITS-1-based-inclusive', bounds=sample['zone'],
                  detector_bpm=_mask(tree, sample, stage), clipping='none', nonfinite='excluded')
    for suffix, field, method, scale in (
        ('mean', 'mean', 'arithmetic_mean', 1), ('median', 'median', 'median_averaged_central_pair', 1),
        ('stdev', 'stdev', 'sample_standard_deviation_n_minus_1', 1),
        ('scaled_mad', 'mad', '1.4826_times_median_absolute_deviation', 1.4826)):
        available = sample['level_available'] if field in ('mean', 'median') else sample[field+'_available']
        name = stage+'.'+suffix
        if available:
            builder.add_measurement(detector, name=name, value=sample[field]*scale, unit='ADU',
                definition=dict(stage=STAGES[stage], method=method, region=region, sample_count=sample['valid_pixels']), sources=sources)
        else:
            builder.add_unavailable(detector, name=name, unit='ADU', stage=STAGES[stage],
                reason='not_requested_or_insufficient_samples', sources=sources)
    for count in ('region_pixels', 'bpm_excluded', 'nonfinite_excluded', 'valid_pixels'):
        if sample['region_pixels']:
            builder.add_measurement(detector, name=stage+'.'+count, value=sample[count], unit='count',
                definition=dict(stage=STAGES[stage], method='explicit_sample_partition', region=region,
                                sample_count=sample['region_pixels']), sources=sources)
        else:
            builder.add_unavailable(detector, name=stage+'.'+count, unit='count', stage=STAGES[stage], reason='region_not_configured', sources=sources)


def publish_handoff(path, directory, *, assessment_id, created_at):
    """Assemble all records before publication; publish leaves then product.

    Conflicts fail without overwriting. A later I/O failure may retain completed
    leaves; a product is published only after its frozen leaves are verified.
    Choose a fresh explicit destination for a new assessment.
    """
    tree = load_handoff(path)
    directory = Path(directory).resolve(strict=True)
    qc.require(directory.is_dir() and qc.text(assessment_id), 'Explicit QC destination/assessment required')
    qc.timestamp(created_at)
    config = Path(tree['configuration_record']).resolve(strict=True)
    qc.require(config.is_file() and config.stat().st_size <= qc.MAX_RECORD_BYTES, 'Invalid configuration snapshot')
    qc.require(type(tree['configuration']) is dict and tree['configuration'] == json.loads(config.read_text()),
               'Configuration snapshot differs from the settings used by the native operation')
    configuration_id = 'sha256:' + hashlib.sha256(json.dumps(tree['configuration'],
        sort_keys=True,allow_nan=False,separators=(',', ':')).encode()).hexdigest()
    names = [qc.qc_filename(Path(m['path']).name) for m in tree['inputs']]
    if tree['bpm']['selected']:
        names.append(qc.qc_filename(Path(tree['bpm']['path']).name))
    names.append(qc.qc_filename(Path(tree['output']).name))
    qc.require(len(set(names)) == len(names), 'QC basenames collide; use an explicit separate assessment')
    qc.require(all(not (directory/n).exists() and not (directory/n).is_symlink() for n in names), 'QC destination conflicts; no overwrite')

    def builder(location, kind, hdu, suffix):
        return qc.BiasQcRecipe(file=dict(id=location, filename=Path(location).name, location=location,
            kind=kind, sha256=None, observed_at=None,
            selectors=[dict(detector_id=tree['detector_id'], hdu_index=hdu,
                            configuration_detector=tree['configuration_detector'])],
            context=dict(readout_id=tree['readout_id'], bin_x=tree['bin_x'], bin_y=tree['bin_y'])),
            assessment_id=assessment_id+':'+suffix, created_at=created_at,
            producer=tree['producer'], operation='cal.bias', configuration_id=configuration_id)

    leaves = []
    for index, member in enumerate(tree['inputs']):
        b = builder(member['path'], 'raw', tree['input_hdu'], str(index))
        source = [_source(member['path'], tree, tree['input_hdu'])]
        for stage in ('raw_active', 'corrected_active', 'prescan', 'overscan'):
            _add_sample(b, tree, stage, member[stage], source)
        profile = member['scan_correction']
        for quantity,method in (('median','legacy_median_of_row_corrections'),
                                ('stdev','legacy_sample_stdev_of_row_corrections')):
            b.add_measurement(tree['detector_id'],name='scan_correction.'+quantity,
                value=profile[quantity],unit='ADU',
                definition=dict(stage='scan_correction_profile',method=method,
                    region=dict(coordinates='FITS-1-based-rows',bounds=[1,profile['rows']],
                        prescan_used=bool(profile['prescan_used']),overscan_used=bool(profile['overscan_used']),
                        rejected_per_row=profile['rejection'],
                        detector_bpm=dict(status='not_applicable',reason='electronic_empty_reads_not_detector_pixels')),
                    sample_count=profile['rows']),sources=source)
        b.add_extension('bias', dict(native_handoff_version=1, bpm=deepcopy(tree['bpm']),
            scan_detector_bpm='not_applicable_electronic_empty_reads'))
        leaves.append(b.seal())
    bpm_record = None
    if tree['bpm']['selected']:
        binding = builder(tree['bpm']['path'], 'product', tree['bpm']['hdu'], 'bpm')
        binding.add_extension('bias_binding', dict(role='bpm', binding=deepcopy(tree['bpm']),
            scope='selected_calibration_binding_only_not_BPM_generation_or_reassessment'))
        bpm_record = binding.seal()
    parent = builder(tree['output'], 'product', tree['output_hdu'], 'product')
    for index, leaf in enumerate(leaves):
        accepted = tree['inputs'][index]['accepted']
        parent.add_input(leaf, qc_path=names[index], participation='used' if accepted else 'rejected',
                         reason=None if accepted else 'native_frame_mean_rejection')
    if bpm_record is not None:
        parent.add_input(bpm_record, qc_path=names[len(leaves)], participation='used')
    product_source = [_source(tree['output'], tree, tree['output_hdu'])]
    for stage in ('master', 'master_unmasked'):
        _add_sample(parent, tree, stage, tree[stage], product_source)
    ron = tree['ron']
    pair_sources = [_source(tree['inputs'][ron[k]]['path'], tree, tree['input_hdu'])
                    for k in ('first', 'second')] if ron['pair_set'] else []
    for name, flag, value, method in (
        ('read_noise', 'stdev_available', 'stdev_adu', 'sample_stdev_raw_difference_div_sqrt2'),
        ('read_noise.mad', 'mad_available', 'mad_adu', '1.4826_MAD_raw_difference_div_sqrt2')):
        if ron[flag]:
            sample = tree['raw_difference']
            parent.add_measurement(tree['detector_id'], name=name, value=ron[value], unit='ADU',
                definition=dict(stage=STAGES['raw_difference'], method=method,
                    region=dict(coordinates='FITS-1-based-inclusive', bounds=sample['zone'],
                                detector_bpm=_mask(tree, sample, 'raw_difference'), correction='none'),
                    sample_count=sample['valid_pixels']), sources=pair_sources)
        else:
            parent.add_unavailable(tree['detector_id'], name=name, unit='ADU', stage=STAGES['raw_difference'],
                reason='pair_not_requested_or_insufficient_samples', sources=pair_sources)
    high = tree['high_offset']
    for name, value, unit in (('pixels.hot', high['count'], 'count'),
                              ('pixels.hot.threshold', high['threshold'], 'ADU')):
        if high['available']:
            parent.add_measurement(tree['detector_id'], name=name, value=value, unit=unit,
                definition=dict(stage=STAGES['master'], method='all_master_pixels_above_masked_median_plus_k_scaled_MAD',
                    region=dict(coordinates='FITS-1-based-inclusive', bounds=tree['master']['zone'], k=high['sigma']),
                    sample_count=tree['master']['region_pixels']), sources=product_source)
        else:
            parent.add_unavailable(tree['detector_id'], name=name, unit=unit, stage=STAGES['master'], reason='MAD_not_requested', sources=product_source)
    parent.add_extension('bias', dict(native_handoff_version=1, bpm=deepcopy(tree['bpm']),
        input_roles=['raw_bias']*len(leaves)+(['bpm'] if bpm_record is not None else []),
        scan_detector_bpm='not_applicable_electronic_empty_reads',
        high_offset=dict(locations=high['locations'], coordinates='FITS-1-based-active',
                         threshold_degenerate=bool(high['degenerate']), physical_quantity='high_bias_offset_not_dark_current')))
    for name in ('master.mean', 'master.median', 'master.stdev', 'master.scaled_mad'):
        parent.summarize_detectors(name)
    product = parent.seal()
    # Use exactly the same schema/ASDF writer and frozen-reference verification.
    qc._asdf()  # Dependency check before publishing any leaf.
    for leaf in leaves + ([bpm_record] if bpm_record is not None else []):
        qc.write_record(leaf, directory, qc_root=directory)
    destination = qc.write_record(product, directory, qc_root=directory)
    return destination


def run_bias_recipe(adapter, native_arguments, directory, *, assessment_id, created_at, receipt):
    """Complete one bias invocation through the existing native and QC paths.

    No numerical defaults, retries, input staging or deletion. Completion means
    the native FITS operation, shared ASDF publication and link verification all
    succeeded. An error retains complete products/records from earlier stages.
    The exclusively created JSON receipt is execution evidence, not saved QC.
    """
    adapter = Path(adapter)
    qc.require(adapter.is_absolute(), 'Explicit absolute native adapter required')
    adapter = adapter.resolve(strict=True)
    qc.require(adapter.is_file() and os.access(adapter, os.X_OK), 'Native adapter is not executable')
    argv = list(native_arguments)
    qc.require(argv[:2] == ['cal', 'bias'] and (len(argv)-2) % 2 == 0,
               'Require explicit cal bias arguments as key/value pairs')
    options = {}
    for key, value in zip(argv[2::2], argv[3::2]):
        qc.require(qc.text(key) and key.startswith('--') and qc.text(value) and key not in options,
                   'Invalid/duplicate native argument')
        options[key] = value
    required = ('--output', '--qc-record', '--config-record', '--log-path', '--work-dir', '--detector-id')
    qc.require(all(key in options for key in required) and options.get('--measurements') == 'yes' and
               options.get('--mad') in ('yes', 'no'), 'Require explicit output paths and measurement/MAD choices')
    for key in required[:-1]:
        qc.require(Path(options[key]).is_absolute(), 'Require absolute native paths')
    directory = Path(directory).resolve(strict=True)
    qc.require(directory.is_dir() and qc.text(assessment_id), 'Explicit QC directory/assessment required')
    qc.timestamp(created_at)
    receipt = Path(receipt)
    qc.require(receipt.is_absolute() and receipt.parent.is_dir(), 'Explicit receipt in an existing directory required')
    targets = [Path(options[key]) for key in required[:4]] + [receipt]
    qc.require(len({p.resolve() for p in targets}) == len(targets), 'Output/receipt paths collide')
    evidence = dict(status='running', stage='preflight', operation='cal.bias',
        adapter=str(adapter), adapter_sha256=hashlib.sha256(adapter.read_bytes()).hexdigest(),
        completion_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        argv=[str(adapter), *argv], native_exit_status=None, native_product=options['--output'],
        qc_product=None, assessment_id=assessment_id, created_at=created_at)
    # Exclusive creation protects an earlier receipt, including dangling links.
    with receipt.open('x', encoding='utf-8') as stream:
        def save():
            stream.seek(0)
            stream.truncate()
            json.dump(evidence, stream, allow_nan=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        try:
            save()
            qc.require(all(not p.exists() and not p.is_symlink() for p in targets[:-1]),
                       'Native output/log/handoff/configuration conflict; no overwrite')
            qc.require(Path(options['--work-dir']).is_dir(), 'Native work directory must exist')
            product_qc = directory / qc.qc_filename(Path(options['--output']).name)
            qc.require(not product_qc.exists() and not product_qc.is_symlink(), 'Product QC conflict; no overwrite')
            qc.require(qc.SCHEMA_PATH.is_file(), 'Shared QC schema resource is missing')
            qc._asdf()  # Fail before native processing if the writer is unavailable.
            evidence['stage'] = 'native'
            save()
            result = subprocess.run(evidence['argv'], cwd=options['--work-dir'], check=False)
            evidence['native_exit_status'] = result.returncode
            qc.require(result.returncode == 0, 'Native bias command failed; retain native log and execution receipt')
            evidence['stage'] = 'qc'
            save()
            handoff = load_handoff(options['--qc-record'])
            qc.require(handoff['output'] == options['--output'] and
                       handoff['configuration_record'] == options['--config-record'] and
                       handoff['detector_id'] == options['--detector-id'], 'Native handoff does not match this invocation')
            qc.require(Path(options['--output']).is_file(), 'Native command did not publish its FITS product')
            destination = publish_handoff(options['--qc-record'], directory,
                assessment_id=assessment_id, created_at=created_at)
            evidence['qc_product'] = str(destination)
            evidence['stage'] = 'verify'
            save()
            records = list(qc.traverse_records(destination, qc_root=directory,
                max_records=len(handoff['inputs']) + 1 + int(handoff['bpm']['selected'])))
            parent = qc.read_record(destination)
            tree = parent.as_dict()
            qc.require(tree['file']['location'] == options['--output'] and
                       tree['record']['assessment_id'] == assessment_id+':product' and
                       tree['provenance']['producer'] == handoff['producer'], 'Saved product QC identity mismatch')
            evidence.update(status='complete', stage='complete', qc_records_verified=len(records),
                            qc_record_digest=parent.digest, producer=handoff['producer'])
            save()
            return destination
        except BaseException as error:
            evidence.update(status='failed', error=dict(type=type(error).__name__, message=str(error)))
            save()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--handoff', type=Path, help='Save QC for an already completed native attempt')
    parser.add_argument('--native-adapter', type=Path, help='Run one complete bias recipe; native arguments follow --')
    parser.add_argument('--receipt', type=Path, help='Fresh execution receipt for a complete invocation')
    parser.add_argument('--qc-directory', type=Path, required=True)
    parser.add_argument('--assessment-id', required=True)
    parser.add_argument('--created-at', required=True)
    parser.add_argument('native_arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        if args.native_adapter:
            qc.require(args.handoff is None and args.receipt is not None,
                       'Complete invocation requires --receipt, without --handoff')
            native = args.native_arguments
            if native[:1] == ['--']:
                native = native[1:]
            destination = run_bias_recipe(args.native_adapter, native, args.qc_directory,
                assessment_id=args.assessment_id, created_at=args.created_at, receipt=args.receipt)
            print('BIAS_RECIPE complete', destination)
        else:
            qc.require(args.handoff is not None and args.receipt is None and not args.native_arguments,
                       'Writer-only invocation requires --handoff, without native arguments/receipt')
            print('QC_PRODUCT', publish_handoff(args.handoff, args.qc_directory,
                  assessment_id=args.assessment_id, created_at=args.created_at))
    except (qc.QcError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, 'Bias attempt failed: '+str(error)+'\nRetain its receipt, logs and any completed files.\n')


if __name__ == '__main__':
    main()
