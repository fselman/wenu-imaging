"""WAD-governed data preflight service and ESO adapters; inspection only.

The record mapping is versioned and provisional, not an ASDF schema validator.
No input writes, FITS preparation copies, processing or association selection.
"""
import argparse
import configparser
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

if __package__:
    from .pycavi_paths import PathResolver
    from .pycavi_project import inspect_fits_headers, Limits
else:
    from pycavi_paths import PathResolver
    from pycavi_project import inspect_fits_headers, Limits

VERSION = "wad-data-preflight-1"
MAPPING = "eso-header-mapping-1"
COMMON = {"INSTRUME", "FILTER", "OBJECT", "EXPTIME", "DATE-OBS", "MJD-OBS", "TELESCOP",
          "ORIGIN", "EXTNAME", "EXTVER", "BITPIX", "BSCALE", "BZERO", "BUNIT",
          "ESO DPR TYPE", "ESO DPR CATG", "ESO DPR TECH", "ESO DET CHIP ID",
          "ESO DET OUT1 CONAD", "ESO DET OUT1 RON", "GAIN"}
CONFIGS = {"OMEGACAM": "omegacam.cfg", "WFI": "wfi.cfg"}


def _keyword(value):
    return value.strip().strip('"').removeprefix("HIERARCH ")


def load_eso_adapter(instrument, config_root=None):
    """Reuse the actual instrument mappings; never derive detector IDs from HDU order."""
    if instrument not in CONFIGS:
        raise ValueError("Unsupported ESO instrument: " + str(instrument))
    root = Path(config_root) if config_root is not None else Path(__file__).parent/"config"
    path = root/CONFIGS[instrument]
    raw = path.read_bytes()
    parser = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=("#",))
    parser.read_string(raw.decode("utf-8"))
    primary = parser["Primary Keywords"]
    fields = {name: _keyword(primary[key]) for name,key in {
        "instrument":"inst_name_key", "filter":"filt_key", "target":"object_key",
        "exposure_s":"inst_exp_key", "date_obs":"dateobs_key", "read_mode":"det_readmode_key",
        "bin_x":"det_binx_key", "bin_y":"det_biny_key", "dpr_type":"dpr_type_key",
        "dpr_category":"dpr_catg_key"}.items()}
    roles = {}
    for prefix, role in [("bias","bias"),("domeff","dome_flat"),("skyff","sky_flat"),
                         ("std","standard"),("sci","science")]:
        cat = primary.get(prefix+"_dpr_catg_val", "").strip().strip('"')
        values = primary.get(prefix+"_dpr_type_val", "")
        for value in next(csv.reader([values],skipinitialspace=True)):
            if value: roles[(cat,value)] = role
    detectors = {}
    for key,value in parser["Extension Keywords"].items():
        if re.fullmatch(r"ext_\d+_name", key):
            name = value.strip().strip('"')
            if name in detectors: raise ValueError("Duplicate configured detector identity")
            gain_key = parser["Extension Keywords"].get(key[:-4]+"gain_key", "")
            detectors[name] = _keyword(gain_key) if gain_key else "ESO DET OUT1 CONAD"
    return {"instrument":instrument, "fields":fields, "roles":roles, "detectors":detectors,
            "config":{"path":str(path.resolve()),"sha256":hashlib.sha256(raw).hexdigest()},
            "mapping_version":MAPPING}


