"""The notebook display must evaluate the saved model, including field edges."""
import ast
from importlib import resources
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Pycavi2'))
from pycavi.pycavi import pycavi_chebyshev as cheb


def notebook_cell():
    root = Path(__file__).resolve().parents[1] / 'Pycavi2/pycavi/notebooks'
    name = '08a_pycavi_illum_chebyshev.ipynb'
    text = ((root / name).read_text() if (root / name).exists() else
            resources.files('pycavi').joinpath('notebooks', name).read_text())
    return ''.join(json.loads(text)['cells'][5]['source'])


def display(coefficients, dimx=317, dimy=223):
    # Execute the actual notebook assignment, with a deliberately rectangular
    # grid and asymmetric field to expose transposition/coordinate mistakes.
    nodes = ast.parse(notebook_cell()).body
    assignment = next(n for n in nodes if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'grid_z'
                              for t in n.targets))
    gx, gy = np.mgrid[1:dimx:11j, 1:dimy:7j]
    namespace = dict(grid_x=gx, grid_y=gy, dimx=dimx, dimy=dimy,
                     coeffs=coefficients, deg=(5, 5),
                     chebyshev_2d_eval=cheb.chebyshev_2d_eval)
    exec(compile(ast.Module(body=[assignment], type_ignores=[]),
                 '<notebook display>', 'exec'), namespace)
    return gx, gy, namespace['grid_z']


class ChebyshevDisplayTests(unittest.TestCase):
    def test_asymmetric_high_orders_match_independent_numpy_at_edges(self):
        coefficients = np.zeros((6, 6))
        coefficients[0, 0] = .03
        coefficients[5, 2] = .07
        coefficients[1, 5] = -.04
        coefficients[5, 5] = .11
        before = coefficients.copy()
        gx, gy, plotted = display(coefficients.ravel())
        expected = np.polynomial.chebyshev.chebval2d(
            2 * (gx - 317 / 2) / 317,
            2 * (gy - 223 / 2) / 223, coefficients).T
        self.assertEqual(plotted.shape, (7, 11))
        np.testing.assert_allclose(plotted, expected, rtol=1e-12, atol=1e-12)
        np.testing.assert_array_equal(coefficients, before)

    def test_saved_model_and_display_agree_across_entire_grid(self):
        coefficients = np.random.default_rng(42).normal(0, .02, 36)
        gx, gy, plotted = display(coefficients)
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / 'model.chebyshev'
            cheb.chebyshev_polynomials((5, 5), coefficients, str(model),
                                      'fixture.fits', dimx=317, dimy=223)
            parsed = cheb.parse_cheb_file(str(model))
            reloaded = cheb.evaluate_2dpoly(
                gx.T, gy.T, parsed['dimx'], parsed['dimy'], (5, 5),
                parsed['polynomials_x'], parsed['polynomials_y'],
                parsed['coefficients'])
        np.testing.assert_allclose(plotted, reloaded, rtol=1e-12, atol=1e-12)

    def test_output_name_identifies_direct_display_and_no_rbf_call_remains(self):
        tree = ast.parse(notebook_cell())
        assignment = next(n for n in tree.body if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == 'inter_type'
                                  for t in n.targets))
        self.assertEqual(ast.literal_eval(assignment.value), 'direct')
        self.assertFalse(any(isinstance(n, ast.Call)
                             and isinstance(n.func, ast.Name)
                             and n.func.id in ('Rbf', 'griddata')
                             for n in ast.walk(tree)))


if __name__ == '__main__':
    unittest.main()
