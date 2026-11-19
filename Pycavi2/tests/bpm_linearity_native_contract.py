"""Native TOML admission with reordered HDUs, both QC modes and BPM policies.

Analytical ramp images verify unchanged correction/statistics; independent saved
readers check native ASDF and relocation. The optional labelled capture writer
covers numerical integration only, never the production serializer.
"""
from pathlib import Path
import sys, json, tempfile, subprocess, hashlib, tomllib
import argparse, os, re, struct
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

with tempfile.TemporaryDirectory(prefix='project-init-', dir=args.work_parent) as temporary:
    root = Path(temporary).resolve()
    raw = root / 'raw'
    raw.mkdir()
    observation = raw / 'observation.fits'
    observation.write_bytes(b'raw input sentinel')

    def initialize(orchestration, reduced, name='Test "project"'):
        return subprocess.run([str(command), 'project', 'init', '--name', name,
                               '--orchestration', str(orchestration), '--raw', str(raw),
                               '--reduced', str(reduced)], cwd=root, capture_output=True, text=True)

    for orchestration, reduced in (('WFI controls', 'WFI output'), ('ocam-candidate', 'ocam-reduced')):
        result = initialize(orchestration, reduced)
        assert result.returncode == 0, result.stderr
        controls = root / orchestration
        output = root / reduced
        project = controls / 'project.toml'
        original = project.read_bytes()
        assert tomllib.loads(original.decode()) == {
            'project_schema_version': 2,
            'project': {'schema_version': 1, 'id': 'Test "project"', 'name': 'Test "project"',
                        'roots': {'raw': str(raw), 'calibration': str(output / 'cal'),
                                  'output': str(output), 'work': str(output / 'work'),
                                  'logs': str(output / 'logs')}},
        }
        assert {p.name for p in output.iterdir()} == {'cal', 'work', 'logs'}
        assert all(p.is_dir() for p in output.iterdir())
        assert {p.name for p in controls.iterdir()} == {'project.toml'}
        assert initialize(orchestration, reduced).returncode != 0
        assert project.read_bytes() == original
    assert initialize('unused controls', 'WFI output').returncode != 0
    assert not (root / 'unused controls').exists()
    assert initialize('raw/controls', 'unused output').returncode != 0
    assert initialize('same', 'same').returncode != 0
    assert not (root / 'unused output').exists() and not (root / 'same').exists()
    assert list(raw.iterdir()) == [observation] and observation.read_bytes() == b'raw input sentinel'
    print('PASS: isolated named projects, minimal TOML, read-only raw and overwrite refusal')

from linearity_preparation_fixture import embedded_native_domains, fixture
from astropy.io import fits

work = Path(tempfile.mkdtemp(prefix='native-admission-', dir=args.work_parent.resolve(strict=True)))
state = fixture(work, separated=True, supplied_bpm=True)
# Model the WFI master: individual headers are below 1 MiB, but the
# complete file exceeds that old cumulative limit. Keep the fixture pixels.
with fits.open(state['master'], mode='update', do_not_scale_image_data=True) as master:
    for hdu in master:
        hdu.header.extend([('COMMENT', 'Retained master-bias QC fixture')] * 7200)
with fits.open(state['master']) as master:
    sizes = [hdu.fileinfo()['datLoc'] - hdu.fileinfo()['hdrLoc'] for hdu in master]
    assert max(sizes) < 1024**2 < sum(sizes)
orch = state['work']
reduced = state['reduced']
for p in ('work', 'logs'):
    (reduced / p).mkdir()
for name, item in state['resolved']['sources'].items():
    profile_text = item['text']
    if name == 'detector_toml':
        profile_text = profile_text.replace(
            '[[detector]]', 'readout_id = ' + json.dumps(state['selection']['readout_id'])
            + '\n\n[[detector]]', 1
        ).replace('native_paf_chip=1', 'native_paf_chip=1\nreference_hdu=0\nenabled=true')
    (orch / (name + '.toml')).write_text(profile_text)
project = (repo / 'docs/architecture/proposed/m2/project-contracts/examples/omegacam.toml').read_text().replace('project_schema_version = 1', 'project_schema_version = 2', 1)
for k, v in dict(raw=state['raw'], calibration=reduced / 'cal', output=reduced, work=reduced / 'work', logs=reduced / 'logs').items():
    project = project.replace('"review locations/' + k + '"', json.dumps(str(v)))
