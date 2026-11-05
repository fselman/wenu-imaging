#!/usr/bin/env python3
"""Prepare one detector's modelling archive from explicit preserved dependencies.

Default is metadata admission only. --execute invokes the native preparation
recipe and common ASDF publisher in a fresh retained directory.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_linearity_config as config
import pycavi_linearity_recipe as recipe


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--detector-toml',type=Path,required=True)
    p.add_argument('--processing-toml',type=Path,required=True)
    p.add_argument('--source-samples',type=Path,required=True)
    p.add_argument('--handoff',type=Path,required=True)
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--source-revision',required=True)
    p.add_argument('--native',type=Path)
    p.add_argument('--execute',action='store_true')
    a=p.parse_args();work=a.run.resolve(strict=True)
    recipe.require(work.is_dir() and not any(work.iterdir()),'Fresh empty retained directory required')
    resolved=config.resolve_files(a.detector_toml,a.processing_toml)
    dependencies=recipe.preparation_dependencies(a.source_samples,a.handoff,resolved)
    if not a.execute:
        report=dict(status='metadata_admitted',raw_FITS_opened=False,measurements_run=False,
                    source_revision=a.source_revision,resolved=resolved,dependencies=dependencies)
        (work/'plan.json').write_text(json.dumps(report,indent=2)+'\n')
        print('LINEARITY PLAN: metadata_admitted',dependencies['selection']['detector'],flush=True)
        return
    recipe.require(a.native is not None,'Explicit qualified native executable required')
    report=recipe.prepare_detector(dependencies,a.native,work,resolved=resolved,
        source_revision=a.source_revision,assessment_id='linearity:'+work.name,
        created_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
    print('LINEARITY PREPARATION:',report['status'],flush=True)
    print('PRODUCT:',report['product']['path'],flush=True)


if __name__=='__main__':main()
