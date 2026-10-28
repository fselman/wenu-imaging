"""Inspect retained Mac multiext evidence; no native execution or artifact edits."""
from pathlib import Path
import argparse,hashlib,json,re,sys
import numpy as np
from astropy.io import fits
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--evidence',type=Path,required=True,help='Extracted original run directory including supplemented build logs')
parser.add_argument('--result',type=Path,required=True,help='Fresh retained output path outside the checkout')
args=parser.parse_args()
repo=args.repo.resolve();root=args.evidence.resolve()
if args.result.exists():raise RuntimeError('Result path already exists; preserve prior inspection')
sys.path.insert(0,str(repo/'mefpp2/tests'))
from bpm_multiext_cases import verify
from bpm_metadata_cases import header_block,PRIMARY
from qualify_split_ownership import allocation_state
from descriptor_snapshots import snapshots

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(purpose=__doc__,status='running',native_execution=False,
 archive_sha256='d2756d00d3dab708efbd8f40e02337a90b51e98514f2ad0ee87793eaa88ec428',manifest_files_verified=1259)
def save(): args.result.write_text(json.dumps(result,indent=2)+'\n')
save()
try:
 r=json.loads((root/'run-provenance.json').read_text())
 assert r['tested_source']==dict(repository='https://github.com/fselman/wenu-imaging',branch='test/stage2-bpm-wfi-multiext',commit='cea3e927f0392d8ec6c97cd40afbac2878aca03f',dirty=False)
 assert r['status']=='passed' and r['execution_complete'] and len(r['cases'])==32 and r['finding_cases']==0 and r['functional_finding_cases']==0
 assert all(r[k] for k in ('sources_unchanged','exported_sources_unchanged','protected_files_unchanged','ownership_reference_unchanged','reference_unchanged','checkout_unchanged'))
 assert not r['installation_performed'] and not r['observational_processing_performed']
 for name,h in r['source_sha256'].items():assert sha(root/'source'/name)==h==sha(repo/name),name
 assert sha(root/'source/mefpp2/CMakeLists.txt')==r['diagnostic_cmake_sha256']
 assert r['allocator']==dict(XMEMORY_MODE=2,XMEMORY_MAXPTRS=2000000)
 for name,h in r['qualified_tool_reports_sha256'].items():assert sha(repo/name)==h
 ref_path=repo/'docs/developer/fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json'
 meta_path=repo/'docs/developer/fixtures/mac-stage2-bpm-metadata-2026-10-27/run-provenance.json'
 assert sha(ref_path)==r['mac_reference_sha256'] and sha(meta_path)==r['ownership_reference_sha256']
 references={c['case']:c for c in json.loads(ref_path.read_text())['cases']}
 metadata={c['case']:c for c in json.loads(meta_path.read_text())['cases']}
 fixture=repo/'mefpp2/tests/fixtures/bpm-cleanup'
 expected={f'c{mode}-{lane}-{inst}-{kind}-flag{flag}' for mode in (90,17) for lane in ('instrumented','leaks') for inst in ('omegacam','wfi') for kind in ('retained','known-response') for flag in (0,1)}
 assert {c['case'] for c in r['cases']}==expected
 commands={c['label']:c for c in r['commands']};assert len(commands)==len(r['commands'])==79
 missing_logs=[]
 for c in commands.values():
  assert c['exit_status']==0
  path=root/Path(c['log']).name
  if path.is_file():assert sha(path)==c['log_sha256']
  else:missing_logs.append(path.name)
 assert set(missing_logs)<= {'build-c90-instrumented.log','build-c90-leaks.log','build-c17-instrumented.log','build-c17-leaks.log'}
 builds=[]
 for build in sorted(p for p in root.glob('build-*') if p.is_dir()):
  info=json.loads((build/'build-info.json').read_text());mode=90 if 'c90' in build.name else 17;instrumented='instrumented' in build.name
  assert info['source_revision']==r['tested_source']['commit'] and int(info['c_standard'])==mode
  assert info['qfits_memory_mode']==2 and info['qfits_max_pointers']==2000000
  assert info['system']=='Darwin' and info['compiler_id']=='AppleClang' and info['cmake_version']=='3.29.3'
  assert info['compiler_version']=='15.0.0.15000100' and info['osx_architectures']=='x86_64'
  assert ('-fsanitize=address,undefined' in info['c_flags'])==instrumented
  assert ('-fsanitize=address,undefined' in info['executable_linker_flags'])==instrumented
  units=json.loads((build/'compile_commands.json').read_text());assert len(units)==101
  for unit in units:
   flags=unit.get('command',' '.join(unit.get('arguments',[])))
   assert '-std=c'+str(mode) in flags
   assert ('-fsanitize=address,undefined' in flags)==instrumented
  builds.append(dict(name=build.name,translation_units=len(units),c_standard=mode,build_info_sha256=sha(build/'build-info.json')))
 assert len(builds)==4
 canonical={};leaks=0;descriptor_boundaries=[];roles=0
 for c in r['cases']:
  assert c['status']==c['functional_status']=='passed' and not c['findings']
  kind,flag,mode,inst,lane=c['fixture'],c['proportional_flag'],c['mode'],c['instrument'],c['lane']
  prior=references['c%d-%s-flag%d'%(mode,kind,flag)]
  for role,o in c['roles'].items():
   roles+=1;case=root/c['case']/role
   assert o['status']==o['functional_status']=='passed' and not o['findings'] and o['exit_status']==0
   assert o['input_sha256']==r['metadata_fixture_manifest']['cases'][inst+'-'+kind]['inputs_sha256']
   for name,h in o['input_sha256'].items():assert sha(case/name)==h
   for name,h in o['output_sha256'].items():assert sha(case/name)==h
   binary=root/('build-c%d-%s'%(mode,lane))/('bpm_original_probe' if role=='ordinary' else 'bpm_ownership_probe')
   assert sha(binary)==o['executable_sha256']
   previous=metadata['c%d-%s-%s-flag%d'%(mode,lane,kind,flag)]['roles'][role]['outputs']
   outputs,origfiles=verify(case,o['input_sha256'],prior,flag,previous,inst,fixture,kind)
   assert outputs==o['outputs'] and origfiles==o['generated_origfiles']
   key=(inst,kind,flag)
   if key in canonical:assert canonical[key]==outputs
   else:canonical[key]=outputs
   # Independent raw input and exact mask readback, beyond reported status.
   for i in range(3):
    name='frame%d.fits'%i;raw=(case/name).read_bytes();parent=(fixture/kind/name).read_bytes()
    primary=header_block(parent[:2880],PRIMARY[i]);primary=header_block(primary,dict(INSTRUME=inst.upper(),TELESCOP='MPI-2.2' if inst=='wfi' else 'VST'))
    assert raw[:2880]==primary and len(raw)==14400
    assert raw[2880:5760]==header_block(parent[2880:5760],{'EXTNAME':'S2_CCD_A'})
    assert raw[5760:8640]==parent[5760:8640]
    assert raw[8640:11520]==header_block(parent[2880:5760],{'EXTNAME':'S2_CCD_B'})
    assert raw[12168:]==parent[6408:]
    a=np.frombuffer(raw[11520:12168],dtype='>f4').reshape(9,18)
    b=np.frombuffer(parent[5760:6408],dtype='>f4').reshape(9,18)
    assert np.array_equal(a[:,:9],b[:,:9][:,::-1]) and np.array_equal(a[:,9:],b[:,9:])
   assert (case/'mefpp.paf').read_bytes()==(repo/('mefpp2/ins/mef/config/'+inst+'.paf')).read_bytes()
   image=fits.getdata(fixture/kind/'frame0.fits',1)[:,:9].astype(np.float64)
   mask=((image/image.mean()>=.5)&(image/image.mean()<=1.5)).astype(np.uint8)
   assert hashlib.sha256(mask.tobytes()).hexdigest()==prior['mask_pixels_sha256']
   for xt in (1,2):
    wanted=mask if xt==1 else mask[:,::-1]
    for path,index in [(case/('returned-%02d.fits'%xt),0),(case/outputs['saved_name'],xt)]:
     with fits.open(path,memmap=False) as hdus:assert np.array_equal(hdus[index].data,wanted)
   logpath=root/Path(commands[c['case']+'-'+role]['log']).name
   assert sha(logpath)==o['log_sha256']
   log=logpath.read_text(errors='replace')
   assert 'ERROR: AddressSanitizer' not in log and 'runtime error:' not in log
   assert re.findall(r'^PASS: extension=([12]) returned 9x9 mask good=(\d+)$',log,re.M)==[('1',str(prior['good'])),('2',str(prior['good']))]
   if role=='observer':
    rows=re.findall(r'^BPM RESULT native_exit=(\d+) constructed=(\d+) destroyed=(\d+) builds=(\d+) masks_released=(\d+) mismatch=(\d+) owner_live=(\d+) mask_live=(\d+)$',log,re.M)
    assert rows==[('0','1','1','2','2','0','0','0')] and o['ownership_contract']==list(rows[0])
    for boundary in ('process-start','after-context','before-build-1','after-build-1','after-mask-release-1','before-build-2','after-build-2','after-mask-release-2','after-context-release','after-driver','after-purge','after-second-purge'):
     state=allocation_state(log,boundary);assert state==o[boundary+'_accounting']
     if boundary in ('process-start','after-purge','after-second-purge'):assert not any(state.values())
    snap=snapshots(log);assert snap==o['descriptor_snapshots'] and not any(snap['changes'].values())
    rows=re.findall(r'^(?:CACHE )?DESCRIPTORS(?: after-(?:second-)?purge)? before=(\d+) after=(\d+) identity_equal=(\d+)$',log,re.M)
    assert len(rows)==3 and all(a==b and eq=='1' for a,b,eq in rows)
    descriptor_boundaries.append(dict(case=c['case'],boundaries=rows))
    if lane=='leaks':
     assert re.findall(r'\b(\d+) leaks? for (\d+) total leaked bytes\b',log)==[('0','0')]
     assert o['leaked_blocks']==o['leaked_bytes']==0
     leaks+=1
 assert roles==64 and leaks==16 and len(canonical)==8
 result.update(status='passed' if not missing_logs else 'available-evidence-passed-build-logs-pending',missing_command_logs=missing_logs,tested_commit=r['tested_source']['commit'],report_sha256=sha(root/'run-provenance.json'),case_pairs=32,roles_verified=roles,mask_pixel_comparisons=roles*81*2*2,input_frame_checks=roles*3,input_extension_checks=roles*3*2,leak_summaries_verified=leaks,allocator_boundaries_verified=32*12,descriptor_boundaries_verified=32*3,commands_verified=len(commands)-len(missing_logs),selected_source_identities_verified=len(r['source_sha256']),builds=builds,descriptor_boundaries=descriptor_boundaries,canonical_products_across_modes_lanes_roles_identical=True,preservation_flags_reported_true=True)
except BaseException as error:
 result.update(status='failed',error=str(error));raise
finally:save()
print(json.dumps({k:v for k,v in result.items() if k not in ('descriptor_boundaries','builds')},indent=2))
