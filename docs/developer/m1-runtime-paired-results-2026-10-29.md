# M1 runtime lifecycles — paired C90 returned results

29 October 2026. Owner-returned terminal results for source
`bca72e8c97cde2e319c7eb5d36bb5fd02b863688`, branch
`work/m1-runtime-lifecycles`. This records the new lifecycle increment, not
completion of M1. Full target archives have not been transferred for independent
inspection; distinguish returned target results from retained agent evidence.

| Check | Intel Mac (MC02VV0HPHTDG) | Representative Chapman4 |
|---|---|---|
| Selected compiler | Xcode Apple Clang 15.0.0 | devtoolset-10 GCC 10.2.1 |
| Mode/build | C90, Debug, resources OFF, config probes ON | Same |
| Private CMake configure / probe-target build | Passed | Passed |
| native_config_snapshot | Passed, 3.43 s | Passed, 0.85 s |
| native_runtime_lifecycle | Passed, 1.59 s | Passed, 0.74 s |
| Focused CTest total | 2/2, 5.03 s | 2/2, 1.59 s |
| Checkout source/status guards | Passed | Passed |

Both runs used the selected absolute Python/build tools, fresh source exports
and private build directories, lowered batch priority and two build jobs.
The shared Chapman environment was checked once on Chapman4. Do not repeat
tool checks or duplicate this run on copycat Chapman3.

## What passed

Configuration regression: 585 exact OCAM values, 249 WFI values, the 249-field
edge fixture, and actual PAF-constructor snapshots for both instruments.

Runtime lifecycle: OCAM, WFI and synthetic stored-override fixtures all passed.
The executed native assertions exercise 268 allocation positions per fixture,
each with transient and persistent OOM; twenty cycles per owner; two independent
contexts; copied primary/MEF selectors, identities/order/paths; invalid and
occupied outputs; unsupported version/execution; result/error independence
after context destruction; empty result metadata; error-message copying; and
preservation of the primary status when allocating its error also fails.

A context's configuration dump remains exact after destroying original owners.
These are lifecycle/configuration tests, not numerical image reductions.
An image reference with HDU index zero tests the descriptor boundary, not
complete scientific support for primary-image processing.

## Retained evidence

Mac directory:
`/Users/fselman/Software/build/wenu-imaging/mac-m1-runtime-e6k9dWjX`.

Reports within that directory:
- `build/test-work/m1-config-ygpd2lar/run-provenance.json`
- `build/test-work/m1-runtime-u8jaybk8/run-provenance.json`

Chapman directory:
`/home/fselman/Software/build/wenu-imaging/chapman-m1-runtime-8FciIk0s`
(resolves beneath `/home1/fselman`).

Reports within that directory:
- `build/test-work/m1-config-atjkv106/run-provenance.json`
- `build/test-work/m1-runtime-fv7ehz_1/run-provenance.json`

Each retains `configure.log`, `build.log`, `tests.log`, exported source and the
private build. Preserve all files; no rerun is required for this receipt.
Mac SHA256 checks passed for the existing engine, user executable configuration
and installed Python reduction module. Chapman SHA256 checks passed for its user
configuration and installed reduction module; its block did not hash the installed
engine. Both checkout HEAD/clean guards passed.

## Limits and next step

Ready for bounded owner review of PR #138. Actual target C17/sanitizer results
are not claimed. Agent strict C90/C17 and ASan/UBSan remain separate evidence;
the successful agent sanitizer run explicitly disabled LeakSanitizer and used
per-object allocation accounting. No full memory/scientific certification.

The opt-in library is uninstalled and outside the normal engine. No actual
CLI adapter, list expansion, calibration-role/applicability check, FITS I/O,
numerical service, QC estimator, notebook change, installation or reduction ran.
Legacy binding/save-flag/effective-override capture and a concrete operation
remain subsequent M1 work. No merge or cleanup until the owner's instruction.
