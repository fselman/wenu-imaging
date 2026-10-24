"""Gaia dependency query/response contracts; no live requests in this suite."""
import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / 'Pycavi2/tools/_gaia_dr3_probe.py'


def load_worker():
    spec = importlib.util.spec_from_file_location('gaia_probe', WORKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QueryTests(unittest.TestCase):
    def test_explicit_small_join_and_notebook_sdss_columns(self):
        worker = load_worker()
        query = worker.build_query()
        self.assertIn('SELECT TOP 5 ', query)
        self.assertIn('JOIN gaiadr3.synthetic_photometry_gspc', query)
        self.assertIn('gspc.source_id = dr3.source_id', query)
        self.assertIn('CONTAINS', query)
        self.assertAlmostEqual(worker.RADIUS_DEG * 60, 5)
        # Compare the existing scientific function's actual literal field lists.
        source = ROOT / 'Pycavi2/pycavi/pycavi/pycavi_zpcal.py'
        tree = ast.parse(source.read_text())
        function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                        and n.name == 'get_gaia_dr3_gspc_df')
        bands = next(ast.literal_eval(n.value) for n in ast.walk(function)
                     if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
                     and t.id == 'bands_list_sdss' for t in n.targets))
        self.assertEqual(set(bands), {'gspc.' + c for c in worker.GSPC_COLUMNS})
        for column in worker.DR3_COLUMNS:
            self.assertIn('dr3.' + column, query)


@unittest.skipUnless(importlib.util.find_spec('astropy') and importlib.util.find_spec('numpy'),
                     'Requires NumPy and Astropy')
class ResponseTests(unittest.TestCase):
    def table(self, count=2):
        import numpy as np
        from astropy.table import Table
        worker = load_worker()
        table = Table({c: np.full(count, 1.) for c in worker.REQUIRED_COLUMNS}, masked=True)
        ids = np.arange(count, dtype=np.int64) + 3200000000000000001
        table['source_id'] = ids
        table['gspc_source_id'] = ids.copy()
        table['ra'] = np.full(count, worker.CENTER[0])
        table['dec'] = np.full(count, worker.CENTER[1])
        table['ra'].unit = table['dec'].unit = 'deg'
        return table

    def test_null_ancillary_data_preserved_and_large_integer_ids_exact(self):
        table = self.table()
        table['radial_velocity'].mask = True
        table['u_sdss_mag'].mask = True
        details = load_worker().validate_table(table)
        self.assertEqual(details['rows'], 2)
        self.assertEqual(details['source_ids'][0], '3200000000000000001')
        self.assertEqual(details['null_or_nonfinite_counts']['radial_velocity'], 2)
        self.assertEqual(details['usable_ri_rows'], 2)
        self.assertEqual(details['column_units']['ra'], 'deg')

    def test_archive_column_case_is_handled_without_changing_native_table(self):
        table = self.table()
        table.rename_column('source_id', 'SOURCE_ID')
        details = load_worker().validate_table(table)
        self.assertIn('SOURCE_ID', details['columns'])
        self.assertIn('SOURCE_ID', table.colnames)
        self.assertNotIn('source_id', table.colnames)

    def test_invalid_schema_count_join_coordinates_and_photometry_rejected(self):
        changes = {
            'missing': lambda t: t.remove_column('r_sdss_mag'),
            'join': lambda t: t['gspc_source_id'].__setitem__(0, 2),
            'outside': lambda t: t['ra'].__setitem__(0, 90.),
            'unit': lambda t: setattr(t['ra'], 'unit', None),
            'photometry': lambda t: t['r_sdss_flux'].__setitem__(slice(None), -1.),
            'float_ids': lambda t: t.replace_column('source_id', t['source_id'].astype(float)),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                table = self.table()
                change(table)
                with self.assertRaises(ValueError):
                    load_worker().validate_table(table)
        for count in (0, 6):
            with self.subTest(count=count), self.assertRaises(ValueError):
                load_worker().validate_table(self.table(count))

    def test_single_async_job_raw_response_and_provenance_preserved(self):
        from astropy.table import Table
        table = self.table()
        calls = []
        class Client:
            def launch_job_async(client, query, **kwargs):
                calls.append((query, kwargs))
                class Job:
                    jobid = 'synthetic-test-job'
                    def save_results(job):
                        table.write(kwargs['output_file'], format='votable')
                    def get_results(job):
                        return Table.read(kwargs['output_file'], format='votable')
                    def get_phase(job):
                        return 'COMPLETED'
                return Job()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            details = load_worker().run_probe(root, Client())
            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0][1]['background'])
            self.assertTrue(calls[0][1]['dump_to_file'])
            self.assertEqual(Table.read(root / 'response.vot')['source_id'][0],
                             3200000000000000001)
            self.assertEqual(json.loads((root / 'job.json').read_text())['job_id'],
                             'synthetic-test-job')
            self.assertEqual(details['rows'], 2)
            original = (root / 'response.vot').read_bytes()
            with self.assertRaises(FileExistsError):
                load_worker().run_probe(root, Client())
            self.assertEqual(len(calls), 1)
            self.assertEqual((root / 'response.vot').read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
