"""Admit archived metadata, author native bindings, invoke one native recipe.

No detector-stage subprocesses, pixel calculations or Python QC publication.
The C coordinator owns execution, image preservation and final MEF/ASDF output.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tomllib
try:
    from . import pycavi_bpm_linearity_recipe as coordinator
    from . import pycavi_bpm_linearity_native as bpm
    from . import pycavi_linearity_native_archive as preparation
except ImportError:
    import pycavi_bpm_linearity_recipe as coordinator
    import pycavi_bpm_linearity_native as bpm
    import pycavi_linearity_native_archive as preparation
require = coordinator.require
START = '${START}'


def quoted(value):
    return json.dumps(str(value), ensure_ascii=True)


def write_preparation_controls(controls, dependencies):
    for name, text in [('native.toml', dependencies['configuration']),
                       *[(name+'.tsv' if name == 'plan' else name+'.toml', text)
                         for name, text in dependencies['transport'].items() if name != 'detector']]:
        (controls/name).write_text(text)
    lines = ['input_index\thdu\tasset\tpath\taccepted\n']
    for row in dependencies['biases']:
        cells = [str(row[k]) for k in ('index', 'hdu', 'asset', 'path', 'accepted')]
        require(all(not any(c in v for c in '\t\r\n\0') for v in cells), 'Invalid bias transport cell')
        lines.append('\t'.join(cells)+'\n')
    (controls/'biases.tsv').write_text(''.join(lines))


def preparation_binding(plan, entry, destination, controls, directories, copies):
    d = entry['dependencies']
    native = Path(plan['layout']['work'])/entry['key']/'preparation/native'
    log = Path(plan['run'])/('CMDP.'+START+'.001.log')
    product = destination/'preparation/asdf'
    for path in (native, product):
        directories.append(str(path))
    controls.mkdir(parents=True)
    write_preparation_controls(controls, d)
    frozen = Path(plan['layout']['work'])/(Path(plan['run']).name+'-metadata')/Path(entry['key']).name
    frozen.mkdir(parents=True)
    images = {p: dict(sha256=digest, stat=coordinator.stat_identity(p)) for p, digest in d['baseline'].items()}
    context = preparation.prepare_context(d, plan['resolved'], frozen, controls,
        source_revision=plan['source_revision'], evidence=dict(native_directory=str(native),
            handoff=d['handoff'], metadata_sha256=d['metadata_sha256'], images=images,
            native_binary_sha256=coordinator.digest(plan['native_recipe']['executable']),
            configuration_sources=plan['configuration_sources'], batch_preservation=None))
    for source in sorted((frozen/'inputs').rglob('*')):
        if source.is_file():
            target = product/source.relative_to(frozen)
            directories.append(str(target.parent))
            copies.append(dict(source=str(source), target=str(target)))
    master_asset = 'master-bias:'+hashlib.sha256(d['master']['product'].encode()).hexdigest()
    argv = ['mefpp_linearity_prepare_command',
        *[str(controls/name) for name in ('native.toml', 'rois.toml', 'sites.toml', 'plan.tsv')],
        d['master']['product'], str(d['master']['hdu']), master_asset,
        str(controls/'biases.tsv'), str(native), '--native-asdf',
        str(product/'linearity-preparation.asdf'), START, str(log), '--context', str(context)]
    return argv


def compile_bindings(plan):
    """Freeze metadata only. The fresh reduced run stays empty until C begins."""
    root = Path(plan['layout']['orchestration'])/Path(plan['run']).name
    root.mkdir()
    directories, copies, detectors = [], [], []
    for index, entry in enumerate(plan['entries']):
        destination = Path(plan['run'])/f'detector-{index:03d}'
        controls = root/f'detector-{index:03d}'/'preparation'
        argv = preparation_binding(plan, entry, destination, controls, directories, copies)
        bpm_argv, fits, sidecar, _, _ = bpm.bpm_request(plan, entry, destination, START,
            deferred_directories=directories)
        # The native command expects a whole-second timestamp for BPM headers.
        bpm_argv[bpm_argv.index('--created-at')+1] = '${START_SECONDS}'
        bpm_argv[0] = 'mefpp_m5'
        detectors.append(dict(detector_id=entry['detector']['detector_id'],
            configuration_detector=entry['detector']['configuration_detector'],
            preparation=argv, bpm=bpm_argv, fits=str(fits), asdf=str(sidecar), prepared=argv[11]))
    dependencies = {**plan['metadata'], **plan['baseline']}
    dependencies[plan['native_recipe']['executable']] = coordinator.digest(plan['native_recipe']['executable'])
    metadata_files = set(root.rglob('*')) | {Path(row['source']) for row in copies}
    for path in metadata_files:
        if path.is_file():
            dependencies[str(path)] = coordinator.digest(path)
            path.chmod(0o444)
    lines = ['# Generated native bindings; edit the authoring TOMLs and regenerate.',
        'bpm_linearity_bindings_schema_version = 1',
        'source_revision = '+quoted(plan['source_revision']), 'recipe = '+quoted(plan['recipe_path']),
        'directories = '+json.dumps(sorted(set(directories), key=lambda p: (len(Path(p).parts), p)), ensure_ascii=True)]
    for path, digest in sorted(dependencies.items()):
        lines += ['\n[[dependencies]]', 'path = '+quoted(path), 'sha256 = '+quoted(digest)]
    for copy in copies:
        lines += ['\n[[copies]]', *[key+' = '+quoted(value) for key, value in copy.items()]]
    for detector in detectors:
        lines.append('\n[[detectors]]')
        for key, value in detector.items():
            lines.append(key+' = '+json.dumps(value, ensure_ascii=True))
    path = root/'native-bindings.toml'
    path.write_text('\n'.join(lines)+'\n')
    path.chmod(0o444)
    return path, detectors


def saved_manifest(plan, receipt):
    """Independent saved readers check native products before the Python index."""
    require(receipt['status'] == 'complete' and receipt['input_preservation'] is True and
            receipt['source_revision'] == plan['source_revision'] and
            receipt['scientific_acceptance'] is False and receipt['linearity_correction'] == 'not_applied',
            'Native recipe did not complete preserved measurement-only processing')
    report = dict(schema_version=1, scope='bpm_linearity', status='complete_for_owner_inspection',
        scientific_acceptance=False, final_mef_state='assembled', linearity_correction='not_applied',
        created_at=receipt['created_at'], native_source_revision=plan['source_revision'],
        assembly_source_revision=plan['source_revision'], product_root=plan['run'], directories=plan['layout'],
        configuration_sources=plan['configuration_sources'], coordinator_sources=plan['coordinator_sources'],
        detectors=[], input_preservation=True)
    require(len(receipt['detectors']) == len(plan['entries']), 'Native detector coverage differs')
    for entry, detector in zip(plan['entries'], receipt['detectors']):
        require(detector['detector_id'] == entry['detector']['detector_id'] and
                detector['configuration_detector'] == entry['detector']['configuration_detector'],
                'Native detector order/mapping differs')
        for key in ('fits', 'asdf', 'prepared'):
            require(Path(detector[key]).resolve(strict=True).is_relative_to(Path(plan['run'])) and
                    coordinator.digest(detector[key]) == detector[key+'_sha256'], 'Native output integrity differs')
        value = preparation.read_product(detector['prepared'])
        bpm.verify_bpm(detector['asdf'], plan, entry, Path(detector['fits']))
        log = str(Path(detector['fits']).with_suffix('.log'))
        product = dict(fits=detector['fits'], asdf=detector['asdf'], log=log,
            sha256={p: coordinator.digest(p) for p in (detector['fits'], detector['asdf'], log)},
            original_flat_indices=[row['index'] for row in entry['dependencies']['selection']['flat']])
        prepared = dict(path=detector['prepared'], sha256=detector['prepared_sha256'], container_schema='2.0.0',
            detector=value['detector'], pairs=len(value['rows']), exposures=len(value['exposure_rows']),
            sites=len(value['direct_site_replay']), trace_frames=len(value['scan_traces']), noise_state='unavailable')
        report['detectors'].append(dict(detector_id=detector['detector_id'],
            configuration_detector=detector['configuration_detector'], preparation=prepared, bpm=product,
            bpm_loaded_input_pixels=entry['bpm_loaded_pixels'], input_pixel_limit=entry['dependencies']['selection']['max_loaded_pixels']))
    product = {key: receipt[key] for key in ('fits', 'asdf', 'log')}
    product['sha256'] = {p: coordinator.digest(p) for p in product.values()}
    for key in ('fits', 'asdf'):
        require(product['sha256'][receipt[key]] == receipt[key+'_sha256'], 'Native final product changed')
    coordinator.assembly.read_product(receipt['asdf'])
    report['bpm_product'] = product
    path = Path(plan['run'])/'native-recipe.toml'
    report['batch_inputs'] = dict(path=str(path), sha256=coordinator.digest(path))
    return report


def execute(admitted):
    plan = deepcopy(admitted)
    plan['source_revision'] = plan['native_recipe']['source_revision']
    coordinator.metadata_unchanged(plan['metadata'])
    executable = plan['native_recipe']['executable']
    binary_digest = coordinator.digest(executable)
    bindings, _ = compile_bindings(plan)
    logs = Path(plan['layout']['logs'])/Path(plan['run']).name
    logs.mkdir()
    with (logs/'native-recipe-command.log').open('x') as stream:
        result = subprocess.run([executable, 'cal', 'bpm-linearity', '--config', plan['recipe_path'],
            '--bindings', str(bindings)], cwd=plan['layout']['orchestration'], stdout=stream, stderr=subprocess.STDOUT)
    require(result.returncode == 0, 'Native recipe failed; retain command log and partial products')
    coordinator.metadata_unchanged(plan['metadata'])
    require(coordinator.digest(executable) == binary_digest, 'Native recipe executable changed')
    receipt_path = Path(plan['run'])/'native-recipe.toml'
    report = saved_manifest(plan, tomllib.loads(receipt_path.read_text()))
    report['binary_sha256'] = dict(native_recipe=binary_digest)
    with (Path(plan['run'])/'manifest.json').open('x') as stream:
        stream.write(json.dumps(report, indent=2)+'\n')
    return report
