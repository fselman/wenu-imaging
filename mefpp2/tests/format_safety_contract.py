"""Bounded actual-format controls, no observations or system exhaustion."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--probe', type=Path, required=True)
parser.add_argument('--work-parent', type=Path, required=True)
args = parser.parse_args()
probe = args.probe.resolve(strict=True)
work = Path(tempfile.mkdtemp(prefix='format-safety-', dir=args.work_parent)).resolve()
source = Path(__file__).resolve().parents[2]
report = dict(status='running', purpose=__doc__, repository=str(source),
              python=sys.executable, retention='Preserve all failed/corrected attempts',
              diagnostic_environment={k: os.environ.get(k) for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')},
              probe=str(probe),
              probe_sha256=hashlib.sha256(probe.read_bytes()).hexdigest(), commands=[])
if (source / '.git').exists():
    for key, command in (('commit', ['rev-parse', 'HEAD']),
                         ('branch', ['branch', '--show-current']),
                         ('dirty_state', ['status', '--porcelain=v1'])):
        report[key] = subprocess.check_output(['git', '-C', str(source), *command], text=True).strip()
else:
    report['source_state'] = 'Exported source; parent runner records exact commit/tree'
print('WORK DIRECTORY:', work, flush=True)
try:
    # Processing: actual formatter/message/header code with fixed test clock;
    # overflow guard runs separately and must fail explicitly, without a crash.
    for extra in ([], ['--swap-overflow'], ['--rtd-cwd-overflow']):
        argv = [str(probe), *extra]
        log = work / (extra[0][2:] + '.log' if extra else 'ordinary.log')
        cwd = work
        if extra == ['--rtd-cwd-overflow']:
            # Private nested cwd reaches the exchange-name boundary without
            # making an RTD connection or changing a user directory.
            while len(str(cwd)) < 500:
                cwd = cwd / ('d' * min(80, max(1, 500 - len(str(cwd)) - 1)))
                cwd.mkdir()
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=cwd, env={**os.environ, 'TZ': 'UTC', 'TERM': 'dumb'},
                                    stdout=stream, stderr=subprocess.STDOUT, timeout=30)
        text = log.read_text(errors='replace')
        report['commands'].append(dict(argv=argv, exit_status=result.returncode,
                                       log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
        # Verification: exact normal outputs/boundaries and explicit failed
        # overflow status; never accept a sanitizer report or signal.
        assert 'ERROR: AddressSanitizer' not in text and 'runtime error:' not in text, text[-5000:]
        if extra == ['--swap-overflow']:
            assert result.returncode == 47 and 'temporary filename too long' in text, text[-5000:]
        elif extra:
            assert result.returncode == 0 and 'RTD cwd overflow rejected offline' in text, text[-5000:]
        else:
            assert result.returncode == 0 and text.count('PASS:') == 8, text[-5000:]
        print('PASS:', extra or 'ordinary controls', flush=True)
    report['status'] = 'passed'
except BaseException as exc:
    report.update(status='failed', error=repr(exc))
    raise
finally:
    (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
    print('EVIDENCE:', work, flush=True)
