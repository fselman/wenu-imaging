"""Launcher boundaries tested without starting a server or changing a kernel."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'tools/start_remote_notebook.py'
spec = importlib.util.spec_from_file_location('remote_notebook_launcher', path)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class RemoteNotebookLauncherTests(unittest.TestCase):
    def test_wrong_machine_stops_before_kernel_lookup(self):
        with patch.object(launcher.platform, 'system', return_value='Darwin'):
            with self.assertRaisesRegex(ValueError, 'chapman3'):
                launcher.prepare_launch(Path('/tmp'), 8888)

    def test_wrong_environment_stops(self):
        with patch.object(launcher.platform, 'system', return_value='Linux'), \
             patch.object(launcher.platform, 'node', return_value='chapman3'), \
             patch.object(launcher.sys, 'prefix', '/wrong-environment'):
            with self.assertRaisesRegex(ValueError, 'wenu-imaging/bin/python'):
                launcher.prepare_launch(Path('/tmp'), 8888)

    def test_safe_command_dry_run_and_wrong_kernel(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            environment = home / '.conda/envs/wenu-imaging'
            python = environment / 'bin/python'
            kernel = types.SimpleNamespace(argv=[str(python), '-m', 'ipykernel_launcher'])
            manager = types.SimpleNamespace(get_kernel_spec=lambda name: kernel)
            fake_module = types.SimpleNamespace(KernelSpecManager=lambda: manager)
            with patch.object(launcher.platform, 'system', return_value='Linux'), \
                 patch.object(launcher.platform, 'node', return_value='chapman3.sc.eso.org'), \
                 patch.object(launcher.Path, 'home', return_value=home), \
                 patch.object(launcher.sys, 'prefix', str(environment)), \
                 patch.object(launcher.sys, 'executable', str(python)), \
                 patch.object(launcher.importlib.util, 'find_spec', return_value=object()), \
                 patch.object(launcher.shutil, 'which', return_value='/usr/bin/nice'), \
                 patch.dict(sys.modules, {'jupyter_client.kernelspec': fake_module}):
                command, env = launcher.prepare_launch(home, 8899)
                self.assertEqual(command[:4], ['/usr/bin/nice', '-n', '10', str(python)])
                self.assertIn('--ip=127.0.0.1', command)
                self.assertIn('--ServerApp.port_retries=0', command)
                self.assertEqual(env['OPENBLAS_NUM_THREADS'], '1')
                with patch.object(launcher.os, 'execve') as execute:
                    self.assertEqual(launcher.main(['--root', temp, '--dry-run']), 0)
                    execute.assert_not_called()
                kernel.argv[0] = '/wrong/python'
                with self.assertRaisesRegex(ValueError, 'outside'):
                    launcher.prepare_launch(home, 8888)


if __name__ == '__main__':
    unittest.main()
