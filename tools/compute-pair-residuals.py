#!/usr/bin/env python3
"""Compute/save immutable ASDF line diagnostics; no plotting, HTML or FITS reads."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_residual_qc as residual
from pycavi_pair_products import batch_products


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    inputs=parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--batch',type=Path)
    inputs.add_argument('--pairs-asdf',type=Path)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--source-revision',required=True)
    parser.add_argument('--fit-signal-min',type=float)
    parser.add_argument('--fit-signal-max',type=float)
    args=parser.parse_args();work=args.run.resolve(strict=True)
    require=residual.qc.require
    require(not any(work.iterdir()),'Fresh empty diagnostic run required')
    require(re.fullmatch('[0-9a-f]{40}',args.source_revision),'Exact computation revision required')
    require(all(v is None or residual.finite(v) for v in (args.fit_signal_min,args.fit_signal_max)), 'Finite fit limits required')
    report=dict(status='failed',products=[],source_revision=args.source_revision,
        raw_FITS_opened=False,pixels_remeasured=False,plotting_performed=False,
        physical_correction_fitted=False)
    frozen={}
    def offline(event,argv):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            raise RuntimeError('Offline diagnostic computation')
        if event=='open' and argv and isinstance(argv[0],(str,bytes)) and str(argv[0]).lower().endswith('.fits'):
            raise RuntimeError('FITS reads forbidden in saved-data computation')
    sys.addaudithook(offline)
    try:
        products,metadata=batch_products(args.batch) if args.batch else ([args.pairs_asdf],{})
        frozen.update(metadata);seen=set()
        for product in products:
            record=residual.qc.read_record(product)
            detector=record.as_dict()['file']['selectors'][0]['detector_id']
            require(detector not in seen,'Duplicate diagnostic detector');seen.add(detector)
            destination=work/detector.replace('ESO_CCD_#','CCD');destination.mkdir()
            print('Computing/saving diagnostic:',detector,flush=True)
            result=residual.publish(product,destination,
                assessment_id='line-residuals:'+args.source_revision+':'+detector,
                created_at=datetime.now(timezone.utc).isoformat(),source_revision=args.source_revision,
                minimum=args.fit_signal_min,maximum=args.fit_signal_max)
            frozen.update(result.pop('inputs_sha256'))
            result['path']=str(Path(result['path']).relative_to(work))
            report['products'].append(result)
        if args.batch:
            require(seen=={f'ESO_CCD_#{n}' for n in range(65,97)},'Incomplete OCAM detector population')
        residual.unchanged(frozen)
        report.update(status='complete',source_preservation=True,inputs_sha256=frozen,
            rows=sum(p['rows'] for p in report['products']),fits=sum(p['fits'] for p in report['products']),
            detectors=len(seen),fit_signal_min=args.fit_signal_min,fit_signal_max=args.fit_signal_max)
    except Exception as error:
        report['error']=repr(error);raise
    finally:
        try:residual.unchanged(frozen)
        except Exception as error:report.update(status='failed',preservation_error=repr(error))
        (work/'index.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        print('DIAGNOSTIC COMPUTATION:',report['status'],flush=True)
        print('RETAINED DIAGNOSTICS:',work,flush=True)
    require(report['status']=='complete','Diagnostic computation failed; retain evidence')

if __name__=='__main__':main()
