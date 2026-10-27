# S2-05 focused BPM ownership repair — 27 October 2026

Status: source repair prepared, actual native Mac compilation/execution pending.
Tracking #109, #110, #111, #112 under #75. Stacked on the retained failed baseline
in PR #108; no merge or branch deletion is authorized. See the
[inspected baseline and exact allocation-size ledger](stage2-bpm-baseline-evidence-2026-10-27.md).

## Changes and preserved behavior

Only two production C files change: common/mefp_lib.c and src/iproc/pixelmaps.c.

- #109: mef_cube_load releases its locally acquired frame list after its helper
  returns. The helper's sole source caller was audited; its inconsistent early
  destruction is removed, giving it a borrowing contract on every return path.
  This avoids introducing double destruction on consistency failure. Returned
  cube planes hold loaded image data, not the frame-list object.
- #110: release scan_double immediately after double_rms, its last read. Median,
  centering, RMS, QC assignments, pixel subtraction and trimming are unchanged.
- #111: pixelmap_dump releases an internally created default FITS header after
  its last use, also on output-open failure. Caller-provided fextra remains
  borrowed and is never destroyed there. Formatting, void return API, data
  writes/padding and publication/error policy remain unchanged.
- #112: BPM publication releases each input primary header and the first input
  extension header after final access, releases its publication frame list,
  keeps its DATE-OBS copy until insertion then releases it, and frees the heap
  output filename after copying. Other input metadata values are borrowed while
  the input header lives because qfits insertion makes its own copy. The context
  destructor releases owned orig_bpm; all repository assignments of that member
  were traced and allocate with strdup. Its NULL-initialized partial-context
  lifetime remains safe. The existing input-header failure return also releases
  locally acquired objects. No new failure-injection mechanism is introduced.

Do not change gains, regression/normalization arithmetic, scan values, mask
thresholds/polarity, pixels, headers/order, detector identities, timestamps or
installation selection to make the resource gate pass. No allocator/cache source
or XMEMORY setting changes. Generated ORIGFILE values remain timestamp-based.
Other recipes' generated metadata members are not silently added to this repair.

## Verification prepared

The native observer, accepted original driver, fixture bytes and independent
output oracle remain unchanged. The retained runner adds a pinned
`--baseline-reference` report and records both changed source files plus the
frame-list implementation. It checks the original baseline source identities
for all unchanged dependencies; the common library and runner are the declared
changed entries in that baseline registry. The original pixelmaps.c identity is
retained in the baseline full build source lists.

Run the same **16 pairs / 32 native calls**, C90/C17 ASan/UBSan and separate
external leaks, on fresh private Mac builds/directories. All returned/production
mask hashes must match the older accepted #90 references, and every normalized
header card, extension, count, threshold and input must additionally match the
inspected failed S2-05 baseline. Only recorded generated ORIGFILE values are
excluded from paired header equality; full raw output hashes are retained.

The old after-driver and intermediate measurements remain recorded. Every
post-purge and second-purge resource field must reach zero; context/mask release
and descriptor contracts must pass with clean diagnostics. Preserve the failed
baseline and verify both reference hashes unchanged. Any residual or unexpected
state remains a finding; the source ledger does not substitute for this run.

Preparation validation: all baseline archive hashes, 32 role input/output sets,
16 paired/reference masks and raw native logs were checked; all postpurge size
multisets match the independent source/FITS-length ledger. Corrected runner
Python syntax, unchanged observer/oracle/fixture identities, source lifetime/
sole-caller audit and whitespace checks pass. No corrected native test ran in
the agent environment. Actual Mac verification and unchanged-driver Chapman3
functional/accounting verification remain pending; tickets #109–#112 stay open.

## Boundary

The current retained cases exercise successful OmegaCAM robust/proportional
construction, bias=NULL and one extension. Some metadata values are absent in
the original synthetic inputs; populated-value borrowing is source-traced, not
independently runtime-qualified by this fixture set. Header-open failure,
consistency-error and shared helper branches are source-audited here; exhaustive
failure injection, other recipes, WFI, multiple extensions, non-NULL bias,
repeated stages and general cache/mmap/swap remain in the applicable later or
remaining S2 gates. No departure or reduced completion criterion is approved.
The first fixture subset is not full S2-05 or Stage 2 acceptance. Compatible
target external diagnostics remain an open gap. Preserve all runs/installations;
prior agreement is required before departures and mandatory review still
precedes Stage 2A/component extraction.
