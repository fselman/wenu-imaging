"""N4: verify and collect retained native TOML evidence; no build/test/import of parser."""
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import tempfile

SEMANTIC='40b47916247e105606bcaaac47a893871edc4e37f8f05f87b490267dc696edb9'


def require(ok,message):
    if not ok:raise RuntimeError(message)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def collect(n1,n23):
    a=json.loads((n1/'run-provenance.json').read_text())
    b=json.loads((n23/'run-provenance.json').read_text())
    require(a['status']=='N1-passed-awaiting-parser-and-ownership-qualification','N1 status')
    require(b['status']=='N2-N3-passed-awaiting-paired-evidence-review','N2/N3 status')
    require(all(a[k] for k in ('production_package_metadata_unchanged','checkout_unchanged','source_and_fixtures_unchanged','cwd_unchanged')),'N1 preservation')
    require(all(b[k] for k in ('production_package_metadata_unchanged','checkout_unchanged','n1_evidence_unchanged','cwd_unchanged')),'N2/N3 preservation')
    require(not a['installation_performed'] and not b['installation_performed'] and not a['production_activation'] and not b['production_activation'],'unexpected installation/activation')
    require(a['packages_before']==a['packages_after']==b['packages_before']==b['packages_after'],'recorded package metadata differs')
    require(sha(n1/'run-provenance.json')==b['n1_report_sha256'],'N1 report link')
    require(sha(n1/'libtomlc17.a')==a['library_sha256'] and sha(n1/'native-toml-probe')==a['binary_sha256'],'N1 binary identity')
    require(a['typed_result']=={'gain':2.1,'detectors':8},'N1 typed result')
    files={}
    def add(label,path,root):
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),'unsafe input: '+label)
        require(label not in files,'duplicate member: '+label)
        files[label]=path
    add('N1/run-provenance.json',n1/'run-provenance.json',n1)
    add('N23/run-provenance.json',n23/'run-provenance.json',n23)
    for name,digest in a['protected_inputs_sha256'].items():
        path=n1/name;require(sha(path)==digest,'N1 input changed: '+name);add('N1/'+name,path,n1)
    for command in a['commands']:
        expected=1 if command['label'] in ('parse-missing','parse-malformed') else 0
        path=Path(command['log'])
        require(command['exit_status']==expected and sha(path)==command['log_sha256'],'N1 command: '+command['label'])
        add('N1/'+path.name,path,n1)
    require(len(b['commands'])==22 and len(b['cases'])==18,'case/command count')
    for command in b['commands']:
        path=Path(command['log'])
        require(command['exit_status']==0 and sha(path)==command['log_sha256'],'N2/N3 command: '+command['label'])
    # Check every recorded artifact, including native payloads that are excluded from transfer.
    for name,digest in b['artifacts'].items():
        path=n23/name
        require(path.resolve().is_relative_to(n23.resolve()) and sha(path)==digest,'N2/N3 artifact: '+name)
        if name not in ('native-toml-n23','libtomlc17.a'):
            add('N23/'+name,path,n23)
    expected=json.loads((n23/'expected-trees.json').read_text())
    require(hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest()==b['semantic_sha256']==SEMANTIC,'semantic digest')
    require(len(expected)==6 and all(case['passed'] for case in b['cases']),'case results')
    for case in b['cases']:
        path=n23/'corpus with spaces'/(case['name']+'.toml')
        require(sha(path)==case['input_sha256'],'case input changed')
        prefix='valid-' if case['expected']=='valid' else 'invalid-'
        result=json.loads((n23/(prefix+case['name']+'.log')).read_text())
        require(result['outstanding']==0 and result['ok']==(case['expected']=='valid'),'case allocation/status')
        if case['expected']=='valid':
            require(result['tree']==case['tree']==expected[case['name']],'recorded typed tree differs')
        else:require(bool(result['error']),'missing negative diagnostic')
    require(b['ownership_cycles']==json.loads((n23/'ownership-cycles.log').read_text())=={'measured_cycles':20,'parse_calls':60,'outstanding':0},'cycles')
    for case,points in [('valid',119),('partial-invalid',120)]:
        result=json.loads((n23/('allocation-failures-'+case+'.log')).read_text())
        require(dict(result,case=case) in b['allocation_controls'],'allocation log/report link')
        require(result=={'injection_points':points,'injections_consumed':points,'rejected':points,'equivalent_fallbacks':0,'outstanding':0},'allocation counts')
    return files


def main():
    target=(platform.system(),platform.node().split('.')[0])
    if target==('Darwin','MC02VV0HPHTDG'):
        parent=Path('/Users/fselman/Software/build/wenu-imaging')
        n1=parent/'native-toml-n1-MC02VV0HPHTDG-j9uh67in'
        n23=parent/'native-toml-n23-MC02VV0HPHTDG-79x2yt3h'
        label='mac'
    elif target==('Linux','chapman4'):
        parent=Path('/home1/fselman/Software/build/wenu-imaging')
        n1=parent/'native-toml-n1-chapman4-ggagd64k'
        n23=parent/'native-toml-n23-chapman4-zaup3mhq'
        label='chapman4'
    else:raise RuntimeError('wrong host')
    files=collect(n1,n23)
    payload={name:path.read_bytes() for name,path in files.items()}
    manifest={'schema_version':1,'purpose':'paired native TOML N1/N2/N3 evidence review','host':platform.node(),
              'semantic_sha256':SEMANTIC,'files':{name:{'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)} for name,data in sorted(payload.items())}}
    output=Path(tempfile.mkdtemp(prefix='evidence-transfer-',dir=n23))
    archive=output/(label+'-native-toml-evidence.tar.gz')
    with tarfile.open(archive,'w:gz') as bundle:
        for name,data in sorted(payload.items()):
            info=tarfile.TarInfo(name);info.size=len(data);bundle.addfile(info,io.BytesIO(data))
        data=(json.dumps(manifest,indent=2)+'\n').encode()
        info=tarfile.TarInfo('manifest.json');info.size=len(data);bundle.addfile(info,io.BytesIO(data))
    require(all(sha(path)==manifest['files'][name]['sha256'] for name,path in files.items()),'source changed during collection')
    print('PASS: native TOML reports/logs/fixtures verified; no tests rerun')
    print('ARCHIVE:',archive)
    print('SHA256:',sha(archive))
    print('BYTES:',archive.stat().st_size)
    print('FILES:',len(files),'plus manifest; native binaries/libraries and real data excluded')


if __name__=='__main__':main()
