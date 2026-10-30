"""Read-only legacy project metadata inspection; no reduction or association policy.

Refs #159. Named lists are evidence of membership, links of references, and FITS
cards of reported metadata. None alone establishes successful processing.
"""
import argparse
import configparser
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import warnings

if __package__:
    from .pycavi_paths import PathResolver, PathResolutionError
else:
    from pycavi_paths import PathResolver, PathResolutionError


# Names come from PartitionsTree/ExposuresPartition, not directory-name guesses.
LIST_ROLES = {"bias.list": "bias", "dome.list": "dome", "sky.list": "sky",
              "mff.list": "master-flat", "std.list": "standard",
              "science.list": "science"}
PRIMARY_FIELDS = {"instrument": "inst_name_key", "target": "object_key",
                  "filter": "filt_key", "exposure": "inst_exp_key"}
STANDARD_KEYS = {"instrument": "INSTRUME", "target": "OBJECT",
                 "filter": "FILTER", "exposure": "EXPTIME"}
DEFAULT_COLUMNS = ("partition", "stage", "member", "hdu", "extname",
                   "instrument", "target", "filter", "exposure", "status")
ROW_KEYS = set(DEFAULT_COLUMNS) | {"path", "hdu_type", "dimensions"}


@dataclass(frozen=True)
class Limits:
    files: int = 10000
    directories: int = 1000
    depth: int = 32
    list_lines: int = 10000
    text_bytes: int = 4 * 1024 * 1024
    hdus: int = 128
    header_bytes: int = 4 * 1024 * 1024

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in vars(self).values()):
            raise ValueError("Inspection limits must be positive integers")


class _HeaderStream:
    """Bound Astropy's header reads while allowing seeks over pixel payloads."""
    def __init__(self, stream, budget):
        self.stream, self.remaining = stream, budget

    def read(self, size=-1):
        if size < 0 or size > self.remaining:
            raise OSError("FITS header read budget exceeded")
        raw = self.stream.read(size)
        self.remaining -= len(raw)
        return raw

    def __getattr__(self, key):
        return getattr(self.stream, key)


def _safe_value(value):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    return str(value)


