"""Bounded raw-only FITS admission: reuse tiny fixtures, never a master/sample pass."""
import argparse
import csv
import hashlib
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
from linearity_files_contract import fixture,plane

p=argparse.ArgumentParser()
p.add_argument('--probe',required=True)
p.add_argument('--paf',required=True)
p.add_argument('--work-parent',type=Path,required=True)
a=p.parse_args();a.work_parent.mkdir(parents=True,exist_ok=True)
work=Path(tempfile.mkdtemp(prefix='linearity-raw-files-',dir=a.work_parent))
print('RETAINED RAW FILE TEST:',work,flush=True)
cases=[(kind,'normal') for kind in range(4)]+[(1,c) for c in
 ('missing','duplicate','amplifier','pair_time','tolerant','hdu','readout','pair_id','registry','limit','rows','alias','flat_alias','roi','pointer')]+[(2,'badmask')]
for kind,case in cases:
    directory=work/f'{kind}-{case}';fixture(directory,kind,'measure')
    if case in ('missing','duplicate','amplifier','pair_time','tolerant'):
        changed=work/f'changed-{case}';fixture(changed,kind,case)
        for src in changed.glob('flat-*.fits'):shutil.copyfile(src,directory/src.name)
    if case=='badmask':
        (directory/'bpm.fits').write_bytes(plane([2]*8,4,2,byte=True,mask=True))
    # Proof that the raw-only path neither needs nor loads the existing master.
    (directory/'bias.fits').unlink()
    before={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in directory.glob('*.fits')}
    run=subprocess.run([a.probe,a.paf,str(directory),str(kind),case],capture_output=True,text=True)
    (directory/'probe.log').write_text(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'{kind}/{case}: '+run.stdout[-2000:]+run.stderr[-4000:])
    assert before=={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in directory.glob('*.fits')}
    if case in ('normal','tolerant'):
        with (directory/'pairs.tsv').open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
        assert len(rows)==4 and rows[0]['first_hdu']=='0' and rows[0]['second_hdu']=='2'
        assert math.isclose(float(rows[0]['mean_signal_adu']),225+1/6 if kind else 222.5,abs_tol=1e-9) # Raw signal, not scan-corrected 200.
        assert [r['pair_id'] for r in rows]==['P0','P0','P1','P1']
print(f'PASS: {len(cases)} raw-only FITS cases, immutable sources and table export')
