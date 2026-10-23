"""Safety and result contracts for the portable dependency-check CLI."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace


TOOL = Path(__file__).resolve().parents[1] / 'Pycavi2/tools/check_dependencies.py'


def load_tool():
    spec = importlib.util.spec_from_file_location('dependency_tool', TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(importlib.util.find_spec('astropy') and importlib.util.find_spec('numpy'),
                     'Numerical fixture checks require Astropy and NumPy')
class ScampOracleTests(unittest.TestCase):
    """Test the synthetic fixture and acceptance oracle, not native SCAMP."""

    def context(self, directory, correct=True, corrupt=False):
        from astropy.io import fits
        context = load_tool().Check(directory)

        def fake_run(command, label):
            if label == 'fit':
                with fits.open(directory / 'input.cat') as hdus:
                    cards = ''.join(card.ljust(80) for card in
                                    hdus[1].data['Field Header Card'][0])
                    header = fits.Header.fromstring(cards, sep='')
                    self.assertEqual(header['NAXIS1'], 1024)
                    self.assertEqual(header['NAXIS2'], 1024)
                    self.assertEqual(header['CTYPE1'], 'RA---TAN')
                    self.assertEqual(len(hdus[2].data), 100)
                with fits.open(directory / 'reference.cat') as hdus:
                    self.assertEqual(len(hdus['LDAC_OBJECTS'].data), 100)
                if correct:
                    header['CRVAL1'] = 123.
                header.totextfile(directory / 'input.head')
                (directory / 'scamp.xml').write_text('<synthetic-test-double/>')
                if corrupt:
                    with (directory / 'input.cat').open('ab') as stream:
                        stream.write(b'changed')
            return SimpleNamespace(stdout='')

        context.run = fake_run
        return context

    def test_known_wcs_is_accepted_and_initial_offset_is_measured(self):
        with tempfile.TemporaryDirectory() as directory:
            result = load_tool().scamp(self.context(Path(directory) / 'test'),
                                      {'scamp': '/synthetic/test-double'})
            self.assertGreater(result['initial_rms_arcsec'], 1.)
            self.assertLess(result['final_rms_arcsec'], 1e-6)

    def test_noop_fit_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(AssertionError, 'Fit did not recover'):
                load_tool().scamp(self.context(Path(directory) / 'test', correct=False),
                                  {'scamp': '/synthetic/test-double'})

    def test_changed_input_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(AssertionError, 'Input changed'):
                load_tool().scamp(self.context(Path(directory) / 'test', corrupt=True),
                                  {'scamp': '/synthetic/test-double'})


class DependencyToolTests(unittest.TestCase):
    def invoke(self, *arguments):
        return subprocess.run([sys.executable, str(TOOL), *map(str, arguments)],
                              capture_output=True, text=True)

    def test_wrong_host_stops_before_output_or_executable_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'result'
            result = self.invoke('sextractor', '--expect-host', 'invalid-host.example',
                                 '--output', output, '--sextractor', '/missing/engine')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Unexpected hostname', result.stderr)
            self.assertFalse(output.exists())

    def test_existing_directory_and_dangling_symlink_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / 'preserve.txt'
            marker.write_text('preserve')
            result = self.invoke('sextractor', '--output', root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), 'preserve')
            link = root / 'dangling'
            link.symlink_to(root / 'missing')
            result = self.invoke('sextractor', '--output', link)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(link.is_symlink())

    def test_dry_run_never_runs_selected_executable_or_creates_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Selecting Python itself would error on an engine invocation. Dry
            # run must only resolve it, even without NumPy/Astropy installed.
            result = self.invoke('sextractor', '--sextractor', sys.executable,
                                 '--expect-host', socket.gethostname().split('.')[0],
                                 '--expect-prefix', sys.prefix,
                                 '--output', root / 'output', '--dry-run')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((root / 'output').exists())

    def test_native_nonzero_is_logged_and_raised(self):
        spec = importlib.util.spec_from_file_location('dependency_tool', TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            context = module.Check(Path(directory) / 'check')
            with self.assertRaises(RuntimeError):
                context.run([sys.executable, '-c',
                             'import sys; print("diagnostic"); sys.exit(7)'], 'failure')
            self.assertEqual(context.commands[0]['exit_code'], 7)
            self.assertIn('diagnostic', (context.directory / 'failure.stdout').read_text())

    @unittest.skipUnless(hasattr(os, 'getpriority') and shutil.which('true'),
                         'Requires POSIX priority support')
    def test_real_child_priority_failure_reporting_and_independent_checks(self):
        parent_priority = os.getpriority(os.PRIO_PROCESS, 0)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'output'
            script = '''
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('dependency_tool', sys.argv[1])
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
def failure(context, paths):
    raise RuntimeError('deliberate failure')
def child(context, paths):
    result = context.run([sys.executable, '-c',
        'import os,json; print(json.dumps({"niceness":os.getpriority(os.PRIO_PROCESS,0),'
        '"threads":os.environ["OPENBLAS_NUM_THREADS"]}))'], 'child')
    return json.loads(result.stdout)
tool.CHECKS['sextractor'] = failure
tool.CHECKS['swarp'] = child
sys.exit(tool.main(['sextractor', 'swarp', '--output', sys.argv[2],
                   '--sextractor', sys.argv[3], '--swarp', sys.argv[3]]))
'''
            result = subprocess.run([sys.executable, '-c', script, str(TOOL),
                                     str(output), shutil.which('true')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((output / 'report.json').read_text())
            self.assertEqual(report['checks']['sextractor']['status'], 'fail')
            self.assertEqual(report['checks']['swarp']['status'], 'pass')
            self.assertGreaterEqual(report['checks']['swarp']['details']['niceness'], 10)
            self.assertEqual(report['checks']['swarp']['details']['threads'], '1')
            self.assertEqual(os.getpriority(os.PRIO_PROCESS, 0), parent_priority)


if __name__ == '__main__':
    unittest.main()
