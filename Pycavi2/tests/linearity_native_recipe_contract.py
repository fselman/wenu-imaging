"""Full recipe envelope -> native ASDF; synthetic readonly images only."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Pycavi2/pycavi/pycavi'))
sys.path.insert(0, str(ROOT/'Pycavi2/tests'))
from linearity_preparation_fixture import fixture, source_archive
import pycavi_linearity_native_archive as archive


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-command', type=Path, required=True)
    parser.add_argument('--source-revision', required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    parent = args.work_parent/('project-location-'+'x'*100)
    parent.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='native-preparation-recipe-', dir=parent)).resolve()
    state = fixture(work, separated=True)
    source = source_archive(state)
    assert len(state['master']) > 127, 'Exercise full locations beyond the asset-ID limit'
    controls, reduced = state['work'], state['reduced']
    for name, item in state['resolved']['sources'].items():
        (controls/(name+'.toml')).write_text(item['text'])
    for name in ('work', 'logs'):
        (reduced/name).mkdir()
    run = reduced/'cal/bpm-linearity/native-recipe'
    run.mkdir(parents=True)
    project = (ROOT/'docs/architecture/proposed/m2/project-contracts/examples/omegacam.toml').read_text()
    project = project.replace('project_schema_version = 1', 'project_schema_version = 2', 1)
    for key, value in dict(raw=state['raw'], calibration=reduced/'cal', output=reduced,
                           work=reduced/'work', logs=reduced/'logs').items():
        project = project.replace('"review locations/'+key+'"', json.dumps(str(value)))
    project = project.replace('"../../examples/omegacam/full.toml"', json.dumps(str(controls/'native.toml')))
    (controls/'project.toml').write_text(project)
    envelope = dict(publication='native', detector_toml='detector_toml.toml',
        processing_toml='processing_toml.toml', source_samples=str(source),
        handoff=str(state['handoff_path']), native=str(args.native_command.resolve(strict=True)),
        run='cal/bpm-linearity/native-recipe', source_revision=args.source_revision)
    text = 'linearity_recipe_schema_version = 1\nproject = "project.toml"\n[preparation]\n'
    text += ''.join(key+' = '+json.dumps(value)+'\n' for key, value in envelope.items())
    configuration = controls/'bpm-linearity.toml'
    configuration.write_text(text)
    protected = [*state['raw'].glob('*.fits'), Path(state['master']), Path(state['selection']['bpm']['path'])]
    fingerprints = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    for path in protected:
        path.chmod(0o444)
    state['raw'].chmod(0o555)
    argv = [sys.executable, str(ROOT/'tools/prepare-linearity.py'), '--config', str(configuration), '--execute']
    result = subprocess.run(argv, cwd=controls, capture_output=True, text=True)
    (reduced/'native-recipe-check.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stdout+result.stderr
    report = json.loads((run/'execution.json').read_text())
    assert report['status'] == 'complete_for_owner_inspection' and report['publication'] == 'native'
    assert report['argv'][5] == state['master'] and len(report['argv'][7]) < 128
    assert report['argv'][7] == 'master-bias:'+hashlib.sha256(state['master'].encode()).hexdigest()
    product = Path(report['product']['path'])
    value = archive.read_product(product)
    assert len(value['exposure_rows']) == 100 and len(value['scan_traces']) == 30
    assert len(value['direct_site_replay']) == 100
    assert value['exposure_rows'][0]['signal_adu'] == 205.5
    assert value['scan_traces'][0]['correction_adu'] == [12, 22, 32, 42]
    assert value['scan_traces'][3]['master_accepted'] == 0
    assert value['fit_state'] == 'not_performed' and value['noise_state'] == 'unavailable'
    assert (controls/'native-recipe/preparation-context.json').is_file()
    assert (reduced/'logs/native-recipe/native.log').is_file()
    private = reduced/'work/native-recipe'
    hidden = reduced/'hidden-native-recipe'
    private.rename(hidden)
    moved = reduced/'relocated-native-archive'
    shutil.move(str(product.parent), moved)
    product = moved/product.name
    assert archive.read_product(product) == value
    with archive.qc._asdf().open(product) as saved:
        tree = dict(saved.tree)
    metrics = tree['qc']['characterization']['detectors'][0]['measurements']
    metrics[0]['value'] += 1
    tampered = moved/'tampered.asdf'
    with archive.qc._asdf().AsdfFile(tree, version='1.6.0') as saved:
        saved.write_to(tampered)
    try:
        archive.read_product(tampered)
    except ValueError:
        pass
    else:
        raise AssertionError('Changed native/saved measurement accepted')
    assert fingerprints == {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in fingerprints}
    assert not list(controls.glob('*.fits'))
    assert subprocess.run(argv, cwd=controls, capture_output=True).returncode != 0
    print('RETAINED NATIVE RECIPE:', work)
    print('PASS: project/recipe envelope, native publication, exact original measurements, immutable input graph')
    print('PASS: saved reader relocation without native files; tampered measurement and repeated run refused')


if __name__ == '__main__':
    main()
