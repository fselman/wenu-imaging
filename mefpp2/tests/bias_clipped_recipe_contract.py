"""Tiny native bias products with shared BPM policy and optional clipping.
Runs with Astropy; native C writes products, a separate ASDF interpreter verifies.
"""
import argparse
import json
from pathlib import Path
import subprocess
import numpy as np
from astropy.io import fits
import bias_recipe_contract as old
from bias_qc_fits_contract import is_addition

p = argparse.ArgumentParser(description=__doc__)
for key in ('work', 'recipe', 'adapter', 'asdf-python'):
    p.add_argument('--' + key, type=Path, required=True)
p.add_argument('--revision', required=True)
a = p.parse_args()
a.work = a.work.resolve()
a.work.mkdir()
a.recipe = a.recipe.resolve(strict=True)
a.adapter = a.adapter.resolve(strict=True)
a.asdf_python = old.interpreter_path(a.asdf_python)
a.reuse_omissions = False
old.ARGS = a
old.WORK = a.work
old.RecipeTests.setUpClass()
case = old.RecipeTests('test_explicit_omissions_and_toml')
base = case.toml.read_text()
products = []
for label, encoding, bad, enabled in [('one-good', 'binary', 'zero', True),
                                     ('zero-good', 'binary', 'nonzero', True),
                                     ('reason8', 'reason8', 'nonzero', True),
                                     ('disabled', 'binary', 'zero', False)]:
    maskfile = a.work / (label + '-mask.fits')
    with fits.open(case.bpm, memmap=False) as h:
        for ext in h[1:]:
            if bad == 'nonzero':
                ext.data = (ext.data == 0).astype(np.uint8)
            if encoding == 'reason8':
                defects = np.flatnonzero(ext.data)
                ext.data.flat[defects] = np.array([2, 128], dtype=np.uint8)
                ext.header['MASKENC'] = 'REASON8'
                ext.header['MASKREG'] = 'WENU_BPM_V1'
        h.writeto(maskfile)
    extra = f'\n"BPM.ENCODING"="{encoding}"\n"BPM.BAD_WHEN"="{bad}"\n'
    if encoding == 'reason8':
        extra += '"BPM.REJECT_BITS"=255\n"BPM.REGISTRY"="WENU_BPM_V1"\n'
    extra += f'"QC.RON.CLIP.ENABLED"={int(enabled)}\n"QC.RON.CLIP.LOW"=5.0\n"QC.RON.CLIP.HIGH"=5.0\n"QC.RON.CLIP.MAX_ITERATIONS"=10\n'
    settings = a.work / (label + '-settings.toml')
    settings.write_text(base + extra)
    cfg = a.work / (label + '.toml')
    text = 'bias_recipe_schema_version=1\nsettings=' + json.dumps(str(settings)) + '\n[bias]\nmad=true\nron_pair=[0,3]\nhigh_sigma=5.0\nreadout_id="synthetic-readout"\nbin_x=1\nbin_y=1\ninput_bpm=' + json.dumps(str(maskfile)) + '\nbpm_coordinates="active"\namplifier_id="explicit"\n'
    for i, identity in enumerate(old.IDS):
        text += f'[[detector]]\nid="{identity}"\nconfiguration_detector={i}\nhdus=[{i+1}]\nbpm_hdu={i+1}\n'
    cfg.write_text(text)
    out = case.destination(label)
    command = [str(a.recipe), 'cal', 'bias', '--config', str(cfg), '--bias', str(case.listing), '--output-dir', str(out)]
    case.run_recipe(command, label, True)
    product = next(out.glob('*.fits'))
    expected = {'recipe_path': str(cfg), 'recipe_snapshot': text, 'revision': a.revision, 'enabled': enabled, 'registry': 'WENU_BPM_V1' if encoding == 'reason8' else None,
                'policy': {}, 'detectors': []}
    import tomllib
    policy = tomllib.loads(settings.read_text())['native']
    for k, v in policy.items():
        if k.startswith(('BPM.', 'QC.RON.CLIP.')):
            import struct
            expected['policy'][k] = {'type': 'string' if isinstance(v, str) else 'int' if isinstance(v, int) else 'float64-bits',
                                     'value': struct.pack('>d', v).hex() if isinstance(v, float) else v}
    with fits.open(product, memmap=False) as h, fits.open(case.bpm, memmap=False) as masks:
        for i, identity in enumerate(old.IDS):
            with fits.open(case.references['masked'][i], memmap=False) as ref:
                assert h[i+1].data.tobytes() == ref[1].data.tobytes()
                for card in ref[1].header.cards:
                    if card.keyword.startswith('ESO MPP QC ') and not is_addition(card.keyword):
                        assert h[i+1].header[card.keyword] == card.value
            with fits.open(case.members[0], memmap=False) as first, fits.open(case.members[3], memmap=False) as second:
                region = [policy[f'MEF.CROP.{axis}.{bound}.CHIP{i+1}'] for axis, bound in [('X','MIN'),('X','MAX'),('Y','MIN'),('Y','MAX')]]
                x1, x2, y1, y2 = region
                d = first[i+1].data.astype(np.float32) - second[i+1].data.astype(np.float32)
                d = d[y1-1:y2, x1-1:x2]
                good = masks[i+1].data != 0
                v = d[good].astype(np.float64)
            nlow = nhigh = iterations = 0
            converged = False
            while len(v) > 1 and iterations < 10:
                iterations += 1
                med = float(np.median(v))
                scale = float(np.std(v, ddof=1))
                lo, hi = med - 5*scale, med + 5*scale
                nlow += int(np.count_nonzero(v < lo)); nhigh += int(np.count_nonzero(v > hi))
                keep = (v >= lo) & (v <= hi)
                if keep.all():
                    converged = True
                    break
                v = v[keep]
            assert converged
            values = {'read_noise.clipped': float(np.std(v, ddof=1)/np.sqrt(2)), 'ron_clip.mean': float(np.mean(v)),
                      'ron_clip.median': float(np.median(v)), 'ron_clip.stdev': float(np.std(v, ddof=1)),
                      'ron_clip.retained': len(v), 'ron_clip.rejected_low': nlow, 'ron_clip.rejected_high': nhigh,
                      'ron_clip.bpm_excluded': int(good.size - np.count_nonzero(good)), 'ron_clip.nonfinite_excluded': 0,
                      'ron_clip.iterations': iterations, 'ron_clip.converged': 1,
                      'ron_clip.sigma_low': 5, 'ron_clip.sigma_high': 5, 'ron_clip.max_iterations': 10}
            expected['detectors'].append({'id': identity, 'clipped': values,
                'header': {k: value for k, value in h[i+1].header.items() if is_addition(k)}})
    expected_path = a.work / (label + '-expected.json')
    expected_path.write_text(json.dumps(expected, indent=2))
    with (a.work / (label + '-asdf.log')).open('x') as log:
        subprocess.run([str(a.asdf_python), '-B', str(old.ROOT/'mefpp2/tests/bias_clipped_asdf_verify.py'),
            '--file', str(product.with_suffix('.asdf')), '--schema', str(old.ROOT/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json'),
            '--expected', str(expected_path)], check=True, timeout=60, stdout=log, stderr=subprocess.STDOUT)
    assert 'xmem:' not in (a.work/(label+'.console.log')).read_text()
    products.append(str(product))
    # An explicit legacy detector polarity cannot override the shared choice.
    conflict = text.replace('bpm_coordinates="active"', 'bpm_coordinates="active"\nbpm_good_value=' + ('1' if bad == 'nonzero' else '0'))
    conflict_path = a.work / (label + '-conflict.toml')
    conflict_path.write_text(conflict)
    command[4] = str(conflict_path)
    refusal = case.destination(label + '-conflict')
    command[-1] = str(refusal)
    case.run_recipe(command, label + '-conflict', False)
    assert not list(refusal.iterdir())
assert case.frozen == {path: old.digest(Path(path)) for path in case.frozen}
(a.work/'results.json').write_text(json.dumps({'successful': True, 'products': products, 'policy_conflicts_refused': 4,
    'observational_raws_read': False, 'source_revision': a.revision}, indent=2) + '\n')
print('PASS: four tiny actual products, exact legacy pixels/QC, independent clipped RON/ASDF/FITS policy checks and four conflicts')
