"""Read-only Chapman3 multiext inspection; no native execution."""
from pathlib import Path
import argparse,hashlib,json,re,sys
import numpy as np
from astropy.io import fits
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--evidence',type=Path,required=True,help='Extracted target run directory')
parser.add_argument('--result',type=Path,required=True,help='Fresh retained result path outside checkout')
args=parser.parse_args()
repo=args.repo.resolve();root=args.evidence.resolve()
if args.result.exists():raise RuntimeError('Preserve earlier result; choose a fresh path')
sys.path.insert(0,str(repo/'mefpp2/tests'))
from bpm_multiext_cases import verify
from bpm_metadata_cases import PRIMARY,header_block
from qualify_split_ownership import allocation_state
from descriptor_snapshots import snapshots

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(purpose=__doc__,status='running',native_execution=False,archive_sha256='2934852a1ac54873bff889758e25e03eba22464a12756079fc54282f7a68afdd',manifest_file_identities_verified=911,external_memory_diagnostic_acceptance=False)
def save():args.result.write_text(json.dumps(result,indent=2)+'\n')
save()
try:
 # Source, references and original run scope.
 r=json.loads((root/'run-provenance.json').read_text())
 assert r['tested_source']==dict(repository='https://github.com/fselman/wenu-imaging',branch='test/stage2-bpm-wfi-multiext',commit='355034606cd6015b9e9abc99744973bf4c081b00',dirty=False)
 assert r['status']=='passed' and r['execution_complete'] and len(r['cases'])==16 and r['finding_cases']==0 and r['functional_finding_cases']==0
 flags={k:v for k,v in r.items() if k.endswith('_unchanged')};assert len(flags)==7 and all(flags.values())
 assert not r['installation_performed'] and not r['observational_processing_performed'] and not r['issue116_closed'] and not r['full_S2_05_accepted']
 assert r['allocator']==dict(XMEMORY_MODE=2,XMEMORY_MAXPTRS=2000000)
 macpath=repo/'docs/developer/fixtures/mac-stage2-bpm-multiext-inspected-2026-10-28/run-provenance.json'
 assert sha(macpath)==r['metadata_mac_reference_sha256']=='95c9c352f8a92ba97d4cfc20e1b3341a4548c1b954e404c3c952967ec0efa430'
 mac=json.loads(macpath.read_text());mac_cases={c['case'].replace('-leaks-','-functional-'):c for c in mac['cases'] if c['lane']=='leaks'}
 for name,h in mac['source_sha256'].items():assert r['source_sha256'][name]==h
 for name,h in r['source_sha256'].items():assert sha(root/'source'/name)==sha(repo/name)==h,name
 assert sha(root/'source/mefpp2/CMakeLists.txt')==r['diagnostic_cmake_sha256']
 for name,h in r['qualified_tool_reports_sha256'].items():assert sha(repo/name)==h
 refpath=repo/'docs/developer/fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json';assert sha(refpath)==r['mac_reference_sha256']
 references={c['case']:c for c in json.loads(refpath.read_text())['cases']}
 parentpath=repo/'docs/developer/fixtures/mac-stage2-bpm-metadata-2026-10-27/run-provenance.json';assert sha(parentpath)=='26868de58bd3a5c05c82304620d00549b79b2de605bd7bffcbeccd4faa9c308d'
 parents={c['case']:c for c in json.loads(parentpath.read_text())['cases']}
 fixture=repo/'mefpp2/tests/fixtures/bpm-cleanup'
 # Build identities, all command logs, explicit uninstrumented language lanes.
 commands={c['label']:c for c in r['commands']};assert len(commands)==len(r['commands'])==39
 for c in commands.values():assert c['exit_status']==0 and sha(root/Path(c['log']).name)==c['log_sha256']
 builds=[]
 for build in sorted(p for p in root.glob('build-*') if p.is_dir()):
  info=json.loads((build/'build-info.json').read_text());mode=90 if 'c90' in build.name else 17
  assert info['source_revision']==r['tested_source']['commit'] and int(info['c_standard'])==mode
  assert info['qfits_memory_mode']==2 and info['qfits_max_pointers']==2000000
  assert info['system']=='Linux' and info['compiler_id']=='GNU' and info['compiler_version']=='10.2.1' and info['cmake_version']=='3.29.6'
  assert '-fsanitize' not in info['c_flags']+info['executable_linker_flags']
  units=json.loads((build/'compile_commands.json').read_text());assert len(units)==101
  for unit in units:
   flags=unit.get('command',' '.join(unit.get('arguments',[])))
   assert '-std=c'+str(mode) in flags and '-fsanitize' not in flags
  lines=(root/(build.name+'.log')).read_text(errors='replace').splitlines()
  errors=[v for v in lines if re.search(r':\d+(?::\d+)?: (?:fatal )?error:|^collect2: error:|^ld:.*(?:error|undefined)|undefined reference to',v)]
  assert not errors
  assert any('Built target bpm_original_probe' in v for v in lines) and any('Built target bpm_ownership_probe' in v for v in lines)
  warnings=[v for v in lines if re.search(r'warning:',v)]
  builds.append(dict(name=build.name,c_standard=mode,translation_units=len(units),build_info_sha256=sha(build/'build-info.json'),warning_lines=len(warnings),compiler_linker_errors=errors))
 assert len(builds)==2
 expected={f'c{mode}-functional-{inst}-{kind}-flag{flag}' for mode in (90,17) for inst in ('omegacam','wfi') for kind in ('retained','known-response') for flag in (0,1)}
 assert {c['case'] for c in r['cases']}==expected
 roles=0;descriptor_boundaries=[]
 for c in r['cases']:
  assert c['status']==c['functional_status']=='passed' and not c['findings']
  mode,kind,flag,inst=c['mode'],c['fixture'],c['proportional_flag'],c['instrument'];assert c['lane']=='functional'
  ref=references['c%d-%s-flag%d'%(mode,kind,flag)]
  for role,o in c['roles'].items():
   roles+=1;case=root/c['case']/role;prior=mac_cases[c['case']]['roles'][role]
   assert o['status']==o['functional_status']=='passed' and o['exit_status']==0 and not o['findings']
   assert o['input_sha256']==prior['input_sha256']==r['metadata_fixture_manifest']['cases'][inst+'-'+kind]['inputs_sha256']
   for name,h in o['input_sha256'].items():assert sha(case/name)==h
   for name,h in o['output_sha256'].items():assert sha(case/name)==h
   binary=root/('build-c%d-functional'%mode)/('bpm_original_probe' if role=='ordinary' else 'bpm_ownership_probe');assert sha(binary)==o['executable_sha256']
   # Exact product/header oracle and direct Mac canonical comparison.
   actual,origfiles=verify(case,o['input_sha256'],ref,flag,parents['c%d-leaks-%s-flag%d'%(mode,kind,flag)]['roles'][role]['outputs'],inst,fixture,kind)
   assert actual==o['outputs']==prior['outputs'] and origfiles==o['generated_origfiles']
   # Independent raw FITS readback: both detector payloads, overscan, padding and masks.
   for i in range(3):
    name='frame%d.fits'%i;raw=(case/name).read_bytes();parent=(fixture/kind/name).read_bytes()
    primary=header_block(header_block(parent[:2880],PRIMARY[i]),dict(INSTRUME=inst.upper(),TELESCOP='MPI-2.2' if inst=='wfi' else 'VST'))
    assert len(raw)==14400 and raw[:2880]==primary
    assert raw[2880:5760]==header_block(parent[2880:5760],{'EXTNAME':'S2_CCD_A'}) and raw[5760:8640]==parent[5760:8640]
    assert raw[8640:11520]==header_block(parent[2880:5760],{'EXTNAME':'S2_CCD_B'}) and raw[12168:]==parent[6408:]
    a=np.frombuffer(raw[11520:12168],dtype='>f4').reshape(9,18);b=np.frombuffer(parent[5760:6408],dtype='>f4').reshape(9,18)
    assert np.array_equal(a[:,:9],b[:,:9][:,::-1]) and np.array_equal(a[:,9:],b[:,9:])
   assert (case/'mefpp.paf').read_bytes()==(repo/('mefpp2/ins/mef/config/'+inst+'.paf')).read_bytes()
   image=fits.getdata(fixture/kind/'frame0.fits',1)[:,:9].astype(np.float64)
   mask=((image/image.mean()>=.5)&(image/image.mean()<=1.5)).astype(np.uint8);assert hashlib.sha256(mask.tobytes()).hexdigest()==ref['mask_pixels_sha256']
   for xt in (1,2):
    wanted=mask if xt==1 else mask[:,::-1]
    for file,idx in [(case/('returned-%02d.fits'%xt),0),(case/actual['saved_name'],xt)]:
     with fits.open(file,memmap=False) as hdus:assert np.array_equal(hdus[idx].data,wanted)
   logpath=root/Path(commands[c['case']+'-'+role]['log']).name;assert sha(logpath)==o['log_sha256'];log=logpath.read_text(errors='replace')
   assert re.findall(r'^PASS: extension=([12]) returned 9x9 mask good=(\d+)$',log,re.M)==[('1',str(ref['good'])),('2',str(ref['good']))]
   if role=='observer':
    rows=re.findall(r'^BPM RESULT native_exit=(\d+) constructed=(\d+) destroyed=(\d+) builds=(\d+) masks_released=(\d+) mismatch=(\d+) owner_live=(\d+) mask_live=(\d+)$',log,re.M)
    assert rows==[('0','1','1','2','2','0','0','0')] and o['ownership_contract']==list(rows[0])
    for boundary in ('process-start','after-context','before-build-1','after-build-1','after-mask-release-1','before-build-2','after-build-2','after-mask-release-2','after-context-release','after-driver','after-purge','after-second-purge'):
     state=allocation_state(log,boundary);assert state==o[boundary+'_accounting']
     if boundary in ('process-start','after-purge','after-second-purge'):assert not any(state.values())
    snap=snapshots(log);assert snap==o['descriptor_snapshots'] and not any(snap['changes'].values())
    rows=re.findall(r'^(?:CACHE )?DESCRIPTORS(?: after-(?:second-)?purge)? before=(\d+) after=(\d+) identity_equal=(\d+)$',log,re.M)
    assert len(rows)==3 and all(a==b and eq=='1' for a,b,eq in rows);descriptor_boundaries.append(dict(case=c['case'],boundaries=rows))
 assert roles==32
 result.update(status='passed',tested_commit=r['tested_source']['commit'],report_sha256=sha(root/'run-provenance.json'),case_pairs=16,roles_verified=32,mask_pixel_comparisons=32*81*2*2,input_frame_checks=32*3,input_extension_checks=32*3*2,commands_verified=39,builds=builds,selected_sources_verified=38,mac_qualified_source_identities_unchanged=37,allocator_boundaries_verified=16*12,descriptor_boundaries_verified=16*3,descriptor_boundaries=descriptor_boundaries,all_target_products_equal_mac=True,reported_preservation_flags={k:v for k,v in r.items() if k.endswith('_unchanged')})
except BaseException as error:
 result.update(status='failed',error=str(error));raise
finally:save()
print(json.dumps({k:v for k,v in result.items() if k not in ('descriptor_boundaries','builds')},indent=2))
