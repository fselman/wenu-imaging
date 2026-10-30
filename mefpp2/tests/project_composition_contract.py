"""M2 project/native composition checks; configuration only, no FITS/reductions."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

from config_snapshot_contract import expected_values
from config_toml_contract import render_snapshot


def toml_document(data):
    """Fixture serializer only; production uses tomllib and the native reader."""
    lines = []
    def scalar(value):
        if type(value) is bool:
            return 'true' if value else 'false'
        return json.dumps(value, ensure_ascii=False)
    def table(node, path=(), array=False):
        if path:
            lines.append(('[[%s]]' if array else '[%s]') % '.'.join(path))
        for key, value in node.items():
            if not isinstance(value, dict) and not (isinstance(value, list) and value and isinstance(value[0], dict)):
                lines.append(key + ' = ' + scalar(value))
        for key, value in node.items():
            if isinstance(value, dict):
                lines.append(''); table(value, path + (key,))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                for child in value:
                    lines.append(''); table(child, path + (key,), True)
    table(data)
    text = '\n'.join(lines) + '\n'
    assert tomllib.loads(text) == data
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-root', 'reader', 'cli-probe', 'work-parent'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    api = root / 'Pycavi2/pycavi/pycavi/pycavi_configuration.py'
    spec = importlib.util.spec_from_file_location('wenu_project_composition_test', api)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    service = module.ConfigurationMigration(root, args.reader.resolve(strict=True))
    work = Path(tempfile.mkdtemp(prefix='m2 project composition ', dir=args.work_parent.resolve(strict=True)))
    print('WORK DIRECTORY:', work, flush=True)
    callers = [work / 'caller one', work / 'caller two']
    for caller in callers:
        caller.mkdir()
    profiles, rejected, commands = [], [], []
    baseline = json.loads((root / 'docs/architecture/proposed/m1/effective-settings-baseline.json').read_text())

    def write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(toml_document(data))
        return path

    def envelope(domains, includes=(), version=2):
        data = dict(project_schema_version=version)
        if version == 2:
            data['include'] = list(includes)
        data.update(copy.deepcopy(domains))
        return data

    def run(argv, label, caller=0, valid=True):
        result = subprocess.run([str(a) for a in argv], cwd=callers[caller],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
        (work / (label + '.log')).write_bytes(result.stdout)
        commands.append(dict(argv=[str(a) for a in argv], cwd=str(callers[caller]), status=result.returncode,
                             log=label + '.log'))
        assert (result.returncode == 0) == valid, (label, result.stdout[-3000:])
        return result

    def values(frozen):
        return {field['native_key']: field['stored'] for field in frozen.as_dict()['settings']['native'].values()}

    def reject(label, path, match=None):
        try:
            service.load_project(path)
        except (module.MigrationError, OSError, ValueError) as exc:
            if match:
                assert match in str(exc), (label, str(exc))
            rejected.append(label)
        else:
            raise AssertionError('Accepted invalid project: ' + label)
        assert values(service.load_project(valid_entry)) == expected[('wfi', 'local')]

    # Independent native/CLI references and shared scientific/recipe/product declarations.
    expected, projects = {}, {}
    shared = None
    shared_path = work / 'shared policies' / 'profiles.toml'
    for instrument in ('omegacam', 'wfi'):
        original = tomllib.loads((root / f'docs/architecture/proposed/m2/project-contracts/examples/{instrument}.toml').read_text())
        domains = {k: copy.deepcopy(v) for k, v in original.items() if k != 'project_schema_version'}
        domains['reduction_profile']['id'] = 'shared-purpose:scientific'
        domains['recipe']['id'] = 'shared-recipe:preprocess'
        domains['product_profile']['id'] = 'shared-product:legacy'
        projects[instrument] = domains
        candidate = {k: v for k, v in domains.items() if k not in ('project', 'processing', 'readout')}
        if shared is None:
            shared = candidate
            write(shared_path, envelope(shared))
        else:
            assert shared == candidate
        native_root = work / instrument / 'native settings'
        shutil.copytree(root / f'docs/architecture/proposed/m2/examples/{instrument}', native_root)
        original_paf = root / f'Pycavi2/pycavi/config/{instrument}.paf'
        cli_values = work / (instrument + '-local-reference.json')
        run([args.cli_probe, work / (instrument + '-request.json'), cli_values, callers[0],
             'mefpp', '--pafname', original_paf, '--biaskappa1', '0.123456789012345',
             '--scanrej', '2 3'], instrument + '-native-cli')
        for mode in ('full', 'entry', 'local'):
            expected[(instrument, mode)] = (json.loads(cli_values.read_text()) if mode == 'local'
                                             else expected_values(baseline, instrument))
            for layout in ('legacy-full', 'version2-full', 'split'):
                directory = work / instrument / (mode + ' ' + layout)
                entry = directory / 'project.toml'
                data = copy.deepcopy(domains)
                native = native_root / (mode + '.toml')
                if layout == 'split':
                    subset = directory / 'declarations' / 'instrument.toml'
                    data['processing']['native_configuration'] = os.path.relpath(native, subset.parent)
                    write(subset, envelope({k: data[k] for k in ('processing', 'readout')}))
                    write(entry, envelope({'project': data['project']},
                                         [os.path.relpath(shared_path, directory), 'declarations/instrument.toml']))
                else:
                    data['processing']['native_configuration'] = os.path.relpath(native, directory)
                    write(entry, envelope(data, version=1 if layout == 'legacy-full' else 2))
                frozen = service.load_project(entry)
                assert values(frozen) == expected[(instrument, mode)]
                snapshot = frozen.as_dict()['settings']['project']
                assert snapshot['native_validation'] == 'native-effective-settings-validated'
                assert snapshot['reference_validation'] == 'not_resolved'
                assert snapshot['execution_ready'] is False
                assert snapshot['product_compliance'] == 'not_validated'
                assert snapshot['resolved_roots']['raw'] == str((directory / data['project']['roots']['raw']).resolve())
                assert len({snapshot['configuration'][k]['id'] for k in ('reduction_profile', 'recipe', 'product_profile')}) == 3
                sources = frozen.as_dict()['sources']
                assert all(hashlib.sha256(s['text'].encode()).hexdigest() == s['sha256'] and
                           s['text'].encode() == Path(s['path']).read_bytes() for s in sources)
                if layout == 'split':
                    assert snapshot['project_domain_sources']['recipe']['source_file'] == str(shared_path)
                    assert snapshot['project_domain_sources']['processing']['source_file'] == str(subset)
                    assert sources[0]['resolved_include'] == [str(shared_path), str(subset)]
                native_sources = [s for s in sources if s['role'] == 'native-toml']
                assert len(native_sources) == {'full': 1, 'entry': 4, 'local': 5}[mode]
                if mode == 'local':
                    assert sum(d['native_key'] == 'MEF.BIAS.KAPPA1' for s in native_sources for d in s['definitions']) == 2
                if layout == 'split':
                    for caller in (0, 1):
                        destination = work / f'cli-{instrument}-{mode}-{caller}'
                        run([sys.executable, '-B', api, '--source-root', root, '--native-reader', args.reader,
                             'freeze-project', entry, '--output', destination],
                            f'cli-{instrument}-{mode}-{caller}', caller=caller)
                        assert (destination / 'configuration.json').read_bytes() == frozen.encoded
                        assert service.restore(destination / 'configuration.json') == frozen
                profiles.append(dict(instrument=instrument, mode=mode, layout=layout, identity=frozen.identity))

    # Existing native compatibility versions also flow through the C resolver;
    # the project never guesses units or decodes native numbers independently.
    for version in (1, 2):
        native = work / f'native compatibility {version}.toml'
        native.write_text(render_snapshot(expected[('wfi', 'full')]).replace('schema_version = 1', f'schema_version = {version}', 1))
        data = copy.deepcopy(projects['wfi'])
        data['processing']['native_configuration'] = str(native)
        project = write(work / f'compatibility project {version}.toml', envelope(data))
        assert values(service.load_project(project)) == expected[('wfi', 'full')]

    for instrument in ('omegacam', 'wfi'):
        example = root / f'docs/architecture/proposed/m2/project-composition-examples/{instrument}/project.toml'
        assert values(service.load_project(example)) == expected[(instrument, 'local')]

    valid_entry = work / 'wfi/local split/project.toml'
    # Identical domains coalesce, with every contribution retained. Relative roots
    # from a subset use that subset's directory, not the entry point or caller.
    fixture = work / 'policy cases'
    duplicate = write(fixture / 'identical.toml', envelope(shared))
    base = tomllib.loads(valid_entry.read_text())
    base['include'] = [str(shared_path), str(duplicate), str(work / 'wfi/local split/declarations/instrument.toml')]
    project_subset = write(fixture / 'roots' / 'project.toml', envelope({'project': base.pop('project')}))
    base['include'].append(str(project_subset))
    combined = write(fixture / 'entry.toml', base)
    record = service.load_project(combined)
    origins = record.as_dict()['provenance']['project_domain_sources']
    assert len(origins['recipe']['contributors']) == 2
    roots = record.as_dict()['settings']['project']['resolved_roots']
    assert roots['raw'] == str(project_subset.parent / projects['wfi']['project']['roots']['raw'])

    # Different declarations fail with both sources, even if a later local value
    # would match one sibling. There is no hidden project-domain last-wins rule.
    conflicting = copy.deepcopy(shared)
    conflicting['recipe']['id'] = 'different-recipe'
    write(duplicate, envelope(conflicting))
    reject('conflicting project domain', combined, 'Conflicting project domain recipe')
    write(duplicate, envelope(shared))
    base['recipe'] = conflicting['recipe']
    write(combined, base)
    reject('conflicting local domain', combined, 'Conflicting project domain recipe')
    del base['recipe']
    base['override_domains'] = ['recipe']
    write(combined, base)
    reject('forbidden project override declaration', combined, 'unknown project composition keys')
    del base['override_domains']
    write(combined, base)

    # Same relative processing text in different files has different authority/bases.
    a = write(fixture / 'a' / 'processing.toml', envelope({'processing': dict(schema_version=1,
              native_mode='legacy_reference', native_configuration='native.toml')}))
    b = write(fixture / 'b' / 'processing.toml', envelope({'processing': dict(schema_version=1,
              native_mode='legacy_reference', native_configuration='native.toml')}))
    bad = write(fixture / 'path conflict.toml', envelope({}, [str(a), str(b)]))
    reject('identical relative text with different path bases', bad, 'Conflicting project domain processing')

    # Closed envelope/domain versions, cycles, required fields and native/readout validation.
    for label, data, match in (
        ('unknown envelope', dict(base, unknown=True), 'unknown project composition keys'),
        ('unsupported envelope version', dict(base, project_schema_version=3), 'unsupported project_schema_version'),
        ('boolean envelope version', dict(base, project_schema_version=True), 'unsupported project_schema_version'),
        ('wrong include type', dict(base, include='one.toml'), 'invalid include array'),
        ('duplicate includes', dict(base, include=[str(shared_path), str(shared_path)]), 'duplicate include entry'),
        ('missing domain', envelope({'project': projects['wfi']['project']}), 'missing keys'),
        ('project include cycle', envelope({}, ['invalid.toml']), 'cycle'),
        ('legacy envelope includes', dict(envelope(projects['wfi'], version=1), include=[]), 'version 1 has no includes'),
    ):
        bad = write(fixture / 'invalid.toml', data)
        reject(label, bad, match)
    bad = write(fixture / 'invalid.toml', envelope({}, ['missing.toml']))
    reject('missing subset', bad)
    bad = write(fixture / 'invalid.toml', envelope({}, [str(work / 'wfi/full legacy-full/project.toml')]))
    reject('version 1 included subset', bad, 'included project subsets require version 2')
    malformed = copy.deepcopy(shared)
    malformed['recipe']['steps'][0]['unknown'] = 'bad'
    write(duplicate, envelope(malformed))
    reject('unknown domain leaf', combined, 'unknown keys')
    malformed = copy.deepcopy(shared)
    malformed['execution']['schema_version'] = 9
    write(duplicate, envelope(malformed))
    reject('unsupported domain version', combined, 'unsupported value')
    write(duplicate, envelope(shared))
    old_readout = copy.deepcopy(projects['wfi'])
    old_readout['processing']['native_configuration'] = str(work / 'wfi/native settings/local.toml')
    old_readout['readout']['detectors'][0]['channels'][0]['overscan']['region']['x_min'] += 1
    bad = write(fixture / 'invalid.toml', envelope(old_readout))
    reject('readout versus resolved native geometry', bad, 'legacy overscan endpoints differ')
    native_cycle = fixture / 'cycle native.toml'
    native_cycle.write_text('schema_version = 3\ninclude = ["cycle native.toml"]\n')
    old_readout = copy.deepcopy(projects['wfi'])
    old_readout['processing']['native_configuration'] = str(native_cycle)
    bad = write(fixture / 'invalid.toml', envelope(old_readout))
    reject('native cycle through project entry', bad, 'cycle')

    # Canonical include aliases and limits are checked without changing source
    # contents or weakening the native readout/override validation gate.
    alias = fixture / 'entry alias.toml'
    alias.symlink_to('entry.toml')
    record = service.load_project(alias)
    assert record.as_dict()['sources'][0]['path'] == str(combined)
    alias.unlink()
    alias.symlink_to('entry alias.toml')
    reject('filesystem symlink loop', alias, 'Cannot resolve project path')
    alias.unlink()
    cycle_a = write(fixture / 'cycle a.toml', envelope({}, ['cycle b.toml']))
    write(fixture / 'cycle b.toml', envelope({}, ['cycle a.toml']))
    reject('indirect project include cycle', cycle_a, 'cycle')
    deep = fixture / 'depth'
    for i in range(17):
        write(deep / f'{i}.toml', envelope({}, [f'{i+1}.toml'] if i < 16 else []))
    reject('project depth limit', deep / '0.toml', 'depth limit')
    wide = fixture / 'width'
    for i in range(64):
        write(wide / f'{i}.toml', envelope({}))
    write(wide / 'entry.toml', envelope({}, [f'{i}.toml' for i in range(64)]))
    reject('project file count limit', wide / 'entry.toml', 'file limit')
    native_bad = fixture / 'invalid native.toml'
    text = (work / 'wfi/native settings/full.toml').read_text()
    assert 'electron/adu' in text
    native_bad.write_text(text.replace('electron/adu', 'adu/electron', 1))
    data = copy.deepcopy(projects['wfi'])
    data['processing']['native_configuration'] = str(native_bad)
    bad = write(fixture / 'invalid.toml', envelope(data))
    reject('native units through project entry', bad, 'value/unit')
    native_bad.write_text(service.render({'MEF.USE.OVERSCAN': {'type': 'int', 'value': 0}},
                         includes=[str(work / 'wfi/native settings/full.toml')], overrides=['MEF.USE.OVERSCAN']))
    reject('resolved native override contradicts readout', bad, 'subtraction disagreement')
    source_text = shared_path.read_text()
    shared_path.write_bytes(source_text.replace('\n', '\r\n').encode())
    crlf = service.load_project(valid_entry)
    assert next(s for s in crlf.as_dict()['sources'] if s['path'] == str(shared_path))['text'].encode() == shared_path.read_bytes()

    # The complete record survives editing/deleting every private source; restore
    # verifies serialized data without attempting to rediscover those old files.
    frozen = service.load_project(valid_entry)
    unchanged = frozen.encoded
    mutated = frozen.as_dict()
    mutated['settings']['project']['configuration']['recipe']['steps'].clear()
    for source in frozen.as_dict()['sources']:
        Path(source['path']).unlink()
    assert frozen.encoded == unchanged
    assert frozen.as_dict()['settings']['project']['configuration']['recipe']['steps']
    saved = work / 'frozen configuration.json'
    saved.write_bytes(frozen.encoded)
    assert service.restore(saved) == frozen
    destination = work / 'failed CLI output'
    run([sys.executable, '-B', api, '--source-root', root, '--native-reader', args.reader,
         'freeze-project', valid_entry, '--output', destination], 'failed-cli', valid=False)
    assert not destination.exists()
    report = dict(profiles=profiles, rejections=rejected, commands=commands, source_root=str(root),
                  python=sys.version, reader_sha256=service.reader_sha256)
    (work / 'run-provenance.json').write_bytes(module.encode(report))
    print(f'PASS: {len(profiles)} complete/split/local OCAM/WFI project profiles; native CLI values exact')
    print('PASS: shared domains, relative bases, all source graphs, CLI/library equality and frozen restore')
    print(f'PASS: {len(rejected)} rejection/recovery controls; failed CLI creates no output')
    print('REPORT:', work / 'run-provenance.json')


if __name__ == '__main__':
    main()
