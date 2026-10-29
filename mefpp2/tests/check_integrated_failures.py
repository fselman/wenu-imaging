"""Python-only F3 controls; synthetic parser records, no native recipe execution."""
from copy import deepcopy
from pathlib import Path
import json,re,tempfile
from unittest.mock import patch
from qualify_integrated_failures_mac import inject,PATCHES,failure_diagnostics,publication_parent,PUBLICATION_SEQUENCE,cube_parent,CUBE_SEQUENCE


def output(lane):
    text='INTEGRATED RESULT native_exit=1 contexts=0 destroyed=0 calibration_calls=0 bpm_calls=0 combine_calls=0 science_loads=0 live_products=0 owner_live=0 mismatch=0\n'
    for phase in ('process-start','after-driver','after-purge','after-second-purge'):
        text+='ACCOUNTING BEGIN '+phase+'\nACCOUNTING END '+phase+'\n'
    text+='DESCRIPTOR LIMIT before soft=256 hard=999 soft_unlimited=0\nDESCRIPTOR LIMIT after soft=999 hard=999 soft_unlimited=0\n'
    for prefix in ('DESCRIPTORS','CACHE DESCRIPTORS after-purge','CACHE DESCRIPTORS after-second-purge'):text+=prefix+' before=3 after=3 identity_equal=1\n'
    if lane=='leaks':text+='0 leaks for 0 total leaked bytes\n'
    return text


