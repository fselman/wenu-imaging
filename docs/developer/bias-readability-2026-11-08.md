# Bias recipe: source review edition

**Conditional acceptance; final source review pending.** The high-level command
is now 60 lines, using the common outer coordinator scaffold. Its support is
split into prepare, input admission, detector processing and product publication
modules. Shared run resources live in `mef_recipe_run.h/.c`; scientific services
and the inner operation lifecycle remain in use. See the
[coordinator design](design/common-recipe-coordinator-v1.md). PR #293 stays draft
and unmerged until the owner reviews the finished result and the relevant Mac
gate passes.

Documentation consolidation is queued **after this refactor**. Historical stage
documents will be reconciled then. Explanatory milestone labels have been removed
from source comments and adapter help. The compatibility command `mefpp_m5` and
its stored producer identity/version remain unchanged pending an explicit
migration; this is an interface/provenance exception, not a documentation link.
New source references must describe behavior or cite an immutable design revision
or GitHub issue. The mandatory instruction is recorded in both agent files.

Issue #292. The owner accepted the mandatory readability policy (PR #291, now merged at 165d02d), then instructed applying it to the bias routines so that he can read and review the result before accepting it. Linearity remains paused.

This candidate expands compressed code, uses descriptive domain names and ordinary option control flow, adds logical spacing/braces, and places twelve sparse source comment landmarks at scientific stages. Existing public function signatures, formulas, operation order, mask populations, median modes, zero-spread/error wording, ownership/cleanup and file/publication contracts are retained. The shared `mefp_lib.c` edit is restricted to `mef_overscan_correction_traced`; the rest of that legacy file and dependency algorithms are unchanged. The outer coordinator now exposes explicit phases; supporting functions retain the established calculation and publication order.

The mathematical guide now describes already accepted average/lower bias stacking consistently and provides a source-file/routine/landmark map in [LaTeX](bias-recipe-mathematical-guide-v1.tex) and [PDF](bias-recipe-mathematical-guide-v1.pdf), pages 2–3. Updating historical wording is not a new scientific decision.

## Suggested reading order

| Read | Source | Entry point / landmarks |
|---|---|---|
| 1. Follow the whole recipe | [Coordinator](../../mefpp2/ins/mef/recipes/mefpp_bias_recipe.c) | `main`: `[BIAS-RECIPE-ADMISSION]`, `[BIAS-DETECTOR-LOOP]`, `[BIAS-PRODUCT-PUBLICATION]` |
| 2. Follow one detector | [Detector processing](../../mefpp2/ins/mef/common/mef_bias_recipe_process.c), then [file adapter](../../mefpp2/ins/mef/common/mef_bias_files.c) | `process_bias_detector`; `load_bias_frames` at `[BIAS-INPUT-LOADING]` |
| 3. Understand correction and QC | [In-memory service](../../mefpp2/ins/mef/common/mef_cal_bias.c) | `mef_cal_bias_measurements`: raw-pair RON, scan correction, master QC landmarks |
| 4. Read the compact scientific kernel | [Frame selection and stack](../../mefpp2/ins/mef/common/mef_bias_kernel.c) | `mef_bias_stack_masked_diagnostic`: `[BIAS-FRAME-SELECTION]`, `[BIAS-TEMPORAL-STACK]` |
| 5. Inspect the row estimator if needed | [Shared scan correction](../../mefpp2/ins/mef/common/mefp_lib.c) | `mef_overscan_correction_traced`, `[SCAN-ROW-CORRECTION]` |
| 6. Inspect output ownership and encoding | [File adapter](../../mefpp2/ins/mef/common/mef_bias_files.c), [QC archive](../../mefpp2/ins/mef/common/mef_bias_product_qc.c), [FITS mapping](../../mefpp2/ins/mef/common/mef_bias_qc_fits.c) | `publish_bias_header`, `[BIAS-DETECTOR-WRITE]`; `mef_bias_product_qc_add`; `mef_bias_qc_fits_header` |
| 7. Inspect configuration details last | [Recipe envelope](../../mefpp2/ins/mef/common/mef_bias_recipe_config.c) | `mef_bias_recipe_expand` |

## First-pass checks (retained historical evidence)

