"""Synthetic named ROI configuration; no FITS, engine execution or installation."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--probe', required=True)
p.add_argument('--work-parent', type=Path, required=True)
a = p.parse_args()
work = Path(tempfile.mkdtemp(prefix='roi-config-', dir=a.work_parent))
print('RETAINED ROI CONFIG TEST:', work, flush=True)
entries = [dict(id='CHIP1.center', detector='CHIP1', amplifier='OUT1', xmin=1, xmax=40, ymin=1, ymax=60),
           dict(id='CHIP1.overlap', detector='CHIP1', amplifier='OUT1', xmin=30, xmax=80, ymin=10, ymax=60),
           dict(id='CHIP8.center', detector='CHIP8', amplifier='OUT1', xmin=10, xmax=70, ymin=20, ymax=80)]
paf_names = dict(id='ID', detector='DETECTOR', amplifier='AMPLIFIER', xmin='X.MIN', xmax='X.MAX', ymin='Y.MIN', ymax='Y.MAX')
def render(fmt, rows):
    if fmt == 'toml':
        return 'roi_schema_version = 1\n' + ''.join('\n[[roi]]\n' + ''.join(
            f'{k} = "{v}"\n' if isinstance(v, str) else f'{k} = {v}\n' for k, v in e.items()) for e in rows)
    return 'PAF.HDR.START;\nPAF.HDR.END;\nMEF.ROI.VERSION 1;\nMEF.ROI.COUNT ' + str(len(rows)) + ';\n' + ''.join(
        f'MEF.ROI.{i}.{paf_names[k]} "{v}";\n' if isinstance(v, str) else f'MEF.ROI.{i}.{paf_names[k]} {v};\n'
        for i, e in enumerate(rows, 1) for k, v in e.items())
def run(fmt, label, text, mode):
    path = work / f'{label}.{fmt}'
    path.write_text(text)
    return subprocess.check_output([a.probe, fmt, str(path), mode], text=True)
outputs=[]
for fmt in ('paf', 'toml'):
    # Equivalent explicit configurations, ownership faults and atomic binding.
    text=render(fmt, entries)
    outputs.append(run(fmt, 'valid', text, 'accept'))
    eso_rows=[dict(e, detector='ESO_CCD_#96' if i==2 else 'ESO_CCD_#65',
                   amplifier='R' if i==2 else 'L') for i,e in enumerate(entries)]
    assert run(fmt, 'eso-identities', render(fmt, eso_rows), 'eso').strip() == 'ESO # identities preserved and bound'
    changes = [('duplicate_id', 1, 'id', 'CHIP1.center'), ('reverse_bounds', 0, 'xmax', 0),
               ('zero_origin', 0, 'xmin', 0), ('fractional', 0, 'xmin', 1.5),
               ('empty_id', 0, 'id', ''), ('long_id', 0, 'id', 'x'*64),
               ('detector_space', 0, 'detector', 'ESO CCD'), ('detector_path', 0, 'detector', '../CCD/65')]
    for label, index, field, value in changes:
        rows = [dict(e) for e in entries]; rows[index][field] = value
        run(fmt, label, render(fmt, rows), 'reject')
    # Unknown and duplicate definitions must not be silently ignored.
    extra = '\nunknown = 3\n' if fmt == 'toml' else '\nMEF.ROI.1.UNKNOWN 3;\n'
    run(fmt, 'unknown', text+extra, 'reject')
    extra = '\nxmin = 3\n' if fmt == 'toml' else '\nMEF.ROI.1.X.MIN 3;\n'
    run(fmt, 'duplicate_key', text+extra, 'reject')
    run(fmt, 'missing', text.replace('ymax = 80', 'missing = 80') if fmt == 'toml'
        else text.replace('MEF.ROI.3.Y.MAX 80;', ''), 'reject')
    run(fmt, 'version', text.replace('version = 1', 'version = 2') if fmt == 'toml'
        else text.replace('VERSION 1;', 'VERSION 2;'), 'reject')
    run(fmt, 'nul', text+'\0', 'reject')
assert outputs[0] == outputs[1]
assert outputs[0].splitlines() == ['CHIP1.center CHIP1 OUT1 1 40 1 60',
    'CHIP1.overlap CHIP1 OUT1 30 80 10 60', 'CHIP8.center CHIP8 OUT1 10 70 20 80']
print('PAF/TOML equivalence, identity binding, atomic errors, ownership and strict schema passed')
