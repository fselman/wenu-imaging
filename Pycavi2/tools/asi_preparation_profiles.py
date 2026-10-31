"""Simple site/camera/directory inputs and generated dataset TOML (#184).

No partitioning, calibration choice or numerical processing. The legacy explicit
profile interface remains available in prepare_zwo_asi.py.
"""
import argparse
import collections
from datetime import datetime
import json
import math
from pathlib import Path
import re
import sys
import tomllib

from astropy.io import fits
from fits_preparation import require, sha, stamp, raw_header, outside, copy_prepared, write_json

VERSION = "zwo-asi-dataset-2"
ROLES = {"bias": "BIAS", "dark": "DARK", "science": "OBJECT", "flat": "FLAT",
         "dome_flat": "FLAT,DOME", "sky_flat": "FLAT,SKY"}
DPR = ("ESO DPR TYPE", "ESO DPR CATG", "ESO DPR TECH")
NUMERIC = ("EXPTIME", "EXPOSURE", "GAIN", "OFFSET", "CCD-TEMP", "FOCALLEN", "APTDIA",
           "SCALE", "XPIXSZ", "YPIXSZ", "PIXSIZE1", "PIXSIZE2")
MODE_KEYS = ("READMODE", "READOUTM", "READOUT", "ADCDEPTH", "ADCBITS", "HIGHSPEED")
SELECTED = {"SIMPLE", "NAXIS", "NAXIS1", "NAXIS2", "BITPIX", "GROUPS", "BSCALE", "BZERO",
            "INSTRUME", "FILTER", "FRAME", "IMAGETYP", "DATE-OBS", "TELESCOP", "OBSERVER",
            "SITELAT", "SITELONG", "BAYERPAT", "XBINNING", "YBINNING", "CHECKSUM", "DATASUM",
            *NUMERIC, *MODE_KEYS, *DPR}
PROV = {"OBSERVAT", "ORIGIN", "WENU PROV PAPER DOI", "WENU PROV DATA DOI",
        "WENU PROV TELESCOPE", "WENU PROV CAMERA", "WENU PROV SENSOR", "WENU PROV SHUTTER"}


def keys(table, allowed, required=()):
    require(type(table) is dict, "Expected TOML table")
    require(not set(table) - set(allowed), "Unknown input keys: " + str(set(table)-set(allowed)))
    require(set(required) <= set(table), "Missing input keys: " + str(set(required)-set(table)))


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def text(value):
    return type(value) is str and bool(value.strip()) and value.isascii() and all(32 <= ord(c) < 127 for c in value)


def toml_text(value):
    """Serialize only our bounded plain-data schema; validate every generated plan."""
    lines = []
    def name(path):
        return ".".join(json.dumps(p, ensure_ascii=False) for p in path)
    def atom(v):
        if type(v) is str:
            return json.dumps(v, ensure_ascii=False)
        if type(v) is bool:
            return str(v).lower()
        if number(v):
            return repr(v)
        if type(v) is list and all(type(x) is not dict for x in v):
            return "[" + ", ".join(atom(x) for x in v) + "]"
        raise ValueError("Unsupported generated TOML value")
    def table(obj, path):
        for k, v in obj.items():
            if type(v) is not dict and not (type(v) is list and v and type(v[0]) is dict):
                lines.append(json.dumps(k) + " = " + atom(v))
        for k, v in obj.items():
            p = path + [k]
            if type(v) is dict:
                lines.extend(["", "[" + name(p) + "]"])
                table(v, p)
            elif type(v) is list and v and type(v[0]) is dict:
                for item in v:
                    require(type(item) is dict, "Mixed generated TOML array")
                    lines.extend(["", "[[" + name(p) + "]]"])
                    table(item, p)
    table(value, [])
    result = "# Generated dataset inventory and proposed preparation; review before apply.\n" + "\n".join(lines) + "\n"
    require(tomllib.loads(result) == value, "Generated TOML does not round-trip")
    return result


