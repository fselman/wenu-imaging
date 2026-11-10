#!/usr/bin/env python3
"""Compare saved linearity measurements by physical input identity; no image I/O."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ('rows', 'exposure_rows', 'direct_site_replay', 'scan_traces', 'raw_bias_diagnostics')
ASSET_FIELDS = {'asset', 'first_asset', 'second_asset', 'bias1_asset', 'bias2_asset'}
INDEX_FIELDS = {'input_index', 'first_input_index', 'second_input_index', 'original_input_index'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fingerprint(context, path):
    if 'input_sha256' in context:
        return context['input_sha256'][path]
    return context['dependency_evidence']['images'][path]['sha256']


def identities(context):
    """Resolve labels to explicit role/path/HDU identities, preserving pair membership."""
    by_asset, by_index, pairs, ordered = {}, {}, {}, []
    for role, members in (('flat', context['selection']['flat']), ('bias', context['biases'])):
        for row in members:
            identity = (role, row['path'], row['hdu'])
            require(row['asset'] not in by_asset and row['index'] not in by_index,
                    'Ambiguous saved input identity/index')
            by_asset[row['asset']] = identity
            by_index[row['index']] = identity
            ordered.append((identity, fingerprint(context, row['path']),
                            None if role=='flat' else row['accepted']))
            if role=='flat':
                pairs.setdefault(row['pair'], []).append(identity)
    require(all(len(group)==2 for group in pairs.values()), 'Incomplete saved pair membership')
    pairs = {key: tuple(sorted(value)) for key, value in pairs.items()}
    directories = {'pair-%04d' % i: value for i, value in enumerate(pairs.values())}
    return by_asset, by_index, pairs, directories, ordered


def canonical_records(value, context, collection):
    by_asset, by_index, pairs, directories, _ = identities(context)

    def convert(item, key=None):
        if isinstance(item, dict):
            return {k: convert(v, k) for k, v in item.items()}
        if isinstance(item, list):
            return [convert(v) for v in item]
        if key in ASSET_FIELDS:
            require(item in by_asset, 'Unknown measured asset: '+str(item))
            return by_asset[item]
        if key in INDEX_FIELDS:
            require(item in by_index, 'Unknown measured original index: '+str(item))
            return by_index[item]
        if key=='pair_id':
            require(item in pairs, 'Unknown measured pair: '+str(item))
            return pairs[item]
        if key in ('pair_directory', 'source_pair_directory'):
            require(item in directories, 'Unknown measured pair directory: '+str(item))
            return directories[item]
        return item

    return Counter(json.dumps(convert(row), sort_keys=True, allow_nan=False,
                              separators=(',', ':')) for row in value[collection])


def calibration(context, role):
    row = context['master'] if role=='master' else context['selection']['bpm']
    if role=='bpm' and row['encoding']=='omitted':
        return ('omitted',)
    path = row['product'] if role=='master' else row['path']
    return (fingerprint(context, path), row['hdu'], None if role=='master' else row['encoding'])


def compare_values(actual, reference, current_context, reference_context):
    require(identities(current_context)[-1]==identities(reference_context)[-1],
            'Ordered physical inputs, frozen fingerprints or bias membership differ')
    require(current_context['resolved']['controls']==reference_context['resolved']['controls'],
            'Processing controls differ')
    for role in ('master', 'bpm'):
        require(calibration(current_context, role)==calibration(reference_context, role),
                role+' calibration bytes/HDU/encoding differ')
    require(actual['detector']==reference['detector'], 'Detector identity differs')
    def geometry(context):
        return next(d for d in context['resolved']['detectors'] if d['detector_id']==actual['detector'])
    require(geometry(current_context)==geometry(reference_context), 'Detector/ROI geometry differs')
    for key in ('measurement_stage', 'noise_state', 'covariance', 'fit_state', 'units'):
        require(actual[key]==reference[key], 'Measurement state differs: '+key)
    counts = {}
    for name in COLLECTIONS:
        left = canonical_records(actual, current_context, name)
        right = canonical_records(reference, reference_context, name)
        if left != right:
            removed, added = list((right-left).elements()), list((left-right).elements())
            raise ValueError(f'{name} differs: {len(removed)} reference records / {len(added)} current records')
        counts[name] = len(actual[name])
    return counts


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_paths(current, reference, expected_producer=None):
    sys.path.insert(0, str(ROOT/'Pycavi2/pycavi/pycavi'))
    import pycavi_bpm_linearity_recipe as reader
    import pycavi_linearity_native_archive as archive
    import pycavi_native_product_qc as qc
    protected = {p: digest(p) for root in (current.parent, reference.parent)
                 for p in root.rglob('*') if p.is_file() and p.suffix in ('.asdf', '.json', '.toml')}
    protected[current] = digest(current)
    protected[reference] = digest(reference)

    def offline(event, values):
        if event.startswith(('subprocess.', 'socket.')) or event=='os.system':
            raise RuntimeError('Saved comparison cannot execute commands or use the network')
        if event=='open' and isinstance(values[0], (str, bytes)):
            name = (values[0].decode() if isinstance(values[0], bytes) else values[0]).lower()
            if name.endswith(('.fits', '.fit', '.fts', '.fits.gz', '.fits.fz', '.tsv')):
                raise RuntimeError('Saved comparison cannot open image or native transport files')
    sys.addaudithook(offline)
    saved = [reader.read_manifest(p) for p in (current, reference)]
    if expected_producer:
        require(saved[0]['manifest']['native_source_revision']==expected_producer, 'Unexpected current producer')
    cohorts = [{d['detector_id']: d for d in value['detectors']} for value in saved]
    require(set(cohorts[0])==set(cohorts[1]), 'Detector coverage differs')
    summaries = []
    for detector in cohorts[0]:
        decoded = [group[detector]['preparation'] for group in cohorts]
        contexts = []
        for path, data, value in zip((current, reference), saved, decoded):
            report = data['manifest']
            member = next(d for d in report['detectors'] if d['detector_id']==detector)
            source = path.parent/Path(member['preparation']['path']).relative_to(report['product_root'])
            product = qc.read(source)
            evidence = {row['name']: row['text'] for row in product['extensions']['native_evidence']}
            context = json.loads(evidence['preparation-context.json'])
            if context.get('native_recipe_schema_version')==2:
                context = {**context, **archive.native_context(context, product, evidence)}
            contexts.append(context)
        counts = compare_values(*decoded, *contexts)
        summaries.append(dict(detector=detector, exact_records=counts))
    require(protected=={p: digest(p) for p in protected}, 'Saved products changed during comparison')
    ingestion = None
    if current.suffix=='.toml':
        receipt = tomllib.loads(current.read_text())
        require(receipt['qc'] is False and receipt['final_mef_state']=='not_requested',
                'Expected supplied-mask, QC-off observational comparison')
        require(all(d['bpm_skipped'] for d in receipt['detectors']), 'Expected supplied BPM reuse')
        ingestion = [dict(detector=d['detector_id'], image_loads=d['image_loads'], corrections=d['corrections'])
                     for d in receipt['detectors']]
    return dict(status='exact_saved_measurements', current=str(current), reference=str(reference),
                producer=saved[0]['manifest']['native_source_revision'], detectors=summaries,
                ingestion=ingestion, normalized_labels=['input indices', 'asset labels', 'pair labels/directories'],
                files_sha256={str(p): sha for p, sha in protected.items()},
                raw_images_opened=False, native_commands_started=False, remeasured=False,
                products_unchanged=True, scientific_acceptance=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--expected-producer')
    parser.add_argument('--report-dir', type=Path, required=True, help='Fresh empty directory below reduced logs')
    args = parser.parse_args()
    directory = args.report_dir.resolve(strict=True)
    require(directory.is_dir() and not any(directory.iterdir()), 'Fresh empty report directory required')
    current = args.current.resolve(strict=True)
    definition = tomllib.loads(current.read_text()) if current.suffix=='.toml' else json.loads(current.read_text())
    require(directory.is_relative_to(Path(definition['directories']['logs']).resolve(strict=True)),
            'Report directory must be below the declared logs root')
    result = compare_paths(current, args.reference.resolve(strict=True), args.expected_producer)
    report = directory/'comparison.json'
    with report.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
    for item in result['detectors']:
        for name, count in item['exact_records'].items():
            print('EXACT:', item['detector'], name, count)
    for item in result['ingestion'] or []:
        print('INGESTION:', item['detector'], item['image_loads'], 'loads;', item['corrections'], 'corrections')
    print('PASS: schema, physical bindings, calibrations, populations and saved measurements')
    print('PASS: products unchanged; no raw FITS/native TSV access, execution or remeasurement')
    print('REPORT:', report)


if __name__=='__main__':
    main()
