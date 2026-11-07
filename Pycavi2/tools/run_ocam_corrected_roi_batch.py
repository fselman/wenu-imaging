"""Finish the corrected ROI archive through the accepted per-detector recipe.

Serial31detector execution; reuse CCD65 and its saved all32 dependency plan.
No estimator, model, dependency installation or native build changes.
"""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import signal
import subprocess
import sys

ROOT=Path('/Users/fselman/Developer/wenu-imaging')
BASE='c73d9a9e3a631fbbb2346beaa3c150c110a60343'
PICTURES=Path('/Users/fselman/Pictures/OCAM/wenu-imaging')
PLANNED=PICTURES/'ocam-linearity-preparation-plan-KSBh9ZXu'
PILOT=PICTURES/'ocam-corrected-roi-CCD65-t6e6o_zg'
PILOT_DIGEST='c12434f5c3bc2fc204968d565819157d4f24f37f20e19b44ff4633451b07549a'
QUALIFIED=Path('/Users/fselman/Software/build/wenu-imaging/mac-linearity-recipe-rSGbf1Mq')
NORMAL=Path('/Users/fselman/anaconda3/envs/wenu-imaging/bin/python')
PRIVATE=Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment')
SCRIPT='Pycavi2/tools/run_ocam_corrected_roi_batch.py'
TEST='Pycavi2/tests/test_corrected_roi_batch.py'


def require(ok,message):
    if not ok:raise RuntimeError(message)


def git(*args):return subprocess.check_output(['/usr/bin/git','-C',str(ROOT),*args])
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_product(product,detector):
    require(product.get('detector')==detector and product.get('noise_state')=='unavailable' and
        tuple(product.get(k) for k in ('pairs','exposures','sites','trace_frames'))==(50,100,100,30),
        'Incomplete/wrong detector preparation product: '+detector)


def run_remaining(plan,pilot,execute,on_complete=None):
    """Serial orchestration contract; execute is the accepted recipe callback."""
    expected={f'ESO_CCD_#{i}' for i in range(65,97)}
    entries=plan['dependencies'];ids=[d['selection']['detector'] for d in entries]
    require(plan.get('status')=='complete_dependency_plan' and len(entries)==32 and
            len(set(ids))==32 and set(ids)==expected,'Require complete unique saved32detector cohort')
    validate_product(pilot,'ESO_CCD_#65');products=[dict(deepcopy(pilot),reused=True)]
    for entry in entries:
        detector=entry['selection']['detector']
        if detector=='ESO_CCD_#65':continue
        result=execute(entry)
        require(result.get('status')=='complete_for_owner_inspection' and result.get('source_preservation') is True
                and result.get('fitted') is False,'Incomplete detector preparation: '+detector)
        product=result['product'];validate_product(product,detector)
        require(all(product['path']!=p['path'] for p in products),'Duplicate preparation output path')
        products.append(dict(deepcopy(product),reused=False))
        if on_complete is not None:on_complete(deepcopy(products))
    require(len(products)==32,'Incomplete output cohort')
    return products


