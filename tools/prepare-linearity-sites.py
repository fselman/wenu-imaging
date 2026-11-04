#!/usr/bin/env python3
"""Validate owner-approved singleton coordinates and prepare native ROI transports.

Metadata only. Original ROI names are retained, but each transport is a selected
physical pixel. This does not modify the maintained full-ROI processing profile.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

FOOTPRINT = runpy.run_path(str(Path(__file__).with_name('detector-footprint.py')))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(sites, detectors, processing):
    s = json.loads(sites.read_text())
    require(s['proposal_schema_version'] == 1 and s['status'] == 'owner_approved_engineering_sampling',
            'Require explicitly approved sampling')
    require(s['source_profiles'] == {'config/detectors/omegacam-1x1.toml': sha(detectors),
                                    'config/processing/omegacam-characterization.toml': sha(processing)},
            'Approved profile hashes differ')
    geometry, policy, trims = FOOTPRINT['load'](detectors, processing)
    require(s['source_paf_sha256'] == policy['source_paf_sha256'], 'PAF lineage differs')
    require(s['frames_per_site'] == 20 and s['common_shutter_parameters'] == 1
            and s['covariance_model'] == s['fit_interval'] == 'not_selected', 'Unreviewed science choice')
    population = s['sites']; require(len(population) == 160, 'Require 160 approved sites')
    maps = {d['id']: d for d in geometry['detector']}
    rois = {r['id']: r for r in policy['roi']}
    require(len(maps) == 32 and len(rois) == 160, 'Require original all32 five-ROI geometry')
    seen = set(); grouped = {d: [] for d in maps}
    for site in population:
        d = maps[site['detector']]; r = rois[site['source_roi']]
        require(site['amplifier'] == d['amplifier'] == r['amplifier']
                and r['detector'] == d['id']
                and site['configuration_detector'] == d['native_paf_chip']-1, 'Independent identity/slot mismatch')
        require(all(type(v) is int for v in site['active_pixel']+site['raw_pixel']), 'Integer pixel required')
        x = (r['xmin']+r['xmax']+(d['readout_sign'][0] < 0))//2
        y = (r['ymin']+r['ymax']+(d['readout_sign'][1] < 0))//2
        crop = trims[d['id']]['retained']
        require(site['active_pixel'] == [x, y] and site['raw_pixel'] == [x+crop[0]-1, y+crop[2]-1],
                'Approved centre/readout reflection/raw crop mismatch')
        key = (d['id'], x, y)
        require(key not in seen, 'Duplicate site'); seen.add(key)
        grouped[d['id']].append(site)
    require(all(len(v) == 5 and len({s['source_roi'] for s in v}) == 5 for v in grouped.values()),
            'Require five distinct ROIs per detector')
    require(s['max_observations_before_admission'] == 3200
            and s['joint_parameters_if_all_sites_admitted'] == 225, 'Budget metadata differs')
    return s, grouped


def prepare(sites, detectors, processing, work):
    require(work.is_dir() and not any(work.iterdir()), 'Fresh empty output required')
    inputs = {str(p.resolve()): sha(p) for p in (sites, detectors, processing, Path(__file__),
                                               Path(__file__).with_name('detector-footprint.py'))}
    s, grouped = validate(sites, detectors, processing)
    manifest = dict(status='prepared_not_executed', pixels_read=False, noise_state='unavailable',
                    fit_interval=None, inputs_sha256=inputs, sampling=s, detectors=[])
    for detector, population in grouped.items():
        name = 'CCD'+detector.split('#')[1]+'.toml'
        text = 'roi_schema_version = 1\n'
        for site in population:
            x, y = site['active_pixel']
            r = dict(id=site['source_roi'], detector=detector, amplifier=site['amplifier'],
                     xmin=x, xmax=x, ymin=y, ymax=y)
            text += '\n[[roi]]\n'+''.join(k+' = '+json.dumps(v)+'\n' for k, v in r.items())
        target = work/name; target.write_text(text)
        manifest['detectors'].append(dict(detector=detector, singleton_rois=name, sha256=sha(target),
                                          max_sites=5, max_observations=100))
    require(inputs == {path: sha(path) for path in inputs}, 'Metadata changed during preparation')
    (work/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (work/'README.md').write_text('Owner-approved 160-site engineering sampling. Metadata only, no FITS opened. Each TOML contains five single-pixel regions with original source ROI names; full-ROI processing profiles remain unchanged. Retain manifest hashes with any future extracted samples. No noise model, fit interval, fitted coefficients or accepted whole-detector calibration. Do not replace unavailable sites. Retain while referenced; erase only after provenance is retained.\n')
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('sites', 'detectors', 'processing', 'run'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    m = prepare(a.sites, a.detectors, a.processing, a.run)
    print('STATUS:', m['status'], '| detectors:', len(m['detectors']), '| sites: 160 | FITS opened: false')


if __name__ == '__main__':
    main()
