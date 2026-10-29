"""D1: fetch and inspect four pinned wheels; never install or import ASDF."""
import argparse
import email
import hashlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name

PINS = {
    'asdf': ('6.0.0', 'asdf-6.0.0-py3-none-any.whl', '152d49f9b2a2cd3ac0321b3ae6d2c30e2cb83d944ec00b8205aebf827fa38a7f'),
    'asdf-standard': ('1.5.0', 'asdf_standard-1.5.0-py3-none-any.whl', '487d192c5eb1335a62c07a88d82503e1fe57911c0876ee183cf572d385f97213'),
    'jmespath': ('1.1.0', 'jmespath-1.1.0-py3-none-any.whl', 'a5663118de4908c91729bea0acadca56526eb2698e83de10cd116ae0f4e97c64'),
    'semantic-version': ('2.10.0', 'semantic_version-2.10.0-py2.py3-none-any.whl', 'de78a3b8e0feda74cabc54aab2da702113e33ac9d9eb9d2389bcf1f58b7d9177'),
}
EXPECTED = {'pycavi':'0.1.0', 'numpy':'1.26.4', 'astropy':'6.1.7',
            'PyYAML':'6.0.3', 'packaging':'26.3', 'attrs':'26.1.0',
            'typing-extensions':'4.16.0', 'importlib-metadata':'9.0.1',
            'zipp':'4.1.2', 'pip':'26.2.2', 'setuptools':'84.2.1'}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def package_snapshot():
    rows = []
    for d in md.distributions():
        text = d.read_text('METADATA') or d.read_text('PKG-INFO') or ''
        record = d.read_text('RECORD') or ''
        rows.append({'name': canonicalize_name(d.metadata['Name']),
                     'version': d.version, 'location': str(d.locate_file('')),
                     'metadata_sha256': hashlib.sha256(text.encode()).hexdigest(),
                     'record_sha256': hashlib.sha256(record.encode()).hexdigest()})
    return sorted(rows, key=lambda x: (x['name'], x['version'], x['location']))


def read_wheel(path, name, pin):
    version, filename, digest = pin
    require(path.name == filename, 'unexpected wheel filename')
    require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'wheel hash mismatch: '+name)
    with zipfile.ZipFile(path) as z:
        metadata = [p for p in z.namelist() if p.endswith('.dist-info/METADATA')]
        wheel = [p for p in z.namelist() if p.endswith('.dist-info/WHEEL')]
        require(len(metadata) == len(wheel) == 1, 'wheel metadata ambiguity')
        info = email.message_from_bytes(z.read(metadata[0]))
        attrs = email.message_from_bytes(z.read(wheel[0]))
    require(canonicalize_name(info['Name']) == name and info['Version'] == version, 'wheel identity')
    require(attrs.get('Root-Is-Purelib', '').lower() == 'true', 'compiled wheel not in D1 scope')
    require(all(t.endswith('-none-any') for t in attrs.get_all('Tag', [])), 'unexpected wheel platform tag')
    if info.get('Requires-Python'):
        require(SpecifierSet(info['Requires-Python']).contains(platform.python_version()), 'wheel Python requirement')
    return {'version': version, 'requires': info.get_all('Requires-Dist', []),
            'requires_python': info.get('Requires-Python'), 'artifact': str(path), 'sha256': digest}


