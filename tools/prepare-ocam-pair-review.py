#!/usr/bin/env python3
"""Review saved OCAM headers and write a proposed first-detector selection; never execute."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import re
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib
ROOT=Path(__file__).resolve().parents[1]
API=runpy.run_path(str(ROOT/'Pycavi2/tools/prepare_ocam_pair_measurements.py'))
single=API['single']

def require(ok,message):
    if not ok:raise ValueError(message)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def stat_identity(path):
    s=path.stat();return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_mode]

def review(inventory,detectors):
    """Pure saved-header policy; current file identity is checked separately."""
    require(not inventory.get('errors'),'Original inventory contains errors')
    require(inventory.get('source_stat_preservation',{}).get('passed') is True,'Original preservation failed/unknown')
    expected=API['selected_sequence'](Path(inventory['raw_root']))
    actual=inventory['selected'];require(len(actual)==30,'Require exact 30-file sequence')
    identities={d['id']:d for d in detectors};require(len(identities)==32,'Require complete OCAM detector profile')
    bindings={};primary_signature=None;templates={};encodings={};warnings=[]
    for wanted,row in zip(expected,actual):
        for field in ('path','index','role','pair_id'):
            require(row.get(field)==wanted[field],f'Sequence mismatch at {wanted["index"]}: {field}')
        require(not row.get('errors'),'Prior metadata error')
        inspection=row['inspection'];hdus=inspection['asset']['hdus'];primary=hdus[0]
        require(primary['hdu']==0,'Missing primary header')
        for key,value in [('INSTRUME','OMEGACAM'),('ESO OBS ID',574184),('EXPTIME',wanted['expected_seconds']),
                          ('ESO DPR TYPE',wanted['expected_type']),('ESO INS FILT1 NAME',wanted['expected_filter'])]:
            require(single(primary,key)==value,f'{Path(row["path"]).name}: {key} mismatch/missing/duplicate')
        signature={key:single(primary,key) for key in ('ESO DET READ MODE','ESO DET READ SPEED','ESO DET READ CLOCK',
                    'ESO DET WIN1 BINX','ESO DET WIN1 BINY','ESO DET OUTPUTS')}
        require(signature=={'ESO DET READ MODE':'normal','ESO DET READ SPEED':'normal',
                'ESO DET READ CLOCK':'mosaic read (ordered)','ESO DET WIN1 BINX':1,'ESO DET WIN1 BINY':1,
                'ESO DET OUTPUTS':32},'Primary readout/clock/binning/output mismatch')
        if primary_signature is None:primary_signature=signature
        require(signature==primary_signature,'Mixed readouts')
        template=[single(primary,'ESO TPL ID'),single(primary,'ESO TPL START')]
        require(all(isinstance(v,str) and v for v in template),'Missing/ambiguous template metadata')
        require(templates.setdefault(row['role'],template)==template,'Mixed template sequence')
        seen={}
        for hdu in hdus[1:]:
            if not hdu.get('dimensions'):continue
            identity=single(hdu,'EXTNAME')
            require(identity in identities and identity not in seen,'Unknown/duplicate output identity')
            d=identities[identity]
            require(hdu['dimensions']==d['raw_size'],'Raw dimensions differ from reviewed profile')
            for key,value in [('ESO DET CHIP ID',identity),('ESO DET OUT1 ID',d['amplifier']),
                              ('ESO DET OUT1 NX',2048),('ESO DET OUT1 NY',4100),
                              ('ESO DET OUT1 PRSCX',48),('ESO DET OUT1 OVSCX',48)]:
                require(single(hdu,key)==value,f'{identity}: {key} mismatch/missing/duplicate')
            encoding=[single(hdu,k) for k in ('BITPIX','BSCALE','BZERO','BUNIT')]
            encodings.setdefault(identity,[])
            if encoding not in encodings[identity]:encodings[identity].append(encoding)
            seen[identity]=hdu['hdu']
        require(set(seen)==set(identities),'Incomplete output coverage')
        bindings[row['index']]=seen
        for diagnostic in inspection.get('diagnostics',[]):
            require(diagnostic['code']=='fits_warning','Non-warning diagnostic in saved inventory')
            warnings.append(diagnostic)
    candidate=[c for c in inventory['candidates'] if Path(c['path']).name=='OCAM_BPM_1x1.fits']
    require(len(candidate)==1,'Require one explicit legacy BPM candidate')
    candidate=candidate[0];mask_bindings={}
    for hdu in candidate['inspection']['asset']['hdus']:
        if not hdu.get('dimensions'):continue
        identity=single(hdu,'EXTNAME');require(identity in identities and identity not in mask_bindings,'BPM identity mismatch')
        require(hdu['dimensions']==[2044,4091] and single(hdu,'BITPIX')==8,'BPM footprint/type mismatch')
        mask_bindings[identity]=hdu['hdu']
    require(set(mask_bindings)==set(identities),'Incomplete BPM coverage')
    return dict(primary_readout=primary_signature,templates=templates,raw_bindings=bindings,bpm_bindings=mask_bindings,
                bpm_path=candidate['path'],raw_encoding_evidence=encodings,diagnostic_count=len(warnings),
                detector_count=32,selected_count=30,flat_count=20,bias_count=10,pair_count=10,
                header_admission='saved headers reviewed; current source stat equality required',
                history_review=['ESO_CCD_#69','ESO_CCD_#77'])

def proposed_selection(inventory,geometry,report,processing):
    d=next(d for d in geometry['detector'] if d['id']=='ESO_CCD_#65')
    rows=inventory['selected'];bias=rows[:2];flats=rows[10:]
    crop=next(t for t in processing['trim'] if t['detector']==d['id'])['retained']
    nroi=sum(r['detector']==d['id'] and r['amplifier']==d['amplifier'] for r in processing['roi'])
    pixels=d['raw_size'][0]*d['raw_size'][1]*22+(crop[1]-crop[0]+1)*(crop[3]-crop[2]+1)
    choices=dict(selection_schema_version=1,detector=d['id'],readout_id='OMEGACAM:normal:ordered:1x1',bin_x=1,bin_y=1,
        raw_saturation_adu=65534,pair_time_tolerance_s=0,max_loaded_pixels=pixels,max_rows=nroi*10,
        with_mad=True,reject_bits=255,exposure_hdu=0)
    def dump(values):return ''.join(k+' = '+(str(v).lower() if type(v) is bool else json.dumps(v))+'\n' for k,v in values.items())
    out='# PROPOSAL FOR OWNER REVIEW. No pixel measurements have run.\n'+dump(choices)
    out+='\n[header_keys]\n'+dump(dict(identity='EXTNAME',amplifier='HIERARCH ESO DET OUT1 ID',
        bin_x='HIERARCH ESO DET WIN1 BINX',bin_y='HIERARCH ESO DET WIN1 BINY',exposure='EXPTIME'))
    for row in flats:
        out+='\n[[flat]]\n'+dump(dict(path=row['path'],hdu=report['raw_bindings'][row['index']][d['id']],
             asset=Path(row['path']).name,index=row['index'],pair=row['pair_id']))
    for row in bias:
        out+='\n[[bias]]\n'+dump(dict(path=row['path'],hdu=report['raw_bindings'][row['index']][d['id']],asset=Path(row['path']).name))
    out+='\n[bpm]\n'+dump(dict(encoding='binary',good_value=1,path=report['bpm_path'],
                                hdu=report['bpm_bindings'][d['id']],asset='OCAM_BPM_1x1.fits'))
    return out,dict(detector=d['id'],bias_paths=[r['path'] for r in bias],raw_saturation_adu=65534,
        bpm_good_value=1,roi_count=nroi,pair_rows=nroi*10,max_loaded_pixels=pixels,
        status='proposal_not_executed',saturation_basis='current native PAF digital exclusion boundary, not an analog nonlinearity threshold',
        bias_basis='first two chronological biases, same admitted configuration; suitability not yet measured',
        bpm_basis='legacy Eclipse 1=good convention; binary counts alone do not establish polarity')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventory',required=True,type=Path)
    p.add_argument('--bpm-review',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();out=a.output.resolve(strict=True)
    require(out.is_dir() and not any(out.iterdir()),'Fresh empty review directory required')
    (out/'README.md').write_text('''# OCAM first-detector selection review

Contains saved header evidence, source stat checks and proposed settings for the
first real raw pair measurement. No pixel measurements or fit are performed.
Keep for the selection/admission review and later reproducibility. It may be
erased after accepted selections and required evidence are retained with the
actual measurement run or after a superseding review replaces this one.
''')
    result=dict(status='reviewing',measurement_executed=False)
    try:
        detector_path=ROOT/'config/detectors/omegacam-1x1.toml';processing_path=ROOT/'config/processing/omegacam-characterization.toml'
        native=ROOT/'mefpp2/ins/mef/config/omegacam.paf'
        evidence=(a.inventory,a.bpm_review,detector_path,processing_path,native,Path(__file__))
        before={str(f):digest(f) for f in evidence}
        inventory=json.loads(a.inventory.read_text())
        with detector_path.open('rb') as stream:geometry=tomllib.load(stream)
        with processing_path.open('rb') as stream:processing=tomllib.load(stream)
        native=ROOT/'mefpp2/ins/mef/config/omegacam.paf'
        require(processing['source_paf_sha256']==digest(native),'Processing/native PAF mismatch')
        require(re.findall(r'^MEF\.SATLEVEL\s+([0-9]+);',native.read_text(),re.M)==['65534'],'Saturation proposal no longer matches PAF; review it')
        report=review(inventory,geometry['detector'])
        checked=[]
        for row in inventory['selected']+[c for c in inventory['candidates'] if c['path']==report['bpm_path']]:
            path=Path(row['path']);require(stat_identity(path)==row['stat_before'],'Source changed since saved headers: '+str(path))
            checked.append(dict(path=str(path),stat_identity=stat_identity(path)))
        # Preserve already obtained review evidence; never rescan mask pixels here.
        json.loads(a.bpm_review.read_text())
        (out/'inventory.json').write_bytes(a.inventory.read_bytes())
        (out/'prior-selection-review.json').write_bytes(a.bpm_review.read_bytes())
        text,proposal=proposed_selection(inventory,geometry,report,processing)
        (out/'selection-proposed.toml').write_text(text)
        require(before=={str(f):digest(f) for f in evidence},'Review source/configuration changed')
        require(all(stat_identity(Path(c['path']))==c['stat_identity'] for c in checked),'Observation changed during review')
        result.update(status='prepared_for_owner_choices',headers=report,proposal=proposal,current_source_stats=checked,
            evidence_sha256=before)
        for key in ('detector','raw_saturation_adu','bpm_good_value','roi_count','pair_rows','max_loaded_pixels'):
            print(key.upper()+':',proposal[key],flush=True)
        encodings={json.dumps(v) for values in report['raw_encoding_evidence'].values() for v in values}
        print('RAW ENCODINGS [BITPIX, BSCALE, BZERO, BUNIT]:',', '.join(sorted(encodings)),flush=True)
        print('PROPOSED BIASES:',*proposal['bias_paths'],sep='\n  ',flush=True)
        print('HEADERS REVIEWED: 30 files × 32 detectors; source stat identities unchanged',flush=True)
    except Exception as error:
        result.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        (out/'review.json').write_text(json.dumps(result,indent=2)+'\n')
        print('STATUS:',result['status'],flush=True);print('REVIEW DIRECTORY:',out,flush=True)

if __name__=='__main__':main()
