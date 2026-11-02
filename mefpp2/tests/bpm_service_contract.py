"""Synthetic typed BPM service, using actual WFI/OmegaCAM PAF snapshots.

Purpose: verify raw-copy/scan/trim/bias/core composition, bit/binary prior
semantics, configuration/HDU separation and lifetimes/failures. Inputs: generated
arrays in the C probe, no observational files. Actions: run both instruments in
a retained private directory. Pass: eight mode/scan controls per instrument,
unchanged configuration bytes and successful failure/owner assertions. This
does not certify acquisition admission, a recipe CLI or scientific calibration.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--probe', type=Path, required=True)
    p.add_argument('--work-parent', type=Path, required=True)
    a = p.parse_args()
    a.work_parent.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix='bpm-service-', dir=a.work_parent))
    report = dict(status='running', scope='synthetic in-memory service only', commands=[])
    try:
        # Actual instrument snapshots; generated pixels and explicit config slot.
        for instrument in ('wfi', 'omegacam'):
            paf = a.source_root.resolve() / 'mefpp2/ins/mef/config' / (instrument + '.paf')
            before = hashlib.sha256(paf.read_bytes()).hexdigest()
            log = run / (instrument + '.log')
            argv = [str(a.probe.resolve()), str(paf)]
            with log.open('x') as stream:
                result = subprocess.run(argv, cwd=run, stdout=stream, stderr=subprocess.STDOUT, timeout=120)
            report['commands'].append(dict(argv=argv, exit=result.returncode, log=str(log)))
            assert result.returncode == 0, log.read_text()[-12000:]
            assert log.read_text().count('PASS: typed BPM mode=') == 8
            assert hashlib.sha256(paf.read_bytes()).hexdigest() == before
        report['status'] = 'passed'
    finally:
        (run / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')
        print('RETAINED BPM SERVICE:', run)
    print('PASS: two instrument snapshots, 16 mode/scan controls and service failure/lifetime checks')


if __name__ == '__main__':
    main()