All eight changed translation units pass C17 syntax and expanded-token comparison with the qualified b833aca7 source, allowing documented identifier changes, explicit braces, macro expansion and source-location metadata. Adjacent string literals are compared by their combined value. This is an expression/order check, not a general proof of semantic equivalence. Seven dedicated bias units also pass `-Wall -Wextra -Werror -pedantic-errors`.

The retained C17/UBSan agent build was reused; its pre-existing bias-adapter option was intentionally enabled to exercise the affected file path. No new Mac build/configuration was created. Sixteen existing OmegaCAM/WFI service/legacy profiles pass exact pixels/QC, zero/tiny-positive spread, strict endpoints and ownership/allocation controls. File-adapter contracts compare real candidate calls against a frozen b833aca7 legacy executable compiled with unchanged dependency archives: PAF/TOML/primary-image pixels, headers/QC, no-clobber and missing-HDU checks pass for both instruments. Four QC/BPM/MAD/RON copying profiles, average-mode/FITS provenance, clipped mapping, one/two-detector selected headers and nine recipe-envelope groups pass. Actual production routines and validators are used; no ASDF writer is substituted. Native full-recipe/ASDF runtime checks remain a Mac gate.

All twelve source landmarks are unique and referenced in the LaTeX guide. The guide compiles to sixteen pages; changed pages and the two-page reading map were rendered and visually reviewed. Retained results, source hashes, renames, development notes and logs are under [evidence](evidence/bias-readability-2026-11-08/results.json). Temporary agent verifier tools are isolated from the user/project environments.

## Review and target gate still pending

This is prepared for the owner's reading, not accepted human comprehension. First review the source and reading map, and revise anything whose flow or scientific meaning remains difficult to follow. Then use fresh actual-host evidence and the selected mutable Mac source/build/cache/tools for the bounded affected-recipe qualification. Preserve the qualified b833aca7 executable (SHA256 4728e6d00c6c1bb5fc55710a53281910a60ad728fa696363cf8dfb22c3593b14), all original products and prior evidence. A checkout synchronization for reading does not update that mutable source or binary.

No observations, installations, coefficient/model work, frozen-linearity dependency substitution or merge/cleanup of this implementation is authorized by this source-review preparation. Linearity remains paused; CCD68/90 residual investigations and viewer Update remain deferred.

## Template/spacing follow-up

The owner explicitly required using the common template for the next structural
revision and blank lines around explanatory comments. Those presentation changes
preserve executable tokens in ten source/header files; the existing operation
runner adds braces only and passes its six ordering/early-stop/cleanup scenarios
in the retained C17/UBSan agent build. See
[evidence](evidence/bias-readability-2026-11-08/presentation-followup.json).
The earlier numerical/file/QC evidence remains identified with the first source
review; no whole bias matrix was replayed for whitespace. This earlier follow-up preceded the structural extraction described below.

## Structural extraction checks

The new coordinator, four support modules and recipe-envelope module pass strict
C17 syntax checks. The shared run library and probe build and execute with UBSan:
exclusive log/no-clobber, failure retention and successful resource completion
pass using an empty synthetic input catalogue. The six inner operation lifecycle
cases pass. Sixteen bias service/legacy profiles and actual PAF/TOML/primary-FITS
contracts pass for OmegaCAM and WFI against the frozen reference. The moved
per-detector algorithm and binding function retain their token sequences (apart
from the integer-parser helper name). See
[structural evidence](evidence/bias-readability-2026-11-08/structural-results.json).
These agent checks do not execute the newly extracted full native recipe or its
ASDF writer; that runtime gate remains explicitly pending on the selected Mac.

The earlier token-comparison claim applies to the first-pass files, not to the
new multi-file coordinator. Source hashes and the updated landmark map identify
this structural candidate separately. No observations or installation occurred.

## Selected Mac testing authorized — 8 November 2026

The owner reviewed the 60-line coordinator, said “Much better”, and instructed
proceeding to testing. This authorizes the bounded synthetic gate; final acceptance
and merge remain pending. Actual-host read-only preflight confirms clean checkout
36381892f4f768c3a2c7450114f96021fd5c76d7, exact b833aca7 production sources,
recipe SHA256 4728e6d00c6c1bb5fc55710a53281910a60ad728fa696363cf8dfb22c3593b14,
full cache SHA256 b09476a9b4ac63e043a292492e289be3aecd295952071b27ea2995c82af0ae4a,
and frozen adapter SHA256
58aeaeb988c56766492cc19a87db115fc1f1b643c0541a7582107e274b600038. The selected
private ASDF interpreter reports 6.0.0. These observations are preflight evidence,
not runtime acceptance of the refactor.

