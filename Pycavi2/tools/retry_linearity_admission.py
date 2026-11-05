"""Bounded #241 receipt checks and all-32 metadata admission; no FITS access.

Export exact new metadata code; reuse the qualified native build and ASDF runtime.
Never overwrite a failed plan, rebuild native code or repeat broad qualification.
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
QUALIFIED=Path('/Users/fselman/Software/build/wenu-imaging/mac-linearity-recipe-rSGbf1Mq')
PICTURES=Path('/Users/fselman/Pictures/OCAM/wenu-imaging')
NORMAL=Path('/Users/fselman/anaconda3/envs/wenu-imaging/bin/python')
PRIVATE=Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment')
SCRIPT='Pycavi2/tools/retry_linearity_admission.py'


def require(ok,message):
    if not ok:raise RuntimeError(message)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['/usr/bin/git','-C',str(ROOT),*args])
def tree(source):return {str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file()}


def worker(work,revision):
    require(Path(sys.prefix).resolve()==PRIVATE.resolve(),'Retained ASDF Python required')
    source=work/'source';old=QUALIFIED/'source'
    proof=json.loads((QUALIFIED/'qualification.json').read_bytes())
    require(proof['status']=='passed' and proof['source_revision']=='d25b10650bcb5a0a3132cdee3f32e2867ee9f3ff'
            and proof['native_controls']==3 and proof['python_controls']==17
            and len(proof['preservation'])==4 and all(proof['preservation'].values()),'Qualified gate differs')
    require(tree(old)==proof['source_sha256'],'Retained qualified source changed')
    # Reuse numerical/FITS/ASDF acceptance only if production code is identical.
    for name,digest in proof['source_sha256'].items():
        if (name.startswith('mefpp2/') or name.startswith('config/') or
            (name.startswith('Pycavi2/pycavi/') and name!='Pycavi2/pycavi/pycavi/pycavi_linearity_recipe.py')):
            require(sha(source/name)==digest,'Unqualified numerical/QC/config change: '+name)
    require(Path(__file__).resolve()==source/SCRIPT,'Unexpected worker source')
    source_before=tree(source)
    guard=runpy.run_path(str(old/'Pycavi2/tests/qualify_inspection_stages.py'))
    prefix_identity=runpy.run_path(str(old/'Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    checkout=guard['checkout'](ROOT);runtime=prefix_identity(PRIVATE)
    require(checkout['head']==BASE and checkout['branch']=='main' and checkout['upstream']=='origin/main'
            and not checkout['status'],'Require preserved clean main')
    executable=QUALIFIED/'build-c17/mefpp2/mefpp_linearity_prepare_command'
    executable_digest=sha(executable)
    sys.path.insert(0,str(source/'Pycavi2/pycavi/pycavi'))
    import pycavi_linearity_config as configuration
    import pycavi_linearity_recipe as recipe
    import pycavi_linearity_preparation_qc as archive
    frozen={}
    report=dict(status='failed',source_revision=revision,native_revision=proof['source_revision'],
        native_executable=str(executable),native_binary_sha256=executable_digest,
        raw_FITS_opened=False,measurements_run=False,metadata_preserved=None,metadata_preservation_scope='captured_metadata_only',dependencies=[])
    def read(path):
        payload=path.read_bytes();frozen[str(path)]=hashlib.sha256(payload).hexdigest();return json.loads(payload)
    try:
        # Only the eight new receipt-admission controls. No native/ASDF matrix.
        log=work/'receipt-controls.log'
        with log.open('x') as out:
            subprocess.run([sys.executable,'-B',str(source/'Pycavi2/tests/test_linearity_bias_receipts.py')],
                           stdout=out,stderr=subprocess.STDOUT,check=True)
        require('Ran 8 tests' in log.read_text() and 'skipped=' not in log.read_text(),'Receipt control inventory differs')
        report['receipt_controls']=8;print('RECEIPT CONTROLS: 8 passed',flush=True)
        resolved=configuration.resolve_files(source/'config/detectors/omegacam-1x1.toml',
            source/'config/processing/omegacam-characterization.toml');report['resolved']=resolved
        saved=read(PICTURES/'ocam-corrected-sample-asdf-xm1ngkg_/persistence/persistence.json')
        catalog=read(PICTURES/'linearity-bias-batch-05ijf_sx/masters.json')
        require(saved['status']=='complete' and len(saved['products'])==32,'Incomplete sample index')
        expected={f'ESO_CCD_#{i}' for i in range(65,97)}
        masters={m['detector']:m for m in catalog['masters']}
        require(catalog['status']=='candidate_signal_products' and len(catalog['masters'])==32
                and set(masters)==expected,'Master cohort differs')
        seen=set()
        for product in saved['products']:
            path=Path(product['path']);record=archive.qc.read_record(path)
            require(record.digest==product['digest'],'Sample index digest differs')
            entry=record.as_dict()['extensions']['corrected_sample_origin']['entry'];detector=entry['detector']
            require(detector in expected and detector not in seen,'Duplicate or unexpected detector')
            require(all(entry['master'][k]==masters[detector][k] for k in ('product','qc_product','hdu')),
                    'Master catalogue differs: '+detector)
            dependencies=recipe.preparation_dependencies(path,Path(entry['master']['product']).parent/'handoff.json',resolved)
            for name,digest in dependencies['metadata_sha256'].items():
                require(name not in frozen or frozen[name]==digest,'Conflicting metadata fingerprints')
                frozen[name]=digest
            report['dependencies'].append(dependencies);seen.add(detector)
            print('ADMITTED:',detector,'biases:',len(dependencies['biases']),
                  'accepted:',sum(b['accepted'] for b in dependencies['biases']),
                  'flats:',len(dependencies['selection']['flat']),flush=True)
        require(seen==expected,'Incomplete detector cohort')
        report.update(status='complete_dependency_plan',detectors=32)
    except Exception as error:
        report['error']=repr(error);raise
    finally:
        checks={}
        for name,check in (
            ('metadata',lambda:all(sha(p)==digest for p,digest in frozen.items()) if frozen else None),
            ('checkout',lambda:guard['checkout'](ROOT)==checkout),
            ('qualified_source',lambda:tree(old)==proof['source_sha256']),
            ('metadata_source',lambda:tree(source)==source_before),
            ('native_binary',lambda:sha(executable)==executable_digest),
            ('private_qc_runtime',lambda:prefix_identity(PRIVATE)==runtime)):
            try:checks[name]=check()
            except Exception as error:checks[name]=False;report.setdefault('preservation_errors',{})[name]=repr(error)
        report['preservation']=checks;report['metadata_preserved']=checks['metadata'];report['metadata_sha256']=frozen
        if not all(checks.values()):report['status']='failed'
        (work/'plan.json').write_text(json.dumps(report,indent=2)+'\n')
        print('RETAINED DEPENDENCY PLAN:',work,flush=True)
        print('PLAN:',report['status'],flush=True);print('PRESERVATION:',checks,flush=True)
    require(report['status']=='complete_dependency_plan','Admission/preservation failed')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--revision',required=True)
    p.add_argument('--run',required=True,type=Path);p.add_argument('--worker',action='store_true');a=p.parse_args()
    require((platform.system(),platform.node().split('.')[0])==('Darwin','MC02VV0HPHTDG'),'Wrong Mac')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,'Use niceness >=10')
    work=a.run.resolve(strict=True);require(work.parent==PICTURES.resolve(),'Unexpected retained-plan parent')
    if a.worker:return worker(work,a.revision)
    require(Path(sys.executable).resolve()==NORMAL.resolve() and Path(sys.prefix).resolve()==NORMAL.parent.parent.resolve(),
            'Normal imaging Python required for bootstrap')
    require(set(x.name for x in work.iterdir())=={'run.py'},'Fresh run must contain only exported runner')
    require(len(a.revision)==40 and git('rev-parse',a.revision+'^{commit}').decode().strip()==a.revision,'Exact fetched commit required')
    require(Path(__file__).resolve()==work/'run.py' and Path(__file__).read_bytes()==git('show',a.revision+':'+SCRIPT),
            'Runner differs from pinned source')
    require(git('rev-parse','HEAD').decode().strip()==BASE and not git('status','--porcelain'),'Checkout changed')
    (work/'source.tar').write_bytes(git('archive','--format=tar',a.revision));source=work/'source';source.mkdir()
    subprocess.run(['/usr/bin/tar','-xf',str(work/'source.tar'),'-C',str(source)],check=True)
    print('REUSING QUALIFIED NATIVE BUILD:',QUALIFIED/'build-c17',flush=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for key in ('PYTHONPATH','PYTHONHOME','LD_PRELOAD','DYLD_INSERT_LIBRARIES','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH'):env.pop(key,None)
    subprocess.run([str(PRIVATE/'bin/python'),'-B',str(source/SCRIPT),'--revision',a.revision,'--run',str(work),'--worker'],
                   cwd=work,env=env,check=True)


if __name__=='__main__':main()
