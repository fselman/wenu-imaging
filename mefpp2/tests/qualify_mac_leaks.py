"""Qualify Mac leaks reachability and qfits RAM accounting, not application memory."""
import argparse
from datetime import datetime, timezone
import configparser
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def accounting(output, label):
    blocks = re.findall(r"ACCOUNTING BEGIN " + label + r"\n(.*?)ACCOUNTING END " + label,
                        output, re.S)
    if len(blocks) != 1:
        raise RuntimeError("Missing/duplicate accounting boundary: " + label)
    block = blocks[0]
    if "SWP_alloc" in block or "MAP_files" in block:
        raise RuntimeError("Control left the declared RAM-only lane")
    counts = re.findall(r"^ALL_npointers\s+(\d+)\s*$", block, re.M)
    sizes = re.findall(r"^ALL_size\s+(\d+)\s*$", block, re.M)
    if not counts and not sizes:
        if block.strip():
            raise RuntimeError("Unexpected zero-accounting output")
        return {"pointers": 0, "bytes": 0}
    if len(counts) != 1 or len(sizes) != 1:
        raise RuntimeError("Unrecognized allocator accounting")
    return {"pointers": int(counts[0]), "bytes": int(sizes[0])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--sdk", type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != "Darwin" or platform.node().split(".")[0] != "MC02VV0HPHTDG":
        raise RuntimeError("STOP: run on the qualified Intel Mac")
    if Path(sys.prefix).resolve() != Path("/Users/fselman/anaconda3"):
        raise RuntimeError("STOP: unexpected Python environment")
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError("STOP: use nice -n 10 for this batch")
    repo = Path(__file__).resolve().parents[2]

    def git(*argv):
        return subprocess.check_output(["git", *argv], cwd=repo, text=True).strip()

    if git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("STOP: checkout must be clean")
    identity = dict(repository="https://github.com/fselman/wenu-imaging",
                    branch=git("symbolic-ref", "--short", "HEAD"),
                    commit=git("rev-parse", "HEAD"), dirty=False)
    compiler = args.compiler.resolve(strict=True)
    sdk = args.sdk.resolve(strict=True)
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
    sources = {
        "leak_controls.c": repo / "mefpp2/tests/leak_controls.c",
        "xmemory.c": repo / "mefpp2/qfits5/src/xmemory.c",
        "xmemory.h": repo / "mefpp2/qfits5/include/xmemory.h",
    }
    source_hashes = {name: digest(p) for name, p in sources.items()}
    root = Path.home() / "Software/build/wenu-imaging"
    if not root.is_dir():
        raise RuntimeError("STOP: imaging build root is absent")
    work = Path(tempfile.mkdtemp(prefix="mac-stage2-leak-controls-", dir=root))
    record = dict(
        schema_version=1, project="wenu-imaging", tested_source=identity,
        host=platform.node(), created_utc=datetime.now(timezone.utc).isoformat(),
        purpose="Qualify leaks reachability and qfits allocation accounting",
        status="running", retention_roles=["acceptance_evidence"],
        compiler=str(compiler), sdk=str(sdk), leaks=str(leaks),
        tool_sha256={str(p): digest(p) for p in (compiler, leaks)},
        source_sha256=source_hashes, protected_sha256=protected,
        allocator={"XMEMORY_MODE": 2, "XMEMORY_MAXPTRS": 2000000, "XMEMORY_DEBUG": 0},
        diagnostic_environment={"MallocStackLogging": "lite", "MallocScribble": "1"},
        removed_child_environment=["ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS",
                                   "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH",
                                   "MallocStackLoggingNoCompact"],
        commands=[], cases=[], installation_performed=False,
        observational_processing_performed=False,
        limits=["Uninstrumented diagnostic controls, not production memory acceptance",
                "Small RAM allocations only; mapped/swap paths unqualified",
                "Reachability is distinct from ownership; no suppression/exclusion rules",
                "Existing invalid-access controls are not repeated"])
    provenance = work / "run-provenance.json"
    save(provenance, record)
    children = []
    print("WORK DIRECTORY:", work, flush=True)

    def directory(name, role):
        path = work / name
        path.mkdir()
        child = path / "run-provenance.json"
        save(child, dict(schema_version=1, project="wenu-imaging",
                         tested_source=identity, parent_manifest=str(provenance),
                         purpose=role, status="running",
                         retention_roles=["acceptance_evidence"]))
        children.append(child)
        return path

    def run(label, argv, cwd, env=None):
        log = work / (label + ".log")
        entry = dict(label=label, argv=list(map(str, argv)), cwd=str(cwd), log=str(log))
        record["commands"].append(entry)
        save(provenance, record)
        print("Running:", label, flush=True)
        with log.open("w") as stream:
            result = subprocess.run(entry["argv"], cwd=cwd, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=120)
        entry.update(exit_status=result.returncode, log_sha256=digest(log))
        save(provenance, record)
        return result.returncode, log

    try:
        source = directory("source", "Unchanged allocator sources and diagnostic driver")
        for name, path in sources.items():
            shutil.copyfile(path, source / name)
            if digest(source / name) != source_hashes[name]:
                raise RuntimeError("Source copy mismatch: " + name)
        code, _ = run("compiler-version", [compiler, "--version"], work)
        if code:
            raise RuntimeError("Compiler inventory failed")
        code, _ = run("os-version", ["/usr/bin/sw_vers"], work)
        if code:
            raise RuntimeError("OS inventory failed")
        for mode in (90, 17):
            build = directory("build-c" + str(mode), "Uninstrumented C%d control executable" % mode)
            executable = build / "leak_controls"
            command = [compiler, "-std=c" + str(mode), "-isysroot", sdk,
                       "-D_DARWIN_C_SOURCE=1", "-DXMEMORY_MODE=2",
                       "-DXMEMORY_MAXPTRS=2000000", "-DXMEMORY_DEBUG=0",
                       "-g", "-O0", "-fno-omit-frame-pointer", "-I", source,
                       source / "leak_controls.c", source / "xmemory.c", "-o", executable]
            code, log = run("compile-c" + str(mode), command, build)
            if code:
                raise RuntimeError("Compilation failed; see " + str(log))
            for kind in ("system-clean", "system-unreachable", "system-rooted",
                         "qfits-clean", "qfits-registered"):
                label = "c%d-%s" % (mode, kind)
                case = directory(label, "Independent leaks/accounting control process")
                env = os.environ.copy()
                for key in record["removed_child_environment"]:
                    env.pop(key, None)
                env.update(record["diagnostic_environment"])
                code, log = run(label, [leaks, "-quiet", "-atExit", "--", executable, kind],
                                case, env)
                output = log.read_text(errors="replace")
                if output.count("CONTROL COMPLETE " + kind) != 1:
                    raise RuntimeError("Control did not complete; see " + str(log))
                initial = accounting(output, "initial")
                final = accounting(output, "final")
                if initial != {"pointers": 0, "bytes": 0}:
                    raise RuntimeError("Nonzero initial allocator state; see " + str(log))
                expected = {"pointers": 1, "bytes": 8192} if kind == "qfits-registered" else {"pointers": 0, "bytes": 0}
                if final != expected:
                    raise RuntimeError("Unexpected final accounting; see " + str(log))
                if kind.startswith("qfits-") and accounting(output, "allocated") != {"pointers": 1, "bytes": 8192}:
                    raise RuntimeError("Allocator did not observe the control block; see " + str(log))
                summaries = re.findall(r"\b(\d+) leaks? for (\d+) total leaked bytes\b", output)
                if len(summaries) != 1:
                    raise RuntimeError("Unrecognized leaks summary; see " + str(log))
                leak_count, leak_bytes = map(int, summaries[0])
                expected_exit = 1 if kind == "system-unreachable" else 0
                if code != expected_exit:
                    raise RuntimeError("Unexpected leaks exit status; see " + str(log))
                if kind == "system-unreachable":
                    if leak_count < 1 or leak_bytes < 8192:
                        raise RuntimeError("Known unreachable block not detected; see " + str(log))
                elif leak_count or leak_bytes:
                    raise RuntimeError("Unexpected leak finding; see " + str(log))
                result = dict(case=label, status="passed", leaks_exit=code,
                              leaked_blocks=leak_count, leaked_bytes=leak_bytes,
                              initial_accounting=initial, final_accounting=final,
                              executable_sha256=digest(executable),
                              log_sha256=digest(log))
                record["cases"].append(result)
                save(case / "run-provenance.json", dict(result, schema_version=1,
                     tested_source=identity, parent_manifest=str(provenance),
                     retention_roles=["acceptance_evidence"]))
                save(provenance, record)
                print("PASS:", label, "leaks=%d bytes=%d; qfits live=%d bytes=%d" %
                      (leak_count, leak_bytes, final["pointers"], final["bytes"]), flush=True)
        record["status"] = "passed"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        record["allocator_sources_unchanged"] = all(digest(p) == source_hashes[n]
                                                   for n, p in sources.items())
        record["protected_files_unchanged"] = all(digest(Path(p)) == h
                                                 for p, h in protected.items())
        record["checkout_unchanged"] = (git("rev-parse", "HEAD") == identity["commit"]
                                       and not git("status", "--porcelain", "--untracked-files=all"))
        if not all(record[k] for k in ("allocator_sources_unchanged", "protected_files_unchanged", "checkout_unchanged")):
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], completed_utc=record["completed_utc"])
                save(child, value)
    if record["status"] != "passed":
        raise RuntimeError("Preservation check failed")
    print("PASS: ten tool controls; application leak qualification remains pending.")
    print("REPORT:", provenance)


if __name__ == "__main__":
    main()
