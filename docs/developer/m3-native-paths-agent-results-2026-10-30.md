# Native explicit paths — agent results, 30 October 2026

The candidate makes the C executable itself accept separated configuration,
input lists/files, calibrations and output/work/log locations, without changing
cwd or invoking Python. The original numerical routines and configuration
catalogs remain in place. See [the interface and limitations](m3-native-paths.md).

Baseline: owner-accepted PR #161, merged main
`ded31e876582dcbe044c2b99167c9d36e8c6ee03`, tree
`0ad88bd9753a67babded385c9166a003459eca65`. Branch: `feature/m3-native-paths`.
These agent runs used an uncommitted candidate; do not interpret the build-info
`unknown` revision as target/commit qualification. [Exact source hashes and raw
logs](fixtures/agent-m3-native-paths-2026-10-30/README.md) identify what ran.

## Actions and outcomes

| Lane | Actual focused checks | Result |
|---|---|---|
| Linux GCC 13.3.0 C90 | `native_cli_capture`, `native_explicit_paths` | 2/2, 27.16 s |
| Linux GCC 13.3.0 C17 | Same two tests | 2/2, 30.25 s |
| C90 ASan + UBSan, `-g -O0 -fno-omit-frame-pointer` | Full `native_explicit_paths` | 1/1, 53.59 s; address/undefined checks only |
| Intel Mac selected tools | Fresh private C90 build and both focused tests | Pending |
| Representative shared Chapman selected tools | Same focused C90 gate | Pending |

CMake/CTest: private 3.29.6; compiler `/usr/bin/gcc`, ar/ranlib `/usr/bin/*`.
Agent-only test Python 3.12.14 uses a private venv, NumPy 1.26.4 and Astropy 6.1.7,
within existing project bounds. No user package, selected production environment,
configured executable, PAF catalog or observation was changed. Native resources
were disabled in these private builds; no install was performed. The normal
engine and affected CLI probe were built; there is no historical matrix replay.

The 51-case CLI capture regression queries the actual production loader through
its existing probe, without numerical processing. The new native test calls
`mefpp` directly: `mef_bb_load`, `mef_paths_*`, existing subset/header/cube
loaders, `mef_engine`, overscan/bias/BPM/dome/sky/master-flat/science routines,
existing FITS writers and `mef_split`. No production Pycavi method is called.
The Python driver creates tiny known-answer fixtures and verifies outputs.

Each instrument has a legacy reference launch, eight successful explicit-path
profiles and seven rejection cases: **16 explicit profiles / 14 rejections** in
total. Success profiles cover complete calibration/science from two unrelated
callers, existing calibration reuse from both callers, a typed list, direct FITS
with relative PAF and explicit log, and split runs from both callers. Failure
controls cover duplicates, distinct equal basenames, missing/partially missing
members, omitted relative-list base, incompatible selected calibration geometry
and an existing output sentinel. They require nonzero positive exits, no new
products and preserved existing outputs, with no sanitizer report or signal.

The test compares exact pixel hashes/shapes/types, FITS cards and ordering with
the same binary's legacy route, normalizing only generated product IDs and their
references. Independent OmegaCAM arrays and WFI bias/BPM arrays are exact. WFI
continuous known-answer checks account for its unchanged frame-rejection limit
and allow 1e-6 relative float32 rounding; explicit-versus-legacy remains exact.
This is functional/numerical regression on synthetic data, not scientific
validation of the instruments or real observations.

Raw/config/list/calibration hashes, modes and mtimes remain unchanged; caller
directories remain empty and final cwd matches invocation. The initial
workspace-backed runs showed mode bits changing without content/mtime changes;
the cause is not established. Those failed attempts are retained. The same
assertions pass with fixtures on `/tmp`, selected through the documented CMake
fixture-parent option; no preservation assertion was removed. The agent runs as
root, so read-only mode settings do not prove kernel-enforced denial for an
unprivileged process. Actual ordinary-user target checks remain necessary.

## Findings retained and corrected

- #163: the first adapter treated a preallocated optional type array as proof of
  a second list column and crashed. It now checks the tokenizer column count,
  frees the unused array for one-column lists, and retains typed/partial cases.
- #165: applying OmegaCAM expected dome values to the unchanged WFI PAF was a
  test error. WFI rejects the synthetic second-chip 48000/52000 levels at 45000;
  its shared-normalized dome is 32000/19600. No production parameter changed.
- #166: direct FITS science skipped allocation of overscan statistics arrays.
  UBSan reproduced the null write. The direct branch now initializes/checks both
  owned arrays, matching the list branch; both instruments pass direct controls.
- Original #159 path dependence: legacy list loading validates against cwd
  before returning. The adapter reuses its tokenizer and resolves members before
  validation, without creating replacement lists. Explicit mode also clears the
  constructor's legacy BPM discovery prefix so omission and split do not probe
  caller files. Existing implicit behavior remains on the legacy route.

Issues #163/#165/#166 remain open pending actual target qualification and review.
Failed development/sanitizer runs are retained with the successful evidence.

## Limits and next gate

LeakSanitizer fails inside this container reading `/proc/.../task`; its failed
run is retained. The passing scoped sanitizer run explicitly sets
`ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` and
`UBSAN_OPTIONS=halt_on_error=1`. It is not leak acceptance. An initial optimized
ASan build was rejected by fortify because existing qfits swap `open(...O_CREAT)`
omits the mode argument (#164); the O0 lane passes without changing that code.
Forced swap/OOM, concurrency, thread safety, whole-dependency memory guarantees,
long FITS strings (#125), and #144 remain outside these successful claims.

Mac and representative Chapman must each build an isolated source export with
the selected tools and run only the two affected CTests; protect the actual
installed nested reduction module and configured engine using discovered paths,
and confirm the checkout stayed clean. Do not install or change engine selection.
M3/#159 remains open for the original cumulative path/overview gates, including
remaining inspector integration. No automatic merge/cleanup, JSON policy change,
new numerical algorithm or milestone reordering follows from these agent results.
