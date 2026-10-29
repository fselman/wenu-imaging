"""Fixed F5: one tiny integrated Chapman3 workflow in C17 and one in C90."""
import argparse,configparser,hashlib,io,json,os,platform,re,resource,shutil,subprocess,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
from prepare_integrated_campaign_fixture import prepare
from integrated_campaign_products import verify,file_hash
from qualify_integrated_campaign_mac import ARGV,save,diagnostic,comparable
from qualify_integrated_repeat_mac import CONTRACTS,TESTED,F3_SHA

F4_SHA='e4cc2db636e46b45f698c98e5a7e4ba65b494e321dbe65d99b9002a09c200a10'
WIRING='''\n# Private integrated observer, not installed.\nadd_executable(integrated_observer tests/integrated_calibration_observer.c)\ntarget_link_libraries(integrated_observer PRIVATE mefpp_common)\ntarget_compile_definitions(integrated_observer PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n'''


def checked_diagnostics(output):
    # One process, one complete actual native return; no injected failures/repeats.
    if re.findall(r'^INTEGRATED CYCLE BEGIN (\d+)$',output,re.M)!=['0'] or re.findall(r'^INTEGRATED CYCLE END (\d+)$',output,re.M)!=['0']:
        raise RuntimeError('Missing/duplicate native cycle')
    if re.search(r'AddressSanitizer:|UndefinedBehaviorSanitizer:|runtime error:|F3 INJECT',output):
        raise RuntimeError('Unexpected diagnostic/injection finding')
    state,findings=diagnostic(output,2,'functional')
    if findings:raise RuntimeError('; '.join(findings))
    return state


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    # Guard the actual qualified host/environment/source before any work directory.
    if platform.system()!='Linux' or platform.node().split('.')[0]!='chapman3':raise RuntimeError('STOP: run on Chapman3')
    if Path(sys.prefix).resolve()!=(Path.home()/'.conda/envs/wenu-imaging').resolve():raise RuntimeError('STOP: qualified Python required')
    if os.getpriority(os.PRIO_PROCESS,0)<10:raise RuntimeError('STOP: nice >=10 required')
    resource.setrlimit(resource.RLIMIT_CORE,(0,0));repo=Path(__file__).resolve().parents[2]
    def git(*argv):return subprocess.check_output(['git',*argv],cwd=repo,text=True).strip()
    if repo!=Path('/home1/fselman/Software/wenu-imaging') or git('symbolic-ref','--short','HEAD')!='test/stage2-integrated-campaign' or git('status','--porcelain','--untracked-files=all'):raise RuntimeError('STOP: clean qualified checkout required')
    commit=git('rev-parse','HEAD')
    if any(not name.startswith('mefpp2/tests/') for name in git('diff','--name-only',TESTED,commit,'--','mefpp2').splitlines()):raise RuntimeError('STOP: Mac-qualified native source differs')
    for name,h in CONTRACTS.items():
        if file_hash(repo/'docs/developer'/name)!=h:raise RuntimeError('STOP: frozen contract differs')
    # Pin independently inspected Mac reference reports, not a new target oracle.
    receipts=repo/'docs/developer/fixtures'
    mac_path=receipts/'mac-integrated-f4-inspected-2026-10-28/run-provenance.json'
    prior_path=receipts/'mac-integrated-f3-inspected-2026-10-28/v2.5-cube-allocation-run-provenance.json'
    if file_hash(mac_path)!=F4_SHA or file_hash(prior_path)!=F3_SHA:raise RuntimeError('STOP: accepted Mac reference differs')
    mac=json.loads(mac_path.read_text());prior=json.loads(prior_path.read_text())
    if mac['status']!='F4-passed-awaiting-review' or not mac['execution_complete'] or mac['native_launches_consumed']!=27 or mac['planned_launches_consumed']!=17 or mac['retest_launches_consumed']!=10 or mac['correction_rounds_consumed']!=2:raise RuntimeError('STOP: accepted campaign/counters differ')
    c90=receipts/'mac-final-c90-inspected-2026-10-28/inspection-result.json'
    if json.loads(c90.read_text())['status']!='accepted-bounded-final-Mac-C90-build':raise RuntimeError('STOP: final Mac C90 acceptance absent')
    reference=prior['cases'][1];expected_inputs={k:v for k,v in reference['input_sha256'].items() if k!='run-provenance.json'}
    # Preserve the actual selected installation and all pinned reference files.
    config=Path(os.environ.get('PYCAVI_ASTROSOFT_CONFIG','~/.pycavi/pycavi_astrosoft.cfg')).expanduser().resolve(strict=True)
    settings=configparser.ConfigParser(interpolation=None);settings.read(config)
    engine=Path(settings['Paths']['mefpp'].strip().strip('"')).expanduser()
    if not engine.is_absolute():engine=Path(shutil.which(str(engine)) or str(engine))
    engine=engine.resolve(strict=True)
    protected={str(p):file_hash(p) for p in (config,engine,mac_path,prior_path,c90)}
    compiler=Path('/opt/rh/devtoolset-10/root/usr/bin/gcc').resolve(strict=True)
    cmake=(Path.home()/'opt/cmake-3.29.6/bin/cmake').resolve(strict=True)
    root=Path.home()/'Software/build/wenu-imaging';work=root/'chapman3-stage2-integrated-F5'
    work.mkdir(exist_ok=False);provenance=work/'run-provenance.json'
    pointer=root/'stage2-integrated-chapman3-F5.json'
    with pointer.open('x') as stream:json.dump(dict(report=str(provenance),source=commit),stream)
    record=dict(schema_version=1,fixed_row='F5',source=dict(commit=commit,dirty=False),host=platform.node(),
        created_utc=datetime.now(timezone.utc).isoformat(),status='preparing',execution_complete=False,
        planned_launches_consumed=17,retest_launches_consumed=10,native_launches_consumed=27,correction_rounds_consumed=2,
        planned_native_launch_limit=19,commands=[],cases=[],protected_sha256=protected,
        tool_sha256={str(p):file_hash(p) for p in (compiler,cmake)},installation_performed=False,scientific_acceptance_claimed=False,
        diagnostic_scope='Target internal ownership/accounting/descriptors only; no external sanitizer/leak qualification',
        inherited_mac_reference_sha256=F4_SHA,prior_mac_reference_sha256=F3_SHA,limits=['#116 unresolved','No scientific/Phase3/full Stage 2 acceptance'])
    save(provenance,record);print('WORK DIRECTORY:',work,flush=True)
    env={k:v for k,v in os.environ.items() if not k.startswith(('S2_','Malloc','DYLD_')) and k not in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS','CC','CFLAGS','CPPFLAGS','LDFLAGS')}
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    env.update(E_VERBOSE='0',E_DEBUG='0')
    def run(label,argv,cwd,native=False):
        item=dict(label=label,argv=list(map(str,argv)),cwd=str(cwd),native=native);record['commands'].append(item)
        if native:
            if record['planned_launches_consumed']>=19:raise RuntimeError('STOP: fixed launch budget exhausted')
            record['planned_launches_consumed']+=1;record['native_launches_consumed']+=1
        save(provenance,record);print('Running:',label,flush=True);log=work/(label+'.log')
        with log.open('w') as stream:code=subprocess.run(item['argv'],cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT).returncode
        item.update(exit_status=code,log=str(log),log_sha256=file_hash(log));save(provenance,record)
        if code:raise RuntimeError(label+' exited '+str(code))
        return log.read_text(errors='replace')
    try:
        # Export unchanged tracked native code; add only private observer build wiring.
        source=work/'source';source.mkdir();archive=subprocess.check_output(['git','archive',commit,'mefpp2'],cwd=repo)
        record['source_archive_sha256']=hashlib.sha256(archive).hexdigest()
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:stream.extractall(source)
        wiring=source/'mefpp2/CMakeLists.txt';wiring.write_text(wiring.read_text()+WIRING)
        record['private_cmake_sha256']=file_hash(wiring);builds={};record['binary_sha256']={}
        # Both explicit mode builds precede the two original planned native launches.
        for mode in ('17','90'):
            build=work/('build-c'+mode)
            run('configure-c'+mode,[cmake,'-S',source/'mefpp2','-B',build,'-G','Unix Makefiles',
                '-DCMAKE_C_COMPILER='+str(compiler),'-DCMAKE_BUILD_TYPE=Debug','-DMEFPP_C_STANDARD='+mode,
                '-DBUILD_TESTING=OFF','-DMEFPP_BUILD_RESOURCES=OFF','-DMEFPP_SOURCE_REVISION='+commit,
                '-DCMAKE_C_FLAGS=-O0 -g -fno-omit-frame-pointer','-DCMAKE_EXE_LINKER_FLAGS='],work)
            run('build-c'+mode,[cmake,'--build',build,'--target','integrated_observer','--parallel','2'],work)
            info=json.loads((build/'build-info.json').read_text())
            if str(info['c_standard'])!=mode or info['source_revision']!=commit or info['system']!='Linux' or info['processor']!='x86_64' or info['compiler_id']!='GNU' or info['compiler_version']!='10.2.1' or info['cmake_version']!='3.29.6' or info['qfits_memory_mode']!=2 or info['qfits_max_pointers']!=2000000:raise RuntimeError('STOP: target build identity differs')
            binary=build/'integrated_observer';builds[mode]=binary;record['binary_sha256'][mode]=file_hash(binary)
        # Exactly one complete tiny recipe per mode; no failure/repeat/raw-data suite.
        for mode in ('17','90'):
            directory=work/('c'+mode+'-functional');fixture=prepare(directory,repo)
            if fixture['input_sha256']!=expected_inputs:raise RuntimeError('STOP: accepted fixture bytes differ')
            case=dict(mode=mode,directory=str(directory),input_sha256=fixture['input_sha256'],fixture_report_sha256=file_hash(directory/'run-provenance.json'),status='running',findings=[])
            record['cases'].append(case);save(provenance,record)
            output=run('F5-c'+mode,[builds[mode],*ARGV],directory,True)
            case['diagnostics']=checked_diagnostics(output)
            products=verify(directory,case['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
            if comparable(products)!=comparable(reference['products']):raise RuntimeError('STOP: exact Mac products/ordered metadata differ')
            case.update(products=products,status='passed');save(provenance,record);print('C'+mode,'passed',flush=True)
        record.update(status='F5-passed-awaiting-review',execution_complete=True)
    except BaseException as error:
        record.update(status='stopped',error=str(error));print('STOP:',error,flush=True)
        if record['cases'] and record['cases'][-1]['status']=='running':record['cases'][-1].update(status='failed',findings=[str(error)])
    finally:
        record['protected_files_unchanged']=all(Path(p).is_file() and file_hash(Path(p))==h for p,h in protected.items())
        record['fixture_inputs_unchanged']=all((Path(c['directory'])/n).is_file() and file_hash(Path(c['directory'])/n)==h for c in record['cases'] for n,h in c['input_sha256'].items())
        record['fixture_reports_unchanged']=all(file_hash(Path(c['directory'])/'run-provenance.json')==c['fixture_report_sha256'] for c in record['cases'])
        record['checkout_unchanged']=git('rev-parse','HEAD')==commit and not git('status','--porcelain','--untracked-files=all')
        if not all(record[k] for k in ('protected_files_unchanged','fixture_inputs_unchanged','fixture_reports_unchanged','checkout_unchanged')):record['status']='stopped-preservation-finding'
        record['finished_utc']=datetime.now(timezone.utc).isoformat();save(provenance,record)
        print('PLANNED LAUNCHES:',record['planned_launches_consumed'],'/ 19; TOTAL:',record['native_launches_consumed'],'; repair rounds: 2 / 2')
        print('STATUS:',record['status']);print('REPORT:',provenance)
    return 0 if record['status']=='F5-passed-awaiting-review' else 1


if __name__=='__main__':sys.exit(main())
