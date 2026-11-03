"""One bounded real WFI bias exercise for owner inspection, Intel Mac only.

Reuse the accepted native/ASDF source and binary; no rebuild or installation.
A private BPM compatibility copy adds only missing PCOUNT/GCOUNT. Pixel payloads
are copied as bytes using Astropy's HDU offsets and verified independently.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import signal
import subprocess
import sys

QUALIFIED = '022cf3683fe47d4de6a7acac1e3799cb49201d40'
MAIN = '47123eedaaa31b4464238ffaaf1b690f7d2cde40'
REPO = Path('/Users/fselman/Developer/wenu-imaging')
BASE = Path('/Users/fselman/anaconda3/envs/wenu-imaging/bin/python')
OLD = Path('/Users/fselman/Software/build/wenu-imaging/mac-bpm-complete-Ia5qliwa')
QC_PYTHON = Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python')
RAW = Path('/Users/fselman/Pictures/WFI/bpm_2003-03-30')
INVENTORY = Path('/Users/fselman/Software/build/wenu-imaging/wfi-sequence-inventory-cAjokACn/inventory.json')
DETECTORS = ['WIN1.CHIP1.OUT1','WIN1.CHIP2.OUT1','WIN1.CHIP3.OUT1','WIN1.CHIP4.OUT1',
             'WIN1.CHIP8.OUT1','WIN1.CHIP7.OUT1','WIN1.CHIP6.OUT1','WIN1.CHIP5.OUT2']


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def span_digest(path, offset, length):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        f.seek(offset)
        while length:
            data = f.read(min(length, 1024*1024))
            require(bool(data), 'Unexpected end of FITS payload')
            h.update(data)
            length -= len(data)
    return h.hexdigest()


def bpm_compatibility_copy(original, destination, expected_names):
    """Only add structural IMAGE cards; no array access, rescaling or repair in place.

    Astropy owns header parsing/serialization and HDU offsets. Compare every
    unrelated card image and each padded data span after writing the new file.
    Existing checksum cards are validated on the original and recomputed on the
    copy through Astropy. Checksum values/comments may change with the header.
    """
    from astropy.io import fits
    original, destination = Path(original), Path(destination)
    original_sha = digest(original)
    spans = []
    with fits.open(original, mode='readonly', memmap=False,
                   lazy_load_hdus=True, do_not_scale_image_data=True) as hdus:
        require(len(hdus) == len(expected_names)+1, 'Unexpected BPM HDU count')
        with original.open('rb') as src, destination.open('xb') as out:
            cursor = 0
            for index, hdu in enumerate(hdus):
                info = hdu.fileinfo()
                require(info['hdrLoc'] == cursor, 'Noncontiguous/unsupported FITS framing')
                header = hdu.header.copy()
                checksum_cards={k:header[k] for k in ('CHECKSUM','DATASUM') if k in header}
                for key,verify in (('CHECKSUM',hdu.verify_checksum),('DATASUM',hdu.verify_datasum)):
                    if key in checksum_cards:
                        require(verify()==1,'Original BPM '+key+' verification failed; retain original')
                if index == 0:
                    require(header.get('SIMPLE') is True and header.get('NAXIS') == 0, 'Expected empty primary')
                else:
                    require(header.get('XTENSION', '').strip() == 'IMAGE' and
                            header.get('BITPIX') == 8 and header.get('NAXIS') == 2 and
                            header.get('EXTNAME') == expected_names[index-1] and
                            [header.get('NAXIS1'),header.get('NAXIS2')] == [2044,4097], 'Unexpected BPM image layout')
                    require('PCOUNT' not in header and 'GCOUNT' not in header, 'Only the inspected missing-card case is supported')
                    header.insert('NAXIS2', ('PCOUNT',0,'No additional image parameters'), after=True)
                    header.insert('PCOUNT', ('GCOUNT',1,'One image array'), after=True)
                before_cards = [c.image for c in hdu.header.cards]
                require([c.image for c in header.cards if c.keyword not in ('PCOUNT','GCOUNT','CHECKSUM','DATASUM')] ==
                        [c.image for c in hdu.header.cards if c.keyword not in ('PCOUNT','GCOUNT','CHECKSUM','DATASUM')], 'Unrelated header changed')
                out.write(header.tostring(sep='',endcard=True,padding=True).encode('ascii'))
                src.seek(info['datLoc'])
                remaining = info['datSpan']
                while remaining:
                    data = src.read(min(remaining,1024*1024))
                    require(bool(data), 'Unexpected end of source payload')
                    out.write(data)
                    remaining -= len(data)
                spans.append(dict(hdu=index, original_offset=info['datLoc'],
                    bytes=info['datSpan'], original_cards=before_cards, checksum_cards_before=checksum_cards,
                    payload_sha256=span_digest(original,info['datLoc'],info['datSpan'])))
                cursor = info['datLoc']+info['datSpan']
            require(cursor == original.stat().st_size, 'Unexpected trailing FITS bytes')
            out.flush()
            os.fsync(out.fileno())
    # Recompute checksums after the new structural cards are in place. The
    # public Astropy implementation reads stored bytes without loading/scaling
    # image arrays; the following independent payload hashes verify this.
    with fits.open(destination, mode='update', memmap=False, do_not_scale_image_data=True) as hdus:
        for row,hdu in zip(spans,hdus):
            if row['checksum_cards_before']:
                hdu.add_checksum(when='BPM header compatibility copy')
        hdus.flush(output_verify='exception')
    with fits.open(destination, mode='readonly', memmap=False, do_not_scale_image_data=True) as hdus:
        hdus.verify('exception')
        require(len(hdus) == len(spans), 'Copied HDU count changed')
        for row,hdu in zip(spans,hdus):
            info = hdu.fileinfo()
            require(info['datSpan'] == row['bytes'] and
                    span_digest(destination,info['datLoc'],info['datSpan']) == row['payload_sha256'], 'BPM payload bytes changed')
            require([c.image for c in hdu.header.cards if c.keyword not in ('PCOUNT','GCOUNT','CHECKSUM','DATASUM')] ==
                    [c for c in row.pop('original_cards') if c[:8].strip() not in ('PCOUNT','GCOUNT','CHECKSUM','DATASUM')], 'Copied unrelated cards changed')
            if row['checksum_cards_before']:
                require(hdu.verify_checksum()==1 and hdu.verify_datasum()==1,'Copied BPM checksum verification failed')
            row['checksum_cards_after']={k:hdu.header[k] for k in ('CHECKSUM','DATASUM') if k in hdu.header}
            row['copy_offset'] = info['datLoc']
    require(digest(original) == original_sha, 'Original BPM changed')
    return dict(original=str(original), original_sha256=original_sha, copy=str(destination),
        copy_sha256=digest(destination), action='add PCOUNT=0 and GCOUNT=1 to eight IMAGE extensions; recompute existing checksums',
        interpretation='legacy binary selection, 1=good, 0=bad; unchanged', payloads=spans)


def main():
    require((platform.system(),platform.node().split('.')[0]) == ('Darwin','MC02VV0HPHTDG'), 'Known Intel Mac only')
    require(Path(sys.executable).resolve() == BASE.resolve(), 'Use imaging guard Python')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10, 'Require niceness >=10')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True)
    a = p.parse_args()
    work = a.run.resolve(strict=True)
    require(work.parent == Path('/Users/fselman/Software/build/wenu-imaging') and
            not a.run.is_symlink() and {f.name for f in work.iterdir()} == {'run.py'}, 'Fresh private run required')
    def git(*parts):
        return subprocess.check_output(['/usr/bin/git','-C',str(REPO),*parts])
    require(git('rev-parse','HEAD').decode().strip() == MAIN and
            git('branch','--show-current').decode().strip() == 'main' and not git('status','--porcelain'), 'Protected clean main changed')
    source = OLD/'source'
    proof = json.loads((OLD/'qualification.json').read_text())
    require(proof['revision'] == QUALIFIED and proof['status'] == 'passed' and
            all(proof['preservation'].values()), 'Accepted Mac qualification missing')
    adapter = OLD/'build-c17/mefpp2/mefpp_m5'
    qualified_binaries = [json.loads(f.read_text()) for f in
        (OLD/'build-c17/mefpp2/test-work').glob('bpm-complete-*/qualification.json')]
    require(sum(r.get('status')=='passed' and r.get('adapter_sha256')==digest(adapter)
                for r in qualified_binaries)==1, 'Accepted binary bytes changed/ambiguous')
    relevant = ['Pycavi2/pycavi/pycavi/pycavi_bias_qc.py','Pycavi2/pycavi/pycavi/pycavi_qc.py',
        'Pycavi2/pycavi/config/qc-schema-1.0.0.json','mefpp2/ins/mef/config/wfi.paf',
        'Pycavi2/tests/qualify_inspection_stages.py','Pycavi2/tests/qualify_libasdf_mac.py']
    for name in relevant:
        require(digest(source/name) == proof['source_sha256'][name], 'Accepted source changed: '+name)
    guard = runpy.run_path(str(source/'Pycavi2/tests/qualify_inspection_stages.py'))
    prefix_identity = runpy.run_path(str(source/'Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    checkout = guard['checkout'](REPO)
    protected = guard['protected_paths']()
    installed = [guard['identity'](f) for f in protected]
    private = prefix_identity(QC_PYTHON.parent.parent)
    inv = json.loads(INVENTORY.read_text())
    require(inv['status']=='headers-inventoried' and inv['input_stat_unchanged'] and len(inv['files'])==22, 'Expected retained WFI inventory')
    def card(hdu,key):
        values=[c['value'] for c in hdu['cards'] if c['key']==key]
        return values[0] if len(values)==1 else None
    members=[]
    for item in inv['files']:
        asset=item['asset']
        if card(asset['hdus'][0],'ESO DPR TYPE')=='BIAS':
            require(asset['metadata']=='read' and len(asset['hdus'])==9 and
                    [h.get('extname') for h in asset['hdus'][1:]]==DETECTORS and
                    all(h['dimensions']==[2142,4128] for h in asset['hdus'][1:]), 'Raw bias layout changed')
            members.append((card(asset['hdus'][0],'DATE-OBS'),Path(asset['path'])))
    members=[f for _,f in sorted(members)]
    require(len(members)==10 and all(f.parent==RAW and f.is_file() for f in members), 'Ten explicit raw biases required')
    bpm=RAW/'WFI_BPM_1x1.fits'; historical=RAW/'WFI_MB_1x1.fits'
    fingerprints={}
    report=dict(status='running',stage='input_lock',purpose='first real WFI detector bias for owner inspection',
        driver_sha256=digest(Path(__file__)), qualified_revision=QUALIFIED, inventory=str(INVENTORY), detector=DETECTORS[0], input_hdu=1,configuration_detector=0,
        mask_good_value=1, mask_coordinates='active', scientific_acceptance=False,inputs=[str(f) for f in members],
        historical_comparison=str(historical), historical_comparison_is_independent_truth=False)
    def save():
        (work/'inspection-run.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        for index,f in enumerate([*members,bpm,historical,INVENTORY,adapter,Path(__file__),*[source/n for n in relevant]],1):
            print('Locking input/code:',index,f.name,flush=True)
            fingerprints[str(f)]=digest(f)
        report['input_sha256']=fingerprints
        report['stage']='bpm_compatibility'
        save()
        copied=work/'WFI_BPM_header_copy.fits'
        compatibility=bpm_compatibility_copy(bpm,copied,DETECTORS)
        (work/'bpm-compatibility.json').write_text(json.dumps(compatibility,indent=2)+'\n')
        fingerprints[str(copied)]=digest(copied)
        listing=work/'bias.list';listing.write_text(''.join(str(f)+'\n' for f in members))
        paf=work/'wfi.paf';paf.write_bytes((source/'mefpp2/ins/mef/config/wfi.paf').read_bytes())
        fingerprints[str(listing)]=digest(listing);fingerprints[str(paf)]=digest(paf)
        qcdir=work/'QC';qcdir.mkdir()
        output=work/'WFI_MB_CHIP1.fits'
        native=['cal','bias','--pafname',str(paf),'--bias',str(listing),
            '--detector-id',DETECTORS[0],'--expected-extname',DETECTORS[0], '--hdu','1','--config-detector','0',
            '--readout-id','WFI:normal:1x1','--bin-x','1','--bin-y','1',
            '--input-bpm',str(copied),'--bpm-hdu','1','--bpm-good-value','1','--bpm-coordinates','active',
            '--bpm-expected-extname',DETECTORS[0],'--output',str(output),'--work-dir',str(work),
            '--log-path',str(work/'native.log'),'--config-record',str(work/'configuration.json'),
            '--qc-record',str(work/'handoff.json'),'--measurements','yes','--mad','yes',
            '--ron-first','0','--ron-second','1','--high-sigma','5']
        argv=[str(QC_PYTHON),'-B',str(source/'Pycavi2/pycavi/pycavi/pycavi_bias_qc.py'),
            '--native-adapter',str(adapter),'--receipt',str(work/'execution.json'),'--qc-directory',str(qcdir),
            '--assessment-id','WFI-20030530-CHIP1:'+work.name,'--created-at',datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            '--',*native]
        report['command']=argv;report['stage']='bias_recipe';save()
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMP_NUM_THREADS='1',
            OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',TMPDIR=str(work))
        for name in ('PYTHONPATH','PYTHONHOME','LD_PRELOAD','DYLD_INSERT_LIBRARIES','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH'):
            env.pop(name,None)
        print('Running first-detector bias; log:',work/'command.log',flush=True)
        with (work/'command.log').open('x') as log:
            process=subprocess.Popen(argv,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            elapsed=0
            while True:
                try:
                    code=process.wait(timeout=30);break
                except subprocess.TimeoutExpired:
                    elapsed+=30
                    print('Still running bias recipe; elapsed:',elapsed,'s; log:',work/'command.log',flush=True)
                    if elapsed>=1800:
                        os.killpg(process.pid,signal.SIGTERM)
                        try:process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid,signal.SIGKILL);process.wait()
                        raise RuntimeError('Bias attempt exceeded 1800 seconds; retain partial artifacts')
        report['exit_status']=code
        require(code==0,'Bias recipe failed; retain command.log/native.log and execution.json')
        receipt=json.loads((work/'execution.json').read_text())
        require(receipt['status']=='complete' and receipt['qc_records_verified']==12,'Incomplete FITS/ASDF verification')
        from astropy.io import fits
        with fits.open(output,mode='readonly',memmap=False) as hdus:
            hdus.verify('exception')
            require(len(hdus)==2 and hdus[1].header.get('EXTNAME')==DETECTORS[0] and
                    [hdus[1].header['NAXIS1'],hdus[1].header['NAXIS2']]==[2044,4097],'Unexpected output detector/shape')
            (work/'product-headers.txt').write_text('\n\n'.join(h.header.tostring(sep='\n') for h in hdus))
        handoff=json.loads((work/'handoff.json').read_text())
        report.update(status='complete_for_owner_inspection',stage='complete',product=str(output),
            qc_product=receipt['qc_product'],accepted_frames=sum(f['accepted'] for f in handoff['inputs']),
            native_summary=dict(master=handoff['master'],ron=handoff['ron'],high_offset=handoff['high_offset']))
        (work/'README.txt').write_text('Owner inspection, not scientific acceptance.\n'
            'New master: WFI_MB_CHIP1.fits, image HDU 1, WIN1.CHIP1.OUT1.\n'
            'Historical comparison: '+str(historical)+' image HDU 1; not an independent truth.\n'
            'Mask: WFI_BPM_header_copy.fits, HDU 1, legacy 1=good.\n'
            'bpm-compatibility.json proves original/copy identities and unchanged padded pixel payloads.\n'
            'QC/WFI_MB_CHIP1.asdf is the product record with frozen links.\n'
            'Native numerical values: handoff.json; effective settings: configuration.json.\n'
            'Execution status: execution.json; stdout/stderr: command.log; native log: native.log.\n'
            'Inspect image structure, row/column patterns, overscan residuals and outliers; compare like detector/coordinates.\n'
            'RON uses the first two chronological raw biases before scan correction; BPM excludes bad active pixels.\n'
            'No BPM was generated, no full response/linearity characterization was performed.\n')
        print('PRODUCT:',output,'[HDU 1]',flush=True)
        print('HISTORICAL COMPARISON:',historical,'[HDU 1]',flush=True)
        print('QC:',receipt['qc_product'],flush=True)
        print('ACCEPTED FRAMES:',report['accepted_frames'],flush=True)
        print('MASTER QC:',json.dumps(handoff['master']),flush=True)
        print('RAW-PAIR RON:',json.dumps(handoff['ron']),flush=True)
    except BaseException as error:
        report.update(status='failed',error=dict(type=type(error).__name__,message=str(error)))
        raise
    finally:
        checks=dict(checkout=checkout==guard['checkout'](REPO),
            installed_files=installed==[guard['identity'](f) for f in protected],
            retained_qc_environment=private==prefix_identity(QC_PYTHON.parent.parent),
            locked_inputs_and_code=all(digest(Path(f))==h for f,h in fingerprints.items()))
        report['preservation']=checks
        if not all(checks.values()):report['status']='failed'
        save()
        print('STATUS:',report['status'],flush=True)
        print('PRESERVATION:',checks,flush=True)
        print('RETAINED RUN:',work,flush=True)
        require(all(checks.values()),'Preservation failed; retain this run')


if __name__=='__main__':
    main()