def load_bundle(observatory, camera, directories):
    bundle = {}
    for label, path in [("observatory", observatory), ("camera", camera), ("directories", directories)]:
        require(path.is_file() and not path.is_symlink(), "Expected regular input TOML: " + label)
        raw = path.read_bytes()
        require(len(raw) <= 256*1024, "Input TOML exceeds limit")
        cfg = tomllib.loads(raw.decode("utf-8"))
        require(type(cfg.get("schema_version")) is int and cfg["schema_version"] == 1,
                "Unknown input schema: " + label)
        bundle[label] = {"path": str(path.resolve()), "sha256": sha(raw), "settings": cfg}
    obs, cam, layout = [bundle[k]["settings"] for k in ("observatory", "camera", "directories")]
    keys(obs, {"schema_version", "name", "origin", "paper_doi", "telescope"}, {"schema_version", "name"})
    require(all(text(v) for k, v in obs.items() if k not in ("schema_version", "telescope")), "Invalid observatory text")
    if "telescope" in obs:
        keys(obs["telescope"], {"name_prefix", "aperture_mm", "focal_length_mm"}, {"name_prefix"})
        require(text(obs["telescope"]["name_prefix"]), "Invalid telescope name")
        require(all(number(v) and v > 0 for k, v in obs["telescope"].items() if k != "name_prefix"),
                "Invalid telescope dimensions")
    required = {"schema_version", "model", "instrume", "monochrome", "width_pixels", "height_pixels", "pixel_size_um"}
    keys(cam, required | {"sensor", "shutter", "manual", "capabilities"}, required)
    require(text(cam["model"]) and cam["model"].startswith("ZWO ASI"), "Expected ZWO ASI model")
    require(cam["monochrome"] is True, "Colour/Bayer preparation remains unqualified")
    require(type(cam["instrume"]) is list and cam["instrume"] and all(text(v) for v in cam["instrume"]), "Invalid INSTRUME aliases")
    require(all(type(cam[k]) is int and cam[k] > 0 for k in ("width_pixels", "height_pixels")), "Invalid camera dimensions")
    require(number(cam["pixel_size_um"]) and cam["pixel_size_um"] > 0, "Invalid pixel size")
    require(all(text(cam[k]) for k in ("sensor", "shutter") if k in cam), "Invalid camera text")
    if "manual" in cam:
        keys(cam["manual"], {"path", "revision", "date", "sha256", "sections"})
        require(all(text(v) for v in cam["manual"].values()), "Invalid manual reference")
    if "capabilities" in cam:
        keys(cam["capabilities"], {"adc_bits", "cooling"})
        require("adc_bits" not in cam["capabilities"] or type(cam["capabilities"]["adc_bits"]) is list
                and all(type(v) is int and v > 0 for v in cam["capabilities"]["adc_bits"]), "Invalid ADC capability")
        require("cooling" not in cam["capabilities"] or text(cam["capabilities"]["cooling"]), "Invalid cooling reference")
    keys(layout, {"schema_version", "data_doi", "directories", "filters"}, {"schema_version", "directories"})
    require("data_doi" not in layout or text(layout["data_doi"]), "Invalid data DOI")
    keys(layout["directories"], ROLES)
    names = {}
    for role, aliases in layout["directories"].items():
        require(type(aliases) is list and all(text(a) and "/" not in a and a not in (".", "..") for a in aliases), "Invalid role directory names")
        for alias in aliases:
            require(alias.casefold() not in names or names[alias.casefold()] == role, "Conflicting directory role aliases")
            names[alias.casefold()] = role
    require(type(layout.get("filters", {})) is dict, "Expected filter mapping table")
    seen = {}
    for alias, value in layout.get("filters", {}).items():
        require(text(alias) and "/" not in alias and text(value), "Invalid filter directory mapping")
        require(alias.casefold() not in seen or seen[alias.casefold()] == value, "Conflicting filter aliases")
        seen[alias.casefold()] = value
    return bundle


def merge_roles(roles):
    roles = set(roles)
    if any(r.startswith("FLAT,") for r in roles):
        roles.discard("FLAT")
    require(len(roles) <= 1, "Contradictory exposure roles")
    return next(iter(roles)) if roles else ""


