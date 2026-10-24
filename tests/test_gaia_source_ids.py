"""Offline regression of the production query/cache boundary and ID-only repair."""
import ast
import contextlib
import csv
import importlib.util
import io
import json
import logging
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
from astropy.table import Table

ROOT = Path(os.environ.get('PYCAVI_SOURCE_ROOT', Path(__file__).resolve().parents[1]))
if os.environ.get('PYCAVI_TEST_INSTALLED'):
    from pycavi.pycavi import pycavi_gaia_ids as ids
else:
    spec = importlib.util.spec_from_file_location('gaia_ids', ROOT / 'Pycavi2/pycavi/pycavi/pycavi_gaia_ids.py')
    ids = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ids)
# The standalone repair utility imports the installed helper only at match time.
import sys
sys.modules['pycavi.pycavi.pycavi_gaia_ids'] = ids
spec = importlib.util.spec_from_file_location('recover', ROOT / 'Pycavi2/tools/recover_gaia_source_ids.py')
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)
VALUES = np.array([3022567708255397888, 3022566746182719104], dtype=np.int64)


def response():
    table = Table({'source_id': VALUES, 'gspc_source_id': VALUES, 'ra': [88., 88.1], 'dec': [-5., -5.1]})
    table['ra'].unit = table['dec'].unit = 'deg'
    return table


class GaiaIDTests(unittest.TestCase):
    def test_aliases_large_ids_csv_and_fits_roundtrip(self):
        if os.environ.get('PYCAVI_TEST_INSTALLED'):
            self.assertEqual(Path(ids.__file__).read_bytes(),
                             (ROOT / 'Pycavi2/pycavi/pycavi/pycavi_gaia_ids.py').read_bytes())
        original = response()
        result = ids.normalize_gaia_identifiers(original)
        self.assertIn('source_id', original.colnames)
        self.assertNotIn('GSPC_SOURCE_ID', result.colnames)
        np.testing.assert_array_equal(result['SOURCE_ID'], VALUES)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ids.csv'
            result.to_pandas().to_csv(path, index=False)
            frame = ids.read_gaia_csv(path)
            np.testing.assert_array_equal(frame.SOURCE_ID, VALUES)
            fits = path.with_suffix('.fits')
            Table.from_pandas(frame).write(fits)
            np.testing.assert_array_equal(Table.read(fits)['SOURCE_ID'], VALUES)

    def test_bad_ids_fail_without_rounding(self):
        for values in (VALUES.astype(float), np.ma.array(VALUES, mask=[0, 1]),
                       [1, 1], [0, 1], np.array([2**63, 2**63+1], dtype=np.uint64)):
            with self.subTest(values=repr(values)), self.assertRaises(ValueError):
                ids.integer_source_ids(values)
        table = response()
        table['gspc_source_id'][0] += 1
        with self.assertRaises(ValueError):
            ids.normalize_gaia_identifiers(table)
        table = response()
        table['SOURCE_ID'] = VALUES
        with self.assertRaises(ValueError):
            ids.normalize_gaia_identifiers(table)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ids.csv'
            for text in ('', '3.022567708255398e18', '3022567708255397888.0', str(2**63)):
                path.write_text('SOURCE_ID,ra\n' + text + ',88\n')
                with self.subTest(text=text), self.assertRaises(ValueError):
                    ids.read_gaia_csv(path)

    def test_actual_production_method_preserves_ids_and_rejects_bad_cache(self):
        # Execute the actual method body with a mocked TAP client, not a copied
        # parser. This isolates unrelated imports and performs no calibration.
        source = ROOT / 'Pycavi2/pycavi/pycavi/pycavi_zpcal.py'
        if os.environ.get('PYCAVI_TEST_INSTALLED'):
            import importlib.util
            source = Path(importlib.util.find_spec('pycavi.pycavi.pycavi_zpcal').origin)
        tree = ast.parse(source.read_text())
        method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                      and node.name == 'get_gaia_dr3_gspc_df')
        table = response()
        for band in ('u_sdss', 'g_sdss', 'r_sdss', 'i_sdss', 'z_sdss',
                     'phot_g_mean', 'phot_bp_mean', 'phot_rp_mean'):
            table[band + '_flux'] = [100., 200.]
            table[band + '_flux_error'] = [1., 2.]
            table[band + '_mag'] = [14., 15.]
        table['classprob_dsc_combmod_star'] = [1., 1.]
        client = SimpleNamespace(launch_job_async=Mock(return_value=SimpleNamespace(get_results=lambda: table)))
        namespace = {'np': np, 'pd': pd, 'os': os, 'logging': logging, 'Gaia': client,
                     'normalize_gaia_identifiers': ids.normalize_gaia_identifiers,
                     'read_gaia_csv': ids.read_gaia_csv,
                     'pycavi_tools': SimpleNamespace(create_ds9_reg_file=Mock())}
        exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec'), namespace)
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            instance = SimpleNamespace(crval1=88., crval2=-5., query_radius=.7, band='r_SDSS',
                                       object='CN_Ori', calibrationdir=directory, query_max_mag=20.)
            result = namespace[method.name](instance)
            np.testing.assert_array_equal(result.SOURCE_ID, VALUES)
            np.testing.assert_array_equal(result.r_SDSS, [14., 15.])
            query = client.launch_job_async.call_args.args[0]
            self.assertIn('dr3.source_id AS SOURCE_ID', query)
            self.assertIn('gspc.source_id AS GSPC_SOURCE_ID', query)
            namespace[method.name](instance)
            self.assertEqual(client.launch_job_async.call_count, 1)
            raw = Path(directory) / 'gaia3_qry_CN_Ori_raw.csv'
            clean = Path(instance.phot_cal_clean)
            clean_hash = recovery.sha256(clean)
            bad = pd.read_csv(raw)
            bad['SOURCE_ID'] = np.nan
            bad.to_csv(raw, index=False)
            with self.assertRaises(ValueError):
                namespace[method.name](instance)
            self.assertEqual(recovery.sha256(clean), clean_hash)
            self.assertEqual(client.launch_job_async.call_count, 1)


