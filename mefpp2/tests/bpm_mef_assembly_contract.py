"""Tiny independent FITS byte/layout checks of the native BPM assembler."""
import argparse
import hashlib
from pathlib import Path
import os
import subprocess
import tempfile
from mef_assembly_contract import card, header, hdus


def fixture(path, detector, prior):
    names = ['BPM', 'COVERAGE', 'NSAMPLE', 'NEWFLAGS', 'SELECTION', prior]
    data = bytearray()
    for i, name in enumerate(names):
        cards = [card('SIMPLE', 'T')] if i == 0 else [card('XTENSION', "'IMAGE'")]
        cards += [card('BITPIX', 16 if i == 2 else 8), card('NAXIS', 2), card('NAXIS1', 3), card('NAXIS2', 2)]
        cards += [card('EXTEND', 'T')] if i == 0 else [card('PCOUNT', 0), card('GCOUNT', 1)]
        cards += [card('EXTNAME', repr(name)), card('ORIGFILE', "'source.fits'"), card('DATASUM', "'0'")]
        if i == 0:
            cards += [card('DETID', repr(detector)), card('MASKENC', "'REASON8'"), card('MASKREG', "'WENU_BPM_V1'")]
        payload = bytes(range(i+1, i+1+(12 if i == 2 else 6)))
        data += header(cards)+payload+b'\0'*(-len(payload)%2880)
    path.write_bytes(data)
    path.chmod(0o444)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    work = Path(tempfile.mkdtemp(prefix='bpm-assembly-', dir=args.work_parent)).resolve()
    controls, reduced = work/'orchestration', work/'reduced'
    for path in (work/'raw', controls, reduced/'cal'):
        path.mkdir(parents=True)
    os.chdir(controls)
    sources = [reduced/'cal'/f'detector-{i}.fits' for i in range(2)]
    for i, path in enumerate(sources):
        fixture(path, f'CCD-{i}', 'PRIORSEL' if i == 0 else 'PRIORFLAGS')
    frozen = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    out = reduced/'CMDP.2026-11-09T20:00:00.000Z.001.fits'
    rows = [str(p) for pair in zip(sources, ['CCD-0', 'CCD-1'], [2, 7]) for p in pair]
    argv = [str(args.probe.resolve()), str(out), 'CCD-1', *rows]
    result = subprocess.run(argv, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    saved = hdus(out)
    assert len(saved) == 13 and int(saved[0][1]['NAXIS']) == 0 and int(saved[0][1]['NEXTEND']) == 12
    assert saved[0][1]['DETID'] == "CCD-1"
    mapping = [(d, 0) for d in range(2)]+[(d, hdu) for d in range(2) for hdu in range(1, 6)]
    for hdu, (d, source_hdu) in enumerate(mapping, 1):
        original = hdus(sources[d])[source_hdu]
        assert saved[hdu][2] == original[2], (hdu, 'padded payload changed')
        values = saved[hdu][1]
        assert values['EXTNAME'].strip(" '") == (f'CCD-{d}' if source_hdu == 0 else original[1]['EXTNAME'].strip(" '"))
        assert int(values['EXTVER']) == [3, 8][d] and values['DETID'].strip(" '") == f'CCD-{d}'
        assert values['ORIGFILE'].strip(" '") == out.name and 'CHECKSUM' not in values
    before = out.read_bytes()
    assert subprocess.run(argv, capture_output=True).returncode != 0 and out.read_bytes() == before
    wrong = argv.copy();wrong[1] = str(reduced/'wrong.fits');wrong[4] = 'wrong-id'
    assert subprocess.run(wrong, capture_output=True).returncode != 0 and not Path(wrong[1]).exists()
    assert frozen == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    print('PASS: two detectors, all padded payload bytes, mask/diagnostic HDUs, reference identity and exclusive publication')
    # Keep each image tiny while crossing the ordinary qfits 128-HDU limit.
    mosaic_sources = []
    detector_ids = [f'CCD-{slot:02d}' for slot in range(32)]
    for slot, detector in enumerate(detector_ids):
        source = reduced/'cal'/f'mosaic-{slot:02d}.fits'
        fixture(source, detector, 'PRIORSEL')
        mosaic_sources.extend((str(source), detector, str(slot)))
    mosaic = reduced/'CMDP.2026-11-09T20:00:00.000Z.002.fits'
    result = subprocess.run([str(args.probe.resolve()), str(mosaic), detector_ids[0],
                             *mosaic_sources], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    expected = [(detector, 0, 'BPM') for detector in detector_ids]
    expected.extend((detector, hdu, role) for detector in detector_ids
                    for hdu, role in enumerate(
                        ('COVERAGE', 'NSAMPLE', 'NEWFLAGS', 'SELECTION', 'PRIORSEL'), 1))
    assert len(hdus(mosaic)) == len(expected) + 1 == 193
    assert result.stdout.splitlines() == [
        f'{detector}\t{source}\t{target}\t{role}'
        for target, (detector, source, role) in enumerate(expected, 1)
    ]
    print('PASS: 32-detector mosaic, 193 HDUs and exact final plane map')
    print('RETAINED BPM ASSEMBLY:', work)


if __name__ == '__main__':
    main()
