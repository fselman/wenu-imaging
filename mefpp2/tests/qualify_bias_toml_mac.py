"""Update only the selected mutable Mac source/build; run bounded tiny checks.
No fresh CMake build, dependency installation, observational reduction or cleanup.
"""
import argparse,hashlib,json,os,platform,re,shutil,socket,subprocess,sys
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repository',type=Path,required=True)
p.add_argument('--revision',required=True)
p.add_argument('--preflight',action='store_true')
a=p.parse_args()
repo=a.repository.resolve()
base='b1f2f50960d64fd17bc1c03fa2bbd70fc9ae1769'
root=Path('/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb')
q=root/'scalar-qc-qualification-c17';build=q/'build';cache_path=build/'CMakeCache.txt'
source=root/'scalar-qc-c17-source';cmake=Path('/opt/local/bin/cmake')
recipe=build/'mefpp2/mefpp_bias_recipe'
asdf_python=Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python')
work=q/('toml-provenance-'+a.revision[:12])
def require(ok,message):
    if not ok:raise RuntimeError(message)
def git(*args):
    return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def cache():
    data={}
    for line in cache_path.read_text().splitlines():
        if line and not line.startswith(('#','//')) and '=' in line:
            k,v=line.split('=',1)
            if ':' in k:data[k]=v
    return data
def setting(c,name):
    values=[v for k,v in c.items() if k.split(':',1)[0]==name]
    require(len(values)==1,'Missing/ambiguous cache setting: '+name)
    return values[0]
require(platform.system()=='Darwin' and socket.gethostname().split('.')[0]=='MC02VV0HPHTDG','Expected selected Intel Mac')
require(str(repo)=='/Users/fselman/Developer/wenu-imaging','Unexpected checkout')
require(git('remote','get-url','origin')=='git@github.com:fselman/wenu-imaging.git','Unexpected origin')
require(git('branch','--show-current')=='main' and git('rev-parse','HEAD')==base,'Preserve expected clean main')
require(not git('status','--porcelain','--untracked-files=all'),'Checkout is dirty')
require(re.fullmatch('[0-9a-f]{40}',a.revision),'Require full revision')
subprocess.run(['git','merge-base','--is-ancestor',base,a.revision],cwd=repo,check=True)
before=cache()
for key,value in {
 'CMAKE_HOME_DIRECTORY':str(source),'CMAKE_COMMAND':str(cmake),
 'CMAKE_C_COMPILER':'/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang',
 'CMAKE_MAKE_PROGRAM':'/usr/bin/make','CMAKE_GENERATOR':'Unix Makefiles',
 'CMAKE_BUILD_TYPE':'Release','CMAKE_C_FLAGS':'','CMAKE_EXE_LINKER_FLAGS':'',
 'CMAKE_OSX_ARCHITECTURES':'','CMAKE_OSX_DEPLOYMENT_TARGET':'','MEFPP_C_STANDARD':'17','MEFPP_SOURCE_REVISION':base,
 'MEFPP_BUILD_BIAS_RECIPE':'ON'}.items():
    require(setting(before,key)==value,'Selected configuration differs: '+key)
require(setting(before,'CMAKE_OSX_SYSROOT')=='/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.2.sdk','SDK differs')
require(setting(before,'MEFPP_ASDF_PREFIX')=='/Users/fselman/Software/build/wenu-imaging/mac-asdf16-streams-o8KPDcUm/libasdf-environment','Native ASDF prefix differs')
require(digest(recipe)=='4fc47f0e33e379864e4850f10ae78f12a22e0b15dce874cc8e23c606b8422e46','Selected recipe changed')
require(asdf_python.is_file(),'Qualified ASDF interpreter missing')
require((root/'warning-fix-build/mefpp2/mefpp_m5').is_file(),'Retained qualified reference adapter missing')
require(Path(setting(before,'MEFPP_ASDF_PREFIX'),'include/asdf').is_dir(),'Retained native ASDF headers missing')
require(Path(setting(before,'MEFPP_ASDF_LIBRARY')).is_file(),'Retained native ASDF library missing')
processes=subprocess.check_output(['ps','-axo','pid=,command='],text=True)
active=[line for line in processes.splitlines() if (str(build) in line or str(source) in line)
        and any(name in line for name in ('cmake','make','clang','mefpp_bias_recipe','bias_product_qc_probe'))]
