"""Qualify the reviewed bias coordinator in the retained Mac C17 build.

Only synthetic inputs are used. Back up the current binary, cache and overlaid
sources; preserve all previous attempts. No installation or observational run.
"""

import argparse
import hashlib
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

BASE = 'b833aca7df520171d9dcf4f0094a43bb5aad33a6'
CANDIDATE = '36381892f4f768c3a2c7450114f96021fd5c76d7'
BASE_BINARY = '4728e6d00c6c1bb5fc55710a53281910a60ad728fa696363cf8dfb22c3593b14'
BASE_CACHE = 'b09476a9b4ac63e043a292492e289be3aecd295952071b27ea2995c82af0ae4a'
ADAPTER_HASH = '58aeaeb988c56766492cc19a87db115fc1f1b643c0541a7582107e274b600038'
ROOT = Path('/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb')
SOURCE = ROOT / 'scalar-qc-c17-source'
QUALIFICATION = ROOT / 'scalar-qc-qualification-c17'
BUILD = QUALIFICATION / 'build'
CACHE = BUILD / 'CMakeCache.txt'
CMAKE = Path('/opt/local/bin/cmake')
RECIPE = BUILD / 'mefpp2/mefpp_bias_recipe'
ADAPTER = ROOT / 'warning-fix-build/mefpp2/mefpp_m5'
ASDF_PYTHON = Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python')
PYTHON_PREFIX = '/Users/fselman/anaconda3/envs/wenu-imaging'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_cache():
    return dict(line.split('=', 1) for line in CACHE.read_text().splitlines()
                if line and not line.startswith(('#', '//')) and '=' in line)


def setting(cache, name):
    values = [value for key, value in cache.items() if key.split(':', 1)[0] == name]
    require(len(values) == 1, 'Missing/ambiguous cache setting: ' + name)
    return values[0]


