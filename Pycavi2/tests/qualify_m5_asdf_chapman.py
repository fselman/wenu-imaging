"""Chapman4 C17 bias/private installation and external ASDF 1.6 qualification.

Use the retained qualified Python ASDF environment. Provision external libasdf
only in a fresh prefix under the retained run. Never override platform limits,
activate environments, replace the selected engine, or open observations.
"""
import argparse
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import re
import runpy
import shlex
import subprocess
import sys
import tarfile

REPO = Path('/home1/fselman/Software/wenu-imaging')
BASE_PYTHON = Path('/home/fselman/.conda/envs/wenu-imaging/bin/python')
PRIVATE = Path('/home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC/D2-private-s6qsxbqf/environment')
BRANCH = 'feat/m5-bias-template-20261102'
TOOLS = dict(compiler=Path('/opt/rh/devtoolset-10/root/usr/bin/gcc'),
    cmake=Path('/home/fselman/opt/cmake-3.29.6/bin/cmake'),
    ctest=Path('/home/fselman/opt/cmake-3.29.6/bin/ctest'), make=Path('/usr/bin/make'),
    ar=Path('/usr/bin/ar'), ranlib=Path('/usr/bin/ranlib'))


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(source):
    return {str(p.relative_to(source)): sha(p) for p in sorted(source.rglob('*')) if p.is_file()}


def installed_packages():
    return sorted((d.metadata['Name'], d.version, str(d.locate_file('')))
                  for d in importlib.metadata.distributions())


def check_virtual_platform(info, actual):
    virtual = {p[0]: p[1] for p in info['virtual_pkgs']}
    require(info['platform'] == 'linux-64' and virtual.get('__glibc') == actual,
            'Conda must report actual linux-64/glibc limits; no override/fallback')


def conda_cli(conda, command):
    """Select only options advertised by this installed Conda, before solving."""
    version = command('conda-version', [conda, '--version'], capture=True).strip()
    match = re.fullmatch(r'conda (\d+)\.(\d+)(?:[^\s]*)', version)
    require(match is not None, 'Unrecognized Conda version: ' + version)
    release = tuple(map(int, match.groups()))
    require(release >= (4, 7), 'Conda predates required repodata/platform support; inspect before proceeding')
    global_help = command('conda-help', [conda, '--help'], capture=True)
    global_options = set(re.findall(r'--[a-z][a-z-]*', global_help))
    base = [conda]
    if '--no-plugins' in global_options:
        base += ['--no-plugins']
    create_help = command('conda-create-help', [*base, 'create', '--help'], capture=True)
    create_options = set(re.findall(r'--[a-z][a-z-]*', create_help))
    for option in ('--repodata-fn', '--strict-channel-priority', '--dry-run', '--json', '--prefix'):
        require(option in create_options, 'Required Conda create option absent: ' + option)
    if '--solver' in create_options:
        solver = ['--solver', 'classic']
    elif '--experimental-solver' in create_options:
        solver = ['--experimental-solver', 'classic']
    else:
        require(release < (22, 11), 'Modern Conda lacks expected solver selection; inspect before proceeding')
        solver = []  # Legacy releases have only the classic solver.
    return base, solver, dict(version=version, no_plugins_cli='--no-plugins' in global_options,
        solver_arguments=solver, legacy_classic_default=not solver,
        note='CONDA_NO_PLUGINS/CONDA_SOLVER requested in child environment; no installed configuration changes')


