"""Python-only F3 controls; synthetic parser records, no native recipe execution."""
from copy import deepcopy
from pathlib import Path
import json,re,tempfile
from unittest.mock import patch
from qualify_integrated_failures_mac import inject,PATCHES,failure_diagnostics


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
    print('F3 parser/injection controls passed; native launches: 0')


if __name__=='__main__':main()
