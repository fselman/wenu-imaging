"""Run the unchanged Mac-qualified BPM driver/fixtures on Chapman3.

Functional C90/C17 regression only: no sanitizer runtime or installation.
"""
import argparse
import configparser
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
import sys
import tarfile
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cmake', type=Path, required=True)
    parser.add_argument('--compiler', type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != 'Linux' or platform.node().split('.')[0] != 'chapman3':
        raise RuntimeError('STOP: run on Chapman3')
    if Path(sys.prefix).resolve() != (Path.home() / '.conda/envs/wenu-imaging').resolve():
        raise RuntimeError('STOP: unexpected Python environment')
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError('STOP: launch this batch with nice -n 10')
    import numpy as np
    from astropy.io import fits
    repo = Path(__file__).resolve().parents[2]

    def git(*argv):
        return subprocess.check_output(['git', *argv], cwd=repo, text=True).strip()

    if git('status', '--porcelain', '--untracked-files=all'):
        raise RuntimeError('STOP: checkout must be clean')
    revision, branch = git('rev-parse', 'HEAD'), git('symbolic-ref', '--short', 'HEAD')
    fixture = repo / 'mefpp2/tests/fixtures/bpm-cleanup'
    manifest = json.loads((fixture / 'manifest.json').read_text())

    def check_fixtures():
        if any(digest(fixture / p) != h for p, h in manifest['files'].items()):
            raise RuntimeError('Qualified fixture changed')

    check_fixtures()
    reference_path = repo / 'docs/developer/fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json'
    reference = json.loads(reference_path.read_text())
    config = Path(os.environ.get('PYCAVI_ASTROSOFT_CONFIG', '~/.pycavi/pycavi_astrosoft.cfg')).expanduser().resolve(strict=True)
    settings = configparser.ConfigParser(interpolation=None)
    settings.read(config)
    selected = Path(settings['Paths']['mefpp'].strip().strip('"')).expanduser()
    if not selected.is_absolute():
        selected = Path(shutil.which(str(selected)) or str(selected))
    selected = selected.resolve(strict=True)
    protected = {str(p): digest(p) for p in (config, selected)}
    cmake, compiler = args.cmake.resolve(strict=True), args.compiler.resolve(strict=True)
    root = Path.home() / 'Software/build/wenu-imaging'
    if not root.is_dir():
        raise RuntimeError('STOP: expected imaging build root is absent')
    work = Path(tempfile.mkdtemp(prefix='chapman3-bpm-cleanup-', dir=root))
    identity = dict(repository='https://github.com/fselman/wenu-imaging', branch=branch, commit=revision, dirty=False)
    record = dict(schema_version=1, project='wenu-imaging', tested_source=identity,
                  host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
                  purpose='Chapman3 functional BPM cleanup regression with unchanged Mac driver/fixtures',
                  status='running', retention_roles=['acceptance_evidence'],
                  diagnostic_scope='Uninstrumented target regression; Mac sanitizer acceptance is separate',
                  installation_performed=False, observational_processing_performed=False,
                  protected_sha256=protected, commands=[], cases=[],
                  fixture_manifest_sha256=digest(fixture / 'manifest.json'),
                  mac_reference_sha256=digest(reference_path),
                  tool_sha256={str(p): digest(p) for p in (cmake, compiler)},
                  python=sys.executable, numpy=np.__version__)
    provenance = work / 'run-provenance.json'
    save(provenance, record)
    print('WORK DIRECTORY:', work, flush=True)
    children = []

    def directory(name, purpose):
        path = work / name
        path.mkdir()
        child = path / 'run-provenance.json'
        save(child, dict(schema_version=1, project='wenu-imaging', tested_source=identity,
                         parent_manifest=str(provenance), purpose=purpose, status='running',
                         retention_roles=['acceptance_evidence']))
        children.append(child)
        return path

    def run(label, argv, cwd):
        entry = dict(label=label, argv=list(map(str, argv)), cwd=str(cwd))
        log = work / (label + '.log')
        entry['log'] = str(log)
        record['commands'].append(entry)
        save(provenance, record)
        print('Running:', label, flush=True)
        env = os.environ.copy()
        env.update(E_VERBOSE='0', E_DEBUG='0')
        with log.open('w') as stream:
            result = subprocess.run(entry['argv'], cwd=cwd, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=600)
        entry.update(exit_status=result.returncode, log_sha256=digest(log))
        save(provenance, record)
        if result.returncode:
            raise RuntimeError(label + ' failed; see ' + str(log))
        return log

    try:
        source = directory('source', 'Exported source with diagnostic target addition only')
        archive = subprocess.check_output(['git', 'archive', revision, 'mefpp2'], cwd=repo)
        record['source_archive_sha256'] = hashlib.sha256(archive).hexdigest()
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(source)
        cmake_file = source / 'mefpp2/CMakeLists.txt'
        cmake_file.write_text(cmake_file.read_text() + '\n# Unchanged Mac-qualified diagnostic driver.\n'
            'add_executable(bpm_cleanup_probe tests/fixtures/bpm-cleanup/bpm_cleanup_probe.c)\n'
            'target_link_libraries(bpm_cleanup_probe PRIVATE mefpp_common)\n')
        record['diagnostic_cmake_sha256'] = digest(cmake_file)
        for mode in (90, 17):
            build = directory('build-c' + str(mode), 'C%d uninstrumented diagnostic build' % mode)
            run('configure-c' + str(mode), [cmake, '-S', source / 'mefpp2', '-B', build,
                '-G', 'Unix Makefiles', '-DCMAKE_C_COMPILER=' + str(compiler),
                '-DCMAKE_BUILD_TYPE=Debug', '-DCMAKE_C_FLAGS=-O0 -g',
                '-DMEFPP_C_STANDARD=' + str(mode), '-DBUILD_TESTING=OFF',
                '-DMEFPP_BUILD_RESOURCES=OFF', '-DMEFPP_SOURCE_REVISION=' + revision], work)
            run('build-c' + str(mode), [cmake, '--build', build, '--target', 'bpm_cleanup_probe', '--parallel', '2'], work)
            executable = build / 'bpm_cleanup_probe'
            for kind in ('retained', 'known-response'):
                for flag in (0, 1):
                    label = 'c%d-%s-flag%d' % (mode, kind, flag)
                    case = directory(label, 'Native BPM returned/saved mask regression')
                    inputs = {}
                    for path in sorted((fixture / kind).iterdir()):
                        shutil.copyfile(path, case / path.name)
                        inputs[path.name] = digest(case / path.name)
                    log = run(label, [executable, str(flag)], case)
                    marker = re.search(r'PASS: returned 9x9 mask good=(\d+)', log.read_text(errors='replace'))
                    outputs = [p for p in case.glob('*.fits') if p.name not in inputs and p.name != 'returned.fits']
                    if marker is None or len(outputs) != 1:
                        raise RuntimeError('Missing output or completion: ' + label)
                    with fits.open(case / 'returned.fits') as ret, fits.open(outputs[0]) as saved, fits.open(case / 'frame0.fits') as raw:
                        mask = ret[0].data
                        if len(saved) != 2 or mask.shape != (9, 9) or not np.array_equal(mask, saved[1].data):
                            raise RuntimeError('Returned/saved geometry or pixels: ' + label)
                        if not np.isin(mask, [0, 1]).all() or saved[1].header['EXTNAME'] != raw[1].header['EXTNAME']:
                            raise RuntimeError('Mask polarity or extension identity: ' + label)
                        good = int(mask.sum())
                        if good != int(marker.group(1)) or saved[1].header['ESO MPP QC NGOODPIX'] != good or saved[1].header['ESO MPP QC NBADPIX'] != 81-good:
                            raise RuntimeError('Mask counts: ' + label)
                        pixels_sha = hashlib.sha256(mask.astype(np.uint8).tobytes()).hexdigest()
                        expected = next(c for c in reference['cases'] if c['case'] == label)
                        if pixels_sha != expected['mask_pixels_sha256']:
                            raise RuntimeError('Mac/Chapman3 mask pixels differ: ' + label)
                        if kind == 'known-response':
                            independent = np.ones((9, 9), dtype=np.uint8)
                            independent.flat[0] = independent.flat[40] = 0
                            if not np.array_equal(mask, independent):
                                raise RuntimeError('Known-response mask: ' + label)
                    if any(digest(case / p) != h for p, h in inputs.items()):
                        raise RuntimeError('Staged inputs changed: ' + label)
                    result = dict(case=label, status='passed', good=good, bad=81-good,
                                  pixels_checked=81, mask_pixels_sha256=pixels_sha,
                                  matches_mac=True, inputs_sha256=inputs,
                                  executable_sha256=digest(executable),
                                  returned_sha256=digest(case / 'returned.fits'),
                                  saved_file=outputs[0].name, saved_sha256=digest(outputs[0]))
                    record['cases'].append(result)
                    save(case / 'run-provenance.json', dict(result, schema_version=1,
                        tested_source=identity, parent_manifest=str(provenance), retention_roles=['acceptance_evidence']))
                    save(provenance, record)
                    print('PASS:', label, 'good=%d bad=%d; exact Mac pixels' % (good, 81-good), flush=True)
        check_fixtures()
        if git('rev-parse', 'HEAD') != revision or git('status', '--porcelain', '--untracked-files=all'):
            raise RuntimeError('Checkout changed during qualification')
        record.update(status='passed', fixtures_unchanged=True, checkout_unchanged=True)
    except BaseException as error:
        record.update(status='failed', error=str(error))
        raise
    finally:
        record['protected_files_unchanged'] = all(digest(Path(p)) == h for p, h in protected.items())
        if not record['protected_files_unchanged']:
            record['status'] = 'failed'
        record['completed_utc'] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value['status'] == 'running':
                value.update(status=record['status'], completed_utc=record['completed_utc'])
                save(child, value)
    if record['status'] != 'passed':
        raise RuntimeError('Preservation check failed')
    print('PASS: eight target cases; exact Mac masks; protected files unchanged.')
    print('REPORT:', provenance)


if __name__ == '__main__':
    main()
