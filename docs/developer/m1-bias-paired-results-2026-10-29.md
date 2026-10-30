# M1 first bias service — paired target results, 29 October 2026

## Status and evidence boundary

Intel Mac and representative Chapman4 private C90 CMake configure/build and all
five focused tests passed at implementation commit
`f5858310e505bfc1b137491dc35676b9245ce674` (PR #145).
The normal `mefpp` executable and the four opt-in probes linked successfully.
Both checkouts remained clean at that revision; protected files passed their
post-run hashes. This increment is ready for bounded owner review; M1 is not
declared complete. No further build or test is needed for this documentation
receipt.

Evidence is owner-returned terminal output inspected in Work chat, not an
independently transferred/hash-audited target archive. The JSON reports and
detailed logs remain at the target paths below. No target C17/sanitizer, LSan,
whole-dependency OOM safety, reentrancy, scientific acceptance or complete
production-reduction claim follows from these results. #144 remains open.

## Builds and selected tools

- Mac work: `/Users/fselman/Software/build/wenu-imaging/mac-m1-bias-4kltu159`.
  Selected Apple Clang 15, /opt/local/bin/cmake and companion ctest, explicit Mac
  SDK/x86_64, /usr/bin/make/ar/ranlib and the wenu-imaging Python 3.11.14.
- Chapman4 work as printed:
  `/home/fselman/Software/build/wenu-imaging/chapman-m1-bias-nm5AG817`.
  CTest resolves the shared home as `/home1/fselman`.
  Selected devtoolset-10 GCC, private CMake/CTest 3.29.6, /usr/bin/make/ar/ranlib
  and shared wenu-imaging Python 3.11.14; inherited MPI CC was overridden for
  the subprocess, not changed globally.
- Fresh git-archive exports, Debug/C90, resources OFF, config probes ON, two
  build jobs and nice 10. Targets: mefpp, config_paf_snapshot, cli_capture_probe,
  input_request_probe and bias_service_probe.
- No tool availability/version/ABI requalification, duplicate Chapman3 run,
  install, package upgrade or normal executable selection change occurred.

## Focused test results

| Test | Mac | Chapman4 | Coverage returned |
|---|---:|---:|---|
| native_config_snapshot | 2.71 s | 0.79 s | OCAM 585, WFI 249, edge 249 exact mapped values; both actual PAF constructor snapshots |
| native_runtime_lifecycle | 1.65 s | 0.70 s | OCAM/WFI/override configuration and lifecycle controls |
| native_cli_capture | 5.20 s | 7.43 s | All 51 CLI cases; no reduction executed |
| native_bias_service | 2.99 s | 2.51 s | Eight legacy-equivalence profiles for each instrument, plus failure/lifetime controls |
| native_input_request | 1.33 s | 0.39 s | All seventeen cases from both unrelated directories |
| Total elapsed | 13.88 s | 11.88 s | 5/5 passed on each platform |

The bias contract compares exact synthetic pixels and existing stored QC with
the frozen pre-refactor body, exercises the changed mef_build_cal through the
actual legacy list/FITS loader, and checks independent analytic values. It
preserves the lower-median convention for even counts. Tiny generated MEFs and
in-memory frames are test fixtures; no observational FITS reduction or full
native recipe launch ran. The service uses explicit one-detector selection and
BPM omission, retaining unsupported status for selected calibrations/unsupported
layouts and explicit pre-M6a variance-unavailable metadata.

The driver also exercises twenty successful cycles and all 24 new-owner
success-path allocation positions in transient/persistent modes in each
instrument's three-frame control fixture. Target summaries confirm the complete
failure/lifetime contracts passed; detailed logs remain in the recorded runs.
These checks cover new service/result/request/diagnostic owners, not retained
Eclipse image/median/cube-rejection allocator failures (#144). New QC/RON
estimators and required variance propagation remain their later milestones.

## Retained reports

Mac reports, relative to the work directory above:

- `build/test-work/m1-config-rgbqyfts/run-provenance.json`
- `build/test-work/m1-runtime-els4hs9j/run-provenance.json`
- `build/test-work/m1-cli-7l0hwslm/run-provenance.json`
- `build/test-work/m1-bias-g62kax5o/run-provenance.json`
- `build/test-work/m1-inputs-kdhzxx3j/run-provenance.json`

Chapman reports, relative to the shared work directory above (resolved
`/home1/fselman/Software/build/wenu-imaging/chapman-m1-bias-nm5AG817`):

- `build/test-work/m1-config-tw2zyzao/run-provenance.json`
- `build/test-work/m1-runtime-jbrpn2ji/run-provenance.json`
- `build/test-work/m1-cli-do3w1t87/run-provenance.json`
- `build/test-work/m1-bias-3z1bnjo_/run-provenance.json`
- `build/test-work/m1-inputs-fwlfg25_/run-provenance.json`

Each work directory retains source.tar, exported source, build tree,
configure.log, build.log, tests.log and protected.sha256. Preserve them.

## Preservation and next step

Mac engine, normal executable configuration and installed reduction Python module
all passed hash verification. Chapman normal configuration and installed
reduction module passed hash verification. Both guarded checkouts stayed at
the tested commit and clean on work/m1-bias-service. No installed payload was
written. The existing SSH LC_CTYPE warning on Chapman was nonfatal; no login or
locale configuration was changed.

The grouped command/service mapping remains adopted interface direction:
`mefpp cal bias` calls `mef_cal_bias` when its CLI/loader adapter is implemented.
This increment does not enable that command, change notebook orchestration or
publish products. General loader/path integration and M1 closure remain
subsequent work; required variances stay M6a.

Next: synchronize the documentation receipt on the Mac, then owner review.
Acceptance and an explicit merge/cleanup instruction precede integration.
No repeat platform test, automatic repair or activation is needed.
