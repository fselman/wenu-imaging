"""Native command end to end with explicit plans and existing tiny FITS fixtures."""
import argparse
import csv
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile
from linearity_files_contract import fixture

def options(kind):
    return dict(detector='D',amplifier='OUT1',slot='0',readout='WFI:test',identity_key='DETID',
        amplifier_key='AMPID',bin_x_key='XBINNING',bin_y_key='YBINNING',bin_x='1',bin_y='1',
        mask_encoding='omitted' if not kind else 'reason8' if kind==1 else 'binary',good_value='1' if kind==3 else '0',
        mask_registry='WENU_BPM_V1',reject_bits='255',saturation='1000',tolerance='0',
        max_pixels='1000',max_rows='4',exposure_key='EXPTIME',exposure_hdu='0',with_mad='1',
        schema='raw-pair-plan-v1',crop='2,5,2,3',raw_width='6',raw_height='4')

def write_plan(path,directory,kind,changes=(),append=''):
    settings=options(kind);settings.update(changes)
    text=''.join(k+'\t'+str(v)+'\n' for k,v in settings.items())
    for i,(hdu,pair) in enumerate([(0,'P0'),(2,'P1'),(0,'P1'),(2,'P0')]):
        text+=f'flat\t{directory/f"flat-{i}.fits"}\t{hdu}\tflat:{i}\t{i}\t{pair}\n'
    for i in range(2):text+=f'bias\t{directory/f"raw-bias-{i}.fits"}\t0\tbias:{i}\n'
    if kind:text+=f'bpm\t{directory/"bpm.fits"}\t0\tbpm:selected\n'
    path.write_text(text+append)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--command',required=True)
    p.add_argument('--paf',required=True,type=Path)
    p.add_argument('--work-parent',required=True,type=Path)
    a=p.parse_args();a.work_parent.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix='pair-command-',dir=a.work_parent));print('RETAINED COMMAND TEST:',work,flush=True)
    paf=work/'tiny.paf';text=a.paf.read_text()
    for field,value in [('X.MIN',2),('X.MAX',5),('Y.MIN',2),('Y.MAX',3)]:
        text,n=re.subn(r'(^MEF\.CROP\.'+re.escape(field)+r'\.CHIP1\s+)\d+;',r'\g<1>'+str(value)+';',text,flags=re.M);assert n==1
    paf.write_text(text)
    roi=work/'selected.toml';roi.write_text('roi_schema_version = 1\n'+''.join(
        f'\n[[roi]]\nid = "R{i}"\ndetector = "D"\namplifier = "OUT1"\nxmin = {i+1}\nxmax = {i+2}\nymin = 1\nymax = 2\n' for i in range(2)))
    for kind in range(4):
        directory=work/f'input-{kind}';fixture(directory,kind,'measure');(directory/'bias.fits').unlink()
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.fits')}
        plan=work/f'plan-{kind}.tsv';write_plan(plan,directory,kind)
        out=work/f'output-{kind}';out.mkdir()
        r=subprocess.run([a.command,str(paf),str(roi),str(plan),str(out)],capture_output=True,text=True)
        (work/f'command-{kind}.log').write_text(r.stdout+r.stderr)
        if r.returncode:raise RuntimeError(r.stdout[-2000:]+r.stderr[-4000:])
        assert (out/'command.complete').read_text()=='raw_pair_tables_complete\n'
        assert (out/'configuration.json').stat().st_size>0
        with (out/'pairs.tsv').open(newline='') as stream:rows=list(csv.DictReader(stream,delimiter='\t'))
        with (out/'bias-ron.tsv').open(newline='') as stream:ron=list(csv.DictReader(stream,delimiter='\t'))
        assert len(rows)==4 and len(ron)==2 and rows[0]['second_hdu']=='2'
        assert [r['pair_id'] for r in rows]==['P0','P0','P1','P1']
        assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.fits')}
        saved={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
        r=subprocess.run([a.command,str(paf),str(roi),str(plan),str(out)],capture_output=True,text=True)
        assert r.returncode and saved=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
    directory=work/'input-1'
    cases=[('negative',[('slot','-1')],''),('overflow',[('max_pixels','999999999999999999999999999999999')],''),
        ('nan',[('saturation','nan')],''),('missing',[],''),('duplicate',[],'detector\tD\n'),
        ('unknown',[],'typo\t1\n'),('blank',[],'\nignored\t1\n'),('crop',[('crop','1,4,2,3')],''),
        ('shape',[('raw_height','5')],''),('mask',[('mask_encoding','omitted')],''),('roi',[('amplifier','OTHER')],'')]
    for name,changes,append in cases:
        plan=work/f'bad-{name}.tsv';write_plan(plan,directory,1,changes,append)
        if name=='missing':plan.write_text(plan.read_text().replace('saturation\t1000\n',''))
        out=work/f'bad-output-{name}';out.mkdir()
        r=subprocess.run([a.command,str(paf),str(roi),str(plan),str(out)],capture_output=True,text=True)
        (work/f'bad-{name}.log').write_text(r.stdout+r.stderr)
        assert r.returncode and not (out/'command.complete').exists(),name
        assert not list(out.iterdir()),name
    print('PASS: 4 complete mask modes, repeated-output preservation and 11 rejected plans')

if __name__=='__main__':main()
