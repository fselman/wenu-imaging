#!/usr/bin/env python3
"""Prepare or execute one detector's raw pair measurements from explicit selections."""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib

SPEC=importlib.util.spec_from_file_location('footprints',Path(__file__).with_name('detector-footprint.py'))
FOOTPRINT=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FOOTPRINT)

def require(ok,message):
    if not ok:raise ValueError(message)

def scalar(value):
    text=str(value)
    require(bool(text) and not any(c in text for c in '\t\n\r\0'),'Plan text contains a delimiter/control')
    return text

def keys(value,expected,label):
    require(isinstance(value,dict) and set(value)==set(expected),f'{label}: require exactly {sorted(expected)}')

def natural(value,minimum=0,maximum=2**63-1):
    require(type(value) is int and minimum<=value<=maximum,'Invalid integer choice')
    return value

def finite(value,minimum=0,positive=False):
    require(type(value) in (int,float) and math.isfinite(value) and (value>minimum if positive else value>=minimum),'Invalid finite numeric choice')
    return value

def source(record,flat=False):
    keys(record,('path','hdu','asset','index','pair') if flat else ('path','hdu','asset'),'source')
    path=Path(scalar(record['path']))
    require(path.is_absolute() and path.is_file(),'Source must be an existing absolute file')
    record=dict(record,path=str(path.resolve(strict=True)))
    natural(record['hdu'],0,127);require(len(scalar(record['asset']))<=127,'Asset identifier too long')
    if flat:natural(record['index'],0,2**31-1);require(len(scalar(record['pair']))<=63,'Pair identifier too long')
    return record

