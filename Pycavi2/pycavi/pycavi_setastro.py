"""Select external astronomy programs without scanning shared filesystems."""

import argparse
import configparser
import os
from pathlib import Path
import shutil
import subprocess
import sys


EXECUTABLES = {
    "mefpp": ("mefpp",),
    "solve-field": ("solve-field",),
    "sextractor": ("sextractor", "source-extractor", "sex"),
    "scamp": ("scamp",),
    "swarp": ("swarp",),
}
DEFAULT_CONFIG = "~/.pycavi/pycavi_astrosoft.cfg"


def find_executables_which(possible_names):
    """Return executable files in PATH order, without invoking a shell."""
    found = []
    for directory in os.get_exec_path():
        for name in possible_names:
            candidate = Path(directory or ".") / name
            if candidate.is_file() and os.access(candidate, os.X_OK):
                path = str(candidate.absolute())
                if path not in found:
                    found.append(path)
    return found


def find_executables_in_roots(possible_names, root_dirs):
    """Search only explicitly supplied roots (retained for API compatibility)."""
    found = []
    for root in root_dirs:
        for directory, dirs, filenames in os.walk(root):
            dirs.sort()
            for name in possible_names:
                path = Path(directory) / name
                if name in filenames and path.is_file() and os.access(path, os.X_OK):
                    value = str(path.absolute())
                    if value not in found:
                        found.append(value)
    return found


def _executable(value):
    path = shutil.which(os.path.expanduser(value))
    if path is None:
        raise FileNotFoundError(f"Not an executable file or PATH command: {value}")
    return str(Path(path).absolute())


def _read_config(config_file):
    config = configparser.ConfigParser(interpolation=None)
    if config_file.exists():
        with config_file.open() as stream:
            config.read_file(stream)
    return config


def find_and_choose_executables(*, overrides=None, config_file=None,
                                non_interactive=False, overwrite=False,
                                search_roots=()):
    """Write the existing [Paths] interface, preserving saved choices by default.

    Explicit overrides take precedence, followed by saved paths, then PATH.
    A partial or invalid selection is an error and does not write a config.
    """
    config_file = Path(config_file or os.environ.get("PYCAVI_ASTROSOFT_CONFIG", DEFAULT_CONFIG)).expanduser()
    config = _read_config(config_file)
    saved = dict(config["Paths"]) if config.has_section("Paths") else {}
    overrides = overrides or {}
    unknown = set(overrides) - EXECUTABLES.keys()
    if unknown:
        raise ValueError(f"Unknown executable keys: {sorted(unknown)}")
    chosen = {}
    for name, aliases in EXECUTABLES.items():
        previous = saved.get(name)
        if name in overrides:
            chosen[name] = _executable(overrides[name])
        elif previous and not overwrite:
            chosen[name] = _executable(previous)
        else:
            candidates = find_executables_which(aliases)
            candidates.extend(p for p in find_executables_in_roots(aliases, search_roots)
                              if p not in candidates)
            if not candidates:
                raise FileNotFoundError(f"{name} not found; specify --{name} /full/path")
            if non_interactive or len(candidates) == 1:
                chosen[name] = candidates[0]
            else:
                print(f"\n{name}:")
                for index, path in enumerate(candidates, 1):
                    print(f"  {index}) {path}")
                while True:
                    response = input(f"Choose {name} [1]: ").strip()
                    try:
                        index = int(response or "1")
                        if not 1 <= index <= len(candidates):
                            raise ValueError
                        chosen[name] = candidates[index - 1]
                        break
                    except ValueError:
                        print("Choose a displayed positive number.")
        print(f"{name}: {chosen[name]}")

    if config_file.is_symlink():
        raise FileExistsError(f"Refusing to replace a symlink: {config_file}")
    if chosen == saved:
        print(f"Configuration unchanged: {config_file}")
        return chosen
    config["Paths"] = chosen
    config_file.parent.mkdir(parents=True, exist_ok=True)
    # Preserve a user-edited configuration before changing it.
    if config_file.exists():
        index = 1
        backup = config_file.with_name(config_file.name + ".bak")
        while backup.exists():
            backup = config_file.with_name(config_file.name + f".bak.{index}")
            index += 1
        shutil.copy2(config_file, backup)
        print(f"Previous configuration saved: {backup}")
    with config_file.open("w") as stream:
        config.write(stream)
    print(f"Configuration saved: {config_file}")
    return chosen


def check_executables(config_file=None):
    """Read and probe selected programs; never modify configuration or run science."""
    path = Path(config_file or os.environ.get("PYCAVI_ASTROSOFT_CONFIG", DEFAULT_CONFIG)).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Configuration not found: {path}")
    config = _read_config(path)
    if not config.has_section("Paths"):
        raise ValueError(f"Missing [Paths] in {path}")
    failed = False
    for name in EXECUTABLES:
        try:
            executable = _executable(config["Paths"][name])
            print(f"{name}: {executable}")
            # mefpp's startup behavior is retained; validate its path only.
            if name == "mefpp":
                print("  Executable present; version not probed.")
                continue
            flag = "--help" if name == "solve-field" else "-v"
            result = subprocess.run([executable, flag], stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, timeout=15)
            lines = result.stdout.strip().splitlines()
            print("  " + "\n  ".join(lines[:8]))
            # solve-field --help can return nonzero even on a working install.
            if result.returncode and name != "solve-field":
                raise RuntimeError(f"Version probe exited {result.returncode}")
            if name == "solve-field" and "Astrometry.net" not in result.stdout:
                raise RuntimeError("Help probe did not identify Astrometry.net")
        except (OSError, KeyError, subprocess.TimeoutExpired, RuntimeError) as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="Configuration path (or PYCAVI_ASTROSOFT_CONFIG)")
    parser.add_argument("--non-interactive", action="store_true", help="Use saved choices or first PATH match without prompts")
    parser.add_argument("--overwrite", action="store_true", help="Rediscover saved choices; back up previous configuration")
    parser.add_argument("--search-root", action="append", default=[], help="Optional recursive search root; repeat as needed")
    parser.add_argument("--check", action="store_true", help="Check saved executables and report versions without writing")
    for name in EXECUTABLES:
        parser.add_argument(f"--{name}", dest=name, metavar="PATH")
    args = parser.parse_args(argv)
    overrides = {name: getattr(args, name) for name in EXECUTABLES if getattr(args, name) is not None}
    if args.check and (overrides or args.overwrite or args.search_root):
        parser.error("--check cannot be combined with path overrides, --overwrite or --search-root")
    try:
        if args.check:
            return check_executables(args.config)
        find_and_choose_executables(overrides=overrides, config_file=args.config,
                                   non_interactive=args.non_interactive or not sys.stdin.isatty(),
                                   overwrite=args.overwrite, search_roots=args.search_root)
    except (OSError, ValueError, configparser.Error, EOFError) as exc:
        print(f"Pycavi executable setup failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
