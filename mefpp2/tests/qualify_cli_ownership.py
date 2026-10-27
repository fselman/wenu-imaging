"""Retained S2-03 CLI ownership baseline on the qualified Intel Mac (#75).

Calls the actual main/mef_bb_load/mef_engine; no Pycavi or image processing.
Functional completion and memory acceptance are reported separately.
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
from qualify_mac_leaks import accounting, digest, save


def cases():
    # Information and first-pass parser paths: no PAF or published context.
    rows = []
    for flag in ("help", "version", "license"):
        rows.append((flag, ["--" + flag], "absent", None, None, 0, 0, None))
    for name, argv in (("no-arguments", []), ("missing-option-value", ["--pafname"]),
                       ("unknown-option", ["--unknown"])):
        rows.append((name, argv, "absent", None, None, 1, 0, None))
    # Configuration failures reuse failure_contract.py's exact mutations.
    for kind in ("absent", "malformed"):
        rows.append(("paf-" + kind, ["--split", "missing.list"], kind,
                     None, None, 1, 0, "PAF"))
    for key in ("MEF.NCHIPS", "MEF.CROP.Y.MAX.CHIP2", "MEF.SATMAX"):
        rows.append(("missing-" + key.lower().replace(".", "-"),
                     ["--split", "missing.list"], "remove", key, None, 1, 0, key))
    for index, value in enumerate(("0", "-1", "junk", "nan", "1e999", "2147483648", "1.5")):
        rows.append(("invalid-count-%d" % index, ["--split", "missing.list"],
                     "replace", "MEF.NCHIPS", value, 1, 0, "MEF.NCHIPS"))
    rows.append(("valueless-satmax", ["--split", "missing.list"], "valueless",
                 "MEF.SATMAX", None, 1, 0, "MEF.SATMAX"))
    # Second-pass parser rejects saturation after constructing the context.
    for index, value in enumerate(("2", "-1", "junk", "nan", "inf", "0.00001", "0.99999")):
        rows.append(("invalid-satmax-%d" % index, ["--satmax", value],
                     "valid", None, None, 1, 1, "satmax"))
    # Engine errors: absent split input (existing contract), missing science
    # calibration names (early engine validation). Neither processes an image.
    rows.append(("missing-split-input", ["--split", "missing.list"],
                 "valid", None, None, 1, 1, "missing.list"))
    rows.append(("missing-science-calibrations", ["--science", "missing.list"],
                 "valid", None, None, 1, 1, "no name provided for dome or sky"))
    return rows


def paf_text(original, kind, key, value):
    if kind == "absent":
        return None
    if kind == "malformed":
        return "this is not a PAF\n"
    if kind == "valid":
        return original
    lines = original.splitlines()
    indices = [i for i, line in enumerate(lines) if line.split() and line.split()[0] == key]
    if len(indices) != 1:
        raise RuntimeError("Unexpected PAF key identity: " + key)
    index = indices[0]
    if kind == "remove":
        del lines[index]
    else:
        lines[index] = key + " " if kind == "valueless" else key + " " + value + ";"
    return "\n".join(lines) + "\n"


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
    compiler, sdk, cmake = [p.resolve(strict=True) for p in (args.compiler, args.sdk, args.cmake)]
    leaks = Path("/usr/bin/leaks").resolve(strict=True)
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
             "mefpp2/qfits5/include/xmemory.h", "mefpp2/ins/mef/config/omegacam.paf",
             "mefpp2/ins/mef/config/wfi.paf", "mefpp2/tests/failure_contract.py",
             "mefpp2/tests/cli_ownership_probe.c", "mefpp2/tests/qualify_cli_ownership.py",
             "mefpp2/tests/qualify_mac_leaks.py"]
    sources = {p: digest(repo / p) for p in names}
    controls = {}
    for kind in ("leak", "diagnostic"):
        path = repo / ("docs/developer/fixtures/mac-stage2-tool-controls-2026-10-27/" +
                       kind + "-run-provenance.json")
        control = json.loads(path.read_text())
        if control["status"] != "passed":
            raise RuntimeError("STOP: tool controls are not accepted")
        for name in ("mefpp2/qfits5/src/xmemory.c", "mefpp2/qfits5/include/xmemory.h"):
            expected = control["source_sha256"].get(name, control["source_sha256"].get(Path(name).name))
            if sources[name] != expected:
                raise RuntimeError("STOP: allocator differs from qualified controls")
        controls[str(path.relative_to(repo))] = digest(path)
    root = Path.home() / "Software/build/wenu-imaging"
    if not root.is_dir():
        raise RuntimeError("STOP: expected imaging build root absent")
    work = Path(tempfile.mkdtemp(prefix="mac-stage2-cli-baseline-", dir=root))
    provenance = work / "run-provenance.json"
    record = dict(schema_version=1, project="wenu-imaging", tested_source=identity,
                  host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
                  purpose="S2-03 unchanged CLI/parser/engine failure ownership baseline",
                  status="running", execution_complete=False, retention_roles=["acceptance_evidence"],
                  source_sha256=sources, protected_sha256=protected, commands=[], cases=[],
                  qualified_tool_reports_sha256=controls,
                  allocator=dict(XMEMORY_MODE=2, XMEMORY_MAXPTRS=2000000),
                  tool_sha256={str(p): digest(p) for p in (compiler, cmake, leaks)},
                  installation_performed=False, observational_processing_performed=False,
                  limits=["CLI failure paths only; no successful split or image/calibration/science processing",
                          "One process per case; does not satisfy same-process repeated stages",
                          "RAM accounting; no cache purge or mapped/swap qualification",
                          "Recipe constructor/destructor references observed; common-library partial cleanup unmodified",
                          "Mac only; Chapman3 unchanged-driver verification pending"])
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

    def run(label, argv, cwd, env):
        log = work / (label + ".log")
        item = dict(label=label, argv=list(map(str, argv)), cwd=str(cwd), log=str(log))
        record["commands"].append(item)
        save(provenance, record)
        print("Running:", label, flush=True)
        try:
            with log.open("w") as stream:
                result = subprocess.run(item["argv"], cwd=cwd, env=env, stdout=stream,
                                        stderr=subprocess.STDOUT, timeout=600 if label.startswith(("build-", "configure-")) else 60)
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
        wiring.write_text(wiring.read_text() + '\n# S2-03 private observer, not installed.\n'
                          'add_executable(cli_ownership_probe tests/cli_ownership_probe.c)\n'
                          'target_link_libraries(cli_ownership_probe PRIVATE mefpp_common)\n'
                          'target_compile_definitions(cli_ownership_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n')
        record["diagnostic_cmake_sha256"] = digest(wiring)
        env = os.environ.copy()
        removed = ["ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS", "DYLD_INSERT_LIBRARIES",
                   "DYLD_LIBRARY_PATH", "MallocStackLogging", "MallocScribble", "MallocStackLoggingNoCompact"]
        for key in removed:
            env.pop(key, None)
        env.update(E_VERBOSE="0", E_DEBUG="0")
        record["removed_child_environment"] = removed
        lane_env = dict(instrumented=dict(ASAN_OPTIONS="detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86",
                                         UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=0"),
                        leaks=dict(MallocStackLogging="lite", MallocScribble="1"))
        record["lane_environment"] = lane_env
        save(provenance, record)
        for label, command in (("compiler-version", [compiler, "--version"]),
                               ("cmake-version", [cmake, "--version"]),
                               ("os-version", ["/usr/bin/sw_vers"])):
            code, log = run(label, command, work, env)
            if code:
                raise RuntimeError("Tool inventory failed: " + str(log))
        for mode in (90, 17):
            for lane in ("instrumented", "leaks"):
                tag = "c%d-%s" % (mode, lane)
                build = directory("build-" + tag, "Ordinary CLI and ownership observer: " + tag)
                flags, link = "-O0 -g -fno-omit-frame-pointer", ""
                if lane == "instrumented":
                    flags += " -fsanitize=address,undefined -fno-sanitize-recover=all"
                    link = "-fsanitize=address,undefined"
                command = [cmake, "-S", source / "mefpp2", "-B", build, "-G", "Unix Makefiles",
                           "-DCMAKE_C_COMPILER=" + str(compiler), "-DCMAKE_OSX_SYSROOT=" + str(sdk),
                           "-DCMAKE_OSX_ARCHITECTURES=x86_64", "-DCMAKE_BUILD_TYPE=Debug",
                           "-DMEFPP_C_STANDARD=" + str(mode), "-DBUILD_TESTING=OFF", "-DMEFPP_BUILD_RESOURCES=OFF",
                           "-DMEFPP_SOURCE_REVISION=" + identity["commit"],
                           "-DCMAKE_C_FLAGS=" + flags, "-DCMAKE_EXE_LINKER_FLAGS=" + link]
                for label, argv in (("configure-" + tag, command), ("build-" + tag,
                                     [cmake, "--build", build, "--target", "mefpp", "cli_ownership_probe", "--parallel", "2"])):
                    code, log = run(label, argv, work, env)
                    if code:
                        raise RuntimeError("Build/configuration failed: " + str(log))
                info = json.loads((build / "build-info.json").read_text())
                if info["qfits_memory_mode"] != 2 or info["qfits_max_pointers"] != 2000000:
                    raise RuntimeError("Unexpected allocator policy")
                ordinary, observer = build / "mefpp", build / "cli_ownership_probe"
                if lane == "instrumented":
                    for executable in (ordinary, observer):
                        code, log = run("symbols-" + tag + "-" + executable.name,
                                        ["/usr/bin/dsymutil", executable], work, env)
                        if code:
                            raise RuntimeError("Debug symbols failed: " + str(log))
                case_env = dict(env, **lane_env[lane])
                for instrument in ("omegacam", "wfi"):
                    original = (source / ("mefpp2/ins/mef/config/" + instrument + ".paf")).read_text()
                    for name, argv, kind, key, value, expected_exit, expected_owners, diagnostic in cases():
                        label = tag + "-" + instrument + "-" + name
                        case = directory(label, "Independent retained CLI rejection/information case")
                        text = paf_text(original, kind, key, value)
                        paf = case / "mefpp.paf"
                        if text is not None:
                            paf.write_text(text)
                        input_sha = digest(paf) if paf.exists() else None
                        result = dict(case=label, mode=mode, lane=lane, instrument=instrument, variant=name,
                                      arguments=argv, input_sha256=input_sha, expected_exit=expected_exit,
                                      expected_owners=expected_owners, status="failed", findings=[])
                        # Ordinary CLI provides independent exit/diagnostic semantics.
                        code, log = run(label + "-ordinary", [ordinary, *argv], case, case_env)
                        output = log.read_text(errors="replace")
                        result.update(ordinary_exit=code, ordinary_log_sha256=digest(log))
                        if code != expected_exit or (diagnostic and diagnostic.lower() not in output.lower()):
                            result["findings"].append("ordinary CLI status/diagnostic contract mismatch")
                        if "ERROR: AddressSanitizer" in output or "runtime error:" in output:
                            result["findings"].append("ordinary CLI invalid-access/undefined-behavior diagnostic")
                        # Observer calls the same main, then snapshots before atexit.
                        command = [observer, *argv]
                        if lane == "leaks":
                            command = [leaks, "-quiet", "-atExit", "--", *command]
                        observed_code, log = run(label + "-observer", command, case, case_env)
                        output = log.read_text(errors="replace")
                        result.update(observer_exit=observed_code, observer_log_sha256=digest(log),
                                      ordinary_sha256=digest(ordinary), observer_sha256=digest(observer))
                        try:
                            matches = re.findall(r"^CLI RESULT native_exit=(\d+) constructed=(\d+) destroyed=(\d+) mismatch=(\d+) owner_live=(\d+)$", output, re.M)
                            expected = (str(expected_exit), str(expected_owners), str(expected_owners), "0", "0")
                            if matches != [expected]:
                                raise RuntimeError("observer CLI/ownership contract mismatch: " + repr(matches))
                            result["ownership_contract"] = list(matches[0])
                            for boundary in ("process-start", "after-cli"):
                                state = accounting(output, boundary)
                                result[boundary + "_accounting"] = state
                                if state != dict(pointers=0, bytes=0):
                                    result["findings"].append("outstanding allocation at " + boundary)
                            if "ERROR: AddressSanitizer" in output or "runtime error:" in output:
                                result["findings"].append("observer invalid-access/undefined-behavior diagnostic")
                            if lane == "leaks":
                                summaries = re.findall(r"\b(\d+) leaks? for (\d+) total leaked bytes\b", output)
                                if len(summaries) != 1:
                                    raise RuntimeError("unrecognized leaks summary")
                                blocks, size = map(int, summaries[0])
                                result.update(leaked_blocks=blocks, leaked_bytes=size)
                                if blocks or size:
                                    result["findings"].append("unreachable allocations reported by leaks")
                            if observed_code != 0:
                                result["findings"].append("observer/tool nonzero exit")
                            if diagnostic and diagnostic.lower() not in output.lower():
                                result["findings"].append("observer diagnostic mismatch")
                        except Exception as error:
                            result["findings"].append(str(error))
                        if (digest(paf) if paf.exists() else None) != input_sha:
                            result["findings"].append("staged PAF changed")
                        if sorted(p.name for p in case.iterdir()) != (["mefpp.paf", "run-provenance.json"] if text is not None else ["run-provenance.json"]):
                            result["findings"].append("unexpected generated output")
                        result["status"] = "failed" if result["findings"] else "passed"
                        record["cases"].append(result)
                        save(case / "run-provenance.json", dict(result, schema_version=1,
                             tested_source=identity, parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                        save(provenance, record)
                        print(("PASS:" if result["status"] == "passed" else "FINDING:"), label, flush=True)
        record["execution_complete"] = len(record["cases"]) == len(cases()) * 8
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
        record["checkout_unchanged"] = (git("rev-parse", "HEAD") == identity["commit"] and
                                       not git("status", "--porcelain", "--untracked-files=all"))
        if not all(record[k] for k in ("sources_unchanged", "exported_sources_unchanged",
                                       "protected_files_unchanged", "checkout_unchanged")):
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], completed_utc=record["completed_utc"])
                save(child, value)
    print("CLI BASELINE: cases=%d; finding cases=%d; complete=%s" %
          (len(record["cases"]), record.get("finding_cases", 0), record["execution_complete"]))
    print("REPORT:", provenance)
    print("Memory gate:", record["status"])
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
