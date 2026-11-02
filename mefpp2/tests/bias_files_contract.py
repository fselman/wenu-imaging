"""Tiny end-to-end bias template: actual legacy reference, PAF, then TOML.

Synthetic processing only; never opens real observations or installs software.
All numerical planes are 18x9 or 9x9. Retain every attempt on the first failure.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np
from astropy.io import fits
from config_toml_contract import render_snapshot
from prepare_integrated_campaign_fixture import prepare


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-root', 'adapter', 'legacy', 'work-parent'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    source = args.source_root.resolve(strict=True)
    adapter, legacy = args.adapter.resolve(strict=True), args.legacy.resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix='m5-bias-', dir=args.work_parent)).resolve()
    other = work / 'unrelated-cwd'; other.mkdir()
    report = dict(status='running', commands=[], profiles=[], source_revision=os.environ.get('MEFPP_TEST_REVISION'),
                  scope='synthetic one-detector bias template; no scientific/Phase3/memory certification',
                  adapter_sha256=digest(adapter), legacy_sha256=digest(legacy))

    def save():
        (work / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')

    def run(label, argv, good=True):
        log = work / (label + '.log')
        entry = dict(label=label, argv=list(map(str, argv)), cwd=str(other), log=str(log))
        report['commands'].append(entry); save()
        env = dict(os.environ, E_VERBOSE='0', E_DEBUG='0')
        env.pop('E_LOGFILE', None)
        with log.open('x') as stream:
            result = subprocess.run(entry['argv'], cwd=other, stdout=stream, stderr=subprocess.STDOUT,
                                    timeout=120, env=env)
        entry['exit_status'] = result.returncode; entry['log_sha256'] = digest(log); save()
        assert (result.returncode == 0) == good, (label, result.returncode, log)
        assert result.returncode >= 0, (label, 'unexpected signal', log)
        return log

    def options(directory, config_flag, config, listing, hdu):
        directory.mkdir()
        return ['cal', 'bias', config_flag, config, '--bias', listing,
                '--detector-id', 'explicit-B', '--hdu', str(hdu), '--config-detector', '1',
                '--readout-id', 'synthetic-readout', '--bin-x', '1', '--bin-y', '1',
                '--input-bpm', 'omitted', '--output', directory / 'bias.fits',
                '--work-dir', directory, '--log-path', directory / 'native.log',
                '--config-record', directory / 'config.json', '--qc-record', directory / 'qc.json']

    def headers(hdu):
        return [card.image for card in hdu.header.cards if card.keyword != 'ORIGFILE']

    print('RETAINED RUN:', work, flush=True)
    try:
        # Build tiny instrument-specific inputs, with a rejected middle frame.
        for instrument in ('omegacam', 'wfi'):
            group = work / instrument; group.mkdir()
            raw = group / 'raw'; fixture = prepare(raw, source)
            text = (source / f'mefpp2/ins/mef/config/{instrument}.paf').read_text()
            overrides = dict(fixture['synthetic_paf_overrides'], **{'MEF.BIAS.KAPPA1': 1.2})
            for key, value in overrides.items():
                text, count = re.subn(r'^' + re.escape(key) + r'\s+[^;\n]*;',
                                     key + ' ' + str(value) + ';', text, flags=re.M)
                assert count == 1, key
            paf = group / 'bias.paf'; paf.write_text(text)
            members = [raw / 'bias0.fits', raw / 'outlier.fits', raw / 'bias1.fits', raw / 'bias2.fits']
            with fits.open(members[0], memmap=False) as hdus:
                hdus[1].data[:, :9] += 100; hdus[2].data[:, :9] += 100
                hdus.writeto(members[1])
            # Nonconstant detector B makes correct detector/HDU selection observable.
            for path in members:
                with fits.open(path, mode='update', memmap=False) as hdus:
                    hdus[0].header['INSTRUME'] = 'WFI' if instrument == 'wfi' else 'OMEGACAM'
                    hdus[2].data[:, :9] += np.arange(9, dtype=np.float32)[None, :] + 7
            listing = group / 'bias.list'; listing.write_text('\n'.join(map(str, members)) + '\n')
            immutable = [*members, listing, paf]
            before = {str(p): digest(p) for p in immutable}
            # Actual old option-based recipe builds both extensions as reference.
            reference = group / 'reference'; reference.mkdir()
            run(instrument + '-legacy', [legacy, '--pafname', paf, '--bias', listing, '--biassave',
                '--output-dir', reference, '--work-dir', reference, '--log-file', reference / 'native.log'])
            products = list(reference.glob('*.fits')); assert len(products) == 1, products
            paf_run = group / 'paf'
            run(instrument + '-paf', [adapter, *options(paf_run, '--pafname', paf, listing, 2)])
            with fits.open(products[0], memmap=False) as old, fits.open(paf_run / 'bias.fits', memmap=False) as new:
                assert len(new) == 2
                np.testing.assert_array_equal(new[1].data, old[2].data)
                np.testing.assert_array_equal(new[1].data, np.tile(np.arange(9, dtype=np.float32) + 7, (9, 1)))
                assert headers(new[0]) == headers(old[0]), 'primary legacy header difference'
                assert headers(new[1]) == headers(old[2]), 'extension legacy header difference'
            qc = json.loads((paf_run / 'qc.json').read_text())
            assert qc['status'] == 'complete' and qc['accepted_frames'] == 3
            assert [f['index'] for f in qc['frames']] == [0, 1, 2, 3]
            assert [f['accepted'] for f in qc['frames']] == [1, 0, 1, 1]
            # TOML is emitted from the actual native PAF snapshot, never parsed
            # from decimal PAF values by a second decoder.
            snapshot = json.loads((paf_run / 'config.json').read_text())
            toml = group / 'bias.toml'; toml.write_text(render_snapshot(snapshot))
            toml_run = group / 'toml'
            run(instrument + '-toml', [adapter, *options(toml_run, '--config', toml, listing, 2)])
            assert snapshot == json.loads((toml_run / 'config.json').read_text())
            assert qc == json.loads((toml_run / 'qc.json').read_text())
            with fits.open(paf_run / 'bias.fits', memmap=False) as first, fits.open(toml_run / 'bias.fits', memmap=False) as second:
                np.testing.assert_array_equal(first[1].data, second[1].data)
                assert all(headers(a) == headers(b) for a, b in zip(first, second))
            # Primary-image storage must reach the same template and arithmetic.
            primary_members = []
            for i, path in enumerate(members):
                dest = group / f'primary-{i}.fits'
                with fits.open(path, memmap=False) as hdus:
                    fits.PrimaryHDU(data=hdus[2].data, header=hdus[0].header).writeto(dest)
                primary_members.append(dest)
            primary_list = group / 'primary.list'
            primary_list.write_text('\n'.join(map(str, primary_members)) + '\n')
            primary_run = group / 'primary'
            run(instrument + '-primary', [adapter, *options(primary_run, '--config', toml, primary_list, 0)])
            with fits.open(primary_run / 'bias.fits', memmap=False) as hdus, fits.open(toml_run / 'bias.fits', memmap=False) as expected:
                hdus.verify('exception'); assert len(hdus) == 2 and hdus[0].data is None
                np.testing.assert_array_equal(hdus[1].data, expected[1].data)
            # Exclusive publication: an existing destination is preserved.
            negative = group / 'existing-output'
            argv = options(negative, '--config', toml, listing, 2)
            target = negative / 'bias.fits'; target.write_bytes(b'protected existing product\n')
            expected_hash = digest(target)
            run(instrument + '-existing-output', [adapter, *argv], good=False)
            assert digest(target) == expected_hash and not list(negative.glob('.mefpp-bias-*'))
            assert json.loads((negative / 'qc.json').read_text())['status'] == 'failed'
            # A missing selected HDU fails before numerical publication.
            missing = group / 'missing-hdu'
            run(instrument + '-missing-hdu', [adapter, *options(missing, '--config', toml, listing, 99)], good=False)
            assert not (missing / 'bias.fits').exists()
            assert before == {str(p): digest(p) for p in immutable}, 'input/config mutation'
            report['profiles'].append(instrument); save()
            print('PASS:', instrument, 'legacy/PAF/TOML/primary pixels, headers, QC, no-clobber and missing-HDU', flush=True)
        report['status'] = 'passed'
    except BaseException:
        report['status'] = 'failed'
        raise
    finally:
        save(); print('EVIDENCE:', work, flush=True)


if __name__ == '__main__':
    main()
