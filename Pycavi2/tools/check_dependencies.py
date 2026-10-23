#!/usr/bin/env python3
"""Run portable, synthetic dependency checks in a fresh evidence directory.

Launch as a separate process, never with notebook %run: this process lowers its
own CPU priority. No science input, package installation or configuration edits.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def executable(value):
    found = shutil.which(value)
    if not found:
        raise ValueError('Executable not found or not executable: ' + value)
    return str(Path(found).absolute())


class Check:
    def __init__(self, directory):
        self.directory = directory
        directory.mkdir()
        self.commands = []

    def run(self, command, label, check=True):
        try:
            result = subprocess.run(
                command, cwd=self.directory, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, timeout=120,
            )
        except subprocess.TimeoutExpired as exc:
            self.commands.append({'argv': command, 'timeout_seconds': 120})
            (self.directory / (label + '.stdout')).write_text(
                (exc.stdout or b'').decode(errors='replace') if isinstance(exc.stdout, bytes)
                else (exc.stdout or ''))
            (self.directory / (label + '.stderr')).write_text(
                (exc.stderr or b'').decode(errors='replace') if isinstance(exc.stderr, bytes)
                else (exc.stderr or ''))
            raise
        (self.directory / (label + '.stdout')).write_text(result.stdout)
        (self.directory / (label + '.stderr')).write_text(result.stderr)
        self.commands.append({'argv': command, 'exit_code': result.returncode})
        if check and result.returncode:
            raise RuntimeError('{} returned {}; see {}'.format(
                command[0], result.returncode, self.directory))
        return result


def compression(context, paths):
    import numpy as np
    from astropy.io import fits
    data = np.arange(4096, dtype=np.int16).reshape(64, 64) - 2048
    header = fits.Header({'OBJECT': 'DEPENDENCY TEST', 'BUNIT': 'adu'})
    fits.PrimaryHDU(data, header).writeto(context.directory / 'input.fits')
    context.run([paths['fpack'], 'input.fits'], 'fpack')
    context.run([paths['funpack'], '-O', 'restored.fits', 'input.fits.fz'], 'funpack')
    with fits.open(context.directory / 'restored.fits') as hdus:
        np.testing.assert_array_equal(hdus[0].data, data)
        assert hdus[0].header['OBJECT'] == 'DEPENDENCY TEST'
        assert hdus[0].header['BUNIT'] == 'adu'
    return {'exact_integer_round_trip': True, 'selected_headers_preserved': True}


def sextractor(context, paths):
    import numpy as np
    from astropy.io import fits
    rng = np.random.default_rng(20261023)
    yy, xx = np.indices((256, 256))
    positions = np.array([[45., 45.], [125., 50.], [205., 75.],
                          [70., 180.], [180., 195.]])
    image = rng.normal(1000., 5., xx.shape)
    for x, y in positions:
        image += 3000. * np.exp(-((xx-x)**2 + (yy-y)**2) / 8.)
    fits.PrimaryHDU(image.astype(np.float32)).writeto(context.directory / 'stars.fits')
    defaults = context.run([paths['sextractor'], '-d'], 'defaults')
    (context.directory / 'default.sex').write_text(defaults.stdout)
    (context.directory / 'parameters.txt').write_text('X_IMAGE\nY_IMAGE\nFLUX_AUTO\nFLAGS\n')
    context.run([
        paths['sextractor'], 'stars.fits', '-c', 'default.sex',
        '-PARAMETERS_NAME', 'parameters.txt', '-CATALOG_NAME', 'catalogue.txt',
        '-CATALOG_TYPE', 'ASCII_HEAD', '-FILTER', 'N', '-DETECT_THRESH', '5',
        '-ANALYSIS_THRESH', '5', '-DETECT_MINAREA', '5', '-WEIGHT_TYPE', 'NONE',
        '-CHECKIMAGE_TYPE', 'NONE', '-GAIN', '1', '-SATUR_LEVEL', '60000',
        '-NTHREADS', '1',
    ], 'extract')
    catalogue = np.loadtxt(context.directory / 'catalogue.txt', ndmin=2)
    assert catalogue.shape[0] >= 5, 'Fewer than five detections'
    assert np.isfinite(catalogue).all(), 'Nonfinite catalogue values'
    distances = np.sqrt(((positions[:, None, :] + 1. -
                           catalogue[None, :, :2])**2).sum(axis=2))
    matched = distances.argmin(axis=1)
    nearest = distances.min(axis=1)
    assert len(set(matched.tolist())) == 5, 'Detection assignments are not unique'
    assert (nearest < 2.).all(), 'Injected stars not recovered within two pixels'
    assert (catalogue[:, 2] > 0).all(), 'Nonpositive flux'
    return {'detections': len(catalogue), 'nearest_distances_pixels': nearest.tolist()}


def swarp(context, paths):
    import numpy as np
    from astropy.io import fits
    from astropy.wcs import WCS
    wcs = WCS(naxis=2)
    wcs.wcs.crpix = [32.5, 32.5]
    wcs.wcs.crval = [123., -30.]
    wcs.wcs.cdelt = [-1./3600., 1./3600.]
    wcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    header = wcs.to_header()
    header['EXPTIME'], header['GAIN'] = 1., 1.
    fits.PrimaryHDU(np.full((64, 64), 100., dtype=np.float32), header).writeto(
        context.directory / 'input.fits')
    defaults = context.run([paths['swarp'], '-d'], 'defaults')
    (context.directory / 'default.swarp').write_text(defaults.stdout)
    context.run([
        paths['swarp'], 'input.fits', '-c', 'default.swarp',
        '-IMAGEOUT_NAME', 'output.fits', '-WEIGHTOUT_NAME', 'weight.fits',
        '-WEIGHT_TYPE', 'NONE', '-SUBTRACT_BACK', 'N', '-RESAMPLE', 'Y',
        '-RESAMPLING_TYPE', 'BILINEAR', '-COMBINE', 'Y', '-COMBINE_TYPE', 'AVERAGE',
        '-CENTER_TYPE', 'MANUAL', '-CENTER', '123.0,-30.0',
        '-PIXELSCALE_TYPE', 'MANUAL', '-PIXEL_SCALE', '1.0',
        '-IMAGE_SIZE', '64,64', '-PROJECTION_TYPE', 'TAN',
        '-CELESTIAL_TYPE', 'EQUATORIAL', '-NTHREADS', '1',
    ], 'resample')
    with fits.open(context.directory / 'output.fits') as hdus:
        image = hdus[0].data
        assert image.shape == (64, 64) and np.isfinite(image).all()
        np.testing.assert_allclose(image[16:48, 16:48], 100., atol=0.01, rtol=0)
        output_wcs = WCS(hdus[0].header).celestial
        assert output_wcs.has_celestial
        assert np.isfinite(output_wcs.all_pix2world([[31.5, 31.5]], 0)).all()
        mean = float(image[16:48, 16:48].mean())
    with fits.open(context.directory / 'weight.fits') as hdus:
        weight = hdus[0].data
        assert weight.shape == (64, 64) and np.isfinite(weight).all()
        assert (weight[16:48, 16:48] > 0).all()
    return {'central_mean': mean, 'finite_wcs': True, 'positive_central_weights': True}


CHECKS = {'fits-compression': compression, 'sextractor': sextractor, 'swarp': swarp}
NEEDS = {'fits-compression': ('fpack', 'funpack'),
         'sextractor': ('sextractor',), 'swarp': ('swarp',)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checks', nargs='+', choices=sorted(CHECKS))
    parser.add_argument('--output', required=True, type=Path,
                        help='New directory; existing paths are refused.')
    parser.add_argument('--expect-host', help='Require this short hostname.')
    parser.add_argument('--expect-prefix', type=Path, help='Require this Python prefix.')
    parser.add_argument('--dry-run', action='store_true', help='Validate paths; write/run nothing.')
    for name, default in [('fpack', 'fpack'), ('funpack', 'funpack'),
                          ('sextractor', 'sex'), ('swarp', 'swarp')]:
        parser.add_argument('--' + name, default=default)
    args = parser.parse_args(argv)
    try:
        if sys.flags.optimize:
            raise ValueError('Run without -O: numerical assertions must be enabled')
        if args.expect_host and socket.gethostname().split('.')[0] != args.expect_host:
            raise ValueError('Unexpected hostname: ' + socket.gethostname())
        if args.expect_prefix and args.expect_prefix.expanduser().resolve() != Path(sys.prefix).resolve():
            raise ValueError('Unexpected Python prefix: ' + sys.prefix)
        output = args.output.expanduser().absolute()
        if output.exists() or output.is_symlink():
            raise ValueError('Refusing existing output path: ' + str(output))
        paths = {name: executable(getattr(args, name))
                 for check in args.checks for name in NEEDS[check]}
        checks = list(dict.fromkeys(args.checks))
        report = {'host': socket.getfqdn(), 'platform': platform.platform(),
                  'python': sys.executable, 'python_version': sys.version,
                  'prefix': sys.prefix, 'checks': {},
                  'executables': paths, 'started_utc': datetime.now(timezone.utc).isoformat()}
        report['tool_sha256'] = sha256(__file__)
        print(json.dumps(report, indent=2), flush=True)
        if args.dry_run:
            print('Dry run: no output directory, imports, jobs or priority changes.')
            return 0
        output.mkdir(parents=True)
        # Separate CLI process only. Descendants inherit priority/thread limits.
        priority = max(10, os.getpriority(os.PRIO_PROCESS, 0))
        os.setpriority(os.PRIO_PROCESS, 0, priority)
        report['niceness'] = os.getpriority(os.PRIO_PROCESS, 0)
        for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS',
                     'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
            os.environ[name] = '1'
        report['executable_sha256'] = {name: sha256(path) for name, path in paths.items()}
        report['distributions'] = sorted(
            [{'name': d.metadata['Name'], 'version': d.version}
             for d in importlib.metadata.distributions()], key=lambda d: d['name'].lower())
        print('Batch niceness:', report['niceness'], flush=True)
        for name in checks:
            context = Check(output / name)
            try:
                for executable_name in NEEDS[name]:
                    flag = '-V' if executable_name in ('fpack', 'funpack') else '-v'
                    context.run([paths[executable_name], flag],
                                executable_name + '-version', check=False)
                details = CHECKS[name](context, paths)
                result = {'status': 'pass', 'details': details}
            except Exception as exc:
                result = {'status': 'fail', 'error': '{}: {}'.format(type(exc).__name__, exc)}
            result['commands'] = context.commands
            report['checks'][name] = result
            (output / 'report.json').write_text(json.dumps(report, indent=2))
            print(name + ': ' + result['status'].upper(), flush=True)
            if result['status'] == 'fail':
                print(result['error'], flush=True)
        report['completed_utc'] = datetime.now(timezone.utc).isoformat()
        (output / 'report.json').write_text(json.dumps(report, indent=2))
        print('Records:', output)
        return int(any(r['status'] != 'pass' for r in report['checks'].values()))
    except (OSError, ValueError) as exc:
        parser.exit(1, 'STOP: {}\n'.format(exc))


if __name__ == '__main__':
    sys.exit(main())
