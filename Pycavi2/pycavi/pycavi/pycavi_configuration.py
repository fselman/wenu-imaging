"""Opt-in configuration migration and immutable requests (Python 3.11+).

The native configuration bridge is explicit. This module never executes a
reduction, changes cwd, searches for calibrations or activates an installation.
CLI and library callers receive the same owned, WAD-checked configuration record.
"""
from __future__ import annotations

import argparse
import configparser
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import tomllib

MAX_BYTES = 4 * 1024 * 1024
MAX_DETECTORS = 4096  # Migration resource policy, not a detector/algorithm default.


class MigrationError(ValueError):
    def __init__(self, message, ledger=None):
        super().__init__(message)
        self.ledger = ledger


def require(condition, message):
    if not condition:
        raise MigrationError(message)


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      separators=(',', ':')).encode('utf-8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_source(path, role, limit=MAX_BYTES):
    path = Path(path).resolve(strict=True)
    require(path.is_file(), f'{path}: expected a regular configuration file')
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit and b'\0' not in raw, f'{path}: size/NUL limit')
    return dict(path=str(path), role=role, text=raw.decode('utf-8'), sha256=digest(raw))


def stored_literal(entry):
    kind, value = entry['type'], entry['value']
    if kind == 'string':
        require(type(value) is str and '\0' not in value and len(value.encode('utf-8')) <= 80, 'Invalid native string')
        return json.dumps(value, ensure_ascii=False)
    if kind == 'int':
        require(type(value) is int and -(2**31) <= value < 2**31, 'Invalid native integer')
        return str(value)
    require(kind in ('float32-bits', 'float64-bits'), 'Unknown native storage kind')
    require(type(value) is str and re.fullmatch(r'[0-9a-f]{%d}' % (8 if kind == 'float32-bits' else 16), value) is not None,
            'Invalid native floating-point bits')
    number, = struct.unpack('>f' if kind == 'float32-bits' else '>d', bytes.fromhex(value))
    require(math.isfinite(number), 'Nonfinite native setting')
    return repr(number)


@dataclass(frozen=True)
class FrozenConfiguration:
    """Immutable bytes; inspection returns fresh objects and performs no I/O."""
    encoded: bytes

    def __post_init__(self):
        require(type(self.encoded) is bytes, 'Frozen configuration requires immutable bytes')

    def as_dict(self):
        return json.loads(self.encoded)

    @property
    def identity(self):
        return digest(self.encoded)

    def plan_fragment(self):
        """Configuration portion only; executable task plans belong to M3–M9."""
        record = self.as_dict()
        return dict(configuration=record['record_id'], configuration_record=record,
                    configuration_sha256=self.identity, execution_ready=False)


