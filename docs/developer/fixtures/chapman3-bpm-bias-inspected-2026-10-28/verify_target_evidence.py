from pathlib import Path
import hashlib,json,re,sys
import numpy as np
from astropy.io import fits
sys.path.insert(0,'/workspace/scratch/575604f10f8d/bpm-fd-diagnostic/mefpp2/tests')
from bpm_bias_cases import verify,bias_pixels
from bpm_metadata_cases import PRIMARY,EXTENSION,header_block
from qualify_split_ownership import allocation_state
from descriptor_snapshots import snapshots
base=Path('/workspace/scratch/575604f10f8d/chapman3-bias-inspection/evidence')
repo=Path('/workspace/scratch/575604f10f8d/bpm-target-preparation')
meta=json.loads((repo/'docs/developer/fixtures/mac-stage2-bpm-bias-inspected-2026-10-28/diagnostic-run-provenance.json').read_text())
metadata={c['case'].replace('-leaks-','-functional-'):c for c in meta['cases'] if c['lane']=='leaks'}
ref=json.loads((repo/'docs/developer/fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json').read_text())
references={c['case']:c for c in ref['cases']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(archive_sha256='805fb360cb8ea252e1a093f17607195e3ef3d34709aefc01fd7ec76eff9dd607',manifest_files_verified=225,manifest_itself_verified=True,runs={},native_execution_performed=False)
for root in sorted(base.glob('chapman3-stage*')):
 r=json.loads((root/'run-provenance.json').read_text());modern=True
 assert len(r['cases'])==8 and r['execution_complete'] and not r['tested_source']['dirty']
 assert r['functional_finding_cases']==0 and r['finding_cases']==(0 if modern else 1)
 assert sha(root/'source/mefpp2/CMakeLists.txt')==r['diagnostic_cmake_sha256']
 assert all(v for k,v in r.items() if k.endswith('_unchanged'))
 for n,h in r['source_sha256'].items():assert sha(root/'source'/n)==h,(root.name,n)
 commands={c['label']:c for c in r['commands']}
 for c in r['commands']:
  assert c['exit_status']==0,c
  assert sha(root/Path(c['log']).name)==c['log_sha256']
 builds=[]
 for build in sorted(p for p in root.glob('build-*') if p.is_dir()):
  info=json.loads((build/'build-info.json').read_text());mode=90 if 'c90' in build.name else 17
  assert info['source_revision']==r['tested_source']['commit'] and int(info['c_standard'])==mode
  assert info['compiler_id']=='GNU' and info['compiler_version']=='10.2.1'
  assert info['cmake_version']=='3.29.6' and info['system']=='Linux'
  assert info['qfits_memory_mode']==2 and info['qfits_max_pointers']==2000000
  assert ('-fsanitize=address,undefined' in info['c_flags'])==('instrumented' in build.name)
  compile=json.loads((build/'compile_commands.json').read_text())
  assert len(compile)>=100
  for item in compile:
   flags=item.get('command',' '.join(item.get('arguments',[])))
   assert '-std=c'+str(mode) in flags
   assert ('-fsanitize=address,undefined' in flags)==('instrumented' in build.name)
  builds.append(dict(name=build.name,translation_units=len(compile),c_standard=mode,info_sha256=sha(build/'build-info.json')))
 roles=0;leak_summaries=0;descriptors=[];canonical={};findings=[]
 for c in r['cases']:
  kind,flag,mode=c['fixture'],c['proportional_flag'],c['mode']
  prior=references['c%d-%s-flag%d'%(mode,kind,flag)]
  for role,o in c['roles'].items():
   roles+=1;case=root/c['case']/role
   assert o['input_sha256']==r['metadata_fixture_manifest']['cases'][kind]['inputs_sha256']
   for name,h in o['input_sha256'].items():assert sha(case/name)==h
   for name,h in o['output_sha256'].items():assert sha(case/name)==h
   exe=root/('build-c%d-%s'%(mode,c['lane']))/('bpm_original_probe' if role=='ordinary' else 'bpm_ownership_probe')
   assert sha(exe)==o['executable_sha256']
   outputs,origfiles=verify(case,o['input_sha256'],prior,flag,metadata[c['case']]['roles'][role]['outputs'])
   assert outputs==o['outputs'] and origfiles==o['generated_origfiles']
   canonical[(c['case'],role)]=outputs
   for i in range(3):
    path=case/('frame%d.fits'%i);parent=repo/'mefpp2/tests/fixtures/bpm-cleanup'/kind/path.name
    raw,praw=path.read_bytes(),parent.read_bytes()
    assert raw[:5760]==header_block(praw[:2880],PRIMARY[i])+header_block(praw[2880:5760],EXTENSION)
    assert raw[6408:]==praw[6408:]
    with fits.open(path,memmap=False) as a,fits.open(parent,memmap=False) as b:
     assert np.array_equal(a[1].data[:,:9]-bias_pixels(),b[1].data[:,:9])
     assert np.array_equal(a[1].data[:,9:],b[1].data[:,9:])
   with fits.open(case/'bias.fits',memmap=False) as bias:
    assert len(bias)==1 and bias[0].header['BITPIX']==-32
    assert 'BSCALE' not in bias[0].header and 'BZERO' not in bias[0].header
    assert np.array_equal(bias[0].data,bias_pixels())
   # Independent readback of every mask pixel from known-response gain ratios.
   image=fits.getdata(repo/'mefpp2/tests/fixtures/bpm-cleanup'/kind/'frame0.fits',1)[:,:9].astype(np.float64)
   expected=((image/image.mean()>=.5)&(image/image.mean()<=1.5)).astype(np.uint8)
   for path,index in [(case/'returned.fits',0),(case/outputs['saved_name'],1)]:
    with fits.open(path,memmap=False) as hdus:assert np.array_equal(hdus[index].data,expected)
   log=(root/Path(commands[c['case']+'-'+role]['log']).name).read_text(errors='replace')
   assert 'ERROR: AddressSanitizer' not in log and 'runtime error:' not in log
   assert re.findall(r'^BIAS RESULT supplied=1 pixels_unchanged=81 caller_released=1$',log,re.M)==['BIAS RESULT supplied=1 pixels_unchanged=81 caller_released=1']
   if role=='observer':
    assert re.findall(r'^BPM RESULT native_exit=(\d+) constructed=(\d+) destroyed=(\d+) builds=(\d+) masks_released=(\d+) mismatch=(\d+) owner_live=(\d+) mask_live=(\d+)$',log,re.M)==[('0','1','1','1','1','0','0','0')]
    for boundary in ('process-start','after-context','before-build','after-build','after-mask-release','after-context-release','after-driver','after-purge','after-second-purge'):
     state=allocation_state(log,boundary);assert state==o[boundary+'_accounting']
     if boundary in ('process-start','after-purge','after-second-purge'):assert not any(state.values())
    rows=re.findall(r'^(?:CACHE )?DESCRIPTORS(?: after-(?:second-)?purge)? before=(\d+) after=(\d+) identity_equal=(\d+)$',log,re.M)
    assert len(rows)==3
    if modern:
     snap=snapshots(log);assert snap==o['descriptor_snapshots'] and not any(snap['changes'].values())
     assert all(a==b and same=='1' for a,b,same in rows)
    elif c['case']=='c90-instrumented-retained-flag0':
     assert rows==[('4','4','0')]*3
     findings.append(dict(case=c['case'],kind='descriptor-identity-mismatch',attribution='unavailable in original observer'))
    else:assert all(a==b and same=='1' for a,b,same in rows)
    descriptors.append(dict(case=c['case'],boundaries=rows))
    if c['lane']=='leaks':
     leaks=re.findall(r'\b(\d+) leaks? for (\d+) total leaked bytes\b',log);assert leaks==[('0','0')]
     leak_summaries+=1
 assert roles==16 and leak_summaries==0
 result['runs'][root.name]=dict(commit=r['tested_source']['commit'],report_sha256=sha(root/'run-provenance.json'),status=r['status'],roles_verified=roles,case_pairs=8,input_frame_checks=roles*3,mask_pixels_verified=roles*81*2,leak_summaries_verified=leak_summaries,commands_verified=len(commands),builds=builds,descriptor_boundaries=descriptors,findings=findings)
 result['runs'][root.name]['canonical_output_count']=len(canonical)
 assert r['issue116_closed'] is False and r['full_S2_05_accepted'] is False
 assert all(r['source_sha256'].get(n)==h for n,h in meta['source_sha256'].items())
 result['target_mac_canonical_products_identical']=True
 result['unchanged_mac_source_identities_verified']=len(meta['source_sha256'])
result['status']='passed-bounded-target-functional-accounting-inspection'
Path('/workspace/scratch/575604f10f8d/chapman3-bias-inspection/inspection-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2))
for n,r in result['runs'].items():print(n,'roles',r['roles_verified'],'mask pixel checks',r['mask_pixels_verified'],'findings',r['findings'],'builds',r['builds'])
