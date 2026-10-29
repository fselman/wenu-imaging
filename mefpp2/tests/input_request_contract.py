"""Compare explicit file/list requests with the actual legacy reader.

Only tiny synthetic files and list text are used. No numerical engine runs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import tempfile


def fits_hdu(primary, detector=None):
    cards = [('SIMPLE  =                    T' if primary else "XTENSION= 'IMAGE   '")]
    cards += ['BITPIX  =                  -32', 'NAXIS   =                    2',
              'NAXIS1  =                    2', 'NAXIS2  =                    2']
    if not primary:
        cards += ['PCOUNT  =                    0', 'GCOUNT  =                    1',
                  "EXTNAME = '%s'" % detector, 'EXTVER  =                    1']
    cards += ['END']
    header = ''.join(card.ljust(80) for card in cards).encode('ascii')
    header += b' ' * (-len(header) % 2880)
    data = struct.pack('>4f', 1.0, 2.0, 3.0, 4.0)
    return header + data + b'\0' * (-len(data) % 2880)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    probe = args.probe.resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix='m1-inputs-', dir=args.work_parent.resolve(strict=True)))
    fixture = work / 'fixture with spaces'
    for folder in ('members', 'lists', 'cal'):
        (fixture / folder).mkdir(parents=True, exist_ok=True)
    # Valid tiny FITS bytes; the request adapter only opens files for readability.
    (fixture / 'members/a.fits').write_bytes(fits_hdu(True))
    # The supplied catalogue, not the adapter, selects the image HDUs.
    primary = b'SIMPLE  =                    T'.ljust(80) + b'BITPIX  =                    8'.ljust(80)
    primary += b'NAXIS   =                    0'.ljust(80) + b'EXTEND  =                    T'.ljust(80) + b'END'.ljust(80)
    primary += b' ' * (-len(primary) % 2880)
    (fixture / 'members/z.fits').write_bytes(primary + fits_hdu(False, 'DET-A') + fits_hdu(False, 'DET-B'))
    (fixture / 'members/with space.fits').write_bytes(fits_hdu(True))
    (fixture / 'cal/bpm.fits').write_bytes(primary + fits_hdu(False, 'DET-A'))
    (fixture / 'lists/input.list').write_text('# ordered legacy members\n\nz.fits SCI\na.fits\nz.fits SCI\n')
    (fixture / 'missing-member').write_text('missing.fits\n')
    (fixture / 'empty').write_text('# comment only\n\n')
    (fixture / 'long-line').write_text('z.fits ' + 'a' * 1100 + '\n')
    (fixture / 'nul').write_bytes(b'z.fits\0SCI\n')
    (fixture / 'quoted-space').write_text('"with space.fits"\n')
    # Presence of the usual default filename must not trigger a BPM lookup.
    (fixture / 'members/OCAM_BPM_1x1.fits').write_text('not a selected mask\n')
    before = {str(p.relative_to(fixture)): sha(p) for p in fixture.rglob('*') if p.is_file()}
    sources = [root / 'mefpp2' / p for p in (
        'ins/mef/common/mef_input_request.c', 'ins/mef/common/mef_input_request.h',
        'ins/mef/common/mef_runtime.c', 'ins/mef/common/mef_runtime.h',
        'tests/input_request_probe.c', 'tests/input_request_contract.py',
        'src/unix/charmatrix.c', 'src/unix/parse_tok.c', 'src/iproc/framelist.c')]
    source_hashes = {str(p): sha(p) for p in sources}
    original_cwd = Path.cwd()
    report = {'status': 'running', 'host': platform.node(), 'platform': platform.platform(),
              'python': sys.executable, 'probe': str(probe), 'probe_sha256': sha(probe),
              'source_sha256': source_hashes, 'commands': [], 'fixture_sha256': before,
              'diagnostic_environment': {k: os.environ.get(k) for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS', 'LSAN_OPTIONS')},
              'scope': 'synthetic file/list requests only; no engine, header/pixel reading or reduction'}
    cases = ['omitted', 'selected', 'direct', 'missing-bpm', 'missing-member', 'empty',
             'long-line', 'nul', 'quoted-space', 'directory', 'unknown-base',
             'unknown-image', 'ambiguous', 'no-guess', 'inconsistent-bpm', 'ownership', 'ownership-selected']
    directories = [work / 'unrelated one', work / 'unrelated two']
    for directory in directories:
        directory.mkdir()

    def run(argv, label, cwd):
        completed = subprocess.run(list(map(str, argv)), cwd=cwd, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, timeout=90)
        log = work / (label + '.log')
        log.write_bytes(completed.stdout)
        report['commands'].append({'argv': list(map(str, argv)), 'cwd': str(cwd),
                                   'exit_status': completed.returncode, 'log': log.name,
                                   'log_sha256': sha(log)})
        if completed.returncode:
            raise RuntimeError('STOP: inspect ' + str(log))
        return completed.stdout.decode('utf-8').splitlines()

    try:
        legacy = run([probe, 'legacy', fixture / 'lists/input.list'], 'legacy', fixture / 'members')
        names = [line.removeprefix('LEGACY:') for line in legacy if line.startswith('LEGACY:')]
        if names != ['z.fits', 'a.fits', 'z.fits']:
            raise RuntimeError('Legacy ordering/duplicate fixture mismatch')
        by_file = {
            'z.fits': [('asset:z', 'DET-B', 2, 1), ('asset:z', 'DET-A', 1, 1)],
            'a.fits': [('asset:a', 'DET-A', 0, 0)],
        }
        expected = ['IMAGE:%s|%s|%s|%d|%d' % (asset, detector, fixture / 'members' / name, hdu, extver)
                    for name in names for asset, detector, hdu, extver in by_file[name]]
        for case in cases:
            outputs = []
            for i, directory in enumerate(directories):
                lines = run([probe, case, fixture], '%s-%d' % (case, i), directory)
                outputs.append([line for line in lines if line.startswith(('IMAGE:', 'BPM:', 'REJECTED:', 'OWNERSHIP:', 'OWNERSHIP-INVALID:'))])
            if outputs[0] != outputs[1]:
                raise RuntimeError('Cwd-dependent output: ' + case)
            images = [line for line in outputs[0] if line.startswith('IMAGE:')]
            if case in ('omitted', 'selected', 'ownership', 'ownership-selected') and images != expected:
                raise RuntimeError('Ordered descriptor mismatch: ' + case)
            if case == 'omitted' and [x for x in outputs[0] if x.startswith('BPM:')] != ['BPM:DET-B:1', 'BPM:DET-A:1']:
                raise RuntimeError('Omitted BPM was not retained')
            if case == 'selected' and 'BPM:DET-A:2' not in outputs[0]:
                raise RuntimeError('Selected BPM was not retained')
            if case == 'direct' and images != ['IMAGE:asset:a|DET-A|%s|0|0' % (fixture / 'members/with space.fits')]:
                raise RuntimeError('Direct primary path with spaces mismatch')
            print('PASS:', case, 'from both unrelated directories', flush=True)
        report['status'] = 'input-request-passed'
        report['case_count'] = len(cases)
        report['execution_directories'] = 2
    except Exception as error:
        report['status'] = 'stopped'; report['error'] = str(error)
        raise
    finally:
        report['fixture_unchanged'] = before == {str(p.relative_to(fixture)): sha(p) for p in fixture.rglob('*') if p.is_file()}
        report['source_unchanged'] = source_hashes == {str(p): sha(p) for p in sources}
        report['cwd_unchanged'] = Path.cwd() == original_cwd
        if not all(report[k] for k in ('fixture_unchanged', 'source_unchanged', 'cwd_unchanged')):
            report['status'] = 'stopped-preservation'
        (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
        print('REPORT:', work / 'run-provenance.json', flush=True)
    if report['status'] != 'input-request-passed':
        raise SystemExit('STOP: preservation failed')


if __name__ == '__main__':
    main()
