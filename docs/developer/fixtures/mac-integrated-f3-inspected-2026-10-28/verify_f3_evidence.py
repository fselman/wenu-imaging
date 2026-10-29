"""Read-only independent F3 archive receipt; no native recipe launches."""
import argparse, hashlib, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'mefpp2/tests'))
from integrated_campaign_products import verify,file_hash
from qualify_integrated_campaign_mac import comparable,diagnostic
from qualify_integrated_failures_mac import failure_diagnostics,CASES


def inspect(root,repo):
    manifest=json.loads((root/'transfer-manifest.json').read_text());assert len(manifest['files'])==539
    for name,h in manifest['files'].items():assert file_hash(root/name)==h,name
    def local(path):return root/Path(path).relative_to(manifest['source_run'])
    attempts=('F3-failures','v2.4-publication','v2.5-cube-allocation')
    expected_sources=('c7223105e402f197d9c0a2b7be9021ee76da7e9c','2e3969c4a1e3bc112325e7a2c7d6f8bdc7f260bb','68f0a04632a63fa53c7549b02cde019112fa80f5')
    fixtures=repo/'docs/developer/fixtures'
    pre=json.loads((fixtures/'agent-integrated-f3-preparation-2026-10-28/run-provenance.json').read_text())
    pub=json.loads((fixtures/'agent-publication-repair-2026-10-28/run-provenance.json').read_text())
    cube=json.loads((fixtures/'agent-cube-allocation-repair-2026-10-28/run-provenance.json').read_text())
    source_maps=({x['path']:x['before_sha256'] for x in pre['private_points']},
                 {'ins/mef/common/mefp_lib.c':pub['native_source_sha256']['mefpp2/ins/mef/common/mefp_lib.c'],'src/iproc/cube_handling.c':pre['private_points'][1]['before_sha256']},
                 {k.removeprefix('mefpp2/'):v for k,v in cube['native_source_sha256'].items()})
    reports=[];latest_roles={};smokes=[];history=[];commands=0;native=0;builds=0
    for label,source,expected in zip(attempts,expected_sources,source_maps):
        report=json.loads((root/label/'run-provenance.json').read_text());reports.append(report)
        assert report['source']==dict(commit=source,dirty=False)
        for key in ('protected_files_unchanged','checkout_unchanged','previous_evidence_unchanged','fixture_inputs_unchanged'):assert report[key],key
        for command in report['commands']:
            assert file_hash(local(command['log']))==command['log_sha256'];commands+=1;native+=int(command['native'])
        for point in report['private_injection_points']:
            path=root/label/'source/mefpp2'/point['path'];assert file_hash(path)==point['after_sha256']
            text=path.read_text();assert text.count(point['new'])==1
            restored=text.replace(point['new'],point['old'])
            assert hashlib.sha256(restored.encode()).hexdigest()==point['before_sha256']==expected[point['path']]
        for p in (root/label).glob('build-c17-*/build-info.json'):
            info=json.loads(p.read_text());builds+=1
            assert info['source_revision']==source and str(info['c_standard'])=='17'
            assert info['system']=='Darwin' and info['osx_architectures']=='x86_64'
            assert info['qfits_memory_mode']==2 and info['qfits_max_pointers']==2000000
            if 'instrumented' in p.parent.name:
                assert '-fsanitize=address,undefined' in info['c_flags']
                symbols=(root/label/'symbols-instrumented.log').read_text();assert '__asan_' in symbols and '__ubsan_' in symbols
        for case in report['cases']:
            directory=local(case['directory'])
            for name,h in case['input_sha256'].items():assert file_hash(directory/name)==h
            for name,h in case['partial_products'].items():assert file_hash(directory/name)==h
            output=(root/label/(case['variant']+'-'+case['lane']+'.log')).read_text(errors='replace')
            history.append(dict(attempt=label,variant=case['variant'],lane=case['lane'],status=case['status'],exit=case['exit_status'],findings=case['findings']))
            if case['status']=='failed':
                if label=='F3-failures':
                    state,findings=failure_diagnostics(output,case['lane'],case['variant']);assert findings==['Native failure status not propagated']
                    assert json.loads(json.dumps(state))==case['diagnostics']
                    block=directory/'OCAM_MB_1x1.fits';assert block.is_dir() and (block/'preserve-marker.txt').read_text()=='F3 protected output blocker\n'
                    assert len(case['partial_products'])==5
                else:
                    assert label=='v2.4-publication' and case['variant']=='cube-allocation' and case['exit_status']==86
                    assert 'F3 INJECT cube allocation' in output and 'runtime error: member access within null pointer' in output and 'cube_handling.c' in output
                continue
            assert case['status']=='passed' and case['exit_status']==0 and not case['findings']
            if case['variant'].endswith('-smoke'):
                products=verify(directory,case['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B']);assert products==case['products']
                smokes.append(comparable(products));state,findings=diagnostic(output,2,case['lane'])
            else:
                state,findings=failure_diagnostics(output,case['lane'],case['variant'])
                assert not case['partial_products']
                latest_roles[(case['variant'],case['lane'])]=dict(source=source,attempt=label,native_exit=state['ownership']['native_exit'],post_purge=state['accounting']['after-second-purge'])
            assert not findings and json.loads(json.dumps(state))==case['diagnostics']
    assert commands==35 and native==14 and builds==6
    assert len(smokes)==2 and smokes[0]==smokes[1]
    assert set(latest_roles)=={(v,l) for v in CASES for l in ('instrumented','leaks')}
    assert len(history)==14 and sum(c['status']=='failed' for c in history)==2
    latest=reports[-1];assert latest['status']=='F3-passed-awaiting-review' and latest['execution_complete']
    assert [latest[k] for k in ('planned_launches_consumed','retest_launches_consumed','native_launches_consumed','correction_rounds_consumed')]==[16,10,26,2]
    for newer,older,label in zip(reports[1:],reports,attempts):
        assert newer['previous_attempt']['sha256']==file_hash(root/label/'run-provenance.json')
    return dict(status='accepted-bounded-F3',archive_sha256='facaf3e6f8aa41fda92c0e205bc696e530afb7f3fbef38ca2b9503d8362c6ebf',files_verified=539,command_logs_verified=35,build_records_verified=builds,final_fixed_roles=10,successful_smokes=2,retained_failed_attempts=2,F3_role_launches=14,total_campaign_launches=26,planned_campaign_launches=16,retests=10,general_repair_rounds=2,latest_report_sha256=file_hash(root/attempts[-1]/'run-provenance.json'),roles=[dict(variant=v,lane=l,**item) for (v,l),item in sorted(latest_roles.items())],history=history,limits=['Controlled tiny fixture and two fixed NULL points, not exhaustive allocator/I/O failure coverage','F4/final C90/compact Chapman3 C17+C90 and #116 disposition remain pending','No scientific/Phase3/full Stage 2 acceptance; qfits #125/#128 deferred'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--result',type=Path,required=True);a=p.parse_args()
    result=inspect(a.evidence,Path(__file__).resolve().parents[4]);a.result.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('roles','history')},indent=2))
