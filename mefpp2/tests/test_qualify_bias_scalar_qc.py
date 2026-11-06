"""Regression of the actual qualification controller's configure invocation.

Mocks only target tools/platform; it does not claim native Mac qualification.
"""
import argparse
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import qualify_bias_scalar_qc_mac as gate


class ConfigureCommandTests(unittest.TestCase):
    def test_qualified_c17_and_sdk_survive_fresh_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = root / 'reference'
            (reference / 'mefpp2').mkdir(parents=True)
            (reference / 'mefpp2/mefpp_m5').touch()
            prefix = root / 'libasdf'
            (prefix / 'include/asdf').mkdir(parents=True)
            asdf = root / 'asdf-python'
            asdf.touch()
            (reference / 'CMakeCache.txt').write_text(
                f'MEFPP_ASDF_PREFIX:PATH={prefix}\n'
                'MEFPP_C_STANDARD:STRING=17\n'
                'CMAKE_C_COMPILER:FILEPATH=/retained/clang\n'
                'CMAKE_OSX_SYSROOT:PATH=/retained/SDK\n'
            )
            options = argparse.Namespace(work=root / 'work', reference_build=reference,
                                         revision='a' * 40, asdf_python=asdf)
            real_is_file = Path.is_file
            called = []

            class ConfigureCaptured(Exception):
                pass

            def capture(argv, **kwargs):
                called.append(argv)
                self.assertIn('-DMEFPP_C_STANDARD=17', argv)
                self.assertIn('-DCMAKE_C_COMPILER:FILEPATH=/retained/clang', argv)
                self.assertIn('-DCMAKE_OSX_SYSROOT:PATH=/retained/SDK', argv)
                self.assertIn('-DMEFPP_ASDF_PREFIX=' + str(prefix), argv)
                raise ConfigureCaptured

            with patch.object(gate.argparse.ArgumentParser, 'parse_args', return_value=options), \
                 patch.object(gate.platform, 'system', return_value='Darwin'), \
                 patch.object(gate.sys, 'executable', '/Users/fselman/anaconda3/envs/wenu-imaging/bin/python'), \
                 patch.object(gate.os, 'getpriority', return_value=10), \
                 patch.object(Path, 'is_file', lambda p: str(p) == '/opt/local/bin/cmake' or real_is_file(p)), \
                 patch.object(gate.subprocess, 'run', side_effect=capture), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(ConfigureCaptured):
                    gate.main()
            self.assertEqual(len(called), 1)


if __name__ == '__main__':
    unittest.main()
