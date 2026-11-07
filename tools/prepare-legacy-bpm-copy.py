#!/usr/bin/env python3
"""Prepare an explicit header-only legacy BPM derivative; never alter its source (#232)."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
import tomllib


def require(ok, message):
    if not ok:
        raise ValueError(message)


def stat_identity(path):
    s = path.stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def payload(stream, start, length, output=None):
    stream.seek(start)
    h = hashlib.sha256()
    while length:
        block = stream.read(min(length, 8 * 1024 * 1024))
        require(bool(block), 'Truncated image payload')
        h.update(block)
        if output is not None:
            require(output.write(block) == len(block), 'Short payload write')
        length -= len(block)
    return h.hexdigest()


def prepare(source, output, expected, source_sha256=None):
    from astropy.io import fits
    require(source.is_file() and source.resolve() != output.resolve(), 'Distinct source/copy required')
    before = stat_identity(source)
    original_hash = digest(source)
    require(source_sha256 is None or original_hash == source_sha256, 'Source differs from recorded payload fingerprint')
    require(stat_identity(source) == before, 'Source changed during hashing')
    records = []
    seen = set()
    with fits.open(source, mode='readonly', memmap=True,
                   do_not_scale_image_data=True, lazy_load_hdus=True) as hdus:
        require(len(hdus) == len(expected) + 1, 'Unexpected HDU count')
        end = 0
        for index, hdu in enumerate(hdus):
            header = hdu.header
            info = hdu.fileinfo()
            require(info['hdrLoc'] == end and info['datLoc'] >= end, 'Noncontiguous HDUs')
            end = info['datLoc'] + info['datSpan']
            require(end <= before[2], 'Payload exceeds source file')
            require('CHECKSUM' not in header, 'CHECKSUM requires a separate reviewed update')
            selected = ('SIMPLE','XTENSION','BITPIX','NAXIS','NAXIS1','NAXIS2',
                        'EXTNAME','PCOUNT','GCOUNT','BSCALE','BZERO')
            require(all(header.count(k) <= 1 for k in selected if k in header),
                    'Duplicate structural/identity card')
            if index == 0:
                require(header.get('SIMPLE') is True and header.get('NAXIS') == 0
                        and info['datSpan'] == 0, 'Require an empty primary')
            else:
                identity = header.get('EXTNAME')
                require(identity in expected and identity not in seen, 'Missing/duplicate detector identity')
                seen.add(identity)
                width, height = expected[identity]
                require(header.get('XTENSION','').strip() == 'IMAGE'
                        and header.get('BITPIX') == 8 and header.get('NAXIS') == 2
                        and [header.get('NAXIS1'), header.get('NAXIS2')] == [width, height],
                        'Unexpected mask image type/geometry')
                require(header.get('BSCALE',1) == 1 and header.get('BZERO',0) == 0,
                        'Unexpected mask scaling')
                require(info['datSpan'] == ((width * height + 2879) // 2880) * 2880,
                        'Image storage span disagrees with mask geometry')
                require(header.get('PCOUNT',0) == 0 and header.get('GCOUNT',1) == 1,
                        'Conflicting existing PCOUNT/GCOUNT')
            records.append(dict(hdu=index, source_offset=info['datLoc'], size=info['datSpan'],
                                header=header.copy(), added=[]))
        require(end == before[2] and seen == set(expected), 'Unaccounted bytes/detectors')
        with source.open('rb') as original, output.open('xb') as target:
            for record in records:
                header = record['header'].copy()
                if record['hdu']:
                    if 'PCOUNT' not in header:
                        header.insert('NAXIS2', ('PCOUNT',0,'No image-extension parameters'), after=True)
                        record['added'].append('PCOUNT')
                    if 'GCOUNT' not in header:
                        header.insert('PCOUNT', ('GCOUNT',1,'One image array'), after=True)
                        record['added'].append('GCOUNT')
                target.write(header.tostring().encode('ascii'))
                record['payload_sha256'] = payload(original, record['source_offset'], record['size'], target)
    # Independent reread: strict FITS structure, every existing card and stored data byte.
    with fits.open(output, mode='readonly', memmap=True,
                   do_not_scale_image_data=True, lazy_load_hdus=True) as copied, output.open('rb') as stream:
        copied.verify('exception')
        require(len(copied) == len(records), 'Copy HDU count differs')
        for record, hdu in zip(records, copied):
            cards = [c.image for c in hdu.header.cards if c.keyword not in record['added']]
            require(cards == [c.image for c in record['header'].cards], 'Existing header cards changed')
            info = hdu.fileinfo()
            require(info['datSpan'] == record['size'] and
                    payload(stream, info['datLoc'], info['datSpan']) == record['payload_sha256'],
                    'Stored pixel/padding bytes differ')
            record['copy_offset'] = info['datLoc']
            del record['header']
    require(stat_identity(source) == before and digest(source) == original_hash
            and stat_identity(source) == before, 'Original BPM changed')
    return dict(status='prepared_verified_copy', original=str(source.resolve()), copy=str(output.resolve()),
                original_sha256=original_hash, copy_sha256=digest(output),
                source_preservation=True, payload_preservation=True, existing_cards_preservation=True,
                detector_count=len(expected), added_card_count=sum(len(r['added']) for r in records),
                records=records, pixel_arrays_accessed=False, mask_values_recalculated=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source','detectors','processing','run'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--source-sha256', required=True)
    a = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{64}',a.source_sha256) is not None, 'Require recorded source SHA256')
    work = a.run.resolve(strict=True)
    require(work.is_dir() and not any(work.iterdir()), 'Fresh empty run directory required')
    report = dict(status='preparing')
    (work/'README.md').write_text('''# Legacy OCAM BPM structural compatibility copy

This directory retains an explicit derivative of the original legacy BPM: only
missing IMAGE-extension PCOUNT=0/GCOUNT=1 cards are added. Original inputs are
read-only. Stored pixel/padding bytes and all existing header cards are verified
unchanged. This is format repair, not new mask generation or scientific acceptance.
Keep this copy and receipt while referenced by measurement/comparison products.
Erase only after those references are retired or migrated and needed provenance
is retained. Failed attempts may be erased after diagnosis/evidence retention.
''')
    try:
        with a.detectors.open('rb') as f:
            geometry = tomllib.load(f)
        with a.processing.open('rb') as f:
            processing = tomllib.load(f)
        require(geometry['instrument'] == processing['instrument'] == 'omegacam'
                and geometry['binning'] == [1,1], 'Require reviewed OCAM 1x1 profiles')
        ids = [d['id'] for d in geometry['detector']]
        require(len(ids) == len(set(ids)) == 32, 'Require all32 detector identities')
        crops = {t['detector']:t['retained'] for t in processing['trim']}
        require(set(crops) == set(ids), 'Crop identities differ')
        expected = {identity:[crops[identity][1]-crops[identity][0]+1,
                              crops[identity][3]-crops[identity][2]+1] for identity in ids}
        report = prepare(a.source.resolve(strict=True), work/'OCAM_BPM_1x1_structural.fits', expected, a.source_sha256)
        report['configuration_sha256'] = {str(p.resolve()):digest(p) for p in (a.detectors,a.processing)}
    except Exception as error:
        report.update(status='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        (work/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
        print('STATUS:',report['status'],flush=True)
        print('RETAINED COPY:',work,flush=True)
    print(json.dumps({k:v for k,v in report.items() if k not in ('records','configuration_sha256')},indent=2))


if __name__ == '__main__':
    main()