def production_file(name):
    path = Path(name)
    return '/tests/' not in name and (
        path.name == 'CMakeLists.txt' or path.suffix in ('.c', '.h', '.def', '.inc', '.cmake')
        or name.endswith('.h.in'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--test-revision', required=True)
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    repository = args.repository.resolve(strict=True)

    def git(*arguments):
        return subprocess.check_output(['git', *arguments], cwd=repository, text=True).strip()

    def source_bytes(revision, name):
        return subprocess.check_output(['git', 'show', revision + ':' + name], cwd=repository)

    # Match the owner's actual-host preflight before touching selected resources.
    require(platform.system() == 'Darwin' and
            socket.gethostname().split('.')[0] == 'MC02VV0HPHTDG', 'Expected selected Intel Mac')
    require(str(repository) == '/Users/fselman/Developer/wenu-imaging', 'Unexpected checkout')
    require(sys.prefix == PYTHON_PREFIX, 'Unexpected Astropy interpreter prefix')
    require(git('remote', 'get-url', 'origin') == 'git@github.com:fselman/wenu-imaging.git',
            'Unexpected origin')
    require(git('branch', '--show-current') == 'refactor/bias-readability', 'Unexpected branch')
    require(git('rev-parse', 'HEAD') == args.test_revision and len(args.test_revision) == 40,
            'Unexpected test checkout revision')
    require(not git('status', '--porcelain', '--untracked-files=all'), 'Checkout is dirty')
    subprocess.run(['git', 'merge-base', '--is-ancestor', CANDIDATE, args.test_revision],
                   cwd=repository, check=True)
    test_changes = git('diff', '--name-only', CANDIDATE, args.test_revision).splitlines()
    require(all(name.startswith(('mefpp2/tests/', 'docs/')) or name == 'AGENTS.md'
                for name in test_changes), 'Test delivery changes production sources')
    before = read_cache()
    require(digest(CACHE) == BASE_CACHE, 'Selected full cache changed since preflight')
    require(setting(before, 'MEFPP_SOURCE_REVISION') == BASE and
            setting(before, 'MEFPP_C_STANDARD') == '17' and
            setting(before, 'MEFPP_BUILD_BIAS_RECIPE') == 'ON' and
            setting(before, 'CMAKE_HOME_DIRECTORY') == str(SOURCE) and
            setting(before, 'CMAKE_COMMAND') == str(CMAKE), 'Selected build differs')
    require(digest(RECIPE) == BASE_BINARY, 'Qualified recipe differs; preserve and inspect')
    require(digest(ADAPTER) == ADAPTER_HASH, 'Frozen reference adapter differs')
    require(ASDF_PYTHON.is_file(), 'Selected ASDF interpreter missing')
    processes = subprocess.check_output(['ps', '-axo', 'pid=,command='], text=True)
    active = [line for line in processes.splitlines()
              if (str(BUILD) in line or str(SOURCE) in line) and any(
                  name in line for name in ('/cmake', '/make', '/clang',
                                           'mefpp_bias_recipe', 'bias_service_probe'))]
    require(not active, 'Selected source/build is active: ' + repr(active))
    production = [name for name in git('ls-tree', '-r', '--name-only', BASE, '--',
                                     'CMakeLists.txt', 'mefpp2', 'third_party').splitlines()
                  if production_file(name)]
    for name in production:
        require((SOURCE / name).is_file() and
                (SOURCE / name).read_bytes() == source_bytes(BASE, name),
                'Mutable production source differs: ' + name)
    names = git('diff', '--name-only', BASE, CANDIDATE, '--', 'mefpp2').splitlines()
    require(names and all(git('cat-file', '-t', CANDIDATE + ':' + name) == 'blob'
                          for name in names), 'Unexpected empty overlay or deletion')
    added = git('diff', '--diff-filter=A', '--name-only', BASE, CANDIDATE, '--', 'mefpp2').splitlines()
    require(all(not (SOURCE / name).exists() for name in added),
            'An added source already exists; retain and inspect')
    print('SOURCE:', SOURCE, '\nBUILD:', BUILD, '\nPRODUCER:', CANDIDATE, flush=True)
    if args.preflight:
        print('PASS: read-only preflight; no changes')
        return

    # Preserve executable/cache and every source owner changed by this attempt.
    work = Path(tempfile.mkdtemp(prefix='readability-' + CANDIDATE[:12] + '-', dir=QUALIFICATION))
    print('WORK DIRECTORY:', work, flush=True)
    shutil.copy2(__file__, work / 'qualification-script.py')
    shutil.copy2(RECIPE, work / 'mefpp_bias_recipe.before')
    shutil.copy2(CACHE, work / 'CMakeCache.before.txt')
    record = dict(status='running', producer_revision=CANDIDATE,
                  test_revision=args.test_revision, host=socket.gethostname(),
                  python=sys.executable, asdf_python=str(ASDF_PYTHON),
                  binary_before=BASE_BINARY, cache_before=BASE_CACHE,
                  reference_adapter_sha256=ADAPTER_HASH, overlay=names,
                  newly_added_sources=added, source_before_sha256={}, source_sha256={},
                  commands=[], results={}, observations_accessed=False, installed=False)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
                       OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       VECLIB_MAXIMUM_THREADS='1')

    def run(label, command, timeout):
        logfile = work / (label + '.log')
        command = list(map(str, command))
        print('Running:', label, '| log:', logfile, flush=True)
        item = dict(label=label, argv=command, log=str(logfile))
        record['commands'].append(item)
        with logfile.open('x') as stream:
            process = subprocess.Popen(command, cwd=BUILD, env=environment,
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
                item['sha256'] = digest(logfile)
        if process.returncode:
            print('\n'.join(logfile.read_text(errors='replace').splitlines()[-35:]), flush=True)
            raise RuntimeError(label + ' failed; retain ' + str(logfile))

    def result(label, path):
        value = json.loads(path.read_text())
        require(value.get('successful') is True, 'Contract did not report success: ' + label)
        record['results'][label] = value

    tests = SOURCE / 'mefpp2/tests'
    common = ['--recipe', RECIPE, '--adapter', ADAPTER, '--asdf-python', ASDF_PYTHON]
    try:
        for name in names:
            destination = SOURCE / name
            if destination.exists():
                saved = work / 'source-before' / name
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, saved)
                record['source_before_sha256'][name] = digest(saved)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source_bytes(CANDIDATE, name))
            record['source_sha256'][name] = digest(destination)

        # Keep the retained compiler/SDK/library configuration; change provenance only.
        run('revision-stamp', [CMAKE, '-DMEFPP_SOURCE_REVISION:STRING=' + CANDIDATE, BUILD], 180)
        configured = read_cache()
        changed = sorted(key for key in before.keys() | configured.keys()
                         if before.get(key) != configured.get(key))
        record['changed_cache_keys'] = changed
        require(changed == ['MEFPP_SOURCE_REVISION:STRING'], 'Unexpected cache changes: ' + repr(changed))
        shutil.copy2(CACHE, work / 'CMakeCache.configured.txt')
        run('build', [CMAKE, '--build', BUILD, '--target', 'mefpp_bias_recipe',
                      'bias_service_probe', 'recipe_run_probe', 'operation_template_probe',
                      '--parallel', '2'], 900)

        record['build_warning_lines'] = [
            line for line in (work / 'build.log').read_text(errors='replace').splitlines()
            if 'warning:' in line]

        # Actual shared run services: exclusive logs, no-clobber, retained failed work.
        run_work = work / 'run-resources'
        run_work.mkdir()
        run('run-resources', [BUILD / 'mefpp2/recipe_run_probe', run_work], 60)
        # Existing inner operation runner: success, early-stop and cleanup ordering.
        run('operation-template', [BUILD / 'mefpp2/operation_template_probe'], 60)
        # Both instruments: exact historical pixels/QC, zero/tiny spread and ownership.
        run('service', [sys.executable, '-B', tests / 'bias_service_contract.py',
                        '--source-root', SOURCE, '--probe', BUILD / 'mefpp2/bias_service_probe',
                        '--work-parent', work], 240)
        # Eight native coordinator groups against the immutable reference adapter.
        # Require FITS/ASDF successes, HDU/mask mapping, no-clobber and typed refusals.
        native_work = work / 'native-recipe'
        native_work.mkdir()
        run('native-recipe', [sys.executable, '-B', tests / 'bias_recipe_contract.py',
                              '--work', native_work, *common], 900)
        result('native-recipe', native_work / 'bias-recipe-results.json')
        # Reuse this attempt's synthetic fixture for selection/primary-image provenance.
        # Require five actual products and four refusals; ASDF independently read.
        header_work = work / 'recipe-envelope'
        run('recipe-envelope', [sys.executable, '-B', tests / 'bias_toml_recipe_contract.py',
                                '--work', header_work, *common, '--revision', CANDIDATE,
                                '--reuse-fixture', native_work], 600)
        result('recipe-envelope', header_work / 'bias-toml-results.json')
        # Independent temporal oracle: lower/default/average, exact input/RON invariance.
        median_work = work / 'recipe-median'
        run('recipe-median', [sys.executable, '-B', tests / 'bias_median_recipe_contract.py',
                              '--work', median_work, *common, '--revision', CANDIDATE,
                              '--reuse-fixture', native_work], 600)
        result('recipe-median', median_work / 'results.json')
        # Actual mask policies and clipped RON must retain FITS/ASDF values and refusals.
        clip_work = work / 'recipe-clipped'
        run('recipe-clipped', [sys.executable, '-B', tests / 'bias_clipped_recipe_contract.py',
                               '--work', clip_work, *common, '--revision', CANDIDATE], 600)
        result('recipe-clipped', clip_work / 'results.json')
        # Exact zero spread must stop with detector/input means before final publication.
        zero_work = work / 'recipe-zero-spread'
        run('recipe-zero-spread', [sys.executable, '-B', tests / 'bias_zero_spread_recipe_contract.py',
                                   '--recipe', RECIPE, '--work', zero_work], 120)
        result('recipe-zero-spread', zero_work / 'results.json')

        require(read_cache() == configured, 'Cache changed during build/tests')
        require(all(digest(SOURCE / name) == value for name, value in record['source_sha256'].items()),
                'Candidate source changed during qualification')
        for name in production:
            if name not in names:
                require((SOURCE / name).read_bytes() == source_bytes(BASE, name),
                        'Unrelated production source changed: ' + name)
        require(digest(work / 'mefpp_bias_recipe.before') == BASE_BINARY, 'Qualified backup changed')
        require(digest(work / 'CMakeCache.before.txt') == BASE_CACHE, 'Cache backup changed')
        require(all(digest(work / 'source-before' / name) == value
                    for name, value in record['source_before_sha256'].items()), 'Source backup changed')
        require(digest(ADAPTER) == ADAPTER_HASH, 'Reference adapter changed')
        require(git('rev-parse', 'HEAD') == args.test_revision and
                not git('status', '--porcelain', '--untracked-files=all'), 'Checkout changed')
        record['status'] = 'passed'
    except BaseException as error:
        record['status'] = 'stopped'
        record['error'] = str(error)
        raise
    finally:
        record['binary_after'] = digest(RECIPE) if RECIPE.is_file() else None
        record['cache_after'] = digest(CACHE) if CACHE.is_file() else None
        (work / 'qualification.json').write_text(json.dumps(record, indent=2) + '\n')
        print('RECEIPT:', work / 'qualification.json', flush=True)
    print('PASS: selected Mac bias readability gate; synthetic only; no installation')


if __name__ == '__main__':
    main()
