"""Compile/run isolated owned-runtime controls; no recipe or FITS processing."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--cc', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    parser.add_argument('--sysroot', type=Path)
    parser.add_argument('--c-standard', choices=('90', '17'), default='90')
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    if not args.cc.is_absolute():
        raise SystemExit('Explicit absolute compiler path required')
    root = args.source_root.resolve(strict=True)
    compiler = args.cc.resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix='m1-runtime-', dir=args.work_parent.resolve(strict=True)))
    print('WORK DIRECTORY:', work, flush=True)
    old = root / 'mefpp2/tests/config_snapshot_contract.py'
    spec = importlib.util.spec_from_file_location('snapshot_contract', old)
    contract = importlib.util.module_from_spec(spec)
    # Do not create __pycache__ in the read-only exported source tree.
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(contract)
    finally:
        sys.dont_write_bytecode = previous
    baseline_path = root / 'docs/architecture/proposed/m1/effective-settings-baseline.json'
    baseline = json.loads(baseline_path.read_text())
    baseline['profiles']['override'] = copy.deepcopy(baseline['profiles']['wfi'])
    override = {'bb->bias_kappa1': 0.123456789012345,
                'bb->pixrej_lo': 0.234567890123456, 'bb->scanrej[0]': 7}
    for field in baseline['registry']:
        if field['legacy_target'] in override:
            baseline['profiles']['override']['values'][field['key_template']]['modeled_stored_value'] = override[field['legacy_target']]
    (work / 'config_snapshot_fixture.h').write_text(contract.fixture_source(baseline))
    # Header-only unit compilation: dimensions use the same measured ABI as the
    # preceding snapshot test. Full native CMake builds perform compiler checks.
    import ctypes
    types = {'CHAR': ctypes.c_char, 'SHORT': ctypes.c_short, 'INT': ctypes.c_int,
             'LONG': ctypes.c_long, 'FLOAT': ctypes.c_float, 'DOUBLE': ctypes.c_double}
    if platform.system() not in ('Linux', 'Darwin'):
        raise SystemExit('Only Linux/Darwin are in scope')
    config = '#include <limits.h>\n' + ''.join('#define SIZEOF_%s %d\n' % (k, ctypes.sizeof(v)) for k, v in types.items())
    config += '#define OS_%s 1\n' % ('LINUX' if platform.system() == 'Linux' else 'DARWIN')
    if struct.pack('=I', 1)[0] == 0:
        config += '#define WORDS_BIGENDIAN 1\n'
    for name in ('mefpp_platform_config.h', 'qfits_platform_config.h'):
        (work / name).write_text(config)
    common = root / 'mefpp2/ins/mef/common'
    sources = [common / 'mef_config.c', common / 'mef_runtime.c', root / 'mefpp2/tests/runtime_lifecycle.c']
    inputs = sources + [common / n for n in ('mef_config.h', 'mef_runtime.h', 'mef_config_fields.def', 'mef_config_members.h', 'mefp_lib.h')]
    inputs += [old, baseline_path, Path(__file__).resolve()]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    executable = work / 'runtime_lifecycle'
    command = [str(compiler), '-std=c' + args.c_standard, '-pedantic-errors',
               '-Wall', '-Wextra', '-Werror', '-UNDEBUG', '-D_DEFAULT_SOURCE=1', '-D_DARWIN_C_SOURCE=1']
    command += ['-I' + str(p) for p in (work, common, root / 'mefpp2/src/include', root / 'mefpp2/qfits5/include')]
    if args.sysroot:
        command += ['-isysroot', str(args.sysroot.resolve(strict=True))]
    if args.sanitize:
        command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
    command += list(map(str, sources)) + ['-o', str(executable)]
    report = {'status': 'running', 'host': platform.node(), 'platform': platform.platform(),
              'python': sys.executable, 'c_standard': args.c_standard,
              'sanitize': args.sanitize, 'commands': [], 'input_sha256': before,
              'diagnostic_environment': {k: os.environ.get(k) for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS', 'LSAN_OPTIONS')}}
    def run(argv, label):
        with (work / (label + '.log')).open('w') as stream:
            result = subprocess.run(argv, cwd=work, stdout=stream, stderr=subprocess.STDOUT, timeout=120)
        report['commands'].append({'argv': argv, 'exit_status': result.returncode, 'log': label + '.log'})
        if result.returncode:
            raise RuntimeError('STOP: inspect ' + str(work / (label + '.log')))
    try:
        run([str(compiler), '--version'], 'compiler')
        run(command, 'compile')
        for profile in baseline['profiles']:
            output = work / (profile + '.json')
            run([str(executable), profile, str(output)], profile)
            if json.loads(output.read_text()) != contract.expected_values(baseline, profile):
                raise RuntimeError('Context config mismatch: ' + profile)
            print('PASS:', profile, 'context configuration and lifecycle controls', flush=True)
        report['status'] = 'runtime-lifecycle-passed'
    except Exception as error:
        report['status'] = 'stopped'
        report['error'] = str(error)
        raise
    finally:
        report['source_unchanged'] = before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
        if not report['source_unchanged']:
            report['status'] = 'stopped-source-changed'
        (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
        print('REPORT:', work / 'run-provenance.json', flush=True)
    if report['status'] != 'runtime-lifecycle-passed':
        raise SystemExit('STOP: source preservation failed')


if __name__ == '__main__':
    main()
