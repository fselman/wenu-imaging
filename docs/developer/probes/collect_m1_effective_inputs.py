"""Collect retained pilot text inputs for M1; never read FITS or launch native tools."""
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile

INSTALL=Path('/Users/fselman/Software/build/wenu-imaging/mac-stage2-1-install-rBleOnWB')
PILOT=INSTALL/'pilot-5-per-instrument'
HEAD='7341c895e9e1eb7008915e1e2cf961532b7eb8a6'
MAX_FILE=16*1024*1024
MAX_TOTAL=96*1024*1024
MAX_ENTRIES=50000


def require(ok,message):
    if not ok:raise RuntimeError(message)


def sha(data):return hashlib.sha256(data).hexdigest()


def select_partition_text(name):
    return (name.endswith('.paf') or name.endswith('.list')
            or name in ('pycavi.cfg','omegacam.cfg','wfi.cfg','mefpp_command.txt','mefpp.log'))


def main():
    require(platform.system()=='Darwin' and platform.node().split('.')[0]=='MC02VV0HPHTDG','wrong host')
    require(sys.prefix=='/Users/fselman/anaconda3/envs/wenu-imaging' and sys.version_info[:3]==(3,11,14),'wrong Python')
    repo=Path('/Users/fselman/Developer/wenu-imaging')
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
    def state():return [git('rev-parse','--show-toplevel'),git('branch','--show-current'),git('rev-parse','HEAD'),git('rev-parse','--symbolic-full-name','@{upstream}'),git('remote','get-url','origin'),git('remote','get-url','--push','origin'),git('status','--porcelain')]
    before=state();origin='git@github.com:fselman/wenu-imaging.git'
    require(Path(before[0]).resolve()==repo.resolve() and before[1:]==['main',HEAD,'refs/remotes/origin/main',origin,origin,''],'checkout changed')
    require(INSTALL.is_dir() and PILOT.is_dir(),'retained pilot missing')
    payload={};sources={};skipped=[];missing=[];total=0;visited=0
    def add(label,path):
        nonlocal total
        if not path.exists():missing.append(str(path));return
        if path.is_symlink():skipped.append({'path':str(path),'reason':'symlink not followed','target':os.readlink(path)});return
        require(path.is_file(),'not a regular file: '+str(path))
        require(not path.name.lower().endswith(('.fits','.fit','.fts','.fz','.gz')),'image/archive input forbidden')
        require(path.stat().st_size<=MAX_FILE,'text file exceeds bound: '+str(path))
        data=path.read_bytes()
        require(b'\0' not in data,'binary input refused: '+str(path))
        data.decode('utf-8')  # Never silently replace undecodable configuration bytes.
        require(label not in payload,'duplicate label')
        total+=len(data);require(total<=MAX_TOTAL,'text collection exceeds bound')
        payload[label]=data;sources[label]={'path':str(path),'sha256':sha(data),'bytes':len(data)}
    projects={}
    for instrument in ('omegacam','wfi'):
        project=PILOT/instrument
        require(project.is_dir(),'project missing: '+instrument)
        inventory={'project':str(project),'commands':[],'pafs':[],'root_entries':sorted(p.name for p in project.iterdir())}
        # Only original native project trees; normalized pixel/WCS directories are excluded.
        for base,dirs,files in os.walk(project,followlinks=False):
            for name in dirs:
                path=Path(base)/name
                if path.is_symlink():skipped.append({'path':str(path),'reason':'directory symlink not followed','target':os.readlink(path)})
            dirs[:]=sorted(d for d in dirs if d not in ('normalized','.git','__pycache__') and not (Path(base)/d).is_symlink())
            for name in sorted(files):
                visited+=1;require(visited<=MAX_ENTRIES,'directory traversal exceeds bound')
                path=Path(base)/name
                relative=path.relative_to(project)
                if select_partition_text(name):
                    label=instrument+'/'+relative.as_posix();add(label,path)
                    if label in payload and name.endswith('.paf'):inventory['pafs'].append({'path':str(relative),'sha256':sources[label]['sha256']})
                    if label in payload and name=='mefpp_command.txt':inventory['commands'].append({'partition':str(relative.parent),'retained_last_command':payload[label].decode('utf-8')})
                elif path.parent==project and name.endswith('.json'):
                    add(instrument+'/'+relative.as_posix(),path)
        # Parent logs retain sequences that a last-command file cannot reconstruct.
        add(instrument+'/logs/native-stage.log',project/'logs/native-stage.log')
        for name in ('normalization-report.json','astrometry-report.json'):
            add(instrument+'/normalized/'+name,project/'normalized'/name)
        require(inventory['pafs'] and inventory['commands'],'native PAF/command evidence missing: '+instrument)
        projects[instrument]=inventory
    add('installation/pycavi_astrosoft.cfg',INSTALL/'pycavi_astrosoft.cfg')
    add('current-user/pycavi_astrosoft.cfg',Path('/Users/fselman/.pycavi/pycavi_astrosoft.cfg'))
    for name in ('run-provenance.json','installation-manifest.json','install-manifest.json'):
        path=INSTALL/name
        if path.is_file():add('installation/'+name,path)
    # Repository templates are comparison inputs, never a substitute for partition-local values.
    configs=repo/'Pycavi2/pycavi/config'
    for name in ('pycavi.cfg','omegacam.cfg','wfi.cfg'):
        add('repository-config/'+name,configs/name)
    for path in sorted(configs.glob('*.paf')):
        add('repository-config/'+path.name,path)
    native=INSTALL/'native/bin/mefpp'
    native_sha=sha(native.read_bytes())
    require(native_sha=='5acd03bc33f1413e475c71130af9f4d7bb81e9547092417fbec6f2b1a44e8d01','retained private engine identity changed')
    # The text snapshot is byte-preserving, not a PAF decoder/effective-value claim.
    require(all(sha(Path(row['path']).read_bytes())==row['sha256'] for row in sources.values()),'source changed while reading')
    require(state()==before,'checkout changed during collection')
    record={'schema_version':1,'status':'M1-text-input-lock-collected-awaiting-interpretation','host':platform.node(),
            'checkout':HEAD,'git_state':before,'scope':'text/provenance snapshot only; no FITS read, native execution or reduction',
            'projects':projects,'sources':sources,'skipped':skipped,'missing_optional':missing,
            'retained_private_engine_sha256':native_sha,'source_bytes_unchanged':True,'checkout_unchanged':True,
            'limits':{'max_file':MAX_FILE,'max_total':MAX_TOTAL,'max_entries':MAX_ENTRIES},
            'caveats':['last-command files may have been overwritten by later operations; inspect retained logs',
                       'current retained files do not alone prove every historical effective setting',
                       'source occurrences are not typed/runtime decoder semantics; resolve precedence/defaults explicitly']}
    record_data=(json.dumps(record,indent=2)+'\n').encode();payload['input-lock.json']=record_data
    manifest={'schema_version':1,'purpose':'M1 retained native text inputs, not scientific data',
              'files':{name:{'sha256':sha(data),'bytes':len(data)} for name,data in sorted(payload.items())}}
    output=Path(tempfile.mkdtemp(prefix='m1-effective-inputs-',dir=INSTALL.parent))
    archive=output/'mac-m1-effective-inputs.tar.gz'
    with tarfile.open(archive,'w:gz') as bundle:
        for name,data in sorted(payload.items()):
            info=tarfile.TarInfo(name);info.size=len(data);bundle.addfile(info,io.BytesIO(data))
        data=(json.dumps(manifest,indent=2)+'\n').encode();info=tarfile.TarInfo('manifest.json');info.size=len(data);bundle.addfile(info,io.BytesIO(data))
    print(json.dumps({'status':record['status'],'projects':{name:{'partition_pafs':len(v['pafs']),'retained_commands':len(v['commands'])} for name,v in projects.items()},'text_files':len(sources),'text_bytes':total,'missing_optional':missing,'skipped_symlinks':skipped},indent=2))
    print('ARCHIVE:',archive)
    print('SHA256:',sha(archive.read_bytes()))
    print('BYTES:',archive.stat().st_size)


if __name__=='__main__':main()
