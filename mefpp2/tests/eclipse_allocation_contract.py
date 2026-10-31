"""Actual connected bias dependency NULL-return controls, #144/#171."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from bias_service_contract import fixtures, digest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root', type=Path, required=True)
parser.add_argument('--probe', type=Path, required=True)
parser.add_argument('--work-parent', type=Path, required=True)
args = parser.parse_args()
root = args.source_root.resolve(strict=True)
probe = args.probe.resolve(strict=True)
work = Path(tempfile.mkdtemp(prefix='eclipse-allocation-', dir=args.work_parent)).resolve()
original_cwd = Path.cwd()
report = {'status': 'running', 'repository': str(root),
          'purpose': 'Synthetic bias dependency NULL-return and exact regression controls',
          'retention': 'Preserve failed and corrected attempts; no installation',
          'probe': str(probe), 'probe_sha256': digest(probe), 'commands': []}
if (root / '.git').exists():
    for key, command in (('commit', ['rev-parse', 'HEAD']),
                         ('branch', ['branch', '--show-current']),
                         ('dirty_state', ['status', '--porcelain=v1'])):
        report[key] = subprocess.check_output(['git', '-C', str(root), *command], text=True).strip()
else:
    report['source_state'] = 'Exported source; parent runner records exact commit/tree'
def save():
    (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
print('WORK DIRECTORY:', work, flush=True)
try:
    # Preparation: retain the accepted synthetic file/FITS fixtures and exact hashes.
    fixture = fixtures(work)
    before = {str(p): digest(p) for p in fixture.iterdir()}
    for instrument in ('omegacam', 'wfi'):
        paf = root / 'mefpp2/ins/mef/config' / (instrument + '.paf')
        log = work / (instrument + '.log')
        argv = [str(probe), str(paf), str(fixture)]
        # Processing: actual service/kernel/dependency code, accepted numerical
        # oracle profiles, then exhaustive single/persistent allocation sweeps.
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=work, stdout=stream, stderr=subprocess.STDOUT, timeout=140)
        report['commands'].append({'instrument': instrument, 'argv': argv, 'cwd': str(work),
                                   'exit_status': result.returncode, 'log_sha256': digest(log)})
        save()
        text = log.read_text(errors='replace')
        if result.returncode != 0:
            print(text[-14000:], flush=True)
            raise RuntimeError(f'{instrument} failed: {result.returncode}; retain {log}')
        # Verification: no signal, incomplete sweep or sanitizer finding is accepted.
        assert text.count('exact legacy pixels/QC and input/result lifetimes') == 8
        assert text.count('PASS: direct ') == 8
        assert text.count('dependency positions x2, recovery and preserved sources') == 2
        assert 'PASS: Eclipse dependency failure contract' in text
        assert 'ERROR: AddressSanitizer' not in text and 'runtime error:' not in text
        print('PASS:', instrument, '8 exact legacy profiles, 8 direct controls and complete dependency sweeps', flush=True)
    # Preservation: synthetic source bytes and caller directory remain unchanged.
    assert before == {str(p): digest(p) for p in fixture.iterdir()}
    assert Path.cwd() == original_cwd
    report['status'] = 'passed'
except BaseException as exc:
    report.update(status='failed', error=repr(exc))
    raise
finally:
    save()
    print('EVIDENCE:', work, flush=True)
