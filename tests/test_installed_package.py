"""Run with a wheel-installed interpreter, from outside the source checkout.

PYCAVI_SOURCE_ROOT points to the checkout for byte-for-byte resource comparison.
Only temporary workspaces and fake executable programs are created.
"""
import ast
import configparser
from contextlib import redirect_stdout
from importlib import metadata, resources
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pycavi
from pycavi.pycavi_setup import setup_pycavi
from pycavi import pycavi_setastro as astro


class InstalledPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="pycavi packaging ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def command(self, name, *args):
        return subprocess.run([str(Path(sys.executable).parent / name), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    def test_installed_code_and_exact_resources(self):
        source = Path(os.environ["PYCAVI_SOURCE_ROOT"]).resolve()
        self.assertNotIn(source, Path(pycavi.__file__).resolve().parents)
        self.assertNotIn(source, Path.cwd().resolve().parents)
        package = resources.files("pycavi")
        for group, pattern in (("notebooks", "*.ipynb"), ("config", "*"), ("data", "*")):
            originals = sorted(p for p in (source / "Pycavi2/pycavi" / group).glob(pattern) if p.is_file())
            self.assertTrue(originals)
            installed = sorted(p.name for p in package.joinpath(group).iterdir() if p.is_file())
            self.assertEqual(installed, [p.name for p in originals])
            for original in originals:
                self.assertEqual(package.joinpath(group, original.name).read_bytes(), original.read_bytes())
        dependencies = metadata.requires("pycavi")
        self.assertTrue(any(d.lower().startswith("ipython") for d in dependencies))
        self.assertTrue(any(d.lower().startswith("scikit-image") for d in dependencies))
        self.assertFalse(any(d.lower().startswith("pathlib") for d in dependencies))

    def test_reduction_notebook_resolves_mefpp_executable_and_resources(self):
        package = resources.files("pycavi")
        notebook = json.loads(package.joinpath("notebooks", "03_pycavi_run.ipynb").read_text())
        assignments = [node for cell in notebook["cells"] if cell["cell_type"] == "code"
                       for node in ast.walk(ast.parse("".join(cell["source"])))
                       if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "mefpp_dir"
                               for target in node.targets)]
        self.assertEqual(len(assignments), 1)
        prefix = self.root / "existing mefpp"
        for directory in ("bin", "config", "static_cal"):
            (prefix / directory).mkdir(parents=True)
        executable = prefix / "bin/mefpp"
        executable.write_text("Not executed by this path-resolution test")
        paf = prefix / "config/omegacam.paf"
        paf.write_text("Existing installed PAF fixture")
        bpm = prefix / "static_cal/OCAM_BPM_1x1.fits"
        bpm.write_bytes(b"Resource-location fixture, not a scientific FITS image")
        namespace = {"os": os, "executable_paths": {"mefpp": str(executable)}}
        exec(compile(ast.Module(body=assignments, type_ignores=[]), "<notebook path>", "exec"), namespace)
        self.assertEqual(Path(namespace["mefpp_dir"]), prefix)

        # Execute actual consumer expressions/functions without importing scientific
        # dependencies or launching mefpp. All resources and copies are disposable.
        tree = ast.parse(package.joinpath("pycavi", "pycavi_associate_reduction.py").read_text())
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        instrument = SimpleNamespace(config_dir=str(self.root / "absent project config"),
                                     mefpp_paf="omegacam.paf", bpm_prefix="OCAM_BPM")
        namespace.update(Path=Path, shutil=shutil, instrument=instrument)
        for function, target in (("mefpp_reduce_bias", "command_line"),
                                 ("mefpp_reduce_bpm", "bpm_file")):
            assignment = next(node for node in ast.walk(functions[function])
                              if isinstance(node, ast.Assign)
                              and any(isinstance(t, ast.Name) and t.id == target for t in node.targets))
            exec(compile(ast.Module(body=[assignment], type_ignores=[]), "<consumer path>", "exec"), namespace)
        self.assertTrue(namespace["command_line"].startswith("nohup " + str(executable) + " "))
        self.assertEqual(Path(namespace["bpm_file"]), bpm)
        exec(compile(ast.Module(body=[functions["copy_paf"]], type_ignores=[]), "<copy_paf>", "exec"), namespace)
        output = self.root / "temporary reduction directory"
        output.mkdir()
        with redirect_stdout(io.StringIO()):
            self.assertTrue(namespace["copy_paf"](namespace["mefpp_dir"], str(output), instrument))
        self.assertEqual((output / "mefpp.paf").read_bytes(), paf.read_bytes())

    def test_setup_preserves_edits_and_overwrite_is_explicit(self):
        workspace = self.root / "notebook workspace"
        result = self.command("pycavi_setup", workspace)
        self.assertEqual(result.returncode, 0, result.stderr)
        files = sorted(p for p in workspace.rglob("*") if p.is_file())
        self.assertEqual(len(files), 32)  # 15 notebooks + 12 config + 4 CSV + readme
        notebook = workspace / "03_pycavi_run.ipynb"
        config = workspace / "config/pycavi.cfg"
        data = next((workspace / "data").glob("*.csv"))
        for path in (notebook, config, data):
            path.write_text("User-edited content")
        result = self.command("pycavi_setup", workspace)
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in (notebook, config, data):
            self.assertEqual(path.read_text(), "User-edited content")
        result = self.command("pycavi_setup", workspace, "--overwrite")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(notebook.read_text(), "User-edited content")

    def test_setup_failure_returns_nonzero(self):
        occupied = self.root / "occupied"
        occupied.write_text("existing file")
        result = self.command("pycavi_setup", occupied)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("setup failed", result.stderr)
        self.assertEqual(occupied.read_text(), "existing file")

    def test_missing_resources_are_not_reported_as_success(self):
        destination = self.root / "missing resources"
        with patch("pycavi.pycavi_setup.resources.files", return_value=self.root):
            with self.assertRaises(FileNotFoundError):
                setup_pycavi(destination)
        self.assertFalse(destination.exists())

    def test_symlink_target_is_not_overwritten(self):
        workspace = self.root / "workspace"
        workspace.mkdir()
        outside = self.root / "outside"
        outside.write_text("Keep me")
        (workspace / "config").mkdir()
        (workspace / "config/pycavi.cfg").symlink_to(outside)
        result = self.command("pycavi_setup", workspace, "--overwrite")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outside.read_text(), "Keep me")

    def make_engines(self):
        directory = self.root / "fake engines"
        directory.mkdir()
        paths = {}
        for name in astro.EXECUTABLES:
            filename = "sex" if name == "sextractor" else name
            executable = directory / filename
            executable.write_text("#!/bin/sh\nprintf 'Astrometry.net fake version 1.0\\n'\n")
            executable.chmod(0o755)
            paths[name] = str(executable)
        return directory, paths

    def test_headless_explicit_paths_and_read_only_check(self):
        directory, paths = self.make_engines()
        config = self.root / "config with spaces.cfg"
        args = ["--config", config, "--non-interactive"]
        for name, path in paths.items():
            args.extend([f"--{name}", path])
        result = self.command("pycavi_setastro", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = config.read_text()
        parser = configparser.ConfigParser()
        parser.read(config)
        self.assertEqual(dict(parser["Paths"]), paths)
        result = self.command("pycavi_setastro", "--config", config, "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("fake version", result.stdout)
        self.assertEqual(config.read_text(), text)
        self.assertFalse(list(self.root.glob("*.bak*")))
        result = self.command("pycavi_setastro", "--config", config, "--non-interactive")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_text(), text)

    def test_path_discovery_sex_alias_and_config_backup(self):
        directory, paths = self.make_engines()
        config = self.root / "astro.cfg"
        with patch.dict(os.environ, {"PATH": str(directory)}), redirect_stdout(io.StringIO()):
            chosen = astro.find_and_choose_executables(config_file=config, non_interactive=True)
            self.assertEqual(chosen, paths)
            original = config.read_bytes()
            replacement = directory / "other sex"
            replacement.write_bytes(Path(paths["sextractor"]).read_bytes())
            replacement.chmod(0o755)
            astro.find_and_choose_executables(config_file=config, non_interactive=True,
                                             overrides={"sextractor": str(replacement)})
            self.assertEqual(config.with_name("astro.cfg.bak").read_bytes(), original)

    def test_bad_selection_leaves_configuration_unchanged(self):
        _, paths = self.make_engines()
        config = self.root / "astro.cfg"
        with redirect_stdout(io.StringIO()):
            astro.find_and_choose_executables(config_file=config, overrides=paths)
        original = config.read_bytes()
        result = self.command("pycavi_setastro", "--config", config, "--non-interactive",
                              "--swarp", self.root / "missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(config.read_bytes(), original)

    def test_check_missing_or_failing_engine_is_nonzero(self):
        _, paths = self.make_engines()
        config = self.root / "astro.cfg"
        with redirect_stdout(io.StringIO()):
            astro.find_and_choose_executables(config_file=config, overrides=paths)
        Path(paths["scamp"]).write_text("#!/bin/sh\nexit 3\n")
        result = self.command("pycavi_setastro", "--config", config, "--check")
        self.assertNotEqual(result.returncode, 0)
        Path(paths["scamp"]).unlink()
        result = self.command("pycavi_setastro", "--config", config, "--check")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
