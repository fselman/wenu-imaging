"""Native TOML subset composition, actual-loader equivalence and failure owners.

Uses source PAF text and synthetic TOML graphs only. No FITS or recipe execution.
"""
import argparse
import copy
import hashlib
import json
import os
import platform
import subprocess
import tempfile
import tomllib
from pathlib import Path

from config_snapshot_contract import expected_values
from config_toml_contract import render_snapshot


def document(values=None, includes=(), overrides=()):
    text = render_snapshot(values or {}).replace('schema_version = 1', 'schema_version = 2')
    return text.replace('[native]', 'include = ' + json.dumps(list(includes)) + '\n'
                        + 'override_keys = ' + json.dumps(list(overrides)) + '\n\n[native]')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-root', 'toml-probe', 'paf-probe', 'cli-probe', 'work-parent'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    probe, paf_probe, cli_probe = (p.resolve(strict=True) for p in
                                   (args.toml_probe, args.paf_probe, args.cli_probe))
    work = Path(tempfile.mkdtemp(prefix='m2 subsets ', dir=args.work_parent.resolve(strict=True)))
    (work / 'cwd one').mkdir(); (work / 'cwd two').mkdir()
    print('WORK DIRECTORY:', work, flush=True)
    commands, success, rejected = [], [], []

    def run(argv, name, cwd=None):
        log = work / (name + '.log')
        with log.open('w') as stream:
            result = subprocess.run([str(x) for x in argv], cwd=cwd or work / 'cwd one',
                                    stdout=stream, stderr=subprocess.STDOUT, timeout=90, check=False)
        commands.append({'argv': [str(x) for x in argv], 'cwd': str(cwd or work / 'cwd one'),
                         'exit_status': result.returncode, 'log': log.name})
        if result.returncode:
            raise RuntimeError('STOP: ' + name + '; inspect ' + str(log))
        return log.read_text()

    def write(name, text):
        path = work / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
        return path

    def accepted(path, expected, name):
        # The probe checks clone/destruction and every composition/snapshot
        # allocation failure as well as the final dump from each caller cwd.
        for i, cwd in enumerate((work / 'cwd one', work / 'cwd two')):
            output = work / (name + '-' + str(i) + '.json')
            run([probe, path, output], name + '-' + str(i), cwd)
            if json.loads(output.read_text()) != expected:
                raise RuntimeError('Wrong effective settings: ' + name)
        success.append(name)

    baseline = json.loads((root / 'docs/architecture/proposed/m1/effective-settings-baseline.json').read_text())
    references = {}
    # Actual PAF reference and equivalent reusable instrument/processing/product
    # subsets for both instruments. Graphs keep all original settings and bits.
    for instrument, profile in baseline['profiles'].items():
        paf = root / ('mefpp2/ins/mef/config/' + instrument + '.paf')
        assert hashlib.sha256(paf.read_bytes()).hexdigest() == profile['project_paf_sha256']
        output = work / (instrument + '-paf.json')
        run([paf_probe, paf, output], instrument + '-paf')
        values = json.loads(output.read_text()); references[instrument] = values
        assert values == expected_values(baseline, instrument)
        instrument_values = {k: v for k, v in values.items() if '.CHIP' in k or k == 'MEF.NCHIPS'}
        processing = {k: v for k, v in values.items() if k not in instrument_values and v['type'] != 'string'}
        product = {k: v for k, v in values.items() if k not in instrument_values and k not in processing}
        for name, part in [('instrument', instrument_values), ('processing', processing), ('product', product)]:
            write(instrument + '/shared settings/' + name + '.toml', document(part))
        entry = write(instrument + '/entry.toml', document(includes=[
            'shared settings/instrument.toml', 'shared settings/processing.toml', 'shared settings/product.toml']))
        for path in entry.parent.rglob('*.toml'):
            tomllib.loads(path.read_text())
        accepted(entry, values, instrument + '-split')
        base = write(instrument + '/base.toml', document(values))
        # Compare permitted local overrides against the actual retained CLI
        # loader, not an independent Python approximation of its conversions.
        legacy = work / (instrument + '-cli.json')
        run([cli_probe, work / (instrument + '-request.json'), legacy, work / 'cwd one',
             'mefpp', '--pafname', paf, '--biaskappa1', '0.123456789012345',
             '--scanrej', '2 3'], instrument + '-cli')
        expected = json.loads(legacy.read_text())
        changed = {k: v for k, v in expected.items() if v != values[k]}
        local = write(instrument + '/local.toml', document(changed, ['base.toml'], changed))
        accepted(local, expected, instrument + '-cli-overrides')
        # Parent explicitly resolves conflicting siblings. Include order cannot
        # silently choose a different scientific value.
        key = 'MEF.BIAS.KAPPA1'; final = {key: expected[key]}
        write(instrument + '/sibling.toml', document({key: {'type': 'float64-bits', 'value': '4004000000000000'}}))
        for order in (['base.toml', 'sibling.toml'], ['sibling.toml', 'base.toml']):
            entry = write(instrument + '/resolved.toml', document(final, order, [key]))
            target = copy.deepcopy(values); target.update(final)
            accepted(entry, target, instrument + '-resolved-' + str(order[0] == 'base.toml'))
        nested_value = {key: {'type': 'float64-bits', 'value': '4001000000000000'}}
        nested = write(instrument + '/nested.toml', document(nested_value, ['local.toml'], [key]))
        nested_expected = copy.deepcopy(expected); nested_expected.update(nested_value)
        accepted(nested, nested_expected, instrument + '-nested-override')
        # Shared-subset diamond and a canonical symlink alias are idempotent.
        write(instrument + '/left.toml', document(includes=['base.toml']))
        write(instrument + '/right.toml', document(includes=['base.toml']))
        diamond = write(instrument + '/diamond.toml', document(includes=['left.toml', 'right.toml']))
        accepted(diamond, values, instrument + '-diamond')
        alias = work / instrument / 'alias.toml'; alias.symlink_to('base.toml')
        aliases = write(instrument + '/aliases.toml', document(includes=['base.toml', './alias.toml']))
        accepted(aliases, values, instrument + '-aliases')
        # An identical explicitly declared replacement is a permitted no-op.
        noop = write(instrument + '/noop.toml', document({key: values[key]}, ['base.toml'], [key]))
        accepted(noop, values, instrument + '-noop')

    # New rejection cases: each must reject before recovering valid WFI settings
    # in the same process. Matching diagnostic text checks the failure reason.
    values = references['wfi']; key = 'MEF.BIAS.KAPPA1'
    full = write('bad/base.toml', document(values))
    write('bad/conflict.toml', document({key: {'type': 'float64-bits', 'value': '4004000000000000'}}))
    real = {key: {'type': 'float64-bits', 'value': '4008000000000000'}}
    assert real[key] != values[key], 'Rejection fixture must actually conflict'
    cases = {
        'siblings-conflict': (document(includes=['base.toml', 'conflict.toml']), 'Conflicting definitions'),
        'parent-undeclared': (document(real, ['base.toml']), 'Conflicting definitions'),
        'override-missing-local': (document(includes=['base.toml'], overrides=[key]), 'missing local value'),
        'override-missing-inherited': (document(real, overrides=[key]), 'no inherited value'),
        'forbid-detector-count': (document({'MEF.NCHIPS': values['MEF.NCHIPS']}, ['base.toml'], ['MEF.NCHIPS']), 'Override forbidden'),
        'forbid-gain': (document({'MEF.CCD.GAIN.CHIP1': values['MEF.CCD.GAIN.CHIP1']}, ['base.toml'], ['MEF.CCD.GAIN.CHIP1']), 'Override forbidden'),
        'forbid-string': (document({'MEF.INSTRUMENT': values['MEF.INSTRUMENT']}, ['base.toml'], ['MEF.INSTRUMENT']), 'Override forbidden'),
        'missing-include': (document(includes=['missing.toml']), 'Cannot resolve configuration'),
        'direct-cycle': (document(includes=['direct-cycle.toml']), 'Include cycle'),
        'missing-final-fields': (document(real), 'MEF.NCHIPS'),
        'version1-include': (document(includes=['version1.toml']), 'require schema_version=2'),
        'unknown-key': (document({'MEF.UNKNOWN': {'type': 'int', 'value': 1}}, ['base.toml']), 'Invalid subset setting'),
        'bad-chip-number': (document({'MEF.CCD.GAIN.CHIP01': values['MEF.CCD.GAIN.CHIP1']}, ['base.toml']), 'Invalid subset setting'),
        'oversized-chip-number': (document({'MEF.CCD.GAIN.CHIP2147483648': values['MEF.CCD.GAIN.CHIP1']}, ['base.toml']), 'Invalid subset setting'),
        'bad-schema': (document(includes=['base.toml']).replace('schema_version = 2', 'schema_version = 3'), 'schema_version'),
        'include-scalar': (document(includes=['base.toml']).replace('["base.toml"]', '"base.toml"'), 'arrays'),
        'include-integer': (document(includes=['base.toml']).replace('["base.toml"]', '[1]'), 'invalid string'),
        'include-empty': (document(includes=['base.toml']).replace('["base.toml"]', '[""]'), 'invalid string'),
        'include-nul': (document(includes=['base.toml']).replace('["base.toml"]', '["base\\u0000.toml"]'), 'invalid string'),
        'duplicate-include': (document(includes=['base.toml', 'base.toml']), 'Duplicate composition-list'),
        'duplicate-override': (document(real, ['base.toml'], [key, key]), 'Duplicate composition-list'),
        'unknown-override': (document(real, ['base.toml'], ['MEF.UNKNOWN']), 'missing local value'),
        'bad-override-type': (document(real, ['base.toml'], [key]).replace('override_keys = ["MEF.BIAS.KAPPA1"]', 'override_keys = true'), 'arrays'),
        'unknown-root': (document(includes=['base.toml']).replace('[native]', 'unknown = 1\n[native]'), 'Unknown root'),
        'long-include': (document(includes=['x' * 10000]), 'Include path limit'),
        'many-includes': (document(includes=[str(i) for i in range(65)]), 'at most 64'),
    }
    write('bad/version1.toml', render_snapshot(values))
    write('bad/cycle-a.toml', document(includes=['cycle-b.toml']))
    write('bad/cycle-b.toml', document(includes=['cycle-a.toml']))
    cases['indirect-cycle'] = (document(includes=['cycle-a.toml']), 'Include cycle')
    (work / 'bad/cycle-link.toml').symlink_to('alias-cycle.toml')
    cases['alias-cycle'] = (document(includes=['cycle-link.toml']), 'Include cycle')
    write('bad/inner.toml', document(real, ['base.toml'], [key]))
    cases['override-scope'] = (document({key: values[key]}, ['inner.toml']), 'Conflicting definitions')
    wrong = copy.deepcopy(values); wrong[key] = {'type': 'string', 'value': 'invalid'}
    write('bad/invalid-child.toml', document(wrong))
    cases['hidden-invalid-child'] = (document(real, ['invalid-child.toml'], [key]), 'Invalid subset setting')
    for i in range(17):
        write('bad/depth-' + str(i) + '.toml', document(includes=['depth-' + str(i + 1) + '.toml']) if i < 16 else document(values))
    cases['depth-limit'] = (document(includes=['depth-0.toml']), 'depth limit')
    for i in range(64):
        write('bad/file-' + str(i) + '.toml', document())
    cases['file-limit'] = (document(includes=['file-' + str(i) + '.toml' for i in range(64)]), 'file limit')
    good = work / 'wfi/entry.toml'
    for name, (text, diagnostic) in cases.items():
        bad = write('bad/' + name + '.toml', text)
        output = work / (name + '-recovery.json')
        log = run([probe, good, output, bad], 'reject-' + name)
        assert diagnostic in log, (name, diagnostic, log)
        assert json.loads(output.read_text()) == values
        rejected.append(name)
    print('PASS:', len(success), 'composition/equivalence profiles from two caller directories', flush=True)
    print('PASS:', len(rejected), 'composition rejection/recovery cases', flush=True)

    # Retain exact source/probe identities and commands for this attempt.
    inputs = [Path(__file__).resolve(), probe, paf_probe, cli_probe]
    inputs += list((root / 'mefpp2/ins/mef/common').glob('mef*toml*.[ch]'))
    inputs.append(root / 'mefpp2/ins/mef/common/mef_toml_override_keys.def')
    report = {'status': 'native-toml-subsets-passed', 'host': platform.node(),
              'platform': platform.platform(), 'commands': commands,
              'profiles': success, 'rejections': rejected,
              'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              'scope': 'native compatibility subsets only; no FITS/recipe/installation or complete M2'}
    (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
    print('REPORT:', work / 'run-provenance.json', flush=True)


if __name__ == '__main__':
    main()
