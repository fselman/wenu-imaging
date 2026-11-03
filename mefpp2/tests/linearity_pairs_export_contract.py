"""Inspect actual native TSV serialization with independent numerical expectations."""
import argparse
import csv
import math
from pathlib import Path
import subprocess
import tempfile

p=argparse.ArgumentParser()
p.add_argument('--probe',required=True)
p.add_argument('--paf',required=True)
p.add_argument('--work-parent',required=True,type=Path)
a=p.parse_args();a.work_parent.mkdir(parents=True,exist_ok=True)
work=Path(tempfile.mkdtemp(prefix='linearity-table-',dir=a.work_parent))
print('RETAINED EXPORT TEST:',work,flush=True)
for missing in (0,1):
    pairs=work/f'pairs-{missing}.tsv';bias=work/f'bias-{missing}.tsv'
    subprocess.run([a.probe,a.paf,str(pairs),str(bias),str(missing)],check=True)
    with pairs.open(newline='') as f: rows=list(csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    with bias.open(newline='') as f: ron=list(csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    assert len(rows)==2 and len(ron)==1
    for r in rows+ron:
        assert None not in r and None not in r.values()
        assert r['schema_version']=='1' and r['detector']=='ESO_CCD_#65' and r['amplifier']=='L'
        assert [r[k] for k in ('raw_xmin','raw_xmax','raw_ymin','raw_ymax')]==['2','5','2','2']
        assert int(r['valid_pixels'])+int(r['bpm_excluded'])+int(r['nonfinite_excluded'])+int(r['saturated'])==4
    assert rows[0]['first_input_index']=='10' and rows[0]['second_input_index']=='13'
    assert rows[1]['first_input_index']=='11' and rows[1]['second_input_index']=='12'
    assert rows[0]['first_asset']==r'F0\\tab\tline\n'
    if missing:
        assert rows[0]['variance_available']=='0' and rows[0]['single_flat_variance_adu2']==''
        assert rows[0]['point_gain_e_per_adu']=='' and rows[0]['gain_state']=='too_few_pixels'
        assert ron[0]['ron_available']=='0' and ron[0]['ron_adu']==''
        assert rows[0]['signal_available']=='1' # one finite pixel still has a level
    else:
        assert math.isclose(float(rows[0]['mean_signal_adu']),90)
        assert math.isclose(float(rows[0]['single_flat_variance_adu2']),4/3)
        assert math.isclose(float(rows[0]['single_bias_variance_adu2']),1/3)
        assert math.isclose(float(rows[0]['point_gain_e_per_adu']),90)
        assert math.isclose(float(ron[0]['ron_adu']),math.sqrt(1/3))
        assert rows[0]['gain_state']=='arithmetic_available'
        assert ron[0]['level_available']=='1' and float(ron[0]['difference_mean_adu'])==0
print('PASS: TSV schema, identity/order, escaped text, counts, known values and unavailable fields')
