"""Explicit byte-identical calibration locations; immutable source records stay intact."""
from copy import deepcopy
from pathlib import Path
try:
    from . import pycavi_linearity_recipe as preparation
except ImportError:
    import pycavi_linearity_recipe as preparation
require = preparation.require


def resolve(rows, calibration):
    require(isinstance(rows, list), 'Calibration bindings must be a list')
    root = Path(calibration).resolve(strict=True)
    result, sources, destinations = [], set(), set()
    for row in rows:
        require(isinstance(row, dict) and set(row) == {'source', 'path', 'sha256'}, 'Incomplete calibration binding')
        source, relative, digest = (row[k] for k in ('source', 'path', 'sha256'))
        require(type(source) is str and Path(source).is_absolute() and
                type(relative) is str and relative and not Path(relative).is_absolute() and
                '..' not in Path(relative).parts, 'Explicit original and calibration-relative copy locations required')
        path = (root/relative).resolve(strict=True)
        require(path.is_relative_to(root) and path.is_file() and source not in sources and str(path) not in destinations,
                'Duplicate or escaping calibration binding')
        require(type(digest) is str and len(digest) == 64 and set(digest) <= set('0123456789abcdef'),
                'Exact preserved calibration SHA256 required')
        sources.add(source); destinations.add(str(path))
        result.append(dict(source=source, path=str(path), sha256=digest))
    return result


def bind(dependencies, resolved, rows, calibration):
    """Rebind only the two calibration locations, never pixels or scientific settings."""
    original = dependencies
    root = Path(calibration).resolve(strict=True)
    allowed = {original['master']['product'], original['selection']['bpm']['path']}
    selected = [row for row in rows if row['source'] in allowed]
    if not selected:
        return original
    value = deepcopy(original)
    for row in selected:
        source, path = row['source'], Path(row['path']).resolve(strict=True)
        require(path.is_file() and path.is_relative_to(root) and original['baseline'][source] == row['sha256'],
                'Calibration copy binding differs from preserved fingerprint or project root')
        value['baseline'][str(path)] = value['baseline'].pop(source)
        if source == original['master']['product']:
            value['master']['product'] = str(path)
        if source == original['selection']['bpm']['path']:
            value['selection']['bpm']['path'] = str(path)
    value['transport'] = preparation.native_plan(resolved, value['selection'],
        original_population(original))
    value['calibration_bindings'] = selected
    value['calibration_root'] = str(root)
    return value


def original_population(dependencies):
    """Read the frozen sampling plan, not image pixels."""
    try:
        from . import pycavi_linearity_preparation_qc as archive
    except ImportError:
        import pycavi_linearity_preparation_qc as archive
    record = archive.qc.read_record(dependencies['source_samples']).as_dict()
    return record['extensions']['corrected_sample_origin']['entry']['population']


def verify_context(context, source):
    """Verify relocated calibration declarations against the embedded original graph."""
    rows = context.get('calibration_bindings', [])
    if not rows:
        return
    try:
        from . import pycavi_linearity_preparation_qc as archive
    except ImportError:
        import pycavi_linearity_preparation_qc as archive
    record = archive.qc.read_record(source).as_dict()
    origin = record['extensions']['corrected_sample_origin']
    entry = origin['entry']
    selection, master = deepcopy(entry['selection']), deepcopy(entry['master'])
    selection['detector'] = entry['detector']
    baseline = {master['product']: origin['master_fingerprint']['sha256']}
    for member in archive.qc.traverse_records(source, qc_root=source.parent):
        file = member.as_dict()['file']
        if file['location'] == selection['bpm']['path'] and file['sha256'] is not None:
            require(file['location'] not in baseline or baseline[file['location']] == file['sha256'],
                    'Conflicting preserved mask fingerprint')
            baseline[file['location']] = file['sha256']
    allowed = {master['product'], selection['bpm']['path']}
    require(len({r['source'] for r in rows}) == len(rows), 'Duplicate archived calibration binding')
    for row in rows:
        require(set(row) == {'source', 'path', 'sha256'} and row['source'] in allowed and
                row['sha256'] == baseline[row['source']] and Path(row['path']).is_absolute() and
                Path(row['path']).is_relative_to(context['calibration_root']), 'Archived calibration-copy proof differs')
        if row['source'] == entry['master']['product']:
            master['product'] = row['path']
        if row['source'] == entry['selection']['bpm']['path']:
            selection['bpm']['path'] = row['path']
    require(context['master'] == master and context['selection'] == selection,
            'Native context changed more than the declared calibration locations')
