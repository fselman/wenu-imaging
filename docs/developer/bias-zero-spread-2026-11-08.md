# Explicit zero-spread bias failure — 8 November 2026

Owner chose stop-and-display, then authorized implementation. Issue #289; [reviewed contract](design/bias-zero-spread-v1.md). The previous suggestion to admit equal means is rejected.

Both native service and legacy bias caller stop explicitly when the computed double-precision frame-mean spread is exactly zero. They report detector identity, every input filename and its corrected mean with 17 significant digits in ADU. The native service returns a specific computation error and no master result. Existing recipe failure propagation stops subsequent detector work and final FITS/ASDF publication; earlier private work/logs remain evidence. No epsilon, inclusive boundaries or changes to nonzero arithmetic. Legacy float QC rounding does not decide the failure.

Internal changes: optional borrowed diagnostic context via an additional kernel entry point; existing wrappers retained. Exact-zero flag is initialized on every call; zero decisions and no accepted frames on that failure. Guard optional NULL releases during early cleanup to avoid allocator chatter. Other numerical/service/QC policies remain unchanged.

## Verification actually executed

Agent C17/GCC build with nonrecovering UBSan passed OmegaCAM and WFI service contracts: 16 existing legacy equivalence profiles with exact pixels/QC and ownership/allocation controls. New controls cover equal means from different pixel arrays, both median modes, BPM/no BPM, strict nonzero endpoints, insufficient inputs/survivors, invalid/empty populations, and positive double spread that rounds to zero in float QC. Native service refuses without output transfer or borrowed-input changes. Caller-output verification checks detector IDs, input filenames and computed means. No sanitizer findings or new compiler warnings; inherited dependency/reference warnings remain.

First endpoint fixture incorrectly expected a one-plane median; corrected to respect the existing three-plane stack minimum. Second native fixture disabled both scans, which existing validation refuses; corrected to use valid scan geometry. A later diagnostic assertion expected raw 100 ADU rather than corrected 0 ADU; corrected only that assertion. All failed attempts are retained alongside the final passing receipt in [evidence](evidence/bias-zero-spread-2026-11-08/results.json).

Updated the main bias mathematical guide and median supplement in LaTeX/PDF; changed pages visually checked. TeX formats/font maps were generated only in scratch because the agent TeX installation lacked generated runtime files; no user environment changed.

## Remaining actual Mac gate

Fresh host/checkout/build evidence is required before synchronization or mutation. Reuse the selected mutable C17 source/build, compiler/SDK/cache and ASDF dependencies. Preserve the qualified 74327c4 recipe binary before relinking. Apply only candidate source differences, stamp actual producer revision and rebuild affected targets using /opt/local/bin/cmake --build; no explicit reconfiguration/export, installation or observations.

Run the affected service checks and `mefpp2/tests/bias_zero_spread_recipe_contract.py` with the selected normal Astropy interpreter and candidate recipe. This prepared checker makes independent tiny FITS files and invokes the actual native recipe once, expecting nonzero exit, exact detector/input means in terminal and retained log, no detector completion or final FITS/ASDF, and unchanged synthetic raws. It does not invoke frozen-reference reductions or ASDF consumers. This recipe checker has only been syntax checked in the agent: native ASDF recipe target is not available here. Do not claim whole-recipe or Mac acceptance yet.

No merge, branch deletion, observational processing, installed-software change, viewer work or detector-residual investigation. Continue the agreed linearity script only after this bounded correction is qualified.
