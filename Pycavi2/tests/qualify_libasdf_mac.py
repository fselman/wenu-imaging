"""Private Intel Mac libasdf trial, called inside the shared QC preservation guard.

Install only libasdf/dependencies into a fresh run prefix. Reuse existing private
Python ASDF 6.0.0, compile one C17 fixture, retain all logs and package identities.
No activation, mefpp build, observations, production install or cleanup.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    if (platform.system(), platform.machine(), platform.node().split('.')[0]) != (
            'Darwin', 'x86_64', 'MC02VV0HPHTDG'):
        raise RuntimeError('Mac qualification only; Chapman requires its own checked preflight')
    work = args.work.resolve(strict=True)
    source = Path(__file__).resolve().parents[2]
    prefix = work / 'libasdf-environment'
    if prefix.exists():
        raise RuntimeError('Require fresh native library prefix; retain previous attempts')
    private_python = Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment')
    if Path(sys.prefix).resolve() != private_python.resolve():
        raise RuntimeError('Use retained private ASDF Python environment')
    compiler = Path('/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang')
    sdk = Path('/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk')
    conda = Path('/Users/fselman/anaconda3/bin/conda')
    for tool in (compiler, sdk, conda):
        if not tool.exists(): raise RuntimeError('Selected tool missing: ' + str(tool))
    env = dict(os.environ, CONDA_PKGS_DIRS=str(work / 'package-cache'),
               CONDA_ENVS_PATH=str(work / 'conda-envs'), CONDA_SUBDIR='osx-64',
               CONDA_REGISTER_ENVS='false', XDG_CACHE_HOME=str(work / 'cache'),
               PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    for key in ('PYTHONPATH', 'DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH',
                'CONDA_OVERRIDE_GLIBC', 'CONDA_OVERRIDE_OSX', 'CONDA_OVERRIDE_ARCHSPEC'):
        env.pop(key, None)
    commands = []
    def command(label, argv, *, capture=False, timeout=1800, command_env=None):
        argv = list(map(str, argv)); commands.append(dict(label=label, argv=argv))
        print('Running:', label, '| log:', work / (label + '.log'), flush=True)
        with (work / (label + '.log')).open('x') as stream:
            process = subprocess.Popen(argv, cwd=work, env=command_env or env,
                                       stdout=stream, stderr=subprocess.STDOUT)
            elapsed = 0
            while True:
                try:
                    code = process.wait(timeout=30)
                    break
                except subprocess.TimeoutExpired:
                    elapsed += 30
                    print('Still running:', label, '| elapsed:', elapsed, 's', flush=True)
                    if elapsed >= timeout:
                        process.kill(); process.wait()
                        raise RuntimeError('Timed out: ' + label)
        output = (work / (label + '.log')).read_text()
        if code:
            print(output[-12000:], flush=True)
            raise RuntimeError('Failed: ' + label + '; retain this run')
        return output if capture else None
    report = dict(status='failed', libasdf='0.3.0', standard='1.6.0',
                  prefix=str(prefix), python=sys.executable, compiler=str(compiler),
                  host=platform.platform(), commands=commands,
                  scope='synthetic C17/Python interchange, not full ASDF conformance')
    try:
        # Solver checks the real macOS virtual package; never override OS/glibc.
        command('conda-platform', [conda, 'info', '--json'])
        create = [conda, 'create', '--yes', '--prefix', prefix, '--override-channels',
                  '--channel', 'conda-forge', '--strict-channel-priority',
                  'libasdf=0.3.0', 'pkg-config']
        command('libasdf-plan', [*create, '--dry-run', '--json'])
        command('libasdf-create', create)
        command('libasdf-packages', [conda, 'list', '--prefix', prefix, '--json'])
        command('libasdf-explicit', [conda, 'list', '--prefix', prefix, '--explicit'])
        packages = json.loads((work / 'libasdf-packages.log').read_text())
        if [p['version'] for p in packages if p['name'] == 'libasdf'] != ['0.3.0']:
            raise RuntimeError('Unexpected libasdf version')
        pc_env = dict(env, PKG_CONFIG_LIBDIR=str(prefix / 'lib/pkgconfig'),
                      PKG_CONFIG_PATH='', PKG_CONFIG_SYSROOT_DIR='')
        flags = shlex.split(command('libasdf-link-flags',
            [prefix / 'bin/pkg-config', '--cflags', '--libs', 'libasdf'],
            capture=True, command_env=pc_env).strip())
        probe = work / 'asdf16-interop'
        command('compile-c17', [compiler, '-std=c17', '-Wall', '-Wextra', '-O1',
            '-isysroot', sdk, source / 'Pycavi2/tests/asdf16_interop.c',
            '-o', probe, *flags, '-Wl,-rpath,' + str(prefix / 'lib')])
        command('linked-libraries', ['/usr/bin/otool', '-L', probe])
        command('interchange', [sys.executable, '-B', source / 'Pycavi2/tests/asdf16_interop.py',
                                '--probe', probe, '--work', work], timeout=300)
        checks = json.loads((work / 'interchange-results.json').read_text())
        if checks['status'] != 'passed' or len(checks['checks']) != 3:
            raise RuntimeError('Incomplete interchange checks')
        report['status'] = 'passed'
    finally:
        (work / 'libasdf-qualification.json').write_text(json.dumps(report, indent=2)+'\n')
        print('LIBASDF QUALIFICATION:', report['status'], '| retained:', work, flush=True)


if __name__ == '__main__':
    main()
