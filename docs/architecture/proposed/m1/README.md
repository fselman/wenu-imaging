# M1 common subroutine template — C90 design contract

Owner requirement, 29 October 2026: provide a template subroutine that all extracted subroutines can use. Make this the first M1 design deliverable, before duplicating interfaces across numerical modules.

Use plain C structs, functions and opaque handles. This is a copyable calling/ownership pattern, not C++ inheritance, macros generating algorithms or a new dispatch framework. Each operation has its own implementation and may have operation-specific configuration/request/result payloads. Share status, error, lifecycle and metadata conventions; do not force bias, flat, linearity and image writing into an identical numerical signature or one giant state struct.

[Header](mef_operation_template.h.txt) and [routine body](mef_operation_template.c.txt) reuse the [accepted M0 native interface sketch](../m0-m0a/native-interface.h.txt). Names and ABI remain provisional. These are syntax-checkable review files, not production code: the operation helpers have declarations only, with implementation deferred to the relevant stage. They cannot perform processing or be linked as a complete library.

## Common pattern

1. Construct a context from immutable validated settings and an explicit resolved request. Copy caller data needed after construction; borrow caller buffers only under a separately specified lifetime contract.
2. Reject invalid/occupied output handles without overwriting them. The caller starts with result/error pointers set to NULL. Status is authoritative; an optional allocated error may remain NULL if error allocation itself fails.
3. Validate operation-specific inputs, layout, detector identity, units, requested/applied correction state and calibration applicability. No implicit file discovery, calibration selection or cwd dependency.
4. Construct a partial result whose destructor is valid at every construction step. Mutable scratch/handles belong to an explicitly owned context; borrowed calibrations/inputs are never freed by the operation.
5. Run the calculation with explicit state. Preserve legacy mathematics and defaults during extraction. Configuration readers, CLI parsing, TOML and ASDF objects stay outside numerical kernels.
6. Check the operation's declared postconditions. Do not introduce new scientific thresholds through a supposedly generic check.
7. Transfer the completed result to the caller only on success. It owns what it needs after context destruction; it must not retain dangling context/workspace pointers.
8. Use one cleanup section for still-local resources on all ordinary failure paths. Do not call exit/abort to handle a routine processing error, mutate environment/cwd, publish a project revision or delete original/published FITS products. Destructors release their owned memory/handles, not science products as a side effect.

A typical caller will create a context, call mef_bias_run (or another operation), inspect status/result/error, then independently destroy result, error and context. The orchestration layer records the run and publishes completed products. A validated result handle is separate from durable product/project publication.

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