project = project.replace('"../../examples/omegacam/full.toml"', json.dumps(str(orch / 'native.toml')))
(orch / 'project-base.toml').write_text(project)
(orch / 'project.toml').write_text('project_schema_version = 2\ninclude = ["project-base.toml"]\n')
(orch / 'project-four-file.toml').write_text(project.split('\n[association]', 1)[0])
geometry, native_recipe = embedded_native_domains((orch / 'native.toml').read_text())
processing_profile = (orch / 'processing_toml.toml').read_text()
trim_start = processing_profile.index('[[trim]]')
roi_start = processing_profile.index('[[roi]]')
embedded_preparation = (
    '\n[preparation]\n'
    + processing_profile[:trim_start].replace('[linearity_preparation]', '[preparation.linearity_preparation]')
    + processing_profile[roi_start:].replace('[[roi]]', '[[preparation.roi]]')
)
(orch / 'four-file-detector.toml').write_text(
    (orch / 'detector_toml.toml').read_text() + '\n'
    + processing_profile[trim_start:roi_start] + geometry
)
cases=[(False,False,'bpm-linearity',True,False),(False,True,'bpm-linearity',True,True),
       *[(a,b,c,False,True) for a,b,c in ((True,True,'bpm-linearity'),(True,False,'bpm-linearity'),(False,True,'bpm-linearity'),(False,False,'bpm-linearity'),(False,False,'linearity'))]]
