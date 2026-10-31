"""Prepare first; execute only the reviewed plan. Synthetic native pipeline timing."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import statistics
import subprocess
import sys
import threading
import time
import warnings

from astropy.io import fits


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def identity(path):
    info = path.stat()
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mode": info.st_mode, "mtime_ns": info.st_mtime_ns}


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2); stream.write("\n")


def prepare(args):
    run = args.run.resolve(strict=True)
    qualified_files = {}
    if args.reference_run or args.candidate_run:
        require(all((args.reference_run, args.candidate_run, args.repository)), "Both qualified runs and repository required")
        caches = []
        for role, revision in (("reference", "2d662b148db56b0292ca6ec3ee9bceb1bc463595"),
                               ("candidate", "5e6bd83beafa744cd2a3be64b5405083c3ae634b")):
            prior = getattr(args, role + "_run").resolve(strict=True)
            report_path = prior / "qualification.json"
            report = json.loads(report_path.read_text())
            require(report["revision"] == revision and report["status"] == "passed" and
                    all(report["preservation"].values()), "Unexpected qualified source/status")
            require(report["host"] == platform.node().split(".")[0], "Different qualification host")
            setattr(args, role, prior / "build-c90/mefpp2/mefpp")
            if role == "candidate":
                args.source_root = prior / "source"
            cache = prior / "build-c90/CMakeCache.txt"
            values = {}
            for line in cache.read_text().splitlines():
                if line and not line.startswith(("#", "//")) and "=" in line and ":" in line.split("=", 1)[0]:
                    key, value = line.split("=", 1); values[key.split(":", 1)[0]] = value
            caches.append(values)
            for path in (report_path, cache):
                qualified_files[str(path)] = identity(path)
        for key in ("CMAKE_BUILD_TYPE", "CMAKE_C_COMPILER", "CMAKE_C_FLAGS", "CMAKE_C_FLAGS_RELEASE",
                    "CMAKE_EXE_LINKER_FLAGS", "CMAKE_AR", "CMAKE_RANLIB", "CMAKE_MAKE_PROGRAM",
                    "CMAKE_OSX_ARCHITECTURES", "CMAKE_OSX_SYSROOT", "MEFPP_C_STANDARD"):
            require(caches[0].get(key) == caches[1].get(key), "Unmatched build setting: " + key)
        require(caches[0]["CMAKE_BUILD_TYPE"] == "Release" and caches[0]["MEFPP_C_STANDARD"] == "90" and
                caches[0]["CMAKE_C_FLAGS_RELEASE"] == "-O2 -DNDEBUG", "Expected optimized serial C90 builds")
        # Old qualified normal-engine sources equal accepted main; opt-in M4 code is not linked there.
        native = ["mefpp2/qfits5", "mefpp2/src", "mefpp2/ins/mef/recipes/mefpp.c"]
        native += ["mefpp2/ins/mef/common/" + name + suffix
                   for name in ("mefp_lib", "mef_bias_kernel", "mef_paths") for suffix in (".c", ".h")]
        subprocess.run(["/usr/bin/git", "-C", str(args.repository), "diff", "--exit-code",
                        "c4a5ba491b087e7e690ef6e53ed5ff2a250dd3ca",
                        "2d662b148db56b0292ca6ec3ee9bceb1bc463595", "--", *native], check=True)
    source = args.source_root.resolve(strict=True)
    require(not any(run.iterdir()), "Plan directory must be fresh/empty")
    require(not run.is_relative_to(source) and not source.is_relative_to(run), "Keep plan outside source")
    sys.path.insert(0, str(source / "mefpp2/tests"))
    from prepare_integrated_campaign_fixture import prepare as fixture
    plan = {"notation": "native-performance-plan-1", "run": str(run), "source_root": str(source),
            "script_sha256": identity(Path(__file__))["sha256"], "executables": {}, "inputs": {}, "runs": [],
            "host": platform.node(), "scope": "tiny synthetic legacy/explicit native pipeline; shared qfits change",
            "qualified_pair": bool(qualified_files), "qualification_inputs": qualified_files,
            "limits": ["not representative full-size image throughput", "does not time opt-in layout adapters",
                       "no automatic performance acceptance", "no observations/install/cache flush"]}
    for role in ("reference", "candidate"):
        exe = getattr(args, role).resolve(strict=True)
        require(exe.is_file() and os.access(exe, os.X_OK), "Expected private executable")
        plan["executables"][role] = {"path": str(exe), "identity": identity(exe)}
    require(plan["executables"]["reference"]["path"] != plan["executables"]["candidate"]["path"], "Different builds required")
    for instrument in ("omegacam", "wfi"):
        root = run / instrument; root.mkdir(); raw = root / "synthetic-inputs"
        # Same frozen fixture factory/PAF overrides as native_paths_contract.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", fits.verify.VerifyWarning)
            value = fixture(raw, source)
        if instrument == "wfi":
            text = (source / "mefpp2/ins/mef/config/wfi.paf").read_text()
            for key, setting in value["synthetic_paf_overrides"].items():
                text, count = re.subn(r"^" + re.escape(key) + r"\s+[^;\n]*;", key + " " + str(setting) + ";", text, flags=re.M)
                require(count == 1, "Unexpected PAF override")
            (raw / "mefpp.paf").write_text(text)
            for path in raw.glob("*.fits"):
                with fits.open(path, mode="update") as hdus:
                    hdus[0].header["INSTRUME"] = "WFI"
        for path in raw.iterdir():
            if path.is_file():
                path.chmod(0o444); plan["inputs"][str(path)] = identity(path)
        raw.chmod(0o555)
        caller = root / "caller"; caller.mkdir(); caller.chmod(0o555)
        sequence = [("warmup", 0, "reference"), ("warmup", 0, "candidate")]
        for pair in range(1, 4):
            roles = ("reference", "candidate") if pair % 2 else ("candidate", "reference")
            sequence += [("measured", pair, role) for role in roles]
        for phase, pair, role in sequence:
            label = f"{instrument}-{phase}-{pair}-{role}"
            out = run / (label + "-output"); scratch = run / (label + "-scratch")
            out.mkdir(); scratch.mkdir()
            argv = [plan["executables"][role]["path"], "--pafname", str(raw / "mefpp.paf"),
                    "--output-dir", str(out), "--work-dir", str(scratch), "--list-base", str(raw)]
            argv += ["--bias", str(raw / "bias.list"), "--biassave", "--biassub", "--bpm", str(raw / "bpm.list"),
                     "--dome", str(raw / "dome.list"), "--domesave", "--sky", str(raw / "sky.list"), "--skysave",
                     "--science", str(raw / "science.list")]
            plan["runs"].append({"label": label, "instrument": instrument, "phase": phase, "pair": pair,
                                 "role": role, "argv": argv, "cwd": str(caller), "output": str(out), "scratch": str(scratch)})
    plan["source_inputs"] = {str(source / name): identity(source / name) for name in (
        "mefpp2/tests/prepare_integrated_campaign_fixture.py", "mefpp2/tests/native_paths_contract.py")}
    save(run / "plan.json", plan)
    print("PLAN:", run / "plan.json")
    print("PREPARED ONLY: 16 native launches planned; none executed")
    print("PLAN SHA256:", identity(run / "plan.json")["sha256"])
    for item in plan["runs"]:
        print(item["label"])


def execute(path):
    plan = json.loads(path.read_text()); run = Path(plan["run"])
    require(plan["notation"] == "native-performance-plan-1", "Unknown plan")
    require(plan["host"] == platform.node(), "Use the prepared host")
    require(plan.get("qualified_pair", False), "Execution requires matched qualified builds; preparation-only examples cannot execute")
    require(plan["script_sha256"] == identity(Path(__file__))["sha256"], "Measurement script changed")
    require(not (run / "results.json").exists() and not (run / "attempt.json").exists(), "Plan already attempted; retain evidence")
    require(os.getpriority(os.PRIO_PROCESS, 0) >= 10, "Require niceness >=10")
    def preserved():
        return (all(identity(Path(p)) == value for p, value in {**plan["inputs"], **plan["source_inputs"],
                                                             **plan["qualification_inputs"]}.items()) and
                all(identity(Path(v["path"])) == v["identity"] for v in plan["executables"].values()))
    require(preserved(), "Prepared inputs/source/executable changed")
    save(run / "attempt.json", {"plan_sha256": identity(path)["sha256"], "started": True})
    sys.path.insert(0, str(Path(plan["source_root"]) / "mefpp2/tests"))
    from native_paths_contract import products
    receipt = {"status": "running", "plan_sha256": identity(path)["sha256"], "runs": [],
               "performance_acceptance": "not automatic; inspect paired differences and resource use"}
    reference = {}; finished = False
    try:
        for item in plan["runs"]:
            require(not any(Path(item["output"]).iterdir()) and not any(Path(item["scratch"]).iterdir()), "Attempt directory is not empty")
            entry = dict(item, load_before=os.getloadavg()); receipt["runs"].append(entry)
            env = dict(os.environ, E_VERBOSE="0", E_DEBUG="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
            env.pop("E_LOGFILE", None)
            timed_out = threading.Event()
            with (run / (item["label"] + ".log")).open("x") as log:
                start = time.perf_counter()
                process = subprocess.Popen(item["argv"], cwd=item["cwd"], env=env,
                                           stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                def stop():
                    try:
                        os.killpg(process.pid, signal.SIGKILL); timed_out.set()
                    except ProcessLookupError:
                        pass
                timer = threading.Timer(120, stop); timer.start()
                try:
                    _, status, usage = os.wait4(process.pid, 0)
                    process.returncode = os.waitstatus_to_exitcode(status)
                except BaseException:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    _, status, _ = os.wait4(process.pid, 0)
                    process.returncode = os.waitstatus_to_exitcode(status)
                    raise
                finally:
                    timer.cancel(); timer.join()
                entry.update(wall_s=time.perf_counter() - start, exit=process.returncode,
                             user_s=usage.ru_utime, system_s=usage.ru_stime,
                             peak_rss_bytes=usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024),
                             input_blocks=usage.ru_inblock, output_blocks=usage.ru_oublock,
                             timed_out=timed_out.is_set(), load_after=os.getloadavg())
            require(process.returncode == 0 and not timed_out.is_set(), "Native attempt failed; do not replay unchanged")
            # Product checks occur outside native timing; retain their separate cost.
            start = time.perf_counter(); value = products(Path(item["output"]))
            require(len(value) == 6, "Expected all six native products")
            if item["phase"] == "warmup" and item["role"] == "reference":
                reference[item["instrument"]] = value
            else:
                require(value == reference[item["instrument"]], "Pixel/metadata mismatch; reject timing comparison")
            entry["validation_wall_s"] = time.perf_counter() - start
            entry["retained_bytes"] = sum(p.stat().st_size for base in ("output", "scratch") for p in Path(item[base]).rglob("*") if p.is_file())
        receipt["paired_summary"] = {}
        for instrument in ("omegacam", "wfi"):
            pairs = []
            for pair in range(1, 4):
                rows = {r["role"]: r for r in receipt["runs"]
                        if r["instrument"] == instrument and r["phase"] == "measured" and r["pair"] == pair}
                ref, cand = rows["reference"], rows["candidate"]
                ref_cpu = ref["user_s"] + ref["system_s"]
                pairs.append({"pair": pair, "wall_ratio": cand["wall_s"] / ref["wall_s"],
                              "cpu_ratio": (cand["user_s"] + cand["system_s"]) / ref_cpu if ref_cpu else None,
                              "rss_difference_bytes": cand["peak_rss_bytes"] - ref["peak_rss_bytes"],
                              "input_blocks_difference": cand["input_blocks"] - ref["input_blocks"],
                              "output_blocks_difference": cand["output_blocks"] - ref["output_blocks"],
                              "retained_bytes_difference": cand["retained_bytes"] - ref["retained_bytes"]})
            ratios = [p["wall_ratio"] for p in pairs]
            receipt["paired_summary"][instrument] = {"pairs": pairs,
                "wall_ratio_median": statistics.median(ratios), "wall_ratio_range": [min(ratios), max(ratios)],
                "interpretation": "review raw pairs/resources; overlap or host noise may be inconclusive"}
        finished = True
    except BaseException as error:
        receipt["error"] = repr(error)
        raise
    finally:
        receipt["inputs_source_executables_preserved"] = preserved()
        receipt["status"] = "completed-awaiting-performance-review" if finished and preserved() else "failed"
        save(run / "results.json", receipt)
        print("RESULT:", receipt["status"], "| EVIDENCE:", run)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-plan", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--reference-run", type=Path)
    parser.add_argument("--candidate-run", type=Path)
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--run", type=Path)
    args = parser.parse_args()
    if args.execute_plan:
        execute(args.execute_plan.resolve(strict=True))
    else:
        require(args.run and ((args.reference_run and args.candidate_run and args.repository) or
                             all((args.reference, args.candidate, args.source_root))), "Preparation paths required")
        prepare(args)


if __name__ == "__main__":
    main()
