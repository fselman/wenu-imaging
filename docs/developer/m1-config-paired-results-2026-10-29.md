# M1 configuration snapshot — paired C90 returned results

29 October 2026. This records owner-returned terminal results for the first M1
implementation increment. It is ready for bounded review, not acceptance of all
M1 work. The retained target logs/reports have not been transferred for independent
archive inspection; distinguish the returned results from the agent evidence.

## Executions

| Property | Intel Mac | Shared Chapman environment |
|---|---|---|
| Actual host | MC02VV0HPHTDG | chapman4.sc.eso.org |
| Source revision | `5d660b9dfc15aada9b4bdeef5bce998f6b36fe9e` | `e5c3aba6e6b35530f528eb4942e54bd8e3b47884` |
| Selected compiler | Xcode Apple Clang 15.0.0 | devtoolset-10 GCC 10.2.1 |
| Selected CMake/CTest | MacPorts absolute paths | Shared `~/opt/cmake-3.29.6/bin/` |
| Language/build | C90, Debug, resources OFF, config probes ON | Same |
| CMake configure and `config_paf_snapshot` target build | Passed | Passed |
| Focused CTest `native_config_snapshot` | 1/1 passed, 3.01 s | 1/1 passed, 0.79 s |

The source difference between these two target revisions is the documentation-only
tool-selection policy; the native implementation and tests are identical.
Each run used the selected Python 3.11.14 environment, a fresh private source
export and build directory, two build jobs and lowered batch priority. It did not
install anything or run the reduction recipe.

Both returned tests report:
- all 585 OCAM mapped values and all 249 WFI mapped values match;
- the 249-field escaping/signed-zero synthetic fixture matches;
- actual PAF-constructor snapshots match for both instruments, after legacy
  object destruction.

The executed synthetic test asserts all 111 snapshot allocation-failure positions
per fixture, twenty ownership cycles per fixture, occupied/invalid output guards,
missing configured strings/detector array, source-independent inspection and
stream I/O failure. A nonzero native assertion/subprocess result fails the CTest.

## Retained target evidence

Mac work directory:
`/Users/fselman/Software/build/wenu-imaging/mac-m1-config-eKZqE79j`.

Mac report within that directory:
`build/test-work/m1-config-hjhrbyzp/run-provenance.json`.

Chapman work directory:
`/home/fselman/Software/build/wenu-imaging/chapman-m1-config-CRnyhqNU`
(resolves under `/home1/fselman/`).

Chapman report:
`/home1/fselman/Software/build/wenu-imaging/chapman-m1-config-CRnyhqNU/build/test-work/m1-config-boau4wbe/run-provenance.json`.

Each work directory retains `configure.log`, `build.log`, `test.log`, the
exported source and private build. Preserve them; do not rerun for this receipt.
Both checkout HEAD/clean guards passed. Mac SHA256 checks passed for the existing
mefpp executable, executable configuration and installed Python reduction module.
Chapman SHA256 checks passed for its executable configuration and installed
Python reduction module; no installed engine checksum was included there.

## Tool selection and limits

The owner confirms Chapman3/4 are copycat hosts sharing home directories.
Use the [selected absolute tools](selected-tools.md) directly; do not duplicate
tool checks, installations or platform qualification between these hostnames.
The M1 task check ran once on Chapman4 as the representative shared environment.

This is C90 configuration/lifecycle qualification of the opt-in library and
configuration-only probe, not a full executable/reduction test suite, a memory
audit of legacy constructors, scientific acceptance or completion of M1.
Actual-target C17 and sanitizer runs are not claimed by these returned results.
Agent C90/C17 unit checks and agent ASan/UBSan remain separately recorded;
LeakSanitizer was unavailable in the agent container and the successful run used
`detect_leaks=0`, with explicit allocation accounting.

The numerical engine and installed interfaces remain unchanged; the snapshot
library is opt-in, not linked into mefpp and not installed. PAF remains active.
Request/context/result/error lifecycles, effective CLI override capture and later
numerical service extraction remain subsequent M1 work. QC definitions and
TOML integration are not introduced here. Review this increment in PR #137;
merge/cleanup still require the owner's instruction.
