"""New command integration only: singleton extraction using qualified sample kernels."""
import argparse
import csv
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile
from linearity_files_contract import fixture, plane
from layout_contract import header
from pair_command_contract import write_plan


def table(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--command', required=True)
    p.add_argument('--paf', type=Path, required=True)
    p.add_argument('--work-parent', type=Path, required=True)
    a = p.parse_args()
    work = Path(tempfile.mkdtemp(prefix='sample-command-', dir=a.work_parent))
    print('RETAINED SAMPLE COMMAND TEST:', work, flush=True)
    text = a.paf.read_text()
    changes = {'MEF.CROP.X.MIN.CHIP1': 2, 'MEF.CROP.X.MAX.CHIP1': 5,
               'MEF.CROP.Y.MIN.CHIP1': 2, 'MEF.CROP.Y.MAX.CHIP1': 3,
               'MEF.USE.PRESCAN': 1, 'MEF.USE.OVERSCAN': 1,
               'MEF.PRESCAN.X.MIN.CHIP1': 1, 'MEF.PRESCAN.X.MAX.CHIP1': 1,
               'MEF.OVERSCAN.X.MIN.CHIP1': 6, 'MEF.OVERSCAN.X.MAX.CHIP1': 6,
               'MEF.SCANREJ.MIN': 0, 'MEF.SCANREJ.MAX': 0}
    for key, value in changes.items():
        text, n = re.subn(r'(^'+re.escape(key)+r'\s+)\d+;', r'\g<1>'+str(value)+';', text, flags=re.M)
        assert n == 1, key
    paf = work/'tiny.paf'; paf.write_text(text)
    roi = work/'sites.toml'
    selected = [(1, 1), (3, 1), (2, 2)]
    def regions(points):
        return 'roi_schema_version = 1\n'+''.join(
            f'\n[[roi]]\nid = "R{i}"\ndetector = "D"\namplifier = "OUT1"\nxmin = {x}\nxmax = {x}\nymin = {y}\nymax = {y}\n'
            for i, (x, y) in enumerate(points))
    roi.write_text(regions(selected))
    def run(name, directory, plan, *, sites=roi, master=None, limit='12', hdu='0', success=True):
        out = work/name; out.mkdir()
        argv = [a.command, str(paf), str(sites), str(plan), str(master or directory/'bias.fits'), hdu,
                'master:selected', '3', limit, str(out)]
        r = subprocess.run(argv, text=True, capture_output=True)
        (work/(name+'.log')).write_text(r.stdout+r.stderr)
        if success and r.returncode:
            raise RuntimeError(name+': '+r.stdout[-1500:]+r.stderr[-4000:])
        assert (r.returncode == 0) == success, name
        assert (out/'command.complete').exists() == success, name
        return out, argv
    for kind in range(4):
        directory = work/f'input-{kind}'; fixture(directory, kind, 'normal')
        before = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in directory.iterdir()}
        plan = work/f'plan-{kind}.tsv'; write_plan(plan, directory, kind)
        text = plan.read_text()
        for original, index in enumerate([8, 3, 11, 4]):
            text = text.replace(f'flat:{original}\t{original}\t', f'flat:{original}\t{index}\t')
        plan.write_text(text)
        out, argv = run(f'output-{kind}', directory, plan)
        rows = table(out/'samples.tsv'); populations = table(out/'population.tsv')
        assert len(rows) == 12 and len(populations) == 4
        assert [int(r['input_index']) for r in rows] == [8]*3+[3]*3+[11]*3+[4]*3
        assert [r['pair_id'] for r in rows] == ['P0']*3+['P1']*6+['P0']*3
        assert [int(rows[3*f]['hdu']) for f in range(4)] == [0, 2, 0, 2]
        for i, row in enumerate(rows):
            frame = i//3; x, y = selected[i%3]
            admitted = not ((kind and (x, y) == (1, 1)) or (frame == 1 and (x, y) == (3, 1)) or (frame == 2 and (x, y) == (2, 2)))
            assert row['admission_state'] == ('admitted' if admitted else 'not_admitted')
            assert row['noise_state'] == 'unavailable'
            assert int(row['raw_x']) == x+1 and int(row['raw_y']) == y+1
            if admitted:
                assert abs(float(row['signal_adu'])-(100*float(row['seconds'])+(y-1)*4+x-1)) < 1e-4
            else:
                assert row['signal_adu'] == ''
        assert populations[1]['nonfinite'] == '1' and populations[2]['saturated'] == '1'
        assert all(sum(int(r[k]) for k in r if k != 'input_index') == 8 for r in populations)
        assert before == {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in directory.iterdir()}
        saved = {q.name: q.read_bytes() for q in out.iterdir()}
        assert subprocess.run(argv, capture_output=True).returncode != 0
        assert saved == {q.name: q.read_bytes() for q in out.iterdir()}
    directory = work/'input-3'; plan = work/'plan-3.tsv'
    duplicate = work/'duplicate.toml'; duplicate.write_text(regions([(1, 1)]*2))
    wide = work/'wide.toml'; wide.write_text(roi.read_text().replace('xmax = 1', 'xmax = 2', 1))
    run('bad-duplicate', directory, plan, sites=duplicate, success=False)
    run('bad-wide', directory, plan, sites=wide, success=False)
    run('bad-capacity', directory, plan, limit='1', success=False)
    run('bad-master', directory, plan, master=directory/'flat-0.fits', success=False)
    extension = work/'extension-master.fits'
    extension.write_bytes(header([('SIMPLE', 'T'), ('BITPIX', '8'), ('NAXIS', '0'), ('EXTEND', 'T')])
                          + plane([3]*8, 4, 2, primary=False))
    run('extension-master', directory, plan, master=extension, hdu='1')
    run('bad-master-hdu', directory, plan, master=extension, success=False)
    wrong = work/'wrong-master.fits'; wrong.write_bytes(plane([3]*8, 4, 2, detector='OTHER'))
    run('bad-identity', directory, plan, master=wrong, success=False)
    bad = work/'bad-plan.tsv'; bad.write_text(plan.read_text()+'detector\tD\n')
    run('bad-plan', directory, bad, success=False)
    # Every selected site masked: explicit empty success, no replacement site.
    (directory/'bpm.fits').write_bytes(plane([0]*8, 4, 2, byte=True, mask=True))
    out, _ = run('empty', directory, plan)
    assert len(table(out/'samples.tsv')) == 12
    assert all(r['signal_adu'] == '' and r['admission_state'] == 'not_admitted' for r in table(out/'samples.tsv'))
    print('PASS: 4 mask encodings, original frame/pair/HDU order, corrected values, explicit missing/empty samples, 7 refusals and immutable outputs/inputs')


if __name__ == '__main__':
    main()
