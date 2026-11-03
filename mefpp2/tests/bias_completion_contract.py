"""One-command bias completion: real native FITS plus common ASDF and receipts.

Synthetic fixtures only. Reuse an independently qualified C17 adapter; this tests
new orchestration, not another native numerical or dependency qualification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from astropy.io import fits
import numpy as np
from prepare_integrated_campaign_fixture import prepare
from config_toml_contract import render_snapshot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-root', 'adapter', 'asdf-python', 'work-parent'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    source = args.source_root.resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix='bias-complete-', dir=args.work_parent)).resolve()
    print('RETAINED COMPLETION RUN:', work, flush=True)
    report = dict(status='running', commands=[], adapter=str(args.adapter), adapter_sha256=sha(args.adapter),
                  purpose='one-command native FITS plus ASDF completion/failure boundaries', cases=[])
    def save():
        (work/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
    try:
        # Preparation: existing tiny fixture/config scaffolding, no new estimator.
        raw=work/'inputs'; fixture=prepare(raw,source)
        paf=work/'bias.paf'
        text=(source/'mefpp2/ins/mef/config/omegacam.paf').read_text()
        for key,value in dict(fixture['synthetic_paf_overrides'],**{'MEF.BIAS.KAPPA1':10}).items():
            text,n=re.subn(r'^'+re.escape(key)+r'\s+[^;\n]*;',key+' '+str(value)+';',text,flags=re.M)
            assert n==1
        paf.write_text(text)
        inputs=[raw/f'bias{i}.fits' for i in range(3)]
        listing=work/'bias.list';listing.write_text('\n'.join(map(str,inputs))+'\n')
        mask=work/'mask.fits';good=np.ones((9,9),dtype=np.uint8);good[1,2]=0
        fits.PrimaryHDU(good).writeto(mask)
        immutable=[*inputs,paf,listing,mask];before={str(p):sha(p) for p in immutable}
        script=source/'Pycavi2/pycavi/pycavi/pycavi_bias_qc.py'
        def run(name,config,*,selected=False,fail=None):
            directory=work/name;directory.mkdir();qcdir=directory/'QC';qcdir.mkdir()
            receipt=directory/'execution.json'
            native=['cal','bias','--config' if config.suffix=='.toml' else '--pafname',str(config),
                '--bias',str(listing),'--detector-id','explicit-B','--hdu','99' if fail=='native' else '2',
                '--config-detector','1','--readout-id','synthetic-readout','--bin-x','1','--bin-y','1',
                '--input-bpm',str(mask) if selected else 'omitted','--output',str(directory/'bias.fits'),
                '--work-dir',str(directory),'--log-path',str(directory/'native.log'),
                '--config-record',str(directory/'config.json'),'--qc-record',str(directory/'handoff.json'),
                '--measurements','yes','--mad','yes','--ron-first','0','--ron-second','1']
            if selected:
                native+=['--bpm-hdu','0','--bpm-good-value','1','--bpm-coordinates','active']
            sentinel=None
            if fail=='qc': sentinel=qcdir/'bias0.asdf'
            if fail=='preflight': sentinel=directory/'bias.fits'
            if fail=='receipt': sentinel=receipt
            if sentinel: sentinel.write_bytes(b'protected earlier attempt\n')
            protected=sha(sentinel) if sentinel else None
            command=[str(args.asdf_python),'-B',str(script),'--native-adapter',str(args.adapter),
                '--receipt',str(receipt),'--qc-directory',str(qcdir),'--assessment-id','fixture:'+name,
                '--created-at','2026-11-02T00:00:00Z','--',*native]
            log=directory/'command.log'
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
            with log.open('x') as stream:
                result=subprocess.run(command,cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
            report['commands'].append(dict(name=name,argv=command,exit_status=result.returncode,log=str(log),sha256=sha(log)));save()
            assert result.returncode>=0 and (result.returncode==0)==(fail is None),log.read_text()[-8000:]
            if sentinel: assert sha(sentinel)==protected
            # Verification: complete is emitted only for the whole recipe; native
            # or QC failure retains truthful phase/state and completed FITS.
            if fail=='receipt':
                assert not (directory/'bias.fits').exists() and not (directory/'native.log').exists()
            else:
                evidence=json.loads(receipt.read_text())
                assert evidence['adapter_sha256']==report['adapter_sha256']
                assert evidence['completion_code_sha256']==sha(script)
                if fail is None:
                    assert evidence['status']=='complete' and evidence['stage']=='complete'
                    assert evidence['native_exit_status']==0 and evidence['qc_records_verified']==(5 if selected else 4)
                    assert Path(evidence['qc_product']).is_file() and len(evidence['qc_record_digest'])==64
                    assert 'BIAS_RECIPE complete' in log.read_text()
                    assert len(list(qcdir.glob('*.asdf')))==(5 if selected else 4)
                    with fits.open(directory/'bias.fits',memmap=False) as hdus:
                        assert hdus[1].data.shape==(9,9) and np.array_equal(hdus[1].data,np.zeros((9,9)))
                else:
                    assert evidence['status']=='failed' and evidence['stage']==fail
                    assert 'BIAS_RECIPE complete' not in log.read_text() and not (qcdir/'bias.asdf').exists()
                    if fail=='native': assert evidence['native_exit_status']!=0 and not (directory/'bias.fits').exists()
                    if fail=='qc': assert evidence['native_exit_status']==0 and (directory/'bias.fits').is_file()
                    if fail=='preflight': assert evidence['native_exit_status'] is None and not (directory/'native.log').exists()
            report['cases'].append(name);save()
            return directory
        # Processing: the actual single command, PAF with omitted BPM then TOML
        # with existing BPM. No generation of a new BPM or scientific thresholds.
        first=run('paf',paf)
        toml=work/'bias.toml';toml.write_text(render_snapshot(json.loads((first/'config.json').read_text())))
        immutable.append(toml);before[str(toml)]=sha(toml)
        run('toml-bpm',toml,selected=True)
        # Failure boundaries: before native, native rejection, after successful
        # FITS but conflicting QC, and protected existing execution receipt.
        run('existing-output',paf,fail='preflight')
        run('missing-hdu',paf,fail='native')
        run('qc-conflict',paf,fail='qc')
        run('existing-receipt',paf,fail='receipt')
        assert before=={str(p):sha(p) for p in immutable}
        assert sha(args.adapter)==report['adapter_sha256']
        report['status']='passed'
        print('PASS: 6 bias completion cases: PAF/TOML, existing/omitted BPM, verified ASDF, preflight/native/QC failures, no overwrite or input mutation')
    finally:
        save()


if __name__=='__main__':
    main()
