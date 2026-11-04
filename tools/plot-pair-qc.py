#!/usr/bin/env python3
"""Plot full-precision saved ASDF pair values only; no FITS/TSV reads or fits (#233)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_pair_qc as bridge
from pycavi_pair_display import exposure_rows


def render(path,directory):
    qc=bridge.qc;path=Path(path).resolve(strict=True);directory=Path(directory).resolve(strict=True)
    qc.require(directory.is_dir() and not any(directory.iterdir()),'Fresh empty plot directory required')
    os.environ['MPLCONFIGDIR']=str(directory/'matplotlib-cache')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter
    before=bridge.small(path)
    record=qc.read_record(path)
    list(qc.traverse_records(path,qc_root=path.parent))
    table=bridge.table_from_record(record)
    qc.require(table['kind']=='pairs','Pair ASDF product required')
    rows=table['rows'];rois=list(dict.fromkeys(r['roi'] for r in rows))
    qc.require(len(rois)<=32,'Too many ROIs for this inspection plot')
    outputs=[]
    for kind,field,label in [('gain','point_gain_e_per_adu','Diagnostic point gain (e⁻/ADU)'),
                             ('variance','single_flat_variance_adu2','Single-flat variance from pair differences (ADU²)'),
                             ('signal_time','signal_adu','Mean bias-subtracted signal (ADU)')]:
        time_plot = kind == 'signal_time'
        plotted = exposure_rows(rows) if time_plot else rows
        xfield = 'exposure_seconds' if time_plot else 'mean_signal_adu'
        fig,ax=plt.subplots(figsize=(10.5,6.6),dpi=160)
        fig.subplots_adjust(left=.13,right=.96,bottom=.18,top=.85)
        data=[]
        for index,roi in enumerate(rois):
            selected=[(i,r) for i,r in enumerate(plotted) if r['roi']==roi and r[xfield] is not None and r[field] is not None]
            selected.sort(key=lambda v:(v[1][xfield],v[1].get('input_index',0)))
            x=[r[xfield] for _,r in selected];y=[r[field] for _,r in selected]
            ax.plot(x,y,marker=['o','s','^','D','v'][index%5],markersize=4.5,linewidth=1.2,label=roi)
            data.append(dict(roi=roi,row_indices=[i for i,_ in selected],signal_adu=x,values=y,
                             excluded_row_indices=[i for i,r in enumerate(plotted) if r['roi']==roi and
                                                   (r[xfield] is None or r[field] is None)]))
            if time_plot:
                data[-1].update(exposure_seconds=x,
                    signal_adu=y, samples=[r for _,r in selected],
                    unavailable_samples=[r for r in plotted if r['roi']==roi and r[field] is None])
        ax.set_xlabel('Exposure time (s)' if time_plot else 'Mean bias-subtracted signal (ADU)');ax.set_ylabel(label)
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax.grid(alpha=.2)
        for spine in ('top','right'):ax.spines[spine].set_visible(False)
        ax.legend(loc='best',fontsize=9)
        if kind=='variance':ax.set_xlim(left=0);ax.set_ylim(bottom=0)
        if time_plot:ax.set_xlim(left=0)
        fig.text(.13,.94,rows[0]['detector']+' — '+('signal versus exposure time' if time_plot else kind+' versus signal'),fontsize=19,weight='bold')
        fig.text(.13,.895,'Output '+rows[0]['amplifier']+' · '+str(len(rois))+' ROIs · full-precision ASDF measurements',fontsize=11,color='#555555')
        note='Each flat exposure shown separately on the pair-common pixel population.' if time_plot else 'Diagnostic arithmetic; no fitted or accepted instrument gain.' if kind=='gain' else 'Variance = ½ Var(F₁ − F₂), including read noise.'
        fig.text(.13,.07,note+' Lines connect measured points; no fit.',fontsize=9,color='#555555')
        fig.text(.13,.035,'Raw pairs without overscan correction; missing values remain unavailable.',fontsize=9,color='#777777')
        output=directory/('signal_vs_exposure_time.png' if time_plot else kind+'_vs_signal.png');fig.savefig(output,facecolor='white');plt.close(fig)
        outputs.append(dict(kind=kind,path=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),series=data))
    qc.require(bridge.small(path)==before,'ASDF source changed during plotting')
    report=dict(status='complete',source=str(path),source_sha256=bridge.sha(before),
                qc_record_digest=record.digest,outputs=outputs,raw_FITS_opened=False,native_TSV_opened=False,
                fitted=False,source_preservation=True)
    (directory/'plots.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pairs-asdf',type=Path,required=True)
    p.add_argument('--output-directory',type=Path,required=True)
    a=p.parse_args()
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            raise RuntimeError('Network disabled while plotting ASDF: '+event)
    sys.addaudithook(offline)
    report=render(a.pairs_asdf,a.output_directory)
    print('ASDF PLOTS:',report['status'])
    for output in report['outputs']:print(output['path'])


if __name__=='__main__':main()
