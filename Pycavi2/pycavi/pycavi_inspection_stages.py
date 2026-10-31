"""Read-only stage views over the legacy inspector's already declared evidence.

No association selection, log-success parsing, image access or result store.
Expected names do not establish historical input identity or completion. Refs #159.
"""
from pathlib import Path

if __package__:
    from .pycavi_product_paths import science_product_paths, NORMALIZED_UNIT
else:
    from pycavi_product_paths import science_product_paths, NORMALIZED_UNIT


CATEGORIES = {"CALIB.MASTER_BIAS": "bias", "CALIB.BPM": "bpm",
              "CALIB.MASTER_DOME_FLAT": "dome", "CALIB.MASTER_SKY_FLAT": "sky",
              "CALIB.MASTER_FLAT": "master-flat", "SCIENCE.MEFIMAGE": "preprocessing"}
CALIBRATIONS = ("bias", "bpm", "dome", "sky", "master-flat")
STAGE_CARDS = {"BUNIT", "ONEADU", "PRODCATG", "ESO PRO CATG",
               "CTYPE1", "CTYPE2", "CRVAL1", "CRVAL2", "CRPIX1", "CRPIX2",
               "CD1_1", "CD1_2", "CD2_1", "CD2_2", "CDELT1", "CDELT2"}


def _primary(asset, key):
    if not asset or not asset["hdus"]:
        return None
    values = [c["value"] for c in asset["hdus"][0]["cards"] if c["key"] == key]
    return values[0] if len(values) == 1 else None


def _role(asset):
    # Conflicting/duplicate category declarations never select one authority.
    if not asset or not asset["hdus"]:
        return None
    cards = [c["value"] for c in asset["hdus"][0]["cards"]
             if c["key"] in ("PRODCATG", "ESO PRO CATG")]
    if not cards or len(set(map(str, cards))) != 1:
        return None
    return CATEGORIES.get(cards[0])


