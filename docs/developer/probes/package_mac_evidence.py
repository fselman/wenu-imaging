"""Collect retained Mac ASDF reports/logs/tiny fixtures; no test rerun."""
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import tempfile

ROOT = Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J')
WORK = ROOT/'Mac-private-k4i17lwh'
SEMANTIC = '4df8a3c69e541d2d4950e9ffdc86b2b57670a1364682611f6f7fc4e5207daf30'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect(work):
    parent = json.loads((work/'run-provenance.json').read_text())
    require(parent['status'] == 'Mac-passed-awaiting-reverse-interchange','parent status')
    require(all(parent[k] for k in ('production_package_metadata_unchanged','checkout_unchanged','d1_report_unchanged','transfer_unchanged')), 'recorded preservation failed')
    require(not parent['production_activation'], 'unexpected production activation')
    require(parent['production_packages_before'] == parent['production_packages_after'], 'package metadata differs')
    require(sha(work/'functional-report.json') == parent['functional_report_sha256'], 'functional report identity')
    require(sha(work/'interchange-report.json') == parent['interchange_report_sha256'], 'interchange report identity')
    functional = json.loads((work/'functional-report.json').read_text())
    interchange = json.loads((work/'interchange-report.json').read_text())
    require(functional['status'] == 'D2-functional-passed-awaiting-Mac-and-interchange','functional status')
    require(interchange['status'] == 'Chapman4-to-Mac-interchange-passed','interchange status')
    require(not functional['network_attempts'] and not interchange['network_attempts'],'network attempted')
    require(interchange['original_fixture_unchanged'] and interchange['cwd_unchanged'],'interchange preservation failed')
    require(parent['semantic_sha256'] == functional['semantic_sha256'] == interchange['semantic_sha256'] == SEMANTIC,'semantic identity')
    require(sha(work/'functional-probe.py') == 'c44fdc6515e623d31ad5ffcf9a84377abc7deb1f45db1a30bd139be02dd5e0fe','functional probe identity')
    expected_wad = json.loads((work/'fixture with spaces/expected-wad.json').read_text())
    require(hashlib.sha256(json.dumps(expected_wad,sort_keys=True,separators=(',',':')).encode()).hexdigest() == SEMANTIC,'expected WAD identity')
    files = {}
    def add(name, path):
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(work.resolve()),'unsafe input: '+name)
        require(name not in files,'duplicate collection name')
        files[name] = path
    for name in ('run-provenance.json','functional-report.json','interchange-report.json','functional-probe.py','mac-dependency-closure.json'):
        add('Mac/'+name,work/name)
    commands = parent['commands']
    require({c['label'] for c in commands} == {'production-pip-check','private-layout','offline-install','candidate-pip-check','functional-probe','chapman-to-mac-interchange'} and len(commands) == 6, 'command membership')
    for command in commands:
        path = Path(command['log'])
        require(command['exit_status'] == 0 and sha(path) == command['log_sha256'],'command log/exit: '+command['label'])
        add('Mac/'+path.name,path)
    require(len(functional['artifacts']) == 6,'fixture artifact count')
    for name, expected in functional['artifacts'].items():
        path = work/name
        require(path.resolve().is_relative_to((work/'fixture with spaces').resolve()), 'artifact outside fixture')
        require(sha(path) == expected, 'artifact identity: '+name)
        add('Mac/'+name,path)
    for ref in expected_wad['files'].values():
        path = work/'fixture with spaces'/ref['path']
        require(path.resolve().is_relative_to((work/'fixture with spaces').resolve()) and sha(path) == ref['sha256'],'FITS binding identity')
    require(len(files) == 17, 'collection count')
    return files


def main():
    require(platform.system() == 'Darwin' and platform.node().split('.')[0] == 'MC02VV0HPHTDG','wrong host')
    require(sha(ROOT/'chapman4-asdf6-evidence.tar.gz') == '146182a5f21acaeb5436d2ffed4f89d81ecd662f6eb8cf75cf475bed9b6b9358','original transfer changed')
    files = collect(WORK)
    # Copy only explicit byte-verified records and synthetic inputs; no environment/data scan.
    payload = {name:path.read_bytes() for name,path in files.items()}
    manifest = {'schema_version':1,'purpose':'Mac qualification evidence and Mac-created fixture for reverse interchange',
                'semantic_sha256':SEMANTIC,
                'files':{name:{'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)} for name,data in sorted(payload.items())}}
    output = Path(tempfile.mkdtemp(prefix='evidence-transfer-',dir=WORK))
    archive = output/'mac-asdf6-evidence.tar.gz'
    with tarfile.open(archive,'w:gz') as bundle:
        for name,data in sorted(payload.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            bundle.addfile(info,io.BytesIO(data))
        data = (json.dumps(manifest,indent=2)+'\n').encode()
        info = tarfile.TarInfo('manifest.json')
        info.size = len(data)
        bundle.addfile(info,io.BytesIO(data))
    require(all(sha(path) == manifest['files'][name]['sha256'] for name,path in files.items()), 'source changed during collection')
    print('PASS: retained report/log/fixture identities; no tests rerun')
    print('ARCHIVE:',archive)
    print('SHA256:',sha(archive))
    print('BYTES:',archive.stat().st_size)
    print('FILES:',len(files),'plus manifest; environment and real data excluded')


if __name__ == '__main__':
    main()
