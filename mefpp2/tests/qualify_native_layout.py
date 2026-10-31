"""Private M4 qualification; tool arguments must follow docs/developer/selected-tools.md."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys
import tarfile


MAIN = "c4a5ba491b087e7e690ef6e53ed5ff2a250dd3ca"
TESTS = {"native_qfits_discovery", "native_layout", "native_bias_service", "native_explicit_paths"}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_tool(declared):
    require(declared.is_absolute(), "Require absolute tool paths")
    require(declared.is_file() and os.access(declared, os.X_OK), "Tool is not executable")
    # Tool entry points may dispatch by argv[0] (for example Xcode ar/ranlib).
    # Canonical identity is evidence only; do not substitute it for invocation.
    declared.resolve(strict=True)
    return declared


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("mac", "chapman"), required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--run", type=Path, required=True)
    for name in ("compiler", "cmake", "ctest", "make", "ar", "ranlib"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--sdk", type=Path)
    args = parser.parse_args()

    # Host/environment guards: no checkout changes, upgrades or installation.
    settings = {
        "mac": ("Darwin", "MC02VV0HPHTDG", "/Users/fselman/Developer/wenu-imaging",
                "/Users/fselman/anaconda3/envs/wenu-imaging"),
        "chapman": ("Linux", "chapman4", "/home1/fselman/Software/wenu-imaging",
                    "/home/fselman/.conda/envs/wenu-imaging"),
    }
    system, host, root, prefix = settings[args.host]
    require((platform.system(), platform.node().split(".")[0]) == (system, host), "Wrong host")
    require(Path(sys.prefix).resolve() == Path(prefix).resolve(), "Wrong environment")
    require(Path(sys.executable).resolve() == (Path(prefix) / "bin/python").resolve(), "Wrong Python")
    require(os.getpriority(os.PRIO_PROCESS, 0) >= 10, "Require niceness >=10")
    repo = Path(root).resolve(strict=True)

    def git(*parts):
        return subprocess.check_output(["/usr/bin/git", "-C", str(repo), *parts])

    require(Path(git("rev-parse", "--show-toplevel").decode().strip()).resolve() == repo, "Wrong checkout")
    require(len(args.revision) == 40 and git("rev-parse", args.revision + "^{commit}").decode().strip() == args.revision,
            "Expected exact fetched revision")
    require(Path(__file__).read_bytes() == git("show", args.revision + ":mefpp2/tests/qualify_native_layout.py"),
            "Runner differs from pinned source")
    guard_path = repo / "Pycavi2/tests/qualify_inspection_stages.py"
    require(guard_path.read_bytes() == git("show", MAIN + ":Pycavi2/tests/qualify_inspection_stages.py"),
            "Protection helper changed")
    guard = runpy.run_path(str(guard_path))
    checkout_before = guard["checkout"](repo)
    require(checkout_before["head"] == MAIN and checkout_before["branch"] == "main" and
            checkout_before["upstream"] == "origin/main" and not checkout_before["status"], "Expected clean main")
    origin = "git@github.com:fselman/wenu-imaging.git" if args.host == "mac" else "https://github.com/fselman/wenu-imaging.git"
    require(checkout_before["origin"] == origin and checkout_before["push"] == origin, "Unexpected origin")
    run = args.run.resolve(strict=True)
    require(not args.run.is_symlink() and run.parent == (Path.home() / "Software/build/wenu-imaging").resolve(),
            "Unexpected private run directory")
    require(not any(run.iterdir()) or {p.name for p in run.iterdir()} == {"qualify.py"}, "Run directory is not fresh")
    tools = {}
    # Invocation paths come from selected-tools.md, never PATH/xcrun rediscovery.
    for name in ("compiler", "cmake", "ctest", "make", "ar", "ranlib"):
        declared = getattr(args, name)
        tools[name] = selected_tool(declared)
    if args.host == "mac":
        require(args.sdk is not None and args.sdk.is_absolute() and args.sdk.is_dir(), "Require selected SDK")
    else:
        require(args.sdk is None, "SDK applies to Mac only")

    # Snapshot installed module, selected historical engine and configuration.
    protected = guard["protected_paths"]()
    installed_before = [guard["identity"](p) for p in protected]
    receipt = {"revision": args.revision, "host": host, "status": "running", "commands": [],
               "tool_sha256": {name: {"path": str(path), "resolved_path": str(path.resolve(strict=True)),
                                      "sha256": sha(path)} for name, path in tools.items()},
               "installation_performed": False, "observational_inputs": "none opened",
               "limits": ["synthetic discovery/layout/bias and existing native-path contracts only", "no observational/scientific/performance acceptance",
                          "no sanitizer or leak-tool claim on targets"]}
    print("RETAINED RUN:", run, flush=True)
    env = dict(os.environ, TMPDIR=str(run), PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1",
               OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    # Do not inherit compiler/linker selection or preload overrides.
    inherited = ("CC", "CXX", "CFLAGS", "CPPFLAGS", "LDFLAGS", "SDKROOT", "MACOSX_DEPLOYMENT_TARGET",
                 "CPATH", "C_INCLUDE_PATH", "LIBRARY_PATH", "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH",
                 "GCC_EXEC_PREFIX", "COMPILER_PATH", "CMAKE_GENERATOR", "CMAKE_TOOLCHAIN_FILE",
                 "LD_PRELOAD", "DYLD_INSERT_LIBRARIES")
    receipt["ignored_build_variables"] = {name: env[name] for name in inherited if name in env}
    for name in inherited:
        env.pop(name, None)

    def command(label, argv, timeout=600):
        log = run / (label + ".log")
        entry = {"label": label, "argv": list(map(str, argv)), "log": str(log)}
        receipt["commands"].append(entry)
        print("Running:", label, "| log:", log, flush=True)
        with log.open("x") as stream:
            result = subprocess.run(entry["argv"], cwd=run, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=timeout)
        entry["exit"] = result.returncode
        entry["sha256"] = sha(log)
        if result.returncode:
            print(log.read_text()[-12000:], flush=True)
        require(result.returncode == 0, "Failed: " + label)
        return log

    finished = False
    try:
        # Export exact tracked source privately; refuse unsafe archive members.
        archive = git("archive", "--format=tar", args.revision)
        receipt["archive_sha256"] = hashlib.sha256(archive).hexdigest()
        source = run / "source"
        source.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            for member in bundle.getmembers():
                name = Path(member.name)
                require(not name.is_absolute() and ".." not in name.parts and
                        (member.isdir() or member.isfile()), "Unsafe archive member")
            bundle.extractall(source)
        receipt["source_sha256"] = {
            str(p.relative_to(source)): sha(p) for p in sorted(source.rglob("*")) if p.is_file()}
        for standard in ("90", "17"):
            # Matched optimized lanes: private probes/engine, used only by synthetic contracts.
            build = run / ("build-c" + standard)
            configure = [tools["cmake"], "-S", source, "-B", build, "-G", "Unix Makefiles",
                         "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_C_FLAGS_RELEASE=-O2 -DNDEBUG",
                         "-DMEFPP_BUILD_RESOURCES=OFF", "-DMEFPP_BUILD_CONFIG_PROBES=ON",
                         "-DMEFPP_SOURCE_REVISION=" + args.revision, "-DMEFPP_C_STANDARD=" + standard,
                         "-DCMAKE_C_COMPILER=" + str(tools["compiler"]),
                         "-DCMAKE_MAKE_PROGRAM=" + str(tools["make"]),
                         "-DCMAKE_AR=" + str(tools["ar"]), "-DCMAKE_RANLIB=" + str(tools["ranlib"]),
                         "-DPython3_EXECUTABLE=" + sys.executable]
            if args.host == "mac":
                configure += ["-DCMAKE_OSX_ARCHITECTURES=x86_64", "-DCMAKE_OSX_SYSROOT=" + str(args.sdk)]
            command("configure-c" + standard, configure)
            command("build-c" + standard, [tools["cmake"], "--build", build, "--parallel", "2",
                                           "--target", "qfits_discovery_probe", "layout_probe", "bias_service_probe", "mefpp"])
            # Inventory four focused native contracts; all inputs are synthetic fixtures.
            selection = "^(native_qfits_discovery|native_layout|native_bias_service|native_explicit_paths)$"
            inventory = command("inventory-c" + standard,
                                [tools["ctest"], "--test-dir", build, "--show-only=json-v1", "-R", selection])
            require({t["name"] for t in json.loads(inventory.read_text())["tests"]} == TESTS,
                    "Unexpected test inventory")
            log = command("tests-c" + standard, [tools["ctest"], "--test-dir", build, "-R", selection,
                                                  "--output-on-failure", "--no-tests=error", "-j", "1"])
            print(log.read_text(), flush=True)
        finished = True
    finally:
        # Preserve installation, checkout and exported source on every exit.
        checks = {"installed_files": installed_before == [guard["identity"](p) for p in protected],
                  "checkout": checkout_before == guard["checkout"](repo)}
        if "source_sha256" in receipt:
            checks["exported_source"] = receipt["source_sha256"] == {
                str(p.relative_to(source)): sha(p) for p in sorted(source.rglob("*")) if p.is_file()}
        receipt["preservation"] = checks
        receipt["status"] = "passed" if finished and all(checks.values()) else "failed"
        with (run / "qualification.json").open("x") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")
        print("QUALIFICATION:", receipt["status"])
        print("PRESERVATION:", checks)
        print("RETAINED EVIDENCE:", run)
        require(all(checks.values()), "Preservation failed")


if __name__ == "__main__":
    main()
