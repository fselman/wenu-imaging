# M3 inspector compact summary and aligned tables — 31 October 2026

31 October [summary/alignment paired receipt](m3-summary-paired-results-2026-10-31.md): source
fc4b26cd1a1eed828a88d818fcdbb7912a2acbe2 passed 24/24 on selected Intel Mac
(6.938 s) and representative Chapman4 (3.563 s), with installed files and clean
main preserved. Direct real --summary displays five aligned CN Ori exposure rows,
retaining warnings and the missing historical flat reference without a wrapper.
The owner-requested interface addition is qualified; M3 closure is recommended
for owner acceptance, then separately instructed merge/cleanup and M4 review.
Documentation-only receipt: no executable change, test replay, install or host sync.
Earlier pending/held notes retain their stated historical scopes.

Owner-requested addition before M3 closure, based on review head
`400d237e673083556a54be726dce0a0a477393a0`, refs #159/PR #178.

**Implemented: `--summary` directly displays the compact exposure report that
previously required a wrapper. Both compact and detailed table titles now align
with measured-width fields. Agent suite passes 24/24; actual selected Mac and
representative Chapman qualification of this presentation addition is pending.**

## Usage and output contract

Add `--summary` to the same `pycavi project inspect` invocation and explicit
root/config/list-base arguments. No additional script or installation is needed.
It reuses the already collected report, without additional metadata reads or any
pixel access, processing, association selection or header modification.

The fixed compact columns are Member, File, Target, Filter, Exposure (s), HDUs
read. Add Partition when multiple partition paths are displayed and Role when
standard memberships are present. Science/standard memberships retain their
identity and order, including repeated members and missing/unresolved inputs.
There is one summary row per selected list membership, not one row per HDU.
HDUs read counts readable headers, including the primary; it is not a physical
detector or pixel-validation count. Missing values display as `-`.

File is the basename for compact reading; full canonical path, original list and
member identity remain in JSON. Fixed summary columns use raw exposure primary
header evidence, including when a processing-stage or detector filter selects
that exposure. This does not claim a selected processing stage completed.
Existing partition/exposure/stage/detector/where controls select summary members;
an explicit sort orders them by their first selected detailed row. Without a
selection, unresolved members remain visible rather than disappearing.

`--columns` continues to control the detailed table. `--summary --format json`
retains the full original report/view and adds `summary.rows`, with explicit
raw-header-only authority and unverified completion. Without `--summary`, the
JSON structure is unchanged. Table spacing is for human display; JSON remains
the structured interface.

Tables use spaces measured over actual rendered fields, not tab stops. Numeric
values/titles align at the right edge of their columns; text aligns left. Names
are shown without JSON quotes in the compact view; detailed cells retain their
prior escaped notation. Control characters remain escaped. Combining/wide
Unicode display widths are handled without another runtime dependency. No value
or title is truncated to force alignment.

## Diagnostics are retained

The compact output includes counts labelled for the whole inspected project,
all non-warning diagnostics with their source paths, and all warning messages
for the first affected file. The full JSON retains every warning/diagnostic;
the summary does not suppress errors or reinterpret unknown completion as success.
Readable ESO metadata/non-fixing warnings from corrected #180 remain unchanged.

## Focused verification and next gate

[Agent evidence](fixtures/agent-m3-summary-2026-10-31/README.md): 24/24 in 5.995 s,
existing private environment at nice10 with bounded numerical threads. The two
new groups verify independent summary expectations for repeated/missing/unknown
members, raw metadata selected through WCS-stage filtering, distinct standard
partitions and actual rendered title/value positions with unequal file names,
target lengths and exposure values. Existing no-array/no-write/caller/header
controls and original/updated client-body comparisons remain in the suite.

The actual-host runner now requires exactly 24 groups. Qualify selected Intel Mac
then representative Chapman4 with protected installed files/clean main and private
exports. Display the historical CN Ori case directly with `--summary` on the
corrected qualified source. No wrapper should be needed for formatting output.
No C build, solver, native engine, observations or install is part of the suite.
Original reader/scientific behavior and prior 22-group real-tree evidence are
preserved. Owner acceptance and separately instructed merge/cleanup remain pending;
M4 detector/layout review remains next. No new scientific prerequisite is added.
