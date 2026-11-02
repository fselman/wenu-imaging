"""Complete ASDF QC for the retained successful WFI CHIP1 native operation.

No native invocation, FITS rewrite, installation or overwrite of earlier evidence.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import runpy
import subprocess
import sys


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[2]
    repo = Path('/Users/fselman/Developer/wenu-imaging')
    old = Path('/Users/fselman/Software/build/wenu-imaging/mac-bpm-complete-Ia5qliwa')
    retained = Path('/Users/fselman/Software/build/wenu-imaging/wfi-first-bias-retry-pKBFGzsm')
    python = Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python')
    require(platform.system() == 'Darwin' and Path(sys.executable).resolve() == python.resolve(),
            'Use the retained Mac QC Python')
    work = args.run.resolve(strict=True)
    require(work.parent == retained.parent and not any(work.iterdir()), 'Fresh empty recovery directory required')
    guard = runpy.run_path(str(old/'source/Pycavi2/tests/qualify_inspection_stages.py'))
    prefix_identity = runpy.run_path(str(old/'source/Pycavi2/tests/qualify_libasdf_mac.py'))['prefix_identity']
    checkout = guard['checkout'](repo)
    require(subprocess.check_output(['/usr/bin/git', '-C', str(repo), 'rev-parse', 'HEAD']).decode().strip()
            == '47123eedaaa31b4464238ffaaf1b690f7d2cde40' and
            not subprocess.check_output(['/usr/bin/git', '-C', str(repo), 'status', '--porcelain']),
            'Protected clean checkout changed')
    protected = guard['protected_paths']()
    installed = [guard['identity'](p) for p in protected]
    environment = prefix_identity(python.parent.parent)
    receipt = json.loads((retained/'execution.json').read_text())
    previous = json.loads((retained/'inspection-run.json').read_text())
    require(receipt['status'] == 'failed' and receipt['stage'] == 'qc' and
            receipt['native_exit_status'] == 0 and all(previous['preservation'].values()),
            'Require preserved successful native operation with failed QC')
    files = dict(previous['input_sha256'])
    require(files and all(digest(p) == value for p, value in files.items()), 'Retained input/code bytes changed')
    require(digest(receipt['adapter']) == receipt['adapter_sha256'], 'Native adapter changed')
    product = Path(receipt['native_product'])
    require(product == retained/'WFI_MB_CHIP1.fits' and product.is_file(), 'Expected retained native product')
    # Keep every earlier artifact, including the failed receipt and any partial QC.
    for path in retained.rglob('*'):
        if path.is_file():
            files[str(path)] = digest(path)
    for path in source.rglob('*'):
        if path.is_file():
            files[str(path)] = digest(path)
    report = dict(status='running', operation='cal.bias.qc_recovery', native_reexecuted=False,
                  previous_receipt=str(retained/'execution.json'), native_product=str(product),
                  native_product_sha256=digest(product), locked_sha256=files,
                  scientific_acceptance=False)
    try:
        sys.path.insert(0, str(source/'Pycavi2/pycavi/pycavi'))
        import pycavi_bias_qc as bias
        import pycavi_qc as qc
        tree = bias.load_handoff(retained/'handoff.json')
        require(tree['output'] == str(product) and tree['detector_id'] == 'WIN1.CHIP1.OUT1' and
                len(tree['inputs']) == 10 and tree['bpm']['selected'], 'Retained handoff identity mismatch')
        destination = bias.publish_handoff(retained/'handoff.json', work,
            assessment_id=receipt['assessment_id']+':qc-recovery',
            created_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
        records = list(qc.traverse_records(destination, qc_root=work, max_records=12))
        require(len(records) == 12 and qc.read_record(destination).as_dict()['file']['location'] == str(product),
                'Expected product, ten raw records and one BPM binding')
        from astropy.io import fits
        with fits.open(product, mode='readonly', memmap=True) as hdus:
            hdus.verify('exception')
            require(len(hdus) == 2 and hdus[1].header['EXTNAME'] == 'WIN1.CHIP1.OUT1' and
                    hdus[1].shape == (4097, 2044), 'Unexpected bias FITS structure')
            (work/'product-headers.txt').write_text('\n\n'.join(str(h.header) for h in hdus)+'\n')
        report.update(status='complete_for_owner_inspection', qc_product=str(destination),
                      qc_records_verified=len(records), master=tree['master'], ron=tree['ron'])
        print('PRODUCT:', product, '[HDU 1]', flush=True)
        print('QC:', destination, flush=True)
        print('MASTER:', json.dumps(tree['master']), flush=True)
        print('RAW-PAIR RON:', json.dumps(tree['ron']), flush=True)
    except BaseException as error:
        report.update(status='failed', error=dict(type=type(error).__name__, message=str(error)))
        raise
    finally:
        checks = dict(checkout=checkout == guard['checkout'](repo),
            installed_files=installed == [guard['identity'](p) for p in protected],
            retained_qc_environment=environment == prefix_identity(python.parent.parent),
            locked_inputs_and_artifacts=all(digest(p) == value for p, value in files.items()))
        report['preservation'] = checks
        if not all(checks.values()):
            report['status'] = 'failed'
        (work/'qc-recovery.json').write_text(json.dumps(report, indent=2)+'\n')
        print('STATUS:', report['status'], flush=True)
        print('PRESERVATION:', checks, flush=True)
        require(all(checks.values()), 'Preservation failed; retain recovery evidence')


if __name__ == '__main__':
    main()
