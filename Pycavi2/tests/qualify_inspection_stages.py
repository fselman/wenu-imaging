"""Guarded, retained actual-host qualification of the focused M3 inspector suite.

Run from an exact git archive; no installation, engine/solver or observations.
Refs #159/#179. Source checkout and configured installed files are protected even
when a synthetic contract fails. The test includes tiny client-body comparisons.
"""
import argparse
import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


def git(root, *args):
    return subprocess.check_output(["/usr/bin/git", "-C", str(root), *args], text=True).strip()


def identity(path):
    path = Path(path).resolve(strict=True)
    stat = path.stat()
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                mode=stat.st_mode, mtime_ns=stat.st_mtime_ns)


def checkout(root):
    return dict(root=str(root), head=git(root, "rev-parse", "HEAD"),
                branch=git(root, "symbolic-ref", "--short", "HEAD"),
                upstream=git(root, "rev-parse", "--abbrev-ref", "@{upstream}"),
                status=git(root, "status", "--porcelain=v1", "--untracked-files=all"),
                origin=git(root, "remote", "get-url", "origin"),
                push=git(root, "remote", "get-url", "--push", "origin"))


def protected_paths():
    # Installed packaging is nested on the actual hosts; do not guess its depth.
    spec = importlib.util.find_spec("pycavi")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError("Selected Python has no installed pycavi package")
    candidates = {p.resolve() for root in spec.submodule_search_locations
                  for p in Path(root).rglob("pycavi_associate_reduction.py")}
    if len(candidates) != 1:
        raise RuntimeError("Installed reduction module is missing or ambiguous")
    if not next(iter(candidates)).is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError("Reduction module is outside the selected installed environment")
    config = Path(os.environ.get("PYCAVI_ASTROSOFT_CONFIG", "~/.pycavi/pycavi_astrosoft.cfg")).expanduser().resolve(strict=True)
    parser = configparser.ConfigParser(interpolation=None)
    with config.open() as stream:
        parser.read_file(stream)
    selected = Path(parser.get("Paths", "mefpp").strip().strip('"')).expanduser()
    if not selected.is_absolute():
        raise RuntimeError("Configured mefpp location must be absolute")
    engine = selected / "bin/mefpp" if selected.is_dir() else selected
    return [next(iter(candidates)), config, engine.resolve(strict=True)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("mac", "chapman"), required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--work-parent", type=Path, required=True)
    args = parser.parse_args()
    machine = platform.node().split(".")[0]
    expected = {"mac": ("Darwin", "MC02VV0HPHTDG", "/Users/fselman/Developer/wenu-imaging"),
                "chapman": ("Linux", "chapman4", "/home1/fselman/Software/wenu-imaging")}[args.host]
    if (platform.system(), machine) != expected[:2]:
        raise RuntimeError("Wrong actual host; no workload started")
    root = args.checkout.resolve(strict=True)
    if root != Path(expected[2]).resolve(strict=True):
        raise RuntimeError("Wrong actual repository root")
    before = checkout(root)
    if before["branch"] != "main" or before["status"] or before["upstream"] != "origin/main":
        raise RuntimeError("Require clean main tracking origin/main; no checkout changes are made")
    allowed_origins = {"git@github.com:fselman/wenu-imaging.git",
                       "https://github.com/fselman/wenu-imaging.git",
                       "ssh://git@ssh.github.com:443/fselman/wenu-imaging.git"}
    if before["origin"] not in allowed_origins or before["push"] not in allowed_origins:
        raise RuntimeError("Unexpected actual repository origin")
    if git(root, "rev-parse", args.revision + "^{commit}") != args.revision:
        raise RuntimeError("Require exact full source revision")
    source = Path(__file__).resolve().parents[2]
    selected_python = Path(sys.executable).resolve()
    expected_python = Path("/Users/fselman/anaconda3/envs/wenu-imaging/bin/python" if args.host == "mac"
                           else "/home/fselman/.conda/envs/wenu-imaging/bin/python").resolve(strict=True)
    expected_prefix = Path("/Users/fselman/anaconda3/envs/wenu-imaging" if args.host == "mac"
                           else "/home/fselman/.conda/envs/wenu-imaging").resolve(strict=True)
    if (selected_python != expected_python or Path(sys.prefix).resolve() != expected_prefix or
            os.getpriority(os.PRIO_PROCESS, 0) < 10):
        raise RuntimeError("Require selected imaging Python and niceness >=10")
    # Source identity check: the exported test/client boundary equals this git object.
    relative = ["pyproject.toml", "Pycavi2/tests/project_inspection_contract.py",
                "Pycavi2/tests/qualify_inspection_stages.py",
                "Pycavi2/tests/fixtures/m3_inspection_legacy_clients.py",
                "Pycavi2/pycavi/pycavi_paths.py", "Pycavi2/pycavi/pycavi_project.py",
                "Pycavi2/pycavi/pycavi_product_paths.py", "Pycavi2/pycavi/pycavi_inspection_stages.py",
                "Pycavi2/pycavi/pycavi/pycavi_metadata.py", "Pycavi2/pycavi/pycavi/pycavi_solve.py",
                "Pycavi2/pycavi/pycavi/pycavi_associate_reduction.py",
                "Pycavi2/pycavi/config/omegacam.cfg", "Pycavi2/pycavi/config/wfi.cfg"]
    hashes = {}
    for name in relative:
        original = subprocess.check_output(["/usr/bin/git", "-C", str(root), "show", args.revision + ":" + name])
        actual = (source / name).read_bytes()
        if actual != original:
            raise RuntimeError("Export source mismatch: " + name)
        hashes[name] = hashlib.sha256(actual).hexdigest()
    protected = protected_paths()
    baseline = [identity(p) for p in protected]
    parent = args.work_parent.resolve(strict=True)
    run = Path(tempfile.mkdtemp(prefix=args.host + "-m3-inspector-stages-", dir=parent))
    report = dict(host=platform.platform(), hostname=machine, python=sys.executable,
                  source_revision=args.revision, source_root=str(source), source_sha256=hashes,
                  checkout_before=before, protected_before=baseline)
    print("RETAINED RUN:", run, flush=True)
    code = 1
    try:
        # Functional test: synthetic inspector checks and original/updated client bodies.
        # No installed production module, native engine, solver or observation is run.
        command = [sys.executable, "-B", str(source / "Pycavi2/tests/project_inspection_contract.py"),
                   "--work-parent", str(run)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1",
                   OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
        report["command"] = command
        with (run / "tests.log").open("w") as stream:
            code = subprocess.run(command, cwd=source, env=env, stdout=stream,
                                  stderr=subprocess.STDOUT).returncode
        report["exit"] = code
        receipts = list(run.glob("m3 project inspection */run-provenance.json"))
        if len(receipts) != 1:
            raise RuntimeError("Missing/ambiguous suite receipt")
        receipt = json.loads(receipts[0].read_text())
        report["suite"] = receipt
        if not receipt["successful"] or receipt["tests"] != 24:
            code = 1
        print((run / "tests.log").read_text(), flush=True)
    finally:
        # Preservation verification runs on success and test failure alike.
        try:
            report["checkout_after"] = checkout(root)
            report["protected_after"] = [identity(p) for p in protected]
            report["preserved"] = report["checkout_after"] == before and report["protected_after"] == baseline
        except Exception as exc:
            report["preserved"] = False
            report["preservation_error"] = repr(exc)
        (run / "run-provenance.json").write_text(json.dumps(report, indent=2) + "\n")
    if not report["preserved"]:
        raise RuntimeError("Protected checkout/installation changed; inspect retained evidence")
    if code:
        raise RuntimeError("Focused qualification failed; inspect retained evidence, do not retry blindly")
    print("PASS: 24 groups; actual checkout, installed module, configured engine/config preserved.", flush=True)


if __name__ == "__main__":
    main()
