#!/usr/bin/env python3
"""Prepare ZWO ASI FITS copies using an explicit TOML camera/dataset policy.

Header-only plan, then reviewed-plan copy. No reduction or pixel interpretation.
"""
import argparse
import collections
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
import sys
import tomllib

from astropy.io import fits
from fits_preparation import require, sha, stamp, raw_header, outside, write_json, copy_prepared

VERSION = "zwo-asi-preparation-1"
DPR = ("ESO DPR TYPE", "ESO DPR CATG", "ESO DPR TECH")
PROVENANCE = {"OBSERVAT", "ORIGIN", "TELESCOP", "OBSERVER",
              "WENU PROV PAPER DOI", "WENU PROV DATA DOI"}
EXPECTED = {"BITPIX", "NAXIS1", "NAXIS2", "BSCALE", "BZERO", "XBINNING", "YBINNING",
            "GAIN", "OFFSET"}
TELESCOPE_EXPECTED = {"TELESCOP", "FOCALLEN", "APTDIA", "SCALE", "PIXSIZE1",
                      "PIXSIZE2", "XPIXSZ", "YPIXSZ"}


def keys(table, allowed, required=()):
    require(isinstance(table, dict), "Expected TOML table")
    require(not set(table) - set(allowed), "Unknown configuration keys: " + str(set(table) - set(allowed)))
    require(set(required) <= set(table), "Missing configuration keys: " + str(set(required) - set(table)))


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def load_profile(path):
    raw = path.read_bytes()
    require(len(raw) <= 256 * 1024, "Configuration exceeds limit")
    cfg = tomllib.loads(raw.decode("utf-8"))
    keys(cfg, {"schema_version", "camera", "dataset", "provenance", "rules", "reference", "telescope"},
         {"schema_version", "camera", "dataset", "provenance", "rules"})
    require(type(cfg["schema_version"]) is int and cfg["schema_version"] == 1, "Unknown schema version")
    keys(cfg["camera"], {"model", "instrume", "monochrome"}, {"model", "instrume", "monochrome"})
    require(isinstance(cfg["camera"]["model"], str) and cfg["camera"]["model"].startswith("ZWO ASI"),
            "Expected ZWO ASI model")
    require(cfg["camera"]["monochrome"] is True, "Only reviewed monochrome primary-image layouts supported")
    aliases = cfg["camera"]["instrume"]
    require(isinstance(aliases, list) and aliases and all(type(v) is str and v for v in aliases),
            "Explicit INSTRUME strings required")
    keys(cfg["dataset"], {"expected", "temperature_c"}, {"expected", "temperature_c"})
    expect = cfg["dataset"]["expected"]
    keys(expect, EXPECTED, EXPECTED)
    require(all(number(v) for v in expect.values()), "Expected header values must be finite numbers")
    for k in ("BITPIX", "NAXIS1", "NAXIS2", "XBINNING", "YBINNING"):
        require(type(expect[k]) is int, "Integer required: " + k)
    require(expect["BITPIX"] in (8, 16, 32, 64, -32, -64), "Unsupported BITPIX")
    require(all(expect[k] > 0 for k in ("NAXIS1", "NAXIS2", "XBINNING", "YBINNING")), "Invalid dimensions/binning")
    require(expect["BSCALE"] != 0 and number(cfg["dataset"]["temperature_c"]), "Invalid scaling/temperature")
    provenance = cfg["provenance"]
    keys(provenance, PROVENANCE, {"OBSERVAT", "ORIGIN", "WENU PROV PAPER DOI", "WENU PROV DATA DOI"})
    for k, v in provenance.items():
        require(type(v) is str and v.strip() and v.isascii() and all(32 <= ord(c) < 127 for c in v),
                "Provenance must be printable ASCII: " + k)
        require(len(fits.Card(k if len(k) <= 8 else "HIERARCH " + k, v).image) <= 80,
                "Provenance value too long: " + k)
    if "telescope" in cfg:
        telescope = cfg["telescope"]
        keys(telescope, {"name_prefix", "expected"}, {"name_prefix", "expected"})
        prefix = telescope["name_prefix"]
        require(type(prefix) is str and prefix.strip() and prefix.isascii()
                and all(32 <= ord(c) < 127 for c in prefix), "Invalid telescope name prefix")
        require(len(fits.Card("HIERARCH WENU PROV TELESCOPE", prefix + " 2000-01-01").image) <= 80,
                "Telescope name exceeds one FITS card")
        keys(telescope["expected"], TELESCOPE_EXPECTED, TELESCOPE_EXPECTED)
        require(type(telescope["expected"]["TELESCOP"]) is str, "Expected TELESCOP must be text")
        require(all(number(v) and v > 0 for k, v in telescope["expected"].items()
                    if k != "TELESCOP"), "Invalid telescope geometry checks")
    rules = cfg["rules"]
    require(isinstance(rules, list) and 0 < len(rules) <= 256, "Expected bounded classification rules")
    directories = set()
    for rule in rules:
        keys(rule, {"directory", "type", "exposure_s", "filename_prefix", "filter", "allow_light_flat"},
             {"directory", "type", "exposure_s", "filename_prefix"})
        directory = rule["directory"]
        require(type(directory) is str and directory and not directory.startswith("/")
                and all(p not in ("", ".", "..") for p in directory.split("/")), "Invalid rule directory")
        require(directory not in directories, "Duplicate directory rule")
        directories.add(directory)
        require(rule["type"] in ("BIAS", "DARK", "OBJECT", "FLAT"), "Unknown exposure type")
        require(number(rule["exposure_s"]) and rule["exposure_s"] >= 0, "Invalid exposure")
        require(type(rule["filename_prefix"]) is str and rule["filename_prefix"]
                and "/" not in rule["filename_prefix"], "Invalid filename prefix")
        require("filter" not in rule or type(rule["filter"]) is str and rule["filter"], "Invalid filter")
        require(rule["type"] not in ("OBJECT", "FLAT") or "filter" in rule, "Filter required")
        require("allow_light_flat" not in rule or (type(rule["allow_light_flat"]) is bool
                and rule["type"] == "FLAT"), "Flat acknowledgement applies only to flats")
    # Reference is descriptive text only, never executable policy or header authority.
    require(isinstance(cfg.get("reference", {}), dict), "Reference must be a table")
    require(all(type(k) is str and type(v) is str for k, v in cfg.get("reference", {}).items()),
            "Reference entries must be strings")
    return {"sha256": sha(raw), "settings": cfg}


