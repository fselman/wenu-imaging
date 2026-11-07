# Bias MEF and native ASDF publication — agreed direction, 6 November 2026

## Executive summary

The bias recipe must run independently of Pycavi, from the orchestration
working directory, reading untouched raw data and writing to the selected
products directory. The final product remains a MEF. Detector work is temporary
and serial initially; the architecture retains the coordination and assembly
boundary needed for later parallel processing and shared flat normalization.
One native-written ASDF accompanies each final FITS product and contains its
relevant QC and embedded input records. Viewer changes follow a successful
full-mosaic real-data run and owner inspection.

This document records the owner's decisions in the current Work conversation.
It supersedes older Python-owned final-ASDF and per-input-sidecar directions
for this new product path. The reviewed operation template remains the basis.
It does not claim that all components described here are implemented.

## Agreed requirements

1. Keep the existing numerical bias operation and arithmetic. Use the native
   recipe template: validate, load, calculate, publish, unconditional cleanup.
2. Keep mefpp runnable without Pycavi. Configuration and explicit input/output
   references carry all required locations; the native engine does not discover
   the upstream project's raw/orchestration/products structure.
3. Invoke real acceptance processing in the orchestration directory. Raw data
   are untouchable. FITS, ASDF and logs go to the selected products directory,
   optionally its explicitly selected bias/ or cal/bias subdirectory.
4. Retain both --output-dir and complete --output. Supplying both must produce
   a clear error and stop before processing or creating products, including
   when they refer to the same parent. A complete --output supplies the final
   FITS basename and its parent becomes the internal output directory.
5. Automatic names are CMDP.<recipe-start-time>.001.fits (calibration) and
   SMDP.<recipe-start-time>.001.fits (science). Sample the start time once per
   recipe execution; increment the product sequence. Complete --output retains
   the caller's supplied name. The ASDF replaces only the final .fits suffix.
6. Preserve MEF final products. Temporarily separated detector results must be
   reassembled after any required detector coordination. Bias introduces no
   new gain harmonization. Flat coordination remains a distinct future stage.
7. Use external libasdf 0.3.0, qualified for the bounded ASDF 1.6.0 surface on
   Mac and Chapman. Reuse the direct mapping-construction workaround for #219
   and preserve #221's unqualified optional Float16 boundary. Bundling is still
   deferred; no new dependency installation is part of this increment.
8. One ASDF per final FITS product contains the relevant QC for all represented
   detectors, embedded input records, input membership/order/rejection, explicit
   raw FITS references, configuration and producer/provenance information.
   Per-input identity and measurements remain distinct within the document.
   FITS pixels stay in FITS. Do not copy a recursive calibration history.
9. Preserve the existing agreed ADU/count QC definitions, corrected/raw stages,
   unavailable states, selected raw-pair RON and independent detector/HDU/config
   mappings. File aggregation is not a new scientific QC policy.
10. Separate plotting creates plots once from saved QC. Pycavi's viewer displays
    those saved plots through recipe -> product -> QC. Saved plot geometry and
    axis metadata support cursor coordinates without regenerating curves.
11. Synthetic functional checks may use special directories. They do not replace
    real full-mosaic acceptance through the actual native recipe. Only after
    that run and inspection should the current viewer gain its Bias entry.
12. Consult before code design, agree design before implementation, and begin
    reviews with a plain-English executive summary and earlier decisions.

## Verified existing boundaries

- mef_cal_bias_measurements: one detector, in-memory numerical result plus QC.
- mef_bias_from_files: mapped file loading and calculation without publication.
- mef_bias_files_execute_measurements: same operation template, currently
  publishes a one-extension MEF through mef_bias_publish.
- mef_hdrpix_dump: checked header/pixel/padding writes; reusable assembly path.
- mefpp_m5: separate opt-in bias/BPM executable; it is not the normal installed
  mefpp. Existing final ASDF completion is still Python, pending replacement.
- Native MEF assembly must preserve logical detector ID, each input's actual
  source HDU, configuration index and output extension ordinal independently.
  Do not select detector metadata merely by ordinal or infer mosaic summaries.

## First implementation increment: product path helper

The new mef_product_paths.h/.c module implements only the agreed output naming
and destination rules. It does not read image files, create directories, change
cwd, write products or invoke Python. It is not yet connected to a recipe.

Implementation details made explicit for review:

- A single sampled instant is formatted in UTC as YYYY-MM-DDTHH:MM:SS.mmmZ.
  A deterministic formatter supports fractional-second/calendar checks without
  altering the machine clock. It does not call the defective packed-time helper
  tracked in #207. Existing historical names and code remain untouched.
- Product numbers start at one; formatting uses at least three digits, so 1000
  remains valid. The future recipe coordinator owns the shared start time and
  sequence; detector processing must not create separate recipe start times.
- Directory arguments resolve once against the invocation directory. The output
  parent must already exist and be writable, retaining the existing native rule.
  The helper neither creates a missing bias/ subdirectory nor chooses raw roots.
- The ASDF and log names inherit the complete final FITS stem. Dots in caller
  basenames and spaces in directory names are preserved.
- Existing FITS/ASDF/log files and dangling symlinks are refused. Checks are not
  cross-process reservations: final publication must still use exclusive writes.
- UTC milliseconds plus a sequence are not a cross-process uniqueness guarantee.
  A collision fails; the helper does not silently rename or overwrite a product.

The helper is deliberately not activated in the existing recipe while native
ASDF publication and final mosaic assembly remain unconnected. Consequently
this commit does not produce a complete bias product or change installed behavior.

## Required following increments

1. Native common product-QC assembly using the approved embedded-input structure
   and libasdf, preserving the shared logical measurement definitions. Review
   concrete schema/version and internal-reference validation before coding it.
2. Single-writer final MEF assembly from temporary detector results, reusing
   checked FITS writers and explicit identity/coverage/header contracts. No
   independent process may append to the final MEF.
3. Connect output selection, recipe start identity, detector processing, native
   QC publication, log destinations and truthful overall completion in the
   standalone recipe entry. Do not depend on Pycavi for completion.
4. Incremental target verification in the existing Mac toolchain/library prefix;
   no dependency installation or replay of unchanged old qualification matrices.
5. Owner-inspected full-mosaic real bias run through orchestration/raw/products.
   Exact actual roots and selected input/config/BPM/RON memberships must be read
   from current target evidence; do not guess or silently replace those choices.
6. Adapt the existing viewer to saved bias plots only after that acceptance.

## Verification of this increment

The standalone product_paths_contract.py compiles the real C helper and its
small native driver with strict C17 warnings. Controls exercise destination
mutual exclusion, complete-name inheritance, generated names, relative paths,
selected nested bias directories, protected outputs/symlinks, invalid arguments,
sequence width, and deterministic/current-clock formatting. Synthetic raw and
orchestration sentinels remain unchanged. It does not execute a bias recipe or
exercise FITS/ASDF serialization, C-library linking, real data or the viewer.

Agent Linux results and target limitations are recorded in the accompanying
status document. The numerical bias, stacking and existing FITS publisher are
unchanged. No installation, merge, cleanup or real-data processing occurs here.

## Existing references

- ../native-operation-recipe-template.md
- ../m3-native-paths.md
- ../libasdf16-private-qualification-2026-11-02.md
- ../m5-asdf-chapman-qualification-2026-11-02.md
- ../bias-bpm-asdf-handoff-2026-11-02.md (older persistence layout)
- ../direct-asdf-viewer-2026-11-06.md (working interim viewer)
