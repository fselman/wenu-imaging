"""Frozen F1/F2 integrated Mac C17 campaign; stop on findings, never retry automatically.

Each workload runs the actual recipe once as ordinary control, once with ASan/UBSan,
and once with external leaks. No Pycavi wrapper or normal installation is exercised.
F3-F5 continue in the same retained campaign after review; this command cannot reset it.
"""
import argparse
import configparser
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import subprocess
import sys
import tarfile
import tempfile
from prepare_integrated_campaign_fixture import prepare
from integrated_campaign_products import verify, file_hash
from qualify_split_ownership import allocation_state
from descriptor_snapshots import snapshots

LOCK_SHA = 'e4572a8f99b4648722a89c6b4b4ffcc539243ef69faeee0dc71999f4a8d6d397'
FROZEN = {'native-roadmap-frozen-v2.0-2026-10-28.md':'1a3b679710fb45796fb136f6d9883efba632522d8a0ead249ce868ef107f1f89',
          'native-roadmap-amendment-v2.1-2026-10-28.md':'06436cf14657ee5585957ead6328bee5218c66a20c36ed4cfc702840c5377626',
          'native-roadmap-amendment-v2.2-2026-10-28.md':'20f23e9fa75d28ea16cda55e549d5cdf6a4e1db9ca3045fd8d6398ed476f3b6b'}
ARGV = ['--pafname','mefpp.paf','--bias','bias.list','--biassave','--biassub',
        '--bpm','bpm.list','--dome','dome.list','--domesave','--sky','sky.list','--skysave','--science','science.list']


def save(path, value):
    temporary=path.with_suffix(path.suffix+'.pending')
    temporary.write_text(json.dumps(value,indent=2)+'\n')
    temporary.replace(path)


def comparable(products):
    return {category:{k:v for k,v in item.items() if k!='name'} for category,item in products.items()}


