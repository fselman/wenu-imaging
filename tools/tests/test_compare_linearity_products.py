"""Physical-label matching must retain exact numerical and population comparisons."""
from copy import deepcopy
import importlib.util
import math
import sys
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('compare_linearity',
    Path(__file__).resolve().parents[1]/'compare-linearity-products.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'Pycavi2/pycavi/pycavi'))
import pycavi_pair_qc as pair_qc
import pycavi_sample_qc as sample_qc


def context(prefix, indices, pair):
    flats = [dict(path='/raw/'+name+'.fits', hdu=1, asset=prefix+name, index=i, pair=pair)
             for name, i in zip(('A', 'B'), indices)]
    biases = [dict(path='/raw/bias.fits', hdu=1, asset=prefix+'bias', index=0, accepted=1),
              dict(path='/raw/bias-second.fits', hdu=1, asset=prefix+'bias-second', index=1, accepted=1)]
    images = {row['path']: dict(sha256=str(i)*64) for i, row in enumerate(flats+biases, 1)}
    images['/cal/master.fits'] = dict(sha256='f'*64)
    return dict(selection=dict(flat=flats, bpm=dict(encoding='omitted')), biases=biases,
                master=dict(product='/cal/master.fits', hdu=1), dependency_evidence=dict(images=images),
                resolved=dict(controls=dict(with_mad=True), detectors=[dict(detector_id='CCD', rois=['R'])]))


def raw_bias_table(prefix):
    # Exercise the real decoder, including nullable text-column units and the
    # original text/hash envelope, with a structurally valid unavailable RON.
    columns = pair_qc.BIAS_COLUMNS
    row = dict.fromkeys(columns, 0)
    row.update(schema_version=1, detector='CCD', amplifier='A', roi='R',
               bias1_asset=prefix+'bias', bias2_asset=prefix+'bias-second',
               bias1_hdu=1, bias2_hdu=1, region_pixels=1, bpm_excluded=1,
               saturation_raw_adu=65534.0, pair_time_tolerance_s=0.0)
    for key in pair_qc.BIAS_OPTIONAL:
        row[key] = None
    for prefix_name in ('active', 'raw'):
        for bound in ('xmin', 'xmax', 'ymin', 'ymax'):
            row[prefix_name+'_'+bound] = 1
    text = '\t'.join(columns)+'\n'+'\t'.join('' if row[k] is None else str(row[k]) for k in columns)+'\n'
    return pair_qc.parse_table(text.encode(), 'bias-ron')


def population_table(first):
    columns = 'input_index outside_selected_sites bpm_excluded sample_excluded nonfinite saturated admitted'
    text = columns.replace(' ', '\t')+'\n'+str(first)+'\t0\t0\t0\t0\t0\t1\n'
    return sample_qc.parse_population(text.encode())


def measurements(prefix, first, pair):
    return dict(detector='CCD', measurement_stage='corrected', noise_state='unavailable',
        covariance=None, fit_state='not_performed', units=dict(signal='ADU'),
        rows=[dict(raw=dict(first_asset=prefix+'A', first_input_index=first,
                            second_asset=prefix+'B', second_input_index=first+1, pair_id=pair),
                   corrected=dict(signal_adu=200.0, valid_pixels=12))],
        exposure_rows=[dict(asset=prefix+'A', input_index=first, hdu=1, roi='R', pair_id=pair,
                            signal_adu=200.0, valid_pixels=12, source_pair_directory='pair-0000')],
        direct_site_replay=[dict(asset=prefix+'A', input_index=first, hdu=1, source_roi='R',
                                pair_id=pair, active_x=1, active_y=2, signal_adu=199.5)],
        scan_traces=[dict(role='bias', asset=prefix+'bias', input_index=0, hdu=1,
                          correction_adu=[1.0, 2.0])],
        raw_bias_diagnostics=[dict(pair_directory='pair-0000',
            table=raw_bias_table(prefix), population=population_table(first))])


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.contexts = [context('new-', (10, 11), 'pair-000'), context('old-', (3, 4), 'flat-2s')]
        self.values = [measurements('new-', 10, 'pair-000'), measurements('old-', 3, 'flat-2s')]

    def compare(self):
        return comparison.compare_values(*self.values, *self.contexts)

    def test_physical_bindings_allow_label_and_index_changes(self):
        before = deepcopy(self.values)
        counts = self.compare()
        self.assertEqual(counts, {key: 1 for key in comparison.COLLECTIONS})
        self.assertEqual(self.values, before)

    def test_nullable_units_are_literal_metadata(self):
        units = self.values[0]['raw_bias_diagnostics'][0]['table']['units']
        self.assertIsNone(units['bias1_asset'])
        self.compare()

    def test_unit_change_is_not_hidden(self):
        self.values[0]['raw_bias_diagnostics'][0]['table']['units']['ron_adu'] = 'electron'
        with self.assertRaisesRegex(ValueError, 'raw_bias_diagnostics differs'):
            self.compare()

    def test_unknown_actual_asset_is_still_rejected(self):
        self.values[0]['direct_site_replay'][0]['asset'] = None
        with self.assertRaisesRegex(ValueError, 'Unknown measured asset'):
            self.compare()

    def test_bad_transport_digest_is_rejected(self):
        self.values[0]['raw_bias_diagnostics'][0]['table']['native_tsv_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'transport digest'):
            self.compare()

    def test_decoded_raw_ron_change_is_not_hidden(self):
        self.values[0]['raw_bias_diagnostics'][0]['table']['rows'][0]['bpm_excluded'] = 0
        with self.assertRaisesRegex(ValueError, 'raw_bias_diagnostics differs'):
            self.compare()

    def test_one_float_step_is_not_hidden(self):
        row = self.values[0]['direct_site_replay'][0]
        row['signal_adu'] = math.nextafter(row['signal_adu'], math.inf)
        with self.assertRaisesRegex(ValueError, 'direct_site_replay differs'):
            self.compare()

    def test_changed_population_is_not_hidden(self):
        self.values[0]['exposure_rows'][0]['valid_pixels'] -= 1
        with self.assertRaisesRegex(ValueError, 'exposure_rows differs'):
            self.compare()

    def test_changed_raw_fingerprint_is_rejected(self):
        self.contexts[0]['dependency_evidence']['images']['/raw/A.fits']['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'fingerprints'):
            self.compare()

    def test_changed_pair_membership_is_rejected(self):
        self.contexts[0]['selection']['flat'][1]['pair'] = 'another-pair'
        with self.assertRaisesRegex(ValueError, 'pair membership'):
            self.compare()

    def test_colliding_identity_is_rejected(self):
        self.contexts[0]['selection']['flat'][0]['index'] = 0
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            self.compare()


if __name__=='__main__':
    unittest.main()
