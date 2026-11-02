"""Safety controls for the Chapman runner; no install, network or native tests."""
from pathlib import Path
import platform
import runpy
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).with_name('qualify_m5_asdf_chapman.py')
check = runpy.run_path(str(RUNNER))['check_virtual_platform']


class ChapmanGuards(unittest.TestCase):
    def test_platform_requires_actual_glibc_and_architecture(self):
        # Reject dependency plans claiming a platform newer/different than Chapman.
        check(dict(platform='linux-64', virtual_pkgs=[['__glibc', '2.17', '0']]), '2.17')
        for info in (dict(platform='linux-64', virtual_pkgs=[['__glibc', '2.28', '0']]),
                     dict(platform='linux-64', virtual_pkgs=[]),
                     dict(platform='osx-64', virtual_pkgs=[['__glibc', '2.17', '0']])):
            with self.assertRaises(RuntimeError):
                check(info, '2.17')

    @unittest.skipIf(platform.node().split('.')[0] == 'chapman4', 'Wrong-host control is for agent host')
    def test_wrong_host_stops_before_directory_creation(self):
        # Execute real CLI guard; no target path may be created on a rejected host.
        root = Path(tempfile.mkdtemp(prefix='chapman-guard-'))
        work = root / 'must-not-exist'
        result = subprocess.run([sys.executable, '-B', str(RUNNER), '--revision', '0' * 40,
                                 '--run', str(work)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Chapman4 only', result.stderr)
        self.assertFalse(work.exists())
        print('RETAINED GUARD CASE:', root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
