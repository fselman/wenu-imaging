"""Metadata admission and saved-value verification for native preparation ASDF.

No ASDF writer, FITS measurement or numerical completion. The native command
publishes its own typed measurements and exact native evidence with libasdf.
"""
import csv
import io
import json
from pathlib import Path
import shutil
import struct
import tomllib
try:
    from . import pycavi_linearity_preparation_qc as previous
    from . import pycavi_native_product_qc as native_qc
except ImportError:
    import pycavi_linearity_preparation_qc as previous
    import pycavi_native_product_qc as native_qc
qc, pair, recipe = previous.qc, previous.pair, previous.recipe
SCHEMA = native_qc.SCHEMA


def prepare_context(dependencies, resolved, directory, controls, *, source_revision, evidence):
    """Freeze admitted dependency metadata, never calculated output values."""
    source = Path(dependencies['source_samples']).resolve(strict=True)
    frozen = previous.graph(source)
    target = directory/'inputs'
    target.mkdir()
    hashes = {}
    for path, digest in frozen.items():
        relative = path.relative_to(source.parent)
        out = target/relative
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, out)
        qc.require(pair.sha(pair.small(out)) == digest, 'Frozen source graph changed')
        hashes[relative.as_posix()] = digest
    context = dict(schema_version=1, input_bpm_policy=dependencies.get('input_bpm_policy', 'archived'),
        resolved=resolved, selection=dependencies['selection'],
        biases=dependencies['biases'], master=dependencies['master'],
        master_snapshot=dependencies['master_snapshot'], source_revision=source_revision,
        source_graph=dict(entry=source.name, sha256=hashes), dependency_evidence=evidence)
    if dependencies.get('bpm_response_limits') is not None:
        context['bpm_response_limits'] = dependencies['bpm_response_limits']
    if dependencies.get('calibration_bindings'):
        context['calibration_bindings'] = dependencies['calibration_bindings']
        context['calibration_root'] = dependencies['calibration_root']
    path = controls/'preparation-context.json'
    with path.open('x') as stream:
        stream.write(recipe.canonical(context)+'\n')
    return path


def native_context(saved, q, texts):
    """Decode native authoring evidence; no original files or historical replay."""
    resolved = recipe.configuration.resolve(saved['detector_profile'], saved['processing_profile'])
    author = tomllib.loads(saved['recipe_source'])
    qc.require(author['bpm_linearity_recipe_schema_version'] == 2 and
               saved['historical_comparison'] == 'not_requested', 'Unexpected native authoring context')
    row = next(r for r in author['detectors'] if r['detector_id'] == saved['detector'])
    snapshot = json.loads(q['provenance']['configuration']['snapshot'])
    native = tomllib.loads(saved['effective_settings_toml'])['native']
    qc.require(set(native) == set(snapshot), 'Native effective configuration keys differ')
    for key, value in native.items():
        typed = snapshot[key]
        actual = struct.pack('>f' if typed['type']=='float32-bits' else '>d', value).hex() if typed['type'].endswith('-bits') else value
        qc.require(actual == typed['value'], 'Native effective configuration differs: '+key)
    limits = {k: author['bpm'].get(k, v) for k,v in (('response_low',0.5),('response_high',1.5))}
    qc.require(recipe.bpm_configuration_snapshot(snapshot, limits) == snapshot, 'Native response policy differs')
    source_digest = saved['input_sha256'].get(saved['recipe'])
    qc.require(pair.sha(saved['recipe_source'].encode()) == source_digest, 'Native recipe evidence digest differs')
    raw, calibration = Path(saved['raw_root']), Path(saved['calibration_root'])
    def location(root, name):
        # Resolve lexical absolute paths without requiring original images.
        return str((root/name).resolve())
    flats=[]
    for i, incoming in enumerate(author['inputs']['flat']):
        path=location(raw,incoming['path'])
        flats.append(dict(path=path,asset=incoming.get('asset',Path(path).name),
            hdu=row.get('flat_hdus',[row['hdu']]*len(author['inputs']['flat']))[i],
            index=incoming.get('input_index',i),pair=f"pair-{incoming['pair']:03d}"))
    biases=[]
    for i, incoming in enumerate(author['inputs']['bias']):
        path=location(raw,incoming)
        biases.append(dict(path=path,asset=Path(path).name,index=i,accepted=int(row['bias_accepted'][i]),
            hdu=row.get('bias_hdus',[row['hdu']]*len(author['inputs']['bias']))[i]))
    controls=resolved['controls']
    mask=dict(encoding='omitted')
    if row['input_bpm'] != 'omitted':
        mask=dict(encoding=controls['mask_encoding'],path=location(calibration,row['input_bpm']),hdu=row['bpm_hdu'])
    selection=dict(detector=row['detector_id'],flat=flats,bpm=mask,
        readout_id=row['readout_id'],bin_x=1,bin_y=1)
    master=dict(product=location(calibration,row['master_bias']),hdu=row['master_hdu'])
    qc.require(saved['master_sha256']==row['master_sha256']==saved['input_sha256'][master['product']],
               'Native master fingerprint differs')
    return dict(resolved=resolved,selection=selection,biases=biases,master=master,
        master_snapshot=snapshot,source_revision=saved['source_revision'],input_bpm_policy='archived',
        dependency_evidence=dict(native_directory='native-evidence',qc_requested=saved['qc_requested']),
        native_sites=row['sites'])


