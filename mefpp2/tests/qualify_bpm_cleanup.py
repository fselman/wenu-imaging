"""Qualify #90 on the Mac using retained baseline inputs and tool settings.

No installation is performed. Native output stays in per-attempt log files.
This is bounded invalid-access and mask regression, not leak qualification.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, record):
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(record, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    baseline = args.baseline.resolve(strict=True)
    old = json.loads((baseline / 'run-provenance.json').read_text())
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    branch = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD'], cwd=repo, text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=repo):
        raise RuntimeError('STOP: qualification requires a clean checkout')
    if platform.system() != 'Darwin' or platform.node().split('.')[0] != 'MC02VV0HPHTDG':
        raise RuntimeError('STOP: this baseline orchestration is for the qualified Mac')
    if Path(os.sys.prefix).resolve() != Path.home() / 'anaconda3':
        raise RuntimeError('STOP: unexpected Python prefix')
    import numpy as np
    from astropy.io import fits

    # Preservation preflight: check exact baseline fixture, driver and protected files.
    for name, expected in old['inputs_sha256'].items():
        if digest(baseline / 'inputs' / name) != expected:
            raise RuntimeError('Baseline fixture changed: ' + name)
    for name, expected in old['protected_sha256'].items():
        if digest(Path(name)) != expected:
            raise RuntimeError('Protected file changed: ' + name)
    driver_path = baseline / 'source/mefpp2/tests/bpm_cleanup_probe.c'
    if digest(driver_path) != old['diagnostic_source_sha256']['driver']:
        raise RuntimeError('Baseline driver changed')
    driver = driver_path.read_text()
    old_tail = '''    fprintf(stderr, "UNEXPECTED: constructor returned without the expected fault\\n");
    if (mask != NULL) pixelmap_del(mask);
    mef_bb_del(bb);
    return 4;'''
    new_tail = '''    if (mask == NULL) return 3;
    if (mask->lx != 9 || mask->ly != 9) return 5;
    pixelmap_dump(mask, "returned.fits", NULL);
    printf("PASS: returned 9x9 mask good=%d\\n", mask->ngoodpix);
    pixelmap_del(mask);
    mef_bb_del(bb);
    return 0;'''
    if driver.count(old_tail) != 1:
        raise RuntimeError('Unexpected baseline driver tail')
    driver = driver.replace(old_tail, new_tail)
    driver = driver.replace('int main(void)', 'int main(int argc, char **argv)')
    driver = driver.replace('bb->bpm_proportional_flag = 1;',
                            'bb->bpm_proportional_flag = (argc == 2) ? atoi(argv[1]) : 1;')

    # Independent attempt: write provenance before any build or test work.
    work = Path(tempfile.mkdtemp(prefix='mac-bpm-cleanup-corrected-', dir=baseline.parent))
    identity = dict(repository='https://github.com/fselman/wenu-imaging',
                    branch=branch, commit=revision, dirty=False)
    record = dict(schema_version=1, project='wenu-imaging', tested_source=identity,
                  host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
                  purpose='Issue 90 corrected constructors and mask regression',
                  status='running', retention_roles=['acceptance_evidence'],
                  baseline=str(baseline), baseline_provenance_sha256=digest(baseline / 'run-provenance.json'),
                  commands=[], cases=[], installation_performed=False,
                  observational_processing_performed=False,
                  diagnostic_scope='Address/undefined checks; leak detection disabled',
                  protected_sha256=old['protected_sha256'])
    provenance = work / 'run-provenance.json'
    save(provenance, record)
    print('WORK DIRECTORY:', work, flush=True)

    children = []

    def directory(path, role):
        path.mkdir()
        save(path / 'run-provenance.json', dict(
            schema_version=1, project='wenu-imaging', tested_source=identity,
            parent_manifest=str(provenance), purpose=role, status='running',
            retention_roles=['acceptance_evidence']))
        children.append(path / 'run-provenance.json')
        return path

    def run(label, argv, cwd, env=None):
        log = work / (label + '.log')
        entry = dict(label=label, argv=list(map(str, argv)), cwd=str(cwd), log=str(log))
        record['commands'].append(entry)
        save(provenance, record)
        print('Running:', label, flush=True)
        with log.open('w') as stream:
            result = subprocess.run(entry['argv'], cwd=cwd, env=env,
                                    stdout=stream, stderr=subprocess.STDOUT, timeout=300)
        entry.update(exit_status=result.returncode, log_sha256=digest(log))
        save(provenance, record)
        if result.returncode:
            raise RuntimeError(label + ' failed; retained log: ' + str(log))
        return log

    try:
        source = directory(work / 'source', 'Exported source with recorded diagnostic additions')
        archive = subprocess.check_output(['git', 'archive', revision, 'mefpp2'], cwd=repo)
        (work / 'source.tar').write_bytes(archive)
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(source)
        probe = source / 'mefpp2/tests/bpm_cleanup_probe.c'
        probe.write_text(driver)
        cmake = source / 'mefpp2/CMakeLists.txt'
        cmake.write_text(cmake.read_text() + '\n# Qualification driver; production routines unchanged.\n'
                         'add_executable(bpm_cleanup_probe tests/bpm_cleanup_probe.c)\n'
                         'target_link_libraries(bpm_cleanup_probe PRIVATE mefpp_common)\n')
        record['diagnostic_sha256'] = dict(driver=digest(probe), cmake=digest(cmake))
        settings = next(c['argv'] for c in old['commands'] if c['label'] == 'configure')
        save(provenance, record)
        pixel_identities = {}
        for mode in (90, 17):
            build = directory(work / ('build-c' + str(mode)), 'C%d diagnostic build' % mode)
            argv = [s.replace(str(baseline), str(work)).replace('-DMEFPP_C_STANDARD=90', '-DMEFPP_C_STANDARD=' + str(mode))
                    .replace('-DMEFPP_SOURCE_REVISION=' + old['commit'], '-DMEFPP_SOURCE_REVISION=' + revision)
                    for s in settings]
            argv[argv.index('-B') + 1] = str(build)
            run('configure-c' + str(mode), argv, work)
            run('build-c' + str(mode), [settings[0], '--build', build, '--target', 'bpm_cleanup_probe', '--parallel', '2'], work)
            executable = build / 'bpm_cleanup_probe'
            run('symbols-c' + str(mode), ['/usr/bin/dsymutil', executable], work)
            for kind in ('retained', 'known-response'):
                for flag in (0, 1):
                    label = 'c%d-%s-flag%d' % (mode, kind, flag)
                    case = directory(work / label, 'Native constructor and saved-mask regression')
                    for name in old['inputs_sha256']:
                        shutil.copyfile(baseline / 'inputs' / name, case / name)
                    # Known response: 79 unit-response pixels, one 1/4 and one 2.
                    # Mean response is 81.25/81; both special pixels are rejected.
                    expected = np.ones((9, 9), dtype=np.uint8)
                    expected.flat[0] = expected.flat[40] = 0
                    if kind == 'known-response':
                        response = np.ones((9, 9), dtype=np.float32)
                        response.flat[0], response.flat[40] = 0.25, 2.0
                        for index, level in enumerate((100., 200., 400.)):
                            path = case / ('frame%d.fits' % index)
                            with fits.open(path, memmap=False) as hdus:
                                if hdus[1].data.shape != (9, 18):
                                    raise RuntimeError('Unexpected raw fixture geometry')
                                hdus[1].data = np.zeros((9, 18), dtype=np.float32)
                                hdus[1].data[:, :9] = response * level
                                hdus.writeto(path, overwrite=True)
                    inputs = {name: digest(case / name) for name in old['inputs_sha256']}
                    env = os.environ.copy()
                    env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:exitcode=86',
                               UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=0', E_VERBOSE='0', E_DEBUG='0')
                    log = run(label, [executable, str(flag)], case, env)
                    if 'PASS: returned 9x9 mask good=' not in log.read_text(errors='replace'):
                        raise RuntimeError('Missing native completion marker: ' + label)
                    # Returned and production-saved masks must agree pixel for pixel.
                    outputs = [p for p in case.glob('*.fits') if p.name not in inputs and p.name != 'returned.fits']
                    if len(outputs) != 1:
                        raise RuntimeError('Expected one production mask: ' + label)
                    with fits.open(case / 'returned.fits') as returned, fits.open(outputs[0]) as saved, fits.open(case / 'frame0.fits') as raw:
                        mask = returned[0].data
                        if len(saved) != 2 or mask.shape != (9, 9) or not np.array_equal(mask, saved[1].data):
                            raise RuntimeError('Saved/returned mask mismatch: ' + label)
                        if not np.isin(mask, [0, 1]).all() or saved[1].header['EXTNAME'] != raw[1].header['EXTNAME']:
                            raise RuntimeError('Mask polarity or extension identity: ' + label)
                        good = int(mask.sum())
                        native_good = re.search(r'PASS: returned 9x9 mask good=(\d+)', log.read_text(errors='replace'))
                        if native_good is None or int(native_good.group(1)) != good:
                            raise RuntimeError('Returned mask count mismatch: ' + label)
                        if saved[1].header['ESO MPP QC NGOODPIX'] != good or saved[1].header['ESO MPP QC NBADPIX'] != 81 - good:
                            raise RuntimeError('Mask counts mismatch: ' + label)
                        if kind == 'known-response' and not np.array_equal(mask, expected):
                            raise RuntimeError('Known-response mask mismatch: ' + label)
                        pixel_hash = hashlib.sha256(mask.astype(np.uint8).tobytes()).hexdigest()
                        key = (kind, flag)
                        if key in pixel_identities and pixel_identities[key] != pixel_hash:
                            raise RuntimeError('C90/C17 pixel mismatch: ' + label)
                        pixel_identities[key] = pixel_hash
                    if any(digest(case / name) != value for name, value in inputs.items()):
                        raise RuntimeError('Staged input changed: ' + label)
                    result = dict(case=label, status='passed', inputs_sha256=inputs,
                                  returned_sha256=digest(case / 'returned.fits'), saved_sha256=digest(outputs[0]),
                                  good=good, bad=81-good, pixels_checked=81,
                                  mask_pixels_sha256=pixel_hash,
                                  known_response_checked=(kind == 'known-response'))
                    record['cases'].append(result)
                    save(case / 'run-provenance.json', dict(result, tested_source=identity, parent_manifest=str(provenance),
                         schema_version=1, retention_roles=['acceptance_evidence']))
                    save(provenance, record)
                    print('PASS:', label, 'good=%d bad=%d' % (good, 81-good), flush=True)
        record['status'] = 'passed'
    except BaseException as error:
        record.update(status='failed', error=str(error))
        raise
    finally:
        protected = all(digest(Path(p)) == h for p, h in old['protected_sha256'].items())
        baseline_ok = all(digest(baseline / 'inputs' / p) == h for p, h in old['inputs_sha256'].items())
        record.update(protected_files_unchanged=protected, baseline_inputs_unchanged=baseline_ok,
                      completed_utc=datetime.now(timezone.utc).isoformat())
        if not protected or not baseline_ok:
            record['status'] = 'failed'
        save(provenance, record)
        for path in children:
            child = json.loads(path.read_text())
            if child['status'] == 'running':
                child.update(status=record['status'], completed_utc=record['completed_utc'])
                save(path, child)
    if record['status'] != 'passed':
        raise RuntimeError('Preservation checks failed')
    print('PASS: eight constructor cases; baseline and protected files unchanged.')
    print('REPORT:', provenance)


if __name__ == '__main__':
    main()