class _Inspector:
    def __init__(self, root, resolver, recursive, list_base, columns, limits):
        self.root, self.resolver = root, resolver
        self.recursive, self.list_base = recursive, list_base
        self.columns, self.limits = columns, limits
        self.keys = dict(STANDARD_KEYS)
        self.assets, self.partitions, self.links = {}, [], []
        self.diagnostics, self.configurations, self.rows = [], [], []
        self.attempt_evidence = []
        self.directories = 0
        self.entries = 0
        self.members = 0

    def diagnostic(self, code, path, message, *, incomplete=True):
        self.diagnostics.append(dict(code=code, path=str(path), message=message,
                                     incomplete=incomplete))

    def text(self, path):
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError("Selected text input is not a regular file")
        with path.open("rb") as stream:
            raw = stream.read(self.limits.text_bytes + 1)
        if len(raw) > self.limits.text_bytes or b"\0" in raw:
            raise ValueError("Text file exceeds limit or contains NUL")
        return raw.decode("utf-8")

    def config(self, path, role):
        record = dict(path=str(path), role=role, authority="explicitly-selected",
                      raw=None, sections={}, status="unreadable")
        self.configurations.append(record)
        try:
            raw = self.text(path)
            record["raw"] = raw
            parser = configparser.ConfigParser(
                inline_comment_prefixes=("#",) if role == "instrument" else None)
            parser.read_string(raw)
            record.update(raw=raw, status="read")
            for section in parser.sections():
                record["sections"][section] = {}
                for key in parser[section]:
                    record["sections"][section][key] = dict(
                        raw=parser.get(section, key, raw=True), value=parser.get(section, key))
            if role == "instrument":
                for field, key in PRIMARY_FIELDS.items():
                    value = parser.get("Primary Keywords", key, fallback="").strip().strip('"')
                    if value:
                        self.keys[field] = value
                    else:
                        self.diagnostic("missing_keyword_mapping", path, key)
            elif parser.has_section("Directories"):
                for key, item in record["sections"]["Directories"].items():
                    if not key.endswith("_dir") or not item["value"].strip():
                        continue
                    try:
                        item["resolved"] = str(self.resolver.reference(
                            item["value"], base=self.list_base))
                    except PathResolutionError as exc:
                        self.diagnostic("unknown_cfg_base", path, f"{key}: {exc}")
        except (OSError, ValueError, configparser.Error) as exc:
            self.diagnostic("configuration_error", path, str(exc))

    def asset(self, declared):
        try:
            path = self.resolver.reference(declared)
        except PathResolutionError as exc:
            self.diagnostic("path_error", declared, str(exc))
            return None
        key = str(path)
        if key in self.assets:
            return self.assets[key]
        if len(self.assets) >= self.limits.files:
            self.diagnostic("asset_limit", declared, "Asset limit reached")
            return None
        item = dict(path=key, status="unavailable", metadata="not-read", hdus=[])
        self.assets[key] = item
        try:
            mode = path.stat().st_mode
            if not stat.S_ISREG(mode):
                raise ValueError("Reference is not a regular file")
            item["status"] = "existing-unverified"
            if path.suffix.lower() not in (".fits", ".fit", ".fts"):
                self.diagnostic("unsupported_reference", path, "Only uncompressed FITS headers are inspected")
                return item
            self.headers(path, item)
        except (OSError, ValueError) as exc:
            self.diagnostic("reference_error", declared, str(exc))
        return item

    def headers(self, path, item):
        from astropy.io import fits
        primary_fields = None
        selected = set(self.keys.values()) | set(self.columns) | {
            "EXTNAME", "EXTVER", "BUNIT", "ESO PRO CATG", "PRODCATG"}
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                with path.open("rb") as stream:
                    bounded = _HeaderStream(stream, self.limits.header_bytes)
                    with fits.open(bounded, mode="readonly", memmap=False,
                                   lazy_load_hdus=True, do_not_scale_image_data=True,
                                   ignore_missing_end=False) as hdus:
                        for index in range(self.limits.hdus + 1):
                            try:
                                hdu = hdus[index]
                            except IndexError:
                                break
                            if index == self.limits.hdus:
                                self.diagnostic("hdu_limit", path, "HDU limit reached")
                                break
                            hdu.verify("exception")
                            header = hdu.header
                            cards = [dict(key=c.keyword, value=_safe_value(c.value), comment=c.comment)
                                     for c in header.cards if c.keyword in selected or
                                     "HIERARCH " + c.keyword in selected]
                            values = {}
                            for card in cards:
                                values.setdefault(card["key"], []).append(card["value"])
                            for key, members in values.items():
                                if len(members) > 1:
                                    self.diagnostic("duplicate_header_key", path, f"HDU {index}: {key}")
                            def single(key):
                                entries = values.get(key.removeprefix("HIERARCH "), [])
                                return entries[0] if len(entries) == 1 else None
                            fields = {field: single(key) for field, key in self.keys.items()}
                            if primary_fields is None:
                                primary_fields = fields
                            elif any(value is not None and primary_fields[key] is not None and
                                     value != primary_fields[key] for key, value in fields.items()):
                                self.diagnostic("primary_extension_conflict", path,
                                                f"HDU {index}: reported primary metadata differs")
                            item["hdus"].append(dict(
                                hdu=index, hdu_type=type(hdu).__name__, extname=single("EXTNAME"),
                                dimensions=[header.get(f"NAXIS{i}") for i in range(1, header.get("NAXIS", 0) + 1)],
                                cards=cards, fields=dict(primary_fields), local_fields=fields,
                                fields_source_hdu=0,
                                selected={key: single(key) for key in self.columns if key not in ROW_KEYS},
                                authority="reported-unverified"))
                for warning in caught:
                    self.diagnostic("fits_warning", path, str(warning.message))
            item["metadata"] = "read"
        except (OSError, ValueError, TypeError, fits.verify.VerifyError) as exc:
            self.diagnostic("fits_error", path, str(exc))
            item["metadata"] = "incomplete"

    def add_rows(self, asset, partition, stage, member=None):
        if asset is None:
            return
        for hdu in asset["hdus"] or [dict(hdu=None, extname=None, fields={}, selected={})]:
            row = dict(partition=partition, stage=stage, member=member,
                       path=asset["path"], status=asset["status"])
            row.update({k: v for k, v in hdu.items() if k in ROW_KEYS})
            row.update(hdu["fields"])
            row.update(hdu["selected"])
            self.rows.append(row)

    def partition(self, path, role):
        relative = str(path.parent.relative_to(self.root))
        record = dict(partition=relative, stage=role, list_path=str(path),
                      member_base=str(self.list_base) if self.list_base else None,
                      members=[], status="membership-evidence-only")
        self.partitions.append(record)
        try:
            text = self.text(path)
            # Match charmatrix/FS_BLANKS: first column, hash only at column zero.
            # Reject CR and overlong lines rather than silently reinterpret them.
            for line_number, line in enumerate(text.split("\n"), 1):
                if line_number > self.limits.list_lines:
                    self.diagnostic("list_limit", path, "List line limit reached")
                    break
                if len(line.encode()) >= 1023 or "\r" in line:
                    self.diagnostic("unsupported_list_line", path, f"Line {line_number}: long line or CR")
                    continue
                if line.startswith("#") or not line.strip(" \t"):
                    continue
                if self.members >= self.limits.list_lines:
                    self.diagnostic("membership_limit", path, "Total membership limit reached")
                    break
                self.members += 1
                tokens = re.split(r"[ \t]+", line.strip(" \t"))
                member = dict(line=line_number, raw=line, columns=tokens,
                              path=None, status="unresolved")
                record["members"].append(member)
                if len(tokens) > 1:
                    self.diagnostic("list_extra_columns", path,
                                    f"Line {line_number}: legacy reader selects first token; no quoted-path support")
                try:
                    resolved = self.resolver.reference(tokens[0], base=self.list_base)
                    member["path"] = str(resolved)
                    asset = self.asset(resolved)
                    member["status"] = asset["status"] if asset else "not-inspected"
                    self.add_rows(asset, relative, role, len(record["members"]))
                except PathResolutionError as exc:
                    self.diagnostic("unknown_list_base", path, f"Line {line_number}: {exc}")
        except (OSError, ValueError) as exc:
            self.diagnostic("list_error", path, str(exc))

    def walk(self, directory, depth=0):
        if depth > self.limits.depth or self.directories >= self.limits.directories:
            self.diagnostic("directory_limit", directory, "Directory depth/count limit reached")
            return
        self.directories += 1
        try:
            with os.scandir(directory) as scan:
                entries = []
                for entry in scan:
                    if self.entries >= self.limits.files:
                        self.diagnostic("entry_limit", directory, "Total directory entry limit reached")
                        break
                    self.entries += 1
                    entries.append(Path(entry.path))
            entries.sort(key=lambda p: p.name)
        except OSError as exc:
            self.diagnostic("directory_error", directory, str(exc))
            return
        for path in entries:
            if path.is_symlink():
                edge = dict(path=str(path), raw_target=None, resolved=None)
                self.links.append(edge)
                try:
                    edge["raw_target"] = os.readlink(path)
                    target = self.resolver.reference(path)
                    edge["resolved"] = str(target)
                    if target.is_dir():
                        self.diagnostic("directory_link_not_followed", path,
                                        "Directory link recorded; traversal is limited to the declared tree")
                        continue
                except (OSError, PathResolutionError) as exc:
                    self.diagnostic("link_error", path, str(exc))
                    continue
            try:
                if path.is_dir():
                    if self.recursive:
                        self.walk(path, depth + 1)
                    else:
                        self.diagnostic("not_recursive", path, "Subdirectory not inspected")
                elif path.name in LIST_ROLES:
                    self.partition(path, LIST_ROLES[path.name])
                elif (path.suffix.lower() in (".fits", ".fit", ".fts") or path.is_symlink() or
                      path.name.lower().endswith((".fits.fz", ".fits.gz", ".fit.fz", ".fit.gz"))):
                    asset = self.asset(path)
                    self.add_rows(asset, str(path.parent.relative_to(self.root)),
                                  "linked-reference" if path.is_symlink() else "unclassified-file")
                elif path.suffix == ".list":
                    self.diagnostic("unknown_list_role", path, "List role is not declared by this legacy adapter")
                elif path.name.startswith("toreduce_") or path.suffix == ".log":
                    self.attempt_evidence.append(dict(
                        path=str(path), kind="marker" if path.name.startswith("toreduce_") else "log",
                        status="present-uninterpreted", completion="unknown"))
            except OSError as exc:
                self.diagnostic("entry_error", path, str(exc))


