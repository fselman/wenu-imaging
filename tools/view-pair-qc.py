#!/usr/bin/env python3
"""Generate offline geometry-driven QC HTML from validated ASDF, never raw images (#235)."""
import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_pair_qc as bridge
from pycavi_pair_display import exposure_rows
from pycavi_pair_products import batch_products
import pycavi_residual_qc as residual_qc
import pycavi_roi_ratio_qc as ratio_qc
spec=importlib.util.spec_from_file_location('footprints',ROOT/'tools/detector-footprint.py')
footprint=importlib.util.module_from_spec(spec);spec.loader.exec_module(footprint)
require=bridge.qc.require


def freeze(paths):
    return {str(Path(p).resolve(strict=True)):bridge.sha(bridge.small(Path(p))) for p in paths}


def unchanged(frozen):
    require(freeze(frozen)==frozen,'QC viewer input changed during generation')


def build(detectors,processing,products,diagnostics=None,ratios=None):
    """Products are explicit pairs.asdf paths; omitted detectors remain visibly missing."""
    geometry,policy,trims=footprint.load(detectors,processing)
    before=freeze([detectors,processing,Path(__file__),Path(__file__).with_name('pair-qc-viewer.html'),Path(__file__).with_name('qc-plot-inspection.js'),ROOT/'config/plotting/signal-axis-v1.json'])
    by_id={d['id']:d for d in geometry['detector']};data={}
    for product in products:
        product=Path(product).resolve(strict=True)
        # Shared QC input trees stay local to the product; freeze only ASDF files.
        before.update(freeze(product.parent.glob('*.asdf')))
        values={};origins={}
        for kind,path in (('pairs',product),('bias-ron',product.with_name('bias-ron.asdf'))):
            record=bridge.qc.read_record(path)
            list(bridge.qc.traverse_records(path,qc_root=path.parent))
            table=bridge.table_from_record(record)
            require(table['kind']==kind,'Wrong QC table product')
            values[kind]=table['rows']
            origins[kind]=dict(path=str(path),sha256=before[str(path)],record_digest=record.digest)
            if kind=='pairs':provenance=record.as_dict()['extensions']['raw_pair_provenance']
        identity=values['pairs'][0]['detector']
        require(identity in by_id and identity not in data,'Unknown/duplicate QC detector')
        detector=by_id[identity];crop=trims[identity]['retained']
        rois=[r for r in policy['roi'] if r['detector']==identity]
        by_roi={r['id']:r for r in rois}
        for kind,rows in values.items():
            require({r['roi'] for r in rows}==set(by_roi),'Saved ROI set differs from maintained processing profile')
            for row in rows:
                require(row['detector']==identity and row['amplifier']==detector['amplifier'] and
                        row['configuration_detector']==detector['native_paf_chip']-1,'Saved detector/output/slot differs from geometry')
                r=by_roi[row['roi']]
                active=[row['active_'+k] for k in ('xmin','xmax','ymin','ymax')]
                require(active==[r[k] for k in ('xmin','xmax','ymin','ymax')],'Saved ROI coordinates differ from profile')
                require([row['raw_'+k] for k in ('xmin','xmax','ymin','ymax')]==
                        [active[0]+crop[0]-1,active[1]+crop[0]-1,active[2]+crop[2]-1,active[3]+crop[2]-1],
                        'Saved raw/retained coordinate relation differs')
        data[identity]=dict(status='available',pairs=values['pairs'],signals=exposure_rows(values['pairs']),bias=values['bias-ron'],sources=origins,
            provenance=provenance,rois=rois,footprint_svg=footprint.svg(detector,trims[identity],rois))
    panels=[dict(geometry=d,**data.get(d['id'],dict(status='missing',pairs=[],signals=[],bias=[],rois=[])))
            for d in geometry['detector']]
    payload=dict(schema_version=1,instrument=geometry['instrument'],panels=panels,
        columns=max(d['mosaic_column'] for d in geometry['detector']),
        rows=max(d['mosaic_row'] for d in geometry['detector']),
        geometry_sources={str(p):before[str(Path(p).resolve())] for p in (detectors,processing)},
        authority='Derived inspection only; authoritative measurements remain in ASDF; no physical correction or accepted gain.')
    if diagnostics is not None:
        diagnostic_index=Path(diagnostics).resolve(strict=True)
        before.update(freeze([diagnostic_index]))
        saved=json.loads(bridge.small(diagnostic_index))
        require(saved['status']=='complete' and saved['source_preservation'], 'Incomplete diagnostic computation')
        supplied=set()
        for item in saved['products']:
            identity=item['detector']
            require(identity in data and identity not in supplied,'Unknown/duplicate diagnostic detector')
            supplied.add(identity)
            path=(diagnostic_index.parent/item['path']).resolve(strict=True)
            require(path.is_relative_to(diagnostic_index.parent),'Diagnostic path escapes run')
            before.update(residual_qc.source_graph(path))
            value=residual_qc.read_product(path,
                expected_source_digest=data[identity]['sources']['pairs']['record_digest'],
                expected_digest=item['digest'])
            data[identity]['diagnostics']=value
            data[identity]['sources']['diagnostics']=dict(path=str(path),record_digest=item['digest'])
        require(supplied==set(data),'Diagnostic detector coverage differs from displayed measurements')
        for panel in panels:
            if panel['status']=='available':
                panel['diagnostics']=data[panel['geometry']['id']]['diagnostics']
    if ratios is not None:
        ratio_index=Path(ratios).resolve(strict=True);before.update(freeze([ratio_index]))
        saved=json.loads(bridge.small(ratio_index))
        require(saved['status']=='complete' and saved['source_preservation'],'Incomplete ratio run')
        seen=set()
        for item in saved['products']:
            identity=item['detector'];require(identity in data and identity not in seen,'Unknown/duplicate ratio detector');seen.add(identity)
            path=(ratio_index.parent/item['path']).resolve(strict=True)
            require(path.is_relative_to(ratio_index.parent),'Ratio path escapes run')
            before.update(residual_qc.source_graph(path))
            value=ratio_qc.read_product(path,expected_digest=item['digest'],
                expected_residual_digest=data[identity].get('sources',{}).get('diagnostics',{}).get('record_digest'))
            require(value['source_pair_digest']==data[identity]['sources']['pairs']['record_digest'],'Ratio/measurement source differs')
            data[identity]['ratio']=value
            data[identity]['sources']['ratio']=dict(path=str(path),record_digest=item['digest'])
        require(seen==set(data),'Ratio detector coverage differs')
        for panel in panels:
            if panel['status']=='available':panel['ratio']=data[panel['geometry']['id']]['ratio']
    unchanged(before)
    return payload,before


