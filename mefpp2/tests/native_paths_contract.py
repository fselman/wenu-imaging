"""Run the real C executable against retained tiny numerical controls (#159/#163)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import warnings

from astropy.io import fits
import numpy as np
from prepare_integrated_campaign_fixture import prepare


def inventory(root):
    return {str(p.relative_to(root)): (hashlib.sha256(p.read_bytes()).hexdigest(),
                                      p.stat().st_mode, p.stat().st_mtime_ns)
            for p in sorted(root.rglob('*')) if p.is_file()}


def products(directory, calibrations=()):
    ids, result = {}, {}
    files = list(directory.glob('*.fits'))
    for p in [*calibrations, *files]:
        with fits.open(p, memmap=False) as hdus:
            if 'PRODCATG' in hdus[0].header:
                ids[hdus[0].header['ORIGFILE']] = hdus[0].header['PRODCATG']
    for p in files:
        with fits.open(p, memmap=False) as hdus:
            if 'PRODCATG' not in hdus[0].header:
                continue
            category = hdus[0].header['PRODCATG']
            assert category not in result
            result[category] = dict(name=p.name, pixels=[], headers=[])
            for hdu in hdus:
                cards = []
                for card in hdu.header.cards:
                    if isinstance(card.value, str) and card.value in ids:
                        cards.append(fits.Card(card.keyword, '@GENERATED:' + ids[card.value], card.comment).image)
                    else:
                        cards.append(card.image)
                result[category]['headers'].append(cards)
                if hdu.data is not None:
                    result[category]['pixels'].append(dict(
                        shape=list(hdu.data.shape), dtype=str(hdu.data.dtype),
                        sha256=hashlib.sha256(np.asarray(hdu.data, dtype='>f8').tobytes()).hexdigest()))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    exe, source = args.executable.resolve(strict=True), args.source_root.resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix='native explicit paths ', dir=args.work_parent)).resolve()
    original_cwd = Path.cwd()
    report = dict(status='running', executable=str(exe), commands=[], profiles=[], negatives=[])
    def save():
        (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
    def run(label, argv, caller, valid=True):
        log = work / (label + '.log')
        item = dict(label=label, argv=[str(exe), *map(str, argv)], cwd=str(caller))
        report['commands'].append(item); save()
        env = dict(os.environ, E_VERBOSE='0', E_DEBUG='0')
        env.pop('E_LOGFILE', None)
        with log.open('w') as stream:
            result = subprocess.run(item['argv'], cwd=caller, env=env,
                                    stdout=stream, stderr=subprocess.STDOUT, timeout=120)
        item['exit_status'] = result.returncode; save()
        assert (result.returncode == 0) == valid, (label, result.returncode, log)
        if not valid:
            assert result.returncode > 0, (label, 'failure must be a controlled exit', log)
        output = log.read_text(errors='replace')
        assert 'ERROR: AddressSanitizer' not in output and 'runtime error:' not in output
        assert Path.cwd() == original_cwd
        if not valid:
            report['negatives'].append(label)
        return log
    def destinations(label, paf, base):
        out, scratch = work / (label + ' output'), work / (label + ' scratch')
        out.mkdir(); scratch.mkdir()
        opts = ['--pafname', paf, '--output-dir', out, '--work-dir', scratch, '--list-base', base]
        return out, scratch, opts
    print('WORK DIRECTORY:', work, flush=True)
    try:
        # Prepare two instrument-specific tiny fixtures and run the legacy C reference.
        for instrument in ('omegacam', 'wfi'):
            root = work / instrument; root.mkdir()
            raw = root / 'raw files'
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', fits.verify.VerifyWarning)
                fixture = prepare(raw, source)
            if instrument == 'wfi':
                text = (source / 'mefpp2/ins/mef/config/wfi.paf').read_text()
                for key, value in fixture['synthetic_paf_overrides'].items():
                    text, count = re.subn(r'^' + re.escape(key) + r'\s+[^;\n]*;',
                                         key + ' ' + str(value) + ';', text, flags=re.M)
                    assert count == 1, key
                (raw / 'mefpp.paf').write_text(text)
                for p in raw.glob('*.fits'):
                    with fits.open(p, mode='update') as hdus:
                        hdus[0].header['INSTRUME'] = 'WFI'
            cfg, lists = root / 'configuration', root / 'input lists'
            cfg.mkdir(); lists.mkdir()
            paf = cfg / 'parameters.paf'; shutil.copyfile(raw / 'mefpp.paf', paf)
            for p in raw.glob('*.list'):
                shutil.copyfile(p, lists / p.name)
            legacy = root / 'legacy reference'
            shutil.copytree(raw, legacy)
            pipeline = ['--bias', 'bias.list', '--biassave', '--biassub', '--bpm', 'bpm.list',
                        '--dome', 'dome.list', '--domesave', '--sky', 'sky.list', '--skysave',
                        '--science', 'science.list']
            run(instrument + '-legacy', ['--pafname', 'mefpp.paf', *pipeline], legacy)
            reference = products(legacy)
            # Raw members in the reference directory also match *.fits: exclude them.
            reference = {k: v for k, v in reference.items() if k in (
                'CALIB.MASTER_BIAS', 'CALIB.BPM', 'CALIB.MASTER_DOME_FLAT',
                'CALIB.MASTER_SKY_FLAT', 'CALIB.MASTER_FLAT', 'SCIENCE.MEFIMAGE')}
            assert len(reference) == 6
            for p in (legacy.glob('*.fits')):
                with fits.open(p) as hdus:
                    cat = hdus[0].header.get('PRODCATG')
                    if cat not in reference:
                        continue
                    kind = ('science' if cat.startswith('SCIENCE') else 'bias' if cat.endswith('MASTER_BIAS')
                            else 'bpm' if cat == 'CALIB.BPM' else 'flat')
                    for xt in (1, 2):
                        expected = np.load(raw / f'expected-{kind}-{xt}.npy')
                        if instrument == 'wfi' and kind in ('flat', 'science'):
                            # WFI rejects 48000/52000 at its unchanged 45000 limit.
                            # Exact legacy/explicit comparison below still has no tolerance.
                            if cat == 'CALIB.MASTER_DOME_FLAT' and xt == 2:
                                expected = np.full_like(expected, 32000 / 19600)
                            assert np.allclose(hdus[xt].data, expected, rtol=1e-6, atol=0), (cat, xt)
                        else:
                            assert np.array_equal(hdus[xt].data, expected), (cat, xt)
            for directory in (raw, cfg, lists):
                for p in directory.iterdir():
                    if p.is_file(): p.chmod(0o444)
                directory.chmod(0o555)
            protected = {str(p): inventory(p) for p in (raw, cfg, lists)}
            report[instrument + '-protected-before'] = protected; save()
            # Process through the C loaders/writers from two unrelated read-only callers.
            callers = [root / 'unrelated caller A', root / 'unrelated caller B']
            for caller in callers: caller.mkdir(); caller.chmod(0o555)
            absolute_pipeline = [lists / token if token.endswith('.list') else token for token in pipeline]
            full_outputs = []
            for i, caller in enumerate(callers):
                label = instrument + '-full-' + str(i)
                out, scratch, opts = destinations(label, paf, raw)
                run(label, [*opts, *absolute_pipeline], caller)
                assert products(out) == reference
                assert not list(caller.iterdir())
                assert 'PATH final-cwd ' + str(caller) in (scratch / 'mefpp.log').read_text()
                full_outputs.append(out)
                report['profiles'].append(label)
            selected = {}
            for p in full_outputs[0].glob('*.fits'):
                with fits.open(p) as hdus: selected[hdus[0].header['PRODCATG']] = p
            calibration_args = ['--bias', selected['CALIB.MASTER_BIAS'], '--biassub',
                                '--bpm', selected['CALIB.BPM'], '--mff', selected['CALIB.MASTER_FLAT']]
            calibration_files = list(selected.values())
            for p in calibration_files: p.chmod(0o444)
            calibration_baseline = inventory(full_outputs[0])
            # Reuse explicit calibration files stored outside the caller/output directories.
            for i, caller in enumerate(callers):
                label = instrument + '-existing-calibrations-' + str(i)
                out, scratch, opts = destinations(label, paf, raw)
                run(label, [*opts, *calibration_args, '--science', lists / 'science.list'], caller)
                actual = products(out, calibration_files)
                assert actual['SCIENCE.MEFIMAGE'] == reference['SCIENCE.MEFIMAGE']
                report['profiles'].append(label)
            # The authoritative tokenizer preserves optional type columns.
            typed = root / 'typed science.list'; typed.write_text('science0.fits SCIENCE\n')
            out, _, opts = destinations(instrument + '-typed', paf, raw)
            run(instrument + '-typed', [*opts, *calibration_args, '--science', typed], callers[0])
            assert products(out, calibration_files)['SCIENCE.MEFIMAGE'] == reference['SCIENCE.MEFIMAGE']
            report['profiles'].append(instrument + '-typed')
            # Direct FITS arguments need no list base; relative CLI arguments use caller cwd.
            out, _, opts = destinations(instrument + '-direct', paf, raw)
            opts = opts[:-2]
            explicit_log = root / 'explicit processing.log'
            opts += ['--log-file', explicit_log]
            relative_paf = os.path.relpath(paf, callers[0])
            opts[1] = relative_paf
            run(instrument + '-direct', [*opts, *calibration_args, '--science', raw / 'science0.fits'], callers[0])
            assert products(out, calibration_files)['SCIENCE.MEFIMAGE'] == reference['SCIENCE.MEFIMAGE']
            report['profiles'].append(instrument + '-direct')
            assert 'PATH final-cwd ' + str(callers[0]) in explicit_log.read_text()
            # Split writes into the explicit output directory and retains raw extension pixels.
            splits = []
            for i, caller in enumerate(callers):
                label = instrument + '-split-' + str(i)
                out, _, opts = destinations(label, paf, raw)
                run(label, [*opts, '--split', lists / 'science.list'], caller)
                snapshot = {}
                for xt in (1, 2):
                    p = out / f'science0_{xt:02d}.fits'
                    with fits.open(p) as result, fits.open(raw / 'science0.fits') as original:
                        assert np.array_equal(result[0].data, original[xt].data)
                        snapshot[p.name] = [c.image for c in result[0].header.cards]
                assert len(list(out.iterdir())) == 2
                splits.append(snapshot); report['profiles'].append(label)
            assert splits[0] == splits[1]
            # Collision and missing-base/input failures must occur before products.
            duplicate = root / 'duplicate.list'; duplicate.write_text('science0.fits\nscience0.fits\n')
            absent = root / 'absent.list'; absent.write_text('missing.fits\n')
            partial = root / 'partial.list'; partial.write_text('science0.fits SCIENCE\nmissing.fits SCIENCE\n')
            collision_root = root / 'collision members'; collision_root.mkdir()
            for directory in ('one', 'two'):
                (collision_root / directory).mkdir()
                shutil.copyfile(raw / 'science0.fits', collision_root / directory / 'science0.fits')
            collision = root / 'collision.list'; collision.write_text('one/science0.fits\ntwo/science0.fits\n')
            for suffix, member, base in [('duplicate', duplicate, True), ('missing', absent, True),
                                          ('partial', partial, True), ('collision', collision, True),
                                          ('unknown-base', lists / 'science.list', False)]:
                label = instrument + '-' + suffix
                out, _, opts = destinations(label, paf, collision_root if suffix == 'collision' else raw)
                if not base: opts = opts[:-2]
                run(label, [*opts, *calibration_args, '--science', member], callers[1], valid=False)
                assert not list(out.iterdir())
            # Reject incompatible selected calibration geometry before any product publication.
            incompatible = root / 'incompatible.fits'
            with fits.open(selected['CALIB.MASTER_BIAS']) as hdus:
                hdus[1].data = np.zeros((8, 9), dtype=np.float32)
                hdus.writeto(incompatible)
            out, _, opts = destinations(instrument + '-incompatible', paf, raw)
            invalid_args = list(calibration_args); invalid_args[1] = incompatible
            run(instrument + '-incompatible', [*opts, *invalid_args, '--science', lists / 'science.list'], callers[0], valid=False)
            assert not list(out.iterdir())
            out, _, opts = destinations(instrument + '-existing-output', paf, raw)
            sentinel = out / reference['SCIENCE.MEFIMAGE']['name']; sentinel.write_bytes(b'preserve me')
            run(instrument + '-existing-output', [*opts, *calibration_args, '--science', lists / 'science.list'], callers[0], valid=False)
            assert sentinel.read_bytes() == b'preserve me'
            # Preserve bytes, mode bits, mtimes, and empty caller directories.
            assert calibration_baseline == inventory(full_outputs[0])
            assert all(not list(c.iterdir()) for c in callers)
            after = {str(p): inventory(p) for p in (raw, cfg, lists)}
            report[instrument + '-protected-after'] = after; save()
            assert protected == after
        report['status'] = 'passed'; save()
        print('PASS:', len(report['profiles']), 'native explicit-path profiles and', len(report['negatives']), 'rejections')
        print('PASS: independent numerical arrays, exact legacy metadata, protected inputs and cwd')
    except BaseException:
        report['status'] = 'failed'
        raise
    finally:
        save()
        print('EVIDENCE:', work, flush=True)


if __name__ == '__main__':
    main()
