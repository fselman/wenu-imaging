"""M2 migration/configuration only: no FITS, reduction, installation or activation."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

from config_snapshot_contract import expected_values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-root', 'reader', 'paf-probe', 'cli-probe', 'domain-probe', 'work-parent'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    module_path = root / 'Pycavi2/pycavi/pycavi/pycavi_configuration.py'
    spec = importlib.util.spec_from_file_location('wenu_configuration_test', module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    service = module.ConfigurationMigration(root, args.reader.resolve(strict=True))
    work = Path(tempfile.mkdtemp(prefix='m2 migration ', dir=args.work_parent.resolve(strict=True)))
    print('WORK DIRECTORY:', work, flush=True)
    callers = [work / 'caller one', work / 'caller two']
    for caller in callers:
        caller.mkdir()
    profiles, rejections, commands = [], [], []
    baseline = json.loads((root / 'docs/architecture/proposed/m1/effective-settings-baseline.json').read_text())

    def run(argv, label, expected=0, caller=0):
        result = subprocess.run([str(a) for a in argv], cwd=callers[caller],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
        (work / (label + '.log')).write_bytes(result.stdout)
        commands.append(dict(argv=[str(a) for a in argv], cwd=str(callers[caller]),
                             status=result.returncode, log=label + '.log'))
        if expected == 0:
            assert result.returncode == 0, (label, result.stdout[-3000:])
        else:
            assert result.returncode != 0, (label, result.stdout[-3000:])
        return result

    def values(frozen):
        return {f['native_key']: f['stored'] for f in frozen.as_dict()['settings']['native'].values()}

    def reject(label, function):
        try:
            function()
        except (module.MigrationError, OSError, ValueError, KeyError):
            rejections.append(label)
        else:
            raise AssertionError('Accepted invalid configuration: ' + label)

    # Actual constructors are independent references; never infer PAF numbers in Python.
    for instrument in ('omegacam', 'wfi'):
        source = root / f'Pycavi2/pycavi/config/{instrument}.paf'
        cfg_files = [('instrument', root / f'Pycavi2/pycavi/config/{instrument}.cfg'),
                     ('project', root / 'Pycavi2/pycavi/config/pycavi.cfg')]
        frozen, text = service.migrate_paf(source, cfg_files=cfg_files)
        assert values(frozen) == expected_values(baseline, instrument)
        examples = root / 'docs/architecture/proposed/m2/migration-examples'
        assert (examples / (instrument + '.toml')).read_text() == text
        evidence = json.loads((examples / 'conversion-evidence.json').read_text())['profiles'][instrument]
        assert evidence['stored_settings'] == values(frozen)
        assert evidence['example_sha256'] == hashlib.sha256(text.encode()).hexdigest()
        assert evidence['original_sources'][0]['text'].encode() == source.read_bytes()
        native_output = work / (instrument + '-original.json')
        run([args.paf_probe, source, native_output], instrument + '-original-paf')
        assert values(frozen) == json.loads(native_output.read_text())
        data = frozen.as_dict()
        assert data['provenance']['exact_stored_value_comparison']
        duplicates = data['provenance']['ledger']['duplicates']
        assert len(duplicates) == (2 if instrument == 'wfi' else 0)
        assert all(d['identical'] and len(d['occurrences']) == 2 for d in duplicates)
        assert len(data['settings']['legacy_cfg']) == 2
        assert sum(len(c['values']) for c in data['settings']['legacy_cfg']) > 70
        assert data['wad_validation'] == 'configuration-attributes-checked'
        assert data['execution_ready'] is False
        # Shared CLI/library and caller independence, including an exclusive publish receipt.
        for caller in (0, 1):
            destination = work / f'{instrument}-cli-{caller}'
            run([sys.executable, '-B', module_path, '--source-root', root,
                 '--native-reader', args.reader, 'migrate-paf', source,
                 '--instrument-cfg', cfg_files[0][1], '--project-cfg', cfg_files[1][1],
                 '--output', destination], f'{instrument}-cli-{caller}', caller=caller)
            assert (destination / 'configuration.json').read_bytes() == frozen.encoded
            assert (destination / 'configuration.toml').read_text() == text
            receipt = json.loads((destination / 'COMPLETE.json').read_text())
            assert all(hashlib.sha256((destination / name).read_bytes()).hexdigest() == sha
                       for name, sha in receipt.items())
            assert service.restore(destination / 'configuration.json') == frozen
        run([sys.executable, '-B', module_path, '--source-root', root,
             '--native-reader', args.reader, 'migrate-paf', source, '--output', destination],
            instrument + '-no-clobber', expected=1)
        # Selected local overrides: compare real retained CLI loader with native TOML.
        local = root / f'docs/architecture/proposed/m2/examples/{instrument}/local.toml'
        local_frozen = service.load_toml(local)
        cli_json, cli_values = work / (instrument + '-cli.json'), work / (instrument + '-cli-values.json')
        run([args.cli_probe, cli_json, cli_values, callers[0], 'mefpp', '--pafname', source,
             '--biaskappa1', '0.123456789012345', '--scanrej', '2 3'], instrument + '-overrides')
        assert values(local_frozen) == json.loads(cli_values.read_text())
        sources = local_frozen.as_dict()['sources']
        assert len(sources) == 5
        assert any(s['override_keys'] for s in sources)
        assert sum(d['native_key'] == 'MEF.BIAS.KAPPA1' for s in sources for d in s['definitions']) == 2
        assert all(hashlib.sha256(s['text'].encode()).hexdigest() == s['sha256'] for s in sources)
        for caller in (0, 1):
            destination = work / f'{instrument}-toml-{caller}'
            run([sys.executable, '-B', module_path, '--source-root', root,
                 '--native-reader', args.reader, 'freeze-toml', local, '--output', destination],
                f'{instrument}-freeze-{caller}', caller=caller)
            assert (destination / 'configuration.json').read_bytes() == local_frozen.encoded
        # Current authoring record and its complete native reference become one frozen record.
        project = root / f'docs/architecture/proposed/m2/project-contracts/examples/{instrument}.toml'
        combined = service.load_project(project)
        assert values(combined) == values(frozen)
        project_data = combined.as_dict()['settings']['project']['configuration']
        assert len({project_data[k]['id'] for k in ('reduction_profile', 'recipe', 'product_profile')}) == 3
        destination = work / (instrument + '-project')
        run([sys.executable, '-B', module_path, '--source-root', root,
             '--native-reader', args.reader, 'freeze-project', project, '--output', destination],
            instrument + '-project')
        assert (destination / 'configuration.json').read_bytes() == combined.encoded
        profiles.append(dict(instrument=instrument, settings=len(values(frozen)),
                             identical_duplicates=len(duplicates), configuration_sha256=frozen.identity))

    # Migration conflict gate, explicit source-line resolution and unchanged originals.
    original = (root / 'Pycavi2/pycavi/config/wfi.paf').read_bytes()
    source = work / 'private source.paf'
    source.write_bytes(original + b'MEF.BIAS.KAPPA1 9.125;\n')
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    try:
        service.migrate_paf(source)
    except module.MigrationError as exc:
        assert exc.ledger['conflicts'][0]['key'] == 'MEF.BIAS.KAPPA1'
        rejections.append('conflicting PAF with occurrence ledger')
    else:
        raise AssertionError('Implicit conflicting PAF accepted')
    line = len(source.read_text().splitlines())
    resolved, _ = service.migrate_paf(source, resolutions={'MEF.BIAS.KAPPA1': line})
    assert values(resolved)['MEF.BIAS.KAPPA1']['value'] == '4022400000000000'  # independently encoded binary64 9.125
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
    reject('invalid source-line resolution', lambda: service.migrate_paf(source, resolutions={'MEF.BIAS.KAPPA1': 1}))
    reject('unused resolution', lambda: service.migrate_paf(source, resolutions={'MEF.BIAS.KAPPA1': line, 'MEF.NCHIPS': 12}))
    source.write_bytes(original.replace(b'\n', b'\r\n'))
    record, _ = service.migrate_paf(source)
    assert record.as_dict()['sources'][0]['text'].encode() == original.replace(b'\n', b'\r\n')
    encoded = record.encoded
    changed = record.as_dict(); changed['sources'].clear()
    source.unlink()
    assert record.encoded == encoded and record.as_dict()['sources']
    saved = work / 'saved.json'; saved.write_bytes(record.encoded)
    assert service.restore(saved) == record
    changed = record.as_dict(); changed['sources'][0]['text'] += 'tampered'
    saved.write_text(json.dumps(changed))
    reject('frozen source tampering', lambda: service.restore(saved))
    changed = record.as_dict(); changed['settings']['native']['processing.bias_kappa1']['stored']['value'] = '0000000000000000'
    saved.write_text(json.dumps(changed))
    reject('frozen stored-value tampering', lambda: service.restore(saved))

    # All native source bytes and override definitions survive edits/deletion; C
    # document clone is checked independently after it destroys the original owner.
    graph = work / 'private graph'
    shutil.copytree(root / 'docs/architecture/proposed/m2/examples/wfi', graph)
    immutable = service.load_toml(graph / 'local.toml')
    exact_sources = {s['path']: Path(s['path']).read_bytes() for s in immutable.as_dict()['sources']}
    assert all(s['text'].encode() == exact_sources[s['path']] for s in immutable.as_dict()['sources'])
    settings, sources = work / 'c-frozen-values.json', work / 'c-frozen-sources.json'
    before = (graph / 'local.toml').read_text()
    run([args.domain_probe, graph / 'local.toml', settings, sources, 'freeze'], 'c-frozen-source-owner')
    assert json.loads(sources.read_text())['files'][0]['text'] == before
    shutil.rmtree(graph)
    assert values(immutable) and immutable.as_dict()['sources'][0]['text'] == before

    # A parent may explicitly resolve sibling disagreement, retaining all three
    # contributions. Symlink targets are frozen as resolved graph edges.
    graph.mkdir()
    (graph / 'base.toml').write_text((root / 'docs/architecture/proposed/m2/examples/wfi/full.toml').read_text())
    (graph / 'other.toml').write_text(service.render({'MEF.BIAS.KAPPA1': {'type': 'float64-bits', 'value': '4022400000000000'}}))
    (graph / 'alias.toml').symlink_to('other.toml')
    (graph / 'entry.toml').write_text(service.render({'MEF.BIAS.KAPPA1': {'type': 'float64-bits', 'value': '4008000000000000'}},
                                                     includes=['base.toml', 'alias.toml'], overrides=['MEF.BIAS.KAPPA1']))
    parent = service.load_toml(graph / 'entry.toml').as_dict()
    assert parent['settings']['native']['processing.bias_kappa1']['stored']['value'] == '4008000000000000'
    assert parent['provenance']['native_sources']['MEF.BIAS.KAPPA1']['explicit_override']
    assert parent['sources'][0]['resolved_include'] == [str(graph / 'base.toml'), str(graph / 'other.toml')]
    assert sum(d['native_key'] == 'MEF.BIAS.KAPPA1' for source in parent['sources'] for d in source['definitions']) == 3
    (graph / 'alias.toml').unlink()
    assert parent['sources'][0]['resolved_include'][1] == str(graph / 'other.toml')

    # Rejection/recovery: migration vocabulary and native semantic gates. Fixtures
    # are private; valid requests immediately following every failure still pass.
    for label, raw in (
        ('unknown PAF key', original + b'MEF.BIAS.KAPPA11 2;\n'),
        ('missing PAF key', original.replace(b'MEF.BIAS.KAPPA1', b'#MEF.BIAS.KAPPA1')),
        ('invalid PAF number', original.replace(b'MEF.BIAS.KAPPA1                        2.0;', b'MEF.BIAS.KAPPA1 nope;')),
        ('oversized PAF line', original + b'#' + b'x' * 1025 + b'\nMEF.UNKNOWN ' + b'x' * 1025 + b';\n'),
        ('invalid detector count', original.replace(b'MEF.NCHIPS', b'#MEF.NCHIPS') + b'MEF.NCHIPS 999999999;\n'),
        ('embedded NUL', original + b'\0'),
    ):
        # Replace independently of spacing for the native numeric failure.
        if label == 'invalid PAF number':
            import re
            raw = re.sub(rb'(MEF.BIAS.KAPPA1)[^\n]+', rb'\1 nope;', original)
        source.write_bytes(raw)
        reject(label, lambda: service.migrate_paf(source))
        assert values(service.load_toml(root / 'docs/architecture/proposed/m2/examples/wfi/full.toml'))
    valid_text = (root / 'docs/architecture/proposed/m2/examples/wfi/full.toml').read_text()
    toml = work / 'invalid.toml'
    cases = {
        'unknown TOML key': valid_text.replace('[processing]', '[processing]\nunknown = 1'),
        'wrong TOML unit': valid_text.replace('unit = "electron/adu"', 'unit = "wrong"', 1),
        'wrong TOML type': valid_text.replace('detector_count = { value = 8', 'detector_count = { value = "8"'),
        'missing TOML field': valid_text.replace('bias_kappa1 =', 'missing ='),
        'subset cycle': 'schema_version = 3\ninclude = ["invalid.toml"]\n',
        'undeclared conflict': service.render({'MEF.BIAS.KAPPA1': {'type': 'float32-bits', 'value': '41120000'}},
                                             includes=[str(root / 'docs/architecture/proposed/m2/examples/wfi/full.toml')]),
        'native NUL source': valid_text + '\0',
    }
    for label, text in cases.items():
        toml.write_bytes(text.encode())
        reject(label, lambda: service.load_toml(toml))
        assert values(service.load_toml(root / 'docs/architecture/proposed/m2/examples/wfi/full.toml'))
    cfg = work / 'invalid.cfg'
    for label, text in (('unknown CFG option', '[General]\nunknown = 1\n'),
                        ('duplicate CFG option', '[General]\ndebug = True\ndebug = False\n'),
                        ('CFG DEFAULT inheritance', '[DEFAULT]\ndebug = True\n[General]\nlog_level = info\n')):
        cfg.write_text(text)
        try:
            service.cfg(cfg, 'project')
        except Exception as exc:
            assert isinstance(exc, (module.MigrationError, __import__('configparser').Error))
            rejections.append(label)
        else:
            raise AssertionError(label)
    # Malformed CLI and failed migrations cannot create their output directory.
    for label, tail in (('CLI malformed resolution', ['migrate-paf', source, '--resolve', 'bad']),
                        ('CLI native failure', ['freeze-toml', toml])):
        output = work / label
        run([sys.executable, '-B', module_path, '--source-root', root, '--native-reader', args.reader,
             *tail, '--output', output], label.replace(' ', '-'), expected=1)
        assert not output.exists()
    report = dict(profiles=profiles, rejections=rejections, commands=commands,
                  python=sys.version, platform=platform.platform(),
                  reader_sha256=service.reader_sha256, source_root=str(root))
    (work / 'run-provenance.json').write_bytes(module.encode(report))
    print('PASS: exact OCAM/WFI PAF and local CLI values; shared CLI/library from two directories')
    print('PASS: duplicate/conflict ledger, frozen parsed source graphs and WAD configuration records')
    print(f'PASS: {len(rejections)} rejection/recovery controls; no-clobber and source/caller independence')
    print('REPORT:', work / 'run-provenance.json')


if __name__ == '__main__':
    main()
