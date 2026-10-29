"""One-use Mac private qualification from the verified Chapman transfer bundle."""
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
import tarfile
import venv

TRANSFER = Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J')
ARCHIVE_SHA = '146182a5f21acaeb5436d2ffed4f89d81ecd662f6eb8cf75cf475bed9b6b9358'
MAC_HEAD = 'b5bfd910614a786b95a598cb6295989c9f6602d6'
INTERCHANGE_SHA = '74c1fa0382ca9c475326d974662810f6f2d0f0dcc42e4d5f069346bfd1d13e80'
D1_REPORT_SHA = 'd2292e08cc5c143559f49373a2f52d19a971459c6b62cfa6ba1fb400d0a1c4e6'
D1_RUNNER_SHA = 'b941efa295b34aa51fa63be737d7891dd24d92b061e810e27d19b46ff491f65f'
PROBE_SHA = 'c44fdc6515e623d31ad5ffcf9a84377abc7deb1f45db1a30bd139be02dd5e0fe'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    require(platform.system() == 'Darwin' and platform.node().split('.')[0] == 'MC02VV0HPHTDG', 'wrong host')
    require(sys.prefix == '/Users/fselman/anaconda3/envs/wenu-imaging' and sys.version_info[:2] == (3,11), 'wrong production Python')
    require(platform.python_version() == '3.11.14', 'Python changed')
    require(platform.machine() == 'x86_64', 'architecture changed')
    archive = TRANSFER/'chapman4-asdf6-evidence.tar.gz'
    require(sha(archive) == ARCHIVE_SHA, 'archive identity differs')
    probe = Path(__file__).with_name('asdf6_functional_probe.py')
    interchange = Path(__file__).with_name('asdf6_interchange_probe.py')
    require(sha(probe) == PROBE_SHA and sha(interchange) == INTERCHANGE_SHA, 'probe identities differ')
    # Verify every archive member before copying regular files to a fresh directory.
    with tarfile.open(archive) as bundle:
        members = bundle.getmembers()
        names = [m.name for m in members]
        require(len(names) == len(set(names)) and len(names) == 24, 'unexpected member count/duplicates')
        require(all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and m.size < 5000000 for m in members), 'unsafe archive member')
        manifest = json.load(bundle.extractfile('manifest.json'))
        require(set(names) == set(manifest['files']) | {'manifest.json'}, 'manifest membership differs')
        payload = {m.name:bundle.extractfile(m).read() for m in members}
        for name, row in manifest['files'].items():
            require(hashlib.sha256(payload[name]).hexdigest() == row['sha256'] and len(payload[name]) == row['bytes'], 'manifest identity: '+name)
    marker = TRANSFER/'Mac-attempt.json'
    require(not marker.exists(), 'Mac trial already attempted; inspect retained result before retry')
    D1 = TRANSFER/'Mac-evidence'/'D1'
    require(not D1.parent.exists(), 'evidence destination already exists')
    require(hashlib.sha256(payload['D1/prepare_chapman_asdf6.py']).hexdigest() == D1_RUNNER_SHA, 'D1 helper identity')
    require(hashlib.sha256(payload['D1/run-provenance.json']).hexdigest() == D1_REPORT_SHA, 'D1 report identity')
    repo = Path('/Users/fselman/Developer/wenu-imaging')
    def git(*args):
        return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
    require(Path(git('rev-parse','--show-toplevel')).resolve() == repo.resolve(), 'checkout root changed')
    require(git('branch','--show-current') == 'main' and git('rev-parse','HEAD') == MAC_HEAD, 'checkout state changed')
    require(git('remote','get-url','origin') == 'git@github.com:fselman/wenu-imaging.git', 'origin changed')
    require(git('rev-parse','--symbolic-full-name','@{upstream}') == 'refs/remotes/origin/main', 'upstream changed')
    require(not git('status','--porcelain'), 'dirty checkout')
    require(git('remote','get-url','--push','origin') == 'git@github.com:fselman/wenu-imaging.git', 'push origin changed')
    # All host/Git guards pass before writing extracted evidence.
    for name, data in payload.items():
        path = D1.parent/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    helper = runpy.run_path(str(D1/'prepare_chapman_asdf6.py'))
    d1 = json.loads((D1/'run-provenance.json').read_text())
    require(d1['status'] == 'D1-passed-awaiting-private-installation' and d1['production_package_metadata_unchanged'] and d1['checkout_unchanged'], 'D1 result')
    before = helper['package_snapshot']()
    expected = dict(helper['EXPECTED'],zipp='4.1.1')
    expected.pop('setuptools')  # Not inventoried in the Mac preflight; preserve actual metadata.
    for name, version in expected.items():
        require(md.version(name) == version, 'production package changed: '+name)
    for name in helper['PINS']:
        try:
            md.distribution(name)
        except md.PackageNotFoundError:
            pass
        else:
            raise RuntimeError('candidate already in production: '+name)
    for name, pin in helper['PINS'].items():
        helper['read_wheel'](D1/'wheels'/pin[1],name,pin)
    requirements = ''.join(f'{name}=={pin[0]} --hash=sha256:{pin[2]}\n' for name,pin in helper['PINS'].items())
    require((D1/'candidate-wheels.txt').read_text() == requirements, 'wheel requirement file changed')
    work = Path(tempfile.mkdtemp(prefix='Mac-private-',dir=TRANSFER))
    with marker.open('x') as stream:
        stream.write(json.dumps({'work':str(work),'runner_sha256':sha(Path(__file__))},indent=2)+'\n')
    report = {'stage':'Mac-private-install-functional-interchange','status':'started','host':platform.node(),
              'archive_sha256':ARCHIVE_SHA, 'd1_report_sha256':D1_REPORT_SHA,'work':str(work),'production_activation':False,
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
        print('MAC WORK DIRECTORY:',work,flush=True)
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
        # Recompute the expected dependency closure against the actual Mac base.
        # The original Chapman report remains immutable, including its zipp 4.1.2.
        candidates = {name:helper['read_wheel'](D1/'wheels'/pin[1],name,pin) for name,pin in helper['PINS'].items()}
        closure = helper['closure'](candidates)
        require(set(closure) == set(d1['dependency_closure']), 'Mac closure membership differs')
        for name, node in closure.items():
            require(node['version'] == ('4.1.1' if name == 'zipp' else d1['dependency_closure'][name]['version']), 'unexpected Mac closure version: '+name)
        mac_expectations = work/'mac-dependency-closure.json'
        mac_expectations.write_text(json.dumps({'dependency_closure':closure},indent=2)+'\n')
        report['dependency_closure'] = closure
        shutil.copyfile(probe,work/'functional-probe.py')
        require(sha(work/'functional-probe.py') == PROBE_SHA,'copied probe differs')
        probe_code,_ = command('functional-probe',[str(python),'-I','-B',str(work/'functional-probe.py'),
            '--work',str(work),'--environment',str(environment),'--d1-report',str(mac_expectations)])
        require(probe_code == 0,'functional probe failed; retain functional-probe.log and report')
        result = json.loads((work/'functional-report.json').read_text())
        require(result['status'] == 'D2-functional-passed-awaiting-Mac-and-interchange','functional status')
        report['functional_report_sha256'] = sha(work/'functional-report.json')
        report['semantic_sha256'] = result['semantic_sha256']
        report['checks'] = result['checks']
        interchange_code,_ = command('chapman-to-mac-interchange',[str(python),'-I','-B',str(interchange),
            '--work',str(work),'--fixture',str(D1.parent/'D2/fixture with spaces'),'--environment',str(environment)])
        require(interchange_code == 0,'interchange failed; retain logs')
        ir = json.loads((work/'interchange-report.json').read_text())
        require(ir['status'] == 'Chapman4-to-Mac-interchange-passed','interchange status')
        report['interchange_report_sha256'] = sha(work/'interchange-report.json')
        report['status'] = 'Mac-passed-awaiting-reverse-interchange' 
    except Exception as exc:
        report['status'] = 'stopped'
        report['error'] = type(exc).__name__+': '+str(exc)
        raise
    finally:
        report['production_packages_after'] = helper['package_snapshot']()
        report['production_package_metadata_unchanged'] = before == report['production_packages_after']
        report['checkout_unchanged'] = git('rev-parse','HEAD') == MAC_HEAD and not git('status','--porcelain')
        report['d1_report_unchanged'] = sha(D1/'run-provenance.json') == D1_REPORT_SHA
        report['transfer_unchanged'] = sha(archive) == ARCHIVE_SHA and all(sha(D1.parent/name) == hashlib.sha256(data).hexdigest() for name,data in payload.items())
        if not all(report[k] for k in ('production_package_metadata_unchanged','checkout_unchanged','d1_report_unchanged','transfer_unchanged')):
            report['status'] = 'stopped-preservation-check'
        (work/'run-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
        print('REPORT:',work/'run-provenance.json',flush=True)
    require(report['status'] == 'Mac-passed-awaiting-reverse-interchange','Mac trial did not pass')
    print(json.dumps({'status':report['status'],'checks':report['checks'],'semantic_sha256':report['semantic_sha256'],
                     'production_package_metadata_unchanged':report['production_package_metadata_unchanged'],
                     'checkout_unchanged':report['checkout_unchanged'],'production_activation':False},indent=2))


if __name__ == '__main__':
    main()
