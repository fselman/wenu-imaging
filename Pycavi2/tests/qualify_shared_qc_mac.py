"""Guarded shared QC qualification; optional isolated libasdf/C17 interchange.

Run guards with installed Python, tests with retained private ASDF Python.
Only --with-libasdf provisions a fresh native dependency prefix and compiles a
synthetic C17 probe. No observation processing, installed environment changes,
checkout changes or repetition of native bias tests.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys
import tarfile

BASE = '47123eedaaa31b4464238ffaaf1b690f7d2cde40'
REPO = Path('/Users/fselman/Developer/wenu-imaging')
PRIVATE = Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--with-libasdf', action='store_true',
                        help='Also provision isolated libasdf 0.3.0 and run one C17 interchange probe')
    args = parser.parse_args()
    require(platform.system() == 'Darwin' and platform.machine() == 'x86_64' and
            platform.node().split('.')[0] == 'MC02VV0HPHTDG', 'Wrong host')
    require(Path(sys.prefix).resolve() == Path('/Users/fselman/anaconda3/envs/wenu-imaging').resolve(),
            'Run guard in installed base environment; tests use retained private ASDF venv')
    require(os.getpriority(os.PRIO_PROCESS, 0) >= 10, 'Require niceness >=10')
    run = args.run.resolve(strict=True)
    require(run.parent == Path('/Users/fselman/Software/build/wenu-imaging') and
            not args.run.is_symlink() and {p.name for p in run.iterdir()} == {'qualify.py'}, 'Unexpected/fresh run required')

    def git(*parts):
        return subprocess.check_output(['/usr/bin/git', '-C', str(REPO), *parts])

    require(len(args.revision) == 40 and git('rev-parse', args.revision).decode().strip() == args.revision,
            'Require exact fetched revision')
    require(Path(__file__).read_bytes() == git('show', args.revision + ':Pycavi2/tests/qualify_shared_qc_mac.py'),
            'Runner differs from pinned source')
    guard_path = REPO / 'Pycavi2/tests/qualify_inspection_stages.py'
    require(guard_path.read_bytes() == git('show', BASE + ':Pycavi2/tests/qualify_inspection_stages.py'),
            'Protection helper changed')
    guard = runpy.run_path(str(guard_path))
    before = guard['checkout'](REPO)
    require(before['branch'] == 'main' and before['head'] == BASE and before['upstream'] == 'origin/main' and
            not before['status'], 'Expected clean main')
    protected = guard['protected_paths']()
    installation = [guard['identity'](p) for p in protected]
    archive = git('archive', '--format=tar', args.revision)
    source = run / 'source'; source.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle.getmembers():
            path = Path(member.name)
            require(not path.is_absolute() and '..' not in path.parts and
                    (member.isfile() or member.isdir()), 'Unsafe export member')
        bundle.extractall(source)
    source_before = {str(p.relative_to(source)): sha(p) for p in sorted(source.rglob('*')) if p.is_file()}
    argv = [str(PRIVATE / 'bin/python'), '-B', str(source / 'Pycavi2/tests/test_shared_qc.py'), '--work', str(run)]
    report = dict(status='running', revision=args.revision, python=sys.executable,
                  prefix=sys.prefix, archive_sha256=hashlib.sha256(archive).hexdigest(), argv=argv,
                  scope='shared QC metadata/ASDF only; no numerical recipe/estimator acceptance',
                  production_installation_performed=False, private_dependency_provisioning=False,
                  native_execution=False, observations_opened=False)
    print('RETAINED QC RUN:', run, flush=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    env.pop('PYTHONPATH', None)
    finished = False
    try:
        with (run / 'qc-contract.log').open('x') as stream:
            result = subprocess.run(argv, cwd=run, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=300)
        report['exit_status'] = result.returncode
        print((run / 'qc-contract.log').read_text(), flush=True)
        require(result.returncode == 0, 'Shared QC contract failed; retain this run')
        contract = json.loads((run / 'qc-contract-results.json').read_text())
        require(contract['successful'] and contract['tests'] == 10 and not contract['network_attempts'],
                'Unexpected contract inventory or network attempt')
        if args.with_libasdf:
            native_argv = [str(PRIVATE / 'bin/python'), '-B',
                           str(source / 'Pycavi2/tests/qualify_libasdf_mac.py'), '--work', str(run)]
            report['native_argv'] = native_argv
            report['native_execution'] = True
            report['private_dependency_provisioning'] = True
            subprocess.run(native_argv, cwd=run, env=env, check=True)
        finished = True
    finally:
        checks = dict(checkout=before == guard['checkout'](REPO),
                      installed_files=installation == [guard['identity'](p) for p in protected],
                      exported_source=source_before == {str(p.relative_to(source)): sha(p)
                                                       for p in sorted(source.rglob('*')) if p.is_file()})
        report['preservation'] = checks
        report['status'] = 'passed' if finished and all(checks.values()) else 'failed'
        (run / 'qc-qualification.json').write_text(json.dumps(report, indent=2)+'\n')
        print('QC QUALIFICATION:', report['status'])
        print('PRESERVATION:', checks)
        print('RETAINED QC RUN:', run)
        require(all(checks.values()), 'Preservation failure')


if __name__ == '__main__':
    main()
