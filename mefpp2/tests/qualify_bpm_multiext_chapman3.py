"""Chapman3 S2-05 two-extension OmegaCAM/WFI functional/accounting checks (#75/#116).

Unchanged Mac-qualified native observer, driver, fixtures and numerical oracle.
Uninstrumented target; compatible external diagnostics remain an open gate.
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
from bpm_multiext_cases import prepare, verify
from descriptor_snapshots import snapshots
from qualify_split_ownership import allocation_state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--cmake", type=Path, required=True)
    args = parser.parse_args()
    # Host/environment/source guards: no installation or source mutation.
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
    # Protect the selected engine/configuration and immutable accepted fixtures.
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
    # Load the exact selected-source inventory of the inspected successful Mac run.
    mac_path = repo / "docs/developer/fixtures/mac-stage2-bpm-multiext-inspected-2026-10-28/run-provenance.json"
    if digest(mac_path) != "95c9c352f8a92ba97d4cfc20e1b3341a4548c1b954e404c3c952967ec0efa430":
        raise RuntimeError("STOP: inspected Mac two-extension OmegaCAM/WFI report differs")
    names = sorted(json.loads(mac_path.read_text())["source_sha256"])
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
    metadata_path = mac_path
    metadata_hash = digest(metadata_path)
    if metadata_hash != "95c9c352f8a92ba97d4cfc20e1b3341a4548c1b954e404c3c952967ec0efa430":
        raise RuntimeError("STOP: two-extension OmegaCAM/WFI Mac reference differs from inspected report")
    metadata = json.loads(metadata_path.read_text())
    if (metadata["tested_source"]["commit"] != "cea3e927f0392d8ec6c97cd40afbac2878aca03f" or
            metadata["status"] != "passed" or not metadata["execution_complete"] or
            len(metadata["cases"]) != 32 or metadata["finding_cases"] != 0):
        raise RuntimeError("STOP: incomplete two-extension OmegaCAM/WFI Mac reference")
    for name, expected in metadata["source_sha256"].items():
        if sources.get(name) != expected:
            raise RuntimeError("STOP: Mac-qualified source/driver/fixture differs: " + name)
    metadata_cases = {c["case"].replace("-leaks-", "-functional-"): c
                       for c in metadata["cases"] if c["lane"] == "leaks"}
    if len(metadata_cases) != 16 or any(c["status"] != "passed" for c in metadata_cases.values()):
        raise RuntimeError("STOP: incomplete Mac functional reference")
    sources["mefpp2/tests/qualify_bpm_multiext_chapman3.py"] = digest(Path(__file__).resolve())
    metadata_manifest = json.loads((repo / "mefpp2/tests/fixtures/bpm-multiext/manifest.json").read_text())
    if metadata_manifest["parent_manifest_sha256"] != digest(repo / "mefpp2/tests/fixtures/bpm-metadata/manifest.json"):
        raise RuntimeError("STOP: metadata fixture parent changed")
    parent_path = repo / "docs/developer/fixtures/mac-stage2-bpm-metadata-2026-10-27/run-provenance.json"
    parent_hash = digest(parent_path)
    if parent_hash != "26868de58bd3a5c05c82304620d00549b79b2de605bd7bffcbeccd4faa9c308d":
        raise RuntimeError("STOP: original metadata contract changed")
    parent_cases = {c["case"]: c for c in json.loads(parent_path.read_text())["cases"]}
    # Retained provenance: fresh source/build/case/role directories before workload.
    root = Path.home() / "Software/build/wenu-imaging"
    if not root.is_dir():
        raise RuntimeError("STOP: expected imaging build root absent")
    work = Path(tempfile.mkdtemp(prefix="chapman3-stage2-bpm-multiext-", dir=root))
    provenance = work / "run-provenance.json"
    record = dict(schema_version=1, project="wenu-imaging", tested_source=identity,
                  host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
                  purpose="S2-05 target two-extension OmegaCAM/WFI functional/accounting verification",
                  prior_issue116_disposition="Original supplied-bias finding remains unresolved/open; no exclusions or reduced gates",
                  issue116_closed=False, full_S2_05_accepted=False,
                  diagnostic_scope="Uninstrumented target; no external sanitizer/leak-tool acceptance",
                  metadata_mac_reference=str(metadata_path),
                  metadata_mac_reference_sha256=metadata_hash,
                  mac_reference_report=str(reference_path), mac_reference_sha256=reference_hash,
                  fixture_manifest_sha256=digest(fixture / "manifest.json"),
                  metadata_fixture_manifest=metadata_manifest,
                  status="running", execution_complete=False, retention_roles=["acceptance_evidence"],
                  source_sha256=sources, protected_sha256=protected, commands=[], cases=[],
                  qualified_tool_reports_sha256=controls,
                  allocator=dict(XMEMORY_MODE=2, XMEMORY_MAXPTRS=2000000),
                  tool_sha256={str(p): digest(p) for p in (compiler, cmake)},
                  installation_performed=False, observational_processing_performed=False,
                  python=sys.executable, numpy=np.__version__, astropy=astropy.__version__,
                  limits=["Two synthetic OmegaCAM/WFI image extensions; not all detectors or observational acceptance",
                          "NULL bias in this slice; separate supplied-bias evidence preserved",
                          "#116 remains unresolved; stop on every finding and retain descriptor details",
                          "Two extension calls in one context are not S2-09 repeated-stage acceptance",
                          "Double purges retain and attribute original state; no unexplained live state waived",
                          "No allocation/I/O injection or general mmap/swap qualification",
                          "Compatible target external diagnostics remain pending; functional/accounting only"])
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
        wiring.write_text(wiring.read_text() + '\n# S2-05 private BPM ownership observers, not installed.\n'
                          'add_executable(bpm_original_probe tests/bpm_multiext_probe.c)\n'
                          'add_executable(bpm_ownership_probe tests/bpm_multiext_ownership_probe.c)\n'
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
        record["lane_environment"] = dict(functional={})
        save(provenance, record)
        # Tool inventory and private C90/C17 uninstrumented native builds.
        for label, command in (("compiler-version", [compiler, "--version"]),
                               ("cmake-version", [cmake, "--version"]),
                               ("os-version", ["uname", "-a"])):
            code, log = run(label, command, work, env)
            if code:
                raise RuntimeError("Tool inventory failed: " + str(log))
        for mode in (90, 17):
            for lane in ("functional",):
                tag = "c%d-%s" % (mode, lane)
                build = directory("build-" + tag, "Original BPM driver and metadata observer: " + tag)
                flags = "-O0 -g -fno-omit-frame-pointer"
                command = [cmake, "-S", source / "mefpp2", "-B", build, "-G", "Unix Makefiles",
                           "-DCMAKE_C_COMPILER=" + str(compiler),
                           "-DCMAKE_BUILD_TYPE=Debug",
                           "-DMEFPP_C_STANDARD=" + str(mode), "-DBUILD_TESTING=OFF", "-DMEFPP_BUILD_RESOURCES=OFF",
                           "-DMEFPP_SOURCE_REVISION=" + identity["commit"],
                           "-DCMAKE_C_FLAGS=" + flags, "-DCMAKE_EXE_LINKER_FLAGS="]
                for label, argv in (("configure-" + tag, command), ("build-" + tag,
                                     [cmake, "--build", build, "--target", "bpm_original_probe", "bpm_ownership_probe", "--parallel", "2"])):
                    code, log = run(label, argv, work, env)
                    if code:
                        raise RuntimeError("Build/configuration failed: " + str(log))
                info = json.loads((build / "build-info.json").read_text())
                if info["qfits_memory_mode"] != 2 or info["qfits_max_pointers"] != 2000000:
                    raise RuntimeError("Unexpected allocator policy")
                if int(info["c_standard"]) != mode or "-fsanitize" in info["c_flags"] + info["executable_linker_flags"]:
                    raise RuntimeError("Unexpected target language/instrumentation flags")
                inventory = json.loads((build / "compile_commands.json").read_text())
                if not inventory:
                    raise RuntimeError("Missing compile-command inventory")
                for unit in inventory:
                    command_text = unit.get("command", " ".join(unit.get("arguments", [])))
                    if "-std=c" + str(mode) not in command_text or "-fsanitize" in command_text:
                        raise RuntimeError("Target compilation flags differ from declared lane")
                ordinary, observer = build / "bpm_original_probe", build / "bpm_ownership_probe"
                case_env = env.copy()
                # Native processing: both instruments with unchanged Mac-qualified fixtures.
                for instrument in ("omegacam", "wfi"):
                    # Native processing: exact Mac-qualified two-extension fixtures and both producers.
                    for kind in ("retained", "known-response"):
                        for flag in (0, 1):
                            label = tag + "-" + instrument + "-" + kind + "-flag" + str(flag)
                            case = directory(label, "Paired original/observed BPM constructor")
                            result = dict(case=label, mode=mode, lane=lane, fixture=kind, proportional_flag=flag, instrument=instrument,
                                          roles={}, findings=[], functional_status="passed")
                            prior = references["c%d-%s-flag%d" % (mode, kind, flag)]
                            for role, executable in (("ordinary", ordinary), ("observer", observer)):
                                child = directory(label + "/" + role, "Retained " + role + " BPM constructor")
                                inputs = prepare(child, fixture, kind, instrument)
                                if inputs != metadata_manifest["cases"][instrument + "-" + kind]["inputs_sha256"]:
                                    raise RuntimeError("Derived metadata input differs from declared manifest")
                                command = [executable, str(flag)]
                                code, log = run(label + "-" + role, command, child, case_env)
                                output = log.read_text(errors="replace")
                                observed = dict(exit_status=code, input_sha256=inputs, findings=[],
                                                executable_sha256=digest(executable), log_sha256=digest(log),
                                                output_sha256={str(p.relative_to(child)): digest(p) for p in child.rglob("*")
                                                               if p.is_file() and p.name != "run-provenance.json"
                                                               and str(p.relative_to(child)) not in inputs})
                                # Products and ownership: exact Mac canonical outputs and input identities.
                                try:
                                    markers = re.findall(r"PASS: extension=([12]) returned 9x9 mask good=(\d+)", output)
                                    if (role == "ordinary" and code != 0) or markers != [("1", str(prior["good"])), ("2", str(prior["good"]))]:
                                        raise RuntimeError("Native BPM completion/exit contract failed")
                                    previous = metadata_cases[label]["roles"][role]
                                    observed["outputs"], observed["generated_origfiles"] = verify(child, inputs, prior, flag,
                                        parent_cases["c%d-leaks-%s-flag%d" % (mode, kind, flag)]["roles"][role]["outputs"],
                                        instrument, fixture, kind)
                                    if observed["outputs"] != previous["outputs"] or inputs != previous["input_sha256"]:
                                        raise RuntimeError("Target masks/headers/inputs differ from two-extension OmegaCAM/WFI Mac")
                                    if role == "observer":
                                        rows = re.findall(r"^BPM RESULT native_exit=(\d+) constructed=(\d+) destroyed=(\d+) builds=(\d+) masks_released=(\d+) mismatch=(\d+) owner_live=(\d+) mask_live=(\d+)$", output, re.M)
                                        if rows != [("0", "1", "1", "2", "2", "0", "0", "0")]:
                                            raise RuntimeError("BPM context/mask owner contract failed")
                                        observed["ownership_contract"] = list(rows[0])
                                    observed["functional_status"] = "passed"
                                except Exception as error:
                                    observed["functional_status"] = "failed"
                                    observed["findings"].append(str(error))
                                    result["functional_status"] = "failed"
                                # Resource/descriptor checks: no exclusions or relaxed gates.
                                if "ERROR: AddressSanitizer" in output or "runtime error:" in output:
                                    observed["findings"].append("invalid-access/undefined-behavior diagnostic")
                                if role == "observer":
                                    if code != 0:
                                        observed["findings"].append("Observer/tool nonzero exit")
                                    try:
                                        observed["descriptor_snapshots"] = snapshots(output)
                                        for boundary in ("process-start", "after-context", "before-build-1", "after-build-1",
                                                         "after-mask-release-1", "before-build-2", "after-build-2",
                                                         "after-mask-release-2", "after-context-release", "after-driver",
                                                         "after-purge", "after-second-purge"):
                                            state = allocation_state(output, boundary)
                                            observed[boundary + "_accounting"] = state
                                            if boundary in ("process-start", "after-purge", "after-second-purge") and any(state.values()):
                                                observed["findings"].append("unexplained live allocation/mapping at " + boundary)
                                        rows = re.findall(r"^DESCRIPTORS before=(\d+) after=(\d+) identity_equal=(\d+)$", output, re.M)
                                        if len(rows) != 1 or rows[0][0] != rows[0][1] or rows[0][2] != "1":
                                            raise RuntimeError("Descriptor observation incomplete/changed at driver return")
                                        observed["descriptors"] = list(rows[0])
                                        if any(observed["descriptor_snapshots"]["changes"].values()):
                                            raise RuntimeError("Per-descriptor identity changed; inspect descriptor_snapshots")
                                        for boundary in ("after-purge", "after-second-purge"):
                                            rows = re.findall(r"^CACHE DESCRIPTORS " + boundary + r" before=(\d+) after=(\d+) identity_equal=(\d+)$", output, re.M)
                                            if len(rows) != 1 or rows[0][0] != rows[0][1] or rows[0][2] != "1":
                                                raise RuntimeError("Descriptor observation incomplete/changed at " + boundary)
                                            observed[boundary + "_descriptors"] = list(rows[0])
                                        limits = re.findall(r"^DESCRIPTOR LIMIT (before|after) soft=(\d+) hard=(\d+) soft_unlimited=(\d+)$", output, re.M)
                                        if len(limits) != 2 or [x[0] for x in limits] != ["before", "after"]:
                                            raise RuntimeError("Descriptor limit observation incomplete")
                                        observed["descriptor_limits"] = [list(x) for x in limits]
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
                            if result["findings"]:
                                record["stopped_for_finding"] = True
                                raise RuntimeError("STOP: inspect retained target findings before further cases; report: " + str(provenance))
        record["execution_complete"] = len(record["cases"]) == 16
        record["functional_finding_cases"] = sum(c["functional_status"] != "passed" for c in record["cases"])
        record["finding_cases"] = sum(c["status"] != "passed" for c in record["cases"])
        record["status"] = "passed" if record["execution_complete"] and not record["finding_cases"] else "failed"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        # Preservation: export/source, references, protected installation and checkout.
        record["sources_unchanged"] = all(digest(repo / p) == h for p, h in sources.items())
        record["exported_sources_unchanged"] = all(
            (work / "source" / p).is_file() and digest(work / "source" / p) == h
            for p, h in sources.items())
        record["protected_files_unchanged"] = all(digest(Path(p)) == h for p, h in protected.items())
        record["metadata_mac_reference_unchanged"] = digest(metadata_path) == metadata_hash
        record["reference_unchanged"] = digest(reference_path) == reference_hash
        record["parent_metadata_reference_unchanged"] = digest(parent_path) == parent_hash
        record["checkout_unchanged"] = (git("rev-parse", "HEAD") == identity["commit"] and
                                       not git("status", "--porcelain", "--untracked-files=all"))
        if not all(record[k] for k in ("sources_unchanged", "exported_sources_unchanged",
                                       "protected_files_unchanged", "checkout_unchanged", "reference_unchanged", "metadata_mac_reference_unchanged", "parent_metadata_reference_unchanged")):
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], completed_utc=record["completed_utc"])
                save(child, value)
    print("TARGET BPM TWO EXTENSIONS: cases=%d; finding cases=%d; complete=%s" %
          (len(record["cases"]), record.get("finding_cases", 0), record["execution_complete"]))
    print("REPORT:", provenance)
    print("Functional finding cases:", record.get("functional_finding_cases", "incomplete"))
    print("Functional/accounting gate:", record["status"])
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