def read_product(path):
    """Reconstruct saved diagnostics without native execution or original images."""
    path = Path(path).resolve(strict=True)
    q = native_qc.read(path)
    qc.require(q['extensions']['record_scope'] == 'one_final_table_product' and
               q['extensions']['table_name'] == 'linearity_preparation' and
               q['provenance']['operation'] == 'linearity.prepare', 'Wrong native preparation product')
    state = q['extensions']['operation_context']['snapshot']
    qc.require(q['provenance']['operation_version'] == 1 and
               all(field in state.split('; ') for field in ('noise_state=unavailable',
                   'covariance=unavailable', 'fit_state=not_performed', 'scientific_acceptance=false')),
               'Native model state must remain measurement only')
    items = q['extensions']['native_evidence']
    texts = {item['name']: item['text'] for item in items}
    qc.require(len(texts) == len(items), 'Duplicate native evidence')
    saved_context = json.loads(texts['preparation-context.json'])
    direct = saved_context.get('native_recipe_schema_version') == 2
    if direct:
        context = native_context(saved_context, q, texts)
        expected = None
        qc.require(q['provenance']['producer']['source_revision']==context['source_revision'], 'Native producer differs')
    else:
        context = json.loads(texts['preparation-context.json'])
        qc.require(context['schema_version'] == 1 and
                   q['provenance']['producer']['source_revision'] == context['source_revision'] and
                   json.loads(q['provenance']['configuration']['snapshot']) == recipe.bpm_configuration_snapshot(
                       context['master_snapshot'], context.get('bpm_response_limits')),
                   'Native producer/configuration differs from admitted dependencies')
        graph = context['source_graph']
        root = (path.parent/'inputs').resolve(strict=True)
        for name, digest in graph['sha256'].items():
            member = (root/name).resolve(strict=True)
            qc.require(member.is_relative_to(root) and pair.sha(pair.small(member)) == digest,
                       'Frozen dependency graph changed')
        source = (root/graph['entry']).resolve(strict=True)
        qc.require(source.is_relative_to(root), 'Source graph escapes archive')
        if context.get('calibration_bindings') or 'input_bpm_policy' in context:
            try:
                from . import pycavi_calibration_bindings as calibrations
            except ImportError:
                import pycavi_calibration_bindings as calibrations
            calibrations.verify_context(context, source)
        expected = previous.sample.read_product(source)
    names = {'configuration.json', 'master-reference.tsv', 'bias-traces.tsv', 'command.complete'}
    names.update(name for name in texts if name.startswith('pair-'))
    transports = {name: dict(text=texts[name], sha256=pair.sha(texts[name].encode())) for name in names}
    # collect only decodes saved native transports; it never repeats an estimator.
    native = context['dependency_evidence']['native_directory']
    value = previous.collect(native, context['resolved'], context['selection'], context['biases'],
        expected, context['master_snapshot'], master_reference=context['master'], transports=transports,
        input_bpm_policy=context.get('input_bpm_policy', 'archived'),
        bpm_response_limits=context.get('bpm_response_limits'))
    if direct:
        expected_sites={(r['asset'],r['index'],r['hdu'],site['roi'],site['x'],site['y'])
            for r in context['selection']['flat'] for site in context['native_sites']}
        actual_sites={(r['asset'],r['input_index'],r['hdu'],r['source_roi'],r['active_x'],r['active_y'])
            for r in value['direct_site_replay']}
        qc.require(actual_sites==expected_sites,'Native direct-site cohort differs from authoring')
        value['historical_comparison']='not_requested'
        value['configuration_sources']=saved_context['input_sha256']

    ordered = context['selection']['flat'] + context['biases']
    records = q['embedded_input_records']
    qc.require(len(records) == len(ordered), 'Incomplete native input cohort')
    for index, (record, original) in enumerate(zip(records, ordered)):
        qc.require(record['record_id'] == record['file']['id'] == original['asset'] and
                   record['file']['location'] == original['path'] and record['original_index'] == original['index'] and
                   record['detectors'][0]['source_hdu'] == original['hdu'] and
                   q['inputs'][index]['record_id'] == original['asset'], 'Native input identity/order/HDU differs')
    detector = q['characterization']['detectors'][0]
    definition = next(d for d in context['resolved']['detectors'] if d['detector_id'] == value['detector'])
    qc.require(detector['detector_id'] == value['detector'] and
               detector['amplifier'] == definition['amplifier_id'] and
               detector['configuration_detector'] == definition['configuration_detector'] and
               detector['readout_id'] == context['selection']['readout_id'] and
               [detector['bin_x'], detector['bin_y']] == [context['selection']['bin_x'], context['selection']['bin_y']],
               'Native detector binding differs')
    calibrations = {c['role']: c for c in q['calibrations']}
    expected = [('master_bias', dict(path=context['master']['product'], hdu=context['master']['hdu']))]
    if context['selection']['bpm']['encoding'] != 'omitted':
        expected.append(('bpm', context['selection']['bpm']))
    qc.require(set(calibrations) == {role for role, _ in expected} and len(q['calibrations']) == len(expected),
               'Native preparation calibration cohort differs')
    for role, original in expected:
        calibration = calibrations[role]
        qc.require(calibration['file']['location'] == original['path'] and
                   calibration['detector_bindings'] == [dict(detector_id=value['detector'], source_hdu=original['hdu'])],
                   'Native preparation calibration selector differs')
    metrics = detector['measurements']
    qc.require(len(metrics) == 2*len(value['exposure_rows'])+1, 'Incomplete native measurements')
    table = list(csv.DictReader(io.StringIO(texts['exposure-table.tsv']), delimiter='\t'))
    qc.require(len(table) == len(value['exposure_rows']), 'Incomplete native exposure table')
    for index, row in enumerate(value['exposure_rows']):
        for field, expected_value in row.items():
            if field in table[index]:
                actual = table[index][field]
                if expected_value is None:
                    matches = actual == ''
                elif isinstance(expected_value, str):
                    matches = actual == expected_value
                else:
                    matches = float(actual) == expected_value
                qc.require(matches, 'Native exposure table differs')
        for offset, field in enumerate(('signal_adu', 'spatial_variance_adu2')):
            m = metrics[2*index+offset]
            qc.require(m['name'] == f'exposure.{index}.{field}' and m['value'] == row[field] and
                       m['sources'] == [row['asset']] and
                       m['status'] == ('unavailable' if row[field] is None else 'measured') and
                       m['definition']['sample_count'] == row['valid_pixels'], 'Native common/saved measurement differs')
    qc.require(metrics[-1]['name'] == 'absolute_noise_covariance' and
               metrics[-1]['status'] == 'unavailable' and metrics[-1]['value'] is None,
               'Noise model must remain unavailable')
    from copy import deepcopy
    value['input_bpm_policy'] = ('omitted' if context['selection']['bpm']['encoding']=='omitted' else 'supplied') if direct else context.get('input_bpm_policy', 'archived')
    value['input_bpm'] = deepcopy(context['selection']['bpm'])
    value['source_revision'] = context['source_revision']
    if 'qc_requested' in context['dependency_evidence']:
        enabled = context['dependency_evidence']['qc_requested']
        qc.require(type(enabled) is bool and 'qc_requested='+str(enabled).lower() in state.split('; '),
                   'Native QC execution differs from frozen request')
        value['qc_requested'] = enabled
    return value


def modelling_inputs(path, *, require_noise=True):
    value = read_product(path)
    if require_noise:
        raise ValueError('Preparation is complete but a reviewed absolute noise/covariance model is unavailable')
    from copy import deepcopy
    return dict(pixel_observations=deepcopy(value['direct_site_replay']),
                roi_diagnostics=deepcopy(value['exposure_rows']), noise_state='unavailable', covariance=None)
