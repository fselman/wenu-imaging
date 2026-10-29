"""Read-only F4 receipt: all archived inputs/products/logs, no native launch."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'mefpp2/tests'))
from qualify_integrated_repeat_mac import cycles,TESTED,F3_SHA
from integrated_campaign_products import verify,file_hash
from qualify_integrated_campaign_mac import comparable


def inspect(root,repo):
    manifest=json.loads((root/'transfer-manifest.json').read_text())
    assert len(manifest['files'])==421
    for name,h in manifest['files'].items():assert file_hash(root/name)==h,name
    work=root/'F4-repeat';r=json.loads((work/'run-provenance.json').read_text())
    assert r['source']==dict(commit='b93ffda7955ccf1b71063f37537125431e62be4d',dirty=False)
    assert r['engine_tested_source']==dict(commit=TESTED,dirty=False)
    assert r['previous_attempt']['sha256']==F3_SHA
    assert r['status']=='F4-passed-awaiting-review' and r['execution_complete']
    assert [r[k] for k in ('planned_launches_consumed','retest_launches_consumed','native_launches_consumed','correction_rounds_consumed')]==[17,10,27,2]
    for key in ('protected_files_unchanged','previous_evidence_unchanged','fixture_inputs_unchanged','fixture_reports_unchanged','checkout_unchanged'):assert r[key],key
    assert len(r['commands'])==1 and r['commands'][0]['native'] and r['commands'][0]['exit_status']==0
    log=work/'F4-repeat.log';assert file_hash(log)==r['commands'][0]['log_sha256']
    states=cycles(log.read_text())
    old=json.loads((repo/'docs/developer/fixtures/mac-integrated-f3-inspected-2026-10-28/v2.5-cube-allocation-run-provenance.json').read_text())
    assert r['binary_sha256']==old['binary_sha256']['instrumented']
    info=json.loads((root/'qualified-build-info.json').read_text())
    prior=json.loads((repo/'docs/developer/fixtures/mac-integrated-f3-inspected-2026-10-28/v2.5-cube-allocation-build-c17-instrumented-build-info.json').read_text())
    assert info==prior
    assert [c['cycle'] for c in r['cases']]==list(range(11))
    assert r['warmup_cycles']==1 and r['measured_cycles']==10 and r['detailed_observation_cycles']==[0,1,2,10]
    accepted=old['cases'][1]
    expected={k:v for k,v in accepted['input_sha256'].items() if k!='run-provenance.json'}
    for c,state in zip(r['cases'],states):
        directory=work/('cycle-%02d'%c['cycle'])
        assert c['status']=='passed' and c['input_sha256']==expected
        assert file_hash(directory/'run-provenance.json')==c['fixture_report_sha256']
        products=verify(directory,c['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
        assert products==c['products'] and comparable(products)==comparable(accepted['products'])
        clean={k:state['diagnostics']['accounting'][k] for k in ('process-start','after-purge','after-second-purge')}
        assert clean==c['cleaned_accounting']
        if c['cycle'] in (0,1,2,10):assert json.loads(json.dumps(state['diagnostics']))==c['diagnostics']
    return dict(status='accepted-bounded-F4',files_verified=421,native_processes=1,warmup_cycles=1,measured_cycles=10,exact_products_verified=66,ordered_detector_arrays_verified=132,post_purge_resources='zero in all eleven cycles; stable descriptors within/across cycles',planned_launches=17,retest_launches=10,total_launches=27,general_rounds=2,engine_source=TESTED,report_sha256=file_hash(work/'run-provenance.json'),log_sha256=file_hash(log),limitations=['Instrumented tiny repeat, not repeated external leaks or scientific acceptance','Final Mac C90 build, compact Chapman C17/C90 and owner review remain pending; #116 unresolved'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',type=Path,required=True);parser.add_argument('--result',type=Path,required=True);args=parser.parse_args()
    result=inspect(args.evidence,Path(__file__).resolve().parents[4]);args.result.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
