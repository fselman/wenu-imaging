"""Actual correction writers with real FITS; model predictions are deterministic mocks."""
import ast
import hashlib
import logging
import os
import shutil
from pathlib import Path
import tempfile
import unittest

import numpy as np
from astropy.io import fits
from astropy.table import Table, MaskedColumn

ROOT = Path(os.environ.get('PYCAVI_SOURCE_ROOT', Path(__file__).resolve().parents[1]))
PACKAGE = ROOT/'Pycavi2/pycavi'
if os.environ.get('PYCAVI_TEST_INSTALLED'):
    import pycavi
    PACKAGE = Path(pycavi.__file__).resolve().parent
SOURCE = PACKAGE/'pycavi/pycavi_catalogue.py'
NAMES = {'load_catalogue', '_illumination_model_digest', '_illumination_already_applied',
         '_record_illumination_model', 'apply_chebyshev_illumination_correction',
         'apply_kriggin_illumination_correction'}
DELTA = np.array([.123456789, -.02, .030001])


def functions():
    namespace = dict(np=np, fits=fits, Table=Table, hashlib=hashlib, logging=logging, os=os)
    # Only model parsing/prediction is stubbed. Actual writers, FITS I/O and
    # provenance/repeat helpers execute unchanged from the tested package.
    namespace['parse_cheb_file'] = lambda path: dict(dimx=100, dimy=200, x_deg=1,
        y_deg=1, polynomials_x=[], polynomials_y=[], coefficients=[])
    namespace['evaluate_2dpoly'] = lambda *args: DELTA.copy()
    namespace['RegularGridInterpolator'] = lambda *args, **kwargs: lambda points: DELTA.copy()
    nodes = [node for node in ast.parse(SOURCE.read_text()).body
             if isinstance(node, ast.FunctionDef) and node.name in NAMES]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace


class IlluminationNullTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.api = functions()
        if os.environ.get('PYCAVI_TEST_INSTALLED'):
            self.assertEqual(SOURCE.read_bytes(),(ROOT/'Pycavi2/pycavi/pycavi/pycavi_catalogue.py').read_bytes())

    def fixture(self, method='chebyshev', band='r_SDSS'):
        path = self.directory/(method+'_'+band+'.fits')
        table = Table({
            'SOURCE_ID_gaia': MaskedColumn([3022567708255397889, 0, 3022566746182719105], mask=[0,1,0]),
            'flags': MaskedColumn(np.array([1,2,0], dtype=np.int16), mask=[0,0,1]),
            'reference_flux': [1.,np.nan,3.],
        })
        table['reference_flux'].unit = 'Jy'
        for tag in ('r_sdss','nb_659'):
            table['x_image_'+tag] = [10.,20.,30.]
            table['y_image_'+tag] = [15.,25.,35.]
            table['mag_auto_'+tag] = np.array([15.,16.,17.], dtype=np.float32)
            table['mag_petro_'+tag] = np.array([15.1,16.1,17.1], dtype=np.float64)
            table['magerr_auto_'+tag] = [.01,.02,.03]
            table['flux_petro_'+tag] = [100.,200.,300.]
        primary = fits.PrimaryHDU()
        primary.header['OBJECT'] = 'Synthetic writer regression'
        fits.HDUList([primary,fits.BinTableHDU(table)]).writeto(path)
        model = self.directory/(method+'_'+band+'.model')
        if method == 'chebyshev':
            model.write_bytes(b'Deterministic mocked Chebyshev model')
        else:
            fits.PrimaryHDU(np.zeros((4,4)), header=fits.Header(
                {'BAND':band,'ORIG_W':100,'ORIG_H':200})).writeto(model)
        name = 'apply_chebyshev_illumination_correction' if method == 'chebyshev' else 'apply_kriggin_illumination_correction'
        return path, model, self.api[name]

    def assert_preserved(self, before, after, changed):
        self.assertEqual(before.colnames, after.colnames)
        for name in before.colnames:
            self.assertEqual(before[name].dtype, after[name].dtype)
            np.testing.assert_array_equal(np.ma.getmaskarray(before[name]), np.ma.getmaskarray(after[name]))
            if name not in changed:
                self.assertEqual(np.asarray(before[name]).tobytes(), np.asarray(after[name]).tobytes(), name)
            else:
                expected = (np.asarray(before[name])+DELTA).astype(before[name].dtype)
                np.testing.assert_array_equal(after[name], expected)

    def test_both_writers_preserve_integer_nulls_other_columns_and_extension_header(self):
        for method in ('chebyshev','kriging'):
            with self.subTest(method=method):
                path, model, apply = self.fixture(method)
                before = Table.read(path, hdu=1)
                header = fits.getheader(path,1).tostring()
                model_bytes = model.read_bytes()
                self.assertEqual(apply(str(model),str(path)),1)
                after = Table.read(path, hdu=1)
                self.assert_preserved(before,after,{'mag_auto_r_sdss','mag_petro_r_sdss'})
                self.assertEqual(fits.getheader(path,1).tostring(),header)
                self.assertEqual(after['SOURCE_ID_gaia'].mask.tolist(),[False,True,False])
                self.assertEqual(int(after['SOURCE_ID_gaia'][0]),3022567708255397889)
                self.assertEqual(model.read_bytes(),model_bytes)
                self.assertEqual(fits.getheader(path)['OBJECT'],'Synthetic writer regression')

    def test_repeat_call_is_byte_identical_and_records_model_hash(self):
        for method in ('chebyshev','kriging'):
            with self.subTest(method=method):
                path,model,apply = self.fixture(method)
                self.assertEqual(apply(str(model),str(path)),1)
                header = fits.getheader(path)
                keys = [key for key in header if key.startswith('ILLCOR')]
                self.assertEqual(len(keys),1)
                suffix = keys[0][6:]
                self.assertEqual(header['ILHASH'+suffix],hashlib.sha256(model.read_bytes()).hexdigest())
                self.assertEqual(header['ILFILE'+suffix],model.name)
                original = path.read_bytes()
                self.assertEqual(apply(str(model),str(path)),0)
                self.assertEqual(path.read_bytes(),original)

    def test_different_model_is_rejected_without_catalogue_changes(self):
        for method in ('chebyshev','kriging'):
            with self.subTest(method=method):
                path,model,apply = self.fixture(method)
                apply(str(model),str(path))
                before = path.read_bytes()
                if method == 'chebyshev':
                    model.write_bytes(b'Changed deterministic mocked model')
                else:
                    with fits.open(model,mode='update') as hdus:
                        hdus[0].header['CHANGED'] = True
                with self.assertRaises(ValueError):
                    apply(str(model),str(path))
                self.assertEqual(path.read_bytes(),before)

    def test_two_band_updates_preserve_all_nulls_and_each_other(self):
        path,model,apply = self.fixture()
        original = Table.read(path,hdu=1)
        apply(str(model),str(path))
        after_r = Table.read(path,hdu=1)
        second = self.directory/'NB_659.model'
        second.write_bytes(b'Second deterministic mocked model')
        apply(str(second),str(path))
        after_both = Table.read(path,hdu=1)
        self.assert_preserved(after_r,after_both,{'mag_auto_nb_659','mag_petro_nb_659'})
        for name in ('SOURCE_ID_gaia','flags'):
            np.testing.assert_array_equal(np.ma.getmaskarray(original[name]),np.ma.getmaskarray(after_both[name]))
        self.assertEqual(len([key for key in fits.getheader(path) if key.startswith('ILLCOR')]),2)

    def test_extra_hdu_and_original_input_copy_are_unchanged(self):
        for method in ('chebyshev','kriging'):
            with self.subTest(method=method):
                original,model,apply = self.fixture(method)
                with fits.open(original,mode='append') as hdus:
                    hdus.append(fits.ImageHDU(np.arange(12,dtype=np.int16).reshape(3,4),name='UNCHANGED'))
                before = original.read_bytes()
                copied = self.directory/(method+'_copy.fits')
                shutil.copy2(original,copied)
                apply(str(model),str(copied))
                self.assertEqual(original.read_bytes(),before)
                with fits.open(original) as a, fits.open(copied) as b:
                    self.assertEqual(len(a),len(b))
                    self.assertEqual(a[2].header.tostring(),b[2].header.tostring())
                    self.assertEqual(a[2].data.tobytes(),b[2].data.tobytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
