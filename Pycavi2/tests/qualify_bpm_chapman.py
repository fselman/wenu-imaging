"""Chapman4 changed-code gate after the actual Mac BPM completion receipt.

Synthetic C17/ASDF contracts only, no Conda/install/activation/observations.
Export the candidate privately while preserving the existing bias-branch checkout.
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
import subprocess
import sys
import tarfile

REPO = Path('/home1/fselman/Software/wenu-imaging')
BASE_PYTHON = Path('/home/fselman/.conda/envs/wenu-imaging/bin/python')
PRIVATE = Path('/home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC/D2-private-s6qsxbqf/environment')
OLD = Path('/home1/fselman/Software/build/wenu-imaging/chapman-m5-asdf16-resume-U4vTGDyf')
CHECKOUT = '07d27330555712ef6bf59a068a578b450e89b4a3'
MAC = '022cf3683fe47d4de6a7acac1e3799cb49201d40'
PREVIOUS = '4417d7d159d08afcff2fbb8518fc90c3f4c84e29'
BRANCH = 'feat/m5-bias-template-20261102'
TOOLS = dict(compiler=Path('/opt/rh/devtoolset-10/root/usr/bin/gcc'),
    cmake=Path('/home/fselman/opt/cmake-3.29.6/bin/cmake'),
    ctest=Path('/home/fselman/opt/cmake-3.29.6/bin/ctest'),
    make=Path('/usr/bin/make'), ar=Path('/usr/bin/ar'), ranlib=Path('/usr/bin/ranlib'))
TESTS = {'native_measurement_stats', 'native_bpm_response', 'native_bpm_service',
         'native_bpm_files', 'native_bpm_publication', 'native_bpm_completion',
         'native_bias_qc_asdf', 'native_bias_files', 'native_bias_service',
         'native_eclipse_allocation', 'native_layout'}
TARGETS = ['measurement_stats_probe', 'bpm_response_probe', 'bpm_service_probe',
           'bpm_files_probe', 'bpm_publication_probe', 'mefpp_m5', 'mefpp',
           'bias_service_probe', 'eclipse_allocation_probe', 'layout_probe']


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def snapshot(source):
    return {str(p.relative_to(source)): sha(p) for p in sorted(source.rglob('*')) if p.is_file()}


def packages():
    return sorted((d.metadata['Name'], d.version, str(d.locate_file('')))
                  for d in importlib.metadata.distributions())


def validate_host():
    require((platform.system(), platform.machine(), platform.node().split('.')[0]) ==
            ('Linux', 'x86_64', 'chapman4'), 'Chapman4 only; no directory creation')
    require(platform.libc_ver() == ('glibc', '2.17'), 'Actual glibc 2.17 required')
    require(Path(sys.prefix).resolve() == BASE_PYTHON.parent.parent.resolve() and
            Path(sys.executable).resolve() == BASE_PYTHON.resolve(), 'Use installed imaging guard Python')
    require(os.getpriority(os.PRIO_PROCESS, 0) >= 10, 'Require niceness >=10')


def test_inventory(payload):
    require({t['name'] for t in payload['tests']} == TESTS and len(payload['tests']) == len(TESTS),
            'Unexpected focused Chapman test inventory')


def prior_receipt(report):
    require(report.get('status') == 'passed' and report.get('revision') == PREVIOUS and
            report.get('actual_glibc') == '2.17' and report.get('private_python') == str(PRIVATE/'bin/python') and
            set(report.get('preservation', {})) == {'checkout','installed_files','production_packages',
                'retained_python_environment','exported_source','external_prefix_after_install'} and
            all(report['preservation'].values()) and
            report.get('shared_qc', {}).get('successful') and report['shared_qc'].get('tests') == 10 and
            report['shared_qc'].get('network_attempts') == [] and
            report.get('interchange', {}).get('status') == 'passed', 'Retained Chapman receipt mismatch')


def main():
    validate_host()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--revision', required=True)
    p.add_argument('--run', type=Path, required=True)
    a = p.parse_args()
    def git(*parts):
        return subprocess.check_output(['/usr/bin/git', '-C', str(REPO), *parts])
    require(re.fullmatch('[0-9a-f]{40}', a.revision) and
            git('rev-parse', a.revision+'^{commit}').decode().strip() == a.revision, 'Pin exact fetched source')
    require(Path(__file__).read_bytes() == git('show', a.revision+':Pycavi2/tests/qualify_bpm_chapman.py'),
            'Runner differs from pinned source')
    # No native/build/QC component changes since the returned actual Mac gate.
    # Runner/docs can advance without asking for an unchanged Mac test replay.
    for name in ('CMakeLists.txt', 'mefpp2', 'third_party', 'Pycavi2/pycavi'):
        require(git('rev-parse', a.revision+':'+name) == git('rev-parse', MAC+':'+name),
                'Mac-qualified native/build/QC tree changed: '+name)
    helper = REPO/'Pycavi2/tests/qualify_inspection_stages.py'
    require(helper.read_bytes() == git('show', MAC+':Pycavi2/tests/qualify_inspection_stages.py'), 'Protection helper changed')
    guard = runpy.run_path(str(helper))
    before = guard['checkout'](REPO)
    require(before['head'] == CHECKOUT and before['branch'] == BRANCH and before['upstream'] == 'origin/'+BRANCH and
            before['origin'] == before['push'] == 'https://github.com/fselman/wenu-imaging.git' and not before['status'],
            'Expected known clean protected Chapman checkout; do not switch it')
    run = a.run.resolve(strict=True)
    require(not a.run.is_symlink() and run.parent == (Path.home()/'Software/build/wenu-imaging').resolve() and
            {f.name for f in run.iterdir()} == {'qualify.py'}, 'Fresh retained build directory required')
    require((PRIVATE/'bin/python').is_file(), 'Retained ASDF environment missing')
    old_report_path = OLD/'chapman-qualification.json'
    previous = json.loads(old_report_path.read_text())
    prior_receipt(previous)
    protected = guard['protected_paths']()
    installed = [guard['identity'](f) for f in protected]
    production_packages = packages()
    helper = REPO/'Pycavi2/tests/qualify_libasdf_mac.py'
    require(helper.read_bytes() == git('show', MAC+':Pycavi2/tests/qualify_libasdf_mac.py'), 'Prefix/log helper changed')
    helpers = runpy.run_path(str(helper))
    prefix_identity = helpers['prefix_identity']
    private_before = prefix_identity(PRIVATE)
    external = Path(previous['external_prefix'])
    require(external == Path('/home1/fselman/Software/build/wenu-imaging/chapman-m5-asdf16-retry-ZES69RYi/libasdf-environment') and
            external.is_dir() and not external.is_symlink(), 'Recorded external prefix missing')
    external_before = prefix_identity(external)
    proofs = {str(old_report_path): sha(old_report_path)}
    for name in ('Pycavi2/pycavi/pycavi/pycavi_qc.py', 'Pycavi2/pycavi/config/qc-schema-1.0.0.json', 'Pycavi2/tests/test_shared_qc.py'):
        require(git('show', PREVIOUS+':'+name) == git('show', a.revision+':'+name) == (OLD/'source'/name).read_bytes(),
                'Shared QC changed; do not reuse its earlier receipt: '+name)
    archive = git('archive', '--format=tar', a.revision)
    source = run/'source'
    source.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle.getmembers():
            name = Path(member.name)
            require(not name.is_absolute() and '..' not in name.parts and (member.isfile() or member.isdir()), 'Unsafe export')
        bundle.extractall(source)
    original_source = snapshot(source)
    env = dict(os.environ, TMPDIR=str(run), XDG_CACHE_HOME=str(run/'cache'),
        PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', OMP_NUM_THREADS='1',
        OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1', MEFPP_TEST_REVISION=a.revision)
    ignored = {}
    for key in list(env):
        if key.startswith('CONDA_OVERRIDE_') or key in ('CC','CXX','CFLAGS','CPPFLAGS','LDFLAGS','CPATH',
                'C_INCLUDE_PATH','LIBRARY_PATH','LD_LIBRARY_PATH','LD_PRELOAD','DYLD_LIBRARY_PATH',
                'DYLD_INSERT_LIBRARIES','PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','GCC_EXEC_PREFIX',
                'COMPILER_PATH','CMAKE_GENERATOR','CMAKE_TOOLCHAIN_FILE','DESTDIR','SDKROOT'):
            ignored[key] = env.pop(key)
    report = dict(status='failed', revision=a.revision, mac_qualified_revision=MAC,
        checkout_revision=CHECKOUT, actual_glibc='2.17', commands=[],
        scope='11 changed-code synthetic C17/native-ASDF contracts; no observations',
        installation_performed=False, dependency_provisioning=False, production_activation=False,
        source_archive_sha256=hashlib.sha256(archive).hexdigest(), private_python=str(PRIVATE/'bin/python'),
        reused_receipt=dict(run=str(OLD), revision=PREVIOUS, report_sha256=proofs[str(old_report_path)]),
        ignored_build_variables=ignored, tools={n:str(path) for n,path in TOOLS.items()})
    def command(label, argv, capture=False, timeout=1800):
        return helpers['run_logged'](label, argv, work=run, env=env,
            commands=report['commands'], capture=capture, timeout=timeout)
    print('RETAINED CHAPMAN BPM RUN:', run, flush=True)
    try:
        versions = command('retained-qc-versions', [PRIVATE/'bin/python','-B','-c',
            "import importlib.metadata as m,json; print(json.dumps({n:m.version(n) for n in ('asdf','asdf-standard','numpy','astropy')}))"], capture=True)
        report['qc_versions'] = json.loads(versions)
        require(report['qc_versions'] == {'asdf':'6.0.0','asdf-standard':'1.5.0','numpy':'1.26.4','astropy':'6.1.7'}, 'Retained QC versions changed')
        build = run/'build-c17'
        command('configure-c17', [TOOLS['cmake'],'-S',source,'-B',build,'-G','Unix Makefiles',
            '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_C_FLAGS_RELEASE=-O2 -DNDEBUG',
            '-DMEFPP_C_STANDARD=17','-DMEFPP_BUILD_CONFIG_PROBES=ON','-DMEFPP_BUILD_BIAS_ADAPTER=ON',
            '-DMEFPP_BUILD_RESOURCES=OFF','-DMEFPP_SOURCE_REVISION='+a.revision,
            '-DCMAKE_C_COMPILER='+str(TOOLS['compiler']),'-DCMAKE_MAKE_PROGRAM='+str(TOOLS['make']),
            '-DCMAKE_AR='+str(TOOLS['ar']),'-DCMAKE_RANLIB='+str(TOOLS['ranlib']),
            '-DPython3_EXECUTABLE='+str(BASE_PYTHON),'-DMEFPP_QC_PYTHON='+str(PRIVATE/'bin/python')])
        command('build-c17',[TOOLS['cmake'],'--build',build,'--parallel','2','--target',*TARGETS])
        selection = '^('+'|'.join(sorted(TESTS))+')$'
        inventory = json.loads(command('inventory-c17',[TOOLS['ctest'],'--test-dir',build,'--show-only=json-v1','-R',selection], capture=True))
        test_inventory(inventory)
        report['tests'] = sorted(TESTS)
        command('tests-c17',[TOOLS['ctest'],'--test-dir',build,'-R',selection,'--output-on-failure',
            '--stop-on-failure','--no-tests=error','-j','1'])
        print((run/'tests-c17.log').read_text(), flush=True)
        report['status'] = 'passed'
    finally:
        checks = dict(checkout=before == guard['checkout'](REPO),
            installed_files=installed == [guard['identity'](f) for f in protected],
            production_packages=production_packages == packages(),
            retained_python_environment=private_before == prefix_identity(PRIVATE),
            external_prefix=external_before == prefix_identity(external),
            exported_source=original_source == snapshot(source),
            retained_receipt=all(sha(Path(f)) == h for f,h in proofs.items()))
        report['preservation'] = checks
        if not all(checks.values()):
            report['status'] = 'failed'
        (run/'chapman-bpm-qualification.json').write_text(json.dumps(report,indent=2)+'\n')
        print('CHAPMAN BPM QUALIFICATION:', report['status'], flush=True)
        print('PRESERVATION:', checks, flush=True)
        print('RETAINED RUN:', run, flush=True)
        require(report['status']=='passed', 'Chapman BPM qualification failed; retain this run')


if __name__ == '__main__':
    main()
