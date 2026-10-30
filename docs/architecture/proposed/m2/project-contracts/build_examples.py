"""Reproducible authoring examples. Project/asset identities are review labels.

Legacy geometry comes from the accepted complete native examples. No physical
amplifier count/identity, readout mode or FITS applicability is inferred.
"""
import json
from pathlib import Path
import tomllib

BASE = Path(__file__).parent


def scalar(value):
    if type(value) is bool:
        return str(value).lower()
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return json.dumps(value, ensure_ascii=False)
    if type(value) is list and not value:
        return '[]'
    raise TypeError(value)


def render(data):
    lines = ['# Authoring validation only; no execution or physical hardware qualification.']
    def table(node, path=(), array=False):
        if path:
            lines.extend(['', ('[[' if array else '[') + '.'.join(path) + (']]' if array else ']')])
        for k, v in node.items():
            if not isinstance(v, dict) and not (isinstance(v, list) and v):
                lines.append(f'{k} = {scalar(v)}')
        for k, v in node.items():
            if isinstance(v, dict):
                table(v, (*path, k))
            elif isinstance(v, list) and v:
                for item in v:
                    table(item, (*path, k), True)
    table(data)
    return '\n'.join(lines) + '\n'


def region(lo, hi):
    return dict(x_min=lo, x_max=hi, unit='pixel', convention='fits-1-based-inclusive')


def channel(name, state='absent', subtract=False, scan=None, signal=None):
    result = dict(id=name, identity_status='unknown', active=True,
                  overscan=dict(state=state, subtract=subtract))
    if scan:
        result['overscan']['region'] = scan
    if signal:
        result['signal'] = signal
    return result


def common(name):
    return dict(project_schema_version=1,
        project=dict(schema_version=1, id='review-project:' + name, name=name,
                     roots={k: 'review locations/' + k for k in ('raw', 'calibration', 'output', 'work', 'logs')}),
        association=dict(schema_version=1, mode='explicit', bindings=[
            dict(group='review-group:science', role='bpm', selection='omitted'),
            dict(group='review-group:science', role='bias', selection='selected',
                 asset_id='synthetic-asset:bias', asset_version=1)]),
        reduction_profile=dict(schema_version=1, id='review-purpose:scientific', purpose='scientific'),
        recipe=dict(schema_version=1, id='review-recipe:preprocess', steps=[
            dict(id='preprocess', operation='mef_sci_pp')]),
        execution=dict(schema_version=1, activation='disabled', mode='serial', workers=1,
                       numerical_threads=1, niceness=10),
        quality=dict(schema_version=1, policy='record_only', estimator_status='not_qualified', thresholds=[]),
        product_profile=dict(schema_version=1, id='review-product:legacy', target='legacy',
                             compliance='not_validated', variance_contract='pre_m6a_unavailable'),
        processing=dict(schema_version=1, native_mode='unavailable'),
        readout=dict(schema_version=1, id='review-readout:' + name, authority='synthetic',
                     metadata_policy='explicit_review', header_evidence=[],
                     mapping_status='unverified', inventory_status='not_established', detectors=[dict(id='review-detector:one',
                     identity_status='unknown', channels=[channel('synthetic-channel:A')])]))


def examples():
    result = {}
    for instrument in ('wfi', 'omegacam'):
        data = common(instrument)
        reference = '../../examples/' + instrument + '/full.toml'
        native = tomllib.loads((BASE / 'examples' / reference).read_text())
        detectors = []
        for i in range(1, native['instrument']['detector_count']['value'] + 1):
            n = native['instrument']['detectors'][f'CHIP{i}']
            detectors.append(dict(id=f'legacy-ordinal:{i}', legacy_ordinal=i,
                identity_status='unknown', channels=[channel('legacy-selected-channel',
                    'defined', bool(native['processing']['use_overscan']['value']),
                    region(n['overscan_x_min']['value'], n['overscan_x_max']['value']))]))
        data['processing'] = dict(schema_version=1, native_mode='legacy_reference', native_configuration=reference)
        data['readout'].update(authority='configured', detectors=detectors)
        result[instrument] = data
    result['no-overscan'] = common('no-overscan')
    defined = common('defined-disabled')
    defined['readout']['detectors'][0]['channels'] = [channel('synthetic-channel:A', 'defined', False, region(101, 110), region(1, 100))]
    result['defined-disabled'] = defined
    dual = common('dual-active')
    dual['readout']['detectors'][0]['channels'] = [
        channel('synthetic-channel:A', 'defined', True, region(101, 110), region(1, 100)),
        channel('synthetic-channel:B', 'defined', True, region(211, 220), region(111, 210))]
    result['dual-active'] = dual
    alternate = common('alternative-selected')
    inactive = channel('synthetic-channel:A', 'defined', False, region(101, 110), region(1, 100))
    inactive['active'] = False
    alternate['readout']['detectors'][0]['channels'] = [inactive,
        channel('synthetic-channel:B', 'defined', True, region(1, 10), region(11, 110))]
    # Synthetic raw header evidence is retained but cannot override the configured
    # alternative-channel geometry or turn unknown hardware identity into fact.
    alternate['readout']['header_evidence'] = [dict(detector_id='review-detector:one',
        asset_id='synthetic-asset:header', asset_version=1, hdu=0, card_index=1,
        field='overscan_region', raw_card="SYNTHSC = '[999:1000,*]' / synthetic unreviewed contradictory candidate".ljust(80),
        trust='unverified', disposition='unresolved')]
    result['alternative-selected'] = alternate
    return result


if __name__ == '__main__':
    for name, data in examples().items():
        (BASE / 'examples' / (name + '.toml')).write_text(render(data))
