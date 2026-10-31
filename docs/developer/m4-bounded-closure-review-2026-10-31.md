# M4 bounded closure review — 31 October 2026

**Recommend owner acceptance of the detector/layout foundation and progression to
M5 calibration decomposition, with the limits below explicit.** This is a bounded
review of native source `5b2518312b962e4e7aeff72e08d370b5e1c6a81a`; it does not
merge PR #186, automatically close the milestone or activate an installed engine.
No further qualification series is proposed for this unchanged source.

## Original M4 requirements and evidence

The controlling [implementation plan](../architecture/proposed/implementation-plan.md#m4--detector-identity-and-image-layout-layer)
requires identity/layout descriptors, independent maps, three storage forms,
separate health/selection/outcome and independent reference context. Its gate is
bounded tiny controls, retaining the legacy mapping as rollback. New calibration
and science command/service integration belongs to M5/M6.

| Requirement | Implemented/qualified evidence | Boundary |
|---|---|---|
| Identity distinct from HDU ordinal | Owned catalogue/map retains logical/configured physical identity, optional header/amplifier evidence, independent selectors and configuration index | Configured claims do not verify hardware; absent identity/EXTVER remains absent. |
| Independent science/calibration maps | Shuffled A/B files resolve independently; known identity-matched plane values and science source order are asserted | Association is caller-owned, not inferred here. |
| Primary HDU0, one extension and MEF | Same Eclipse decoder and mef_cal_bias entry produce exact decoded unsigned endpoints and independently known bias pixels across all three storage forms | No no-scan/generic CMOS science readiness follows. |
| Health, selection and source order | Excluded detector retains ID/order/health; selected map remains deterministic | Result publication/processing outcomes are later-service responsibilities. |
| Independent shared reference context | Excluded reference remains available; missing/unknown required reference fails rather than selecting another | M4 validates reference availability/compatibility; flat/science normalization algorithms remain unchanged and their service integration belongs to M5/M6. |
| Existing FITS implementation reused | M4 consumes qfits-owned headers/offsets and ordered card views, with checked shared discovery | Separate M4 framing parser removed after owner review. |
| Controlled unsupported inputs and owners | Count/header budgets, duplicates, malformed/truncated/FIFO inputs, source changes, metadata-owner allocation failures, range rejection and repeated offset growth | Dependency-global fatal allocator/cache/concurrency policy is not generally requalified. |

The original acceptance of tiny extracted-detector/mosaic controls is retained:
same relevant instrument/configuration and required scan context, known plane and
bias results, and separately checked shared-reference availability. This does not
claim a new full flat/science service or normalization pipeline. Those services
are the next decomposition work, not hidden prerequisites added to this layer.

## Actual target and agent qualification

| Target | C90 discovery/layout/bias/native paths | C17 same four contracts |
|---|---|---|
| Intel Mac | 4/4, 33.64 s | 4/4, 33.83 s |
| Representative Chapman4 | 4/4, 21.78 s | 4/4, 21.82 s |

- Mac retained `/Users/fselman/Software/build/wenu-imaging/mac-m4-offset-storage-O0fe7K62`.
- Chapman retained `/home1/fselman/Software/build/wenu-imaging/chapman-m4-offset-storage-Lclm7Q3B`.

Both report installation/checkout/export preservation and exact test inventories.
No original observations were opened, installation made or engine selection
changed. Console receipts were returned by the owner; full host archives were
not transferred. Source-specific agent C90/C17 4/4 and scoped ASan/UBSan 3/3 pass,
including repeated growth to 300 extensions; legacy leak limitation is retained.
See [correction/source evidence](qfits-offset-storage-correction-2026-10-31.md).
Test durations are not throughput measurements.

The repeated full runtime checks for the small offset-storage fix were conservative.
Future small corrections should select changed-boundary controls and required
compilation, reusing unaffected numerical evidence instead of replaying every
runtime lane automatically. Nothing needs rerunning to record this review.

## Bounded performance review

The initial matched case compared accepted-main-equivalent normal-engine source
at 2d662b1 with the first qfits-reuse candidate 5e6bd83, using retained private O2
C90 executables. Exact products passed on both hosts. Mac timing medians were
near parity; Chapman medians were slower and CPU ratios varied. The absolute
Chapman records showed low mean host load and a common existing sleep(1) for
ORIGFILE uniqueness. That naming behavior is unchanged and remains in timings.

Inspection found avoidable temporary heap offsets introduced by the patch. #197
restores the ordinary stack buffers and grows only on actual higher counts.
The fresh **Chapman-only** follow-up uses qualified candidate 5b251831, unchanged
fixtures/measurement method, one warm-up per role and three alternating pairs per
instrument: sixteen native calls, no rebuild, exact six-product comparisons.

Retained corrected run:
`/home1/fselman/Software/build/wenu-imaging/chapman-m4-performance-corrected-2yqy7u5t/plan`.
Plan SHA256: `6d0ef4b23f5cd92d5a2a1749f67a6375f9ab8ba3a3da93e7eb251910de40e7dc`.
All calls/products/identity checks complete; installed files and checkout preserved.

| Instrument | Paired wall ratios (candidate/reference) | Median | CPU ratios |
|---|---|---:|---|
| OmegaCAM | 0.967964, 0.872940, 1.012129 | 0.967964 | 0.905523, 0.624419, 1.044184 |
| WFI | 0.943896, 0.953957, 0.984158 | 0.953957 | 0.832499, 0.842618, 0.947356 |

No consistent timing penalty appears after the correction in this bounded case.
This is **not** a proven general speedup, a statistical confidence claim, or proof
that all initial variation was caused by the offset allocations. Retained bytes
match; reported block counters do not increase. RSS still varies: all three
OmegaCAM differences are positive (about 1.8–4.0 MiB), and WFI spans about
-6.0 to +9.6 MiB. No reduced-memory-footprint or universal resource-equivalence
claim is made. The source-specific unnecessary allocations are removed; broader
allocator/page-residency behavior is not diagnosed by three process samples.

No automatic percent penalty is allowed. These few variable samples do not
prove the broad no-performance-penalty requirement; that obligation stays explicit.
This review recommends accepting the bounded detector/layout foundation without
expanding this series further. Numerical
throughput on full-sized observations, opt-in layout-adapter cost when integrated
and transient scratch peak remain unmeasured; carry those explicit performance
obligations to the executable M5/M6 boundaries and cumulative acceptance. Owner
acceptance of this recommendation is a scope decision, not a silently granted
performance waiver. Previous and corrected results remain retained.

## Limits and next decision

- Whole-file offsets remain limited to INT_MAX bytes, just under 2 GiB on these
  targets. Checked refusal is not large-file support. #195 remains open; this
  review does not permanently adopt that limit for future instruments/products.
- The bounded native profile is raw imaging without random groups/heaps; a map
  supports one 2-D plane per detector, not general amplifier reassembly.
- Bath's real primary-image header evidence and Python preflight/profile work are
  retained. No actual Bath calibration, physical gain/readout validation, generic
  CMOS/no-scan science processing, variance or scientific-quality acceptance is
  claimed. Real profile/service integration remains explicit future work.
- Automatic new-workflow activation, installed replacement, full calibration/
  science dispatch and output publication are not part of this opt-in boundary.

If the owner accepts this bounded closure, separately instructed merge/cleanup
can integrate PR #186, then M5 begins calibration decomposition with preserved
legacy results, shared-reference semantics, ownership/errors and performance.
Start with a concrete map of the existing calibration paths and extract one
coherent operation at a time. No parallelism, new numerical method, Python
replacement or broad FITS redesign is smuggled into that next step.
