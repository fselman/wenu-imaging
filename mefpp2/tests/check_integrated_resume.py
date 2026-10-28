"""Python-only guard checks: preserve reviewed failure and forbid duplicate/reset attempts."""
import json
from pathlib import Path
import tempfile
from copy import deepcopy
from unittest.mock import patch
from qualify_integrated_campaign_mac import begin_attempt,save
from integrated_campaign_products import file_hash


def main():
    with tempfile.TemporaryDirectory(prefix='integrated-resume-check-') as temp:
        parent=Path(temp);old=parent/'mac-stage2-integrated-du1sqj06';old.mkdir()
        root=old/'F1-ordinary';root.mkdir();raw=root/'input.fits';raw.write_bytes(b'preserved input')
        log=old/'F1-ordinary.log';log.write_text('preserved log\n')
        report=old/'run-provenance.json';pointer=parent/'stage2-integrated-active-campaign.json'
        record=dict(source=dict(commit='fa2e5c2f508e18d18981b8e987b86cc4a411c1df'),status='stopped',
                    execution_complete=False,native_launches_consumed=1,correction_rounds_consumed=0,
                    protected_sha256={},protected_files_unchanged=True,checkout_unchanged=True,raw_files_preserved=True,
                    commands=[dict(log=str(log),log_sha256=file_hash(log))],cases=[dict(fixed_row='F1',lane='ordinary',
                    status='failed',exit_status=0,directory=str(root),input_sha256={'input.fits':file_hash(raw)},
                    findings=['Known-answer array differs: CALIB.MASTER_DOME_FLAT extension 2'])])
        save(report,record);save(pointer,dict(report=str(report)));before=report.read_bytes()
        # Reject a fresh campaign reset when the existing pointer is present.
        try:begin_attempt(parent,pointer,'corrected',{})
        except FileExistsError:pass
        else:raise AssertionError('Campaign reset accepted')
        # Reject altered original evidence before reserving the correction directory.
        log.write_text('changed\n')
        try:begin_attempt(parent,pointer,'corrected',{},report)
        except RuntimeError as error:assert 'original log changed' in str(error)
        else:raise AssertionError('Changed original log accepted')
        log.write_text('preserved log\n')
        # Accept only the reviewed first failure, preserving its bytes and counters.
        work,previous=begin_attempt(parent,pointer,'corrected',{},report)
        assert work==old/'correction-round-1'
        assert previous['planned_launches']==1 and previous['correction_round']==1
        assert previous['input_sha256']==record['cases'][0]['input_sha256']
        assert report.read_bytes()==before
        # A duplicate retry cannot overwrite the reserved correction directory.
        try:begin_attempt(parent,pointer,'corrected',{},report)
        except FileExistsError:pass
        else:raise AssertionError('Duplicate correction accepted')
        save(pointer,dict(report=str(work/'run-provenance.json')))
        try:begin_attempt(parent,pointer,'corrected',{},report)
        except RuntimeError as error:assert 'already advanced' in str(error)
        else:raise AssertionError('Advanced campaign accepted old retry')
        # Final round: one failed diagnostic plus one successful workflow smoke.
        second=work/'run-provenance.json'
        r2=deepcopy(record);r2['source']['commit']='f0242b24aa4ebe54171287f3439902df8cc6f576'
        ordinary=deepcopy(record['cases'][0]);ordinary.update(status='passed',findings=[],products={})
        instrumented=deepcopy(ordinary);instrumented.update(lane='instrumented',status='failed',
            findings=['Live tracked resources at after-purge','Live tracked resources at after-second-purge'])
        r2.update(cases=[ordinary,instrumented],native_launches_consumed=3,planned_launches_consumed=2,
            retest_launches_consumed=1,correction_rounds_consumed=1,
            previous_attempt=dict(report=str(report),sha256=file_hash(report)))
        save(second,r2);save(pointer,dict(report=str(second)));second_bytes=second.read_bytes()
        # Product-reader behavior is independently checked; mock only its guard result here.
        with patch('qualify_integrated_campaign_mac.verify',return_value={}):
            final,prior=begin_attempt(parent,pointer,'final-correction',{},second)
        assert final==old/'correction-round-2' and prior['correction_round']==2
        assert prior['planned_launches']==2 and prior['retest_launches']==1 and prior['native_launches']==3
        assert prior['retest_labels']==['F1-ordinary','F1-instrumented']
        assert second.read_bytes()==second_bytes and report.read_bytes()==before
        third=final/'run-provenance.json';save(third,dict(cases=[]));save(pointer,dict(report=str(third)))
        try:begin_attempt(parent,pointer,'unapproved-third',{},third)
        except RuntimeError as error:assert 'no third correction' in str(error)
        else:raise AssertionError('Third repair round accepted')
        # v2.2 is a separate explicit one-use exception, not a third general round.
        r3=deepcopy(r2);r3['source']['commit']='3e60e8cbf198bd786dd1929e48e60f5c066be854'
        r3.update(native_launches_consumed=5,retest_launches_consumed=3,correction_rounds_consumed=2,
            previous_report_unchanged=True,previous_attempt=dict(report=str(second),sha256=file_hash(second)))
        state=dict(pointers=4,bytes=32,mapped_files=0,mapped_references=0,swap_bytes=0)
        r3['cases'][1]['diagnostics']=dict(accounting={'after-purge':state,'after-second-purge':state})
        save(third,r3);save(pointer,dict(report=str(third)))
        with patch('qualify_integrated_campaign_mac.verify',return_value={}):
            exception,prior=begin_attempt(parent,pointer,'bias-qc-only',{},third,True)
        assert exception==old/'v2.2-bias-qc' and prior['correction_round']==2
        assert prior['approved_exception']=='v2.2-bias-qc'
        assert prior['planned_launches']==2 and prior['retest_launches']==3 and prior['native_launches']==5
        with patch('qualify_integrated_campaign_mac.verify',return_value={}):
            try:begin_attempt(parent,pointer,'duplicate-exception',{},third,True)
            except FileExistsError:pass
            else:raise AssertionError('Duplicate exception accepted')
        # A different residual does not qualify for this narrow authorization.
        bad=deepcopy(r3);bad['cases'][1]['diagnostics']['accounting']['after-purge']['bytes']=40
        save(third,bad)
        try:begin_attempt(parent,pointer,'different-failure',{},third,True)
        except RuntimeError as error:assert 'reviewed F1 failure' in str(error)
        else:raise AssertionError('Unreviewed residual accepted')
    print('Resume guards passed; native launches: 0')


if __name__=='__main__':main()
