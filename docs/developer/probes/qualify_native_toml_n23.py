"""N2/N3: bounded TOML agreement and tracked ownership, reusing passed N1 library."""
import datetime
import hashlib
import importlib.metadata as md
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import tomllib

DRIVER_SHA = 'e2cce1970f42cfa23576828b97d6fa3274e7468681688dbaa3d894972304ac71'
PINS = {'src/tomlc17.c':'7476923b6c9b8f0858b82b63ed6107f57448882983390e70c31327f7d3e2a362',
        'src/tomlc17.h':'29c0909092f4b23c7edce705167064f4a90548db5334b4aa2cd95d7ad801adb9'}
VALID = {
 'settings': '''[instrument]
name="WFI"
active=true
gain=2.1
chips=["CCD-A", "CCD-P"]
[paths]
raw="data with spaces/área"
[observing]
date=2001-12-11
time=02:01:24.777
local=2001-12-11T02:01:24
utc=2001-12-11T02:01:24.777Z
offset=2001-12-11T02:01:24-03:30
''',
 'numbers': '''lo=-9223372036854775808
hi=9223372036854775807
hex=0x7F
binary=0b1010
octal=0o755
under=1_000_000
exp=6.022e23
negative_zero=-0.0
nan=nan
positive_inf=+inf
negative_inf=-inf
''',
 'strings': '''"quoted.key" = "línea \\u03b1 \\U0001F30C"
"" = ""
"área" = 'C:\\data with spaces'
multiline = """first
second"""
quoted = "a\\tb\\nc\\\"d\\\\e"
''',
 'groups': '''[[science]]
id="s1"
exposure=20.0
[science.selection]
filter="r_SDSS"
[[science]]
id="s2"
exposure=20.0
[science.selection]
filter="r_SDSS"
''',
 'structures': '''a.b.c = 2
inline={x=1, y=[false,true], nested={name="bias"}}
arrays=[[1,2],[3,4]]
empty=[]
''',
 'empty': '',
}
INVALID = {
 'duplicate-key':b'x=1\nx=2\n',
 'duplicate-table':b'[a]\nx=1\n[a]\ny=2\n',
 'malformed':b'[instrument\n',
 'overflow-positive':b'x=9223372036854775808\n',
 'overflow-negative':b'x=-9223372036854775809\n',
 'invalid-date':b'x=2026-02-30\n',
 'invalid-number':b'x=01\n',
 'bad-unicode-escape':b'x="\\U00110000"\n',
 'control-byte':b'x="a\x01b"\n',
 'utf8-overlong':b'x="\xc0\x80"\n',
 'utf8-surrogate':b'x="\xed\xa0\x80"\n',
 'utf8-out-of-range':b'x="\xf4\x90\x80\x80"\n',
}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value):
    if isinstance(value,dict):
        return {'type':'table','value':{k:normalized(v) for k,v in value.items()}}
    if isinstance(value,list):
        return {'type':'array','value':[normalized(v) for v in value]}
    if isinstance(value,bool): kind='boolean'
    elif isinstance(value,int): kind='integer'; value=str(value)
    elif isinstance(value,float):
        kind='float'
        if math.isnan(value): value='nan'
        elif math.isinf(value): value='-inf' if value<0 else 'inf'
    elif isinstance(value,datetime.datetime):
        kind='datetime' if value.tzinfo is None else 'offset-datetime'
        value=value.isoformat(timespec='microseconds')
    elif isinstance(value,datetime.time): kind='time'; value=value.isoformat(timespec='microseconds')
    elif isinstance(value,datetime.date): kind='date'; value=value.isoformat()
    elif isinstance(value,str): kind='string'
    else: raise RuntimeError('unexpected oracle type')
    return {'type':kind,'value':value}


def oracle(text):
    value=tomllib.loads(text)
    def ranges(node):
        if isinstance(node,dict):
            for item in node.values(): ranges(item)
        elif isinstance(node,list):
            for item in node: ranges(item)
        elif type(node) is int and not -(2**63)<=node<2**63:
            raise ValueError('outside shared signed-64 integer contract')
    ranges(value)
    return value


def equal(a,b):
    if isinstance(a,dict): return isinstance(b,dict) and a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,list): return isinstance(b,list) and len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    if isinstance(a,float):
        return isinstance(b,(int,float)) and a==b and (a!=0 or math.copysign(1,a)==math.copysign(1,b))
    return type(a) is type(b) and a==b


def snapshot():
    rows=[]
    for d in md.distributions():
        text=d.read_text('METADATA') or d.read_text('PKG-INFO') or ''
        record=d.read_text('RECORD') or ''
        rows.append((d.metadata['Name'],d.version,str(d.locate_file('')),
                     hashlib.sha256(text.encode()).hexdigest(),hashlib.sha256(record.encode()).hexdigest()))
    return sorted(rows)


