"""Regression for Conda diagnostics contaminating machine-readable stdout.

Uses only synthetic Python subprocesses; no Conda, network or native execution.
"""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

run_logged = runpy.run_path(str(Path(__file__).with_name('qualify_libasdf_mac.py')))['run_logged']


class TrialLoggingTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='asdf-trial-logging-'))
        self.commands = []
        print('RETAINED LOGGING CASE:', self.work)

    def invoke(self, code):
        with redirect_stdout(io.StringIO()):
            return run_logged('fixture', [sys.executable, '-B', '-c', code],
                work=self.work, env=dict(os.environ), commands=self.commands, capture=True)

    def test_json_with_plugin_warning_is_not_contaminated(self):
        output = self.invoke('import sys; sys.stderr.write("plugin warning\\n"); '
                             'sys.stdout.write(\'{"virtual_pkgs":[["__osx","13.7.8","0"]]}\')')
        self.assertEqual(json.loads(output)['virtual_pkgs'][0][1], '13.7.8')
        self.assertEqual((self.work / 'fixture.log').read_text(), output)
        self.assertEqual((self.work / 'fixture.stderr.log').read_text(), 'plugin warning\n')
        self.assertEqual(self.commands[0]['exit_status'], 0)

    def test_failed_process_preserves_both_streams_and_fails(self):
        with self.assertRaisesRegex(RuntimeError, 'Failed: fixture'):
            self.invoke('import sys; sys.stdout.write("partial output"); '
                        'sys.stderr.write("dependency failure"); sys.exit(7)')
        self.assertEqual((self.work / 'fixture.log').read_text(), 'partial output')
        self.assertEqual((self.work / 'fixture.stderr.log').read_text(), 'dependency failure')
        self.assertEqual(self.commands[0]['exit_status'], 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
