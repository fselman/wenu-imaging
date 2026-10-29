"""Read the transferred Mac fixture in the retained Chapman4 private environment, offline."""
import argparse
import hashlib
import json
import platform
import importlib.metadata as md
from pathlib import Path
import shutil
import sys


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--environment', type=Path, required=True)
    args = parser.parse_args()
    require(platform.system() == 'Linux' and platform.node().split('.')[0] == 'chapman4', 'wrong host')
    require(sys.base_prefix == '/home/fselman/.conda/envs/wenu-imaging', 'wrong base Python')
    retained = Path('/home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC/D2-private-s6qsxbqf/environment')
    require(Path(sys.prefix).resolve() == retained.resolve() == args.environment.resolve(), 'wrong retained private environment')
    require(sys.version_info[:3] == (3,11,14), 'Python changed')
    expected = {'asdf':'6.0.0','asdf-standard':'1.5.0','jmespath':'1.1.0','semantic-version':'2.10.0',
                'numpy':'1.26.4','astropy':'6.1.7','zipp':'4.1.2','importlib-metadata':'9.0.1',
                'attrs':'26.1.0','typing-extensions':'4.16.0','packaging':'26.3','PyYAML':'6.0.3'}
    for name, version in expected.items():
        require(md.version(name) == version, 'dependency changed: '+name)
        location = Path(md.distribution(name).locate_file('')).resolve()
        base = retained if name in ('asdf','asdf-standard','jmespath','semantic-version') else Path(sys.base_prefix)
        require(location.is_relative_to(base.resolve()), 'unexpected dependency location: '+name)
    work, fixture = args.work.resolve(), args.fixture.resolve()
    require(not (work/'interchange-report.json').exists(), 'interchange already attempted')
    report = {'status':'started', 'direction':'Mac-to-Chapman4', 'network_attempts':[], 'versions':expected}
    original_cwd = Path.cwd()
    before = {str(p.relative_to(fixture)):digest(p) for p in fixture.rglob('*') if p.is_file()}
    def offline(event, arguments):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'):
            report['network_attempts'].append(event)
            raise RuntimeError('network attempted: '+event)
    sys.addaudithook(offline)
    try:
        import asdf
        import numpy as np
        from astropy.io import fits
        from asdf.exceptions import ValidationError
        require(Path(asdf.__file__).resolve().is_relative_to(args.environment.resolve()), 'ASDF outside private environment')
        expected = json.loads((fixture/'expected-wad.json').read_text())
        semantic = hashlib.sha256(json.dumps(expected, sort_keys=True, separators=(',',':')).encode()).hexdigest()
        require(semantic == '4df8a3c69e541d2d4950e9ffdc86b2b57670a1364682611f6f7fc4e5207daf30', 'unexpected Mac semantics')
        science = np.arange(16,dtype=np.float32).reshape(4,4)
        mask = np.zeros((4,4),dtype=np.uint16)
        mask[0,0] = 1
        arrays = {'signal':science,'primary':science,'variance':np.full((4,4),0.25,dtype=np.float32),'mask':mask}
        relocated = work/'interchange relocated fixture'
        shutil.copytree(fixture, relocated)
        # Read the transferred ASDF and all four FITS bindings before/after relocation.
        with asdf.config_context() as config:
            config.validate_on_read = True
            for base in (fixture, relocated):
                schema = (base/'local-schema.json').as_uri()
                with asdf.open(base/'project.asdf',custom_schema=schema,lazy_load=False,strict_extension_check=True) as af:
                    af.validate()
                    require(af.tree['wad'] == expected, 'transferred ASDF semantics differ')
                for name, ref in expected['files'].items():
                    path = (base/ref['path']).resolve()
                    require(path.is_relative_to(base) and digest(path) == ref['sha256'], 'FITS binding/hash differs')
                    with fits.open(path,memmap=False) as hdul:
                        hdu = hdul[ref['hdu_index']]
                        require(ref['extname'] is None or hdu.header.get('EXTNAME') == ref['extname'], 'extension mismatch')
                        require(hdu.header.get('DETECTOR') == ref['detector_id'] and hdu.header.get('BUNIT') == ref['unit'], 'metadata mismatch')
                        require(list(hdu.data.shape) == ref['shape'] and np.array_equal(hdu.data,arrays[name]), 'pixels/shape differ')
                # The transferred negative artifact must still fail its custom schema.
                try:
                    with asdf.open(base/'invalid-record.asdf',custom_schema=schema,lazy_load=False) as af:
                        af.validate()
                except ValidationError:
                    pass
                else:
                    raise RuntimeError('transferred invalid record accepted')
        require(not report['network_attempts'], 'network attempted')
        report.update(status='Mac-to-Chapman4-interchange-passed',semantic_sha256=semantic,
                      checks=['transferred ASDF semantics and custom schema','all four FITS references and exact synthetic arrays',
                              'relocation with spaces','transferred invalid record rejected'])
    except Exception as exc:
        report.update(status='stopped',error=type(exc).__name__+': '+str(exc))
        raise
    finally:
        after = {str(p.relative_to(fixture)):digest(p) for p in fixture.rglob('*') if p.is_file()}
        report['original_fixture_unchanged'] = before == after
        report['cwd_unchanged'] = Path.cwd() == original_cwd
        if not report['original_fixture_unchanged'] or not report['cwd_unchanged']:
            report['status'] = 'stopped-preservation-check'
        (work/'interchange-report.json').write_text(json.dumps(report,indent=2)+'\n')
    require(report['status'] == 'Mac-to-Chapman4-interchange-passed','interchange did not pass')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
