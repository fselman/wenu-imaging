"""S2-05 supplied-bias BPM ownership qualification on Intel Mac (#75).

Separate supplied-bias driver/observer; deterministic additive pixel fixtures.
Check first-frame values and every unaffected reference card with diagnostics.
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
from bpm_bias_cases import prepare, verify
from qualify_split_ownership import allocation_state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--cmake", type=Path, required=True)
    args = parser.parse_args()
    # Host/environment/source guards.
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
    # Fixture/reference/control identity verification.
    fixture = repo / "mefpp2/tests/fixtures/bpm-cleanup"
    fixture_manifest = json.loads((fixture / "manifest.json").read_text())
    for name, expected in fixture_manifest["files"].items():
        if digest(fixture / name) != expected:
            raise RuntimeError("STOP: accepted BPM fixture/driver differs: " + name)
    reference_path = repo / "docs/developer/fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json"
    reference_hash = digest(reference_path)
    if reference_hash != "90eff4ddb869bac73601ca3818ed4f94452fe5146013c85a8d0e3755459eee4a":
        raise RuntimeError("STOP: accepted reference report changed")
    import numpy as np
    import astropy
    reference = json.loads(reference_path.read_text())
    if reference["status"] != "passed" or len(reference["cases"]) != 8:
        raise RuntimeError("STOP: accepted BPM reference incomplete")
    references = {c["case"]: c for c in reference["cases"]}
    names = ["mefpp2/ins/mef/common/mefp_lib.c", "mefpp2/ins/mef/common/mefp_lib.h",
             "mefpp2/src/iproc/detector.c", "mefpp2/src/iproc/pixelmaps.c",
             "mefpp2/src/iproc/framelist.c", "mefpp2/qfits5/src/xmemory.c",
             "mefpp2/qfits5/include/xmemory.h", "mefpp2/qfits5/src/cache.c",
             "mefpp2/tests/bpm_ownership_probe.c", "mefpp2/tests/bpm_ownership_cases.py",
             "mefpp2/tests/qualify_bpm_ownership.py", "mefpp2/tests/qualify_split_ownership.py",
             "mefpp2/tests/qualify_mac_leaks.py", "mefpp2/tests/split_ownership_cases.py",
             "mefpp2/tests/fixtures/bpm-cleanup/manifest.json",
             "mefpp2/tests/bpm_metadata_cases.py", "mefpp2/tests/qualify_bpm_bias.py",
             "mefpp2/tests/bpm_bias_cases.py", "mefpp2/tests/bpm_bias_probe.c",
             "mefpp2/tests/bpm_bias_ownership_probe.c",
             "mefpp2/tests/fixtures/bpm-bias/manifest.json"]
    names += ["mefpp2/tests/fixtures/bpm-cleanup/" + name for name in fixture_manifest["files"]]
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
    metadata_manifest = json.loads((repo / "mefpp2/tests/fixtures/bpm-bias/manifest.json").read_text())
    if metadata_manifest["parent_manifest_sha256"] != digest(repo / "mefpp2/tests/fixtures/bpm-metadata/manifest.json"):
        raise RuntimeError("STOP: metadata derivative parent changed")
    ownership_path = repo / "docs/developer/fixtures/mac-stage2-bpm-metadata-2026-10-27/run-provenance.json"
    ownership_hash = digest(ownership_path)
    if ownership_hash != "26868de58bd3a5c05c82304620d00549b79b2de605bd7bffcbeccd4faa9c308d":
        raise RuntimeError("STOP: inspected ownership reference changed")
    ownership = json.loads(ownership_path.read_text())
    if (ownership["tested_source"]["commit"] != "c6a7a2bf05f8962cd9db4d72989b420f10159406" or
            ownership["status"] != "passed" or not ownership["execution_complete"] or
            len(ownership["cases"]) != 16):
        raise RuntimeError("STOP: incomplete ownership reference")
    for name, expected in ownership["source_sha256"].items():
        if digest(repo / name) != expected:
            raise RuntimeError("STOP: qualified native source/driver/fixture changed: " + name)
    sources.update(ownership["source_sha256"])
    ownership_cases = {c["case"]: c for c in ownership["cases"]}
    root = Path.home() / "Software/build/wenu-imaging"
    if not root.is_dir():
        raise RuntimeError("STOP: expected imaging build root absent")
    work = Path(tempfile.mkdtemp(prefix="mac-stage2-bpm-bias-", dir=root))
    provenance = work / "run-provenance.json"
    record = dict(schema_version=1, project="wenu-imaging", tested_source=identity,
                  host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
                  purpose="S2-05 supplied-bias BPM and BPM ownership qualification",
                  ownership_reference=str(ownership_path), ownership_reference_sha256=ownership_hash,
                  metadata_fixture_manifest=metadata_manifest,
                  mac_reference_report=str(reference_path), mac_reference_sha256=reference_hash,
                  fixture_manifest_sha256=digest(fixture / "manifest.json"),
                  status="running", execution_complete=False, retention_roles=["acceptance_evidence"],
                  source_sha256=sources, protected_sha256=protected, commands=[], cases=[],
                  qualified_tool_reports_sha256=controls,
                  allocator=dict(XMEMORY_MODE=2, XMEMORY_MAXPTRS=2000000),
                  tool_sha256={str(p): digest(p) for p in (compiler, cmake, leaks)},
                  installation_performed=False, observational_processing_performed=False,
                  python=sys.executable, numpy=np.__version__, astropy=astropy.__version__,
                  limits=["Additive supplied-bias derivatives of accepted OmegaCAM BPM fixtures; no WFI/observational acceptance",
                          "Both regression producers with populated metadata, supplied bias and one extension; WFI/multiple extensions remain pending",
                          "One native call per process; no same-process repeated-stage qualification",
                          "Original after-driver state retained; double purge diagnoses cache but cannot waive other live state",
                          "No allocation/I/O injection or general mmap/swap qualification",
                          "Mac first; unchanged-driver target verification remains pending"])
    # Retained provenance before any build or native processing.
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
        # Export unchanged production and separate supplied-bias test drivers; append private targets only.
        source = directory("source", "Exported source and diagnostic target wiring")
        archive = subprocess.check_output(["git", "archive", identity["commit"], "mefpp2"], cwd=repo)
        record["source_archive_sha256"] = hashlib.sha256(archive).hexdigest()
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(source)
        for name, expected in sources.items():
            if digest(source / name) != expected:
                raise RuntimeError("Exported source mismatch: " + name)
        wiring = source / "mefpp2/CMakeLists.txt"
        wiring.write_text(wiring.read_text() + '\n# S2-05 private BPM ownership observers, not installed.\n'
                          'add_executable(bpm_original_probe tests/bpm_bias_probe.c)\n'
                          'add_executable(bpm_ownership_probe tests/bpm_bias_ownership_probe.c)\n'
                          'target_link_libraries(bpm_original_probe PRIVATE mefpp_common)\n'
                          'target_link_libraries(bpm_ownership_probe PRIVATE mefpp_common)\n'
                          'target_compile_definitions(bpm_original_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n'
                          'target_compile_definitions(bpm_ownership_probe PRIVATE ${MEFPP_FEATURE_DEFINITIONS})\n')
        record["diagnostic_cmake_sha256"] = digest(wiring)
        env = os.environ.copy()
        removed = ["ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS", "DYLD_INSERT_LIBRARIES",
                   "DYLD_LIBRARY_PATH", "MallocStackLogging", "MallocScribble", "MallocStackLoggingNoCompact", "S2_SPLIT_WRITE_LIMIT", "S2_SPLIT_CACHE_CONTROL"]
        for key in removed:
            env.pop(key, None)
        env.update(E_VERBOSE="0", E_DEBUG="0")
        record["removed_child_environment"] = removed
        lane_env = dict(instrumented=dict(ASAN_OPTIONS="detect_leaks=0:halt_on_error=1:abort_on_error=0:exitcode=86",
                                         UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=0"),
                        leaks=dict(MallocStackLogging="lite", MallocScribble="1"))
        record["lane_environment"] = lane_env
        save(provenance, record)
        # Tool inventory and C90/C17 diagnostic builds.
        for label, command in (("compiler-version", [compiler, "--version"]),
                               ("cmake-version", [cmake, "--version"]),
                               ("os-version", ["/usr/bin/sw_vers"])):
            code, log = run(label, command, work, env)
            if code:
                raise RuntimeError("Tool inventory failed: " + str(log))
        for mode in (90, 17):
            for lane in ("instrumented", "leaks"):
                tag = "c%d-%s" % (mode, lane)
                build = directory("build-" + tag, "Original BPM driver and ownership observer: " + tag)
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
                                     [cmake, "--build", build, "--target", "bpm_original_probe", "bpm_ownership_probe", "--parallel", "2"])):
                    code, log = run(label, argv, work, env)
                    if code:
                        raise RuntimeError("Build/configuration failed: " + str(log))
                info = json.loads((build / "build-info.json").read_text())
                if info["qfits_memory_mode"] != 2 or info["qfits_max_pointers"] != 2000000:
                    raise RuntimeError("Unexpected allocator policy")
                ordinary, observer = build / "bpm_original_probe", build / "bpm_ownership_probe"
                if lane == "instrumented":
                    for executable in (ordinary, observer):
                        code, log = run("symbols-" + tag + "-" + executable.name,
                                        ["/usr/bin/dsymutil", executable], work, env)
                        if code:
                            raise RuntimeError("Debug symbols failed: " + str(log))
                case_env = dict(env, **lane_env[lane])
                # Supplied-bias processing: recover accepted pixels through both production regressions.
                for kind in ("retained", "known-response"):
                    for flag in (0, 1):
                        label = tag + "-" + kind + "-flag" + str(flag)
                        case = directory(label, "Paired supplied-bias original/observed BPM constructor")
                        result = dict(case=label, mode=mode, lane=lane, fixture=kind, proportional_flag=flag,
                                      roles={}, findings=[], functional_status="passed")
                        prior = references["c%d-%s-flag%d" % (mode, kind, flag)]
                        for role, executable in (("ordinary", ordinary), ("observer", observer)):
                            child = directory(label + "/" + role, "Retained " + role + " BPM constructor")
                            inputs = prepare(child, fixture, kind)
                            if inputs != metadata_manifest["cases"][kind]["inputs_sha256"]:
                                raise RuntimeError("Supplied-bias fixture differs from declared derivative")
                            command = [executable, str(flag)]
                            if lane == "leaks" and role == "observer":
                                command = [leaks, "-quiet", "-atExit", "--", *command]
                            code, log = run(label + "-" + role, command, child, case_env)
                            output = log.read_text(errors="replace")
                            observed = dict(exit_status=code, input_sha256=inputs, findings=[],
                                            executable_sha256=digest(executable), log_sha256=digest(log),
                                            output_sha256={str(p.relative_to(child)): digest(p) for p in child.rglob("*")
                                                           if p.is_file() and p.name != "run-provenance.json"
                                                           and str(p.relative_to(child)) not in inputs})
                            # Output, supplied-bias lifetime and metadata verification.
                            try:
                                markers = re.findall(r"PASS: returned 9x9 mask good=(\d+)", output)
                                if (role == "ordinary" and code != 0) or markers != [str(prior["good"])]:
                                    raise RuntimeError("Native BPM completion/exit contract failed")
                                if re.findall(r"^BIAS RESULT supplied=1 pixels_unchanged=81 caller_released=1$", output, re.M) != ["BIAS RESULT supplied=1 pixels_unchanged=81 caller_released=1"]:
                                    raise RuntimeError("Supplied bias lifetime/content contract failed")
                                previous = ownership_cases[label]["roles"][role]["outputs"]
                                observed["outputs"], observed["generated_origfiles"] = verify(child, inputs, prior, flag, previous)
                                if role == "observer":
                                    rows = re.findall(r"^BPM RESULT native_exit=(\d+) constructed=(\d+) destroyed=(\d+) builds=(\d+) masks_released=(\d+) mismatch=(\d+) owner_live=(\d+) mask_live=(\d+)$", output, re.M)
                                    if rows != [("0", "1", "1", "1", "1", "0", "0", "0")]:
                                        raise RuntimeError("BPM context/mask owner contract failed")
                                    observed["ownership_contract"] = list(rows[0])
                                observed["functional_status"] = "passed"
                            except Exception as error:
                                observed["functional_status"] = "failed"
                                observed["findings"].append(str(error))
                                result["functional_status"] = "failed"
                            if "ERROR: AddressSanitizer" in output or "runtime error:" in output:
                                observed["findings"].append("invalid-access/undefined-behavior diagnostic")
                            # Resource, descriptor, double-purge and external-leak verification.
                            if role == "observer":
                                if code != 0:
                                    observed["findings"].append("Observer/tool nonzero exit")
                                try:
                                    for boundary in ("process-start", "after-context", "before-build", "after-build",
                                                     "after-mask-release", "after-context-release", "after-driver",
                                                     "after-purge", "after-second-purge"):
                                        state = allocation_state(output, boundary)
                                        observed[boundary + "_accounting"] = state
                                        if boundary in ("process-start", "after-purge", "after-second-purge") and any(state.values()):
                                            observed["findings"].append("unexplained live allocation/mapping at " + boundary)
                                    rows = re.findall(r"^DESCRIPTORS before=(\d+) after=(\d+) identity_equal=(\d+)$", output, re.M)
                                    if len(rows) != 1 or rows[0][0] != rows[0][1] or rows[0][2] != "1":
                                        raise RuntimeError("Descriptor observation incomplete/changed at driver return")
                                    observed["descriptors"] = list(rows[0])
                                    for boundary in ("after-purge", "after-second-purge"):
                                        rows = re.findall(r"^CACHE DESCRIPTORS " + boundary + r" before=(\d+) after=(\d+) identity_equal=(\d+)$", output, re.M)
                                        if len(rows) != 1 or rows[0][0] != rows[0][1] or rows[0][2] != "1":
                                            raise RuntimeError("Descriptor observation incomplete/changed at " + boundary)
                                        observed[boundary + "_descriptors"] = list(rows[0])
                                    limits = re.findall(r"^DESCRIPTOR LIMIT (before|after) soft=(\d+) hard=(\d+) soft_unlimited=(\d+)$", output, re.M)
                                    if len(limits) != 2 or [x[0] for x in limits] != ["before", "after"]:
                                        raise RuntimeError("Descriptor limit observation incomplete")
                                    observed["descriptor_limits"] = [list(x) for x in limits]
                                    if lane == "leaks":
                                        rows = re.findall(r"\b(\d+) leaks? for (\d+) total leaked bytes\b", output)
                                        if len(rows) != 1:
                                            raise RuntimeError("Unrecognized leaks summary")
                                        blocks, size = map(int, rows[0])
                                        observed.update(leaked_blocks=blocks, leaked_bytes=size)
                                        if blocks or size:
                                            observed["findings"].append("Unreachable allocation reported by leaks")
                                except Exception as error:
                                    observed["findings"].append(str(error))
                            observed["status"] = "failed" if observed["findings"] else "passed"
                            result["roles"][role] = observed
                            result["findings"].extend(role + ": " + f for f in observed["findings"])
                            save(child / "run-provenance.json", dict(observed, schema_version=1,
                                 tested_source=identity, parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                        left, right = result["roles"]["ordinary"], result["roles"]["observer"]
                        if left["input_sha256"] != right["input_sha256"] or left.get("outputs") != right.get("outputs"):
                            result["findings"].append("Original/observer inputs or numerical/header outputs differ")
                            result["functional_status"] = "failed"
                        result["status"] = "failed" if result["findings"] else "passed"
                        record["cases"].append(result)
                        save(case / "run-provenance.json", dict(result, schema_version=1,
                             tested_source=identity, parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                        save(provenance, record)
                        print(("PASS:" if result["status"] == "passed" else "FINDING:"), label,
                              "functional=" + result["functional_status"], flush=True)
        record["execution_complete"] = len(record["cases"]) == 16
        record["functional_finding_cases"] = sum(c["functional_status"] != "passed" for c in record["cases"])
        record["finding_cases"] = sum(c["status"] != "passed" for c in record["cases"])
        record["status"] = "passed" if record["execution_complete"] and not record["finding_cases"] else "failed"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        # Source/export/reference/installation preservation and final status.
        record["sources_unchanged"] = all(digest(repo / p) == h for p, h in sources.items())
        record["exported_sources_unchanged"] = all(
            (work / "source" / p).is_file() and digest(work / "source" / p) == h
            for p, h in sources.items())
        record["protected_files_unchanged"] = all(digest(Path(p)) == h for p, h in protected.items())
        record["ownership_reference_unchanged"] = digest(ownership_path) == ownership_hash
        record["reference_unchanged"] = digest(reference_path) == reference_hash
        record["checkout_unchanged"] = (git("rev-parse", "HEAD") == identity["commit"] and
                                       not git("status", "--porcelain", "--untracked-files=all"))
        if not all(record[k] for k in ("sources_unchanged", "exported_sources_unchanged",
                                       "protected_files_unchanged", "checkout_unchanged", "reference_unchanged", "ownership_reference_unchanged")):
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], completed_utc=record["completed_utc"])
                save(child, value)
    print("BPM SUPPLIED BIAS: cases=%d; finding cases=%d; complete=%s" %
          (len(record["cases"]), record.get("finding_cases", 0), record["execution_complete"]))
    print("REPORT:", provenance)
    print("Functional finding cases:", record.get("functional_finding_cases", "incomplete"))
    print("Resource/memory gate:", record["status"])
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
