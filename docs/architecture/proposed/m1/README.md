# M1 common subroutine template — C90 design contract

Owner requirement, 29 October 2026: provide a template subroutine that all extracted subroutines can use. Make this the first M1 design deliverable, before duplicating interfaces across numerical modules.

Use plain C structs, functions and opaque handles. This is a copyable calling/ownership pattern, not C++ inheritance, macros generating algorithms or a new dispatch framework. Each operation has its own implementation and may have operation-specific configuration/request/result payloads. Share status, error, lifecycle and metadata conventions; do not force bias, flat, linearity and image writing into an identical numerical signature or one giant state struct.

[Header](mef_operation_template.h.txt) and [routine body](mef_operation_template.c.txt) reuse the [accepted M0 native interface sketch](../m0-m0a/native-interface.h.txt). Public entry-point names below are owner-selected; argument layouts and ABI remain review sketches. These are syntax-checkable review files, not production code: the operation helpers have declarations only, with implementation deferred to the relevant stage. They cannot perform processing or be linked as a complete library.

## Owner-selected service names and qc stage

| Purpose | Entry point |
|---|---|
| Master bias creation | `mef_cal_bias` |
| Bad-pixel mask creation | `mef_cal_bpm` |
| Dark calibration creation | `mef_cal_dark` |
| Fringe-frame creation | `mef_cal_fringes` |
| Linearity calibration/model creation | `mef_cal_linearity` |
| Dome flat creation | `mef_cal_domeff` |
| Sky flat creation | `mef_cal_skyff` |
| Master flat creation | `mef_cal_mff` |
| Apply requested calibrations / science preprocessing | `mef_sci_pp` |

These spellings are fixed by the owner, including plural `fringes` and no `_run` suffix. [Service declaration sketch](mef_services.h.txt) records all nine names. The representative template now uses `mef_cal_bias`; private helper names such as `mef_cal_bias_kernel` and `mef_cal_bias_qc` are implementation sketches rather than additional public operations. Dark/linearity/fringe names do not advance their numerical implementation ahead of M6b–M6d. Existing calibration applications may be factored into private kernels reused by `mef_sci_pp`; fringe subtraction remains the later Python operation already planned.

Every applicable builder and science stage has an explicit **qc** phase. The review template calls the operation's qc helper after calculation/structural result checks and before transferring the completed result. It can use input/intermediate statistics retained in the context; overscan information must remain available even if the image is subsequently trimmed. This is a declared stage and QC result contract, not a chosen estimator or quality cut.

For bias, candidate measures supplied by the owner are mean level, RON and overscan mean level. Exact definitions, regions, masks, per-frame/per-detector/per-amplifier aggregation, input requirements, units, estimators and thresholds are **TBD**. QC records must distinguish measured/configured/assumed inputs and unavailable/not-requested values. Carry metric name, value/availability, units, method/version and source/selection provenance in the result, with concrete WAD/C field definitions reviewed later.

QC measurement/reporting is distinct from operational result validation and any scientific acceptance rule. No implicit rejection thresholds, automatic parameter/header replacement or calibration reselection is introduced. The declaration-only scaffold propagates a helper's non-OK execution status but does not define scientific quality rejection; required/optional QC and partial-output/failure policy must be settled before runtime implementation. See the new M5a qc milestone.

## Common pattern

1. Construct a context from immutable validated settings and an explicit resolved request. Copy caller data needed after construction; borrow caller buffers only under a separately specified lifetime contract.
2. Reject invalid/occupied output handles without overwriting them. The caller starts with result/error pointers set to NULL. Status is authoritative; an optional allocated error may remain NULL if error allocation itself fails.
3. Validate operation-specific inputs, layout, detector identity, units, requested/applied correction state and calibration applicability. No implicit file discovery, calibration selection or cwd dependency.
4. Construct a partial result whose destructor is valid at every construction step. Mutable scratch/handles belong to an explicitly owned context; borrowed calibrations/inputs are never freed by the operation.
5. Run the calculation with explicit state. Preserve legacy mathematics and defaults during extraction. Configuration readers, CLI parsing, TOML and ASDF objects stay outside numerical kernels.
6. Check the operation's declared postconditions. Do not introduce new scientific thresholds through a supposedly generic check.
7. Execute the explicit qc phase using the retained inputs/intermediates and attach declared measurements/availability to the result; estimators and scientific thresholds are not defined by the template.
8. Transfer the completed result to the caller only on success. It owns what it needs after context destruction; it must not retain dangling context/workspace pointers.
9. Use one cleanup section for still-local resources on all ordinary failure paths. Do not call exit/abort to handle a routine processing error, mutate environment/cwd, publish a project revision or delete original/published FITS products. Destructors release their owned memory/handles, not science products as a side effect.