def header_role(value):
    require(type(value) is str, "Invalid frame-type label")
    normalized = value.strip().casefold()
    values = {"bias": "BIAS", "bias frame": "BIAS", "dark": "DARK", "dark frame": "DARK",
              "light": "OBJECT", "light frame": "OBJECT", "object": "OBJECT",
              "flat": "FLAT", "flat frame": "FLAT", "flat,dome": "FLAT,DOME", "flat,sky": "FLAT,SKY"}
    require(normalized in values, "Unknown frame-type label: " + value)
    return values[normalized]


def inspect(path, root, bundle):
    obs, cam, layout = [bundle[k]["settings"] for k in ("observatory", "camera", "directories")]
    relative = path.relative_to(root)
    before = stamp(path)
    raw, end = raw_header(path)
    h = fits.Header.fromstring(raw.decode("ascii"), sep="")
    counts = collections.Counter(c.keyword for c in h.cards)
    require(all(counts[k] <= 1 for k in SELECTED | PROV), "Duplicate selected header card")
    for k in h:
        canonical = k.replace(".", " ")
        require(canonical not in {*DPR, "DPR TYPE", "DPR CATG", "DPR TECH"} or k in DPR, "Noncanonical DPR alias")
    require(h.get("SIMPLE") is True and type(h.get("NAXIS")) is int and h["NAXIS"] == 2, "Expected primary 2D image")
    require(type(h.get("BITPIX")) is int and h["BITPIX"] in (8,16,32,64,-32,-64), "Invalid BITPIX")
    for key, maximum in [("NAXIS1", cam["width_pixels"]), ("NAXIS2", cam["height_pixels"])]:
        require(type(h.get(key)) is int and 0 < h[key] <= maximum, "Invalid image dimension: " + key)
    for key in ("XBINNING", "YBINNING"):
        require(key not in h or type(h[key]) is int and h[key] > 0, "Invalid binning")
    require(h.get("GROUPS", False) is False and not str(h.get("BAYERPAT", "")).strip(), "Unsupported groups/Bayer layout")
    for key in ("BSCALE", "BZERO", *NUMERIC):
        require(key not in h or number(h[key]), "Nonfinite/nonnumeric acquisition value: " + key)
    require(h.get("BSCALE", 1) != 0, "Invalid BSCALE")
    require(all(k not in h or h[k] >= 0 for k in ("EXPTIME", "EXPOSURE")), "Negative exposure")
    if "EXPTIME" in h and "EXPOSURE" in h:
        require(math.isclose(h["EXPTIME"], h["EXPOSURE"], rel_tol=1e-8), "EXPTIME/EXPOSURE conflict")
    for key in ("PIXSIZE1", "PIXSIZE2"):
        require(key not in h or math.isclose(h[key], cam["pixel_size_um"], rel_tol=1e-6), "Camera pixel size conflicts: " + key)
    warnings = []
    additions = {"OBSERVAT": obs["name"], "WENU PROV CAMERA": cam["model"]}
    for src, dest in [("origin", "ORIGIN"), ("paper_doi", "WENU PROV PAPER DOI")]:
        if src in obs:
            additions[dest] = obs[src]
    if "data_doi" in layout:
        additions["WENU PROV DATA DOI"] = layout["data_doi"]
    for src, dest in [("sensor", "WENU PROV SENSOR"), ("shutter", "WENU PROV SHUTTER")]:
        if src in cam:
            additions[dest] = cam[src]
    if "INSTRUME" in h:
        require(h["INSTRUME"] in cam["instrume"], "INSTRUME conflicts with camera profile")
    else:
        additions["INSTRUME"] = cam["instrume"][0]
        warnings.append("missing_camera_identity_supplied_by_profile")
    if "telescope" in obs:
        telescope = obs["telescope"]
        for src, key in [("aperture_mm", "APTDIA"), ("focal_length_mm", "FOCALLEN")]:
            if src in telescope and key in h:
                require(math.isclose(h[key], telescope[src], rel_tol=1e-6), "Telescope geometry conflict: " + key)
        observed = h.get("DATE-OBS", "")
        require(type(observed) is str and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?", observed), "Missing/invalid DATE-OBS for dated telescope name")
        additions["WENU PROV TELESCOPE"] = telescope["name_prefix"] + " " + datetime.fromisoformat(observed).date().isoformat()
        if not all(k in h for k in ("APTDIA", "FOCALLEN")):
            warnings.append("telescope_geometry_not_fully_reported")
    # Every directory component has meaning independent of its position in the path.
    role_aliases = {a.casefold(): ROLES[k] for k,v in layout["directories"].items() for a in v}
    dir_role = merge_roles(role_aliases[p.casefold()] for p in relative.parts[:-1] if p.casefold() in role_aliases)
    reported_role = merge_roles(header_role(h[k]) for k in ("FRAME", "IMAGETYP") if k in h)
    declared = merge_roles([r for r in (dir_role, header_role(h[DPR[0]]) if DPR[0] in h else "") if r])
    if declared.startswith("FLAT") and reported_role == "OBJECT":
        role = declared
        warnings.append("directory_flat_light_header_requires_acknowledgement")
    else:
        role = merge_roles([r for r in (declared, reported_role) if r])
    require(role, "Exposure role unknown: supply a role directory or a recognized header label")
    classification = dict(zip(DPR, (role, "SCIENCE" if role == "OBJECT" else "CALIB", "IMAGE")))
    additions.update(classification)
    # FILTER is header-first; directory aliases are cross-checks or missing-card proposals.
    aliases = {k.casefold(): v for k,v in layout.get("filters", {}).items()}
    bands = {aliases[p.casefold()] for p in relative.parts[:-1] if p.casefold() in aliases}
    require(len(bands) <= 1, "Contradictory filter directories")
    directory_filter = next(iter(bands)) if bands else ""
    require("FILTER" not in h or type(h["FILTER"]) is str, "Invalid FILTER card")
    recorded_filter = h.get("FILTER", "").strip()
    require("FILTER" not in h or recorded_filter, "Empty FILTER card needs review")
    effective_filter = aliases.get(recorded_filter.casefold(), recorded_filter)
    if directory_filter and recorded_filter:
        require(directory_filter == effective_filter, "Header/directory FILTER conflict")
    if not recorded_filter and directory_filter:
        effective_filter = directory_filter
        additions["FILTER"] = directory_filter
    elif not recorded_filter:
        warnings.append("filter_unknown")
    for key, value in additions.items():
        require(text(value) and len(fits.Card(key if len(key)<=8 else "HIERARCH "+key, value).image) <= 80,
                "Proposed FITS value too long/invalid: " + key)
        require(key not in h or type(h[key]) is str and h[key] == value, "Existing card conflicts: " + key)
    payload = h["NAXIS1"] * h["NAXIS2"] * abs(h["BITPIX"]) // 8
    require(before[2] == len(raw) + ((payload+2879)//2880)*2880, "Truncated/extra payload or additional HDU")
    require(stamp(path) == before, "Source changed during inspection")
    reported = {}
    for key in sorted(SELECTED | PROV):
        if key in h:
            value = h[key]
            reported[key] = value if type(value) in (str,int,bool) or number(value) else str(value)
    missing = [k for k in ("GAIN", "OFFSET", "CCD-TEMP", "EXPTIME", "XBINNING", "YBINNING") if k not in h]
    if not any(k in h for k in MODE_KEYS):
        missing.append("detector_mode")
    return {"file": relative.as_posix(), "source_stat": before, "header_sha256": sha(raw),
            "data_offset": len(raw), "classification": classification, "additions": additions,
            "filter": effective_filter, "warnings": warnings, "missing_metadata": missing,
            "reported": reported, "header_cards": [raw[i:i+80].decode("ascii") for i in range(0,end,80)],
            "checksum_cards_removed_in_copy": [k for k in ("CHECKSUM", "DATASUM") if k in h]}


def inventory(root, bundle):
    # Reuse the already qualified bounded file scanner and its nonregular-input checks.
    import prepare_zwo_asi as legacy
    result = legacy.inventory(root, bundle, inspector=inspect)
    result["notation"] = VERSION
    result["summary"] = {
        "roles": dict(collections.Counter(r["classification"][DPR[0]] for r in result["entries"])),
        "filters": dict(collections.Counter(r["filter"] or "<unknown>" for r in result["entries"])),
        "settings": {k: dict(collections.Counter(str(r["reported"].get(k,"<unknown>")) for r in result["entries"]))
                     for k in ("EXPTIME","GAIN","OFFSET","CCD-TEMP","XBINNING","YBINNING")}}
    return result


def apply_plan(plan_path, expected_sha, output, accept_flats, bundle):
    content = plan_path.read_bytes()
    require(sha(content) == expected_sha, "Reviewed dataset TOML SHA256 differs")
    plan = tomllib.loads(content.decode("utf-8"))
    require(plan.get("notation") == VERSION, "Unknown dataset TOML version")
    root = Path(plan["root"])
    require(inventory(root, bundle) == plan, "Inputs/header/configuration changed since reviewed plan")
    require(not plan["errors"], "Plan contains blocked inputs")
    require(accept_flats or not any("directory_flat_light_header_requires_acknowledgement" in r["warnings"] for r in plan["entries"]), "Flat-Light headers require --accept-directory-flats")
    require(outside(output,root) and outside(root,output), "Output must be separate from inputs")
    require(not output.exists() and not output.is_symlink(), "Output must be new")
    output.mkdir()
    marker = output/"PREPARATION_INCOMPLETE"
    marker.write_text("Do not admit this directory to the pipeline.\n")
    products = []
    for record in plan["entries"]:
        source = root/record["file"]
        require(inspect(source,root,bundle) == record, "Source changed before preparation")
        products.append(copy_prepared(source,output/record["file"],record,expected_sha,history="ZWO ASI prep plan "))
    require(inventory(root,bundle) == plan, "Source inventory changed during preparation")
    require(load_bundle(*(Path(bundle[k]["path"]) for k in ("observatory","camera","directories"))) == bundle,
            "Configuration changed during preparation")
    write_json(output/"preparation-manifest.json", {"notation":VERSION,"reviewed_plan_sha256":expected_sha,
               "accept_directory_flats":accept_flats,"plan":plan,"products":products})
    marker.rename(output/"PREPARATION_COMPLETE")
    print("PREPARED:",output,"| files:",len(products),"| payload bytes verified")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command",required=True)
    for action in ("plan","apply"):
        p=commands.add_parser(action)
        for name in ("observatory","camera","directories"):
            p.add_argument("--"+name,type=Path,required=True)
        if action=="plan":
            p.add_argument("--root",type=Path,required=True)
            p.add_argument("--report",type=Path,required=True,help="Generated dataset TOML")
        else:
            p.add_argument("--plan",type=Path,required=True)
            p.add_argument("--expected-plan-sha256",required=True)
            p.add_argument("--output",type=Path,required=True)
            p.add_argument("--accept-directory-flats",action="store_true")
    args=parser.parse_args(argv)
    try:
        bundle=load_bundle(args.observatory,args.camera,args.directories)
        if args.command=="plan":
            require(outside(args.report,args.root),"Report must be outside raw inputs")
            plan=inventory(args.root,bundle)
            with args.report.open("x",encoding="utf-8") as stream:
                stream.write(toml_text(plan))
            print("DATASET TOML:",args.report,"| SHA256:",sha(args.report.read_bytes()))
            print("CLASSIFICATIONS:",dict(collections.Counter(r["classification"][DPR[0]] for r in plan["entries"])),"| BLOCKED:",len(plan["errors"]))
            print("DISCOVERED SETTINGS:",json.dumps(plan["summary"]["settings"],sort_keys=True))
            print("WARNINGS:",dict(collections.Counter(w for r in plan["entries"] for w in r["warnings"])))
            for error in plan["errors"]:
                print("BLOCKED:",json.dumps(error))
            return 2 if plan["errors"] else 0
        apply_plan(args.plan,args.expected_plan_sha256,args.output,args.accept_directory_flats,bundle)
        return 0
    except (OSError,ValueError,KeyError,TypeError,fits.verify.VerifyError) as exc:
        print("STOP:",exc,file=sys.stderr)
        return 2
