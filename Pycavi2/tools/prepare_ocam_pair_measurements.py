"""Saved header-only preparation of the owner-selected 13 March 2017 sequence.

Reuse the shared bounded FITS inspector. No image arrays, pairing inference,
calibration selection, native calculation or writes to source files.
"""
import argparse
import configparser
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

BIAS_TIMES = (
    '09:50:05.624', '09:50:48.373', '09:51:31.403', '09:52:14.404',
    '09:52:57.394', '09:53:40.384', '09:54:23.384', '09:55:06.394',
    '09:55:49.384', '09:56:31.804')
FLATS = (
    ('11:34:43.759', 2), ('11:35:30.570', 70), ('11:37:25.420', 40),
    ('11:38:50.390', 5), ('11:39:40.380', 10), ('11:40:35.390', 30),
    ('11:41:50.391', 20), ('11:42:55.391', 50), ('11:44:30.391', 60),
    ('11:46:16.391', 7), ('11:47:08.392', 7), ('11:48:00.392', 60),
    ('11:49:45.392', 50), ('11:51:20.392', 20), ('11:52:25.393', 30),
    ('11:53:40.483', 10), ('11:54:35.393', 5), ('11:55:25.563', 40),
    ('11:56:50.383', 70), ('11:58:45.683', 2))
KEYS = ('INSTRUME', 'DATE-OBS', 'EXPTIME', 'ESO DPR TYPE', 'ESO DPR CATG',
        'ESO DPR TECH', 'ESO TPL ID', 'ESO TPL START', 'ESO TPL EXPNO',
        'ESO TPL NEXP', 'ESO OBS ID', 'ESO INS FILT1 NAME', 'ESO DET READ MODE',
        'ESO DET READ SPEED', 'ESO DET READ CLOCK', 'ESO DET WIN1 BINX',
        'ESO DET WIN1 BINY', 'ESO DET CHIP ID', 'ESO DET CHIP NAME',
        'ESO DET OUTPUTS', 'ESO DET NOUTPUTS', 'ESO DET OUT1 ID',
        'ESO DET OUT1 NAME', 'ESO DET OUT1 CONAD', 'ESO DET OUT1 GAIN',
        'ESO DET OUT1 RON', 'ESO DET OUT1 NX', 'ESO DET OUT1 NY',
        'ESO DET OUT1 X', 'ESO DET OUT1 Y', 'ESO DET OUT1 OVSCX',
        'ESO DET OUT1 PRSCX', 'ESO DET OUT1 SATURATE', 'SATURATE',
        'DATAMAX', 'DATAMIN', 'BITPIX', 'BUNIT', 'BSCALE', 'BZERO',
        'NAXIS', 'NAXIS1', 'NAXIS2', 'PCOUNT', 'GCOUNT', 'EXTNAME',
        'DATASEC', 'DETSEC', 'CCDSEC', 'TRIMSEC', 'BIASSEC',
        'MASKENC', 'MASKREG', 'ESO PRO CATG', 'PRODCATG', 'CHECKSUM', 'DATASUM')


def selected_sequence(raw_root):
    rows = []
    for index, (time, seconds) in enumerate([(t, 0) for t in BIAS_TIMES] + list(FLATS)):
        flat = index >= len(BIAS_TIMES)
        rows.append(dict(index=index, path=str(raw_root / ('OMEGA.2017-03-13T'+time+'.fits')),
                         role='flat' if flat else 'bias', expected_seconds=seconds,
                         expected_filter='v_STRM' if flat else 'r_SDSS',
                         expected_type='FLAT,DOME,DETGAIN' if flat else 'BIAS', expected_obs_id=574184,
                         pair_id=('flat-%02ds' % seconds) if flat else None))
    return rows


def single(hdu, key):
    values = [c.get('value') for c in hdu.get('cards', ()) if c['key'] == key]
    return values[0] if len(values) == 1 else None


def stat_identity(path):
    st = path.stat()
    return [st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_mode]


