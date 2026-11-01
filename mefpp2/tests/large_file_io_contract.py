"""Approved IO roadmap fixtures/oracles: private sparse files, no observations."""
import argparse
import json
import shutil
import struct
import subprocess
import tempfile
import resource
import signal
import time
import sys
import hashlib
from pathlib import Path

BLOCK = 2880
SIDE = 4096
COUNT = 65
PLANE = SIDE * SIDE * 4
PADDED = (PLANE + BLOCK - 1) // BLOCK * BLOCK


def header(cards):
    body = b"".join(f"{k:8}= {v:>20}".ljust(80).encode("ascii") for k, v in cards)
    body += b"END".ljust(80)
    return body.ljust((len(body) + BLOCK - 1) // BLOCK * BLOCK, b" ")


def fixtures(root, large=False):
    reserve = 12 * 2**30 if large else 512 * 2**20
    assert shutil.disk_usage(root).free >= reserve, f"Need {reserve} bytes free for this phase"
    sparse_check = root / "sparse-check"
    with sparse_check.open("wb") as stream:
        stream.truncate(64 * 2**20)
    assert sparse_check.stat().st_blocks * 512 < 2**20, "Sparse filesystem required"
    sparse_check.unlink()
    mef = root / "large-mef.fits"
    positions = [(0, BLOCK, BLOCK, 0)]
    with mef.open("wb") as stream:
        stream.write(header([("SIMPLE", "T"), ("BITPIX", "8"), ("NAXIS", "0"), ("EXTEND", "T")]))
        for i in range(1, COUNT + 1):
            start = BLOCK + (i - 1) * (BLOCK + PADDED)
            stream.seek(start)
            stream.write(header([("XTENSION", "'IMAGE   '"), ("BITPIX", "-32"),
                ("NAXIS", "2"), ("NAXIS1", str(SIDE)), ("NAXIS2", str(SIDE)),
                ("PCOUNT", "0"), ("GCOUNT", "1"), ("BSCALE", "1"), ("BZERO", "0"),
                ("EXTNAME", f"'CCD{i:03}'"), ("EXTVER", str(i))]))
            data = start + BLOCK
            stream.seek(data); stream.write(struct.pack(">f", float(i)))
            stream.seek(data + PLANE - 4); stream.write(struct.pack(">f", float(i + 100)))
            positions.append((start, BLOCK, data, PADDED))
        stream.truncate(BLOCK + COUNT * (BLOCK + PADDED))
    cube = root / "large-cube.fits"
    cube_bytes = BLOCK + (COUNT * PLANE + BLOCK - 1) // BLOCK * BLOCK
    with cube.open("wb") as stream:
        stream.write(header([("SIMPLE", "T"), ("BITPIX", "-32"), ("NAXIS", "3"),
            ("NAXIS1", str(SIDE)), ("NAXIS2", str(SIDE)), ("NAXIS3", str(COUNT))]))
        stream.seek(BLOCK + (COUNT - 1) * PLANE)
        stream.write(struct.pack(">f", 73.0))
        stream.truncate(cube_bytes)
    for p in (mef, cube):
        p.chmod(0o444)
    return mef, cube, positions


def tiny_mef(path):
    with path.open("wb") as stream:
        stream.write(header([("SIMPLE", "T"), ("BITPIX", "8"), ("NAXIS", "0"), ("EXTEND", "T")]))
        for i in range(1, 3):
            stream.write(header([("XTENSION", "'IMAGE   '"), ("BITPIX", "-32"),
                ("NAXIS", "2"), ("NAXIS1", "6"), ("NAXIS2", "4"),
                ("PCOUNT", "0"), ("GCOUNT", "1"), ("BSCALE", "1"), ("BZERO", "0"),
                ("EXTNAME", f"'CCD{i:03}'"), ("EXTVER", str(i))]))
            values = [float(i)] + [0.0] * 22 + [float(i + 100)]
            stream.write(struct.pack(">24f", *values).ljust(BLOCK, b"\0"))
    path.chmod(0o444)


def validate_output(path, side_x, side_y, count):
    """One complete bounded-memory pixel pass; Astropy supplies independent HDU framing."""
    import numpy as np
    from astropy.io import fits
    plane_bytes = side_x * side_y * 4
    padded = (plane_bytes + BLOCK - 1) // BLOCK * BLOCK
    assert path.stat().st_size == BLOCK + count * (BLOCK + padded)
    checked = 0
    with fits.open(path, memmap=False, do_not_scale_image_data=True) as hdus, path.open("rb") as stream:
        assert len(hdus) == count + 1
        assert hdus[0].header["NAXIS"] == 0
        for i in range(1, count + 1):
            hdu = hdus[i]
            assert (hdu.header["BITPIX"], hdu.header["NAXIS1"], hdu.header["NAXIS2"]) == (-32, side_x, side_y)
            assert (hdu.header["EXTNAME"], hdu.header["EXTVER"], hdu.header["BSCALE"], hdu.header["BZERO"]) == (f"CCD{i:03}", i, 1, 0)
            expected_start = BLOCK + (i - 1) * (BLOCK + padded)
            assert hdu.fileinfo()["hdrLoc"] == expected_start
            assert hdu.fileinfo()["datLoc"] == expected_start + BLOCK
            stream.seek(expected_start + BLOCK)
            pixels = side_x * side_y
            for first in range(0, pixels, 2**20):
                n = min(2**20, pixels - first)
                actual = np.frombuffer(stream.read(n * 4), dtype=">f4")
                expected = np.full(n, -16.0, dtype=np.float32)
                if first == 0:
                    expected[0] = i - 16
                if first + n == pixels:
                    expected[-1] = i + 100 - 16
                assert np.array_equal(actual, expected), (i, first)
                checked += n
            assert stream.read(padded - plane_bytes) == b"\0" * (padded - plane_bytes)
    return checked


def write_limit():
    signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024, 1024))


