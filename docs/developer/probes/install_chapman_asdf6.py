"""One-use D2 private install/probe, offline from the accepted D1 wheels."""
import hashlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import sys
import tempfile
import venv

D1 = Path('/home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC')
D1_REPORT_SHA = 'd2292e08cc5c143559f49373a2f52d19a971459c6b62cfa6ba1fb400d0a1c4e6'
D1_RUNNER_SHA = 'b941efa295b34aa51fa63be737d7891dd24d92b061e810e27d19b46ff491f65f'
PROBE_SHA = 'c44fdc6515e623d31ad5ffcf9a84377abc7deb1f45db1a30bd139be02dd5e0fe'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    require(platform.system() == 'Linux' and platform.node().split('.')[0] == 'chapman4', 'wrong host')
    require(sys.prefix == '/home/fselman/.conda/envs/wenu-imaging' and sys.version_info[:2] == (3,11), 'wrong production Python')
    require(os.confstr('CS_GNU_LIBC_VERSION') == 'glibc 2.17', 'libc changed')
    require(sha(D1/'run-provenance.json') == D1_REPORT_SHA, 'D1 report identity changed')
    require(sha(D1/'prepare_chapman_asdf6.py') == D1_RUNNER_SHA, 'D1 helper changed')
    probe = Path(__file__).with_name('asdf6_functional_probe.py')
    require(sha(probe) == PROBE_SHA, 'functional probe changed')
    helper = runpy.run_path(str(D1/'prepare_chapman_asdf6.py'))
    d1 = json.loads((D1/'run-provenance.json').read_text())
    require(d1['status'] == 'D1-passed-awaiting-private-installation', 'D1 status')
    require(d1['production_package_metadata_unchanged'] and d1['checkout_unchanged'], 'D1 preservation')
    repo = Path('/home1/fselman/Software/wenu-imaging')
    def git(*args):
        return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
    require(git('branch','--show-current') == 'main' and git('rev-parse','HEAD') == d1['checkout'], 'checkout state changed')
    require(git('remote','get-url','origin') == 'https://github.com/fselman/wenu-imaging.git', 'origin changed')
    require(git('rev-parse','--symbolic-full-name','@{upstream}') == 'refs/remotes/origin/main', 'upstream changed')
    require(not git('status','--porcelain'), 'dirty checkout')
    before = helper['package_snapshot']()
    require(before == d1['packages_after'], 'production package metadata changed since D1')
    for name, pin in helper['PINS'].items():
        helper['read_wheel'](D1/'wheels'/pin[1],name,pin)
    requirements = ''.join(f'{name}=={pin[0]} --hash=sha256:{pin[2]}\n' for name,pin in helper['PINS'].items())
    require((D1/'candidate-wheels.txt').read_text() == requirements, 'wheel requirement file changed')
    marker = D1/'D2-attempt.json'
    require(not marker.exists(), 'D2 already attempted; retain prior attempt and inspect before retry')
    work = Path(tempfile.mkdtemp(prefix='D2-private-',dir=D1))
    with marker.open('x') as stream:
        stream.write(json.dumps({'work':str(work),'runner_sha256':sha(Path(__file__))},indent=2)+'\n')
    report = {'stage':'D2-private-install-and-functional','status':'started','host':platform.node(),
              'd1_report_sha256':D1_REPORT_SHA,'work':str(work),'production_activation':False,
              'production_packages_before':before,'commands':[],'installation_scope':'private venv only; production site-packages read-only base'}
    def command(label, argv):
        log = work/(label+'.log')
        print('Running:',label,'| log:',log,flush=True)
        with log.open('w') as stream:
            result = subprocess.run(argv,cwd=work,stdout=stream,stderr=subprocess.STDOUT,timeout=180)
        report['commands'].append({'label':label,'argv':argv,'exit_status':result.returncode,'log':str(log),'log_sha256':sha(log)})
        return result.returncode, log.read_text(errors='replace')
    def issues(code,text):
        return set(line.strip() for line in text.splitlines() if line.strip()) if code else set()
    try:
        print('D2 WORK DIRECTORY:',work,flush=True)
        baseline_code,baseline_text = command('production-pip-check',[sys.executable,'-I','-B','-m','pip','--isolated','--disable-pip-version-check','check'])
        report['baseline_dependency_issues'] = sorted(issues(baseline_code,baseline_text))
        environment = work/'environment'
        # No ensurepip bootstrap: use the already installed pip read-only.
        venv.EnvBuilder(system_site_packages=True,with_pip=False,symlinks=True).create(environment)
        python = environment/'bin/python'
        layout_code,layout_text = command('private-layout',[str(python),'-I','-B','-c',
            'import json,sys,sysconfig,pip; print(json.dumps({"prefix":sys.prefix,"base_prefix":sys.base_prefix,"purelib":sysconfig.get_path("purelib"),"pip":pip.__file__}))'])
        require(layout_code == 0,'private Python layout failed')
        layout = json.loads(layout_text)
        require(Path(layout['prefix']).resolve() == environment.resolve(),'private prefix mismatch')
        target = Path(layout['purelib']).resolve()
        require(target.is_relative_to(environment.resolve()),'installation target outside private environment')
        require(Path(layout['pip']).resolve().is_relative_to(Path(sys.prefix).resolve()),'pip not from retained base')
        report['private_layout'] = layout
        install_code,_ = command('offline-install',[str(python),'-I','-B','-m','pip','--isolated','--disable-pip-version-check','install',
            '--no-index','--no-deps','--no-compile','--require-hashes','--target',str(target),
            '--find-links',str(D1/'wheels'),'-r',str(D1/'candidate-wheels.txt')])
        require(install_code == 0,'offline private install failed')
        report['private_installation_performed'] = True
        candidate_code,candidate_text = command('candidate-pip-check',[str(python),'-I','-B','-m','pip','--isolated','--disable-pip-version-check','check'])
        report['candidate_dependency_issues'] = sorted(issues(candidate_code,candidate_text))
        added = issues(candidate_code,candidate_text)-issues(baseline_code,baseline_text)
        require(not added,'new dependency problems: '+'; '.join(sorted(added)))
        shutil.copyfile(probe,work/'functional-probe.py')
        require(sha(work/'functional-probe.py') == PROBE_SHA,'copied probe differs')
        probe_code,_ = command('functional-probe',[str(python),'-I','-B',str(work/'functional-probe.py'),
            '--work',str(work),'--environment',str(environment),'--d1-report',str(D1/'run-provenance.json')])
        require(probe_code == 0,'functional probe failed; retain functional-probe.log and report')
        result = json.loads((work/'functional-report.json').read_text())
        require(result['status'] == 'D2-functional-passed-awaiting-Mac-and-interchange','functional status')
        report['functional_report_sha256'] = sha(work/'functional-report.json')
        report['semantic_sha256'] = result['semantic_sha256']
        report['checks'] = result['checks']
        report['status'] = 'Chapman4-D2-passed-awaiting-Mac-and-interchange'
    except Exception as exc:
        report['status'] = 'stopped'
        report['error'] = type(exc).__name__+': '+str(exc)
        raise
    finally:
        report['production_packages_after'] = helper['package_snapshot']()
        report['production_package_metadata_unchanged'] = before == report['production_packages_after']
        report['checkout_unchanged'] = git('rev-parse','HEAD') == d1['checkout'] and not git('status','--porcelain')
        report['d1_report_unchanged'] = sha(D1/'run-provenance.json') == D1_REPORT_SHA
        if not all(report[k] for k in ('production_package_metadata_unchanged','checkout_unchanged','d1_report_unchanged')):
            report['status'] = 'stopped-preservation-check'
        (work/'run-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
        print('REPORT:',work/'run-provenance.json',flush=True)
    require(report['status'] == 'Chapman4-D2-passed-awaiting-Mac-and-interchange','D2 did not pass')
    print(json.dumps({'status':report['status'],'checks':report['checks'],'semantic_sha256':report['semantic_sha256'],
                     'production_package_metadata_unchanged':report['production_package_metadata_unchanged'],
                     'checkout_unchanged':report['checkout_unchanged'],'production_activation':False},indent=2))


if __name__ == '__main__':
    main()
