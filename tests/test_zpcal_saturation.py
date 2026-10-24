"""Exercise the actual zpcal writer without catalogue queries or plotting."""
import ast
import hashlib
import shutil
from datetime import datetime
import importlib.util
import logging
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import warnings

import numpy as np
from astropy.io import fits

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Pycavi2'))
from pycavi.pycavi.pycavi_metadata import calibrated_saturation_cards


def actual_writer():
    # Compile the unchanged writer body from the actual module. Importing the
    # whole zpcal module initializes unrelated remote catalogue clients.
    path = Path(importlib.util.find_spec('pycavi.pycavi.pycavi_zpcal').origin)
    tree = ast.parse(path.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ZPCalibration')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'update_frame')
    namespace = {'np': np, 'fits': fits, 'logging': logging, 'datetime': datetime,
                 'pycavi_tools': SimpleNamespace(pycavi_qc_plot_hist=Mock()),
                 'calibrated_saturation_cards': calibrated_saturation_cards}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['update_frame']


class SaturationTests(unittest.TestCase):
    def test_real_pilot_values_are_in_physical_pixel_units(self):
        factor = 2.10315823839273e-19
        cards = calibrated_saturation_cards(1759.4343046875001, factor, -21.374,
                                           input_saturate=1735.307911879)
        self.assertAlmostEqual(cards['SATLEVEL'] / factor, 1759.4343046875001)
        self.assertAlmostEqual(cards['SATURATE'] / factor, 1735.307911879)
        self.assertTrue(np.isfinite(cards['MAGSATL']))

    def test_unknown_saturation_is_not_invented(self):
        for value in (None, 'UNKNOWN', np.nan, np.inf, 0., -1.):
            cards = calibrated_saturation_cards(value, 1e-19, -21.374)
            self.assertEqual(cards['SATLEVEL'], 'UNKNOWN')
            self.assertEqual(cards['MAGSATL'], 'UNKNOWN')
            self.assertNotIn('SATURATE', cards)
        cards = calibrated_saturation_cards(10., 1e-19, -21.374, input_saturate='UNKNOWN')
        self.assertEqual(cards['SATURATE'], 'UNKNOWN')

    def test_invalid_conversion_factors_fail(self):
        for factor in (0., -1., np.inf, np.nan):
            with self.assertRaises(ValueError):
                calibrated_saturation_cards(10., factor, -21.374)

    def fixture(self, path, satlevel=None):
        header = fits.Header({'BUNIT': 'e-/s', 'SATURATE': 1735.307911879,
                              'MJD-OBS': 57823., 'MJD-END': 57823.1})
        if satlevel is not None:
            header['SATLEVEL'] = satlevel
        fits.writeto(path, np.arange(20, dtype=np.float32).reshape(4, 5), header)
        keyword = {'HIERARCH ESO PYCAVI QC BUNIT': 'erg/s/cm**2/A',
                   'HIERARCH ESO PYCAVI QC MAGZP': -21.374,
                   'HIERARCH ESO PYCAVI QC MAGSKY': 20.,
                   'HIERARCH ESO PYCAVI QC SKYSTD': 1e-20}
        return SimpleNamespace(frame=str(path), keyword=keyword,
                               comment={key: '' for key in keyword}, magzp=-21.374,
                               factor_dn_to_flambda=2.10315823839273e-19,
                               mefpp_header_cards=[],
                               phase3_cards=[('SATLEVEL', 1759.4343046875001, 'Original e-/s')],
                               instrument=SimpleNamespace(img_sec_x1=0, img_sec_x2=4,
                                                          img_sec_y1=0, img_sec_y2=5))

    def run_writer(self, obj):
        # The existing writer's hard-coded 10000:10100 QC window is empty in
        # these deliberately small fixtures; it does not affect pixel updates.
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='Mean of empty slice', category=RuntimeWarning)
            actual_writer()(obj)

    def test_writer_does_not_restore_unscaled_parent_card(self):
        for original_level in (None, 1759.4343046875001):
            with self.subTest(original_level=original_level), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'image.fits'
                obj = self.fixture(path, original_level)
                self.run_writer(obj)
                data, header = fits.getdata(path, header=True)
                np.testing.assert_allclose(data, np.arange(20).reshape(4, 5)*obj.factor_dn_to_flambda, rtol=1e-6)
                self.assertAlmostEqual(header['SATLEVEL']/obj.factor_dn_to_flambda, 1759.4343046875001)
                self.assertAlmostEqual(header['SATURATE']/obj.factor_dn_to_flambda, 1735.307911879)
                self.assertEqual(header['BUNIT'], 'erg/s/cm**2/A')
                self.assertEqual(header['MJD-OBS'], 57823.)

    def test_repeat_uses_cumulative_parent_but_incremental_native_scale(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'image.fits'
            obj = self.fixture(path)
            self.run_writer(obj)
            first_data, first_header = fits.getdata(path, header=True)
            first_data = first_data.copy()  # Detach the memmap before the second write.
            obj.factor_dn_to_flambda = 1.1
            self.run_writer(obj)
            second_data, second_header = fits.getdata(path, header=True)
            np.testing.assert_allclose(second_data, first_data*1.1, rtol=1e-6)
            cumulative = second_header['ESO PYCAVI QC DN2FLAM']
            self.assertAlmostEqual(second_header['SATLEVEL']/cumulative, 1759.4343046875001)
            self.assertAlmostEqual(second_header['SATURATE']/first_header['SATURATE'], 1.1)

    def test_existing_result_can_be_repaired_without_rescaling_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'old-calibration.fits'
            output = Path(directory) / 'corrected-copy.fits'
            factor = 2.10315823839273e-19
            header = fits.Header({'BUNIT': 'erg/s/cm**2/A', 'MAGZP': -21.374,
                                  'SATLEVEL': 1759.4343046875001,
                                  'SATURATE': 1735.307911879, 'MJD-OBS': 57823.})
            fits.writeto(source, np.arange(20, dtype=np.float32).reshape(4, 5)*factor, header)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            shutil.copy2(source, output)
            with fits.open(output, mode='update', do_not_scale_image_data=True) as hdus:
                hdus[0].header.update(calibrated_saturation_cards(
                    1759.4343046875001, factor, -21.374, input_saturate=1735.307911879))
                hdus[0].add_checksum()
            with fits.open(source, do_not_scale_image_data=True) as before, fits.open(output, do_not_scale_image_data=True) as after:
                self.assertEqual(before[0].data.tobytes(), after[0].data.tobytes())
                self.assertEqual(before[0].data.dtype, after[0].data.dtype)
                self.assertEqual(after[0].header['BUNIT'], before[0].header['BUNIT'])
                self.assertEqual(after[0].header['MJD-OBS'], before[0].header['MJD-OBS'])
                self.assertEqual(after[0].verify_checksum(), 1)
                self.assertAlmostEqual(after[0].header['SATLEVEL']/factor, 1759.4343046875001)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)

    def test_writer_without_parent_saturation_uses_input_units(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'image.fits'
            obj = self.fixture(path, 100.)
            obj.phase3_cards = []
            self.run_writer(obj)
            header = fits.getheader(path)
            self.assertAlmostEqual(header['SATLEVEL']/obj.factor_dn_to_flambda, 100.)


if __name__ == '__main__':
    unittest.main()
