"""Physical-label matching must retain exact numerical and population comparisons."""
from copy import deepcopy
import importlib.util
import math
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('compare_linearity',
    Path(__file__).resolve().parents[1]/'compare-linearity-products.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


def context(prefix, indices, pair):
    flats = [dict(path='/raw/'+name+'.fits', hdu=1, asset=prefix+name, index=i, pair=pair)
             for name, i in zip(('A', 'B'), indices)]
    biases = [dict(path='/raw/bias.fits', hdu=1, asset=prefix+'bias', index=0, accepted=1)]
    images = {row['path']: dict(sha256=str(i)*64) for i, row in enumerate(flats+biases, 1)}
    images['/cal/master.fits'] = dict(sha256='f'*64)
    return dict(selection=dict(flat=flats, bpm=dict(encoding='omitted')), biases=biases,
                master=dict(product='/cal/master.fits', hdu=1), dependency_evidence=dict(images=images),
                resolved=dict(controls=dict(with_mad=True), detectors=[dict(detector_id='CCD', rois=['R'])]))


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
            table=dict(rows=[dict(bias1_asset=prefix+'bias', variance=3.0)]),
            population=dict(frames=[dict(input_index=first, admitted=1)]))])


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.contexts = [context('new-', (10, 11), 'pair-000'), context('old-', (1, 2), 'flat-2s')]
        self.values = [measurements('new-', 10, 'pair-000'), measurements('old-', 1, 'flat-2s')]

    def compare(self):
        return comparison.compare_values(*self.values, *self.contexts)

    def test_physical_bindings_allow_label_and_index_changes(self):
        before = deepcopy(self.values)
        counts = self.compare()
        self.assertEqual(counts, {key: 1 for key in comparison.COLLECTIONS})
        self.assertEqual(self.values, before)

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
