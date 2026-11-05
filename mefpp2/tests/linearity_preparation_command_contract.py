"""New preparation CLI: independent tiny FITS, TOML and original-site replay."""
import argparse
import csv
import hashlib
import math
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Pycavi2/tests'))
from linearity_preparation_fixture import fixture,native_argv


def main():
    p=argparse.ArgumentParser();p.add_argument('--command',type=Path,required=True);p.add_argument('--work-parent',type=Path,required=True);a=p.parse_args()
    a.work_parent.mkdir(parents=True,exist_ok=True);work=Path(tempfile.mkdtemp(prefix='linearity-preparation-',dir=a.work_parent));s=fixture(work)
    print('RETAINED PREPARATION COMMAND:',work,flush=True)
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in work.glob('*.fits')}
    out=work/'native';out.mkdir();r=subprocess.run(native_argv(s,a.command,out),capture_output=True,text=True)
    (work/'native-command.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,r.stdout+r.stderr
    assert (out/'command.complete').read_text()=='linearity_preparation_complete_noise_unavailable\n'
    groups=sorted(out.glob('pair-*'));assert len(groups)==10
    for g in groups:
        with (g/'corrected.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
        with (g/'pairs.tsv').open() as f:raw=list(csv.DictReader(f,delimiter='\t'))
        assert len(rows)==5
        for row,source in zip(rows,raw):
            assert row['valid_pixels']=='12' and math.isclose(float(row['first_spatial_variance_adu2']),13.,rel_tol=4e-16)
            assert math.isclose(float(row['second_spatial_variance_adu2']),13.,rel_tol=4e-16) and float(row['difference_variance_adu2'])==0
            assert float(row['first_mean_adu'])==100*float(source['first_seconds'])+5.5
            assert float(row['second_mean_adu'])==100*float(source['second_seconds'])+5.5
        with (g/'samples.tsv').open() as f:samples=list(csv.DictReader(f,delimiter='\t'))
        assert len(samples)==10 and all(float(x['signal_adu'])==100*float(x['seconds'])+int(x['active_x'])-1 for x in samples)
    with (out/'bias-traces.tsv').open() as f:traces=list(csv.DictReader(f,delimiter='\t'))
    assert len(traces)==40 and sum(x['master_accepted']=='0' for x in traces)==4
    # A completed output is immutable and cannot be reused for another execution.
    saved={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
    r=subprocess.run(native_argv(s,a.command,out),capture_output=True,text=True);assert r.returncode
    assert saved=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
    for mode in ('wrong-master','budget','duplicate-bias'):
        target=work/('bad-'+mode);target.mkdir();argv=native_argv(s,a.command,target)
        if mode=='wrong-master':argv[6]='0'
        elif mode=='budget':
            path=work/'small-plan.tsv';path.write_text((work/'plan.tsv').read_text().replace('max_pixels\t10000','max_pixels\t1'));argv[4]=str(path)
        else:
            path=work/'duplicate-bias.tsv';data=(work/'biases.tsv').read_text().splitlines();path.write_text('\n'.join(data+[data[1]])+'\n');argv[8]=str(path)
        r=subprocess.run(argv,capture_output=True,text=True);assert r.returncode and not (target/'command.complete').exists()
    assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in work.glob('*.fits')}
    print('PASS: 20 shuffled-HDU/nonconsecutive flats, 10 biases including rejection, 100 direct sites, ROI moments, trace order and 4 conflict/output refusals')


if __name__=='__main__':main()
