"""Opt-in shared QC assembly, ASDF sidecars and bounded offline traversal.

No numerical recipe, raw-file mutation, input discovery or environment activation.
Native/recipe callers supply measurements with explicit definitions and origins.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import tempfile
from urllib.parse import quote

SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'config/qc-schema-1.0.0.json'
SCHEMA_VERSION = '1.0.0'
MAX_RECORD_BYTES = 32 * 1024 * 1024


class QcError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise QcError(message)


def encoded(value):
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False,
                          separators=(',', ':')).encode('utf-8')
    except (TypeError, ValueError, RecursionError) as error:
        raise QcError('QC values must be finite, acyclic primitive data') from error


def text(value):
    return type(value) is str and bool(value.strip()) and '\0' not in value


def timestamp(value):
    require(text(value), 'Explicit assessment timestamp required')
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as error:
        raise QcError('Invalid assessment timestamp') from error
    require(stamp.tzinfo is not None, 'Assessment timestamp needs timezone')


def qc_filename(filename):
    require(text(filename) and Path(filename).name == filename and '\\' not in filename,
            'Require a basename, with full source location stored separately')
    require(filename.lower().endswith('.fits') and len(filename) > 5,
            'Current sidecar naming supports .fits only; compression policy is pending')
    # References are local filesystem names, not URLs. Escape reserved characters
    # (including literal percent) once so timestamped FITS basenames stay unique.
    # Tilde escapes avoid ASDF treating percent escapes as URI decoding.
    return quote(filename[:-5], safe='-._').replace('~', '%7E').replace('%', '~') + '.asdf'


def _local_reference(value):
    require(text(value) and not Path(value).is_absolute() and '\\' not in value and
            ':' not in value and '?' not in value and '#' not in value and
            value.endswith('.asdf'), 'QC references must be local relative ASDF paths')


def _validate(record):
    """Format-independent invariants; structural validation also runs in ASDF."""
    require(type(record) is dict and set(record) == {
        'file', 'characterization', 'record', 'provenance', 'inputs', 'extensions'},
        'Unknown or missing common QC sections')
    file = record['file']
    require(file['kind'] in ('raw', 'product') and text(file['id']) and text(file['location']),
            'Missing characterized file identity/location/kind')
    qc_filename(file['filename'])
    require(file['sha256'] is None or (type(file['sha256']) is str and
            len(file['sha256']) == 64 and all(c in '0123456789abcdef' for c in file['sha256'])),
            'Invalid supplied file digest')
    meta = record['record']
    require(meta['schema_version'] == SCHEMA_VERSION and text(meta['assessment_id']),
            'Unknown schema version or missing assessment identity')
    timestamp(meta['created_at'])
    provenance = record['provenance']
    require(text(provenance['operation']) and text(provenance['configuration_id']),
            'Missing operation/configuration origin')
    require(set(provenance['producer']) == {'name', 'version', 'source_revision'} and
            all(text(v) for v in provenance['producer'].values()), 'Explicit producer identity required')
    detector_ids = [d['detector_id'] for d in record['characterization']['detectors']]
    require(len(detector_ids) == len(set(detector_ids)) and all(text(d) for d in detector_ids),
            'Duplicate or missing logical detector ID')
    selectors = file['selectors']
    require({s['detector_id'] for s in selectors} == set(detector_ids) and
            len(selectors) == len(detector_ids), 'Detector coverage/selector mismatch')
    require(all(type(s['hdu_index']) is int and s['hdu_index'] >= 0 for s in selectors),
            'Explicit nonnegative source HDU required; no detector-ID inference')
    own_hdus = {s['detector_id']: s['hdu_index'] for s in selectors}
    require([i['index'] for i in record['inputs']] == list(range(len(record['inputs']))),
            'Input order/indices must be original and contiguous')
    require(file['kind'] != 'raw' or not record['inputs'], 'Raw QC cannot own recipe membership')
    allowed_sources = {file['id'], *(i['file_id'] for i in record['inputs'])}
    for member in record['inputs']:
        _local_reference(member['qc']['path'])
        require(text(member['file_id']) and text(member['qc']['assessment_id']) and
                len(member['qc']['record_digest']) == 64, 'Incomplete frozen input QC reference')
        decision = member['participation']
        require(decision['status'] in ('used', 'rejected', 'not_used', 'pending'), 'Unknown participation')
        require(decision['reason'] is None or text(decision['reason']), 'Invalid participation reason')
        require(decision['status'] not in ('rejected', 'not_used') or text(decision['reason']),
                'Exclusion/unused membership needs an explicit reason')
    for detector in record['characterization']['detectors']:
        names = []
        for m in detector['measurements']:
            names.append(m['name'])
            require(text(m['name']) and text(m['unit']), 'Measurement name/unit required')
            require(m['status'] in ('measured', 'unavailable', 'invalid'), 'Unknown measurement state')
            definition = m['definition']
            require(text(definition['stage']), 'Measurement processing stage required')
            if m['status'] == 'measured':
                require(m['value'] is not None and m['reason'] is None and
                        text(definition['method']) and type(definition['region']) is dict and
                        bool(definition['region']) and type(definition['sample_count']) is int and
                        definition['sample_count'] > 0 and bool(m['sources']),
                        'Measured values need method, region, sample count and origin')
                values = m['value'] if type(m['value']) is list else [m['value']]
                require(bool(values) and all(type(v) in (int, float) and math.isfinite(v) for v in values),
                        'Measurement must contain finite numeric values')
                if m['unit'] == 'count':
                    require(all(type(v) is int and v >= 0 for v in values), 'Pixel counts must be nonnegative integers')
            else:
                require(m['value'] is None and text(m['reason']), 'Unavailable/invalid is not zero')
            require(all(s['file_id'] in allowed_sources and s['detector_id'] == detector['detector_id'] and
                        type(s['hdu_index']) is int and s['hdu_index'] >= 0 for s in m['sources']),
                    'Measurement origin must identify the corresponding file/detector/HDU')
            require(all(s['file_id'] != file['id'] or s['hdu_index'] == own_hdus[s['detector_id']]
                        for s in m['sources']), 'Measurement source HDU disagrees with file selector')
        require(len(names) == len(set(names)), 'Duplicate measurement name in detector')
    for summary in record['characterization']['summaries']:
        require(summary['statistic'] in ('mean', 'median') and text(summary['measurement']),
                'Unknown detector summary')
        contributors = summary['contributors']
        excluded = summary['not_measured']
        require(len(contributors) == len(set(contributors)) and
                set(contributors).isdisjoint(excluded) and
                set(contributors) | set(excluded) == set(detector_ids),
                'Summary must account for every configured output detector')
        require(summary['value'] is None if not contributors else
                type(summary['value']) in (int, float) and math.isfinite(summary['value']),
                'Invalid summary value or unavailable contributors')
    encoded(record)


@dataclass(frozen=True)
class QcRecord:
    """Immutable owned record. Encoded bytes are internal, not a JSON output."""
    _encoded: bytes

    def __post_init__(self):
        require(type(self._encoded) is bytes, 'Record requires owned bytes')
        try:
            _validate(json.loads(self._encoded))
        except (KeyError, TypeError, json.JSONDecodeError) as error:
            raise QcError('Malformed QC record') from error

    def as_dict(self):
        return json.loads(self._encoded)

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(self.as_dict(), ensure_ascii=False, allow_nan=False,
                                        sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class QcRecipe:
    """Common record lifecycle; recipe-specific adapters only supply values."""
    def __init__(self, *, file, assessment_id, created_at, producer, operation, configuration_id):
        file = deepcopy(file)
        self._tree = dict(file=file,
                          characterization=dict(detectors=[dict(detector_id=s['detector_id'], measurements=[])
                                                           for s in file['selectors']], summaries=[]),
                          record=dict(schema_version=SCHEMA_VERSION, assessment_id=assessment_id, created_at=created_at),
                          provenance=dict(producer=deepcopy(producer), operation=operation,
                                          configuration_id=configuration_id), inputs=[], extensions={})
        self._sealed = False

    def _open(self):
        require(not self._sealed, 'QC builder already sealed')

    def add_measurement(self, detector_id, *, name, value, unit, definition, sources,
                        status='measured', reason=None):
        self._open()
        matches = [d for d in self._tree['characterization']['detectors'] if d['detector_id'] == detector_id]
        require(len(matches) == 1, 'Measurement detector outside declared coverage')
        require(name not in {m['name'] for m in matches[0]['measurements']}, 'Duplicate detector measurement')
        matches[0]['measurements'].append(deepcopy(dict(name=name, value=value, unit=unit, definition=definition,
                                                      sources=sources, status=status, reason=reason)))

    def add_extension(self, name, value):
        """Attach explicitly named recipe metadata through the common owner."""
        self._open()
        require(text(name) and name not in self._tree['extensions'], 'Duplicate/invalid extension name')
        encoded(value)
        self._tree['extensions'][name] = deepcopy(value)

    def add_input(self, record, *, qc_path, participation, reason=None):
        self._open()
        require(isinstance(record, QcRecord), 'Require a sealed input QC record')
        _local_reference(qc_path)
        leaf = record.as_dict()
        self._tree['inputs'].append(dict(index=len(self._tree['inputs']), file_id=leaf['file']['id'],
            qc=dict(path=qc_path, assessment_id=leaf['record']['assessment_id'], record_digest=record.digest),
            participation=dict(status=participation, reason=reason)))

    def add_unavailable(self, detector_id, *, name, unit, stage, reason, sources=()):
        self.add_measurement(detector_id, name=name, value=None, unit=unit,
            definition=dict(method=None, stage=stage, region=None, sample_count=None),
            sources=list(sources), status='unavailable', reason=reason)

    def summarize_detectors(self, name):
        """Requested scalar mean/median only; never invent zero for missing data."""
        self._open()
        values, ids, missing, unit, definitions = [], [], [], None, []
        summaries = self._tree['characterization']['summaries']
        require(not any(s['measurement'] == name for s in summaries), 'Detector summary already exists')
        for detector in self._tree['characterization']['detectors']:
            matches = [m for m in detector['measurements'] if m['name'] == name]
            if matches:
                require(unit in (None, matches[0]['unit']), 'Cannot summarize mixed units')
                unit = matches[0]['unit']
            if not matches or matches[0]['status'] != 'measured':
                missing.append(detector['detector_id']); continue
            m = matches[0]
            require(type(m['value']) in (int, float), 'Vector profiles have no implicit detector average')
            require(unit in (None, m['unit']), 'Cannot summarize mixed units')
            unit = m['unit']; values.append(m['value']); ids.append(detector['detector_id'])
            definitions.append((m['definition']['stage'], m['definition']['method']))
        require(len(set(definitions)) <= 1, 'Cannot summarize different stages/methods')
        for statistic, function in [('mean', statistics.mean), ('median', statistics.median)]:
            summaries.append(dict(measurement=name, statistic=statistic,
                                  value=function(values) if values else None, unit=unit,
                                  contributors=list(ids), not_measured=list(missing)))

    def seal(self):
        self._open()
        record = QcRecord(encoded(self._tree))
        self._sealed = True
        return record


class BiasQcRecipe(QcRecipe):
    """First recipe adapter. No pixel calculations or definition defaults."""
    METRICS = {
        'overscan.level': 'ADU', 'overscan.rms': 'ADU', 'bias.level': 'ADU',
        'bias.rms': 'ADU', 'pixels.hot': 'count', 'read_noise': 'ADU',
        'profile.rows': 'ADU', 'profile.columns': 'ADU',
        'pixels.invalid': 'count', 'pixels.clipped': 'count',
    }

    # Native bias-stage measurements use the same common descriptors/schema.
    for _stage in ('raw_active', 'corrected_active', 'prescan', 'overscan',
                   'master', 'master_unmasked'):
        for _name in ('mean', 'median', 'stdev', 'scaled_mad'):
            METRICS[_stage+'.'+_name] = 'ADU'
        for _name in ('region_pixels', 'bpm_excluded', 'nonfinite_excluded', 'valid_pixels'):
            METRICS[_stage+'.'+_name] = 'count'
    METRICS.update({'read_noise.mad': 'ADU', 'pixels.hot.threshold': 'ADU',
                    'scan_correction.median': 'ADU', 'scan_correction.stdev': 'ADU'})

    def __init__(self, **kwargs):
        require(kwargs['operation'] == 'cal.bias', 'Bias adapter operation mismatch')
        super().__init__(**kwargs)

    def add_measurement(self, detector_id, **measurement):
        name = measurement['name']
        require(name in self.METRICS and measurement['unit'] == self.METRICS[name],
                'Unknown bias QC quantity or unit; no electron/gain conversion')
        if name in ('read_noise', 'read_noise.mad') and measurement.get('status', 'measured') == 'measured':
            require(len(measurement['sources']) == 2 and
                    len({s['file_id'] for s in measurement['sources']}) == 2,
                    'Pair-difference RON must identify two distinct input files')
        super().add_measurement(detector_id, **measurement)

    def summarize_detectors(self, name):
        require(name in self.METRICS, 'Unknown bias summary quantity')
        super().summarize_detectors(name)


def _asdf():
    try:
        import asdf
    except ImportError as error:
        raise QcError('Use the qualified ASDF environment; no automatic installation') from error
    require(asdf.__version__ == '6.0.0', 'This opt-in writer targets qualified ASDF 6.0.0')
    return asdf


def _check_linked_origins(parent_tree, leaf):
    file = leaf['file']
    hdus = {s['detector_id']: s['hdu_index'] for s in file['selectors']}
    for detector in parent_tree['characterization']['detectors']:
        for measurement in detector['measurements']:
            for source in measurement['sources']:
                if source['file_id'] == file['id']:
                    require(source['detector_id'] in hdus and
                            hdus[source['detector_id']] == source['hdu_index'],
                            'Paired/input measurement origin disagrees with referenced QC selector')


def _linked_record(parent, member, root):
    _local_reference(member['qc']['path'])
    path = (parent / member['qc']['path']).resolve(strict=True)
    require(path.is_relative_to(root), 'QC reference escapes supplied project root')
    record = read_record(path)
    tree = record.as_dict()
    require(tree['file']['id'] == member['file_id'] and
            tree['record']['assessment_id'] == member['qc']['assessment_id'] and
            record.digest == member['qc']['record_digest'], 'Linked QC identity/content mismatch')
    return record


def write_record(record, directory, *, qc_root=None):
    """One common ASDF writer; input files are never opened, copied or modified."""
    require(isinstance(record, QcRecord), 'Require a sealed common QC record')
    directory = Path(directory).resolve(strict=True)
    require(directory.is_dir(), 'QC directory must already exist')
    root = Path(qc_root).resolve(strict=True) if qc_root is not None else directory
    require(root.is_dir() and directory.is_relative_to(root), 'QC destination outside supplied root')
    destination = directory / qc_filename(record.as_dict()['file']['filename'])
    require(not destination.exists() and not destination.is_symlink(), 'QC name conflict; no overwrite')
    asdf = _asdf()
    for member in record.as_dict()['inputs']:
        leaf = _linked_record(directory, member, root)
        _check_linked_origins(record.as_dict(), leaf.as_dict())
    temporary = None
    try:
        fd, name = tempfile.mkstemp(prefix='.qc-', suffix='.asdf', dir=directory)
        temporary = Path(name)
        with os.fdopen(fd, 'wb') as stream:
            with asdf.AsdfFile({'qc': record.as_dict()}, version='1.6.0',
                               custom_schema=SCHEMA_PATH.as_uri()) as af:
                af.validate()
                af.write_to(stream)
        require(temporary.stat().st_size <= MAX_RECORD_BYTES, 'QC record exceeds configured limit')
        os.link(temporary, destination)  # Exclusive publication, including racing writers.
        return destination
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_record(path):
    path = Path(path).resolve(strict=True)
    require(path.is_file() and path.stat().st_size <= MAX_RECORD_BYTES, 'Invalid/oversized QC file')
    asdf = _asdf()
    with asdf.open(path, custom_schema=SCHEMA_PATH.as_uri(), lazy_load=False,
                   strict_extension_check=True) as af:
        af.validate()
        return QcRecord(encoded(dict(af.tree['qc'])))


def traverse_records(product_path, *, qc_root, max_records=10000):
    """Monitor foundation: each assessment once; verify linked identity/content.

    References are explicit common descriptors, not automatically resolved $ref
    objects. Only local QC files inside qc_root are opened; no FITS arrays.
    """
    root = Path(qc_root).resolve(strict=True)
    require(root.is_dir() and type(max_records) is int and max_records > 0, 'Invalid traversal bounds')
    cache, active, identities = {}, set(), {}

    def visit(path, expected=None, parent_tree=None):
        path = path.resolve(strict=True)
        require(path.is_relative_to(root), 'QC reference escapes supplied project root')
        require(path not in active, 'Cyclic QC references')
        if path in cache:
            record = cache[path]
        else:
            require(len(cache) < max_records, 'QC traversal limit reached')
            record = read_record(path)
            cache[path] = record
        tree = record.as_dict()
        if expected is not None:
            require(tree['file']['id'] == expected['file_id'] and
                    tree['record']['assessment_id'] == expected['qc']['assessment_id'] and
                    record.digest == expected['qc']['record_digest'], 'Linked QC identity/content mismatch')
            _check_linked_origins(parent_tree, tree)
        assessment = tree['record']['assessment_id']
        require(assessment not in identities or identities[assessment] == record.digest,
                'Conflicting content for assessment identity')
        if assessment in identities:
            return
        identities[assessment] = record.digest
        yield record
        active.add(path)
        for member in tree['inputs']:
            _local_reference(member['qc']['path'])
            yield from visit(path.parent / member['qc']['path'], member, tree)
        active.remove(path)

    yield from visit(Path(product_path))

