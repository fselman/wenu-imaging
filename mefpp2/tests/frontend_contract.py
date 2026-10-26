"""Test the public configure/make contract with a recorded, deliberately fake backend."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(sys.argv.pop(1)).resolve()


class FrontendContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='mefpp frontend ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'source with spaces'
        self.native = self.repo / 'mefpp2'
        (self.native / 'cmake').mkdir(parents=True)
        for name in ('configure', 'Makefile', 'cmake/frontend.sh'):
            shutil.copy2(SOURCE / name, self.native / name)
        # Entry fixture: emulate the root dispatch; real root files are exercised by integration.
        (self.repo / 'configure').write_text('#!/bin/sh\nexec ./mefpp2/configure "$@"\n')
        (self.repo / 'configure').chmod(0o755)
        (self.repo / 'Makefile').write_text(
            (SOURCE / 'Makefile').read_text().replace('./cmake/', './mefpp2/cmake/'))
        self.tools = self.root / 'tools'
        self.tools.mkdir()
        self.log = self.root / 'calls.jsonl'
        backend = '''import json, os, sys
from pathlib import Path
args = sys.argv[1:]
if Path(sys.argv[0]).name == 'ctest': action = 'check'
elif args[0] == '--build': action = 'build'
elif args[0] == '--install': action = 'install'
else: action = 'configure'
with open(os.environ['FRONTEND_TRACE'], 'a') as f:
    f.write(json.dumps({'action':action, 'args':args, 'destdir':os.environ.get('DESTDIR')})+'\\n')
if os.environ.get('FRONTEND_FAIL') == action: sys.exit(57)
'''
        self.cmake = self.tool('cmake', backend)
        self.tool('ctest', backend)
        self.compiler = self.tool('compiler', 'pass\n')
        self.funpack = self.tool('funpack', 'pass\n')
        self.make = shutil.which('make')
        assert self.make
        self.env = os.environ.copy()
        for key in ('CC', 'AR', 'RANLIB', 'LD', 'MAKE', 'CMAKE', 'FUNPACK', 'PYTHON',
                    'DESTDIR', 'FRONTEND_FAIL'):
            self.env.pop(key, None)
        self.env.update(CMAKE=str(self.cmake), CC=str(self.compiler),
                        FUNPACK=str(self.funpack), MAKE=self.make,
                        FRONTEND_TRACE=str(self.log))

    def tool(self, name, body):
        path = self.tools / name
        path.write_text('#!' + sys.executable + '\n' + body)
        path.chmod(0o755)
        return path

    def run_at(self, cwd, *args, extra=None):
        env = self.env.copy()
        if extra:
            env.update(extra)
        return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def configure(self, cwd=None, *args, extra=None):
        return self.run_at(cwd or self.repo, './configure', *args, extra=extra)

    def test_help_and_unconfigured_make(self):
        # Help/no-configuration: help is read-only; make cannot use an unconfigured build.
        result = self.configure(None, '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.repo / '.mefpp-config').exists())
        result = self.run_at(self.repo, self.make)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Run ./configure first', result.stderr)
        self.assertEqual(self.calls(), [])

    def test_root_build_install_and_destdir_forwarding(self):
        # Public sequence: configure -> make -> make install, with literal spaced paths/staging.
        prefix = self.root / 'prefix with spaces'
        result = self.configure(None, '--prefix=' + str(prefix))
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.calls()[0]['args']
        self.assertIn('-DMEFPP_C_STANDARD=90', config)
        self.assertIn('-DBUILD_TESTING=OFF', config)
        self.assertIn('-DCMAKE_INSTALL_PREFIX=' + str(prefix), config)
        self.assertEqual(self.run_at(self.repo, self.make).returncode, 0)
        result = self.run_at(self.repo, self.make, 'install', extra={'DESTDIR': str(self.root/'stage')})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([c['action'] for c in self.calls()], ['configure', 'build', 'build', 'install'])
        self.assertEqual(self.calls()[-1]['destdir'], str(self.root/'stage'))

    def test_component_directory_and_literal_build_path(self):
        # Component entry: select C17 and preserve spaces/dollar signs as data, without eval.
        build = self.root / 'build $literal with spaces'
        result = self.configure(self.native, '--build-dir=' + str(build), '--c-standard=17')
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_at(self.native, self.make)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls()[-1]['args'], ['--build', str(build), '--parallel', '1'])

    def test_failed_reconfigure_invalidates_selected_build(self):
        # Configure failure: propagate nonzero and block stale previous configuration.
        self.assertEqual(self.configure().returncode, 0)
        result = self.configure(extra={'FRONTEND_FAIL': 'configure'})
        self.assertEqual(result.returncode, 57)
        result = self.run_at(self.repo, self.make)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No successful configuration', result.stderr)

    def test_build_failure_prevents_install_and_install_failure_propagates(self):
        # Make failures: failed compilation prevents install; installer errors also remain nonzero.
        self.assertEqual(self.configure().returncode, 0)
        result = self.run_at(self.repo, self.make, 'install', extra={'FRONTEND_FAIL': 'build'})
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('install', [c['action'] for c in self.calls()])
        result = self.run_at(self.repo, self.make, 'install', extra={'FRONTEND_FAIL': 'install'})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls()[-1]['action'], 'install')

    def test_missing_tools_are_clear_and_invalidate_configuration(self):
        # Missing tools: explain the prerequisite and never leave an old build selected.
        self.assertEqual(self.configure().returncode, 0)
        result = self.configure(extra={'FUNPACK': '/nonexistent/mefpp-test-funpack'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('funpack', result.stderr)
        self.assertNotEqual(self.run_at(self.repo, self.make).returncode, 0)
        result = self.configure(extra={'CMAKE': '/nonexistent/mefpp-test-cmake'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CMake not found', result.stderr)

    def test_optional_check_enables_tests_and_uses_matching_ctest(self):
        # Developer checks: enable tests, rebuild and run the CTest beside the selected CMake.
        self.assertEqual(self.configure().returncode, 0)
        result = self.run_at(self.repo, self.make, 'check')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls()
        self.assertEqual([c['action'] for c in calls], ['configure', 'configure', 'build', 'check'])
        self.assertIn('-DBUILD_TESTING=ON', calls[1]['args'])
        self.assertIn('--no-tests=error', calls[-1]['args'])

    def test_mac_defaults_use_xcode_tools(self):
        # Platform simulation: verify Xcode selection/SDK arguments without claiming Mac execution.
        compiler = self.compiler
        self.tool('uname', 'import sys\nprint("Darwin" if sys.argv[1] == "-s" else "x86_64")\n')
        self.tool('xcrun', 'import sys\nprint(' + repr(str(compiler)) + ' if sys.argv[1] == "--find" else "/fake SDK")\n')
        env = {'PATH': str(self.tools) + os.pathsep + self.env['PATH'], 'CC': ''}
        result = self.configure(extra=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        args = self.calls()[0]['args']
        for key in ('CMAKE_C_COMPILER', 'CMAKE_AR', 'CMAKE_RANLIB', 'CMAKE_LINKER'):
            self.assertIn('-D' + key + '=' + str(compiler), args)
        self.assertIn('-DCMAKE_OSX_SYSROOT=/fake SDK', args)
        self.assertIn('-DCMAKE_OSX_ARCHITECTURES=x86_64', args)

    def test_in_source_build_directory_is_rejected_early(self):
        # Source protection: reject a source-tree root as the binary directory before CMake.
        for path in (self.native, self.repo, self.repo / 'nonexistent/..'):
            result = self.configure(None, '--build-dir=' + str(path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('separate binary directory', result.stderr)
            self.assertEqual(self.calls(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
