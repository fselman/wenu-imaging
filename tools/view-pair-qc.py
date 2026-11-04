#!/usr/bin/env python3
"""Generate offline geometry-driven QC HTML from validated ASDF, never raw images (#235)."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_pair_qc as bridge
from pycavi_pair_display import exposure_rows
spec=importlib.util.spec_from_file_location('footprints',ROOT/'tools/detector-footprint.py')
footprint=importlib.util.module_from_spec(spec);spec.loader.exec_module(footprint)
require=bridge.qc.require


def freeze(paths):
    return {str(Path(p).resolve(strict=True)):bridge.sha(bridge.small(Path(p))) for p in paths}


def unchanged(frozen):
    require(freeze(frozen)==frozen,'QC viewer input changed during generation')


def build(detectors,processing,products):
    """Products are explicit pairs.asdf paths; omitted detectors remain visibly missing."""
    geometry,policy,trims=footprint.load(detectors,processing)
    before=freeze([detectors,processing,Path(__file__),Path(__file__).with_name('pair-qc-viewer.html'),Path(__file__).with_name('pair-qc-residuals.js')])
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
        authority='Derived inspection only; authoritative measurements remain in ASDF; no fit or accepted gain.')
    unchanged(before)
    return payload,before


def render(payload):
    # Escaping '<' prevents script termination by any untrusted asset/ROI/provenance text.
    encoded=json.dumps(payload,ensure_ascii=True,allow_nan=False).replace('<','\\u003c')
    template=Path(__file__).with_name('pair-qc-viewer.html').read_text()
    require(template.count('__QC_PAYLOAD__')==1,'Invalid QC template')
    require(template.count('__QC_RESIDUAL_SCRIPT__')==1,'Invalid residual module placeholder')
    script=Path(__file__).with_name('pair-qc-residuals.js').read_text()
    require('</script' not in script.lower(),'Unsafe embedded diagnostic module')
    return template.replace('__QC_PAYLOAD__',encoded).replace('__QC_RESIDUAL_SCRIPT__',script)


def batch_products(batch):
    batch=batch.resolve(strict=True)
    paths=[batch/name for name in ('batch.json','execution.json','shared-verification.json')]
    frozen=freeze(paths)
    manifest,receipt,verification=[json.loads(bridge.small(p)) for p in paths]
    require(receipt['status']=='complete_for_owner_inspection' and receipt['source_preservation'] is True and
            receipt['detectors_processed']==len(manifest['entries']) and verification['status']=='passed',
            'Require completed preserved batch')
    require(receipt['manifest_sha256']==frozen[str(paths[0])] and verification['hash_passes_per_image']==2,
            'Batch manifest/verification differs')
    for label in ('before','after'):
        path=batch/('shared-'+label+'.json');frozen.update(freeze([path]))
        require(frozen[str(path)]==verification[label+'_sha256'],'Shared verification hash differs')
    require(json.loads(bridge.small(batch/'shared-before.json'))==json.loads(bridge.small(batch/'shared-after.json')),
            'Shared source verification contents differ')
    products=[Path(manifest['reference']['pairs'])]
    for entry in manifest['entries']:
        parent=Path(entry['measurement']).parent
        require(parent.is_relative_to(batch/'detectors'),'Batch detector path escapes retained batch')
        persistence=parent/'persistence.json';frozen.update(freeze([persistence]))
        saved=json.loads(bridge.small(persistence));path=parent/'asdf/pairs.asdf'
        require(saved['status']=='complete' and saved['roundtrip_exact'] is True and
                saved['metadata_preservation'] is True and saved['products']['pairs']['path']==str(path),
                'Incomplete detector ASDF publication')
        require(bridge.qc.read_record(path).digest==saved['products']['pairs']['digest'],'Saved product digest differs')
        products.append(path)
    return products,frozen


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',type=Path,required=True)
    p.add_argument('--run',type=Path,required=True,help='Fresh empty derived viewer directory')
    a=p.parse_args();work=a.run.resolve(strict=True)
    require(not any(work.iterdir()),'Fresh empty viewer directory required')
    report=dict(status='failed',raw_FITS_opened=False,native_TSV_opened=False,fitted=False,diagnostic_line_fit_available=True,physical_correction_fitted=False)
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            raise RuntimeError('Offline viewer generation')
    sys.addaudithook(offline)
    try:
        products,frozen=batch_products(a.batch)
        payload,inputs=build(ROOT/'config/detectors/omegacam-1x1.toml',ROOT/'config/processing/omegacam-characterization.toml',products)
        frozen.update(inputs)
        require(len(payload['panels'])==32 and all(d['status']=='available' for d in payload['panels']),
                'Completed OCAM batch requires all32 detectors')
        output=work/'qc-mosaic.html';output.write_text(render(payload))
        data_path=work/'qc-data.json';data_path.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
        unchanged(frozen)
        report.update(status='complete_for_owner_inspection',detectors=32,
            signal_time_rows=sum(len(d['signals']) for d in payload['panels']),
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
