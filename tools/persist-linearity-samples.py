#!/usr/bin/env python3
"""Persist completed singleton samples with the common ASDF writer; no pixels or fit."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_sample_qc as bridge


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',type=Path,required=True);p.add_argument('--run',type=Path,required=True)
    p.add_argument('--source-revision',required=True)
    a=p.parse_args();work=a.run.resolve(strict=True)
    bridge.qc.require(work.is_dir() and not any(work.iterdir()),'Fresh persistence directory required')
    report=dict(status='failed',raw_FITS_opened=False,pixels_remeasured=False,fitted=False)
    (work/'README.md').write_text('Corrected singleton sample ASDF derived from the completed native batch. No FITS opened, images hashed, measurements rerun, noise/fit policy chosen or correction applied. Master QC copies preserve semantic record identities and relative frozen links; original source locations remain provenance. Each product retains exact native text and typed values, missing as None. persistence.json is authoritative for this stage; keep it with ASDF while downstream recipes reference these samples. Failed attempts retain partial evidence and cannot resume/overwrite. No automatic cleanup.\n')
    try:
        target=work/'asdf';target.mkdir()
        report=bridge.publish_batch(a.batch,target,assessment_id='OCAM-corrected-samples:'+work.name,
            created_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),serializer_revision=a.source_revision)
    except Exception as error:
        report.update(status='failed',error=repr(error));raise
    finally:
        (work/'persistence.json').write_text(json.dumps(report,indent=2)+'\n')
        print('CORRECTED SAMPLE ASDF:',report['status'],flush=True)
        print('RETAINED PERSISTENCE:',work,flush=True)
        if report['status']=='complete':print('DETECTORS:',len(report['products']),'ROWS:',report['rows'],'RECORDS:',report['records'],flush=True)


if __name__=='__main__':main()
