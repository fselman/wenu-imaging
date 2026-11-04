"""One-use serial approved singleton extraction. Native transports only, no fit/ASDF writer."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys
import tomllib

ROOT=Path('/Users/fselman/Developer/wenu-imaging')
PICTURES=Path('/Users/fselman/Pictures/OCAM/wenu-imaging')
NORMAL=Path('/Users/fselman/anaconda3/envs/wenu-imaging/bin/python')
PRIVATE=Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment')
QUALIFICATION=Path('/Users/fselman/Software/build/wenu-imaging/mac-sample-command-1iwkve9e')
NATIVE_REVISION='f560d67a23a6ede62ff6b8fccd755349456c10f6'
QC_QUALIFICATION=Path('/Users/fselman/Software/build/wenu-imaging/mac-pair-qc-viewer-n3dsjk5f')
PILOT=PICTURES/'linearity-bias-CCD65-epw82wy3'
BIAS_BATCH=PICTURES/'linearity-bias-batch-05ijf_sx'
RAW_BATCH=PICTURES/'ocam-raw-pairs-serial-nx_j6g1j/batch'
REFERENCE=PICTURES/'ccd65-raw-pairs-bpmfixed-zfs377ok'
SAMPLE_COLUMNS='schema_version detector amplifier configuration_detector source_roi active_x active_y raw_x raw_y asset input_index hdu pair_id seconds admission_state signal_adu noise_state'.split()
POP_COLUMNS='input_index outside_selected_sites bpm_excluded sample_excluded nonfinite saturated admitted'.split()


def require(ok,message):
    if not ok:raise RuntimeError(message)


def read(path):
    return json.loads(Path(path).read_text())


def catalog_entries(catalog,batch,pilot,execution):
    require(catalog['status']=='candidate_signal_products' and catalog['variance_state']=='unavailable', 'Wrong master catalog')
    require(batch['status']=='complete_for_owner_inspection' and batch['detectors_processed']==31
            and batch['source_preservation'] is True and batch['preservation'] and all(batch['preservation'].values()), 'Incomplete bias batch')
    require(pilot['status']=='complete_for_owner_inspection' and pilot['preservation'] and all(pilot['preservation'].values()), 'Incomplete bias pilot')
    require(execution['status']=='complete' and execution['native_exit_status']==0,'Incomplete pilot recipe')
    entries=catalog['masters'];ids={f'ESO_CCD_#{n}' for n in range(65,97)}
    require(len(entries)==32 and {e['detector'] for e in entries}==ids, 'Require all32 unique masters')
    results=batch['results'];require(len(results)==31 and {r['detector'] for r in results}==ids-{'ESO_CCD_#65'}, 'Wrong batch result identities')
    indexed={r['detector']:r for r in results};indexed['ESO_CCD_#65']=dict(execution,**{
        'detector':'ESO_CCD_#65','product':pilot['product'],'qc_product':pilot['qc_product'],'accepted_frames':pilot['accepted_frames']})
    merged=[]
    for entry in entries:
        r=indexed[entry['detector']]
        require(r['status']=='complete' and r['native_exit_status']==0 and entry['hdu']==1
                and entry['product']==r['product'] and entry['qc_product']==r['qc_product'], 'Master identity/path/HDU differs')
        if entry['detector']!='ESO_CCD_#65':
            require(entry['product'] in r['outputs'] and entry['qc_product'] in r['outputs'],'Master baseline missing')
        merged.append(dict(entry,recipe=r))
    return merged


def image_pass(paths,expected,fingerprint,label):
    values={}
    require(len(paths)==len(set(map(str,paths))), 'Duplicate image path')
    for i,path in enumerate(paths,1):
        print(label,'image',i,'/',len(paths),flush=True)
        value=fingerprint(path);wanted=expected[str(path)]
        if wanted is not None:require(value['sha256']==wanted,'Image differs from retained baseline: '+str(path))
        values[str(path)]=value
    return values


def read_tsv(path,columns):
    with Path(path).open(newline='') as f:
        reader=csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE)
        require(reader.fieldnames==columns,'Unexpected TSV columns')
        rows=list(reader)
    require(all(None not in r and None not in r.values() for r in rows),'Malformed TSV row')
    return rows


def integer(text):
    require(text.isascii() and text.isdecimal(),'Invalid integer transport')
    return int(text)


def admit_tables(directory,entry,selection,population,active_pixels):
    require((directory/'command.complete').read_text()=='corrected_samples_complete_noise_unavailable\n','Missing native marker')
    rows=read_tsv(directory/'samples.tsv',SAMPLE_COLUMNS);counts=read_tsv(directory/'population.tsv',POP_COLUMNS)
    frames=selection['flat'];require(len(rows)==len(frames)*len(population) and len(counts)==len(frames),'Incomplete sample population')
    admitted=0
    for frame_index,frame in enumerate(frames):
        group=rows[frame_index*len(population):(frame_index+1)*len(population)]
        times=set();available=0
        for row,site in zip(group,population):
            require(row['schema_version']=='1' and row['detector']==entry['detector'] and row['amplifier']==site['amplifier']
                    and integer(row['configuration_detector'])==site['configuration_detector'] and row['source_roi']==site['source_roi']
                    and [integer(row['active_x']),integer(row['active_y'])]==site['active_pixel']
                    and [integer(row['raw_x']),integer(row['raw_y'])]==site['raw_pixel'], 'Sample coordinate/identity mismatch')
            require(row['asset']==frame['asset'] and integer(row['input_index'])==frame['index'] and integer(row['hdu'])==frame['hdu']
                    and row['pair_id']==frame['pair'] and row['noise_state']=='unavailable','Frame provenance/noise state mismatch')
            seconds=float(row['seconds']);require(math.isfinite(seconds) and seconds>0,'Invalid exact exposure');times.add(seconds)
            require(row['admission_state'] in ('admitted','not_admitted'),'Unknown admission state')
            if row['admission_state']=='admitted':
                require(bool(row['signal_adu']) and math.isfinite(float(row['signal_adu'])),'Missing/nonfinite admitted signal')
                available+=1
            else:require(row['signal_adu']=='','Unavailable signal must be blank')
        require(len(times)==1,'Frame exposure varies across sites')
        c=counts[frame_index];values={k:integer(v) for k,v in c.items()}
        require(values['input_index']==frame['index'] and values['outside_selected_sites']==active_pixels-len(population)
                and values['sample_excluded']==0 and values['admitted']==available
                and sum(v for k,v in values.items() if k not in ('input_index','outside_selected_sites'))==len(population), 'Population counters disagree')
        admitted+=available
    return dict(rows=len(rows),admitted=admitted,not_admitted=len(rows)-admitted,noise_state='unavailable')


def validate_qc(manifest,destination):
    """Existing shared reader/traversal only, in retained private ASDF runtime."""
    require(Path(sys.prefix).resolve()==PRIVATE.resolve(),'Private QC Python required')
    from importlib.metadata import version
    require(version('asdf')=='6.0.0' and version('asdf-standard')=='1.5.0','Unexpected retained ASDF versions')
    sys.path.insert(0,str(QC_QUALIFICATION/'source/Pycavi2/pycavi/pycavi'))
    import pycavi_qc as qc
    import pycavi_bias_qc as bias
    results=[]
    for entry in read(manifest):
        handoff=bias.load_handoff(entry['handoff']);recipe=entry['recipe']
        require(handoff['detector_id']==entry['detector'] and handoff['configuration_detector']==entry['configuration_detector']
                and handoff['output']==entry['product'] and handoff['output_hdu']==entry['hdu']
                and handoff['readout_id']=='OMEGACAM:normal:ordered:1x1'
                and handoff['bin_x']==handoff['bin_y']==1 and handoff['producer']==recipe['producer']
                and handoff['input_hdu']==entry['expected_input_hdu']
                and [m['path'] for m in handoff['inputs']]==entry['expected_bias_paths']
                and handoff['bpm']['selected']==1 and handoff['bpm']['path']==entry['expected_bpm']['path']
                and handoff['bpm']['hdu']==entry['expected_bpm']['hdu']
                and handoff['bpm']['good_value']==1 and handoff['bpm']['active_only']==1, 'Master handoff binding mismatch')
        record=qc.read_record(entry['qc_product']);tree=record.as_dict()
        list(qc.traverse_records(entry['qc_product'],qc_root=Path(entry['qc_product']).parent,max_records=12))
        require(record.digest==recipe['qc_record_digest'] and tree['file']['location']==entry['product']
                and tree['provenance']['producer']==handoff['producer']
                and tree['file']['selectors']==[dict(detector_id=entry['detector'],hdu_index=entry['hdu'],configuration_detector=entry['configuration_detector'])],
                'Master QC digest/location/producer/selector mismatch')
        require(handoff['configuration']==read(handoff['configuration_record']), 'Master configuration snapshot differs')
        configuration_id='sha256:'+hashlib.sha256(json.dumps(handoff['configuration'],sort_keys=True,allow_nan=False,separators=(',', ':')).encode()).hexdigest()
        require(tree['provenance']['configuration_id']==configuration_id,'Master configuration/QC lineage differs')
        require(len(tree['inputs'])==11 and len(handoff['inputs'])==10,'Expected ten bias leaves and BPM')
        accepted=[m['accepted'] for m in handoff['inputs']]
        require(sum(accepted)==recipe['accepted_frames'] and tree['inputs'][-1]['participation']['status']=='used'
                and tree['inputs'][-1]['file_id']==entry['expected_bpm']['path'],'Master accepted membership/BPM differs')
        for member,decision in zip(tree['inputs'][:10],accepted):
            require(member['participation']['status']==('used' if decision else 'rejected')
                    and member['file_id']==entry['expected_bias_paths'][member['index']], 'Master participation/source differs')
        results.append(dict(detector=entry['detector'],qc_digest=record.digest,
            members=[dict(path=m['path'],accepted=m['accepted']) for m in handoff['inputs']],
            accepted_frames=sum(accepted),variance_state='unavailable'))
        print('Verified master ASDF:',entry['detector'],sum(accepted),'/ 10',flush=True)
    Path(destination).write_text(json.dumps(dict(status='complete',masters=results),indent=2)+'\n')


def launch(argv,log):
    with log.open('x') as output:
        process=subprocess.Popen(argv,stdout=output,stderr=subprocess.STDOUT)
        while True:
            try:code=process.wait(timeout=30);break
            except subprocess.TimeoutExpired:print('Still running:',log.parent.name,flush=True)
    if code:print(log.read_text()[-8000:],flush=True)
    require(code==0,'Command failed; retain '+str(log))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision');parser.add_argument('--run',type=Path)
    parser.add_argument('--validate-qc',nargs=2,type=Path)
    args=parser.parse_args()
    require((platform.system(),platform.node().split('.')[0])==('Darwin','MC02VV0HPHTDG'),'Wrong Mac')
    if args.validate_qc:validate_qc(*args.validate_qc);return
    require(args.revision and args.run,'Revision/run required')
    require(Path(sys.executable).resolve()==NORMAL.resolve() and Path(sys.prefix)==NORMAL.parent.parent,'Normal imaging Python required')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,'Require niceness >=10')
    work=args.run.resolve(strict=True)
    require(work.parent==PICTURES and {p.name for p in work.iterdir()}=={'run.py','checks.py'},'Fresh retained run required')
    def git(*arguments):return subprocess.check_output(['/usr/bin/git','-C',str(ROOT),*arguments])
    require(Path(__file__).resolve()==work/'run.py' and Path(__file__).read_bytes()==git('show',args.revision+':Pycavi2/tools/run_ocam_linearity_samples.py'),'Exact controller required')
    require((work/'checks.py').read_bytes()==git('show',args.revision+':Pycavi2/tests/test_ocam_sample_batch.py'),'Exact controls required')
    source=QUALIFICATION/'source';proof=read(QUALIFICATION/'qualification.json')
    require(proof['status']=='passed' and proof['source_revision']==NATIVE_REVISION and proof['preservation'] and all(proof['preservation'].values()),'Passed native gate required')
    snapshot=runpy.run_path(str(source/'Pycavi2/tests/qualify_sample_command_mac.py'))['digest_source']
    exported=snapshot(source);require(exported==proof['source_sha256'],'Qualified native source changed')
    command=Path(proof['executables']['mefpp_sample_extract']['path'])
    require(command==QUALIFICATION/'build-c17/mefpp2/mefpp_sample_extract','Unexpected qualified binary path')
    require((PILOT/'run.py').read_bytes()==git('show','c93dcd9152ec58fee495b4bf84bdc6bffc0529ef:Pycavi2/tools/run_ocam_linearity_bias.py'),'Pilot controller differs')
    helper=runpy.run_path(str(PILOT/'run.py'));fingerprint=helper['fingerprint'];sha=helper['sha']
    require(sha(command)==proof['executables']['mefpp_sample_extract']['sha256'],'Native binary changed')
    qcsource=QC_QUALIFICATION/'source';qcproof=read(QC_QUALIFICATION/'qualification.json')
    qcsnapshot=runpy.run_path(str(qcsource/'Pycavi2/tests/qualify_pair_qc_mac.py'))['source_digest']
    qcexported=qcsnapshot(qcsource)
    require(qcproof['status']=='passed' and qcproof['preservation'] and all(qcproof['preservation'].values())
            and qcproof['source_revision']=='aecce5c4404342614723dc718099e62c2f86a9c2'
            and qcexported==qcproof['source_sha256'],'Qualified QC source changed')
    guard=runpy.run_path(str(qcsource/'Pycavi2/tests/qualify_inspection_stages.py'))
    before=guard['checkout'](ROOT);print(json.dumps(before,indent=2),flush=True)
    require(before['head']=='c73d9a9e3a631fbbb2346beaa3c150c110a60343' and before['branch']=='main'
            and before['upstream']=='origin/main' and not before['status'] and before['origin']==before['push']=='git@github.com:fselman/wenu-imaging.git','Require unchanged clean imaging main/origin')
    protected=guard['protected_paths']();installed=[guard['identity'](p) for p in protected]
    prefix_identity=runpy.run_path(str(qcsource/'Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity'];runtime=prefix_identity(PRIVATE)
    launch([str(NORMAL),'-B',str(work/'checks.py'),'--module',str(work/'run.py')],work/'checks.log')
    print((work/'checks.log').read_text(),flush=True)
    launch([str(PRIVATE/'bin/python'),'-B',str(work/'checks.py'),'--module',str(work/'run.py'),
            '--qc','--work',str(work)],work/'checks-qc.log')
    print((work/'checks-qc.log').read_text(),flush=True)
    catalog_path=BIAS_BATCH/'masters.json';batch_path=BIAS_BATCH/'overall-execution.json'
    catalog=read(catalog_path);batch=read(batch_path);pilot=read(PILOT/'outer-execution.json');execution=read(PILOT/'execution.json')
    require(catalog['batch_receipt']==str(batch_path) and batch['controller_revision']=='d84568b5fedeffe4201d095222ee09224ee8cc73','Wrong retained bias batch')
    masters=catalog_entries(catalog,batch,pilot,execution)
    # The original65 pilot has no recorded historical whole-FITS hash. Its approved
    # path/HDU and semantic QC digest are checked; establish its byte baseline now.
    raw_execution=read(REFERENCE/'measurement/execution.json');lineage=read(REFERENCE/'lineage.json')
    require(raw_execution['status']=='complete_for_owner_inspection' and raw_execution['source_preservation'] is True
            and raw_execution['source_revision']=='512092fa3180653f165f744a1ba7d9991e251f03','Incomplete raw reference')
    references={r['path']:r['sha256'] for r in raw_execution['inputs']}
    review_paths=[Path(p) for p in pilot['inputs'] if Path(p).name=='review.json']
    require(len(review_paths)==1 and sha(review_paths[0])==lineage['owner_approval']['review_sha256']
            ==pilot['inputs'][str(review_paths[0])]['sha256'],'Approved header review differs')
    review=read(review_paths[0]);raw_manifest=read(RAW_BATCH/'batch.json');raw_receipt=read(RAW_BATCH/'execution.json')
    require(raw_receipt['status']=='complete_for_owner_inspection' and raw_receipt['source_preservation'] is True,'Incomplete raw batch')
    transports={e['detector']:Path(e['measurement']) for e in raw_manifest['entries']}
    require(len(transports)==31 and 'ESO_CCD_#65' not in transports,'Wrong original raw transports')
    transports['ESO_CCD_#65']=REFERENCE/'measurement'
    old_batch=runpy.run_path(str(source/'tools/run-ocam-pair-batch.py'))
    runner=old_batch['runner'];reference_selection=tomllib.loads((REFERENCE/'measurement/selection.toml').read_text())
    require(sha(REFERENCE/'measurement/selection.toml')==lineage['derived_selection_sha256'],'Reference selection differs')
    selected=work/'singleton-sites';selected.mkdir()
    sites=runpy.run_path(str(source/'tools/prepare-linearity-sites.py'))
    sites_manifest=sites['prepare'](source/'config/characterization/omegacam-linearity-pilot-sites.json',
        source/'config/detectors/omegacam-1x1.toml',source/'config/processing/omegacam-characterization.toml',selected)
    geometry,policy,trims=runner.FOOTPRINT.load(source/'config/detectors/omegacam-1x1.toml',source/'config/processing/omegacam-characterization.toml')
    by_id={d['id']:d for d in geometry['detector']};population=sites_manifest['sampling']['sites']
    meta=[Path(__file__),work/'checks.py',work/'checks.log',QUALIFICATION/'qualification.json',QC_QUALIFICATION/'qualification.json',
          catalog_path,batch_path,PILOT/'outer-execution.json',PILOT/'execution.json',REFERENCE/'measurement/execution.json',
          REFERENCE/'lineage.json',review_paths[0],RAW_BATCH/'batch.json',RAW_BATCH/'execution.json',command,*selected.iterdir()]
    expected={};images=[];entries=[]
    for master in sorted(masters,key=lambda m:by_id[m['detector']]['native_paf_chip']):
        identity=master['detector'];d=by_id[identity];m=transports[identity]
        selection=tomllib.loads((m/'selection.toml').read_text())
        require(selection==old_batch['remap'](reference_selection,review,identity),'Saved raw selection binding differs')
        plan,_,_,_,_=runner.prepare(source/'config/detectors/omegacam-1x1.toml',source/'config/processing/omegacam-characterization.toml',m/'selection.toml',source/'mefpp2/ins/mef/config/omegacam.paf')
        require((m/'plan.tsv').read_text()==plan,'Saved native raw plan differs')
        meta.extend((m/'selection.toml',m/'plan.tsv'))
        handoff=Path(master['product']).parent/'handoff.json';meta.append(handoff)
        for q in Path(master['qc_product']).parent.glob('*.asdf'):meta.append(q)
        meta.extend((Path(master['product']).parent/'execution.json',Path(master['product']).parent/'configuration.json'))
        for path,value in master['recipe'].get('outputs',{}).items():
            if path!=master['product']:
                require(sha(path)==value['sha256'],'Retained bias output changed: '+path);meta.append(Path(path))
        image=Path(master['product']);images.append(image)
        expected[str(image)]=master['recipe']['outputs'][str(image)]['sha256'] if identity!='ESO_CCD_#65' else None
        require(len({review['headers']['raw_bindings'][str(i)][identity] for i in range(10)})==1,'Master requires one reviewed bias HDU')
        master.update(handoff=str(handoff),configuration_detector=d['native_paf_chip']-1,
            expected_input_hdu=review['headers']['raw_bindings']['0'][identity],
            expected_bias_paths=[r['path'] for r in review['current_source_stats'][:10]],
            expected_bpm=dict(path=reference_selection['bpm']['path'],hdu=review['headers']['bpm_bindings'][identity]))
        directory=work/identity.replace('ESO_CCD_#','CCD');directory.mkdir();(directory/'native').mkdir()
        points=[p for p in population if p['detector']==identity];crop=trims[identity]['retained']
        entries.append(dict(detector=identity,configuration_detector=d['native_paf_chip']-1,master=master,
            selection=selection,population=points,active_pixels=(crop[1]-crop[0]+1)*(crop[3]-crop[2]+1),directory=str(directory),
            argv=[str(command),str(source/'mefpp2/ins/mef/config/omegacam.paf'),str(selected/(directory.name+'.toml')),
                  str(m/'plan.tsv'),str(image),'1',image.name,'5','100',str(directory/'native')]))
    shared=[Path(f['path']) for f in reference_selection['flat']]+[Path(reference_selection['bpm']['path'])]
    require(len(shared)==len(set(shared))==21,'Expected20 flats plus structural BPM')
    for image in shared:require(str(image) in references,'Missing original image baseline');expected[str(image)]=references[str(image)]
    images=shared+images;require(len(images)==53,'Expected53 selected image inputs')
    qc_manifest=work/'master-qc-inputs.json';qc_manifest.write_text(json.dumps(masters,indent=2)+'\n');meta.append(qc_manifest)
    (work/'plan.json').write_text(json.dumps(dict(controller_revision=args.revision,native_revision=NATIVE_REVISION,
        entries=entries,images=[str(p) for p in images],original65_historical_FITS_hash_available=False,
        original65_admission_basis='approved product path/HDU, retained semantic QC digest; fresh full-file hash before/after'),indent=2)+'\n')
    meta.append(work/'plan.json')
    (work/'README.md').write_text('Approved160-site OCAM engineering corrected samples. Original20 flats, five single pixels per detector, qualified scan/master service. No raw pair/RON/bias recipe rerun, noise model, fit interval, coefficients, accepted calibration, new ASDF publication or plot/HTML stage. Native TSVs are intermediate transports. Missing observations stay explicit. Only overall-execution.json establishes53-image/metadata/product preservation and all32 completion. Retain failed/partial runs; never auto-resume/overwrite. Keep while fitting/provenance references these samples; remove only after required evidence is retained. Original65 historical FITS hash was unavailable; approved path/HDU and semantic QC digest are checked and a new whole-file baseline established here.\n')
    frozen={str(p):fingerprint(p) for p in dict.fromkeys(meta)}
    report=dict(status='running',controller_revision=args.revision,native_revision=NATIVE_REVISION,detectors_processed=0,
        rows=0,results=[],fitted=False,noise_state='unavailable',fit_interval=None,ASDF_published=False,source_preservation=False)
    before_images={};products={};report_path=work/'overall-execution.json'
    def save():report_path.write_text(json.dumps(report,indent=2)+'\n')
    try:
        launch([str(PRIVATE/'bin/python'),'-B',str(work/'run.py'),'--validate-qc',str(qc_manifest),str(work/'master-qc-validation.json')],work/'master-qc.log')
        print((work/'master-qc.log').read_text(),flush=True)
        qc_result=read(work/'master-qc-validation.json');require(qc_result['status']=='complete' and len(qc_result['masters'])==32,'Incomplete master ASDF verification')
        report['master_lineage']=qc_result
        for p in (work/'master-qc-validation.json',work/'master-qc.log'):frozen[str(p)]=fingerprint(p)
        before_images=image_pass(images,expected,fingerprint,'Before');report['inputs']=before_images;save()
        for entry in entries:
            directory=Path(entry['directory']);report['current_detector']=entry['detector'];save();print('EXTRACTING:',entry['detector'],flush=True)
            launch(entry['argv'],directory/'command.log')
            require({p.name for p in (directory/'native').iterdir()}=={'samples.tsv','population.tsv','configuration.json','command.complete'},'Unexpected native output set')
            summary=admit_tables(directory/'native',entry,entry['selection'],entry['population'],entry['active_pixels'])
            files={str(p):fingerprint(p) for p in directory.rglob('*') if p.is_file()};products.update(files)
            report['results'].append(dict(detector=entry['detector'],status='native_complete_pending_overall_verification',**summary,outputs=files))
            report.update(detectors_processed=len(report['results']),rows=report['rows']+summary['rows']);save()
        require(report['detectors_processed']==32 and report['rows']==3200,'Incomplete all32 extraction')
        report.update(status='native_complete_pending_source_verification',current_detector=None)
    except Exception as error:report.update(status='failed',error=repr(error));raise
    finally:
        checks={}
        def verified_images():
            if len(before_images)!=53:return False
            after=image_pass(images,expected,fingerprint,'After');report['after_inputs']=after
            return after==before_images
        for name,check in (
            ('shared_images',verified_images),('frozen_metadata',lambda:all(fingerprint(p)==v for p,v in frozen.items())),
            ('products',lambda:all(fingerprint(p)==v for p,v in products.items())),
            ('checkout',lambda:guard['checkout'](ROOT)==before),
            ('installed_files',lambda:[guard['identity'](p) for p in protected]==installed),
            ('native_source',lambda:snapshot(source)==exported),('qc_source',lambda:qcsnapshot(qcsource)==qcexported),
            ('private_qc_runtime',lambda:prefix_identity(PRIVATE)==runtime)):
            try:checks[name]=check()
            except Exception as error:checks[name]=False;report.setdefault('preservation_errors',{})[name]=repr(error)
        if report['status']=='native_complete_pending_source_verification' and all(checks.values()):report['status']='complete_for_owner_inspection'
        else:report['status']='failed'
        report.update(preservation=checks,source_preservation=checks['shared_images'],metadata_inputs=frozen,hash_passes_per_image=2 if len(before_images)==53 else None)
        save();print('OVERALL STATUS:',report['status'],flush=True);print('PRESERVATION:',checks,flush=True)
        print('DETECTORS:',report['detectors_processed'],'ROWS:',report['rows'],flush=True);print('RETAINED SAMPLES:',work,flush=True)
    require(report['status']=='complete_for_owner_inspection','Extraction or preservation failed; retain all evidence')


if __name__=='__main__':main()
