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
    Path(b['path']).write_bytes(plane(data,8,4,extra=[('EXPTIME','0'),('MJD-OBS','60000.0'),('ORIGFILE',"'bias.fits'"),('EXTNAME',"'ESO_CCD_#65'")],detector='ESO_CCD_#65',amplifier='L'))
orch=s['work'];reduced=s['reduced']
for n in ['work','logs']:(reduced/n).mkdir()
proj=(root/'docs/architecture/proposed/m2/project-contracts/examples/omegacam.toml').read_text().replace('project_schema_version = 1','project_schema_version = 2',1)
for k,v in dict(raw=s['raw'],calibration=reduced/'cal',output=reduced,work=reduced/'work',logs=reduced/'logs').items():proj=proj.replace('"review locations/'+k+'"',json.dumps(str(v)))
proj=proj.replace('"../../examples/omegacam/full.toml"',json.dumps(str(orch/'native.toml')))
(orch/'project.toml').write_text(proj)
(reduced/'cal/bias/new').mkdir()
list_dir = reduced/'cal/sof'
list_dir.mkdir()
listing = list_dir/'bias.list'
paths = [b['path'] for b in s['biases']]
rows = [path+'\tBIAS\n' for path in paths]
listing.write_text(''.join(rows))
text='''bias_recipe_schema_version=1
project="project.toml"
settings="native.toml"
run="cal/bias/new"
[inputs]
list=LIST_PATH
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
(orch/'bias.toml').write_text(text.replace('LIST_PATH', json.dumps(str(listing))))
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
# The recipe inherits detector identity and HDU from the shared profile.
(orch / "detector.toml").write_text("""
footprint_schema_version = 1
readout_id = "OMEGACAM:normal:ordered:1x1"
binning = [1, 1]

[[detector]]
id = "ESO_CCD_#65"
native_paf_chip = 1
reference_hdu = 0
enabled = true

[[detector]]
id = "ESO_CCD_#66"
native_paf_chip = 2
enabled = false
""")
shared = reduced / "cal/bias/shared"
shared.mkdir()
shared_config = orch / "shared.toml"
shared_text = text.split("[[detector]]", 1)[0]
shared_text = "\n".join(
    line for line in shared_text.splitlines()
    if not line.startswith(("readout_id=", "bin_x=", "bin_y="))
) + "\n"
shared_config.write_text(
    shared_text.replace("cal/bias/new", "cal/bias/shared")
    .replace("[inputs]", 'detector_toml="detector.toml"\n[inputs]')
    .replace("LIST_PATH", json.dumps(str(listing)))
)
result = execute(shared_config)
assert result.returncode == 0, result.stdout + result.stderr
assert image_payloads(next(shared.glob("*.fits"))) == planes
result = execute(shared_config, "--detectors", "ESO_CCD_#66")
assert result.returncode != 0 and "disabled" in result.stderr, result.stderr
print("PASS: shared detector defaults preserve pixels and exclude disabled detectors")

legacy=reduced/'cal/bias/legacy';legacy.mkdir()
(orch/'old.list').write_text(''.join(b['path']+'\n' for b in s['biases']))
old='\n'.join(line for line in text.splitlines() if not line.startswith(('project=','run=','[inputs]','list=')))+'\n'
(orch/'legacy.toml').write_text(old)
result=execute(orch/'legacy.toml','--bias',str(orch/'old.list'),'--output-dir',str(legacy))
assert result.returncode==0,result.stdout+result.stderr
assert image_payloads(next(legacy.glob('*.fits')))==planes
cases = [
    ('wrong-class', [paths[0]+'\tFLAT,LAMP\n', *rows[1:]], False, 'DPR.TYPE BIAS only'),
    ('duplicate', [*rows, rows[0]], False, 'Invalid observation list'),
    ('missing-class', [paths[0]+'\n', *rows[1:]], False, 'Invalid observation list'),
    ('relative-fits', [Path(paths[0]).name+'\tBIAS\n', *rows[1:]], False, 'observation path must be absolute'),
    ('relative-list', rows, True, 'inputs.list requires an absolute path'),
]
for label, members, relative, message in cases:
    target = reduced/('cal/bias/'+label)
    target.mkdir()
    case_list = orch/(label+'.list')
    case_list.write_text(''.join(members))
    list_path = case_list.name if relative else str(case_list)
    config = orch/(label+'.toml')
    config.write_text(text.replace('cal/bias/new', 'cal/bias/'+label)
                      .replace('LIST_PATH', json.dumps(list_path)))
    result = execute(config)
    assert result.returncode != 0 and message in result.stderr, (label, result.stderr)
    assert not list(target.rglob('*.fits')), label
(orch/'classified-cli.list').write_text(''.join(rows))
result = execute(orch/'legacy.toml', '--input', 'classified-cli.list', '--output-dir', str(legacy))
assert result.returncode != 0 and '--input requires an absolute path' in result.stderr, result.stderr
assert before=={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in before}
print('PASS: classified and legacy bias lists, exact 7.5 ADU master pixels; malformed/duplicate/wrong-class/relative paths refused; inputs unchanged')
print('RETAINED',work)