def recorded_funpack():
    # Reuse the selected executable from the accepted installed-runtime build.
    old = Path('/home1/fselman/Software/build/wenu-imaging/chapman-large-file-install-SLEBL3NJ')
    require(old.is_dir(), 'Missing retained accepted runtime installation')
    values = set()
    for cache in old.rglob('CMakeCache.txt'):
        for line in cache.read_text().splitlines():
            match = re.fullmatch(r'MEFPP_FUNPACK:(?:FILEPATH|STRING)=(.+)', line)
            if match:
                values.add(match[1])
    require(len(values) == 1, 'Missing/ambiguous previously selected funpack; inspect retained build')
    path = Path(values.pop())
    require(path.is_absolute() and path.is_file() and os.access(path, os.X_OK), 'Recorded funpack unavailable')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    require((platform.system(), platform.machine(), platform.node().split('.')[0]) ==
            ('Linux', 'x86_64', 'chapman4'), 'Chapman4 only')
    require(Path(sys.prefix).resolve() == BASE_PYTHON.parent.parent.resolve() and
            Path(sys.executable).resolve() == BASE_PYTHON.resolve(), 'Use installed imaging Python guard')
    require(os.getpriority(os.PRIO_PROCESS, 0) >= 10, 'Require niceness >=10')
    require(platform.libc_ver() == ('glibc', '2.17'), 'Require actual Chapman glibc 2.17')
    run = args.run.resolve(strict=True)
    require(not args.run.is_symlink() and run.parent == (Path.home() / 'Software/build/wenu-imaging').resolve()
            and {p.name for p in run.iterdir()} == {'qualify.py'}, 'Require fresh retained run')
    def git(*parts):
        return subprocess.check_output(['/usr/bin/git', '-C', str(REPO), *parts])
    require(len(args.revision) == 40 and git('rev-parse', 'HEAD').decode().strip() == args.revision,
            'Expected exact candidate checkout')
    require(Path(__file__).read_bytes() == git('show', args.revision + ':Pycavi2/tests/qualify_m5_asdf_chapman.py'),
            'Runner differs from pinned source')
    guard = runpy.run_path(str(REPO / 'Pycavi2/tests/qualify_inspection_stages.py'))
    before = guard['checkout'](REPO)
    require(before['branch'] == BRANCH and before['upstream'] == 'origin/' + BRANCH and
            not before['status'] and before['origin'] == before['push'] == 'https://github.com/fselman/wenu-imaging.git',
            'Expected exact clean candidate tracking its origin branch')
    protected = guard['protected_paths']()
    install_before = [guard['identity'](p) for p in protected]
    packages_before = installed_packages()
    require((PRIVATE / 'bin/python').is_file(), 'Missing retained Python ASDF environment')
    private_identity = runpy.run_path(str(REPO / 'Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    private_before = private_identity(PRIVATE)
    funpack = recorded_funpack()
    archive = git('archive', '--format=tar', args.revision)
    source = run / 'source'; source.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle.getmembers():
            path = Path(member.name)
            require(not path.is_absolute() and '..' not in path.parts and
                    (member.isfile() or member.isdir()), 'Unsafe export member')
        bundle.extractall(source)
    exported_before = snapshot(source)
    run_logged = runpy.run_path(str(source / 'Pycavi2/tests/qualify_libasdf_mac.py'))['run_logged']
    commands = []
    report = dict(status='failed', revision=args.revision, host=platform.platform(),
        actual_glibc='2.17', source_archive_sha256=hashlib.sha256(archive).hexdigest(), commands=commands,
        python=str(BASE_PYTHON), private_python=str(PRIVATE / 'bin/python'), funpack=str(funpack),
        scope='synthetic bias contracts, private normal runtime install and ASDF 1.6 interchange',
        production_activation=False, observations_opened=False, standard='1.6.0', libasdf='0.3.0')
    print('RETAINED CHAPMAN RUN:', run, flush=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
        OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
        CONDA_PKGS_DIRS=str(run / 'package-cache'), CONDA_ENVS_PATH=str(run / 'conda-envs'),
        CONDA_REGISTER_ENVS='false', CONDA_NO_PLUGINS='true', CONDA_SOLVER='classic',
        CONDA_SUBDIR='linux-64', XDG_CACHE_HOME=str(run / 'cache'))
    for key in list(env):
        if key.startswith('CONDA_OVERRIDE_') or key in ('PYTHONPATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH',
                'DYLD_LIBRARY_PATH', 'CC', 'CXX', 'CFLAGS', 'CPPFLAGS', 'LDFLAGS', 'CPATH',
                'LIBRARY_PATH', 'C_INCLUDE_PATH', 'GCC_EXEC_PREFIX', 'COMPILER_PATH',
                'PKG_CONFIG_PATH', 'PKG_CONFIG_LIBDIR', 'PKG_CONFIG_SYSROOT_DIR', 'DESTDIR'):
            env.pop(key, None)
    def command(label, argv, *, capture=False, timeout=1800, command_env=None):
        return run_logged(label, argv, work=run, env=command_env or env,
                          commands=commands, capture=capture, timeout=timeout)
    conda = Path('/home/fselman/anaconda3/bin/conda')
    prefix = run / 'libasdf-environment'
    library_before = None
    try:
        # Package gate first: respect real glibc before launching functional tests.
        conda_base, solver_options, capabilities = conda_cli(conda, command)
        report['conda_capabilities'] = capabilities
        info = json.loads(command('conda-platform', [*conda_base, 'info', '--json'], capture=True))
        check_virtual_platform(info, '2.17')
        create = [*conda_base, 'create', '--yes', '--prefix', prefix,
            '--override-channels', '--channel', 'conda-forge', '--strict-channel-priority',
            *solver_options, '--repodata-fn', 'repodata.json', 'libasdf=0.3.0', 'pkgconf>=2']
        command('libasdf-plan', [*create, '--dry-run', '--json'])
        command('libasdf-create', create)
        packages = json.loads(command('libasdf-packages',
            [*conda_base, 'list', '--prefix', prefix, '--json'], capture=True))
        require([p['version'] for p in packages if p['name'] == 'libasdf'] == ['0.3.0'], 'Unexpected libasdf')
        command('libasdf-explicit', [*conda_base, 'list', '--prefix', prefix, '--explicit'])
        library_before = private_identity(prefix)
        report['external_prefix'] = str(prefix)
        # Run the shared QC schema/sidecar/traversal contracts once on this platform.
        qc_work = run / 'qc'; qc_work.mkdir()
        command('shared-qc', [PRIVATE / 'bin/python', '-B', source / 'Pycavi2/tests/test_shared_qc.py',
                              '--work', qc_work], timeout=300)
        qc = json.loads((qc_work / 'qc-contract-results.json').read_text())
        require(qc['successful'] and qc['tests'] == 10 and not qc['network_attempts'], 'Incomplete shared QC gate')
        report['shared_qc'] = qc
        # Build only the standalone C17 ASDF consumer; do not link ASDF into mefpp.
        pc_env = dict(env, PKG_CONFIG_LIBDIR=str(prefix / 'lib/pkgconfig'), PKG_CONFIG_PATH='',
            PKG_CONFIG_SYSROOT_DIR='', PKG_CONFIG_ALLOW_SYSTEM_CFLAGS='1', PKG_CONFIG_ALLOW_SYSTEM_LIBS='1')
        flags = shlex.split(command('libasdf-link-flags', [prefix / 'bin/pkgconf', '--cflags', '--libs', 'libasdf'],
                                    command_env=pc_env, capture=True))
        probe = run / 'asdf16-interop'
        command('compile-asdf-c17', [TOOLS['compiler'], '-std=c17', '-Wall', '-Wextra', '-O1',
            '-I' + str(prefix / 'include'), source / 'Pycavi2/tests/asdf16_interop.c', '-o', probe,
            '-L' + str(prefix / 'lib'), *flags, '-Wl,-rpath,' + str(prefix / 'lib')])
        linked = command('linked-libraries', ['/usr/bin/ldd', probe], capture=True)
        require('not found' not in linked and str(prefix / 'lib/libasdf') in linked,
                'Unexpected/missing linked ASDF library')
        command('interchange', [PRIVATE / 'bin/python', '-B', source / 'Pycavi2/tests/asdf16_interop.py',
                                '--probe', probe, '--work', run], timeout=300)
        interchange = json.loads((run / 'interchange-results.json').read_text())
        require(interchange['status'] == 'passed' and len(interchange['checks']) == 3 and
                not interchange['network_attempts'], 'Incomplete interchange gate')
        report['interchange'] = interchange
        # C17 native bias/template/layout/path controls plus a separate runtime install.
        native = run / 'native'; native.mkdir()
        argv = [BASE_PYTHON, '-B', source / 'mefpp2/tests/qualify_bias_files_mac.py', '--host', 'chapman',
            '--candidate-checkout', '--private-install', '--funpack', funpack,
            '--revision', args.revision, '--run', native]
        for name, path in TOOLS.items():
            argv += ['--' + name, path]
        command('native-bias-install-c17', argv, timeout=1800)
        native_report = json.loads((native / 'qualification.json').read_text())
        require(native_report['status'] == 'passed' and native_report['installation_performed'] and
                all(native_report['preservation'].values()), 'Native bias/install qualification failed')
        report['native_report'] = str(native / 'qualification.json')
        report['status'] = 'passed'
    finally:
        checks = dict(checkout=before == guard['checkout'](REPO),
            installed_files=install_before == [guard['identity'](p) for p in protected],
            production_packages=packages_before == installed_packages(),
            retained_python_environment=private_before == private_identity(PRIVATE),
            exported_source=exported_before == snapshot(source))
        if library_before is not None:
            checks['external_prefix_after_install'] = library_before == private_identity(prefix)
        report['preservation'] = checks
        if not all(checks.values()):
            report['status'] = 'failed'
        (run / 'chapman-qualification.json').write_text(json.dumps(report, indent=2) + '\n')
        print('CHAPMAN QUALIFICATION:', report['status'], flush=True)
        print('PRESERVATION:', checks, flush=True)
        print('RETAINED RUN:', run, flush=True)
        require(all(checks.values()), 'Preservation failure')


if __name__ == '__main__':
    main()
