"""Authorized real 32-detector average-median run using the selected Mac launcher.
No build, reconfiguration, installation, raw rewrite or earlier-product cleanup.
"""
import hashlib,json,os,platform,re,socket,stat,subprocess,tempfile,tomllib
from pathlib import Path

repo=Path('/Users/fselman/Developer/wenu-imaging')
project=Path('/Users/fselman/Pictures/OCAM/test_recipes')
orch=project/'orchestration';reduced=project/'reduced/cal/bias'
root=Path('/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb')
build=root/'scalar-qc-qualification-c17/build';recipe=build/'mefpp2/mefpp_bias_recipe'
cache=build/'CMakeCache.txt';launcher=orch/'run-bias.sh';config=orch/'bias-recipe.toml';listing=orch/'bias.list'
qualified=root/'scalar-qc-qualification-c17/median-fixture-retry-a203d040ffe3/qualification.json'
reference=reduced/'CMDP.2026-11-07T21:05:44.919Z.001.fits'
def require(ok,message):
    if not ok:raise RuntimeError(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(p):
    s=p.stat();return dict(bytes=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,inode=s.st_ino)
def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
require(platform.system()=='Darwin' and socket.gethostname().split('.')[0]=='MC02VV0HPHTDG','Expected selected Mac')
require(git('branch','--show-current')=='main' and git('rev-parse','HEAD')=='af24c3699957d03a11f26c0bc47172b202ca0ede','Preserve selected main')
require(not git('status','--porcelain','--untracked-files=all'),'Checkout dirty')
receipt=json.loads(qualified.read_text())
require(receipt['successful'] and receipt['producer_revision']=='74327c49832a9337fad49a0bec1b5fd7af81cde5','Native qualification differs')
require(digest(recipe)==receipt['binary_sha256'] and digest(cache)==receipt['cache_sha256'],'Qualified binary/cache changed')
require(orch.is_dir() and reduced.is_dir() and launcher.is_file() and os.access(launcher,os.X_OK),'Normal directories/launcher missing')
require(config.is_file() and not config.is_symlink(),'Expected regular recipe TOML')
original=config.read_text();cfg=tomllib.loads(original)
require(cfg['bias_recipe_schema_version']==1,'Unexpected recipe schema')
settings=Path(cfg['settings']);settings=settings if settings.is_absolute() else orch/settings
require(settings.resolve()==(orch/'bias.toml').resolve(),'Unexpected processing settings')
native=tomllib.loads(settings.read_text())['native']
require(native.get('MEF.BIAS.MEDIAN.EVEN.HANDLING','average')=='average','Conflicting explicit shared median setting')
for k,v in {'BPM.ENCODING':'binary','BPM.BAD_WHEN':'zero','QC.RON.CLIP.ENABLED':1,'QC.RON.CLIP.LOW':5.0,'QC.RON.CLIP.HIGH':5.0,'QC.RON.CLIP.MAX_ITERATIONS':10}.items():
    require(native.get(k)==v,'Retained processing choice differs: '+k)
bias=cfg['bias']
for k,v in {'mad':True,'ron_pair':[0,1],'high_sigma':5.0,'readout_id':'OMEGACAM:normal:ordered:1x1','bin_x':1,'bin_y':1,'bpm_good_value':1,'bpm_coordinates':'active'}.items():
    require(bias.get(k)==v,'Retained recipe choice differs: '+k)
bpm=Path('/Users/fselman/Pictures/OCAM/wenu-imaging/legacy-bpm-structure-b1h9egzp/prepared/OCAM_BPM_1x1_structural.fits')
require(Path(bias['input_bpm']).resolve()==bpm.resolve(),'Structural BPM differs')
ids=[n for start in (65,73,81,89,69,77,85,93) for n in range(start,start+4)]
require(len(cfg['detector'])==32,'Expected complete detector catalogue')
for i,(d,n) in enumerate(zip(cfg['detector'],ids)):
    require(d['id']==f'ESO_CCD_#{n}' and d['configuration_detector']==i and d['hdus']==[i+1] and d['bpm_hdu']==i+1,'Detector binding differs')
raw=[Path(v.strip()) for v in listing.read_text().splitlines() if v.strip()]
times=['09:50:05.624','09:50:48.373','09:51:31.403','09:52:14.404','09:52:57.394','09:53:40.384','09:54:23.384','09:55:06.394','09:55:49.384','09:56:31.804']
require(raw==[Path('/Users/fselman/Pictures/OCAM/bpm')/('OMEGA.2017-03-13T'+t+'.fits') for t in times],'Ordered raw inputs differ')
require(all(v.stat().st_size==576604800 for v in raw),'Raw input sizes differ')
for suffix in ('.fits','.asdf','.log'):require(reference.with_suffix(suffix).is_file(),'Retained reference missing')
# Verify the one retained launcher command, including its complete absolute paths.
expected=f'exec nice -n 10 {recipe} cal bias --config {config} --bias {listing} --output-dir {reduced} "$@"'
lines=launcher.read_text().splitlines()
require(lines==['#!/bin/bash','set -euo pipefail','test "$(uname -s):$(hostname -s)" = "Darwin:MC02VV0HPHTDG"','export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1',expected],'Launcher differs from retained invocation')
processes=subprocess.check_output(['ps','-axo','pid=,command='],text=True)
require(not [v for v in processes.splitlines() if str(recipe) in v],'Selected recipe already active')
old_files=sorted(v for v in reduced.iterdir() if v.is_file() and v.suffix in ('.fits','.asdf','.log'))
preserved={str(v):identity(v) for v in [*raw,*old_files,settings,bpm,listing,launcher,recipe,cache,qualified]}
# Change only the chosen estimator in the processing envelope; retain all else.
if 'median_even_handling' in bias:
    updated,count=re.subn(r'(?m)^(\s*median_even_handling\s*=)[^\n]*$',r'\1 "average"',original)
    require(count==1,'Ambiguous median setting')
else:
    updated,count=re.subn(r'(?m)^\[bias\]\s*$', '[bias]\nmedian_even_handling = "average"',original)
    require(count==1,'Missing/ambiguous bias table')
changed=tomllib.loads(updated);wanted=tomllib.loads(original);wanted['bias']['median_even_handling']='average'
require(changed==wanted,'Unexpected TOML change')
work=Path(tempfile.mkdtemp(prefix='bias-median-average-real-',dir=orch))
(work/'bias-recipe.toml.before').write_text(original)
(work/'bias-recipe.toml.used').write_text(updated)
(work/'preserved-files.json').write_text(json.dumps(preserved,indent=2)+'\n')
if updated!=original:
    pending=work/'bias-recipe.toml.pending';pending.write_text(updated);pending.chmod(stat.S_IMODE(config.stat().st_mode));os.replace(pending,config)
console=work/'console.log'
print('BACKUP:',work/'bias-recipe.toml.before',flush=True)
print('MEDIAN: average; DETECTORS: all; INPUTS: ten retained raw frames',flush=True)
print('INVOCATION:',launcher,'--detectors all',flush=True)
print('CONSOLE:',console,flush=True)
with console.open('x') as log:
    proc=subprocess.Popen([str(launcher),'--detectors','all'],cwd=orch,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    for line in proc.stdout:
        print(line,end='',flush=True);log.write(line);log.flush()
    code=proc.wait()
unchanged=preserved=={p:identity(Path(p)) for p in preserved}
now=set(v for v in reduced.iterdir() if v.is_file() and v.suffix in ('.fits','.asdf','.log'))
created=sorted(now-set(old_files))
fits_products=[v for v in created if v.suffix=='.fits']
product_set_valid=len(fits_products)==1 and set(created)=={fits_products[0].with_suffix(s) for s in ('.fits','.asdf','.log')}
complete='BIAS_RECIPE_COMPLETE' in console.read_text()
result=dict(successful=code==0 and unchanged and product_set_valid and complete and config.read_text()==updated,exit_status=code,producer_revision=receipt['producer_revision'],binary_sha256=receipt['binary_sha256'],cache_sha256=receipt['cache_sha256'],median_even_handling='average',detectors='all',inputs=list(map(str,raw)),products=list(map(str,created)),reference=str(reference),preserved=unchanged,console=str(console),recipe_config_unchanged_since_launch=config.read_text()==updated)
(work/'run-results.json').write_text(json.dumps(result,indent=2)+'\n')
require(unchanged,'Retained input/product/build identity changed; inspect receipt')
require(config.read_text()==updated,'Recipe configuration changed during run')
require(code==0,'Recipe failed; preserve retained private work and console')
require(product_set_valid,'Unexpected product set')
require(complete,'Missing completion marker')
print('PASS: all-detector recipe complete; raw metadata, earlier products and selected build unchanged.')
print('FITS:',fits_products[0]);print('ASDF:',fits_products[0].with_suffix('.asdf'));print('RECEIPT:',work/'run-results.json')
