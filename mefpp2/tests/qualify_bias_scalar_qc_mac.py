"""Focused Mac gate for additive bias scalar headers; no real observations.

Run from an exported candidate source tree. Reuse the qualified libasdf prefix,
compiler/SDK and old one-detector reference adapter; never rebuild/install them.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--reference-build', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--asdf-python', type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != 'Darwin':
        raise RuntimeError('Actual Mac qualification required')
    if not re.fullmatch('[0-9a-f]{40}', args.revision):
        raise ValueError('Require exact source revision')
    if not sys.executable.startswith('/Users/fselman/anaconda3/envs/wenu-imaging/'):
        raise RuntimeError('Use the established Astropy environment')
    cache = {}
    for line in (args.reference_build / 'CMakeCache.txt').read_text().splitlines():
        if line and not line.startswith(('#', '//')) and '=' in line:
            key_type, value = line.split('=', 1)
            key, kind = key_type.split(':', 1)
            cache[key] = (kind, value)
    prefix = Path(cache['MEFPP_ASDF_PREFIX'][1])
    adapter = args.reference_build / 'mefpp2/mefpp_m5'
    if not adapter.is_file() or not (prefix / 'include/asdf').is_dir():
        raise RuntimeError('Retained qualified reference/runtime missing')
    cmake = Path('/opt/local/bin/cmake')
    if not cmake.is_file() or not args.asdf_python.is_file():
        raise RuntimeError('Selected tool missing')
    work = args.work.absolute()
    work.mkdir()  # Exclusive new evidence directory; no automatic retry.
    build = work / 'build'
    checks = work / 'checks'
    checks.mkdir()
    headers = work / 'headers'
    headers.mkdir()
    # Batch work is always nice >= 10, including direct script invocation.
    priority = os.getpriority(os.PRIO_PROCESS, 0)
    if priority < 10:
        os.nice(10 - priority)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')

    def run(name, argv, timeout):
        print('Running:', name, '| log:', work / (name + '.log'), flush=True)
        with (work / (name + '.log')).open('x') as log:
            result = subprocess.run(list(map(str, argv)), cwd=work, env=env,
                                    stdout=log, stderr=subprocess.STDOUT,
                                    timeout=timeout)
        if result.returncode:
            raise RuntimeError(f'{name} failed: inspect its retained log')

    argv = [cmake, '-S', ROOT, '-B', build, '-DBUILD_TESTING=OFF',
            '-DMEFPP_BUILD_BIAS_RECIPE=ON', '-DMEFPP_BUILD_WARNING_PROBE=OFF',
            '-DMEFPP_BUILD_RESOURCES=OFF',
            '-DMEFPP_SOURCE_REVISION=' + args.revision,
            '-DMEFPP_ASDF_PREFIX=' + str(prefix)]
    for key in ('CMAKE_C_COMPILER', 'CMAKE_OSX_SYSROOT',
                'CMAKE_OSX_DEPLOYMENT_TARGET', 'CMAKE_OSX_ARCHITECTURES',
                'CMAKE_BUILD_TYPE', 'CMAKE_C_FLAGS'):
        if key in cache and cache[key][1]:
            kind, value = cache[key]
            argv.append(f'-D{key}:{kind}={value}')
    run('configure', argv, 120)
    run('build', [cmake, '--build', build, '--target',
                  'mefpp_bias_recipe', 'bias_product_qc_probe', '--parallel', '2'], 600)
    build_text = (work / 'build.log').read_text()
    if re.search(r'\bwarning:', build_text):
        raise RuntimeError('Compiler warning reported: inspect build.log')
    run('native-probe', [build / 'mefpp2/bias_product_qc_probe',
                         ROOT / 'mefpp2/ins/mef/config/omegacam.paf', headers], 60)
    # Independent Astropy parsing of the actual qfits-emitted 80-byte cards.
    from astropy.io import fits
    files = sorted(headers.glob('*.hdr'))
    if len(files) != 8:
        raise RuntimeError('Missing serialized native profile headers')
    for path in files:
        header = fits.Header.fromstring(path.read_bytes().decode('ascii'), sep='')
        for card in header.cards:
            card.verify('exception')
        if header['ESO MPP QC MAPVER'] != 'bias-scalar/1':
            raise RuntimeError('Mapping version mismatch')
        for key in header:
            if key.endswith(' S'):
                base = key[:-2]
                measured = header[key] == 'measured'
                if (base in header) != measured:
                    raise RuntimeError('Unavailable/value collision: ' + base)
    # Changed native publication boundary warrants all eight focused recipe
    # groups, including three successful products, exact legacy cards/pixels,
    # complete FITS/ASDF scalars/context and exclusive-publication failures.
    run('recipe-contract', [sys.executable, '-B', ROOT / 'mefpp2/tests/bias_recipe_contract.py',
                            '--work', checks, '--recipe', build / 'mefpp2/mefpp_bias_recipe',
                            '--adapter', adapter, '--asdf-python', args.asdf_python], 600)
    receipt = dict(successful=True, source_revision=args.revision,
                   native_profiles=8, independent_header_parses=8,
                   compiler_warnings=0, observations_opened=False,
                   installed=False, reference_adapter=str(adapter),
                   recipe_results=json.loads((checks / 'bias-recipe-results.json').read_text()))
    with (work / 'qualification.json').open('x') as stream:
        json.dump(receipt, stream, indent=2)
    print('PASS: focused Mac scalar-QC qualification.', flush=True)
    print('Receipt:', work / 'qualification.json', flush=True)


if __name__ == '__main__':
    main()
