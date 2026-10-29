# M1 owned request/context/result/error lifecycles

Owner instruction: proceed after acceptance/merge of PR #137 and clean Mac/shared
Chapman main `1d991a22a39d6133ab19721b7bb3a6dd11394264` (29 October 2026).
This implements the next isolated lifecycle boundary. It does not complete M1.

## Implementation

`mef_runtime.h/.c` adds opaque request, context, result and error objects using
the existing `mef_status` and per-object `mef_allocator` from `mef_config.h`.
All code uses C90. The API is internal and uninstalled, not a frozen public ABI.

| Object | Owned data | Lifetime rule |
|---|---|---|
| Request | Operation/version, ordered input/calibration image references, work/output/log paths | Constructor deep-copies arrays and every string; descriptor is borrowed only during the call. |
| Context | Independent configuration clone and independent request copy | Caller may destroy both originals after construction; no process-global mutable state. |
| Result | Operation tag and copied product-reference metadata | Independent of context; construction alone does not claim a successful reduction or create products. |
| Error | Primary status and copied message | Independent of context and original message; secondary error-allocation failure leaves NULL while the primary returned status remains authoritative. |

Each constructor rejects occupied outputs without overwriting them. All owners
support NULL-safe destruction and cleanup from partial construction. Custom
allocator callbacks/user data must outlive every object created with them,
including errors/results that survive a context. Read-only accessor views are
borrowed until their owning object is destroyed; callers must not free or mutate
them. No asynchronous cancellation/thread-safety qualification is claimed.

`mef_config_clone` extends the accepted configuration snapshot to make the context
independent. It retains actual stored scalar types, small arrays, detector
settings and copied strings. Synthetic effective double/integer overrides test
that cloning preserves stored values instead of re-reading defaults or narrowing
them through an old PAF conversion. This is not an implementation of CLI override
parsing or capture.

The initial request descriptor uses the M0 image-reference vocabulary: stable
asset/detector identities, an absolute resolved path, a nonnegative physical HDU
index and an optional extension name/version. Index zero is allowed for primary
images. Detector identity is independent of HDU index. Input/calibration order is
preserved; no sorting, deduplication or inferred selection is performed.

Validation is structural only: required text, absolute Unix paths, selector
shape, operation/version and array-size bounds. It does not open FITS, verify
HDU selectors against file contents, resolve paths, check calibration roles or
applicability, load variance/mask planes, measure QC or create associations. Those
remain their own adapter/loader/science milestones. This descriptor is not the
final WAD/project schema or a replacement for the legacy request fields.

Operation tags cover the owner-selected `mef_cal_bias`, `mef_cal_bpm`,
`mef_cal_dark`, `mef_cal_fringes`, `mef_cal_linearity`, `mef_cal_domeff`,
`mef_cal_skyff`, `mef_cal_mff` and `mef_sci_pp` services. Version 1 is the initial
lifecycle contract. Unknown versions fail explicitly. `mef_execute` currently
returns `MEF_ERR_UNSUPPORTED` for every valid context with no result; it never
pretends that an unconnected numerical service produced data. The declaration-only
operation/QC template remains unchanged and is not linked as a fake calibration.

## Build and verification

The existing `MEFPP_BUILD_CONFIG_PROBES` option remains OFF by default. When
enabled, the isolated static snapshot library also builds the new runtime module;
`native_runtime_lifecycle` is an additional focused CTest. The engine executable
does not link this library and installed payloads are unchanged. The new test
runner can also compile directly with the explicit selected compiler and SDK.
Use the recorded project tools; do not reinstall or recheck the shared Chapman
toolchain. New task-specific checks run once on a representative Chapman host.

Agent Ubuntu/GCC 13.3 strict C90 and C17 tests pass with
`-pedantic-errors -Wall -Wextra -Werror`. The successful final C90 lane uses
ASan/UBSan with `ASAN_OPTIONS=detect_leaks=0`; no LeakSanitizer pass is claimed.
All 268 successful-construction allocation positions across request/context/
result/error/config-clone builders are injected, both as a single failed call
and as persistent OOM. Every checked owner count returns to zero, including
secondary error-allocation failure. Twenty cycles per owner also pass.

Both instrument fixtures retain exact context config dumps (585 OCAM and 249
WFI fields) after original configuration destruction. A third synthetic override
fixture passes. Tests cover two simultaneous independent contexts, primary/MEF
selectors, immutable copied ordering/identities/paths, malformed selectors and
oversized arrays, invalid allocator/output handles, unsupported versions and
execution, copied error text, independent result/error lifetimes, empty result
metadata, and preserving unsupported status even when error allocation fails.
The previous configuration snapshot OCAM/WFI/edge regression checks also pass.

Returned Intel Mac and representative Chapman4 C90 CMake probe builds and both
focused tests now pass (2/2); see the [paired receipt](../../../developer/m1-runtime-paired-results-2026-10-29.md).
These are returned terminal results, not independently inspected target archives.
Target C17/sanitizer results are not claimed. The increment is ready for bounded
review, with no further run needed for this documentation receipt. No FITS/reduction processing,
scientific acceptance, installation or notebook change has occurred. Retain all
accepted baselines and private evidence; do not replay the historical matrix.

## Remaining M1 work

Adapt actual legacy file/list/save-flag/CLI bindings and effective numeric
overrides to these boundaries; verify the retained request map and normalization
against the old path. Do not infer that the initial builder already captures
those legacy semantics. Then connect one real operation, using the accepted
validation/calculation/postcondition/qc/ownership pattern before broader numerical
extraction. QC definitions remain TBD, and TOML remains M2. No new lineage
cascade, concurrency, variance algorithm or ASDF persistence is introduced here.