def inspect_project(root, *, invocation_base, recursive=False, list_base=None,
                    project_config=None, instrument_config=None, columns=(), limits=Limits()):
    """Return independent metadata, preserving ordered lists and unknown authority.

    No chdir, writes, shell commands, array access, association selection or hashes
    of FITS payloads. Relative legacy members need an explicitly recorded base.
    """
    resolver = PathResolver(Path(invocation_base))
    root = resolver.argument(root)
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory")
    columns = tuple(columns) or DEFAULT_COLUMNS
    if any(not isinstance(key, str) or not key or any(ord(c) < 32 for c in key) for key in columns):
        raise ValueError("Columns must be nonempty printable names")
    inspector = _Inspector(root, resolver, recursive,
                           resolver.argument(list_base) if list_base is not None else None,
                           columns, limits)
    for role, path in (("project", project_config), ("instrument", instrument_config)):
        if path is not None:
            inspector.config(resolver.argument(path), role)
    inspector.walk(root)
    counts = {}
    for diagnostic in inspector.diagnostics:
        counts[diagnostic["code"]] = counts.get(diagnostic["code"], 0) + 1
    return dict(notation="wenu-legacy-project-inspection-1", root=str(root),
                configurations=inspector.configurations, partitions=inspector.partitions,
                assets=list(inspector.assets.values()), links=inspector.links,
                rows=inspector.rows, diagnostics=inspector.diagnostics,
                attempt_evidence=inspector.attempt_evidence,
                coverage=dict(recursive=recursive, directories=inspector.directories,
                              assets=len(inspector.assets), partitions=len(inspector.partitions),
                              diagnostics=len(inspector.diagnostics), diagnostics_by_code=counts,
                              complete=not any(d["incomplete"] for d in inspector.diagnostics),
                              limits=dict(vars(limits))),
                authority="legacy-evidence-only", execution_ready=False)


