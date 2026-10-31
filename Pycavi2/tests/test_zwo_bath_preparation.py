"""Synthetic #184 helper controls; no observational inputs/native programs."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import sys
import unittest
from unittest import mock

from astropy.io import fits

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

SPEC = importlib.util.spec_from_file_location(
    "prepare_zwo_bath", Path(__file__).resolve().parents[1] / "tools/prepare_zwo_bath.py")
prep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prep)
EVIDENCE = Path(tempfile.mkdtemp(prefix="zwo-bath-preparation-controls-"))


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix=self._testMethodName + "-", dir=EVIDENCE))
        self.root = self.work / "raw"
        self.root.mkdir()

    def frame(self, relative="Blue/M_51_Light_Blue_32_secs_001.fits", changes=None,
              extra=None):
        # Fixtures: sparse full-shape payloads match the real helper's strict profile.
        path = self.root / relative
        kind, _, band, exposure = prep.role_for(Path(relative))
        frame = {"BIAS": "Bias", "DARK": "Dark"}.get(kind, "Light")
        values = {"SIMPLE": True, "BITPIX": 16, "NAXIS": 2, "NAXIS1": 4656,
                  "NAXIS2": 3520, "BSCALE": 1, "BZERO": 32768,
                  "INSTRUME": prep.CAMERA, "XBINNING": 1, "YBINNING": 1,
                  "GAIN": 139.0, "OFFSET": 10.0, "CCD-TEMP": -5.0,
                  "EXPTIME": exposure, "FILTER": band or "Ha", "FRAME": frame,
                  "IMAGETYP": frame + " Frame", "DATE-OBS": "2020-01-01T01:02:03",
                  "OBJECT": "M 51"}
        values.update(changes or {})
        header = fits.Header()
        for key, value in values.items():
            if value is not None:
                header[key] = value
        for key, value in extra or []:
            header.append((key, value))
        raw = header.tostring().encode("ascii")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
            stream.write(struct.pack(">hhh", -32768, -1, 32767))
            stream.truncate(len(raw) + ((4656 * 3520 * 2 + 2879) // 2880) * 2880)
        return path

    def plan(self):
        plan = prep.inventory(self.root)
        path = self.work / "plan.json"
        prep.write_json(path, plan)
        return path, prep.sha(path.read_bytes())

    def test_directory_roles_and_no_source_writes(self):
        # Role/metadata checks: all four roles and four bands, including mislabelled flats.
        names = ["Bias/Bias_0.000032_secs_001.fits", "Darks/Dark_30_secs_001.fits"]
        for band, exposure in prep.FILTERS.items():
            names += [f"{band}/M_51_Light_{band}_32_secs_001.fits",
                      f"Flats/{band}/Light_{band}_{exposure:.3f}_secs_001.fits"]
        paths = [self.frame(name) for name in names]
        before = [prep.stamp(p) for p in paths]
        plan = prep.inventory(self.root)
        self.assertEqual(plan["errors"], [])
        self.assertEqual(len(plan["entries"]), 10)
        self.assertEqual(before, [prep.stamp(p) for p in paths])
        counts = prep.collections.Counter(r["classification"][prep.DPR[0]] for r in plan["entries"])
        self.assertEqual(counts, {"BIAS": 1, "DARK": 1, "OBJECT": 4, "FLAT": 4})

    def test_copy_payload_cards_scaling_and_checksum_policy(self):
        # Copy equivalence: verify exact opaque bytes, original nonchecksum cards and scaling.
        path = self.frame(changes={"CHECKSUM": "0000000000000000", "DATASUM": "0"})
        original = path.read_bytes()
        plan_path, digest = self.plan()
        output = self.work / "prepared"
        prep.apply_plan(plan_path, digest, output, False)
        product = output / path.relative_to(self.root)
        self.assertEqual(path.read_bytes(), original)
        src_header, _ = prep.raw_header(path)
        dst_header, _ = prep.raw_header(product)
        self.assertEqual(original[len(src_header):], product.read_bytes()[len(dst_header):])
        old = fits.Header.fromstring(src_header.decode("ascii"), sep="")
        new = fits.Header.fromstring(dst_header.decode("ascii"), sep="")
        for card in old.cards:
            if card.keyword not in ("CHECKSUM", "DATASUM"):
                self.assertEqual(card.image, new.cards[card.keyword].image)
        self.assertNotIn("CHECKSUM", new)
        self.assertNotIn("DATASUM", new)
        with fits.open(product, memmap=False) as hdus:
            self.assertEqual(hdus[0].section[0, :3].tolist(), [0, 32767, 65535])
        manifest = json.loads((output / "preparation-manifest.json").read_text())
        self.assertEqual(manifest["products"][0]["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertTrue((output / "PREPARATION_COMPLETE").exists())
        self.assertFalse((output / "PREPARATION_INCOMPLETE").exists())
        with self.assertRaises(ValueError):
            prep.apply_plan(plan_path, digest, output, False)

    def test_flat_acknowledgement_and_existing_classification(self):
        # Classification safeguards: conflict acknowledgement does not rewrite IMAGETYP.
        path = self.frame("Flats/Blue/Light_Blue_0.035_secs_001.fits",
                          extra=[("HIERARCH ESO DPR TYPE", "FLAT")])
        plan, digest = self.plan()
        out = self.work / "prepared"
        with self.assertRaises(ValueError):
            prep.apply_plan(plan, digest, out, False)
        self.assertFalse(out.exists())
        prep.apply_plan(plan, digest, out, True)
        hdr = fits.getheader(out / path.relative_to(self.root))
        self.assertEqual(hdr["IMAGETYP"], "Light Frame")
        self.assertEqual(hdr.count("ESO DPR TYPE"), 1)
        self.assertEqual(hdr["ESO DPR TYPE"], "FLAT")

    def test_conflicting_duplicate_and_alias_cards(self):
        # Bad classification controls: no conflicting, duplicate or competing alias survives.
        path = self.frame(extra=[("HIERARCH ESO DPR TYPE", "DARK")])
        self.assertTrue(prep.inventory(self.root)["errors"])
        path.unlink()
        path = self.frame(extra=[("HIERARCH ESO DPR TYPE", "OBJECT"),
                                 ("HIERARCH ESO DPR TYPE", "OBJECT")])
        self.assertTrue(prep.inventory(self.root)["errors"])
        path.unlink()
        self.frame(extra=[("DPR.TYPE", "OBJECT")])
        self.assertTrue(prep.inventory(self.root)["errors"])

    def test_metadata_misclassification_controls(self):
        # Light checks: camera, geometry, gain, band, exposure, frame and mono evidence.
        changes = [{"INSTRUME": "different"}, {"NAXIS1": 8}, {"GAIN": None},
                   {"FILTER": "Red"}, {"EXPTIME": 30}, {"FRAME": "Dark"},
                   {"BAYERPAT": "RGGB"}, {"CCD-TEMP": float("inf")}]
        # FITS cannot serialize infinity as a header value; test missing temperature instead.
        changes[-1] = {"CCD-TEMP": None}
        for change in changes:
            with self.subTest(change=change):
                path = self.frame(changes=change)
                self.assertTrue(prep.inventory(self.root)["errors"])
                path.unlink()

    def test_stale_or_changed_plan_refuses_output(self):
        # Reviewed-plan binding: changed JSON hash or source stat invalidates preparation.
        path = self.frame()
        plan, digest = self.plan()
        out = self.work / "prepared"
        with self.assertRaises(ValueError):
            prep.apply_plan(plan, "0" * 64, out, False)
        with path.open("ab") as stream:
            stream.write(b" ")
        with self.assertRaises(ValueError):
            prep.apply_plan(plan, digest, out, False)
        self.assertFalse(out.exists())

    def test_unknown_symlink_and_extra_hdu_inputs_block_all(self):
        # Admission controls: unknown paths, links and excess payload cannot be skipped silently.
        path = self.frame()
        (self.root / "alias.fits").symlink_to(path)
        unknown = self.root / "Unknown"
        unknown.mkdir()
        (unknown / "frame.fits").write_bytes(b"bad")
        (self.root / "compressed.fits.gz").write_bytes(b"unsupported")
        with path.open("ab") as stream:
            stream.write(b" " * 2880)
        plan, digest = self.plan()
        self.assertEqual(len(json.loads(plan.read_text())["errors"]), 4)
        out = self.work / "prepared"
        with self.assertRaises(ValueError):
            prep.apply_plan(plan, digest, out, False)
        self.assertFalse(out.exists())

    def test_boundary_growth_and_incomplete_failure_marker(self):
        # Header growth/failure: padding boundary is safe; failed copies remain visibly incomplete.
        path = self.frame(extra=[("COMMENT", str(i)) for i in range(16)])
        plan, digest = self.plan()
        out = self.work / "prepared"
        prep.apply_plan(plan, digest, out, False)
        product = out / path.relative_to(self.root)
        self.assertGreater(len(prep.raw_header(product)[0]), len(prep.raw_header(path)[0]))
        failed = self.work / "failed"
        with mock.patch.object(prep, "copy_prepared", side_effect=OSError("synthetic I/O failure")):
            with self.assertRaises(OSError):
                prep.apply_plan(plan, digest, failed, False)
        self.assertTrue((failed / "PREPARATION_INCOMPLETE").exists())
        self.assertFalse((failed / "PREPARATION_COMPLETE").exists())

    def test_output_and_report_source_protection(self):
        # Destination safety: never place a report or prepared tree inside original inputs.
        self.frame()
        self.assertEqual(prep.main(["plan", "--root", str(self.root),
                                   "--report", str(self.root / "report.json")]), 2)
        plan, digest = self.plan()
        with self.assertRaises(ValueError):
            prep.apply_plan(plan, digest, self.root / "prepared", False)
        self.assertFalse((self.root / "prepared").exists())


if __name__ == "__main__":
    print("RETAINED SYNTHETIC EVIDENCE:", EVIDENCE, flush=True)
    unittest.main(verbosity=2)
