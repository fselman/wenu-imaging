#!/usr/bin/env python3
"""Author project/recipe controls and import immutable calibration bytes; no reduction."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_linearity_config as configuration
import pycavi_linearity_recipe as preparation
import pycavi_bpm_linearity_plan as planner
require = preparation.require


def project_text(raw, controls, reduced, resolved, readout):
    def section(name, values):
        return '\n['+name+']\n'+''.join(k+' = '+json.dumps(v)+'\n' for k, v in values.items())
    instrument = resolved['instrument']
    text = 'project_schema_version = 2\n'
    text += section('project', dict(schema_version=1, id=instrument+':test-project', name=instrument+' characterization'))
    text += section('project.roots', {k: os.path.relpath(v, controls) for k, v in dict(
        raw=raw, calibration=reduced/'cal', output=reduced, work=reduced/'work', logs=reduced/'logs').items()})
    text += section('association', dict(schema_version=1, mode='explicit', bindings=[]))
    text += section('reduction_profile', dict(schema_version=1, id=instrument+':scientific', purpose='scientific'))
    text += section('recipe', dict(schema_version=1, id=instrument+':bpm-linearity'))
    for name, operation in [('measure-linearity', 'mef_cal_linearity'), ('characterize-bpm', 'mef_cal_bpm')]:
        text += '\n[[recipe.steps]]\n'+f'id = {json.dumps(name)}\noperation = {json.dumps(operation)}\n'
    # This existing project descriptor does not activate a generic executor.
    # The recipe's explicit --execute command remains the execution entry point.
    text += section('execution', dict(schema_version=1, activation='disabled', mode='serial', workers=1, numerical_threads=1, niceness=10))
    text += section('quality', dict(schema_version=1, policy='record_only', estimator_status='not_qualified', thresholds=[]))
    text += section('product_profile', dict(schema_version=1, id=instrument+':calibration', target='legacy',
        compliance='not_validated', variance_contract='pre_m6a_unavailable'))
    text += section('processing', dict(schema_version=1, native_mode='legacy_reference', native_configuration='characterization-native.toml'))
    text += section('readout', dict(schema_version=1, id=readout, authority='configured', metadata_policy='explicit_review',
        header_evidence=[], mapping_status='unverified', inventory_status='not_established'))
    for detector in resolved['detectors']:
        text += '\n[[readout.detectors]]\n'+f'id = {json.dumps(detector["detector_id"])}\n'
        text += f'legacy_ordinal = {detector["configuration_detector"]+1}\nidentity_status = "unknown"\n'
        text += '\n[[readout.detectors.channels]]\n'+f'id = {json.dumps(detector["amplifier_id"])}\nidentity_status = "unknown"\nactive = true\n'
        use = bool(detector['native_settings']['use_overscan'])
        text += section('readout.detectors.channels.overscan', dict(state='defined', subtract=use))
        lo, hi = detector['native_settings']['overscan']
        text += section('readout.detectors.channels.overscan.region', dict(x_min=lo, x_max=hi,
            y_min=1, y_max=detector['raw_size'][1], unit='pixel', convention='fits-1-based-inclusive'))
    return text


def import_calibration(source, destination, expected):
    """Copy complete FITS bytes and verify their frozen digest; never decode pixels."""
    def identity():
        value = source.stat()
        return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_mode
    before = identity()
    destination.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    temporary = destination.with_name(destination.name+'.importing')
    with source.open('rb') as incoming, temporary.open('xb') as outgoing:
        for block in iter(lambda: incoming.read(1024*1024), b''):
            h.update(block); outgoing.write(block)
        outgoing.flush(); os.fsync(outgoing.fileno())
    require(identity() == before and h.hexdigest() == expected, 'Calibration source differs from preserved bytes')
    require(preparation.image_fingerprint(temporary)['sha256'] == expected, 'Calibration copy verification failed')
    temporary.chmod(0o444)
    os.link(temporary, destination)
    temporary.unlink()
    return dict(source=str(source), path=str(destination), sha256=expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('orchestration', 'raw', 'reduced', 'samples', 'handoff', 'bpm', 'native-preparation', 'assembly'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--native-revision', required=True)
    parser.add_argument('--assembly-revision', required=True)
    parser.add_argument('--detector', required=True)
    parser.add_argument('--detector-config', type=Path, required=True)
    parser.add_argument('--processing-config', type=Path, required=True)
    parser.add_argument('--upper-fraction', type=float, required=True)
    parser.add_argument('--minimum-span', type=float, required=True)
    parser.add_argument('--maximum-pair-difference', type=float, required=True)
    parser.add_argument('--prepare', action='store_true', help='Write fresh controls and byte-identical calibration copies')
    args = parser.parse_args()
    controls, raw = args.orchestration.resolve(strict=True), args.raw.resolve(strict=True)
    reduced = args.reduced.resolve(strict=True)
    detector_config = args.detector_config.resolve(strict=True)
    processing_config = args.processing_config.resolve(strict=True)
    resolved = configuration.resolve_files(detector_config, processing_config)
    dependencies = preparation.preparation_dependencies(args.samples, args.handoff, resolved)
    require(dependencies['selection']['detector'] == args.detector, 'Pilot detector differs from source archive')
    require(all(Path(r['path']).resolve(strict=True).is_relative_to(raw)
                for r in dependencies['selection']['flat']+dependencies['biases']), 'Observation outside raw root')
    targets = {name: controls/name for name in ('project.toml', 'detector.toml',
        'processing.toml', 'characterization-native.toml', 'bpm-linearity-recipe.toml')}
    require(all(not p.exists() and not p.is_symlink() for p in targets.values()), 'Project controls already exist; retain them')
    print('ADMITTED ORIGINAL:', args.samples, flush=True)
    print('DETECTOR:', args.detector, '| FLATS:', len(dependencies['selection']['flat']), flush=True)
    print('PROCESSING CONTROLS:', json.dumps(resolved['controls']), flush=True)
    if not args.prepare:
        print('Metadata preview only; pass --prepare to author project/recipe and calibration copies.')
        return
    for path in (reduced/'cal', reduced/'work', reduced/'logs', reduced/'cal/bpm-linearity'):
        path.mkdir(exist_ok=True)
    imports = Path(tempfile.mkdtemp(prefix='characterization-', dir=reduced/'cal'))
    copies = []
    for source in (dependencies['master']['product'], dependencies['selection']['bpm']['path']):
        copies.append(import_calibration(Path(source), imports/Path(source).name, dependencies['baseline'][source]))
    texts = {'project.toml': project_text(raw, controls, reduced, resolved, dependencies['selection']['readout_id']), 'detector.toml': detector_config.read_text(),
             'processing.toml': processing_config.read_text(), 'characterization-native.toml': dependencies['configuration']}
    run = Path(tempfile.mkdtemp(prefix='pilot-CCD65-', dir=reduced/'cal/bpm-linearity'))
    text = 'bpm_linearity_recipe_schema_version = 1\nproject = "project.toml"\n'
    text += 'run = '+json.dumps(run.relative_to(reduced).as_posix())+'\n'
    sections = dict(native=dict(bpm=str(args.bpm.resolve(strict=True)), preparation=str(args.native_preparation.resolve(strict=True)),
        source_revision=args.native_revision), assembly=dict(executable=str(args.assembly.resolve(strict=True)),
        source_revision=args.assembly_revision, reference_detector=args.detector),
        preparation=dict(detector_toml='detector.toml', processing_toml='processing.toml'),
        bpm=dict(acquisition='quick', output_mode='new', upper_fraction=args.upper_fraction,
                 minimum_span_fraction=args.minimum_span, maximum_pair_difference=args.maximum_pair_difference))
    for name, values in sections.items():
        text += '\n['+name+']\n'+''.join(k+' = '+json.dumps(v)+'\n' for k, v in values.items())
    selected = next(d for d in resolved['detectors'] if d['detector_id'] == args.detector)
    text += '\n[[detectors]]\n'+''.join(k+' = '+json.dumps(v)+'\n' for k, v in dict(detector_id=args.detector,
        source_samples=str(args.samples.resolve(strict=True)), handoff=str(args.handoff.resolve(strict=True)),
        reference_rois=[r['id'] for r in selected['rois']]).items())
    for row in copies:
        text += '\n[[calibration_bindings]]\n'+''.join(k+' = '+json.dumps(v)+'\n' for k, v in dict(
            source=row['source'], path=Path(row['path']).relative_to(reduced/'cal').as_posix(), sha256=row['sha256']).items())
    texts['bpm-linearity-recipe.toml'] = text
    for name, value in texts.items():
        with targets[name].open('x') as stream:
            stream.write(value)
    plan = planner.admit(targets['bpm-linearity-recipe.toml'])
    receipt = dict(status='metadata_admitted_no_reduction', recipe=str(targets['bpm-linearity-recipe.toml']),
        run=str(run), calibration_copies=copies, metadata_sha256=plan['metadata'], native=plan['native'],
        processing_controls=resolved['controls'])
    with (imports/'import.json').open('x') as stream:
        json.dump(receipt, stream, indent=2); stream.write('\n')
    print('READY:', targets['project.toml'], flush=True)
    print('RECIPE:', targets['bpm-linearity-recipe.toml'], flush=True)
    print('REDUCED RUN:', run, flush=True)
    print('COPY RECEIPT:', imports/'import.json', flush=True)
    print('PASS: project/recipe admitted; calibration bytes preserved; no reduction performed.', flush=True)


if __name__ == '__main__':
    main()
