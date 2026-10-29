"""F4: one qualified instrumented process, tiny warmup plus ten measured cycles."""
import argparse, json, os, platform, re, resource, subprocess, sys
from datetime import datetime,timezone
from pathlib import Path
from prepare_integrated_campaign_fixture import prepare
from integrated_campaign_products import verify,file_hash
from qualify_integrated_campaign_mac import ARGV,FROZEN,save,diagnostic,comparable

F3_SHA='404805478bb6608ca366e9599b16fdb0f622bdf5688c42769782a25174ad8aea'
TESTED='68f0a04632a63fa53c7549b02cde019112fa80f5'
CONTRACTS={**FROZEN,'native-roadmap-amendment-v2.4-2026-10-28.md':'937609ff2945d3abbdd12b382a053556f7c6e06748c37055e37d8f1f36ac3c1c',
           'native-roadmap-amendment-v2.5-2026-10-28.md':'af394c20a2f3846d3ff7886cc2ef4d90e412098f13d247384cfa691967451244'}


def cycles(output):
    """Every cycle must return and clean up; warmup defines the descriptor baseline."""
    if re.search(r'AddressSanitizer:|UndefinedBehaviorSanitizer:|runtime error:',output):raise RuntimeError('Sanitizer finding')
    begin=[int(x) for x in re.findall(r'^INTEGRATED CYCLE BEGIN (\d+)$',output,re.M)]
    end=[int(x) for x in re.findall(r'^INTEGRATED CYCLE END (\d+)$',output,re.M)]
    if begin!=list(range(11)) or end!=begin:raise RuntimeError('Incomplete/duplicate/reordered warmup or measured cycles')
    blocks=list(re.finditer(r'^INTEGRATED CYCLE BEGIN (\d+)\n(.*?)^INTEGRATED CYCLE END \1\n',output,re.M|re.S))
    if len(blocks)!=11:raise RuntimeError('Cycle log boundaries incomplete')
    results=[];baseline=None
    for block in blocks:
        index=int(block[1]);state,findings=diagnostic(block[2],2,'instrumented')
        if findings:raise RuntimeError('Cycle '+str(index)+': '+'; '.join(findings))
        cleaned=state['descriptor_snapshots']['boundaries']['after-second-purge']
        if baseline is None:baseline=cleaned
        elif cleaned!=baseline:raise RuntimeError('Cleaned descriptor baseline changed at cycle '+str(index))
        results.append(dict(cycle=index,diagnostics=state))
    return results


