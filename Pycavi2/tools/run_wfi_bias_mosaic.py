"""Seven remaining WFI bias operations and lossless eight-detector packaging.

Reuse inspected CHIP1, qualified native adapter, common ASDF writer and private
BPM copy. No new estimator, dependency provisioning or installation.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import signal
import subprocess
import sys

HERE = Path(__file__).resolve()
SOURCE = HERE.parents[2]
BASELINE = runpy.run_path(str(HERE.with_name('run_wfi_bias_inspection.py')))
for _name in ('OLD','MAIN','REPO','BASE','QC_PYTHON','RAW','DETECTORS','digest','require'):
    globals()[_name] = BASELINE[_name]
FIRST = Path('/Users/fselman/Software/build/wenu-imaging/wfi-first-bias-retry-pKBFGzsm')
FIRST_QC = Path('/Users/fselman/Software/build/wenu-imaging/wfi-bias-qc-only-oibMOu8t')


def assemble(products, destination, names, shape=(4097, 2044)):
    """Package existing detector images with Astropy; verify unchanged pixels."""
    import numpy as np
    from astropy.io import fits
    require(len(products) == len(names) == 8, 'Eight ordered detector products required')
    primary = fits.PrimaryHDU()
    primary.header['INSTRUME'] = 'WFI'
    primary.header.add_history('Assembly of eight native cal bias detector products; no pixel processing.')
    hdus = fits.HDUList([primary])
    for product, name in zip(products, names):
        with fits.open(product, mode='readonly', memmap=False) as leaf:
            leaf.verify('exception')
            require(len(leaf) == 2 and leaf[1].header['EXTNAME'] == name and leaf[1].shape == shape,
                    'Detector product identity/shape mismatch')
            header = leaf[1].header.copy()
            for key in ('CHECKSUM','DATASUM'):
                header.remove(key, ignore_missing=True, remove_all=True)
            hdus.append(fits.ImageHDU(data=leaf[1].data.copy(), header=header))
    hdus.writeto(destination, overwrite=False, checksum=True)
    hdus.close()
    with fits.open(destination, mode='readonly', memmap=False) as mosaic:
        mosaic.verify('exception')
        require(len(mosaic) == 9, 'Unexpected assembled HDU count')
        for index, (product, name) in enumerate(zip(products, names), 1):
            require(mosaic[index].header['EXTNAME'] == name and
                    mosaic[index].verify_checksum() == 1 and mosaic[index].verify_datasum() == 1,
                    'Assembled identity/checksum failure')
            with fits.open(product, mode='readonly', memmap=False) as leaf:
                require(mosaic[index].data.dtype == leaf[1].data.dtype and
                        np.array_equal(mosaic[index].data, leaf[1].data, equal_nan=True),
                        'Assembly changed detector pixels or data type')


def publish_collection(product, qcroot, leaves, names, assessment):
    """Use the common record/link lifecycle; measurements stay in leaf records."""
    import pycavi_qc as qc
    file = dict(id=str(product), filename=product.name, location=str(product), kind='product',
        sha256=digest(product), observed_at=None,
        selectors=[dict(detector_id=name, hdu_index=i+1, configuration_detector=i)
                   for i,name in enumerate(names)],
        context=dict(instrument='WFI', readout_id='WFI:normal:1x1', bin_x=1, bin_y=1))
    builder = qc.QcRecipe(file=file, assessment_id=assessment,
        created_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        producer=dict(name='WFI-detector-product-assembly', version='1', source_revision='sha256:'+digest(HERE)),
        operation='cal.bias.assembly', configuration_id='sha256:'+digest(product))
    bindings=[]
    for i,(leaf,name) in enumerate(zip(leaves,names),1):
        record=qc.read_record(leaf)
        require(record.as_dict()['file']['selectors'][0]['detector_id'] == name,
                'Leaf QC detector mismatch')
        builder.add_input(record, qc_path=leaf.relative_to(qcroot).as_posix(), participation='used')
        bindings.append(dict(detector_id=name, output_hdu=i, source_hdu=1,
                             source_product=record.as_dict()['file']['location'],
                             source_qc=leaf.relative_to(qcroot).as_posix()))
    builder.add_extension('detector_assembly',dict(pixel_operation='none',bindings=bindings,
                          measurements='retained in linked detector product records'))
    return qc.write_record(builder.seal(),qcroot)


def run_logged(argv, directory):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',
             OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',TMPDIR=str(directory))
    for key in ('PYTHONPATH','PYTHONHOME','LD_PRELOAD','DYLD_INSERT_LIBRARIES','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH'):
        env.pop(key,None)
    print('RUNNING:',directory.name,'|',directory/'command.log',flush=True)
    with (directory/'command.log').open('x') as log:
        process=subprocess.Popen(argv,cwd=directory,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            for elapsed in range(30,1801,30):
                try:
                    code=process.wait(timeout=30)
                    require(code==0,'Detector operation failed; retain '+str(directory/'command.log'))
                    return
                except subprocess.TimeoutExpired:
                    print('Still running:',directory.name,'elapsed',elapsed,'s',flush=True)
            raise RuntimeError('Detector operation exceeded 1800 seconds')
        finally:
            if process.poll() is None:
                os.killpg(process.pid,signal.SIGTERM)
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL);process.wait()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args()
    require((platform.system(),platform.node().split('.')[0])==('Darwin','MC02VV0HPHTDG') and
            Path(sys.executable).resolve()==QC_PYTHON.resolve(), 'Use selected Intel Mac QC Python')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,'Require niceness >=10')
    work=args.run.resolve(strict=True)
    require(not args.run.is_symlink() and work.parent==FIRST.parent and not any(work.iterdir()),
            'Fresh empty run directly under build root required')
    guard_path=OLD/'source/Pycavi2/tests/qualify_inspection_stages.py'
    guard=runpy.run_path(str(guard_path))
    installed_snapshot=runpy.run_path(str(HERE.with_name('resume_wfi_bias_qc.py')))['installed_snapshot']
    prefix_identity=runpy.run_path(str(OLD/'source/Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    checkout=guard['checkout'](REPO)
    require(checkout['head']==MAIN and checkout['branch']=='main' and not checkout['status'], 'Protected main changed')
    installed=installed_snapshot(BASE,guard_path)
    environment=prefix_identity(QC_PYTHON.parent.parent)
    locks={}
    report=dict(status='running',scientific_acceptance=False,native_operations_planned=7,
                native_operations_started=0,reused_detector=DETECTORS[0],detectors=[])
    def save():
        (work/'mosaic-run.json').write_text(json.dumps(report,indent=2)+'\n')
    try:
        first_report=json.loads((FIRST_QC/'qc-recovery.json').read_text())
        require(first_report['status']=='complete_for_owner_inspection' and
                all(first_report['preservation'].values()),'CHIP1 QC recovery not complete/preserved')
        locks.update(first_report['locked_sha256'])
        current_qc = SOURCE/'Pycavi2/pycavi/pycavi/pycavi_qc.py'
        require(digest(current_qc) in [h for p,h in locks.items()
                if p.endswith('/Pycavi2/pycavi/pycavi/pycavi_qc.py')],
                'Common QC helper differs from actual Mac recovery-qualified bytes')
        require(locks and all(digest(p)==h for p,h in locks.items()),'Earlier locked bytes changed')
        require(digest(FIRST/'WFI_MB_CHIP1.fits')==first_report['native_product_sha256'],'Inspected CHIP1 changed')
        adapter=OLD/'build-c17/mefpp2/mefpp_m5'
        receipt=json.loads((FIRST/'execution.json').read_text())
        require(receipt['native_exit_status']==0 and digest(adapter)==receipt['adapter_sha256'],'Qualified adapter changed')
        # Only the common QC naming helper changes; native completion/schema stay accepted.
        for relative in ('Pycavi2/pycavi/pycavi/pycavi_bias_qc.py','Pycavi2/pycavi/config/qc-schema-1.0.0.json'):
            require((SOURCE/relative).read_bytes()==(OLD/'source'/relative).read_bytes(),'Unexpected completion/schema change')
        for root in (FIRST,FIRST_QC,SOURCE):
            for path in root.rglob('*'):
                if path.is_file(): locks[str(path)]=digest(path)
        report['locked_sha256']=locks;save()
        sys.path.insert(0,str(SOURCE/'Pycavi2/pycavi/pycavi'))
        import pycavi_qc as qc
        original_arguments=receipt['argv'][3:]
        require(len(original_arguments)%2==0,'Unexpected original argument structure')
        options=dict(zip(original_arguments[::2],original_arguments[1::2]))
        require(options['--detector-id']==DETECTORS[0] and options['--config-detector']=='0','Unexpected CHIP1 invocation')
        members=(FIRST/'bias.list').read_text().splitlines()
        require(len(members)==10 and all(Path(p).parent==RAW for p in members),'Unexpected raw bias list')
        from astropy.io import fits
        with fits.open(FIRST/'WFI_BPM_header_copy.fits',mode='readonly') as mask:
            require([h.header.get('EXTNAME') for h in mask[1:]]==DETECTORS,'BPM detector order changed')
        qcroot=work/'QC';qcroot.mkdir()
        copied=qcroot/'slot1';copied.mkdir()
        for path in FIRST_QC.glob('*.asdf'):
            shutil.copyfile(path,copied/path.name)
        first_leaf=copied/'WFI_MB_CHIP1.asdf'
        require(len(list(qc.traverse_records(first_leaf,qc_root=qcroot,max_records=12)))==12,'Reused QC links incomplete')
        products=[FIRST/'WFI_MB_CHIP1.fits'];leaves=[first_leaf]
        report['detectors'].append(dict(hdu=1,detector_id=DETECTORS[0],reused=True,
            product=str(products[0]),qc_product=str(first_leaf)))
        for slot,name in enumerate(DETECTORS[1:],1):
            directory=work/('slot'+str(slot+1));directory.mkdir()
            qdir=qcroot/directory.name;qdir.mkdir()
            selected=dict(options)
            output=directory/('WFI_MB_'+name.split('.')[1]+'.fits')
            selected.update({'--detector-id':name,'--expected-extname':name,'--hdu':str(slot+1),
                '--config-detector':str(slot),'--bpm-hdu':str(slot+1),'--bpm-expected-extname':name,
                '--output':str(output),'--work-dir':str(directory),'--log-path':str(directory/'native.log'),
                '--config-record':str(directory/'configuration.json'),'--qc-record':str(directory/'handoff.json')})
            native=['cal','bias',*[x for pair in selected.items() for x in pair]]
            argv=[str(QC_PYTHON),'-B',str(SOURCE/'Pycavi2/pycavi/pycavi/pycavi_bias_qc.py'),
                '--native-adapter',str(adapter),'--receipt',str(directory/'execution.json'),
                '--qc-directory',str(qdir),'--assessment-id','WFI-20030530:'+work.name+':'+name,
                '--created-at',datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'--',*native]
            report['native_operations_started']+=1;save()
            run_logged(argv,directory)
            result=json.loads((directory/'execution.json').read_text())
            require(result['status']=='complete' and result['qc_records_verified']==12,'Incomplete detector receipt')
            leaf=Path(result['qc_product'])
            require(len(list(qc.traverse_records(leaf,qc_root=qcroot,max_records=12)))==12,'Detector QC verification failed')
            products.append(output);leaves.append(leaf)
            handoff=json.loads((directory/'handoff.json').read_text())
            report['detectors'].append(dict(hdu=slot+1,detector_id=name,reused=False,product=str(output),
                product_sha256=digest(output),qc_product=str(leaf),master=handoff['master'],ron=handoff['ron'],
                accepted_frames=sum(row['accepted'] for row in handoff['inputs'])))
            save()
        mosaic=work/'WFI_MB_1x1.fits'
        assemble(products,mosaic,DETECTORS)
        destination=publish_collection(mosaic,qcroot,leaves,DETECTORS,'WFI-mosaic:'+work.name)
        records=list(qc.traverse_records(destination,qc_root=qcroot,max_records=97))
        require(len(records)==97,'Expected assembly plus eight twelve-record QC trees')
        report.update(status='complete_for_owner_inspection',product=str(mosaic),product_sha256=digest(mosaic),
                      qc_product=str(destination),qc_records_verified=len(records))
        print('PRODUCT:',mosaic,flush=True)
        print('QC:',destination,flush=True)
        for row in report['detectors']:
            print('HDU',row['hdu'],row['detector_id'],'reused' if row['reused'] else 'new',flush=True)
    except BaseException as error:
        report.update(status='failed',error=dict(type=type(error).__name__,message=str(error)))
        raise
    finally:
        checks=dict(checkout=checkout==guard['checkout'](REPO),
            installed_files=installed==installed_snapshot(BASE,guard_path),
            retained_qc_environment=environment==prefix_identity(QC_PYTHON.parent.parent),
            locked_inputs_and_artifacts=all(digest(p)==h for p,h in locks.items()))
        report['preservation']=checks
        if not all(checks.values()):report['status']='failed'
        save()
        print('STATUS:',report['status'],flush=True)
        print('PRESERVATION:',checks,flush=True)
        print('RETAINED RUN:',work,flush=True)
        require(all(checks.values()),'Preservation failed; retain this run')


if __name__=='__main__':
    main()
