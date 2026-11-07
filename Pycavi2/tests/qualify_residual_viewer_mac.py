"""Actual Intel Mac straight-line residual display qualification (#235).

Reuse retained ASDF6 runtime. No installation, dependency provisioning, native
build, observation access, numerical recomputation or old native test matrix.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys

ROOT=Path('/Users/fselman/Developer/wenu-imaging')
BASE='c73d9a9e3a631fbbb2346beaa3c150c110a60343'
PYTHON=Path('/Users/fselman/anaconda3/envs/wenu-imaging/bin/python')
PRIVATE=Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment')


def require(ok,message):
    if not ok:raise RuntimeError(message)


def git(*args):
    return subprocess.check_output(['/usr/bin/git','-C',str(ROOT),*args])


def source_digest(source):
    return {str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(source.rglob('*')) if p.is_file()}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--revision',required=True);p.add_argument('--run',type=Path,required=True)
    a=p.parse_args()
    require((platform.system(),platform.machine(),platform.node().split('.')[0])==
            ('Darwin','x86_64','MC02VV0HPHTDG'),'Wrong Intel Mac')
    require(Path(sys.executable).resolve()==PYTHON.resolve() and
            Path(sys.prefix).resolve()==PYTHON.parent.parent.resolve(),'Use normal installed imaging Python')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,'Use niceness >=10')
    require(len(a.revision)==40 and git('rev-parse',a.revision+'^{commit}').decode().strip()==a.revision,
            'Exact fetched source required')
    work=a.run.resolve(strict=True)
    require(work.parent==Path('/Users/fselman/Software/build/wenu-imaging').resolve() and
            set(q.name for q in work.iterdir())=={'qualify.py'},'Fresh retained run required')
    require(Path(__file__).resolve()==work/'qualify.py' and Path(__file__).read_bytes()==
            git('show',a.revision+':Pycavi2/tests/qualify_residual_viewer_mac.py'),'Qualifier differs from source')
    require((PRIVATE/'bin/python').is_file(),'Retained qualified ASDF Python is missing; do not install a replacement')
    archive=work/'source.tar';archive.write_bytes(git('archive','--format=tar',a.revision))
    source=work/'source';source.mkdir()
    subprocess.run(['/usr/bin/tar','-xf',str(archive),'-C',str(source)],check=True)
    guard=runpy.run_path(str(source/'Pycavi2/tests/qualify_inspection_stages.py'))
    prefix_identity=runpy.run_path(str(source/'Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    before=guard['checkout'](ROOT)
    require(before['head']==BASE and before['branch']=='main' and before['upstream']=='origin/main'
            and not before['status'],'Require unchanged clean main')
    require(before['origin']==before['push']=='git@github.com:fselman/wenu-imaging.git','Unexpected origin')
    protected=guard['protected_paths']();installed=[guard['identity'](q) for q in protected]
    exported=source_digest(source);private=prefix_identity(PRIVATE)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',MPLCONFIGDIR=str(work/'matplotlib-cache'),
             OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
    report=dict(status='failed',source_revision=a.revision,private_python=str(PRIVATE/'bin/python'),
                checkout_before=before,source_sha256=exported,commands=[],native_execution=False,
                observations_opened=False,installation_performed=False,dependency_provisioning=False)
    print('RETAINED RESIDUAL-VIEWER QUALIFICATION:',work,flush=True)
    def command(name,argv):
        log=work/(name+'.log');print('Running:',name,'| log:',log,flush=True)
        with log.open('x') as stream:
            process=subprocess.Popen([str(q) for q in argv],cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT)
            while True:
                try:code=process.wait(timeout=30);break
                except subprocess.TimeoutExpired:print('Still running:',name,flush=True)
        report['commands'].append(dict(name=name,argv=[str(q) for q in argv],exit_status=code,log=str(log)))
        require(code==0,name+' failed; retain '+str(log))
        return log
    try:
        log=command('retained-qc-versions',[PRIVATE/'bin/python','-B','-c',
            "import importlib.metadata as m,sys,json; print(json.dumps({'prefix':sys.prefix,'versions':{n:m.version(n) for n in ('asdf','asdf-standard','numpy','matplotlib')}}))"])
        report['runtime']=json.loads(log.read_text())
        require(Path(report['runtime']['prefix']).resolve()==PRIVATE.resolve() and
                report['runtime']['versions']['asdf']=='6.0.0' and
                report['runtime']['versions']['asdf-standard']=='1.5.0','Unexpected retained ASDF runtime')
        prior=Path('/Users/fselman/Software/build/wenu-imaging/mac-signal-time-j4ke56uy/qualification.json')
        previous=json.loads(prior.read_text())
        require(previous['status']=='passed' and all(previous['preservation'].values()) and
                previous['source_revision']=='56b7f489f8b1a0359aa9d5ac312711bd3a27111e',
                'Prior actual Mac signal/time display gate not admitted')
        require(report['runtime']['versions']==previous['runtime']['versions'],
                'Qualified ASDF/NumPy/Matplotlib versions changed')
        reused=[name for name in previous['source_sha256'] if
                name.startswith('Pycavi2/pycavi/pycavi/') or
                name in ('tools/plot-pair-qc.py','tools/run-pair-measurements.py','tools/detector-footprint.py')]
        require(reused and all(exported[name]==previous['source_sha256'][name] for name in reused),
                'Qualified numerical/ASDF/plot modules changed; prior gates cannot be reused')
        report['reused_gate']=dict(path=str(prior),sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),
                                  unchanged_files=reused)
        log=command('qualifier-dispatch',[PYTHON,'-B',source/'Pycavi2/tests/test_residual_qualifier_dispatch.py'])
        print(log.read_text(),flush=True)
        for name,script,filename,count in (
            ('signal-time-viewer','test_pair_qc_viewer.py','pair-viewer-results.json',8),):
            target=work/name;target.mkdir()
            log=command(name,[PRIVATE/'bin/python','-B',source/'Pycavi2/tests'/script,'--work',target])
            print(log.read_text(),flush=True)
            result=json.loads((target/filename).read_text())
            require(result['tests']==count and result['successful'] is True and not result['network_attempts'],
                    'Incomplete/offline display contract: '+name)
        report['status']='passed'
    except Exception as error:
        report.update(status='failed',error=repr(error));raise
    finally:
        checks={}
        for name,check in (
            ('checkout',lambda:guard['checkout'](ROOT)==before),
            ('installed_files',lambda:[guard['identity'](q) for q in protected]==installed),
            ('exported_source',lambda:source_digest(source)==exported),
            ('private_qc_runtime',lambda:prefix_identity(PRIVATE)==private)):
            try:checks[name]=check()
            except Exception as error:checks[name]=False;report.setdefault('preservation_errors',{})[name]=repr(error)
        if not all(checks.values()):report['status']='failed'
        report['preservation']=checks
        (work/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
        print('QUALIFICATION:',report['status'],flush=True);print('PRESERVATION:',checks,flush=True)
    require(report['status']=='passed','Qualification/preservation failed')


if __name__=='__main__':main()
