# M4 readiness review — 31 October 2026

Baseline: accepted merged main `3a61df627edfdbb1ef43cc3c956dff74bd28c066`.
This is source/contract review in preparation for the owner's requested M4 review.
It starts no implementation, test, installation or data processing. The
[M3 cumulative review](m3-cumulative-review-2026-10-31.md) retains M3 open for its
original inspector-stage integration requirement; resolve that before advancing.

## Original M4 scope, unchanged

Source of authority: [implementation plan, M4](../architecture/proposed/implementation-plan.md#m4--detector-identity-and-image-layout-layer).

| Original requirement | Existing foundation | Remaining M4 work |
|---|---|---|
| Physical detector identity independent of ordinal HDU; per-file index/name/version, amplifier/geometry, type/scaling, units and original order | `mef_image_ref` in `mef_runtime.h` already carries asset record ID, detector ID, resolved path, HDU index and optional EXTNAME/EXTVER | Validate/resolve these references against actual FITS layouts; carry the remaining required metadata and its authority without inventing hardware IDs |
| Each calibration has its own detector map | Resolved requests have explicit calibration roles and per-detector BPM selected/omitted state | Bind science/calibration images independently by detector identity rather than sharing an ordinal selector |
| Primary HDU 0, one image extension and MEF | Metadata descriptors permit nonnegative HDU indices; file/list adapter accepts a caller-supplied catalogue | Actual loading/service adapters must support each layout; a valid descriptor alone is not numerical layout acceptance |
| Health, user selection and processing outcome remain separate | Requests/results are independently owned; inspector reports observed layout without hardware validation | Explicit selection/status semantics and deterministic output order; no detector renumbering when one is excluded |
| Normalization reference independent of selected output detectors | Legacy shared-normalization reference and accepted equivalence fixtures exist | Preserve/reference that same normalization context when selecting subsets; fail if unavailable rather than silently choose another detector |

## As-is source boundaries

- `mef_input_request.c::valid_catalogue` rejects duplicate detector/HDU mappings
  within a supplied file catalogue, but this adapter checks readability, not FITS
  headers, geometry, units or hardware identity. Its header explicitly assigns
  layout discovery to M4.
- `mef_runtime.h` copies caller-supplied selectors. A caller assertion of
  detector identity is not verification that the corresponding HDU contains it.
- The legacy engine loads bias/BPM/dome/sky/master-flat through the selected
  `bb->xtnum`. `mef_paths.c::calibration_geometry` checks configured cropped
  dimensions, not physical detector matching. A same-sized shuffled calibration
  can therefore pass that structural check without proving correct mapping.
  This is a source risk addressed by planned M4, not a reproduced new target defect.
- `mef_cal_bias` already supports a bounded one-detector raw-plane service with
  explicit configuration mapping. It rejects primary-HDU requests and does not
  establish the M4 primary-image/MEF equivalence gate. Extend/reuse this boundary
  where appropriate instead of creating another scientific implementation.
- The project inspector records EXTNAME, HDU index/type/dimensions and selected
  header cards as reported-unverified data. Keep that distinction when a real
  layout validator is introduced.

## Required contract decisions before M4 code

These implement original M4 requirements; they are not additional milestones.

1. Identify authoritative detector metadata/mappings for OCAM/WFI and a generic
   supplied-map primary-image case. Preserve raw/configured/characterized sources
   and explicit conflicts. EXTNAME, an ordinal and an ESO OB/template ID must not
   be silently promoted into physical detector identity.
2. Define the selected HDU index/name/version consistency rule, duplicate or
   missing identity rejection, and how unsupported ambiguous files fail before
   arithmetic. Keep any qualified legacy mapping explicit and inspectable.
3. Specify selected output order separately from per-file HDU order; represent
   health, explicit exclusion and failed processing without changing identities.
4. Specify required normalization-reference inputs when the reference detector
   is not selected for output. Preserve the existing algorithm/reference; a new
   normalization policy requires its own explicit scientific decision.
5. Reuse the established C90 request/config/result/error pattern, appropriate
   `.h`/`.c` changes together and opt-in compatibility boundaries. No accidental
   public ABI commitment or new parser/library dependency is implied.

## Bounded original verification gate

Prepare tiny fixtures only after the identity contract is explicit:

| Control | Required observation |
|---|---|
| Same detector identities, differently ordered calibration HDUs | Correct per-file identity binding; same expected pixels, never ordinal pairing |
| Duplicate, missing, unknown or inconsistent IDs/selectors | Controlled failure before arithmetic; explicit diagnostic and owner cleanup |
| Selected detector subset and different physical file order | Stable IDs and declared deterministic output order; excluded detector not renumbered |
| Same detector as primary image, single image extension and MEF member | Reach the same detector processing entry point with equivalent numerical results and metadata meaning |
| Extracted detector versus mosaic counterpart | Equivalent result using the same required calibration and shared-normalization context |
| Normalization reference absent from output selection or unavailable | Retain supplied qualified reference context, or reject explicitly; never substitute silently |

Expected testing exercises the new FITS/layout resolver and the existing detector
service/compatibility adapter, not association selection, full observational
reduction or a general memory matrix. Before any execution announce exact routines,
fixtures, outputs and pass criteria; retain the matching script comments. Select
targeted C90/C17/ownership controls appropriate to changes and qualify changed
interfaces on actual selected Intel Mac and representative Chapman. No new
toolchain installation or repetition of accepted Stage 2/2.1 is required by this
review.

## Preserved scope

mefpp receives explicitly selected observations/calibrations and validates basic
structural compatibility. ESO OB/template grouping, calibration selection and
other observatories' partition schemes belong to Pycavi (M8), not this detector
resolver. Preserve separate exposure/OB/template times and IDs.

Optional input BPM stays explicit selected/omitted; selected invalid masks do not
become omission. Required variance initialization/propagation remains M6a. New QC
estimators, linearity/dark/fringe science, generic CMOS characterization, runtime
parallelism, ASDF persistence, binding and installed activation remain at their
original milestones. M4 primary/one-extension support is not full single-detector
scientific or CMOS qualification.

No M4 runtime acceptance or implementation authorization is inferred from this
readiness document. Following completion and acceptance of M3, use this original
scope to prepare one concrete M4 interface/fixture review before code changes.
