"""One tiny native recipe failure: explicit zero spread, no final products.

Uses only synthetic FITS. No reference reductions, ASDF decoding or observations.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from astropy.io import fits
from prepare_integrated_campaign_fixture import prepare


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipe', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    work = args.work.absolute()
    work.mkdir(exist_ok=False)
    # Prepare tiny independent files with exactly constant corrected means.
    raw = work / 'raw'
    prepare(raw, root)
    paf = work / 'bias.paf'
    text = (raw / 'mefpp.paf').read_text()
    for key, value in {'MEF.BIAS.FRAMENUM.MIN': 3, 'MEF.BIAS.KAPPA1': 2}.items():
        text, count = re.subn(r'^' + re.escape(key) + r'\s+[^;\n]*;',
                             key + ' ' + str(value) + ';', text, flags=re.M)
        assert count == 1, key
    paf.write_text(text)
    paths = []
    for index in range(3):
        path = raw / f'equal-{index}.fits'
        with fits.open(raw / 'bias0.fits', memmap=False) as original:
            hdus = fits.HDUList([h.copy() for h in original])
            for hdu in hdus[1:]:
                hdu.data[:] = 100
                hdu.data[:, :9] = 102
            hdus.writeto(path)
            hdus.close()
        paths.append(path)
    frozen = {str(p): digest(p) for p in raw.iterdir() if p.is_file()}
    listing = work / 'bias.list'
    listing.write_text('\n'.join(map(str, paths)) + '\n')
    output = work / 'products'
    output.mkdir()
    orchestration = work / 'orchestration'
    orchestration.mkdir()
    # Invoke the actual selected C recipe once; failure is the expected outcome.
    command = [str(args.recipe.absolute()), 'cal', 'bias', '--pafname', str(paf),
               '--bias', str(listing), '--output-dir', str(output),
               '--reference-detector', 'F1_CCD_A', '--mad', 'no',
               '--detector-id', 'F1_CCD_A', '--config-detector', '0',
               '--readout-id', 'synthetic', '--bin-x', '1', '--bin-y', '1',
               '--amplifier-id', 'whole', '--input-bpm', 'omitted', '--hdu', '1']
    completed = subprocess.run(command, cwd=orchestration, capture_output=True,
                               text=True, timeout=60, env=dict(os.environ, OMP_NUM_THREADS='1'))
    (work / 'console.log').write_text(completed.stdout + completed.stderr)
    # Verify terminal/log diagnostics, refusal before publication and raw preservation.
    assert completed.returncode != 0, 'Zero spread unexpectedly succeeded'
    logs = list(output.glob('*.log'))
    assert len(logs) == 1, 'Expected one retained recipe failure log'
    log = logs[0].read_text()
    for stream in (completed.stderr, log):
        assert 'Bias zero-spread failure: detector [F1_CCD_A]' in stream
        assert 'sigma=0 ADU' in stream and 'stopped before stacking' in stream
        for index, path in enumerate(paths, 1):
            assert f'input {index} [{path}]: corrected mean=2 ADU' in stream
    assert 'FAILED;' in log and 'DETECTOR_DONE' not in log
    assert 'MEF_ASSEMBLY_START' not in log and 'NATIVE_ASDF_START' not in log
    assert not list(output.rglob('*.fits')) and not list(output.rglob('*.asdf'))
    assert frozen == {str(p): digest(p) for p in raw.iterdir() if p.is_file()}
    (work / 'results.json').write_text(json.dumps({
        'successful': True, 'expected_recipe_exit': completed.returncode,
        'command': command, 'recipe_sha256': digest(args.recipe),
        'raw_unchanged': True, 'final_products': [], 'native_recipe_invocations': 1,
        'raw_observations_accessed': False}, indent=2) + '\n')
    print('PASS: native zero-spread recipe failure; terminal/log identity and exact means; no FITS/ASDF; raw unchanged')


if __name__ == '__main__':
    main()