def _cell(value):
    # Keep embedded tabs/newlines/control bytes from corrupting terminal tables.
    return json.dumps(value, ensure_ascii=True, allow_nan=False) if value is not None else "-"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    project = commands.add_parser("project").add_subparsers(dest="action", required=True)
    inspect = project.add_parser("inspect")
    inspect.add_argument("root", type=Path)
    inspect.add_argument("--recursive", action="store_true")
    inspect.add_argument("--list-base", type=Path)
    inspect.add_argument("--project-config", type=Path)
    inspect.add_argument("--instrument-config", type=Path)
    inspect.add_argument("--format", choices=("table", "json"), default="table")
    inspect.add_argument("--columns", nargs="+", default=list(DEFAULT_COLUMNS))
    inspect.add_argument("--where", action="append", default=[], metavar="COLUMN=VALUE")
    inspect.add_argument("--sort", metavar="COLUMN")
    inspect.add_argument("--partition")
    inspect.add_argument("--stage")
    inspect.add_argument("--detector", help="Reported EXTNAME; not hardware identity validation")
    args = parser.parse_args(argv)
    try:
        report = inspect_project(args.root, invocation_base=Path.cwd(), recursive=args.recursive,
                                 list_base=args.list_base, project_config=args.project_config,
                                 instrument_config=args.instrument_config, columns=args.columns)
        rows = report["rows"]
        filters = list(args.where)
        for key, value in (("partition", args.partition), ("stage", args.stage), ("extname", args.detector)):
            if value is not None:
                filters.append(key + "=" + value)
        for expression in filters:
            key, separator, value = expression.partition("=")
            if not separator or key not in ROW_KEYS | set(args.columns):
                raise ValueError("Filter requires a selected column or row field: COLUMN=VALUE")
            rows = [row for row in rows if str(row.get(key)) == value]
        if args.sort:
            if args.sort not in ROW_KEYS | set(args.columns):
                raise ValueError("Sort requires a selected column or row field")
            def order(row):
                value = row.get(args.sort)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    return (0, value)
                return (1, str(value)) if value is not None else (2, "")
            rows = sorted(rows, key=order)
        report["view"] = dict(rows=rows, columns=args.columns, filters=filters, sort=args.sort,
                              selection_only=True)
        if args.format == "json":
            print(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False))
        else:
            print("Project:", _cell(report["root"]))
            print("Coverage:", "complete" if report["coverage"]["complete"] else "incomplete",
                  "| partitions:", len(report["partitions"]), "| assets:", len(report["assets"]))
            print("Sequence: listed inputs -> linked calibration evidence -> available file headers")
            print("Processing/normalization/WCS completion: unverified; no filename-based inference")
            print("\t".join(args.columns))
            for row in rows:
                print("\t".join(_cell(row.get(key)) for key in args.columns))
            for diagnostic in report["diagnostics"]:
                print("DIAGNOSTIC", _cell(diagnostic))
        return 0
    except (OSError, ValueError, configparser.Error, ImportError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
