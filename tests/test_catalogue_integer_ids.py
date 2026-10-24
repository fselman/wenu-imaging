"""Actual-function tests: preserve exact integer matches without changing selection."""
import ast
import io
import json
import os
from pathlib import Path
import unittest

import numpy as np
from astropy.table import Table, MaskedColumn, hstack
from astropy.coordinates import SkyCoord
from astropy import units as u

ROOT = Path(os.environ.get('PYCAVI_SOURCE_ROOT', Path(__file__).resolve().parents[1]))
PACKAGE = ROOT / 'Pycavi2/pycavi'
if os.environ.get('PYCAVI_TEST_INSTALLED'):
    import pycavi
    PACKAGE = Path(pycavi.__file__).resolve().parent

source = PACKAGE / 'pycavi/pycavi_catalogue.py'
function = next(node for node in ast.parse(source.read_text()).body
                if isinstance(node, ast.FunctionDef) and node.name == 'crossmatch_catalogues')
namespace = dict(np=np, Table=Table, MaskedColumn=MaskedColumn, hstack=hstack, SkyCoord=SkyCoord, u=u)
exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), namespace)
crossmatch = namespace['crossmatch_catalogues']
IDENTIFIERS = np.array([3022567708255397889, 3022566746182719105], dtype=np.int64)


class CatalogueIntegerTests(unittest.TestCase):
    def tables(self):
        long = Table({'ra_a': [88., 89., 90.], 'de_a': [-5., -5., -5.], 'number_a': [1, 2, 3]})
        short = Table({'ra_b': [88., 90.], 'de_b': [-5., -5.],
                       'source_id_b': IDENTIFIERS, 'flux_b': [1.25, 2.5],
                       'flags_b': np.array([0, 4], dtype=np.int16)})
        short['source_id_b'].description = 'Exact external identifier'
        short['source_id_b'].meta['release'] = 'DR3'
        return long, short

    def match(self, long, short, reverse=False):
        if reverse:
            return crossmatch(short, long, radec_tag_1=['ra_b', 'de_b'], radec_tag_2=['ra_a', 'de_a'])
        return crossmatch(long, short, radec_tag_1=['ra_a', 'de_a'], radec_tag_2=['ra_b', 'de_b'])

    def test_integer_ids_masks_and_float_measurements_both_orders(self):
        for reverse in (False, True):
            long, short = self.tables()
            before = (long.copy(), short.copy())
            result = self.match(long, short, reverse)
            self.assertEqual(len(result), 3)
            self.assertEqual(result['source_id_b'].dtype, np.dtype('int64'))
            np.testing.assert_array_equal(result['source_id_b'][[0, 2]], IDENTIFIERS)
            np.testing.assert_array_equal(result['source_id_b'].mask, [False, True, False])
            self.assertEqual(result['flags_b'].dtype, np.dtype('int16'))
            np.testing.assert_allclose(result['flux_b'], [1.25, np.nan, 2.5], equal_nan=True)
            np.testing.assert_allclose(result['ra_b'], [88., np.nan, 90.], equal_nan=True)
            np.testing.assert_array_equal(result['number_a'], [1, 2, 3])
            self.assertEqual(result['source_id_b'].description, short['source_id_b'].description)
            self.assertEqual(result['source_id_b'].meta, short['source_id_b'].meta)
            for original, actual in zip(before, (long, short)):
                np.testing.assert_array_equal(original.as_array(), actual.as_array())

    def test_fits_roundtrip_keeps_integer_ids_and_missing_mask(self):
        result = self.match(*self.tables())
        buffer = io.BytesIO()
        result.write(buffer, format='fits')
        buffer.seek(0)
        restored = Table.read(buffer, format='fits')
        self.assertEqual(restored['source_id_b'].dtype.kind, 'i')
        self.assertEqual(restored['source_id_b'].dtype.itemsize, 8)
        np.testing.assert_array_equal(restored['source_id_b'].mask, [False, True, False])
        np.testing.assert_array_equal(restored['source_id_b'][[0, 2]], IDENTIFIERS)

    def test_existing_source_masks_and_unsigned_dtype_survive(self):
        long, short = self.tables()
        short['source_id_b'] = MaskedColumn(IDENTIFIERS, mask=[True, False])
        short['flags_b'] = short['flags_b'].astype(np.uint16)
        result = self.match(long, short)
        np.testing.assert_array_equal(result['source_id_b'].mask, [True, True, False])
        self.assertEqual(int(result['source_id_b'][2]), int(IDENTIFIERS[1]))
        self.assertEqual(result['flags_b'].dtype, np.dtype('uint16'))

    def test_integer_ids_in_long_anchor_and_existing_radius_selection(self):
        long, short = self.tables()
        long['source_id_a'] = np.array([2**53+1, 2**53+3, 2**53+5], dtype=np.int64)
        short['ra_b'][0] += .5 / (3600 * np.cos(np.deg2rad(-5.)))
        inside = self.match(long, short)
        np.testing.assert_array_equal(inside['source_id_a'], long['source_id_a'])
        self.assertFalse(inside['source_id_b'].mask[0])
        outside = crossmatch(long, short, max_sep=.1,
                             radec_tag_1=['ra_a','de_a'], radec_tag_2=['ra_b','de_b'])
        np.testing.assert_array_equal(outside['source_id_b'].mask, [True, True, False])

    def test_actual_notebook_reads_gaia_with_exact_cache_reader(self):
        notebook = json.loads((PACKAGE / 'notebooks/09_pycavi_makeCatalogue.ipynb').read_text())
        nodes = [node for cell in notebook['cells'] if cell['cell_type'] == 'code'
                 for node in ast.walk(ast.parse(''.join(cell['source'])))]
        assignments = [node for node in nodes if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == 'gaia_catalogue'
                               for target in node.targets)
                       and isinstance(node.value, ast.Call) and node.value.args
                       and isinstance(node.value.args[0], ast.Name)
                       and node.value.args[0].id == 'query_gaia']
        self.assertEqual(len(assignments), 1)
        self.assertIsInstance(assignments[0].value.func, ast.Name)
        self.assertEqual(assignments[0].value.func.id, 'read_gaia_csv')
        self.assertTrue(any(isinstance(node, ast.ImportFrom)
                            and node.module == 'pycavi.pycavi.pycavi_gaia_ids'
                            and any(alias.name == 'read_gaia_csv' for alias in node.names)
                            for node in nodes))
        if os.environ.get('PYCAVI_TEST_INSTALLED'):
            self.assertEqual(source.read_bytes(),
                             (ROOT / 'Pycavi2/pycavi/pycavi/pycavi_catalogue.py').read_bytes())
            self.assertEqual((PACKAGE / 'notebooks/09_pycavi_makeCatalogue.ipynb').read_bytes(),
                             (ROOT / 'Pycavi2/pycavi/notebooks/09_pycavi_makeCatalogue.ipynb').read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
