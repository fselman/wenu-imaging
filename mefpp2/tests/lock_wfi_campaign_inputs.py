"""Lock selected WFI input identities and read small pixel samples; no native processing."""
from collections import defaultdict
from datetime import datetime,timezone
import hashlib,json,re,tarfile,tempfile
from pathlib import Path
import platform,sys
import numpy as np
from astropy.io import fits


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def lock(selection, inventory_path, paf_bytes):
    # Guards and source identities: never substitute or modify a selected input.
    if platform.system()!='Darwin' or platform.node().split('.')[0]!='MC02VV0HPHTDG':
        raise RuntimeError('STOP: expected qualified Mac')
    if Path(sys.prefix).resolve()!=Path('/Users/fselman/anaconda3'):
        raise RuntimeError('STOP: unexpected Python environment')
    if digest(inventory_path)!=selection['source_inventory_sha256']:
        raise RuntimeError('STOP: original inventory identity differs')
    if hashlib.sha256(paf_bytes).hexdigest()!=selection['paf_sha256']:
        raise RuntimeError('STOP: WFI configuration identity differs')
    build=Path.home()/'Software/build/wenu-imaging'
    if not build.is_dir():raise RuntimeError('STOP: expected evidence root absent')
    work=Path(tempfile.mkdtemp(prefix='mac-integrated-wfi-input-lock-',dir=build))
    report=work/'run-provenance.json'
    record=dict(purpose=__doc__,status='running',native_execution=False,native_launches_consumed=0,
        created_utc=datetime.now(timezone.utc).isoformat(),selection=selection,
        selection_canonical_sha256=hashlib.sha256(json.dumps(selection,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        input_files={},errors=[],scientific_outputs_created=False,normal_installation_changed=False,
        preview_note='Small configured-region samples and overscan medians are readiness diagnostics, not native overscan correction or a calibrated BPM.')
    def save():
        tmp=report.with_suffix('.json.tmp');tmp.write_text(json.dumps(record,indent=2)+'\n');tmp.replace(report)
    # Retained provenance and exact configuration/list files before any raw reads.
    save();print('WORK DIRECTORY:',work,flush=True)
    (work/'mefpp.paf').write_bytes(paf_bytes)
    for kind,paths in selection['roles'].items():(work/(kind+'.list')).write_text('\n'.join(paths)+'\n')
    paf=dict(re.findall(r'^(MEF\.[A-Z0-9.]+)\s+([^;\n]+);',paf_bytes.decode(),re.M))
    def number(key):return int(float(paf[key].strip()))
    try:
        for number_done,(name,declared) in enumerate(sorted(selection['files'].items()),1):
            path=Path(name);item=dict(path=name)
            # Content hashing and stat preservation; collect every missing input in one report.
            try:
                before=path.stat()
                if (before.st_size,before.st_mtime_ns,before.st_ino)!=(declared['size'],declared['mtime_ns'],declared['inode']):
                    raise RuntimeError('Input stat identity changed since inventory')
                item['sha256']=digest(path);item['size']=before.st_size
                previews=[]
                # Small physical-pixel samples: Astropy Section avoids loading whole planes.
                with fits.open(path,mode='readonly',memmap=False,do_not_scale_image_data=False) as hdus:
                    if len(hdus)!=9:raise RuntimeError('Expected primary plus eight detector extensions')
                    for xt,extname in enumerate(selection['extension_order'],1):
                        h=hdus[xt].header
                        if h.get('EXTNAME')!=extname or (h.get('NAXIS1'),h.get('NAXIS2'))!=(2142,4128):
                            raise RuntimeError('Detector identity/geometry differs')
                        suffix='.CHIP'+str(xt)
                        cx=number('MEF.CROP.X.MIN'+suffix)-1+(number('MEF.MEDIAN.REG.X1')+number('MEF.MEDIAN.REG.X2'))//2
                        cy=number('MEF.CROP.Y.MIN'+suffix)-1+(number('MEF.MEDIAN.REG.Y1')+number('MEF.MEDIAN.REG.Y2'))//2
                        x0,x1=cx-128,cx+128;y0,y1=cy-128,cy+128
                        if x0<0 or y0<0 or x1>h['NAXIS1'] or y1>h['NAXIS2']:raise RuntimeError('Sample outside detector geometry')
                        sample=np.asarray(hdus[xt].section[y0:y1,x0:x1],dtype=np.float64)
                        lo=number('MEF.OVERSCAN.X.MIN'+suffix)-1;hi=number('MEF.OVERSCAN.X.MAX'+suffix)
                        scan=np.asarray(hdus[xt].section[y0:y1,lo:hi],dtype=np.float64)
                        if not np.isfinite(sample).all() or not np.isfinite(scan).all():raise RuntimeError('Nonfinite sampled pixels')
                        center=float(np.median(sample));overscan=float(np.median(scan))
                        previews.append(dict(extension=xt,extname=extname,raw_sample_median=center,
                            overscan_sample_median=overscan,signal_preview=center-overscan,
                            sample_region_0based=[x0,x1,y0,y1],sample_min=float(sample.min()),sample_max=float(sample.max())))
                after=path.stat()
                if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):
                    raise RuntimeError('Input changed during hash/readback')
                item.update(status='identity-locked',stat_preserved=True,detector_samples=previews)
            except Exception as error:
                item.update(status='blocked',error=str(error));record['errors'].append(dict(path=name,error=str(error)))
            record['input_files'][name]=item;save()
            print('INPUT CHECKED:',number_done,'/',selection['unique_files'],path.name,item['status'],flush=True)
        # Summarize each recipe input's measured intensity levels for the one readiness review.
        levels={}
        for kind,paths in selection['roles'].items():
            per_detector=defaultdict(list)
            for path in paths:
                for sample in record['input_files'].get(path,{}).get('detector_samples',[]):
                    per_detector[sample['extension']].append(sample['signal_preview'])
            levels[kind]={str(xt):vals for xt,vals in sorted(per_detector.items())}
        record['sampled_signal_levels']=levels
        record['all_selected_file_identities_locked']=not record['errors'] and len(record['input_files'])==selection['unique_files']
        record['status']='identity-locked-readiness-review-pending' if record['all_selected_file_identities_locked'] else 'blocked-input-lock'
        record['finished_utc']=datetime.now(timezone.utc).isoformat()
    except BaseException as error:
        record.update(status='failed',error=str(error));raise
    finally:save()
    # One compact report archive; raw FITS inputs remain at their original paths.
    archive=work/'wfi-input-lock.tar.gz'
    files=sorted(p for p in work.iterdir() if p.is_file() and p!=archive)
    with tarfile.open(archive,'x:gz') as bundle:
        for p in files:bundle.add(p,arcname=p.name)
    with tarfile.open(archive) as bundle:
        if set(bundle.getnames())!={p.name for p in files}:raise RuntimeError('Archive member mismatch')
        for p in files:
            if bundle.extractfile(p.name).read()!=p.read_bytes():raise RuntimeError('Archived input-lock report differs')
    print('STATUS:',record['status'],'ERRORS:',len(record['errors']))
    print('BPM SIGNAL PREVIEWS:',json.dumps(record['sampled_signal_levels'].get('bpm',{})))
    print('ARCHIVE:',archive);print('SHA256:',digest(archive))
    print('Native launches consumed: 0; calibration/science processing: none')
    return record


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection',type=Path,required=True)
    parser.add_argument('--inventory',type=Path,required=True)
    parser.add_argument('--paf',type=Path,required=True)
    args=parser.parse_args()
    lock(json.loads(args.selection.read_text()),args.inventory,args.paf.read_bytes())
