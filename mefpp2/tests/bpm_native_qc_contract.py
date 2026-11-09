"""Actual native BPM results -> shared product QC, with preserved file inputs.

The default gate checks C typed records and FITS without an ASDF dependency.
With --asdf-python, the probe must use the existing native ASDF writer; a
separate reader validates schema, every input binding and stored histograms.
"""
import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from astropy.io import fits
from bpm_files_contract import fixture, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    parser.add_argument('--asdf-python', type=Path)
    parser.add_argument('--adapter', type=Path)
    parser.add_argument('--source-revision', default='0000000000000000000000000000000000000000')
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    assert not args.adapter or args.asdf_python, 'Native CLI verification requires the independent ASDF reader'
    environment = dict(os.environ, MEFPP_TEST_REVISION=args.source_revision)
    run = Path(tempfile.mkdtemp(prefix='bpm-native-qc-', dir=args.work_parent)).resolve()
    print('RETAINED NATIVE BPM QC:', run, flush=True)
    for index, (mode, kind, count, policy) in enumerate(
            [(0, 1, 12, 'normal'), (1, 3, 10, 'normal'),
             (0, 0, 10, 'normal'), (0, 4, 10, 'no_mad')]):
        case = run/str(index)
        case.mkdir()
        raw, controls, reduced = (case/name for name in ('raw', 'orchestration', 'reduced'))
        fixture(raw, count, kind)
        controls.mkdir()
        calibrations = reduced/'cal'
        calibrations.mkdir(parents=True)
        for name in ('bias.fits', 'prior.fits'):
            if (raw/name).exists():
                (raw/name).rename(calibrations/name)
        config = controls/'instrument.paf'
        text = (root/'mefpp2/ins/mef/config/wfi.paf').read_text()
        overrides = {'MEF.BPM.PROPFLAG': mode, 'MEF.BPM.HGAINTHR': 1.5,
                     'MEF.USE.PRESCAN': 1, 'MEF.USE.OVERSCAN': 1,
                     'MEF.SCANREJ.MIN': 0, 'MEF.SCANREJ.MAX': 0,
                     'MEF.PRESCAN.X.MIN.CHIP3': 1, 'MEF.PRESCAN.X.MAX.CHIP3': 2,
                     'MEF.OVERSCAN.X.MIN.CHIP3': 9, 'MEF.OVERSCAN.X.MAX.CHIP3': 10,
                     'MEF.CROP.X.MIN.CHIP3': 3, 'MEF.CROP.X.MAX.CHIP3': 8,
                     'MEF.CROP.Y.MIN.CHIP3': 2, 'MEF.CROP.Y.MAX.CHIP3': 5}
        for key, value in overrides.items():
            text, replaced = re.subn(r'^'+re.escape(key)+r'\s+[^;\n]*;',
                                    key+' '+str(value)+';', text, flags=re.M)
            assert replaced == 1, key
        config.write_text(text)
        inputs = [*raw.glob('*.fits'), *calibrations.glob('*.fits'), config]
        before = {str(path): digest(path) for path in inputs}
        for path in inputs:
            path.chmod(0o444)
        raw.chmod(0o555)
        output = reduced/'cal/bpm/run'
        output.mkdir(parents=True)
        command = [str(args.probe.resolve()), str(config), str(raw), str(count), str(kind),
                   '1', str(mode), policy, str(output), str(calibrations)]
        result = subprocess.run(command, cwd=controls, env=environment, capture_output=True, text=True, timeout=60)
        (output/'test.log').write_text(result.stdout+result.stderr)
        assert result.returncode == 0, result.stdout+result.stderr
        handoff = json.loads((output/'handoff.json').read_text())
        with fits.open(output/'product.fits', memmap=False) as images:
            reasons = np.bincount(images[0].data.ravel(), minlength=256).tolist()
            coverage = np.bincount(images['COVERAGE'].data.ravel(), minlength=3).tolist()
        assert handoff['reason_histogram'] == reasons
        assert handoff['fit_histogram'] == coverage
        if args.asdf_python:
            check = r'''
import asdf,json,sys
from pathlib import Path
output,root,reference_directory=map(Path,sys.argv[1:])
with asdf.open(output/'product.asdf', custom_schema=(root/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json').as_uri(),lazy_load=False) as saved:
    qc=saved.tree['qc']
    assert qc['extensions']['record_scope']=='one_final_primary_image_product'
    assert qc['provenance']['operation']=='cal.bpm'
    native=json.loads(qc['extensions']['operation_context']['snapshot'])
    reference=json.loads((reference_directory/'handoff.json').read_text())
    reference['output']=str(output/'product.fits')
    assert native==reference
    assert qc['provenance']['producer']['source_revision']==native['source_revision']
    detector=qc['characterization']['detectors'][0]
    assert detector['output_hdu']==0
    metrics={m['name']:m for m in detector['measurements']}
    assert metrics['reason_histogram']['value']==native['reason_histogram']
    assert metrics['fit_histogram']['value']==native['fit_histogram']
    for i,(binding,record,source) in enumerate(zip(qc['inputs'],qc['embedded_input_records'],native['inputs'])):
        assert record['file']['location']==source['file']['path']
        assert record['record_id']==source['file']['asset_id']
        assert record['original_index']==i
        assert binding['participation_by_detector'][0]['status']==('used' if source['included'] else 'rejected')
        values={m['name']:m for m in record['detectors'][0]['measurements']}
        assert record['detectors'][0]['source_hdu']==source['file']['hdu']
        assert values['integration_seconds']['value']==source['integration_seconds']
        assert values['reference_level']['value']==source['reference_level']
        assert values['reference_samples']['value']==source['reference_samples']
    assert len(qc['embedded_input_records'])==len(native['inputs'])
print('PASS: native ASDF schema, original input/HDU mapping and complete operation context')
'''
            checked = subprocess.run([str(args.asdf_python), '-c', check, str(output), str(root), str(output)],
                                     cwd=controls, capture_output=True, text=True, timeout=60)
            assert checked.returncode == 0, checked.stdout+checked.stderr
            print(checked.stdout.strip(), flush=True)
        if args.adapter:
            listing, roi = controls/'flats.tsv', controls/'roi.txt'
            listing.write_text(''.join(f'{raw}/flat-{i}.fits\t{2 if i%2 else 0}\t{i//2}\n' for i in range(count)))
            roi.write_text('1 4 1 4\n3 6 1 4\n')
            native = output/'native-cli'
            native.mkdir()
            argv = [str(args.adapter), 'cal', 'bpm', '--pafname', str(config),
                '--flats', str(listing), '--detector-id', 'D', '--config-detector', '2',
                '--readout-id', 'readout:test', '--bin-x', '1', '--bin-y', '1',
                '--master-bias', str(calibrations/'bias.fits'), '--bias-hdu', '0',
                '--input-bpm', str(calibrations/'prior.fits') if kind else 'omitted',
                '--bpm-encoding', 'omitted' if not kind else 'binary' if kind>=3 else 'reason8',
                '--reject-bits', '255', '--acquisition', 'quick', '--exposure-key', 'EXPTIME',
                '--exposure-hdu', '0', '--saturation', '1000', '--upper-fraction', '.85',
                '--minimum-span', '.15', '--maximum-pair-difference', '.02',
                '--roi-file', str(roi), '--mad', 'no' if policy=='no_mad' else 'yes',
                '--output-mode', 'new' if kind>=3 else 'combined',
                '--created-at', '2026-11-02T19:00:00Z', '--output', str(native/'product.fits'),
                '--work-dir', str(native), '--log-path', str(native/'native.log'),
                '--config-record', str(native/'configuration.json'), '--native-asdf', str(native/'product.asdf')]
            if kind:
                argv += ['--bpm-hdu', '0', '--bpm-coordinates', 'active' if kind in (1,3) else 'raw']
                argv += ['--bpm-good-value', '0' if kind==3 else '1'] if kind>=3 else ['--bpm-registry', 'WENU_BPM_V1']
            completed = subprocess.run(argv, cwd=controls, capture_output=True, text=True, timeout=60)
            (native/'command.log').write_text(completed.stdout+completed.stderr)
            assert completed.returncode == 0, completed.stdout+completed.stderr
            assert not (native/'handoff.json').exists()
            assert 'BPM_ASDF_WRITTEN' in (native/'native.log').read_text()
            with fits.open(native/'product.fits') as actual, fits.open(output/'product.fits') as reference:
                assert len(actual)==len(reference)
                for actual_hdu, reference_hdu in zip(actual, reference):
                    assert np.array_equal(actual_hdu.data, reference_hdu.data)
            checked = subprocess.run([str(args.asdf_python), '-c', check, str(native), str(root), str(output)],
                                     cwd=controls, capture_output=True, text=True, timeout=60)
            assert checked.returncode == 0, checked.stdout+checked.stderr
            saved = {str(path):digest(path) for path in native.iterdir() if path.is_file()}
            repeated = subprocess.run(argv, cwd=controls, capture_output=True, text=True, timeout=60)
            assert repeated.returncode != 0
            assert saved == {str(path):digest(path) for path in native.iterdir() if path.is_file()}
            print('PASS: production native CLI, exact FITS arrays, native ASDF, no Python handoff and no-clobber', flush=True)
        assert before == {str(path): digest(path) for path in inputs}
        assert len(list(raw.iterdir())) == count
        assert not list(controls.glob('*.fits'))
    print('PASS: four native BPM QC cases; orchestration cwd, read-only raw/calibrations, reduced outputs')


if __name__ == '__main__':
    main()
