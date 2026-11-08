"""Read product/BPM pixels and native ASDF; never open raw frame data.
Creates comparison reports under orchestration; scientific products stay read-only.
"""
import hashlib,json,os,platform,socket,subprocess,tempfile
from pathlib import Path
import numpy as np
from astropy.io import fits

ASDF_READER=r'''
import json,sys
from pathlib import Path
import asdf
import numpy as np
v=json.load(sys.stdin);root=Path(v['source'])
sys.path.insert(0,str(root/'mefpp2/tests'))
from bias_qc_fits_contract import verify
schema=(root/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json').read_bytes()
def clean(x):
    if isinstance(x,dict):return {k:clean(z) for k,z in x.items()}
    if isinstance(x,(list,tuple)):return [clean(z) for z in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x
def mapped(ms,own):
    result={}
    for m in clean(ms):
        m['sources']=['<own-product>' if s==own else s for s in m['sources']]
        assert m['name'] not in result;result[m['name']]=m
    return result
def master_change(name):
    return (name.startswith(('master.','master_unmasked.','pixels.hot')) and name!='pixels.hot.sigma') or name in ('legacy.product_median','legacy.product_stdev')
with asdf.config_context() as c:
    c.add_resource_mapping({json.loads(schema)['id']:schema})
    with asdf.open(Path(v['new']).with_suffix('.asdf'),custom_schema=json.loads(schema)['id'],lazy_load=False,strict_extension_check=True) as nf, asdf.open(Path(v['old']).with_suffix('.asdf'),custom_schema=json.loads(schema)['id'],lazy_load=False,strict_extension_check=True) as of:
        nf.validate();of.validate();n=nf.tree['qc'];o=of.tree['qc']
        assert n['file']['location']==v['new'] and o['file']['location']==v['old']
        assert n['provenance']['producer']['source_revision']=='74327c49832a9337fad49a0bec1b5fd7af81cde5'
        assert o['provenance']['producer']['source_revision']=='f95cc9b333be9e53d2695d77d643906ce06222ab'
        ns=json.loads(n['provenance']['configuration']['snapshot']);os=json.loads(o['provenance']['configuration']['snapshot'])
        assert ns.pop('MEF.BIAS.MEDIAN.EVEN.HANDLING')=={'type':'string','value':'average'}
        assert ns==os,'Other numerical configuration changed'
        assert n['provenance']['recipe_configuration']['snapshot']==v['config_text']
        assert clean(n['inputs'])==clean(o['inputs']),'Input membership changed'
        assert clean(n['embedded_input_records'])==clean(o['embedded_input_records']),'Input QC changed'
        assert clean(n['calibrations'])==clean(o['calibrations']),'Calibration identities changed'
        rows=[];checked=0
        for i,(nd,od) in enumerate(zip(n['characterization']['detectors'],o['characterization']['detectors'])):
            assert nd['detector_id']==od['detector_id']==v['ids'][i]
            assert nd['output_hdu']==od['output_hdu']==i+1
            assert nd['configuration_detector']==od['configuration_detector']==i
            assert nd['median_even_handling']=='average' and od.get('median_even_handling','lower')=='lower'
            checked+=verify(v['new_headers'][i],n,nd)+verify(v['old_headers'][i],o,od)
            a=mapped(nd['measurements'],v['new']);b=mapped(od['measurements'],v['old'])
            assert a.keys()==b.keys()
            for name in a:
                if not master_change(name):assert a[name]==b[name],(nd['detector_id'],name)
            used=sum(next(d for d in item['participation_by_detector'] if d['detector_id']==nd['detector_id'])['status']=='used' for item in n['inputs'])
            def values(ms):return {k:x['value'] for k,x in ms.items() if k.startswith(('master.','master_unmasked.','pixels.hot')) and k not in ('pixels.hot.x','pixels.hot.y')}
            rows.append(dict(id=nd['detector_id'],used=used,new=values(a),old=values(b)))
        assert len(rows)==len(n['characterization']['detectors'])==len(o['characterization']['detectors'])==32
print(json.dumps(dict(rows=rows,mapped_cards=checked)))
'''

def identity(p):
    s=p.stat();return [s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_ino]
