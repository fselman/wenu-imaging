"""Offline catalogue and notebook regressions using disposable FITS files."""
import ast
from datetime import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.table import Table

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pycavi.pycavi import pycavi_catalogue as catalogue
from pycavi.pycavi.pycavi_chebyshev import chebyshev_polynomials, chebyshev_2d_eval


def notebook_cell(index):
    path = ROOT / 'pycavi/notebooks/09_pycavi_makeCatalogue.ipynb'
    return ''.join(json.loads(path.read_text())['cells'][index]['source'])


def prepare_function():
    # Load the actual preparation function without importing unrelated wrappers.
    path = ROOT / 'pycavi/pycavi/pycavi_astromatic_tools.py'
    node = next(n for n in ast.parse(path.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == 'prepare_to_sextract')
    namespace = {'os': os, 'logging': logging}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace[node.name]


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.path = self.work / 'catalogue.fits'
        self.x = np.array([20., 40., 80.])
        self.y = np.array([30., 50., 70.])
        table = Table({'x_image_r_sdss': self.x, 'y_image_r_sdss': self.y,
                       'mag_auto_r_sdss': [13., 14., 15.],
                       'mag_petro_r_sdss': [13.1, 14.1, 15.1],
                       'magerr_auto_r_sdss': [0.01, 0.02, 0.03],
                       'flux_petro_r_sdss': [100., 200., 300.],
                       'r_SDSS_gaia': [13., 14., 15.]})
        fits.HDUList([fits.PrimaryHDU(), fits.BinTableHDU(table)]).writeto(self.path)
        self.model_path = self.work / 'target_r_SDSS.chebyshev'
        self.coeffs = np.array([0.02, 0.01, -0.015, 0.003])
        chebyshev_polynomials((1, 1), self.coeffs, str(self.model_path), 'test.fits', 100, 100)

    def test_clean_single_two_and_three_filters(self):
        for bands in (['r_SDSS'], ['r_SDSS', 'g_SDSS'], ['r_SDSS', 'g_SDSS', 'i_SDSS']):
            with self.subTest(bands=bands):
                data = {}
                for i, band in enumerate(bands):
                    data['ALPHA_J2000_' + band] = np.array([120., 121., np.nan]) + i * .00001
                    data['DELTA_J2000_' + band] = np.array([-35., -36., -37.]) + i * .00001
                    for kind in ('auto', 'iso', 'petro', 'best'):
                        data['MAGERR_' + kind.upper() + '_' + band] = np.ones(3) * .02
                clean = catalogue.clean_merged_catalogue(Table(data), {b: 4 for b in bands})
                self.assertEqual(len(clean), 2)
                np.testing.assert_allclose(clean['raj2000'], np.array([120., 121.]) + np.mean(np.arange(len(bands))) * .00001)
                np.testing.assert_allclose(clean['dej2000'], np.array([-35., -36.]) + np.mean(np.arange(len(bands))) * .00001)
                np.testing.assert_allclose(clean['magerr_auto_r_sdss'], .04)

    def test_chebyshev_sign_provenance_and_repeat_are_correct(self):
        before = fits.getdata(self.path, 1).copy()
        expected = chebyshev_2d_eval(self.x, self.y, 100, 100, self.coeffs, (1, 1))
        self.assertEqual(catalogue.apply_chebyshev_illumination_correction(str(self.model_path), str(self.path)), 1)
        after = fits.getdata(self.path, 1)
        for name in ('mag_auto_r_sdss', 'mag_petro_r_sdss'):
            np.testing.assert_allclose(after[name], before[name] + expected)
        for name in ('magerr_auto_r_sdss', 'flux_petro_r_sdss', 'r_SDSS_gaia', 'x_image_r_sdss'):
            np.testing.assert_array_equal(after[name], before[name])
        header = fits.getheader(self.path)
        self.assertEqual(header['ILLCOR00'], 'r_sdss')
        self.assertEqual(header['ILHASH00'], hashlib.sha256(self.model_path.read_bytes()).hexdigest())
        saved = self.path.read_bytes()
        self.assertEqual(catalogue.apply_chebyshev_illumination_correction(str(self.model_path), str(self.path)), 0)
        self.assertEqual(saved, self.path.read_bytes())
        self.model_path.write_text(self.model_path.read_text() + '\n# changed model identity\n')
        with self.assertRaisesRegex(ValueError, 'different illumination model'):
            catalogue.apply_chebyshev_illumination_correction(str(self.model_path), str(self.path))
        self.assertEqual(saved, self.path.read_bytes())

    def test_legacy_band_marker_prevents_reapplication(self):
        with fits.open(self.path, mode='update') as hdul:
            hdul[0].header['ILLCOR03'] = 'r_SDSS'
        saved = self.path.read_bytes()
        self.assertEqual(catalogue.apply_chebyshev_illumination_correction(str(self.model_path), str(self.path)), 0)
        self.assertEqual(saved, self.path.read_bytes())

    def test_kriging_uses_shared_repeat_guard(self):
        path = self.work / 'r.kriging.fits'
        header = fits.Header({'BAND': 'r_SDSS', 'ORIG_W': 100, 'ORIG_H': 100})
        fits.writeto(path, np.full((6, 6), .02), header)
        before = fits.getdata(self.path, 1)['mag_auto_r_sdss'].copy()
        self.assertEqual(catalogue.apply_kriggin_illumination_correction(str(path), str(self.path)), 1)
        np.testing.assert_allclose(fits.getdata(self.path, 1)['mag_auto_r_sdss'], before + .02)
        saved = self.path.read_bytes()
        self.assertEqual(catalogue.apply_kriggin_illumination_correction(str(path), str(self.path)), 0)
        self.assertEqual(saved, self.path.read_bytes())

    def test_prepare_uses_real_catalogue_path_and_redo(self):
        prepare = prepare_function()
        image = str(self.work / 'image.fits')
        output = self.work / 'image.cat'
        self.assertTrue(prepare(image, False))
        output.write_text('old catalogue')
        self.assertFalse(prepare(image, False))
        self.assertEqual(output.read_text(), 'old catalogue')
        self.assertTrue(prepare(image, True))
        self.assertFalse(output.exists())

    def test_notebook_creation_and_correction_preserve_baseline(self):
        # Exercise the real notebook cells and FITS/catalogue functions; only
        # external source extraction is replaced by a small deterministic table.
        science = str(self.work / 'science/CP_Pup')
        cal = Path(science) / 'Calibration_dir'
        cal.mkdir(parents=True)
        target = cal / 'CP_Pup_r_SDSS.coadd.fits'
        header = fits.Header({'FILTER': 'r_SDSS', 'OBJECT': 'CP Pup', 'MAGZP': 21.,
                              'RA': 122.9, 'DEC': -35.3})
        header['HIERARCH ESO PYCAVI QC DN2FLAM'] = 1.
        fits.writeto(target, np.ones((4, 4)), header)
        pd.DataFrame({'raj2000': [122.9, 123.], 'dej2000': [-35.3, -35.4],
                      'r_SDSS': [13., 14.]}).to_csv(cal / 'gaia3_qry_CP_Pup_raw.csv', index=False)
        def extract(path, directory, pars):
            self.assertTrue(Path(directory).is_dir())
            self.assertEqual(pars['MAG_ZEROPOINT'], 21.)
            data = {'ALPHA_J2000': [122.9, 123.], 'DELTA_J2000': [-35.3, -35.4],
                    'X_IMAGE': [20., 40.], 'Y_IMAGE': [30., 50.], 'MAG_AUTO': [13., 14.]}
            for kind in ('AUTO', 'ISO', 'PETRO', 'BEST'):
                data['MAGERR_' + kind] = [.01, .02]
            fits.HDUList([fits.PrimaryHDU(), fits.BinTableHDU(), fits.BinTableHDU(Table(data))]).writeto(str(path)[:-5] + '.cat', overwrite=True)
        runner = Mock(side_effect=extract)
        other_science = str(self.work / 'science/Other')
        other_cal = Path(other_science) / 'Calibration_dir'
        shutil.copytree(cal, other_cal)
        other_target = other_cal / target.name
        env = {'os': os, 'Path': Path, 'logging': logging, 'np': np, 'pd': pd,
               'fits': fits, 'Table': Table, 'datetime': datetime,
               'hashlib': hashlib, 'shutil': shutil,
               'zpcal_dict': {science: [str(target)], other_science: [str(other_target)]},
               'config': {'Directories': {'sex_dir_name': 'Sextractor_dir'}},
               'pycavi_astromatic_tools': SimpleNamespace(prepare_to_sextract=prepare_function(), run_sextractor_on_target=runner)}
        for name in ('getheaderfromframe', 'load_catalogue', 'crossmatch_catalogues',
                     'clean_merged_catalogue', 'apply_chebyshev_illumination_correction',
                     'apply_kriggin_illumination_correction'):
            env[name] = getattr(catalogue, name)
        # No reduced_science_dir or target_name supplied: fresh-kernel regression.
        exec(notebook_cell(3), env)
        baseline = cal / 'CP_Pup_merged_catalogue.fits'
        other_baseline = other_cal / baseline.name
        self.assertFalse(other_baseline.exists())
        saved = baseline.read_bytes()
        self.assertEqual(len(fits.getdata(baseline, 1)), 2)
        datetime.fromisoformat(fits.getheader(baseline)['DATE'])
        exec(notebook_cell(3), env)
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(saved, baseline.read_bytes())
        # Selecting the second object must not be affected by filter-loop indices.
        exec(notebook_cell(3).replace('idx_selected = [0]', 'idx_selected = [1]'), env)
        self.assertTrue(other_baseline.exists())
        self.assertEqual(saved, baseline.read_bytes())
        env['selected_illumination_models'] = {}
        with self.assertRaisesRegex(ValueError, 'Select model paths explicitly'):
            exec(notebook_cell(6), env)
        env['selected_illumination_models'] = {science: {'r_SDSS': str(self.model_path)}}
        exec(notebook_cell(6), env)
        output = Path(env['corrected_catalogues'][0])
        self.assertNotEqual(output, baseline)
        self.assertEqual(saved, baseline.read_bytes())
        corrected_bytes = output.read_bytes()
        exec(notebook_cell(6), env)
        self.assertEqual(corrected_bytes, output.read_bytes())
        # An existing copy cannot silently be reused with a rebuilt baseline.
        with fits.open(baseline, mode='update') as hdul:
            hdul[0].header['TEST'] = True
        with self.assertRaisesRegex(ValueError, 'different baseline'):
            exec(notebook_cell(6), env)


if __name__ == '__main__':
    unittest.main()
