"""Tiny generated FITS only: explicit file binding and detached sample ownership.

Reuse the existing standard-library FITS fixture header writer. No observations,
ASDF publication, uncertainty estimation, installed files or external packages.
"""
import argparse
import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile
from layout_contract import header


def plane(values, width, height, *, primary=True, mask=False, byte=False, extra=(), detector='D', amplifier='OUT1'):
    cards = [('SIMPLE', 'T')] if primary else [('XTENSION', "'IMAGE   '")]
    cards += [('BITPIX', '8' if byte else '-32'), ('NAXIS', '2'), ('NAXIS1', str(width)), ('NAXIS2', str(height))]
    if not primary:
        cards += [('PCOUNT', '0'), ('GCOUNT', '1')]
    cards += [('DETID', repr(detector)), ('AMPID', repr(amplifier)),
              ('BUNIT', "'mask'" if mask else "'ADU'"), ('XBINNING', '1'), ('YBINNING', '1')]
    cards += list(extra)
    data = struct.pack('>' + str(width*height) + ('B' if byte else 'f'), *values)
    return header(cards) + data.ljust(((len(data)+2879)//2880)*2880, b'\0')


def fixture(work, kind, case):
    work.mkdir()
    (work/'bias.fits').write_bytes(plane([3]*8, 4, 2))
    for f, t in enumerate([2, 5, 5, 2]):
        data = []
        for y in range(4):
            data += [10+10*y] + [12+10*y+3+100*t+(y-1)*4+x for x in range(4)] + [14+10*y]
        if f == 1:
            data[6+3] = float('nan')
        if f == 2:
            data[12+2] = 1000  # Exact physical raw saturation boundary.
        seconds = t + (.01 if f == 1 and case in ('pair_time', 'tolerant') else 0)
        extra = [('EXPTIME', str(seconds))]
        if f == 0 and case == 'missing':
            extra = []
        if f == 0 and case == 'duplicate':
            extra += [('EXPTIME', str(seconds))]
        amp = 'OTHER' if f == 0 and case == 'amplifier' else 'OUT1'
        if f % 2:
            primary = header([('SIMPLE', 'T'), ('BITPIX', '8'), ('NAXIS', '0'), ('EXTEND', 'T')] + extra)
            content = primary + plane([9000]*24, 6, 4, primary=False, detector='OTHER') + plane(data, 6, 4, primary=False, amplifier=amp)
        else:
            content = plane(data, 6, 4, extra=extra, amplifier=amp)
        (work/f'flat-{f}.fits').write_bytes(content)
    if kind:
        flags = [1, 0, 0, 0, 0, 0, 128, 0]
        values = flags if kind == 1 else [int(v != 0) if kind == 2 else int(v == 0) for v in flags]
        extra = [('MASKENC', "'REASON8'"), ('MASKREG', "'WENU_BPM_V1'")] if kind == 1 else []
        (work/'bpm.fits').write_bytes(plane(values, 4, 2, byte=True, mask=True, extra=extra))


def legacy_bpm_fixture(work):
    """Exercise the existing BPM adapter after extraction of unchanged helpers."""
    work.mkdir()
    bias = [5+.5*k for k in range(24)]
    (work/'bias.fits').write_bytes(plane(bias, 6, 4))
    for f, t in enumerate([1, 3]):
        data = []
        for y in range(6):
            for x in range(10):
                value = 100+3*f+y
                if 1 <= y <= 4 and 2 <= x <= 7:
                    k=(y-1)*6+x-2
                    response = .25 if k == 0 else 2 if k == 23 else 1
                    value += bias[k]+100*t*response
                data.append(value)
        extra=[('EXPTIME', str(t))]
        if f:
            primary=header([('SIMPLE', 'T'), ('BITPIX', '8'), ('NAXIS', '0'), ('EXTEND', 'T')]+extra)
            content=primary+plane([20000]*60, 10, 6, primary=False, detector='OTHER')+plane(data, 10, 6, primary=False)
        else:
            content=plane(data, 10, 6, extra=extra)
        (work/f'flat-{f}.fits').write_bytes(content)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probe', required=True)
    p.add_argument('--bpm-probe', required=True)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--work-parent', type=Path, required=True)
    a = p.parse_args()
    work = Path(tempfile.mkdtemp(prefix='linearity-files-', dir=a.work_parent))
    print('RETAINED LINEARITY FILE TEST:', work, flush=True)
    cases = [(kind, 'normal') for kind in range(4)] + [(1, case) for case in
             ('missing', 'duplicate', 'amplifier', 'pair_time', 'tolerant', 'hdu', 'readout', 'pair_id', 'registry', 'limit')]
    for kind, case in cases:
        directory=work/f'{kind}-{case}'
        fixture(directory, kind, case)
        before={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.fits')}
        completed=subprocess.run([a.probe, str(a.source_root/'mefpp2/ins/mef/config/wfi.paf'), str(directory), str(kind), case], text=True, capture_output=True)
        if completed.returncode:
            raise RuntimeError(f'{kind}/{case}: {completed.stdout[-3000:]}\n{completed.stderr[-6000:]}')
        assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.fits')}
        (directory/'probe.log').write_text(completed.stdout+completed.stderr)
    directory=work/'legacy-bpm'
    legacy_bpm_fixture(directory)
    before={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.fits')}
    completed=subprocess.run([a.bpm_probe, str(a.source_root/'mefpp2/ins/mef/config/wfi.paf'), str(directory), '2', '0', '1', '0', 'normal'], text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError('Affected BPM control: '+completed.stdout[-2000:]+completed.stderr[-4000:])
    assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.fits')}
    (directory/'probe.log').write_text(completed.stdout+completed.stderr)
    print('PASS: 14 FITS cases, source pixel/header preservation and existing BPM metadata/control')


if __name__ == '__main__':
    main()
