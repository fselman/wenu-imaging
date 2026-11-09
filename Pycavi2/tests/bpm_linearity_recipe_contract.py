"""Synthetic combined detector-characterization flow; native operations only.

Actual ASDF publication needs the retained native producer. Fixture wrappers may
exercise orchestration/readers locally, but do not qualify the C ASDF backend.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
import shutil
import stat
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'Pycavi2/pycavi/pycavi'), str(ROOT/'Pycavi2/tests')]
from linearity_preparation_fixture import fixture, source_archive
import pycavi_bpm_linearity_plan as planner
import pycavi_bpm_linearity_recipe as recipe
import pycavi_linearity_native_archive as archive


def rename_fixture_directory(source, destination):
    """macOS requires write permission on the directory being renamed."""
    mode = stat.S_IMODE(source.stat().st_mode)
    source.chmod(mode | stat.S_IWUSR)
    try:
        moved = source.rename(destination)
    except BaseException:
        source.chmod(mode)
        raise
    moved.chmod(mode)


def verify_saved_case(work):
    raw, controls, reduced = work/'raw', work/'orchestration', work/'reduced'
    run = reduced/'cal/bpm-linearity/combined'
    path = controls/'bpm-linearity.toml'
    guard = raw/'preservation-guard.bin'
    assert raw.is_dir() and not (work/'hidden-raw').exists()
    os.chdir(controls)
    relocated = Path(tempfile.mkdtemp(prefix='relocated-characterization-', dir=reduced))/'product'
    shutil.copytree(run, relocated)
    hidden = work/'hidden-raw'
    rename_fixture_directory(raw, hidden)
    native_run = subprocess.run
    try:
        subprocess.run = lambda *a, **k: (_ for _ in ()).throw(AssertionError('Saved reader executed a command'))
        saved = recipe.read_manifest(relocated/'manifest.json')
        assert len(saved['detectors'][0]['preparation']['exposure_rows']) == 100
        assert saved['FITS_integrity_rechecked'] is False
    finally:
        subprocess.run = native_run
        rename_fixture_directory(hidden, raw)
    frozen = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}
    try:
        planner.admit(path)
    except ValueError:
        pass
    else:
        raise AssertionError('Completed run admitted for overwrite')
    assert frozen == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}
    guard_before = guard.stat()
    guard_receipt = Path(tempfile.mkdtemp(prefix='guard-check-', dir=reduced))/'inputs.json'
    guard_inputs = recipe.BatchInputs({str(guard): hashlib.sha256(guard.read_bytes()).hexdigest()}, guard_receipt)
    guard.write_bytes(b'modified')
    os.utime(guard, ns=(guard_before.st_atime_ns, guard_before.st_mtime_ns))
    guard_inputs.observe(guard)
    try:
        guard_inputs.verify()
    except ValueError:
        pass
    else:
        raise AssertionError('Changed bytes with restored timestamp escaped final verification')
    finally:
        guard.write_bytes(b'original')
        os.utime(guard, ns=(guard_before.st_atime_ns, guard_before.st_mtime_ns))
    print('PASS: saved-product relocation without raw inputs or subprocesses; overwrite and byte-preservation guards')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bpm', type=Path, required=True)
    parser.add_argument('--preparation', type=Path, required=True)
    parser.add_argument('--source-revision', required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    parser.add_argument('--assembly', type=Path, help='Also publish the final BPM MEF with this native command')
    parser.add_argument('--assembly-source-revision', help='Exact assembler source revision')
    parser.add_argument('--verify-saved', type=Path, help='Finish checks on an already processed synthetic case; no native execution')
    args = parser.parse_args()
    if args.verify_saved:
        verify_saved_case(args.verify_saved.resolve(strict=True))
        return
    priority = os.getpriority(os.PRIO_PROCESS, 0)
    if priority < 10:
        os.nice(10-priority)
    work = Path(tempfile.mkdtemp(prefix='combined-characterization-', dir=args.work_parent)).resolve()
    state = fixture(work, separated=True)
    source = source_archive(state)
    guard = state['raw']/'preservation-guard.bin'
    guard.write_bytes(b'original')
    controls, reduced = state['work'], state['reduced']
    os.chdir(controls)
    for name, item in state['resolved']['sources'].items():
        (controls/(name+'.toml')).write_text(item['text'])
    for name in ('work', 'logs'):
        (reduced/name).mkdir()
    run = reduced/'cal/bpm-linearity/combined'
    run.mkdir(parents=True)
    project = (ROOT/'docs/architecture/proposed/m2/project-contracts/examples/omegacam.toml').read_text()
    project = project.replace('project_schema_version = 1', 'project_schema_version = 2', 1)
    for key, value in dict(raw=state['raw'], calibration=reduced/'cal', output=reduced,
                           work=reduced/'work', logs=reduced/'logs').items():
        project = project.replace('"review locations/'+key+'"', json.dumps(str(value)))
    project = project.replace('"../../examples/omegacam/full.toml"', json.dumps(str(controls/'native.toml')))
    (controls/'project.toml').write_text(project)
    text = 'bpm_linearity_recipe_schema_version = 1\nproject = "project.toml"\nrun = "cal/bpm-linearity/combined"\n'
    sections = dict(native=dict(bpm=str(args.bpm.resolve(strict=True)), preparation=str(args.preparation.resolve(strict=True)),
        source_revision=args.source_revision), preparation=dict(detector_toml='detector_toml.toml', processing_toml='processing_toml.toml'),
        bpm=dict(acquisition='quick', output_mode='new', upper_fraction=0.85,
                 minimum_span_fraction=0.001, maximum_pair_difference=0.02))
    if args.assembly:
        assert args.assembly_source_revision
        sections['assembly'] = dict(executable=str(args.assembly.resolve(strict=True)),
            source_revision=args.assembly_source_revision, reference_detector='ESO_CCD_#65')
    for key, value in sections.items():
        text += '\n['+key+']\n'+''.join(name+' = '+json.dumps(item)+'\n' for name, item in value.items())
    text += '\n[[detectors]]\ndetector_id = "ESO_CCD_#65"\nreference_rois = ["CCD65.R0"]\n'
    text += 'source_samples = '+json.dumps(str(source))+'\nhandoff = '+json.dumps(str(state['handoff_path']))+'\n'
    path = controls/'bpm-linearity.toml'
    path.write_text(text)
    protected = [*state['raw'].glob('*.fits'), Path(state['master']), Path(state['selection']['bpm']['path'])]
    for member in protected:
        member.chmod(0o444)
    state['raw'].chmod(0o555)
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    original = recipe.preparation.image_fingerprint
    try:
        recipe.preparation.image_fingerprint = lambda *a: (_ for _ in ()).throw(AssertionError('Metadata admission opened image bytes'))
        plan = planner.admit(path)
    finally:
        recipe.preparation.image_fingerprint = original
    assert not list(run.iterdir()) and len(plan['entries']) == 1
    invalid = controls/'invalid.toml'
    invalid.write_text(text.replace('reference_rois = ["CCD65.R0"]', 'reference_rois = ["unknown"]'))
    try:
        planner.admit(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('Unknown reference ROI admitted')
    assert not list(run.iterdir())
    calls = Counter()
    def counted(name):
        calls[str(name)] += 1
        return original(name)
    recipe.preparation.image_fingerprint = counted
    try:
        result = recipe.execute(plan)
    finally:
        recipe.preparation.image_fingerprint = original
    assert result['status'] == ('complete_for_owner_inspection' if args.assembly else 'detector_characterization_complete_for_owner_inspection')
    assert result['input_preservation'] and result['final_mef_state'] == ('assembled' if args.assembly else 'not_assembled')
    assert calls == Counter({name: 2 for name in plan['baseline']})
    member = result['detectors'][0]
    value = archive.read_product(member['preparation']['path'])
    assert len(value['exposure_rows']) == 100 and len(value['direct_site_replay']) == 100
    assert value['exposure_rows'][0]['signal_adu'] == 205.5 and value['scan_traces'][3]['master_accepted'] == 0
    assert member['bpm']['original_flat_indices'] == [r['index'] for r in state['selection']['flat']]
    with (run/'manifest.json').open() as stream:
        assert json.load(stream) == result
    assert before == {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in before}
    verify_saved_case(work)
    print('RETAINED COMBINED CHARACTERIZATION:', work)
    print('PASS: metadata-first admission, explicit prior/reference populations, serial native stages and joined manifest')
    print('PASS: shared images hashed exactly once before/after; exact measurements, input preservation and no overwrite')
    print('SCOPE: final BPM MEF included' if args.assembly else 'SCOPE: detector products only')
    print('Scientific/observational acceptance remains pending')


if __name__ == '__main__':
    main()
