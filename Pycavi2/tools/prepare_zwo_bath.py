#!/usr/bin/env python3
"""Bath/ASI1600MM Pro raw classification helper (#184), not a reduction engine.

Plan reads headers/stat only. Apply makes new copies, preserving all payload
bytes and all original cards except stale primary CHECKSUM/DATASUM cards.
No pixel arrays, Pycavi routines, native programs or calibration selection.
"""
import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

from astropy.io import fits

from fits_preparation import (require, sha, stamp, raw_header, outside, write_json,
                              copy_prepared)

VERSION = "bath-dpr-preparation-1"
CAMERA = "ZWO CCD ASI1600MM Pro"
FILTERS = {"Blue": 0.035, "Green": 0.055, "Red": 0.1, "Luminance": 0.018}
DPR = ("ESO DPR TYPE", "ESO DPR CATG", "ESO DPR TECH")
MAX_HEADER = 256 * 1024


def role_for(relative):
    parts = relative.parts
    if len(parts) == 2 and parts[0] in ("Bias", "Darks"):
        kind = "BIAS" if parts[0] == "Bias" else "DARK"
        return kind, "CALIB", None, 0.000032 if kind == "BIAS" else 30.0
    if len(parts) == 2 and parts[0] in FILTERS:
        return "OBJECT", "SCIENCE", parts[0], 32.0
    if len(parts) == 3 and parts[0] == "Flats" and parts[1] in FILTERS:
        return "FLAT", "CALIB", parts[1], FILTERS[parts[1]]
    raise ValueError("Unknown directory layout; no classification guessed")