def main():
    zero=dict(pointers=0,bytes=0,mapped_files=0,mapped_references=0,swap_bytes=0)
    descriptors=dict(changes={'after-driver':[],'after-purge':[],'after-second-purge':[]})
    # Mock low-level observation text parsers only for these focused admission controls.
    with patch('qualify_integrated_failures_mac.allocation_state',return_value=zero),patch('qualify_integrated_failures_mac.snapshots',return_value=descriptors):
        for lane in ('instrumented','leaks'):
            text=output(lane);assert not failure_diagnostics(text,lane,'missing-list')[1]
            assert failure_diagnostics(text.replace('native_exit=1','native_exit=0'),lane,'missing-list')[1]
            assert failure_diagnostics(text.replace('owner_live=0','owner_live=1'),lane,'missing-list')[1]
            assert failure_diagnostics(text+'runtime error: null pointer\n',lane,'missing-list')[1]
            assert failure_diagnostics(text.replace('identity_equal=1','identity_equal=0'),lane,'missing-list')[1]
            assert failure_diagnostics(text,lane,'context-allocation')[1]
            assert not failure_diagnostics(text+'F3 INJECT context allocation\n',lane,'context-allocation')[1]
            assert not failure_diagnostics(text+'F3 INJECT cube allocation\n',lane,'cube-allocation')[1]
            try:failure_diagnostics(text.replace('INTEGRATED RESULT','CRASH'),lane,'missing-list')
            except RuntimeError:pass
            else:raise AssertionError('Missing native return accepted')
        assert failure_diagnostics(output('leaks').replace('0 leaks for 0','1 leaks for 8'),'leaks','missing-list')[1]
        bad=deepcopy(zero);bad['bytes']=8
        with patch('qualify_integrated_failures_mac.allocation_state',return_value=bad):assert failure_diagnostics(output('instrumented'),'instrumented','missing-list')[1]
    # Private patching is anchored, preserves the originals and rejects a second application.
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        for name,old,new in PATCHES:
            p=root/'mefpp2'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(old)
        receipt=inject(root);assert len(receipt)==2
        for name,old,new in PATCHES:assert (root/'mefpp2'/name).read_text()==new
        try:inject(root)
        except RuntimeError:pass
        else:raise AssertionError('Duplicate/changed injection anchor accepted')
    # v2.4 admits only this reviewed failure and its exhausted original counters.
    passed=dict(status='passed',exit_status=0,findings=[])
    cases=[]
    for variant,lane in [('missing-list','instrumented'),('missing-list','leaks'),('corrupt-frame','instrumented'),('corrupt-frame','leaks')]:
        case=deepcopy(passed);case.update(variant=variant,lane=lane);cases.append(case)
    cases.append(dict(variant='blocked-output',lane='instrumented',status='failed',exit_status=0,
        findings=['Native failure status not propagated'],diagnostics=dict(ownership=dict(native_exit=0)),
        partial_products={name:'hash' for name in ('science0_pre.fits','OCAM_SKYFF_S2_1x1.fits','OCAM_BPM_1x1.fits','OCAM_MFF_S2_1x1.fits','OCAM_DOMEFF_S2_1x1.fits')}))
    parent=dict(source=dict(commit='c7223105e402f197d9c0a2b7be9021ee76da7e9c'),status='stopped',execution_complete=False,
        planned_launches_consumed=11,retest_launches_consumed=6,native_launches_consumed=17,correction_rounds_consumed=2,
        cases=cases,protected_files_unchanged=True,checkout_unchanged=True,previous_evidence_unchanged=True,fixture_inputs_unchanged=True)
    publication_parent(parent)
    for mutate in (lambda r:r.update(native_launches_consumed=0),lambda r:r.update(correction_rounds_consumed=3),
                   lambda r:r['cases'][-1].update(findings=[]),lambda r:r['cases'][0].update(status='failed'),
                   lambda r:r.update(fixture_inputs_unchanged=False),lambda r:r['cases'][-1].update(partial_products={})):
        bad=deepcopy(parent);mutate(bad)
        try:publication_parent(bad)
        except RuntimeError:pass
        else:raise AssertionError('Unreviewed publication parent accepted')
    assert len(PUBLICATION_SEQUENCE)==7 and PUBLICATION_SEQUENCE[:2]==(('blocked-output','instrumented'),('publication-smoke','instrumented'))
    assert PUBLICATION_SEQUENCE[2:]==(('blocked-output','leaks'),('context-allocation','instrumented'),('context-allocation','leaks'),('cube-allocation','instrumented'),('cube-allocation','leaks'))
    # v2.5 accepts only the six-role publication attempt ending in injected UBSan.
    cube_cases=[]
    for variant,lane in PUBLICATION_SEQUENCE[:5]:
        case=deepcopy(passed);case.update(variant=variant,lane=lane);cube_cases.append(case)
    cube_cases.append(dict(variant='cube-allocation',lane='instrumented',status='failed',exit_status=86,
        findings=['Observer/tool exited nonzero (not a clean observed native failure)',
                  'Missing native return/cleanup observation (possible crash/exit)'],partial_products={}))
    cube_record=deepcopy(parent);cube_record.update(source=dict(commit='2e3969c4a1e3bc112325e7a2c7d6f8bdc7f260bb'),cases=cube_cases,
        planned_launches_consumed=15,retest_launches_consumed=8,native_launches_consumed=23,publication_exception_consumed=True)
    cube_parent(cube_record)
    for mutate in (lambda r:r.update(native_launches_consumed=0),lambda r:r.update(correction_rounds_consumed=3),
                   lambda r:r.update(publication_exception_consumed=False),lambda r:r['cases'][-1].update(exit_status=1),
                   lambda r:r['cases'][0].update(status='failed'),lambda r:r.update(fixture_inputs_unchanged=False),
                   lambda r:r['cases'][-1].update(partial_products={'unexpected.fits':'hash'})):
        bad=deepcopy(cube_record);mutate(bad)
        try:cube_parent(bad)
        except RuntimeError:pass
        else:raise AssertionError('Unreviewed cube parent accepted')
    assert CUBE_SEQUENCE==(('cube-allocation','instrumented'),('cube-smoke','instrumented'),('cube-allocation','leaks'))
    print('F3 parser/injection controls passed; native launches: 0')


if __name__=='__main__':main()