def diagnostic(output, detectors, lane):
    """Read every ownership/allocator/descriptor checkpoint, retaining nonzero stage states."""
    findings=[];result={}
    rows=re.findall(r'^INTEGRATED RESULT (.+)$',output,re.M)
    if len(rows)!=1:raise RuntimeError('Missing/duplicate native ownership result')
    result['ownership']={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',rows[0])}
    expected=dict(native_exit=0,contexts=1,destroyed=1,calibration_calls=3*detectors,
                  bpm_calls=detectors,combine_calls=detectors,science_loads=detectors,
                  live_products=0,owner_live=0,mismatch=0)
    if result['ownership']!=expected:findings.append('Native status/ownership/stage count differs')
    labels=re.findall(r'^ACCOUNTING BEGIN (\S+)$',output,re.M)
    if len(set(labels))!=len(labels):raise RuntimeError('Duplicate accounting boundary')
    required={'process-start','after-context','before-context-release','after-context-release',
              'after-driver','after-purge','after-second-purge'}
    if not required.issubset(labels):raise RuntimeError('Incomplete allocator observations')
    result['accounting']={label:allocation_state(output,re.escape(label)) for label in labels}
    for label in ('process-start','after-purge','after-second-purge'):
        if any(result['accounting'][label].values()):findings.append('Live tracked resources at '+label)
    result['descriptor_snapshots']=snapshots(output)
    if any(result['descriptor_snapshots']['changes'].values()):findings.append('Per-descriptor identity changed (#116)')
    for prefix in ('DESCRIPTORS','CACHE DESCRIPTORS after-purge','CACHE DESCRIPTORS after-second-purge'):
        rows=re.findall(r'^'+prefix+r' before=(\d+) after=(\d+) identity_equal=(\d+)$',output,re.M)
        if len(rows)!=1 or rows[0][0]!=rows[0][1] or rows[0][2]!='1':
            findings.append('Descriptor gate failed: '+prefix)
    result['descriptor_limits']=re.findall(r'^DESCRIPTOR LIMIT (before|after) soft=(\d+) hard=(\d+) soft_unlimited=(\d+)$',output,re.M)
    if len(result['descriptor_limits'])!=2:findings.append('Missing descriptor limit observations')
    if lane=='leaks':
        rows=re.findall(r'\b(\d+) leaks? for (\d+) total leaked bytes\b',output)
        result['leaks']=rows
        if len(rows)!=1 or tuple(rows[0])!=('0','0'):findings.append('External leak summary missing/nonzero')
    return result,findings



def begin_attempt(parent, pointer, commit, protected, previous_path=None, allow_bias_qc=False):
    """Continue a reviewed failure, with the original campaign and two-round limit."""
    if allow_bias_qc and previous_path is None:raise RuntimeError('STOP: bias-QC exception requires its reviewed parent')
    if previous_path is None:
        with pointer.open('x') as stream:json.dump(dict(status='initializing',source=commit),stream)
        return Path(tempfile.mkdtemp(prefix='mac-stage2-integrated-',dir=parent)),None
    previous_path=previous_path.resolve(strict=True)
    campaign=parent/'mac-stage2-integrated-du1sqj06'
    first=campaign/'run-provenance.json'
    second=campaign/'correction-round-1/run-provenance.json'
    third=campaign/'correction-round-2/run-provenance.json'
    exception=None
    active=json.loads(pointer.read_text())
    if Path(active['report']).resolve()!=previous_path:raise RuntimeError('STOP: active campaign already advanced')
    previous=json.loads(previous_path.read_text());cases=previous['cases']
    if previous_path==first.resolve(strict=True):
        correction_round=1;planned=1;retests=0;total=1;labels=['F1-ordinary'];reference=None
        valid=(previous['source']['commit']=='fa2e5c2f508e18d18981b8e987b86cc4a411c1df'
            and len(cases)==1 and cases[0]['fixed_row']=='F1' and cases[0]['lane']=='ordinary'
            and cases[0]['status']=='failed' and cases[0]['exit_status']==0
            and cases[0]['findings']==['Known-answer array differs: CALIB.MASTER_DOME_FLAT extension 2'])
    elif previous_path==second.resolve(strict=True):
        correction_round=2;planned=2;retests=1;total=3
        labels=['F1-ordinary','F1-instrumented'];reference=cases[0]['products']
        valid=(previous['source']['commit']=='f0242b24aa4ebe54171287f3439902df8cc6f576'
            and len(cases)==2 and cases[0]['fixed_row']=='F1' and cases[0]['lane']=='ordinary'
            and cases[0]['status']=='passed' and not cases[0]['findings']
            and cases[1]['fixed_row']=='F1' and cases[1]['lane']=='instrumented'
            and cases[1]['status']=='failed' and cases[1]['exit_status']==0
            and cases[1]['findings']==['Live tracked resources at after-purge','Live tracked resources at after-second-purge']
            and previous['planned_launches_consumed']==planned and previous['retest_launches_consumed']==retests)
        ancestor=previous['previous_attempt']
        if file_hash(Path(ancestor['report']))!=ancestor['sha256']:raise RuntimeError('STOP: original ancestor changed')
    elif allow_bias_qc and previous_path==third.resolve(strict=True):
        exception='v2.2-bias-qc';correction_round=2;planned=2;retests=3;total=5
        labels=['F1-ordinary','F1-instrumented'];reference=cases[0]['products']
        valid=(previous['source']['commit']=='3e60e8cbf198bd786dd1929e48e60f5c066be854'
            and len(cases)==2 and cases[0]['fixed_row']=='F1' and cases[0]['lane']=='ordinary'
            and cases[0]['status']=='passed' and not cases[0]['findings']
            and cases[1]['fixed_row']=='F1' and cases[1]['lane']=='instrumented'
            and cases[1]['status']=='failed' and cases[1]['exit_status']==0
            and cases[1]['findings']==['Live tracked resources at after-purge','Live tracked resources at after-second-purge']
            and previous['planned_launches_consumed']==planned and previous['retest_launches_consumed']==retests
            and previous['previous_report_unchanged'])
        expected=dict(pointers=4,bytes=32,mapped_files=0,mapped_references=0,swap_bytes=0)
        if valid:
            valid=all(cases[1]['diagnostics']['accounting'][phase]==expected
                for phase in ('after-purge','after-second-purge'))
        ancestor=previous['previous_attempt']
        for depth in range(2):
            if file_hash(Path(ancestor['report']))!=ancestor['sha256']:raise RuntimeError('STOP: ancestor evidence changed')
            ancestor=json.loads(Path(ancestor['report']).read_text()).get('previous_attempt')
            if ancestor is None:break
    else:raise RuntimeError('STOP: unexpected failed campaign; no third correction round')
    if (not valid or previous['status']!='stopped' or previous['execution_complete']
        or previous['native_launches_consumed']!=total
        or previous['correction_rounds_consumed']!=(2 if exception else correction_round-1)):
        raise RuntimeError('STOP: parent is not the reviewed F1 failure')
    if previous['protected_sha256']!=protected:raise RuntimeError('STOP: protected installation identity changed')
    for key in ('protected_files_unchanged','checkout_unchanged','raw_files_preserved'):
        if not previous[key]:raise RuntimeError('STOP: parent preservation finding')
    # Verify all prior command logs, fixture inputs and reported output identities.
    for command in previous['commands']:
        if file_hash(Path(command['log']))!=command['log_sha256']:raise RuntimeError('STOP: original log changed')
    for case in cases:
        root=Path(case['directory'])
        for name,h in case['input_sha256'].items():
            if file_hash(root/name)!=h:raise RuntimeError('STOP: original fixture input changed')
        if 'products' in case:
            actual=verify(root,case['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
            if actual!=case['products']:raise RuntimeError('STOP: original product evidence changed')
    if allow_bias_qc and exception is None:raise RuntimeError('STOP: wrong parent for bias-QC exception')
    work=campaign/(exception or ('correction-round-'+str(correction_round)));work.mkdir(exist_ok=False)
    return work,dict(report=str(previous_path),sha256=file_hash(previous_path),source=previous['source'],
        planned_launches=planned,retest_launches=retests,native_launches=total,
        reviewed_defects=[121] if correction_round==1 else [122,123,124],correction_round=correction_round,
        retest_labels=labels,product_reference=reference,input_sha256=cases[0]['input_sha256'],approved_exception=exception)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--sdk',type=Path,required=True)
    parser.add_argument('--cmake',type=Path,required=True)
    parser.add_argument('--input-lock',type=Path,required=True)
    parser.add_argument('--resume-correction',type=Path,help='Reviewed F1 failure report; continue its fixed global repair round (1 or 2 only)')
    parser.add_argument('--bias-qc-exception',action='store_true',help='Approved one-time v2.2 four-array cleanup exception only')
    args=parser.parse_args()
    # Guards and input/reference lock: no native launch occurs in this section.
    if platform.system()!='Darwin' or platform.node().split('.')[0]!='MC02VV0HPHTDG':
        raise RuntimeError('STOP: qualified Intel Mac required')
    if Path(sys.prefix).resolve()!=Path('/Users/fselman/anaconda3'):
        raise RuntimeError('STOP: unexpected Python environment')
    if os.getpriority(os.PRIO_PROCESS,0)<10:raise RuntimeError('STOP: use nice -n 10')
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    repo=Path(__file__).resolve().parents[2]
    def git(*argv):return subprocess.check_output(['git',*argv],cwd=repo,text=True).strip()
    if repo.resolve()!=Path('/Users/fselman/Developer/wenu-imaging'):raise RuntimeError('STOP: wrong repository path')
    if git('status','--porcelain','--untracked-files=all'):raise RuntimeError('STOP: clean source required')
    if git('symbolic-ref','--short','HEAD')!='test/stage2-integrated-campaign':raise RuntimeError('STOP: wrong branch')
    commit=git('rev-parse','HEAD')
    for name,h in FROZEN.items():
        if file_hash(repo/'docs/developer'/name)!=h:raise RuntimeError('STOP: frozen contract changed')
    lockpath=args.input_lock.resolve(strict=True)
    if file_hash(lockpath)!=LOCK_SHA:raise RuntimeError('STOP: input lock is not the inspected report')
    lock=json.loads(lockpath.read_text());selection=lock['selection']
    if selection!=json.loads((repo/'mefpp2/tests/fixtures/integrated-campaign/wfi-selection.json').read_text()):
        raise RuntimeError('STOP: selected dataset changed')
    if lock['errors'] or not lock['all_selected_file_identities_locked']:raise RuntimeError('STOP: incomplete input lock')
    compiler,sdk,cmake=[p.resolve(strict=True) for p in (args.compiler,args.sdk,args.cmake)]
    leaks=Path('/usr/bin/leaks').resolve(strict=True)
    config=Path(os.environ.get('PYCAVI_ASTROSOFT_CONFIG','~/.pycavi/pycavi_astrosoft.cfg')).expanduser().resolve(strict=True)
    settings=configparser.ConfigParser(interpolation=None);settings.read(config)
    engine=Path(settings['Paths']['mefpp'].strip().strip('"')).expanduser()
    if not engine.is_absolute():engine=Path(shutil.which(str(engine)) or str(engine))
    engine=engine.resolve(strict=True)
    protected={str(p):file_hash(p) for p in (config,engine)}
    controls={}
    for kind in ('leak','diagnostic'):
        p=repo/('docs/developer/fixtures/mac-stage2-tool-controls-2026-10-27/'+kind+'-run-provenance.json')
        control=json.loads(p.read_text())
        if control['status']!='passed':raise RuntimeError('STOP: unaccepted tool controls')
        for name in ('mefpp2/qfits5/src/xmemory.c','mefpp2/qfits5/include/xmemory.h'):
            if file_hash(repo/name)!=control['source_sha256'].get(name,control['source_sha256'].get(Path(name).name)):
                raise RuntimeError('STOP: qualified allocator changed')
        controls[str(p.relative_to(repo))]=file_hash(p)
    parent=Path.home()/'Software/build/wenu-imaging';parent.mkdir(parents=True,exist_ok=True)
    pointer=parent/'stage2-integrated-active-campaign.json'
    # A correction continues the original campaign; it cannot reset its counters.
    work,previous=begin_attempt(parent,pointer,commit,protected,args.resume_correction,args.bias_qc_exception)
    provenance=work/'run-provenance.json'
    record=dict(schema_version=1,project='wenu-imaging',source=dict(commit=commit,dirty=False),
                created_utc=datetime.now(timezone.utc).isoformat(),status='running',execution_complete=False,
                planned_native_launch_limit=19,native_launches_consumed=0,correction_rounds_consumed=0,
                correction_round_limit=2,commands=[],cases=[],protected_sha256=protected,
                input_lock_sha256=LOCK_SHA,qualified_tool_reports_sha256=controls,
                tool_sha256={str(p):file_hash(p) for p in (compiler,cmake,leaks)},
                installation_performed=False,scientific_acceptance_claimed=False,
                remaining_fixed_rows=['F3','F4','F5'],limits=['F1/F2 only; no full Stage 2 acceptance',
                '#116 remains unresolved; exact descriptor gates active','No large-file mmap/swap stress'])
    record.update(previous_attempt=previous,planned_launches_consumed=previous['planned_launches'] if previous else 0,
                  retest_launches_consumed=previous['retest_launches'] if previous else 0,
                  native_launches_consumed=previous['native_launches'] if previous else 0,
                  correction_rounds_consumed=previous['correction_round'] if previous else 0,
                  bias_qc_exception_consumed=bool(previous and previous.get('approved_exception')))
    save(provenance,record);save(pointer,dict(report=str(provenance),source=commit))
    print('WORK DIRECTORY:',work,flush=True)
    env=os.environ.copy()
    removed=[k for k in env if k.startswith(('S2_','Malloc','DYLD_')) or k in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS')]
    for key in removed:env.pop(key,None)
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    env.update(E_VERBOSE='0',E_DEBUG='0')
    record['removed_child_environment']=removed
    def run(label,argv,cwd,childenv,native=False):
        item=dict(label=label,argv=list(map(str,argv)),cwd=str(cwd),native=native)
        record['commands'].append(item)
        if native:
            if previous and label in previous['retest_labels']:
                limit=previous['retest_launches']+len(previous['retest_labels'])
                if record['retest_launches_consumed']>=limit:raise RuntimeError('STOP: correction retest budget consumed')
                record['retest_launches_consumed']+=1
                item['purpose']=(previous.get('approved_exception') or ('correction-round-'+str(previous['correction_round'])))+' F1 validation'
            else:
                if record['planned_launches_consumed']>=6:raise RuntimeError('STOP: F1/F2 planned launch budget exhausted')
                record['planned_launches_consumed']+=1;item['purpose']='fixed planned row'
            record['native_launches_consumed']+=1
        save(provenance,record);print('Running:',label,flush=True)
        log=work/(label+'.log')
        try:
            with log.open('w') as stream:
                completed=subprocess.run(item['argv'],cwd=cwd,env=childenv,stdout=stream,stderr=subprocess.STDOUT)
            item['exit_status']=completed.returncode
            return completed.returncode,log.read_text(errors='replace')
        finally:
            item['log']=str(log);item['log_sha256']=file_hash(log) if log.exists() else None
            save(provenance,record)
    rawstats={};staged={}
    try:
        # Private source/build only: normal checkout, engine and configuration stay protected.
        source=work/'source';source.mkdir()
        archive=subprocess.check_output(['git','archive',commit,'mefpp2'],cwd=repo)
        record['source_archive_sha256']=hashlib.sha256(archive).hexdigest()
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:stream.extractall(source)
        wiring=source/'mefpp2/CMakeLists.txt'
        wiring.write_text(wiring.read_text()+'\n# Private integrated observer, not installed.\n'
            'add_executable(integrated_observer tests/integrated_calibration_observer.c)\n'
            'target_link_libraries(integrated_observer PRIVATE mefpp_common)\n'
            'target_compile_definitions(integrated_observer PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n')
        record['private_cmake_sha256']=file_hash(wiring)
        builds={}
        for lane in ('ordinary','instrumented','leaks'):
            build=work/('build-c17-'+lane)
            flags='-O0 -g -fno-omit-frame-pointer';link=''
            if lane=='instrumented':
                flags+=' -fsanitize=address,undefined -fno-sanitize-recover=all';link='-fsanitize=address,undefined'
            command=[cmake,'-S',source/'mefpp2','-B',build,'-G','Unix Makefiles',
                '-DCMAKE_C_COMPILER='+str(compiler),'-DCMAKE_OSX_SYSROOT='+str(sdk),'-DCMAKE_OSX_ARCHITECTURES=x86_64',
                '-DCMAKE_BUILD_TYPE=Debug','-DMEFPP_C_STANDARD=17','-DBUILD_TESTING=OFF','-DMEFPP_BUILD_RESOURCES=OFF',
                '-DMEFPP_SOURCE_REVISION='+commit,'-DCMAKE_C_FLAGS='+flags,'-DCMAKE_EXE_LINKER_FLAGS='+link]
            for label,argv in [('configure-'+lane,command),('build-'+lane,[cmake,'--build',build,'--target',
                'mefpp' if lane=='ordinary' else 'integrated_observer','--parallel','2'])]:
                code,_=run(label,argv,work,env)
                if code:raise RuntimeError('Build failed: '+label)
            info=json.loads((build/'build-info.json').read_text())
            if info['qfits_memory_mode']!=2 or info['qfits_max_pointers']!=2000000:raise RuntimeError('Allocator policy changed')
            binary=build/('mefpp' if lane=='ordinary' else 'integrated_observer');builds[lane]=binary
            if lane=='instrumented':
                code,output=run('symbols-instrumented',['/usr/bin/nm',binary],work,env)
                if code or '__asan_' not in output or '__ubsan_' not in output:raise RuntimeError('Diagnostic symbols absent')
            if lane=='leaks':
                code,_=run('dsym-leaks',['/usr/bin/dsymutil',binary],work,env)
                if code:raise RuntimeError('dsymutil failed')
        record['binary_sha256']={lane:file_hash(p) for lane,p in builds.items()}
        # F1: three complete tiny workflows; F2 starts only after every F1 lane passes.
        for fixed,tiny in [('F1',True),('F2',False)]:
            reference=None
            if not tiny:
                # Copy each locked original once; never hardlink or chmod the originals.
                shared=work/'wfi-inputs';shared.mkdir()
                for name,item in lock['input_files'].items():
                    raw=Path(name);st=raw.stat();rawstats[name]=[st.st_size,st.st_mtime_ns,st.st_ino]
                    locked=selection['files'][name]
                    if rawstats[name]!=[locked['size'],locked['mtime_ns'],locked['inode']]:raise RuntimeError('Raw stat identity differs from lock: '+name)
                    if file_hash(raw)!=item['sha256']:raise RuntimeError('Raw input differs from lock: '+name)
                    target=shared/raw.name
                    if target.exists():raise RuntimeError('Duplicate raw basename')
                    shutil.copyfile(raw,target)
                    if file_hash(target)!=item['sha256']:raise RuntimeError('Staged raw copy mismatch')
                    target.chmod(0o444);staged[name]=str(target)
                record['raw_stat_before']=rawstats;record['raw_staging']=staged
            for lane in ('ordinary','instrumented','leaks'):
                case=dict(fixed_row=fixed,lane=lane,status='running',findings=[])
                record['cases'].append(case);save(provenance,record)
                directory=work/(fixed+'-'+lane)
                if tiny:
                    fixture=prepare(directory,source)
                    inputs=fixture['input_sha256'];names=['F1_CCD_A','F1_CCD_B'];detectors=2
                    if previous and inputs!=previous['input_sha256']:raise RuntimeError('STOP: correction fixture/reference changed')
                else:
                    directory.mkdir();inputs={};names=selection['extension_order'];detectors=8
                    paf=source/selection['paf_source']
                    if file_hash(paf)!=selection['paf_sha256']:raise RuntimeError('WFI configuration changed')
                    shutil.copyfile(paf,directory/'mefpp.paf')
                    for role,files in selection['roles'].items():
                        (directory/(role+'.list')).write_text('\n'.join(staged[n] for n in files)+'\n')
                    inputs={p.name:file_hash(p) for p in directory.iterdir()}
                    inputs.update({staged[n]:item['sha256'] for n,item in lock['input_files'].items()})
                case.update(directory=str(directory),input_sha256=inputs)
                childenv=env.copy()
                if lane=='instrumented':childenv.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=0')
                if lane=='leaks':childenv.update(MallocStackLogging='lite',MallocScribble='1')
                command=[builds[lane],*ARGV]
                if lane=='leaks':command=[leaks,'-quiet','-atExit','--',*command]
                code,output=run(fixed+'-'+lane,command,directory,childenv,native=True)
                case['exit_status']=code
                if code:case['findings'].append('Native/tool process returned nonzero')
                if 'ERROR: AddressSanitizer' in output or 'runtime error:' in output:case['findings'].append('ASan/UBSan finding')
                # All six products: independent tiny arrays or exact WFI control comparison.
                try:
                    case['products']=verify(directory,inputs,detectors,tiny,names)
                    if tiny and previous and previous['product_reference'] is not None:
                        if comparable(case['products'])!=comparable(previous['product_reference']):
                            case['findings'].append('Products/ordered metadata differ from retained corrected ordinary result')
                    if reference is None:reference=comparable(case['products'])
                    elif comparable(case['products'])!=reference:case['findings'].append('Products/ordered metadata differ from ordinary control')
                except Exception as error:case['findings'].append(str(error))
                if lane!='ordinary':
                    try:
                        case['diagnostics'],findings=diagnostic(output,detectors,lane)
                        case['findings'].extend(findings)
                    except Exception as error:case['findings'].append(str(error))
                case['status']='failed' if case['findings'] else 'passed';save(provenance,record)
                print(fixed,lane,case['status'],flush=True)
                if case['findings']:raise RuntimeError('STOP: '+fixed+' '+lane+': '+'; '.join(case['findings']))
        record['status']='F1-F2-passed-awaiting-review';record['execution_complete']=True
    except BaseException as error:
        record['status']='stopped';record['error']=str(error)
        print(str(error),flush=True)
    finally:
        record['protected_files_unchanged']=all(file_hash(Path(p))==h for p,h in protected.items())
        record['checkout_unchanged']=git('rev-parse','HEAD')==commit and not git('status','--porcelain','--untracked-files=all')
        record['raw_files_preserved']=all([Path(p).stat().st_size,Path(p).stat().st_mtime_ns,Path(p).stat().st_ino]==st and file_hash(Path(p))==lock['input_files'][p]['sha256'] for p,st in rawstats.items())
        record['previous_report_unchanged']=not previous or file_hash(Path(previous['report']))==previous['sha256']
        record['finished_utc']=datetime.now(timezone.utc).isoformat()
        if not all(record[k] for k in ('protected_files_unchanged','checkout_unchanged','raw_files_preserved','previous_report_unchanged')):record['status']='stopped-preservation-finding'
        save(provenance,record)
        print('PLANNED LAUNCHES:',record['planned_launches_consumed'],'/ 19; correction retests:',record['retest_launches_consumed'],flush=True)
        print('TOTAL NATIVE LAUNCHES:',record['native_launches_consumed'],'; correction rounds:',record['correction_rounds_consumed'],'/ 2',flush=True)
        print('BIAS-QC EXCEPTION:',record['bias_qc_exception_consumed'],flush=True)
        print('STATUS:',record['status'],flush=True);print('REPORT:',provenance,flush=True)
    return 0 if record['execution_complete'] and record['status']=='F1-F2-passed-awaiting-review' else 1


if __name__=='__main__':sys.exit(main())
