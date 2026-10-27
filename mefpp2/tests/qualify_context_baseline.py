"""Record S2-02 context cleanup baseline; findings fail the memory gate."""
import argparse
import configparser
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import platform
from qualify_mac_leaks import digest, save, accounting


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--cmake", type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != "Darwin" or platform.node().split(".")[0] != "MC02VV0HPHTDG":
        raise RuntimeError("STOP: run on the qualified Intel Mac")
    if Path(sys.prefix).resolve() != Path("/Users/fselman/anaconda3"):
        raise RuntimeError("STOP: unexpected Python environment")
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError("STOP: launch this batch with nice -n 10")
    repo = Path(__file__).resolve().parents[2]

    def git(*argv):
        return subprocess.check_output(["git", *argv], cwd=repo, text=True).strip()

    if git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("STOP: checkout must be clean")
    identity = dict(repository="https://github.com/fselman/wenu-imaging",
                    branch=git("symbolic-ref", "--short", "HEAD"),
                    commit=git("rev-parse", "HEAD"), dirty=False)
    compiler, sdk, cmake = [p.resolve(strict=True) for p in
                            (args.compiler, args.sdk, args.cmake)]
    config = Path(os.environ.get("PYCAVI_ASTROSOFT_CONFIG",
                                "~/.pycavi/pycavi_astrosoft.cfg")).expanduser().resolve(strict=True)
    settings = configparser.ConfigParser(interpolation=None)
    settings.read(config)
    engine = Path(settings["Paths"]["mefpp"].strip().strip('"')).expanduser()
    if not engine.is_absolute():
        engine = Path(shutil.which(str(engine)) or str(engine))
    engine = engine.resolve(strict=True)
    protected = {str(p): digest(p) for p in (config, engine)}
    relevant = ["mefpp2/ins/mef/common/mefp_lib.c", "mefpp2/ins/mef/common/mefp_lib.h",
                "mefpp2/qfits5/src/xmemory.c", "mefpp2/qfits5/include/xmemory.h",
                "mefpp2/ins/mef/config/omegacam.paf", "mefpp2/ins/mef/config/wfi.paf",
                "mefpp2/tests/context_ownership_probe.c", "mefpp2/tests/qualify_mac_leaks.py"]
    source_hashes = {p: digest(repo / p) for p in relevant}
    root = Path.home() / "Software/build/wenu-imaging"
    if not root.is_dir():
        raise RuntimeError("STOP: expected imaging build root is absent")
    work = Path(tempfile.mkdtemp(prefix="mac-stage2-context-baseline-", dir=root))
    provenance = work / "run-provenance.json"
    record = dict(schema_version=1, project="wenu-imaging", tested_source=identity,
                  host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
                  purpose="S2-02 unchanged context construction/destruction and rejection baseline",
                  status="running", execution_complete=False,
                  retention_roles=["acceptance_evidence"], commands=[], cases=[],
                  source_sha256=source_hashes, protected_sha256=protected,
                  installation_performed=False, observational_processing_performed=False,
                  limits=["Context/PAF only: no mef_engine, image reduction or Pycavi",
                          "No allocator failure injection; no full repeated-stage gate",
                          "Mac RAM diagnostic/accounting lanes; target verification pending",
                          "No correction of issue 99 applied"])
    save(provenance, record)
    print("WORK DIRECTORY:", work, flush=True)
    children = []

    def directory(name, purpose):
        path = work / name
        path.mkdir()
        child = path / "run-provenance.json"
        save(child, dict(schema_version=1, project="wenu-imaging", tested_source=identity,
                         parent_manifest=str(provenance), purpose=purpose, status="running",
                         retention_roles=["acceptance_evidence"]))
        children.append(child)
        return path

    def run(label, argv, cwd, env=None):
        log = work / (label + ".log")
        item = dict(label=label, argv=list(map(str, argv)), cwd=str(cwd), log=str(log))
        record["commands"].append(item)
        save(provenance, record)
        print("Running:", label, flush=True)
        with log.open("w") as stream:
            result = subprocess.run(item["argv"], cwd=cwd, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=600)
        item.update(exit_status=result.returncode, log_sha256=digest(log))
        save(provenance, record)
        return result.returncode, log

    try:
        source = directory("source", "Exported source with diagnostic target wiring only")
        archive = subprocess.check_output(["git", "archive", identity["commit"], "mefpp2"], cwd=repo)
        record["source_archive_sha256"] = hashlib.sha256(archive).hexdigest()
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(source)
        wiring = source / "mefpp2/CMakeLists.txt"
        wiring.write_text(wiring.read_text() +
            "\n# S2-02: production constructor/destructor unchanged.\n"
            "add_executable(context_ownership_probe tests/context_ownership_probe.c)\n"
            "target_link_libraries(context_ownership_probe PRIVATE mefpp_common)\n")
        record["diagnostic_cmake_sha256"] = digest(wiring)
        clean_env = os.environ.copy()
        removed = ["ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS", "DYLD_INSERT_LIBRARIES",
                   "DYLD_LIBRARY_PATH", "MallocStackLogging", "MallocScribble",
                   "MallocStackLoggingNoCompact"]
        for key in removed:
            clean_env.pop(key, None)
        clean_env.update(E_VERBOSE="0", E_DEBUG="0")
        record["removed_child_environment"] = removed
        record["lane_environment"] = {
            "instrumented": {"ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86",
                             "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=0"},
            "leaks": {"MallocStackLogging": "lite", "MallocScribble": "1"}}
        save(provenance, record)
        kinds = [("valid-1", None, None, 1),
                 ("valid-3", None, None, 3),
                 ("missing-count", "MEF.NCHIPS", None, 1),
                 ("missing-geometry", "MEF.CROP.Y.MAX.CHIP2", None, 1),
                 ("missing-final", "MEF.SATMAX", None, 1),
                 ("invalid-count", "MEF.NCHIPS", "junk", 1)]
        for mode in (90, 17):
            for lane in ("instrumented", "leaks"):
                tag = "c%d-%s" % (mode, lane)
                build = directory("build-" + tag, "C%d %s context diagnostic build" % (mode, lane))
                flags = "-O0 -g -fno-omit-frame-pointer"
                link_flags = ""
                if lane == "instrumented":
                    flags += " -fsanitize=address,undefined -fno-sanitize-recover=all"
                    link_flags = "-fsanitize=address,undefined"
                command = [cmake, "-S", source / "mefpp2", "-B", build, "-G", "Unix Makefiles",
                           "-DCMAKE_C_COMPILER=" + str(compiler), "-DCMAKE_OSX_SYSROOT=" + str(sdk),
                           "-DCMAKE_OSX_ARCHITECTURES=x86_64", "-DCMAKE_BUILD_TYPE=Debug",
                           "-DMEFPP_C_STANDARD=" + str(mode), "-DBUILD_TESTING=OFF",
                           "-DMEFPP_BUILD_RESOURCES=OFF", "-DMEFPP_SOURCE_REVISION=" + identity["commit"],
                           "-DCMAKE_C_FLAGS=" + flags, "-DCMAKE_EXE_LINKER_FLAGS=" + link_flags]
                code, log = run("configure-" + tag, command, work, clean_env)
                if code:
                    raise RuntimeError("Configuration failed; see " + str(log))
                code, log = run("build-" + tag, [cmake, "--build", build, "--target",
                                               "context_ownership_probe", "--parallel", "2"], work, clean_env)
                if code:
                    raise RuntimeError("Build failed; see " + str(log))
                info = json.loads((build / "build-info.json").read_text())
                if info["qfits_memory_mode"] != 2 or info["qfits_max_pointers"] != 2000000:
                    raise RuntimeError("Unexpected allocator build policy")
                executable = build / "context_ownership_probe"
                if lane == "instrumented":
                    code, log = run("symbols-" + tag, ["/usr/bin/dsymutil", executable], work, clean_env)
                    if code:
                        raise RuntimeError("Symbol generation failed; see " + str(log))
                for instrument, chips in (("omegacam", 32), ("wfi", 8)):
                    original = (source / ("mefpp2/ins/mef/config/" + instrument + ".paf")).read_text()
                    for kind, key, replacement, repeats in kinds:
                        label = tag + "-" + instrument + "-" + kind
                        case = directory(label, "Independent constructor/rejection and cleanup observation")
                        text = original
                        if key is not None:
                            lines = original.splitlines()
                            matches = [i for i, line in enumerate(lines) if line.split() and line.split()[0] == key]
                            if len(matches) != 1:
                                raise RuntimeError("Unexpected PAF key identity: " + key)
                            index = matches[0]
                            if replacement is None:
                                del lines[index]
                            else:
                                lines[index] = key + " " + replacement + ";"
                            text = "\n".join(lines) + "\n"
                        paf = case / "context.paf"
                        paf.write_text(text)
                        input_hash = digest(paf)
                        expected_chips = chips if key is None else 0
                        command = [executable, paf.name, str(expected_chips), str(repeats)]
                        if lane == "leaks":
                            command = ["/usr/bin/leaks", "-quiet", "-atExit", "--"] + command
                        env = dict(clean_env, **record["lane_environment"][lane])
                        code, log = run(label, command, case, env)
                        output = log.read_text(errors="replace")
                        result = dict(case=label, lane=lane, instrument=instrument, variant=kind,
                                      repeats=repeats, exit_status=code, input_sha256=input_hash,
                                      executable_sha256=digest(executable), log_sha256=digest(log),
                                      status="failed", findings=[])
                        try:
                            if output.count("CONTEXT COMPLETE repeats=" + str(repeats)) != 1:
                                raise RuntimeError("Native context completion missing")
                            native = re.findall(r"CONTEXT RESULT iteration=(\d+) created=(\d+) chips=(\d+)", output)
                            expected_rows = [(str(i), "1" if expected_chips else "0", str(expected_chips))
                                             for i in range(1, repeats + 1)]
                            if native != expected_rows:
                                raise RuntimeError("Context result contract mismatch")
                            result["context_contract"] = "passed"
                            result["configuration_lines"] = re.findall(r"^CONFIG .*", output, re.M)
                            before = accounting(output, "baseline")
                            states = [accounting(output, "after-" + str(i)) for i in range(1, repeats+1)]
                            after = accounting(output, "final")
                            result.update(baseline_accounting=before, after_calls=states, final_accounting=after)
                            if accounting(output, "process-start") != {"pointers": 0, "bytes": 0}:
                                result["findings"].append("nonzero process-start accounting")
                            if after != before or any(s != before for s in states):
                                result["findings"].append("outstanding or changing allocation ownership after destruction")
                            if lane == "instrumented":
                                if code != 0 or "ERROR: AddressSanitizer" in output or "runtime error:" in output:
                                    result["findings"].append("invalid-access or undefined-behavior diagnostic")
                            else:
                                summaries = re.findall(r"\b(\d+) leaks? for (\d+) total leaked bytes\b", output)
                                if len(summaries) != 1 or code not in (0, 1):
                                    raise RuntimeError("Unrecognized leaks execution")
                                blocks, size = map(int, summaries[0])
                                result.update(leaked_blocks=blocks, leaked_bytes=size)
                                if blocks or size or code:
                                    result["findings"].append("unreachable allocation reported by leaks")
                            if digest(paf) != input_hash:
                                raise RuntimeError("Staged input changed")
                            result["status"] = "failed" if result["findings"] else "passed"
                        except Exception as error:
                            result["findings"].append(str(error))
                        record["cases"].append(result)
                        save(case / "run-provenance.json", dict(result, schema_version=1, tested_source=identity,
                             parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                        save(provenance, record)
                        final = result.get("final_accounting", {})
                        print(("PASS:" if result["status"] == "passed" else "FINDING:"), label,
                              "final pointers=%s bytes=%s" % (final.get("pointers", "?"), final.get("bytes", "?")),
                              flush=True)
        record["execution_complete"] = True
        record["finding_cases"] = sum(c["status"] != "passed" for c in record["cases"])
        record["status"] = "failed" if record["finding_cases"] else "passed"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        record["sources_unchanged"] = all(digest(repo / p) == h for p, h in source_hashes.items())
        record["protected_files_unchanged"] = all(digest(Path(p)) == h for p, h in protected.items())
        record["checkout_unchanged"] = (git("rev-parse", "HEAD") == identity["commit"]
                                       and not git("status", "--porcelain", "--untracked-files=all"))
        if not all(record[k] for k in ("sources_unchanged", "protected_files_unchanged", "checkout_unchanged")):
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], completed_utc=record["completed_utc"])
                save(child, value)
    print("CONTEXT BASELINE: cases=%d; finding cases=%d; complete=%s" %
          (len(record["cases"]), record.get("finding_cases", 0), record["execution_complete"]))
    print("REPORT:", provenance)
    print("Memory gate:", record["status"])
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
