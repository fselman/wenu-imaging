"""Focused retained Mac C17 named ROI configuration qualification.

Purpose: read equivalent synthetic PAF/TOML plans using the existing parsers,
resolve named detector/amplifier identity independently of order, check active
bounds, overlap, strict schema, frozen source, atomic failures and allocation
cleanup. Build normal mefpp; do not process FITS or install anything. Exactly
one focused CTest entry must pass with checkout/install/export preserved.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys
import time

CMAKE = "/opt/local/bin/cmake"
CTEST = "/opt/local/bin/ctest"
PYTHON = "/Users/fselman/anaconda3/envs/wenu-imaging/bin/python"
ROOT = Path("/Users/fselman/Developer/wenu-imaging")
BASE = "c73d9a9e3a631fbbb2346beaa3c150c110a60343"


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def git(*args):
    return subprocess.check_output(["/usr/bin/git", "-C", str(ROOT), *args])


def digest_source(source):
    # Source and checked test boundaries, not generated build output.
    paths = [p for p in source.rglob("*") if p.is_file() and
             (p.suffix in (".c", ".h", ".py", ".cmake") or
              p.name in ("CMakeLists.txt", "pyproject.toml"))]
    return {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def execute(name, command, work, env, commands):
    log = work / (name + ".log")
    print("Running:", name, "| log:", log, flush=True)
    commands.append(dict(stage=name, argv=command, log=str(log)))
    with log.open("w") as output:
        process = subprocess.Popen(command, cwd=work, env=env, stdout=output,
                                   stderr=subprocess.STDOUT)
        # Poll with a timeout so sustained operations remain visible.
        while True:
            try:
                code = process.wait(timeout=30)
                break
            except subprocess.TimeoutExpired:
                print("Still running:", name, flush=True)
    if code:
        print(log.read_text()[-12000:], flush=True)
        raise RuntimeError(name + " failed; retain its log")
    return log


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--revision", required=True)
    p.add_argument("--run", type=Path, required=True)
    a = p.parse_args()
    require((platform.system(), platform.node().split(".")[0]) ==
            ("Darwin", "MC02VV0HPHTDG"), "Wrong actual Mac")
    require(Path(sys.executable).resolve() == Path(PYTHON).resolve() and
            Path(sys.prefix).resolve() == Path(PYTHON).parent.parent.resolve(),
            "Use normal installed imaging Python")
    require(os.getpriority(os.PRIO_PROCESS, 0) >= 10, "Use niceness >=10")
    require(len(a.revision) == 40 and
            git("rev-parse", a.revision + "^{commit}").decode().strip() == a.revision,
            "Require fetched exact source commit")
    work = a.run.resolve(strict=True)
    require(work.parent == Path("/Users/fselman/Software/build/wenu-imaging").resolve(),
            "Unexpected retained-run parent")
    require(set(q.name for q in work.iterdir()) == {"qualify.py"},
            "Fresh run may contain only the exported qualifier")
    require(Path(__file__).resolve() == work / "qualify.py", "Unexpected qualifier path")
    require((work / "qualify.py").read_bytes() ==
            git("show", a.revision + ":Pycavi2/tests/qualify_roi_config_mac.py"),
            "Qualifier differs from fetched source")

    # Exact archive extraction; no user-checkout update or installation.
    archive = work / "source.tar"
    archive.write_bytes(git("archive", "--format=tar", a.revision))
    source = work / "source"
    source.mkdir()
    subprocess.run(["/usr/bin/tar", "-xf", str(archive), "-C", str(source)], check=True)
    guard = runpy.run_path(str(source / "Pycavi2/tests/qualify_inspection_stages.py"))
    before = guard["checkout"](ROOT)
    require(before["head"] == BASE and before["branch"] == "main" and
            before["upstream"] == "origin/main" and not before["status"],
            "Require unchanged clean main at accepted base")
    require(before["origin"] == before["push"] ==
            "git@github.com:fselman/wenu-imaging.git", "Unexpected origin")
    protected = guard["protected_paths"]()
    installed = [guard["identity"](q) for q in protected]
    exported = digest_source(source)
    build = work / "build-c17"
    report = dict(status="running", source_revision=a.revision,
                  host=platform.platform(), python=sys.executable, commands=[],
                  checkout_before=before, installed_before=installed,
                  source_sha256=exported,
                  purpose="Synthetic named ROI configuration and binding software qualification only")
    print("RETAINED MAC ROI-CONFIG RUN:", work, flush=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1",
               OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    for key in ("CC", "CXX", "CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS"):
        env.pop(key, None)
    try:
        command = [CMAKE, "-S", str(source), "-B", str(build), "-G", "Unix Makefiles",
                   "-DCMAKE_C_COMPILER=/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang",
                   "-DCMAKE_OSX_SYSROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk",
                   "-DCMAKE_OSX_ARCHITECTURES=x86_64", "-DCMAKE_AR=/usr/bin/ar",
                   "-DCMAKE_RANLIB=/usr/bin/ranlib", "-DCMAKE_MAKE_PROGRAM=/usr/bin/make",
                   "-DCMAKE_C_FLAGS=", "-DCMAKE_EXE_LINKER_FLAGS=",
                   "-DCMAKE_BUILD_TYPE=Release", "-DMEFPP_C_STANDARD=17",
                   "-DMEFPP_BUILD_RESOURCES=OFF", "-DMEFPP_BUILD_BIAS_ADAPTER=ON",
                   "-DMEFPP_SOURCE_REVISION=" + a.revision,
                   "-DPython3_EXECUTABLE=" + PYTHON]
        execute("configure-c17", command, work, env, report["commands"])
        execute("build-c17", [CMAKE, "--build", str(build), "--target",
                "roi_config_probe", "mefpp", "-j", "2"],
                work, env, report["commands"])
        # Inventory prevents an empty/mismatched regex from passing silently.
        selection = "^native_roi_config$"
        inventory = subprocess.check_output([CTEST, "--test-dir", str(build),
                    "-N", "-R", selection, "--show-only=json-v1"], env=env, text=True)
        (work / "inventory-c17.json").write_text(inventory)
        names = {t["name"] for t in json.loads(inventory)["tests"]}
        require(names == {"native_roi_config"},
                "Unexpected focused test inventory")
        log = execute("tests-c17", [CTEST, "--test-dir", str(build), "-R", selection,
                      "--output-on-failure"], work, env, report["commands"])
        print(log.read_text(), flush=True)
        report["status"] = "passed"
    except Exception as exc:
        report.update(status="failed", error=repr(exc))
        raise
    finally:
        checks = {}
        for name, check in (
            ("checkout", lambda: guard["checkout"](ROOT) == before),
            ("installed_files", lambda: [guard["identity"](q) for q in protected] == installed),
            ("exported_source", lambda: digest_source(source) == exported)):
            try:
                checks[name] = check()
            except Exception as exc:
                checks[name] = False
                report.setdefault("preservation_errors", {})[name] = repr(exc)
        report["preservation"] = checks
        if not all(checks.values()):
            report["status"] = "failed"
        (work / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")
        print("QUALIFICATION:", report["status"], flush=True)
        print("PRESERVATION:", checks, flush=True)
    require(report["status"] == "passed", "Qualification/preservation failed")


if __name__ == "__main__":
    main()

