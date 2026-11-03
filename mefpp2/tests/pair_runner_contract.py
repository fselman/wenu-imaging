"""One-detector orchestration around the real native command, on tiny FITS only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from linearity_files_contract import fixture

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--command',required=True)
p.add_argument('--runner',type=Path,required=True)
p.add_argument('--paf',type=Path,required=True)
p.add_argument('--work-parent',type=Path,required=True)
a=p.parse_args();a.work_parent.mkdir(parents=True,exist_ok=True)
work=Path(tempfile.mkdtemp(prefix='pair-runner-',dir=a.work_parent));print('RETAINED RUNNER TEST:',work,flush=True)
data=work/'inputs';fixture(data,3,'measure');(data/'bias.fits').unlink()
config=work/'tiny.paf';text=a.paf.read_text()
for key,value in [('X.MIN',2),('X.MAX',5),('Y.MIN',2),('Y.MAX',3)]:
    text,n=re.subn(r'(^MEF\.CROP\.'+re.escape(key)+r'\.CHIP1\s+)\d+;',r'\g<1>'+str(value)+';',text,flags=re.M);assert n==1
config.write_text(text)
detectors=work/'detectors.toml';detectors.write_text('''footprint_schema_version=1
instrument="test"
binning=[1,1]
[[detector]]
id="D"
amplifier="OUT1"
native_paf_chip=1
reference_hdu=0
mosaic_column=1
mosaic_row=1
raw_size=[6,4]
illuminated=[2,5,2,3]
prescan=[1,1,1,4]
overscan=[6,6,1,4]
amplifier_corner="lower-left"
''')
processing=work/'processing.toml';processing.write_text('''processing_footprint_schema_version=1
instrument="test"
roi_coordinates="retained-active"
source_paf_sha256="'''+hashlib.sha256(config.read_bytes()).hexdigest()+'''"
[[trim]]
detector="D"
retained=[2,5,2,3]
prescan_sample=[1,1,1,4]
overscan_sample=[6,6,1,4]
[[roi]]
id="center"
detector="D"
amplifier="OUT1"
xmin=1
xmax=2
ymin=1
ymax=2
''')
selection=work/'selection.toml'
s='''selection_schema_version=1
detector="D"
readout_id="WFI:test"
bin_x=1
bin_y=1
raw_saturation_adu=1000
pair_time_tolerance_s=0
max_loaded_pixels=1000
max_rows=2
with_mad=true
reject_bits=255
exposure_hdu=0
[header_keys]
identity="DETID"
amplifier="AMPID"
bin_x="XBINNING"
bin_y="YBINNING"
exposure="EXPTIME"
'''
for i,(hdu,pair) in enumerate([(0,'P0'),(2,'P1'),(0,'P1'),(2,'P0')]):
    s+=f'\n[[flat]]\npath={json.dumps(str(data/f"flat-{i}.fits"))}\nhdu={hdu}\nasset="F{i}"\nindex={i}\npair="{pair}"\n'
for i in range(2):s+=f'\n[[bias]]\npath={json.dumps(str(data/f"raw-bias-{i}.fits"))}\nhdu=0\nasset="B{i}"\n'
s+=f'\n[bpm]\nencoding="binary"\ngood_value=1\npath={json.dumps(str(data/"bpm.fits"))}\nhdu=0\nasset="BPM"\n'
selection.write_text(s)
base=[sys.executable,'-B',str(a.runner),'--detectors',str(detectors),'--processing',str(processing),
      '--selection',str(selection),'--native-paf',str(config),'--command',a.command,'--source-revision','1'*40]
for execute in (False,True):
    run=work/('execute' if execute else 'prepare');run.mkdir()
    result=subprocess.run(base+['--run',str(run)]+(['--execute'] if execute else []),capture_output=True,text=True)
    (work/f'{run.name}.log').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(result.stdout[-2000:]+result.stderr[-4000:])
    receipt=json.loads((run/'execution.json').read_text())
    assert receipt['status']==('complete_for_owner_inspection' if execute else 'prepared_not_executed')
    assert receipt['source_preservation'] and (run/'README.md').is_file()
    assert (run/'native').exists()==execute
    if execute:assert receipt['output_rows']=={'pairs.tsv':2,'bias-ron.tsv':1}
# A stale crop profile fails without numerical execution and retains a failed receipt.
config.write_text(config.read_text()+'\n# intentional mismatch\n')
run=work/'failed';run.mkdir()
r=subprocess.run(base+['--run',str(run),'--execute'],capture_output=True,text=True)
assert r.returncode and json.loads((run/'execution.json').read_text())['status']=='failed'
assert not (run/'native').exists() and (run/'README.md').exists()
print('PASS: prepare-only, real native execution, source fingerprints, README and refused stale configuration')