def source_identity(path, spans):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for hs, hz, ds, dz in spans:
            stream.seek(hs); digest.update(stream.read(hz))
            if dz:
                stream.seek(ds); digest.update(stream.read(4))
                # Large MEF last sentinel is before padding; cube last is zero.
                last = ds + (PLANE if len(spans) > 1 else COUNT * PLANE) - 4
                stream.seek(last); digest.update(stream.read(4))
                if len(spans) == 1:
                    stream.seek(ds + (COUNT - 1) * PLANE); digest.update(stream.read(4))
    st = path.stat()
    return (st.st_size, st.st_mtime_ns, st.st_mode, digest.hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--work-parent", type=Path, required=True)
    parser.add_argument("--phase", choices=["discovery", "reads", "writes", "focused", "large"], default="focused")
    args = parser.parse_args()
    args.work_parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="large-file-io-", dir=args.work_parent))
    print("PLAN: two sparse ~4.063-GiB inputs; one <=4.063-GiB materialized output only in large phase; native planned <1 GiB RAM", flush=True)
    print("RETAINED RUN:", root, flush=True)
    mef, cube, positions = fixtures(root, large=args.phase == "large")
    records = []
    cube_spans = [(0, BLOCK, BLOCK, cube.stat().st_size - BLOCK)]
    before = {mef.name: source_identity(mef, positions), cube.name: source_identity(cube, cube_spans)}
    for path, spans in ((mef, positions), (cube, [(0, BLOCK, BLOCK, cube.stat().st_size - BLOCK)])):
        argv = [str(args.probe.resolve()), "discover", str(path)]
        r = subprocess.run(argv, text=True, capture_output=True, timeout=60)
        records.append({"argv": argv, "exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
        assert r.returncode == 0, records[-1]
        expected = [f"EXTENSIONS {len(spans)-1}"]
        for i, (hs, hz, ds, dz) in enumerate(spans):
            expected += [f"HEADER {i} {hs} {hz}", f"DATA {i} {ds} {dz}"]
        assert r.stdout.splitlines() == expected, records[-1]
    for kind, cards in (
        ("overflow", [("SIMPLE", "T"), ("BITPIX", "64"), ("NAXIS", "3"),
            ("NAXIS1", "2147483647"), ("NAXIS2", "2147483647"), ("NAXIS3", "2147483647")]),
        ("truncated", [("SIMPLE", "T"), ("BITPIX", "-32"), ("NAXIS", "2"), ("NAXIS1", "4"), ("NAXIS2", "4")]),
    ):
        bad = root / (kind + ".fits")
        bad.write_bytes(header(cards)); bad.chmod(0o444)
        r = subprocess.run([str(args.probe.resolve()), "discover", str(bad)], capture_output=True, text=True, timeout=30)
        assert r.returncode == 1, (kind, r.returncode, r.stderr)
    if args.phase in ("reads", "focused", "large"):
        for mode, path in (("read-mef", mef), ("read-cube", cube)):
            argv = [str(args.probe.resolve()), mode, str(path)]
            r = subprocess.run(argv, text=True, capture_output=True, timeout=180)
            records.append({"argv": argv, "exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
            assert r.returncode == 0, records[-1]
    checked_pixels = 0
    if args.phase in ("writes", "focused", "large"):
        for boundary in (2**31, 2**32):
            pad = root / f"padding-{boundary}.bin"
            with pad.open("wb") as stream:
                stream.truncate(boundary + 1)
            r = subprocess.run([str(args.probe.resolve()), "pad", str(pad)], capture_output=True, text=True, timeout=30)
            assert r.returncode == 0, r.stderr
            expected = (boundary + 1 + BLOCK - 1) // BLOCK * BLOCK
            assert pad.stat().st_size == expected
            with pad.open("rb") as stream:
                stream.seek(boundary + 1)
                assert stream.read() == b"\0" * (expected - boundary - 1)
        tiny = root / "tiny-mef.fits"
        tiny_mef(tiny)
        tiny_before = (tiny.stat().st_size, tiny.stat().st_mtime_ns, tiny.stat().st_mode)
        output = root / "tiny-processed.fits"
        r = subprocess.run([str(args.probe.resolve()), "process", str(tiny), str(output)], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, (r.returncode, r.stderr)
        checked_pixels += validate_output(output, 6, 4, 2)
        assert tiny_before == (tiny.stat().st_size, tiny.stat().st_mtime_ns, tiny.stat().st_mode)
        r = subprocess.run([str(args.probe.resolve()), "write-failure", str(root / "short-write.bin")],
            capture_output=True, text=True, timeout=30, preexec_fn=write_limit)
        assert r.returncode == 0, (r.returncode, r.stderr)
        records.append({"control": "private RLIMIT_FSIZE short-write refusal", "exit": r.returncode})
    large_seconds = None
    if args.phase == "large":
        output = root / "large-processed.fits"
        argv = [str(args.probe.resolve()), "process", str(mef), str(output)]
        print("START: existing image_loadext -> image_sub_local -> mef_hdrpix_dump; output:", output, flush=True)
        start = time.monotonic()
        r = subprocess.run(argv, text=True, capture_output=True, timeout=1800)
        large_seconds = time.monotonic() - start
        records.append({"argv": argv, "exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
        assert r.returncode == 0, records[-1]
        assert output.stat().st_size > 2**32
        print("VALIDATING: every output pixel, header order/scaling and padding in one bounded-memory pass", flush=True)
        checked_pixels += validate_output(output, SIDE, SIDE, COUNT)
    peak_rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * (1 if sys.platform == "darwin" else 1024)
    assert peak_rss <= 4 * 2**30, ("native RSS exceeds approved budget", peak_rss)
    assert sum(p.stat().st_blocks * 512 for p in root.iterdir() if p.is_file()) <= 32 * 2**30
    assert before == {mef.name: source_identity(mef, positions), cube.name: source_identity(cube, cube_spans)}
    receipt = {"stage": {"discovery": "IO-1", "reads": "IO-2", "writes": "IO-3", "focused": "IO-4 focused", "large": "IO-4 large"}[args.phase], "status": "passed", "commands": records,
        "files": {p.name: {"logical_bytes": p.stat().st_size, "physical_bytes": p.stat().st_blocks * 512} for p in (mef, cube)},
        "checked_processed_pixels": checked_pixels, "large_processing_seconds": large_seconds,
        "maximum_child_peak_rss_bytes": peak_rss,
        "scope": args.phase + "; synthetic image I/O, not scientific/full recipe acceptance"}
    (root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS:", receipt["stage"], "wide I/O controls; RETAINED:", root)


if __name__ == "__main__":
    main()
