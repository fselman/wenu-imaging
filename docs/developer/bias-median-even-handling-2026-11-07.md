# Detector-local bias median: even sample handling

Issue #287. Owner selected `median_even_handling`, default `average`, and approved the [scientific contract](design/bias-median-even-handling-v1.md). This deliberately changes even-count bias master pixels; explicit `lower` retains historical pixels. Odd counts are unchanged. No cross-detector normalization is introduced.

```toml
[bias]
median_even_handling = "average"
```

This belongs in the recipe TOML, with the existing short launcher invocation. Shared processing TOML may instead carry optional native `MEF.BIAS.MEDIAN.EVEN.HANDLING` (typed domain `processing.bias_median_even_handling`); explicit disagreements fail. PAF uses the same native key. Both omission paths default bias stacking to average. Manual legacy `mef_bb` constructors must initialize the new enum (zero means average); the PAF/TOML constructors do so explicitly.

Implementation adds `median_pixelvalue_opts`, `cube_avg_median_opts`, and `mef_bias_stack_masked_opts`. Native `mef_cal_bias`, legacy `mef_build_cal`, immutable configuration/clone/settings, result QC and serialization carry the choice. Unrelated generic Eclipse wrappers retain their old behavior. Average mode uses one Wirth selection plus the maximum of its lower partition, reusing the existing timeline buffer. It computes the midpoint in double before one working-type conversion.

Each detector records its actual mode in ASDF `characterization.detectors[].median_even_handling` and FITS `ESO MPP QC MED EVEN`. Old sidecars without this optional field remain schema valid. Master spatial statistics/high-offset diagnostics are recalculated from the new detector pixels. Input/scan QC, membership and all raw-pair RON estimators are unchanged. Raw-pair MAD quantization is a separate issue and is not changed here.

## Agent evidence

Native C17/UBSan numerical probe passed 3200 independent sorted-oracle cases, odd/even cube/input-preservation tests, finite extremes, generic-wrapper compatibility and actual default-average/explicit-lower bias kernels. Four historical service/QC profiles, new average service/FITS mode profile and reason-mask service profile passed. Shared native/domain config/clone tests passed 42 cases; recipe config tests passed nine groups including new valid/invalid settings. All 18 changed C translation units passed strict syntax checks. Evidence is in `evidence/bias-median-even-handling-2026-11-07`.

A synthetic 2048x4100 detector, ten-frame microbenchmark used the same 40-byte timeline in both modes: average 0.767 CPU s and lower 0.643 CPU s on the agent workspace. These are illustrative, not Mac timing claims; no per-pixel allocation or additional image scratch is added. Numerical tests use UBSan and do not substitute an ASDF implementation.

The parallel [LaTeX guide](mathematics/mefpp/bias-median-even-handling.tex) and [render-checked PDF](mathematics/mefpp/bias-median-even-handling.pdf) connect formula, implementation and validation limits.

## Pending selected-Mac gate

`mefpp2/tests/qualify_bias_median_mac.py` first supports a read-only preflight. It expects clean main af24c3699957d03a11f26c0bc47172b202ca0ede and the existing mutable source/build at the qualified f95cc9b producer. It verifies actual source/cache/tool/SDK identities, retains changed source/cache/recipe bytes, and updates only candidate files and the deliberate revision stamp before building affected existing targets. No new build/source export, compiler choice, dependency install or ordinary reconfiguration.

The actual-product contract first reproduces frozen historical lower reference pixels/QC through the legacy PAF path. Symmetrically bracketed active-plane triplets expose the central scan-corrected planes for an independent sorted temporal-median oracle. Default average, explicit average and lower native products are checked pixel-for-pixel. The separate ASDF interpreter checks schema, full mapped FITS QC, effective mode, independently recomputed spatial master mean/median/stdev/MAD, and exact unchanged input QC/raw-pair RON across modes. Unknown/conflicting modes must fail. These actual Mac native ASDF/product checks have not run in the agent workspace (Astropy/native ASDF runtime unavailable).

Preserve main, viewer branch/PR #283, selected build/cache/toolchain, old binaries, all real inputs/products and prior qualification evidence. No observational rerun, installation, merge or cleanup is authorized by preparing this patch. The issue remains open pending actual Mac evidence.

## Actual Mac fixture refusal and test-only correction

The selected Mac build, median-oracle probe, average service profile, historical service profiles and shared policy gate passed at native producer `74327c49832a9337fad49a0bec1b5fd7af81cde5`. The actual recipe contract also completed its historical-lower FITS/ASDF comparison before the next case failed: the identical-plane oracle listed the same raw path three times. The recipe correctly refused it with `Duplicate raw input path`. This is a test-fixture error; the input-identity guard must remain unchanged.

The correction creates three independent regular synthetic files with identical bytes and distinct resolved paths. An explicit duplicate-path refusal case is retained. Agent testing verifies identical bytes, distinct paths and distinct filesystem identities. `--reuse-fixture` reuses the failed attempt's tiny inputs/references without invoking the old reference adapter again. New orchestration/products/oracle copies are written in a fresh retry directory; retained files are hashed and preserved.

`mefpp2/tests/retry_bias_median_mac.py` updates only test files, verifies the existing native producer source and cache, and reruns the corrected actual-product contract. It records producer and test revisions separately and checks exact executable/cache and failed-attempt preservation. No native rebuild, revision-stamp change, reconfiguration, dependency change, real-data access or cleanup is needed. The complete default-average/lower product oracle remains pending this retry; the earlier partial run is not full acceptance.


## Zero-spread fixture correction

The first test-only retry passed distinct-input validation but stopped in bias stacking. Source review shows an inherited condition: strict frame-mean rejection (`mean > low && mean < high`) rejects all samples when the spread is exactly zero and both bounds equal the mean. This is separate from the new median convention; the original F1 fixture already avoids zero-width intervals. Preserve both failures and this finding. No frame-rejection policy change is included in the median patch.

The oracle now uses distinct synthetic files with exactly representable active-region offsets -1, 0, +1 ADU. Scan pixels are unchanged. The odd temporal median therefore remains the original central corrected plane, while frame means have nonzero spread. Agent NumPy checks establish exact central median, unit frame-mean spread and unchanged scan pixels. A native C17/UBSan kernel check independently reproduces the inherited zero-spread refusal and accepts the bracketed planes with exact central pixels. This changes only the oracle fixture; neither production rejection nor median code changes.

The retry helper freezes every earlier `median-fixture-retry-*` directory as well as the original qualification attempt. It continues to use native producer 74327c49832a9337fad49a0bec1b5fd7af81cde5, writing a new test-revision directory without rebuilding or reconfiguring. Complete actual Mac product/ASDF acceptance is still pending.
