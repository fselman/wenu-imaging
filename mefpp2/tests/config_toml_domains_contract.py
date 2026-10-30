"""Native typed domains/units and owned source records; configuration only."""
import argparse
import copy
import hashlib
import json
import platform
import re
import struct
import subprocess
import tempfile
import tomllib
from pathlib import Path

from config_snapshot_contract import expected_values
from config_toml_contract import render_snapshot


def scalar(entry):
    if entry['type'] == 'string':
        return json.dumps(entry['value'], ensure_ascii=False)
    if entry['type'] == 'int':
        return str(entry['value'])
    return repr(struct.unpack('>f' if entry['type'] == 'float32-bits' else '>d', bytes.fromhex(entry['value']))[0])


def describe(catalog, key):
    for field in catalog['fields']:
        pattern = re.escape(field['native_pattern']).replace('%d', '([1-9][0-9]*)')
        match = re.fullmatch(pattern, key)
        if match:
            result = dict(field)
            result['path'] = field['path_pattern'] % int(match[1]) if match.groups() else field['path_pattern']
            return result
    raise ValueError('Uncatalogued key: ' + key)


def render_domains(values, catalog, includes=(), overrides=()):
    tree = {}
    for key, entry in values.items():
        field = describe(catalog, key); parts = field['path'].split('.')
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = (entry, field['unit'])
    lines = ['# Native domain schema v1; configured values, no unit conversion.',
             'schema_version = 3', 'include = ' + json.dumps(list(includes)),
             'override_keys = ' + json.dumps([describe(catalog, k)['path'] for k in overrides])]

    def table(node, parts):
        lines.extend(['', '[' + '.'.join(parts) + ']'])
        if len(parts) == 1:
            lines.append('schema_version = 1')
        for key, value in node.items():
            if isinstance(value, tuple):
                entry, unit = value
                lines.append(key + ' = { value = ' + scalar(entry) + ', unit = ' + json.dumps(unit) + ' }')
        for key, value in node.items():
            if isinstance(value, dict):
                table(value, parts + [key])
    for key, node in tree.items():
        table(node, [key])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-root', 'probe', 'paf-probe', 'cli-probe', 'work-parent'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    probe, paf_probe, cli_probe = (p.resolve(strict=True) for p in (args.probe, args.paf_probe, args.cli_probe))
    work = Path(tempfile.mkdtemp(prefix='m2 domains ', dir=args.work_parent.resolve(strict=True)))
    (work / 'cwd one').mkdir(); (work / 'cwd two').mkdir()
    print('WORK DIRECTORY:', work, flush=True)
    commands, profiles, rejected = [], [], []

    def run(argv, label, cwd=None):
        log = work / (label + '.log')
        with log.open('w') as stream:
            result = subprocess.run([str(x) for x in argv], cwd=cwd or work / 'cwd one', stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=120, check=False)
        commands.append({'argv': [str(x) for x in argv], 'cwd': str(cwd or work / 'cwd one'),
                         'exit_status': result.returncode, 'log': log.name})
        if result.returncode:
            raise RuntimeError('STOP: ' + label + '; inspect ' + str(log))
        return log.read_text()

    def write(name, text):
        path = work / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
        tomllib.loads(text)
        return path

    # Independent coverage gate: compiled descriptors cover every accepted getter
    # template and agree with documented storage; unit checks name key physics.
    catalog_path = work / 'catalog.json'
    run([probe, '--catalog', catalog_path], 'catalog')
    catalog = json.loads(catalog_path.read_text())
    documented = json.loads((root / 'docs/architecture/proposed/m2/typed-field-catalog.json').read_text())
    assert catalog == documented
    baseline = json.loads((root / 'docs/architecture/proposed/m1/effective-settings-baseline.json').read_text())
    assert {f['native_pattern'] for f in catalog['fields']} == {f['key_template'] for f in baseline['registry']}
    assert len(catalog['fields']) == 151
    by_key = {f['native_pattern']: f for f in catalog['fields']}
    types = {'int': 'int32', 'float': 'float32', 'double': 'float64', 'char *': 'string'}
    for old in baseline['registry']:
        assert by_key[old['key_template']]['storage'] == types[old['legacy_storage_type'].split('[')[0]]
    for key, unit in [('MEF.CCD.GAIN.CHIP1', 'electron/adu'), ('MEF.CCD.RON.CHIP1', 'electron'),
                      ('MEF.CRVAL1.CHIP1', 'degree'), ('MEF.CRPIX1.CHIP1', 'pixel'),
                      ('MEF.SATLEVEL', 'adu'), ('MEF.BIAS.KAPPA1', '1'), ('MEF.NCHIPS', 'count')]:
        assert describe(catalog, key)['unit'] == unit

    def inspect(path, expected, label, mode=None, inherited=None):
        settings = work / (label + '-settings.json'); sources = work / (label + '-sources.json')
        argv = [probe, path, settings, sources]
        if mode:
            argv.append(mode)
        run(argv, label)
        assert json.loads(settings.read_text()) == expected
        meta = json.loads(sources.read_text())
        assert meta['source_hash_state'] == 'not-recorded'
        assert set(meta['fields']) == set(expected)
        for key, record in meta['fields'].items():
            field = describe(catalog, key)
            assert record['path'] == field['path'] and record['unit'] == field['unit']
            assert record['storage'] == field['storage'] and record['authority'] == 'configured'
            assert Path(record['source_file']).is_absolute() and record['source_line'] >= 1
            if mode != 'freeze':
                lines = Path(record['source_file']).read_text().splitlines()
                assert record['source_line'] <= len(lines)
                if record['input_schema_version'] == 3:
                    raw = tomllib.loads('\n'.join(lines)); leaf = raw
                    for part in record['source_key'].split('.'):
                        leaf = leaf[part]
                    assert leaf['unit'] == record['unit']
                    assert record['unit_origin'] == 'declared'
                else:
                    assert record['unit_origin'] == 'schema' and record['source_key'] == key
            if inherited is not None:
                assert record['inherited'] == inherited
        profiles.append(label)
        return meta

    # Actual native PAF/CLI references; full and split typed examples for each
    # instrument retain every original value/bit and original PAF source hash.
    references = {}
    for instrument, profile in baseline['profiles'].items():
        paf = root / ('mefpp2/ins/mef/config/' + instrument + '.paf')
        assert hashlib.sha256(paf.read_bytes()).hexdigest() == profile['project_paf_sha256']
        ref = work / (instrument + '-paf.json')
        run([paf_probe, paf, ref], instrument + '-paf')
        values = json.loads(ref.read_text()); references[instrument] = values
        assert values == expected_values(baseline, instrument)
        full = write(instrument + '/full.toml', render_domains(values, catalog))
        inspect(full, values, instrument + '-full', inherited=False)
        parts = {name: {k: v for k, v in values.items() if describe(catalog, k)['path'].startswith(name + '.')}
                 for name in ('instrument', 'processing', 'product')}
        for name, part in parts.items():
            write(instrument + '/shared settings/' + name + '.toml', render_domains(part, catalog))
        entry = write(instrument + '/entry.toml', render_domains({}, catalog, [
            'shared settings/instrument.toml', 'shared settings/processing.toml', 'shared settings/product.toml']))
        inspect(entry, values, instrument + '-split', inherited=True)
        legacy = work / (instrument + '-cli.json')
        run([cli_probe, work / (instrument + '-request.json'), legacy, work / 'cwd one', 'mefpp',
             '--pafname', paf, '--biaskappa1', '0.123456789012345', '--scanrej', '2 3'], instrument + '-cli')
        expected = json.loads(legacy.read_text()); changed = {k: v for k, v in expected.items() if v != values[k]}
        local = write(instrument + '/local.toml', render_domains(changed, catalog, ['entry.toml'], changed))
        meta = inspect(local, expected, instrument + '-override')
        for key, record in meta['fields'].items():
            assert record['explicit_override'] == (key in changed)
            assert record['inherited'] == (key not in changed)
        # Frozen document/clone survive editing a private test source after load.
        frozen = write(instrument + '/frozen.toml', render_domains(values, catalog))
        inspect(frozen, values, instrument + '-frozen', mode='freeze', inherited=False)
        assert frozen.read_text() == 'changed after loading\n'

    # Old formats also yield honest unit/source records, without inventing a PAF
    # origin: the actual source is the loaded TOML and units come from the catalog.
    values = references['wfi']
    for version in (1, 2):
        path = write('legacy-' + str(version) + '.toml', render_snapshot(values).replace('schema_version = 1', 'schema_version = ' + str(version)))
        inspect(path, values, 'legacy-' + str(version), inherited=False)
    edge = copy.deepcopy(values)
    for value in edge.values():
        if value['type'] == 'string': value['value'] = 'quoted "text" \\ newline\n café'
        elif value['type'] == 'float32-bits': value['value'] = '80000000'
        elif value['type'] == 'float64-bits': value['value'] = '8000000000000000'
    edge_path = write('quoted " café/edge.toml', render_domains(edge, catalog))
    inspect(edge_path, edge, 'edge', inherited=False)

    # Schema/unit/provenance rejection, followed by valid same-process recovery.
    text = render_domains(values, catalog); good = work / 'wfi/entry.toml'
    def change(part, replacement):
        assert part in text
        return text.replace(part, replacement, 1)
    unit_gain = 'gain = { value = ' + scalar(values['MEF.CCD.GAIN.CHIP1']) + ', unit = "electron/adu" }'
    cases = {
        'wrong-gain-unit': change('unit = "electron/adu"', 'unit = "adu/electron"'),
        'missing-unit': change(unit_gain, unit_gain.replace(', unit = "electron/adu"', '')),
        'unit-nul': change('unit = "electron/adu"', 'unit = "electron/adu\\u0000ignored"'),
        'unit-type': change('unit = "electron/adu"', 'unit = 1'),
        'scalar-instead-of-descriptor': change(unit_gain, 'gain = 2.0'),
        'integer-instead-of-real': change(unit_gain, 'gain = { value = 2, unit = "electron/adu" }'),
        'fake-source': change(unit_gain, unit_gain[:-2] + ', source = "measured" }'),
        'unknown-unit-conversion': change('unit = "degree"', 'unit = "radian"'),
        'missing-domain-version': change('[instrument]\nschema_version = 1', '[instrument]'),
        'wrong-domain-version': change('[instrument]\nschema_version = 1', '[instrument]\nschema_version = 2'),
        'bool-domain-version': change('[instrument]\nschema_version = 1', '[instrument]\nschema_version = true'),
        'unknown-field': text + '\n[processing.unknown]\nvalue = 1\nunit = "1"\n',
        'unknown-empty-container': text + '\n[product.unknown]\n',
        'noncanonical-chip': change('[instrument.detectors.CHIP1]', '[instrument.detectors.CHIP01]'),
        'zero-chip': change('[instrument.detectors.CHIP1]', '[instrument.detectors.CHIP0]'),
        'unknown-input-version': change('schema_version = 3', 'schema_version = 4'),
        'mixed-native': text + '\n[native]\n"MEF.NCHIPS" = 8\n',
        'recipe-is-not-product-map': text + '\n[recipe]\nschema_version = 1\n',
        'reduction-profile-is-distinct': text + '\n[reduction_profile]\nschema_version = 1\n',
        'product-profile-is-distinct': text + '\n[product_profile]\nschema_version = 1\n',
        'missing-final-fields': render_domains({}, catalog),
        'legacy-override-name': render_domains({}, catalog).replace('override_keys = []', 'override_keys = ["MEF.BIAS.KAPPA1"]'),
    }
    write('bad/legacy.toml', render_snapshot(values).replace('schema_version = 1', 'schema_version = 2'))
    cases['mixed-include-version'] = render_domains({}, catalog, ['legacy.toml'])
    forbidden = {'MEF.CCD.GAIN.CHIP1': values['MEF.CCD.GAIN.CHIP1']}
    cases['forbidden-detector-override'] = render_domains(forbidden, catalog, ['../wfi/entry.toml'], forbidden)
    # A unit error remains invalid even when a parent's valid local replacement
    # would otherwise hide the child's value.
    bias_key = 'MEF.BIAS.KAPPA1'
    bias_line = 'bias_kappa1 = { value = ' + scalar(values[bias_key]) + ', unit = "1" }'
    write('bad/invalid-child.toml', text.replace(bias_line, bias_line.replace('unit = "1"', 'unit = "adu"')))
    cases['hidden-unit-error'] = render_domains({bias_key: values[bias_key]}, catalog, ['invalid-child.toml'], [bias_key])
    for name, bad_text in cases.items():
        bad = work / 'bad' / (name + '.toml'); bad.parent.mkdir(exist_ok=True); bad.write_text(bad_text)
        settings = work / (name + '-recovery.json'); sources = work / (name + '-sources.json')
        log = run([probe, good, settings, sources, bad], 'reject-' + name)
        assert 'REJECTED:' in log and json.loads(settings.read_text()) == values
        rejected.append(name)
    print('PASS:', len(profiles), 'typed/document/lifetime profiles; 151 catalog templates', flush=True)
    print('PASS:', len(rejected), 'domain/unit rejection/recovery cases', flush=True)

    # Retain provenance and exact code/schema/probe identities for this attempt.
    inputs = [Path(__file__).resolve(), probe, paf_probe, cli_probe,
              root / 'docs/architecture/proposed/m2/typed-field-catalog.json']
    inputs += list((root / 'mefpp2/ins/mef/common').glob('mef*toml*.[ch]'))
    inputs += list((root / 'mefpp2/ins/mef/common').glob('mef_config_domains.*'))
    report = {'status': 'typed-native-domains-passed', 'host': platform.node(), 'platform': platform.platform(),
              'commands': commands, 'profiles': profiles, 'rejections': rejected,
              'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              'scope': 'three native domains and owned winning-source records; no source hashes/full histories, ASDF or science execution'}
    (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
    print('REPORT:', work / 'run-provenance.json', flush=True)


if __name__ == '__main__':
    main()
