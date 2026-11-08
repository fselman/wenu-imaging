"""Test-only retry after the duplicate synthetic path refusal; no native build."""
import argparse,hashlib,json,os,platform,socket,subprocess,sys
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repository',type=Path,required=True)
p.add_argument('--test-revision',required=True)
a=p.parse_args();repo=a.repository.resolve()
producer='74327c49832a9337fad49a0bec1b5fd7af81cde5'
base='af24c3699957d03a11f26c0bc47172b202ca0ede'
root=Path('/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb')
source=root/'scalar-qc-c17-source';q=root/'scalar-qc-qualification-c17';build=q/'build'
previous=q/('median-even-'+producer[:12]);work=q/('median-fixture-retry-'+a.test_revision[:12])
recipe=build/'mefpp2/mefpp_bias_recipe';cache_path=build/'CMakeCache.txt'
asdf_python=Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python')
def require(ok,message):
    if not ok:raise RuntimeError(message)
def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def cache(path):
    return dict(line.split('=',1) for line in path.read_text().splitlines()
                if line and not line.startswith(('#','//')) and '=' in line)
require(platform.system()=='Darwin' and socket.gethostname().split('.')[0]=='MC02VV0HPHTDG','Expected selected Mac')
require(str(repo)=='/Users/fselman/Developer/wenu-imaging','Unexpected checkout')
require(git('remote','get-url','origin')=='git@github.com:fselman/wenu-imaging.git','Unexpected origin')
require(git('branch','--show-current')=='main' and git('rev-parse','HEAD')==base,'Preserve clean main')
require(not git('status','--porcelain','--untracked-files=all'),'Checkout dirty')
subprocess.run(['git','merge-base','--is-ancestor',producer,a.test_revision],cwd=repo,check=True)
names=git('diff','--name-only',producer,a.test_revision).splitlines()
require(names and all(v.startswith(('mefpp2/tests/','docs/')) for v in names),'Retry contains production changes')
require(not work.exists(),'Retain existing retry: '+str(work))
require('Duplicate raw input path' in (previous/'median-recipe.log').read_text(),'Unexpected failed baseline')
for label in ('median-even','average-profile','legacy-profiles'):
    require('PASS:' in (previous/(label+'.log')).read_text(),'Earlier native gate missing: '+label)
require(json.loads((previous/'policy/results.json').read_text())['successful'],'Earlier policy gate failed')
before_cache=cache(cache_path);initial_cache=cache(previous/'CMakeCache.before.txt')
require(before_cache.get('MEFPP_SOURCE_REVISION:STRING')==producer,'Producer cache stamp differs')
require([k for k in sorted(set(before_cache)|set(initial_cache)) if before_cache.get(k)!=initial_cache.get(k)]==['MEFPP_SOURCE_REVISION:STRING'],'Selected configuration changed')
for name in git('ls-tree','-r','--name-only',producer,'--','CMakeLists.txt','mefpp2').splitlines():
    path=Path(name)
    if '/tests/' not in name and (path.name=='CMakeLists.txt' or path.suffix in ('.c','.h','.def','.inc','.cmake') or path.name.endswith('.h.in') or path.name=='qc-product-schema-2.0.0.json'):
        require((source/name).read_bytes()==subprocess.check_output(['git','show',producer+':'+name],cwd=repo),'Production source differs: '+name)
processes=subprocess.check_output(['ps','-axo','pid=,command='],text=True)
require(not [line for line in processes.splitlines() if (str(build) in line or str(source) in line) and any(v in line for v in ('cmake','make','clang','mefpp_bias_recipe','bias_product_qc_probe'))],'Selected build active')
require(recipe.is_file() and asdf_python.is_file(),'Selected runtime missing')
attempts=[previous]+sorted(v for v in q.glob('median-fixture-retry-*') if v.is_dir())
retained={str(v):digest(v) for attempt in attempts for v in attempt.rglob('*') if v.is_file()}
binary_before=digest(recipe);cache_before=digest(cache_path)
work.mkdir()
for name in names:
    if name.startswith('mefpp2/tests/'):
        target=source/name
        if target.exists():
            saved=work/'source-before'/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(target.read_bytes())
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(subprocess.check_output(['git','show',a.test_revision+':'+name],cwd=repo))
priority=os.getpriority(os.PRIO_PROCESS,0)
if priority<10:os.nice(10-priority)
log=work/'median-recipe.log';print('Running corrected recipe contract | log:',log,flush=True)
with log.open('x') as f:
    result=subprocess.run([sys.executable,'-B',str(source/'mefpp2/tests/bias_median_recipe_contract.py'),
        '--work',str(work/'recipe'),'--recipe',str(recipe),'--adapter',str(root/'warning-fix-build/mefpp2/mefpp_m5'),
        '--asdf-python',str(asdf_python),'--revision',producer,'--reuse-fixture',str(previous/'recipe')],
        cwd=build,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1'),stdout=f,stderr=subprocess.STDOUT,timeout=600)
require(digest(recipe)==binary_before and digest(cache_path)==cache_before,'Executable/cache changed')
require(retained=={p:digest(Path(p)) for p in retained},'Failed attempt changed')
require(not git('status','--porcelain','--untracked-files=all'),'Main checkout changed')
require(result.returncode==0,'Corrected contract failed; retain log '+str(log))
receipt=dict(successful=True,producer_revision=producer,test_revision=a.test_revision,
    binary_sha256=binary_before,cache_sha256=cache_before,previous_qualification=str(previous),preserved_attempts=list(map(str,attempts)),
    previous_gates=['median-even','average-profile','legacy-profiles','policy'],
    recipe_results=json.loads((work/'recipe/results.json').read_text()),
    failed_attempt_preserved=True,rebuilt=False,reconfigured=False,raw_observations_accessed=False)
(work/'qualification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(log.read_text())
print('PASS: recipe/cache unchanged; failed attempt, fixtures and main preserved.')
print('RECEIPT:',work/'qualification.json')