def worker(work,revision):
    require(Path(sys.prefix).resolve()==PRIVATE.resolve(),'Retained ASDF Python required')
    plan_path=PLANNED/'plan.json';plan=json.loads(plan_path.read_bytes());source=PLANNED/'source'
    require(plan['status']=='complete_dependency_plan' and plan['source_revision']=='0a87c995fd170a40df21845aad711d59238ed7fd'
            and len(plan['preservation'])==6 and all(plan['preservation'].values()),'Accepted plan differs')
    helper_path=source/'Pycavi2/tools/retry_linearity_admission.py'
    require(helper_path.read_bytes()==git('show',plan['source_revision']+':Pycavi2/tools/retry_linearity_admission.py'),
            'Accepted source helper changed')
    helper=runpy.run_path(str(helper_path))
    proof=json.loads((QUALIFIED/'qualification.json').read_bytes())
    require(proof['status']=='passed' and helper['tree'](QUALIFIED/'source')==proof['source_sha256'],
            'Retained qualified source changed')
    recipe_path='Pycavi2/pycavi/pycavi/pycavi_linearity_recipe.py'
    require((source/recipe_path).read_bytes()==git('show',plan['source_revision']+':'+recipe_path),'Accepted recipe changed')
    for name,digest in proof['source_sha256'].items():
        if name.startswith(('mefpp2/','config/','Pycavi2/pycavi/')) and name!=recipe_path:
            require(sha(source/name)==digest,'Unqualified production change: '+name)
    native=Path(plan['native_executable']);require(sha(native)==plan['native_binary_sha256'],'Native binary changed')
    guard=runpy.run_path(str(QUALIFIED/'source/Pycavi2/tests/qualify_inspection_stages.py'))
    prefix_identity=runpy.run_path(str(QUALIFIED/'source/Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    def state():
        return dict(checkout=guard['checkout'](ROOT),installed_files=[guard['identity'](p['path']) for p in proof['installed_before']],
            qualified_source=helper['tree'](QUALIFIED/'source'),preparation_source=helper['tree'](source),
            private_qc_runtime=prefix_identity(PRIVATE),native_binary=sha(native),saved_plan=sha(plan_path),
            reused_pilot=helper['tree'](PILOT),controller=sha(work/'run.py'))
    before=state();require(before['installed_files']==proof['installed_before'],'Installed files changed')
    checkout=before['checkout'];require(checkout['head']==BASE and checkout['branch']=='main' and
        checkout['upstream']=='origin/main' and not checkout['status'],'Require preserved clean main')
    sys.path.insert(0,str(source/'Pycavi2/pycavi/pycavi'))
    import pycavi_linearity_recipe as recipe
    import pycavi_linearity_preparation_qc as archive
    pilot=json.loads((PILOT/'outer-execution.json').read_bytes())
    require(pilot['status']=='complete_for_owner_inspection' and len(pilot['preservation'])==8 and
            all(pilot['preservation'].values()) and pilot['product']['digest']==PILOT_DIGEST,'CCD65 receipt differs')
    reused=archive.read_product(pilot['product']['path'],expected_digest=PILOT_DIGEST)
    require(reused['detector']=='ESO_CCD_#65','Wrong reused detector')
    pilot_product=dict(pilot['product'],execution_receipt=str(PILOT/'outer-execution.json'))
    images=deepcopy(pilot['inputs']);completed={};active=['starting remaining31detectors'];current=[None]
    report=dict(status='running',controller_revision=revision,source_revision=plan['source_revision'],
        native_revision=plan['native_revision'],saved_plan=str(plan_path),qualified_run=str(QUALIFIED),
        reused_detector='ESO_CCD_#65',products=[dict(pilot_product,reused=True)],detectors_processed=0,
        fitted=False,scientific_acceptance=False,noise_state='unavailable',measurements_run=True)
    def save():
        (work/'overall-execution.json').write_text(json.dumps(report,indent=2)+'\n')
    def published(products):
        report['products']=products;report['detectors_processed']=len(products)-1;save()
    def execute(entry):
        detector=entry['selection']['detector'];active[0]=detector
        directory=work/detector.replace('ESO_CCD_#','CCD');directory.mkdir();current[0]=directory
        print('PREPARING:',report['detectors_processed']+1,'/31',detector,flush=True)
        result=recipe.prepare_detector(entry,native,directory,resolved=plan['resolved'],
            source_revision=plan['source_revision'],assessment_id='linearity:'+work.name+':'+detector,
            created_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
        for name,fingerprint in result['inputs'].items():
            require(name not in images or images[name]==fingerprint,'Shared image identity changed across detectors')
            images[name]=fingerprint
        result['product']=dict(result['product'],execution_receipt=str(directory/'execution.json'))
        completed[str(directory)]=helper['tree'](directory)
        print('COMPLETED:',detector,'exposures:',result['product']['exposures'],flush=True)
        return result
    signal.signal(signal.SIGALRM,lambda *_:print('Still preparing:',active[0],flush=True))
    signal.setitimer(signal.ITIMER_REAL,30,30);save()
    print('RETAINED CORRECTED ROI BATCH:',work,flush=True)
    print('REUSING CCD65:',pilot_product['path'],flush=True)
    image_check=None
    try:
        report['products']=run_remaining(plan,pilot_product,execute,published)
        expected=set().union(*(set(d['baseline']) for d in plan['dependencies']))
        require(set(images)==expected,'Incomplete batch image guard coverage')
        active[0]='final shared-image verification';after_images={}
        for i,name in enumerate(sorted(images),1):
            print('Final image guard:',i,'/',len(images),Path(name).name,flush=True)
            after_images[name]=recipe.image_fingerprint(name)
        image_check=after_images==images;require(image_check,'Final shared-image preservation failed')
        report.update(status='complete_for_owner_inspection',detectors_processed=31,
            detectors_total=32,exposure_rows=3200,pair_roi_rows=1600,site_rows=3200,trace_frames=960,
            inputs=images,after_inputs=after_images)
    except Exception as error:
        report.update(status='failed',error=repr(error))
        if current[0] is not None and (current[0]/'native.log').is_file():
            print((current[0]/'native.log').read_text()[-8000:],flush=True)
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        try:
            after=state();checks={name:before[name]==after[name] for name in before}
        except Exception as error:
            checks={name:None for name in before};report['preservation_error']=repr(error)
        try:checks['completed_products']=all(helper['tree'](Path(p))==digest for p,digest in completed.items())
        except Exception as error:checks['completed_products']=None;report['product_preservation_error']=repr(error)
        checks['images']=image_check;report['preservation']=checks
        if not all(checks.values()):report['status']='failed'
        save()
        if report['status']=='complete_for_owner_inspection':
            (work/'index.json').write_text(json.dumps(dict(status=report['status'],products=report['products'],
                source_revision=plan['source_revision'],measurement_stage=archive.STAGE),indent=2)+'\n')
        print('BATCH:',report['status'],flush=True);print('PRESERVATION:',checks,flush=True)
        print('PRODUCTS:',len(report['products']),'NEW:',report['detectors_processed'],'REUSED: 1',flush=True)
        print('RETAINED CORRECTED ROI BATCH:',work,flush=True)
    require(report['status']=='complete_for_owner_inspection','Batch/preservation failed')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--revision',required=True)
    p.add_argument('--run',required=True,type=Path);p.add_argument('--worker',action='store_true');a=p.parse_args()
    require((platform.system(),platform.node().split('.')[0])==('Darwin','MC02VV0HPHTDG'),'Wrong Mac')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,'Use niceness >=10')
    work=a.run.resolve(strict=True);require(work.parent==PICTURES.resolve(),'Unexpected retained batch parent')
    require(Path(__file__).resolve()==work/'run.py' and Path(__file__).read_bytes()==git('show',a.revision+':'+SCRIPT),
            'Controller differs from pinned source')
    if a.worker:return worker(work,a.revision)
    require(Path(sys.executable).resolve()==NORMAL.resolve() and Path(sys.prefix).resolve()==NORMAL.parent.parent.resolve(),
            'Normal imaging Python required for bootstrap')
    require(set(x.name for x in work.iterdir())=={'run.py'},'Fresh batch must contain only exported controller')
    require(git('rev-parse','HEAD').decode().strip()==BASE and not git('status','--porcelain'),'Checkout changed')
    test=work/'controls.py';test.write_bytes(git('show',a.revision+':'+TEST))
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
             CORRECTED_ROI_BATCH_DRIVER=str(work/'run.py'))
    for key in ('PYTHONPATH','PYTHONHOME','LD_PRELOAD','DYLD_INSERT_LIBRARIES','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH'):env.pop(key,None)
    log=work/'orchestration-controls.log'
    with log.open('x') as out:result=subprocess.run([sys.executable,'-B',str(test)],env=env,stdout=out,stderr=subprocess.STDOUT)
    if result.returncode:print(log.read_text(),flush=True)
    require(result.returncode==0 and 'Ran 3 tests' in log.read_text(),'Batch orchestration controls failed; retain log')
    print('ORCHESTRATION CONTROLS: 3 passed',flush=True)
    subprocess.run([str(PRIVATE/'bin/python'),'-B',str(work/'run.py'),'--revision',a.revision,'--run',str(work),'--worker'],
                   cwd=work,env=env,check=True)


if __name__=='__main__':main()
