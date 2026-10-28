"""Python-only controls for the one-use F2 continuation; no mefpp launch."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from astropy.io import fits
from integrated_campaign_products import file_hash
from qualify_integrated_campaign_mac import begin_bpm_filename_attempt, save, verify_bpm_filenames


def main():
    with tempfile.TemporaryDirectory() as temp:
        parent=Path(temp);campaign=parent/'mac-stage2-integrated-du1sqj06'
        old=campaign/'v2.2-bias-qc';old.mkdir(parents=True)
        repo=parent/'repo';common=repo/'mefpp2/ins/mef/common/mefp_lib.c';common.parent.mkdir(parents=True)
        original='                qfits_header_add_after(fhdr_extra,cval_prev, cval, flist->name[i], bb->bpm_frame_i_comment,NULL);'
        common.write_text('                /* Record the filename, as for bias/dome/sky provenance. */\n'+original.replace('flist->name[i], bb->bpm_frame_i_comment','get_basename(flist->name[i]), bb->bpm_frame_i_comment'))
        ancestor=None
        for index,sha in enumerate(['fa2e5c2f508e18d18981b8e987b86cc4a411c1df','f0242b24aa4ebe54171287f3439902df8cc6f576','3e60e8cbf198bd786dd1929e48e60f5c066be854']):
            path=campaign/('ancestor-%d.json'%index)
            save(path,dict(source=dict(commit=sha),previous_attempt=ancestor))
            ancestor=dict(report=str(path),sha256=file_hash(path))
        cases=[];commands=[]
        for row,lane in [('F1','ordinary'),('F1','instrumented'),('F1','leaks'),('F2','ordinary')]:
            root=old/(row+'-'+lane);root.mkdir();raw=root/'input.dat';raw.write_bytes(b'input')
            log=old/(row+'-'+lane+'.log');log.write_text('retained diagnostic')
            commands.append(dict(label=row+'-'+lane,log=str(log),log_sha256=file_hash(log)))
            case=dict(fixed_row=row,lane=lane,directory=str(root),input_sha256={'input.dat':file_hash(raw)},
                      status='passed',exit_status=0,findings=[],products={},diagnostics={})
            if row=='F2':
                case.update(status='failed',exit_status=-4,findings=['Native/tool process returned nonzero','Expected exactly six integrated FITS products; found 2'])
                for name in ('WFI_BPM_1x1.fits','WFI_MB_1x1.fits'):(root/name).write_bytes(b'partial product')
            cases.append(case)
        record=dict(source=dict(commit='92421749d8350d9b6438d7b16014555a228f2c5f'),cases=cases,commands=commands,
            status='stopped',execution_complete=False,planned_launches_consumed=4,retest_launches_consumed=5,
            native_launches_consumed=9,correction_rounds_consumed=2,bias_qc_exception_consumed=True,
            protected_sha256={},protected_files_unchanged=True,checkout_unchanged=True,raw_files_preserved=True,
            previous_report_unchanged=True,previous_attempt=ancestor)
        report=old/'run-provenance.json';pointer=parent/'stage2-integrated-active-campaign.json'
        save(report,record);save(pointer,dict(report=str(report)))
        def git(argv,**kwargs):
            if argv[1]=='diff':return 'mefpp2/ins/mef/common/mefp_lib.c\n'
            if argv[1]=='show':return original
            raise AssertionError(argv)
        def begin():return begin_bpm_filename_attempt(parent,pointer,{},report,repo,'corrected')
        # Isolate the guard unit: real FITS/product diagnostics have independent controls.
        with patch('qualify_integrated_campaign_mac.subprocess.check_output',side_effect=git), \
             patch('qualify_integrated_campaign_mac.verify',return_value={}), \
             patch('qualify_integrated_campaign_mac.diagnostic',return_value=({},[])):
            for mutate in (
                lambda r:r.update(native_launches_consumed=0),
                lambda r:r.update(planned_launches_consumed=3),
                lambda r:r.update(correction_rounds_consumed=3),
                lambda r:r['cases'][-1].update(exit_status=1),
                lambda r:r['cases'][0].update(status='failed'),
                lambda r:r.update(raw_files_preserved=False),
                lambda r:r.update(previous_attempt=None),
            ):
                bad=deepcopy(record);mutate(bad);save(report,bad)
                try:begin()
                except RuntimeError:pass
                else:raise AssertionError('Unreviewed parent accepted')
            save(report,record)
            # Changed retained logs must stop before creating a new directory.
            log=Path(commands[0]['log']);log.write_text('changed')
            try:begin()
            except RuntimeError as error:assert 'log changed' in str(error)
            else:raise AssertionError('Changed log accepted')
            log.write_text('retained diagnostic')
            approved=common.read_text();common.write_text(approved+'\n/* extra native change */\n')
            try:begin()
            except RuntimeError as error:assert 'differs from approved' in str(error)
            else:raise AssertionError('Extra native change accepted')
            common.write_text(approved)
            before=report.read_bytes();work,prior=begin()
            assert prior['retest_labels']==['F2-ordinary'] and prior['planned_launches']==4
            assert prior['retest_launches']==5 and prior['native_launches']==9
            assert len(prior['inherited_cases'])==3 and prior['correction_round']==2
            assert report.read_bytes()==before
            try:begin()
            except FileExistsError:pass
            else:raise AssertionError('Duplicate F2 retry accepted')
            save(pointer,dict(report=str(work/'run-provenance.json')))
            try:begin()
            except RuntimeError as error:assert 'already advanced' in str(error)
            else:raise AssertionError('Advanced pointer accepted')
        # Real Astropy cards: accept basenames, reject full paths or missing HDU cards.
        path=parent/'provenance.fits';inputs=['/some/input/frame.fits']
        primary=fits.PrimaryHDU();primary.header['HIERARCH ESO MPP BPM FRAME001']='frame.fits'
        fits.HDUList([primary]).writeto(path);verify_bpm_filenames(path,inputs)
        for value in ('/some/input/frame.fits','wrong.fits'):
            with fits.open(path,mode='update') as hdus:hdus[0].header['ESO MPP BPM FRAME001']=value
            try:verify_bpm_filenames(path,inputs)
            except RuntimeError:pass
            else:raise AssertionError('Bad provenance accepted')
        fits.HDUList([primary,fits.ImageHDU()]).writeto(path,overwrite=True)
        try:verify_bpm_filenames(path,inputs)
        except RuntimeError:pass
        else:raise AssertionError('Missing extension provenance accepted')
    print('F2 one-use resume and filename provenance controls passed; native launches: 0')


if __name__=='__main__':main()
