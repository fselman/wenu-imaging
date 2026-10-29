"""Package only retained reports/logs/wheels/tiny fixtures; no test rerun."""
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import tempfile

if platform.system() != 'Linux' or platform.node().split('.')[0] != 'chapman4':
    raise SystemExit('STOP: run evidence packaging on chapman4')

d1 = Path('/home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC')
d2 = d1/'D2-private-s6qsxbqf'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(d1/'run-provenance.json') == 'd2292e08cc5c143559f49373a2f52d19a971459c6b62cfa6ba1fb400d0a1c4e6'
a = json.loads((d1/'run-provenance.json').read_text())
b = json.loads((d2/'run-provenance.json').read_text())
assert b['status'] == 'Chapman4-D2-passed-awaiting-Mac-and-interchange'
assert all(b[k] for k in ('production_package_metadata_unchanged','checkout_unchanged','d1_report_unchanged'))
assert not b['production_activation']
assert sha(d2/'functional-report.json') == b['functional_report_sha256']
f = json.loads((d2/'functional-report.json').read_text())
assert f['status'] == 'D2-functional-passed-awaiting-Mac-and-interchange'
assert f['semantic_sha256'] == b['semantic_sha256'] == '4df8a3c69e541d2d4950e9ffdc86b2b57670a1364682611f6f7fc4e5207daf30'
assert not f['network_attempts']
files = {}
def add(label, path, root):
    assert path.is_file() and not path.is_symlink()
    assert path.resolve().is_relative_to(root.resolve())
    assert label not in files
    files[label] = path
for name in ('run-provenance.json','candidate-wheels.txt','prepare_chapman_asdf6.py','install_chapman_asdf6.py','asdf6_functional_probe.py'):
    add('D1/'+name,d1/name,d1)
for node in a['dependency_closure'].values():
    if node['source'] == 'downloaded-wheel':
        p = Path(node['artifact'])
        assert sha(p) == node['sha256']
        add('D1/wheels/'+p.name,p,d1/'wheels')
for name in ('run-provenance.json','functional-report.json','functional-probe.py'):
    add('D2/'+name,d2/name,d2)
for command in b['commands']:
    p = Path(command['log'])
    assert sha(p) == command['log_sha256']
    add('D2/'+p.name,p,d2)
for name, expected in f['artifacts'].items():
    p = d2/name
    assert sha(p) == expected
    add('D2/'+name,p,d2/'fixture with spaces')
manifest = {'schema_version':1,'purpose':'Chapman ASDF qualification evidence and tiny interchange fixtures',
            'semantic_sha256':f['semantic_sha256'],
            'files':{name:{'sha256':sha(path),'bytes':path.stat().st_size} for name,path in sorted(files.items())}}
output_dir = Path(tempfile.mkdtemp(prefix='evidence-transfer-',dir=d2))
archive = output_dir/'chapman4-asdf6-evidence.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for name,path in sorted(files.items()):
        tar.add(path,arcname=name,recursive=False)
    content = (json.dumps(manifest,indent=2)+'\n').encode()
    info = tarfile.TarInfo('manifest.json')
    info.size = len(content)
    tar.addfile(info,io.BytesIO(content))
print('ARCHIVE:',archive)
print('SHA256:',sha(archive))
print('BYTES:',archive.stat().st_size)
print('FILES:',len(files),'plus manifest; environment excluded')
