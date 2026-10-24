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

## Chapman3 acceptance, 24 October 2026

Commit `9fcde16172afb5cd2a0c25218bda1230034e169b` installed and passed eight
source and eight installed ID regressions, ten installed-package/resource checks
and pip check. Installed helper, zpcal and Kriging modules match the pinned
source. Records: `~/wenu-gaia-id-fix-q2nr2iv3`; wheel SHA256
`789cb0dbfb6f76df34d7c4fc64be17b908f70ffc2ec539adcd5cf351c616599d`.

The single recovery job completed in
`~/omegacam/testing/wenu-imaging-test/gaia-id-recovery-jh763zwi`:

- Job `355a4f3e-cfa9-11f1-9d98-bc97e148b76b-O` at the Gaia ESA TAP endpoint.
- Query SHA256 `43d08a34433c8c2e8c93eeb6d8bcd258656a6997853ee8c227f511d4d10ce08f`.
- Native response SHA256 `d6160348a631b92808bfeeda126868f6a9b1cf43591f2097495f79ddcf3d1505`.
- Both raw 6245-row files and both clean 981-row files recovered unique exact IDs,
  each with maximum separation **0.0 arcsec**. Every non-ID field and input hash
  is unchanged. Per-row mappings and report remain with the native response.
- Target `identity-output-check.json` independently reread original/repaired CSV
  fields, checked all mapping rows/hashes and clean-ID subsets, and verified exact
  int64 identifiers through the installed cache reader, Astropy Table and FITS
  round trips in memory. No query was repeated and no calibration was rerun.

| Recovered output in `recovered/catalogues/` | SHA256 |
|---|---|
| r_SDSS/gaia3_qry_CN_Ori_raw.csv | 1fb92e95277c88d923e1d458baf29571bf654bbe9e270240e54e688f9cd8732a |
| r_SDSS/gaia3_qry_CN_Ori_r_SDSS_clean.csv | 87cba6b3bfdb33ef42ffdad68801796d7b17484226bce491f56b5ba0142248ec |
| NB_659/gaia3_qry_CN_Ori_raw.csv | 560dca89d85b081ec11d85feaa922518af3a2e6197a84c81c1ca06de40cea186 |
| NB_659/gaia3_qry_CN_Ori_NB_659_clean.csv | a0578f6d30c512a6375db925d5667884bc685646fb1fa3ac8665b334604c03c8 |

#44 acceptance is met; a correction/evidence comment precedes closure. PR #45
remains unmerged and is stacked on unmerged reader PR #43. Use recovered CSVs
only in fresh notebook 09 staging; existing calibration headers/files and science
products remain immutable. Functional identity acceptance does not validate
catalogue construction, scientific photometry or later illumination correction.