def configuration(source):
    cfg = source / 'Pycavi2/pycavi/config/omegacam.cfg'
    paf = source / 'mefpp2/ins/mef/config/omegacam.paf'
    parser = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=('#',))
    parser.read_string(cfg.read_text())
    configured = []
    for key, value in parser['Extension Keywords'].items():
        match = re.fullmatch(r'ext_(\d+)_name', key)
        if match:
            configured.append(dict(detector_id=value.strip().strip('"'),
                                   python_config_entry=int(match[1])-1))
    # Inventory exact PAF declarations only; native code remains parser authority.
    declarations = []
    for line in paf.read_text().splitlines():
        match = re.match(r'\s*(MEF\.(?:USE\.(?:PRE|OVER)SCAN|(?:PRE|OVER)SCAN\.X\.(?:MIN|MAX)\.CHIP\d+|CROP\.[XY]\.(?:MIN|MAX)\.CHIP\d+|SCANREJ\.(?:MIN|MAX)))\s+([^;]+);', line)
        if match:
            declarations.append(dict(key=match[1], declared_value=match[2].strip()))
    return dict(configured_detectors=configured, scan_geometry_declarations=declarations,
                sources=[dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (cfg, paf)])


def assess(row, result, configured):
    """Metadata checks only. Every changed selection remains explicit in output."""
    errors = []
    asset = result.get('asset') or {}
    hdus = asset.get('hdus', [])
    if not hdus:
        return ['No readable headers']
    for d in result.get('diagnostics', ()):
        if d['code'] != 'fits_warning':
            errors.append(d['code'] + ': ' + d['message'])
    primary = hdus[0]
    for key, expected in (('INSTRUME', 'OMEGACAM'), ('ESO DPR TYPE', row['expected_type']),
                          ('ESO INS FILT1 NAME', row['expected_filter']),
                          ('ESO OBS ID', row['expected_obs_id'])):
        if single(primary, key) != expected:
            errors.append(key + ' conflicts with selected sequence')
    seconds = single(primary, 'EXPTIME')
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds != row['expected_seconds']:
        errors.append('EXPTIME differs from declared level; retain exact header value for review')
    ids = []
    for hdu in hdus:
        if not hdu.get('dimensions'):
            continue
        detector = single(hdu, 'EXTNAME')
        if not isinstance(detector, str) or detector not in configured or detector in ids:
            errors.append('Missing/unknown/duplicate detector identity at HDU '+str(hdu['hdu']))
        ids.append(detector)
        if len(hdu['dimensions']) != 2:
            errors.append('Non-2D image at HDU '+str(hdu['hdu']))
    if set(ids) != set(configured):
        errors.append('Detector coverage differs from configured identities')
    return errors


