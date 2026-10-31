"""Tiny FITS fixtures for the actual C M4 layout/bias boundary (#182)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def header(cards):
    lines = []
    for key, value in cards:
        line = f"{key} = {value}" if len(key) > 8 else f"{key:<8}= {value:>20}"
        if len(line) > 80:
            raise ValueError(line)
        lines.append(line.ljust(80))
    return ("".join(lines) + "END".ljust(80)).encode("ascii").ljust(
        ((len(lines) + 1 + 35) // 36) * 2880, b" ")


EMPTY = header([("SIMPLE", "T"), ("BITPIX", "8"), ("NAXIS", "0"), ("EXTEND", "T")])


def image(detector, value=0, *, primary=False, unsigned=False, values=None, extra=(), width=10, height=6):
    cards = [("SIMPLE", "T")] if primary else [("XTENSION", "'IMAGE   '")]
    cards += [("BITPIX", "16" if unsigned else "-32"), ("NAXIS", "2"),
              ("NAXIS1", str(width)), ("NAXIS2", str(height))]
    if not primary:
        cards += [("PCOUNT", "0"), ("GCOUNT", "1"), ("EXTNAME", "'SCI'")]
    cards += [("DETID", repr(detector)), ("AMPID", repr("amp-" + detector)),
              ("BUNIT", "'ADU'"), ("XBINNING", "1"), ("YBINNING", "1"),
              ("DATASEC", "'[1:10,1:6]'"), ("DETSEC", "'[1:10,1:6]'")]
    if unsigned:
        cards += [("BSCALE", "1"), ("BZERO", "32768")]
        values = [-32768, -32767, -1, 0, 32767] + [-32768] * (width * height - 5)
    elif values is None:
        values = [value] * (width * height)
    cards += list(extra)
    payload = struct.pack(f">{width * height}" + ("h" if unsigned else "f"), *values).ljust(2880, b"\0")
    return header(cards) + payload


def fixtures(directory):
    directory.mkdir()
    files = {
        "unsigned-primary.fits": image("A", primary=True, unsigned=True),
        "unsigned-extension.fits": EMPTY + image("A", unsigned=True),
        "unsigned-mosaic.fits": EMPTY + image("B", 201) + image("A", unsigned=True),
        "science.fits": EMPTY + image("A", 101) + image("B", 201),
        "calibration.fits": EMPTY + image("B", 21) + image("A", 11),
        "only-b.fits": image("B", 21, primary=True),
        "trimmed.fits": image("A", 11, primary=True, width=6, height=4),
        "duplicate-id.fits": EMPTY + image("A", 11) + image("A", 21),
        "duplicate-card.fits": image("A", primary=True, extra=[("BSCALE", "1"), ("BSCALE", "2")]),
        "bad-scale.fits": image("A", primary=True, extra=[("BSCALE", "NaN")]),
        "mutable.fits": image("A", 101, primary=True),
        "telemetry.fits": image("A", 101, primary=True, extra=[
            ("HIERARCH ESO DET TLM2 END", "3.300e-05 / Telemetry value")]),
        "hierarchical-id.fits": image("A", 101, primary=True, extra=[
            ("HIERARCH ESO DET CHIP ID", "'configured-chip-A'")]),
    }
    configured = image("A", primary=True, unsigned=True)
    kept = [configured[i:i + 80] for i in range(0, 2880, 80)
            if configured[i:i + 8].strip() not in (b"DETID", b"AMPID", b"BUNIT")]
    files["configured-primary.fits"] = b"".join(kept).ljust(2880, b" ") + configured[2880:]
    table = header([("XTENSION", "'BINTABLE'"), ("BITPIX", "8"), ("NAXIS", "2"),
                    ("NAXIS1", "8"), ("NAXIS2", "1"), ("PCOUNT", "0"),
                    ("GCOUNT", "1"), ("TFIELDS", "1"), ("DETID", "'A'")])
    files["table.fits"] = EMPTY + table + b"\0" * 2880
    valid = image("A", 101, primary=True)
    files["truncated.fits"] = valid[:-100]
    files["missing-end.fits"] = valid.replace(b"END" + b" " * 77, b" " * 80, 1)
    files["bad-identity.fits"] = valid.replace(b"'A'", b" 23", 1)
    for frame in range(3):
        values = [100 + y + 3 * frame +
                  (10 + frame + x + 2 * y if 2 <= x <= 7 else 0)
                  for y in range(6) for x in range(10)]
        files[f"bias-primary-{frame}.fits"] = image("A", primary=True, values=values)
        files[f"bias-extension-{frame}.fits"] = EMPTY + image("A", values=values)
        files[f"bias-mosaic-{frame}.fits"] = EMPTY + image("B", 201) + image("A", values=values)
    for name, content in files.items():
        (directory / name).write_bytes(content)
    os.mkfifo(directory / "nonregular.fifo")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--work-parent", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    probe = args.probe.resolve(strict=True)
    args.work_parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="m4-layout-", dir=args.work_parent))
    print("WORK DIRECTORY:", work, flush=True)
    # Provenance: freeze the sources/native probe; no installed program is selected.
    inputs = [root / "mefpp2" / path for path in (
        "ins/mef/common/mef_layout.c", "ins/mef/common/mef_layout.h",
        "ins/mef/common/mef_cal_bias.c", "ins/mef/common/mef_cal_bias.h",
        "tests/layout_probe.c", "tests/layout_contract.py")]
    before = {str(p): digest(p) for p in inputs}
    report = {"status": "running", "python": sys.executable, "platform": platform.platform(),
              "host": platform.node(), "probe": str(probe), "probe_sha256": digest(probe),
              "source_sha256": before, "commands": [],
              "scope": "tiny synthetic actual C layout/bias controls; no observational/normalization/CMOS/performance acceptance"}
    try:
        for instrument in ("omegacam", "wfi"):
            # Fixtures: known header/layout/pixel cases; mutable.fits is explicitly altered.
            folder = work / instrument
            fixtures(folder)
            immutable = {str(p): digest(p) for p in folder.glob("*.fits") if p.name != "mutable.fits"}
            mutable_size = (folder / "mutable.fits").stat().st_size
            paf = root / "mefpp2/ins/mef/config" / (instrument + ".paf")
            argv = [str(probe), str(folder.resolve()), str(paf)]
            log = work / (instrument + ".log")
            # Native checks: six groups including actual primary/MEF mef_cal_bias equality.
            with log.open("w") as stream:
                result = subprocess.run(argv, cwd=work, stdout=stream,
                                        stderr=subprocess.STDOUT, timeout=180)
            report["commands"].append({"argv": argv, "exit_status": result.returncode,
                                       "log": str(log), "log_sha256": digest(log)})
            if result.returncode:
                raise RuntimeError(f"{instrument} failed; retain {log}; do not replay unchanged")
            if "PASS: M4 native layout contract (six groups)" not in log.read_text():
                raise RuntimeError("Incomplete native control output")
            # Preservation: all immutable inputs/config/source bytes stay exact.
            if immutable != {str(p): digest(p) for p in folder.glob("*.fits") if p.name != "mutable.fits"}:
                raise RuntimeError("Immutable synthetic input changed")
            if (folder / "mutable.fits").stat().st_size != mutable_size + 1:
                raise RuntimeError("Expected source-change control did not run")
            print("PASS:", instrument, "six native groups; immutable fixture bytes preserved", flush=True)
        if before != {str(p): digest(p) for p in inputs}:
            raise RuntimeError("Sources changed during verification")
        report["status"] = "passed"
    finally:
        (work / "run-provenance.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS: M4 layout contract; no target/performance/scientific acceptance", flush=True)


if __name__ == "__main__":
    main()
