"""Independent tiny FITS and prior sample-archive fixture for preparation."""
from copy import deepcopy
import json
import hashlib
from pathlib import Path
import re
import struct
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'mefpp2/tests'))
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
from linearity_files_contract import plane
from layout_contract import header
from config_snapshot_contract import expected_values
import pycavi_linearity_config as config
import pycavi_linearity_recipe as recipe


def fixture(work):
    work=Path(work);work.mkdir(parents=True,exist_ok=True);name='ESO_CCD_#65'
    detector='''footprint_schema_version=1
instrument="omegacam"
binning=[1,1]
[[detector]]
id="ESO_CCD_#65"
amplifier="L"
native_paf_chip=1
raw_size=[8,4]
illuminated=[2,7,1,4]
prescan=[1,1,1,4]
overscan=[8,8,1,4]
'''
    processing='''processing_footprint_schema_version=1
linearity_preparation_schema_version=1
instrument="omegacam"
roi_schema_version=1
roi_coordinates="retained-active"
use_prescan=1
use_overscan=1
scan_reject_low=0
scan_reject_high=0
[linearity_preparation]
raw_saturation_adu=65534.0
reject_bits=255
mask_encoding="binary"
binary_good_value=1
pair_time_tolerance_s=0.0
with_mad=true
bias_mean_min_adu=0.0
bias_mean_max_adu=1000.0
bias_stack_kappa=2.0
bias_min_frames=3
high_offset_sigma=5.0
[[trim]]
detector="ESO_CCD_#65"
retained=[2,7,2,3]
prescan_sample=[1,1,1,4]
overscan_sample=[8,8,1,4]
'''
    for i in range(5):processing+=f'\n[[roi]]\nid="CCD65.R{i}"\ndetector="{name}"\namplifier="L"\nxmin=1\nxmax=6\nymin=1\nymax=2\n'
    resolved=config.resolve(detector,processing)
    baseline=json.loads((ROOT/'docs/architecture/proposed/m1/effective-settings-baseline.json').read_text())
    all_values=expected_values(baseline,'wfi')
    snapshot={k:v for k,v in all_values.items() if not re.search(r'\.CHIP([2-9]|[1-9][0-9]+)$',k)}
    values={'MEF.NCHIPS':1,'MEF.USE.PRESCAN':1,'MEF.USE.OVERSCAN':1,'MEF.SCANREJ.MIN':0,'MEF.SCANREJ.MAX':0,
        'MEF.BIAS.FRAMENUM.MIN':3,'MEF.PRESCAN.X.MIN.CHIP1':1,'MEF.PRESCAN.X.MAX.CHIP1':1,
        'MEF.OVERSCAN.X.MIN.CHIP1':8,'MEF.OVERSCAN.X.MAX.CHIP1':8,'MEF.CROP.X.MIN.CHIP1':2,
        'MEF.CROP.X.MAX.CHIP1':7,'MEF.CROP.Y.MIN.CHIP1':2,'MEF.CROP.Y.MAX.CHIP1':3}
    for k,v in values.items():snapshot[k]={'type':'int','value':v}
    snapshot['MEF.BIAS.KAPPA1']={'type':'float64-bits','value':struct.pack('>d',2.).hex()}
    snapshot['MEF.INSTRUMENT']={'type':'string','value':'OMEGACAM'}
    flats=[]
    for f in range(20):
        t=2+min(f,19-f);data=[]
        for y in range(4):
            data.append(10+10*y+3*f)
            data += [12+10*y+3*f+3+100*t+(y-1)*6+x for x in range(6)]
            data.append(14+10*y+3*f)
        extra=[('EXPTIME',str(t))]
        if f%2:
            content=header([('SIMPLE','T'),('BITPIX','8'),('NAXIS','0'),('EXTEND','T')]+extra)
            content+=plane([0]*32,8,4,primary=False,detector='OTHER')
            content+=plane(data,8,4,primary=False,detector=name,amplifier='L');hdu=2
        else:content=plane(data,8,4,extra=extra,detector=name,amplifier='L');hdu=0
        path=work/f'flat{f}.fits';path.write_bytes(content)
        flats.append(dict(path=str(path),hdu=hdu,asset=path.name,index=10+f,pair=f'P{min(f,19-f)}'))
    biases=[]
    for f in range(10):
        data=[]
        for y in range(4):
            data.append(10+10*y+20*f)
            data += [12+10*y+20*f+3+((1 if x%2 else -1) if f==0 else 0) for x in range(6)]
            data.append(14+10*y+20*f)
        path=work/f'bias{f}.fits';path.write_bytes(plane(data,8,4,extra=[('EXPTIME','0')],detector=name,amplifier='L'))
        biases.append(dict(path=str(path),hdu=0,asset=path.name,index=f,accepted=int(f!=3)))
    empty=header([('SIMPLE','T'),('BITPIX','8'),('NAXIS','0'),('EXTEND','T')])
    master=work/'master.fits';master.write_bytes(empty+plane([3]*12,6,2,primary=False,detector=name,amplifier='L'))
    bpm=work/'bpm.fits';bpm.write_bytes(empty+plane([1]*12,6,2,primary=False,byte=True,mask=True,detector=name,amplifier='L'))
    selection=dict(selection_schema_version=1,detector=name,readout_id='OMEGACAM:normal:ordered:1x1',bin_x=1,bin_y=1,
        raw_saturation_adu=65534.,pair_time_tolerance_s=0.,max_loaded_pixels=10000,max_rows=50,with_mad=True,reject_bits=255,
        exposure_hdu=0,header_keys=dict(identity='DETID',amplifier='AMPID',bin_x='XBINNING',bin_y='YBINNING',exposure='EXPTIME'),
        flat=flats,bias=[{k:b[k] for k in ('path','hdu','asset')} for b in biases[:2]],
        bpm=dict(path=str(bpm),hdu=1,asset=bpm.name,encoding='binary',good_value=1))
    sites=[dict(detector=name,amplifier='L',configuration_detector=0,source_roi=f'CCD65.R{i}',
                active_pixel=[i+1,1],raw_pixel=[i+2,2]) for i in range(5)]
    prepared=recipe.native_plan(resolved,selection,sites)
    (work/'native.toml').write_text(recipe.native_configuration(resolved,snapshot))
    for k,filename in [('plan','plan.tsv'),('rois','rois.toml'),('sites','sites.toml')]:(work/filename).write_text(prepared[k])
    (work/'biases.tsv').write_text('input_index\thdu\tasset\tpath\taccepted\n'+''.join(
        f"{b['index']}\t{b['hdu']}\t{b['asset']}\t{b['path']}\t{b['accepted']}\n" for b in biases))
    return dict(work=work,resolved=resolved,selection=selection,sites=sites,biases=biases,master=str(master),snapshot=snapshot)


