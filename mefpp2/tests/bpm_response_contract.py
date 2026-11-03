"""Synthetic response checks and independent Astropy verification of byte I/O.

Purpose/inputs: generated active planes and all byte values; no observational
data. Actions: invoke the Eclipse probe; verify headers/content via Astropy;
create explicit-HDU and malformed encoding/type/scaling inputs. Pass: exact
0..255 preservation, correct selected extension, all negative cases rejected,
no input changes. This is software validation, not detector characterization.
"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from astropy.io import fits


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--probe', type=Path, required=True)
    p.add_argument('--work-parent', type=Path, required=True)
    a = p.parse_args()
    a.work_parent.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix='bpm-response-', dir=a.work_parent))

    def probe(*parts):
        subprocess.run([str(a.probe), *map(str, parts)], check=True, timeout=30)

    # Independent in-memory arithmetic/reference/coverage/error controls.
    probe()
    # C writes one primary 8-bit HDU; Astropy independently checks every value.
    target = run / 'all-bytes.fits'
    probe('write', target)
    expected = np.arange(256, dtype=np.uint8).reshape(1, 256)
    with fits.open(target) as hdus:
        hdus.verify('exception')
        assert hdus[0].header['BITPIX'] == 8
        assert hdus[0].header['MASKENC'] == 'REASON8'
        assert hdus[0].header['MASKREG'] == 'WENU_BPM_V1'
        np.testing.assert_array_equal(hdus[0].data, expected)
    assert target.stat().st_size % 2880 == 0
    before = hashlib.sha256(target.read_bytes()).hexdigest()
    probe('read', target, 0)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == before
    # Selected extension, not primary BITPIX: extension bytes under 16-bit primary.
    primary = fits.PrimaryHDU(np.zeros((2, 2), dtype=np.int16))
    extension = fits.ImageHDU(expected)
    extension.header['MASKENC'] = 'REASON8'
    extension.header['MASKREG'] = 'WENU_BPM_V1'
    mef = run / 'selected-extension.fits'
    fits.HDUList([primary, extension]).writeto(mef)
    probe('read', mef, 1)
    probe('reject', mef, 0)
    for name, data in [('wrong-type', expected.astype(np.int16)),
                       ('wrong-rank', expected.reshape(1, 1, 256))]:
        bad = fits.PrimaryHDU(data)
        bad.header['MASKENC'] = 'REASON8'
        bad.header['MASKREG'] = 'WENU_BPM_V1'
        path = run / (name + '.fits')
        bad.writeto(path)
        probe('reject', path, 0)
    # Explicit registry/encoding/type/scaling guards; no polarity inference.
    cases = [('MASKREG', 'UNKNOWN'), ('MASKENC', 'BINARY'), ('BSCALE', 2), ('BZERO', 1)]
    for key, value in cases:
        bad = fits.PrimaryHDU(expected)
        bad.header['MASKENC'] = 'REASON8'
        bad.header['MASKREG'] = 'WENU_BPM_V1'
        bad.header[key] = value
        path = run / (key.lower() + '.fits')
        bad.writeto(path)
        probe('reject', path, 0)
    print('PASS: response contract and all 256 byte flags, exact selected-HDU round trips, malformed masks rejected')
    print('Retained:', run)


if __name__ == '__main__':
    main()
