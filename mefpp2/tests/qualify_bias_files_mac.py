"""Private M5 qualification (bias or response core, C17); selected-tools.md governs tool arguments."""
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
FILE_QC_TESTS = {"native_bias_qc_asdf", "shared_qc_asdf", "native_bias_files", "native_bias_service", "native_layout", "native_eclipse_allocation"}
QC_PYTHON = Path("/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python")
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


QUALIFIED_BIAS = "eeacca38346a2d09d88e262513abda189d6b01e3"


def reuse_bias_adapter(old, source, git, tool_hashes):
    """Fail closed unless the accepted C17 binary and its native source match."""
    old = old.resolve(strict=True)
    report_path = old / "qualification.json"
    report = json.loads(report_path.read_text())
    require(report["revision"] == QUALIFIED_BIAS and report["status"] == "passed" and
            report["preservation"] == dict(installed_files=True, checkout=True,
                exported_source=True, retained_qc_controls=True), "Unqualified retained native run")
    require(report["tool_sha256"] == tool_hashes, "Selected native tools changed")
    configure = next(c for c in report["commands"] if c["label"] == "configure-c17")
    tests = next(c for c in report["commands"] if c["label"] == "tests-c17")
    require(configure["exit"] == tests["exit"] == 0 and "-DMEFPP_C_STANDARD=17" in configure["argv"],
            "Retained native lane is not passed C17")
    tests_log = Path(tests["log"]).resolve(strict=True)
    require(tests_log.is_relative_to(old) and sha(tests_log) == tests["sha256"], "Retained test evidence changed")
    archive = git("archive", "--format=tar", QUALIFIED_BIAS)
    require(hashlib.sha256(archive).hexdigest() == report["archive_sha256"], "Retained source archive mismatch")
    def native(name):
        path = Path(name)
        return path.suffix in (".c", ".h", ".def", ".cmake") or path.name == "CMakeLists.txt"
    native_hashes = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle.getmembers():
            if member.isfile() and native(member.name):
                require(not Path(member.name).is_absolute() and '..' not in Path(member.name).parts, "Unsafe native source name")
                native_hashes[member.name] = hashlib.sha256(bundle.extractfile(member).read()).hexdigest()
    current = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file() and native(p.name)}
    require(native_hashes and current == set(native_hashes), "Native source/build inventory changed")
    for name, digest in native_hashes.items():
        require(report["source_sha256"].get(name) == digest == sha(old/"source"/name) == sha(source/name),
                "Native code/build input changed; cannot reuse: " + name)
    adapter = old/"build-c17/mefpp2/mefpp_m5"
    require(adapter.is_file() and not adapter.is_symlink(), "Missing retained adapter")
    proofs = []
    for path in (old/"build-c17/mefpp2/test-work").glob("m5-bias-*/qualification.json"):
        proof = json.loads(path.read_text())
        if proof.get("status") == "passed" and proof.get("source_revision") == QUALIFIED_BIAS and any(
                c.get("argv", [None])[0] == str(adapter) and c.get("exit_status") == 0 for c in proof.get("commands", [])):
            require(proof["adapter_sha256"] == sha(adapter), "Qualified adapter bytes changed")
            proofs.append(path)
    require(len(proofs) == 1, "Require one matching passed native binary proof")
    controls = {str(p): sha(p) for p in (report_path, tests_log, adapter, proofs[0])}
    return adapter, dict(run=str(old), revision=QUALIFIED_BIAS, controls=controls,
                        native_source_files=len(native_hashes), adapter_sha256=sha(adapter))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("mac", "chapman"), required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--bias-only", action="store_true", help="Rebuild affected candidate and run only native_bias_files")
    parser.add_argument("--measurements", action="store_true", help="Run new numerical QC and affected bias/allocation contracts")
    parser.add_argument("--bpm-response", action="store_true", help="Mac: checked Eclipse response and exact 8-bit mask core only")
    parser.add_argument("--bpm-service", action="store_true", help="Mac: typed BPM numerical composition and operation-template contracts")
    parser.add_argument("--file-qc", action="store_true", help="Mac BPM file-to-ASDF handoff and affected contracts")
    parser.add_argument("--qc-python", type=Path)
    parser.add_argument("--complete-bias", action="store_true", help="Only the one-command completion contract; reuse qualified C17 native code")
    parser.add_argument("--reuse-native-run", type=Path)
    for name in ("compiler", "cmake", "ctest", "make", "ar", "ranlib"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--sdk", type=Path)
    parser.add_argument("--candidate-checkout", action="store_true",
                        help="Chapman only: protect clean checked-out candidate instead of main")
    parser.add_argument("--private-install", action="store_true",
                        help="Install full normal runtime in run/install after the five contracts")
    parser.add_argument("--funpack", type=Path)
    args = parser.parse_args()
    require(not (args.bpm_response and args.bpm_service), "Choose one BPM increment")
    require(not (args.bpm_response or args.bpm_service) or (args.host == "mac" and not any((args.complete_bias,
            args.file_qc, args.measurements, args.bias_only, args.private_install,
            args.candidate_checkout, args.qc_python, args.reuse_native_run))),
            "BPM core/service requires the separate private Mac C17 gate")
    require(not args.complete_bias or (args.host == "mac" and not args.file_qc and
            not args.measurements and not args.bias_only and not args.private_install and
            args.qc_python == QC_PYTHON and args.reuse_native_run is not None), "Completion gate requires qualified retained Mac/native runs")
    require(args.complete_bias or args.reuse_native_run is None, "Native reuse is completion-only")
    require(not args.file_qc or (args.host == "mac" and not args.measurements and not args.bias_only and
            not args.private_install and args.qc_python == QC_PYTHON), "File/QC gate requires the retained Mac ASDF Python")
    require(args.file_qc or args.complete_bias or args.qc_python is None, "QC Python requires a QC/completion gate")
    if args.file_qc or args.complete_bias:
        selected_tool(args.qc_python)
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
               "selection": "typed BPM service and operation-template contracts" if args.bpm_service else "checked response/8-bit mask and existing measurement contracts" if args.bpm_response else "one bias completion contract; qualified native binary reused" if args.complete_bias else "six file-to-ASDF/affected contracts" if args.file_qc else ("four measurement/bias/allocation contracts" if args.measurements else ("native_bias_files only" if args.bias_only else "five focused contracts")),
               "inherited_four_passes": "native f20a9ab7a0758775d020480be1e1daa547716e3b actual Mac run; not rerun" if args.bias_only else None,
               "limits": ["synthetic BPM numerical service only; no acquisition admission or publication" if args.bpm_service else "synthetic response/mask/measurement core only; no new recipe CLI" if args.bpm_response else "synthetic operation-template/file-bias/layout/bias/native-path contracts only", "no observational/scientific/performance acceptance",
                          "no sanitizer or leak-tool claim on targets"]}
    print("RETAINED RUN:", run, flush=True)
    env = dict(os.environ, TMPDIR=str(run), PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", OPENBLAS_NUM_THREADS="1",
               OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1",
               MEFPP_TEST_REVISION=args.revision)
    # Do not inherit compiler/linker selection or preload overrides.
    inherited = ("CC", "CXX", "CFLAGS", "CPPFLAGS", "LDFLAGS", "SDKROOT", "MACOSX_DEPLOYMENT_TARGET",
                 "CPATH", "C_INCLUDE_PATH", "LIBRARY_PATH", "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH",
                 "GCC_EXEC_PREFIX", "COMPILER_PATH", "CMAKE_GENERATOR", "CMAKE_TOOLCHAIN_FILE",
                 "LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")
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

    qc_initial = None
    qc_controls = """import hashlib,importlib.metadata as m,json,sys
from pathlib import Path
names=('asdf','asdf-standard','numpy')
versions={n:m.version(n) for n in names}
assert versions=={'asdf':'6.0.0','asdf-standard':'1.5.0','numpy':'1.26.4'}, versions
controls={}
for n in names:
 d=m.distribution(n)
 for f in d.files or ():
  if str(f).endswith('.dist-info/METADATA'):
   p=Path(d.locate_file(f)); controls[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
p=Path(m.distribution('asdf').locate_file('asdf/__init__.py')); controls[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
print(json.dumps(dict(prefix=sys.prefix,versions=versions,controls=controls),sort_keys=True))
"""
    finished = False
    try:
        if args.file_qc or args.complete_bias:
            qc_initial = json.loads(command("qc-environment-before", [args.qc_python, "-B", "-c", qc_controls]).read_text())
            require(Path(qc_initial["prefix"]).resolve() == args.qc_python.parent.parent.resolve(), "Wrong retained ASDF prefix")
            receipt["qc_environment"] = qc_initial
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
        if args.complete_bias:
            old = args.reuse_native_run.resolve(strict=True)
            require(not args.reuse_native_run.is_symlink() and old.parent == run.parent and old != run,
                    "Unexpected retained native run")
            adapter, proof = reuse_bias_adapter(old, source, git, receipt["tool_sha256"])
            receipt["reused_native"] = proof
            print("REUSED QUALIFIED C17 ADAPTER:", adapter, flush=True)
            log = command("completion-reuse-guards", [sys.executable, "-B", source / "mefpp2/tests/test_bias_completion_reuse.py"])
            print(log.read_text(), flush=True)
            log = command("bias-completion", [sys.executable, "-B", source / "mefpp2/tests/bias_completion_contract.py",
                "--source-root", source, "--adapter", adapter, "--asdf-python", args.qc_python, "--work-parent", run])
            print(log.read_text(), flush=True)
        for standard in (() if args.complete_bias else ("17",)):
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
            if args.file_qc or args.complete_bias:
                configure += ["-DMEFPP_QC_PYTHON=" + str(args.qc_python)]
            command("configure-c" + standard, configure)
            targets = ["mefpp_m5", "mefpp"] if args.bias_only else [
                "operation_template_probe", "layout_probe", "bias_service_probe", "mefpp_m5", "mefpp"]
            if args.measurements:
                targets = ["measurement_stats_probe", "bias_service_probe", "eclipse_allocation_probe", "mefpp_m5", "mefpp"]
            if args.bpm_response:
                targets = ["bpm_response_probe", "measurement_stats_probe"]
            if args.bpm_service:
                targets = ["bpm_service_probe", "operation_template_probe"]
            if args.file_qc or args.complete_bias:
                targets = ["layout_probe", "bias_service_probe", "eclipse_allocation_probe", "mefpp_m5", "mefpp"]
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
            if args.bpm_response:
                expected_tests = {"native_bpm_response", "native_measurement_stats"}
                selection = "^(" + "|".join(sorted(expected_tests)) + ")$"
            if args.bpm_service:
                expected_tests = {"native_bpm_service", "native_operation_template"}
                selection = "^(" + "|".join(sorted(expected_tests)) + ")$"
            if args.file_qc or args.complete_bias:
                expected_tests = FILE_QC_TESTS
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
        if (args.file_qc or args.complete_bias) and qc_initial is not None:
            try:
                after = json.loads(command("qc-environment-after", [args.qc_python, "-B", "-c", qc_controls]).read_text())
                checks["retained_qc_controls"] = after == qc_initial
            except Exception:
                checks["retained_qc_controls"] = False
        if "reused_native" in receipt:
            checks["reused_native_controls"] = all(Path(p).is_file() and sha(Path(p)) == digest
                for p, digest in receipt["reused_native"]["controls"].items())
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
