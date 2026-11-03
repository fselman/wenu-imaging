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


class CondaCliTests(unittest.TestCase):
    def discover(self, version, global_help, extra_create):
        cli = runpy.run_path(str(RUNNER))['conda_cli']
        calls = []
        def command(label, argv, capture=False):
            calls.append(list(map(str, argv)))
            if '--no-plugins' in argv and '--no-plugins' not in global_help:
                raise AssertionError('Unsupported plugin flag reached subprocess')
            if label == 'conda-version':
                return 'conda ' + version
            if label == 'conda-help':
                return global_help
            if label == 'conda-create-help':
                return '--repodata-fn --strict-channel-priority --dry-run --json --prefix ' + extra_create
            raise AssertionError('Capability discovery attempted provisioning')
        return cli('/conda', command), calls

    def test_legacy_conda_never_receives_modern_flags(self):
        # Emulate a CLI that rejects --no-plugins and has no solver selector.
        (base, solver, evidence), calls = self.discover('4.10.3', '--version --help', '')
        self.assertEqual(base, ['/conda'])
        self.assertEqual(solver, [])
        self.assertTrue(evidence['legacy_classic_default'])
        self.assertEqual(calls[-1], ['/conda', 'create', '--help'])

    def test_modern_conda_uses_advertised_flags(self):
        (base, solver, evidence), calls = self.discover('24.11.3', '--no-plugins --help', '--solver')
        self.assertEqual(base, ['/conda', '--no-plugins'])
        self.assertEqual(solver, ['--solver', 'classic'])
        self.assertFalse(evidence['legacy_classic_default'])
        self.assertEqual(calls[-1], ['/conda', '--no-plugins', 'create', '--help'])

    def test_transition_selector_and_unknown_modern_cli(self):
        (base, solver, evidence), calls = self.discover('22.9.0', '--help', '--experimental-solver')
        self.assertEqual(solver, ['--experimental-solver', 'classic'])
        with self.assertRaisesRegex(RuntimeError, 'lacks expected solver'):
            self.discover('24.11.3', '--help', '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
