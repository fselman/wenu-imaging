#!/usr/bin/env python3
"""Qualify native BPM QC using the retained Mac cache and libasdf installation.

Temporarily overlay known source revisions, build two private candidate binaries,
then restore the original source/cache/adapter before running synthetic tests.
No dependency installation, observation processing or engine selection.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resume_linearity_candidate(args, build, git):
    """Recheck the recipe with an unchanged native producer; never rebuild it."""
    native_revision = 'e7c46646116f4cbca2eaf6955a4315c39f3e3f3b'
    require(args.linearity and not args.reuse_probe, 'Resume only the linearity recipe check')
    require(not git('diff', '--name-only', native_revision, args.revision, '--', 'mefpp2'),
            'Native dependencies changed; retained producer cannot be reused')
    candidate = args.resume_linearity_candidate.resolve(strict=True)
    require(candidate.is_relative_to(build.parent.parent) and candidate != build.parent.parent,
            'Candidate outside retained build root')
    command = candidate/'mefpp_linearity_prepare_command'
    receipts = list(candidate.glob('reduced/native-preparation-recipe-*/reduced/cal/bpm-linearity/native-recipe/execution.json'))
    require(len(receipts) == 1, 'Expected one retained failed recipe receipt')
    receipt = json.loads(receipts[0].read_text())
    require(receipt['status'] == 'failed' and Path(receipt['argv'][0]).resolve() == command,
            'Unexpected failed recipe producer')
    require(command.is_file() and not command.is_symlink() and
            sha(command) == receipt['native_binary_sha256'], 'Retained native executable changed')
    context_path = Path(receipt['argv'][-1]).resolve(strict=True)
    require(context_path.is_relative_to(candidate) and
            json.loads(context_path.read_text())['source_revision'] == native_revision,
            'Retained native revision differs')
    require('COVERAGE: real native ASDF, independent schema/value reader' in
            (candidate/'linearity-native-asdf-checks.log').read_text(),
            'Direct native ASDF check did not pass')
    previous = candidate/'validation-source'
    require(all(not path.is_symlink() for path in previous.rglob('*')), 'Retained validation symlink')
    sources = [path for path in previous.rglob('*') if path.is_file()]
    for path in sources:
        name = path.relative_to(previous).as_posix()
        require(not path.is_symlink() and path.read_bytes() == git('show', native_revision+':'+name),
                'Retained validation source changed: '+name)
    selected = build.parent.parent/'main-bias-jk_5noln/mefpp_bias_recipe'
    require(sha(selected) == '3c28e637a07cfa05ec83e18d238115c73e1b77b305b4ed0bf62d2d033e7cdacd',
            'Selected bias producer differs')
    protected = [selected, command, build/'CMakeCache.txt', build/'mefpp2/mefpp_bias_recipe']
    for instrument in ('WFI', 'OCAM'):
        folder = Path('/Users/fselman/Pictures')/instrument/'test_recipes/orchestration'
        protected += [folder/'run-bias.sh', folder/'bias-recipe.toml']
    guards = {str(path): sha(path) for path in protected}
    retry = Path(tempfile.mkdtemp(prefix='linearity-recipe-recheck-', dir=candidate))
    validation = retry/'validation-source'
    shutil.copytree(previous, validation)
    for path in sources:
        name = path.relative_to(previous)
        (validation/name).write_bytes(git('show', args.revision+':'+name.as_posix()))
    additional = ['Pycavi2/pycavi/pycavi/pycavi_native_product_qc.py']
    if args.combined:
        additional += ['tools/run-bpm-linearity.py', 'Pycavi2/tests/bpm_linearity_recipe_contract.py']
        additional += ['Pycavi2/pycavi/pycavi/'+name+'.py' for name in (
            'pycavi_bpm_linearity_plan', 'pycavi_bpm_linearity_recipe', 'pycavi_bpm_linearity_native')]
    for name in additional:
        path = validation/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(git('show', args.revision+':'+name))
    import sys
    label = 'bpm-linearity-coordinator-checks' if args.combined else 'linearity-native-recipe-checks'
    log = retry/(label+'.log')
    print('REUSING NATIVE:', command, '| SHA256:', sha(command), flush=True)
    print('RUNNING:', label, '| LOG:', log, flush=True)
    environment = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                       MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    try:
        with log.open('xb') as stream:
            if args.combined:
                bpm = candidate/'mefpp_m5'
                require(bpm.is_file(), 'Retained BPM producer unavailable')
                guards[str(bpm)] = sha(bpm)
                arguments = [args.asdf_python, validation/'Pycavi2/tests/bpm_linearity_recipe_contract.py',
                    '--bpm', bpm, '--preparation', command, '--source-revision', native_revision,
                    '--work-parent', candidate/'reduced']
            else:
                arguments = [args.asdf_python, validation/'Pycavi2/tests/linearity_native_recipe_contract.py',
                    '--native-command', command, '--source-revision', native_revision,
                    '--work-parent', candidate/'reduced']
            process = subprocess.Popen(list(map(str, arguments)), cwd=candidate/'orchestration',
                env=environment, stdout=stream, stderr=subprocess.STDOUT)
            try:
                while True:
                    try:
                        code = process.wait(timeout=30)
                        break
                    except subprocess.TimeoutExpired:
                        print(label+': still running', flush=True)
            except BaseException:
                process.terminate(); process.wait(); raise
    finally:
        require({name: sha(Path(name)) for name in guards} == guards, 'Protected files changed')
    require(code == 0, 'Recipe check failed; inspect '+str(log))
    report = dict(successful=True, native_source_revision=native_revision,
        verification_source_revision=args.revision, native_binary_sha256=sha(command),
        original_failure_receipt=str(receipts[0]), check=label, protected_files=guards, log=str(log))
    (retry/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(log.read_text(), end='', flush=True)
    print('PASS:', label, 'with retained native producers; no build repeated', flush=True)
    print('VERIFICATION:', retry/'verification.json', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--asdf-python', type=Path, required=True)
    parser.add_argument('--reuse-probe', type=Path, help='Retained df562fe native-ASDF probe; build only the corrected CLI')
    parser.add_argument('--linearity', action='store_true', help='Also build and qualify native preparation publication and its recipe envelope')
    parser.add_argument('--resume-linearity-candidate', type=Path, help='Recheck only the recipe using the unchanged e7c4664 producer')
    parser.add_argument('--combined', action='store_true', help='Recheck the combined detector coordinator using retained native producers')
    args = parser.parse_args()
    require(not args.combined or args.resume_linearity_candidate is not None, 'Combined check requires a retained candidate')
    require(platform.system()=='Darwin' and platform.node().split('.')[0]=='MC02VV0HPHTDG', 'Wrong qualification host')
    require(platform.machine()=='x86_64', 'Expected retained Intel environment')
    require(len(args.revision)==40 and set(args.revision)<=set('0123456789abcdef'), 'Exact revision required')
    checkout, build = args.checkout.resolve(strict=True), args.build.resolve(strict=True)
    def git(*arguments):
        return subprocess.check_output(['git','-C',str(checkout),*arguments])
    require(git('remote','get-url','origin').decode().strip()=='git@github.com:fselman/wenu-imaging.git', 'Wrong origin')
    require(not git('status','--porcelain'), 'Checkout must be clean')
    require(git('rev-parse','HEAD').decode().strip()=='ecf41ea347a20058c7eab435eb9d6fb10b5be02f', 'Unexpected checkout HEAD')
    require(git('rev-parse','origin/feat/bpm-linearity-recipe-template').decode().strip()==args.revision, 'Unexpected candidate branch')
    cache = build/'CMakeCache.txt'
    cached = cache.read_bytes()
    entries = {line.split(':',1)[0]:line.split('=',1)[1] for line in cached.decode().splitlines()
               if line and not line.startswith(('#','//')) and ':' in line and '=' in line}
    source = Path(entries['CMAKE_HOME_DIRECTORY']).resolve(strict=True)
    prefix = Path(entries['MEFPP_ASDF_PREFIX']).resolve(strict=True)
    require(source==Path('/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb/scalar-qc-c17-source'), 'Unexpected cached source')
    require(entries['CMAKE_BUILD_TYPE']=='Release' and entries['MEFPP_C_STANDARD']=='17', 'Unexpected build profile')
    require((prefix/'include/asdf/file.h').is_file() and (prefix/'lib/libasdf.dylib').is_file(), 'Retained libasdf unavailable')
    require(args.asdf_python.is_file(), 'Retained ASDF reader unavailable')
    if args.resume_linearity_candidate:
        resume_linearity_candidate(args, build, git)
        return
    reused_probe = None
    if args.reuse_probe:
        reused_probe = args.reuse_probe.resolve(strict=True)
        require(reused_probe.is_file() and reused_probe.name=='bpm_native_asdf_probe', 'Invalid retained probe')
        changed = set(git('diff','--name-only','df562fe6ac68569a1cd729ec727bd5bce89ac363',args.revision).decode().splitlines())
        allowed = {'mefpp2/ins/mef/recipes/mefpp_bpm_adapter.c',
                   'mefpp2/tests/bpm_native_qc_contract.py', 'tools/qualify-bpm-native-qc-mac.py'}
        require(changed <= allowed, 'Retained probe dependencies changed; full build required')
        reused_digest = sha(reused_probe)
    cmake = Path('/opt/local/bin/cmake')
    require(cmake.is_file(), 'Retained CMake unavailable')
    original_revision = entries['MEFPP_SOURCE_REVISION']
    def blob(revision, name):
        result = subprocess.run(['git','-C',str(checkout),'show',revision+':'+name], capture_output=True)
        return result.stdout if result.returncode==0 else None
    names = git('diff','--name-only',original_revision,args.revision,'--','mefpp2').decode().splitlines()
    require(names, 'No native candidate changes')
    originals, replacements, modes = {}, {}, {}
    references = (original_revision, 'ecf41ea347a20058c7eab435eb9d6fb10b5be02f',
                  '0dbd8039e6d830901576b13f545dd8a3cff9ff80', args.revision)
    for name in names:
        path = source/name
        require(not path.is_symlink() and (not path.exists() or path.is_file()), 'Unexpected source object: '+name)
        before = path.read_bytes() if path.exists() else None
        if before is not None:
            require(any(before==blob(revision,name) for revision in references), 'Source differs from retained revisions: '+name)
        originals[name] = before
        modes[name] = path.stat().st_mode & 0o777 if before is not None else 0o644
        replacements[name] = blob(args.revision,name)
    selected = build.parent.parent/'main-bias-jk_5noln/mefpp_bias_recipe'
    require(selected.is_file() and sha(selected)=='3c28e637a07cfa05ec83e18d238115c73e1b77b305b4ed0bf62d2d033e7cdacd', 'Selected bias producer differs')
    protected = [selected, build/'mefpp2/mefpp_bias_recipe']
    for instrument in ('WFI','OCAM'):
        folder = Path('/Users/fselman/Pictures')/instrument/'test_recipes/orchestration'
        protected += [folder/'run-bias.sh', folder/'bias-recipe.toml']
    guards = {str(path):sha(path) for path in protected}
    adapter = build/'mefpp2/mefpp_m5'
    adapter_before = adapter.read_bytes() if adapter.exists() else None
    linearity_command = build/'mefpp2/mefpp_linearity_prepare_command'
    linearity_before = linearity_command.read_bytes() if args.linearity and linearity_command.exists() else None
    linearity_mode = linearity_command.stat().st_mode & 0o777 if linearity_before is not None else 0o755
    adapter_mode = adapter.stat().st_mode & 0o777 if adapter.exists() else 0o755
    candidate = Path(tempfile.mkdtemp(prefix='bpm-native-qc-',dir=build.parent.parent))
    print('CANDIDATE DIRECTORY:',candidate,flush=True)
    backup = candidate/'original-source'
    backup.mkdir()
    for name, content in originals.items():
        if content is not None:
            target=backup/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(content)
    (candidate/'original-cache.txt').write_bytes(cached)
    if adapter_before is not None:
        (candidate/'original-mefpp_m5').write_bytes(adapter_before)
    if linearity_before is not None:
        (candidate/'original-linearity-command').write_bytes(linearity_before)
    (candidate/'restore-manifest.json').write_text(json.dumps(dict(source=str(source),build=str(build),
        files={name:dict(existed=value is not None,mode=modes[name]) for name,value in originals.items()},
        linearity_command=dict(enabled=args.linearity,path=str(linearity_command),
            existed=linearity_before is not None,mode=linearity_mode)),indent=2)+'\n')
    def run(arguments, label, cwd):
        log=candidate/(label+'.log')
        print('RUNNING:',label,'| LOG:',log,flush=True)
        with log.open('xb') as stream:
            environment=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                             MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
            process=subprocess.Popen(list(map(str,arguments)),cwd=cwd,env=environment,
                                     stdout=stream,stderr=subprocess.STDOUT)
            try:
                while True:
                    try:
                        code=process.wait(timeout=30); break
                    except subprocess.TimeoutExpired:
                        print(label+': still running',flush=True)
            except BaseException:
                process.terminate(); process.wait(); raise
        require(code==0,label+' failed; inspect '+str(log))
    try:
        for name, content in replacements.items():
            path=source/name
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(content)
        run([cmake,'-S',source,'-B',build,'-DMEFPP_BUILD_BIAS_RECIPE=ON',
             '-DMEFPP_SOURCE_REVISION='+args.revision], 'candidate-configure',checkout)
        targets=['mefpp_m5'] if reused_probe else ['mefpp_m5','bpm_native_asdf_probe']
        if args.linearity:
            targets.append('mefpp_linearity_prepare_command')
        run([cmake,'--build',build,'--parallel','2','--target',*targets], 'candidate-build',checkout)
        shutil.copy2(build/'mefpp2/mefpp_m5',candidate/'mefpp_m5')
        if args.linearity:
            shutil.copy2(build/'mefpp2/mefpp_linearity_prepare_command',candidate/'mefpp_linearity_prepare_command')
        if reused_probe:
            require(sha(reused_probe)==reused_digest, 'Retained probe changed during qualification')
            shutil.copy2(reused_probe,candidate/'bpm_native_asdf_probe')
        else:
            shutil.copy2(build/'mefpp2/bpm_native_asdf_probe',candidate/'bpm_native_asdf_probe')
    finally:
        for name, content in originals.items():
            path=source/name
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content); path.chmod(modes[name])
        if adapter_before is None:
            adapter.unlink(missing_ok=True)
        else:
            adapter.write_bytes(adapter_before); adapter.chmod(adapter_mode)
        if args.linearity:
            if linearity_before is None:
                linearity_command.unlink(missing_ok=True)
            else:
                linearity_command.write_bytes(linearity_before); linearity_command.chmod(linearity_mode)
        try:
            run([cmake,'-S',source,'-B',build,'-DMEFPP_BUILD_BIAS_RECIPE='+entries['MEFPP_BUILD_BIAS_RECIPE'],
                 '-DMEFPP_SOURCE_REVISION='+original_revision], 'restore-configuration',checkout)
        finally:
            cache.write_bytes(cached)
        require(all((source/name).read_bytes()==value if value is not None else not (source/name).exists()
                    for name,value in originals.items()), 'Source restoration differs')
        require({name:sha(Path(name)) for name in guards}==guards, 'Protected producer/configuration changed')
        require(cache.read_bytes()==cached and (adapter.read_bytes() if adapter.exists() else None)==adapter_before,
                'Cache/adapter restoration differs')
        if args.linearity:
            require((linearity_command.read_bytes() if linearity_command.exists() else None)==linearity_before,
                    'Original preparation executable differs after restoration')
        print('PASS: cached source/cache/adapter and selected bias configuration preserved',flush=True)
    validation = candidate/'validation-source'
    required = ['mefpp2/tests/bpm_native_qc_contract.py','mefpp2/tests/bpm_files_contract.py',
                'mefpp2/ins/mef/config/wfi.paf','mefpp2/ins/mef/config/qc-product-schema-2.0.0.json']
    if args.linearity:
        required += [
            'mefpp2/tests/linearity_native_archive_contract.py',
            'mefpp2/tests/linearity_files_contract.py', 'mefpp2/tests/layout_contract.py',
            'mefpp2/tests/config_snapshot_contract.py',
            'Pycavi2/tests/linearity_preparation_fixture.py', 'Pycavi2/tests/test_sample_qc.py',
            'Pycavi2/tests/linearity_native_recipe_contract.py',
            'Pycavi2/tools/run_ocam_linearity_samples.py', 'tools/prepare-linearity.py',
            'Pycavi2/pycavi/config/qc-schema-1.1.0.json',
            'docs/architecture/proposed/m1/effective-settings-baseline.json',
            'docs/architecture/proposed/m2/project-contracts/validate_project.py',
            'docs/architecture/proposed/m2/project-contracts/catalog.json',
            'docs/architecture/proposed/m2/project-contracts/examples/omegacam.toml']
        required += ['Pycavi2/pycavi/pycavi/'+name+'.py' for name in (
            'pycavi_qc','pycavi_pair_qc','pycavi_sample_qc','pycavi_linearity_config',
            'pycavi_linearity_recipe','pycavi_linearity_preparation_qc','pycavi_linearity_native_archive','pycavi_native_product_qc',
            'pycavi_configuration')]
    for name in required:
        path=validation/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(blob(args.revision,name))
    orchestration, reduced = candidate/'orchestration', candidate/'reduced'
    orchestration.mkdir(); reduced.mkdir()
    import sys
    run([sys.executable,validation/required[0],'--source-root',validation,
         '--probe',candidate/'bpm_native_asdf_probe','--adapter',candidate/'mefpp_m5',
         '--asdf-python',args.asdf_python,'--source-revision',args.revision,'--work-parent',reduced],
        'native-asdf-checks',orchestration)
    if args.linearity:
        run([sys.executable, validation/'mefpp2/tests/linearity_native_archive_contract.py',
             '--command', candidate/'mefpp_linearity_prepare_command',
             '--asdf-python',args.asdf_python,'--work-parent',reduced], 'linearity-native-asdf-checks',orchestration)
        run([args.asdf_python, validation/'Pycavi2/tests/linearity_native_recipe_contract.py',
             '--native-command', candidate/'mefpp_linearity_prepare_command',
             '--source-revision',args.revision,'--work-parent',reduced], 'linearity-native-recipe-checks',orchestration)
    receipt=dict(source_revision=args.revision,successful=True,observations_opened=False,
        binaries={name:dict(path=str(candidate/name),sha256=sha(candidate/name))
                  for name in ('mefpp_m5','bpm_native_asdf_probe')},protected_files=guards)
    if args.linearity:
        receipt['linearity_preparation']=dict(successful=True,
            path=str(candidate/'mefpp_linearity_prepare_command'),
            sha256=sha(candidate/'mefpp_linearity_prepare_command'))
    if reused_probe:
        receipt['reused_probe']=dict(path=str(reused_probe),sha256=reused_digest,
            build_revision='df562fe6ac68569a1cd729ec727bd5bce89ac363')
    (candidate/'candidate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS: native BPM FITS/ASDF, independent schema/value checks and production CLI',flush=True)
    print('CANDIDATE DIRECTORY:',candidate,flush=True)


if __name__=='__main__':
    main()