def parent_guard(report):
    if (report['source']!=dict(commit=TESTED,dirty=False) or report['status']!='F3-passed-awaiting-review'
        or not report['execution_complete'] or not report['cube_exception_consumed']
        or [report[k] for k in ('planned_launches_consumed','retest_launches_consumed','native_launches_consumed','correction_rounds_consumed')]!=[16,10,26,2]):
        raise RuntimeError('STOP: F3 parent/counters differ')
    if [(c['variant'],c['lane'],c['status']) for c in report['cases']]!=[
        ('cube-allocation','instrumented','passed'),('cube-smoke','instrumented','passed'),('cube-allocation','leaks','passed')]:raise RuntimeError('STOP: F3 case sequence differs')
    if any(c['findings'] for c in report['cases']):raise RuntimeError('STOP: F3 finding')
    for key in ('protected_files_unchanged','checkout_unchanged','previous_evidence_unchanged','fixture_inputs_unchanged'):
        if not report[key]:raise RuntimeError('STOP: F3 preservation finding')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    # Actual host, native source, accepted report/binary and one-use phase guards.
    if platform.system()!='Darwin' or platform.node().split('.')[0]!='MC02VV0HPHTDG':raise RuntimeError('STOP: qualified Mac required')
    if Path(sys.prefix).resolve()!=Path('/Users/fselman/anaconda3') or os.getpriority(os.PRIO_PROCESS,0)<10:raise RuntimeError('STOP: qualified Python / nice >=10 required')
    resource.setrlimit(resource.RLIMIT_CORE,(0,0));repo=Path(__file__).resolve().parents[2]
    def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
    if repo!=Path('/Users/fselman/Developer/wenu-imaging') or git('symbolic-ref','--short','HEAD')!='test/stage2-integrated-campaign' or git('status','--porcelain','--untracked-files=all'):raise RuntimeError('STOP: clean qualified checkout required')
    commit=git('rev-parse','HEAD')
    changed=git('diff','--name-only',TESTED,commit,'--','mefpp2').splitlines()
    if any(not name.startswith('mefpp2/tests/') for name in changed):raise RuntimeError('STOP: qualified native source changed')
    for name,h in CONTRACTS.items():
        if file_hash(repo/'docs/developer'/name)!=h:raise RuntimeError('STOP: frozen contract changed')
    parent=Path.home()/'Software/build/wenu-imaging';campaign=parent/'mac-stage2-integrated-du1sqj06'
    prior=campaign/'v2.5-cube-allocation/run-provenance.json'
    if file_hash(prior)!=F3_SHA:raise RuntimeError('STOP: F3 report differs from inspected receipt')
    old=json.loads(prior.read_text());parent_guard(old)
    pointer=parent/'stage2-integrated-active-campaign.json'
    if Path(json.loads(pointer.read_text())['report']).resolve()!=prior.resolve():raise RuntimeError('STOP: campaign already advanced')
    binary=prior.parent/'build-c17-instrumented/integrated_observer'
    if file_hash(binary)!=old['binary_sha256']['instrumented']:raise RuntimeError('STOP: qualified binary changed/missing')
    info=json.loads((binary.parent/'build-info.json').read_text())
    if info['source_revision']!=TESTED or str(info['c_standard'])!='17' or info['qfits_memory_mode']!=2 or info['qfits_max_pointers']!=2000000 or '-fsanitize=address,undefined' not in info['c_flags']:raise RuntimeError('STOP: binary qualification differs')
    protected=old['protected_sha256'];preserved={str(prior):F3_SHA,str(binary):old['binary_sha256']['instrumented']}
    for name,h in protected.items():
        if file_hash(Path(name))!=h:raise RuntimeError('STOP: selected installation changed')
    for command in old['commands']:
        if file_hash(Path(command['log']))!=command['log_sha256']:raise RuntimeError('STOP: qualified log changed')
        preserved[command['log']]=command['log_sha256']
    work=campaign/'F4-repeat';work.mkdir(exist_ok=False);provenance=work/'run-provenance.json'
    reference=old['cases'][1];expected_inputs={k:v for k,v in reference['input_sha256'].items() if k!='run-provenance.json'}
    record=dict(schema_version=1,fixed_row='F4',source=dict(commit=commit,dirty=False),engine_tested_source=old['source'],
        created_utc=datetime.now(timezone.utc).isoformat(),status='preparing',execution_complete=False,
        previous_attempt=dict(report=str(prior),sha256=F3_SHA),binary=str(binary),binary_sha256=old['binary_sha256']['instrumented'],
        planned_launches_consumed=16,retest_launches_consumed=10,native_launches_consumed=26,correction_rounds_consumed=2,
        planned_native_launch_limit=19,installation_performed=False,scientific_acceptance_claimed=False,
        warmup_cycles=1,measured_cycles=10,detailed_observation_cycles=[0,1,2,10],commands=[],cases=[],protected_sha256=protected)
    save(provenance,record);save(pointer,dict(report=str(provenance),source=commit));print('WORK DIRECTORY:',work,flush=True)
    try:
        # Eleven fresh tiny fixtures; no raw WFI and no extra native control launch.
        for index in range(11):
            directory=work/('cycle-%02d'%index);fixture=prepare(directory,repo)
            if fixture['input_sha256']!=expected_inputs:raise RuntimeError('STOP: fixed fixture/expectations changed')
            record['cases'].append(dict(cycle=index,directory=str(directory),input_sha256=fixture['input_sha256'],fixture_report_sha256=file_hash(directory/'run-provenance.json'),status='prepared'))
        env={k:v for k,v in os.environ.items() if not k.startswith(('S2_','Malloc','DYLD_')) and k not in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS')}
        for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
        env.update(S2_INTEGRATED_REPEAT='10',E_VERBOSE='0',E_DEBUG='0',ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=0')
        command=dict(label='F4-warmup-plus-ten',argv=[str(binary),*ARGV],cwd=str(work),native=True)
        record['commands'].append(command);record.update(status='running',planned_launches_consumed=17,native_launches_consumed=27)
        save(provenance,record);print('Running: F4 warmup + cycles 1..10 (one process)',flush=True)
        log=work/'F4-repeat.log'
        with log.open('w') as stream:code=subprocess.run(command['argv'],cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT).returncode
        command.update(exit_status=code,log=str(log),log_sha256=file_hash(log));save(provenance,record)
        if code:raise RuntimeError('STOP: observer exited nonzero: '+str(code))
        observed=cycles(log.read_text(errors='replace'))
        for case,result in zip(record['cases'],observed):
            products=verify(Path(case['directory']),case['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
            if comparable(products)!=comparable(reference['products']):raise RuntimeError('Cycle products/ordered metadata differ from accepted smoke')
            case.update(status='passed',products=products)
            state=result['diagnostics']
            case['cleaned_accounting']={k:state['accounting'][k] for k in ('process-start','after-purge','after-second-purge')}
            if case['cycle'] in (0,1,2,10):case['diagnostics']=state
            print('CYCLE',case['cycle'],'passed',flush=True)
        record.update(status='F4-passed-awaiting-review',execution_complete=True)
    except BaseException as error:record.update(status='stopped',error=str(error));print(str(error),flush=True)
    finally:
        record['protected_files_unchanged']=all(Path(p).is_file() and file_hash(Path(p))==h for p,h in protected.items())
        record['previous_evidence_unchanged']=all(Path(p).is_file() and file_hash(Path(p))==h for p,h in preserved.items())
        record['fixture_inputs_unchanged']=all((Path(c['directory'])/n).is_file() and file_hash(Path(c['directory'])/n)==h for c in record['cases'] for n,h in c['input_sha256'].items())
        record['fixture_reports_unchanged']=all(file_hash(Path(c['directory'])/'run-provenance.json')==c['fixture_report_sha256'] for c in record['cases'])
        record['checkout_unchanged']=git('rev-parse','HEAD')==commit and not git('status','--porcelain','--untracked-files=all')
        if not all(record[k] for k in ('protected_files_unchanged','previous_evidence_unchanged','fixture_inputs_unchanged','fixture_reports_unchanged','checkout_unchanged')):record['status']='stopped-preservation-finding'
        record['finished_utc']=datetime.now(timezone.utc).isoformat();save(provenance,record)
        print('PLANNED LAUNCHES:',record['planned_launches_consumed'],'/ 19; TOTAL:',record['native_launches_consumed'],'; repair rounds: 2 / 2',flush=True)
        print('STATUS:',record['status'],flush=True);print('REPORT:',provenance,flush=True)
    return 0 if record['status']=='F4-passed-awaiting-review' else 1


if __name__=='__main__':sys.exit(main())
