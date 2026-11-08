# Explicit zero-spread bias failure — 8 November 2026

Owner chose stop-and-display, then authorized implementation. Issue #289; [reviewed contract](design/bias-zero-spread-v1.md). The previous suggestion to admit equal means is rejected.

Both native service and legacy bias caller stop explicitly when the computed double-precision frame-mean spread is exactly zero. They report detector identity, every input filename and its corrected mean with 17 significant digits in ADU. The native service returns a specific computation error and no master result. Existing recipe failure propagation stops subsequent detector work and final FITS/ASDF publication; earlier private work/logs remain evidence. No epsilon, inclusive boundaries or changes to nonzero arithmetic. Legacy float QC rounding does not decide the failure.

Internal changes: optional borrowed diagnostic context via an additional kernel entry point; existing wrappers retained. Exact-zero flag is initialized on every call; zero decisions and no accepted frames on that failure. Guard optional NULL releases during early cleanup to avoid allocator chatter. Other numerical/service/QC policies remain unchanged.

## Verification actually executed

Agent C17/GCC build with nonrecovering UBSan passed OmegaCAM and WFI service contracts: 16 existing legacy equivalence profiles with exact pixels/QC and ownership/allocation controls. New controls cover equal means from different pixel arrays, both median modes, BPM/no BPM, strict nonzero endpoints, insufficient inputs/survivors, invalid/empty populations, and positive double spread that rounds to zero in float QC. Native service refuses without output transfer or borrowed-input changes. Caller-output verification checks detector IDs, input filenames and computed means. No sanitizer findings or new compiler warnings; inherited dependency/reference warnings remain.

First endpoint fixture incorrectly expected a one-plane median; corrected to respect the existing three-plane stack minimum. Second native fixture disabled both scans, which existing validation refuses; corrected to use valid scan geometry. A later diagnostic assertion expected raw 100 ADU rather than corrected 0 ADU; corrected only that assertion. All failed attempts are retained alongside the final passing receipt in [evidence](evidence/bias-zero-spread-2026-11-08/results.json).

Updated the main bias mathematical guide and median supplement in LaTeX/PDF; changed pages visually checked. TeX formats/font maps were generated only in scratch because the agent TeX installation lacked generated runtime files; no user environment changed.

## Actual Mac qualification passed

Owner supplied the successful receipt and a second read-only hash/cache verification on MC02VV0HPHTDG. Native producer **b833aca7df520171d9dcf4f0094a43bb5aad33a6**, recipe SHA256 **4728e6d00c6c1bb5fc55710a53281910a60ad728fa696363cf8dfb22c3593b14**. All twelve supplied source hashes match the reviewed files. See [Mac acceptance](evidence/bias-zero-spread-2026-11-08/mac-acceptance.json).

The selected existing C17/AppleClang/SDK14.2/Unix Makefiles build was reused. Only `MEFPP_SOURCE_REVISION:STRING` changed in the full CMake cache. Incremental recipe/service build and both OmegaCAM/WFI service contracts passed. One actual native recipe invocation on three distinct tiny synthetic FITS inputs returned the expected exit status **1**; terminal and retained log identify F1_CCD_A and all three corrected means of 2 ADU. No detector completion, final MEF assembly, FITS or ASDF occurred. Synthetic raws stayed unchanged. No observational read or installation.

The prior 74327c4 recipe is preserved in the attempt's `mefpp_bias_recipe.before`, SHA256 4105209f0f0954284f944adfc26387837ffdbec93a98d7556f7a77b063bde469. Attempt directory: `/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb/scalar-qc-qualification-c17/zero-spread-b833aca7df52-9gkd9jaj`. Original logs, source/cache backups and `qualification.json` remain there. The repository acceptance file records owner-supplied evidence; it does not pretend that full host logs were downloaded.

Three AppleClang warnings came from unchanged `mefpp2/tests/bias_legacy_reference.c`: unused `scancorr` (line 11), unused `bias` (line 12), and potentially uninitialized `normFactor` in the flat-normalization branch (line 306). Source inspection confirms the tested `what="bias"` path returns at line 198 before that branch; other accepted entry types are dome/sky, which assign the factor, and unknown types return before loading. No reference arithmetic, production code or warning flags were changed to silence them. These warnings do not invalidate the bounded bias qualification; this is not a qualification of historical flat processing.

The correction is qualified and ready for owner review/integration. This acceptance update changes documentation only: keep producer b833aca7, with no relink, repeated gate, installation or reduction. Merge/branch cleanup still require the owner's corresponding instruction. Then resume the agreed linearity script using saved products; CCD68/90 residuals and viewer Update remain deferred.