def prepare(source, raw_root, output, inspector=None):
    if output.exists() or output.is_symlink() or output.resolve().is_relative_to(raw_root.resolve()):
        raise ValueError('Require a new inventory directory outside raw data')
    selected = selected_sequence(raw_root)
    cfg = configuration(source)
    configured = {d['detector_id']: d for d in cfg['configured_detectors']}
    if inspector is None:
        sys.path.insert(0, str(source / 'Pycavi2/pycavi'))
        from pycavi_project import inspect_fits_headers, Limits
        def inspector(path):
            return inspect_fits_headers(path, invocation_base=raw_root, keys=KEYS,
                                        limits=Limits(files=160, hdus=64, header_bytes=4*1024*1024))
    output.mkdir()
    report = dict(version='ocam-pair-preparation-1', scope='header-only', raw_root=str(raw_root),
                  configuration=cfg, selected=[], candidates=[], detector_bindings=[],
                  errors=[], unresolved=['BPM selection and encoding/polarity',
                  'Per-amplifier ROI rectangles', 'Raw saturation exclusion boundary',
                  'Raw bias pair selection', 'Resolved amplifier/readout bindings'],
                  raw_pixels_read=False, calibration_selection_executed=False,
                  measurement_executed=False, ready_for_measurement=False)
    selected_paths = {Path(r['path']).resolve() for r in selected}
    candidates = sorted(p for p in raw_root.glob('*.fits') if p.resolve() not in selected_paths)
    if len(candidates) > 128:
        report['errors'].append('More than 128 unselected FITS candidates; discovery refused')
        candidates = []
    protected = {}
    try:
        for index, entry in enumerate(selected + [dict(path=str(p), role='unselected-candidate') for p in candidates], 1):
            path = Path(entry['path'])
            row = dict(entry)
            try:
                before = stat_identity(path)
                result = inspector(path)
                row['inspection'] = result
                row['stat_before'] = before
                protected[str(path)] = before
                row['source_stat_preserved'] = stat_identity(path) == before
                if not row['source_stat_preserved']:
                    report['errors'].append('Source changed: '+str(path))
                if entry['role'] != 'unselected-candidate':
                    row['errors'] = assess(entry, result, configured)
                    report['errors'].extend(path.name+': '+e for e in row['errors'])
            except (OSError, ValueError, TypeError) as exc:
                row['errors'] = [str(exc)]
                report['errors'].append(path.name+': '+str(exc))
            report['candidates' if entry['role']=='unselected-candidate' else 'selected'].append(row)
            print('Headers inspected:', index, '/', len(selected)+len(candidates), flush=True)
        # Match identities across files independently; ordinal slots below come
        # only from configuration and are explicitly unverified native bindings.
        for claim in cfg['configured_detectors']:
            found = []
            for row in report['selected']:
                for hdu in (row.get('inspection', {}).get('asset') or {}).get('hdus', ()):
                    if single(hdu, 'EXTNAME') == claim['detector_id']:
                        found.append(dict(file_index=row['index'], hdu=hdu['hdu'],
                                          dimensions=hdu['dimensions'],
                                          chip_id=single(hdu, 'ESO DET CHIP ID'),
                                          amplifier_id=single(hdu, 'ESO DET OUT1 ID')))
            report['detector_bindings'].append(dict(**claim, observed=found,
                         configuration_detector=None, native_binding_validated=False,
                         history_review=claim['detector_id'] in ('ESO_CCD_#69', 'ESO_CCD_#77')))
    except Exception as exc:
        report['errors'].append('Preparation interrupted: '+repr(exc))
        raise
    finally:
        changed = []
        for path, identity in protected.items():
            try:
                if stat_identity(Path(path)) != identity:
                    changed.append(path)
            except OSError:
                changed.append(path)
        report['source_stat_preservation'] = dict(passed=not changed, changed=changed,
                            scope='stat identity only; no pixel checksum or payload validation')
        report['status'] = 'blocked_metadata' if report['errors'] or changed else 'prepared_for_selection_review'
        (output/'inventory.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
        with (output/'sequence.tsv').open('w', newline='') as f:
            writer=csv.writer(f, delimiter='\t')
            writer.writerow(['Index','Role','Pair','Expected_s','Header_s','File','Metadata_errors'])
            for row in report['selected']:
                hdus=(row.get('inspection', {}).get('asset') or {}).get('hdus', [])
                writer.writerow([row['index'], row['role'], row['pair_id'] or '', row['expected_seconds'],
                                 single(hdus[0], 'EXPTIME') if hdus else '', row['path'], len(row.get('errors', []))])
        pairs = {}
        for row in report['selected']:
            if row['pair_id']:
                pairs.setdefault(row['pair_id'], []).append(row['index'])
        (output/'pairs.json').write_text(json.dumps(pairs, indent=2)+'\n')
        print('SELECTED:', len(report['selected']), '| BIASES: 10 | FLATS: 20 | PAIRS:', len(pairs))
        print('UNSELECTED FITS CANDIDATES:', len(report['candidates']))
        print('STATUS:', report['status'])
        print('OBS.ID REQUIRED: 574184')
        print('PYTHON CONFIGURATION ENTRIES (zero-based; native configuration slot unresolved):')
        for binding in report['detector_bindings']:
            observed=binding['observed']
            layouts={(v['hdu'], tuple(v['dimensions'])) for v in observed}
            print(binding['python_config_entry'], binding['detector_id'],
                  'files='+str(len(observed)), 'layouts='+json.dumps(sorted(layouts)),
                  'history-review' if binding['history_review'] else '')
        for row in report['candidates']:
            hdus=(row.get('inspection', {}).get('asset') or {}).get('hdus', [])
            print('UNSELECTED CANDIDATE:', Path(row['path']).name,
                  '| type:', single(hdus[0], 'ESO DPR TYPE') if hdus else None,
                  '| product:', single(hdus[0], 'ESO PRO CATG') if hdus else None,
                  '| HDUs:', len(hdus))
        print('SOURCE STAT PRESERVATION:', report['source_stat_preservation']['passed'])
        for error in report['errors']:
            print('METADATA:', error)
        print('INVENTORY:', output/'inventory.json')
        print('SEQUENCE:', output/'sequence.tsv')
        print('PAIR MEMBERSHIP:', output/'pairs.json')
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--raw-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(argv)
    report = prepare(a.source_root.resolve(strict=True), a.raw_root.resolve(strict=True), a.output)
    return 2 if report['status']=='blocked_metadata' else 0


if __name__ == '__main__':
    sys.exit(main())