def prepare(detectors,processing,selection,native):
    geometry,policy,trims=FOOTPRINT.load(detectors,processing)
    with selection.open('rb') as stream:s=tomllib.load(stream)
    keys(s,('selection_schema_version','detector','readout_id','bin_x','bin_y','raw_saturation_adu',
        'pair_time_tolerance_s','max_loaded_pixels','max_rows','with_mad','reject_bits','exposure_hdu',
        'header_keys','flat','bias','bpm'),'selection')
    require(s['selection_schema_version']==1,'Unknown selection schema')
    d=next((d for d in geometry['detector'] if d['id']==s['detector']),None)
    require(d is not None,'Unknown selected detector')
    require([s['bin_x'],s['bin_y']]==geometry['binning'],'Selected binning differs from detector profile')
    natural(s['bin_x'],1,64);natural(s['bin_y'],1,64)
    require(policy['source_paf_sha256']==hashlib.sha256(native.read_bytes()).hexdigest(),'Native PAF differs from processing profile source')
    keys(s['header_keys'],('identity','amplifier','bin_x','bin_y','exposure'),'header keys')
    for value in s['header_keys'].values():require(len(scalar(value))<=80,'Header key too long')
    finite(s['raw_saturation_adu'],positive=True);finite(s['pair_time_tolerance_s'])
    natural(s['max_loaded_pixels'],1);natural(s['max_rows'],1);natural(s['reject_bits'],0,255)
    natural(s['exposure_hdu'],0,127);require(type(s['with_mad']) is bool,'with_mad must be explicit true/false')
    require(isinstance(s['flat'],list) and 2<=len(s['flat'])<=64 and not len(s['flat'])%2,'Require 2..64 paired flats')
    require(isinstance(s['bias'],list) and len(s['bias'])==2,'Require exactly two raw biases')
    flats=[source(f,True) for f in s['flat']];biases=[source(b) for b in s['bias']]
    bpm=s['bpm'];encoding=bpm.get('encoding')
    if encoding=='omitted':keys(bpm,('encoding',),'omitted BPM');mask=None;good=0;registry='-'
    else:
        extra='good_value' if encoding=='binary' else 'registry'
        require(encoding in ('binary','reason8'),'Unknown BPM encoding')
        keys(bpm,('encoding','path','hdu','asset',extra),'BPM')
        mask=source({k:bpm[k] for k in ('path','hdu','asset')})
        good=natural(bpm['good_value'],0,1) if encoding=='binary' else 0
        registry=scalar(bpm['registry']) if encoding=='reason8' else '-'
    sources=flats+biases+([mask] if mask else [])
    require(len({f['asset'] for f in sources})==len(sources),'Duplicate asset ID')
    require(len({f['index'] for f in flats})==len(flats),'Duplicate input index')
    refs=[(Path(f['path']).stat().st_dev,Path(f['path']).stat().st_ino,f['hdu']) for f in sources]
    require(len(set(refs))==len(refs),'Aliased source file/HDU')
    pairs=[f['pair'] for f in flats]
    require(all(pairs.count(name)==2 for name in pairs),'Each flat pair must have exactly two members')
    regions=[r for r in policy.get('roi',[]) if r['detector']==d['id'] and r['amplifier']==d['amplifier']]
    require(bool(regions),'No selected ROIs')
    require(s['max_rows']>=len(regions)*(len(flats)//2),'Pair row ceiling too small')
    w,h=d['raw_size'];crop=trims[d['id']]['retained'];aw,ah=crop[1]-crop[0]+1,crop[3]-crop[2]+1
    require(s['max_loaded_pixels']>=w*h*(len(flats)+2)+(aw*ah if mask else 0),'Loaded-pixel budget too small')
    hkeys=s['header_keys']
    settings=dict(detector=d['id'],amplifier=d['amplifier'],slot=d['native_paf_chip']-1,
        readout=scalar(s['readout_id']),identity_key=hkeys['identity'],amplifier_key=hkeys['amplifier'],
        bin_x_key=hkeys['bin_x'],bin_y_key=hkeys['bin_y'],bin_x=s['bin_x'],bin_y=s['bin_y'],
        mask_encoding=encoding,good_value=good,mask_registry=registry,reject_bits=s['reject_bits'],
        saturation=s['raw_saturation_adu'],tolerance=s['pair_time_tolerance_s'],max_pixels=s['max_loaded_pixels'],
        max_rows=s['max_rows'],exposure_key=hkeys['exposure'],exposure_hdu=s['exposure_hdu'],
        with_mad=int(s['with_mad']),schema='raw-pair-plan-v1',crop=','.join(map(str,crop)),raw_width=w,raw_height=h)
    lines=['\t'.join((k,scalar(v))) for k,v in settings.items()]
    for f in flats:lines.append('\t'.join(map(scalar,('flat',f['path'],f['hdu'],f['asset'],f['index'],f['pair']))))
    for b in biases:lines.append('\t'.join(map(scalar,('bias',b['path'],b['hdu'],b['asset']))))
    if mask:lines.append('\t'.join(map(scalar,('bpm',mask['path'],mask['hdu'],mask['asset']))))
    roi='roi_schema_version = 1\n'
    for r in regions:
        roi+='\n[[roi]]\n'+''.join(f'{k} = {json.dumps(v)}\n' for k,v in r.items())
    return '\n'.join(lines)+'\n',roi,sources,len(regions),(d['id'],d['amplifier'])

def fingerprint(path):
    path=Path(path);before=path.stat();digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):digest.update(chunk)
    after=path.stat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
            (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Source changed during hashing')
    return dict(path=str(path.resolve()),device=after.st_dev,inode=after.st_ino,size=after.st_size,
        mtime_ns=after.st_mtime_ns,ctime_ns=after.st_ctime_ns,sha256=digest.hexdigest())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('detectors','processing','selection','native-paf','command','run'):
        p.add_argument('--'+name,required=True,type=Path)
    p.add_argument('--source-revision',required=True)
    p.add_argument('--execute',action='store_true',help='Execute; default only prepares the plan')
    a=p.parse_args();require(re.fullmatch('[0-9a-f]{40}',a.source_revision) is not None,'Require exact source revision')
    work=a.run.resolve(strict=True);require(work.is_dir() and not any(work.iterdir()),'Fresh empty run directory required')
    report=dict(status='preparing',source_revision=a.source_revision,mode='raw_pair_measurements',detectors_processed=0)
    (work/'README.md').write_text('''# Raw pair measurement review

This directory retains the explicit selections, generated native plan, raw pair
and bias RON tables, native configuration snapshot, logs and source fingerprints.
It is needed for reviewing and reproducing this detector measurement. It is not
a fitted calibration. execution.json is the authoritative overall status; a native
completion marker alone does not establish that final source checks passed. Keep original observations unchanged in their source paths.
It may be erased after its measurements are accepted or superseded and any tables
or provenance needed for future comparison have been retained elsewhere under the
instrument Pictures/wenu-imaging hierarchy. A failed attempt may be erased after
the failure is documented and any required evidence is retained.
''')
    try:
        paths=list(dict.fromkeys(str(p.resolve(strict=True)) for p in
            (a.detectors,a.processing,a.selection,a.native_paf,a.command,Path(__file__),Path(__file__).with_name('detector-footprint.py'))))
        before=[fingerprint(path) for path in paths]
        plan,rois,sources,nroi,identity=prepare(a.detectors,a.processing,a.selection,a.native_paf)
        extras=[path for path in dict.fromkeys(s['path'] for s in sources) if path not in paths]
        for i,path in enumerate(extras,1):
            print(f'Fingerprinting observation {i}/{len(extras)}',flush=True);before.append(fingerprint(path))
        paths+=extras
        report.update(inputs=before,detector=identity[0],amplifier=identity[1])
        (work/'plan.tsv').write_text(plan);(work/'selected-rois.toml').write_text(rois)
        (work/'selection.toml').write_bytes(a.selection.read_bytes())
        argv=[str(a.command.resolve()),str(a.native_paf.resolve()),str(work/'selected-rois.toml'),str(work/'plan.tsv'),str(work/'native')]
        report.update(argv=argv,roi_count=nroi,source_freezing='before/after fingerprints; not a file lock')
        if a.execute:
            (work/'native').mkdir()
            with (work/'command.log').open('w') as log:
                code=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT).returncode
            report['native_exit_status']=code
            require(code==0,'Native command failed; retain command.log and partial files')
            require((work/'native/command.complete').read_text()=='raw_pair_tables_complete\n','Missing/invalid native completion marker')
            rows={}
            for filename in ('pairs.tsv','bias-ron.tsv'):
                with (work/'native'/filename).open(newline='') as stream:
                    table=list(csv.DictReader(stream,delimiter='\t',quoting=csv.QUOTE_NONE))
                require(bool(table) and all(None not in row and None not in row.values() for row in table),'Incomplete exported table')
                rows[filename]=len(table)
            require(rows['bias-ron.tsv']==nroi and rows['pairs.tsv']==nroi*(len([s for s in sources if 'pair' in s])//2),'Unexpected output row count')
            report['output_rows']=rows
            report['outputs']=[fingerprint(f) for f in sorted((work/'native').iterdir())]
        after=[]
        for i,path in enumerate(paths,1):
            print(f'Verifying source {i}/{len(paths)}',flush=True);after.append(fingerprint(path))
        require(before==after,'Source changed during preparation/execution')
        report['source_preservation']=True
        report['status']='complete_for_owner_inspection' if a.execute else 'prepared_not_executed'
        report['detectors_processed']=1 if a.execute else 0
    except Exception as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}')
        raise
    finally:
        (work/'execution.json').write_text(json.dumps(report,indent=2)+'\n')
        print('STATUS:',report['status'],flush=True)
        print('RETAINED RUN:',work,flush=True)

if __name__=='__main__':main()
