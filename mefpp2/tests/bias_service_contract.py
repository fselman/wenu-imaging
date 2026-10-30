"""Run synthetic bias equivalence/lifetime controls; never reduce real FITS."""
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def card(key, value):
    return f'{key:<8}= {value:>20}'.ljust(80).encode('ascii')


def header(cards):
    data = b''.join(card(key, value) for key, value in cards) + b'END'.ljust(80)
    return data.ljust((len(data) + 2879) // 2880 * 2880, b' ')


def fixtures(work):
    directory = work / 'synthetic'
    directory.mkdir()
    if any(c.isspace() for c in str(directory)):
        raise RuntimeError('Legacy list fixture members require paths without whitespace')
    # Tiny MEFs exercise the actual mef_build_cal file/list/extension bridge.
    # The service receives the matching in-memory images; no astronomical data.
    primary = header([('SIMPLE', 'T'), ('BITPIX', '8'), ('NAXIS', '0'), ('EXTEND', 'T')])
    extension = header([('XTENSION', "'IMAGE   '"), ('BITPIX', '-32'), ('NAXIS', '2'),
                        ('NAXIS1', '10'), ('NAXIS2', '6'), ('PCOUNT', '0'), ('GCOUNT', '1')])
    for profile in range(8):
        members = []
        for i in range(6 if profile == 1 else 5):
            values = []
            for y in range(6):
                for x in range(10):
                    value = 100 + y + 3*i
                    if 2 <= x <= 7:
                        value += 10 + i + x + 2*y
                        if profile == 2 and i == 4:
                            value += 100
                        if profile == 3:
                            value -= i
                    values.append(value)
            pixels = struct.pack('>60f', *values).ljust(2880, b'\0')
            path = directory / f'profile-{profile}-frame-{i}.fits'
            path.write_bytes(primary + extension + pixels + extension + pixels)
            members.append(str(path))
        (directory / f'profile-{profile}.list').write_text('\n'.join(members) + '\n')
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    probe = args.probe.resolve(strict=True)
    original_cwd = Path.cwd()
    work = Path(tempfile.mkdtemp(prefix='m1-bias-', dir=args.work_parent.resolve(strict=True)))
    print('WORK DIRECTORY:', work, flush=True)
    fixture_directory = fixtures(work)
    fixture_before = {str(p): digest(p) for p in fixture_directory.iterdir()}
    common = root / 'mefpp2/ins/mef/common'
    inputs = [p for p in common.iterdir() if p.suffix in ('.c', '.h', '.def')]
    inputs += [root / 'mefpp2/tests' / p for p in (
        'bias_service_probe.c', 'bias_legacy_reference.c', 'bias_service_contract.py')]
    inputs += [root / 'mefpp2/ins/mef/config' / (p + '.paf') for p in ('omegacam', 'wfi')]
    before = {str(p): digest(p) for p in inputs}
    report = {'status': 'running', 'host': platform.node(), 'platform': platform.platform(),
              'python': sys.executable, 'probe': str(probe), 'probe_sha256': digest(probe),
              'commands': [], 'source_sha256': before, 'fixture_sha256': fixture_before,
              'diagnostic_environment': {k: os.environ.get(k) for k in
                  ('ASAN_OPTIONS', 'UBSAN_OPTIONS', 'LSAN_OPTIONS')},
              'scope': 'synthetic ADU bias service and legacy file/list/FITS bridge; no astronomical-data reduction, recipe launch or installation; variance unavailable'}
    try:
        # Compare exact frozen legacy arithmetic/QC, then failure/ownership controls.
        for instrument in ('omegacam', 'wfi'):
            paf = root / 'mefpp2/ins/mef/config' / (instrument + '.paf')
            argv = [str(probe), str(paf), str(fixture_directory)]
            log = work / (instrument + '.log')
            with log.open('w') as stream:
                completed = subprocess.run(argv, cwd=work, stdout=stream,
                                           stderr=subprocess.STDOUT, timeout=180)
            report['commands'].append({'argv': argv, 'cwd': str(work),
                'exit_status': completed.returncode, 'log': str(log), 'log_sha256': digest(log)})
            if completed.returncode != 0:
                raise RuntimeError(f'{instrument} failed; retain {log}; do not rerun')
            text = log.read_text()
            if text.count('exact legacy pixels/QC and input/result lifetimes') != 8:
                raise RuntimeError(f'Incomplete equivalence coverage: {log}')
            if 'zero new owners' not in text or 'PASS: bias service contract;' not in text:
                raise RuntimeError(f'Incomplete lifecycle coverage: {log}')
            print('PASS:', instrument, '8 legacy equivalence profiles and failure/lifetime controls', flush=True)
        # Verification only: the source/configuration fixtures and parent cwd stay unchanged.
        report['source_unchanged'] = before == {str(p): digest(p) for p in inputs}
        report['cwd_unchanged'] = original_cwd == Path.cwd()
        report['fixtures_unchanged'] = fixture_before == {str(p): digest(p) for p in fixture_directory.iterdir()}
        if not report['source_unchanged'] or not report['cwd_unchanged'] or not report['fixtures_unchanged']:
            raise RuntimeError('Preservation check failed')
        report['status'] = 'bias-service-passed'
    except Exception as error:
        report['status'] = 'stopped'
        report['error'] = str(error)
        raise
    finally:
        target = work / 'run-provenance.json'
        target.write_text(json.dumps(report, indent=2) + '\n')
        print('REPORT:', target, flush=True)


if __name__ == '__main__':
    main()
