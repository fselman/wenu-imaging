"""Native TOML admission with reordered HDUs, both QC modes and BPM policies.

Analytical ramp images verify unchanged correction/statistics; independent saved
readers check native ASDF and relocation. The optional labelled capture writer
covers numerical integration only, never the production serializer.
"""
from pathlib import Path
import sys, json, tempfile, subprocess, hashlib, tomllib
import argparse, os, re
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'Pycavi2/tests'), str(ROOT / 'Pycavi2/pycavi/pycavi')]
parser = argparse.ArgumentParser(description='Tiny standalone native recipe contract; no archived inputs or observations')
parser.add_argument('--command', type=Path, required=True)
parser.add_argument('--work-parent', type=Path, required=True)
parser.add_argument('--source-revision', required=True)
parser.add_argument('--capture-writer', action='store_true', help='Local numerical check only; does not qualify native ASDF')
args = parser.parse_args()
command = args.command.resolve(strict=True)
repo = ROOT
with tempfile.TemporaryDirectory(prefix='recipe-help-', dir=args.work_parent) as empty:
    entries = re.findall('MEF_RECIPE\\("([^"]+)", "([^"]+)", [^,]+, ([01]),', (ROOT / 'mefpp2/ins/mef/common/mef_recipe_catalogue.def').read_text())
    assert len({(category, operation) for category, operation, _ in entries}) == len(entries)
    runtime = (ROOT / 'mefpp2/ins/mef/common/mef_runtime.h').read_text()
    declared = {(category.lower(), name.lower()) for category, name in re.findall('MEF_OP_(CAL|SCI)_([A-Z]+)', runtime)}
    assert declared <= {(category, name) for category, name, _ in entries}
    calls = [(['--help'], True), (['cal', '--help'], True), (['sci', '--help'], True)]
    for category, operation, ready in entries:
        calls.append(([category, operation, '--help'], True))
        if ready == '0':
            calls.append(([category, operation, '--config', 'absent.toml'], False))
    calls += [(['unknown', '--help'], False), (['cal', 'unknown', '--help'], False)]
    for arguments, success in calls:
        check = subprocess.run([str(command), *arguments], cwd=empty, capture_output=True, text=True)
        assert (check.returncode == 0) == success, (arguments, check.stdout, check.stderr)
        if not success and arguments[0] != 'unknown' and (arguments[1] != 'unknown'):
            assert 'pending; no processing performed' in check.stderr
        assert not list(Path(empty).iterdir()), arguments
    print('PASS: complete catalogue, data-free hierarchical help and pending execution refusal')
from linearity_preparation_fixture import fixture
work = Path(tempfile.mkdtemp(prefix='native-admission-', dir=args.work_parent.resolve(strict=True)))
state = fixture(work, separated=True, supplied_bpm=True)
orch = state['work']
reduced = state['reduced']
for p in ('work', 'logs'):
    (reduced / p).mkdir()
for name, item in state['resolved']['sources'].items():
    (orch / (name + '.toml')).write_text(item['text'])
project = (repo / 'docs/architecture/proposed/m2/project-contracts/examples/omegacam.toml').read_text().replace('project_schema_version = 1', 'project_schema_version = 2', 1)
for k, v in dict(raw=state['raw'], calibration=reduced / 'cal', output=reduced, work=reduced / 'work', logs=reduced / 'logs').items():
    project = project.replace('"review locations/' + k + '"', json.dumps(str(v)))
