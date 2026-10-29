# M1 resolved calibration/BPM bindings — paired target receipt

29 October 2026. Tested source:
`b3c5948b6c729f396c3f87d441e5da8978b21358`, PR #142.

## Executive summary

Private C90 CMake builds and all three focused CTests passed on the Intel Mac
and representative Chapman4. Both passed all 51 CLI compatibility cases,
effective configuration snapshots and the runtime suite containing the new
resolved calibration/BPM ownership controls. Ready for owner review; M1 remains
incomplete and no numerical service is connected.

This receipt records the owner's returned terminal output. Target reports/logs
remain on the respective machines; no independently transferred/hash-audited
target archive is claimed. No test was repeated for this documentation update.

## Results

| Target | Configuration | Runtime lifecycle/bindings | CLI capture | Total |
|---|---|---|---|---|
| Intel Mac MC02VV0HPHTDG | pass, 2.28 s | pass, 1.64 s | 51 pass, 4.99 s | 3/3, 8.91 s |
| Chapman4 shared environment | pass, 0.78 s | pass, 0.74 s | 51 pass, 7.58 s | 3/3, 9.17 s |

The configuration suite reports 585 exact OmegaCAM values, 249 WFI values,
249 edge values and both actual PAF constructor snapshots. Runtime suite
passes for OmegaCAM, WFI and a synthetic override profile. At this source its
driver compiles resolved_request.c with the earlier lifecycle controls; the
returned CTest output summarizes profile success, with individual control
messages retained in each profile log.

The added controls exercise all nine operation identities with omitted input
BPMs, all eight calibration roles, mixed per-detector choices, repeated input
detectors, seventeen rejected binding variations and independent context data
after caller mutation/destruction. They inject all 164 new construction/context
allocation positions per profile in transient/persistent failure modes and run
twenty ownership cycles per construction mode. Prior 268 allocation-position
controls remain included. These counts describe the source-defined passing
suite, not a separate target allocator/sanitizer report.

CLI suite passes twelve retained forms, default/full/repeated/partial/empty
bindings, bounded display selectors, rejected commands and informational exits.
The private probe exercises the actual loader/capture, never the numerical engine.

## Retained paths

Mac:
`/Users/fselman/Software/build/wenu-imaging/mac-m1-bindings-C7u3IVRx`

- `configure.log`, `build.log`, `tests.log`, `protected.sha256`
- `build/test-work/m1-config-9laxvw9_/run-provenance.json`
- `build/test-work/m1-runtime-se9b8ej1/run-provenance.json`
- `build/test-work/m1-cli-slb6luq6/run-provenance.json`

Chapman:
`/home/fselman/Software/build/wenu-imaging/chapman-m1-bindings-Q8C9pdVu`
(resolved CTest paths use `/home1/fselman`):

- `configure.log`, `build.log`, `tests.log`, `protected.sha256`
- `build/test-work/m1-config-p5_nluqp/run-provenance.json`
- `build/test-work/m1-runtime-_zhq04x6/run-provenance.json`
- `build/test-work/m1-cli-z8bv9eav/run-provenance.json`

## Selection and preservation

Both runs use fresh Git source exports and the established absolute paths in
[selected-tools.md](selected-tools.md): Mac Xcode compiler/SDK and MacPorts
CMake/CTest; Chapman devtoolset-10 GCC and shared private CMake/CTest 3.29.6.
Debug C90, resources OFF, config probes/testing ON, nice 10 and two build jobs.
No repeat tool qualification or additional copycat Chapman host run is needed.
The nonfatal SSH locale warning did not prevent testing.

Mac returned OK hashes for the installed mefpp, normal executable configuration
and installed Python reduction module. Chapman returned OK hashes for its normal
configuration and installed reduction module. Final guards confirmed clean
review checkouts at the tested source. No installation, engine/configuration
switch, notebook, real FITS processing or reduction ran.

## Limits and next work

These requests validate structural metadata and copied ownership. They do not
validate file availability, dimensions or calibration applicability and do not
report a mask applied. Legacy BPM discovery and CLI/list-to-operation conversion
are unchanged; mef_execute still returns unsupported. A future I/O/service
boundary must fail a selected missing/invalid BPM and honor explicit omission.

Prior agent strict C90/C17 and corrected C90 ASan/UBSan checks remain separate
evidence in the committed agent fixture directory. Target C17/sanitizer,
LeakSanitizer, whole-engine memory/scientific acceptance, variance processing and
whole-chain no-BPM operation are unclaimed. Required variance support remains M6a.

Next is owner review of this increment. After authorized integration, continue
the resolved input/list bridge and a concrete operation through the common
pattern. Preserve all evidence and working installations. This documentation-only
receipt needs no rebuild, processing or installation and authorizes no merge or
branch deletion by itself.
