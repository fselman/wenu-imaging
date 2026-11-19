#!/usr/bin/env python3
"""Independently reconstruct saved flat products with NumPy and FITS readers."""
import argparse
from contextlib import ExitStack
from hashlib import file_digest
import json
from pathlib import Path
import tomllib

import asdf
from astropy.io import fits
import numpy as np


def read_toml(path):
    return tomllib.loads(path.read_text())


def resolve(directory, name):
    return (directory / name).resolve(strict=True)


def lower_median(values, axis=None):
    count = values.size if axis is None else values.shape[axis]
    assert count > 0, "Empty median population"
    if count == 2:
        return np.add.reduce(values, axis=axis, dtype=np.float32) / np.float32(2)
    index = (count - 1) // 2
    partitioned = np.partition(values, index, axis=axis)
    return partitioned[index] if axis is None else np.take(partitioned, index, axis=axis)


def hdu_map(hdus):
    names = [h.header['EXTNAME'] for h in hdus[1:]]
    assert len(names) == len(set(names)), "Duplicate detector identity"
    return {name: index for index, name in enumerate(names, 1)}


def corrected_plane(hdu, chip, settings, bias):
    raw = np.array(hdu.data, dtype=np.float32, copy=True)
    assert np.isfinite(raw).all(), "Nonfinite raw pixels"
    scans = []
    for kind in ('prescan', 'overscan'):
        if settings[f'use_{kind}']:
            low = chip[f'{kind}_x_min']['value'] - 1
            high = chip[f'{kind}_x_max']['value']
            scans.append(raw[:, low:high])
    ordered = np.sort(np.concatenate(scans, axis=1), axis=1)
    low, high = settings['reject_scan_low'], settings['reject_scan_high']
    retained = ordered[:, low:ordered.shape[1] - high]
    assert retained.shape[1] > 0, "Empty scan population"
    levels = retained.mean(axis=1, dtype=np.float64).astype(np.float32)
    raw -= levels[:, None]
    x0 = chip['trimreg_x_min']['value'] - 1
    x1 = chip['trimreg_x_max']['value']
    y0 = chip['trimreg_y_min']['value'] - 1
    y1 = chip['trimreg_y_max']['value']
    plane = raw[y0:y1, x0:x1].copy()
    assert plane.shape == bias.shape, "Bias geometry differs"
    plane -= bias
    return plane


def compare_pixels(expected, actual):
    assert expected.shape == actual.shape, "Output geometry differs"
    finite = np.isfinite(expected) & np.isfinite(actual)
    changed = int(np.count_nonzero(expected != actual))
    maximum = float(np.max(np.abs(expected[finite].astype(np.float64) - actual[finite]))) if finite.any() else None
    return {'pixels': int(expected.size), 'different': changed,
            'nonfinite': int(np.count_nonzero(~finite)), 'maximum_absolute_difference': maximum}


