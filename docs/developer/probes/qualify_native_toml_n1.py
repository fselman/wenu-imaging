"""N1: pinned private C99 static parser + strict C90 caller; no installation."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import tomllib

REVISION = '4987cf895df61f702d19e3481f34b032ab29ed3a'
PINS = {
    'src/tomlc17.c':'7476923b6c9b8f0858b82b63ed6107f57448882983390e70c31327f7d3e2a362',
    'src/tomlc17.h':'29c0909092f4b23c7edce705167064f4a90548db5334b4aa2cd95d7ad801adb9',
    'LICENSE':'f949d0976f85076c96fc5122f0632b5a1b806d8b2badbe968c42c97230e6e79e',
}
HEADER = '''/* Test-only C90 boundary: no upstream parser types. */
#ifndef N1_BOUNDARY_H
#define N1_BOUNDARY_H
#include <stddef.h>
int n1_parse(const char *path, double *gain, long *detectors,
             char *error, size_t capacity);
#endif
'''
BRIDGE = '''/* Test-only glue, compiled as C99 to consume the upstream header. */
#include "boundary.h"
#include "tomlc17.h"
#include <limits.h>
#include <string.h>
static void n1_error(char *dst, size_t capacity, const char *text)
{
    if (capacity != 0) {
        strncpy(dst, text, capacity - 1);
        dst[capacity - 1] = '\\0';
    }
}
int n1_parse(const char *path, double *gain, long *detectors,
             char *error, size_t capacity)
{
    toml_result_t result;
    toml_datum_t g;
    toml_datum_t d;
    int status;
    result = toml_parse_file_ex(path);
    status = 1;
    if (!result.ok) {
        n1_error(error, capacity, result.errmsg);
    } else {
        g = toml_seek(result.toptab, "instrument.gain");
        d = toml_seek(result.toptab, "instrument.detectors");
        if (g.type != TOML_FP64 || d.type != TOML_INT64) {
            n1_error(error, capacity, "gain/detector type mismatch");
        } else if (d.u.int64 < LONG_MIN || d.u.int64 > LONG_MAX) {
            n1_error(error, capacity, "detector value outside C90 long range");
        } else {
            *gain = g.u.fp64;
            *detectors = (long)d.u.int64;
            status = 0;
        }
    }
    toml_free(result);
    return status;
}
'''
CALLER = '''/* Test-only caller compiled with strict ISO C90 diagnostics. */
#include "boundary.h"
#include <stdio.h>
int main(int argc, char **argv)
{
    double gain;
    long detectors;
    char error[512];
    if (argc != 2) {
        return 2;
    }
    if (n1_parse(argv[1], &gain, &detectors, error, sizeof(error)) != 0) {
        fprintf(stderr, "%s\\n", error);
        return 1;
    }
    printf("{\\"gain\\":%.17g,\\"detectors\\":%ld}\\n", gain, detectors);
    return 0;
}
'''


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_snapshot():
    import importlib.metadata as md
    rows = []
    for d in md.distributions():
        metadata = d.read_text('METADATA') or d.read_text('PKG-INFO') or ''
        record = d.read_text('RECORD') or ''
        rows.append((d.metadata['Name'],d.version,str(d.locate_file('')),
                     hashlib.sha256(metadata.encode()).hexdigest(),hashlib.sha256(record.encode()).hexdigest()))
    return sorted(rows)


def main():
    system, host = platform.system(), platform.node().split('.')[0]
    if (system,host) == ('Darwin','MC02VV0HPHTDG'):
        repo = Path('/Users/fselman/Developer/wenu-imaging')
        prefix = '/Users/fselman/anaconda3/envs/wenu-imaging'
        head = 'b5bfd910614a786b95a598cb6295989c9f6602d6'
        origin = 'git@github.com:fselman/wenu-imaging.git'
        compiler = '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang'
        expected_compiler = 'Apple clang version 15.0.0'
        flags = ['-isysroot','/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk','-arch','x86_64']
    elif (system,host) == ('Linux','chapman4'):
        repo = Path('/home1/fselman/Software/wenu-imaging')
        prefix = '/home/fselman/.conda/envs/wenu-imaging'
        head = '0fa9eaf157359a93f2a9196f6fff05dc3e96e220'
        origin = 'https://github.com/fselman/wenu-imaging.git'
        compiler = '/opt/rh/devtoolset-10/root/usr/bin/gcc'
        expected_compiler = 'gcc (GCC) 10.2.1'
        flags = []
        require(os.confstr('CS_GNU_LIBC_VERSION') == 'glibc 2.17','libc changed')
    else:
        raise RuntimeError('wrong host')
    require(sys.prefix == prefix and sys.version_info[:3] == (3,11,14),'wrong Python')
    require(platform.machine() == 'x86_64','wrong architecture')
    def git(*args):
        return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
    def state():
        return {'root':git('rev-parse','--show-toplevel'),'branch':git('branch','--show-current'),
                'head':git('rev-parse','HEAD'),'upstream':git('rev-parse','--symbolic-full-name','@{upstream}'),
                'origin':git('remote','get-url','origin'),'push_origin':git('remote','get-url','--push','origin'),
                'porcelain':git('status','--porcelain')}
    original_cwd = Path.cwd()
    before_git = state()
    require(Path(before_git['root']).resolve() == repo.resolve() and before_git['branch'] == 'main'
            and before_git['head'] == head and before_git['upstream'] == 'refs/remotes/origin/main'
            and before_git['origin'] == before_git['push_origin'] == origin and not before_git['porcelain'],'checkout changed')
    require(Path(compiler).is_file() and Path('/usr/bin/ar').is_file(),'selected native tools unavailable')
    before_packages = package_snapshot()
    parent = Path.home()/'Software/build/wenu-imaging'
    require(parent.is_dir(),'build parent missing')
    marker = parent/('native-toml-n1-'+host+'-attempt.json')
    require(not marker.exists(),'N1 already attempted; retain and inspect its result before any retry')
    work = Path(tempfile.mkdtemp(prefix='native-toml-n1-'+host+'-',dir=parent)).resolve()
    with marker.open('x') as stream:
        json.dump({'work':str(work),'runner_sha256':sha(Path(__file__))},stream)
    report = {'stage':'native-toml-N1','status':'started','host':platform.node(),'work':str(work),
              'upstream_revision':REVISION,'commands':[],'production_activation':False,'installation_performed':False,
              'python':sys.executable,'packages_before':before_packages,'git_before':before_git,
              'inherited_build_variables_ignored':{k:os.environ[k] for k in ('CC','CFLAGS','CPPFLAGS','LDFLAGS','SDKROOT') if k in os.environ}}
    env = dict(os.environ,PATH='/usr/bin:/bin:/usr/sbin:/sbin',LC_ALL='C')
    for key in ('CC','CXX','CFLAGS','CPPFLAGS','LDFLAGS','SDKROOT','MACOSX_DEPLOYMENT_TARGET','CPATH','C_INCLUDE_PATH','LIBRARY_PATH','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH','GCC_EXEC_PREFIX','COMPILER_PATH'):
        env.pop(key,None)
    def command(label,argv,expected=0):
        log = work/(label+'.log')
        print('Running:',label,'| log:',log,flush=True)
        try:
            with log.open('w') as stream:
                result = subprocess.run(argv,cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=90)
            report['commands'].append({'label':label,'argv':argv,'exit_status':result.returncode,'log':str(log),'log_sha256':sha(log)})
            require(result.returncode == expected,'unexpected exit for '+label)
            return log.read_text(errors='replace')
        except subprocess.TimeoutExpired:
            report['commands'].append({'label':label,'argv':argv,'timed_out':True,'log':str(log),'log_sha256':sha(log)})
            raise
    try:
        print('N1 WORK DIRECTORY:',work,flush=True)
        version = command('compiler-version',[compiler,'--version'])
        require(expected_compiler in version,'compiler version changed')
        report['compiler_sha256'] = sha(Path(compiler).resolve())
        report['archiver_sha256'] = sha(Path('/usr/bin/ar').resolve())
        if system == 'Darwin':
            sdk = command('sdk',['/usr/bin/xcrun','--show-sdk-path']).strip()
            require(sdk == flags[1],'SDK changed')
        # Fetch only pinned external source/license; never run upstream build/install scripts.
        for name,expected_sha in PINS.items():
            path = work/name
            path.parent.mkdir(parents=True,exist_ok=True)
            command('fetch-'+path.name,['/usr/bin/curl','--fail','--location','--connect-timeout','15','--max-time','60',
                    'https://raw.githubusercontent.com/cktan/tomlc17/'+REVISION+'/'+name,'--output',str(path)])
            require(sha(path) == expected_sha,'source identity mismatch: '+name)
        for name,content in [('boundary.h',HEADER),('bridge.c',BRIDGE),('caller.c',CALLER)]:
            (work/name).write_text(content)
        fixture = work/'config with spaces.toml'
        fixture.write_text('[instrument]\ngain=2.1\ndetectors=8\n')
        bad = work/'malformed.toml'
        bad.write_text('[instrument\n')
        protected = {str(p.relative_to(work)):sha(p) for p in (work/'src/tomlc17.c',work/'src/tomlc17.h',work/'LICENSE',work/'boundary.h',work/'bridge.c',work/'caller.c',fixture,bad)}
        common = [compiler,*flags,'-Wall','-Wextra','-pedantic-errors','-O0','-g','-I',str(work/'src'),'-I',str(work)]
        # Explicitly distinct language modes: dependency/glue C99, caller C90.
        command('compile-parser',[*common,'-std=c99','-c',str(work/'src/tomlc17.c'),'-o',str(work/'tomlc17.o')])
        command('archive',['/usr/bin/ar','rcs',str(work/'libtomlc17.a'),str(work/'tomlc17.o')])
        command('compile-bridge',[*common,'-std=c99','-c',str(work/'bridge.c'),'-o',str(work/'bridge.o')])
        command('compile-c90-caller',[*common,'-std=c90','-c',str(work/'caller.c'),'-o',str(work/'caller.o')])
        executable = work/'native-toml-probe'
        command('link',[compiler,*flags,str(work/'caller.o'),str(work/'bridge.o'),str(work/'libtomlc17.a'),'-lm','-o',str(executable)])
        # One successful absolute-path parse through the C90 boundary, plus two error smokes.
        result = json.loads(command('parse-positive',[str(executable),str(fixture)]))
        wanted = tomllib.loads(fixture.read_text())['instrument']
        require(result == wanted and type(result['detectors']) is int and type(result['gain']) is float,'typed result differs from tomllib')
        for label,path in [('parse-missing',work/'absent.toml'),('parse-malformed',bad)]:
            require(command(label,[str(executable),str(path)],expected=1).strip(),'missing error diagnostic')
        dependency_argv = ['/usr/bin/otool','-L',str(executable)] if system == 'Darwin' else ['/usr/bin/ldd',str(executable)]
        runtime = command('linked-runtime',dependency_argv)
        require('not found' not in runtime,'missing linked runtime')
        report.update(status='N1-passed-awaiting-parser-and-ownership-qualification',typed_result=result,
                      protected_inputs_sha256=protected,binary_sha256=sha(executable),library_sha256=sha(work/'libtomlc17.a'),
                      source_sha256=PINS,compiler_version=version,linked_runtime=runtime)
        require(all(sha(work/name)==digest for name,digest in protected.items()),'source/fixture changed')
        report['source_and_fixtures_unchanged'] = True
    except Exception as exc:
        report.update(status='stopped',error=type(exc).__name__+': '+str(exc))
        raise
    finally:
        report['packages_after'] = package_snapshot()
        report['production_package_metadata_unchanged'] = report['packages_after'] == before_packages
        report['git_after'] = state()
        report['checkout_unchanged'] = report['git_after'] == before_git
        report['cwd_unchanged'] = Path.cwd() == original_cwd
        if not report['production_package_metadata_unchanged'] or not report['checkout_unchanged'] or not report['cwd_unchanged']:
            report['status'] = 'stopped-preservation-check'
        (work/'run-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
        print('REPORT:',work/'run-provenance.json',flush=True)
    require(report['status'] == 'N1-passed-awaiting-parser-and-ownership-qualification','N1 did not pass')
    print(json.dumps({k:report[k] for k in ('status','typed_result','production_package_metadata_unchanged','checkout_unchanged','source_and_fixtures_unchanged','installation_performed')},indent=2))


if __name__ == '__main__':
    main()
