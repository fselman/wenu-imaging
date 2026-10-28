# S2-05 two-extension OmegaCAM/WFI BPM ownership — 28 October 2026

Status: test-only preparation from merged main
`664f501fe723a924b6a2395d00f70cba1fb03ab7`, following Fernando's instruction to
proceed. Actual Mac processing and subsequent unchanged-driver Chapman3
verification are pending. No production source, normal installation or
observational data is changed.

## Boundary and purpose

Continue S2-05/#75 with two distinguishable image extensions for both instrument
configurations. Exercise the first-extension primary-header creation and the
later-extension append branch of `mef_build_bpm`, plus context/returned-mask
ownership. This does not finish S2-05 or authorize S2-06. #116 remains open and
unresolved; stop on any finding and retain exact per-descriptor evidence.
All earlier supplied-bias, metadata, baseline, repeat and target evidence stays
preserved. The new raw linearity frames are not accessed or processed.

Two synthetic extensions are a bounded create/append gate, not full 8-chip WFI
or 32-chip OmegaCAM qualification, observational WFI validation, general error
injection, S2-09 repeated-stage acceptance or mmap/swap qualification. Those
requirements and compatible Chapman3 external diagnostics remain open. No merge
or deletion of this new branch is authorized.

## Inputs and native processing

The immutable retained and known-response three-frame fixtures and populated
first-frame metadata are reused. Extension A retains its exact 9x18 payload.
Extension B mirrors only the 9x9 science area in X, retaining the overscan bytes,
padding and a distinct EXTNAME. Expected masks are the accepted 81 pixels and
their exact mirror; they are explicitly checked to be distinguishable. This
makes a wrong extension selection observable. The input manifest fixes every
derived file identity. Original instrument PAFs are staged unchanged.

The new driver constructs one context with `mef_bb_new_from_paf`, selects
extensions 1 then 2 and releases each returned mask once before destroying the
context with `mef_bb_del`. Only the synthetic geometry, flags and thresholds are
set in the driver: 9x9 science, columns 10–18 overscan, no prescan, zero scan
rejection and the already agreed 0.5–1.5 bounds. WFI's installed PAF upper bound
is not edited; the test explicitly uses the common accepted threshold contract.
Bias is NULL in this slice; supplied-bias acceptance remains separate.

Actual calls are `mef_build_bpm` → `mef_cube_load` →
`mef_cube_overscan_correction` → `cube_create_gainmap_robust` or
`cube_create_gainmap_proportional` → `image_normalize` →
`image_threshold2pixelmap` → `pixelmap_dump`. Header publication, frame-list
loading and qfits header lifetimes are exercised inside this path. Pycavi is not
called. There is no new calibration algorithm or numerical-policy change.

## Mac matrix and acceptance

32 ordinary/observer pairs (64 native processes): C90/C17 × instrument
OmegaCAM/WFI × retained/known-response × robust/proportional × separate
ASan/UBSan and uninstrumented external-leaks lanes. Each process calls the
constructor twice, once per extension. The tested allocator remains mode 2,
maximum 2,000,000 registrations. Qualified tool controls and accepted metadata
reference reports are pinned and verified before execution.

Required results:

- Exact returned/saved pixels for each extension, mask polarity/counts, BITPIX 8,
  no scaling, exactly one primary plus two image HDUs and the declared detector
  order; no extra products or changed staged inputs.
- Exact ordered canonical reference cards except declared INSTRUME, TELESCOP and
  EXTNAME values. The second extension omits the six primary metadata cards that
  the unchanged constructor inserts only for extension 1. Their absence is an
  explicit baseline contract, not a new propagation correction. Generated
  ORIGFILE is recorded separately and must be shared/nonempty across all HDUs.
- One context constructed/destroyed, two masks built/released, no live owner or
  ownership mismatch. Twelve allocator boundaries include both build/release
  sequences. Process start and both purges must be zero; all other observations
  remain retained for attribution.
- Exact descriptor identities at driver return and both purges, per-fd details,
  clean ASan/UBSan and zero external leaks. No exclusion or weakened gate.
- Source/export/reference/selected engine/configuration/checkout preservation.
  Fresh retained provenance precedes builds and processing; any finding stops
  subsequent cases and leaves a failed/incomplete report.

The first actual Mac run is the baseline for these new cases. Its full evidence
must be inspected before preparing an unchanged native target runner. Agent
Python/syntax checks do not establish Mac or Chapman3 acceptance.

## Preparation verification

`check_bpm_multiext_preparation.py` checks input science/overscan/padding and
original PAF readback, anchors the independent mask to the accepted reference,
constructs synthetic output controls and rejects deliberate wrong pixels,
first-frame metadata and complete-HDU order. Constructed controls test the
oracle, not production algorithms. Retain failed and corrected preparation
reports and source hashes. C90/C17 syntax-only checks compile both driver and
observer with production allocator definitions, without native execution.

The first preparation attempt exposed an incorrect fixed-offset HDU-swap
negative control. It is retained as failed preparation; the control now swaps
complete header/data HDUs. The corrected check passed eight constructed cases
and 24 deliberate rejections. No production defect is inferred from that test
preparation error. Final preparation evidence is recorded under
`fixtures/agent-stage2-bpm-multiext-preparation-2026-10-28/`.