`mefpp2/tests/qualify_bias_readability_mac.py` guards this exact state, preserves
the binary/cache/affected source files, overlays the reviewed producer revision,
changes only its producer cache stamp and incrementally builds the recipe and
affected probes. It runs shared run ownership/no-clobber/failure checks, inner
lifecycle checks, the two-instrument service/reference contract, eight native
coordinator groups, envelope/header/primary-HDU coverage, temporal-median oracle,
BPM/clipped-RON contracts and explicit zero-spread refusal. Native FITS/ASDF are
created by the actual C recipe; the separate ASDF interpreter verifies the
stored products and schema. Fresh synthetic directories only; no observations,
installation, dependency changes, new build tree or unrelated recipe qualification.

The runner prints progress every 30 seconds while a command is active, stops
before dependent groups on failure, retains every log/output/backup and writes
`qualification.json` in a fresh `readability-36381892f4f7-*` directory under the
retained qualification parent. No automatic restoration, retry, cleanup or merge.
The runner has passed Python compilation and CLI-help checks in the agent;
its actual Mac execution remains pending. The previously recorded agent results
retain their original scope. Documentation consolidation follows this refactor.

## Mac gate stopped at fixture reuse; scoped continuation — issue #294

Owner supplied actual execution at test head 7bfe6edd99a1bf15d496ee9257baf29ebf84e2fa.
The reviewed 3638189 producer built successfully in the retained tree. Shared run
resources, inner operation lifecycle, both-instrument service/reference and all
eight native recipe groups passed. Envelope verification stopped at the full
configuration-snapshot equality assertion. Retained attempt:
`/Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb/scalar-qc-qualification-c17/readability-36381892f4f7-dkg784s0`.
Its receipt is `qualification.json`. Nothing after envelope ran. Preserve all
partial products, logs, passed groups, executable/cache and source backups.

Source analysis found a harness omission: normal fixture setup explicitly adds
`MEF.BIAS.MEDIAN.EVEN.HANDLING=lower` to the expected snapshot/emitted TOML because
the older frozen adapter dump predates that provenance field. The envelope reuse
branch reloads that old dump but failed to restore the policy. The corrected
branch verifies the declared TOML policy and restores that exact typed field.
Full snapshot equality, pixels, QC, FITS/header, schema and provenance assertions
remain intact. No production source is changed. An isolated execution of the
actual metadata-restoration branch reproduces the missing expectation and passes
after correction; it is not native/ASDF runtime qualification. See the retained
[check](evidence/bias-readability-2026-11-08/reused-fixture-regression.json).

`inspect_bias_reuse_snapshot.py` independently reads the failed ASDF with the
selected ASDF interpreter, validates its schema and requires exactly the one
missing expected policy. `continue_bias_readability_mac.py` performs that check
before changing test support; any other difference stops the continuation.
It verifies the saved passed-group receipts, current executable/cache and full
production source; overlays only the corrected envelope test, and uses a fresh
retry directory. It reruns envelope and continues the previously unrun median,
clipped-RON and zero-spread groups. It does not rebuild, reconfigure or repeat
the passed groups. Previous-attempt files are hashed before/after; the executable,
cache, frozen reference, checkout and source preservation are checked in the
receipt. Progress is printed every 30 seconds while a command runs. All retries
and failed attempts remain separate.

Python compilation/CLI and metadata-restoration checks pass in the agent. The
actual saved one-field cause and remaining Mac native groups are pending target
execution. Issue #294 stays open; final acceptance/merge and documentation
consolidation remain pending.

## Continuation preflight correction — issue #295

The owner invocation at bf432bf stopped before creating a retry directory or
changing source/build resources. An accidental preflight reference to `record`
preceded its initialization. The correction removes only that premature overlay
check; initial preflight compares the prior receipt, and finalization still checks
the new test overlay. Simulated host/receipt execution reproduces the original
exception and reaches the first-write boundary after correction. This validates
runner control flow only, not Mac/native results. The retained failed attempt,
producer binary/cache, already passed groups and all pending native groups remain
unchanged. Continue the same bounded test-only gate; no rebuild or reconfiguration.
