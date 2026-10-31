"""TOML/provenance controls using synthetic FITS only; no native engine calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import prepare_zwo_asi as prep
import test_zwo_bath_preparation as legacy
from astropy.io import fits

CONFIG = Path(__file__).resolve().parents[1] / "config/preparation/zwo_asi1600mm_bath.toml"
EVIDENCE = Path(tempfile.mkdtemp(prefix="zwo-asi-provenance-controls-"))


class AsiTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix=self._testMethodName + "-", dir=EVIDENCE))
        self.root = self.work / "raw"
        self.root.mkdir()
        self.config = self.work / "profile.toml"
        self.config.write_bytes(CONFIG.read_bytes())

    def frame(self, relative="Blue/M_51_Light_Blue_32_secs_001.fits", changes=None, extra=None):
        # Synthetic telescope signature mirrors the owner-returned 260-frame inventory.
        geometry = {"TELESCOP": "SynScan", "FOCALLEN": 1600.0, "APTDIA": 200.0,
                    "SCALE": 0.4899625, "PIXSIZE1": 3.8, "PIXSIZE2": 3.8,
                    "XPIXSZ": 3.8, "YPIXSZ": 3.8}
        geometry.update(changes or {})
        return legacy.PreparationTests.frame(self, relative, geometry, extra)

    def inventory(self):
        return prep.inventory(self.root, prep.load_profile(self.config))

    def plan(self):
        path = self.work / "plan.json"
        prep.write_json(path, self.inventory())
        return path, prep.sha(path.read_bytes())

    def test_all_roles_and_bands(self):
        # Role equivalence: retain all ten Bath role/filter groups from TOML.
        names = ["Bias/Bias_0.000032_secs_001.fits", "Darks/Dark_30_secs_001.fits"]
        for band, exposure in {"Blue": .035, "Green": .055, "Red": .1, "Luminance": .018}.items():
            names += [f"{band}/M_51_Light_{band}_32_secs_001.fits",
                      f"Flats/{band}/Light_{band}_{exposure:.3f}_secs_001.fits"]
        for name in names:
            self.frame(name)
        result = self.inventory()
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["entries"]), 10)
        self.assertEqual(sum("directory_flat_light_header_requires_acknowledgement" in r["warnings"]
                             for r in result["entries"]), 4)

    def test_copy_provenance_and_preservation(self):
        # Copy integrity: original cards, INSTRUME, unsigned pixels and payload survive.
        source = self.frame(changes={"CHECKSUM": "0000000000000000", "DATASUM": "0"})
        original = source.read_bytes()
        plan, digest = self.plan()
        output = self.work / "prepared"
        prep.apply_plan(plan, digest, output, False, self.config)
        product = output / source.relative_to(self.root)
        old_raw, old_end = prep.raw_header(source)
        new_raw, new_end = prep.raw_header(product)
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(product.read_bytes()[len(new_raw):], original[len(old_raw):])
        preserved = [old_raw[i:i+80] for i in range(0, old_end, 80)
                     if old_raw[i:i+8] not in (b"CHECKSUM", b"DATASUM ")]
        self.assertEqual(new_raw[:80*len(preserved)], b"".join(preserved))
        hdr = fits.getheader(product)
        for k, v in prep.load_profile(self.config)["settings"]["provenance"].items():
            self.assertEqual(hdr[k], v)
            self.assertEqual(hdr.count(k), 1)
        self.assertEqual(hdr["INSTRUME"], "ZWO CCD ASI1600MM Pro")
        self.assertEqual(hdr["TELESCOP"], "SynScan")
        self.assertEqual(hdr["WENU PROV TELESCOPE"], "BPO StellaLyra RC 8-inch 2020-01-01")
        self.assertNotIn("CHECKSUM", hdr)
        self.assertNotIn("DATASUM", hdr)
        with fits.open(product, memmap=False) as hdus:
            self.assertEqual(hdus[0].section[0, :3].tolist(), [0, 32767, 65535])
        manifest = json.loads((output / "preparation-manifest.json").read_text())
        self.assertEqual(manifest["plan"]["profile"]["sha256"], prep.sha(self.config.read_bytes()))
        self.assertEqual(manifest["products"][0]["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertTrue((output / "PREPARATION_COMPLETE").is_file())

    def test_provenance_conflicts_duplicates_and_consistent_values(self):
        # Conflict policy: no silent overwrite or duplicate provenance/camera identity.
        for changes, extra in [({"OBSERVAT": "Elsewhere"}, []),
                               ({"INSTRUME": "Another camera"}, []),
                               ({}, [("OBSERVAT", "Bath Physics Observatory")]*2),
                               ({}, [("HIERARCH WENU PROV PAPER DOI", "wrong")])]:
            path = self.frame(changes=changes, extra=extra)
            self.assertTrue(self.inventory()["errors"])
            path.unlink()
        source = self.frame(changes={"OBSERVAT": "Bath Physics Observatory"})
        plan, digest = self.plan()
        output = self.work / "prepared"
        prep.apply_plan(plan, digest, output, False, self.config)
        self.assertEqual(fits.getheader(output/source.relative_to(self.root)).count("OBSERVAT"), 1)

    def test_config_and_source_staleness(self):
        # Plan binding: even a configuration comment change blocks old-plan application.
        self.frame()
        plan, digest = self.plan()
        self.config.write_text(self.config.read_text() + "# changed\n")
        output = self.work / "prepared"
        with self.assertRaises(ValueError):
            prep.apply_plan(plan, digest, output, False, self.config)
        self.assertFalse(output.exists())
        self.config.write_bytes(CONFIG.read_bytes())
        with mock.patch.object(prep, "copy_prepared", side_effect=OSError("injected")):
            with self.assertRaises(OSError):
                prep.apply_plan(plan, digest, output, False, self.config)
        self.assertTrue((output / "PREPARATION_INCOMPLETE").exists())
        self.assertFalse((output / "PREPARATION_COMPLETE").exists())

    def test_flat_acknowledgement_and_aliases(self):
        # Flat role ambiguity still requires explicit acknowledgement; aliases stay blocked.
        self.frame("Flats/Blue/Light_Blue_0.035_secs_001.fits")
        plan, digest = self.plan()
        output = self.work / "prepared"
        with self.assertRaises(ValueError):
            prep.apply_plan(plan, digest, output, False, self.config)
        self.assertFalse(output.exists())
        prep.apply_plan(plan, digest, output, True, self.config)
        product = output/"Flats/Blue/Light_Blue_0.035_secs_001.fits"
        self.assertEqual(fits.getheader(product)["IMAGETYP"], "Light Frame")
        self.frame(extra=[("HIERARCH ESO.DPR.TYPE", "OBJECT")])
        self.assertTrue(self.inventory()["errors"])

    def test_configuration_restrictions(self):
        # Safe configuration: reject unknown/injected pixel keys and malformed policies.
        text = self.config.read_text()
        variants = [text.replace('OBSERVAT =', 'BITPIX ='),
                    text.replace('NAXIS1 = 4656', 'NAXIS1 = -1'),
                    text.replace('GAIN = 139.0', 'GAIN = nan'),
                    text.replace('monochrome = true', 'monochrome = false'),
                    text.replace('directory = "Bias"', 'directory = "../Bias"'),
                    text.replace('schema_version = 1', 'schema_version = 2'),
                    text.replace('type = "BIAS"', 'type = "UNKNOWN"'),
                    text.replace('OFFSET = 10.0', 'OFFSET = 10.0\nTYPO = 1'),
                    text[:text.index('[reference]')].replace('schema_version = 1',
                        'schema_version = 1\nreference = []') + text[text.index('[[rules]]'):]]
        for variant in variants:
            self.config.write_text(variant)
            with self.assertRaises(ValueError):
                prep.load_profile(self.config)

    def test_other_camera_policy_and_shape(self):
        # Generic policy: different camera identity, geometry, path and exposure come from TOML.
        path = self.frame()
        raw, _ = prep.raw_header(path)
        hdr = fits.Header.fromstring(raw.decode("ascii"), sep="")
        hdr["INSTRUME"] = "ZWO CCD ASI-test"
        hdr["NAXIS1"], hdr["NAXIS2"], hdr["EXPTIME"] = 3, 2, 12.0
        other = self.root / "Science/Star_12_secs_001.fits"
        other.parent.mkdir()
        other.write_bytes(hdr.tostring().encode("ascii") + b"\0" * 2880)
        path.unlink()
        text = self.config.read_text().replace("ZWO ASI1600MM Pro", "ZWO ASI-test")
        text = text.replace("ZWO CCD ASI1600MM Pro", "ZWO CCD ASI-test")
        text = text.replace("NAXIS1 = 4656", "NAXIS1 = 3").replace("NAXIS2 = 3520", "NAXIS2 = 2")
        text = text.replace('directory = "Blue"', 'directory = "Science"')
        text = text.replace('filename_prefix = "M_51_Light_Blue"', 'filename_prefix = "Star"')
        text = text.replace('exposure_s = 32.0', 'exposure_s = 12.0')
        self.config.write_text(text)
        self.assertEqual(self.inventory()["errors"], [])
        self.assertEqual(len(self.inventory()["entries"]), 1)

    def test_unknown_inputs_and_source_changes(self):
        # Source controls: linked/unknown inputs and changed header identity are refused.
        source = self.frame()
        plan, digest = self.plan()
        with source.open("r+b") as stream:
            stream.seek(100)
            stream.write(b"X")
        with self.assertRaises(ValueError):
            prep.apply_plan(plan, digest, self.work/"prepared", False, self.config)
        source.unlink()
        source = self.frame()
        (self.root/"linked.fits").symlink_to(source)
        (self.root/"unknown.fits").write_bytes(b"not a fits")
        self.assertEqual(len(self.inventory()["errors"]), 2)

    def test_dated_telescope_names(self):
        # Dated identity: each original DATE-OBS supplies its own calendar date.
        first = self.frame(changes={"DATE-OBS": "2022-01-08T22:04:06.108"})
        second = self.frame("Blue/M_51_Light_Blue_32_secs_002.fits",
                            changes={"DATE-OBS": "2022-02-06T19:06:04.613"})
        plan, digest = self.plan()
        output = self.work / "prepared"
        prep.apply_plan(plan, digest, output, False, self.config)
        for source, day in [(first, "2022-01-08"), (second, "2022-02-06")]:
            hdr = fits.getheader(output / source.relative_to(self.root))
            self.assertEqual(hdr["WENU PROV TELESCOPE"], "BPO StellaLyra RC 8-inch " + day)
            self.assertEqual(hdr["TELESCOP"], "SynScan")
            self.assertEqual(hdr["DATE-OBS"], fits.getheader(source)["DATE-OBS"])

    def test_telescope_signature_date_and_conflict_controls(self):
        # Identification refusal: geometry/date errors and duplicate/conflicting identity block copies.
        cases = [({"FOCALLEN": 910.0}, []), ({"APTDIA": 130.0}, []),
                 ({"SCALE": 0.86}, []), ({"TELESCOP": "Other"}, []),
                 ({"DATE-OBS": None}, []), ({"DATE-OBS": "2022-02-30T12:00:00"}, []),
                 ({"DATE-OBS": "20220108"}, []),
                 ({}, [("DATE-OBS", "2020-01-01T01:02:03")]),
                 ({}, [("HIERARCH WENU PROV TELESCOPE", "Another telescope")])]
        for changes, extra in cases:
            source = self.frame(changes=changes, extra=extra)
            self.assertTrue(self.inventory()["errors"], (changes, extra))
            source.unlink()

    def test_cli_plan_apply_and_destination_guards(self):
        # CLI integration: actual plan/apply calls and report/input separation use fresh outputs.
        self.frame()
        helper = Path(prep.__file__)
        plan = self.work/"cli-plan.json"
        args = [sys.executable, str(helper)]
        subprocess.run(args + ["plan", "--config", str(self.config), "--root", str(self.root),
                              "--report", str(plan)], check=True)
        output = self.work/"prepared"
        subprocess.run(args + ["apply", "--config", str(self.config), "--plan", str(plan),
                              "--expected-plan-sha256", prep.sha(plan.read_bytes()),
                              "--output", str(output)], check=True)
        self.assertTrue((output/"PREPARATION_COMPLETE").is_file())
        self.assertEqual(prep.main(["plan", "--config", str(self.config), "--root", str(self.root),
                                   "--report", str(self.root/"bad.json")]), 2)


if __name__ == "__main__":
    # Evidence: keep every synthetic fixture/output for review.
    print("RETAINED EVIDENCE:", EVIDENCE, flush=True)
    unittest.main(verbosity=2)
