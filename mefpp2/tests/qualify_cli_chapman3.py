"""Chapman3 S2-03 functional/qfits-accounting verification (#75, #103).

Calls the actual main/mef_bb_load/mef_engine; no Pycavi or image processing.
Uninstrumented target verification; no external sanitizer/leak-tool claim.
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
from qualify_cli_ownership import cases, paf_text


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
             "mefpp2/qfits5/include/xmemory.h", "mefpp2/ins/mef/config/omegacam.paf",
             "mefpp2/ins/mef/config/wfi.paf", "mefpp2/tests/failure_contract.py",
             "mefpp2/tests/cli_ownership_probe.c", "mefpp2/tests/qualify_cli_ownership.py",
             "mefpp2/tests/qualify_mac_leaks.py"]
    sources = {p: digest(repo / p) for p in names}
    for name in ("mefpp2/src/unix/getopt.c", "mefpp2/tests/getopt_name_probe.c"):
        sources[name] = digest(repo / name)
    reference_path = repo / "docs/developer/fixtures/mac-stage2-cli-corrected-2026-10-27/run-provenance.json"
    reference_sha = digest(reference_path)
    if reference_sha != "a17450679412c1e591aee3a06de163b41add42c6ef8d7382accfaeab57f8acc8":
        raise RuntimeError("STOP: Mac reference differs from the inspected report")
    mac = json.loads(reference_path.read_text())
    if not mac["execution_complete"] or mac["status"] != "passed" or len(mac["cases"]) != 224:
        raise RuntimeError("STOP: incomplete Mac acceptance")
    for name, expected in mac["source_sha256"].items():
        if sources.get(name) != expected:
            raise RuntimeError("STOP: Mac-qualified source/driver/fixture differs: " + name)
    reference = {c["case"]: c for c in mac["cases"] if c["lane"] == "leaks"}
    if len(reference) != 112 or any(c["status"] != "passed" for c in reference.values()):
        raise RuntimeError("STOP: Mac functional reference incomplete")
    sources["mefpp2/tests/qualify_cli_chapman3.py"] = digest(Path(__file__).resolve())
    root = Path.home() / "Software/build/wenu-imaging"
    if not root.is_dir():
        raise RuntimeError("STOP: expected imaging build root absent")
    work = Path(tempfile.mkdtemp(prefix="chapman3-stage2-cli-", dir=root))
    provenance = work / "run-provenance.json"
    record = dict(schema_version=1, project="wenu-imaging", tested_source=identity,
                  host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
                  purpose="S2-03 Chapman3 CLI functional/ownership-accounting verification",
                  phase="target", mac_reference_report=str(reference_path),
                  mac_reference_report_sha256=reference_sha,
                  status="running", execution_complete=False, retention_roles=["acceptance_evidence"],
                  source_sha256=sources, protected_sha256=protected, commands=[], cases=[], parser_checks=[],
                  allocator=dict(XMEMORY_MODE=2, XMEMORY_MAXPTRS=2000000),
                  tool_sha256={str(p): digest(p) for p in (compiler, cmake)},
                  installation_performed=False, observational_processing_performed=False,
                  limits=["CLI failure paths only; no successful split or image/calibration/science processing",
                          "One process per case; does not satisfy same-process repeated stages",
                          "RAM accounting; no cache purge or mapped/swap qualification",
                          "Recipe constructor/destructor references observed; common-library partial cleanup unmodified",
                          "Uninstrumented GCC target; no compatible external sanitizer/leak-tool claim"])
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
                          'target_compile_definitions(cli_ownership_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n'
                          'add_executable(getopt_name_probe tests/getopt_name_probe.c)\n'
                          'target_link_libraries(getopt_name_probe PRIVATE eclipse)\n'
                          'target_compile_definitions(getopt_name_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n')
        record["diagnostic_cmake_sha256"] = digest(wiring)
        if record["diagnostic_cmake_sha256"] != mac["diagnostic_cmake_sha256"]:
            raise RuntimeError("STOP: diagnostic target wiring differs from Mac")
        env = os.environ.copy()
        removed = ["ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS", "DYLD_INSERT_LIBRARIES",
                   "DYLD_LIBRARY_PATH", "MallocStackLogging", "MallocScribble", "MallocStackLoggingNoCompact", "LD_PRELOAD", "LD_LIBRARY_PATH"]
        for key in removed:
            env.pop(key, None)
        env.update(E_VERBOSE="0", E_DEBUG="0")
        record["removed_child_environment"] = removed
        lane_env = {"functional": {}}
        record["lane_environment"] = lane_env
        save(provenance, record)
        for label, command in (("compiler-version", [compiler, "--version"]),
                               ("cmake-version", [cmake, "--version"]),
                               ("os-version", ["/usr/bin/uname", "-a"])):
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
                                     [cmake, "--build", build, "--target", "mefpp", "cli_ownership_probe", "getopt_name_probe", "--parallel", "2"])):
                    code, log = run(label, argv, work, env)
                    if code:
                        raise RuntimeError("Build/configuration failed: " + str(log))
                info = json.loads((build / "build-info.json").read_text())
                if info["qfits_memory_mode"] != 2 or info["qfits_max_pointers"] != 2000000:
                    raise RuntimeError("Unexpected allocator policy")
                ordinary, observer = build / "mefpp", build / "cli_ownership_probe"
                case_env = dict(env, **lane_env[lane])
                # #103 regression: exact/unique/ambiguous prefixes, required
                # argument forms, unknown options and unchanged short parsing.
                parser_case = directory(tag + "-parser-contract", "Thirteen bundled getopt matching contracts")
                parser_executable = build / "getopt_name_probe"
                parser_code, parser_log = run(tag + "-parser-contract", [parser_executable], parser_case, case_env)
                parser_output = parser_log.read_text(errors="replace")
                parser_result = dict(case=tag + "-parser-contract", exit_status=parser_code,
                                     executable_sha256=digest(parser_executable), log_sha256=digest(parser_log),
                                     status="passed" if parser_code == 0 and
                                     parser_output.count("PARSER COMPLETE checks=13 failed=0") == 1 and
                                     len(re.findall(r"^PARSER PASS ", parser_output, re.M)) == 13 and
                                     "ERROR: AddressSanitizer" not in parser_output and
                                     "runtime error:" not in parser_output else "failed")
                record["parser_checks"].append(parser_result)
                save(parser_case / "run-provenance.json", dict(parser_result, schema_version=1,
                     tested_source=identity, parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                save(provenance, record)
                if parser_result["status"] != "passed":
                    raise RuntimeError("Parser regression failed: " + str(parser_log))
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
                            if observed_code != 0:
                                result["findings"].append("observer/tool nonzero exit")
                            if diagnostic and diagnostic.lower() not in output.lower():
                                result["findings"].append("observer diagnostic mismatch")
                        except Exception as error:
                            result["findings"].append(str(error))
                        if (digest(paf) if paf.exists() else None) != input_sha:
                            result["findings"].append("staged PAF changed")
                        if reference:
                            expected = reference[label.replace("-functional-", "-leaks-")]
                            keys = ("arguments", "input_sha256", "expected_exit", "expected_owners",
                                    "ordinary_exit", "ownership_contract", "after-cli_accounting")
                            result["mac_values_match"] = all(result.get(k) == expected.get(k) for k in keys)
                            if not result["mac_values_match"]:
                                result["findings"].append("CLI/input/ownership values differ from accepted Mac reference")
                        if sorted(p.name for p in case.iterdir()) != (["mefpp.paf", "run-provenance.json"] if text is not None else ["run-provenance.json"]):
                            result["findings"].append("unexpected generated output")
                        result["status"] = "failed" if result["findings"] else "passed"
                        record["cases"].append(result)
                        save(case / "run-provenance.json", dict(result, schema_version=1,
                             tested_source=identity, parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                        save(provenance, record)
                        print(("PASS:" if result["status"] == "passed" else "FINDING:"), label, flush=True)
        record["execution_complete"] = len(record["cases"]) == len(cases()) * 4
        if reference:
            record["mac_values_match"] = all(c.get("mac_values_match") for c in record["cases"])
        record["finding_cases"] = sum(c["status"] != "passed" for c in record["cases"])
        record["status"] = "passed" if record["execution_complete"] and not record["finding_cases"] else "failed"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        record["sources_unchanged"] = all(digest(repo / p) == h for p, h in sources.items())
        record["reference_report_unchanged"] = digest(reference_path) == reference_sha
        record["exported_sources_unchanged"] = all(
            (work / "source" / p).is_file() and digest(work / "source" / p) == h
            for p, h in sources.items())
        record["protected_files_unchanged"] = all(digest(Path(p)) == h for p, h in protected.items())
        record["checkout_unchanged"] = (git("rev-parse", "HEAD") == identity["commit"] and
                                       not git("status", "--porcelain", "--untracked-files=all"))
        if not all(record[k] for k in ("sources_unchanged", "exported_sources_unchanged",
                                       "protected_files_unchanged", "checkout_unchanged", "reference_report_unchanged")):
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], completed_utc=record["completed_utc"])
                save(child, value)
    print("TARGET CLI: cases=%d; finding cases=%d; complete=%s" %
          (len(record["cases"]), record.get("finding_cases", 0), record["execution_complete"]))
    print("REPORT:", provenance)
    print("Functional/accounting gate:", record["status"])
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