def render(payload):
    # Escaping '<' prevents script termination by any untrusted asset/ROI/provenance text.
    payload=deepcopy(payload)
    payload['plot_axis_spec']=json.loads((ROOT/'config/plotting/signal-axis-v1.json').read_text())
    encoded=json.dumps(payload,ensure_ascii=True,allow_nan=False).replace('<','\\u003c')
    template=Path(__file__).with_name('pair-qc-viewer.html').read_text()
    require(template.count('__QC_PAYLOAD__')==1,'Invalid QC template')
    require(template.count('__QC_PLOT_INSPECTION__')==1,'Invalid plot module placeholder')
    module=Path(__file__).with_name('qc-plot-inspection.js').read_text()
    require('</script' not in module.lower(),'Unsafe plot inspection module')
    return template.replace('__QC_PAYLOAD__',encoded).replace('__QC_PLOT_INSPECTION__',module)




def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',type=Path,required=True)
    p.add_argument('--ratios',type=Path,help='Completed compute-roi-ratios index.json')
    p.add_argument('--diagnostics',type=Path,help='Completed compute-pair-residuals index.json')
    p.add_argument('--run',type=Path,required=True,help='Fresh empty derived viewer directory')
    a=p.parse_args();work=a.run.resolve(strict=True)
    require(not any(work.iterdir()),'Fresh empty viewer directory required')
    report=dict(status='failed',raw_FITS_opened=False,native_TSV_opened=False,fitted=False,diagnostic_line_fit_available=bool(a.diagnostics),physical_correction_fitted=False)
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            raise RuntimeError('Offline viewer generation')
    sys.addaudithook(offline)
    try:
        products,frozen=batch_products(a.batch)
        payload,inputs=build(ROOT/'config/detectors/omegacam-1x1.toml',ROOT/'config/processing/omegacam-characterization.toml',products,diagnostics=a.diagnostics,ratios=a.ratios)
        frozen.update(inputs)
        require(len(payload['panels'])==32 and all(d['status']=='available' for d in payload['panels']),
                'Completed OCAM batch requires all32 detectors')
        output=work/'qc-mosaic.html';output.write_text(render(payload))
        data_path=work/'qc-data.json';data_path.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
        unchanged(frozen)
        report.update(status='complete_for_owner_inspection',detectors=32,
            signal_time_rows=sum(len(d['signals']) for d in payload['panels']),
            ratio_rows=sum(len(d.get('ratio',{}).get('rows',[])) for d in payload['panels']),
            data_output=dict(path=str(data_path),sha256=bridge.sha(data_path.read_bytes())),
            pair_rows=sum(len(d['pairs']) for d in payload['panels']),bias_rows=sum(len(d['bias']) for d in payload['panels']),
            inputs_sha256=frozen,output=dict(path=str(output),sha256=bridge.sha(output.read_bytes())),source_preservation=True)
    except Exception as error:
        report['error']=repr(error);raise
    finally:
        (work/'viewer.json').write_text(json.dumps(report,indent=2)+'\n')
        (work/'README.md').write_text('Derived offline ASDF QC mosaic. Measurements remain authoritative in their retained ASDF records. No raw images or native TSV files are opened. Keep while needed for inspection; regenerate from retained inputs after changes. No automatic cleanup. viewer.json records status and fingerprints.\n')
        print('VIEWER STATUS:',report['status'],flush=True)
        print('RETAINED VIEWER:',work,flush=True)
    print(json.dumps({k:report[k] for k in ('detectors','pair_rows','signal_time_rows','bias_rows','output','data_output')},indent=2))


if __name__=='__main__':main()
