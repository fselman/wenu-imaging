"""Python-only guard checks: preserve reviewed failure and forbid duplicate/reset attempts."""
import json
from pathlib import Path
import tempfile
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
    print('Resume guards passed; native launches: 0')


if __name__=='__main__':main()
