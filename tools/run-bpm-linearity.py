#!/usr/bin/env python3
"""Coordinate serial native detector characterization from one recipe TOML.

Default: admit the complete metadata plan without opening FITS pixels. --execute
retains detector products and a joined manifest, with optional native final MEF publication.
"""
import argparse
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_bpm_linearity_plan as planner
import pycavi_bpm_linearity_recipe as recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--qc', choices=('true', 'false'), help='Override optional QC; science ROI measurements remain enabled')
    args = parser.parse_args()
    plan = planner.admit(args.config)
    if args.qc is not None:
        if plan['native_recipe'] is None:
            parser.error('--qc requires the native shared-cube recipe')
        plan['qc'] = args.qc == 'true'
    if not args.execute:
        print(json.dumps(dict(qc=plan['qc'], status='metadata_admitted', run=plan['run'], raw_FITS_opened=False,
            final_mef_state='planned' if plan['assembly'] and (plan['native_recipe'] is None or
                any(e['dependencies']['selection']['bpm']['encoding']=='omitted' for e in plan['entries'])) else 'not_requested', detectors=[e['detector']['detector_id'] for e in plan['entries']],
            unique_image_files=len(plan['baseline']), bpm=plan['bpm'],
            bpm_loaded_input_pixels=[e['bpm_loaded_pixels'] for e in plan['entries']]), indent=2))
        return
    current = os.getpriority(os.PRIO_PROCESS, 0)
    if current < 10:
        os.nice(10-current)
    if plan['native_recipe'] is not None:
        from pycavi_bpm_linearity_native_recipe import execute
        report = execute(plan)
    else:
        report = recipe.execute(plan)
    print('BPM_LINEARITY:', report['status'], flush=True)
    print('MANIFEST:', Path(plan['run'])/'manifest.json', flush=True)


if __name__ == '__main__':
    main()
