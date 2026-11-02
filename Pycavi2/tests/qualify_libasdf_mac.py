"""Private Intel Mac libasdf trial, called inside the shared QC preservation guard.

Install only libasdf/dependencies into a fresh run prefix. Reuse existing private
Python ASDF 6.0.0, compile one C17 fixture, retain all logs and package identities.
No activation, mefpp build, observations, production install or cleanup.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys


def run_logged(label, argv, *, work, env, commands, capture=False, timeout=1800):
    """Keep machine-readable stdout separate from retained diagnostics.

    Conda 24.11 can emit entry-point warnings even with --no-plugins. A zero
    exit status does not imply empty stderr; never mix it into JSON/link flags.
    """
    argv = list(map(str, argv))
    stdout_path = work / (label + '.log')
    stderr_path = work / (label + '.stderr.log')
    record = dict(label=label, argv=argv, stdout=str(stdout_path), stderr=str(stderr_path))
    commands.append(record)
    print('Running:', label, '| stdout:', stdout_path, '| stderr:', stderr_path, flush=True)
    with stdout_path.open('x') as stdout, stderr_path.open('x') as stderr:
        process = subprocess.Popen(argv, cwd=work, env=env, stdout=stdout, stderr=stderr)
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
                    record['exit_status'] = process.returncode
                    raise RuntimeError('Timed out: ' + label)
    record['exit_status'] = code
    output = stdout_path.read_text()
    diagnostics = stderr_path.read_text()
    if diagnostics:
        print('Diagnostics retained:', stderr_path, flush=True)
    if code:
        print(output[-12000:], flush=True)
        print(diagnostics[-12000:], flush=True)
        raise RuntimeError('Failed: ' + label + '; retain this run')
    return output if capture else None


def prefix_identity(prefix):
    """Hash regular files and record symlinks without following directory links."""
    result = {}
    for base, dirs, files in os.walk(prefix, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(base) / name
            key = str(path.relative_to(prefix))
            if path.is_symlink():
                result[key] = ['symlink', os.readlink(path)]
            elif path.is_file():
                digest = hashlib.sha256()
                with path.open('rb') as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(chunk)
                result[key] = ['file', path.stat().st_mode, digest.hexdigest()]
    return result


def retained_prefix(old, work):
    """Accept only the inspected installed trial and its original passed guards."""
    if old.is_symlink():
        raise RuntimeError('Retained run must not be a symlink')
    old = old.resolve(strict=True)
    if old == work or old.parent != work.parent:
        raise RuntimeError('Retained run must be separate and under the build root')
    outer = json.loads((old / 'qc-qualification.json').read_text())
    native = json.loads((old / 'libasdf-qualification.json').read_text())
    if (outer['revision'] != 'ad42ef7a2795f1420b131e4c0df4feae53b5ed6c' or
            outer['preservation'] != dict(checkout=True, installed_files=True, exported_source=True)):
        raise RuntimeError('Retained run revision/preservation mismatch')
    prefix = old / 'libasdf-environment'
    if prefix.is_symlink() or native['prefix'] != str(prefix) or native['libasdf'] != '0.3.0':
        raise RuntimeError('Retained prefix mismatch')
    passed = {c['label']: c.get('exit_status') for c in native['commands']}
    for label in ('conda-platform', 'libasdf-plan', 'libasdf-create',
                  'libasdf-packages', 'libasdf-explicit', 'libasdf-link-flags'):
        if passed.get(label) != 0:
            raise RuntimeError('Retained provisioning incomplete: ' + label)
    packages = json.loads((old / 'libasdf-packages.log').read_text())
    if [p['version'] for p in packages if p['name'] == 'libasdf'] != ['0.3.0']:
        raise RuntimeError('Retained package inventory mismatch')
    records = [json.loads(p.read_text()) for p in (prefix / 'conda-meta').glob('*.json')]
    matches = [p for p in records if p['name'] == 'libasdf']
    listed = [p for p in packages if p['name'] == 'libasdf'][0]
    if len(matches) != 1 or matches[0]['version'] != '0.3.0' or matches[0]['build'] != listed['build_string']:
        raise RuntimeError('Installed libasdf metadata differs from retained inventory')
    for name in ('include/asdf.h', 'lib/pkgconfig/libasdf.pc', 'bin/pkgconf'):
        if not (prefix / name).is_file():
            raise RuntimeError('Missing retained dependency file: ' + name)
    return prefix


def compiler_command(compiler, sdk, source, probe, prefix, flags):
    # Conda pkgconf can filter its own prefix as a system path. Xcode does not
    # share those defaults: make the selected header and library paths explicit.
    return [compiler, '-std=c17', '-Wall', '-Wextra', '-O1', '-isysroot', sdk,
            '-I' + str(prefix / 'include'), source, '-o', probe,
            '-L' + str(prefix / 'lib'), *flags, '-Wl,-rpath,' + str(prefix / 'lib')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--reuse-libasdf-run', type=Path,
                        help='Reuse inspected installed libasdf prefix without Conda calls')
    args = parser.parse_args()
    if (platform.system(), platform.machine(), platform.node().split('.')[0]) != (
            'Darwin', 'x86_64', 'MC02VV0HPHTDG'):
        raise RuntimeError('Mac qualification only; Chapman requires its own checked preflight')
    work = args.work.resolve(strict=True)
    source = Path(__file__).resolve().parents[2]
    prefix = work / 'libasdf-environment'
    reused_before = None
    if args.reuse_libasdf_run:
        prefix = retained_prefix(args.reuse_libasdf_run, work)
        reused_before = prefix_identity(prefix)
    elif prefix.exists():
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
               CONDA_NO_PLUGINS='true', CONDA_SOLVER='classic', SYSTEM_VERSION_COMPAT='0',
               PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    for key in ('PYTHONPATH', 'DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH',
                'CONDA_OVERRIDE_GLIBC', 'CONDA_OVERRIDE_OSX', 'CONDA_OVERRIDE_ARCHSPEC'):
        env.pop(key, None)
    # Old Conda/Python may report 10.16 on Ventura. Correct the virtual package
    # only to the independently measured real version, never to a newer OS.
    actual_os = subprocess.check_output(['/usr/bin/sw_vers', '-productVersion'],
                                        env=env, text=True).strip()
    if actual_os != '13.7.8':
        raise RuntimeError('Unexpected actual macOS version: ' + actual_os)
    env['CONDA_OVERRIDE_OSX'] = actual_os
    conda_command = [conda, '--no-plugins']
    commands = []
    def command(label, argv, *, capture=False, timeout=1800, command_env=None):
        return run_logged(label, argv, work=work, env=command_env or env,
                          commands=commands, capture=capture, timeout=timeout)
    report = dict(status='failed', libasdf='0.3.0', standard='1.6.0',
                  prefix=str(prefix), python=sys.executable, compiler=str(compiler),
                  host=platform.platform(), commands=commands,
                  actual_macos=actual_os, conda_osx_correction=actual_os,
                  solver='classic', external_plugins_disabled_requested=True,
                  scope='synthetic C17/Python interchange, not full ASDF conformance')
    report['dependency_provisioning'] = not bool(args.reuse_libasdf_run)
    report['reused_run'] = str(args.reuse_libasdf_run) if args.reuse_libasdf_run else None
    try:
        if not args.reuse_libasdf_run:
            command('conda-platform', [*conda_command, 'info', '--json'])
            info = json.loads((work / 'conda-platform.log').read_text())
            virtual = {p[0]: p[1] for p in info['virtual_pkgs']}
            if virtual.get('__osx') != actual_os:
                raise RuntimeError('Conda does not report the verified real macOS version')
            create = [*conda_command, 'create', '--yes', '--prefix', prefix, '--override-channels',
                      '--channel', 'conda-forge', '--strict-channel-priority',
                      '--solver', 'classic', '--repodata-fn', 'repodata.json',
                      'libasdf=0.3.0', 'pkgconf>=2']
            command('libasdf-plan', [*create, '--dry-run', '--json'])
            command('libasdf-create', create)
            command('libasdf-packages', [*conda_command, 'list', '--prefix', prefix, '--json'])
            command('libasdf-explicit', [*conda_command, 'list', '--prefix', prefix, '--explicit'])
            packages = json.loads((work / 'libasdf-packages.log').read_text())
            if [p['version'] for p in packages if p['name'] == 'libasdf'] != ['0.3.0']:
                raise RuntimeError('Unexpected libasdf version')
        pc_env = dict(env, PKG_CONFIG_LIBDIR=str(prefix / 'lib/pkgconfig'),
                      PKG_CONFIG_PATH='', PKG_CONFIG_SYSROOT_DIR='',
                      PKG_CONFIG_ALLOW_SYSTEM_CFLAGS='1', PKG_CONFIG_ALLOW_SYSTEM_LIBS='1')
        flags = shlex.split(command('libasdf-link-flags',
            [prefix / 'bin/pkgconf', '--cflags', '--libs', 'libasdf'],
            capture=True, command_env=pc_env).strip())
        probe = work / 'asdf16-interop'
        command('compile-c17', compiler_command(compiler, sdk,
            source / 'Pycavi2/tests/asdf16_interop.c', probe, prefix, flags))
        command('linked-libraries', ['/usr/bin/otool', '-L', probe])
        command('interchange', [sys.executable, '-B', source / 'Pycavi2/tests/asdf16_interop.py',
                                '--probe', probe, '--work', work], timeout=300)
        checks = json.loads((work / 'interchange-results.json').read_text())
        if checks['status'] != 'passed' or len(checks['checks']) != 3:
            raise RuntimeError('Incomplete interchange checks')
        report['status'] = 'passed'
    finally:
        if reused_before is not None:
            preserved = reused_before == prefix_identity(prefix)
            report['reused_prefix_preserved'] = preserved
            report['reused_prefix_manifest_sha256'] = hashlib.sha256(
                json.dumps(reused_before, sort_keys=True).encode()).hexdigest()
            if not preserved:
                report['status'] = 'failed'
        (work / 'libasdf-qualification.json').write_text(json.dumps(report, indent=2)+'\n')
        print('LIBASDF QUALIFICATION:', report['status'], '| retained:', work, flush=True)
        if reused_before is not None and not report['reused_prefix_preserved']:
            raise RuntimeError('Retained dependency prefix changed')


if __name__ == '__main__':
    main()
