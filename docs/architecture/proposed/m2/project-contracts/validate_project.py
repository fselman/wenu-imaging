"""Closed authoring contract. No scientific defaults, FITS access or execution.

This review-layer validator does not replace the accepted native reader. A native
reference is one complete schema-3 file; native numeric qualification is a
separate gate. All source bytes and hashes are frozen before returning.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
import tomllib

MAX_BYTES = 4 * 1024 * 1024
CATALOG = Path(__file__).with_name('catalog.json')


class ContractError(ValueError):
    pass


def require(condition, path, message):
    if not condition:
        raise ContractError(f'{path}: {message}')


def check(value, spec, path):
    kind = spec['type']
    if kind == 'table':
        require(type(value) is dict, path, 'expected table')
        fields = spec['fields']
        require(not value.keys() - fields.keys(), path,
                f'unknown keys: {sorted(value.keys() - fields.keys())}')
        missing = fields.keys() - value.keys() - set(spec['optional'])
        require(not missing, path, f'missing keys: {sorted(missing)}')
        for key, item in value.items():
            check(item, fields[key], f'{path}.{key}')
    elif kind == 'array':
        require(type(value) is list, path, 'expected array')
        require(spec['minimum'] <= len(value) <= spec['maximum'], path, 'array length outside contract')
        for i, item in enumerate(value):
            check(item, spec['items'], f'{path}[{i}]')
    else:
        expected = dict(string=str, integer=int, boolean=bool)[kind]
        require(type(value) is expected, path, f'expected {kind}, no coercion')
        if kind == 'string':
            require(bool(value.strip()) and all(ord(c) >= 32 and ord(c) != 127 for c in value),
                    path, 'empty/control text is not allowed')
        if 'enum' in spec:
            require(value in spec['enum'], path, f'unsupported value {value!r}')
        for bound in ('minimum', 'maximum'):
            if bound in spec:
                require(value >= spec[bound] if bound == 'minimum' else value <= spec[bound],
                        path, f'outside {bound}')


def region_check(region, path):
    require(region['x_min'] <= region['x_max'], path, 'reversed x endpoints')
    require(('y_min' in region) == ('y_max' in region), path, 'both y endpoints required or both omitted')
    if 'y_min' in region:
        require(region['y_min'] <= region['y_max'], path, 'reversed y endpoints')


def overlaps(a, b):
    x = max(a['x_min'], b['x_min']) <= min(a['x_max'], b['x_max'])
    # Missing y denotes all rows in the selected readout channel, not a guess
    # at actual FITS dimensions. Bounds/layout applicability remains M4.
    y = ('y_min' not in a or 'y_min' not in b or
         max(a['y_min'], b['y_min']) <= min(a['y_max'], b['y_max']))
    return x and y


def unique(values, path):
    require(len(values) == len(set(values)), path, 'duplicate identity')


def validate(data, catalog=None):
    if catalog is None:
        catalog = json.loads(CATALOG.read_text())
    check(data, catalog['schema'], 'project')
    ids = [data[k]['id'] for k in ('project', 'reduction_profile', 'recipe', 'product_profile', 'readout')]
    unique(ids, 'profile/recipe/project/readout IDs')
    unique([s['id'] for s in data['recipe']['steps']], 'recipe.steps')
    bindings = data['association']['bindings']
    unique([(b['group'], b['role']) for b in bindings], 'association.bindings')
    for b in bindings:
        selected = b['selection'] == 'selected'
        require(('asset_id' in b) == selected and ('asset_version' in b) == selected,
                'association.bindings', 'selected requires exact asset ID/version; omitted forbids them')
    readout = data['readout']
    detectors = readout['detectors']
    unique([d['id'] for d in detectors], 'readout.detectors')
    unique([d['legacy_ordinal'] for d in detectors if 'legacy_ordinal' in d], 'legacy ordinals')
    evidence = readout['header_evidence']
    unique([(e['asset_id'], e['asset_version'], e['hdu'], e['card_index']) for e in evidence],
           'readout.header_evidence')
    for item in evidence:
        require(item['detector_id'] in {d['id'] for d in detectors}, 'header_evidence', 'unknown local detector reference')
        require(len(item['raw_card']) == 80 and all(32 <= ord(c) <= 126 for c in item['raw_card']),
                'header_evidence', 'retain one exact 80-byte ASCII FITS card; do not reinterpret it')
    physical = []
    for d in detectors:
        path = f'readout.{d["id"]}'
        require(('physical_detector_id' in d) == (d['identity_status'] == 'verified'),
                path, 'verified detector identity requires ID; unknown forbids an invented ID')
        if 'physical_detector_id' in d:
            physical.append(d['physical_detector_id'])
        channels = d['channels']
        unique([c['id'] for c in channels], path)
        unique([c['physical_amplifier_id'] for c in channels if 'physical_amplifier_id' in c], path)
        require(any(c['active'] for c in channels), path, 'at least one selected active channel required')
        signals = []
        for c in channels:
            cp = f'{path}.{c["id"]}'
            require(('physical_amplifier_id' in c) == (c['identity_status'] == 'verified'),
                    cp, 'verified amplifier identity requires ID; unknown forbids an invented ID')
            o = c['overscan']
            require(('region' in o) == (o['state'] == 'defined'), cp, 'defined requires region; absent forbids region')
            require(not o['subtract'] or (c['active'] and o['state'] == 'defined'),
                    cp, 'subtraction requires active channel with defined overscan')
            if 'region' in o:
                region_check(o['region'], cp + '.overscan')
            if 'signal' in c:
                region_check(c['signal'], cp + '.signal')
                if c['active']:
                    signals.append(c['signal'])
        # Same detector coordinate system: all active signal regions must be
        # disjoint, including other channels' overscan. Never share one side
        # implicitly across two simultaneously active amplifier channels.
        for i, a in enumerate(signals):
            require(all(not overlaps(a, b) for b in signals[i+1:]), path, 'active signal regions overlap')
            for c in channels:
                if c['active'] and c['overscan']['state'] == 'defined':
                    require(not overlaps(a, c['overscan']['region']), path, 'signal overlaps active overscan')
        if sum(c['active'] for c in channels) > 1:
            require(all('signal' in c for c in channels if c['active']), path,
                    'multi-channel readout requires explicit signal regions')
    unique(physical, 'physical detector IDs')
    if readout['mapping_status'] == 'verified':
        require(all(d['identity_status'] == 'verified' and all(c['identity_status'] == 'verified'
                for c in d['channels'] if c['active']) for d in detectors),
                'readout', 'verified mapping requires verified selected detector/amplifier identities')
    processing = data['processing']
    require(('native_configuration' in processing) == (processing['native_mode'] == 'legacy_reference'),
            'processing', 'legacy_reference requires native file; unavailable forbids fallback file')


def native_consistency(data, native):
    """Only check the bridge fields; the existing C reader owns native validation."""
    require(native.get('schema_version') == 3 and not native.get('include') and not native.get('override_keys'),
            'native', 'bridge reference must be one complete standalone version-3 file')
    try:
        count = native['instrument']['detector_count']['value']
        native_detectors = native['instrument']['detectors']
        use = native['processing']['use_overscan']['value']
        require(type(count) is int and type(use) is int and use in (0, 1), 'native', 'invalid bridge count/overscan flag')
        detectors = data['readout']['detectors']
        require(len(detectors) == count and {d.get('legacy_ordinal') for d in detectors} == set(range(1, count+1)),
                'native', 'exact legacy detector ordinal coverage required')
        require(set(native_detectors) == {f'CHIP{i}' for i in range(1, count+1)}, 'native', 'unexpected native detector coverage')
        for d in detectors:
            active = [c for c in d['channels'] if c['active']]
            require(len(active) == 1, 'native', 'legacy bridge supports one active channel per detector only')
            o = active[0]['overscan']
            require(o['subtract'] == bool(use), 'native', 'readout/native subtraction disagreement')
            # Legacy constructors require geometry even when scan correction is
            # disabled. Do not silently fill missing regions with zero/sentinels.
            require(o['state'] == 'defined', 'native', 'legacy reference still requires its retained geometry')
            region = o['region']
            require('y_min' not in region, 'native', 'legacy overscan is an x strip over all channel rows')
            n = native_detectors[f'CHIP{d["legacy_ordinal"]}']
            require((region['x_min'], region['x_max']) == (n['overscan_x_min']['value'], n['overscan_x_max']['value']),
                    'native', 'legacy overscan endpoints differ')
    except (KeyError, TypeError) as exc:
        raise ContractError(f'native: missing/invalid bridge fields: {exc}') from exc


@dataclass(frozen=True)
class FrozenProject:
    """Owned serialized bytes: caller edits cannot redefine the loaded request."""
    encoded: bytes

    def as_dict(self):
        return json.loads(self.encoded)


def read_source(path):
    require(path.is_file(), str(path), 'expected regular source file')
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, str(path), 'source size limit exceeded')
    return raw


def load(path):
    path = Path(path).resolve(strict=True)
    raw = read_source(path)
    data = tomllib.loads(raw.decode('utf-8'))
    catalog_raw = read_source(CATALOG)
    validate(data, json.loads(catalog_raw))
    sources = [dict(role='project', path=str(path), sha256=hashlib.sha256(raw).hexdigest(),
                    text=raw.decode('utf-8'))]
    native_status = 'unavailable'
    if data['processing']['native_mode'] == 'legacy_reference':
        native_path = (path.parent / data['processing']['native_configuration']).resolve(strict=True)
        native_raw = read_source(native_path)
        native_consistency(data, tomllib.loads(native_raw.decode('utf-8')))
        sources.append(dict(role='native', path=str(native_path), sha256=hashlib.sha256(native_raw).hexdigest(),
                            text=native_raw.decode('utf-8')))
        native_status = 'reference-consistent-not-native-validated'
    roots = {k: str((path.parent / v).resolve()) for k, v in data['project']['roots'].items()}
    snapshot = dict(notation='wenu-project-authoring-snapshot-1', configuration=data,
                    validation_catalog_sha256=hashlib.sha256(catalog_raw).hexdigest(),
                    resolved_roots=roots, sources=sources, native_validation=native_status,
                    execution_ready=False, reference_validation='not_resolved',
                    header_metadata_review=('pending' if data['readout']['header_evidence'] else 'not_supplied'),
                    product_compliance='not_validated',
                    wad_validation='review-crosswalk-only')
    return FrozenProject(json.dumps(snapshot, sort_keys=True, ensure_ascii=False,
                                   allow_nan=False, separators=(',', ':')).encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    try:
        result = load(args.project)
    except (ContractError, OSError, ValueError, RecursionError) as exc:
        print(f'INVALID: {exc}', file=sys.stderr)
        return 1
    print(result.encoded.decode('utf-8'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