class ConfigurationMigration:
    """Source-checkout resource boundary; no installed/stable ABI is claimed."""
    def __init__(self, source_root, native_reader):
        self.root = Path(source_root).resolve(strict=True)
        reader = Path(native_reader)
        require(reader.is_absolute(), 'Supply an explicit absolute native-reader path')
        self.reader = reader.resolve(strict=True)
        require(self.reader.is_file(), 'Native reader must be a regular executable')
        self.resources = [read_source(self.root / path, 'migration-contract') for path in (
            'docs/architecture/proposed/m2/typed-field-catalog.json',
            'docs/architecture/proposed/m0-m0a/configuration-ledger.json',
            'docs/architecture/proposed/m0-m0a/contract-catalog.json')]
        self.catalog, self.ledger, self.wad = [json.loads(s['text']) for s in self.resources]
        self.reader_sha256 = digest(self.reader.read_bytes())

    def field(self, key):
        for field in self.catalog['fields']:
            match = re.fullmatch(re.escape(field['native_pattern']).replace('%d', '([1-9][0-9]*)'), key)
            if match:
                item = dict(field)
                item['path'] = (item['path_pattern'] % int(match[1]) if match.groups()
                                else item['path_pattern'])
                return item
        raise MigrationError(f'Uncatalogued native key: {key}')

    def render(self, settings, includes=(), overrides=()):
        """Write stored C values, never decode raw PAF numbers or add defaults."""
        tree = {}
        for key, value in settings.items():
            field = self.field(key)
            parts = field['path'].split('.')
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = (value, field['unit'])
        lines = ['# Migrated native stored values; no new scientific defaults.',
                 'schema_version = 3', 'include = ' + json.dumps(list(includes)),
                 'override_keys = ' + json.dumps([self.field(k)['path'] for k in overrides])]

        def table(node, parts):
            lines.extend(['', '[' + '.'.join(parts) + ']'])
            if len(parts) == 1:
                lines.append('schema_version = 1')
            for key, value in node.items():
                if isinstance(value, tuple):
                    entry, unit = value
                    lines.append(f'{key} = {{ value = {stored_literal(entry)}, unit = {json.dumps(unit)} }}')
            for key, value in node.items():
                if isinstance(value, dict):
                    table(value, parts + [key])
        for key, node in tree.items():
            table(node, [key])
        result = '\n'.join(lines) + '\n'
        tomllib.loads(result)
        return result

    def native(self, mode, path):
        # Capture bounded metadata only. Process isolation is the legacy PAF
        # allocator/parser boundary, not a call to the numerical mefpp engine.
        with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            result = subprocess.run([str(self.reader), mode, str(path)], stdout=output,
                                    stderr=errors, timeout=120, check=False)
            output.seek(0); errors.seek(0)
            raw = output.read(128 * MAX_BYTES + 1)
            diagnostic = errors.read(16384).decode('utf-8', errors='replace')
        require(result.returncode == 0, f'Native {mode} validation failed: {diagnostic}')
        require(len(raw) <= 128 * MAX_BYTES, 'Native metadata report limit')
        document = json.loads(raw)
        require(set(document) == {'settings', 'sources'}, 'Unsupported native bridge report')
        return document

    def freeze(self, settings, sources, provenance, project=None, cfg=None):
        # Runtime validation is deliberately scoped to the WAD configuration
        # attributes, not unresolved images/assets/tasks or future ASDF schemas.
        count = settings.get('MEF.NCHIPS', {}).get('value')
        require(type(count) is int and 0 < count <= MAX_DETECTORS, 'Invalid native detector count')
        expected_keys = set()
        for field in self.catalog['fields']:
            pattern = field['native_pattern']
            if '%d' in pattern:
                expected_keys.update(pattern % i for i in range(1, count + 1))
            else:
                expected_keys.add(pattern)
        require(set(settings) == expected_keys, 'Incomplete/extra native configuration settings')
        for source in sources:
            require(digest(source['text'].encode('utf-8')) == source['sha256'], 'Source text/hash mismatch')
        fields = {}
        for key, value in settings.items():
            field = self.field(key)
            expected = dict(int32='int', float32='float32-bits', float64='float64-bits', string='string')
            require(value['type'] == expected[field['storage']], f'{key}: storage mismatch')
            stored_literal(value)
            fields[field['path']] = dict(native_key=key, storage=field['storage'],
                                         unit=field['unit'], role=field['role'], stored=value)
        require(set(self.wad['record_types']['configuration']) == {'settings', 'sources', 'compatibility'},
                'Unsupported WAD configuration attributes')
        data = dict(kind='configuration', logical_id='', version=1, record_id='',
                    settings=dict(native=fields, project=project, legacy_cfg=cfg or []),
                    sources=sources, compatibility='legacy-native-stored-values-v1',
                    provenance=provenance, execution_ready=False,
                    wad_validation='configuration-attributes-checked',
                    wad_contract_sha256=self.resources[2]['sha256'])
        require(type(data['settings']) is dict and type(data['sources']) is list and
                type(data['compatibility']) is str, 'Invalid WAD configuration attributes')
        identity = digest(encode(data))
        data['logical_id'] = 'configuration:' + identity
        data['record_id'] = data['logical_id'] + '@1'
        return FrozenConfiguration(encode(data))

    def load_toml(self, path):
        document = self.native('toml', Path(path).resolve(strict=True))
        meta = document['sources']
        require(meta.get('files') and set(meta['fields']) == set(document['settings']),
                'Reader lacks frozen sources or field coverage')
        sources = []
        paths = set()
        for file in meta['files']:
            require(file['path'] not in paths, 'Duplicate frozen source identity')
            paths.add(file['path'])
            raw = file['text'].encode('utf-8')
            sources.append(dict(file, role='native-toml', sha256=digest(raw)))
        for key, field in meta['fields'].items():
            expected = self.field(key)
            require(all(field[name] == expected[name] for name in ('path', 'storage', 'unit', 'role')),
                    f'{key}: compiled/documented catalog mismatch')
            require(field['source_file'] in paths, f'{key}: missing winning source')
            field['source_sha256'] = next(s['sha256'] for s in sources if s['path'] == field['source_file'])
        provenance = dict(native_sources=meta['fields'],
                          native_reader_sha256=self.reader_sha256,
                          contracts=[dict(path=s['path'], sha256=s['sha256']) for s in self.resources])
        return self.freeze(document['settings'], sources, provenance)

    def paf_ledger(self, source, resolutions):
        entries = []
        groups = {}
        for line, text in enumerate(source['text'].splitlines(), 1):
            require(len(text.encode('utf-8')) < 1023, f'PAF line {line}: legacy line limit')
            if not text.strip() or text.lstrip().startswith('#'):
                continue
            match = re.fullmatch(r'([A-Za-z0-9_.]+)[ \t]+([^;]*);(?:[ \t]*(?:#.*)?)?', text)
            require(match is not None, f'PAF line {line}: ambiguous/unsupported syntax; review before migration')
            key, literal = match.groups()
            entry = dict(line=line, key=key, literal=literal.strip(), text=text)
            entries.append(entry); groups.setdefault(key, []).append(entry)
        require(entries and entries[0]['key'] == 'PAF.HDR.START', 'Missing PAF header')
        known = {e['key'] for e in self.ledger['paf_entries']}
        headers = {'PAF.HDR.START', 'PAF.HDR.END', 'PAF.TYPE', 'PAF.ID', 'PAF.NAME', 'PAF.DESC',
                   'PAF.CRTE.NAME', 'PAF.CRTE.DAYTIM', 'PAF.LCHG.NAME', 'PAF.LCHG.DAYTIM', 'PAF.CHCK.CHECKSUM'}
        for key in groups:
            if key not in known | headers:
                self.field(key)  # A new per-detector ordinal must still be catalogued.
        conflicts, duplicates, selected = [], [], {}
        require(type(resolutions) is dict, 'Resolutions must map exact keys to source line numbers')
        for key, occurrences in groups.items():
            chosen = occurrences[0]
            if len(occurrences) > 1:
                same = len({e['literal'] for e in occurrences}) == 1
                duplicate = dict(key=key, identical=same, occurrences=occurrences)
                duplicates.append(duplicate)
                if not same:
                    if key not in resolutions:
                        conflicts.append(duplicate)
                    else:
                        require(type(resolutions[key]) is int, 'Resolution line must be an integer')
                        matches = [e for e in occurrences if e['line'] == resolutions[key]]
                        require(len(matches) == 1, f'{key}: resolution must select an actual source occurrence')
                        chosen = matches[0]
            selected[key] = chosen
        ledger = dict(entries=entries, duplicates=duplicates, resolutions=resolutions,
                      conflicts=conflicts, selected=selected)
        if conflicts:
            raise MigrationError('Conflicting PAF definitions require explicit source-line resolution: ' +
                                 ', '.join(c['key'] for c in conflicts), ledger)
        require(set(resolutions) <= {d['key'] for d in duplicates if not d['identical']},
                'Unused/identical/nonconflicting PAF resolution')
        count = selected.get('MEF.NCHIPS', {}).get('literal', '')
        require(re.fullmatch(r'[+]?[0-9]+', count) is not None and 0 < int(count) <= MAX_DETECTORS,
                'Missing/invalid detector count or migration resource limit')
        consumed = set()
        for field in self.catalog['fields']:
            pattern = field['native_pattern']
            consumed.update(pattern % i for i in range(1, int(count) + 1)) if '%d' in pattern else consumed.add(pattern)
        require(not consumed - selected.keys(), 'Missing required PAF keys: ' + ', '.join(sorted(consumed - selected.keys())))
        ledger['unconsumed_keys'] = sorted(set(selected) - consumed)
        # The unchanged decoder sees one explicitly selected occurrence per key.
        canonical = '\n'.join(e['text'] for e in entries if selected[e['key']] is e) + '\n'
        return ledger, canonical

    def cfg(self, path, role):
        require(role in ('instrument', 'project'), 'Unknown CFG role')
        source = read_source(path, 'legacy-' + role + '-cfg')
        parser = configparser.ConfigParser(inline_comment_prefixes=('#',) if role == 'instrument' else None)
        parser.read_string(source['text'])
        require(not parser.defaults(), 'CFG DEFAULT inheritance requires separate explicit review')
        template = 'omegacam.cfg' if role == 'instrument' else 'pycavi.cfg'
        allowed = {(e['section'], e['option']) for e in self.ledger['cfg_entries']
                   if Path(e['file']).name in (('omegacam.cfg', 'wfi.cfg') if role == 'instrument' else (template,))}
        destinations = {'General': 'execution', 'Provenance': 'project', 'Directories': 'project.roots',
                        'Project': 'instrument', 'Data': 'instrument', 'Primary Keywords': 'association.metadata',
                        'Extension Keywords': 'instrument.detectors'}
        values = []
        for section in parser.sections():
            require(section in destinations, f'Unknown CFG section: {section}')
            for option in parser[section]:
                require((section, option) in allowed, f'Unknown CFG option: {section}.{option}')
                value = parser.get(section, option)
                values.append(dict(section=section, option=option, value=value,
                                   raw_value=parser.get(section, option, raw=True),
                                   destination=destinations[section], status='retained-not-executed'))
        return source, dict(role=role, path=source['path'], values=values,
                            semantics='legacy ConfigParser strings; no defaults or path authority inferred')

    def migrate_paf(self, path, *, resolutions=None, cfg_files=()):
        source = read_source(path, 'legacy-paf')
        ledger, canonical = self.paf_ledger(source, resolutions or {})
        # Snapshot source bytes before native reads: a concurrent original edit
        # cannot change this import. Never repair or overwrite the original PAF.
        with tempfile.TemporaryDirectory(prefix='wenu migration ') as work:
            work = Path(work)
            paf = work / 'selected.paf'; paf.write_bytes(canonical.encode('utf-8'))
            native = self.native('paf', paf)['settings']
            text = self.render(native)
            toml = work / 'converted.toml'; toml.write_bytes(text.encode('utf-8'))
            roundtrip = self.native('toml', toml)['settings']
        require(roundtrip == native, 'STOP: native PAF/TOML stored values differ')
        sources = [source]
        cfg = []
        for role, cfg_path in cfg_files:
            cfg_source, cfg_record = self.cfg(cfg_path, role)
            require(role not in {c['role'] for c in cfg}, f'Duplicate CFG role: {role}')
            sources.append(cfg_source); cfg.append(cfg_record)
        field_sources = {}
        for key in native:
            selected = ledger['selected'][key]
            field_sources[key] = dict(path=source['path'], sha256=source['sha256'],
                                      source_line=selected['line'], source_literal=selected['literal'])
        provenance = dict(migration='PAF-to-native-domain-3', ledger=ledger,
                          native_sources=field_sources, native_reader_sha256=self.reader_sha256,
                          converted_toml_sha256=digest(text.encode('utf-8')),
                          exact_stored_value_comparison=True,
                          contracts=[dict(path=s['path'], sha256=s['sha256']) for s in self.resources])
        return self.freeze(native, sources, provenance, cfg=cfg), text

    def _project_contract(self):
        # Reuse the accepted domain schema/semantic checks. Composition is a new
        # envelope; it does not fork domain defaults, native parsing or readout math.
        resource = self.root / 'docs/architecture/proposed/m2/project-contracts/validate_project.py'
        spec = importlib.util.spec_from_file_location('wenu_m2_project_contract', resource)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        catalog = read_source(module.CATALOG, 'project-contract')
        return module, catalog, json.loads(catalog['text'])

    def _compose_project(self, path, validator, catalog):
        # Explicit first envelope: disjoint/identical project domains only.
        # Project-domain override allowlist is empty. Numeric overrides remain
        # entirely in the already qualified native schema-2/3 resolver.
        fields = catalog['schema']['fields']
        domains = set(fields) - {'project_schema_version'}
        files, cached, active = [], {}, set()

        def scoped(domain, value, source):
            # Identical relative text from different containing files need not
            # identify the same root/reference. Compare its declared path base too.
            value = json.loads(encode(value))
            if domain == 'project':
                value['roots'] = {k: str(resolve(source.parent / v, strict=False))
                                  for k, v in value['roots'].items()}
            if domain == 'processing' and value['native_mode'] == 'legacy_reference':
                value['native_configuration'] = str(resolve(source.parent / value['native_configuration'], strict=False))
            return encode(value)

        def resolve(member, strict=True):
            try:
                return Path(member).resolve(strict=strict)
            except RuntimeError as exc:
                raise MigrationError(f'Cannot resolve project path {member}: {exc}') from exc

        def load(member, depth):
            require(depth < 16, 'Project composition depth limit')
            member = resolve(member)
            key = str(member)
            require(key not in active, f'Project include cycle: {member}')
            if key in cached:
                return cached[key]
            require(len(files) < 64, 'Project composition file limit')
            source = read_source(member, 'project-toml')
            data = tomllib.loads(source['text'])
            version = data.get('project_schema_version')
            require(type(version) is int and version in (1, 2),
                    f'{member}: unsupported project_schema_version')
            require(not depth or version == 2, f'{member}: included project subsets require version 2')
            require(version == 2 or 'include' not in data, f'{member}: version 1 has no includes')
            require(not data.keys() - domains - {'project_schema_version', 'include'},
                    f'{member}: unknown project composition keys')
            includes = data.get('include', [])
            require(type(includes) is list and len(includes) <= 64 and
                    all(type(v) is str and v.strip() and all(ord(c) >= 32 and ord(c) != 127 for c in v)
                        for v in includes), f'{member}: invalid include array')
            require(len(includes) == len(set(includes)), f'{member}: duplicate include entry')
            local = {domain: value for domain, value in data.items() if domain in domains}
            for domain, value in local.items():
                validator.check(value, fields[domain], f'{member}:{domain}')
            source.update(input_schema_version=version, include=includes,
                          resolved_include=[], definitions=list(local))
            files.append(source)
            active.add(key)
            merged = {}

            def insert(domain, binding):
                if domain in merged:
                    old = merged[domain]
                    require(old['scoped'] == binding['scoped'],
                            f'Conflicting project domain {domain}: {old["source"]} versus {binding["source"]}; '
                            'choose one explicit domain subset; project replacements are forbidden')
                else:
                    merged[domain] = binding

            for relative in includes:
                child = resolve(member.parent / relative)
                source['resolved_include'].append(str(child))
                for domain, binding in load(child, depth + 1).items():
                    insert(domain, binding)
            for domain, value in local.items():
                insert(domain, dict(value=value, source=key, sha256=source['sha256'],
                                    scoped=scoped(domain, value, member)))
            active.remove(key)
            cached[key] = merged
            return merged

        bindings = load(path, 0)
        # Envelope v2 resolves to the already versioned domain-v1 configuration.
        # All leaf checks, cross-domain IDs and readout rules stay authoritative.
        effective = dict(project_schema_version=1, **{k: v['value'] for k, v in bindings.items()})
        validator.validate(effective, catalog)
        origins = {}
        for domain, binding in bindings.items():
            origins[domain] = dict(source_file=binding['source'], source_sha256=binding['sha256'],
                                   source_key=domain, selection='first-identical-domain-origin',
                                   contributors=[dict(path=f['path'], sha256=f['sha256'])
                                                 for f in files if domain in f['definitions']])
        roots = {k: str(resolve(Path(bindings['project']['source']).parent / value, strict=False))
                 for k, value in effective['project']['roots'].items()}
        processing = effective['processing']
        require(processing['native_mode'] == 'legacy_reference',
                'Project has no native settings; configuration remains unavailable')
        native_path = resolve(Path(bindings['processing']['source']).parent / processing['native_configuration'])
        return effective, files, origins, roots, native_path

    def load_project(self, path):
        validator, catalog_source, catalog = self._project_contract()
        data, project_sources, origins, roots, native_path = self._compose_project(path, validator, catalog)
        # The C reader captures every actual native subset and owns resolution;
        # do not reread mutable TOML, flatten before capture, or recreate defaults.
        native_record = self.load_toml(native_path).as_dict()
        settings = {field['native_key']: field['stored']
                    for field in native_record['settings']['native'].values()}
        normalized_native = tomllib.loads(self.render(settings))
        validator.native_consistency(data, normalized_native)
        sources = project_sources + native_record['sources']
        project = dict(notation='wenu-project-configuration-snapshot-2', configuration=data,
                       validation_catalog_sha256=catalog_source['sha256'],
                       resolved_roots=roots, sources=sources,
                       project_domain_sources=origins,
                       native_validation='native-effective-settings-validated',
                       execution_ready=False, reference_validation='not_resolved',
                       header_metadata_review=('pending' if data['readout']['header_evidence'] else 'not_supplied'),
                       product_compliance='not_validated', wad_validation='configuration-attributes-checked')
        provenance = dict(native_record['provenance'],
                          project_catalog_sha256=catalog_source['sha256'],
                          project_domain_sources=origins,
                          project_composition=dict(versions=[1, 2], domain_schema_version=1,
                                                   override_allowlist=[], conflicts='reject'))
        return self.freeze(settings, sources, provenance, project=project)


    def restore(self, path):
        """Verify a saved configuration without reopening any input/settings file."""
        data = json.loads(read_source(path, 'frozen-configuration', limit=128 * MAX_BYTES)['text'])
        for source in data['sources']:
            require(digest(source['text'].encode('utf-8')) == source['sha256'],
                    'Frozen source hash mismatch')
        settings = {field['native_key']: field['stored'] for field in data['settings']['native'].values()}
        frozen = self.freeze(settings, data['sources'], data['provenance'],
                             data['settings']['project'], data['settings']['legacy_cfg'])
        require(frozen.as_dict() == data, 'Frozen identity/schema/settings mismatch')
        return frozen


