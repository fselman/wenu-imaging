# M4 native layout paired results — 31 October 2026

Source `2d662b148db56b0292ca6ec3ee9bceb1bc463595` in PR #186 passes both
focused contracts in optimized C90 and C17 on the selected Intel Mac and
representative Chapman4. Normal mefpp links in both modes but is not run.
Installed module/selected engine/configuration, clean main c4a5ba4 and exported
source are preserved on both. No observation was opened or installation made.

| Contract | Mac C90 | Mac C17 | Chapman C90 | Chapman C17 |
|---|---:|---:|---:|---:|
| native_layout | 1.82 s | 1.53 s | 0.36 s | 0.35 s |
| native_bias_service | 2.43 s | 2.70 s | 0.65 s | 0.75 s |
| Total | 2/2, 4.26 s | 2/2, 4.24 s | 2/2, 1.01 s | 2/2, 1.10 s |

Times identify attempts; these are not matched performance measurements.
Source/configuration fixtures and probe receipts are retained inside each run.
These are owner-returned console receipts, not independently transferred full
host build archives.

- Corrected Mac: `/Users/fselman/Software/build/wenu-imaging/mac-m4-layout-corrected-Ban7s6aY`.
- Chapman4: `/home1/fselman/Software/build/wenu-imaging/chapman-m4-layout-rbEFQMbx`.
- Failed Mac, retained: `/Users/fselman/Software/build/wenu-imaging/mac-m4-layout-DRyH42lM`.

## Corrections qualified

#185: nonregular-file/FIFO refusal before opening is included in native_layout
on both actual targets. This is not a claim of general concurrent-path safety.

#193: the failed Mac link.txt shows ar creating libqfits.a, then an incorrect
`libtool libqfits.a` command where ranlib was intended. The runner had resolved
the selected executable entry point. Correction preserves invocation spelling,
records the canonical target/hash separately, and uses the existing
[selected-tools.md](selected-tools.md) record directly. The agent executable
regression fails before and passes after; actual corrected targets now pass.
Correction/evidence comments precede closure of both issues.

No dependency warning suppression or native numerical change was used to obtain
these passes. Original failed evidence is retained; no synthetic replay is
needed just to record this receipt.

## Remaining original M4 work

The [original milestone](../architecture/proposed/implementation-plan.md#m4--detector-identity-and-image-layout-layer)
requires independent per-file identity/layout maps, supported storage forms,
selection/order and separately supplied reference context. The paired controls
exercise those contracts and exact primary/extension/mosaic bias results. Full
calibration/science command adapters and extraction belong to M5/M6; do not
silently enlarge M4 into a full new reduction chain. The first map does not
reassemble multi-HDU amplifiers or qualify Bath no-scan science calibration.

The remaining M4 evidence must be planned after the reader direction is accepted:
actual instrument mappings, applicable shared-reference equivalence and matched
optimized performance. Existing Python preflight does not qualify a different
native reader. M4 #182 and PR #186 remain open. No full new reduction chain is
added to this milestone.

## Reader architecture review hold

The owner challenged the new reader implementation and instructed a reuse review.
See [the source/design review](m4-header-reader-reuse-review-2026-10-31.md).
Existing qfits already covers primary/extension headers, card order/duplicates and
HDU discovery. Its concrete count/offset gaps are recorded as #194/#195, with no
implementation or execution in this review. Prefer a thin M4 metadata/map adapter
and narrowly reviewed dependency changes over a second framing parser.

The proposed native catalogue client, its small agent fixture checks and its
twelve-observation handoff remain unpublished and held privately; no original
observation was opened. They are excluded from the review delivery. The paired
results above remain valid for their exact implementation, but do not approve
that architecture. No new functional test or benchmark is needed for this
review-only update. PR #186/M4 remain open for the design decision.
