"""Populate a user-owned notebook workspace from installed resources."""

import argparse
from importlib import resources
from pathlib import Path
import shutil
import sys


def setup_pycavi(destination=".", *, overwrite=False):
    """Copy templates and reference data; preserve existing files by default.

    Returns counts of copied and preserved files. Errors propagate to callers.
    This does not create calibrations or run any processing programs.
    """
    destination = Path(destination).expanduser()
    package = resources.files("pycavi")
    groups = (("config", {".cfg", ".paf"}),
              ("notebooks", {".ipynb"}),
              ("data", {".csv", ""}))
    copies = []
    # Check every resource group before creating the destination.
    for group, suffixes in groups:
        source = package.joinpath(group)
        if not source.is_dir():
            raise FileNotFoundError(f"Installed Pycavi resource directory missing: {group}")
        files = sorted((p for p in source.iterdir()
                        if p.is_file() and p.suffix in suffixes), key=lambda p: p.name)
        if not files:
            raise FileNotFoundError(f"No installed Pycavi resources in: {group}")
        target = destination if group == "notebooks" else destination / group
        copies.extend((p, target / p.name) for p in files)

    counts = {"copied": 0, "preserved": 0}
    for source, target in copies:
        if target.is_symlink():
            raise FileExistsError(f"Refusing to write through a symlink: {target}")
        if target.exists() and not overwrite:
            if not target.is_file():
                raise IsADirectoryError(f"Expected a file: {target}")
            counts["preserved"] += 1
            print(f"Preserved: {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as incoming, target.open("wb" if overwrite else "xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        counts["copied"] += 1
        print(f"Copied: {target}")
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", default=".", help="Notebook workspace (default: current directory)")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing templates; edited files will be lost")
    args = parser.parse_args(argv)
    try:
        counts = setup_pycavi(args.destination, overwrite=args.overwrite)
    except (OSError, ModuleNotFoundError) as exc:
        print(f"Pycavi setup failed: {exc}", file=sys.stderr)
        return 1
    print(f"Copied {counts['copied']}; preserved {counts['preserved']} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
