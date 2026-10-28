"""F3: five fixed tiny-fixture failures, ASan/UBSan then external leaks; stop on findings."""
import argparse, hashlib, io, json, os, platform, re, resource, subprocess, sys, tarfile
from pathlib import Path
from prepare_integrated_campaign_fixture import prepare
from integrated_campaign_products import file_hash
from qualify_integrated_campaign_mac import ARGV, FROZEN, save, diagnostic, comparable
from integrated_campaign_products import verify
from qualify_split_ownership import allocation_state
from descriptor_snapshots import snapshots

CASES=('missing-list','corrupt-frame','blocked-output','context-allocation','cube-allocation')
PUBLICATION_SEQUENCE=(('blocked-output','instrumented'),('publication-smoke','instrumented'),('blocked-output','leaks'),('context-allocation','instrumented'),('context-allocation','leaks'),('cube-allocation','instrumented'),('cube-allocation','leaks'))
PATCHES=(('ins/mef/common/mefp_lib.c','bb = calloc(1, sizeof(mef_bb));','bb = (getenv("S2_F3_ALLOC") != NULL && !strcmp(getenv("S2_F3_ALLOC"), "context")) ? (fprintf(stderr, "F3 INJECT context allocation\\n"), (void *)0) : calloc(1, sizeof(mef_bb));'),
         ('src/iproc/cube_handling.c','n = malloc(sizeof(cube_t)) ;','n = (getenv("S2_F3_ALLOC") != NULL && !strcmp(getenv("S2_F3_ALLOC"), "cube")) ? (fprintf(stderr, "F3 INJECT cube allocation\\n"), (void *)0) : malloc(sizeof(cube_t)) ;'))


def inject(source):
    """Patch only disposable build copies; exactly one declared allocation per case."""
    receipt=[]
    for name,old,new in PATCHES:
        p=source/'mefpp2'/name;text=p.read_text()
        if text.count(old)!=1:raise RuntimeError('STOP: injection anchor differs: '+name)
        before=file_hash(p);p.write_text(text.replace(old,new))
        receipt.append(dict(path=name,before_sha256=before,after_sha256=file_hash(p),old=old,new=new))
    return receipt


