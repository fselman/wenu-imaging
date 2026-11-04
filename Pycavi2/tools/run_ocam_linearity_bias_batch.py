"""Serial remaining-detector bias dependency, reusing completed CCD65 and shared source hashes."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import sys

PILOT=Path('/Users/fselman/Pictures/OCAM/wenu-imaging/linearity-bias-CCD65-epw82wy3')
PILOT_REVISION='c93dcd9152ec58fee495b4bf84bdc6bffc0529ef'


def require(ok,message):
    if not ok:raise RuntimeError(message)


def options(argv):
    require(argv[:2]==['cal','bias'] and len(argv)%2==0,'Invalid native bias argument list')
    result=dict(zip(argv[2::2],argv[3::2]))
    require(len(result)*2==len(argv)-2,'Duplicate native bias option')
    return result


def detector_plan(template,geometry,review,members,directory):
    """Change only independent bindings/output locations; retain all recipe choices."""
    identity=geometry['id'];base=options(template)
    hdus=[review['headers']['raw_bindings'][str(i)][identity] for i in range(len(members))]
    require(len(set(hdus))==1,'Existing bias adapter requires a common HDU across selected raw files')
    hdu=hdus[0];bpm_hdu=review['headers']['bpm_bindings'][identity]
    update={'--detector-id':identity,'--expected-extname':identity,'--hdu':str(hdu),
        '--config-detector':str(geometry['native_paf_chip']-1),'--bpm-hdu':str(bpm_hdu),
        '--bpm-expected-extname':identity,'--output':str(directory/(identity.replace('ESO_CCD_#','OCAM_MB_CCD')+'_candidate.fits')),
        '--work-dir':str(directory),'--log-path':str(directory/'native.log'),
        '--config-record':str(directory/'configuration.json'),'--qc-record':str(directory/'handoff.json')}
    require(set(update)<=set(base),'Pilot native options lack explicit bindings')
    base.update(update)
    return dict(detector=identity,hdu=hdu,bpm_hdu=bpm_hdu,configuration_detector=geometry['native_paf_chip']-1,
                directory=str(directory),native=['cal','bias',*[item for kv in base.items() for item in kv]])


def serial(entries,command,save):
    """A blocking command must finish and be admitted before the next detector."""
    results=[]
    for entry in entries:
        result=command(entry)
        require(result['status']=='complete','Incomplete native/ASDF bias recipe')
        require(result['native_exit_status']==0,'Failed native bias recipe')
        require(result['detector']==entry['detector'],'Completed detector identity mismatch')
        results.append(result);save(results)
    return results


def image_pass(paths,expected,fingerprint,label):
    values={}
    for i,path in enumerate(paths,1):
        print(label,'shared image',i,'/',len(paths),flush=True)
        value=fingerprint(path)
        require(value['sha256']==expected[str(path)]['sha256'],'Shared input differs from completed pilot')
        values[str(path)]=value
    return values


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',required=True);parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args()
    require((platform.system(),platform.node().split('.')[0])==('Darwin','MC02VV0HPHTDG'),'Wrong Mac')
    root=Path('/Users/fselman/Developer/wenu-imaging')
    pictures=Path('/Users/fselman/Pictures/OCAM/wenu-imaging')
    normal=Path('/Users/fselman/anaconda3/envs/wenu-imaging/bin/python')
    require(Path(sys.prefix)==normal.parent.parent and Path(sys.executable).resolve()==normal.resolve(),'Normal imaging Python required')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,'Require niceness >=10')
    work=args.run.resolve(strict=True)
    require(work.parent==pictures and set(p.name for p in work.iterdir())=={'run.py','checks.py'},'Fresh retained batch required')
    exact=subprocess.check_output(['/usr/bin/git','-C',str(root),'show',args.revision+':Pycavi2/tools/run_ocam_linearity_bias_batch.py'])
    require(Path(__file__).resolve()==work/'run.py' and Path(__file__).read_bytes()==exact,'Exact controller required')
    pilot=json.loads((PILOT/'outer-execution.json').read_text())
    require(pilot['status']=='complete_for_owner_inspection' and all(pilot['preservation'].values())
            and pilot['controller_revision']==PILOT_REVISION,'Completed preserved CCD65 pilot required')
    old_driver=PILOT/'run.py'
    require(old_driver.read_bytes()==subprocess.check_output(['/usr/bin/git','-C',str(root),'show',
        PILOT_REVISION+':Pycavi2/tools/run_ocam_linearity_bias.py']),'Pilot controller differs')
    helper=runpy.run_path(str(old_driver));fingerprint=helper['fingerprint'];stamp=helper['stamp'];sha=helper['sha']
    source=helper['QUALIFICATION']/'source';private=helper['PRIVATE']
    proof=json.loads((helper['QUALIFICATION']/'qualification.json').read_text())
    guard=runpy.run_path(str(source/'Pycavi2/tests/qualify_inspection_stages.py'))
    snapshot=runpy.run_path(str(source/'Pycavi2/tests/qualify_pair_qc_mac.py'))['source_digest']
    prefix_identity=runpy.run_path(str(source/'Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    before=guard['checkout'](root);print(json.dumps(before,indent=2),flush=True)
    require(before['head']=='c73d9a9e3a631fbbb2346beaa3c150c110a60343' and before['branch']=='main'
        and before['upstream']=='origin/main' and not before['status'],'Unchanged clean main required')
    require(before['origin']==before['push']=='git@github.com:fselman/wenu-imaging.git','Unexpected origin')
    exported=snapshot(source)
    require(proof['status']=='passed' and all(proof['preservation'].values()) and exported==proof['source_sha256'],
        'Qualified QC source changed')
    installed_paths=guard['protected_paths']();installed=[guard['identity'](p) for p in installed_paths]
    runtime=prefix_identity(private);reference=snapshot(PILOT)
    checks_path=work/'checks.py'
    require(checks_path.read_bytes()==subprocess.check_output(['/usr/bin/git','-C',str(root),'show',
        args.revision+':Pycavi2/tests/test_ocam_bias_batch.py']),'Focused batch checks differ')
    print('Running focused batch orchestration controls...',flush=True)
    with (work/'checks.log').open('x') as log:
        check_code=subprocess.run([str(normal),'-B',str(checks_path),'--module',str(work/'run.py')],
            stdout=log,stderr=subprocess.STDOUT).returncode
    print((work/'checks.log').read_text(),flush=True)
    require(check_code==0,'Focused batch controls failed; no observations processed')
    pilot_execution=json.loads((PILOT/'execution.json').read_text())
    require(pilot_execution['status']=='complete' and pilot_execution['native_exit_status']==0,'Original bias recipe receipt incomplete')
    template=pilot['argv'][pilot['argv'].index('--')+1:];base=options(template)
    adapter=Path(pilot['argv'][pilot['argv'].index('--native-adapter')+1]);writer=Path(pilot['argv'][2])
    for path in (adapter,writer):require(sha(path)==pilot['inputs'][str(path)]['sha256'],'Pilot binary/mapper changed')
    members=[Path(p) for p in Path(base['--bias']).read_text().splitlines()]
    require(len(members)==len(set(members))==10,'Ten shared bias inputs required')
    bpm=Path(base['--input-bpm']);images=members+[bpm]
    reviews=[Path(p) for p in pilot['inputs'] if Path(p).name=='review.json']
    require(len(reviews)==1 and sha(reviews[0])==pilot['inputs'][str(reviews[0])]['sha256'],'Saved header review changed')
    review=json.loads(reviews[0].read_text())
    import tomllib
    with (source/'config/detectors/omegacam-1x1.toml').open('rb') as stream:geometry=tomllib.load(stream)
    ids=[d['id'] for d in geometry['detector']]
    require(set(ids)=={f'ESO_CCD_#{n}' for n in range(65,97)} and len(ids)==32,'All32 detector identities required')
    # Preserve previously admitted shared PAF/list, all pilot products/records and metadata.
    for path in (Path(base['--pafname']),Path(base['--bias'])):
        require(sha(path)==pilot['inputs'][str(path)]['sha256'],'Pilot recipe configuration changed')
    require(shutil.disk_usage(pictures).free>3*1024**3,'Need at least3GiB free for retained candidate masters/headroom')
    entries=[]
    for detector in sorted(geometry['detector'],key=lambda d:d['native_paf_chip']):
        if detector['id']=='ESO_CCD_#65':continue
        directory=work/detector['id'].replace('ESO_CCD_#','CCD');directory.mkdir();(directory/'QC').mkdir()
        entries.append(detector_plan(template,detector,review,members,directory))
    plan=dict(controller_revision=args.revision,pilot=str(PILOT),native_adapter=str(adapter),entries=entries,
        shared_images=[str(p) for p in images],native_revision=pilot['native_revision'],serializer_revision=pilot['serializer_revision'])
    (work/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    (work/'README.md').write_text('Remaining31 serial OCAM median-bias signal candidates for linearity. CCD65 reused. Shared10 bias files and structuralBPM hashed before/after the complete batch; existing qualified native/ASDF recipe reused without numerical/default changes. Per-detector recipe completion is provisional until overall-execution.json source/preservation checks pass. On failure all partial products/logs remain; never resume/overwrite. Raw first2 RON pair unchanged, master variance unavailable. No linearity fit, accepted calibration, plotting/HTML or install. Keep while dependent linearity work references these candidates; erase only after required comparison/provenance retained.\n')
    report=dict(status='running',controller_revision=args.revision,detectors_processed=0,reference_detector_reused=True,
        source_preservation=False,results=[],variance_state='unavailable',fitted=False,plotting_performed=False)
    frozen={};after={};created=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    report_path=work/'overall-execution.json'
    def save(results):
        report.update(results=results,detectors_processed=len(results))
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    for key in ('PYTHONPATH','PYTHONHOME','LD_PRELOAD','DYLD_INSERT_LIBRARIES','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH'):env.pop(key,None)
    def command(entry):
        directory=Path(entry['directory'])
        argv=[str(private/'bin/python'),'-B',str(writer),'--native-adapter',str(adapter),
            '--receipt',str(directory/'execution.json'),'--qc-directory',str(directory/'QC'),
            '--assessment-id','OCAM-linearity-bias:'+work.name+':'+entry['detector'],'--created-at',created,'--',*entry['native']]
        print('BIAS RECIPE:',entry['detector'],flush=True)
        with (directory/'command.log').open('x') as log:
            process=subprocess.Popen(argv,cwd=directory,env=env,stdout=log,stderr=subprocess.STDOUT)
            while True:
                try:code=process.wait(timeout=30);break
                except subprocess.TimeoutExpired:print('Still running:',entry['detector'],flush=True)
        if code:print((directory/'command.log').read_text()[-8000:],flush=True)
        require(code==0,'Bias recipe failed: '+entry['detector'])
        executed=json.loads((directory/'execution.json').read_text())
        handoff=json.loads((directory/'handoff.json').read_text())
        require(handoff['detector_id']==entry['detector'] and handoff['input_hdu']==entry['hdu'] and
            handoff['configuration_detector']==entry['configuration_detector'] and
            handoff['bpm']['hdu']==entry['bpm_hdu'] and handoff['bpm']['path']==str(bpm) and
            handoff['bpm']['good_value']==1 and handoff['bpm']['active_only']==1 and
            handoff['readout_id']==base['--readout-id'] and handoff['output_hdu']==1 and
            executed['producer']==pilot_execution['producer'] and
            [p['path'] for p in handoff['inputs']]==[str(p) for p in members],'Native bias bindings differ')
        produced=[p for p in directory.rglob('*') if p.is_file()]
        executed.update(detector=entry['detector'],accepted_frames=sum(p['accepted'] for p in handoff['inputs']),
                        outputs={str(p):fingerprint(p) for p in produced},
                        product=handoff['output'],source_preservation_scope='pending overall batch verification')
        require(Path(executed['product']).is_file() and Path(executed['qc_product']).is_file(),'Missing native/ASDF product')
        print('ACCEPTED:',entry['detector'],executed['accepted_frames'],'/ 10',flush=True)
        return executed
    try:
        frozen=image_pass(images,pilot['inputs'],fingerprint,'Before')
        report['inputs']=frozen;save([])
        results=serial(entries,command,save)
        require(len(results)==31,'Missing detector results')
        report['status']='native_and_ASDF_complete_pending_source_verification'
    except Exception as error:
        report.update(status='failed',error=repr(error));raise
    finally:
        checks={}
        try:
            if len(frozen)==len(images):
                after=image_pass(images,pilot['inputs'],fingerprint,'After')
                checks['shared_inputs']=after==frozen
            else:checks['shared_inputs']=False
        except Exception as error:checks['shared_inputs']=False;report['source_verification_error']=repr(error)
        def unchanged_products():
            for i,result in enumerate(report['results'],1):
                print('Verifying detector products',i,'/',len(report['results']),result['detector'],flush=True)
                for path,value in result['outputs'].items():
                    if fingerprint(path)!=value:return False
            return True
        for name,check in (
            ('products',unchanged_products),
            ('checkout',lambda:guard['checkout'](root)==before),
            ('installed_files',lambda:[guard['identity'](p) for p in installed_paths]==installed),
            ('exported_source',lambda:snapshot(source)==exported),
            ('private_qc_runtime',lambda:prefix_identity(private)==runtime),
            ('reference_pilot',lambda:snapshot(PILOT)==reference),
            ('native_adapter',lambda:sha(adapter)==pilot['inputs'][str(adapter)]['sha256'])):
            try:checks[name]=check()
            except Exception as error:checks[name]=False;report.setdefault('preservation_errors',{})[name]=repr(error)
        report.update(preservation=checks,source_preservation=checks['shared_inputs'],after_inputs=after)
        if report['status']=='native_and_ASDF_complete_pending_source_verification' and all(checks.values()):
            try:
                catalog=[dict(detector='ESO_CCD_#65',product=pilot['product'],qc_product=pilot['qc_product'],hdu=1)]
                catalog.extend(dict(detector=r['detector'],product=r['product'],qc_product=r['qc_product'],hdu=1) for r in report['results'])
                with (work/'masters.json').open('x') as stream:
                    json.dump(dict(status='candidate_signal_products',variance_state='unavailable',batch_receipt=str(report_path),masters=catalog),stream,indent=2)
                    stream.write('\n')
                report.update(status='complete_for_owner_inspection',hash_passes_per_image=2)
            except Exception as error:report.update(status='failed',catalog_error=repr(error))
        else:report['status']='failed'
        report_path.write_text(json.dumps(report,indent=2)+'\n')
        print('OVERALL STATUS:',report['status'],flush=True);print('DETECTORS COMPLETED:',report['detectors_processed'],flush=True)
        print('PRESERVATION:',checks,flush=True);print('RETAINED BIAS BATCH:',work,flush=True)
    require(report['status']=='complete_for_owner_inspection','Bias batch/preservation failed; retain all evidence')
    print('MASTER CATALOG:',work/'masters.json',flush=True)


if __name__=='__main__':main()
