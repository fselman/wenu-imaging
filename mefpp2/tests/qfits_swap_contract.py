"""Bounded actual qfits forced-swap and ownership controls (#164/#168)."""
import argparse
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--probe', type=Path, required=True)
parser.add_argument('--work-parent', type=Path, required=True)
args = parser.parse_args()
probe = args.probe.resolve(strict=True)
work = Path(tempfile.mkdtemp(prefix='qfits swap ', dir=args.work_parent)).resolve()
report = {'status': 'running', 'probe': str(probe),
          'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(), 'cases': []}
def save():
    (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
print('WORK DIRECTORY:', work, flush=True)
try:
    # Preparation: isolated scratch, alternate directory and unrelated caller per case.
    cases = ('ram', 'success', 'exit', 'signal', 'realloc', 'write-eintr', 'write-short',
             'open', 'truncate', 'write', 'write-zero', 'map', 'unlink',
             'collision', 'symlink', 'cleanup-collision', 'overflow',
             'registration-overflow', 'unmap', 'close')
    successes = {'ram', 'success', 'exit', 'realloc', 'write-eintr', 'write-short', 'cleanup-collision'}
    for label in cases:
        root = work / label; root.mkdir()
        scratch, alternate, caller = (root / name for name in ('scratch space', 'alternate', 'caller'))
        for p in (scratch, alternate, caller): p.mkdir()
        target = root / 'sentinel'; target.write_bytes(b'unowned target')
        target_before = (target.read_bytes(), target.stat().st_mode, target.stat().st_mtime_ns)
        argv = [str(probe), label, str(scratch), str(target if label == 'symlink' else alternate)]
        log = root / 'probe.log'
        # Forced fallback/recovery: only this probe injects malloc/syscall outcomes.
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=caller, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=30)
        item = {'label': label, 'argv': argv, 'cwd': str(caller), 'exit_status': result.returncode}
        report['cases'].append(item); save()
        expected = -signal.SIGTERM if label == 'signal' else (0 if label in successes else 1)
        assert result.returncode == expected, (label, result.returncode, log)
        output = log.read_text(errors='replace')
        assert 'PROBE FAILURE' not in output and 'ERROR: AddressSanitizer' not in output
        assert 'runtime error:' not in output
        # Ownership verification: C exit observer checks descriptors/counters and retained RAM.
        if label != 'signal':
            assert 'PASS: descriptors, owners and RAM after exit cleanup' in output
        if label not in ('ram', 'success', 'cleanup-collision'):
            assert 'PASS: retained allocation data' in output
        files = list(scratch.iterdir())
        if label in ('collision', 'cleanup-collision'):
            assert len(files) == 1 and files[0].read_bytes() == b'sentinel'
        elif label == 'symlink':
            assert len(files) == 1 and files[0].is_symlink() and files[0].resolve() == target
        else:
            assert not files, (label, files)
        assert not list(alternate.iterdir()) and not list(caller.iterdir())
        assert target_before == (target.read_bytes(), target.stat().st_mode, target.stat().st_mtime_ns)
        print('PASS:', label, flush=True)
    report['status'] = 'passed'
    print('PASS: 20 forced-swap/ownership cases; no system RAM exhaustion', flush=True)
except BaseException as exc:
    report.update(status='failed', error=repr(exc))
    raise
finally:
    save()
    print('EVIDENCE:', work, flush=True)
