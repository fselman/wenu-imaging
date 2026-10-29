# Bounded contract verification

Baseline: 0fa9eaf157359a93f2a9196f6fff05dc3e96e220. This package changes documentation/review fixtures only. The check uses Python's standard library and no user data, native engine, ASDF runtime or extra dependencies.

## Prepared and executed in the agent environment

| Check | Inputs/routine | Pass criterion / limitation |
|---|---|---|
| Review-record structure | check_contract.validate; catalog + 25 linked records | Exact kind fields and primitive types; version/ID consistency and resolved typed references |
| Frozen plan | Two project/association/bias versions | Old plan/selection remains exact while new project selects a different version |
| Metadata authority | Synthetic original zero/configured nonzero gain | Both values and explicit configured source/conflict retained |
| Detector descriptor | Same detector with primary HDU 0, extension 1 and ordinal 7 | Descriptor validation passes independent of calibration HDU ordinal; no FITS inspection claim |
| Relocation | Changed raw root binding in project revision 2 | Old plan unchanged; no actual file movement/resolution |
| Negative controls | 13 isolated in-memory mutations | Reject unsupported schema, duplicate ID, absent/wrong-kind reference, unknown field, bad HDU, duplicate group member, incompatible detector, changed task calibration, task self-cycle, stale plan snapshot, fabricated unavailable variance and false publication |

The checker validates a deliberately limited review notation, not every possible WAD field, calibration policy, dependency graph or numerical input. A frozen plan with unavailable inputs is representable; readiness/execution preflight must reject actual launch until inputs are qualified.

## Later checks attached to their implementing milestones

| Milestone | Smallest intended controls / completion evidence |
|---|---|
| M1/M2 | Existing OCAM/WFI PAF-to-typed effective settings, constructor/default/CLI precedence; equivalent TOML settings and explicit invalid-value handling |
| M3 | Same request from two unrelated cwd values, read-only input roots, spaces/duplicate basenames; inspector nested/shared/missing/cyclic references, stable metadata and truthful coverage |
| M4 | Real tiny primary-HDU, single-extension and permuted-MEF FITS; ID/name/index agreement, geometry and independently mapped calibrations |
| M5/M6 | Extracted calibration/science routines against accepted arrays/metadata with unchanged settings; explicit errors, cleanup and ordered temporary output |
| M6a–M6d | Separate analytic/synthetic acceptance for variance, response models, dark construction/scaling/subtraction and fringe template construction; uncertainty and correction-state rules agreed first |
| M7 | ASDF round-trip with offline schemas, supported/unsupported versions and missing/mismatched references; expected-parent revision check and interrupted manifest publication |
| M8/M9 | Bounded legacy import and shared notebook/headless plan; missing calibration blocks dependent work, shared calibration once, resume exact plan without repeat normalization |
| M10 | Binding decision; only if adopted, repeated success/failure/lifecycle and CLI/library equivalence on actual Mac/Linux targets |
| M11 | One cumulative accepted OCAM five-exposure and WFI five-exposure comparison through notebook 04; targeted single-detector/new-feature controls separately identified |

No fixed native launch count is invented for the refactor. Freeze concrete smallest inputs/commands/pass criteria before each implementing increment. Do not replay the exhausted Stage 2 compiler/memory matrix or reduce the 963 historical Chapman memberships. Existing numerical defaults/common mosaic references and static BPM baseline remain intact.

## Not established by this preparation

- No real ASDF schema/converter/runtime or C TOML parser was installed/qualified.
- No code generation, C build, scientific calculation or FITS I/O was performed.
- No actual user Mac/Chapman execution or changed-interface qualification occurred.
- No persistence transaction, stale-writer recovery, full covariance or automatic cascade is implemented by the JSON checker.

Review the contracts and pending choices before claiming M0/M0a accepted or beginning native implementation.
