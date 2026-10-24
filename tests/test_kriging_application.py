"""Actual cubic catalogue application with real synthetic FITS and SciPy."""
import ast
import hashlib
import logging
import os
from pathlib import Path
import tempfile
import unittest

import numpy as np
from astropy.io import fits
from astropy.table import Table, MaskedColumn
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(os.environ.get('PYCAVI_SOURCE_ROOT', Path(__file__).resolve().parents[1]))
PACKAGE = ROOT/'Pycavi2/pycavi'
if os.environ.get('PYCAVI_TEST_INSTALLED'):
    import pycavi
    PACKAGE = Path(pycavi.__file__).resolve().parent
SOURCE = PACKAGE/'pycavi/pycavi_catalogue.py'
NAMES = {'load_catalogue','_illumination_model_digest','_illumination_already_applied',
         '_record_illumination_model','apply_kriggin_illumination_correction'}
namespace = dict(np=np, fits=fits, Table=Table, hashlib=hashlib, logging=logging,
                 os=os, RegularGridInterpolator=RegularGridInterpolator)
nodes = [node for node in ast.parse(SOURCE.read_text()).body
         if isinstance(node,ast.FunctionDef) and node.name in NAMES]
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),namespace)
apply = namespace['apply_kriggin_illumination_correction']


class KrigingApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        if os.environ.get('PYCAVI_TEST_INSTALLED'):
            self.assertEqual(SOURCE.read_bytes(),(ROOT/'Pycavi2/pycavi/pycavi/pycavi_catalogue.py').read_bytes())

    def fixture(self, coords, shape=(5,6), nonlinear=False):
        x = np.linspace(1,311,shape[1])
        y = np.linspace(1,173,shape[0])
        xx,yy = np.meshgrid(x,y)
        grid = .0007*xx+.0013*yy
        if nonlinear:
            grid += .03*np.sin(xx/70)*np.cos(yy/50)
        model = self.directory/'r_SDSS.kriging.fits'
        fits.PrimaryHDU(grid,header=fits.Header({'BAND':'r_SDSS','ORIG_W':311,
                        'ORIG_H':173})).writeto(model)
        count = len(coords)
        table = Table({'x_image_r_sdss':coords[:,0], 'y_image_r_sdss':coords[:,1],
                       'mag_auto_r_sdss':np.full(count,15.,dtype=np.float64),
                       'mag_petro_r_sdss':np.full(count,16.,dtype=np.float32),
                       'magerr_auto_r_sdss':np.full(count,.02),
                       'flux_petro_r_sdss':np.full(count,100.),
                       'SOURCE_ID_gaia':MaskedColumn(np.full(count,3022567708255397889,dtype=np.int64),
                                                    mask=np.arange(count)%2==1)})
        catalogue = self.directory/'catalogue.fits'
        fits.HDUList([fits.PrimaryHDU(),fits.BinTableHDU(table)]).writeto(catalogue)
        return model,catalogue,grid,x,y

    def check_application(self, coords, shape=(5,6), nonlinear=False):
        model,path,grid,x,y = self.fixture(coords,shape,nonlinear)
        before = Table.read(path,hdu=1)
        extension = fits.getheader(path,1).tostring()
        original = model.read_bytes()
        # Independent direct cubic evaluation on physical (y,x) coordinates.
        expected = RegularGridInterpolator((y,x),grid,method='cubic')(
            np.column_stack((coords[:,1],coords[:,0])))
        self.assertEqual(apply(str(model),str(path)),1)
        after = Table.read(path,hdu=1)
        for name in before.colnames:
            np.testing.assert_array_equal(np.ma.getmaskarray(before[name]),np.ma.getmaskarray(after[name]))
            if name.startswith('mag_auto') or name.startswith('mag_petro'):
                values = np.array(before[name],copy=True)
                values += expected
                np.testing.assert_array_equal(after[name],values)
            else:
                self.assertEqual(np.asarray(before[name]).tobytes(),np.asarray(after[name]).tobytes(),name)
        self.assertEqual(fits.getheader(path,1).tostring(),extension)
        self.assertEqual(model.read_bytes(),original)
        return after,grid,expected

    def test_affine_rectangular_field_grid_interior_and_all_four_corners(self):
        coords = np.array([[1.,1.],[311.,1.],[1.,173.],[311.,173.],[52.,107.],[207.,38.]])
        after,grid,expected = self.check_application(coords)
        analytic = .0007*coords[:,0]+.0013*coords[:,1]
        np.testing.assert_allclose(np.asarray(after['mag_auto_r_sdss'])-15.,analytic,rtol=0,atol=1e-12)

    def test_nonlinear_rectangular_grid_sample_nodes(self):
        xx,yy = np.meshgrid(np.linspace(1,311,6),np.linspace(1,173,5))
        coords = np.column_stack((xx.ravel(),yy.ravel()))
        after,grid,expected = self.check_application(coords,nonlinear=True)
        # Preserve SciPy's existing cubic/default iterative solver; node recovery
        # is subject to its numerical tolerance, not a bit-exact linear read.
        residual = np.asarray(after['mag_auto_r_sdss'])-15.-grid.ravel()
        # Existing gcrotmk defaults rtol=1e-5; RGI supplies an absolute floor
        # of 1e-6. Check its node residual in that same L2 convergence norm.
        bound = max(1e-6, 1e-5*np.linalg.norm(grid))
        self.assertLessEqual(np.linalg.norm(residual), bound*(1+1e-8))

    def test_legacy_square_grid_on_non_square_field(self):
        self.check_application(np.array([[1.,1.],[311.,173.],[135.,82.]]),shape=(5,5))

    def test_outside_physical_extent_rejected_before_catalogue_changes(self):
        for coords in (np.array([[0.,80.]]),np.array([[312.,80.]]),
                       np.array([[30.,0.]]),np.array([[30.,174.]])):
            with self.subTest(coords=coords.tolist()), tempfile.TemporaryDirectory() as temporary:
                self.directory = Path(temporary)
                model,path,*_ = self.fixture(coords)
                before = path.read_bytes()
                with self.assertRaises(ValueError):
                    apply(str(model),str(path))
                self.assertEqual(path.read_bytes(),before)

    def test_repeat_and_changed_model_guards_preserve_catalogue(self):
        model,path,*_ = self.fixture(np.array([[1.,1.],[311.,173.],[80.,40.]]))
        apply(str(model),str(path))
        original = path.read_bytes()
        self.assertEqual(apply(str(model),str(path)),0)
        self.assertEqual(path.read_bytes(),original)
        with fits.open(model,mode='update') as hdus:
            hdus[0].data[0,0] += .001
        with self.assertRaises(ValueError):
            apply(str(model),str(path))
        self.assertEqual(path.read_bytes(),original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