def inspect(path, root, profile):
    cfg = profile["settings"]
    relative = path.relative_to(root)
    matches = [r for r in cfg["rules"] if relative.parent.as_posix() == r["directory"]]
    require(len(matches) == 1, "Unknown directory layout; no classification guessed")
    rule = matches[0]
    before = stamp(path)
    raw, _ = raw_header(path)
    header = fits.Header.fromstring(raw.decode("ascii"), sep="")
    selected = {"SIMPLE", "NAXIS", "INSTRUME", "EXPTIME", "EXPOSURE", "CCD-TEMP",
                "FILTER", "FRAME", "IMAGETYP", "BAYERPAT", "GROUPS", "CHECKSUM", "DATASUM",
                *EXPECTED, *DPR, *cfg["provenance"]}
    if "telescope" in cfg:
        selected.update({"DATE-OBS", "WENU PROV TELESCOPE", *TELESCOPE_EXPECTED})
    counts = collections.Counter(card.keyword for card in header.cards)
    require(all(counts[k] <= 1 for k in selected), "Duplicate selected header card")
    for k in header:
        canonical = k.replace(".", " ")
        require(canonical not in {*DPR, "DPR TYPE", "DPR CATG", "DPR TECH"} or k in DPR,
                "Noncanonical DPR alias needs review")
    require(header.get("SIMPLE") is True and type(header.get("NAXIS")) is int
            and header["NAXIS"] == 2, "Expected primary 2D image")
    require(header.get("INSTRUME") in cfg["camera"]["instrume"], "INSTRUME conflicts with camera profile")
    for k, v in cfg["dataset"]["expected"].items():
        require(number(header.get(k)) and header[k] == v, "Unexpected or missing " + k)
    for k in ("BITPIX", "NAXIS1", "NAXIS2", "XBINNING", "YBINNING"):
        require(type(header[k]) is int, "Structural/binning values must be integers")
    require(header.get("GROUPS", False) is False, "Random groups unsupported")
    require(not str(header.get("BAYERPAT", "")).strip(), "Bayer metadata on monochrome input")
    for k in ("EXPTIME", "EXPOSURE"):
        if k == "EXPTIME" or k in header:
            require(number(header.get(k)) and math.isclose(header[k], rule["exposure_s"], rel_tol=1e-8),
                    "Exposure disagrees with directory profile")
    temperature = header.get("CCD-TEMP")
    require(number(temperature), "Missing/invalid CCD-TEMP")
    warnings = []
    if temperature != cfg["dataset"]["temperature_c"]:
        warnings.append("temperature_differs_from_profile")
    if "filter" in rule:
        require(header.get("FILTER") == rule["filter"], "Filter disagrees with directory")
    else:
        warnings.append("bias_dark_filter_not_used_for_classification")
    kind = rule["type"]
    pair = tuple(str(header.get(k, "")).strip().lower() for k in ("FRAME", "IMAGETYP"))
    expected_pair = {"BIAS": ("bias", "bias frame"), "DARK": ("dark", "dark frame"),
                     "OBJECT": ("light", "light frame"), "FLAT": ("flat", "flat frame")}[kind]
    if kind == "FLAT" and rule.get("allow_light_flat", False) and pair == ("light", "light frame"):
        warnings.append("directory_flat_light_header_requires_acknowledgement")
    else:
        require(pair == expected_pair, "Frame type contradicts directory")
    match = re.fullmatch(re.escape(rule["filename_prefix"]) + r"_([0-9.]+)_secs_[0-9]+\.fits",
                         path.name, flags=re.IGNORECASE)
    require(match is not None and math.isclose(float(match[1]), rule["exposure_s"], rel_tol=1e-8),
            "Filename/exposure disagrees with profile")
    classification = dict(zip(DPR, (kind, "SCIENCE" if kind == "OBJECT" else "CALIB", "IMAGE")))
    additions = {**classification, **cfg["provenance"]}
    if "telescope" in cfg:
        # Identification requires the complete reviewed header signature, not a camera guess.
        for k, v in cfg["telescope"]["expected"].items():
            actual = header.get(k)
            require((type(actual) is str and actual == v) if k == "TELESCOP"
                    else (number(actual) and actual == v), "Telescope signature mismatch: " + k)
        observed = header.get("DATE-OBS")
        require(type(observed) is str and re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?",
            observed) is not None, "Expected ISO DATE-OBS timestamp for telescope name")
        day = datetime.fromisoformat(observed).date().isoformat()
        additions["WENU PROV TELESCOPE"] = cfg["telescope"]["name_prefix"] + " " + day
    for k, v in additions.items():
        require(k not in header or type(header[k]) is type(v) and header[k] == v,
                "Existing header conflicts with profile: " + k)
    payload = header["NAXIS1"] * header["NAXIS2"] * (abs(header["BITPIX"]) // 8)
    require(before[2] == len(raw) + ((payload + 2879) // 2880) * 2880,
            "Truncated/extra payload or additional HDU; layout needs review")
    require(stamp(path) == before, "Source changed during inspection")
    return {"file": relative.as_posix(), "source_stat": before, "header_sha256": sha(raw),
            "data_offset": len(raw), "classification": classification, "additions": additions,
            "warnings": warnings, "reported": {k: header.get(k) for k in sorted(selected)},
            "checksum_cards_removed_in_copy": [k for k in ("CHECKSUM", "DATASUM") if k in header]}


def inventory(root, profile, inspector=None):
    if inspector is None:
        inspector = inspect
    require(root.is_dir() and not root.is_symlink(), "Expected regular input directory")
    entries, errors, ignored = [], [], collections.Counter()
    total = 0
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in list(dirs):
            if (Path(directory) / name).is_symlink():
                errors.append({"file": str((Path(directory) / name).relative_to(root)), "error": "Symlink directory refused"})
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
                entries.append(inspector(path, root, profile))
            except (OSError, ValueError, KeyError, TypeError, fits.verify.VerifyError) as exc:
                errors.append({"file": relative, "error": str(exc)})
    require(entries or errors, "No FITS candidates found")
    return {"notation": VERSION, "root": str(root.resolve()), "profile": profile,
            "entries": entries, "errors": errors, "ignored": dict(ignored)}


def apply_plan(plan_path, expected_sha, output, accept_flats, config):
    content = plan_path.read_bytes()
    require(sha(content) == expected_sha, "Reviewed plan SHA256 differs")
    plan = json.loads(content)
    require(plan.get("notation") == VERSION, "Unknown plan version")
    profile = load_profile(config)
    root = Path(plan["root"])
    require(inventory(root, profile) == plan, "Dataset/header/configuration changed since reviewed plan")
    require(not plan["errors"], "Plan contains blocked inputs")
    require(accept_flats or not any("directory_flat_light_header_requires_acknowledgement" in r["warnings"]
                                  for r in plan["entries"]), "Flat/Light conflict requires --accept-directory-flats")
    require(outside(output, root) and outside(root, output), "Output must be separate from inputs")
    require(outside(config, output) and outside(plan_path, output), "Output contains preparation inputs")
    require(not output.exists() and not output.is_symlink(), "Output must be new")
    output.mkdir()
    marker = output / "PREPARATION_INCOMPLETE"
    marker.write_text("Do not admit this directory to the pipeline.\n")
    products = []
    for record in plan["entries"]:
        source = root / record["file"]
        require(inspect(source, root, profile) == record, "Source changed before preparation")
        products.append(copy_prepared(source, output / record["file"], record, expected_sha,
                                      history="ZWO ASI prep plan "))
    require(inventory(root, load_profile(config)) == plan, "Source/configuration changed during preparation")
    write_json(output / "preparation-manifest.json", {
        "notation": VERSION, "reviewed_plan_sha256": expected_sha,
        "accept_directory_flats": accept_flats, "plan": plan, "products": products})
    marker.rename(output / "PREPARATION_COMPLETE")
    print("PREPARED:", output, "| files:", len(products), "| payload bytes verified")


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if any(a in ("--observatory", "--camera", "--directories") or
           a.startswith(("--observatory=", "--camera=", "--directories=")) for a in arguments):
        from asi_preparation_profiles import main as simple_main
        return simple_main(arguments)
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "apply"):
        command = commands.add_parser(name)
        command.add_argument("--config", type=Path, required=True)
        if name == "plan":
            command.add_argument("--root", type=Path, required=True)
            command.add_argument("--report", type=Path, required=True)
        else:
            command.add_argument("--plan", type=Path, required=True)
            command.add_argument("--expected-plan-sha256", required=True)
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--accept-directory-flats", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            require(outside(args.report, args.root), "Report must be outside raw inputs")
            require(args.report.resolve() != args.config.resolve(), "Report would replace configuration")
            report = inventory(args.root, load_profile(args.config))
            write_json(args.report, report)
            print("PLAN:", args.report, "| SHA256:", sha(args.report.read_bytes()))
            print("CLASSIFICATIONS:", dict(collections.Counter(r["classification"][DPR[0]]
                  for r in report["entries"])), "| BLOCKED:", len(report["errors"]))
            print("WARNINGS:", dict(collections.Counter(w for r in report["entries"] for w in r["warnings"])))
            for error in report["errors"]:
                print("BLOCKED:", json.dumps(error))
            return 2 if report["errors"] else 0
        apply_plan(args.plan, args.expected_plan_sha256, args.output, args.accept_directory_flats, args.config)
        return 0
    except (OSError, ValueError, KeyError, TypeError, fits.verify.VerifyError) as exc:
        print("STOP:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
