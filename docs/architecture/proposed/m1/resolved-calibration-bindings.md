# M1 resolved calibration roles and explicit BPM choices

Owner authorized the next M1 request integration after accepted PR #141 and
clean Mac/shared Chapman main 30ebe2a148021b2719bb8c5972b678150e86489c.

## Implementation boundary

This increment adds the internal ANSI C90 mef_resolved_request_spec and
mef_request_create_resolved constructor to the existing runtime module.
It owns a typed role for every calibration reference and one explicit BPM
choice for each distinct input detector. The existing mef_request_spec layout
and untyped constructor remain unchanged; no new uninitialized members are
required of existing callers. The resolved view is NULL for those old requests.

Calibration roles use the eight owner-selected calibration families: bias,
BPM, dark, fringes, linearity, domeff, skyff and mff. These identify selected
calibration descriptors; they do not implement their algorithms or finalize
the future representation of coefficient/model products. No role is inferred
from a filename, list, configured default or requested operation.

Every input detector has exactly one selected/omitted BPM choice; repeated
exposures of that detector share that request choice. A selected choice needs
exactly one BPM calibration reference with the same detector ID. An omitted
choice permits none. Duplicate or unknown detector choices, absent choices,
zero/unknown states, missing/duplicate selected BPM references, role-count
mismatches and invalid image descriptors fail before a request is returned.
All supplied calibration descriptors belong to an input detector. Existing
array order, asset IDs and per-file HDU index/name/version are copied unchanged.

Different BPM choices for exposures of the same detector require separate
requests. This is a per-operation detector contract, not an implicit scientific
association rule. Other calibration applicability and operation-specific required
inputs remain later service validation; metadata construction is not numerical
acceptance. Even mef_cal_bpm can have no input BPM without claiming that a
requested BPM output has already been produced.

## Ownership and failure behavior

The new builder reuses the existing request copier and per-object allocator.
Role arrays, selection arrays and detector strings are independently copied.
Partial construction is destructible; failure never transfers a partial request.
Occupied output/error handles remain unchanged. Optional error allocation may
also fail; the returned status remains authoritative.

Context construction clones the resolved bindings as well as config/base
request data. Destroying the source request or changing the caller's strings,
roles or choices cannot change that context. Destruction releases each owner
once, including every new partial-construction allocation. Const views are
borrowed until owner destruction. There is no global mutable state, environment
or cwd mutation, or new installed ABI.

## Explicit limitations and next integration

The constructor performs structural metadata checks only. Absolute paths in
tests intentionally need not exist. A selected file that is unreadable, missing,
or has wrong dimensions/layout must fail at the later I/O/service boundary;
this constructor cannot prove that from a path string. Selected/omitted is not
applied/validated-FITS. No result/application status is fabricated.

The raw CLI capture still preserves unresolved lexical bindings. There is not
yet a conversion from lists to these resolved descriptors, a new CLI no-BPM
option, an engine routing change or a numerical service. The legacy engine's
BPM discovery has not been disabled. A future connector must consume the typed
choice rather than reintroduce a configured BPM after omission; passing only
the base view to the old engine does not meet that requirement.

mef_execute still returns unsupported and no numerical result. First connect
the existing input/list reader to these descriptors without inventing asset or
HDU identities, then connect a bounded concrete operation through the accepted
common template. General file-discovery replacement remains M3; shared
detector-layout generalization remains M4. M1 is not complete.

The [accepted BPM/variance policy](../bpm-variance-policy.md) controls all later
services: generated validity flags remain separate from optional input BPMs;
required variance initialization/propagation stays at M6a. This increment adds
no variance-off switch, noise model, estimator, QC threshold or scientific rule.

## Verification

The existing native_runtime_lifecycle driver now compiles the added
tests/resolved_request.c alongside its prior controls. For each of OmegaCAM,
WFI and the synthetic override fixture, controls exercise all nine operation
identities with omitted BPMs, all eight calibration roles, mixed per-detector
choices, repeated input detectors, seventeen rejected binding variations,
independence after source mutation/destruction, occupied/invalid outputs and
continued unsupported execution. Existing untyped requests remain untyped
through context copying.

For each profile, all 164 construction/context allocation positions are injected
in transient and persistent failure modes, with zero outstanding tracked owners;
twenty successful cycles per construction mode also pass. The preceding 268
runtime/config/result/error allocation controls remain passing. These checks
account for the tested owner allocations, not whole-engine leak acceptance.

Agent Ubuntu/GCC 13.3 strict C90 and C17 compilation with -pedantic-errors,
-Wall -Wextra -Werror passes, as do both runtime suites for all three profiles.
The C90 ASan/UBSan suite also passes with detect_leaks=0 and halt_on_error=1;
no LeakSanitizer result is claimed. A fresh C90 CLI probe built against the
changed runtime passes all 51 existing CLI cases without executing the engine.
Existing legacy compilation warnings remain retained, not described as a
warning-free production build.

Reports and profile logs are retained under
docs/developer/fixtures/m1-resolved-agent-2026-10-29/. Actual Mac/representative
Chapman CMake builds and the three focused tests remain pending. Use existing
selected tools and fresh private exports; no new tool qualification or duplicate
Chapman host test. No installation, real FITS read, reduction or notebook ran.
