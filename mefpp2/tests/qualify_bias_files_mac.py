"""Private M5 bias-template qualification (Mac or Chapman, C17 only); tool arguments must follow docs/developer/selected-tools.md."""
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


MAIN = "47123eedaaa31b4464238ffaaf1b690f7d2cde40"
MEASUREMENT_TESTS = {"native_measurement_stats", "native_bias_service", "native_bias_files", "native_eclipse_allocation"}
TESTS = {"native_operation_template", "native_bias_files", "native_layout", "native_bias_service", "native_explicit_paths"}


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
    parser.add_argument("--bias-only", action="store_true", help="Rebuild affected candidate and run only native_bias_files")
    parser.add_argument("--measurements", action="store_true", help="Run new numerical QC and affected bias/allocation contracts")
    for name in ("compiler", "cmake", "ctest", "make", "ar", "ranlib"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--sdk", type=Path)
    parser.add_argument("--candidate-checkout", action="store_true",
                        help="Chapman only: protect clean checked-out candidate instead of main")
    parser.add_argument("--private-install", action="store_true",
                        help="Install full normal runtime in run/install after the five contracts")
    parser.add_argument("--funpack", type=Path)
    args = parser.parse_args()
    require(not (args.measurements and (args.bias_only or args.private_install)), "Measurement gate is separate from legacy selections/install")
    require(not args.candidate_checkout or args.host == "chapman", "Candidate checkout is Chapman only")
    require(not args.private_install or (args.host == "chapman" and not args.bias_only and args.funpack),
            "Private install requires full Chapman gate and recorded funpack")

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
    require(Path(__file__).read_bytes() == git("show", args.revision + ":mefpp2/tests/qualify_bias_files_mac.py"),
            "Runner differs from pinned source")
    guard_path = repo / "Pycavi2/tests/qualify_inspection_stages.py"
    require(guard_path.read_bytes() == git("show", MAIN + ":Pycavi2/tests/qualify_inspection_stages.py"),
            "Protection helper changed")
    guard = runpy.run_path(str(guard_path))
    checkout_before = guard["checkout"](repo)
    expected_branch = "feat/m5-bias-template-20261102" if args.candidate_checkout else "main"
    expected_head = args.revision if args.candidate_checkout else MAIN
    require(checkout_before["head"] == expected_head and checkout_before["branch"] == expected_branch and
            checkout_before["upstream"] == "origin/" + expected_branch and not checkout_before["status"],
            "Expected exact clean protected checkout")
    origin = "git@github.com:fselman/wenu-imaging.git" if args.host == "mac" else "https://github.com/fselman/wenu-imaging.git"
    require(checkout_before["origin"] == origin and checkout_before["push"] == origin, "Unexpected origin")
    run = args.run.resolve(strict=True)
    build_root = (Path.home() / "Software/build/wenu-imaging").resolve()
    allowed_run = run.parent == build_root or (args.candidate_checkout and
                  run.name == "native" and run.parent.parent == build_root)
    require(not args.run.is_symlink() and allowed_run, "Unexpected private run directory")
    require(not any(run.iterdir()) or {p.name for p in run.iterdir()} == {"qualify.py"}, "Run directory is not fresh")
    install_prefix = run / "install"
    require(not install_prefix.exists(), "Private install prefix must be fresh")
    if args.private_install:
        selected_tool(args.funpack)
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
               "selection": "four measurement/bias/allocation contracts" if args.measurements else ("native_bias_files only" if args.bias_only else "five focused contracts"),
               "inherited_four_passes": "native f20a9ab7a0758775d020480be1e1daa547716e3b actual Mac run; not rerun" if args.bias_only else None,
               "limits": ["synthetic operation-template/file-bias/layout/bias/native-path contracts only", "no observational/scientific/performance acceptance",
                          "no sanitizer or leak-tool claim on targets"]}
    print("RETAINED RUN:", run, flush=True)
    env = dict(os.environ, TMPDIR=str(run), PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1",
               OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1",
               MEFPP_TEST_REVISION=args.revision)
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
        for standard in ("17",):
            # One optimized C17 build only, used by synthetic contracts.
            build = run / ("build-c" + standard)
            configure = [tools["cmake"], "-S", source, "-B", build, "-G", "Unix Makefiles",
                         "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_C_FLAGS_RELEASE=-O2 -DNDEBUG",
                         "-DMEFPP_BUILD_RESOURCES=" + ("ON" if args.private_install else "OFF"),
                         "-DMEFPP_BUILD_CONFIG_PROBES=ON",
                         "-DMEFPP_BUILD_BIAS_ADAPTER=ON",
                         "-DMEFPP_SOURCE_REVISION=" + args.revision, "-DMEFPP_C_STANDARD=" + standard,
                         "-DCMAKE_C_COMPILER=" + str(tools["compiler"]),
                         "-DCMAKE_MAKE_PROGRAM=" + str(tools["make"]),
                         "-DCMAKE_AR=" + str(tools["ar"]), "-DCMAKE_RANLIB=" + str(tools["ranlib"]),
                         "-DPython3_EXECUTABLE=" + sys.executable]
            if args.private_install:
                configure += ["-DMEFPP_FUNPACK=" + str(args.funpack),
                              "-DCMAKE_INSTALL_PREFIX=" + str(install_prefix)]
            if args.host == "mac":
                configure += ["-DCMAKE_OSX_ARCHITECTURES=x86_64", "-DCMAKE_OSX_SYSROOT=" + str(args.sdk)]
            command("configure-c" + standard, configure)
            targets = ["mefpp_m5", "mefpp"] if args.bias_only else [
                "operation_template_probe", "layout_probe", "bias_service_probe", "mefpp_m5", "mefpp"]
            if args.measurements:
                targets = ["measurement_stats_probe", "bias_service_probe", "eclipse_allocation_probe", "mefpp_m5", "mefpp"]
            if args.private_install:
                targets.append("mefpp_resources")
            command("build-c" + standard, [tools["cmake"], "--build", build, "--parallel", "2",
                                           "--target", *targets])
            # Inventory the selected focused contracts; all inputs are synthetic fixtures.
            selection = "^native_bias_files$" if args.bias_only else "^(native_operation_template|native_bias_files|native_layout|native_bias_service|native_explicit_paths)$"
            expected_tests = {"native_bias_files"} if args.bias_only else TESTS
            if args.measurements:
                expected_tests = MEASUREMENT_TESTS
                selection = "^(" + "|".join(sorted(expected_tests)) + ")$"
            inventory = command("inventory-c" + standard,
                                [tools["ctest"], "--test-dir", build, "--show-only=json-v1", "-R", selection])
            require({t["name"] for t in json.loads(inventory.read_text())["tests"]} == expected_tests,
                    "Unexpected test inventory")
            log = command("tests-c" + standard, [tools["ctest"], "--test-dir", build, "-R", selection,
                                                  "--output-on-failure", "--stop-on-failure", "--no-tests=error", "-j", "1"])
            print(log.read_text(), flush=True)
        if args.private_install:
            # Exercise the existing full runtime installer once, into a new prefix.
            command("install-c17", [tools["cmake"], "--install", build, "--prefix", install_prefix])
            receipt["installation_performed"] = True
            manifest = json.loads((install_prefix / "share/mefpp/build-manifest.json").read_text())
            require(manifest["installed_files"], "Empty installed manifest")
            for relative, expected in manifest["installed_files"].items():
                path = Path(relative)
                require(not path.is_absolute() and ".." not in path.parts, "Invalid installed path")
                require(sha(install_prefix / path) == expected, "Installed file hash mismatch: " + relative)
            require(sha(install_prefix / "bin/mefpp") == sha(build / "mefpp2/mefpp"),
                    "Installed/built engine mismatch")
            command("installed-cli", [tools["cmake"], "-DEXECUTABLE=" + str(install_prefix / "bin/mefpp"),
                                     "-P", source / "mefpp2/tests/cli_usage.cmake"])
            receipt["private_install"] = dict(prefix=str(install_prefix), manifest=manifest,
                normal_runtime_verified=True, bias_adapter_remains_opt_in=True,
                adapter_path=str(build / "mefpp2/mefpp_m5"))
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
