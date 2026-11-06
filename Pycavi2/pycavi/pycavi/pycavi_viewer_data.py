"""Direct display reads of completed corrected QC products (#243).

Only the selected files are decoded. Immediate links are compared against the
selected records, never followed into copied calibration graphs. Deep audit
readers and all scientific computation/publication code remain separate.
"""
from copy import deepcopy
import json
from pathlib import Path
from time import perf_counter

import pycavi_pair_qc as pairs
import pycavi_measurement_display as measurements
from pycavi_residual_qc import UNITS as LINE_UNITS
from pycavi_roi_ratio_qc import UNITS as RATIO_UNITS
from pycavi_residuals import finite
from pycavi_roi_ratio import KEYS

qc = pairs.qc
require = qc.require
STAGE = measurements.CORRECTED
PREPARATION_UNITS = dict(signal='ADU', variance='ADU2', trace='ADU', exposure='s',
                         coordinates='FITS-1-based-inclusive')


class DisplayReader:
    """One launch, one decode per selected product; retain small identities only."""
    def __init__(self, progress=None):
        self.inputs = {}
        self.identities = {}
        self.timings = []
        self.progress = progress or (lambda message: None)

    def json(self, path):
        path = Path(path).resolve(strict=True)
        content = pairs.small(path)
        self.inputs[str(path)] = pairs.sha(content)
        return json.loads(content)

    def read(self, path, *, kind, expected_digest=None):
        path = Path(path).resolve(strict=True)
        require(path not in self.identities, 'Display product supplied more than once')
        self.progress(f'Reading {kind}: {path}')
        started = perf_counter()
        fingerprint = pairs.sha(pairs.small(path))
        record = qc.read_record(path)  # Common ASDF/schema checks, no graph walk.
        digest = record.digest
        require(expected_digest is None or digest == expected_digest, 'Display index digest differs')
        tree = record.as_dict()
        identity = dict(digest=digest, file_id=tree['file']['id'],
                        assessment_id=tree['record']['assessment_id'], sha256=fingerprint)
        self.identities[path] = identity
        self.inputs[str(path)] = fingerprint
        seconds = perf_counter() - started
        self.timings.append(dict(kind=kind, path=str(path), seconds=seconds))
        self.progress(f'Loaded {kind} [{len(self.identities)} ASDF]: {seconds:.3f} s')
        return tree, identity

    def admit_preparation(self, batch):
        """Check the saved batch metadata without opening products a first time."""
        batch = Path(batch).resolve(strict=True)
        index = self.json(batch / 'index.json')
        receipt = self.json(batch / 'overall-execution.json')
        require(index['status'] == receipt['status'] == 'complete_for_owner_inspection' and
                index['measurement_stage'] == STAGE and index['products'] == receipt['products'] and
                receipt['detectors_total'] == 32 and receipt['detectors_processed'] == 31 and
                len(receipt['preservation']) == 11 and
                all(v is True for v in receipt['preservation'].values()),
                'Require completed preserved corrected preparation batch')
        products = []; expected = {}; seen = set()
        for item in index['products']:
            detector = item['detector']
            require(detector not in seen, 'Duplicate preparation detector')
            seen.add(detector)
            path = Path(item['path']).resolve(strict=True)
            require(path.name == 'linearity-preparation.asdf' and path not in expected and
                    tuple(item[k] for k in ('pairs', 'exposures', 'sites', 'trace_frames')) == (50, 100, 100, 30) and
                    item['noise_state'] == 'unavailable', 'Incomplete preparation product')
            if detector == 'ESO_CCD_#65':
                require(item['reused'] is True and receipt['reused_detector'] == detector, 'Invalid reused detector')
            else:
                require(item['reused'] is False and
                        path.is_relative_to(batch / detector.replace('ESO_CCD_#', 'CCD')),
                        'New preparation path escapes detector directory')
            expected[path] = item
            products.append(path)
        require(len(products) == 32 and seen == {f'ESO_CCD_#{i}' for i in range(65, 97)},
                'Incomplete preparation cohort')
        return products, expected

    @staticmethod
    def selector(tree, detector, table):
        require(tree['file']['selectors'] == [dict(detector_id=detector, table_name=table)],
                'Display detector/table selector differs')

    @staticmethod
    def link(tree, source, sha256):
        require(len(tree['inputs']) == 1, 'Diagnostic needs one immediate source')
        member = tree['inputs'][0]
        require(member['file_id'] == source['file_id'] and
                member['qc']['assessment_id'] == source['assessment_id'] and
                member['qc']['record_digest'] == source['digest'] and sha256 == source['sha256'],
                'Display immediate source identity/content differs')

    def preparation(self, path, expected=None):
        tree, identity = self.read(path, kind='preparation',
                                   expected_digest=expected['digest'] if expected else None)
        value = tree['extensions']['linearity_preparation']
        require(tree['provenance']['operation'] == 'linearity.prepare' and
                value['schema_version'] == 1 and value['measurement_stage'] == STAGE and value['units'] == PREPARATION_UNITS and
                value['noise_state'] == 'unavailable' and value['covariance'] is None and
                value['fit_state'] == 'not_performed', 'Invalid preparation stage/units/model state')
        detector = value['detector']
        require(expected is None or detector == expected['detector'], 'Preparation index detector differs')
        self.selector(tree, detector, 'linearity_preparation')
        require(value['rows'] and value['exposure_rows'] and value['raw_bias_diagnostics'],
                'Empty saved preparation tables')
        if expected:
            require(len(value['rows']) == expected['pairs'] and len(value['exposure_rows']) == expected['exposures'],
                    'Preparation index/table counts differ')
        signals = measurements.preparation_rows(value)  # Lossless selection, no estimator.
        require(all(r['detector'] == detector and r['processing_stage'] == STAGE for r in signals),
                'Preparation signal detector/stage differs')
        metrics = tree['characterization']['detectors'][0]['measurements']
        require(len(metrics) == 2 * len(signals), 'Incomplete common measurements')
        for i, row in enumerate(value['exposure_rows']):
            for offset, field, unit in ((0, 'signal_adu', 'ADU'), (1, 'spatial_variance_adu2', 'ADU2')):
                metric = metrics[2*i+offset]
                require(metric['name'] == f'exposure.{i}.{field}' and metric['value'] == row[field] and
                        metric['unit'] == unit and metric['definition']['stage'] == STAGE,
                        'Common/saved preparation measurement differs')
        bias = value['raw_bias_diagnostics'][0]['table']['rows']
        require(all(pairs.canonical(d['table']['rows']) == pairs.canonical(bias)
                    for d in value['raw_bias_diagnostics']), 'Raw bias diagnostics differ across pairs')
        context = tree['extensions']['linearity_preparation_context']
        self.progress(f'Validated {detector}: {len(signals)} exposure/ROI rows')
        return dict(kind='preparation', stage=STAGE, identity=identity,
                    signals=signals, pairs=[deepcopy(r['raw']) for r in value['rows']], bias=deepcopy(bias),
                    provenance=dict(measurement_stage=STAGE, raw_diagnostic_stage=measurements.RAW,
                        selection=deepcopy(context['selection']),
                        native_receipt=dict(directory=context['native_directory'], operation='linearity.prepare'),
                        serializer=deepcopy(tree['provenance']['producer'])))

    @staticmethod
    def configuration(tree, value):
        require(tree['provenance']['configuration_id'] ==
                'sha256:' + pairs.sha(pairs.canonical(value['configuration']).encode()),
                'Display diagnostic configuration differs')

    def line(self, path, measurement, expected_digest):
        tree, identity = self.read(path, kind='line diagnostics', expected_digest=expected_digest)
        value = tree['extensions']['line_residual_diagnostic']
        require(tree['provenance']['operation'] == 'diagnostic.unweighted_line_residuals' and
                value['schema_version'] == 1 and value['units'] == LINE_UNITS and
                value['measurement_stage'] == measurement['stage'] and value['source_kind'] == 'preparation' and
                value['source_pair_digest'] == value['source_measurement_digest'] == measurement['identity']['digest'],
                'Invalid saved line schema/units/stage/source')
        self.link(tree, measurement['identity'], value['source_pair_sha256'])
        self.configuration(tree, value)
        original = measurement['signals']
        self.selector(tree, original[0]['detector'], 'line_residuals')
        require(len(original) == len(value['rows']), 'Diagnostic population differs')
        for source, row in zip(original, value['rows']):
            require(pairs.canonical(source) == pairs.canonical({k: row[k] for k in source}),
                    'Original samples changed in diagnostic')
            require(type(row['fit_included']) is bool and all(row[k] is None or finite(row[k])
                    for k in ('line_prediction_adu', 'residual_adu', 'residual_percent', 'count_rate_adu_per_s')),
                    'Invalid saved line values')
        rois = {r['roi'] for r in original}
        require(len(value['fits']) == len(rois) and {f['roi'] for f in value['fits']} == rois,
                'ROI fit coverage differs')
        for fit in value['fits']:
            require(fit['status'] in ('available', 'unavailable') and type(fit['n']) is int and fit['n'] >= 0,
                    'Invalid saved fit status/count')
            if fit['status'] == 'available':
                require(fit['reason'] is None and fit['n'] >= 2 and all(finite(fit[k]) for k in
                        ('intercept_adu', 'slope_adu_per_s', 'time_center_s', 'signal_center_adu')),
                        'Invalid saved line coefficients')
            else:
                require(type(fit['reason']) is str and fit['intercept_adu'] is None and
                        fit['slope_adu_per_s'] is None, 'Invalid unavailable fit')
        require(tree['file']['sha256'] == value['transport_sha256'], 'Derived table fingerprint differs')
        self.progress(f'Validated line diagnostics: {len(value["rows"])} rows, {len(value["fits"])} fits')
        return value, identity

    def ratio(self, path, measurement, line, line_identity, expected_digest):
        tree, identity = self.read(path, kind='ratio diagnostics', expected_digest=expected_digest)
        value = tree['extensions']['roi_ratio_diagnostic']
        require(tree['provenance']['operation'] == 'diagnostic.same_exposure_roi_ratio' and
                value['schema_version'] == 1 and value['units'] == RATIO_UNITS and
                value['source_residual_digest'] == line_identity['digest'] and
                value['source_pair_digest'] == measurement['identity']['digest'] and
                value['measurement_stage'] == measurement['stage'] and value['source_kind'] == 'preparation',
                'Invalid saved ratio schema/units/stage/source')
        self.link(tree, line_identity, value['source_residual_sha256'])
        self.configuration(tree, value)
        self.selector(tree, measurement['signals'][0]['detector'], 'roi_ratio')
        originals = {tuple(r[k] for k in KEYS) + (r['roi'],): r for r in line['rows']}
        require(len(originals) == len(line['rows']), 'Duplicate saved line exposure')
        config = value['configuration']; norm = value['normalization']
        require(config['method'] == 'same_exposure_ratio_v1' and
                config['reference_method'] == 'arithmetic_mean_of_individual_ratios' and
                config['numerator_roi'] != config['denominator_roi'] and
                config['uncertainty_state'] == 'unavailable' and config['physical_correction_fitted'] is False,
                'Unknown ratio method/configuration')
        lo, hi = config['reference_signal_min_adu'], config['reference_signal_max_adu']
        require(finite(lo) and finite(hi) and lo <= hi, 'Invalid ratio interval')
        seen = set(); members = []
        for row in value['rows']:
            key = tuple(row[k] for k in KEYS)
            require(key not in seen, 'Duplicate stored ratio exposure'); seen.add(key)
            for label in ('numerator', 'denominator'):
                sample = row[label]; expected = originals.get(key + (sample['roi'],))
                require(expected is not None and pairs.canonical(sample) == pairs.canonical(expected),
                        'Ratio sample/source identity differs')
            n, d = row['numerator'], row['denominator']
            require(n['roi'] == config['numerator_roi'] and d['roi'] == config['denominator_roi'] and
                    all(row[k] == n[k] == d[k] for k in (*KEYS, 'detector', 'amplifier', 'exposure_seconds')) and
                    row['signal_adu'] == row['numerator_signal_adu'] == n['signal_adu'] and
                    row['denominator_signal_adu'] == d['signal_adu'] and row['roi'] == 'ratio',
                    'Ratio row metadata/source differs')
            require(type(row['reference_included']) is bool, 'Ratio membership must be boolean')
            if row['reference_included']: members.append({k: row[k] for k in KEYS})
            require(all(row[k] is None or finite(row[k]) for k in
                    ('raw_ratio', 'normalized_ratio', 'ratio_departure_percent')), 'Invalid saved ratio values')
        require(len(seen) == len([r for r in line['rows'] if r['roi'] == config['numerator_roi']]),
                'Ratio exposure coverage differs')
        require(norm['members'] == members and norm['count'] == len(members), 'Ratio reference membership differs')
        require(norm['reference_ratio'] is None or (finite(norm['reference_ratio']) and norm['reference_ratio'] > 0),
                'Invalid saved ratio reference')
        require(tree['file']['sha256'] == value['transport_sha256'], 'Ratio table fingerprint differs')
        self.progress(f'Validated ratio diagnostics: {len(value["rows"])} rows')
        return value, identity
