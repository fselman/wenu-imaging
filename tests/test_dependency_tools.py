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


TOOL = Path(__file__).resolve().parents[1] / 'Pycavi2/tools/check_dependencies.py'


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