project = project.replace('"../../examples/omegacam/full.toml"', json.dumps(str(orch / 'native.toml')))
(orch / 'project-base.toml').write_text(project)
(orch / 'project.toml').write_text('project_schema_version = 2\ninclude = ["project-base.toml"]\n')
for qc, supplied, operation in ((True, True, 'bpm-linearity'), (True, False, 'bpm-linearity'), (False, True, 'bpm-linearity'), (False, False, 'bpm-linearity'), (False, False, 'linearity')):
    out = Path(tempfile.mkdtemp(prefix='native-', dir=reduced / 'cal'))
    text = 'bpm_linearity_recipe_schema_version = 2\nproject = "project.toml"\nsettings = "native.toml"\nrun = ' + json.dumps(str(out.relative_to(reduced))) + '\nqc = ' + str(qc).lower() + '\n'
    sections = dict(assembly=dict(reference_detector='ESO_CCD_#65'), preparation=dict(detector_toml='detector_toml.toml', processing_toml='processing_toml.toml'), bpm=dict(acquisition='quick', output_mode='new', upper_fraction=0.85, minimum_span_fraction=0.99, maximum_pair_difference=0.02, response_low=0.6, response_high=1.4), identity=dict(identity_key='DETID', amplifier_key='AMPID', bin_x_key='XBINNING', bin_y_key='YBINNING', exposure_key='EXPTIME', exposure_hdu=0))
    for key, value in sections.items():
        text += '\n[' + key + ']\n' + ''.join((k + ' = ' + json.dumps(v) + '\n' for k, v in value.items()))
    text += '\n[inputs]\nbias = ' + json.dumps([b['path'] for b in state['biases']]) + '\n'
    pairs = {}
    for f in state['selection']['flat']:
        pair = pairs.setdefault(f['pair'], len(pairs))
        text += '\n[[inputs.flat]]\n' + ''.join((k + ' = ' + json.dumps(v) + '\n' for k, v in dict(path=f['path'], pair=pair, input_index=f['index']).items()))
    d = dict(detector_id='ESO_CCD_#65', configuration_detector=0, hdu=0, flat_hdus=[f['hdu'] for f in state['selection']['flat']], readout_id=state['selection']['readout_id'], master_bias=state['master'], master_hdu=1, master_sha256=hashlib.sha256(Path(state['master']).read_bytes()).hexdigest(), input_bpm=state['selection']['bpm']['path'] if supplied else 'omitted', bpm_hdu=1, bias_accepted=[bool(b['accepted']) for b in state['biases']], reference_rois=['CCD65.R0'], sites=[dict(roi=f'CCD65.R{i}', x=i + 1, y=1) for i in range(5)], max_loaded_pixels=10000, max_rows=50)
    text += '\n[[detectors]]\n'
    for k, v in d.items():
        if k != 'sites':
            text += k + ' = ' + json.dumps(v) + '\n'
    for site in d['sites']:
        text += '\n[[detectors.sites]]\n' + ''.join((k + ' = ' + json.dumps(v) + '\n' for k, v in site.items()))
    if qc and supplied:
        text = text.replace('qc = true\n', '')
    if not qc and supplied:
        text = text.replace('qc = false\n', 'qc = true\n')
    file = orch / (out.name + '.toml')
    file.write_text(text)
    argv = [str(command), 'cal', operation, '--config', str(file)]
    if not qc and supplied:
        argv += ['--qc', 'false']
    result = subprocess.run(argv, cwd=orch, capture_output=True, text=True)
    if result.returncode:
        print('FAILED', file)
        print(result.stdout, result.stderr)
        raise SystemExit(result.returncode)
    receipt = tomllib.loads((out / 'native-recipe.toml').read_text())
    controls = orch / out.name / 'detector-000'
    native = Path(tomllib.loads((orch / out.name / 'native-bindings.toml').read_text())['detectors'][0]['preparation'][9])
    import pycavi_linearity_native_archive as archive
    import pycavi_linearity_preparation_qc as reader
    saved = json.loads((controls / 'context.json').read_text())
    q = dict(provenance=dict(configuration=dict(snapshot=(native / 'configuration.json').read_text())))
    context = archive.native_context(saved, q, {})
    value = reader.collect(native, context['resolved'], context['selection'], context['biases'], None, context['master_snapshot'], master_reference=context['master'])
    assert len(value['rows']) == 50 and len(value['exposure_rows']) == 100 and (len(value['scan_traces']) == 30) and (len(value['direct_site_replay']) == 100)
    assert value['exposure_rows'][0]['signal_adu'] == 205.5
    assert all((r['signal_adu'] == 200 + (r['active_x'] - 1) for r in value['direct_site_replay'] if r['input_index'] == 10))
    assert receipt['qc'] == qc
    assert receipt['detectors'][0]['bpm_skipped'] == (supplied or operation == 'linearity')
    assert receipt['source_revision'] == args.source_revision
    assert receipt['detectors'][0]['image_loads'] == (32 if supplied else 31)
    assert receipt['detectors'][0]['corrections'] == 30
    if not args.capture_writer:
        import pycavi_bpm_linearity_recipe as saved_reader
        decoded = saved_reader.read_manifest(out / 'native-recipe.toml')
        assert len(decoded['detectors'][0]['preparation']['exposure_rows']) == 100
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
        original_run = subprocess.run
        subprocess.run = lambda *a, **k: (_ for _ in ()).throw(AssertionError('Saved reader executed a subprocess'))
        try:
            relocated = Path(tempfile.mkdtemp(prefix='relocated-', dir=reduced)) / 'product'
            import shutil
            shutil.copytree(out, relocated)
            raw_mode = state['raw'].stat().st_mode
            state['raw'].chmod(raw_mode | 128)
            hidden = state['raw'].rename(state['raw'].with_name('hidden-raw'))
            try:
                assert len(saved_reader.read_manifest(relocated / 'native-recipe.toml')['detectors'][0]['preparation']['direct_site_replay']) == 100
            finally:
                hidden.rename(state['raw'])
                state['raw'].chmod(raw_mode)
        finally:
            subprocess.run = original_run
        assert before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
    repeated = subprocess.run(argv, cwd=orch, capture_output=True, text=True)
    assert repeated.returncode != 0, 'Completed run was overwritten'
    print('PASS', operation, qc, supplied, receipt['detectors'][0]['image_loads'], receipt['detectors'][0]['corrections'], 'native context, analytical signals, 50/100/30/100 measurements')
for label, old, new in (('identity-type', 'exposure_hdu = 0', 'exposure_hdu = "zero"'), ('unknown-site-field', 'x = 1\n', 'x = 1\nunknown_coordinate = 9\n'), ('missing-master', 'master_sha256 = "' + d['master_sha256'] + '"', 'master_sha256 = "' + '0' * 64 + '"'), ('combined-without-prior', 'output_mode = "new"', 'output_mode = "combined"')):
    out = Path(tempfile.mkdtemp(prefix='invalid-', dir=reduced / 'cal'))
    invalid = text.replace(old, new).replace(str(Path(receipt['product_root']).relative_to(reduced)), str(out.relative_to(reduced)))
    assert invalid != text
    file = orch / (out.name + '.toml')
    file.write_text(invalid)
    result = subprocess.run([str(command), 'cal', 'bpm-linearity', '--config', str(file)], cwd=orch, capture_output=True, text=True)
    assert result.returncode != 0, label
    assert not list(out.rglob('*.fits')) and (not list(out.rglob('*.asdf'))), label
    if args.capture_writer:
        assert 'loads=0 unique=0' in result.stderr, (label, result.stderr)
print('PASS: project includes, non-clobber and invalid-input admission before image loading')
print('RETAINED', work)
