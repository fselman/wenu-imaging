"""Continue the stopped Mac readability gate after a fixture-only repair (#294).

Preserve the entire previous attempt and reuse its binary/cache and passed groups.
Confirm the exact saved mismatch, then run only the failed and unrun groups.
"""

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import tomllib

import qualify_bias_readability_mac as gate

PREVIOUS = gate.QUALIFICATION / 'readability-36381892f4f7-dkg784s0'
PREVIOUS_HEAD = '7bfe6edd99a1bf15d496ee9257baf29ebf84e2fa'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--test-revision', required=True)
    args = parser.parse_args()
    repository = args.repository.resolve(strict=True)
    require = gate.require
    digest = gate.digest

    def git(*arguments):
        return subprocess.check_output(['git', *arguments], cwd=repository, text=True).strip()

    def contents(revision, name):
        return subprocess.check_output(['git', 'show', revision + ':' + name], cwd=repository)

    require(platform.system() == 'Darwin' and
            socket.gethostname().split('.')[0] == 'MC02VV0HPHTDG', 'Expected selected Intel Mac')
    require(str(repository) == '/Users/fselman/Developer/wenu-imaging' and
            sys.prefix == gate.PYTHON_PREFIX, 'Unexpected checkout or interpreter')
    require(git('remote', 'get-url', 'origin') == 'git@github.com:fselman/wenu-imaging.git',
            'Unexpected origin')
    require(git('branch', '--show-current') == 'refactor/bias-readability' and
            git('rev-parse', 'HEAD') == args.test_revision, 'Unexpected checkout revision')
    require(not git('status', '--porcelain', '--untracked-files=all'), 'Checkout is dirty')
    subprocess.run(['git', 'merge-base', '--is-ancestor', PREVIOUS_HEAD, args.test_revision],
                   cwd=repository, check=True)
    changed = git('diff', '--name-only', PREVIOUS_HEAD, args.test_revision).splitlines()
    require(changed and all(name.startswith(('mefpp2/tests/', 'docs/')) for name in changed),
            'Retry changes production sources')
    before = json.loads((PREVIOUS / 'qualification.json').read_text())
    require(before['status'] == 'stopped' and before['producer_revision'] == gate.CANDIDATE,
            'Unexpected retained attempt')
    passed = ['revision-stamp', 'build', 'run-resources', 'operation-template', 'service', 'native-recipe']
    commands = before['commands']
    require([item['label'] for item in commands] == passed + ['recipe-envelope'] and
            all(item['exit_status'] == 0 for item in commands[:-1]) and
            commands[-1]['exit_status'] == 1, 'Earlier gate results differ')
    for item in commands:
        require(digest(Path(item['log'])) == item['sha256'], 'Earlier command log changed')
    native = json.loads((PREVIOUS / 'native-recipe/bias-recipe-results.json').read_text())
    require(native['successful'] and native['tests'] == 8 and native['real_asdf_exercised'],
            'Earlier complete native groups did not pass')
    require(digest(gate.RECIPE) == before['binary_after'] and
            digest(gate.CACHE) == before['cache_after'], 'Built recipe/cache changed')
    require(gate.read_cache() == dict(line.split('=', 1) for line in
            (PREVIOUS / 'CMakeCache.configured.txt').read_text().splitlines()
            if line and not line.startswith(('#', '//')) and '=' in line), 'Configured cache differs')
    require(digest(gate.ADAPTER) == gate.ADAPTER_HASH, 'Frozen reference adapter changed')
    require(all(digest(gate.SOURCE / name) == value
                for name, value in before['source_sha256'].items()) and all(
            digest(gate.SOURCE / name) == value
            for name, value in record.get('test_overlay_sha256', {}).items()), 'Previous source overlay changed')
    for name in git('ls-tree', '-r', '--name-only', gate.CANDIDATE, '--',
                    'CMakeLists.txt', 'mefpp2', 'third_party').splitlines():
        if gate.production_file(name):
            require((gate.SOURCE / name).read_bytes() == contents(gate.CANDIDATE, name),
                    'Production source differs: ' + name)
    require(tomllib.loads((PREVIOUS / 'native-recipe/bias.toml').read_text())
            ['native']['MEF.BIAS.MEDIAN.EVEN.HANDLING'] == 'lower', 'Fixture policy differs')
    processes = subprocess.check_output(['ps', '-axo', 'pid=,command='], text=True)
    require(not [line for line in processes.splitlines()
                 if (str(gate.BUILD) in line or str(gate.SOURCE) in line) and
                 any(name in line for name in ('/cmake', '/make', '/clang', 'mefpp_bias_recipe'))],
            'Selected source/build is active')

    # Hash only the retained synthetic attempt, never observational directories.
    preserved = {str(path): digest(path) for path in PREVIOUS.rglob('*') if path.is_file()}
    binary_before, cache_before = digest(gate.RECIPE), digest(gate.CACHE)
    work = Path(tempfile.mkdtemp(prefix='readability-fixture-retry-', dir=gate.QUALIFICATION))
    shutil.copy2(__file__, work / 'continuation-script.py')
    print('WORK DIRECTORY:', work, flush=True)
    record = dict(status='running', issue=294, producer_revision=gate.CANDIDATE,
                  test_revision=args.test_revision, previous_attempt=str(PREVIOUS),
                  preserved_attempt_sha256=preserved, reused_passed_groups=passed,
                  binary_before=binary_before, cache_before=cache_before,
                  commands=[], results={}, rebuilt=False, reconfigured=False,
                  observations_accessed=False, installed=False)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
                       OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       VECLIB_MAXIMUM_THREADS='1')

    def run(label, command, timeout):
        log = work / (label + '.log')
        command = list(map(str, command))
        print('Running:', label, '| log:', log, flush=True)
        item = dict(label=label, argv=command, log=str(log))
        record['commands'].append(item)
        with log.open('x') as stream:
            process = subprocess.Popen(command, cwd=gate.BUILD, env=environment,
                                       stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            deadline = time.monotonic() + timeout
            try:
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(command, timeout)
                    try:
                        process.wait(timeout=min(30, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        if time.monotonic() >= deadline:
                            raise
                        print('Still running:', label, flush=True)
            except BaseException:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                item['interrupted'] = True
                raise
            finally:
                item['exit_status'] = process.returncode
                stream.flush()
                item['sha256'] = digest(log)
        if process.returncode:
            print('\n'.join(log.read_text(errors='replace').splitlines()[-35:]), flush=True)
            raise RuntimeError(label + ' failed; retain ' + str(log))

    def result(label, path):
        value = json.loads(path.read_text())
        require(value.get('successful') is True, 'Contract did not succeed: ' + label)
        record['results'][label] = value

    tests = gate.SOURCE / 'mefpp2/tests'
    common = ['--recipe', gate.RECIPE, '--adapter', gate.ADAPTER,
              '--asdf-python', gate.ASDF_PYTHON]
    try:
        # Before modifying test support or repeating products, confirm the actual
        # schema-valid saved ASDF differs by exactly the omitted explicit policy.
        run('confirm-retained-mismatch', [gate.ASDF_PYTHON, '-B',
            repository / 'mefpp2/tests/inspect_bias_reuse_snapshot.py', '--attempt', PREVIOUS], 60)
        # Overlay this one test only. Keep the failed run, products and binary intact.
        name = 'mefpp2/tests/bias_toml_recipe_contract.py'
        saved = work / 'bias_toml_recipe_contract.before.py'
        shutil.copy2(gate.SOURCE / name, saved)
        require(saved.read_bytes() == contents(gate.CANDIDATE, name), 'Test backup differs from producer')
        (gate.SOURCE / name).write_bytes(contents(args.test_revision, name))
        record['test_overlay_sha256'] = {name: digest(gate.SOURCE / name)}
        # Retry five envelope products/four refusals using the passed synthetic fixture.
        envelope = work / 'recipe-envelope'
        run('recipe-envelope', [sys.executable, '-B', tests / 'bias_toml_recipe_contract.py',
            '--work', envelope, *common, '--revision', gate.CANDIDATE,
            '--reuse-fixture', PREVIOUS / 'native-recipe'], 600)
        result('recipe-envelope', envelope / 'bias-toml-results.json')
        # Continue the previously unrun independent temporal-median/FITS/ASDF oracle.
        median = work / 'recipe-median'
        run('recipe-median', [sys.executable, '-B', tests / 'bias_median_recipe_contract.py',
            '--work', median, *common, '--revision', gate.CANDIDATE,
            '--reuse-fixture', PREVIOUS / 'native-recipe'], 600)
        result('recipe-median', median / 'results.json')
        # Continue mask-encoding/clipped-RON checks against real reference pixels/QC.
        clipped = work / 'recipe-clipped'
        run('recipe-clipped', [sys.executable, '-B', tests / 'bias_clipped_recipe_contract.py',
            '--work', clipped, *common, '--revision', gate.CANDIDATE], 600)
        result('recipe-clipped', clipped / 'results.json')
        # Finally require explicit zero-spread diagnostics and no final products.
        zero = work / 'recipe-zero-spread'
        run('recipe-zero-spread', [sys.executable, '-B', tests / 'bias_zero_spread_recipe_contract.py',
            '--recipe', gate.RECIPE, '--work', zero], 120)
        result('recipe-zero-spread', zero / 'results.json')
        record['status'] = 'passed'
    except BaseException as error:
        record['status'] = 'stopped'
        record['error'] = str(error)
        raise
    finally:
        record['binary_unchanged'] = digest(gate.RECIPE) == binary_before
        record['cache_unchanged'] = digest(gate.CACHE) == cache_before
        record['previous_attempt_unchanged'] = preserved == {
            str(path): digest(path) for path in PREVIOUS.rglob('*') if path.is_file()}
        record['reference_adapter_unchanged'] = digest(gate.ADAPTER) == gate.ADAPTER_HASH
        record['checkout_unchanged'] = (git('rev-parse', 'HEAD') == args.test_revision and
                                      not git('status', '--porcelain', '--untracked-files=all'))
        record['source_unchanged_except_test_overlay'] = all(
            digest(gate.SOURCE / name) == record.get('test_overlay_sha256', {}).get(name, value)
            for name, value in before['source_sha256'].items()) and all(
            digest(gate.SOURCE / name) == value
            for name, value in record.get('test_overlay_sha256', {}).items())
        valid = all(record[key] for key in ('binary_unchanged', 'cache_unchanged',
                    'previous_attempt_unchanged', 'reference_adapter_unchanged',
                    'checkout_unchanged', 'source_unchanged_except_test_overlay'))
        if not valid:
            record['status'] = 'stopped'
            record['preservation_error'] = 'Preservation check failed; inspect before proceeding'
        (work / 'qualification.json').write_text(json.dumps(record, indent=2) + '\n')
        print('RECEIPT:', work / 'qualification.json', flush=True)
        require(valid, 'Preservation failed; retain receipt')
    print('PASS: remaining Mac bias gates; prior groups/evidence and executable/cache preserved')


if __name__ == '__main__':
    main()