def native_argv(state,command,out):
    w=state['work']
    return [str(command),str(w/'native.toml'),str(w/'rois.toml'),str(w/'sites.toml'),str(w/'plan.tsv'),
            state['master'],'1','master.fits',str(w/'biases.tsv'),str(out)]


def source_archive(state):
    # Reuse the existing shared-ASDF test factory and serializer, replacing its
    # prior fixture table with independent analytic values for these tiny FITS.
    import test_sample_qc as existing
    sample=existing.bridge;w=state['work'];_,old,_,_,_,origin=existing.fixture(w)
    entry=old['entry'];entry['selection']=state['selection'];entry['population']=state['sites']
    entry['active_pixels']=12;old['native_configuration']=state['snapshot']
    qc=sample.qc;masterdir=w/'fixture-master';masterdir.mkdir();members=[]
    descriptors=state['biases']+[dict(path=str(w/'bpm.fits'),hdu=1,asset='bpm.fits',accepted=1)]
    for i,b in enumerate(descriptors):
        builder=qc.QcRecipe(file=dict(id=b['path'],filename=Path(b['path']).name,location=b['path'],
            kind='raw' if i<10 else 'product',sha256=None,observed_at=None,
            selectors=[dict(detector_id=entry['detector'],hdu_index=b['hdu'],configuration_detector=0)],
            context=dict(readout_id=state['selection']['readout_id'],bin_x=1,bin_y=1)),
            assessment_id='fixture-master:'+b['asset'],created_at='2026-11-05T00:00:00Z',
            producer=dict(name='fixture',version='1',source_revision='old-native'),operation='cal.bias',configuration_id='sha256:'+recipe.hashlib.sha256(recipe.canonical(state['snapshot']).encode()).hexdigest())
        leaf=builder.seal();path=qc.write_record(leaf,masterdir);members.append((leaf,path,b['accepted']))
    builder=qc.QcRecipe(file=dict(id=state['master'],filename='master.fits',location=state['master'],kind='product',sha256=hashlib.sha256(Path(state['master']).read_bytes()).hexdigest(),
        observed_at=None,selectors=[dict(detector_id=entry['detector'],hdu_index=1,configuration_detector=0)],context={}),
        assessment_id='fixture-master:product',created_at='2026-11-05T00:00:00Z',
        producer=dict(name='fixture',version='1',source_revision='old-native'),operation='cal.bias',configuration_id='sha256:'+recipe.hashlib.sha256(recipe.canonical(state['snapshot']).encode()).hexdigest())
    for leaf,path,accepted in members:builder.add_input(leaf,qc_path=path.name,
        participation='used' if accepted else 'rejected',reason=None if accepted else 'fixture_rejection')
    master=builder.seal();path=qc.write_record(master,masterdir)
    old['master_records']=[master]+[r for r,_,_ in members]
    entry['master'].update(qc_product=str(path),recipe=dict(qc_record_digest=master.digest))
    lines=['\t'.join(sample.COLUMNS)]
    for f,frame in enumerate(state['selection']['flat']):
        for i,point in enumerate(state['sites']):
            lines.append('\t'.join(map(str,[1,entry['detector'],'L',0,point['source_roi'],i+1,1,i+2,2,
                frame['asset'],frame['index'],frame['hdu'],frame['pair'],2+min(f,19-f),'admitted',
                100*(2+min(f,19-f))+i,'unavailable'])))
    old['table']=sample.parse(('\n'.join(lines)+'\n').encode())
    old['population']=sample.parse_population(('input_index\toutside_selected_sites\tbpm_excluded\tsample_excluded\tnonfinite\tsaturated\tadmitted\n'+
        ''.join(f'{10+i}\t7\t0\t0\t0\t0\t5\n' for i in range(20))).encode())
    for source in state['selection']['flat']+[state['selection']['bpm']]+[dict(path=state['master'])]:
        origin['image_fingerprints'][source['path']]=dict(sha256=hashlib.sha256(Path(source['path']).read_bytes()).hexdigest(),stat=[1,2,3,4,5,6])
    target=w/'prior-samples';target.mkdir()
    state['master_qc']=master
    state['handoff']=dict(detector_id=entry['detector'],configuration_detector=0,output=state['master'],output_hdu=1,
        readout_id=state['selection']['readout_id'],bin_x=1,bin_y=1,input_hdu=0,producer=master.as_dict()['provenance']['producer'],
        configuration=state['snapshot'],configuration_record=str(w/'configuration.json'),
        inputs=[dict(path=b['path'],accepted=b['accepted']) for b in state['biases']])
    (w/'configuration.json').write_text(json.dumps(state['snapshot']))
    (w/'handoff.json').write_text(json.dumps(state['handoff']))
    (w/'outer-execution.json').write_text(json.dumps(dict(status='complete_for_owner_inspection',
        detector=entry['detector'],product=state['master'],qc_product=str(path),
        preservation={k:True for k in ('checkout','installed_files','exported_source','private_qc_runtime','inputs')},
        inputs={b['path']:dict(sha256=hashlib.sha256(Path(b['path']).read_bytes()).hexdigest()) for b in state['biases']})))
    return Path(sample.publish_entry(old,target,assessment_id='prior',created_at='2026-11-05T00:00:00Z',
        serializer_revision='a'*40,origin=origin)['path'])
