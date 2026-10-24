# Gaia DR3 source identifiers: production repair and recovery

24 October 2026, [#44](https://github.com/fselman/wenu-imaging/issues/44).
Notebook 09 preflight found 6245/6245 empty SOURCE_ID values in each cached raw
query; both cleaned calibration catalogues inherit the loss. The inspected
notebook 07 run directories contain no original response or TAP job reference.
This blocks catalogue identity/provenance acceptance, not the already checked
pixel scaling. Existing science products and previous evidence remain intact.

The production method selected duplicate unaliased source_id columns, removed
one, then reindexed to uppercase SOURCE_ID without retaining/renaming the other.
The new query explicitly aliases DR3 and GSPC identifiers and validates equality,
non-null integer type, positive signed-64-bit range and uniqueness before keeping
SOURCE_ID. Cached IDs are first read as decimal strings and then converted to
int64; no float intermediate. Broken caches fail before rewriting cleaned data
or issuing another query. Geometry, columns used for photometry, transformations,
selection and calibration remain unchanged. This does not recover old IDs by itself.

## Bounded recovery tool

`Pycavi2/tools/recover_gaia_source_ids.py` accepts a JSON manifest listing up to
four `{path, sha256, group}` inputs. The current pilot has raw and clean CSVs for
each filter. It requires that every existing ID field be empty, validates input
hashes/positions/row widths, and derives one bounding box from the cached DR3
positions (margin 1e-6 degree in declination and cosine-adjusted RA, covering the
full identity-matching radius; at most two degrees per axis and 12000 unique
positions). The one anonymous query requests only DR3/GSPC IDs and DR3 positions,
with TOP min(25000, 2*N+1). Hitting the cap is a failure, not evidence of completeness.
No photometry is retrieved or replaced. RA-wrap boxes or positions at |dec| >=85 degrees
are rejected rather than silently widening the request.

Without `--allow-network`, the tool prints its preflight/query and makes no writes
or requests. With it, run at niceness >=10 and supply a new output directory.
The query child has socket timeout 30 seconds and a parent limit of 180 seconds.
It preserves ADQL, job ID before waiting, native VOTable, phase and hashes; VOTable QUERY_STATUS must be present and OK. A
failure records an error and performs no retry; inspect the retained job record
before considering another query (a timeout can leave an archive job running).

Each cached position must have exactly one response within 0.0001 arcsec, using
spherical coordinates. This tight same-release/epoch identity check is deliberately
not a general nearest-neighbour scientific crossmatch. Missing, ambiguous,
non-integer, duplicate or many-to-one identities fail. All mappings are checked
before writing, then the complete catalogue directory is published by rename.
Original files are never overwritten. Repaired CSVs preserve row/column order and
every non-ID field's parsed text, including numeric formatting and missing values;
CSV quoting/line endings need not remain byte-identical. Each output has an exact
row/ID/separation mapping CSV, hashes, and a report. These outputs are inputs to
later catalogue staging, not automatic replacement of calibration provenance.
No image edits, zero-point recalibration or model refitting occur.

## Verification and remaining acceptance

Eight focused offline regressions passed from source and against an isolated
wheel installation; ten installed-package/resource checks also passed. Records:
`/tmp/wenu-gaia-id-check-qyxz6pj_` (initial wheel/checks), with final focused rerun
against the same installed code after mapping-sidecar/test additions. Tests execute
the actual production query method body with a fake TAP client, exact large-ID
CSV/FITS round trips, invalid cache rejection without requery/clean-file changes,
all-match-before-publish, unchanged non-ID field strings, ambiguity/missing/cap
failures, preflight no-write/no-query behavior and one-attempt timeout handling.
They do not run a full calibration or a live query, and do not establish target
installation or independent photometric accuracy.

Chapman3 installation and live recovery are pending. Keep #44 open until both
filters' original raw/clean inputs match unambiguously, identifiers survive target
CSV/Table/FITS round trips, non-ID fields and original hashes are unchanged, and
the target installed production method/cache tests pass. Notebook 09 is not yet
qualified. PR #43's reader correction remains a separate unmerged prerequisite.
