"""Offline numerical regression tests; no catalogue queries or FITS writes.

Run: python -m unittest discover -s Pycavi2/tests -v
"""
import ast
import importlib.util
import inspect
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "pycavi/pycavi/pycavi_chebyshev.py"
spec = importlib.util.spec_from_file_location("chebyshev_model", MODULE)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class ChebyshevModelTests(unittest.TestCase):
    def test_export_round_trip_matches_numpy_including_highest_orders(self):
        rng = np.random.default_rng(42)
        dimx, dimy = 19099, 19987
        # Include image corners and interior points, and unequal axis degrees.
        x = np.r_[0, dimx, 0, dimx, rng.uniform(0, dimx, 80)]
        y = np.r_[0, 0, dimy, dimy, rng.uniform(0, dimy, 80)]
        for deg in ((0, 0), (1, 1), (2, 4), (5, 5)):
            with self.subTest(deg=deg), tempfile.TemporaryDirectory() as tmp:
                coeffs = rng.normal(0, 0.01, (deg[0] + 1, deg[1] + 1))
                if deg != (0, 0):
                    coeffs[0, 0] = 0  # Sparse file: omitted zero is still zero.
                expected = np.polynomial.chebyshev.chebval2d(
                    2 * x / dimx - 1, 2 * y / dimy - 1, coeffs
                )
                path = Path(tmp) / "model.chebyshev"
                matrix, px, py = model.chebyshev_polynomials(
                    deg, coeffs.ravel(), str(path), "synthetic.fits", dimx, dimy
                )
                np.testing.assert_allclose(model.evaluate_2dpoly(
                    x, y, dimx, dimy, deg, px, py, matrix
                ), expected, atol=1e-12, rtol=1e-12)
                parsed = model.parse_cheb_file(str(path))
                self.assertEqual(set(parsed["polynomials_x"]), set(range(deg[0] + 1)))
                self.assertEqual(set(parsed["polynomials_y"]), set(range(deg[1] + 1)))
                np.testing.assert_allclose(model.evaluate_2dpoly(
                    x, y, parsed["dimx"], parsed["dimy"],
                    (parsed["x_deg"], parsed["y_deg"]),
                    parsed["polynomials_x"], parsed["polynomials_y"],
                    parsed["coefficients"]
                ), expected, atol=1e-12, rtol=1e-12)

    def test_weighted_fit_recovers_known_degree_five_surface(self):
        rng = np.random.default_rng(15)
        x, y = rng.uniform(0, 100, (2, 120))
        coeffs = rng.normal(0, 0.01, 36)
        z = model.chebyshev_2d_eval(x, y, 100, 100, coeffs, (5, 5))
        residuals, fitted, _, rank, _ = model.fit_chebyshev(
            x, y, z, rng.uniform(0.01, 0.03, 120), 100, 100, (5, 5)
        )
        self.assertEqual(rank, 36)
        np.testing.assert_allclose(fitted, coeffs, atol=1e-12, rtol=1e-12)
        np.testing.assert_allclose(residuals, 0, atol=1e-12)

    def test_truncated_legacy_basis_requires_regeneration(self):
        with self.assertRaisesRegex(ValueError, "regenerate"):
            model.evaluate_2dpoly(
                np.array([50.]), np.array([50.]), 100, 100, (1, 1),
                {0: "1"}, {0: "1"}, np.ones((2, 2))
            )


class NotebookPlotContracts(unittest.TestCase):
    def test_calls_bind_residuals_and_save_paths_to_correct_parameters(self):
        # Read actual signatures without importing network-active zpcal module.
        source = ast.parse((ROOT / "pycavi/pycavi/pycavi_zpcal.py").read_text())
        names = {"plot_illumination_correction", "plot_corrected_residuals",
                 "plot_spatial_residuals"}
        signatures = {}
        for node in source.body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                stub = ast.FunctionDef(name=node.name, args=node.args,
                                       body=[ast.Pass()], decorator_list=[])
                namespace = {}
                exec(compile(ast.fix_missing_locations(ast.Module(
                    body=[stub], type_ignores=[])), "<signature>", "exec"), namespace)
                signatures[node.name] = inspect.signature(namespace[node.name])

        for notebook in ("07c_pycavi_zpcal_qc_and_illum.ipynb",
                         "08a_pycavi_illum_chebyshev.ipynb"):
            with self.subTest(notebook=notebook), tempfile.TemporaryDirectory() as tmp:
                seen = {}
                def capture(name):
                    def call(*args, **kwargs):
                        seen[name] = signatures[name].bind(*args, **kwargs).arguments
                    return call
                env = {name: capture(name) for name in names}
                for key in ("x_subset", "y_subset", "z_subset", "x_check", "y_check", "z_corr"):
                    env[key] = np.arange(8.) + len(env)
                gx, gy = np.mgrid[0:100:5j, 0:80:4j]
                gz = gx + 2 * gy
                env.update(grid_x=gx, grid_y=gy, dimx=100, dimy=80,
                           method="Chebyshev", fit_plot=tmp + "/fit.png",
                           fit_image_title="Synthetic", res_plot_str=tmp + "/res",
                           determine_errors=True, err_type="err_simple",
                           grid_z=gz if notebook.startswith("07c") else gz.T,
                           z_on_grid=gz.T)
                cells = json.loads((ROOT / "pycavi/notebooks" / notebook).read_text())["cells"]
                for cell in cells:
                    if cell["cell_type"] != "code":
                        continue
                    text = "".join(cell["source"])
                    # Also ensure every code cell parses.
                    tree = ast.parse(text)
                    if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                           and n.func.id in names for n in ast.walk(tree)):
                        exec(compile(tree, notebook, "exec"), env)
                self.assertEqual(set(seen), names)
                for name in names - {"plot_illumination_correction"}:
                    self.assertIs(seen[name]["z_corr"], env["z_corr"])
                    self.assertIs(seen[name]["x_check"], env["x_check"])
                    self.assertTrue(seen[name]["save_plot"].endswith(".png"))
                surface = seen["plot_illumination_correction"]
                np.testing.assert_equal(surface["grid_z"], surface["grid_x"] + 2 * surface["grid_y"])


if __name__ == "__main__":
    unittest.main()
