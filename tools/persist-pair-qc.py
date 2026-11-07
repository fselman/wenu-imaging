#!/usr/bin/env python3
"""Persist a completed native raw-pair run through shared ASDF QC (#233)."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_pair_qc as bridge


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--measurement-run',type=Path,required=True)
    p.add_argument('--run',type=Path,required=True,help='Fresh empty persistence attempt directory')
    p.add_argument('--assessment-id',required=True)
    p.add_argument('--created-at',required=True)
    p.add_argument('--source-revision',required=True,help='Exact serializer source, distinct from native revision')
    a=p.parse_args();work=a.run.resolve(strict=True)
    bridge.qc.require(work.is_dir() and not any(work.iterdir()),'Fresh empty persistence directory required')
    report=dict(status='failed',measurement_run=str(a.measurement_run),raw_FITS_opened=False,pixels_remeasured=False)
    (work/'README.md').write_text('''# Raw-pair ASDF persistence

Retains full-precision native pair/bias tables in shared ASDF QC, linked input
binding records, source evidence and a truthful persistence receipt. No pixel
measurement or reassessment occurs. Keep while measurements/plots reference these
records; erase only after superseded and required comparison/provenance is retained.
Failed attempts may retain completed leaves; do not overwrite or silently resume.
''')
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            raise RuntimeError('Network is disabled during QC persistence: '+event)
    sys.addaudithook(offline)
    try:
        records=work/'records';records.mkdir()
        report.update(bridge.publish(a.measurement_run,records,assessment_id=a.assessment_id,
            created_at=a.created_at,serializer_revision=a.source_revision))
    except Exception as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}')
        raise
    finally:
        (work/'persistence.json').write_text(json.dumps(report,indent=2)+'\n')
        print('ASDF PERSISTENCE:',report['status'],flush=True)
        print('RETAINED PERSISTENCE:',work,flush=True)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
