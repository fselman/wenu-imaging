"""Reuse the selected Mac C17 build for explicit zero-spread qualification.

Preserves binary/cache/source backups and receipts; no observations or install.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import tempfile

BASE = '74327c49832a9337fad49a0bec1b5fd7af81cde5'
OLD_BINARY = '4105209f0f0954284f944adfc26387837ffdbec93a98d7556f7a77b063bde469'
ROOT = Path('/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb')
SOURCE = ROOT / 'scalar-qc-c17-source'
QUALIFICATION = ROOT / 'scalar-qc-qualification-c17'
BUILD = QUALIFICATION / 'build'
CACHE = BUILD / 'CMakeCache.txt'
CMAKE = Path('/opt/local/bin/cmake')
RECIPE = BUILD / 'mefpp2/mefpp_bias_recipe'
PYTHON_PREFIX = '/Users/fselman/anaconda3/envs/wenu-imaging'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_cache():
    return dict(line.split('=', 1) for line in CACHE.read_text().splitlines()
                if line and not line.startswith(('#', '//')) and '=' in line)


def setting(cache, name):
    values = [v for k, v in cache.items() if k.split(':', 1)[0] == name]
    require(len(values) == 1, 'Missing/ambiguous cache setting: ' + name)
    return values[0]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', type=Path, required=True)
    p.add_argument('--revision', required=True)
    p.add_argument('--preflight', action='store_true')
    a = p.parse_args()
    # Guard the actual host, checkout, interpreter, binary and full selected cache.
    require(platform.system() == 'Darwin' and socket.gethostname().split('.')[0] == 'MC02VV0HPHTDG', 'Expected selected Intel Mac')
    require(sys.prefix == PYTHON_PREFIX, 'Unexpected normal Astropy Python prefix')
    repo = a.repository.resolve(strict=True)
    require(str(repo) == '/Users/fselman/Developer/wenu-imaging', 'Unexpected checkout')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=repo, text=True).strip()
    require(git('rev-parse', '--show-toplevel') == str(repo), 'Unexpected Git root')
    require(git('remote', 'get-url', 'origin') == 'git@github.com:fselman/wenu-imaging.git', 'Unexpected origin')
    require(git('branch', '--show-current') == 'fix/bias-zero-spread-diagnostic', 'Unexpected branch')
    require(git('rev-parse', 'HEAD') == a.revision and len(a.revision) == 40, 'Revision differs')
    require(not git('status', '--porcelain', '--untracked-files=all'), 'Checkout is dirty')
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, a.revision], cwd=repo, check=True)
    before = read_cache()
    expected = {
        'CMAKE_HOME_DIRECTORY': str(SOURCE), 'CMAKE_COMMAND': str(CMAKE),
        'CMAKE_C_COMPILER': '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang',
        'CMAKE_MAKE_PROGRAM': '/usr/bin/make', 'CMAKE_GENERATOR': 'Unix Makefiles',
        'CMAKE_BUILD_TYPE': 'Release', 'CMAKE_C_FLAGS': '', 'CMAKE_EXE_LINKER_FLAGS': '',
        'CMAKE_OSX_ARCHITECTURES': '', 'CMAKE_OSX_DEPLOYMENT_TARGET': '',
        'CMAKE_OSX_SYSROOT': '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.2.sdk',
        'MEFPP_C_STANDARD': '17', 'MEFPP_SOURCE_REVISION': BASE,
        'MEFPP_BUILD_BIAS_RECIPE': 'ON',
        'MEFPP_ASDF_PREFIX': '/Users/fselman/Software/build/wenu-imaging/mac-asdf16-streams-o8KPDcUm/libasdf-environment',
    }
    for k, v in expected.items():
        require(setting(before, k) == v, 'Selected configuration differs: ' + k)
    require(Path(setting(before, 'MEFPP_ASDF_LIBRARY')).is_file(), 'Selected native ASDF library missing')
    require(digest(RECIPE) == OLD_BINARY, 'Qualified recipe changed; preserve and inspect')
    processes = subprocess.check_output(['ps', '-axo', 'pid=,command='], text=True)
    active = [line for line in processes.splitlines() if (str(BUILD) in line or str(SOURCE) in line)
              and any(s in line for s in ('cmake', '/make', '/clang', 'mefpp_bias_recipe', 'bias_service_probe'))]
    require(not active, 'Selected source/build is active: ' + repr(active))
    # Verify unchanged production sources before overlaying only candidate differences.
    for name in git('ls-tree', '-r', '--name-only', BASE, '--', 'CMakeLists.txt', 'mefpp2', 'third_party').splitlines():
        path = Path(name)
        if '/tests/' not in name and (path.name == 'CMakeLists.txt' or path.suffix in ('.c', '.h', '.def', '.cmake') or name.endswith('.h.in')):
            require((SOURCE / name).read_bytes() == subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=repo), 'Mutable production source differs: ' + name)
    names = git('diff', '--name-only', BASE, a.revision, '--', 'mefpp2').splitlines()
    require(names and all(git('cat-file', '-t', a.revision + ':' + n) == 'blob' for n in names), 'Unexpected deletion or empty overlay')
    print('SOURCE:', SOURCE, '\nBUILD:', BUILD, '\nCANDIDATE:', a.revision, flush=True)
    if a.preflight:
        print('PASS: read-only selected-build/source/binary preflight; no changes')
        return
    # Preserve this attempt, qualified binary, full cache and changed source files.
    work = Path(tempfile.mkdtemp(prefix='zero-spread-' + a.revision[:12] + '-', dir=QUALIFICATION))
    print('WORK DIRECTORY:', work, flush=True)
    shutil.copy2(__file__, work / 'qualification-script.py')
    shutil.copy2(RECIPE, work / 'mefpp_bias_recipe.before')
    shutil.copy2(CACHE, work / 'CMakeCache.before.txt')
    record = dict(status='running', revision=a.revision, binary_before=OLD_BINARY,
                  host=socket.gethostname(), python=sys.executable, overlay=names,
                  source_sha256={}, commands=[], observations_accessed=False, installed=False)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
               VECLIB_MAXIMUM_THREADS='1')
    def run(label, argv, timeout):
        log = work / (label + '.log')
        print('Running:', label, '| log:', log, flush=True)
        command = list(map(str, argv))
        with log.open('x') as stream:
            completed = subprocess.run(command, cwd=BUILD, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
        record['commands'].append(dict(label=label, argv=command, exit_status=completed.returncode, log=str(log), sha256=digest(log)))
        if completed.returncode:
            print('\n'.join(log.read_text(errors='replace').splitlines()[-25:]), flush=True)
            raise RuntimeError(label + ' failed; preserve ' + str(log))
    try:
        for name in names:
            dest = SOURCE / name
            if dest.exists():
                saved = work / 'source-before' / name
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, saved)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(subprocess.check_output(['git', 'show', a.revision + ':' + name], cwd=repo))
            record['source_sha256'][name] = digest(dest)
        # Change only producer provenance in the existing configuration, not the toolchain.
        run('revision-stamp', [CMAKE, '-DMEFPP_SOURCE_REVISION:STRING=' + a.revision, BUILD], 120)
        after = read_cache()
        changed = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
        require(changed == ['MEFPP_SOURCE_REVISION:STRING'], 'Unexpected full-cache changes: ' + repr(changed))
        record['changed_cache_keys'] = changed
        # Incrementally build only the recipe and affected service/legacy probe.
        run('build', [CMAKE, '--build', BUILD, '--target', 'mefpp_bias_recipe', 'bias_service_probe', '--parallel', '2'], 600)
        # Exercise kernel/service/legacy boundaries and exact historical pixels/QC.
        run('service', [sys.executable, '-B', SOURCE / 'mefpp2/tests/bias_service_contract.py',
                       '--source-root', SOURCE, '--probe', BUILD / 'mefpp2/bias_service_probe', '--work-parent', work], 180)
        # One actual native recipe on tiny synthetic FITS; explicit failure is expected.
        run('recipe-zero-spread', [sys.executable, '-B', SOURCE / 'mefpp2/tests/bias_zero_spread_recipe_contract.py',
                                  '--recipe', RECIPE, '--work', work / 'recipe'], 120)
        # Verify full cache, source overlay, checkout and retained binary preservation.
        require(read_cache() == after, 'Cache changed during build/tests')
        require(all(digest(SOURCE / n) == h for n, h in record['source_sha256'].items()), 'Source overlay changed')
        require(not git('status', '--porcelain', '--untracked-files=all') and git('rev-parse', 'HEAD') == a.revision, 'Checkout changed')
        require(digest(work / 'mefpp_bias_recipe.before') == OLD_BINARY, 'Reference backup changed')
        record['recipe_results'] = json.loads((work / 'recipe/results.json').read_text())
        record['binary_after'] = digest(RECIPE)
        record['status'] = 'passed'
    except Exception as error:
        record['status'] = 'stopped'
        record['error'] = str(error)
        raise
    finally:
        (work / 'qualification.json').write_text(json.dumps(record, indent=2) + '\n')
        print('RECEIPT:', work / 'qualification.json', flush=True)
    print('PASS: selected Mac zero-spread service/legacy and native recipe failure gate; no observations or installation')


if __name__ == '__main__':
    main()
