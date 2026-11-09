#!/usr/bin/env python3
"""Inspect completed BPM/linearity products. Never execute native code or read raw FITS."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def equal_payload(left, right, source, target):
    a, b = left.fileinfo(), right.fileinfo()
    assert a['datSpan'] == b['datSpan'], 'Stored image spans differ'
    source.seek(a['datLoc']); target.seek(b['datLoc'])
    remaining = a['datSpan']
    while remaining:
        count = min(remaining, 65536)
        x, y = source.read(count), target.read(count)
        assert len(x) == len(y) == count and x == y, 'Stored pixel/padding bytes differ'
        remaining -= count


def inspect(manifest, source_root):
    sys.path.insert(0, str(source_root/'Pycavi2/pycavi/pycavi'))
    import numpy as np
    from astropy.io import fits
    import pycavi_bpm_linearity_recipe as recipe
    import pycavi_linearity_preparation_qc as previous
    import pycavi_native_product_qc as native_qc
    saved = recipe.read_manifest(manifest)
    report = saved['manifest']
    assert report['final_mef_state'] == 'assembled'
    # Saved ASDF reading has already verified copied graph, joined values and bindings.
    def local(name):
        path = (manifest.parent/Path(name).relative_to(report['product_root'])).resolve(strict=True)
        assert path.is_relative_to(manifest.parent), 'Product escapes manifest root'
        return path
    protected = {}
    for item in report['detectors']:
        protected.update({local(p): sha for p, sha in item['bpm']['sha256'].items()})
        protected[local(item['preparation']['path'])] = item['preparation']['sha256']
    protected.update({local(p): sha for p, sha in report['bpm_product']['sha256'].items()})
    for path, expected in protected.items():
        assert digest(path) == expected, ('Published file changed', path)
    summaries = []
    final = local(report['bpm_product']['fits'])
    with fits.open(final, memmap=True, do_not_scale_image_data=True) as assembled, Path(final).open('rb') as target:
        assert assembled[0].header['NAXIS'] == 0
        assert len(assembled)-1 == assembled[0].header['NEXTEND'] == len(saved['bpm_product']['image_planes'])
        for member, decoded in zip(report['detectors'], saved['detectors']):
            detector = member['detector_id']
            preparation = decoded['preparation']
            prepared_qc = native_qc.read(local(member['preparation']['path']))
            evidence = {e['name']: e['text'] for e in prepared_qc['extensions']['native_evidence']}
            context = json.loads(evidence['preparation-context.json'])
            # Only the embedded frozen archive is required; original image locations are not opened.
            original = local(member['preparation']['path']).parent/'inputs'/context['source_graph']['entry']
            expected = previous.sample.read_product(original)['rows']
            assert preparation['direct_site_replay'] == expected
            rows = preparation['exposure_rows']
            assert len(rows) == len(context['selection']['flat'])*len(next(d['rois'] for d in context['resolved']['detectors'] if d['detector_id'] == detector))
            input_file = local(member['bpm']['fits'])
            planes = [p for p in saved['bpm_product']['image_planes'] if p['detector_id'] == detector]
            metrics = {m['name']: m for m in decoded['bpm']['characterization']['detectors'][0]['measurements']}
            with fits.open(input_file, memmap=True, do_not_scale_image_data=True) as native, Path(input_file).open('rb') as source_stream:
                for plane in planes:
                    left, right = native[plane['source_hdu']], assembled[plane['output_hdu']]
                    assert right.header['DETID'] == detector
                    assert right.header['EXTVER'] == member['configuration_detector']+1
                    assert right.header['EXTNAME'] == (plane['role'] if plane['source_hdu'] else detector)
                    assert right.header['ORIGFILE'] == Path(final).name
                    for key in ('BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2'):
                        assert right.header[key] == left.header[key]
                    equal_payload(left, right, source_stream, target)
                by_role = {p['role']: assembled[p['output_hdu']] for p in planes}
                flags = np.asarray(by_role['BPM'].data)
                coverage = np.asarray(by_role['COVERAGE'].data)
                selection = np.asarray(by_role['SELECTION'].data)
                histogram = np.bincount(flags.ravel(), minlength=256).tolist()
                fits_histogram = np.bincount(coverage.ravel(), minlength=3).tolist()
                assert histogram == metrics['reason_histogram']['value']
                assert fits_histogram == metrics['fit_histogram']['value']
                assert flags.shape == coverage.shape == selection.shape
                assert set(np.unique(selection)) <= {0, 1}
                assert set(np.unique(coverage)) <= {0, 1, 2}
                summary = dict(detector=detector, shape=list(flags.shape), pixels=int(flags.size),
                    exact_payload_planes=len(planes), direct_samples_exact=len(expected), pair_roi_records=len(preparation['rows']),
                    exposure_roi_records=len(rows), trace_frames=len(preparation['scan_traces']),
                    reason_histogram={str(i): int(n) for i, n in enumerate(histogram) if n},
                    fit_states=dict(zip(('unavailable', 'fit', 'legacy_ls_fallback'), fits_histogram)),
                    selected_pixels=int(np.count_nonzero(selection)), output_mode=by_role['BPM'].header['MASKROLE'],
                    roi_summary=[])
                del flags, coverage, selection
                for role in ('BPM', 'COVERAGE', 'SELECTION'):
                    del by_role[role].data
            for roi in dict.fromkeys(row['roi'] for row in rows):
                cohort = [row for row in rows if row['roi'] == roi]
                means = [r['signal_adu'] for r in cohort if r['signal_adu'] is not None]
                variances = [r['spatial_variance_adu2'] for r in cohort if r['spatial_variance_adu2'] is not None]
                summary['roi_summary'].append(dict(roi=roi, measurements=len(cohort),
                    signal_adu_range=[min(means), max(means)] if means else None,
                    spatial_variance_adu2_range=[min(variances), max(variances)] if variances else None))
            assert preparation['fit_state'] == 'not_performed' and preparation['noise_state'] == 'unavailable'
            summaries.append(summary)
    for path, expected in protected.items():
        assert digest(path) == expected, ('Published file changed during inspection', path)
    return dict(status='saved_product_checks_passed', manifest=str(manifest), detectors=summaries,
        raw_images_opened=False, reduction_repeated=False, published_files_unchanged=True,
        scientific_acceptance=False, linearity_correction='not_applied', qc_viewer='pending')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    manifest = args.manifest.resolve(strict=True)
    result = inspect(manifest, args.source_root.resolve(strict=True))
    parent = json.loads(manifest.read_text())
    directory = Path(tempfile.mkdtemp(prefix=manifest.parent.name+'-inspection-', dir=parent['directories']['logs']))
    with (directory/'inspection.json').open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
    for d in result['detectors']:
        print(d['detector'], 'shape', d['shape'], '| exact pixel/padding planes:', d['exact_payload_planes'])
        print('EXACT retained direct samples:', d['direct_samples_exact'])
        print('PAIR/EXPOSURE ROI RECORDS:', d['pair_roi_records'], d['exposure_roi_records'])
        print('REASON CODES:', d['reason_histogram'])
        print('COVERAGE:', d['fit_states'], '| SELECTED:', d['selected_pixels'], '/', d['pixels'])
        print('BPM OUTPUT MODE:', d['output_mode'], '| zero means no detected reasons, not certification')
        for row in d['roi_summary']:
            print('ROI:', row['roi'], '| ADU range:', row['signal_adu_range'], '| spatial variance ADU2 range:', row['spatial_variance_adu2_range'])
    print('PASS: saved schema/QC/bindings, exact retained direct samples and final pixel payloads; published files unchanged')
    print('REPORT:', directory/'inspection.json')
    print('Scientific inspection and QC Viewer acceptance remain pending.')


if __name__ == '__main__':
    main()
