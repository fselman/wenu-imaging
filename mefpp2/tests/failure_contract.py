"""Native failure/valid-split qualification using disposable, stdlib-only FITS.

Exercises mef_bb_load/new_from_paf, mef_engine and mef_split, not Pycavi or
calibration construction. Successful synthetic splitting is not science acceptance.
"""
import hashlib
from pathlib import Path
import resource
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import unittest

ENGINE = Path(sys.argv.pop(1)).resolve()
PAF = Path(sys.argv.pop(1)).resolve()


def card(key, value=None):
    text = key if value is None else f"{key:<8}= {value:>20}"
    return text.ljust(80).encode("ascii")


def header(cards):
    block = b"".join(cards + [card("END")])
    return block + b" " * (-len(block) % 2880)


def mosaic(path):
    primary = header([card("SIMPLE", "T"), card("BITPIX", "8"),
                      card("NAXIS", "0"), card("EXTEND", "T"),
                      card("OBJECT", "'synthetic'")])
    blocks = [primary]
    for name, values in (("CCD_A", (1, 2, 3, 4, 5, 6)),
                         ("CCD_B", (-1, -2, -3, -4, -5, -6))):
        blocks.append(header([
            card("XTENSION", "'IMAGE   '"), card("BITPIX", "16"),
            card("NAXIS", "2"), card("NAXIS1", "3"), card("NAXIS2", "2"),
            card("PCOUNT", "0"), card("GCOUNT", "1"), card("EXTNAME", repr(name)),
        ]))
        data = struct.pack(">6h", *values)
        blocks.append(data + b"\0" * (-len(data) % 2880))
    path.write_bytes(b"".join(blocks))


