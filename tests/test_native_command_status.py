"""Exercise actual wrapper function bodies with real subprocesses; no science imports."""
import ast
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "Pycavi2/pycavi/pycavi/pycavi_associate_reduction.py"


class CommandStatusTests(unittest.TestCase):
    def setUp(self):
        # Preparation: execute unmodified production function ASTs, omitting imports.
        tree = ast.parse(SOURCE.read_text())
        names = {"run_commands", "mefpp_reduce_science"}
        body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
        self.ns = dict(os=os, Path=Path, subprocess=subprocess, logging=logging)
        exec(compile(ast.Module(body=body, type_ignores=[]), str(SOURCE), "exec"), self.ns)
        self.tmp = tempfile.TemporaryDirectory(prefix="pycavi-status-")
        self.addCleanup(self.tmp.cleanup)
        self.cwd = Path.cwd()
        os.chdir(self.tmp.name)
        self.addCleanup(os.chdir, self.cwd)

    def run_child(self, code, logfile=None):
        args = [sys.executable, "-c", code]
        return self.ns["run_commands"](args, p_shell=False, logfile=logfile)

    def test_nonzero_without_error_text(self):
        # Native status: nonzero is failure even when stdout/stderr contain no error.
        for log in (None, "native.log"):
            with self.subTest(log=log):
                self.assertEqual(self.run_child("raise SystemExit(7)", log), 1)

    def test_success_and_legacy_error_text(self):
        # Compatibility: retain successful return convention and error-text detection.
        self.assertEqual(self.run_child("print('completed')"), 0)
        self.assertEqual(self.run_child("print('Error legacy failure')", "native.log"), 1)
        self.assertEqual(self.run_child("print('error legacy failure')"), 1)

    def test_verbose_child_does_not_deadlock(self):
        # Pipe handling: child output exceeding pipe capacity must be drained while waiting.
        self.assertEqual(self.run_child("import sys; sys.stdout.write('x'*200000); sys.stderr.write('y'*200000)"), 0)

    def test_spawn_failure_closes_log(self):
        # Launch failure: preserve the exception and close the opened log stream.
        with self.assertRaises(FileNotFoundError):
            self.ns["run_commands"](["/no/such/native-engine"], p_shell=False, logfile="spawn.log")
        Path("spawn.log").unlink()

    def test_science_wrapper_raises_and_restores_cwd(self):
        # Wrapper propagation: real failing child, helper-only setup, restored caller cwd.
        base = Path(self.tmp.name) / "science"
        base.mkdir()
        for name in ("science.list", "BIAS_1x1.fits", "FLAT_r_1x1.fits"):
            (base / name).touch()
        prefix = Path(self.tmp.name) / "engine"
        (prefix / "bin").mkdir(parents=True)
        fake = prefix / "bin/mefpp"
        fake.write_text("#!/bin/sh\nexit 7\n")
        fake.chmod(0o755)
        self.ns["copy_paf"] = lambda *args: True
        self.ns["check_mef_bpm"] = lambda *args: True
        part = type("Partition", (), {})()
        part.base_path, part.filter = str(base), "r"
        instrument = SimpleNamespace(bias_prefix="BIAS", mff_prefix="FLAT")
        original = Path.cwd()
        with self.assertRaisesRegex(Exception, "Error running"):
            self.ns["mefpp_reduce_science"](str(prefix), [part], instrument)
        self.assertEqual(Path.cwd(), original)
        self.assertIn(str(fake), (base / "mefpp_command.txt").read_text())


if __name__ == "__main__":
    unittest.main()