def preflight_files(paths, *, invocation_base, instrument=None, limits=Limits(), config_root=None):
    """Assess explicit FITS assets with a shared reader; do not rewrite correct ESO headers.

    Each effective attribute carries its exact header/config source. A passed
    metadata assessment is not calibration, numerical or product acceptance.
    """
    if instrument is not None and instrument not in CONFIGS:
        raise ValueError("Supported adapters: OMEGACAM, WFI")
    paths = list(paths)
    if not paths or len(paths) > limits.files:
        raise ValueError("Supply a nonempty bounded input file list")
    resolver = PathResolver(Path(invocation_base))
    adapters = {name:load_eso_adapter(name,config_root) for name in CONFIGS}
    selected_keys = COMMON | {key for a in adapters.values() for key in a["fields"].values()} | {
        key for a in adapters.values() for key in a["detectors"].values()}
    observations = []
    seen = set()
    for declared in paths:
        path = resolver.argument(declared)
        record = {"path":str(path),"declared":str(declared),"attributes":{},"images":[],
                  "diagnostics":[],"unknown":[],"proposed_additions":{},"preparation_required":None,
                  "readiness":{"scope":"metadata-ingestion","profile":"raw-imaging","status":"blocked",
                               "calibration":"not-assessed","scientific":"not-assessed",
                               "payload_integrity":"not-checked"}}
        observations.append(record)
        def diagnostic(code,message,severity="error",hdu=None):
            d={"code":code,"message":message,"severity":severity}
            if hdu is not None:d["hdu"]=hdu
            record["diagnostics"].append(d)
        if path in seen:
            diagnostic("duplicate_input","Input resolves to an already selected asset")
            continue
        seen.add(path)
        try:
            before = path.stat()
            identity = [before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_mode]
            result = inspect_fits_headers(path,invocation_base=resolver.invocation_base,
                                          keys=tuple(sorted(selected_keys)),limits=limits)
            asset = result["asset"]
            record["original"] = asset
            for d in result["diagnostics"]:
                diagnostic(d["code"],d["message"],"warning" if d["code"]=="fits_warning" else "error")
            if not asset or not asset["hdus"]:
                diagnostic("unreadable_headers","No readable HDU headers")
                continue
            def values(hdu):
                out={}
                for card in hdu["cards"]:
                    out.setdefault(card["key"],[]).append(card["value"])
                return out
            header_values = [values(h) for h in asset["hdus"]]
            def single(index,key):
                members=header_values[index].get(key,[])
                if len(members)>1:
                    diagnostic("duplicate_metadata",key,hdu=index)
                    return None
                return members[0] if members else None
            reported_instrument=single(0,"INSTRUME")
            adapter=adapters.get(instrument or reported_instrument)
            if adapter is None:
                diagnostic("unsupported_instrument",str(reported_instrument))
                continue
            record["adapter"]={"instrument":adapter["instrument"],"mapping_version":MAPPING,
                               "config":adapter["config"]}
            if reported_instrument != adapter["instrument"]:
                diagnostic("instrument_conflict","INSTRUME differs from selected adapter")
            def attribute(name,key,unit=None,required=False,fallback=None):
                value=single(0,key); source_key=key
                if value is None and fallback:
                    value=single(0,fallback);source_key=fallback
                if value is None:
                    record["unknown"].append(name)
                    diagnostic("missing_metadata",name,"error" if required else "warning")
                    return None
                record["attributes"][name]={"value":value,"authority":"reported-unverified",
                    "source":{"hdu":0,"keyword":source_key,"mapping_version":MAPPING}}
                if unit:record["attributes"][name]["unit"]=unit
                return value
            for name,key in adapter["fields"].items():
                attribute(name,key,unit="s" if name=="exposure_s" else None,
                          required=name in ("instrument","exposure_s","dpr_type","dpr_category"),
                          fallback="FILTER" if name=="filter" else None)
            attribute("dpr_technique","ESO DPR TECH",required=True)
            attribute("telescope","TELESCOP")
            attribute("origin","ORIGIN")
            exp=record["attributes"].get("exposure_s",{}).get("value")
            if type(exp) not in (int,float) or not math.isfinite(exp) or exp < 0:
                diagnostic("invalid_exposure","Exposure must be finite, numeric and nonnegative")
            for name in ("instrument","filter","dpr_type","dpr_category","dpr_technique"):
                value=record["attributes"].get(name,{}).get("value")
                if value is not None and (type(value) is not str or not value.strip()):
                    diagnostic("invalid_metadata",name+" must be nonempty text")
            for name in ("bin_x","bin_y"):
                v=record["attributes"].get(name,{}).get("value")
                if v is not None and (type(v) is not int or v<1):diagnostic("invalid_binning",name)
            filt=record["attributes"].get("filter",{}).get("value")
            generic=single(0,"FILTER")
            if generic is not None and filt is not None and generic != filt:
                diagnostic("filter_conflict","Generic FILTER and instrument filter disagree")
            cat=single(0,adapter["fields"]["dpr_category"])
            typ=single(0,adapter["fields"]["dpr_type"])
            role=adapter["roles"].get((cat,typ)) if type(cat) is str and type(typ) is str else None
            if role in ("science","dome_flat","sky_flat","standard") and filt is None:
                diagnostic("missing_filter","Selected exposure role requires filter metadata")
            technique=record["attributes"].get("dpr_technique",{}).get("value")
            if type(technique) is str and technique.split(",")[0] != "IMAGE":
                diagnostic("unsupported_technique","Adapter supports imaging observations")
            if role:
                record["attributes"]["exposure_role"]={"value":role,"authority":"configured-mapping",
                    "source":{"keywords":[adapter["fields"]["dpr_category"],adapter["fields"]["dpr_type"]],
                              "configuration_sha256":adapter["config"]["sha256"],"mapping_version":MAPPING}}
            else:
                record["unknown"].append("exposure_role")
                diagnostic("unmapped_role","DPR combination has no existing reduction-role mapping","warning")
            ids=set()
            for index,hdu in enumerate(asset["hdus"]):
                dims=hdu["dimensions"]
                if not dims:continue
                if hdu["hdu_type"] not in ("PrimaryHDU","ImageHDU"):
                    diagnostic("nonimage_hdu","Nonimage HDU retained but not mapped","warning",index)
                    continue
                if len(dims)!=2 or any(type(v) is not int or v<=0 for v in dims):
                    diagnostic("invalid_geometry","Expected positive 2D image",hdu=index)
                name=single(index,"EXTNAME")
                if not name or type(name) is not str:
                    diagnostic("missing_detector_identity","Image needs an explicit detector identity",hdu=index)
                elif name in ids:
                    diagnostic("duplicate_detector_identity",name,hdu=index)
                else:ids.add(name)
                if name not in adapter["detectors"]:
                    diagnostic("unknown_detector_identity",str(name),hdu=index)
                bitpix=single(index,"BITPIX")
                if type(bitpix) is not int or bitpix not in (8,16,32,64,-32,-64):
                    diagnostic("invalid_bitpix","Unsupported FITS encoding",hdu=index)
                for key in ("BSCALE","BZERO"):
                    v=single(index,key)
                    if v is not None and (type(v) not in (int,float) or not math.isfinite(v) or key=="BSCALE" and v==0):
                        diagnostic("invalid_scaling",key,hdu=index)
                # Exposure-level metadata may be repeated, but cannot contradict the primary.
                for key in {"INSTRUME","FILTER",*adapter["fields"].values(),"ESO DPR TECH"}:
                    local=single(index,key);primary=single(0,key)
                    if index and local is not None and primary is not None and local!=primary:
                        diagnostic("primary_extension_conflict",key,hdu=index)
                # Cross-keyword filter agreement is required as well as repeated-card agreement.
                for key in {"FILTER",adapter["fields"]["filter"]}:
                    local=single(index,key)
                    if index and local is not None and filt is not None and local!=filt:
                        diagnostic("extension_filter_conflict",key,hdu=index)
                gain_key=adapter["detectors"].get(name,"ESO DET OUT1 CONAD")
                gain=single(index,gain_key)
                if gain is None:
                    diagnostic("unknown_detector_gain",str(name),"warning",index)
                elif type(gain) not in (int,float) or not math.isfinite(gain) or gain<=0:
                    diagnostic("invalid_detector_gain",gain_key,hdu=index)
                record["images"].append({"detector_id":name,"hdu":hdu["hdu"],"shape":list(reversed(dims)),
                    "bitpix":bitpix,"gain":{"value":gain,"unit":"electron/adu","source_keyword":gain_key,
                    "authority":"reported-unverified"},"unit":single(index,"BUNIT"),
                    "selector_source":"EXTNAME","source_hdu":hdu["hdu"]})
            if not record["images"]:diagnostic("no_image_planes","No image detectors found")
            absent=set(adapter["detectors"])-ids
            if absent:diagnostic("partial_detector_coverage",", ".join(sorted(absent)),"warning")
            after=path.stat()
            current=[after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_mode]
            if current!=identity:diagnostic("source_changed","Source identity changed during preflight")
            record["identity"]={"stat":identity,"verification":"header/stat only; pixel hash not computed"}
        except (OSError,ValueError,TypeError) as exc:
            diagnostic("input_error",str(exc))
        blocked=any(d["severity"]=="error" for d in record["diagnostics"])
        record["readiness"]["status"]="blocked" if blocked else ("passed-with-warnings" if record["diagnostics"] else "passed")
        record["preparation_required"] = None if blocked else False
    return {"notation":VERSION,"mapping_version":MAPPING,"stage":"data_preflight",
            "wad_schema_conformance":"not-claimed","observations":observations,
            "summary":{"assets":len(observations),"blocked":sum(r["readiness"]["status"]=="blocked" for r in observations)},
            "writes_to_inputs":False,"preparation_executed":False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files",nargs="+",type=Path)
    parser.add_argument("--instrument",choices=sorted(CONFIGS))
    parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        paths=[p.resolve() for p in args.files]
        output=args.report.resolve()
        if (output in paths or output.exists() or args.report.is_symlink()
                or any(output.is_relative_to(p.parent) for p in paths)):
            raise ValueError("Report must be new and outside raw input directories")
        report=preflight_files(args.files,invocation_base=Path.cwd(),instrument=args.instrument)
        with output.open("x") as f:json.dump(report,f,indent=2,allow_nan=False);f.write("\n")
        print(json.dumps(report["summary"],sort_keys=True));print("REPORT:",output)
        return 2 if report["summary"]["blocked"] else 0
    except (OSError,ValueError,TypeError) as exc:
        print("STOP:",exc,file=sys.stderr);return 2


if __name__=="__main__":sys.exit(main())
