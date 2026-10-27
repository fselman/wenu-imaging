"""Chapman3 S2-04 split/cache functional and qfits-accounting checks (#75).

Unchanged Mac-qualified native driver/fixtures; no target external-tool claim.
"""
import argparse
import configparser
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import subprocess
import sys
import tarfile
import tempfile
from qualify_mac_leaks import digest, save
from split_ownership_cases import cases, prepare, input_hashes, verify, restrict_output


from qualify_split_ownership import allocation_state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--cmake", type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != "Linux" or platform.node().split(".")[0] != "chapman3":
        raise RuntimeError("STOP: run on Chapman3")
    if Path(sys.prefix).resolve() != (Path.home() / ".conda/envs/wenu-imaging").resolve():
        raise RuntimeError("STOP: unexpected Python environment")
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError("STOP: launch with nice -n 10")
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    repo = Path(__file__).resolve().parents[2]

    def git(*argv):
        return subprocess.check_output(["git", *argv], cwd=repo, text=True).strip()

    if git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("STOP: checkout must be clean")
    identity = dict(repository="https://github.com/fselman/wenu-imaging",
                    branch=git("symbolic-ref", "--short", "HEAD"),
                    commit=git("rev-parse", "HEAD"), dirty=False)
    compiler, cmake = [p.resolve(strict=True) for p in (args.compiler, args.cmake)]
    config = Path(os.environ.get("PYCAVI_ASTROSOFT_CONFIG",
                                "~/.pycavi/pycavi_astrosoft.cfg")).expanduser().resolve(strict=True)
    settings = configparser.ConfigParser(interpolation=None)
    settings.read(config)
    engine = Path(settings["Paths"]["mefpp"].strip().strip('"')).expanduser()
    if not engine.is_absolute():
        engine = Path(shutil.which(str(engine)) or str(engine))
    engine = engine.resolve(strict=True)
    protected = {str(p): digest(p) for p in (config, engine)}
    names = ["mefpp2/ins/mef/recipes/mefpp.c", "mefpp2/ins/mef/common/mefp_lib.c",
             "mefpp2/ins/mef/common/mefp_lib.h", "mefpp2/qfits5/src/xmemory.c",
             "mefpp2/qfits5/include/xmemory.h", "mefpp2/qfits5/src/cache.c", "mefpp2/src/unix/getopt.c",
             "mefpp2/ins/mef/config/omegacam.paf", "mefpp2/ins/mef/config/wfi.paf",
             "mefpp2/tests/failure_contract.py", "mefpp2/tests/split_ownership_probe.c",
             "mefpp2/tests/split_ownership_cases.py", "mefpp2/tests/qualify_split_ownership.py",
             "mefpp2/tests/qualify_mac_leaks.py"]
    sources = {p: digest(repo / p) for p in names}
    reference_path = repo / "docs/developer/fixtures/mac-stage2-split-cache-2026-10-27/run-provenance.json"
    reference_hash = digest(reference_path)
    if reference_hash != "299895e850c473c21645e8ecc03f21ef785160a6896492cef00198bcd59b3f78":
        raise RuntimeError("STOP: Mac reference differs from inspected report")
    reference = json.loads(reference_path.read_text())
    if (reference["tested_source"]["commit"] != "5322bb952e6958a93594692fcf1e96c58fbf800d" or
            not reference["execution_complete"] or reference["status"] != "passed" or
            len(reference["cases"]) != 80):
        raise RuntimeError("STOP: incomplete Mac reference")
    for name, expected in reference["source_sha256"].items():
        if sources.get(name) != expected:
            raise RuntimeError("STOP: Mac-qualified source/driver/fixture differs: " + name)
    reference_cases = {c["case"]: c for c in reference["cases"] if c["lane"] == "leaks"}
    if len(reference_cases) != 40 or any(c["status"] != "passed" for c in reference_cases.values()):
        raise RuntimeError("STOP: incomplete Mac functional reference")
    sources["mefpp2/tests/qualify_split_chapman3.py"] = digest(Path(__file__).resolve())
    root = Path.home() / "Software/build/wenu-imaging"
    if not root.is_dir():
        raise RuntimeError("STOP: expected imaging build root absent")
    work = Path(tempfile.mkdtemp(prefix="chapman3-stage2-split-", dir=root))
    provenance = work / "run-provenance.json"
    record = dict(schema_version=1, project="wenu-imaging", tested_source=identity,
                  host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
                  purpose="S2-04 target split/cache functional and qfits-accounting verification",
                  diagnostic_scope="Uninstrumented target; no compatible external sanitizer/leak-tool claim",
                  cache_reference=str(reference_path) if reference_path else None,
                  cache_reference_sha256=reference_hash,
                  status="running", execution_complete=False, retention_roles=["acceptance_evidence"],
                  source_sha256=sources, protected_sha256=protected, commands=[], cases=[],
                  allocator=dict(XMEMORY_MODE=2, XMEMORY_MAXPTRS=2000000),
                  tool_sha256={str(p): digest(p) for p in (compiler, cmake)},
                  installation_performed=False, observational_processing_performed=False,
                  limits=["Synthetic two-detector splitting only; no calibration/science reduction or Pycavi",
                          "One CLI call per process; no same-process repeated-stage qualification",
                          "Cache control preserves after-cli then calls the public purge twice" if reference_path else
                          "No explicit cache purge: outstanding registrations require attribution",
                          "Only mappings exercised by split; no general mmap/swap allocator qualification",
                          "Descriptor identity/count observed across CLI; no syscall-level exhaustive I/O injection",
                          "Uninstrumented GCC target; no external sanitizer/leak-tool acceptance"])
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

    def run(label, argv, cwd, env, preexec_fn=None):
        log = work / (label + ".log")
        item = dict(label=label, argv=list(map(str, argv)), cwd=str(cwd), log=str(log))
        record["commands"].append(item)
        save(provenance, record)
        print("Running:", label, flush=True)
        try:
            with log.open("w") as stream:
                result = subprocess.run(item["argv"], cwd=cwd, env=env, stdout=stream,
                                        stderr=subprocess.STDOUT, preexec_fn=preexec_fn, timeout=600 if label.startswith(("build-", "configure-")) else 60)
            item["exit_status"] = result.returncode
        except BaseException as error:
            item["error"] = str(error)
            raise
        finally:
            item["log_sha256"] = digest(log) if log.exists() else None
            save(provenance, record)
        return result.returncode, log

    try:
        # Source/export: no production file modifications; append private target only.
        source = directory("source", "Exported source and diagnostic target wiring")
        archive = subprocess.check_output(["git", "archive", identity["commit"], "mefpp2"], cwd=repo)
        record["source_archive_sha256"] = hashlib.sha256(archive).hexdigest()
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(source)
        for name, expected in sources.items():
            if digest(source / name) != expected:
                raise RuntimeError("Exported source mismatch: " + name)
        wiring = source / "mefpp2/CMakeLists.txt"
        wiring.write_text(wiring.read_text() + '\n# S2-04 private split observer, not installed.\n'
                          'add_executable(split_ownership_probe tests/split_ownership_probe.c)\n'
                          'target_link_libraries(split_ownership_probe PRIVATE mefpp_common)\n'
                          'target_compile_definitions(split_ownership_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n')
        record["diagnostic_cmake_sha256"] = digest(wiring)
        if record["diagnostic_cmake_sha256"] != reference["diagnostic_cmake_sha256"]:
            raise RuntimeError("STOP: diagnostic wiring differs from Mac")
        env = os.environ.copy()
        removed = ["ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS", "DYLD_INSERT_LIBRARIES",
                   "DYLD_LIBRARY_PATH", "MallocStackLogging", "MallocScribble", "MallocStackLoggingNoCompact", "S2_SPLIT_WRITE_LIMIT", "S2_SPLIT_CACHE_CONTROL", "LD_PRELOAD", "LD_LIBRARY_PATH"]
        for key in removed:
            env.pop(key, None)
        env.update(E_VERBOSE="0", E_DEBUG="0")
        record["removed_child_environment"] = removed
        lane_env = {"functional": {}}
        record["lane_environment"] = lane_env
        save(provenance, record)
        for label, command in (("compiler-version", [compiler, "--version"]),
                               ("cmake-version", [cmake, "--version"]),
                               ("os-version", ["/usr/bin/uname", "-srmo"])):
            code, log = run(label, command, work, env)
            if code:
                raise RuntimeError("Tool inventory failed: " + str(log))
        for mode in (90, 17):
            for lane in ("functional",):
                tag = "c%d-%s" % (mode, lane)
                build = directory("build-" + tag, "Ordinary CLI and ownership observer: " + tag)
                flags, link = "-O0 -g -fno-omit-frame-pointer", ""
                command = [cmake, "-S", source / "mefpp2", "-B", build, "-G", "Unix Makefiles",
                           "-DCMAKE_C_COMPILER=" + str(compiler), "-DCMAKE_BUILD_TYPE=Debug",
                           "-DMEFPP_C_STANDARD=" + str(mode), "-DBUILD_TESTING=OFF", "-DMEFPP_BUILD_RESOURCES=OFF",
                           "-DMEFPP_SOURCE_REVISION=" + identity["commit"],
                           "-DCMAKE_C_FLAGS=" + flags, "-DCMAKE_EXE_LINKER_FLAGS=" + link]
                for label, argv in (("configure-" + tag, command), ("build-" + tag,
                                     [cmake, "--build", build, "--target", "mefpp", "split_ownership_probe", "--parallel", "2"])):
                    code, log = run(label, argv, work, env)
                    if code:
                        raise RuntimeError("Build/configuration failed: " + str(log))
                info = json.loads((build / "build-info.json").read_text())
                if info["qfits_memory_mode"] != 2 or info["qfits_max_pointers"] != 2000000:
                    raise RuntimeError("Unexpected allocator policy")
                ordinary, observer = build / "mefpp", build / "split_ownership_probe"
                case_env = dict(env, **lane_env[lane])
                for instrument in ("omegacam", "wfi"):
                    original = (source / ("mefpp2/ins/mef/config/" + instrument + ".paf")).read_text()
                    for variant in cases():
                        label = tag + "-" + instrument + "-" + variant
                        case = directory(label, "Independent split case with ordinary/observer runs")
                        result = dict(case=label, mode=mode, lane=lane, instrument=instrument,
                                      variant=variant, roles={}, findings=[], functional_status="passed")
                        for role, executable in (("ordinary", ordinary), ("observer", observer)):
                            child = directory(label + "/" + role, "Retained " + role + " synthetic split")
                            argv, expected_exit, diagnostic, expected_outputs = prepare(child, original, variant)
                            inputs = input_hashes(child)
                            command = [executable, *argv]
                            child_env = dict(case_env)
                            preexec_fn = None
                            if role == "observer" and reference_path:
                                child_env["S2_SPLIT_CACHE_CONTROL"] = "1"
                            if variant == "failed-write":
                                if role == "ordinary":
                                    preexec_fn = restrict_output
                                else:
                                    child_env["S2_SPLIT_WRITE_LIMIT"] = "4096"
                            code, log = run(label + "-" + role, command, child, child_env, preexec_fn)
                            output = log.read_text(errors="replace")
                            observed = dict(exit_status=code, expected_native_exit=expected_exit,
                                            arguments=argv, input_sha256=inputs, findings=[],
                                            executable_sha256=digest(executable), log_sha256=digest(log))
                            try:
                                if role == "ordinary":
                                    if code != expected_exit:
                                        raise RuntimeError("ordinary CLI exit contract mismatch")
                                else:
                                    matches = re.findall(r"^CLI RESULT native_exit=(\d+) constructed=(\d+) destroyed=(\d+) mismatch=(\d+) owner_live=(\d+)$", output, re.M)
                                    if matches != [(str(expected_exit), "1", "1", "0", "0")]:
                                        raise RuntimeError("observer native exit/context owner contract mismatch")
                                    observed["ownership_contract"] = list(matches[0])
                                if diagnostic and diagnostic.lower() not in output.lower():
                                    raise RuntimeError("missing expected diagnostic: " + diagnostic)
                                observed["outputs"] = verify(child, inputs, expected_outputs)
                                if reference_cases:
                                    prior = reference_cases[label.replace("-functional-", "-leaks-", 1)]["roles"][role]
                                    if (observed["outputs"] != prior["outputs"] or
                                            inputs != prior["input_sha256"] or
                                            expected_exit != prior["expected_native_exit"]):
                                        raise RuntimeError("retained reference input/output/exit mismatch")
                                observed["functional_status"] = "passed"
                            except Exception as error:
                                observed["functional_status"] = "failed"
                                observed["findings"].append(str(error))
                                result["functional_status"] = "failed"
                            # Diagnostics/resource states do not overwrite functional results.
                            if "ERROR: AddressSanitizer" in output or "runtime error:" in output:
                                observed["findings"].append("invalid-access/undefined-behavior diagnostic")
                            if role == "observer":
                                try:
                                    for boundary in ("process-start", "after-cli"):
                                        state = allocation_state(output, boundary)
                                        observed[boundary + "_accounting"] = state
                                        if any(state.values()) and not (reference_path and boundary == "after-cli"):
                                            observed["findings"].append("unattributed live allocation/mapping at " + boundary)
                                    rows = re.findall(r"^DESCRIPTORS before=(\d+) after=(\d+) identity_equal=(\d+)$", output, re.M)
                                    if len(rows) != 1 or rows[0][0] != rows[0][1] or rows[0][2] != "1":
                                        raise RuntimeError("open-descriptor state changed or observation incomplete")
                                    observed["descriptors"] = list(rows[0])
                                    limits = re.findall(r"^DESCRIPTOR LIMIT (before|after) soft=(\d+) hard=(\d+) soft_unlimited=(\d+)$", output, re.M)
                                    if len(limits) != 2 or [x[0] for x in limits] != ["before", "after"]:
                                        raise RuntimeError("descriptor limit observation incomplete")
                                    observed["descriptor_limits"] = [list(x) for x in limits]
                                    if reference_path:
                                        state = observed["after-cli_accounting"]
                                        cached = variant not in ("missing-input", "non-fits")
                                        filename = argv[1] if variant == "valid-absolute" else "mosaic.fits"
                                        expected = dict(pointers=5 if cached else 0,
                                                        bytes=len(filename.encode()) + 1 + 16 * (2 if variant == "truncated-data" else 3) if cached else 0,
                                                        mapped_files=0, mapped_references=0, swap_bytes=0)
                                        if state != expected:
                                            raise RuntimeError("after-cli state differs from cache-size prediction")
                                        for boundary in ("after-purge", "after-second-purge"):
                                            state = allocation_state(output, boundary)
                                            observed[boundary + "_accounting"] = state
                                            if any(state.values()):
                                                raise RuntimeError("nonzero resource state at " + boundary)
                                            rows = re.findall(r"^CACHE DESCRIPTORS " + boundary + r" before=(\d+) after=(\d+) identity_equal=(\d+)$", output, re.M)
                                            if len(rows) != 1 or rows[0][0] != rows[0][1] or rows[0][2] != "1":
                                                raise RuntimeError("cache purge descriptor contract mismatch at " + boundary)
                                            observed[boundary + "_descriptors"] = list(rows[0])
                                        observed["cache_attribution"] = "passed"
                                    if code != 0:
                                        observed["findings"].append("observer/tool nonzero exit")
                                except Exception as error:
                                    observed["findings"].append(str(error))
                            observed["status"] = "failed" if observed["findings"] else "passed"
                            result["roles"][role] = observed
                            result["findings"].extend(role + ": " + f for f in observed["findings"])
                            save(child / "run-provenance.json", dict(observed, schema_version=1,
                                 tested_source=identity, parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                        left, right = result["roles"]["ordinary"], result["roles"]["observer"]
                        if left["input_sha256"] != right["input_sha256"] or left.get("outputs") != right.get("outputs"):
                            result["findings"].append("ordinary/observer input or output mismatch")
                            result["functional_status"] = "failed"
                        result["status"] = "failed" if result["findings"] else "passed"
                        record["cases"].append(result)
                        save(case / "run-provenance.json", dict(result, schema_version=1,
                             tested_source=identity, parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                        save(provenance, record)
                        print(("PASS:" if result["status"] == "passed" else "FINDING:"), label,
                              "functional=" + result["functional_status"], flush=True)
        record["execution_complete"] = len(record["cases"]) == len(cases()) * 4
        record["functional_finding_cases"] = sum(c["functional_status"] != "passed" for c in record["cases"])
        record["finding_cases"] = sum(c["status"] != "passed" for c in record["cases"])
        record["status"] = "passed" if record["execution_complete"] and not record["finding_cases"] else "failed"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        record["sources_unchanged"] = all(digest(repo / p) == h for p, h in sources.items())
        record["exported_sources_unchanged"] = all(
            (work / "source" / p).is_file() and digest(work / "source" / p) == h
            for p, h in sources.items())
        record["protected_files_unchanged"] = all(digest(Path(p)) == h for p, h in protected.items())
        record["cache_reference_unchanged"] = not reference_path or digest(reference_path) == reference_hash
        record["checkout_unchanged"] = (git("rev-parse", "HEAD") == identity["commit"] and
                                       not git("status", "--porcelain", "--untracked-files=all"))
        if not all(record[k] for k in ("sources_unchanged", "exported_sources_unchanged",
                                       "protected_files_unchanged", "checkout_unchanged", "cache_reference_unchanged")):
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], completed_utc=record["completed_utc"])
                save(child, value)
    print("TARGET SPLIT: cases=%d; finding cases=%d; complete=%s" %
          (len(record["cases"]), record.get("finding_cases", 0), record["execution_complete"]))
    print("REPORT:", provenance)
    print("Functional finding cases:", record.get("functional_finding_cases", "incomplete"))
    print("Functional/accounting gate:", record["status"])
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