require(not active,'Selected source/build active: '+repr(active))
# Verify production inputs before applying only the candidate's changes.
for name in git('ls-tree','-r','--name-only',base,'--','CMakeLists.txt','mefpp2').splitlines():
    path=Path(name)
    if '/tests/' not in name and (path.name=='CMakeLists.txt' or path.suffix in ('.c','.h','.def','.inc','.cmake') or path.name.endswith('.h.in')):
        require((source/name).read_bytes()==subprocess.check_output(['git','show',base+':'+name],cwd=repo),'Source changed: '+name)
names=git('diff','--name-only',base,a.revision,'--','mefpp2').splitlines()
require(names and all(git('cat-file','-t',a.revision+':'+name)=='blob' for name in names),'Unexpected source deletion')
print('SOURCE:',source,'\nBUILD:',build,'\nCACHE SHA256:',digest(cache_path))
print('PATCH FILES:',json.dumps(names,indent=2))
print('CANDIDATE:',a.revision)
require(not work.exists(),'Retain existing attempt: '+str(work))
if a.preflight:
    print('PASS: read-only preflight; no files changed.')
    raise SystemExit(0)
work.mkdir()
shutil.copy2(recipe,work/'mefpp_bias_recipe.before')
shutil.copy2(cache_path,work/'CMakeCache.before.txt')
# Retain changed source bytes before updating this same mutable source.
for name in names:
    dest=source/name
    if dest.exists():
        saved=work/'source-before'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,saved)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(subprocess.check_output(['git','show',a.revision+':'+name],cwd=repo))
priority=os.getpriority(os.PRIO_PROCESS,0)
if priority<10:os.nice(10-priority)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
def run(name,argv,timeout):
    log=work/(name+'.log');print('Running:',name,'| log:',log,flush=True)
    with log.open('x') as f:
        r=subprocess.run(list(map(str,argv)),cwd=build,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    require(r.returncode==0,name+' failed; retain log '+str(log))
    return log
# Deliberate revision update; same cache/compiler/SDK/dependencies. Existing
# target-source changes regenerate build files; no new target or build tree.
run('revision-stamp',[cmake,'-DMEFPP_SOURCE_REVISION:STRING='+a.revision,build],120)
after=cache()
changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
require(changed==['MEFPP_SOURCE_REVISION:STRING'],'Unexpected cache changes: '+repr(changed))
log=run('build',[cmake,'--build',build,'--target','mefpp_bias_recipe','bias_product_qc_probe','--parallel','2'],600)
require(not re.search(r'\bwarning:',log.read_text(),re.I),'Build warnings; inspect '+str(log))
headers=work/'headers';headers.mkdir()
run('headers',[build/'mefpp2/bias_product_qc_probe','headers',source/'mefpp2/ins/mef/config/omegacam.paf',headers],60)
run('recipe-contract',[sys.executable,'-B',source/'mefpp2/tests/bias_toml_recipe_contract.py',
    '--work',work/'checks','--recipe',recipe,'--adapter',root/'warning-fix-build/mefpp2/mefpp_m5',
    '--asdf-python',asdf_python,'--revision',a.revision],600)
require(cache()==after,'Cache changed during tests')
require(not git('status','--porcelain','--untracked-files=all'),'Main checkout changed')
receipt=dict(successful=True,source_revision=a.revision,binary_sha256=digest(recipe),
             changed_cache_keys=changed,recipe_results=json.loads((work/'checks/bias-toml-results.json').read_text()),
             raw_observations_accessed=False,installed=False)
(work/'qualification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS: native TOML selection and selected provenance, one/two-detector FITS/ASDF.')
print('RECIPE:',recipe,'\nRECEIPT:',work/'qualification.json')