A typical caller will create a context, call mef_cal_bias (or another operation), inspect status/result/error, then independently destroy result, error and context. The orchestration layer records the run and publishes completed products. A validated result handle is separate from durable product/project publication.

## What each new routine must declare

- Operation identity/version and purpose; input/configuration types, units, valid domains and selection/order assumptions.
- Input/calibration ownership, mutability, permitted aliasing and lifetime; detector/HDU layouts and explicit work/output locations.
- Output signal/variance/mask definitions and units; unknown/unavailable values and covariance limits; correction state and provenance fields. Missing variance is not zero variance.
- Scratch requirements and cleanup owner, error/status behavior, partial-construction guarantees and any cancellation/progress/logging hooks.
- Determinism/normalization dependencies and actual reentrancy limits. Explicit state prepares for parallelism but does not prove underlying Eclipse/qfits/parser code thread-safe.
- Preservation/equivalence fixtures and changed-ownership controls for success, invalid inputs and allocation/processing failure. No full historical reduction replay by default.

Use function pointers only where a real callback is needed (for example progress or cancellation), carried with explicit user context. Do not add a universal vtable/registry before the CLI/library/planner actually needs one. Optional mefppy must call these same C services, without a separate scientific implementation or process exits in a Python host.

## ANSI C and verification boundary

The template uses ISO C90 vocabulary: declarations at block starts, /* comments */, ordinary pointers/enums and goto cleanup. No C99 bool/stdint/VLA/designated initializer, C++ classes or compiler-specific facilities. The scoped external tomlc17 C99 exception does not change this template's baseline.

Agent check: compile-only strict C90 validation of the header/body with the neighboring M0 sketch. This checks syntax and calling declarations only: no link, helper implementation, lifecycle success or numerical behavior is established. M1 must implement and qualify common lifecycle/error helpers and at least one concrete operation before numerical extraction reuses the pattern. Include success, invalid/occupied outputs, partial construction, allocation failure and error-after-context-destruction controls, with no global state or implicit cwd/environment mutation. Actual Mac/Chapman checks remain part of that implementation gate.

Apply the full entry-point pattern to processing/service routines. Small private numerical helpers can use direct typed array/scalar arguments with the same ownership/error rules; do not allocate a context/result for every pixel operation.

Compile-only review check from the repository root:

```sh
cc -std=c90 -pedantic-errors -Wall -Wextra -Werror -fsyntax-only -x c docs/architecture/proposed/m1/mef_operation_template.c.txt
```

## First implementation increment

Owner authorized implementation after the verified effective-input map. See [owned configuration snapshot](config-snapshot.md): isolated C90 lifecycle/copy/dump implementation and focused tests; agent checks and returned Mac/Chapman C90 CMake probe builds/focused CTest pass; see the [paired receipt](../../../developer/m1-config-paired-results-2026-10-29.md). This is ready for bounded review, with target C17/sanitizer runs unclaimed. The numerical operation template above remains a design scaffold; M1 is not complete.

## Owned runtime increment

PR #137's configuration increment is accepted and merged at 1d991a22a39d6133ab19721b7bb3a6dd11394264. The next [runtime lifecycle implementation](runtime-lifecycles.md) adds independently owned request/context/result/error objects and configuration cloning. Agent strict C90/C17 and failure/lifetime checks pass. Returned Mac and representative Chapman4 C90 CMake probe builds and both focused tests also pass (2/2); see the [paired runtime receipt](../../../developer/m1-runtime-paired-results-2026-10-29.md). This increment is ready for bounded review; target C17/sanitizer results are not claimed. Execution returns unsupported until a numerical service is connected. The legacy CLI adapter, concrete operation/QC implementation and full M1 completion remain pending.

## Legacy CLI compatibility increment

After accepted PR #138, the [owned CLI capture](cli-compatibility.md) copies actual loader bindings/flags/original argv and effective config, retaining multi-step invocation semantics. Agent C90/C17 and corrected ASan/UBSan pass 51 cases. Diagnostic-only #139 bounds correction retains its failed first evidence; actual Mac/representative Chapman private C90 builds and three focused tests pass 3/3 (51 CLI cases each); see the [paired CLI receipt](../../../developer/m1-cli-paired-results-2026-10-29.md). Ready for owner review, with target C17/sanitizers unclaimed. #133 remains unchanged. This is not yet a resolved-operation adapter or complete M1; normal parser and numerical engine source are unchanged, and no image processing ran.