for qc, supplied, operation, listed, include_bias in cases:
    out = Path(tempfile.mkdtemp(prefix='native-', dir=reduced / 'cal'))
    text = 'bpm_linearity_recipe_schema_version = 2\nproject = "project.toml"\nsettings = "native.toml"\nrun = ' + json.dumps(str(out.relative_to(reduced))) + '\nqc = ' + str(qc).lower() + '\n'
    sections = dict(assembly=dict(reference_detector='ESO_CCD_#65'), preparation=dict(detector_toml='detector_toml.toml', processing_toml='processing_toml.toml'), bpm=dict(acquisition='quick', output_mode='new', upper_fraction=0.85, minimum_span_fraction=0.99, maximum_pair_difference=0.02, response_low=0.6, response_high=1.4), identity=dict(identity_key='DETID', amplifier_key='AMPID', bin_x_key='XBINNING', bin_y_key='YBINNING', exposure_key='EXPTIME', exposure_hdu=0))
    for key, value in sections.items():
        if key == 'bpm' and listed and not supplied:
            value['acquisition'] = 'provisional'
        text += '\n[' + key + ']\n' + ''.join((k + ' = ' + json.dumps(v) + '\n' for k, v in value.items()))
    text += '\n[inputs]\nbias = ' + json.dumps([b['path'] for b in state['biases']]) + '\n'
    pairs = {}
    for f in state['selection']['flat']:
        pair = pairs.setdefault(f['pair'], len(pairs))
        incoming = dict(path=f['path'], pair=pair, input_index=f['index'])
        if qc and supplied:
            incoming.pop('input_index')
        text += '\n[[inputs.flat]]\n' + ''.join((k + ' = ' + json.dumps(v) + '\n' for k, v in incoming.items()))
    d = dict(detector_id='ESO_CCD_#65', configuration_detector=0, hdu=0, flat_hdus=[f['hdu'] for f in state['selection']['flat']], readout_id=state['selection']['readout_id'], master_bias=state['master'], master_hdu=1, master_sha256=hashlib.sha256(Path(state['master']).read_bytes()).hexdigest(), input_bpm=state['selection']['bpm']['path'] if supplied else 'omitted', bpm_hdu=1, bias_accepted=[bool(b['accepted']) for b in state['biases']], reference_rois=['CCD65.R0'], sites=[dict(roi=f'CCD65.R{i}', x=i + 1, y=1) for i in range(5)], max_loaded_pixels=10000, max_rows=50)
    if listed and not supplied:
        for key in ('configuration_detector', 'hdu', 'readout_id'):
            del d[key]
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
    if listed:
        listing=state['raw']/(out.name+'.list')
        records=([(b['path'],'BIAS') for b in state['biases']] if include_bias else [])
        records += [(f['path'],'FLAT,LAMP') for f in state['selection']['flat']]
        listing.write_text(''.join(path+'\t'+kind+'\n' for path,kind in records))
        start=text.index('\n[inputs]'); end=text.index('\n[[detectors]]',start)
        text=text[:start]+'\n[inputs]\nlist = '+json.dumps(str(listing))+'\n'+text[end:]
        if listed:
            text='\n'.join(line for line in text.splitlines() if not line.startswith('bias_accepted ='))+'\n'
        assert '[[inputs.flat]]' not in text
    if listed:
        text = (text.replace('settings = "native.toml"', 'detector_toml = "four-file-detector.toml"')
                .replace('project = "project.toml"', 'project = "project-four-file.toml"'))
        text = text.replace(
            '\n[preparation]\ndetector_toml = "detector_toml.toml"\nprocessing_toml = "processing_toml.toml"\n',
            '',
        )
        text += embedded_preparation + native_recipe
    file = orch / (out.name + '.toml')
    file.write_text(text)
    argv = [str(command), 'cal', operation, '--config', str(file)]
    if not qc and supplied:
        argv += ['--qc', 'false']
    hidden = []
    if listed:
        for name in ('native.toml', 'processing_toml.toml'):
            path = orch / name
            hidden.append((path.rename(orch / (name + '.hidden')), path))
    try:
        result = subprocess.run(argv, cwd=orch, capture_output=True, text=True)
    finally:
        for parked, path in hidden:
            parked.rename(path)
    if result.returncode:
        print('FAILED', file)
        print(result.stdout, result.stderr)
        raise SystemExit(result.returncode)
    if listed and not supplied:
        assert not any('free requested on NULL pointer' in line and 'mef_bpm_files.c' in line
                       for line in result.stderr.splitlines()), result.stderr
    receipt = tomllib.loads((out / 'native-recipe.toml').read_text())
    controls = orch / out.name / 'detector-000'
    native = Path(tomllib.loads((orch / out.name / 'native-bindings.toml').read_text())['detectors'][0]['preparation'][9])
    import pycavi_linearity_native_archive as archive
    import pycavi_linearity_preparation_qc as reader
    saved = json.loads((controls / 'context.json').read_text())
    if listed:
        expected_settings = tomllib.loads((orch / 'native.toml').read_text())['native']
        for key, value in (('MEF.BPM.LGAINTHR', 0.6), ('MEF.BPM.HGAINTHR', 1.4)):
            expected_settings[key], = struct.unpack('>f', struct.pack('>f', value))
        assert tomllib.loads(saved['effective_settings_toml'])['native'] == expected_settings
        assert saved['recipe_source'] == saved['processing_profile'] == text
        assert saved['detector_profile'] == (orch / 'four-file-detector.toml').read_text()
    q = dict(provenance=dict(configuration=dict(snapshot=(native / 'configuration.json').read_text())))
    context = archive.native_context(saved, q, {})
    value = reader.collect(native, context['resolved'], context['selection'], context['biases'], None, context['master_snapshot'], master_reference=context['master'])
    assert len(value['rows']) == 50 and len(value['exposure_rows']) == 100 and (len(value['scan_traces']) == (30 if include_bias else 20)) and (len(value['direct_site_replay']) == 100)
    assert value['exposure_rows'][0]['signal_adu'] == 205.5
    assert all((r['signal_adu'] == 200 + (r['active_x'] - 1) for r in value['direct_site_replay'] if r['input_index'] == (10 if include_bias else 0)))
    assert receipt['qc'] == qc
    assert receipt['detectors'][0]['bpm_skipped'] == (supplied or operation == 'linearity')
    assert receipt['source_revision'] == args.source_revision
    assert receipt['detectors'][0]['image_loads'] == (20+(10 if include_bias else 0)+1+int(supplied))
    assert receipt['detectors'][0]['corrections'] == (30 if include_bias else 20)
    if not include_bias:
        assert not value['raw_bias_diagnostics']
        assert all(r['raw']['gain_state']=='bias_evidence_unavailable' and r['raw']['matched_ron_available']==0 for r in value['rows'])
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
    print('PASS', operation, qc, supplied, receipt['detectors'][0]['image_loads'], receipt['detectors'][0]['corrections'], 'four-file' if listed else 'inline-compatibility', 'analytical signals; pair/exposure/direct-site counts 50/100/100')
