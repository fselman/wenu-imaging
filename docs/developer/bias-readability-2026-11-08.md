# Bias recipe: source review edition

Issue #292. The owner accepted the mandatory readability policy (PR #291, now merged at 165d02d), then instructed applying it to the bias routines so that he can read and review the result before accepting it. Linearity remains paused.

This candidate expands compressed code, uses descriptive domain names and ordinary option control flow, adds logical spacing/braces, and places twelve sparse source comment landmarks at scientific stages. Existing public function signatures, formulas, operation order, mask populations, median modes, zero-spread/error wording, ownership/cleanup and file/publication contracts are retained. The shared `mefp_lib.c` edit is restricted to `mef_overscan_correction_traced`; the rest of that legacy file and dependency algorithms are unchanged. Existing operation boundaries are retained in this first pass; function extraction can be driven by source-review feedback rather than an arbitrary length limit.

The mathematical guide now describes already accepted average/lower bias stacking consistently and provides a source-file/routine/landmark map in [LaTeX](bias-recipe-mathematical-guide-v1.tex) and [PDF](bias-recipe-mathematical-guide-v1.pdf), pages 2–3. Updating historical wording is not a new scientific decision.

## Suggested reading order

| Read | Source | Entry point / landmarks |
|---|---|---|
| 1. Follow the whole recipe | [Coordinator](../../mefpp2/ins/mef/recipes/mefpp_bias_recipe.c) | `main`: `[BIAS-RECIPE-ADMISSION]`, `[BIAS-DETECTOR-LOOP]`, `[BIAS-PRODUCT-PUBLICATION]` |
| 2. Follow one detector | Same coordinator, then [file adapter](../../mefpp2/ins/mef/common/mef_bias_files.c) | `process_bias_detector`; `load_bias_frames` at `[BIAS-INPUT-LOADING]` |
| 3. Understand correction and QC | [In-memory service](../../mefpp2/ins/mef/common/mef_cal_bias.c) | `mef_cal_bias_measurements`: raw-pair RON, scan correction, master QC landmarks |
| 4. Read the compact scientific kernel | [Frame selection and stack](../../mefpp2/ins/mef/common/mef_bias_kernel.c) | `mef_bias_stack_masked_diagnostic`: `[BIAS-FRAME-SELECTION]`, `[BIAS-TEMPORAL-STACK]` |
| 5. Inspect the row estimator if needed | [Shared scan correction](../../mefpp2/ins/mef/common/mefp_lib.c) | `mef_overscan_correction_traced`, `[SCAN-ROW-CORRECTION]` |
| 6. Inspect output ownership and encoding | [File adapter](../../mefpp2/ins/mef/common/mef_bias_files.c), [QC archive](../../mefpp2/ins/mef/common/mef_bias_product_qc.c), [FITS mapping](../../mefpp2/ins/mef/common/mef_bias_qc_fits.c) | `publish_bias_header`, `[BIAS-DETECTOR-WRITE]`; `mef_bias_product_qc_add`; `mef_bias_qc_fits_header` |
| 7. Inspect configuration details last | [Recipe envelope](../../mefpp2/ins/mef/common/mef_bias_recipe_config.c) | `mef_bias_recipe_expand` |

## Checks actually run in the agent workspace

All eight changed translation units pass C17 syntax and expanded-token comparison with the qualified b833aca7 source, allowing documented identifier changes, explicit braces, macro expansion and source-location metadata. Adjacent string literals are compared by their combined value. This is an expression/order check, not a general proof of semantic equivalence. Seven dedicated bias units also pass `-Wall -Wextra -Werror -pedantic-errors`.

The retained C17/UBSan agent build was reused; its pre-existing bias-adapter option was intentionally enabled to exercise the affected file path. No new Mac build/configuration was created. Sixteen existing OmegaCAM/WFI service/legacy profiles pass exact pixels/QC, zero/tiny-positive spread, strict endpoints and ownership/allocation controls. File-adapter contracts compare real candidate calls against a frozen b833aca7 legacy executable compiled with unchanged dependency archives: PAF/TOML/primary-image pixels, headers/QC, no-clobber and missing-HDU checks pass for both instruments. Four QC/BPM/MAD/RON copying profiles, average-mode/FITS provenance, clipped mapping, one/two-detector selected headers and nine recipe-envelope groups pass. Actual production routines and validators are used; no ASDF writer is substituted. Native full-recipe/ASDF runtime checks remain a Mac gate.

All twelve source landmarks are unique and referenced in the LaTeX guide. The guide compiles to sixteen pages; changed pages and the two-page reading map were rendered and visually reviewed. Retained results, source hashes, renames, development notes and logs are under [evidence](evidence/bias-readability-2026-11-08/results.json). Temporary agent verifier tools are isolated from the user/project environments.

## Review and target gate still pending

This is prepared for the owner's reading, not accepted human comprehension. First review the source and reading map, and revise anything whose flow or scientific meaning remains difficult to follow. Then use fresh actual-host evidence and the selected mutable Mac source/build/cache/tools for the bounded affected-recipe qualification. Preserve the qualified b833aca7 executable (SHA256 4728e6d00c6c1bb5fc55710a53281910a60ad728fa696363cf8dfb22c3593b14), all original products and prior evidence. A checkout synchronization for reading does not update that mutable source or binary.

No observations, installations, coefficient/model work, frozen-linearity dependency substitution or merge/cleanup of this implementation is authorized by this source-review preparation. Linearity remains paused; CCD68/90 residual investigations and viewer Update remain deferred.
