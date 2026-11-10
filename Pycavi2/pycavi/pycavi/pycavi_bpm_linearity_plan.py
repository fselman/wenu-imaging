"""Closed combined-recipe admission. Metadata only; no FITS pixel access."""
import hashlib
import math
from pathlib import Path
import tomllib
try:
    from .pycavi_configuration import ProjectComposition
    from . import pycavi_linearity_config as configuration
    from . import pycavi_linearity_recipe as preparation
    from . import pycavi_calibration_bindings as calibrations
except ImportError:
    from pycavi_configuration import ProjectComposition
    import pycavi_linearity_config as configuration
    import pycavi_linearity_recipe as preparation
    import pycavi_calibration_bindings as calibrations
require = preparation.require
ROOT = Path(__file__).resolve().parents[3]


def fields(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected), 'Unknown/incomplete '+label)


def reference(base, value):
    require(type(value) is str and value.strip(), 'Nonempty path required')
    return (base/value).resolve(strict=True)


def admit(path):
    path = Path(path).resolve(strict=True)
    data = tomllib.loads(path.read_text())
    fields(data, ('bpm_linearity_recipe_schema_version', 'project', 'run',
                  'preparation', 'bpm', 'detectors') + tuple(k for k in ('native', 'assembly', 'calibration_bindings', 'native_recipe', 'qc') if k in data), 'combined recipe')
    require(type(data['bpm_linearity_recipe_schema_version']) is int and
            data['bpm_linearity_recipe_schema_version'] == 1, 'Unsupported combined recipe')
    project_path = reference(path.parent, data['project'])
    project = ProjectComposition(ROOT).resolve_project(project_path)
    roots = project['roots']
    layout = dict(raw=roots['raw'], orchestration=str(project_path.parent),
                  reduced=roots['output'], calibration=roots['calibration'], work=roots['work'], logs=roots['logs'])
    require(path.is_relative_to(project_path.parent), 'Recipe must be in orchestration')
    run = data['run']
    require(type(run) is str and run and not Path(run).is_absolute() and
            all(part not in ('.', '..') for part in Path(run).parts), 'Relative output run required')
    run = (Path(roots['output'])/run).resolve(strict=True)
    require(run.is_relative_to(Path(roots['output'])) and run != Path(roots['output']) and
            run.is_dir() and not any(run.iterdir()), 'Fresh empty reduced run directory required')
    require(type(data.get('qc', True)) is bool, 'qc must be true or false')
    native_recipe = data.get('native_recipe')
    require(native_recipe is not None or data.get('qc', True), 'QC-off requires the native shared-cube recipe')
    assembly = data.get('assembly')
    require(('native' in data) != (native_recipe is not None), 'Select one native recipe or legacy stage producers')
    if native_recipe is not None:
        fields(native_recipe, ('executable', 'source_revision'), 'native recipe')
        native_recipe = dict(native_recipe)
        native_recipe['executable'] = str(reference(path.parent, native_recipe['executable']))
        revision = native_recipe['source_revision']
        fields(assembly, ('reference_detector',), 'native assembly')
        assembly = dict(assembly, executable=native_recipe['executable'], source_revision=revision)
        binaries = dict(bpm=native_recipe['executable'], preparation=native_recipe['executable'], assembly=native_recipe['executable'])
    else:
        fields(data['native'], ('bpm', 'preparation', 'source_revision'), 'native producers')
        revision = data['native']['source_revision']
        binaries = {name: str(reference(path.parent, data['native'][name])) for name in ('bpm', 'preparation')}
        if assembly is not None:
            fields(assembly, ('executable', 'source_revision', 'reference_detector'), 'assembly')
            require(type(assembly['source_revision']) is str and len(assembly['source_revision']) == 40 and
                    set(assembly['source_revision']) <= set('0123456789abcdef'), 'Exact assembly revision required')
            binaries['assembly'] = str(reference(path.parent, assembly['executable']))
    require(type(revision) is str and len(revision) == 40 and
            set(revision) <= set('0123456789abcdef'), 'Exact native source revision required')
    fields(data['preparation'], ('detector_toml', 'processing_toml') +
           (('input_bpm',) if 'input_bpm' in data['preparation'] else ()), 'preparation configuration')
    input_bpm = data['preparation'].get('input_bpm', 'archived')
    require(input_bpm in ('archived', 'omitted'), 'input_bpm must be archived or omitted')
    require(native_recipe is not None or input_bpm=='archived', 'Explicit BPM omission requires the native recipe')
    controls = {name: reference(path.parent, data['preparation'][name])
                for name in ('detector_toml', 'processing_toml')}
    require(all(p.is_relative_to(project_path.parent) for p in controls.values()),
            'Detector/processing TOMLs must be in orchestration')
    resolved = configuration.resolve_files(controls['detector_toml'], controls['processing_toml'])
    policy = data['bpm']
    fields(policy, ('acquisition', 'output_mode', 'upper_fraction', 'minimum_span_fraction',
                    'maximum_pair_difference') + tuple(k for k in ('response_low', 'response_high') if k in policy), 'BPM controls')
    response_limits = None
    if native_recipe is not None:
        response_limits = {key: policy.get(key, default) for key, default in
                           (('response_low', 0.5), ('response_high', 1.5))}
        preparation.bpm_configuration_snapshot({}, response_limits)
        policy.update(response_limits)
    else:
        require(not any(k in policy for k in ('response_low', 'response_high')),
                'Response limits require the native shared-cube recipe')
    require(policy['acquisition'] in ('quick', 'provisional') and policy['output_mode'] in ('new', 'combined'),
            'Explicit supported BPM acquisition/output mode required')
    for key, positive in [('upper_fraction', True), ('minimum_span_fraction', True), ('maximum_pair_difference', False)]:
        value = policy[key]
        require(type(value) in (int, float) and math.isfinite(value) and (value > 0 if positive else value >= 0),
                'Invalid BPM '+key)
    require(policy['upper_fraction'] <= 1 and policy['minimum_span_fraction'] <= 1, 'BPM fraction exceeds one')
    require(isinstance(data['detectors'], list) and 0 < len(data['detectors']) <= len(resolved['detectors']),
            'Explicit nonempty detector selection required')
    catalogue = {d['detector_id']: (i, d) for i, d in enumerate(resolved['detectors'])}
    bindings = calibrations.resolve(data.get('calibration_bindings', []), roots['calibration'])
    used_bindings = set()
    entries, positions, baseline, metadata = [], [], {}, {}
    for index, entry in enumerate(data['detectors']):
        fields(entry, ('detector_id', 'source_samples', 'handoff', 'reference_rois'), 'detector entry')
        require(type(entry['detector_id']) is str and entry['detector_id'] in catalogue, 'Unknown detector')
        position, detector = catalogue[entry['detector_id']]
        positions.append(position)
        dependencies = preparation.preparation_dependencies(reference(path.parent, entry['source_samples']),
            reference(path.parent, entry['handoff']), resolved, input_bpm=input_bpm)
        dependencies = calibrations.bind(dependencies, resolved, bindings, roots['calibration'])
        if response_limits is not None:
            dependencies['bpm_response_limits'] = response_limits
            effective = preparation.bpm_configuration_snapshot(dependencies['master_snapshot'], response_limits)
            dependencies['configuration'] = preparation.native_configuration(resolved, effective)
        used_bindings.update(r['source'] for r in dependencies.get('calibration_bindings', []))
        require(dependencies['selection']['detector'] == entry['detector_id'], 'Detector dependency differs')
        ids = entry['reference_rois']
        rois = {r['id']: r for r in detector['rois']}
        require(isinstance(ids, list) and ids and all(type(v) is str and v in rois for v in ids) and
                len(set(ids)) == len(ids), 'Explicit unique BPM reference ROI names required')
        selection = dependencies['selection']
        require(selection['bpm']['encoding'] in ('binary', 'reason8', 'omitted'), 'Explicit prior-mask policy required')
        creating = native_recipe is None or selection['bpm']['encoding'] == 'omitted'
        if creating and policy['output_mode'] == 'combined':
            require(selection['bpm']['encoding'] == 'reason8', 'Combined BPM requires known prior reason bits')
        pairs = {row['pair'] for row in selection['flat']}
        require(not creating or policy['acquisition'] != 'quick' or len(pairs) >= 5, 'Quick BPM requires at least five pairs')
        for target, incoming in ((baseline, dependencies['baseline']), (metadata, dependencies['metadata_sha256'])):
            for name, digest in incoming.items():
                require(name not in target or target[name] == digest, 'Conflicting shared input digest: '+name)
                target[name] = digest
        crop = detector['retained']
        active_pixels = (crop[1]-crop[0]+1)*(crop[3]-crop[2]+1)
        loaded_pixels = len(selection['flat'])*math.prod(detector['raw_size'])+2*active_pixels
        require(loaded_pixels <= selection['max_loaded_pixels'], 'BPM input planes exceed the admitted loaded-pixel limit')
        key = str(Path(run.name)/f'detector-{index:03d}')
        entries.append(dict(detector=detector, dependencies=dependencies, key=key, bpm_loaded_pixels=loaded_pixels,
            reference_rois=[[rois[name][k] for k in ('xmin', 'xmax', 'ymin', 'ymax')] for name in ids]))
    require(used_bindings == {row['source'] for row in bindings}, 'Unused calibration copy binding')
    require(positions == sorted(set(positions)), 'Select unique detectors in detector-TOML catalogue order')
    if assembly is not None:
        require(assembly['reference_detector'] in [e['detector']['detector_id'] for e in entries], 'Explicit selected assembly reference required')
        common = entries[0]['dependencies']['selection']
        for entry in entries[1:]:
            selected = entry['dependencies']['selection']
            require([r['path'] for r in selected['flat']] == [r['path'] for r in common['flat']],
                    'Assembly requires common ordered flat inputs')
    sources = {item['path']: item['sha256'] for item in project['sources']}
    sources[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    native_reference = Path(project['native_configuration'])
    sources[str(native_reference)] = hashlib.sha256(native_reference.read_bytes()).hexdigest()
    for name, item in resolved['sources'].items():
        sources[resolved['source_paths'][name]] = item['sha256']
    sources[project['catalog']['path']] = project['catalog']['sha256']
    code_paths = [Path(__file__).with_name(name+'.py') for name in ('pycavi_bpm_linearity_plan',
        'pycavi_bpm_linearity_recipe', 'pycavi_bpm_linearity_native', 'pycavi_bpm_linearity_assembly', 'pycavi_linearity_recipe',
        'pycavi_linearity_native_archive', 'pycavi_native_product_qc', 'pycavi_calibration_bindings',
        'pycavi_bpm_linearity_native_recipe')]
    code_paths.append(ROOT/'tools/run-bpm-linearity.py')
    code_sources = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in code_paths}
    metadata.update(sources)
    metadata.update(code_sources)
    for root in ('orchestration', 'work', 'logs'):
        require(not (Path(layout[root])/run.name).exists(), 'Batch control/work/log destination exists')
    # Reuse the same directory/input admission as the single-detector recipe.
    for entry in entries:
        preparation.validate_preparation_inputs(entry['dependencies'], layout)
    return dict(recipe_path=str(path), qc=data.get('qc', True), native_recipe=native_recipe, assembly=assembly, run=str(run), layout=layout, resolved=resolved, native=binaries, source_revision=revision,
                bpm=policy, entries=entries, baseline=baseline, metadata=metadata, configuration_sources=sources, coordinator_sources=code_sources)