for label, old, new in (('identity-type', 'exposure_hdu = 0', 'exposure_hdu = "zero"'), ('unknown-site-field', 'x = 1\n', 'x = 1\nunknown_coordinate = 9\n'), ('missing-master', 'master_sha256 = "' + d['master_sha256'] + '"', 'master_sha256 = "' + '0' * 64 + '"'), ('combined-without-prior', 'output_mode = "new"', 'output_mode = "combined"'),
    ('bias-flat-index-collision', 'input_index = 10', 'input_index = 0'),
    ('flat-index-collision', 'input_index = 11', 'input_index = 10'),
    ('index-type', 'input_index = 10', 'input_index = "ten"'),
    ('bias-flat-asset-collision', '\n[[inputs.flat]]\n', '\n[[inputs.flat]]\nasset = '+json.dumps(Path(state['biases'][0]['path']).name)+'\n')):
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
# Header-derived pairing must reject incomplete and ambiguous cohorts, before pixels.
import shutil
extra=state['raw']/'third-same-exposure.fits'
shutil.copyfile(state['selection']['flat'][0]['path'],extra)
flats=[r['path'] for r in state['selection']['flat']]
for label, members in [('missing-partner',flats[:-1]),('ambiguous-partner',[*flats,str(extra)]),
                       ('duplicate-list-entry',[*flats,flats[0]]),
                       ('relative-fits',[Path(flats[0]).name,*flats[1:]]),
                       ('relative-list',flats)]:
    out=Path(tempfile.mkdtemp(prefix=label+'-',dir=reduced/'cal'))
    listing=orch/(out.name+'.list')
    listing.write_text(''.join(name+'\tFLAT,LAMP\n' for name in members))
    start=text.index('\n[inputs]');end=text.index('\n[[detectors]]',start)
    list_path = listing.name if label == 'relative-list' else str(listing)
    authored=text[:start]+'\n[inputs]\nlist = '+json.dumps(list_path)+'\n'+text[end:]
    authored='\n'.join(line for line in authored.splitlines() if not line.startswith('bias_accepted ='))+'\n'
    authored=authored.replace(str(Path(receipt['product_root']).relative_to(reduced)),str(out.relative_to(reduced)))
    file=orch/(out.name+'.toml');file.write_text(authored)
    result=subprocess.run([str(command),'cal','bpm-linearity','--config',str(file)],cwd=orch,capture_output=True,text=True)
    assert result.returncode!=0 and not list(out.rglob('*.fits')),label
    if args.capture_writer:assert 'loads=0 unique=0' in result.stderr,(label,result.stderr)
    if label == 'relative-list':
        assert 'inputs.list requires an absolute path' in result.stderr, result.stderr
    if label == 'relative-fits':
        assert 'observation path must be absolute' in result.stderr, result.stderr
print('PASS: duplicate entries, incomplete or ambiguous pairs, and relative paths refused before image loads')
profile_text = (orch / 'detector_toml.toml').read_text()
(orch / 'disabled-detector.toml').write_text(
    profile_text.replace('enabled=true', 'enabled=false', 1)
)
out = Path(tempfile.mkdtemp(prefix='disabled-', dir=reduced / 'cal'))
disabled_recipe = orch / (out.name + '.toml')
disabled_recipe.write_text(text.replace(
    str(Path(receipt['product_root']).relative_to(reduced)), str(out.relative_to(reduced))
).replace('detector_toml.toml', 'disabled-detector.toml'))
result = subprocess.run(
    [str(command), 'cal', 'bpm-linearity', '--config', str(disabled_recipe)],
    cwd=orch, capture_output=True, text=True,
)
assert result.returncode != 0 and 'Unknown or disabled BPM/linearity detector' in result.stderr, result.stderr
assert not list(out.rglob('*.fits')) and not list(out.rglob('*.asdf'))
if args.capture_writer:
    assert 'loads=0 unique=0' in result.stderr, result.stderr
print('PASS: a disabled BPM/linearity detector is refused before image loads')
print('RETAINED', work)
