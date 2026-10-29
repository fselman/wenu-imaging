"""Read-only compiler/Git preflight for the bounded native TOML trial."""
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def main():
    host = platform.node().split('.')[0]
    targets = {
        ('Darwin','MC02VV0HPHTDG'): ('/Users/fselman/Developer/wenu-imaging',
            '/Users/fselman/anaconda3/envs/wenu-imaging','b5bfd910614a786b95a598cb6295989c9f6602d6',
            'git@github.com:fselman/wenu-imaging.git'),
        ('Linux','chapman4'): ('/home1/fselman/Software/wenu-imaging',
            '/home/fselman/.conda/envs/wenu-imaging','0fa9eaf157359a93f2a9196f6fff05dc3e96e220',
            'https://github.com/fselman/wenu-imaging.git'),
    }
    if (platform.system(),host) not in targets:
        raise RuntimeError('wrong host')
    root, prefix, head, origin = targets[(platform.system(),host)]
    if sys.prefix != prefix or sys.version_info[:3] != (3,11,14):
        raise RuntimeError('unexpected Python')
    def command(argv):
        try:
            r = subprocess.run(argv,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=15)
            return {'argv':argv,'exit_status':r.returncode,'output':r.stdout.strip()[:6000]}
        except (OSError,subprocess.TimeoutExpired) as exc:
            return {'argv':argv,'error':str(exc)}
    def git(*args):
        return subprocess.check_output(['git','-C',root,*args],text=True).strip()
    state = {'root':git('rev-parse','--show-toplevel'),'branch':git('branch','--show-current'),
             'head':git('rev-parse','HEAD'),'upstream':git('rev-parse','--symbolic-full-name','@{upstream}'),
             'origin_fetch':git('remote','get-url','origin'),'origin_push':git('remote','get-url','--push','origin'),
             'porcelain':git('status','--porcelain')}
    if not (Path(state['root']).resolve() == Path(root).resolve() and state['branch'] == 'main'
            and state['head'] == head and state['upstream'] == 'refs/remotes/origin/main'
            and state['origin_fetch'] == state['origin_push'] == origin and not state['porcelain']):
        raise RuntimeError('actual checkout differs: '+json.dumps(state))
    candidates = {path for name in ('cc','gcc','clang','cmake','make') if (path := shutil.which(name))}
    # Inspect known possible compiler locations only; do not install/activate a toolchain.
    extra = ('/usr/bin/cc','/usr/bin/gcc','/usr/bin/clang',
             '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang',
             '/opt/local/bin/gcc-mp-13') if platform.system() == 'Darwin' else (
             '/usr/bin/cc','/usr/bin/gcc','/opt/rh/devtoolset-10/root/usr/bin/gcc')
    candidates.update(p for p in extra if Path(p).is_file())
    tools = [dict(command([p,'--version']),resolved=str(Path(p).resolve())) for p in sorted(candidates)]
    report = {'scope':'read-only inventory; no compilation, linking, installation or parser execution',
              'host':platform.node(),'os':platform.platform(),'machine':platform.machine(),
              'python':sys.executable,'python_version':sys.version,'prefix':sys.prefix,
              'git':state,'tools':tools,'archiver':shutil.which('ar'),
              'build_environment':{k:os.environ[k] for k in ('CC','CFLAGS','CPPFLAGS','LDFLAGS','SDKROOT','MACOSX_DEPLOYMENT_TARGET') if k in os.environ}}
    if platform.system() == 'Linux':
        report['libc'] = os.confstr('CS_GNU_LIBC_VERSION')
    elif Path('/usr/bin/xcrun').is_file():
        report['sdk'] = command(['/usr/bin/xcrun','--show-sdk-path'])
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