class FailureContract(unittest.TestCase):
    def setUp(self):
        # Preparation: fresh workspace and disabled core dumps for native cases.
        self.tmp = tempfile.TemporaryDirectory(prefix="mefpp-failure-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        self.original_engine = hashlib.sha256(ENGINE.read_bytes()).hexdigest()
        self.original_paf = hashlib.sha256(PAF.read_bytes()).hexdigest()

    def tearDown(self):
        # Preservation: native executable and source configuration stay unchanged.
        self.assertEqual(hashlib.sha256(ENGINE.read_bytes()).hexdigest(), self.original_engine)
        self.assertEqual(hashlib.sha256(PAF.read_bytes()).hexdigest(), self.original_paf)

    def paf(self, text=None):
        path = self.root / "mefpp.paf"
        path.write_text(PAF.read_text() if text is None else text)
        return path

    def run_native(self, *args, preexec_fn=None):
        return subprocess.run([str(ENGINE), *map(str, args)], cwd=self.root,
                              capture_output=True, timeout=10, preexec_fn=preexec_fn)

    def failed(self, result, diagnostic):
        # Error contract: controlled nonzero, relevant diagnostic, no crash.
        self.assertGreater(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(diagnostic.lower().encode(), (result.stdout + result.stderr).lower())

    def split_valid(self, absolute=False, explicit=False):
        self.paf()
        raw = self.root / "mosaic.fits"
        mosaic(raw)
        args = ["--split", str(raw) if absolute else raw.name]
        if explicit:
            external = self.root / "configuration with spaces"
            external.mkdir()
            chosen = external / "chosen.paf"
            shutil.move(self.root / "mefpp.paf", chosen)
            args += ["--pafname", str(chosen)]
        result = self.run_native(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.check_extension(1, "CCD_A", (1, 2, 3, 4, 5, 6))
        self.check_extension(2, "CCD_B", (-1, -2, -3, -4, -5, -6))
        self.assertFalse(list(self.root.glob("*.tmp.*")))
        return raw

    def check_extension(self, index, name, values):
        # Independent readback: raw FITS cards and big-endian pixels, no qfits oracle.
        data = (self.root / f"mosaic_{index:02d}.fits").read_bytes()
        self.assertEqual(len(data) % 2880, 0)
        cards = [data[i:i+80] for i in range(0, len(data), 80)]
        end = next(i for i, item in enumerate(cards) if item[:8].strip() == b"END")
        offset = ((end + 1) * 80 + 2879) // 2880 * 2880
        self.assertEqual(struct.unpack(">6h", data[offset:offset+12]), values)
        joined = b"".join(cards[:end])
        self.assertIn(name.encode(), joined)
        self.assertIn(b"synthetic", joined)
        self.assertEqual(data[offset+12:], b"\0" * (len(data)-offset-12))

    def test_information_without_paf(self):
        # CLI information: help/version/license succeed without configuration.
        for flag in ("--help", "--version", "--license"):
            with self.subTest(flag=flag):
                result = self.run_native(flag)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(list(self.root.glob("*.fits")))

    def test_missing_and_invalid_paf(self):
        # Configuration failures: no PAF and a malformed PAF fail before processing.
        self.failed(self.run_native("--split", "missing.list"), "PAF")
        self.paf("this is not a PAF\n")
        self.failed(self.run_native("--split", "missing.list"), "PAF")
        self.assertFalse(list(self.root.glob("*.fits")))

    def test_required_keys(self):
        # Partial construction: early/late missing keys and invalid numeric values.
        original = PAF.read_text()
        for key in ("MEF.NCHIPS", "MEF.CROP.Y.MAX.CHIP2", "MEF.SATMAX"):
            with self.subTest(key=key):
                self.paf("\n".join(line for line in original.splitlines()
                                   if not line.split() or line.split()[0] != key) + "\n")
                self.failed(self.run_native("--split", "missing.list"), key)
        for value in ("0", "-1", "junk", "nan", "1e999", "2147483648", "1.5"):
            with self.subTest(nchips=value):
                self.paf("\n".join(
                    f"MEF.NCHIPS {value};" if line.split() and line.split()[0] == "MEF.NCHIPS" else line
                    for line in original.splitlines()) + "\n")
                self.failed(self.run_native("--split", "missing.list"), "MEF.NCHIPS")

    def test_required_key_without_value(self):
        # PAF parser state: a value-less key must not reuse the preceding query value.
        original = PAF.read_text()
        text = "\n".join(
            "MEF.SATMAX " if line.split() and line.split()[0] == "MEF.SATMAX" else line
            for line in original.splitlines()
        ) + "\n"
        self.paf(text)
        self.failed(self.run_native("--split", "missing.list"), "MEF.SATMAX")

    def test_invalid_cli_and_satmax(self):
        # CLI failures: missing/unknown arguments and unchanged saturation limits.
        for args in (("--pafname",), ("--unknown",), ()):
            with self.subTest(args=args):
                result = self.run_native(*args)
                self.assertGreater(result.returncode, 0)
        self.paf()
        for value in ("2", "-1", "junk", "nan", "inf", "0.00001", "0.99999"):
            with self.subTest(satmax=value):
                self.failed(self.run_native("--satmax", value), "satmax")

    def test_missing_split_input(self):
        # Nested failure: an absent split input reaches the process exit status.
        self.paf()
        self.failed(self.run_native("--split", "missing.list"), "missing.list")
        self.assertFalse(list(self.root.glob("*.fits")))

    def test_valid_default_and_absolute_split(self):
        # Positive regression: default PAF, valid pixels/headers, absolute input path.
        self.split_valid(absolute=True)

    def test_explicit_paf(self):
        # PAF selection: explicit file with spaces works without a cwd PAF.
        self.split_valid(explicit=True)

    def test_partial_publish_failure(self):
        # Partial-output failure: retain completed extension and protect existing data.
        self.paf()
        mosaic(self.root / "mosaic.fits")
        blocker = self.root / "mosaic_02.fits"
        blocker.mkdir()
        (blocker / "sentinel").write_bytes(b"preserve")
        self.failed(self.run_native("--split", "mosaic.fits"), "publish")
        self.check_extension(1, "CCD_A", (1, 2, 3, 4, 5, 6))
        self.assertEqual((blocker / "sentinel").read_bytes(), b"preserve")
        self.assertFalse(list(self.root.glob("*.tmp.*")))

    def test_failed_write_cleanup(self):
        # I/O failure: constrain child file size, handle EFBIG without SIGXFSZ death.
        self.paf()
        mosaic(self.root / "mosaic.fits")
        def restrict_output():
            signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
            resource.setrlimit(resource.RLIMIT_FSIZE, (4096, 4096))
        self.failed(self.run_native("--split", "mosaic.fits", preexec_fn=restrict_output), "output")
        self.assertFalse(list(self.root.glob("mosaic_*.fits")))
        self.assertFalse(list(self.root.glob("*.tmp.*")))


if __name__ == "__main__":
    unittest.main()
