"""Native publication + qualified common-ASDF contract, generated pixels only.

Purpose: validate exact integer HDUs, exclusive publication and native-to-ASDF
mapping. Inputs: existing generated bound-FITS fixtures; no observations.
Actions: C publisher after context/map destruction; independent Astropy checks;
qualified ASDF child for schema/content/frozen references. Pass: exact 8/16-bit
values, no source mutation/overwrite/partial final output, valid sidecars and
negative-case rejection. No install, numerical fit change or Phase3 claim.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from astropy.io import fits

from bpm_files_contract import fixture, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--probe', type=Path, required=True)
    p.add_argument('--asdf-python', type=Path, required=True)
    p.add_argument('--work-parent', type=Path, required=True)
    a = p.parse_args()
    a.work_parent.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix='bpm-publication-', dir=a.work_parent))
    print('RETAINED BPM PUBLICATION:', run, flush=True)
    # Both fit modes; byte priors, unknown binary reasons, exclusions, no prior.
    cases = [(0, 1, 10, 'normal'), (1, 2, 12, 'normal'),
             (0, 3, 10, 'normal'), (1, 0, 10, 'normal'), (0, 1, 10, 'unavailable')]
    for index, (mode, kind, count, case) in enumerate(cases):
        work = run/f'case-{index}'
        fixture(work, count, kind, case)
        originals = {p: digest(p) for p in work.iterdir()}
        argv = [str(a.probe), str(a.source_root/'mefpp2/ins/mef/config/wfi.paf'), str(work),
                str(count), str(kind), '1', str(mode), case]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        (run/f'case-{index}.log').write_text(result.stdout+'\n'+result.stderr)
        assert result.returncode == 0, result.stdout[-3000:]+result.stderr[-7000:]
        assert not list(work.glob('.mefpp-bpm-*'))
        t = json.loads((work/'handoff.json').read_text())
        with fits.open(work/'product.fits') as hdus:
            hdus.verify('exception')
            assert len(hdus) == (6 if kind else 5)
            assert [h.header['BITPIX'] for h in hdus] == [8, 8, 16, 8, 8]+([8] if kind else [])
            assert hdus[0].header['MASKREG'] == 'WENU_BPM_V1'
            assert hdus[0].header['DATE'] == t['created_at'][:-1] and hdus[0].header['TIMESYS'] == 'UTC'
            assert hdus[0].header['BUNIT'] == 'mask' and hdus[0].header['READMODE'] == 'readout:test'
            assert hdus[0].header['XBINNING'] == hdus[0].header['YBINNING'] == 1
            assert hdus[0].header['MASKROLE'] == ('NEW' if kind >= 3 else 'COMBINED')
            assert hdus[0].header['HIERARCH ESO PRO REC1 ID'] == 'wenu.cal.bpm'
            assert hdus[0].header['HIERARCH ESO PRO REC1 RAW1 NAME'] == 'flat-0.fits'
            for raw_index, item in enumerate(t['inputs'], 1):
                assert hdus[0].header[f'HIERARCH ESO PRO REC1 RAW{raw_index} NAME'] == Path(item['file']['path']).name
            assert hdus[0].header['NRAW'] == count
            assert hdus[0].header['NUSED'] == (10 if count == 12 else count)
            assert hdus[0].data[0, 0] == (5 if kind in (1, 2) else 4)
            assert hdus[0].data[-1, -1] == (136 if kind in (1, 2) else 8)
            assert hdus['NSAMPLE'].data[-1, -1] == 6
            assert hdus['NEWFLAGS'].data[0, 0] == 4
            assert hdus['SELECTION'].data[0, 0] == 0
            if kind in (1, 2):
                assert hdus['PRIORFLAGS'].data[-1, -1] == 128
            if kind >= 3:
                assert hdus['PRIORSEL'].data[0, 0] == 0
                assert hdus[0].data[1, 1] == 0 and hdus['PRIORSEL'].data[1, 1] == 0
                assert hdus['SELECTION'].data[1, 1] == 0
            if case == 'unavailable':
                assert hdus[0].data[0, 3] == 0
                assert hdus['COVERAGE'].data[0, 3] == 0
                assert hdus['NSAMPLE'].data[0, 3] == 0
                assert hdus['SELECTION'].data[0, 3] == 0
            np.testing.assert_array_equal(np.bincount(hdus[0].data.ravel(), minlength=256), t['reason_histogram'])
            np.testing.assert_array_equal(np.bincount(hdus['COVERAGE'].data.ravel(), minlength=3), t['fit_histogram'])
        with fits.open(work/'integer-boundaries.fits') as h:
            h.verify('exception')
            np.testing.assert_array_equal(h[0].data, [[-32768, -1, 0, 32767]])
        with fits.open(work/'integer-bytes.fits') as h:
            h.verify('exception')
            np.testing.assert_array_equal(h[0].data, np.arange(256).reshape(1, 256))
        for path in work.glob('*.fits'):
            if path.is_file() and not path.is_symlink():
                assert path.stat().st_size % 2880 == 0
        # The retained qualified Python handles only QC mapping/schema/I/O.
        argv = [str(a.asdf_python), '-B', str(a.source_root/'mefpp2/tests/bpm_asdf_contract.py'),
                '--module-root', str(a.source_root/'Pycavi2/pycavi/pycavi'), '--work', str(work)]
        completed = subprocess.run(argv, capture_output=True, text=True, timeout=120)
        (run/f'asdf-{index}.log').write_text(completed.stdout+'\n'+completed.stderr)
        assert completed.returncode == 0, completed.stdout[-3000:]+completed.stderr[-7000:]
        assert all(digest(p) == h for p, h in originals.items())
    print('PASS: five native FITS/ASDF publication cases, byte/int16 boundaries, protected outputs and frozen provenance')


if __name__ == '__main__':
    main()
