"""Read-only WFI header inventory for the accepted frozen Stage 2 campaign.

No native engine, pixel-array access, calibration selection or raw-file mutation.
Full content hashes are deferred to the one selected input lock.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import tarfile
import tempfile
import warnings
from astropy.io import fits

KEYS = ('INSTRUME', 'TELESCOP', 'ORIGFILE', 'DATE-OBS', 'MJD-OBS', 'EXPTIME',
        'OBJECT', 'IMAGETYP', 'FILTER', 'ESO DPR CATG', 'ESO DPR TYPE', 'ESO DPR TECH',
        'ESO INS FILT1 NAME', 'ESO INS FILT1 ID', 'ESO DET WIN1 BINX', 'ESO DET WIN1 BINY',
        'ESO DET READ CLOCK', 'ESO DET READ SPEED', 'ESO DET READ CURNAME',
        'ESO OBS PROG ID', 'ESO OBS ID')
EXT_KEYS = ('EXTNAME', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'EXTVER',
            'ESO DET CHIP ID', 'ESO DET CHIP NAME', 'DATASEC', 'BIASSEC', 'TRIMSEC',
            'CRPIX1', 'CRPIX2', 'GAIN', 'RDNOISE')


def values(header, keys):
    return {key: header[key] for key in keys if key in header}


def inspect(path):
    # Header/stat readback only: never request hdu.data or checksum the pixel payload.
    before = path.stat()
    row = dict(path=str(path), resolved_path=str(path.resolve()), size=before.st_size,
               mtime_ns=before.st_mtime_ns, inode=before.st_ino)
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            with fits.open(path, mode='readonly', memmap=True,
                           lazy_load_hdus=True, do_not_scale_image_data=True) as hdus:
                row['primary'] = values(hdus[0].header, KEYS)
                if path.name.lower().endswith('.gz'):
                    # Avoid sequential decompression of entire gzip pixel streams in inventory.
                    row['extensions'] = None
                    row['geometry_note'] = 'gzip primary header only; selected-file geometry checked at input lock'
                else:
                    row['extensions'] = [dict(index=i, **values(hdu.header, EXT_KEYS))
                                         for i, hdu in enumerate(hdus) if i]
            row['header_warnings'] = [str(w.message) for w in caught]
    except Exception as error:
        row['error'] = str(error)
    after = path.stat()
    row['stat_unchanged'] = (before.st_size, before.st_mtime_ns, before.st_ino) == (
        after.st_size, after.st_mtime_ns, after.st_ino)
    if not row['stat_unchanged']:
        raise RuntimeError('Input changed during header inspection: ' + str(path))
    return row


def main():
    # Host/environment guards: use the known Mac collection and qualified Python.
    if platform.system() != 'Darwin' or platform.node().split('.')[0] != 'MC02VV0HPHTDG':
        raise RuntimeError('STOP: expected qualified Mac')
    if Path(sys.prefix).resolve() != Path('/Users/fselman/anaconda3'):
        raise RuntimeError('STOP: unexpected Python environment')
    raw = Path('/Users/fselman/Pictures/WFI').resolve(strict=True)
    if not raw.is_dir():
        raise RuntimeError('STOP: WFI collection is not a directory')
    build = Path.home() / 'Software/build/wenu-imaging'
    if not build.is_dir():
        raise RuntimeError('STOP: expected build/evidence root absent')
    work = Path(tempfile.mkdtemp(prefix='mac-integrated-wfi-inventory-', dir=build))
    report = work / 'run-provenance.json'
    record = dict(purpose=__doc__, status='running', native_execution=False,
                  raw_root=str(raw), host=platform.node(), python=sys.executable,
                  created_utc=datetime.now(timezone.utc).isoformat(), files=[],
                  pixel_data_accessed=False, selected_inputs=False,
                  full_raw_content_hashes_taken=False, native_launches_consumed=0)

    def save():
        temporary = report.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(record, indent=2, default=str) + '\n')
        temporary.replace(report)

    # Provenance precedes the one metadata inventory; directory symlinks are not traversed.
    save()
    print('WORK DIRECTORY:', work, flush=True)
    try:
        suffixes = ('.fits', '.fit', '.fts', '.fits.fz', '.fit.fz', '.fts.fz',
                    '.fits.gz', '.fit.gz', '.fts.gz')
        for directory, dirs, names in os.walk(raw, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
            for name in sorted(names):
                if name.lower().endswith(suffixes):
                    record['files'].append(inspect(Path(directory) / name))
                    if len(record['files']) % 25 == 0:
                        save()
                        print('HEADERS INSPECTED:', len(record['files']), flush=True)
        # Group declared header values without inferring calibration lists from filenames.
        groups = Counter()
        for row in record['files']:
            h = row.get('primary', {})
            group = (h.get('ESO DPR CATG', ''), h.get('ESO DPR TYPE', h.get('IMAGETYP', '')),
                     h.get('ESO INS FILT1 NAME', h.get('FILTER', '')),
                     h.get('ESO DET WIN1 BINX', ''), h.get('ESO DET WIN1 BINY', ''),
                     h.get('ESO DET READ CURNAME', h.get('ESO DET READ SPEED', '')))
            groups[tuple(map(str, group))] += 1
        record['groups'] = [dict(category=k[0], type=k[1], filter=k[2], binx=k[3], biny=k[4],
                                 readout=k[5], count=n) for k, n in sorted(groups.items())]
        record['header_errors'] = sum('error' in row for row in record['files'])
        record['status'] = 'completed-with-header-errors' if record['header_errors'] else 'completed'
        record['stat_preservation_passed'] = all(row['stat_unchanged'] for row in record['files'])
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    except BaseException as error:
        record.update(status='failed', error=str(error))
        raise
    finally:
        save()
    # Package only the inventory report; original scientific files remain in place.
    archive = work / 'wfi-header-inventory.tar.gz'
    with tarfile.open(archive, 'x:gz') as bundle:
        bundle.add(report, arcname=report.name)
    with tarfile.open(archive) as bundle:
        if bundle.getnames() != [report.name] or bundle.extractfile(report.name).read() != report.read_bytes():
            raise RuntimeError('Inventory archive readback failed')
    print('FILES:', len(record['files']), 'HEADER ERRORS:', record['header_errors'])
    for group in record['groups']:
        print('GROUP:', json.dumps(group))
    print('ARCHIVE:', archive)
    print('SHA256:', hashlib.sha256(archive.read_bytes()).hexdigest())
    print('Native launches consumed: 0; calibration/science processing: none')


if __name__ == '__main__':
    main()
