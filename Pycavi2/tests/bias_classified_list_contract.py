"""Shared list contract through the actual bias coordinator; synthetic inputs only."""
import sys,tempfile,json,subprocess
from pathlib import Path
import argparse, hashlib, struct
p=argparse.ArgumentParser(description='Classified bias list and legacy list produce identical tiny masters; no observations')
p.add_argument('--command',type=Path,required=True)
p.add_argument('--work-parent',type=Path,required=True)
a=p.parse_args()
root=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(root/'Pycavi2/tests'),str(root/'Pycavi2/pycavi/pycavi')]
from linearity_preparation_fixture import fixture
work=Path(tempfile.mkdtemp(prefix='bias-list-contract-',dir=a.work_parent))
s=fixture(work,separated=True)
from linearity_files_contract import plane
for i,b in enumerate(s['biases']):
    data=[]
    for y in range(4):data += [10+10*y+20*i]+[15+10*y+21*i]*6+[14+10*y+20*i]
    Path(b['path']).write_bytes(plane(data,8,4,extra=[('EXPTIME','0'),('MJD-OBS','60000.0'),('ORIGFILE',"'bias.fits'")],detector='ESO_CCD_#65',amplifier='L'))
orch=s['work'];reduced=s['reduced']
for n in ['work','logs']:(reduced/n).mkdir()
proj=(root/'docs/architecture/proposed/m2/project-contracts/examples/omegacam.toml').read_text().replace('project_schema_version = 1','project_schema_version = 2',1)
for k,v in dict(raw=s['raw'],calibration=reduced/'cal',output=reduced,work=reduced/'work',logs=reduced/'logs').items():proj=proj.replace('"review locations/'+k+'"',json.dumps(str(v)))
proj=proj.replace('"../../examples/omegacam/full.toml"',json.dumps(str(orch/'native.toml')))
(orch/'project.toml').write_text(proj)
(reduced/'cal/bias/new').mkdir()
(orch/'bias.list').write_text(''.join(Path(b['path']).name+'\tBIAS\n' for b in s['biases']))
text='''bias_recipe_schema_version=1
project="project.toml"
settings="native.toml"
run="cal/bias/new"
[inputs]
list="bias.list"
[bias]
median_even_handling="average"
qc="legacy"
mad=false
readout_id="OMEGACAM:normal:ordered:1x1"
bin_x=1
bin_y=1
input_bpm="omitted"
amplifier_id="L"
[[detector]]
id="ESO_CCD_#65"
configuration_detector=0
hdus=[0]
'''
(orch/'bias.toml').write_text(text)
def execute(recipe, *extra):
    return subprocess.run([str(a.command.resolve()),'cal','bias','--config',str(recipe),*extra],cwd=orch,text=True,capture_output=True)

before={b['path']:hashlib.sha256(Path(b['path']).read_bytes()).hexdigest() for b in s['biases']}
result=execute(orch/'bias.toml')
assert result.returncode==0,result.stdout+result.stderr
product=next((reduced/'cal/bias/new').glob('*.fits'))
# Independent FITS block reader: compare stored image bytes, not time/header labels.
def image_payloads(path):
    data=path.read_bytes(); offset=0; output=[]
    while offset<len(data):
        cards={}; position=offset
        while True:
            card=data[position:position+80].decode('ascii');position+=80
            if card[:8].strip()=='END':break
            if card[8:10]=='= ':cards[card[:8].strip()]=card[10:].split('/')[0].strip()
        offset=((position+2879)//2880)*2880
        rank=int(cards['NAXIS']); count=1 if rank else 0
        for axis in range(rank):count*=int(cards['NAXIS'+str(axis+1)])
        size=count*abs(int(cards['BITPIX']))//8
        if count:output.append((cards['BITPIX'],data[offset:offset+size]))
        offset+=((size+2879)//2880)*2880
    return output
planes=image_payloads(product)
assert len(planes)==1 and planes[0][0]=='-32'
assert set(struct.unpack('>'+str(len(planes[0][1])//4)+'f',planes[0][1]))=={7.5}
legacy=reduced/'cal/bias/legacy';legacy.mkdir()
(orch/'old.list').write_text(''.join(b['path']+'\n' for b in s['biases']))
old='\n'.join(line for line in text.splitlines() if not line.startswith(('project=','run=','[inputs]','list=')))+'\n'
(orch/'legacy.toml').write_text(old)
result=execute(orch/'legacy.toml','--bias',str(orch/'old.list'),'--output-dir',str(legacy))
assert result.returncode==0,result.stdout+result.stderr
assert image_payloads(next(legacy.glob('*.fits')))==planes
for label,listing in [('wrong-class',Path(s['biases'][0]['path']).name+'\tFLAT,LAMP\n'),
                       ('duplicate',Path(s['biases'][0]['path']).name+'\tBIAS\n'+Path(s['biases'][0]['path']).name+'\tBIAS\n'),
                       ('missing-class',Path(s['biases'][0]['path']).name+'\n')]:
    target=reduced/('cal/bias/'+label);target.mkdir()
    (orch/(label+'.list')).write_text(listing)
    (orch/(label+'.toml')).write_text(text.replace('cal/bias/new','cal/bias/'+label).replace('list="bias.list"','list="'+label+'.list"'))
    result=execute(orch/(label+'.toml'))
    assert result.returncode!=0 and not list(target.rglob('*.fits')),label
assert before=={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in before}
print('PASS: classified and legacy bias lists, exact 7.5 ADU master pixels; malformed/duplicate/wrong-class refused; inputs unchanged')
print('RETAINED',work)
