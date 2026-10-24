"""Saved-grid mapping and actual notebook QC calls; no Kriging refitting."""
import ast
import copy
import hashlib
from importlib import resources, util
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
from astropy.io import fits
from scipy.interpolate import RegularGridInterpolator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Pycavi2'))


def library_tree(name):
    path = Path(util.find_spec('pycavi.pycavi.' + name).origin)
    return ast.parse(path.read_text()), path


def actual_reader():
    # Compile the real reader without importing unrelated Kriging fit engines.
    tree, path = library_tree('pycavi_kriging')
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'get_kriging_interpolation')
    namespace = dict(np=np, fits=fits, RegularGridInterpolator=RegularGridInterpolator)
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace[function.name]


class KrigingReadbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'grid.fits'
        self.reader = actual_reader()

    def make_grid(self, nx=7, ny=5):
        self.width, self.height = 301, 151
        self.gx, self.gy = np.meshgrid(np.linspace(1, self.width, nx),
                                     np.linspace(1, self.height, ny))
        self.grid = .001 * self.gx + .002 * self.gy
        header = fits.Header(dict(ORIG_W=self.width, ORIG_H=self.height,
                                  FACTOR=nx, VARIOMOD='gaussian'))
        fits.PrimaryHDU(data=self.grid, header=header).writeto(self.path)

    def test_exact_nodes_endpoints_and_rectangular_returned_grid(self):
        self.make_grid()
        before = hashlib.sha256(self.path.read_bytes()).digest()
        values, gx, gy, stored, header = self.reader(
            str(self.path), self.gx.ravel(), self.gy.ravel())
        np.testing.assert_allclose(values.reshape(self.grid.shape), self.grid,
                                   rtol=0, atol=1e-14)
        np.testing.assert_array_equal(gx, self.gx)
        np.testing.assert_array_equal(gy, self.gy)
        np.testing.assert_array_equal(stored, self.grid)
        self.assertEqual(header['ORIG_W'], self.width)
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).digest(), before)

    def test_affine_interior_and_scalar_values_in_physical_coordinates(self):
        self.make_grid()
        x = np.array([1., 17.25, 111.1, 300.8, 301.])
        y = np.array([151., 90.5, 14.75, 100.2, 1.])
        values, *_ = self.reader(str(self.path), x, y)
        np.testing.assert_allclose(values, .001*x + .002*y, rtol=0, atol=1e-14)
        value, *_ = self.reader(str(self.path), 37.5, 84.25)
        self.assertAlmostEqual(float(value), .001*37.5 + .002*84.25, places=14)

    def test_outside_physical_image_extent_is_rejected(self):
        self.make_grid()
        for x, y in ((0., 1.), (302., 1.), (1., 0.), (1., 152.)):
            with self.subTest(x=x, y=y), self.assertRaises(ValueError):
                self.reader(str(self.path), x, y)

    def test_legacy_square_grid_on_non_square_field(self):
        self.make_grid(50, 50)
        values, *_ = self.reader(str(self.path), self.gx.ravel(), self.gy.ravel())
        np.testing.assert_allclose(values.reshape(50, 50), self.grid,
                                   rtol=0, atol=1e-14)


class NotebookReadbackPlotTests(unittest.TestCase):
    def test_actual_08c_calls_bind_distinct_coordinates_and_residuals(self):
        source = Path(__file__).resolve().parents[1] / 'Pycavi2/pycavi/notebooks'
        name = '08c_pycavi_illum_read_kriging.ipynb'
        text = ((source/name).read_text() if (source/name).exists() else
                resources.files('pycavi').joinpath('notebooks', name).read_text())
        notebook = json.loads(text)
        tree, path = library_tree('pycavi_zpcal')
        namespace = {
            'x_subset': np.array([1000., 2000.]),
            'y_subset': np.array([3000., 4000.]),
            'z_subset': np.array([.01, -.02]),
            'x_check': np.array([1100., 2200.]),
            'y_check': np.array([3300., 4400.]),
            'z_corr': np.array([.001, -.002]),
            'dimx': 10000, 'dimy': 20000,
            'res_plot_str': 'fixture', 'determine_errors': True, 'err_type': 'none',
        }
        for cell_index, function_name, keys in (
            (7, 'plot_corrected_residuals', ('x_check', 'z_corr')),
            (8, 'plot_spatial_residuals', ('x_check', 'y_check', 'z_corr')),
        ):
            with self.subTest(function=function_name):
                # Keep the actual library signature but return its bound args.
                definition = copy.deepcopy(next(
                    n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == function_name))
                definition.body = ast.parse('return locals()').body
                module = ast.fix_missing_locations(ast.Module(
                    body=[definition], type_ignores=[]))
                exec(compile(module, str(path), 'exec'), namespace)
                cell = ast.parse(''.join(notebook['cells'][cell_index]['source']))
                call = next(n for n in ast.walk(cell) if isinstance(n, ast.Call)
                            and isinstance(n.func, ast.Name) and n.func.id == function_name)
                self.assertFalse(call.args, 'QC bindings should use explicit keywords')
                result = eval(compile(ast.Expression(body=call), '<notebook call>', 'eval'),
                              namespace)
                for key in keys:
                    self.assertIs(result[key], namespace[key])


if __name__ == '__main__':
    unittest.main()
