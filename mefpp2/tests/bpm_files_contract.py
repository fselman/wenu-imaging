"""Generated FITS only: bound acquisition and saturation/coverage controls.

Purpose: validate the native file adapter before publication. Actions: Astropy
creates tiny primary/MEF flats, selected active bias and explicit priors; C uses
M4 binding/loading and the typed BPM service. Pass: known response/flags, exact
original-index exclusions, paired/time/span rejection and unchanged inputs.
Neither observations nor installed production files are used.
"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from astropy.io import fits


def identity(h, mask=False):
    h['DETID'] = 'D'
    h['BUNIT'] = 'mask' if mask else 'ADU'
    h['XBINNING'] = h['YBINNING'] = 1


def fixture(path, count, kind, case='normal'):
    path.mkdir()
    bias = (5 + .5*np.arange(24)).reshape(4, 6).astype(np.float32)
    h = fits.PrimaryHDU(bias)
    identity(h.header)
    h.writeto(path/'bias.fits')
    times = [3, 1, 5, 2, 4, 20]
    for i in range(count):
        t = [1, 3][i] if count == 2 else times[i//2]
        signal = 100*t
        if case == 'partial_levels':
            if i < 4:
                signal = 100
            elif i == 10:
                signal = 300
        if case == 'partial_span':
            if i < 10:
                signal = 100+10*(i//2)
            elif i == 10:
                signal = 300
        if case == 'narrow':
            signal *= .1
        if case == 'same_signal':
            signal = 100
        if case == 'lamp' and i == 1:
            signal *= 1.2
        data = np.repeat((100+3*i+np.arange(6))[:, None], 10, axis=1).astype(np.float32)
        response = np.ones((4, 6), dtype=np.float32)
        response[0, 0] = .25
        response[-1, -1] = 2
        data[1:5, 2:8] += bias+signal*response
        if i % 2:
            primary = fits.PrimaryHDU()
            other = fits.ImageHDU(np.full((6, 10), 20000, dtype=np.float32))
            other.header['DETID'] = 'OTHER'
            selected = fits.ImageHDU(data)
            identity(selected.header)
            hdus = fits.HDUList([primary, other, selected])
        else:
            primary = fits.PrimaryHDU(data)
            identity(primary.header)
            hdus = fits.HDUList([primary])
        primary.header['EXPTIME'] = t + (.1 if case == 'pair_time' and i == 1 else 0)
        if case == 'missing_time' and i == 0:
            del primary.header['EXPTIME']
        if case == 'duplicate_time' and i == 0:
            primary.header.append(('EXPTIME', t))
        hdus.writeto(path/f'flat-{i}.fits')
    if kind:
        active = kind in (1, 3)
        data = np.zeros((4, 6) if active else (6, 10), dtype=np.uint8)
        view = data if active else data[1:5, 2:8]
        if kind <= 2:
            view[0, 0], view[-1, -1] = 1, 128
        elif kind == 3:
            view[0, 0] = view[-1, -1] = 1  # Explicit 0=good.
        else:
            view[:] = 1  # Explicit 1=good; scan pixels deliberately zero.
            view[0, 0] = view[-1, -1] = 0
        h = fits.PrimaryHDU(data)
        identity(h.header, mask=True)
        if kind <= 2:
            h.header['MASKENC'] = 'REASON8'
            h.header['MASKREG'] = 'WRONG' if case == 'registry' else 'WENU_BPM_V1'
        h.writeto(path/'prior.fits')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--probe', type=Path, required=True)
    p.add_argument('--work-parent', type=Path, required=True)
    a = p.parse_args()
    a.work_parent.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix='bpm-files-', dir=a.work_parent))
    print('RETAINED BPM FILE INPUT:', run, flush=True)
    configurations = a.source_root.resolve()/'mefpp2/ins/mef/config'

    def check(instrument, mode, kind, count=10, case='normal', expected=True):
        work = run/f'{instrument}-{mode}-{kind}-{count}-{case}'
        fixture(work, count, kind, case)
        before = {p.name: digest(p) for p in work.iterdir()}
        paf = configurations/(instrument+'.paf')
        config_before = digest(paf)
        argv = [str(a.probe.resolve()), str(paf), str(work), str(count), str(kind),
                str(int(expected)), str(mode), case]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=40)
        (run/(work.name+'.log')).write_text(result.stdout+'\n'+result.stderr)
        assert result.returncode == 0, result.stdout[-4000:]+result.stderr[-6000:]
        assert before == {p.name: digest(p) for p in work.iterdir()}
        assert config_before == digest(paf)

    # Both instrument snapshots/modes, each primary/MEF input mixed in one call.
    for instrument in ('wfi', 'omegacam'):
        for mode in (0, 1):
            check(instrument, mode, 1)
    # Polarity/coordinate paths, explicit all-saturated frame exclusion, minimum.
    for kind in (0, 2, 3, 4):
        check('wfi', 0, kind)
    check('wfi', 0, 1, 12)
    check('wfi', 0, 1, 2)
    # Metadata/pair preflight failures and signal-dependent admission failures.
    for case in ('missing_time', 'duplicate_time', 'pair_time', 'pair_ids', 'registry',
                 'readout', 'narrow', 'lamp', 'same_signal'):
        check('wfi', 0, 1, case=case, expected=False)
    check('wfi', 0, 1, 8, expected=False)
    check('wfi', 0, 1, 12, case='partial_levels', expected=False)
    check('wfi', 0, 1, 12, case='partial_span', expected=False)
    print('PASS: 22 bound-FITS acquisition/coverage/encoding/ownership cases; all inputs preserved')


if __name__ == '__main__':
    main()