def publish_bundle(destination, files):
    """Exclusive new directory, never overwrite a prior request or source file."""
    destination = Path(destination)
    destination.mkdir()  # Parent must exist; EEXIST is a refusal, not a retry.
    for name, raw in files.items():
        with (destination / name).open('xb') as stream:
            stream.write(raw)
    # A final receipt distinguishes complete publication from an interrupted one.
    with (destination / 'COMPLETE.json').open('xb') as stream:
        stream.write(encode({name: digest(raw) for name, raw in files.items()}))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--native-reader', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    migrate = sub.add_parser('migrate-paf')
    migrate.add_argument('path', type=Path)
    migrate.add_argument('--resolve', action='append', default=[], metavar='KEY=LINE')
    migrate.add_argument('--instrument-cfg', type=Path)
    migrate.add_argument('--project-cfg', type=Path)
    migrate.add_argument('--output', type=Path, required=True)
    for name in ('freeze-toml', 'freeze-project'):
        command = sub.add_parser(name)
        command.add_argument('path', type=Path)
        command.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        service = ConfigurationMigration(args.source_root, args.native_reader)
        if args.command == 'migrate-paf':
            resolutions = {}
            for item in args.resolve:
                key, line = item.rsplit('=', 1)
                require(key not in resolutions, f'Duplicate resolution for {key}')
                resolutions[key] = int(line)
            cfg = [(role, path) for role, path in (('instrument', args.instrument_cfg),
                                                  ('project', args.project_cfg)) if path is not None]
            frozen, text = service.migrate_paf(args.path, resolutions=resolutions, cfg_files=cfg)
            files = {'configuration.toml': text.encode('utf-8')}
        else:
            frozen = (service.load_toml(args.path) if args.command == 'freeze-toml'
                      else service.load_project(args.path))
            files = {}
        files['configuration.json'] = frozen.encoded
        files['plan-configuration.json'] = encode(frozen.plan_fragment())
        publish_bundle(args.output, files)
        print(f'CONFIGURATION: {frozen.identity}\nOUTPUT: {args.output}')
        return 0
    except (MigrationError, OSError, ValueError, KeyError, TypeError, configparser.Error, subprocess.SubprocessError) as exc:
        print(f'INVALID: {exc}', file=sys.stderr)
        if isinstance(exc, MigrationError) and exc.ledger is not None:
            print(encode(exc.ledger).decode('utf-8'), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
