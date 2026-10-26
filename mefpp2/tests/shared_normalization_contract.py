"""Run the Mac-qualified native fixture in an isolated, recorded test attempt."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, record):
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("fixtures", type=Path)
    parser.add_argument("kind", choices=("dome", "sky"))
    parser.add_argument("order", choices=("0", "1"))
    parser.add_argument("work_root", type=Path)
    parser.add_argument("source_revision")
    parser.add_argument("source_branch")
    args = parser.parse_args()
    executable = args.executable.resolve(strict=True)
    fixtures = args.fixtures.resolve(strict=True)
    manifest_path = fixtures / "transfer-manifest.json"
    manifest = json.loads(manifest_path.read_text())

    # Fixture identity: retain the exact qualified driver and synthetic inputs.
    for name, expected in manifest["files"].items():
        if digest(fixtures / name) != expected:
            raise RuntimeError("Qualified fixture changed: " + name)
    manifest_sha = digest(manifest_path)

    # Provenance and isolation: retain independent attempts, including failures.
    args.work_root.mkdir(parents=True, exist_ok=True)
    identity = {
        "repository": "https://github.com/fselman/wenu-imaging",
        "branch": None if args.source_branch == "unknown" else args.source_branch,
        "commit": None if args.source_revision == "unknown" else args.source_revision,
        "dirty": None,
        "identity_note": "CMake source identity; outer build record must capture dirty state",
    }
    container = args.work_root / "run-provenance.json"
    try:
        with container.open("x") as stream:
            json.dump({
                "schema_version": 1, "project": "wenu-imaging",
                "purpose": "Container for independent shared-normalization attempts",
                "tested_source": identity,
                "status": "incomplete", "status_note": "See each attempt for its result",
                "retention_roles": ["acceptance_evidence"],
            }, stream, indent=2)
            stream.write("\n")
    except FileExistsError:
        pass
    work = Path(tempfile.mkdtemp(
        prefix=args.kind + "-order" + args.order + "-", dir=args.work_root
    ))
    command = [str(executable), args.kind, args.order]
    record = {
        "schema_version": 1, "project": "wenu-imaging",
        "purpose": "Production mef_build_cal shared mosaic normalization",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "tested_source": identity, "kind": args.kind, "order": int(args.order),
        "commands": [command], "executable_sha256": digest(executable),
        "fixture_manifest_sha256": manifest_sha,
        "fixture_manifest": str(manifest_path),
        "inputs": {}, "status": "running",
        "retention_roles": ["acceptance_evidence"],
    }
    provenance = work / "run-provenance.json"
    save(provenance, record)
    print("Shared-normalization attempt:", work, flush=True)
    try:
        for source in sorted((fixtures / ("order-" + args.order)).iterdir()):
            if source.is_file():
                target = work / source.name
                shutil.copyfile(source, target)
                record["inputs"][source.name] = digest(target)
        save(provenance, record)

        # Native functional test: real constructor checks all 324 returned pixels.
        env = os.environ.copy()
        env.update(E_VERBOSE="0", E_DEBUG="0")
        log = work / "native.log"
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=work, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=60)
        record["exit_status"] = result.returncode
        output = log.read_text(errors="replace")
        if result.returncode or output.count("PASS: " + args.kind + " order=") != 4:
            raise RuntimeError("Native normalization failed:\n" + output[-8000:])

        # Preservation checks: neither staged nor repository fixtures may change.
        for name, expected in record["inputs"].items():
            if digest(work / name) != expected:
                raise RuntimeError("Staged fixture changed: " + name)
        for name, expected in manifest["files"].items():
            if digest(fixtures / name) != expected:
                raise RuntimeError("Repository fixture changed: " + name)
        if digest(manifest_path) != manifest_sha:
            raise RuntimeError("Fixture manifest changed")
        record.update(status="passed", pixels_checked=324,
                      fixtures_unchanged=True, log_sha256=digest(log))
        print(output, end="")
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(provenance, record)


if __name__ == "__main__":
    main()