class RecoveryTests(unittest.TestCase):
    def manifest(self, directory):
        path = Path(directory) / 'raw.csv'
        path.write_text('SOURCE_ID,raj2000,dej2000,flux,note\n,88.0000000,-5.0,1.234500e-18,"a,b"\n,88.1,-5.1,,x\n')
        return [{'path': str(path), 'sha256': recovery.sha256(path), 'group': 'r_SDSS'}]

    def test_recovery_changes_only_identifier_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.manifest(directory)
            entries, query, cap = recovery.prepare(manifest)
            self.assertIn('SELECT TOP 5', query)
            self.assertNotIn('flux', query)
            output = Path(directory) / 'output'
            output.mkdir()
            details = recovery.recover(entries, response(), cap, output)
            with Path(details[0]['output']).open(newline='') as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(rows[1][0], str(VALUES[0]))
            self.assertEqual(rows[1][1:], ['88.0000000', '-5.0', '1.234500e-18', 'a,b'])
            self.assertTrue(details[0]['non_id_fields_unchanged'])
            self.assertEqual(recovery.sha256(manifest[0]['path']), manifest[0]['sha256'])
            with self.assertRaises(ValueError):
                recovery.recover(entries, response(), cap, output)

    def test_missing_ambiguous_truncated_or_duplicate_matches_fail(self):
        coords = np.array([[88., -5.], [88.1, -5.1]])
        for kind in ('missing', 'ambiguous', 'cap', 'duplicate'):
            table = response()
            cap = 10
            if kind == 'missing':
                table['ra'][0] += .001
            elif kind == 'ambiguous':
                table.add_row((3022567708255397999, 3022567708255397999, 88., -5.))
            elif kind == 'cap':
                cap = 2
            else:
                coords = np.array([[88., -5.], [88., -5.]])
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                recovery.match_ids(coords, table, cap)

    def test_all_matches_checked_before_publishing_and_inputs_hash_guarded(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.manifest(directory)
            entries, query, cap = recovery.prepare(manifest)
            output = Path(directory) / 'output'
            output.mkdir()
            table = response()
            table['ra'][0] += .001
            with self.assertRaises(ValueError):
                recovery.recover(entries, table, cap, output)
            self.assertEqual(list(output.iterdir()), [])
            Path(manifest[0]['path']).write_text('changed')
            with self.assertRaises(ValueError):
                recovery.prepare(manifest)

    def test_preflight_has_no_writes_or_network_and_timeout_has_no_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'manifest.json'
            manifest.write_text(json.dumps(self.manifest(directory)))
            output = Path(directory) / 'new-output'
            arguments = ['recover', '--manifest', str(manifest), '--output', str(output)]
            with patch.object(sys, 'argv', arguments), patch.object(recovery.subprocess, 'run') as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    recovery.main()
                run.assert_not_called()
                self.assertFalse(output.exists())
            with patch.object(sys, 'argv', arguments + ['--allow-network']), \
                    patch.object(recovery.os, 'getpriority', return_value=10), \
                    patch.object(recovery.subprocess, 'run', side_effect=__import__('subprocess').TimeoutExpired('query', 180)) as run:
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(__import__('subprocess').TimeoutExpired):
                    recovery.main()
                self.assertEqual(run.call_count, 1)
                self.assertEqual(run.call_args.kwargs['timeout'], 180)
                self.assertEqual(json.loads((output / 'report.json').read_text())['status'], 'fail')
                self.assertFalse((output / 'catalogues').exists())

    def test_single_job_records_identity_and_native_result(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            job = SimpleNamespace(jobid='mock-123', get_phase=lambda: 'COMPLETED', get_results=Mock())
            def save():
                self.assertTrue((directory / 'job.json').exists())
                raw = directory / 'response.vot'
                response().write(raw, format='votable')
                from xml.etree import ElementTree as ET
                tree = ET.parse(raw)
                ET.SubElement(tree.getroot(), 'INFO', name='QUERY_STATUS', value='OK')
                tree.write(raw, encoding='utf-8')
            job.save_results = save
            client = SimpleNamespace(launch_job_async=Mock(return_value=job))
            recovery.retrieve(directory, 'SELECT TOP 5 ...', client)
            self.assertEqual(client.launch_job_async.call_count, 1)
            self.assertTrue((directory / 'response.vot').exists())
            self.assertEqual(json.loads((directory / 'job.json').read_text())['job_id'], 'mock-123')


if __name__ == '__main__':
    unittest.main(verbosity=2)