def inspect(path, root):
    """Dataset-specific light checks; no payload read or physical flat validation."""
    relative = path.relative_to(root)
    kind, category, band, exposure = role_for(relative)
    before = stamp(path)
    raw, end = raw_header(path)
    header = fits.Header.fromstring(raw.decode("ascii"), sep="")
    counts = collections.Counter(card.keyword for card in header.cards)
    selected = ("SIMPLE", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "BSCALE",
                "BZERO", "INSTRUME", "XBINNING", "YBINNING", "EXPTIME",
                "GAIN", "OFFSET", "CCD-TEMP", "FILTER", "FRAME", "IMAGETYP",
                "BAYERPAT", "DATASUM", "CHECKSUM", *DPR)
    require(all(counts[k] <= 1 for k in selected), "Duplicate selected header card")
    # Refuse alternative spellings, rather than leaving competing classifications.
    aliases = ("DPR.TYPE", "DPR.CATG", "DPR.TECH", "DPR TYPE", "DPR CATG",
               "DPR TECH", "ESO.DPR.TYPE", "ESO.DPR.CATG", "ESO.DPR.TECH")
    require(not any(k in header for k in aliases), "Noncanonical DPR alias needs review")
    expected = {"SIMPLE": True, "BITPIX": 16, "NAXIS": 2, "NAXIS1": 4656,
                "NAXIS2": 3520, "BSCALE": 1, "BZERO": 32768,
                "INSTRUME": CAMERA, "XBINNING": 1, "YBINNING": 1,
                "GAIN": 139.0, "OFFSET": 10.0}
    for key, value in expected.items():
        require(header.get(key) == value and not (
            isinstance(header.get(key), bool) and key != "SIMPLE"),
            "Unexpected or missing " + key)
    require(header["SIMPLE"] is True, "SIMPLE must be a FITS boolean")
    require(all(type(header[k]) is int for k in
                ("BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "XBINNING", "YBINNING")),
            "Structural/binning values must be integers")
    require(header.get("GROUPS", False) is False, "Random groups unsupported")
    require(not str(header.get("BAYERPAT", "")).strip(), "Bayer metadata on mono fixture")
    for key, value in (("EXPTIME", exposure),):
        actual = header.get(key)
        require(isinstance(actual, (float, int)) and not isinstance(actual, bool)
                and math.isfinite(actual) and math.isclose(actual, value, rel_tol=1e-8),
                "Exposure disagrees with directory profile")
    if "EXPOSURE" in header:
        require(math.isclose(float(header["EXPOSURE"]), exposure, rel_tol=1e-8),
                "EXPOSURE and EXPTIME disagree")
    temperature = header.get("CCD-TEMP")
    require(isinstance(temperature, (int, float)) and not isinstance(temperature, bool)
            and math.isfinite(temperature), "Missing/invalid CCD-TEMP")
    warnings = []
    if temperature != -5.0:
        warnings.append("temperature_differs_from_minus5")
    if band:
        require(header.get("FILTER") == band, "Filter disagrees with directory")
    else:
        warnings.append("bias_dark_filter_not_used_for_classification")
    frame = str(header.get("FRAME", "")).strip().lower()
    imagetype = str(header.get("IMAGETYP", "")).strip().lower()
    allowed = {"BIAS": ("bias", "bias frame"), "DARK": ("dark", "dark frame"),
               "OBJECT": ("light", "light frame"), "FLAT": ("flat", "flat frame")}
    if kind == "FLAT" and (frame, imagetype) == ("light", "light frame"):
        warnings.append("directory_flat_light_header_requires_acknowledgement")
    else:
        require((frame, imagetype) == allowed[kind], "Frame type contradicts directory")
    prefix = "Bias" if kind == "BIAS" else "Dark" if kind == "DARK" else (
        "M_51_Light_" + band if kind == "OBJECT" else "Light_" + band)
    match = re.fullmatch(re.escape(prefix) + r"_([0-9.]+)_secs_[0-9]+\.fits",
                         path.name, flags=re.IGNORECASE)
    require(match is not None and math.isclose(float(match[1]), exposure, rel_tol=1e-8),
            "Filename/exposure disagrees with directory profile")
    proposed = dict(zip(DPR, (kind, category, "IMAGE")))
    for key, value in proposed.items():
        require(key not in header or header[key] == value,
                "Existing DPR classification conflicts: " + key)
    # This narrow helper accepts exactly the known single-primary payload layout.
    payload_size = ((4656 * 3520 * 2 + 2879) // 2880) * 2880
    require(before[2] == len(raw) + payload_size,
            "Truncated/extra payload or additional HDU; layout needs review")
    require(stamp(path) == before, "Source changed during header inspection")
    return {"file": relative.as_posix(), "source_stat": before,
            "header_sha256": sha(raw), "data_offset": len(raw),
            "classification": proposed, "warnings": warnings,
            "reported": {k: header.get(k) for k in
                         ("FRAME", "IMAGETYP", "EXPTIME", "FILTER", "CCD-TEMP")},
            "checksum_cards_removed_in_copy": [k for k in ("CHECKSUM", "DATASUM")
                                               if k in header]}


def inventory(root):
    require(root.is_dir() and not root.is_symlink(), "Expected regular input directory")
    entries, errors, ignored = [], [], collections.Counter()
    total = 0
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in list(dirs):
            if (Path(directory) / name).is_symlink():
                errors.append({"file": str((Path(directory) / name).relative_to(root)),
                               "error": "Symlink directory refused"})
                dirs.remove(name)
        dirs.sort()
        for name in sorted(names):
            total += 1
            require(total <= 10000, "File inventory exceeds limit")
            path = Path(directory) / name
            relative = str(path.relative_to(root))
            if path.is_symlink() or not path.is_file():
                errors.append({"file": relative, "error": "Nonregular input refused"})
                continue
            if path.name.lower().endswith((".fits.gz", ".fit.gz", ".fts.gz", ".fz")):
                errors.append({"file": relative, "error": "Compressed FITS unsupported"})
                continue
            if path.suffix.lower() not in (".fits", ".fit", ".fts"):
                ignored[path.suffix.lower() or "(none)"] += 1
                continue
            try:
                entries.append(inspect(path, root))
            except Exception as exc:
                errors.append({"file": relative, "error": str(exc)})
    require(entries or errors, "No FITS candidates found")
    return {"notation": VERSION, "root": str(root.resolve()), "entries": entries,
            "errors": errors, "ignored": dict(ignored)}


def apply_plan(plan_path, expected_sha, output, accept_flats):
    content = plan_path.read_bytes()
    require(sha(content) == expected_sha, "Reviewed plan SHA256 differs")
    plan = json.loads(content)
    require(plan.get("notation") == VERSION, "Unknown plan version")
    root = Path(plan["root"])
    # Recompute every rule and source identity; the JSON is not executable authority.
    fresh = inventory(root)
    require(fresh == plan, "Dataset/header/settings changed since reviewed plan")
    require(not plan["errors"], "Plan contains blocked inputs")
    require(accept_flats or not any(
        "directory_flat_light_header_requires_acknowledgement" in r["warnings"]
        for r in plan["entries"]), "Flat/Light conflict requires --accept-directory-flats")
    require(outside(output, root) and outside(root, output), "Output must be separate from inputs")
    require(not output.exists() and not output.is_symlink(), "Output must be new")
    output.mkdir()
    marker = output / "PREPARATION_INCOMPLETE"
    marker.write_text("Do not admit this directory to the pipeline.\n")
    results = []
    for record in plan["entries"]:
        source = root / record["file"]
        require(inspect(source, root) == record, "Source changed before preparation")
        results.append(copy_prepared(source, output / record["file"], record, expected_sha))
    require(inventory(root) == plan, "Source inventory changed during preparation")
    write_json(output / "preparation-manifest.json", {
        "notation": VERSION, "reviewed_plan_sha256": expected_sha,
        "accept_directory_flats": accept_flats, "plan": plan, "products": results})
    marker.rename(output / "PREPARATION_COMPLETE")
    print("PREPARED:", output, "| files:", len(results), "| payload bytes verified")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="Header-only dry run; never edits source FITS")
    plan.add_argument("--root", type=Path, required=True)
    plan.add_argument("--report", type=Path, required=True)
    apply = commands.add_parser("apply", help="Write classified copies from an exact reviewed plan")
    apply.add_argument("--plan", type=Path, required=True)
    apply.add_argument("--expected-plan-sha256", required=True)
    apply.add_argument("--output", type=Path, required=True)
    apply.add_argument("--accept-directory-flats", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            require(outside(args.report, args.root), "Report must be outside raw inputs")
            report = inventory(args.root)
            write_json(args.report, report)
            print("PLAN:", args.report, "| SHA256:", sha(args.report.read_bytes()))
            counts = collections.Counter(r["classification"][DPR[0]] for r in report["entries"])
            print("CLASSIFICATIONS:", dict(counts), "| BLOCKED:", len(report["errors"]))
            print("WARNINGS:", dict(collections.Counter(
                w for r in report["entries"] for w in r["warnings"])))
            for error in report["errors"]:
                print("BLOCKED:", json.dumps(error))
            return 2 if report["errors"] else 0
        apply_plan(args.plan, args.expected_plan_sha256, args.output, args.accept_directory_flats)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("STOP:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
