"""Reproduce legacy native-install findings in disposable fixtures, not a target qualification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile


def main():
    # Isolation and provenance: accept explicit source, create fresh records, lower priority.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--records-parent", required=True, type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    records = Path(tempfile.mkdtemp(prefix="native-install-probes-", dir=args.records_parent))
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        os.nice(10 - os.getpriority(os.PRIO_PROCESS, 0))
    results = []
    originals = {}

    def copy_file(src, dest):
        originals[str(src)] = hashlib.sha256(src.read_bytes()).hexdigest()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    def fixture(name, package, names):
        folder = records / name
        folder.mkdir()
        for path in names:
            copy_file(source / package / path, folder / path)
        return folder

    def run(name, cwd, command, env=None):
        result = subprocess.run(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=30)
        log = records / (name + ".log")
        log.write_text(result.stdout)
        row = dict(name=name, command=command, cwd=str(cwd), returncode=result.returncode,
                   log=str(log))
        results.append(row)
        return result, row

    # Compiler failure: invoke each original configure with cc/gcc stubs that fail.
    stubs = records / "failing-compilers"
    stubs.mkdir()
    for name in ("cc", "gcc"):
        script = stubs / name
        script.write_text("#!/bin/sh\nexit 42\n")
        script.chmod(0o755)
    environment = dict(os.environ, PATH=str(stubs))
    for package in ("qfits52", "mefpp2"):
        folder = fixture(package + "-no-compiler", package, ["configure"])
        result, row = run(package + "-no-compiler", folder,
                          ["/bin/sh", "./configure"], environment)
        row["failure_reported"] = "cannot find cc or gcc" in result.stdout
        row["failure_hidden_by_zero_exit"] = row["failure_reported"] and result.returncode == 0

    # Configure errors/help: compile only the small bootstrap, not either scientific library.
    for package in ("qfits52", "mefpp2"):
        folder = fixture(package + "-invalid-os", package, ["configure", "sysconf.c"])
        (folder / ("src/include" if package == "mefpp2" else "src")).mkdir(parents=True)
        result, row = run(package + "-invalid-os", folder,
                          ["/bin/sh", "./configure", "--os=invalid-audit-os"])
        row["failure_reported"] = "unsupported OS" in result.stdout
        row["failure_hidden_by_zero_exit"] = row["failure_reported"] and result.returncode == 0
        result, row = run(package + "-help", folder, ["/bin/sh", "./configure", "--help"])
        row["spurious_header_move_error"] = "cannot stat" in result.stdout or "No such file" in result.stdout

    # Compiler selection/Darwin generator: inspect emitted config, without compiling Mac objects.
    folder = fixture("qfits-generator", "qfits52", ["configure", "sysconf.c"])
    (folder / "src").mkdir()
    environment = dict(os.environ, CC="/audit/requested-compiler-not-used")
    result, row = run("qfits-darwin-cc", folder,
                      ["/bin/sh", "./configure", "--with-cc", "--os=darwin"], environment)
    config = (folder / "config.make").read_text()
    row["generated_config"] = config
    row["CC_environment_ignored"] = "CC      = cc" in config
    row["RELOC_appended_to_CFLAGS"] = any(
        line.startswith("CFLAGS") and "RELOC" in line for line in config.splitlines())

    # Linux assembler flag: exercise only a trivial C translation unit with the emitted GCC flag.
    if platform.system() == "Linux":
        unit = folder / "empty.c"
        unit.write_text("int native_audit_empty(void) { return 0; }\n")
        result, row = run("linux-Wa-q", folder,
                          ["gcc", "-Wa,-q", "-c", str(unit), "-o", str(folder / "empty.o")])
        row["flag_rejected"] = result.returncode != 0

    # Incomplete installs: run original install recipes in fixture-only prefixes without products.
    for package in ("qfits52", "mefpp2"):
        folder = fixture(package + "-unbuilt-install", package, ["Makefile"])
        prefix = folder / "installed"
        (folder / "config.make").write_text("prefix = " + str(prefix) + "\nDYNSUF = so\n")
        result, row = run(package + "-unbuilt-install", folder, ["make", "install"])
        row["installed_files"] = [str(p.relative_to(prefix)) for p in prefix.rglob("*") if p.is_file()]
        row["incomplete_install_returns_success"] = result.returncode == 0 and not row["installed_files"]

    # Missing tests: exercise qfits make check with its absent test directory.
    folder = fixture("qfits-no-tests", "qfits52", ["Makefile"])
    (folder / "config.make").write_text("DYNSUF = so\n")
    result, row = run("qfits-no-tests", folder, ["make", "check"])
    row["no_test_directory_in_source"] = not (source / "qfits52/test").exists()
    row["empty_check_returns_success"] = result.returncode == 0 and row["no_test_directory_in_source"]

    # Recursive failure: use the real qfits progs recipe with a deliberately failing child make.
    folder = fixture("qfits-child-failure", "qfits52", ["Makefile"])
    (folder / "config.make").write_text("DYNSUF = so\n")
    for name, content in (("main", "all:\n\t@echo AUDIT_CHILD_FAILURE\n\t@exit 23\n"),
                          ("saft", "all:\n\t@true\n")):
        (folder / name).mkdir()
        (folder / name / "Makefile").write_text(content)
    result, row = run("qfits-child-failure", folder, ["make", "progs"])
    row["child_failure_hidden"] = "AUDIT_CHILD_FAILURE" in result.stdout and result.returncode == 0

    # Preservation/report: hash all copied source files again and retain host-labelled results.
    for name, expected in originals.items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
    report = dict(platform=platform.platform(), source=str(source), records=str(records),
                  source_files_unchanged=True, source_sha256=originals, results=results,
                  scope="Agent-host disposable installation audit probes; no Mac/chapman3 build qualification")
    (records / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({"records": str(records), "results": [
        {k: v for k, v in row.items() if k not in {"generated_config", "command", "cwd", "log"}}
        for row in results]}, indent=2))


if __name__ == "__main__":
    main()
