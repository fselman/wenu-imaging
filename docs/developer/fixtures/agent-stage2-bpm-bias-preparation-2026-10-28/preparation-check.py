# Preparation checks only: no native tool, Pycavi or observational processing.
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
r=Path('/workspace/scratch/1f5208e4c0f5/wenu-imaging')
sys.path.insert(0,str(r/'mefpp2/tests'))
from bpm_bias_cases import prepare, bias_pixels
from bpm_metadata_cases import prepare as parent_prepare
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=r/'docs/developer/fixtures/agent-stage2-bpm-bias-preparation-2026-10-28'
report={'schema_version':1,'project':'wenu-imaging','tested_source':{'repository':'https://github.com/fselman/wenu-imaging','branch':subprocess.check_output(['git','branch','--show-current'],cwd=r,text=True).strip(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'dirty':True},'created_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Python-only supplied-bias fixture preparation; no native execution','status':'running','retention_roles':['acceptance_evidence'],'checks':[],'native_execution':False}
(out/'run-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 # Syntax: parse new Python sources without generating bytecode in the checkout.
 for name in ('bpm_bias_cases.py','qualify_bpm_bias.py'):
  ast.parse((r/'mefpp2/tests'/name).read_text())
 report['checks'].append('Python syntax: 2 sources passed')
 # Parent/control/source identities: independently compare all accepted metadata source hashes.
 ref=r/'docs/developer/fixtures/mac-stage2-bpm-metadata-2026-10-27/run-provenance.json'
 assert h(ref)=='26868de58bd3a5c05c82304620d00549b79b2de605bd7bffcbeccd4faa9c308d'
 accepted=json.loads(ref.read_text())
 for name,sha in accepted['source_sha256'].items(): assert h(r/name)==sha,name
 report['checks'].append('All %d accepted metadata source/fixture identities unchanged'%len(accepted['source_sha256']))
 # Deterministic derivatives: retain both independently prepared instances per fixture.
 manifest={'schema_version':1,'purpose':'S2-05 supplied-bias additive derivatives; unchanged overscan/metadata','source_commit':report['tested_source']['commit'],'parent_manifest':'mefpp2/tests/fixtures/bpm-metadata/manifest.json','parent_manifest_sha256':h(r/'mefpp2/tests/fixtures/bpm-metadata/manifest.json'),'bias_pattern':'16 + 8*y + 2*x; [4,5]=4096; zero-based y,x; float32','cases':{}}
 fixture=r/'mefpp2/tests/fixtures/bpm-cleanup'
 for kind in ('retained','known-response'):
  paths=[]
  for lane in ('parent','first','second'):
   d=out/(kind+'-'+lane);d.mkdir(exist_ok=True)
   (d/'run-provenance.json').write_text(json.dumps({'schema_version':1,'tested_source':report['tested_source'],'purpose':lane+' Python fixture preparation','status':'running','retention_roles':['acceptance_evidence'],'parent_manifest':'../run-provenance.json'},indent=2)+'\n')
   paths.append(d)
  parent,a,b=paths
  parent_prepare(parent,fixture,kind)
  aa=prepare(a,fixture,kind);bb=prepare(b,fixture,kind)
  assert aa==bb
  manifest['cases'][kind]={'inputs_sha256':aa,'exact_float_recovery':True}
  for i in range(3):
   p=(parent/('frame%d.fits'%i)).read_bytes();q=(a/('frame%d.fits'%i)).read_bytes()
   assert p[:5760]==q[:5760] and p[6408:]==q[6408:]
   original=np.frombuffer(p[5760:6408],dtype='>f4').reshape(9,18)
   biased=np.frombuffer(q[5760:6408],dtype='>f4').reshape(9,18)
   assert np.array_equal(original[:,9:],biased[:,9:])
   assert np.array_equal(biased[:,:9]-bias_pixels(),original[:,:9])
  for name in ('frames.list','mefpp.paf'):assert (a/name).read_bytes()==(parent/name).read_bytes()
  raw=(a/'bias.fits').read_bytes()
  assert len(raw)==5760 and np.array_equal(np.frombuffer(raw[2880:3204],dtype='>f4').reshape(9,9),bias_pixels())
  # Sensitivity: independent proportional fit, not a production mefpp result.
  def independent_mask(path):
   cube=np.array([np.frombuffer((path/('frame%d.fits'%i)).read_bytes()[5760:6408],dtype='>f4').reshape(9,18)[:,:9] for i in range(3)],dtype=np.float64)
   x=np.median(cube,axis=(1,2))
   gain=np.einsum('i,ijk->jk',x,cube)/np.dot(x,x)
   gain/=gain.mean()
   return (gain>=.5)&(gain<=1.5)
  plain,uncorrected=independent_mask(parent),independent_mask(a)
  assert plain.sum()==79 and not np.array_equal(plain,uncorrected)
  report['checks'].append(kind+': six identical staged hashes; 3 exact frame recoveries; unchanged overscan/headers/padding/PAF/list; skipped subtraction changes independent proportional mask')
  for d in paths:
   p=d/'run-provenance.json';v=json.loads(p.read_text());v['status']='passed';p.write_text(json.dumps(v,indent=2)+'\n')
 (r/'mefpp2/tests/fixtures/bpm-bias/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 report['source_sha256']={str(p.relative_to(r)):h(p) for p in [r/'mefpp2/tests'/n for n in ('bpm_bias_cases.py','qualify_bpm_bias.py','bpm_bias_probe.c','bpm_bias_ownership_probe.c')]}
 report['status']='passed'
except BaseException as e:
 report['status']='failed';report['error']=str(e);raise
finally:
 report['completed_utc']=datetime.now(timezone.utc).isoformat()
 (out/'run-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