def verify_component(recipe_path, product_path):
    recipe = read_toml(recipe_path)
    project_path = resolve(recipe_path.parent, recipe['project'])
    roots = read_toml(project_path)['project']['roots']
    cal = resolve(project_path.parent, roots['calibration'])
    profile = read_toml(resolve(recipe_path.parent, recipe['detector_toml']))
    settings = recipe['flat']
    selected = [d for d in profile['detector'] if d['enabled'] and
                settings['detector'] in ('all', d['id'])]
    reference = next(d['id'] for d in selected if settings['detector'] != 'all' or d['native_paf_chip'] == 1)
    selected.sort(key=lambda d: d['id'] != reference)
    bias_path = resolve(cal, recipe['inputs']['master_bias'])
    listing = Path(recipe['inputs']['list']).resolve(strict=True)
    paths = [Path(line.rsplit(None, 1)[0]).resolve(strict=True)
             for line in listing.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
    assert len(paths) == len(set(paths)), 'Duplicate exposure path'
    records = []
    reference_level = None
    with ExitStack() as stack:
        archive = stack.enter_context(asdf.open(product_path.with_suffix('.asdf')))
        qc = archive.tree['qc']
        assert qc['provenance']['configuration']['snapshot'] == recipe_path.read_text()
        evidence = {item['name']: item['text'] for item in qc['extensions']['native_evidence']}
        assert evidence['bias_subtraction'] == 'per_exposure_before_admission_and_normalization'
        (calibration,) = qc['calibrations']
        assert Path(calibration['file']['location']).resolve(strict=True) == bias_path
        with bias_path.open('rb') as stream:
            assert calibration['file']['sha256'] == file_digest(stream, 'sha256').hexdigest()
        bias_hdus = stack.enter_context(fits.open(bias_path, memmap=False))
        outputs = stack.enter_context(fits.open(product_path, memmap=False))
        inputs = [stack.enter_context(fits.open(path, memmap=False)) for path in paths]
        input_maps = [hdu_map(hdus) for hdus in inputs]
        bias_map, output_map = hdu_map(bias_hdus), hdu_map(outputs)
        assert set(output_map) == {d['id'] for d in selected}, 'Output detector set differs'
        saved = qc['embedded_input_records']
        assert [Path(row['file']['location']).resolve(strict=True) for row in saved] == paths
        for path, row in zip(paths, saved, strict=True):
            with path.open('rb') as stream:
                assert row['file']['sha256'] == file_digest(stream, 'sha256').hexdigest()
        for detector in selected:
            name = detector['id']
            print(f'CHECK {recipe_path.name} {name}', flush=True)
            chip = profile['native']['instrument']['detectors'][f"CHIP{detector['native_paf_chip']}"]
            gain = float(np.float32(chip['gain']['value']))
            ron = float(np.float32(chip['ron']['value']))
            bias = np.array(bias_hdus[bias_map[name]].data, dtype=np.float32)
            del bias_hdus[bias_map[name]].data
            planes, medians, decisions, exposure_checks = [], [], [], []
            median_sum = np.float32(0)
            for index, (hdus, mapping) in enumerate(zip(inputs, input_maps, strict=True)):
                plane = corrected_plane(hdus[mapping[name]], chip, settings, bias)
                del hdus[mapping[name]].data
                mean = float(plane.mean(dtype=np.float64))
                accepted = np.float32(settings['frame_mean_low_adu']) < mean < np.float32(settings['frame_mean_high_adu'])
                decision = next(d for d in qc['inputs'][index]['participation_by_detector'] if d['detector_id'] == name)
                decisions.append(bool(accepted) == (decision['status'] == 'used'))
                bound = next(d for d in saved[index]['detectors'] if d['detector_id'] == name)
                assert bound['source_hdu'] == mapping[name]
                measured = bound['measurements'][0]
                check = {'path': str(paths[index]), 'corrected_mean_adu': mean,
                         'accepted': bool(accepted), 'normalization_median_adu': None,
                         'saved_median_adu': measured['value']}
                exposure_checks.append(check)
                if not accepted:
                    medians.append(measured['status'] == 'unavailable')
                    continue
                sigma = np.sqrt((ron / gain) ** 2 + mean / gain)
                low = mean - float(np.float32(settings['clip_low_sigma'])) * sigma
                high = mean + float(np.float32(settings['clip_high_sigma'])) * sigma
                x0, x1, y0, y1 = settings['normalization_region']
                region = plane[y0 - 1:y1, x0 - 1:x1]
                values = region[(region.astype(np.float64) > low) & (region.astype(np.float64) < high)]
                median = float(lower_median(values))
                assert abs(median) >= 1e-4, 'Near-zero median requires explicit inspection'
                check['normalization_median_adu'] = median
                check['normalization_pixel_count'] = int(values.size)
                medians.append(measured['status'] == 'measured' and measured['value'] == median)
                median_sum = np.float32(float(median_sum) + median)
                planes.append((plane.astype(np.float64) / median).astype(np.float32))
            assert len(planes) >= settings['minimum_frames'], 'Insufficient admitted frames'
            level = np.float32(median_sum / np.float32(len(planes)))
            if name == reference:
                reference_level = level
            expected = lower_median(np.stack(planes), axis=0)
            scale = np.float32(level / reference_level)
            expected = (expected.astype(np.float64) * float(scale)).astype(np.float32)
            hdu = outputs[output_map[name]]
            result = compare_pixels(expected, hdu.data)
            result.update(detector=name, exposures=exposure_checks, normalization_medians_match=all(medians),
                          participation_matches=all(decisions), admitted_frames=len(planes),
                          normalization_header_matches=hdu.header['ESO MPP QC FRMEDIAN'] == float(level))
            records.append(result)
            del hdu.data
            del planes, expected
    return records


def box_sum(values, radius):
    # Separable window sums avoid allocating one full image per window position.
    padded = np.pad(values.astype(np.float64), ((radius, radius), (radius, radius)))
    width = 2 * radius + 1
    horizontal = np.pad(np.cumsum(padded, axis=1, dtype=np.float64), ((0, 0), (1, 0)))
    horizontal = horizontal[:, width:] - horizontal[:, :-width]
    vertical = np.pad(np.cumsum(horizontal, axis=0, dtype=np.float64), ((1, 0), (0, 0)))
    return vertical[width:] - vertical[:-width]


def verify_mff(recipe_path, product_path):
    recipe = read_toml(recipe_path)
    project_path = resolve(recipe_path.parent, recipe['project'])
    roots = read_toml(project_path)['project']['roots']
    cal = resolve(project_path.parent, roots['calibration'])
    records = []
    with ExitStack() as stack:
        components = {key: stack.enter_context(fits.open(resolve(cal, recipe['inputs'][key]), memmap=False))
                      for key in ('dome', 'sky', 'bpm')}
        maps = {key: hdu_map(hdus) for key, hdus in components.items()}
        outputs = stack.enter_context(fits.open(product_path, memmap=False))
        for name, index in hdu_map(outputs).items():
            print(f'CHECK MFF {name}', flush=True)
            dome = np.array(components['dome'][maps['dome'][name]].data, dtype=np.float32)
            sky = np.array(components['sky'][maps['sky'][name]].data, dtype=np.float32)
            mask = components['bpm'][maps['bpm'][name]].data
            assert np.isin(mask, (0, 1)).all(), 'Nonbinary BPM'
            good = mask == recipe['inputs']['bpm_good_value']
            assert np.isfinite(dome).all() and np.isfinite(sky).all()
            ratio = np.zeros_like(sky)
            np.divide(sky, dome, out=ratio, where=np.abs(dome.astype(np.float64)) > 1e-30)
            radius = recipe['mff']['radius']
            counts = box_sum(good, radius)
            assert (counts > 0).all(), 'Empty smoothing window'
            smoothed = (box_sum(np.where(good, ratio, 0), radius) / counts).astype(np.float32)
            expected = (smoothed * dome).astype(np.float32)
            result = compare_pixels(expected, outputs[index].data)
            result['detector'] = name
            records.append(result)
            for key, hdus in components.items():
                del hdus[maps[key][name]].data
            del outputs[index].data
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for kind in ('dome', 'sky', 'mff'):
        parser.add_argument(f'--{kind}-recipe', type=Path, required=True)
        parser.add_argument(f'--{kind}-product', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    assert not args.report.exists(), 'Report already exists'
    report = {'dome': verify_component(args.dome_recipe, args.dome_product),
              'sky': verify_component(args.sky_recipe, args.sky_product),
              'mff': verify_mff(args.mff_recipe, args.mff_product)}
    passed = all(row['different'] == 0 and row['nonfinite'] == 0 and
                 row.get('normalization_medians_match', True) and
                 row.get('participation_matches', True) and
                 row.get('normalization_header_matches', True)
                 for rows in report.values() for row in rows)
    report['passed'] = passed
    with args.report.open('x') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print('REPORT', args.report)
    assert passed, 'Numerical differences found; inspect the report before choosing any tolerance'
    print('PASS: independent dome, sky and MFF arithmetic at zero pixel tolerance')


if __name__ == '__main__':
    main()
