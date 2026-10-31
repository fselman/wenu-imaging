# M4 first native layout increment — 31 October 2026

Owner accepted the interface/fixture review and instructed implementation after
the Windows clarification at `c81cb86f79659fba89bed9ba16e6a96cbad62992`.
Track [M4 #182](https://github.com/fselman/wenu-imaging/issues/182); this candidate
is on `feat/m4-native-layout-20261031`, based on the unchanged review/helper
branch `docs/m4-interface-fixtures-20261031` (PR #183). The owner's pending Mac
helper command therefore remains pinned to its accepted source.

## Integration and next target step

PR #192 is accepted and merged at `c4a5ba491b087e7e690ef6e53ed5ff2a250dd3ca`.
Both actual checkouts are clean there and installations are preserved. PR #186
now targets main; its prerequisite branch was deleted after integration. The
historical pending-helper wording above describes the original publication only.
The merged candidate retains both native and preflight histories and changes no
native C, CMake, fixture or oracle bytes from `a7bb518116cc5df674507e6c3cca24a70ca335fe`.
Agent Linux C90/C17 layout+bias pass 2/2 in 1.22/1.24 s; normal mefpp links in both
lanes but is not executed. [Integration receipts](fixtures/agent-m4-integration-2026-10-31/receipt.json)
retain logs; these durations are not benchmarks.

[qualify_native_layout.py](../../mefpp2/tests/qualify_native_layout.py) is the new
private Mac/Chapman runner. It requires explicit absolute selected tools, pinned
source, niceness >=10 and clean main c4a5ba4. It exports exact tracked source into
a fresh retained build directory, builds layout/bias probes and links the normal
engine in optimized C90 and C17, inventories exactly the two focused contracts,
and runs only tiny synthetic FITS. Original observations are never opened. It
verifies installed module/engine/configuration, checkout and exported source on
success/failure and retains qualification.json plus command logs. No install,
normal-engine execution, sanitizer, scientific or performance claim. Runner
syntax is checked; actual target runs remain pending. Tool discovery precedes
the first Mac launch rather than guessing compiler/SDK/CMake paths.

The original M4 gate compares an extracted detector with its mosaic counterpart
under the same required shared context. Full calibration/science command adapters
belong to M5/M6. Target layout/bias acceptance alone must not be described as full
M4 closure: instrument mapping, applicable shared-reference equivalence and
matched performance assessment remain for cumulative review. Keep this boundary
explicit so deferred services do not silently become prerequisites or claims.

## Implemented C boundary

[mef_layout.h](../../mefpp2/ins/mef/common/mef_layout.h) and
[mef_layout.c](../../mefpp2/ins/mef/common/mef_layout.c) implement the first internal
C90 catalogue/map/plane-loader boundary. It is opt-in through the existing
`MEFPP_BUILD_CONFIG_PROBES` development library, not an installed/frozen ABI or
normal-engine switch. No new parser/library dependency or Windows abstraction.

- `mef_layout_read`: bounded FITS header framing uses existing qfits card parsing,
  skips opaque payload by checked offsets, and retains original HDU order, type,
  dimensions/scaling, independently present EXTNAME/EXTVER, optional caller-named
  identity/amplifier cards, binning, unit and raw geometry evidence. It reads no
  image arrays and never modifies headers. Unselected telemetry values are not
  parsed. Default bounds are 4096 HDUs/16 MiB total header blocks; NAXIS above 3,
  random groups and unknown extension types are unsupported. Structural/card
  conflicts, malformed required values, truncation and arithmetic overflow fail.
- `mef_layout_bind`: each file independently binds explicit logical detector IDs
  by checked header ID or explicit HDU/index/name/version assertions. No absent
  EXTVER or physical identity is invented. Map owns its path/metadata, outlives
  catalogue/caller descriptors and preserves original HDU order including excluded
  detectors. Physical IDs are configured claims; header matches do not verify
  hardware. Explicit readout/geometry context, binning, active rectangle, unit,
  configuration-detector index, health and output selection remain distinct.
- `mef_layout_compatible`: pairs selected science/calibration planes by logical
  ID, checking explicit units/readout context, known physical/amplifier conflicts,
  binning and active dimensions. Raw science can include scans while a calibration
  is already trimmed. A required normalization reference is supplied separately,
  including when excluded from output; missing required context fails. The caller
  has already selected calibrations. No association or normalization algorithm.
- `mef_layout_load`: checks source identity and calls the existing
  `image_loadext(path, index, 0, 1)` for all layouts. FITS scaling and the working
  plane remain in Eclipse/qfits; the new layer adds no full-image copy. Dimensions
  stay within the existing loader's int pixel-count range. BITPIX64 is discoverable
  but loading is explicitly unsupported by this existing pixel loader.
- `mef_cal_bias` now accepts the same validated in-memory plane for HDU 0 as for
  an extension. Its old HDU-0 rejection is removed; arithmetic, ownership, scans,
  trim, rejection and QC are unchanged. The old unsupported-primary control is
  replaced by actual loaded-primary/extension/mosaic numerical equality in the
  new C probe. Existing bias regression otherwise remains intact.

Metadata owners use the existing allocator/status/error pattern, including
NULL-start/occupied-output handling and authoritative allocation-failure status.
Loaded images retain their existing `image_del` owner; legacy global allocator,
cache, thread-safety and whole-dependency OOM policy are unchanged. Input files
must remain immutable during use: stat comparisons are not snapshot locks and
do not defend against deliberately restored timestamps or concurrent path races.

The first map supports one two-dimensional image per logical detector, with raw
amplifier/geometry evidence; multi-HDU amplifier reassembly is not implemented.
Configured geometry/readout identity is explicit caller authority, not independent
verification of every instrument's physical coordinate model. Raw-unit fallback
is marked configured rather than a fabricated BUNIT. Classification/admission
remains the separate [preparation contract](../data-preparation.md).

## Focused agent qualification

Existing private tools, optimized GNU C90/C17 builds, no resource install or
environment upgrade. Normal `mefpp` also links in both modes; numerical code in
that executable is not switched to the opt-in layout library. Retained
[evidence](fixtures/agent-m4-layout-2026-10-31/README.md) records exact sources,
commands, build/cache locations and scope. Actual target evidence remains pending.

| Check | Evidence |
|---|---|
| First C90/C17 layout + existing bias | Both 2/2 pass (1.45 s / 1.34 s); preserved before later guard/control additions |
| Corrected C90/C17 layout + existing bias | Both 2/2 pass (1.26 s / 1.34 s), including #185 FIFO refusal and hierarchical/telemetry controls |
| Scoped C90 ASan/UBSan layout + bias | 2/2 pass (4.57 s), no sanitizer finding; leak detection disabled for legacy global caches |
| Final layout refinements | Affected layout test repeated in C90/C17/ASan after configured-primary and active-region controls, then final pixel-count guard; final logs/source hashes retained separately |

The actual C [probe](../../mefpp2/tests/layout_probe.c) is driven by tiny stdlib
[FITS fixtures](../../mefpp2/tests/layout_contract.py), for both actual OCAM/WFI
configuration constructors. Its six groups cover unsigned endpoints/scaling in
primary/one-extension/mosaic storage; absent EXTVER and configured unknown identity/
units; shuffled independent calibration HDUs; selected order/health/reference;
duplicate/missing/inconsistent selectors, units/binning and active rectangles;
header/HDU bounds and malformed/truncated/FIFO input; every new metadata-owner
allocation position; source-change rejection; and actual `mef_cal_bias` equality
across storage layouts with the same required scan/calibration configuration.
Known-answer bias pixels are independently asserted and immutable input files
are SHA256-checked. Only the designated mutable synthetic fixture is changed.

Source finding [#185](https://github.com/fselman/wenu-imaging/issues/185): the first
candidate used fopen before checking regular-file type, permitting FIFO blocking.
It is corrected with a pre-open regular-file check plus opened-identity comparison
and a FIFO control. No production/target hang was observed. Keep #185 open pending
actual Mac/representative Chapman qualification; initial sources/logs remain saved.

## Remaining M4 gates and handoff

M4 remains open. Qualify this candidate on selected Intel Mac and representative
Chapman using fresh actual tools/checkout evidence, protected installed files and
private source/builds. Do not reinstall or activate. The pending Bath helper plan
is a separate actual-Mac preparation check and does not exercise this C API.

Complete actual instrument metadata/mapping review and integration into the
execution adapters at the appropriate boundary. The tiny bias equality above is
not complete science/shared-normalization equivalence: this increment checks
reference availability without changing that algorithm. New normal-engine request
dispatch, writer selection/publication and multi-amplifier processing are not
claimed. Full Bath no-scan calibration remains unsupported; primary loading alone
does not qualify CMOS/gain/noise/dark applicability or M6a variance.

Native performance preservation remains a required pending same-workload gate.
No benchmark or throughput claim follows from test durations, unchanged inner
loops or a successful link. The current normal engine is not activated with this
new boundary. New layout discovery uses ordinary Mac/Linux stat/fopen/fseeko and
timestamp fields; note those for a possible later Windows adapter only. They add
no Windows-driven abstraction, overhead or Mac/Linux acceptance condition.

After actual evidence and remaining original gates, perform cumulative review
before claiming full M4 closure. No merge, cleanup or installed activation is
implied by the owner's authorization to implement this increment.