def closure(candidates):
    result = {}
    pending = list(candidates)
    markers = default_environment()
    markers['extra'] = ''
    while pending:
        name = canonicalize_name(pending.pop())
        if name in result:
            continue
        if name in candidates:
            node = dict(candidates[name], source='downloaded-wheel')
        else:
            d = md.distribution(name)
            node = {'version': d.version, 'requires': d.requires or [],
                    'requires_python': d.metadata.get('Requires-Python'),
                    'source': 'existing-production-package', 'location': str(d.locate_file(''))}
        if node['requires_python']:
            require(SpecifierSet(node['requires_python']).contains(platform.python_version()), 'dependency Python requirement: '+name)
        result[name] = node
        for text in node['requires']:
            req = Requirement(text)
            if req.marker and not req.marker.evaluate(markers):
                continue
            require(not req.url and not req.extras, 'additional URL/extra dependency requires review')
            target = canonicalize_name(req.name)
            version = candidates[target]['version'] if target in candidates else md.version(target)
            require(req.specifier.contains(version, prereleases=True), 'dependency conflict: '+text+'; installed/candidate '+version)
            pending.append(target)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    require(platform.system() == 'Linux' and platform.node().split('.')[0] == 'chapman4', 'wrong host')
    require(sys.version_info[:2] == (3, 11), 'wrong Python')
    require(sys.prefix == '/home/fselman/.conda/envs/wenu-imaging', 'wrong production prefix')
    require(os.confstr('CS_GNU_LIBC_VERSION') == 'glibc 2.17', 'libc state changed')
    repo = Path('/home1/fselman/Software/wenu-imaging')
    def git(*argv):
        return subprocess.check_output(['git', '-C', str(repo), *argv], text=True).strip()
    require(git('branch', '--show-current') == 'main', 'unexpected branch')
    require(git('rev-parse', 'HEAD') == '0fa9eaf157359a93f2a9196f6fff05dc3e96e220', 'unexpected checkout')
    require(git('remote', 'get-url', 'origin') == 'https://github.com/fselman/wenu-imaging.git', 'unexpected origin')
    require(not git('status', '--porcelain'), 'dirty checkout')
    for name, version in EXPECTED.items():
        require(md.version(name) == version, 'package state changed: '+name)
    for name in PINS:
        try:
            md.distribution(name)
        except md.PackageNotFoundError:
            pass
        else:
            raise RuntimeError('candidate already installed: '+name)
    work = args.work.resolve()
    parent = (Path.home()/'Software/build/wenu-imaging').resolve()
    require(work.parent == parent and work.name.startswith('chapman4-asdf6-download-'), 'unexpected work directory')
    require(work.is_dir() and not (work/'run-provenance.json').exists() and not (work/'wheels').exists(), 'not a fresh work directory')
    before = package_snapshot()
    report = {'stage':'D1-download-and-metadata', 'status':'started', 'host':platform.node(),
              'python':sys.executable, 'python_version':sys.version, 'checkout':git('rev-parse','HEAD'),
              'packages_before':before, 'installation_performed':False, 'asdf_imported':False,
              'production_activation':False}
    report_path = work/'run-provenance.json'
    try:
        (work/'wheels').mkdir()
        requirements = work/'candidate-wheels.txt'
        requirements.write_text(''.join(f'{name}=={pin[0]} --hash=sha256:{pin[2]}\n' for name,pin in PINS.items()))
        command = [sys.executable,'-m','pip','--isolated','--disable-pip-version-check','download',
                   '--index-url','https://pypi.org/simple','--no-cache-dir','--only-binary=:all:',
                   '--no-deps','--require-hashes','--retries','0','--timeout','15',
                   '--dest',str(work/'wheels'),'-r',str(requirements)]
        report['command'] = command
        print('WORK DIRECTORY:', work, flush=True)
        print('Downloading four pinned wheels; log:',work/'download.log',flush=True)
        with (work/'download.log').open('w') as log:
            proc = subprocess.run(command,cwd=work,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        report['download_exit_status'] = proc.returncode
        require(proc.returncode == 0, 'wheel download failed; retain download.log')
        require({p.name for p in (work/'wheels').iterdir()} == {p[1] for p in PINS.values()}, 'unexpected artifact set')
        candidates = {name:read_wheel(work/'wheels'/pin[1],name,pin) for name,pin in PINS.items()}
        report['dependency_closure'] = closure(candidates)
        report['status'] = 'D1-passed-awaiting-private-installation'
    except Exception as exc:
        report['status'] = 'stopped'
        report['error'] = str(exc)
        raise
    finally:
        report['packages_after'] = package_snapshot()
        report['production_package_metadata_unchanged'] = before == report['packages_after']
        report['checkout_unchanged'] = git('rev-parse','HEAD') == report['checkout'] and not git('status','--porcelain')
        if not report['production_package_metadata_unchanged'] or not report['checkout_unchanged']:
            report['status'] = 'stopped-preservation-check'
        report_path.write_text(json.dumps(report,indent=2)+'\n')
        print('REPORT:',report_path,flush=True)
    require(report['status'] == 'D1-passed-awaiting-private-installation', 'D1 did not pass')
    print('PASS: four wheel hashes/metadata and constrained dependency closure; production package metadata/checkout unchanged')
    print('No installation, ASDF import, native build, FITS read or reduction ran.')


if __name__ == '__main__':
    main()