def build_stages(inspector):
    """Build a bounded evidence view after traversal; preserve list/member order."""
    records = []
    original_assets = list(inspector.assets.values())
    by_directory = {}
    for partition in inspector.partitions:
        by_directory.setdefault(str(Path(partition["list_path"]).parent), set()).add(partition["stage"])

    def append(partition, stage, path, relation, *, role=None, member=None, source=None):
        if len(records) >= inspector.limits.files:
            if not any(d["code"] == "stage_limit" for d in inspector.diagnostics):
                inspector.diagnostic("stage_limit", inspector.root, "Stage record limit reached")
            return
        asset = None
        if path is not None:
            try:
                canonical = str(inspector.resolver.reference(path))
                asset = inspector.assets.get(canonical)
                # A nonexistent expected location is an unbuilt product, not a read error.
                if asset is None and (Path(path).exists() or Path(path).is_symlink()):
                    asset = inspector.asset(path)
            except (OSError, ValueError) as exc:
                inspector.diagnostic("stage_path_error", path, str(exc))
        record = dict(partition=partition["partition"], stage=stage, role=role,
                      member=member, path=str(path) if path is not None else None,
                      source=source, relation=relation,
                      status=asset["status"] if asset else "unavailable" if path else "unresolved",
                      metadata=asset["metadata"] if asset else "not-read",
                      completion="unknown", validation="not-established", publication="unknown",
                      evidence=[])
        if asset:
            record["resolved_path"] = asset["path"]
            record["evidence"] = [dict(hdu=h["hdu"], cards=[c for c in h["cards"] if c["key"] in STAGE_CARDS])
                                  for h in asset["hdus"]]
            category = _role(asset)
            if stage in ("preprocessing", "normalization", "wcs") and category in CALIBRATIONS:
                inspector.diagnostic("stage_header_conflict", path,
                                     "Expected science location reports a calibration category")
                record["relation"] = "conflicting-expected-location"
            if stage == "normalization":
                record["reported_normalized_unit"] = _primary(asset, "BUNIT") == NORMALIZED_UNIT
                record["in_place"] = True
        directory = Path(partition["list_path"]).parent
        record["attempt_partition"] = partition["partition"]
        # Logs/markers describe the partition, not proof of an exposure-specific run.
        record["attempt_scope"] = "partition-only; uninterpreted"
        records.append(record)
        if asset:
            before = len(inspector.rows)
            inspector.add_rows(asset, partition["partition"], stage, member)
            rows = inspector.rows[before:]
        else:
            row = dict(partition=partition["partition"], stage=stage, member=member,
                       path=record["path"], status=record["status"], hdu=None, extname=None)
            inspector.rows.append(row)
            rows = [row]
        for row in rows:
            row.update(role=role, relation=record["relation"], completion="unknown",
                       source=source, input=source.get("input") if source else None,
                       validation="not-established", publication="unknown")

    for partition in inspector.partitions:
        directory = Path(partition["list_path"]).parent
        partition["attempt_evidence"] = [dict(e) for e in inspector.attempt_evidence
                                         if Path(e["path"]).parent == directory]
        # Existing category cards describe product roles; they never establish success.
        # Link edges establish declared references even when the producer is not built.
        linked_paths = set()
        for link in inspector.links:
            if Path(link["path"]).parent != directory or not link["resolved"]:
                continue
            target = link["resolved"]
            asset = inspector.assets.get(target)
            role = _role(asset)
            declared = by_directory.get(str(Path(target).parent), set()) & set(CALIBRATIONS)
            categories = [c["value"] for h in (asset["hdus"][:1] if asset else [])
                          for c in h["cards"] if c["key"] in ("PRODCATG", "ESO PRO CATG")]
            if len(categories) != len(set(map(str, categories))) or len(set(map(str, categories))) > 1:
                inspector.diagnostic("calibration_role_conflict", link["path"],
                                     "Duplicate or conflicting product category evidence")
                append(partition, "calibration", Path(link["path"]), "conflicting-declared-link",
                       source=dict(kind="symlink-category-conflict", path=link["path"]))
                linked_paths.add(target)
                continue
            if role in CALIBRATIONS and declared and role not in declared:
                inspector.diagnostic("calibration_role_conflict", link["path"],
                                     "Product category contradicts declared producer list role")
                append(partition, "calibration", Path(link["path"]), "conflicting-declared-link",
                       source=dict(kind="symlink-category-conflict", path=link["path"],
                                   reported_role=role, producer_roles=sorted(declared)))
                linked_paths.add(target)
                continue
            if role not in CALIBRATIONS and len(declared) == 1:
                role = next(iter(declared))
            if role in CALIBRATIONS:
                linked_paths.add(target)
                append(partition, "calibration", Path(link["path"]), "declared-link",
                       role=role, source=dict(kind="symlink", path=link["path"],
                                             raw_target=link["raw_target"], resolved=target))
        for asset in original_assets:
            if Path(asset["path"]).parent != directory or asset["path"] in linked_paths:
                continue
            role = _role(asset)
            if role in CALIBRATIONS:
                append(partition, "calibration", Path(asset["path"]), "reported-product-role",
                       role=role, source=dict(kind="primary-category", path=asset["path"]))
        if partition["stage"] not in ("science", "standard"):
            continue
        # A lack of selected calibration evidence must not become an invented selection.
        if not any(r["partition"] == partition["partition"] and r["stage"] == "calibration" for r in records):
            append(partition, "calibration", None, "not-declared",
                   source=dict(kind="no-declared-calibration-reference", path=partition["list_path"]))
        names = {}
        for member in partition["members"]:
            if member["path"]:
                names.setdefault(Path(member["path"]).stem, set()).add(member["path"])
        for index, member in enumerate(partition["members"], 1):
            ambiguous = member["path"] and len(names[Path(member["path"]).stem]) > 1
            if ambiguous:
                inspector.diagnostic("ambiguous_stage_location", partition["list_path"],
                                     "Distinct input paths share a legacy product basename")
            supported = member["path"] and Path(member["path"]).suffix.lower() in (".fits", ".fit", ".fts")
            expected = science_product_paths(member["path"], directory) if supported and not ambiguous else {}
            for stage in ("preprocessing", "normalization", "wcs"):
                append(partition, stage, expected.get(stage),
                       "ambiguous" if ambiguous else "expected-location" if expected else
                       "unsupported-input-format" if member["path"] else "unknown-input-base",
                       member=index, source=dict(kind="legacy-product-convention", list=partition["list_path"],
                                                 line=member["line"], input=member["path"],
                                                 identity_verified=False))
    return records
