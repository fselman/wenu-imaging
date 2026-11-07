"""Verified native-ASDF recovery; no image calculations or raw-file access.

The native probe emits staging only. This independent ASDF6 reader validates
schema, complete measurement/array preservation, FITS scalar context and explicit
recovery provenance before exclusive final publication. The failed log stays as-is.
"""
import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import uuid
from collections.abc import Mapping
from bias_qc_fits_contract import verify

ROOT = Path(__file__).resolve().parents[2]


def exact(expected, actual, path='root'):
    """Full metadata comparison, including binary64 bits and sequence order."""
    if isinstance(expected, Mapping):
        assert isinstance(actual, Mapping) and set(expected) == set(actual), path
        for key in expected:
            exact(expected[key], actual[key], path + '/' + str(key))
    elif isinstance(expected, (list, tuple)):
        assert isinstance(actual, (list, tuple)) and len(expected) == len(actual), path
        for index, (a, b) in enumerate(zip(expected, actual)):
            exact(a, b, path + '/' + str(index))
    elif isinstance(expected, float):
        assert isinstance(actual, float), (path, type(actual))
        assert struct.pack('>d', expected) == struct.pack('>d', actual), path
    else:
        assert type(expected) is type(actual) and expected == actual, path


def expected_qc(original, fits, created, start, failed_log, revision):
    q = copy.deepcopy(original)
    previous = q['file']['id']
    assert previous == q['file']['location']
    q['file'].update(id=str(fits), location=str(fits), filename=fits.name)
    q['record'].update(assessment_id=str(fits), created_at=created)
    q['provenance']['producer'] = dict(
        name='mefpp_product_qc_recover_verified', version='1', source_revision=revision,
    )
    q['provenance']['recipe_start'] = start
    q['provenance']['log_path'] = str(failed_log)
    for detector in q['characterization']['detectors']:
        for measurement in detector['measurements']:
            measurement['sources'] = [str(fits) if s == previous else s
                                      for s in measurement['sources']]
    return q


