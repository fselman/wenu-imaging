#!/usr/bin/env python3
"""Build a self-contained bias QC inspection page from product ASDF files once.

Run with the qualified ASDF interpreter. No FITS/raw reads, scientific
recalculation, representative JD, database or native build is involved.
"""
import argparse
from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
import math
import numbers
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plain(value):
    """Detach JSON metadata while the ASDF file is open; never follow paths."""
    if isinstance(value, Mapping):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, numbers.Integral):
        return int(value)
    if isinstance(value, numbers.Real):
        require(math.isfinite(value), 'Nonfinite scalar in QC metadata')
        return float(value)
    if hasattr(value, 'tolist'):
        return plain(value.tolist())
    raise ValueError('Unsupported stored metadata type: ' + type(value).__name__)


def signature(path):
    s = path.stat()
    return s.st_size, s.st_mtime_ns, s.st_ino


def read_product(path, schema):
    # Each ASDF is opened and schema-validated exactly once per generation.
    import asdf
    schema_id = json.loads(schema)['id']
    with asdf.config_context() as config:
        config.add_resource_mapping({schema_id: schema})
        with asdf.open(path, custom_schema=schema_id, lazy_load=False,
                       strict_extension_check=True) as record:
            record.validate()
            q = record.tree['qc']
            require(q['provenance']['operation'] == 'cal.bias', 'Not a bias product')
            detectors = q['characterization']['detectors']
            # Arrays are summarized, never represented as scalar measurements.
            return extract(path, q, detectors)


def extract(path, q, detectors=None):
    """Project validated native records to an inspection-only scalar collection."""
    detectors = q['characterization']['detectors'] if detectors is None else detectors
    identity = str(path)
    require(q['file']['filename'] == path.with_suffix('.fits').name,
            'ASDF/FITS stem mismatch')
    ids = [d['detector_id'] for d in detectors]
    require(len(ids) == len(set(ids)) and ids, 'Empty/duplicate detector IDs')
    inputs = q['embedded_input_records']
    require(len({v['record_id'] for v in inputs}) == len(inputs), 'Duplicate input IDs')
    sequence = [v['file']['location'] for v in inputs]
    sequence_id = hashlib.sha256(json.dumps(sequence, ensure_ascii=True).encode()).hexdigest()
    product = dict(id=identity, filename=path.name, fits=q['file']['location'],
                   created_at=q['record']['created_at'], detectors=ids,
                   raw_sequence=sequence_id, raw_inputs=sequence,
                   metadata=plain(dict(file=q['file'], record=q['record'],
                                       provenance=q['provenance'], calibrations=q['calibrations'],
                                       extensions=q.get('extensions', {}),
                                       detector_bindings=[{k: v for k, v in d.items()
                                                           if k != 'measurements'} for d in detectors])),
                   array_measurements=[], rows=[])

    def append(values, detector, scope, input_id=None, input_path=None, source_hdu=None):
        names = set()
        for measurement in values:
            name = measurement['name']
            require(name not in names, 'Duplicate measurement: ' + name)
            names.add(name)
            value = measurement['value']
            scalar = value is None or isinstance(value, (str, bool, numbers.Real))
            if not scalar:
                product['array_measurements'].append(dict(
                    detector=detector['detector_id'], scope=scope, input=input_id,
                    name=name, unit=measurement['unit'], count=len(value)))
                continue
            row = dict(product=identity, detector=detector['detector_id'],
                       output_hdu=detector['output_hdu'],
                       configuration_detector=detector['configuration_detector'],
                       scope=scope, input=input_id, input_path=input_path,
                       source_hdu=source_hdu, measurement=plain(measurement))
            product['rows'].append(row)

    by_id = {d['detector_id']: d for d in detectors}
    for d in detectors:
        append(d['measurements'], d, 'product')
    for record in inputs:
        require([d['detector_id'] for d in record['detectors']] == ids,
                'Embedded detector order differs from product')
        for binding in record['detectors']:
            append(binding['measurements'], by_id[binding['detector_id']], 'input',
                   record['record_id'], record['file']['location'], binding['source_hdu'])
    product['participation'] = plain(q['inputs'])
    return product


def collect(directory, schema, reader=read_product):
    paths = sorted(directory.glob('*.asdf'))
    require(paths, 'No top-level product ASDF files in ' + str(directory))
    products, errors = [], []
    for path in paths:
        before = signature(path)
        try:
            product = reader(path, schema)
            require(signature(path) == before, 'ASDF changed while being read')
            products.append(product)
            print('LOADED:', path.name, 'detectors=', len(product['detectors']),
                  'scalar rows=', len(product['rows']), flush=True)
        except Exception as error:
            errors.append(dict(path=str(path), error=str(error)))
            print('UNAVAILABLE:', path.name, str(error), file=sys.stderr, flush=True)
        require(signature(path) == before, 'ASDF changed during collection: ' + str(path))
    return dict(schema_version=1, directory=str(directory), products=products,
                errors=errors, files_discovered=len(paths), read_attempts=len(paths),
                generated_at=datetime.now(timezone.utc).isoformat(),
                observation_epoch_policy='not_selected')


def render(data):
    template = Path(__file__).with_name('bias-qc-viewer.html').read_text()
    scripts = '\n'.join(Path(__file__).with_name(name).read_text() for name in
                        ('qc-plot-inspection.js', 'bias-qc-inspection.js'))
    # Product paths, comments and error text are untrusted HTML content.
    payload = json.dumps(data, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c')
    require(template.count('__BIAS_QC_DATA__') == template.count('__BIAS_QC_SCRIPT__') == 1,
            'Invalid inspection page template')
    return template.replace('__BIAS_QC_SCRIPT__', scripts).replace('__BIAS_QC_DATA__', payload)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--products', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    directory = a.products.resolve(strict=True)
    output = a.output.absolute()
    require(directory.is_dir(), 'Products path is not a directory')
    require(output.suffix.lower() == '.html', 'Output must end in .html')
    require(not output.resolve().is_relative_to(directory),
            'Save the inspection page outside the reduced-products directory')
    require(not output.exists(), 'Preserve existing inspection page: ' + str(output))
    require(output.parent.is_dir(), 'Create the chosen output directory explicitly first')
    schema = (ROOT/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json').read_bytes()
    data = collect(directory, schema)
    require(data['products'], 'No validated bias products; no inspection page written')
    with output.open('x') as stream:
        stream.write(render(data))
    print('PAGE:', output)
    print('PASS: inspection generated; no FITS/raw reads or source changes.')
    if data['errors']:
        print('INCOMPLETE:', len(data['errors']), 'unavailable files are listed in the page.')
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
