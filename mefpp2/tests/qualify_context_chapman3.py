"""Chapman3 functional/qfits-accounting verification of Mac-qualified contexts."""
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
import shutil
import subprocess
import sys
import tarfile
import tempfile
from qualify_mac_leaks import digest, save, accounting


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cmake", type=Path, required=True)
    parser.add_argument("--compiler", type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != "Linux" or platform.node().split(".")[0] != "chapman3":
        raise RuntimeError("STOP: run on Chapman3")
    if Path(sys.prefix).resolve() != (Path.home() / ".conda/envs/wenu-imaging").resolve():
        raise RuntimeError("STOP: unexpected Python environment")
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError("STOP: launch with nice -n 10")
    repo = Path(__file__).resolve().parents[2]

    def git(*argv):
        return subprocess.check_output(["git", *argv], cwd=repo, text=True).strip()

    if git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("STOP: checkout must be clean")
    identity = dict(repository="https://github.com/fselman/wenu-imaging",
                    branch=git("symbolic-ref", "--short", "HEAD"),
                    commit=git("rev-parse", "HEAD"), dirty=False)
    reference_path = repo / "docs/developer/fixtures/mac-stage2-context-corrected-2026-10-27/run-provenance.json"
    mac = json.loads(reference_path.read_text())
    if mac["status"] != "passed" or len(mac["cases"]) != 48:
        raise RuntimeError("STOP: accepted Mac reference is absent/incomplete")
    for name, expected in mac["source_sha256"].items():
        if digest(repo / name) != expected:
            raise RuntimeError("STOP: Mac-qualified source/driver/fixture changed: " + name)
    reference = {c["case"]: c for c in mac["cases"] if c["lane"] == "leaks"}
    compiler, cmake = args.compiler.resolve(strict=True), args.cmake.resolve(strict=True)
    config = Path(os.environ.get("PYCAVI_ASTROSOFT_CONFIG",
                                "~/.pycavi/pycavi_astrosoft.cfg")).expanduser().resolve(strict=True)
    settings = configparser.ConfigParser(interpolation=None)
    settings.read(config)
    engine = Path(settings["Paths"]["mefpp"].strip().strip('"')).expanduser()
    if not engine.is_absolute():
        engine = Path(shutil.which(str(engine)) or str(engine))
    engine = engine.resolve(strict=True)
    protected = {str(p): digest(p) for p in (config, engine)}
    root = Path.home() / "Software/build/wenu-imaging"
    if not root.is_dir():
        raise RuntimeError("STOP: expected imaging build root is absent")
    work = Path(tempfile.mkdtemp(prefix="chapman3-stage2-context-", dir=root))
    provenance = work / "run-provenance.json"
    record = dict(
        schema_version=1, project="wenu-imaging", tested_source=identity,
        host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
        purpose="S2-02 target context/PAF equivalence and qfits accounting",
        status="running", execution_complete=False, retention_roles=["acceptance_evidence"],
        diagnostic_scope="Uninstrumented functional/qfits bookkeeping; no external leak or sanitizer coverage",
        mac_reference_commit=mac["tested_source"]["commit"],
        mac_reference_sha256=digest(reference_path), source_sha256=mac["source_sha256"],
        tool_sha256={str(p): digest(p) for p in (compiler, cmake)},
        protected_sha256=protected, commands=[], cases=[],
        installation_performed=False, observational_processing_performed=False,
        limits=["Context/PAF only; no image/science processing or mef_engine calls",
                "No allocation injection, full repeat-stage, mapped/swap or external memory-tool acceptance"])
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

    def run(label, argv, cwd):
        log = work / (label + ".log")
        entry = dict(label=label, argv=list(map(str, argv)), cwd=str(cwd), log=str(log))
        record["commands"].append(entry)
        save(provenance, record)
        print("Running:", label, flush=True)
        env = os.environ.copy()
        env.update(E_VERBOSE="0", E_DEBUG="0")
        with log.open("w") as stream:
            result = subprocess.run(entry["argv"], cwd=cwd, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=600)
        entry.update(exit_status=result.returncode, log_sha256=digest(log))
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
            "\n# Unchanged Mac-qualified context diagnostic driver.\n"
            "add_executable(context_ownership_probe tests/context_ownership_probe.c)\n"
            "target_link_libraries(context_ownership_probe PRIVATE mefpp_common)\n")
        record["diagnostic_cmake_sha256"] = digest(wiring)
        kinds = [("valid-1", None, None, 1), ("valid-3", None, None, 3),
                 ("missing-count", "MEF.NCHIPS", None, 1),
                 ("missing-geometry", "MEF.CROP.Y.MAX.CHIP2", None, 1),
                 ("missing-final", "MEF.SATMAX", None, 1),
                 ("invalid-count", "MEF.NCHIPS", "junk", 1)]
        for mode in (90, 17):
            build = directory("build-c" + str(mode), "C%d uninstrumented target build" % mode)
            code, log = run("configure-c" + str(mode), [
                cmake, "-S", source / "mefpp2", "-B", build, "-G", "Unix Makefiles",
                "-DCMAKE_C_COMPILER=" + str(compiler), "-DCMAKE_BUILD_TYPE=Debug",
                "-DCMAKE_C_FLAGS=-O0 -g", "-DCMAKE_EXE_LINKER_FLAGS=",
                "-DMEFPP_C_STANDARD=" + str(mode), "-DBUILD_TESTING=OFF",
                "-DMEFPP_BUILD_RESOURCES=OFF", "-DMEFPP_SOURCE_REVISION=" + identity["commit"]], work)
            if code:
                raise RuntimeError("Configuration failed; see " + str(log))
            code, log = run("build-c" + str(mode), [cmake, "--build", build, "--target",
                                                 "context_ownership_probe", "--parallel", "2"], work)
            if code:
                raise RuntimeError("Build failed; see " + str(log))
            info = json.loads((build / "build-info.json").read_text())
            if info["qfits_memory_mode"] != 2 or info["qfits_max_pointers"] != 2000000:
                raise RuntimeError("Unexpected allocator policy")
            executable = build / "context_ownership_probe"
            for instrument, chips in (("omegacam", 32), ("wfi", 8)):
                original = (source / ("mefpp2/ins/mef/config/" + instrument + ".paf")).read_text()
                for kind, key, replacement, repeats in kinds:
                    label = "c%d-functional-%s-%s" % (mode, instrument, kind)
                    mac_key = "c%d-leaks-%s-%s" % (mode, instrument, kind)
                    expected = reference[mac_key]
                    case = directory(label, "Native context/PAF contract and cleanup observation")
                    text = original
                    if key is not None:
                        lines = original.splitlines()
                        matches = [i for i, line in enumerate(lines) if line.split() and line.split()[0] == key]
                        if len(matches) != 1:
                            raise RuntimeError("Unexpected fixture key: " + key)
                        index = matches[0]
                        if replacement is None:
                            del lines[index]
                        else:
                            lines[index] = key + " " + replacement + ";"
                        text = "\n".join(lines) + "\n"
                    paf = case / "context.paf"
                    paf.write_text(text)
                    input_hash = digest(paf)
                    if input_hash != expected["input_sha256"]:
                        raise RuntimeError("Target PAF differs from Mac: " + label)
                    code, log = run(label, [executable, paf.name, str(chips if key is None else 0), str(repeats)], case)
                    output = log.read_text(errors="replace")
                    result = dict(case=label, mac_reference_case=mac_key, instrument=instrument,
                                  variant=kind, repeats=repeats, input_sha256=input_hash,
                                  executable_sha256=digest(executable), log_sha256=digest(log),
                                  exit_status=code, status="failed", findings=[])
                    try:
                        if code or output.count("CONTEXT COMPLETE repeats=" + str(repeats)) != 1:
                            raise RuntimeError("Native completion/exit mismatch")
                        native = re.findall(r"CONTEXT RESULT iteration=(\d+) created=(\d+) chips=(\d+)", output)
                        native_expected = [(str(i), "1" if key is None else "0",
                                            str(chips if key is None else 0)) for i in range(1, repeats+1)]
                        if native != native_expected:
                            raise RuntimeError("Constructor result mismatch")
                        config_lines = re.findall(r"^CONFIG .*", output, re.M)
                        if config_lines != expected["configuration_lines"]:
                            raise RuntimeError("Mac/target context values differ")
                        result.update(context_contract="passed", configuration_lines=config_lines,
                                      matches_mac=True)
                        snapshots = {name: accounting(output, name) for name in
                                     ["process-start", "baseline", "final"] +
                                     ["after-" + str(i) for i in range(1, repeats+1)]}
                        result["accounting"] = snapshots
                        if any(s != {"pointers": 0, "bytes": 0} for s in snapshots.values()):
                            raise RuntimeError("Nonzero target ownership snapshot")
                        if digest(paf) != input_hash:
                            raise RuntimeError("Staged input changed")
                        result["status"] = "passed"
                    except Exception as error:
                        result["findings"].append(str(error))
                    record["cases"].append(result)
                    save(case / "run-provenance.json", dict(result, schema_version=1, tested_source=identity,
                         parent_manifest=str(provenance), retention_roles=["acceptance_evidence"]))
                    save(provenance, record)
                    print(("PASS:" if result["status"] == "passed" else "FINDING:"), label,
                          "Mac values match; cleanup zero" if result["status"] == "passed" else "see retained log",
                          flush=True)
        record["execution_complete"] = True
        record["finding_cases"] = sum(c["status"] != "passed" for c in record["cases"])
        record["status"] = "failed" if record["finding_cases"] else "passed"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        record["sources_unchanged"] = all(digest(repo / p) == h for p, h in mac["source_sha256"].items())
        record["mac_reference_unchanged"] = digest(reference_path) == record["mac_reference_sha256"]
        record["protected_files_unchanged"] = all(digest(Path(p)) == h for p, h in protected.items())
        record["checkout_unchanged"] = (git("rev-parse", "HEAD") == identity["commit"] and
                                       not git("status", "--porcelain", "--untracked-files=all"))
        if not all(record[k] for k in ("sources_unchanged", "mac_reference_unchanged",
                                      "protected_files_unchanged", "checkout_unchanged")):
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], completed_utc=record["completed_utc"])
                save(child, value)
    print("TARGET CONTEXT: cases=%d; finding cases=%d; complete=%s" %
          (len(record["cases"]), record.get("finding_cases", 0), record["execution_complete"]))
    print("REPORT:", provenance)
    print("Functional/accounting gate:", record["status"])
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
