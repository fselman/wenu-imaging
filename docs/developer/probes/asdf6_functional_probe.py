"""D2 child: offline core ASDF + tiny FITS references, never real images."""
import argparse
import copy
import hashlib
import importlib.metadata as md
import json
from pathlib import Path
import shutil
import sys
import tomllib


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--environment', type=Path, required=True)
    parser.add_argument('--d1-report', type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    require(work.is_dir() and not (work/'functional-report.json').exists(), 'not fresh probe work')
    report = {'status':'started', 'scope':'tiny synthetic dependency probe, not WAD production implementation',
              'network_attempts':[], 'checks':[], 'reduction_performed':False}
    def offline(event, arguments):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'):
            report['network_attempts'].append(event)
            raise RuntimeError('network attempted during offline probe: '+event)
    sys.addaudithook(offline)
    try:
        import asdf
        from asdf.exceptions import ValidationError
        import astropy
        from astropy.io import fits
        import numpy as np
        from packaging.markers import default_environment
        from packaging.requirements import Requirement
        from packaging.utils import canonicalize_name

        require(Path(asdf.__file__).resolve().is_relative_to(args.environment.resolve()), 'ASDF not imported from private environment')
        require(asdf.__version__ == '6.0.0', 'unexpected ASDF')
        require(np.__version__ == '1.26.4' and astropy.__version__ == '6.1.7', 'scientific versions changed')
        for module in (np, astropy):
            require(Path(module.__file__).resolve().is_relative_to(Path(sys.base_prefix).resolve()), 'scientific import outside retained base')
        require(sys.prefix != sys.base_prefix, 'not inside candidate venv')
        d1 = json.loads(args.d1_report.read_text())
        environment = default_environment()
        environment['extra'] = ''
        actual = {}
        for name, node in d1['dependency_closure'].items():
            require(md.version(name) == node['version'], 'installed dependency changed: '+name)
            d = md.distribution(name)
            actual[name] = {'version':d.version, 'location':str(d.locate_file(''))}
            for text in d.requires or []:
                req = Requirement(text)
                if req.marker and not req.marker.evaluate(environment):
                    continue
                require(not req.url and not req.extras, 'unplanned runtime URL/extra')
                target = canonicalize_name(req.name)
                require(target in d1['dependency_closure'], 'new dependency outside D1 closure')
                require(req.specifier.contains(md.version(target), prereleases=True), 'installed dependency conflict')
        report['versions'] = actual
        report['imports'] = {'asdf':asdf.__file__, 'numpy':np.__file__, 'astropy':astropy.__file__, 'python':sys.executable, 'prefix':sys.prefix, 'base_prefix':sys.base_prefix}
        report['checks'].append('private imports and exact installed dependency closure')

        good_toml = '[instrument]\nname="WFI"\nexposure=20.0\nchips=["CCD-A", "CCD-P"]\nactive=true\n[paths]\nraw="data with spaces"\n'
        require(tomllib.loads(good_toml)['instrument']['chips'] == ['CCD-A','CCD-P'], 'TOML structure')
        for bad in ('x=1\nx=2\n', 'x=[1,\n'):
            try:
                tomllib.loads(bad)
            except tomllib.TOMLDecodeError:
                pass
            else:
                raise RuntimeError('invalid TOML accepted')
        report['checks'].append('TOML tables/arrays/paths and duplicate/malformed rejection')

        original_cwd = Path.cwd()
        fixture = work/'fixture with spaces'
        inputs = fixture/'tiny inputs'
        inputs.mkdir(parents=True)
        science = np.arange(16, dtype=np.float32).reshape(4,4)
        variance = np.full((4,4), 0.25, dtype=np.float32)
        quality = np.zeros((4,4), dtype=np.uint16)
        quality[0,0] = 1
        hdus = [fits.PrimaryHDU()]
        for name, array, unit in (('SCI',science,'adu'),('VAR',variance,'adu^2'),('DQ',quality,'1')):
            hdu = fits.ImageHDU(array, name=name)
            hdu.header['DETECTOR'] = 'CCD-A'
            hdu.header['BUNIT'] = unit
            hdus.append(hdu)
        fits.HDUList(hdus).writeto(inputs/'mef.fits', overwrite=False)
        primary = fits.PrimaryHDU(science)
        primary.header['DETECTOR'] = 'CCD-P'
        primary.header['BUNIT'] = 'adu'
        primary.writeto(inputs/'primary.fits', overwrite=False)
        def ref(file, index, name, detector, unit):
            return {'path':file, 'hdu_index':index, 'extname':name, 'detector_id':detector,
                    'unit':unit, 'shape':[4,4], 'sha256':digest(inputs/Path(file).name)}
        refs = {'signal':ref('tiny inputs/mef.fits',1,'SCI','CCD-A','adu'),
                'variance':ref('tiny inputs/mef.fits',2,'VAR','CCD-A','adu^2'),
                'mask':ref('tiny inputs/mef.fits',3,'DQ','CCD-A','1'),
                'primary':ref('tiny inputs/primary.fits',0,None,'CCD-P','adu')}
        wad = {'schema_version':'0.1.0-probe', 'project_id':'synthetic:project', 'project_revision':2,
               'membership':['synthetic:science@1'], 'selected_bias':'synthetic:bias@2',
               'frozen_plan':{'id':'synthetic:plan@1','project_revision':1,'bias':'synthetic:bias@1','gain':{'value':2.0,'unit':'electron/adu','source':'configured'}},
               'files':refs, 'unknown_variance_model':None, 'normalization_applied':False}
        schema = {'$schema':'http://stsci.edu/schemas/asdf/asdf-schema-1.1.0',
                  'id':'asdf://wenu-imaging.invalid/schemas/dependency-probe-1.0.0',
                  'type':'object', 'required':['wad'], 'properties':{'wad':{'type':'object',
                  'required':['schema_version','project_id','project_revision','membership','frozen_plan','files'],
                  'properties':{'schema_version':{'enum':['0.1.0-probe']}, 'project_id':{'type':'string'},
                  'project_revision':{'type':'integer'}, 'membership':{'type':'array','items':{'type':'string'}},
                  'frozen_plan':{'type':'object'}, 'files':{'type':'object'}}}}}
        schema_path = fixture/'local-schema.json'
        schema_path.write_text(json.dumps(schema,indent=2)+'\n')
        schema_uri = schema_path.as_uri()
        project = fixture/'project.asdf'
        with asdf.config_context() as config:
            config.validate_on_read = True
            with asdf.AsdfFile({'wad':wad},version='1.5.0',custom_schema=schema_uri) as af:
                af.validate()
                af.write_to(project)
            with asdf.open(project,custom_schema=schema_uri,lazy_load=False,strict_extension_check=True) as af:
                af.validate()
                require(af.tree['wad'] == wad, 'ASDF semantic round-trip')
            for key, value in (('schema_version','unsupported'),('project_revision','not-an-integer')):
                bad = copy.deepcopy(wad)
                bad[key] = value
                try:
                    with asdf.AsdfFile({'wad':bad},version='1.5.0',custom_schema=schema_uri) as af:
                        af.validate()
                except ValidationError:
                    pass
                else:
                    raise RuntimeError('invalid custom-schema record accepted')
            bad_file = fixture/'invalid-record.asdf'
            with asdf.AsdfFile({'wad':dict(wad,project_revision='invalid')},version='1.5.0') as af:
                af.write_to(bad_file)
            try:
                with asdf.open(bad_file,custom_schema=schema_uri,lazy_load=False) as af:
                    af.validate()
            except ValidationError:
                pass
            else:
                raise RuntimeError('invalid file read accepted')
        report['checks'].append('offline ASDF 1.5.0 semantic round-trip and custom-schema positive/negative validation')

        def resolve(record, base):
            path = base/record['path']
            require(path.is_file(), 'missing FITS reference')
            require(digest(path) == record['sha256'], 'FITS content mismatch')
            with fits.open(path,memmap=False) as hdul:
                require(0 <= record['hdu_index'] < len(hdul), 'HDU out of range')
                hdu = hdul[record['hdu_index']]
                if record['extname'] is not None:
                    require(hdu.header.get('EXTNAME') == record['extname'], 'HDU name/index disagreement')
                require(hdu.header.get('DETECTOR') == record['detector_id'], 'detector mismatch')
                require(hdu.header.get('BUNIT') == record['unit'], 'unit mismatch')
                require(list(hdu.data.shape) == record['shape'], 'shape mismatch')
                return hdu.data.copy()
        before_files = {str(p.relative_to(fixture)):digest(p) for p in fixture.rglob('*') if p.is_file()}
        for name, expected in (('signal',science),('variance',variance),('mask',quality),('primary',science)):
            require(np.array_equal(resolve(refs[name],fixture),expected), 'FITS pixels/plane mismatch')
        for changed in (dict(refs['signal'],path='absent.fits'), dict(refs['signal'],detector_id='wrong'),
                        dict(refs['signal'],hdu_index=2), dict(refs['signal'],shape=[2,8])):
            try:
                resolve(changed,fixture)
            except RuntimeError:
                pass
            else:
                raise RuntimeError('invalid FITS selector accepted')
        relocated = work/'relocated fixture'
        shutil.copytree(fixture,relocated)
        require(np.array_equal(resolve(refs['signal'],relocated),science),'relocation failed')
        after_files = {str(p.relative_to(fixture)):digest(p) for p in fixture.rglob('*') if p.is_file()}
        require(before_files == after_files,'original synthetic fixtures changed')
        require(Path.cwd() == original_cwd,'cwd changed')
        require(not report['network_attempts'],'offline probe attempted network')
        report['checks'].append('MEF/primary signal variance mask references, rejected selectors, relocation, original fixture/cwd preservation')
        report['semantic_sha256'] = hashlib.sha256(json.dumps(wad,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        (fixture/'expected-wad.json').write_text(json.dumps(wad,sort_keys=True,indent=2)+'\n')
        report['artifacts'] = {str(p.relative_to(work)):digest(p) for p in fixture.rglob('*') if p.is_file()}
        report['status'] = 'D2-functional-passed-awaiting-Mac-and-interchange'
    except Exception as exc:
        report['status'] = 'stopped'
        report['error'] = type(exc).__name__+': '+str(exc)
        raise
    finally:
        (work/'functional-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'checks':report['checks'],'network_attempts':report['network_attempts'],
                      'semantic_sha256':report['semantic_sha256']},indent=2))


if __name__ == '__main__':
    main()
