"""Numerical TOML admission. Synthetic edits only; no FITS or native execution."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_linearity_config as config


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.detector = (ROOT/'config/detectors/omegacam-1x1.toml').read_text()
        self.processing = (ROOT/'config/processing/omegacam-characterization.toml').read_text()

    def test_real_config_resolves_samples_not_full_bands(self):
        value = config.resolve(self.detector, self.processing)
        self.assertEqual(len(value['detectors']), 32)
        self.assertEqual(sum(len(d['rois']) for d in value['detectors']), 160)
        first = value['detectors'][0]
        self.assertEqual(first['full_regions']['overscan'], [2097,2144,1,4200])
        self.assertEqual(first['native_settings']['overscan'], [2100,2142])
        self.assertEqual(first['native_settings']['trim'], [51,2094,5,4095])
        upper = next(d for d in value['detectors'] if d['detector_id']=='ESO_CCD_#81')
        self.assertEqual(upper['native_settings']['overscan'], [5,48])
        self.assertEqual(upper['native_settings']['trim'], [51,2094,105,4195])
        self.assertEqual((first['scan_kept'],upper['scan_kept']), (23,24))
        self.assertEqual(value['sources']['processing_toml']['text'], self.processing)
        self.assertEqual(value, json.loads(json.dumps(value, allow_nan=False)))

    def test_missing_controls_and_no_paf_fallback(self):
        for old in ('linearity_preparation_schema_version = 1\n', 'raw_saturation_adu = 65534.0\n'):
            with self.assertRaises(ValueError):
                config.resolve(self.detector, self.processing.replace(old,''))
        # Historical PAF locator is provenance only and is never opened or applied.
        altered = self.processing.replace('source_paf = "mefpp2/ins/mef/config/omegacam.paf"',
                                           'source_paf = "/nonexistent/unused.paf"')
        self.assertEqual(config.resolve(self.detector, altered)['detectors'][0]['scan_kept'],23)

    def test_sample_bounds_edges_and_retained_roi_validation(self):
        for old,new in [('overscan_sample = [2100, 2142, 1, 4200]', 'overscan_sample = [2090, 2142, 1, 4200]'),
                        ('overscan_sample = [2100, 2142, 1, 4200]', 'overscan_sample = [2100, 2142, 2, 4200]'),
                        ('xmax = 640', 'xmax = 3000')]:
            with self.assertRaises(ValueError):config.resolve(self.detector,self.processing.replace(old,new,1))

    def test_typed_flags_ranges_and_sample_counts(self):
        for old,new in [('use_overscan = 1','use_overscan = true'),
                        ('scan_reject_high = 10','scan_reject_high = 40'),
                        ('raw_saturation_adu = 65534.0','raw_saturation_adu = nan'),
                        ('bias_min_frames = 3','bias_min_frames = true'),
                        ('bias_mean_max_adu = 1000.0','bias_mean_max_adu = -1.0')]:
            with self.assertRaises(ValueError):config.resolve(self.detector,self.processing.replace(old,new,1))

    def test_unknown_detector_and_duplicate_roi_fail(self):
        with self.assertRaises(ValueError):
            config.resolve(self.detector,self.processing.replace('detector = "ESO_CCD_#65"','detector = "UNKNOWN"',1))
        with self.assertRaises(ValueError):
            config.resolve(self.detector,self.processing.replace('id = "CCD65.serial_far"','id = "CCD65.near_readout"',1))

    def test_outputs_do_not_share_mutable_settings(self):
        result = config.resolve(self.detector,self.processing);saved=deepcopy(result)
        result['detectors'][0]['native_settings']['overscan'][0]=1
        self.assertEqual(result['detectors'][0]['samples']['overscan'][0],2100)
        self.assertEqual(saved,config.resolve(self.detector,self.processing))


if __name__ == '__main__':unittest.main()
