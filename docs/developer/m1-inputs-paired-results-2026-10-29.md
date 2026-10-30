# M1 file/list requests — paired target receipt

29 October 2026. Tested source:
`c9f974f680e72de48c6b0af24de3e1887f42a5e8`, PR #143.

## Executive summary

Private C90 CMake builds and all four focused tests pass on the Intel Mac and
representative Chapman4. Both targets pass 51 CLI cases and all seventeen new
file/list cases from each of two unrelated directories, alongside configuration
and runtime ownership checks. Ready for owner review; M1 is not complete.

This receipt records the owner's returned terminal output, not an independently
transferred/hash-audited target archive. Reports and full logs remain at the
paths below. No test was repeated for this documentation-only update.

## Results

| Target | Configuration | Runtime | CLI capture | Input requests | Total |
|---|---|---|---|---|---|
| Intel Mac MC02VV0HPHTDG | pass, 2.63 s | pass, 1.40 s | 51 pass, 5.42 s | 17 cases, two directories, 1.47 s | 4/4, 10.94 s |
| Chapman4 shared environment | pass, 0.78 s | pass, 0.67 s | 51 pass, 7.51 s | 17 cases, two directories, 0.39 s | 4/4, 9.41 s |

The configuration suite reports 585 exact OmegaCAM values, 249 WFI values,
249 edge values and both actual PAF constructor snapshots. Runtime passes for
OmegaCAM, WFI and synthetic overrides, including the previously implemented
resolved calibration/BPM metadata and ownership controls.

The input-request suite exercises actual mef_request_from_input and compares
against actual framelist_load in its recorded base. Cases cover omitted/selected
BPM, direct files, missing selected BPM/member, empty/oversized/NUL/quoted-space
lists, directory input, unknown base/image, ambiguous catalogue, explicit kind
without fallback, contradictory BPM and ownership for both mask choices.

Passing assertions include exact ordered duplicate expansion, supplied
detector/HDU mappings, unchanged cwd, and allocation cleanup. The source-defined
controls inject 34 omitted-BPM and 40 selected-BPM successful-construction
positions, twenty cycles per success mode, plus 43 positions in the missing
selected-BPM failure path. These are assertions in the passing suite; individual
control logs remain beneath the input-request work directory, not a separate
target sanitizer or whole-dependency allocator report. Existing Eclipse parser
allocations are outside the new allocator injection counts.

Quoted-space list names remain unsupported and are tested as rejection.
Spaces in containing paths and direct filenames are supported. Tiny synthetic
FITS bytes are generated and hashed by the Python test; the native adapter
checks file readability without interpreting headers or image arrays.
No astronomical inputs or numerical engine are used.

## Retained evidence

Mac work:
`/Users/fselman/Software/build/wenu-imaging/mac-m1-inputs-6mRHXKw6`

- `configure.log`, `build.log`, `tests.log`, `protected.sha256`
- `build/test-work/m1-config-igiuh4uy/run-provenance.json`
- `build/test-work/m1-runtime-_h_xa13b/run-provenance.json`
- `build/test-work/m1-cli-s0__ytwq/run-provenance.json`
- `build/test-work/m1-inputs-bi2ss7i9/run-provenance.json`

Chapman work:
`/home/fselman/Software/build/wenu-imaging/chapman-m1-inputs-LNRZTfpN`
(resolved CTest paths use `/home1/fselman`):

- `configure.log`, `build.log`, `tests.log`, `protected.sha256`
- `build/test-work/m1-config-rg_7swf_/run-provenance.json`
- `build/test-work/m1-runtime-ivv76ibh/run-provenance.json`
- `build/test-work/m1-cli-ur1pwa6q/run-provenance.json`
- `build/test-work/m1-inputs-f58edi76/run-provenance.json`

## Selected tools and preservation

Both runs used fresh Git exports, Debug C90, resources OFF, probes/testing ON,
nice 10 and two build jobs. Explicit paths follow [selected-tools.md](selected-tools.md):
Mac Xcode compiler/SDK and MacPorts CMake/CTest; Chapman devtoolset-10 GCC and
shared private CMake/CTest 3.29.6. No new tool/version/hash qualification or
duplicate copycat Chapman host run is required. The nonfatal SSH locale warning
did not prevent testing.

Mac returned OK hashes for installed mefpp, normal executable configuration and
installed Python reduction module. Chapman returned OK for its normal
configuration and installed reduction module. Final guards confirm both review
checkouts stayed clean at the tested source. No installation, executable switch,
notebook or astronomical-data reduction ran; all prior evidence is preserved.

## Limits and next work

The new adapter validates file access and constructs resolved requests using a
supplied image catalogue. It does not establish FITS format/geometry,
calibration applicability, atomic input locking, application of masks or thread
safety. Normal CLI routing and engine BPM discovery remain unchanged. General
M3/M4 path/layout work and the first concrete numerical service remain later
integration. Required variance creation/propagation stays at M6a.

Earlier agent C90/C17 and C90 ASan/UBSan evidence remains separate in the
committed fixture directory. Target C17/sanitizers, LeakSanitizer, whole-engine
memory/scientific acceptance and complete no-BPM processing are not claimed.
ASan agent runs used detect_leaks=0. No new scientific/QC policy is introduced.

Next: owner review, then explicitly authorized integration/cleanup. Continue
with the concrete operation through the accepted common template afterward.
This documentation-only receipt needs no rebuild, installation, repeated
qualification or processing; it does not authorize merge/branch deletion.
