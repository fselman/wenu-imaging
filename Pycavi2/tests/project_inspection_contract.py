"""Focused metadata-only M3 controls; generated fixtures remain under work-parent."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

import astropy
from astropy.io import fits
from astropy.io.fits.hdu.image import _ImageBaseHDU
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / "Pycavi2/pycavi"
sys.path.insert(0, str(MODULES))
from pycavi_paths import PathResolver, PathResolutionError
from pycavi_project import inspect_project, Limits, main

WORK = None


def inventory(root):
    result = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(base) / name
            info = path.lstat()
            result[str(path.relative_to(root))] = dict(
                mode=info.st_mode, mtime=info.st_mtime_ns,
                content=os.readlink(path) if path.is_symlink() else
                hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
    return result


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix=self._testMethodName + "-", dir=WORK))
        self.root = self.work / "project with spaces"
        self.root.mkdir()
        self.raw = self.work / "raw with spaces"
        self.raw.mkdir()
        self.caller_a = self.work / "caller a"
        self.caller_b = self.work / "caller b"
        self.caller_a.mkdir(); self.caller_b.mkdir()
        self.original_cwd = Path.cwd()

    def tearDown(self):
        self.assertEqual(Path.cwd(), self.original_cwd)

    def image(self, path, *, instrument="WFI", target="field", exposure=10., filter_name="r"):
        path.parent.mkdir(parents=True, exist_ok=True)
        header = fits.Header()
        header["INSTRUME"] = instrument
        header["OBJECT"] = target
        header["EXPTIME"] = exposure
        header["FILTER"] = filter_name
        header["HIERARCH ESO INS FILT1 NAME"] = filter_name
        header["DATE-OBS"] = "2026-10-30T00:00:00"
        hdus = fits.HDUList([fits.PrimaryHDU(header=header),
                             fits.ImageHDU(np.arange(6, dtype=np.int16).reshape(2, 3), name="CCD_A"),
                             fits.ImageHDU(np.zeros((1, 2), dtype=np.int16), name="CCD_B")])
        hdus.writeto(path)
        return path

    def listed(self, name="science.list", content="frame.fits\n"):
        path = self.root / "nested partition" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(content)
        return path

    def inspect(self, **kwargs):
        return inspect_project(self.root, invocation_base=self.caller_a, recursive=True, **kwargs)

    def codes(self, report):
        return [item["code"] for item in report["diagnostics"]]

    def cli(self, caller, *extra, valid=True):
        argv = [sys.executable, "-B", str(MODULES / "pycavi_project.py"), "project", "inspect",
                str(self.root), "--recursive", "--format", "json", *map(str, extra)]
        result = subprocess.run(argv, cwd=caller, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if valid else 1, result.stderr)
        return json.loads(result.stdout) if valid else result

    # Explicit argument/reference bases: no fallback to a library caller's cwd.
    def test_path_bases(self):
        resolver = PathResolver(self.caller_a)
        self.assertEqual(resolver.argument("../raw with spaces"), self.raw)
        self.assertEqual(resolver.reference("frame.fits", base=self.raw), self.raw / "frame.fits")
        with self.assertRaises(PathResolutionError):
            resolver.reference("frame.fits")
        with self.assertRaises(PathResolutionError):
            PathResolver(Path("relative"))

    # Full ordered membership and shared references retain one canonical asset.
    def test_nested_shared_membership_and_headers(self):
        image = self.image(self.raw / "frame.fits")
        self.listed(content="frame.fits\nframe.fits\n")
        other = self.root / "calibration"; other.mkdir()
        (other / "bias.list").write_text("frame.fits\n")
        (self.root / "linked_master.fits").symlink_to(image)
        (self.root / "toreduce_science").touch()
        (self.root / "mefpp.log").write_text("success-looking text is not a validated result")
        report = self.inspect(list_base=self.raw, columns=("DATE-OBS",))
        self.assertTrue(report["coverage"]["complete"], report["diagnostics"])
        self.assertEqual(len(report["assets"]), 1)
        self.assertEqual(len(report["partitions"]), 2)
        science = next(p for p in report["partitions"] if p["stage"] == "science")
        self.assertEqual([m["line"] for m in science["members"]], [1, 2])
        self.assertEqual(report["assets"][0]["hdus"][1]["dimensions"], [3, 2])
        self.assertEqual(report["assets"][0]["hdus"][1]["fields"]["target"], "field")
        self.assertEqual(report["assets"][0]["hdus"][1]["fields_source_hdu"], 0)
        self.assertEqual(len(report["attempt_evidence"]), 2)
        self.assertTrue(all(e["completion"] == "unknown" for e in report["attempt_evidence"]))
        self.assertTrue(all(a["status"] == "existing-unverified" for a in report["assets"]))
        self.assertFalse(report["execution_ready"])

    def test_unknown_base_and_missing_absolute_member(self):
        self.listed(content="frame.fits\n" + str(self.raw / "missing.fits") + "\n")
        report = self.inspect()
        self.assertIn("unknown_list_base", self.codes(report))
        self.assertIn("reference_error", self.codes(report))
        self.assertFalse(report["coverage"]["complete"])
        self.assertIsNone(report["partitions"][0]["members"][0]["path"])
        self.assertEqual(report["assets"][0]["status"], "unavailable")

    def test_list_legacy_first_column_and_invalid_lines(self):
        self.image(self.raw / "frame.fits")
        self.listed(content="#comment\n\nframe.fits extra\nframe.fits\r\n" + "x" * 1023 + "\n")
        report = self.inspect(list_base=self.raw)
        self.assertEqual(len(report["partitions"][0]["members"]), 1)
        self.assertIn("list_extra_columns", self.codes(report))
        self.assertEqual(self.codes(report).count("unsupported_list_line"), 2)
        self.assertEqual(report["partitions"][0]["members"][0]["columns"], ["frame.fits", "extra"])

    def test_malformed_text_and_nonregular_inputs(self):
        path = self.listed(content="\0")
        report = self.inspect()
        self.assertIn("list_error", self.codes(report))
        path.unlink(); os.mkfifo(path)
        report = self.inspect()
        self.assertIn("list_error", self.codes(report))

    def test_no_recursive_scan_and_limits(self):
        self.listed()
        report = inspect_project(self.root, invocation_base=self.caller_a)
        self.assertIn("not_recursive", self.codes(report))
        for limits, codes in ((Limits(directories=1), {"directory_limit"}),
                              (Limits(depth=1), {"directory_limit"}),
                              (Limits(files=1), {"entry_limit"}),
                              (Limits(list_lines=1), {"list_limit", "membership_limit"}),
                              (Limits(text_bytes=1), {"list_error"})):
            with self.subTest(limits=limits):
                deeper = self.root / "nested partition" / "deeper"; deeper.mkdir(exist_ok=True)
                (deeper / "science.list").write_text("a\nb\n")
                report = self.inspect(limits=limits)
                self.assertFalse(report["coverage"]["complete"])
                self.assertTrue(codes.intersection(self.codes(report)), report["diagnostics"])
        with self.assertRaises(ValueError):
            Limits(files=0)

    def test_links_dangling_cycles_directories(self):
        (self.root / "missing.fits").symlink_to(self.raw / "absent.fits")
        (self.root / "cycle-a").symlink_to("cycle-b")
        (self.root / "cycle-b").symlink_to("cycle-a")
        (self.root / "loop-dir").symlink_to(self.root, target_is_directory=True)
        report = self.inspect()
        self.assertEqual(len(report["links"]), 4)
        self.assertIn("reference_error", self.codes(report))
        self.assertIn("link_error", self.codes(report))
        self.assertIn("directory_link_not_followed", self.codes(report))
        self.assertFalse(report["coverage"]["complete"])

    def test_duplicate_basenames_are_not_merged(self):
        first = self.image(self.raw / "first" / "same.fits", target="one")
        second = self.image(self.raw / "second" / "same.fits", target="two")
        self.listed(content="first/same.fits\nsecond/same.fits\n")
        report = self.inspect(list_base=self.raw)
        self.assertEqual(len(report["assets"]), 2)
        self.assertEqual([a["hdus"][0]["fields"]["target"] for a in report["assets"]], ["one", "two"])

    def test_actual_instrument_mappings_and_cfg_authority(self):
        self.image(self.raw / "frame.fits")
        self.listed()
        config = self.work / "pycavi.cfg"
        config.write_text("[Provenance]\ninstrument=WFI\n[Directories]\nraw_data_dir=relative\n")
        for instrument in ("wfi", "omegacam"):
            report = self.inspect(list_base=self.raw, project_config=config,
                                  instrument_config=ROOT / "Pycavi2/pycavi/config" / (instrument + ".cfg"))
            self.assertEqual(report["configurations"][1]["authority"], "explicitly-selected")
            self.assertEqual(report["configurations"][0]["sections"]["Directories"]["raw_data_dir"]["raw"], "relative")
            self.assertEqual(report["configurations"][0]["sections"]["Directories"]["raw_data_dir"]["resolved"], str(self.raw / "relative"))
        report = self.inspect(project_config=config)
        self.assertIn("unknown_cfg_base", self.codes(report))
        config.write_text("[broken")
        self.assertIn("configuration_error", self.codes(self.inspect(project_config=config)))

    # Trap pixel loading and prove byte/mode/mtime preservation of read-only roots.
    def test_no_arrays_no_writes_and_caller_independence(self):
        path = self.image(self.raw / "frame.fits")
        with fits.open(path, mode="append") as hdus:
            hdus.append(fits.BinTableHDU.from_columns([
                fits.Column(name="VALUE", format="J", array=np.arange(3))]))
        self.listed(); path.chmod(0o444)
        self.raw.chmod(0o555)
        before = inventory(self.work)
        with patch.object(_ImageBaseHDU, "_get_scaled_image_data", side_effect=AssertionError("pixel read")), \
                patch.object(fits.BinTableHDU, "_get_tbdata", side_effect=AssertionError("table read")):
            report = self.inspect(list_base=self.raw)
        self.assertTrue(report["coverage"]["complete"], report["diagnostics"])
        self.assertEqual(len(report["assets"][0]["hdus"]), 4)
        self.assertEqual(before, inventory(self.work))
        report["assets"][0]["hdus"][0]["fields"]["target"] = "caller mutation"
        self.assertEqual(self.inspect(list_base=self.raw)["assets"][0]["hdus"][0]["fields"]["target"], "field")

    def test_fits_errors_duplicate_cards_and_header_conflicts(self):
        (self.root / "broken.fits").write_text("not FITS")
        (self.root / "compressed.fits.gz").write_bytes(b"unsupported fixture")
        (self.root / "undeclared.list").write_text("not a known partition role")
        self.assertIn("fits_error", self.codes(self.inspect()))
        path = self.image(self.root / "valid.fits")
        with fits.open(path, mode="update") as hdus:
            hdus[0].header.append(("OBJECT", "different", "duplicate"))
            hdus[1].header["EXPTIME"] = 99.
        report = self.inspect()
        self.assertIn("duplicate_header_key", self.codes(report))
        self.assertIn("unsupported_reference", self.codes(report))
        self.assertIn("unknown_list_role", self.codes(report))
        self.assertIn("primary_extension_conflict", self.codes(report))
        asset = next(a for a in report["assets"] if a["path"] == str(path))
        self.assertIsNone(asset["hdus"][0]["fields"]["target"])
        self.assertEqual(asset["hdus"][1]["local_fields"]["exposure"], 99.)

    def test_header_and_hdu_budgets(self):
        self.image(self.root / "multi.fits")
        self.assertIn("hdu_limit", self.codes(self.inspect(limits=Limits(hdus=1))))
        self.assertIn("fits_error", self.codes(self.inspect(limits=Limits(header_bytes=10))))

    # Actual CLI JSON and views must agree across unrelated caller directories.
    def test_cli_library_equality_and_views(self):
        self.image(self.raw / "frame.fits")
        self.listed()
        before = inventory(self.root)
        a = self.cli(self.caller_a, "--list-base", self.raw, "--columns", "path", "extname", "EXPTIME")
        b = self.cli(self.caller_b, "--list-base", self.raw, "--columns", "path", "extname", "EXPTIME")
        self.assertEqual(a, b)
        # Resolve the real console entry target through the nested package too.
        target = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["scripts"]["pycavi"]
        self.assertEqual(target, "pycavi.pycavi_project:main")
        package = subprocess.run([
            sys.executable, "-B", "-m", target.split(":")[0], "project", "inspect",
            str(self.root), "--recursive", "--format", "json", "--list-base", str(self.raw),
            "--columns", "path", "extname", "EXPTIME"], cwd=self.caller_b,
            env=dict(os.environ, PYTHONPATH=str(ROOT / "Pycavi2")), capture_output=True, text=True)
        self.assertEqual(package.returncode, 0, package.stderr)
        self.assertEqual(json.loads(package.stdout), b)
        view = a.pop("view")
        expected = self.inspect(list_base=self.raw, columns=("path", "extname", "EXPTIME"))
        self.assertEqual(a, expected)
        self.assertEqual(view["rows"], expected["rows"])
        selected = self.cli(self.caller_a, "--list-base", self.raw,
                            "--columns", "extname", "target", "EXPTIME",
                            "--detector", "CCD_A", "--stage", "science", "--sort", "EXPTIME")
        self.assertEqual(len(selected["view"]["rows"]), 1)
        self.assertEqual(selected["view"]["rows"][0]["target"], "field")
        self.assertEqual(before, inventory(self.root))

    def test_cli_rejections_and_table(self):
        self.image(self.root / "frame\tname.fits")
        self.cli(self.caller_a, "--where", "unknown=x", valid=False)
        self.cli(self.caller_a, "--sort", "unknown", valid=False)
        # Table and JSON are stdout only; there is no output/project writer.
        result = subprocess.run([sys.executable, "-B", str(MODULES / "pycavi_project.py"),
                                 "project", "inspect", str(self.root), "--columns", "path", "status"], cwd=self.caller_b,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("existing-unverified", result.stdout)
        self.assertIn("completion: unverified", result.stdout)
        self.assertNotIn("frame\tname", result.stdout)
        self.assertIn("frame\\tname", result.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-parent", type=Path, required=True)
    args = parser.parse_args()
    WORK = Path(tempfile.mkdtemp(prefix="m3 project inspection ", dir=args.work_parent))
    print("WORK DIRECTORY:", WORK, flush=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(InspectionTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(python=sys.version, executable=sys.executable, astropy=astropy.__version__,
                  numpy=np.__version__, source_root=str(ROOT), tests=result.testsRun,
                  failures=[str(t) for t, _ in result.failures], errors=[str(t) for t, _ in result.errors],
                  successful=result.wasSuccessful())
    (WORK / "run-provenance.json").write_text(json.dumps(report, indent=2) + "\n")
    print("EVIDENCE:", WORK, flush=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)