def main():
    system,host=platform.system(),platform.node().split('.')[0]
    if (system,host)==('Darwin','MC02VV0HPHTDG'):
        n1=Path('/Users/fselman/Software/build/wenu-imaging/native-toml-n1-MC02VV0HPHTDG-j9uh67in')
        repo=Path('/Users/fselman/Developer/wenu-imaging')
        prefix='/Users/fselman/anaconda3/envs/wenu-imaging'
        expected_head='b5bfd910614a786b95a598cb6295989c9f6602d6'
        origin='git@github.com:fselman/wenu-imaging.git'
        compiler='/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang'
        flags=['-isysroot','/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk','-arch','x86_64']
    elif (system,host)==('Linux','chapman4'):
        n1=Path('/home1/fselman/Software/build/wenu-imaging/native-toml-n1-chapman4-ggagd64k')
        repo=Path('/home1/fselman/Software/wenu-imaging')
        prefix='/home/fselman/.conda/envs/wenu-imaging'
        expected_head='0fa9eaf157359a93f2a9196f6fff05dc3e96e220'
        origin='https://github.com/fselman/wenu-imaging.git'
        compiler='/opt/rh/devtoolset-10/root/usr/bin/gcc'
        flags=[]
        require(os.confstr('CS_GNU_LIBC_VERSION')=='glibc 2.17','libc changed')
    else: raise RuntimeError('wrong host')
    require(sys.prefix==prefix and sys.version_info[:3]==(3,11,14),'wrong Python')
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
    def state():return [git('rev-parse','--show-toplevel'),git('branch','--show-current'),git('rev-parse','HEAD'),git('rev-parse','--symbolic-full-name','@{upstream}'),git('remote','get-url','origin'),git('remote','get-url','--push','origin'),git('status','--porcelain')]
    before_git=state()
    require(Path(before_git[0]).resolve()==repo.resolve() and before_git[1:]==['main',expected_head,'refs/remotes/origin/main',origin,origin,''],'checkout changed')
    driver=Path(__file__).with_name('native_toml_n23.c')
    require(sha(driver)==DRIVER_SHA,'driver changed')
    old=json.loads((n1/'run-provenance.json').read_text())
    require(old['status']=='N1-passed-awaiting-parser-and-ownership-qualification','N1 not passed')
    require(old['production_package_metadata_unchanged'] and old['checkout_unchanged'] and old['source_and_fixtures_unchanged'],'N1 preservation')
    require(sha(Path(compiler).resolve())==old['compiler_sha256'],'compiler identity changed')
    require(sha(n1/'libtomlc17.a')==old['library_sha256'] and sha(n1/'native-toml-probe')==old['binary_sha256'],'N1 binaries changed')
    protected={str(n1/'run-provenance.json'):sha(n1/'run-provenance.json')}
    for name,digest in old['protected_inputs_sha256'].items():
        require(sha(n1/name)==digest,'N1 input changed: '+name)
        protected[str(n1/name)]=digest
    for cmd in old['commands']:
        require(sha(Path(cmd['log']))==cmd['log_sha256'],'N1 log changed')
        require(cmd['exit_status']==(1 if cmd['label'] in ('parse-missing','parse-malformed') else 0),'N1 command status')
        protected[cmd['log']]=cmd['log_sha256']
    for name,digest in PINS.items():require(sha(n1/name)==digest,'pinned source changed')
    protected[str(n1/'libtomlc17.a')]=sha(n1/'libtomlc17.a')
    protected[str(n1/'native-toml-probe')]=sha(n1/'native-toml-probe')
    before_packages=snapshot()
    require(json.dumps(before_packages)==json.dumps(old['packages_after']),'production metadata changed since N1')
    original_cwd=Path.cwd()
    parent=n1.parent
    marker=parent/('native-toml-n23-'+host+'-attempt.json')
    require(not marker.exists(),'N2/N3 already attempted; inspect result before retry')
    work=Path(tempfile.mkdtemp(prefix='native-toml-n23-'+host+'-',dir=parent)).resolve()
    with marker.open('x') as stream:json.dump({'work':str(work),'runner_sha256':sha(Path(__file__))},stream)
    report={'status':'started','stage':'native-toml-N2-N3','host':platform.node(),'work':str(work),
            'n1_report_sha256':protected[str(n1/'run-provenance.json')],'commands':[],'cases':[],
            'installation_performed':False,'production_activation':False,'packages_before':before_packages,
            'diagnostic_scope':'documented parser allocator hooks; no sanitizer or all-process leak claim',
            'parser_options':'check_utf8=true; tracked allocator/free; set once per process before parsing'}
    env=dict(os.environ,PATH='/usr/bin:/bin:/usr/sbin:/sbin',LC_ALL='C')
    for key in ('CC','CXX','CFLAGS','CPPFLAGS','LDFLAGS','SDKROOT','MACOSX_DEPLOYMENT_TARGET','CPATH','C_INCLUDE_PATH','LIBRARY_PATH','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH','GCC_EXEC_PREFIX','COMPILER_PATH'):env.pop(key,None)
    def command(label,argv):
        log=work/(label+'.log')
        print('Running:',label,'| log:',log,flush=True)
        with log.open('w') as stream:r=subprocess.run(argv,cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=90)
        report['commands'].append({'label':label,'argv':argv,'exit_status':r.returncode,'log':str(log),'log_sha256':sha(log)})
        require(r.returncode==0,'failed: '+label)
        return log.read_text(errors='replace')
    try:
        print('N2/N3 WORK DIRECTORY:',work,flush=True)
        for name in ('libtomlc17.a','src/tomlc17.h'):shutil.copyfile(n1/name,work/Path(name).name)
        shutil.copyfile(driver,work/'driver.c')
        executable=work/'native-toml-n23'
        command('compile-link',[compiler,*flags,'-std=c99','-Wall','-Wextra','-pedantic-errors','-O0','-g','-I',str(work),str(work/'driver.c'),str(work/'libtomlc17.a'),'-lm','-o',str(executable)])
        corpus=work/'corpus with spaces';corpus.mkdir()
        expected={}
        for name,text in VALID.items():
            path=corpus/(name+'.toml');path.write_bytes(text.encode('utf-8'))
            wanted=normalized(oracle(text));expected[name]=wanted
            actual=json.loads(command('valid-'+name,[str(executable),'dump',str(path)]))
            require(actual['ok'] and actual['outstanding']==0 and equal(wanted,actual['tree']),'valid semantics/type mismatch: '+name)
            report['cases'].append({'name':name,'expected':'valid','passed':True,'input_sha256':sha(path),'tree':actual['tree']})
        for name,data in INVALID.items():
            path=corpus/(name+'.toml');path.write_bytes(data)
            try:oracle(data.decode('utf-8'))
            except (UnicodeDecodeError,tomllib.TOMLDecodeError,ValueError) as exc:oracle_error=type(exc).__name__
            else:raise RuntimeError('invalid oracle fixture accepted: '+name)
            actual=json.loads(command('invalid-'+name,[str(executable),'dump',str(path)]))
            require(not actual['ok'] and actual['error'] and actual['outstanding']==0,'negative/cleanup mismatch: '+name)
            report['cases'].append({'name':name,'expected':'invalid','oracle_rejection':oracle_error,'passed':True,'input_sha256':sha(path)})
        # Larger partial trees exercise ownership beyond the scalar N1 fixture.
        stress=''.join('[group%d]\nname="chip %d"\nvalues=[1,2,3,4,5,6,7,8]\n'%(i,i) for i in range(12))
        good=corpus/'ownership-valid.toml';good.write_text(stress)
        bad=corpus/'ownership-partial-invalid.toml';bad.write_text(stress+'broken=[1,\n')
        cycles=json.loads(command('ownership-cycles',[str(executable),'cycles',str(good),str(bad)]))
        require(cycles=={'measured_cycles':20,'parse_calls':60,'outstanding':0},'repeat ownership mismatch')
        report['ownership_cycles']=cycles
        injections=[]
        for label,path in [('valid',good),('partial-invalid',bad)]:
            result=json.loads(command('allocation-failures-'+label,[str(executable),'failures',str(path),str(good)]))
            require(0<result['injection_points']<=256 and result['injection_points']==result['injections_consumed'] and result['outstanding']==0,'allocation controls mismatch')
            injections.append(dict(result,case=label))
        report['allocation_controls']=injections
        expected_path=work/'expected-trees.json';expected_path.write_text(json.dumps(expected,sort_keys=True,indent=2)+'\n')
        report['semantic_sha256']=hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        report['artifacts']={str(p.relative_to(work)):sha(p) for p in work.rglob('*') if p.is_file()}
        report['status']='N2-N3-passed-awaiting-paired-evidence-review'
    except Exception as exc:
        report.update(status='stopped',error=type(exc).__name__+': '+str(exc));raise
    finally:
        report['packages_after']=snapshot()
        report['production_package_metadata_unchanged']=before_packages==report['packages_after']
        report['checkout_unchanged']=state()==before_git
        report['n1_evidence_unchanged']=all(sha(Path(name))==digest for name,digest in protected.items())
        report['cwd_unchanged']=Path.cwd()==original_cwd
        if not all(report[k] for k in ('production_package_metadata_unchanged','checkout_unchanged','n1_evidence_unchanged','cwd_unchanged')):report['status']='stopped-preservation-check'
        (work/'run-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
        print('REPORT:',work/'run-provenance.json',flush=True)
    require(report['status']=='N2-N3-passed-awaiting-paired-evidence-review','N2/N3 did not pass')
    print(json.dumps({k:report[k] for k in ('status','semantic_sha256','ownership_cycles','allocation_controls','production_package_metadata_unchanged','checkout_unchanged','n1_evidence_unchanged')},indent=2))


if __name__=='__main__':main()
