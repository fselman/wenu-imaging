#!/usr/bin/env python3
"""Display saved BPM/linearity ASDF with the existing offline QC plots."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Pycavi2/pycavi/pycavi'))
from pycavi_bpm_linearity_display import ManifestReader


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--detectors', type=Path, required=True)
    parser.add_argument('--processing', type=Path, required=True)
    parser.add_argument('--run', type=Path, required=True, help='Fresh empty directory below reduced')
    args = parser.parse_args()
    started = perf_counter()
    def progress(message):
        print(f'[{perf_counter()-started:.3f} s] {message}', flush=True)
    def offline(event, values):
        if event.startswith('socket.') or event in ('subprocess.Popen', 'os.system'):
            raise RuntimeError('Saved QC display cannot use network or subprocesses')
        if event == 'open' and isinstance(values[0], (str, bytes)):
            name = str(values[0]).lower()
            if name.endswith(('.fits', '.fit', '.fts', '.fits.gz', '.fits.fz', '.tsv')):
                raise RuntimeError('Saved QC display cannot open images or native TSV files')
    sys.addaudithook(offline)
    reader = ManifestReader(args.manifest, progress)
    work = args.run.resolve(strict=True)
    reduced = Path(reader.manifest['directories']['reduced']).resolve(strict=True)
    if not work.is_relative_to(reduced) or any(work.iterdir()):
        raise ValueError('Fresh empty derived viewer directory below reduced required')
    detectors, processing = [reader.configuration(p) for p in (args.detectors, args.processing)]
    spec = importlib.util.spec_from_file_location('pair_viewer', ROOT/'tools/view-pair-qc.py')
    viewer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(viewer)
    progress('Projecting saved rows onto the existing plots')
    payload, frozen = viewer.build(detectors, processing, list(reader.records), reader=reader)
    for panel in payload['panels']:
        if panel['status'] == 'available':
            panel['bpm'] = reader.bpm[panel['geometry']['id']]
    payload['recipe'] = dict(name='BPM / linearity', manifest=str(reader.path),
        created_at=reader.manifest['created_at'], scientific_acceptance=False,
        linearity_correction='not_applied')
    payload['validation'] = dict(scope='saved_manifest_and_embedded_evidence',
        FITS_integrity_rechecked=False, raw_images_opened=False, native_commands_started=False)
    progress('Writing offline viewer')
    output = work/'qc-mosaic.html'
    output.write_text(viewer.render(payload))
    (work/'qc-data.json').write_text(json.dumps(payload, allow_nan=False, separators=(',', ':'))+'\n')
    viewer.unchanged(frozen)
    report = dict(status='complete_for_owner_inspection', output=str(output),
        detectors=sum(p['status'] == 'available' for p in payload['panels']),
        signal_rows=sum(len(p['signals']) for p in payload['panels']),
        inputs_sha256=frozen, source_preservation=True, **payload['validation'],
        elapsed_seconds=perf_counter()-started)
    (work/'viewer.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: saved ASDF display; no image reads, native commands or new fits', flush=True)
    print('VIEWER:', output, flush=True)


if __name__ == '__main__':
    main()