def main():
    import asdf
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-asdf', 'fits', 'failed-log', 'assembly-log',
                 'native-probe', 'receipt'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--revision', required=True)
    a = p.parse_args()
    for name in ('reference_asdf', 'fits', 'failed_log', 'assembly_log', 'native_probe'):
        setattr(a, name, getattr(a, name).resolve(strict=True))
    assert re.fullmatch('[0-9a-f]{40}', a.revision)
    assert a.fits.suffix == '.fits'
    final = a.fits.with_suffix('.asdf')
    assert not final.exists() and not final.is_symlink(), final
    assert not a.receipt.exists(), a.receipt
    stage = Path(str(final) + '.tmp-recovery-' + uuid.uuid4().hex[:8])
    native_log = a.receipt.with_suffix('.native.log')
    assert not native_log.exists(), native_log
    starts = [line[6:] for line in a.failed_log.read_text().splitlines()
              if line.startswith('START ')]
    assert len(starts) == 1
    start = starts[0]
    datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
    created = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    reference_fits = a.reference_asdf.with_suffix('.fits')
    protected = [a.reference_asdf, reference_fits, a.fits, a.failed_log,
                 a.assembly_log, a.native_probe]

    def fingerprint(path):
        st = path.stat()
        return [st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_mode]

    before = {str(path): fingerprint(path) for path in protected}
    receipt = dict(status='started', recovery_tool_revision=a.revision,
                   reference_asdf=str(a.reference_asdf), fits=str(a.fits),
                   staging=str(stage), native_log=str(native_log),
                   source_fingerprints=before, raw_files_accessed=False,
                   prior_owner_verified_legacy_qc_groups=864,
                   prior_owner_verified_identical_detector_payloads=32)
    with a.receipt.open('x') as stream:
        json.dump(receipt, stream, indent=2)

    schema = (ROOT / 'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json').read_bytes()
    schema_id = json.loads(schema)['id']
    with asdf.config_context() as config:
        config.add_resource_mapping({schema_id: schema})
        with asdf.open(a.reference_asdf, custom_schema=schema_id, lazy_load=False,
                       strict_extension_check=True) as af:
            af.validate()
            original = copy.deepcopy(af.tree['qc'])
        assert original['file']['location'] == str(reference_fits)
        q = expected_qc(original, a.fits, created, start, a.failed_log, a.revision)

        # FITS access stays in the established Astropy environment. Headers only.
        reader = r'''
import json, sys
from astropy.io import fits
records = []
with fits.open(sys.argv[1], mode='readonly', memmap=True) as hdus:
 assert len(hdus) == 33
 for index in range(1, len(hdus)):
  h = hdus[index].header
  keys = [c.keyword for c in h.cards if c.keyword.startswith('ESO MPP QC ')]
  assert len(keys) == len(set(keys))
  records.append(dict(detector=h['ESO DET CHIP ID'], hdu=index,
                      header={key:h[key] for key in keys}))
print(json.dumps(records))
'''
        result = subprocess.run([
            '/Users/fselman/anaconda3/envs/wenu-imaging/bin/python', '-B', '-c',
            reader, str(a.fits),
        ], check=True, capture_output=True, text=True)
        if result.stderr:
            print(result.stderr, end='')
        headers = json.loads(result.stdout)

        def fits_check(tree):
            ds = {d['detector_id']: d for d in tree['characterization']['detectors']}
            assert len(ds) == len(headers) == 32
            total = 0
            for row in headers:
                d = ds[row['detector']]
                assert d['output_hdu'] == row['hdu']
                total += verify(row['header'], tree, d)
            assert total == 89445, total
            return total

        fits_check(q)
        print('PASS: reference QC agrees with all 89445 FITS scalar/context cards.', flush=True)
        argv = [str(a.native_probe), 'recover-verified', str(a.reference_asdf),
                str(a.fits), str(stage), str(a.failed_log), str(a.assembly_log),
                created, start, a.revision]
        receipt['native_command'] = argv
        try:
            with native_log.open('x') as stream:
                result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT, timeout=120)
            if result.returncode:
                raise RuntimeError('Native staging failed; inspect ' + str(native_log))
            print('Native staging written; independently verifying complete record...', flush=True)
            with asdf.open(stage, custom_schema=schema_id, lazy_load=False,
                           strict_extension_check=True) as af:
                af.validate()
                exact(q, af.tree['qc'])
                expected_recovery = dict(
                    method='verified_reference_qc_reuse', status='recovered_product_qc',
                    original_recipe_status='incomplete_after_assembly_failure',
                    reference_asdf=str(a.reference_asdf), failed_recipe_log=str(a.failed_log),
                    assembly_recovery_log=str(a.assembly_log), recovered_at=created,
                    recovery_tool_source_revision=a.revision,
                    measurement_policy='reference_values_definitions_arrays_and_inputs_preserved',
                    verification_basis='caller_verified_FITS_scalar_context_and_prior_pixel_comparison',
                    reference_product=original['file'], reference_record=original['record'],
                    reference_provenance=original['provenance'],
                )
                exact(expected_recovery, af.tree['recovery'])
                total = fits_check(af.tree['qc'])
            assert before == {str(path): fingerprint(path) for path in protected}
            # Native emission is verified before exclusive final publication.
            import os
            os.link(stage, final)
            stage.unlink()
            receipt.update(status='recovered_and_verified', final_asdf=str(final),
                           scalar_context_cards=total, all_reference_measurements_preserved=True,
                           reference_arrays_preserved=True, schema_validated=True,
                           original_recipe_status='incomplete_after_assembly_failure')
        except Exception as error:
            receipt.update(status='failed', error=repr(error))
            raise
        finally:
            receipt['protected_files_preserved'] = before == {
                str(path): fingerprint(path) for path in protected
            }
            a.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
            assert receipt['protected_files_preserved']
    print('PASS: native recovered ASDF, complete values/arrays/provenance and FITS agreement.')
    print('ASDF:', final)
    print('Receipt:', a.receipt)
    print('Original ASDF and failed log preserved; this is an explicitly recovered product.')


if __name__ == '__main__':
    main()
