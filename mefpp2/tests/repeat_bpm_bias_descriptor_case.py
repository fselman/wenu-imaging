"""Focused fresh-process diagnostic for #116; not S2-09 or new qualification.

Reuse the inspected C90 ASan/UBSan observer binary. Retain ten independent
retained-fixture/robust attempts, exact outputs and all descriptor/resource data.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import resource
import subprocess
import sys
import tempfile
from bpm_bias_cases import prepare, verify
from descriptor_snapshots import snapshots
from qualify_mac_leaks import digest, save
from qualify_split_ownership import allocation_state

REFERENCE_SHA256 = "eb7b590cd4993ecfb72224e51da2093da179d3be7fdd8299099f5d26f8539df5"
BINARY_SHA256 = "b89332ba536ee53e51ef13273cab88f515f0e09b46b94a8c58a903310bed3820"
CASE = "c90-instrumented-retained-flag0"


def observe(output, code):
    """Read the unchanged native completion, resource and descriptor contracts."""
    result = dict(findings=[], exit_status=code)
    if code != 0:
        result["findings"].append("Nonzero native exit")
    if "ERROR: AddressSanitizer" in output or "runtime error:" in output:
        result["findings"].append("ASan/UBSan diagnostic")
    if re.findall(r"^BIAS RESULT supplied=1 pixels_unchanged=81 caller_released=1$", output, re.M) != [
            "BIAS RESULT supplied=1 pixels_unchanged=81 caller_released=1"]:
        result["findings"].append("Missing/incorrect borrowed-bias completion")
    if re.findall(r"^PASS: returned 9x9 mask good=(\d+)$", output, re.M) != ["79"]:
        result["findings"].append("Missing/incorrect native mask completion")
    rows = re.findall(r"^BPM RESULT native_exit=(\d+) constructed=(\d+) destroyed=(\d+) builds=(\d+) masks_released=(\d+) mismatch=(\d+) owner_live=(\d+) mask_live=(\d+)$", output, re.M)
    if rows != [("0", "1", "1", "1", "1", "0", "0", "0")]:
        result["findings"].append("Context/mask ownership contract failed")
    limits = re.findall(r"^DESCRIPTOR LIMIT (before|after) soft=(\d+) hard=(\d+) soft_unlimited=(\d+)$", output, re.M)
    if len(limits) != 2 or [row[0] for row in limits] != ["before", "after"]:
        result["findings"].append("Missing/incomplete descriptor-limit observation")
    result["descriptor_limits"] = [list(row) for row in limits]
    # Parse every available boundary even when another observation fails.
    for boundary in ("process-start", "after-context", "before-build", "after-build",
                     "after-mask-release", "after-context-release", "after-driver",
                     "after-purge", "after-second-purge"):
        try:
            state = allocation_state(output, boundary)
            result[boundary + "_accounting"] = state
            if boundary in ("process-start", "after-purge", "after-second-purge") and any(state.values()):
                result["findings"].append("Unexplained tracked resource at " + boundary)
        except RuntimeError as error:
            result["findings"].append(str(error))
    try:
        result["descriptor_snapshots"] = snapshots(output)
        if any(result["descriptor_snapshots"]["changes"].values()):
            result["findings"].append("Descriptor identity changed")
    except RuntimeError as error:
        result["findings"].append(str(error))
    rows = re.findall(r"^DESCRIPTORS before=(\d+) after=(\d+) identity_equal=(\d+)$", output, re.M)
    if len(rows) != 1 or rows[0][0] != rows[0][1] or rows[0][2] != "1":
        result["findings"].append("Original descriptor gate failed at driver return")
    for phase in ("after-purge", "after-second-purge"):
        rows = re.findall(r"^CACHE DESCRIPTORS " + phase + r" before=(\d+) after=(\d+) identity_equal=(\d+)$", output, re.M)
        if len(rows) != 1 or rows[0][0] != rows[0][1] or rows[0][2] != "1":
            result["findings"].append("Original descriptor gate failed at " + phase)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    args = parser.parse_args()
    # Guards: known Mac/Python, clean source and lowered batch priority.
    if platform.system() != "Darwin" or platform.node().split(".")[0] != "MC02VV0HPHTDG":
        raise RuntimeError("STOP: run on the qualified Intel Mac")
    if Path(sys.prefix).resolve() != Path("/Users/fselman/anaconda3"):
        raise RuntimeError("STOP: unexpected Python environment")
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError("STOP: launch with nice -n 10")
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    repo = Path(__file__).resolve().parents[2]

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

    if git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("STOP: checkout must be clean")
    identity = dict(repository="https://github.com/fselman/wenu-imaging",
                    branch=git("symbolic-ref", "--short", "HEAD"), commit=git("rev-parse", "HEAD"), dirty=False)
    # Reference/binary protection: use only the inspected source and existing payload.
    reference_path = args.reference.expanduser().resolve(strict=True)
    committed = repo / "docs/developer/fixtures/mac-stage2-bpm-bias-inspected-2026-10-28/diagnostic-run-provenance.json"
    if digest(reference_path) != REFERENCE_SHA256 or digest(committed) != REFERENCE_SHA256:
        raise RuntimeError("STOP: inspected reference identity differs")
    reference = json.loads(reference_path.read_text())
    if reference["status"] != "passed" or not reference["execution_complete"]:
        raise RuntimeError("STOP: incomplete reference")
    case = next(c for c in reference["cases"] if c["case"] == CASE)
    previous = case["roles"]["observer"]
    executable = reference_path.parent / "build-c90-instrumented/bpm_ownership_probe"
    if digest(executable) != BINARY_SHA256 or previous["executable_sha256"] != BINARY_SHA256:
        raise RuntimeError("STOP: inspected native binary differs")
    sources = dict(reference["source_sha256"])
    for name, expected in sources.items():
        if digest(repo / name) != expected:
            raise RuntimeError("STOP: qualified source/fixture differs: " + name)
    sources[str(Path(__file__).resolve().relative_to(repo))] = digest(Path(__file__))
    protected = reference["protected_sha256"]
    if not all(digest(Path(p)) == h for p, h in protected.items()):
        raise RuntimeError("STOP: selected installation/configuration differs")
    fixture = repo / "mefpp2/tests/fixtures/bpm-cleanup"
    numerical = json.loads((repo / "docs/developer/fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json").read_text())
    prior = next(c for c in numerical["cases"] if c["case"] == "c90-retained-flag0")
    # Fresh retained directories/provenance: never reuse either original run.
    parent = Path.home() / "Software/build/wenu-imaging"
    if not parent.is_dir():
        raise RuntimeError("STOP: expected imaging build root absent")
    work = Path(tempfile.mkdtemp(prefix="mac-bpm-bias-descriptor-repeat-", dir=parent))
    provenance = work / "run-provenance.json"
    record = dict(schema_version=1, purpose="Ten independent-process attempts to reproduce #116",
                  tested_source=identity, native_source=reference["tested_source"], status="running",
                  created_utc=datetime.now(timezone.utc).isoformat(), execution_complete=False,
                  reference=str(reference_path), reference_sha256=REFERENCE_SHA256,
                  binary=str(executable), binary_sha256=BINARY_SHA256,
                  source_sha256=sources, protected_sha256=protected, commands=[], attempts=[],
                  retention_roles=["diagnostic_evidence"], installation_performed=False,
                  compilation_performed=False, observational_processing_performed=False,
                  same_process_repetition=False, issue116_closed=False,
                  limits=["One previously failing C90 ASan/UBSan case; no new full-suite qualification",
                          "Ten separate processes do not satisfy S2-09",
                          "No independent external-leaks lane; retain the inspected full-suite evidence",
                          "Nonreproduction does not explain the original mismatch or waive #116"])
    save(provenance, record)
    children = []
    print("WORK DIRECTORY:", work, flush=True)
    # Environment: reproduce the qualified instrumented lane, without inherited injections.
    env = os.environ.copy()
    for key in reference["removed_child_environment"]:
        env.pop(key, None)
    env.update(reference["lane_environment"]["instrumented"], E_DEBUG="0", E_VERBOSE="0")
    record["native_environment"] = dict(reference["lane_environment"]["instrumented"],
        E_DEBUG="0", E_VERBOSE="0", **{k: env.get(k) for k in (
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")})
    record["parent_niceness"] = os.getpriority(os.PRIO_PROCESS, 0)
    try:
        for index in range(1, 11):
            root = work / ("attempt-%02d" % index)
            root.mkdir()
            children.append(root / "run-provenance.json")
            save(root / "run-provenance.json", dict(tested_source=identity, parent=str(provenance),
                 purpose="Fresh-process retained/robust supplied-bias diagnostic", status="running"))
            # Stage exact accepted inputs; call the unchanged production-linked binary once.
            inputs = prepare(root, fixture, "retained")
            if inputs != previous["input_sha256"]:
                raise RuntimeError("STOP: diagnostic input identity differs")
            log = work / (root.name + ".log")
            command = dict(argv=[str(executable), "0"], cwd=str(root), log=str(log))
            record["commands"].append(command)
            save(provenance, record)
            try:
                with log.open("w") as stream:
                    process = subprocess.run(command["argv"], cwd=root, env=env, stdout=stream,
                                             stderr=subprocess.STDOUT, timeout=60)
                command["exit_status"] = process.returncode
            except BaseException as error:
                command["error"] = str(error)
                raise
            finally:
                command["log_sha256"] = digest(log) if log.is_file() else None
                save(provenance, record)
            # Output/resource verification: unchanged exact oracle plus all original gates.
            observed = observe(log.read_text(errors="replace"), process.returncode)
            observed.update(attempt=index, input_sha256=inputs)
            try:
                outputs, origfiles = verify(root, inputs, prior, 0, previous["outputs"])
                observed.update(outputs=outputs, generated_origfiles=origfiles)
            except Exception as error:
                observed["findings"].append("Product verification: " + str(error))
            observed["output_sha256"] = {p.name: digest(p) for p in root.iterdir()
                                         if p.is_file() and p.name not in inputs and p.name != "run-provenance.json"}
            observed["status"] = "finding" if observed["findings"] else "no-finding"
            record["attempts"].append(observed)
            save(root / "run-provenance.json", dict(observed, tested_source=identity,
                 parent=str(provenance), retention_roles=["diagnostic_evidence"]))
            save(provenance, record)
            print("ATTEMPT %02d: %s" % (index, observed["status"]), flush=True)
        record["execution_complete"] = True
        record["finding_attempts"] = sum(bool(a["findings"]) for a in record["attempts"])
        record["descriptor_change_attempts"] = sum(any(a.get("descriptor_snapshots", {}).get("changes", {}).values()) for a in record["attempts"])
        record["status"] = "diagnostic-findings" if record["finding_attempts"] else "diagnostic-complete-no-reproduction"
    except BaseException as error:
        record.update(status="failed-or-interrupted", error=str(error))
        raise
    finally:
        # Preservation: retain evidence even on error; verify original binary/reference/install/source.
        record["binary_unchanged"] = digest(executable) == BINARY_SHA256
        record["reference_unchanged"] = digest(reference_path) == REFERENCE_SHA256
        record["sources_unchanged"] = all(digest(repo / n) == h for n, h in sources.items())
        record["protected_files_unchanged"] = all(digest(Path(p)) == h for p, h in protected.items())
        record["checkout_unchanged"] = git("rev-parse", "HEAD") == identity["commit"] and not git("status", "--porcelain", "--untracked-files=all")
        if not all(record[k] for k in ("binary_unchanged", "reference_unchanged", "sources_unchanged",
                                       "protected_files_unchanged", "checkout_unchanged")):
            record["status"] = "preservation-failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)
        for child in children:
            value = json.loads(child.read_text())
            if value["status"] == "running":
                value.update(status=record["status"], parent_error=record.get("error"),
                             completed_utc=record["completed_utc"])
                save(child, value)
    print("DIAGNOSTIC:", record["status"], "attempts:", len(record["attempts"]),
          "finding attempts:", record.get("finding_attempts", "incomplete"))
    print("Descriptor-change attempts:", record.get("descriptor_change_attempts", "incomplete"))
    print("REPORT:", provenance)
    print("#116 remains open; this is not S2-09 or new full-suite acceptance.")
    return 0 if record["status"] == "diagnostic-complete-no-reproduction" else 1


if __name__ == "__main__":
    sys.exit(main())
