"""Read-only checks of the M0a review notation, not an ASDF schema validator.

Run with Python 3.11 from any cwd. All mutations below are in-memory negative
controls; no project, FITS, source or installed package is opened or modified.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(bundle, catalog):
    require(bundle['notation'] == catalog['notation'], 'notation')
    require(bundle['schema_version'] == catalog['version'], 'unsupported version')
    require(bundle['synthetic'] is True, 'synthetic scope')
    records = bundle['records']
    by_id = {r['record_id']: r for r in records}
    require(len(by_id) == len(records), 'duplicate record ID')
    types = {'string': lambda x: isinstance(x, str) and bool(x),
             'integer': lambda x: type(x) is int and x > 0,
             'number': lambda x: type(x) in (int, float),
             'object': lambda x: isinstance(x, dict),
             'array': lambda x: isinstance(x, list),
             'ref': lambda x: isinstance(x, str) and x in by_id,
             'nullable_ref': lambda x: x is None or (isinstance(x, str) and x in by_id),
             'refs': lambda x: isinstance(x, list) and all(isinstance(y, str) and y in by_id for y in x),
             'strings': lambda x: isinstance(x, list) and all(isinstance(y, str) for y in x),
             'integers': lambda x: isinstance(x, list) and all(type(y) is int and y > 0 for y in x)}
    def get(ref, kind):
        require(ref in by_id and by_id[ref]['kind'] == kind, 'reference type: '+str(ref))
        return by_id[ref]
    for r in records:
        require(r['kind'] in catalog['record_types'], 'unknown kind')
        fields = dict(catalog['common'], **catalog['record_types'][r['kind']])
        require(set(r) == set(fields), 'missing/unknown field: '+r['record_id'])
        for name, kind in fields.items():
            require(types[kind](r[name]), 'field type/reference: '+r['record_id']+'.'+name)
        require(r['record_id'] == r['logical_id']+'@'+str(r['version']), 'version identity')
        if r['kind'] == 'image':
            get(r['asset'], 'asset')
            require(len(r['shape']) == 2, 'image dimensions')
            h = r['hdu']
            require(type(h.get('index')) is int and h['index'] >= 0, 'HDU selector')
            require(h.get('extver', 1) > 0, 'EXTVER')
            require(r['variance']['state'] in ('unavailable', 'supplied', 'modeled'), 'variance state')
            if r['variance']['state'] == 'unavailable':
                require(r['variance']['image'] is None, 'missing variance is not an array')
            else:
                get(r['variance']['image'], 'image')
        elif r['kind'] == 'calibration':
            im = get(r['image'], 'image')
            require(r['applicability']['detector_id'] == im['detector_id'], 'calibration detector')
        elif r['kind'] == 'group':
            require(len(r['members']) == len(set(r['members'])), 'duplicate membership')
            for ref in r['members']:
                get(ref, 'observation')
        elif r['kind'] == 'association':
            get(r['group'], 'group')
            for role, ref in r['selected'].items():
                require(ref in r['candidates'], 'selection outside candidates')
                require(get(ref, 'calibration')['calibration_type'] == role, 'calibration role')
        elif r['kind'] == 'project':
            if r['parent'] is not None:
                parent = get(r['parent'], 'project')
                require(parent['logical_id'] == r['logical_id'] and parent['version'] < r['version'], 'project parent')
            get(r['configuration'], 'configuration')
        elif r['kind'] == 'task':
            require(len(r['detectors']) == len(set(r['detectors'])), 'duplicate detector request')
            for ref in r['depends_on']:
                get(ref, 'task')
            for ref in r['inputs']:
                get(ref, 'observation')
            for role, ref in r['calibrations'].items():
                cal = get(ref, 'calibration')
                require(cal['calibration_type'] == role, 'task calibration role')
                require(cal['applicability']['detector_id'] in r['detectors'], 'task detector compatibility')
            for ref in r['outputs']:
                require(get(ref, 'product')['producer'] == r['record_id'], 'output producer')
        elif r['kind'] == 'plan':
            project = get(r['project'], 'project')
            require(r['state'] == 'frozen', 'plan state')
            require(r['configuration'] == project['configuration'], 'plan configuration snapshot')
            require(r['groups'] == project['groups'] and r['associations'] == project['associations'], 'plan membership snapshot')
            task_set = set(r['tasks'])
            selected = {}
            for ref in r['associations']:
                selected.update(get(ref, 'association')['selected'])
            colors = {}
            def visit(ref):
                require(colors.get(ref) != 'active', 'task dependency cycle')
                if colors.get(ref) == 'done':
                    return
                colors[ref] = 'active'
                t = get(ref, 'task')
                require(t['configuration'] == r['configuration'], 'task settings snapshot')
                require(t['calibrations'] == selected, 'task association snapshot')
                members = [m for g in r['groups'] for m in get(g, 'group')['members']]
                require(all(x in members for x in t['inputs']), 'task outside selected group')
                for dep in t['depends_on']:
                    require(dep in task_set, 'dependency outside plan')
                    visit(dep)
                colors[ref] = 'done'
            for ref in r['tasks']:
                visit(ref)
        elif r['kind'] == 'run':
            plan = get(r['plan'], 'plan')
            for ref in r['attempts']:
                at = get(ref, 'attempt')
                require(at['run'] == r['record_id'] and at['task'] in plan['tasks'], 'run attempt')
        elif r['kind'] == 'attempt':
            require(r['state'] == 'not_started' and r['outcome'] == 'not_run' and not r['products'], 'fixture claims execution')
        elif r['kind'] == 'product':
            require(r['state'] == 'planned' and r['verification'] == 'not_verified', 'fixture claims publication')
            require(r['record_id'] in get(r['producer'], 'task')['outputs'], 'product owner')
            get(r['plan'], 'plan')
            get(r['image'], 'image')
    get(bundle['entry_project'], 'project')
    return by_id


def main():
    catalog = json.loads((ROOT/'contract-catalog.json').read_text())
    original = json.loads((ROOT/'project-example.json').read_text())
    by_id = validate(original, catalog)
    require(by_id['plan:original@1']['project'] == 'project:example@1', 'old plan moved')
    require(by_id['association:science@1']['selected']['bias'] == 'calibration:bias@1', 'old selection moved')
    require(by_id['association:science@2']['selected']['bias'] == 'calibration:bias@2', 'new selection missing')
    gain = by_id['observation:science@1']['attributes']['gain']
    require(gain['source'] == 'configured' and gain['raw_value'] == 0 and gain['conflict'], 'authority evidence')
    for index, extname in [(0, None), (1, 'CCD-A'), (7, 'CCD-A')]:
        variant = copy.deepcopy(original)
        row = next(x for x in variant['records'] if x['record_id']=='image:science@1')
        row['hdu'] = {'index': index, 'extname': extname, 'extver': 1}
        validate(variant, catalog)
    changed = copy.deepcopy(original)
    next(r for r in changed['records'] if r['record_id']=='project:example@2')['roots']['raw'] = 'file:///RELOCATED/raw/'
    validate(changed, catalog)
    require(next(r for r in changed['records'] if r['record_id']=='plan:original@1') == by_id['plan:original@1'], 'relocation changed plan')
    def mutate(label, fn):
        bad = copy.deepcopy(original)
        rows = {r['record_id']: r for r in bad['records']}
        fn(bad, rows)
        try:
            validate(bad, catalog)
        except (ValueError, KeyError, TypeError):
            return
        raise AssertionError('negative control accepted: '+label)
    controls = [
        ('unknown schema', lambda b,r: b.update(schema_version='99')),
        ('duplicate ID', lambda b,r: b['records'].append(copy.deepcopy(b['records'][0]))),
        ('unresolved reference', lambda b,r: r['task:native@1'].update(configuration='absent@1')),
        ('wrong reference kind', lambda b,r: r['image:science@1'].update(asset='group:science@1')),
        ('unknown field', lambda b,r: r['task:native@1'].update(implicit_cwd='guess')),
        ('bad HDU', lambda b,r: r['image:science@1']['hdu'].update(index=-1)),
        ('duplicate member', lambda b,r: r['group:science@1']['members'].append('observation:science@1')),
        ('wrong detector', lambda b,r: r['calibration:bias@1']['applicability'].update(detector_id='CCD-B')),
        ('moving selection', lambda b,r: r['task:native@1']['calibrations'].update(bias='calibration:bias@2')),
        ('task cycle', lambda b,r: r['task:native@1']['depends_on'].append('task:native@1')),
        ('stale plan', lambda b,r: r['plan:original@1'].update(project='project:example@2')),
        ('fabricated variance', lambda b,r: r['image:science@1']['variance'].update(image='image:bias@1')),
        ('false publication', lambda b,r: r['product:native@1'].update(state='published')),
    ]
    for name, action in controls:
        mutate(name, action)
    print(f'PASS: {len(by_id)} records; exact old/new selection, metadata authority, 3 HDU descriptors, relocation; {len(controls)} rejected controls')
    print('Scope: offline review notation only; no ASDF/FITS I/O, scientific validation or native processing')


if __name__ == '__main__':
    main()