def failure_diagnostics(output,lane,variant):
    """Failure status replaces success-stage counts; cleanup/descriptor/leak gates stay exact."""
    findings=[];result={}
    rows=re.findall(r'^INTEGRATED RESULT (.+)$',output,re.M)
    if len(rows)!=1:raise RuntimeError('Missing native return/cleanup observation (possible crash/exit)')
    owner={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',rows[0])};result['ownership']=owner
    if owner['native_exit']<=0:findings.append('Native failure status not propagated')
    if owner['contexts']!=owner['destroyed'] or any(owner[k] for k in ('live_products','owner_live','mismatch')):
        findings.append('Unbalanced failure-path owners')
    labels=re.findall(r'^ACCOUNTING BEGIN (\S+)$',output,re.M)
    required={'process-start','after-driver','after-purge','after-second-purge'}
    if len(set(labels))!=len(labels) or not required.issubset(labels):raise RuntimeError('Incomplete/duplicate accounting boundaries')
    result['accounting']={label:allocation_state(output,re.escape(label)) for label in labels}
    for label in ('process-start','after-purge','after-second-purge'):
        if any(result['accounting'][label].values()):findings.append('Live tracked resources at '+label)
    result['descriptor_snapshots']=snapshots(output)
    if any(result['descriptor_snapshots']['changes'].values()):findings.append('Descriptor identity changed (#116)')
    for prefix in ('DESCRIPTORS','CACHE DESCRIPTORS after-purge','CACHE DESCRIPTORS after-second-purge'):
        values=re.findall(r'^'+prefix+r' before=(\d+) after=(\d+) identity_equal=(\d+)$',output,re.M)
        if len(values)!=1 or values[0][0]!=values[0][1] or values[0][2]!='1':findings.append('Descriptor gate failed: '+prefix)
    result['descriptor_limits']=re.findall(r'^DESCRIPTOR LIMIT (before|after) soft=(\d+) hard=(\d+) soft_unlimited=(\d+)$',output,re.M)
    if len(result['descriptor_limits'])!=2:findings.append('Missing descriptor limits')
    allocation={'context-allocation':'context','cube-allocation':'cube'}.get(variant)
    markers=re.findall(r'^F3 INJECT (context|cube) allocation$',output,re.M)
    if markers!=([allocation] if allocation else []):findings.append('Missing/unexpected allocation injection marker')
    if lane=='leaks':
        values=re.findall(r'\b(\d+) leaks? for (\d+) total leaked bytes\b',output)
        result['leaks']=values
        if values!=[('0','0')]:findings.append('External leak summary missing/nonzero')
    if 'ERROR: AddressSanitizer' in output or 'runtime error:' in output:findings.append('ASan/UBSan finding')
    return result,findings



def publication_parent(old):
    """Admit only the reviewed false-success F3 parent, never reset its budget."""
    if (old['source']['commit']!='c7223105e402f197d9c0a2b7be9021ee76da7e9c'
        or old['status']!='stopped' or old['execution_complete']
        or [old[k] for k in ('planned_launches_consumed','retest_launches_consumed','native_launches_consumed','correction_rounds_consumed')]!=[11,6,17,2]):
        raise RuntimeError('STOP: unreviewed publication parent/counters')
    expected=[('missing-list','instrumented'),('missing-list','leaks'),('corrupt-frame','instrumented'),('corrupt-frame','leaks'),('blocked-output','instrumented')]
    if [(c['variant'],c['lane']) for c in old['cases']]!=expected:raise RuntimeError('STOP: parent case order differs')
    for case in old['cases'][:4]:
        if case['status']!='passed' or case['findings'] or case['exit_status']!=0:raise RuntimeError('STOP: parent early case not passed')
    failed=old['cases'][-1]
    if (failed['status']!='failed' or failed['exit_status']!=0 or failed['findings']!=['Native failure status not propagated']
        or failed['diagnostics']['ownership']['native_exit']!=0):raise RuntimeError('STOP: not reviewed false success')
    for key in ('protected_files_unchanged','checkout_unchanged','previous_evidence_unchanged','fixture_inputs_unchanged'):
        if not old[key]:raise RuntimeError('STOP: parent preservation finding')
    if set(failed['partial_products'])!={'science0_pre.fits','OCAM_SKYFF_S2_1x1.fits','OCAM_BPM_1x1.fits','OCAM_MFF_S2_1x1.fits','OCAM_DOMEFF_S2_1x1.fits'}:
        raise RuntimeError('STOP: reviewed partial product set differs')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('compiler','sdk','cmake'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--resume-publication',action='store_true',help='Approved one-use v2.4 publication repair only')
    args=p.parse_args()
    # Actual-host/source guards and inherited successful campaign; no processing here.
    if platform.system()!='Darwin' or platform.node().split('.')[0]!='MC02VV0HPHTDG':raise RuntimeError('STOP: qualified Mac required')
    if Path(sys.prefix).resolve()!=Path('/Users/fselman/anaconda3') or os.getpriority(os.PRIO_PROCESS,0)<10:raise RuntimeError('STOP: qualified Python / nice >=10 required')
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    repo=Path(__file__).resolve().parents[2]
    def git(*a):return subprocess.check_output(['git',*a],cwd=repo,text=True).strip()
    if repo!=Path('/Users/fselman/Developer/wenu-imaging') or git('status','--porcelain','--untracked-files=all'):raise RuntimeError('STOP: clean qualified checkout required')
    if git('symbolic-ref','--short','HEAD')!='test/stage2-integrated-campaign':raise RuntimeError('STOP: wrong branch')
    commit=git('rev-parse','HEAD')
    changed=git('diff','--name-only','f5afd08fbfb35a8a50409c92352f9061c92c1f69',commit,'--','mefpp2').splitlines()
    native=[name for name in changed if not name.startswith('mefpp2/tests/')]
    allowed=['mefpp2/ins/mef/common/mefp_lib.c','mefpp2/ins/mef/common/mefp_lib.h','mefpp2/ins/mef/recipes/mefpp.c']
    if args.resume_publication:
        if native!=allowed:raise RuntimeError('STOP: repair source scope differs')
        receipt=json.loads((repo/'docs/developer/fixtures/agent-publication-repair-2026-10-28/run-provenance.json').read_text())
        if any(file_hash(repo/name)!=receipt['native_source_sha256'][name] for name in allowed):raise RuntimeError('STOP: repair source identity differs')
        if file_hash(repo/'docs/developer/native-roadmap-amendment-v2.4-2026-10-28.md')!='937609ff2945d3abbdd12b382a053556f7c6e06748c37055e37d8f1f36ac3c1c':raise RuntimeError('STOP: v2.4 changed')
    elif native:raise RuntimeError('STOP: qualified production source changed')
    for name,h in FROZEN.items():
        if file_hash(repo/'docs/developer'/name)!=h:raise RuntimeError('STOP: frozen contract changed')
    parent=Path.home()/'Software/build/wenu-imaging';campaign=parent/'mac-stage2-integrated-du1sqj06'
    prior=campaign/('F3-failures/run-provenance.json' if args.resume_publication else 'v2.3-bpm-filenames/run-provenance.json');old=json.loads(prior.read_text())
    pointer=parent/'stage2-integrated-active-campaign.json'
    if Path(json.loads(pointer.read_text())['report']).resolve()!=prior.resolve():raise RuntimeError('STOP: campaign already advanced')
    if args.resume_publication:
        publication_parent(old)
    else:
        if old['source']['commit']!='f5afd08fbfb35a8a50409c92352f9061c92c1f69' or old['status']!='F1-F2-passed-awaiting-review' or not old['execution_complete']:raise RuntimeError('STOP: F1/F2 acceptance parent differs')
        if [old[k] for k in ('planned_launches_consumed','retest_launches_consumed','native_launches_consumed','correction_rounds_consumed')]!=[6,6,12,2]:raise RuntimeError('STOP: inherited counters differ')
        for key in ('protected_files_unchanged','checkout_unchanged','raw_files_preserved','previous_report_unchanged','inherited_evidence_unchanged'):
            if not old[key]:raise RuntimeError('STOP: parent preservation finding')
    protected=old['protected_sha256']
    if not all(file_hash(Path(k))==h for k,h in protected.items()):raise RuntimeError('STOP: selected installation changed')
    compiler,sdk,cmake=[a.resolve(strict=True) for a in (args.compiler,args.sdk,args.cmake)]
    for tool in (compiler,cmake):
        if file_hash(tool)!=old['tool_sha256'][str(tool)]:raise RuntimeError('STOP: tool changed')
    leaks=Path('/usr/bin/leaks')
    if file_hash(leaks)!=old['tool_sha256'][str(leaks)]:raise RuntimeError('STOP: leaks tool changed')
    preserved={str(prior):file_hash(prior)}
    for command in old['commands']:
        if file_hash(Path(command['log']))!=command['log_sha256']:raise RuntimeError('STOP: prior command log changed')
        preserved[command['log']]=command['log_sha256']
    smoke_reference=None;smoke_inputs=None
    if args.resume_publication:
        logs={c['label']:Path(c['log']) for c in old['commands']}
        for case in old['cases']:
            for name,h in case['input_sha256'].items():
                path=Path(case['directory'])/name
                if file_hash(path)!=h:raise RuntimeError('STOP: prior fixture changed')
                preserved[str(path)]=h
            for name,h in case['partial_products'].items():
                path=Path(case['directory'])/name
                if file_hash(path)!=h:raise RuntimeError('STOP: prior partial output changed')
                preserved[str(path)]=h
            state,findings=failure_diagnostics(logs[case['variant']+'-'+case['lane']].read_text(errors='replace'),case['lane'],case['variant'])
            if findings!=case['findings'] or json.loads(json.dumps(state))!=case['diagnostics']:raise RuntimeError('STOP: retained F3 diagnostics differ')
        ancestor=old['previous_attempt'];path=Path(ancestor['report'])
        if file_hash(path)!=ancestor['sha256']:raise RuntimeError('STOP: F2 ancestor changed')
        preserved[str(path)]=ancestor['sha256'];accepted=json.loads(path.read_text())['inherited_cases'][0]
        smoke_reference=accepted['products'];smoke_inputs=accepted['input_sha256']
    work=campaign/('v2.4-publication' if args.resume_publication else 'F3-failures');work.mkdir(exist_ok=False)
    record=dict(schema_version=1,source=dict(commit=commit,dirty=False),fixed_row='F3',status='running',execution_complete=False,
        previous_attempt=dict(report=str(prior),sha256=file_hash(prior)),planned_launches_consumed=old['planned_launches_consumed'],retest_launches_consumed=old['retest_launches_consumed'],
        native_launches_consumed=old['native_launches_consumed'],correction_rounds_consumed=2,planned_native_launch_limit=19,commands=[],cases=[],
        selected_cases=list(CASES),lane_order=['instrumented','leaks'],protected_sha256=protected,
        inherited_source=old['source'],installation_performed=False,scientific_acceptance_claimed=False,
        raw_WFI_opened=False,tool_sha256={str(t):file_hash(t) for t in (compiler,cmake,leaks)})
    record['publication_exception_consumed']=args.resume_publication
    report=work/'run-provenance.json';save(report,record);save(pointer,dict(report=str(report),source=commit))
    print('WORK DIRECTORY:',work,flush=True)
    env={k:v for k,v in os.environ.items() if not k.startswith(('S2_','Malloc','DYLD_')) and k not in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS')}
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    env.update(E_VERBOSE='0',E_DEBUG='0')
    def run(label,argv,cwd,child,native=False):
        item=dict(label=label,argv=list(map(str,argv)),cwd=str(cwd),native=native);record['commands'].append(item)
        if native:
            if len(record['cases'])>10 or record['planned_launches_consumed']>=16:raise RuntimeError('STOP: F3 launch cap')
            if args.resume_publication and label in ('blocked-output-instrumented','publication-smoke-instrumented'):
                if record['retest_launches_consumed']>=8:raise RuntimeError('STOP: publication retests consumed')
                record['retest_launches_consumed']+=1;item['purpose']='v2.4 approved retest'
            else:
                record['planned_launches_consumed']+=1;item['purpose']='original fixed F3 role'
            record['native_launches_consumed']+=1
        log=work/(label+'.log');save(report,record);print('Running:',label,flush=True)
        with log.open('w') as stream:code=subprocess.run(item['argv'],cwd=cwd,env=child,stdout=stream,stderr=subprocess.STDOUT).returncode
        item.update(exit_status=code,log=str(log),log_sha256=file_hash(log));save(report,record)
        return code,log.read_text(errors='replace')
    try:
        # Disposable export and exactly two dormant, recorded allocation-failure points.
        source=work/'source';source.mkdir();archive=subprocess.check_output(['git','archive',commit,'mefpp2'],cwd=repo)
        record['source_archive_sha256']=hashlib.sha256(archive).hexdigest()
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:stream.extractall(source)
        record['private_injection_points']=inject(source)
        wiring=source/'mefpp2/CMakeLists.txt';wiring.write_text(wiring.read_text()+'\nadd_executable(integrated_observer tests/integrated_calibration_observer.c)\ntarget_link_libraries(integrated_observer PRIVATE mefpp_common)\ntarget_compile_definitions(integrated_observer PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n')
        record['private_cmake_sha256']=file_hash(wiring);builds={}
        for lane in ('instrumented','leaks'):
            build=work/('build-c17-'+lane);flags='-O0 -g -fno-omit-frame-pointer';link=''
            if lane=='instrumented':flags+=' -fsanitize=address,undefined -fno-sanitize-recover=all';link='-fsanitize=address,undefined'
            argv=[cmake,'-S',source/'mefpp2','-B',build,'-G','Unix Makefiles','-DCMAKE_C_COMPILER='+str(compiler),'-DCMAKE_OSX_SYSROOT='+str(sdk),'-DCMAKE_OSX_ARCHITECTURES=x86_64','-DCMAKE_BUILD_TYPE=Debug','-DMEFPP_C_STANDARD=17','-DBUILD_TESTING=OFF','-DMEFPP_BUILD_RESOURCES=OFF','-DMEFPP_SOURCE_REVISION='+commit,'-DCMAKE_C_FLAGS='+flags,'-DCMAKE_EXE_LINKER_FLAGS='+link]
            for label,cmd in [('configure-'+lane,argv),('build-'+lane,[cmake,'--build',build,'--target','integrated_observer','--parallel','2'])]:
                code,_=run(label,cmd,work,env)
                if code:raise RuntimeError('Build failed: '+label)
            info=json.loads((build/'build-info.json').read_text())
            if info['qfits_memory_mode']!=2 or info['qfits_max_pointers']!=2000000:raise RuntimeError('Allocator policy changed')
            binary=build/'integrated_observer';builds[lane]=binary
            code,output=run('symbols-'+lane,['/usr/bin/nm',binary],work,env)
            if code or (lane=='instrumented' and ('__asan_' not in output or '__ubsan_' not in output)):raise RuntimeError('Symbols missing')
            if lane=='leaks':
                code,_=run('dsym-leaks',['/usr/bin/dsymutil',binary],work,env)
                if code:raise RuntimeError('dsymutil failed')
        record['binary_sha256']={k:file_hash(v) for k,v in builds.items()}
        sequence=(PUBLICATION_SEQUENCE if args.resume_publication else [(v,l) for v in CASES for l in ('instrumented','leaks')])
        record['execution_sequence']=sequence;save(report,record)
        for variant,lane in sequence:
            label=variant+'-'+lane;directory=work/label;fixture=prepare(directory,source);argv=list(ARGV);child=env.copy()
            # The intentional failure is set before input identities are locked.
            if variant=='missing-list':argv[argv.index('--bias')+1]='missing-bias.list'
            if variant=='corrupt-frame':(directory/'bias0.fits').write_bytes(b'F3 deliberately corrupt selected input\n')
            if variant=='blocked-output':
                block=directory/'OCAM_MB_1x1.fits';block.mkdir();(block/'preserve-marker.txt').write_text('F3 protected output blocker\n')
            if variant in ('context-allocation','cube-allocation'):child['S2_F3_ALLOC']=variant.split('-')[0]
            inputs={str(p.relative_to(directory)):file_hash(p) for p in directory.rglob('*') if p.is_file()}
            case=dict(variant=variant,lane=lane,directory=str(directory),input_sha256=inputs,status='running',findings=[])
            record['cases'].append(case);save(report,record)
            if lane=='instrumented':child.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=0')
            else:child.update(MallocStackLogging='lite',MallocScribble='1')
            command=[builds[lane],*argv]
            if lane=='leaks':command=[leaks,'-quiet','-atExit','--',*command]
            code,output=run(label,command,directory,child,True);case['exit_status']=code
            if code:case['findings'].append('Observer/tool exited nonzero (not a clean observed native failure)')
            try:
                if variant=='publication-smoke':
                    if fixture['input_sha256']!=smoke_inputs:raise RuntimeError('Smoke fixture/expectations changed')
                    case['products']=verify(directory,fixture['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
                    if comparable(case['products'])!=comparable(smoke_reference):raise RuntimeError('Smoke canonical products differ from accepted F1')
                    case['diagnostics'],findings=diagnostic(output,2,lane)
                else:
                    case['diagnostics'],findings=failure_diagnostics(output,lane,variant)
                case['findings'].extend(findings)
            except Exception as error:case['findings'].append(str(error))
            if not all(file_hash(directory/n)==h for n,h in inputs.items()):case['findings'].append('Protected fixture/blocker changed')
            case['partial_products']={p.name:file_hash(p) for p in directory.glob('*.fits') if p.is_file() and p.name not in inputs}
            if variant!='publication-smoke' and (variant!='blocked-output' or args.resume_publication) and case['partial_products']:case['findings'].append('Unexpected products before declared early failure')
            case['status']='failed' if case['findings'] else 'passed';save(report,record);print(variant,lane,case['status'],flush=True)
            if case['findings']:raise RuntimeError('STOP: '+label+': '+'; '.join(case['findings']))
        record.update(status='F3-passed-awaiting-review',execution_complete=True)
    except BaseException as error:record.update(status='stopped',error=str(error));print(str(error),flush=True)
    finally:
        record['protected_files_unchanged']=all(file_hash(Path(k))==h for k,h in protected.items())
        record['checkout_unchanged']=git('rev-parse','HEAD')==commit and not git('status','--porcelain','--untracked-files=all')
        record['previous_evidence_unchanged']=all(Path(k).is_file() and file_hash(Path(k))==h for k,h in preserved.items())
        record['fixture_inputs_unchanged']=all((Path(c['directory'])/n).is_file() and file_hash(Path(c['directory'])/n)==h for c in record['cases'] for n,h in c['input_sha256'].items())
        if not all(record[k] for k in ('protected_files_unchanged','checkout_unchanged','previous_evidence_unchanged','fixture_inputs_unchanged')):record['status']='stopped-preservation-finding'
        save(report,record)
        print('PLANNED LAUNCHES:',record['planned_launches_consumed'],'/ 19; TOTAL:',record['native_launches_consumed'],'; repair rounds: 2 / 2',flush=True)
        print('STATUS:',record['status'],flush=True);print('REPORT:',report,flush=True)
    return 0 if record['status']=='F3-passed-awaiting-review' else 1


if __name__=='__main__':sys.exit(main())
