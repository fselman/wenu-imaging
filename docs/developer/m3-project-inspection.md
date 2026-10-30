# M3 first increment — explicit bases and read-only legacy inspection

Subsequent corrected target verification passed 15/15 on both Mac and Chapman
at 2c820effff393d5ea4e1555439397ef7c7a6cda6, with protected installed files and
checkouts unchanged. See [paired results](m3-project-inspection-paired-results-2026-10-30.md). Earlier draft/target-pending
statements in this retained receipt are historical; full M3 remains open.

Subsequent target run: original 14-group driver passed on Mac but failed three
canonical fixture comparisons on Chapman. See the [correction and exact evidence](m3-inspection-canonical-fixtures-2026-10-30.md).
The corrected driver has 15 groups and passes agent alias reproduction; corrected
actual target checks remain pending. Production inspector/path behavior is unchanged.

30 October 2026. M2 was owner-accepted/closed and PR #158 merged at
`b872c8f44c1b54982069a3f94735da492a9dd739`; returned Mac and Chapman main were clean
and the merged branch removed. The owner instructed Proceed with original M3.
[Tracker #159](https://github.com/fselman/wenu-imaging/issues/159) retains its full
scope. This first increment implements path-base primitives and a bounded legacy
metadata inspector. It does not complete M3 or route numerical execution yet.

## API and command

New outer-package modules:

- `Pycavi2/pycavi/pycavi_paths.py`: `PathResolver` captures an absolute invocation
  base; `.argument` resolves user paths once, while `.reference` requires an
  explicit absolute base for relative document/list references. No cwd change,
  environment-variable expansion or filesystem writes occur.
- `Pycavi2/pycavi/pycavi_project.py`: `inspect_project` and `main` share the same
  metadata path. It reuses ConfigParser and Astropy FITS, not new CFG/FITS parsers.
  It imports no reduction wrapper and launches no engine or external astronomy tool.

The new console target is `pycavi = pycavi.pycavi_project:main` in the existing
Python distribution. It does not modify installed scripts during source testing.
Existing setup commands and dependency bounds are unchanged. In an exported
checkout use the selected Python directly; installing a new wheel is not required:

```bash
/absolute/python -B /absolute/checkout/Pycavi2/pycavi/pycavi_project.py \
  project inspect /absolute/project --recursive \
  --project-config /absolute/selected/pycavi.cfg \
  --instrument-config /absolute/selected/wfi.cfg \
  --list-base /absolute/recorded-original-execution-directory
```

This is interface documentation, not an instruction to inspect private observations
now. Do not substitute the list's parent directory for an unknown historical base.
The inspector reports unresolved relative members when `--list-base` is omitted;
absolute members do not require it. Relative selected legacy CFG directory values
use that same explicitly supplied legacy base, or are reported unresolved. It does
not guess a legacy base from a containing file. Future TOML/ASDF references use
the explicit containing-document/root bindings required by the plan.

## Evidence, order and authority

Named `bias.list`, `dome.list`, `sky.list`, `mff.list`, `std.list` and `science.list`
are the membership interfaces in the existing PartitionsTree/ExposuresPartition
source. Their role and line order, repeated members, raw lines and columns are
retained. Relative tokens resolve from the declared original base. The read-only
adapter follows charmatrix's first-column/space-tab/comment-at-column-zero rules;
unknown list-role files and extra columns are visible diagnostics, not invented quoted filenames. CR-bearing
and overlong legacy lines are explicitly unsupported. A base directory containing
spaces works; whitespace within a legacy filename token is not newly supported.

Selected project CFG uses existing ConfigParser interpolation; selected instrument
CFG uses its existing inline-comment behavior. Both raw text/values and interpreted
strings are retained. Instrument primary-keyword mappings select instrument,
object/target, filter and exposure cards. Without an instrument CFG the four
explicit standard-key defaults are INSTRUME, OBJECT, FILTER and EXPTIME; no private
instrument configuration is implicitly discovered or installed. This is evidence
inspection, not validation of a configuration's suitability for execution.

The declared root tree is traversed in sorted order within the coverage limits.
Canonical file references deduplicate shared assets, while partitions retain every
membership and link edge. Duplicate basenames remain separate assets by resolved
path. File links retain literal and resolved targets, including missing targets.
Directory links are recorded but not recursively followed; cycles/omitted coverage
are diagnosed instead of guessed or repaired.

FITS is opened read-only and lazily through a bounded header stream. Astropy reads
HDU headers and seeks past payloads; no `.data`, pixel/table array loading, full-file
hash or data validation is requested. Reported extension names, HDU indices/types
and dimensions describe observed layout, not verified physical detector identity.
The four mapped primary fields remain explicitly primary-header evidence; local
extension values/cards stay separately available, and conflicting values are
reported. Duplicate selected FITS cards remain separate; no first/last authority
is silently chosen. Missing fields remain unavailable.

Assets are unavailable or existing-unverified. Successful header reading does not
validate calibration applicability, normalization, WCS, scientific processing or
publication. `toreduce_*` markers and log paths are present-uninterpreted evidence;
log text is not treated as completion proof. Other FITS files remain unclassified
files or linked references. Filename matches do not establish successful products
or historical calibration selections. No association policy is recomputed.

## Views and bounded coverage

Default output is a concise overview plus a table. Optional controls:

| Option | Meaning |
|---|---|
| `--columns NAME ...` | Select row fields or exact FITS card names; quote HIERARCH names containing spaces |
| `--where COLUMN=VALUE` | Repeatable exact string equality over a selected column or row field |
| `--sort COLUMN` | Stable numeric ordering for numeric values, then strings, then unavailable values |
| `--partition PATH` | Drill down to a root-relative partition |
| `--stage ROLE` | Drill down to declared list role or observed reference category |
| `--detector EXTNAME` | Select reported extension name; no hardware identity claim |
| `--format json` | Current machine-readable JSON notation on stdout for notebooks/tools |

JSON here is a transient metadata export to stdout; no new project store or saved
format transition is introduced. Existing M2 JSON outputs remain as instructed;
M7's planned ASDF service is unchanged. Table text escapes control bytes so paths
and card values cannot corrupt tabular terminal output. JSON preserves full raw
and selected metadata plus the view; filters do not erase the underlying inventory.

Coverage reports declared traversal counts, limit values, diagnostic counts/codes
and completeness. Recursive false, unreadable/missing references, unsupported
inputs, directory links and limits are visible. Coverage is scoped to the declared
root tree and explicitly selected/listed file references; configured external roots
are not automatically scanned. It is not certification that all project assets or
metadata are known. Default ceilings are 10,000 entries/assets and total list
members, 1,000 directories, depth 32, 10,000 lines per list, 4 MiB per selected text
file, 128 HDUs and 4 MiB of header reads per FITS file. Library callers can supply
positive explicit `Limits`. Partial output retains its diagnostics.

A valid inspection returns CLI status 0 even with incomplete coverage; consumers
must inspect coverage/diagnostics. Invalid invocation/root/config path resolution
or unavailable dependencies returns nonzero. Neither outcome writes project files.
Inspection is not an atomic filesystem snapshot; concurrent external changes may
produce diagnostics, and no transaction or recovered immutable run is claimed.

## Actual checks and retained attempts

Agent Linux, Python 3.12.14, private test environment with existing declared
Astropy 6.1.7 / NumPy 1.26.4 dependency versions. This private test installation
changes no user/selected environment or repository dependency bounds.
`Pycavi2/tests/project_inspection_contract.py` runs 14 grouped unittest controls.
Final corrected run: 14/14 passed, 3.398 s, in
`/workspace/scratch/555b377cf948/m3 project inspection iadqqrx2`.

The suite covers explicit bases, nested/shared/repeated memberships, duplicate
basenames, both committed instrument mappings, raw CFG authority and unknown
bases, malformed FITS/CFG/text, FIFO rejection, dangling/cyclic links, directory
links, text/list/entry/depth/HDU/header limits, duplicate/conflicting FITS cards,
views and malformed CLI controls. It compares actual CLI/library reports from
two unrelated caller directories and the console target through package import.
Read-only fixture files/roots retain bytes, permissions and mtimes; cwd remains
unchanged. Traps on Astropy image/table array loading prove the header-only lane.
Independent caller mutation cannot alter a later report.

Retained attempts:

- Initial run: 12 pass / two fixture failures. Absolute legacy tokens containing
  whitespace were invalid fixture assumptions; corrected to relative members with
  an explicit base. Production list semantics were preserved.
- Intermediate corrected run: 14 pass before adding package-entry/extra controls.
- Expanded run: one JSON-decoding error from the nested package's existing import
  banner. [#59](https://github.com/fselman/wenu-imaging/issues/59) records that banner
  as owner-requested; it remains unchanged. [#160](https://github.com/fselman/wenu-imaging/issues/160)
  tracks the new command's entry placement correction. New modules now live in the
  outer command package; no global stdout suppression or old import change.
- The corrected package-entry run passed 14/14 in 6.972 s; final controls also
  diagnose discovered compressed FITS and unknown list roles. The final run above
  passes all 14 groups.

[Retained agent evidence](fixtures/agent-m3-project-inspection-2026-10-30/README.md)
contains the logs, final report, selected environment inventory and source hashes.
Actual selected-tool Mac/representative Chapman checks remain pending. No target
pass, installed-wheel acceptance, C90/C17/sanitizer or numerical qualification is
claimed. Source syntax/metadata and documentation checks are separate.

## Remaining M3 gate

This first increment supplies metadata inspection/path primitives, not a completed
M3 inspector or execution integration. Complete the original M3 routing through
CLI/loaders/context/writers for explicit input/list/calibration/config and
output/work/log destinations; replace mandatory cwd changes/implicit PAF search in
the new execution path, preserve private legacy arenas only where required, handle
duplicate output basenames and show same-request pixel/metadata equivalence from
two caller directories with read-only input roots.

Extend the overview with authoritative calibration/product role and processing-stage
provenance as those explicit references become available. This first adapter does
not decode PAF product names, identify validated normalization/WCS outcomes or
resolve ASDF projects. The full M3 inspection/processing gates remain on #159;
none are waived or moved. Later ASDF/planning adapters reuse the path and reporting
boundaries rather than inventing a second scientific association engine.

No original data, installed package/engine, normal reductions, numerical C,
scientific defaults, ASDF scope or later milestone order changes. Owner review
and actual target checks precede separately instructed merge/cleanup.
