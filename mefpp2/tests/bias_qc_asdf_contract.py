"""Synthetic native BPM file binding -> shared ASDF QC, offline and opt-in.

No observations, installations or dependency provisioning. Independent NumPy
answers check native values; shared schema/writer/traversal checks saved records.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile



def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_records(source, handoff, records, name):
    """ASDF-only worker: no Astropy/native-image dependencies in this Python."""
    sys.path.insert(0, str(source/'Pycavi2/pycavi/pycavi'))
    import pycavi_bias_qc as bridge
    import pycavi_qc as qc
    attempts = []
    def offline(event, arguments):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'):
            attempts.append(event)
            raise RuntimeError('Network attempt in ASDF worker: '+event)
    sys.addaudithook(offline)
    tree=bridge.load_handoff(handoff)
    destination=bridge.publish_handoff(handoff,records,assessment_id='fixture:'+name,created_at='2026-11-02T00:00:00Z')
    saved=qc.read_record(destination).as_dict()
    measurements={m['name']:m for m in saved['characterization']['detectors'][0]['measurements']}
    for stage in ('master','master_unmasked'):
        for suffix,field,scale in (('mean','mean',1),('median','median',1),('stdev','stdev',1),('scaled_mad','mad',1.4826)):
            m=measurements[stage+'.'+suffix]
            if tree[stage]['mad_available'] or field!='mad':
                assert m['value']==tree[stage][field]*scale
            else: assert m['status']=='unavailable' and m['value'] is None
    if tree['ron']['pair_set']:
        assert measurements['read_noise']['value']==tree['ron']['stdev_adu']
        assert [s['file_id'] for s in measurements['read_noise']['sources']]==[tree['inputs'][i]['path'] for i in (0,1)]
        assert measurements['read_noise']['definition']['region']['correction']=='none'
    else:
        assert measurements['read_noise']['status']=='unavailable'
    assert saved['extensions']['bias']['high_offset']['locations']==tree['high_offset']['locations']
    leaf=qc.read_record(records/'bias0.asdf').as_dict()
    scan={m['name']:m for m in leaf['characterization']['detectors'][0]['measurements']}
    assert scan['overscan.mean']['definition']['region']['detector_bpm']['status']=='not_applicable'
    assert scan['scan_correction.median']['value']==tree['inputs'][0]['scan_correction']['median']
    assert scan['scan_correction.stdev']['definition']['sample_count']==9
    expected_records=5 if tree['bpm']['selected'] else 4
    assert len(list(qc.traverse_records(destination,qc_root=records)))==expected_records
    if tree['bpm']['selected']:
        assert saved['inputs'][-1]['file_id']==tree['bpm']['path']
        assert saved['extensions']['bias']['input_roles'][-1]=='bpm'
    assert all(p.read_bytes().startswith(b'#ASDF') and b'#ASDF_STANDARD 1.6.0' in p.read_bytes()[:150] for p in records.glob('*.asdf'))
    assert all(i['participation']['status']=='used' for i in saved['inputs'])
    hashes={p.name:digest(p) for p in records.iterdir()}
    try: bridge.publish_handoff(handoff,records,assessment_id='retry',created_at='2026-11-02T00:00:00Z')
    except qc.QcError: pass
    else: raise AssertionError('ASDF conflict accepted')
    assert hashes=={p.name:digest(p) for p in records.iterdir()}
    moved=records.parent/'moved QC';shutil.copytree(records,moved)
    assert len(list(qc.traverse_records(moved/'bias.asdf',qc_root=moved)))==expected_records
    assert not attempts
    print('PASS: ASDF1.6 values/origins/links/locations, optional values, conflicts and relocation',name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,required=True)
    for name in ('adapter','work-parent','asdf-python','handoff','qc-directory'):
        parser.add_argument('--'+name,type=Path)
    parser.add_argument('--verify-asdf',action='store_true')
    parser.add_argument('--profile')
    args = parser.parse_args()
    source = args.source_root.resolve(strict=True)
    if args.verify_asdf:
        verify_records(source,args.handoff,args.qc_directory,args.profile)
        return
    import numpy as np
    from astropy.io import fits
    from prepare_integrated_campaign_fixture import prepare
    assert args.adapter and args.work_parent and args.asdf_python
    work = Path(tempfile.mkdtemp(prefix='bias-qc-asdf-', dir=args.work_parent)).resolve()
    print('RETAINED BIAS QC RUN:', work, flush=True)
    sys.path.insert(0, str(source/'Pycavi2/pycavi/pycavi'))
    import pycavi_bias_qc as bridge
    import pycavi_qc as qc
    attempts = []
    def offline(event, arguments):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'):
            attempts.append(event)
            raise RuntimeError('Network attempt in bias QC contract: '+event)
    sys.addaudithook(offline)
    report = dict(status='running', profiles=[], commands=[], network_attempts=attempts,
                  scope='tiny synthetic native file-to-ASDF; no observational/scientific/installation acceptance')
    def save():
        (work/'qualification.json').write_text(json.dumps(report, indent=2)+'\n')
    def run(label, argv, good=True):
        log = work/(label+'.log')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', E_VERBOSE='0', E_DEBUG='0')
        with log.open('x') as stream:
            result = subprocess.run(list(map(str, argv)), cwd=work, env=env,
                stdout=stream, stderr=subprocess.STDOUT, timeout=120)
        report['commands'].append(dict(label=label, exit_status=result.returncode, log=str(log), sha256=digest(log))); save()
        assert result.returncode >= 0 and (result.returncode == 0) == good, (label,log.read_text()[-6000:])
    try:
        # Preparation: tiny 18x9 raw planes and 9x9 active area, known defects,
        # row-varying pedestals and a scan outlier unrelated to detector BPM.
        raw = work/'input-files'; fixture = prepare(raw, source)
        text = (source/'mefpp2/ins/mef/config/omegacam.paf').read_text()
        for key,value in dict(fixture['synthetic_paf_overrides'], **{'MEF.BIAS.KAPPA1':10}).items():
            text,n = re.subn(r'^'+re.escape(key)+r'\s+[^;\n]*;',key+' '+str(value)+';',text,flags=re.M)
            assert n == 1
        paf=work/'bias.paf'; paf.write_text(text)
        members=[raw/f'bias{i}.fits' for i in range(3)]
        arrays=[]
        yy,xx=np.indices((9,18))
        for i,path in enumerate(members):
            data=(100+(i+1)*yy).astype(np.float32)
            data[:,:9]+=20+i+xx[:,:9]+2*yy[:,:9]
            data[1,2]+=1000
            data[:,9]+=1000
            with fits.open(path,mode='update',memmap=False) as hdus:
                hdus[2].data[:]=data
            arrays.append(data.copy())
        listing=work/'bias.list'; listing.write_text('\n'.join(map(str,members))+'\n')
        good=np.ones((9,9),dtype=np.uint8);good[1,2]=0
        active=work/'active mask.fits';fits.PrimaryHDU(good).writeto(active)
        raw_encoded=np.ones((9,18),dtype=np.int16)
        raw_encoded[:,:9]=1-good  # 0=good, 1=bad; all scan positions labelled bad.
        raw_mask=work/'raw mask.fits'
        fits.HDUList([fits.PrimaryHDU(),fits.ImageHDU(raw_encoded,name='MASK')]).writeto(raw_mask)
        invalid=work/'nonbinary.fits';bad=good.copy();bad[0,0]=2;fits.PrimaryHDU(bad).writeto(invalid)
        fractional=work/'float mask.fits';fits.PrimaryHDU(good.astype(np.float32)).writeto(fractional)
        wrong=work/'wrong geometry.fits';fits.PrimaryHDU(good[:8]).writeto(wrong)
        immutable=[*members,listing,paf,active,raw_mask,invalid,fractional,wrong]
        before={str(p):digest(p) for p in immutable}
        signals=[]
        def argv(directory, mask, coordinates='active', hdu=0, good_value=1, mad='yes', pair=True):
            directory.mkdir()
            command=[args.adapter,'cal','bias','--pafname',paf,'--bias',listing,
                '--detector-id','explicit-B','--hdu','2','--config-detector','1',
                '--readout-id','synthetic-readout','--bin-x','1','--bin-y','1',
                '--input-bpm',mask or 'omitted','--output',directory/'bias.fits','--work-dir',directory,
                '--log-path',directory/'native.log','--config-record',directory/'config.json',
                '--qc-record',directory/'handoff.json','--measurements','yes','--mad',mad]
            if mask:
                command+=['--bpm-hdu',str(hdu),'--bpm-good-value',str(good_value),'--bpm-coordinates',coordinates]
            if pair: command+=['--ron-first','0','--ron-second','1']
            return command
        # Processing: actual C17 layout loader, Eclipse mask/statistics, bias
        # template and FITS publisher; both encodings and scan-independent BPM.
        for name,mask,coordinates,hdu,good_value in (
            ('active',active,'active',0,1),('raw',raw_mask,'raw',1,0),('omitted',None,'active',0,1)):
            directory=work/name
            command=argv(directory,mask,coordinates,hdu,good_value)
            if name=='raw': command+=['--bpm-expected-extname','MASK']
            run(name,command)
            tree=bridge.load_handoff(directory/'handoff.json')
            selected=good.astype(bool) if mask else np.ones((9,9),bool)
            delta=(arrays[0]-arrays[1])[:,:9][selected].astype(np.float64)
            expected=np.std(delta,ddof=1)/np.sqrt(2)
            assert abs(tree['ron']['stdev_adu']-expected)<1e-10
            med=np.median(delta); mad=np.median(np.abs(delta-med))*1.4826/np.sqrt(2)
            assert abs(tree['ron']['mad_adu']-mad)<1e-10
            expected_count=80 if mask else 81
            assert tree['inputs'][0]['raw_active']['valid_pixels']==expected_count
            for i, member in enumerate(tree['inputs']):
                correction=arrays[i][:,9:].mean(axis=1,dtype=np.float64).astype(np.float32)
                assert abs(member['scan_correction']['median']-np.median(correction))<1e-5
                assert abs(member['scan_correction']['stdev']-np.std(correction.astype(np.float64),ddof=1))<1e-6
                corrected=arrays[i][:,:9]-correction[:,None]
                for stage,values in (('raw_active',arrays[i][:,:9][selected]),('corrected_active',corrected[selected])):
                    values=values.astype(np.float64)
                    stats=member[stage]
                    assert abs(stats['mean']-values.mean())<1e-8
                    assert abs(stats['median']-np.median(values))<1e-8
                    assert abs(stats['stdev']-values.std(ddof=1))<1e-6
                    assert abs(stats['mad']-np.median(abs(values-np.median(values))))<1e-8
                assert member['overscan']['bpm_supplied']==0 and member['overscan']['bpm_excluded']==0
                assert member['overscan']['valid_pixels']==81
            if mask:
                assert tree['high_offset']['count']==1 and tree['high_offset']['locations']==[[3,2]]
            with fits.open(directory/'bias.fits',memmap=False) as hdus:
                signal=hdus[1].data.copy(); signals.append(signal)
                assert signal.shape==(9,9)
                values=signal[selected].astype(np.float64)
                assert abs(tree['master']['mean']-values.mean())<1e-10
                assert abs(tree['master']['stdev']-values.std(ddof=1))<1e-6
                assert tree['master']['median']==np.median(values)
            # Mapping/persistence: only existing common builder/schema/writer;
            # round-trip every descriptor and traverse frozen input references.
            records=directory/'QC';records.mkdir()
            run(name+'-asdf',[args.asdf_python,'-B',Path(__file__).resolve(),
                '--verify-asdf','--source-root',source,'--handoff',directory/'handoff.json',
                '--qc-directory',records,'--profile',name])
            report['profiles'].append(name);save()
        # Same correction/stack pixels with raw, active or omitted BPM: scans
        # are unaffected; all three frames accepted despite active defects.
        assert np.array_equal(signals[0],signals[1]) and np.array_equal(signals[0],signals[2])
        # Optional estimators/pair produce unavailable values, not fabricated 0.
        directory=work/'optional';run('optional',argv(directory,active,mad='no',pair=False))
        records=directory/'QC';records.mkdir()
        run('optional-asdf',[args.asdf_python,'-B',Path(__file__).resolve(),
            '--verify-asdf','--source-root',source,'--handoff',directory/'handoff.json',
            '--qc-directory',records,'--profile','optional'])
        # Negative native binding controls fail before publishing any FITS.
        for label,mask,coordinates,hdu,good_value in (
            ('nonbinary',invalid,'active',0,1),('float',fractional,'active',0,1),
            ('geometry',wrong,'active',0,1),('wrong-hdu',raw_mask,'raw',0,0),
            ('polarity',active,'active',0,2),('wrong-extname',raw_mask,'raw',1,0)):
            directory=work/label
            command=argv(directory,mask,coordinates,hdu,good_value)
            if label=='wrong-extname': command+=['--bpm-expected-extname','OTHER']
            run(label,command,good=False)
            assert not (directory/'bias.fits').exists()
        # Malformed/partial transport and contradictory scan masking must fail
        # before any canonical records are published.
        original=json.loads((work/'active/handoff.json').read_text())
        for label,mutate in (
            ('failed',lambda t:t.update(status='failed')),
            ('counts',lambda t:t['master'].update(valid_pixels=1)),
            ('scan-bpm',lambda t:t['inputs'][0]['overscan'].update(bpm_supplied=1)),
            ('pair',lambda t:t['ron'].update(second=0)),
            ('locations',lambda t:t['high_offset'].update(locations=[[999,999]])),
            ('configuration',lambda t:t.update(configuration={'tampered':True}))):
            broken=deepcopy(original);mutate(broken)
            path=work/(label+'-handoff.json');path.write_text(json.dumps(broken))
            records=work/(label+'-QC');records.mkdir()
            try: bridge.publish_handoff(path,records,assessment_id=label,created_at='2026-11-02T00:00:00Z')
            except qc.QcError: pass
            else: raise AssertionError('Malformed transport accepted: '+label)
            assert not list(records.iterdir())
        assert before=={str(p):digest(p) for p in immutable} and not attempts
        report['status']='passed'
        print('PASS: raw/active/omitted BPM, explicit polarity/HDU, electronic scan independence, raw RON, ASDF1.6 values/origins/links/locations, optional and failure controls')
    finally:
        save()


if __name__=='__main__':
    main()
