# M3 native explicit paths — paired target results, 30 October 2026

Selected-tool Intel Mac and representative shared Chapman4 passed private C90
builds and both focused CTests at code revision
`113156b94fe68f7bf2848c93ecd7451551db2984` (PR #167), tree
`9314c04aa9311fa58a32fdc035fcf3f0e87fadd5`. Protected installed files and clean
review checkouts stayed unchanged. This increment is ready for owner review;
original full M3 remains open under #159.

The C executable itself selects configuration, input files/lists, calibrations,
output/work directories and log, without changing its invocation directory or
using Python for runtime path resolution. Existing numerical routines remain
in use. See [the native contract](m3-native-paths.md) and retained
[agent evidence](m3-native-paths-agent-results-2026-10-30.md).

## Returned actual target results

| Target | CLI capture | Native explicit paths | Total |
|---|---:|---:|---:|
| Intel Mac MC02VV0HPHTDG | Passed, 6.48 s | Passed, 30.98 s | 2/2, 37.47 s |
| Shared Chapman4 | Passed, 6.88 s | Passed, 29.69 s | 2/2, 36.60 s |

Actual retained work directories:

- Mac: `/Users/fselman/Software/build/wenu-imaging/mac-m3-native-paths-nem9pvi8`
- Chapman4: `/home1/fselman/Software/build/wenu-imaging/chapman-m3-native-paths-ehitgzsr`

Each contains export/extract/configure/build/test-inventory/tests logs, private
source/build/test fixtures and run-provenance.json. These are owner-returned
console results from the guarded commands; raw host files remain at the paths
above and have not been downloaded or independently re-read by the agent.
Times identify attempts, not performance benchmarks.

Both command groups guarded OS/host, resolved repository, origin fetch/push,
branch, exact HEAD, upstream and clean status. They exported tracked source at
the exact revision into a fresh private directory, used the already selected
absolute compiler/CMake/CTest/Python/make/ar/ranlib paths (Mac SDK/x86_64
explicit), C90 Debug, two build jobs and niceness 10. Numerical thread limits
were one; inherited build-selection variables were removed for child commands.
They built the normal mefpp executable and cli_capture_probe, with configuration
probes enabled, native resources disabled and no installation. Test inventory
required exactly native_cli_capture and native_explicit_paths before execution.
No historical matrix, C17/sanitizer target replay or dependency/tool upgrade.

## What the tests establish

The 51-case CLI test queries the actual production loader through its existing
probe, without processing images. The native contract calls the actual C
mef_bb_load/mef_engine, path/list/header/cube loaders, calibration/science
routines, FITS writers and mef_split. Python only creates/verifies tiny synthetic
fixtures; no production Pycavi reduction method is exercised.

Both instruments run their legacy reference plus 16 total successful explicit
profiles and 14 controlled rejections. Successful controls cover complete
bias/BPM/dome/sky/master-flat/science construction from two unrelated callers,
separate existing calibration reuse from both callers, typed lists, direct FITS
science with relative PAF and explicit log, and split pixels from both callers.
Failure controls cover duplicates, distinct same-basename inputs, missing/partial
members, unknown relative-list base, incompatible calibration shape and existing
output preservation. They require controlled positive failure exits and no new
products; a signal/crash is not an accepted rejection.

The contract checks independent known arrays and exact legacy-versus-explicit
pixels and FITS cards/order, normalizing only generated product identifiers and
references to those identifiers. WFI keeps its instrument-specific frame rejection
threshold and documented independent float-rounding tolerance; exact legacy
comparison is not weakened. Input/config/list/calibration hashes, modes and mtimes,
empty caller directories and final cwd are checked. This is functional numerical
regression, not observational/scientific or detector-identity acceptance.

The host drivers independently discover the installed nested reduction module and
read the configured engine from actual [Paths] mefpp configuration, then compare
bytes/modes/mtimes and resolved identities before/after. Both returned PASS for
protected installed files and checkout unchanged, including after the tests.
Actual module locations retain the nested `pycavi/pycavi` layout; no guessed flat
package path or configured-engine substitution was used. Chapman canonical /home1
paths were retained, without changing the home-directory alias or locale setup.

## Corrections and limits

#163 optional type-column ownership, #165 WFI fixture expectations and #166 direct
science-FITS statistics allocation have passed their focused agent and actual
Mac/representative Chapman gates. Record the correction/paired evidence in each
issue before closing these bounded defects. Preserve their original failed runs.

Existing #164 swap/O_CREAT, #125 long FITS strings and #144 wider allocation limits
remain open. Agent address/undefined sanitizer results retain their explicit
LeakSanitizer limitation; these target C90 checks add no leak, forced-swap/OOM,
concurrency/atomic-publication, thread-safety or scientific acceptance. Supported
legacy whitespace-list/path-length bounds remain as documented. Full original
M3/#159 execution and inspector integration is a separate cumulative gate.

This receipt changes documentation only; tested code and fixtures are unchanged,
so it needs no rebuild or test replay. Keep the working installations, configured
engine, selected tools, source catalogs and all evidence. No ASDF publication,
JSON policy change, milestone reordering or automatic merge/cleanup. Owner review
and a separate merge/cleanup instruction remain required.
