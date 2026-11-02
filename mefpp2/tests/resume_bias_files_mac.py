"""Resume only the failed M5 bias contract with retained actual-Mac C17 binaries.

No rebuild, source overwrite, installation or repetition of four passed tests.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys

BASE = '47123eedaaa31b4464238ffaaf1b690f7d2cde40'
NATIVE = 'f20a9ab7a0758775d020480be1e1daa547716e3b'
OLD = Path('/Users/fselman/Software/build/wenu-imaging/mac-m5-bias-c17-JvkN2Fl6')
REPO = Path('/Users/fselman/Developer/wenu-imaging')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    require(platform.system() == 'Darwin' and platform.machine() == 'x86_64' and
            platform.node().split('.')[0] == 'MC02VV0HPHTDG', 'Wrong host')
    require(Path(sys.prefix) == Path('/Users/fselman/anaconda3/envs/wenu-imaging'), 'Wrong Python')
    require(os.getpriority(os.PRIO_PROCESS, 0) >= 10, 'Require niceness >=10')
    run = args.run.resolve(strict=True)
    require(run.parent == Path('/Users/fselman/Software/build/wenu-imaging') and
            not args.run.is_symlink(), 'Unexpected retry directory')
    require({p.name for p in run.iterdir()} == {'resume.py', 'bias_files_contract.py'}, 'Retry is not fresh')

    def git(*parts):
        return subprocess.check_output(['/usr/bin/git', '-C', str(REPO), *parts])

    require(len(args.revision) == 40 and git('rev-parse', args.revision).decode().strip() == args.revision,
            'Require exact correction commit')
    for leaf, tracked in [('resume.py', 'resume_bias_files_mac.py'),
                          ('bias_files_contract.py', 'bias_files_contract.py')]:
        require((run / leaf).read_bytes() == git('show', args.revision + ':mefpp2/tests/' + tracked),
                'Retry script differs from pinned source')
    changed = git('diff', '--name-only', NATIVE, args.revision).decode().splitlines()
    require(set(changed) <= {'mefpp2/tests/bias_files_contract.py',
                            'mefpp2/tests/resume_bias_files_mac.py',
                            'docs/developer/m5-bias-template-2026-11-02.md'},
            'Correction includes changes outside test/documentation scope')
    previous = json.loads((OLD / 'qualification.json').read_text())
    require(previous['revision'] == NATIVE and previous['status'] == 'failed' and
            all(previous['preservation'].values()), 'Unexpected original qualification')
    source = OLD / 'source'
    expected_source = previous['source_sha256']

    def source_hashes():
        return {str(p.relative_to(source)): sha(p) for p in sorted(source.rglob('*')) if p.is_file()}

    require(source_hashes() == expected_source, 'Original failed-run export changed')
    evidence = OLD / 'build-c17/mefpp2/test-work/m5-bias-q9vj_ndd/qualification.json'
    failed = json.loads(evidence.read_text())
    require(failed['status'] == 'failed' and not failed['profiles'], 'Unexpected failed bias evidence')
    adapter = OLD / 'build-c17/mefpp2/mefpp_m5'
    legacy = OLD / 'build-c17/mefpp2/mefpp'
    require(sha(adapter) == failed['adapter_sha256'] and sha(legacy) == failed['legacy_sha256'],
            'Retained binary identity changed')
    guard = runpy.run_path(str(source / 'Pycavi2/tests/qualify_inspection_stages.py'))
    before = guard['checkout'](REPO)
    require(before['branch'] == 'main' and before['head'] == BASE and not before['status'] and
            before['upstream'] == 'origin/main', 'Expected clean unchanged main')
    protected = guard['protected_paths']()
    installation = [guard['identity'](p) for p in protected]
    preserved_files = [OLD / 'qualification.json', OLD / 'tests-c17.log', evidence]
    hashes = {str(p): sha(p) for p in preserved_files}
    argv = [sys.executable, '-B', str(run / 'bias_files_contract.py'), '--source-root', str(source),
            '--adapter', str(adapter), '--legacy', str(legacy), '--work-parent', str(run)]
    report = dict(status='running', correction_revision=args.revision, native_revision=NATIVE,
                  inherited_qualification=str(OLD), test='native_bias_files only', argv=argv,
                  rebuild=False, installation=False, original_evidence_sha256=hashes,
                  binaries={'adapter': sha(adapter), 'legacy': sha(legacy)})
    print('RETAINED RETRY:', run, flush=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
               PYTHONPATH=str(source / 'mefpp2/tests'), OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
               MEFPP_TEST_REVISION=NATIVE)
    env.pop('E_LOGFILE', None)
    passed = False
    try:
        with (run / 'bias-files.log').open('x') as stream:
            result = subprocess.run(argv, cwd=run, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=600)
        report['exit_status'] = result.returncode
        print((run / 'bias-files.log').read_text(), flush=True)
        require(result.returncode == 0, 'Bias contract failed; retain this attempt')
        passed = True
    finally:
        checks = dict(checkout=before == guard['checkout'](REPO),
                      installation=installation == [guard['identity'](p) for p in protected],
                      original_source=source_hashes() == expected_source,
                      original_evidence=hashes == {str(p): sha(p) for p in preserved_files},
                      binaries=sha(adapter) == failed['adapter_sha256'] and sha(legacy) == failed['legacy_sha256'])
        report['preservation'] = checks
        report['status'] = 'passed' if passed and all(checks.values()) else 'failed'
        (run / 'resume-qualification.json').write_text(json.dumps(report, indent=2) + '\n')
        print('RESUME QUALIFICATION:', report['status'])
        print('PRESERVATION:', checks)
        print('RETAINED RETRY:', run)
        require(all(checks.values()), 'Preservation failure')


if __name__ == '__main__':
    main()
