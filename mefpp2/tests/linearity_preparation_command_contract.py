"""New preparation CLI: independent tiny FITS, TOML and original-site replay."""
import argparse
import csv
import hashlib
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Pycavi2/tests'))
from linearity_preparation_fixture import fixture,native_argv


def main():
    p=argparse.ArgumentParser();p.add_argument('--command',type=Path,required=True);p.add_argument('--work-parent',type=Path,required=True);a=p.parse_args()
    a.command = a.command.resolve(strict=True)
    a.work_parent.mkdir(parents=True,exist_ok=True);work=Path(tempfile.mkdtemp(prefix='linearity-preparation-',dir=a.work_parent)).resolve();s=fixture(work,separated=True)
    orchestration, raw_directory, reduced = s['work'], s['raw'], s['reduced']
    os.chdir(orchestration)
    print('RETAINED PREPARATION COMMAND:',work,flush=True)
    inputs = [*raw_directory.glob('*.fits'), Path(s['master']), Path(s['selection']['bpm']['path'])]
    for path in inputs:
        path.chmod(0o444)
    raw_directory.chmod(0o555)
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    out=reduced/'cal/bpm-linearity/native';out.mkdir(parents=True);r=subprocess.run(native_argv(s,a.command,out),capture_output=True,text=True)
    (reduced/'native-command.log').write_text(r.stdout+r.stderr)
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
        target=reduced/('bad-'+mode);target.mkdir();argv=native_argv(s,a.command,target)
        if mode=='wrong-master':argv[6]='0'
        elif mode=='budget':
            path=orchestration/'small-plan.tsv';path.write_text((orchestration/'plan.tsv').read_text().replace('max_pixels\t10000','max_pixels\t1'));argv[4]=str(path)
        else:
            path=orchestration/'duplicate-bias.tsv';data=(orchestration/'biases.tsv').read_text().splitlines();path.write_text('\n'.join(data+[data[1]])+'\n');argv[8]=str(path)
        r=subprocess.run(argv,capture_output=True,text=True);assert r.returncode and not (target/'command.complete').exists()
    assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    assert len(list(raw_directory.iterdir())) == 30 and not list(orchestration.glob('*.fits'))
    assert Path.cwd() == orchestration
    print('PASS: orchestration cwd; read-only raw/calibration inputs preserved; outputs and logs under reduced')
    print('PASS: 20 shuffled-HDU/nonconsecutive flats, 10 biases including rejection, 100 direct sites, ROI moments, trace order and 4 conflict/output refusals')


if __name__=='__main__':main()