def require(ok,message):
    if not ok:raise RuntimeError(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def qc(header,path):
    cards=[c for c in header.cards if c.keyword.startswith('ESO MPP QC ')]
    values={c.keyword:c.value for c in cards};require(len(cards)==len(values),'Duplicate QC card')
    require(values['ESO MPP QC ASDF']==path.with_suffix('.asdf').name and values['ESO MPP QC PROD']==path.name,'Wrong own-product identity')
    return values

def check_statistics(data,good,wanted):
    require(np.isfinite(data).all(),'Nonfinite product pixels')
    for prefix,mask in [('master.',good),('master_unmasked.',np.ones(data.shape,dtype=bool))]:
        values=data[mask].astype(np.float64);median=float(np.median(values))
        measured=dict(mean=float(np.mean(values)),median=median,stdev=float(np.std(values,ddof=1)),scaled_mad=float(np.median(np.abs(values-median)))*1.4826,valid_pixels=len(values),region_pixels=data.size,bpm_excluded=data.size-len(values),nonfinite_excluded=0)
        for name,value in measured.items():
            stored=wanted[prefix+name]
            require(stored is not None and np.isclose(stored,value,rtol=2e-7,atol=2e-8),f'Independent {prefix+name}: stored {stored}, recomputed {value}')
    require(int(np.count_nonzero(data>wanted['pixels.hot.threshold']))==wanted['pixels.hot'],'High-offset count disagrees with pixels')

require(platform.system()=='Darwin' and socket.gethostname().split('.')[0]=='MC02VV0HPHTDG','Expected selected Mac')
base=Path('/Users/fselman/Pictures/OCAM/test_recipes');orch=base/'orchestration';reduced=base/'reduced/cal/bias'
new=reduced/'CMDP.2026-11-08T00:41:24.199Z.001.fits';old=reduced/'CMDP.2026-11-07T21:05:44.919Z.001.fits'
source=Path('/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb/scalar-qc-c17-source')
asdf_python=Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python')
run=orch/'bias-median-average-real-dlraaym2/run-results.json';receipt=json.loads(run.read_text())
require(receipt['successful'] and receipt['preserved'] and receipt['median_even_handling']=='average','Unexpected real-run receipt')
require(str(new) in receipt['products'] and receipt['reference']==str(old),'Product paths disagree with receipt')
config=orch/'bias-recipe.toml';config_text=config.read_text();used=run.with_name('bias-recipe.toml.used')
require(config_text==used.read_text(),'Configuration changed after run')
bpm=Path('/Users/fselman/Pictures/OCAM/wenu-imaging/legacy-bpm-structure-b1h9egzp/prepared/OCAM_BPM_1x1_structural.fits')
files=[new,old,new.with_suffix('.asdf'),old.with_suffix('.asdf'),new.with_suffix('.log'),old.with_suffix('.log'),config,used,run,bpm]
preserved={str(v):identity(v) for v in files}
with fits.open(new,mode='readonly',memmap=True) as nh, fits.open(old,mode='readonly',memmap=True) as oh:
    require(len(nh)==len(oh)==33,'Expected 32-detector products')
    ids=[v.header['EXTNAME'] for v in nh[1:]]
    require(ids==[v.header['EXTNAME'] for v in oh[1:]],'Detector order differs')
    new_headers=[qc(v.header,new) for v in nh[1:]];old_headers=[qc(v.header,old) for v in oh[1:]]
work=Path(tempfile.mkdtemp(prefix='bias-median-comparison-',dir=orch))
priority=os.getpriority(os.PRIO_PROCESS,0)
if priority<10:os.nice(10-priority)
payload=dict(source=str(source),new=str(new),old=str(old),ids=ids,new_headers=new_headers,old_headers=old_headers,config_text=config_text)
print('Checking native ASDF schema, complete FITS mapping and input/RON invariance...',flush=True)
r=subprocess.run([str(asdf_python),'-B','-c',ASDF_READER],input=json.dumps(payload),capture_output=True,text=True,timeout=180)
(work/'asdf-verification.log').write_text(r.stderr)
require(r.returncode==0,'ASDF verification failed; inspect '+str(work/'asdf-verification.log'))
verified=json.loads(r.stdout);results=[]
print('Master means/medians: ADU; pixel shifts: average minus lower',flush=True)
print('CCD             used   mean lower   mean average   delta mean   median lower  median average   pixel check',flush=True)
with fits.open(new,mode='readonly',memmap=True) as nh, fits.open(old,mode='readonly',memmap=True) as oh, fits.open(bpm,mode='readonly',memmap=True) as mh:
    for i,row in enumerate(verified['rows'],1):
        a=nh[i].data;b=oh[i].data;good=mh[i].data==1
        require(a.shape==b.shape==good.shape,'Image/BPM shapes differ')
        check_statistics(a,good,row['new']);check_statistics(b,good,row['old'])
        delta=np.subtract(a,b,dtype=np.float64)
        require(np.isfinite(delta).all(),'Nonfinite difference')
        if row['used']%2:
            require(a.dtype==b.dtype and np.array_equal(a.view('>u4'),b.view('>u4')),'Odd-count pixel bytes changed')
            check='EXACT'
        else:
            require(np.min(delta)>=0,'Even average fell below historical lower')
            check='NONNEGATIVE'
        row['pixel_delta']=dict(min=float(np.min(delta)),max=float(np.max(delta)),mean=float(np.mean(delta)),changed=int(np.count_nonzero(delta)))
        row['mean_shift']=row['new']['master.mean']-row['old']['master.mean'];results.append(row)
        print(f"{row['id']:15} {row['used']:2}/10 {row['old']['master.mean']:12.6f} {row['new']['master.mean']:14.6f} {row['mean_shift']:12.6f} {row['old']['master.median']:14.6f} {row['new']['master.median']:15.6f}   {check}",flush=True)
require(preserved=={p:identity(Path(p)) for p in preserved},'Scientific file identity changed')
report=dict(successful=True,new=str(new),reference=str(old),rows=results,mapped_cards=verified['mapped_cards'],independent_master_statistics_tolerance=dict(relative=2e-7,absolute_adu=2e-8),raw_frames_opened=False,scientific_files_unchanged=True)
(work/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: native ASDF schema and',verified['mapped_cards'],'mapped FITS/ASDF cards.')
print('PASS: unchanged input QC, membership, numerical settings and RON; independently recomputed master statistics/hot counts.')
print('PASS: odd-count pixel bytes exact; even-count pixel shifts nonnegative. No raw frames opened; scientific files unchanged.')
print('REPORT:',work/'comparison.json')
