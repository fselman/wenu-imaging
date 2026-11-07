"""Bounded real CCD65 median-bias pilot for linearity, using qualified recipe components."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys

ROOT=Path('/Users/fselman/Developer/wenu-imaging')
NORMAL=Path('/Users/fselman/anaconda3/envs/wenu-imaging/bin/python')
PICTURES=Path('/Users/fselman/Pictures/OCAM/wenu-imaging')
QUALIFICATION=Path('/Users/fselman/Software/build/wenu-imaging/mac-pair-qc-viewer-n3dsjk5f')
OLD=Path('/Users/fselman/Software/build/wenu-imaging/mac-bpm-complete-Ia5qliwa')
PRIVATE=Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment')


def require(ok,message):
    if not ok:raise RuntimeError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def stamp(path):
    s=Path(path).stat()
    return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_mode,s.st_ctime_ns]


def fingerprint(path):
    before=stamp(path);digest=sha(path)
    require(stamp(path)==before,'Source changed while hashing: '+str(path))
    return dict(sha256=digest,stat=before)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--revision',required=True);p.add_argument('--run',type=Path,required=True)
    a=p.parse_args()
    require((platform.system(),platform.node().split('.')[0])==('Darwin','MC02VV0HPHTDG'),'Wrong Mac')
    require(Path(sys.prefix)==NORMAL.parent.parent and Path(sys.executable).resolve()==NORMAL.resolve(),'Use normal imaging Python')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,'Require niceness >=10')
    work=a.run.resolve(strict=True)
    require(work.parent==PICTURES and set(f.name for f in work.iterdir())=={'run.py'},'Fresh purpose directory required')
    exact=subprocess.check_output(['/usr/bin/git','-C',str(ROOT),'show',a.revision+':Pycavi2/tools/run_ocam_linearity_bias.py'])
    require(Path(__file__).resolve()==work/'run.py' and exact==Path(__file__).read_bytes(),'Exact fetched controller required')
    source=QUALIFICATION/'source'
    qualified=json.loads((QUALIFICATION/'qualification.json').read_text())
    require(qualified['status']=='passed' and qualified['source_revision']=='aecce5c4404342614723dc718099e62c2f86a9c2'
            and all(qualified['preservation'].values()),'Passed retained QC source required')
    guard=runpy.run_path(str(source/'Pycavi2/tests/qualify_inspection_stages.py'))
    snapshot=runpy.run_path(str(source/'Pycavi2/tests/qualify_pair_qc_mac.py'))['source_digest']
    prefix_identity=runpy.run_path(str(source/'Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    before=guard['checkout'](ROOT);print(json.dumps(before,indent=2),flush=True)
    require(before['head']=='c73d9a9e3a631fbbb2346beaa3c150c110a60343' and before['branch']=='main'
            and before['upstream']=='origin/main' and not before['status'],'Unchanged clean main required')
    require(before['origin']==before['push']=='git@github.com:fselman/wenu-imaging.git','Unexpected origin')
    exported=snapshot(source);require(exported==qualified['source_sha256'],'Retained QC source changed')
    installed_paths=guard['protected_paths']();installed=[guard['identity'](v) for v in installed_paths]
    runtime=prefix_identity(PRIVATE)
    proof=json.loads((OLD/'qualification.json').read_text())
    require(proof['revision']=='022cf3683fe47d4de6a7acac1e3799cb49201d40' and proof['status']=='passed'
            and all(proof['preservation'].values()),'Passed complete native bias/BPM adapter required')
    adapter=OLD/'build-c17/mefpp2/mefpp_m5';adapter_hash=sha(adapter)
    native_proofs=[json.loads(v.read_text()) for v in (OLD/'build-c17/mefpp2/test-work').glob('bpm-complete-*/qualification.json')]
    require(sum(v.get('status')=='passed' and v.get('adapter_sha256')==adapter_hash for v in native_proofs)==1,
            'Native qualified binary changed/ambiguous')
    writer=source/'Pycavi2/pycavi/pycavi/pycavi_bias_qc.py'
    require(sha(writer)==proof['source_sha256']['Pycavi2/pycavi/pycavi/pycavi_bias_qc.py'],'Qualified bias mapper changed')
    reference=PICTURES/'ccd65-raw-pairs-bpmfixed-zfs377ok'
    lineage=json.loads((reference/'lineage.json').read_text())
    reviews=[v for v in PICTURES.glob('first-pair-review-*/review.json')
             if sha(v)==lineage['owner_approval']['review_sha256']]
    require(len(reviews)==1,'Require one exact approved saved-header review')
    review_path=reviews[0]
    review=json.loads(review_path.read_text())
    require(review['headers']['bias_count']==10 and review['headers']['bpm_bindings']['ESO_CCD_#65']==1,
            'Reviewed bias count/BPM binding differs')
    records=review['current_source_stats'][:10]
    members=[Path(v['path']) for v in records]
    require(len(members)==len(set(members))==10 and
            all(review['headers']['raw_bindings'][str(i)]['ESO_CCD_#65']==1 for i in range(10)),
            'Require ten reviewed CCD65 biases in HDU1')
    for member,record in zip(members,records):
        require(stamp(member)[1:5]==record['stat_identity'][1:5],'Reviewed bias source changed: '+str(member))
    prep_path=PICTURES/'legacy-bpm-structure-b1h9egzp/prepared/preparation.json'
    prep=json.loads(prep_path.read_text());bpm=Path(prep['copy'])
    require(prep['status']=='prepared_verified_copy' and prep['payload_preservation'] is True
            and prep['copy_sha256']==lineage['derived_bpm_sha256'],'Structural BPM proof differs')
    paf_source=source/'mefpp2/ins/mef/config/omegacam.paf'
    require(sha(paf_source)=='709d65acdeea6c889ed1468cbb3966d5de93ec654ee030032a096ca12624333f','Canonical PAF differs')
    paf=work/'omegacam.paf';paf.write_bytes(paf_source.read_bytes())
    listing=work/'bias.list';listing.write_text(''.join(str(v)+'\n' for v in members))
    qc=work/'QC';qc.mkdir();output=work/'OCAM_MB_CCD65_candidate.fits'
    native=['cal','bias','--pafname',str(paf),'--bias',str(listing),
        '--detector-id','ESO_CCD_#65','--expected-extname','ESO_CCD_#65','--hdu','1','--config-detector','0',
        '--readout-id','OMEGACAM:normal:ordered:1x1','--bin-x','1','--bin-y','1',
        '--input-bpm',str(bpm),'--bpm-hdu','1','--bpm-good-value','1','--bpm-coordinates','active',
        '--bpm-expected-extname','ESO_CCD_#65','--output',str(output),'--work-dir',str(work),
        '--log-path',str(work/'native.log'),'--config-record',str(work/'configuration.json'),
        '--qc-record',str(work/'handoff.json'),'--measurements','yes','--mad','yes',
        '--ron-first','0','--ron-second','1','--high-sigma','5']
    argv=[str(PRIVATE/'bin/python'),'-B',str(writer),'--native-adapter',str(adapter),
        '--receipt',str(work/'execution.json'),'--qc-directory',str(qc),
        '--assessment-id','OCAM-linearity-bias-CCD65:'+work.name,
        '--created-at',datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'--',*native]
    paths=members+[bpm,paf,listing,adapter,writer,Path(__file__),review_path,prep_path,reference/'lineage.json',reference/'measurement/execution.json']
    frozen={};report=dict(status='failed',detector='ESO_CCD_#65',master_inputs=10,native_revision=proof['revision'],
        serializer_revision=qualified['source_revision'],controller_revision=a.revision,argv=argv,
        variance_state='unavailable',fitted=False,plotting_performed=False,scientific_acceptance=False)
    (work/'README.md').write_text('CCD65 scan-corrected median-master bias candidate for linearity sample preparation. Reuses the qualified native bias recipe, canonical PAF and ten reviewed biases. First two biases remain raw RON inputs. Full frame/scan QC and legacy rejection decisions retained in shared ASDF. Master variance remains unavailable; no RON-squared/N assignment or fit/correction acceptance. Retain while the linearity work references this candidate; remove only after required comparison/provenance is retained. No automatic cleanup. outer-execution.json is the guarded overall status.\n')
    print('PAF BIAS SETTINGS:',flush=True)
    for line in paf.read_text().splitlines():
        if line.startswith(('MEF.BIAS.FRAMETHR.','MEF.BIAS.KAPPA1','MEF.BIAS.FRAMENUM.MIN','MEF.SCANREJ.MIN','MEF.SCANREJ.MAX')):print(line,flush=True)
    def verify_inputs():
        for i,(path,item) in enumerate(frozen.items(),1):
            print('Verifying source',i,'/',len(frozen),Path(path).name,flush=True)
            if fingerprint(path)!=item:return False
        return True
    try:
        for i,path in enumerate(paths,1):
            print('Freezing input',i,'/',len(paths),path.name,flush=True);frozen[str(path)]=fingerprint(path)
        require(frozen[str(bpm)]['sha256']==prep['copy_sha256'],'BPM bytes changed')
        old_receipt=json.loads((reference/'measurement/execution.json').read_text())
        require(old_receipt['status']=='complete_for_owner_inspection' and old_receipt['source_preservation'] is True,'Reference raw pair receipt incomplete')
        previous={v['path']:v for v in old_receipt['inputs']}
        for path in members[:2]:require(frozen[str(path)]['sha256']==previous[str(path)]['sha256'],'Approved raw RON pair changed')
        report['inputs']=frozen
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        for key in ('PYTHONPATH','PYTHONHOME','LD_PRELOAD','DYLD_INSERT_LIBRARIES','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH'):env.pop(key,None)
        print('RUNNING CCD65 BIAS RECIPE:',work,flush=True)
        with (work/'command.log').open('x') as log:
            child=subprocess.Popen(argv,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT)
            while True:
                try:code=child.wait(timeout=30);break
                except subprocess.TimeoutExpired:print('Still running bias recipe...',flush=True)
        print((work/'command.log').read_text()[-8000:],flush=True)
        require(code==0,'Native/ASDF bias recipe failed; retain all logs')
        executed=json.loads((work/'execution.json').read_text())
        require(executed['status']=='complete' and executed['native_exit_status']==0,'Bias recipe incomplete')
        handoff=json.loads((work/'handoff.json').read_text())
        report.update(status='complete_for_owner_inspection',product=str(output),qc_product=executed['qc_product'],
                      accepted_frames=sum(v['accepted'] for v in handoff['inputs']))
        print('FRAME QC: asset / accepted / raw mean ADU / corrected mean ADU / scan median ADU / scan stdev ADU',flush=True)
        for member in handoff['inputs']:
            print(Path(member['path']).name,member['accepted'],
                  member['raw_active']['mean'] if member['raw_active']['level_available'] else None,
                  member['corrected_active']['mean'] if member['corrected_active']['level_available'] else None,
                  member['scan_correction']['median'],member['scan_correction']['stdev'],sep='\t',flush=True)
        print('ACCEPTED FRAMES:',report['accepted_frames'],'/',len(handoff['inputs']),flush=True)
    except Exception as error:
        report.update(status='failed',error=repr(error));raise
    finally:
        checks={}
        for name,check in (
            ('checkout',lambda:guard['checkout'](ROOT)==before),
            ('installed_files',lambda:[guard['identity'](v) for v in installed_paths]==installed),
            ('exported_source',lambda:snapshot(source)==exported),
            ('private_qc_runtime',lambda:prefix_identity(PRIVATE)==runtime),
            ('inputs',verify_inputs)):
            try:checks[name]=check()
            except Exception as error:checks[name]=False;report.setdefault('preservation_errors',{})[name]=repr(error)
        report['preservation']=checks
        if not all(checks.values()):report['status']='failed'
        (work/'outer-execution.json').write_text(json.dumps(report,indent=2)+'\n')
        print('OVERALL STATUS:',report['status'],flush=True);print('PRESERVATION:',checks,flush=True)
        print('RETAINED BIAS PILOT:',work,flush=True)
        if report.get('product'):print('MASTER:',report['product'],flush=True);print('QC:',report['qc_product'],flush=True)
    require(report['status']=='complete_for_owner_inspection','Bias recipe or preservation failed')


if __name__=='__main__':main()
