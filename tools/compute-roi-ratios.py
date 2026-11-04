#!/usr/bin/env python3
"""Compute/save same-exposure ROI ratio ASDF from saved diagnostic rows; no plots."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_roi_ratio_qc as ratio


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-index',type=Path,required=True)
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--source-revision',required=True)
    p.add_argument('--numerator-suffix',default='near_readout')
    p.add_argument('--denominator-suffix',default='parallel_far')
    p.add_argument('--reference-min',type=float,default=15000.)
    p.add_argument('--reference-max',type=float,default=35000.)
    a=p.parse_args();work=a.run.resolve(strict=True);index=a.source_index.resolve(strict=True)
    require=ratio.qc.require
    require(not any(work.iterdir()),'Fresh empty ratio run required')
    require(re.fullmatch('[0-9a-f]{40}',a.source_revision),'Exact ratio revision required')
    require(ratio.residual.finite(a.reference_min) and ratio.residual.finite(a.reference_max)
            and a.reference_min<=a.reference_max,'Finite ordered reference limits required')
    frozen={str(index):ratio.pairs.sha(ratio.pairs.small(index))}
    report=dict(status='failed',products=[],source_revision=a.source_revision,source_index=str(index),
        raw_FITS_opened=False,pixels_remeasured=False,line_fits_recomputed=False,plotting_performed=False)
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            raise RuntimeError('Offline ROI ratio computation')
        if event=='open' and args and isinstance(args[0],(str,bytes)) and str(args[0]).lower().endswith('.fits'):
            raise RuntimeError('FITS reads forbidden')
    sys.addaudithook(offline)
    try:
        original=json.loads(ratio.pairs.small(index))
        require(original['status']=='complete' and original['source_preservation'],'Incomplete source diagnostic run')
        seen=set()
        for item in original['products']:
            source=(index.parent/item['path']).resolve(strict=True)
            require(source.is_relative_to(index.parent),'Source diagnostic path escapes run')
            require(ratio.qc.read_record(source).digest==item['digest'],'Source diagnostic record changed')
            detector=item['detector'];require(detector not in seen,'Duplicate source detector');seen.add(detector)
            target=work/detector.replace('ESO_CCD_#','CCD');target.mkdir()
            print('Computing/saving ROI ratio:',detector,flush=True)
            product=ratio.publish(source,target,assessment_id='roi-ratio:'+a.source_revision+':'+detector,
                created_at=datetime.now(timezone.utc).isoformat(),source_revision=a.source_revision,
                minimum=a.reference_min,maximum=a.reference_max,numerator_suffix=a.numerator_suffix,denominator_suffix=a.denominator_suffix)
            require(product['detector']==detector,'Ratio detector differs')
            frozen.update(product.pop('inputs_sha256'));product['path']=str(Path(product['path']).relative_to(work))
            report['products'].append(product)
        require(seen and len(seen)==original['detectors'],'Incomplete ratio detector set')
        ratio.residual.unchanged(frozen)
        report.update(status='complete',source_preservation=True,inputs_sha256=frozen,
            detectors=len(seen),rows=sum(p['rows'] for p in report['products']),
            reference_min=a.reference_min,reference_max=a.reference_max)
    except Exception as error:report['error']=repr(error);raise
    finally:
        try:ratio.residual.unchanged(frozen)
        except Exception as error:report.update(status='failed',preservation_error=repr(error))
        (work/'index.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        print('ROI RATIO COMPUTATION:',report['status'],flush=True)
        print('RETAINED RATIOS:',work,flush=True)
    require(report['status']=='complete','Ratio computation failed; retain evidence')

if __name__=='__main__':main()
