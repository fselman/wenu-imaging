"""Complete cal bpm command on synthetic inputs, no installation.

Purpose: check orchestration and explicit CLI binding after component acceptance.
Inputs: tiny generated primary/MEF flats, selected bias and optional prior.
Actions: PAF/TOML native command, common ASDF publication and failure boundaries.
Pass: exact byte product/coverage, verified references, truthful receipt on every
failure, no overwrite or mutation. Existing numerical contracts are retained.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from astropy.io import fits
from bpm_files_contract import fixture, digest
from config_toml_contract import render_snapshot


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source-root', 'adapter', 'asdf-python', 'work-parent'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    a.work_parent.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix='bpm-complete-', dir=a.work_parent)).resolve()
    print('RETAINED BPM COMPLETION:', run, flush=True)
    source = a.source_root.resolve()
    module = source/'Pycavi2/pycavi/pycavi/pycavi_bpm_qc.py'
    adapter = a.adapter.resolve()
    original_adapter = digest(adapter)
    report = dict(status='running', cases=[], commands=[], adapter_sha256=original_adapter)
    immutable = {}

    def save():
        (run/'qualification.json').write_text(json.dumps(report, indent=2)+'\n')

    def case(name, *, kind=1, mode=0, count=10, toml=None, fail=None):
        work = run/name
        work.mkdir()
        raw = work/'input with spaces'
        fixture(raw, count, kind, 'unavailable')
        text = (source/'mefpp2/ins/mef/config/wfi.paf').read_text()
        overrides = {'MEF.BPM.PROPFLAG': mode, 'MEF.BPM.HGAINTHR': 1.5,
                     'MEF.USE.PRESCAN': 1, 'MEF.USE.OVERSCAN': 1,
                     'MEF.SCANREJ.MIN': 0, 'MEF.SCANREJ.MAX': 0,
                     'MEF.PRESCAN.X.MIN.CHIP3': 1, 'MEF.PRESCAN.X.MAX.CHIP3': 2,
                     'MEF.OVERSCAN.X.MIN.CHIP3': 9, 'MEF.OVERSCAN.X.MAX.CHIP3': 10,
                     'MEF.CROP.X.MIN.CHIP3': 3, 'MEF.CROP.X.MAX.CHIP3': 8,
                     'MEF.CROP.Y.MIN.CHIP3': 2, 'MEF.CROP.Y.MAX.CHIP3': 5}
        for key, value in overrides.items():
            text, n = re.subn(r'^'+re.escape(key)+r'\s+[^;\n]*;', key+' '+str(value)+';', text, flags=re.M)
            assert n == 1, key
        config = raw/('bpm.toml' if toml else 'bpm.paf')
        config.write_text(render_snapshot(toml) if toml else text)
        listing = raw/'flats.tsv'
        listing.write_text(''.join(f'{raw}/flat-{i}.fits\t{99 if fail=="native" and i==0 else (2 if i%2 else 0)}\t{i//2}\n' for i in range(count)))
        roi = raw/'roi.txt'
        roi.write_text('1 4 1 4\n3 6 1 4\n')
        if fail == 'manifest':
            listing.write_text(str(raw/'flat-0.fits')+'\t0\t0\textra\n')
        for path in raw.iterdir():
            immutable[path] = digest(path)
        qcdir = work/'QC'
        qcdir.mkdir()
        native = ['cal', 'bpm', '--config' if toml else '--pafname', str(config),
            '--flats', str(listing), '--detector-id', 'D', '--config-detector', '2',
            '--readout-id', 'readout:test', '--bin-x', '1', '--bin-y', '1',
            '--master-bias', str(raw/'bias.fits'), '--bias-hdu', '0',
            '--input-bpm', str(raw/'prior.fits') if kind else 'omitted',
            '--bpm-encoding', 'omitted' if not kind else 'binary' if kind>=3 else 'reason8',
            '--reject-bits', '255', '--acquisition', 'provisional' if count==2 else 'quick',
            '--exposure-key', 'EXPTIME', '--exposure-hdu', '0', '--saturation', '1000',
            '--upper-fraction', '.85', '--minimum-span', '.15', '--maximum-pair-difference', '.02',
            '--roi-file', str(roi), '--mad', 'yes', '--output-mode', 'new' if kind>=3 else 'combined',
            '--created-at', '2026-11-02T20:00:00Z', '--output', str(work/'bpm.fits'),
            '--work-dir', str(work), '--log-path', str(work/'native.log'),
            '--config-record', str(work/'configuration.json'), '--qc-record', str(work/'handoff.json')]
        if kind:
            native += ['--bpm-hdu', '0', '--bpm-coordinates', 'active' if kind in (1,3) else 'raw']
            native += ['--bpm-good-value', '0' if kind==3 else '1'] if kind>=3 else ['--bpm-registry', 'WENU_BPM_V1']
        if fail == 'binary-combined':
            native[native.index('--output-mode')+1] = 'combined'
        receipt = work/'execution.json'
        sentinel = work/'bpm.fits' if fail=='preflight' else receipt if fail=='receipt' else None
        if sentinel:
            sentinel.write_bytes(b'protected earlier attempt\n')
        native_adapter = adapter
        if fail == 'qc':
            # Simulate a QC destination appearing after preflight/native success.
            # This wrapper is test scaffolding, never a production injection hook.
            native_adapter = work/'late-conflict'
            native_adapter.write_text('#!'+str(a.asdf_python)+'\nimport subprocess,sys\nfrom pathlib import Path\n'
                f'r=subprocess.run([{str(adapter)!r},*sys.argv[1:]])\n'
                f'if r.returncode==0: Path({str(qcdir/"flat-0.asdf")!r}).write_bytes(b"protected late file")\n'
                'sys.exit(r.returncode)\n')
            native_adapter.chmod(0o700)
        command = [str(a.asdf_python), '-B', str(module), '--native-adapter', str(native_adapter),
            '--receipt', str(receipt), '--qc-directory', str(qcdir), '--assessment-id', 'fixture:'+name, '--', *native]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
        completed = subprocess.run(command, capture_output=True, text=True, env=env, timeout=120)
        (work/'command.log').write_text(completed.stdout+'\n'+completed.stderr)
        report['commands'].append(dict(name=name, argv=command, exit_status=completed.returncode))
        save()
        assert (completed.returncode==0) == (fail is None), (work/'command.log').read_text()[-6000:]
        if sentinel:
            assert sentinel.read_bytes() == b'protected earlier attempt\n'
        if fail != 'receipt':
            evidence = json.loads(receipt.read_text())
            if fail:
                assert evidence['status']=='failed' and 'BPM_RECIPE complete' not in completed.stdout
                expected_stage = 'qc' if fail=='qc' else 'preflight' if fail in ('preflight','manifest') else 'native'
                assert evidence['stage'] == expected_stage, evidence
                if fail=='qc':
                    assert evidence['native_exit_status']==0 and (work/'bpm.fits').is_file()
                    assert (qcdir/'flat-0.asdf').read_bytes()==b'protected late file'
                    assert not (qcdir/'bpm.asdf').exists()
                else:
                    assert not (work/'bpm.fits').exists() or fail=='preflight'
            else:
                assert evidence['status']==evidence['stage']=='complete'
                assert evidence['native_exit_status']==0 and evidence['qc_records_verified']==count+2+bool(kind)
                assert evidence['adapter_sha256']==original_adapter and evidence['completion_code_sha256']==digest(module)
                assert len(evidence['qc_record_digest'])==64 and 'BPM_RECIPE complete' in completed.stdout
                assert len(list(qcdir.glob('*.asdf')))==count+2+bool(kind)
                assert b'#ASDF_STANDARD 1.6.0' in (qcdir/'bpm.asdf').read_bytes()[:120]
                with fits.open(work/'bpm.fits') as h:
                    h.verify('exception')
                    assert h[0].header['BITPIX']==8 and h[0].data.shape==(4,6)
                    assert h[0].data[0,0]==(5 if kind in (1,2) else 4)
                    assert h[0].data[0,3]==h['COVERAGE'].data[0,3]==h['NSAMPLE'].data[0,3]==h['SELECTION'].data[0,3]==0
                    if kind>=3:
                        assert h[0].data[1,1]==0 and h['PRIORSEL'].data[1,1]==h['SELECTION'].data[1,1]==0
                if count==12:
                    handoff=json.loads((work/'handoff.json').read_text())
                    assert not handoff['inputs'][-1]['included'] and not handoff['inputs'][-2]['included']
                assert not list(work.glob('.mefpp-bpm-*'))
        report['cases'].append(name)
        save()
        return work

    try:
        first = case('quick-paf')
        snapshot = json.loads((first/'configuration.json').read_text())
        case('quick-toml', kind=2, toml=snapshot)
        case('binary-new', kind=3, mode=1)
        case('binary-one-raw', kind=4)
        case('excluded-flats', count=12)
        case('provisional-omitted', kind=0, count=2, mode=1)
        case('protected-output', fail='preflight')
        case('wrong-hdu', fail='native')
        case('malformed-manifest', fail='manifest')
        case('protected-receipt', fail='receipt')
        case('late-qc-conflict', fail='qc')
        case('binary-combined', kind=3, fail='binary-combined')
        assert all(digest(p)==h for p,h in immutable.items())
        assert digest(adapter)==original_adapter
        report['status']='passed'
        print('PASS: 12 complete BPM command cases; PAF/TOML, priors, quick/provisional, exact byte/coverage, frozen ASDF and failure preservation')
    finally:
        save()


if __name__ == '__main__':
    main()
