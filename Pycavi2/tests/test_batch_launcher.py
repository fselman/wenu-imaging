"""Exercise batch process priority and status without a real pilot environment."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
try:
    spec = importlib.util.spec_from_file_location('batch_launcher', TOOLS / 'run_batch.py')
    batch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(batch)
finally:
    sys.path.pop(0)


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux niceness semantics')
class BatchLauncherTests(unittest.TestCase):
    def test_dry_run_does_not_change_priority_or_execute(self):
        with patch.object(batch, 'validate_runtime'), \
             patch.object(batch.os, 'setpriority') as priority, \
             patch.object(batch.os, 'execvpe') as execute:
            self.assertEqual(batch.main(['--dry-run', '--', 'echo', 'a b']), 0)
            priority.assert_not_called()
            execute.assert_not_called()

    def test_wrong_runtime_stops_before_priority_or_execution(self):
        with patch.object(batch, 'validate_runtime', side_effect=ValueError('wrong host')), \
             patch.object(batch.os, 'setpriority') as priority, \
             patch.object(batch.os, 'execvpe') as execute:
            with self.assertRaises(SystemExit):
                batch.main(['--', 'echo', 'unused'])
            priority.assert_not_called()
            execute.assert_not_called()

    def test_real_child_and_grandchild_priority_parent_unchanged_and_exit_status(self):
        before = os.getpriority(os.PRIO_PROCESS, 0)
        # Only substitute the pilot machine check; exercise real setpriority/exec.
        probe = ('import os,subprocess,sys,json; '
                 'print(json.dumps([os.getpriority(os.PRIO_PROCESS,0), '
                 'int(subprocess.check_output([sys.executable,"-c",'
                 '"import os; print(os.getpriority(os.PRIO_PROCESS,0))"]))])); '
                 'sys.exit(7)')
        code = ('import sys; sys.path.insert(0,sys.argv[1]); import run_batch; '
                'run_batch.validate_runtime=lambda:None; '
                'run_batch.main(["--",sys.executable,"-c",sys.argv[2]])')
        result = subprocess.run([sys.executable, '-c', code, str(TOOLS), probe],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(json.loads(result.stdout.splitlines()[-1]),
                         [max(10, before)] * 2)
        self.assertEqual(os.getpriority(os.PRIO_PROCESS, 0), before)


if __name__ == '__main__':
    unittest.main()
