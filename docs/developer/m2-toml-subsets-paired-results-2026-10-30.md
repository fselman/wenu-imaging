# M2 TOML subsets — paired target results — 30 October 2026

## Status and evidence boundary

Intel Mac and representative Chapman4 private C90 builds and both focused TOML
tests passed at implementation `d622bbec7e9784ab9fa6211080cfd4955ff3a08d`
(PR #148). Normal mefpp and config_paf_snapshot, config_toml_snapshot and
cli_capture_probe linked successfully on both targets. Protected installed files
and clean review checkouts passed preservation checks.

The second M2 increment is ready for bounded owner review. It adds reusable
native compatibility subsets and explicit restricted overrides, not the final
eight domain schemas, normal engine activation or complete M2.
See the [composition contract](../architecture/proposed/m2/native-subset-composition.md)
and [agent receipt](m2-toml-subsets-agent-results-2026-10-30.md).

Evidence is owner-returned terminal output inspected in Work chat, not an
independently transferred/hash-audited target-build archive. Detailed target
reports/logs remain in the paths below. No target C17/sanitizer/LSan, parser-wide
OOM, thread-safety, safe-Python-host, scientific or full-pipeline claim follows.
Existing legacy warnings remain; this is not a new warning-baseline audit.

## Actual target builds

| Target | Selected tools | Private work directory |
|---|---|---|
| Intel Mac MC02VV0HPHTDG, macOS 13.7.8 | Apple Clang 15, /opt/local/bin/cmake and ctest, explicit SDK/x86_64, /usr/bin/make/ar/ranlib, selected Python 3.11.14 | /Users/fselman/Software/build/wenu-imaging/mac-m2-subsets-XMrE6a9y |
| Chapman4, EL7 x86_64, shared home | devtoolset-10 GCC 10.2.1, private CMake/CTest 3.29.6, /usr/bin/make/ar/ranlib, selected Python 3.11.14 | /home/fselman/Software/build/wenu-imaging/chapman-m2-subsets-tXQ65FQm |

Fresh git-archive exports, Debug/C90, resources OFF, config probes ON, two jobs
and nice 10. Inherited build/compiler selections were recorded and cleared only
in each task subshell. No login/global environment or installation was changed.
Core composition/mapping retain C90; only the parser/private shim have the
documented C99 exception. This receipt is not an independent audit of target
compile_commands; the source target definitions and agent evidence are retained.

Chapman3/4 share the owner-qualified environment. Only representative Chapman4
ran this increment; no duplicate Chapman3/tool qualification is required.
The known SSH LC_CTYPE warning was nonfatal; no locale configuration was changed.

## Returned focused results

| Test | Mac | Chapman4 |
|---|---:|---:|
| native_config_toml | Passed, 4.32 s | Passed, 3.03 s |
| native_config_toml_subsets | Passed, 25.26 s | Passed, 24.67 s |
| Total | 2/2 passed, 29.59 s | 2/2 passed, 27.70 s |

Both targets reported:

- 585 exact OCAM, 249 exact WFI and 249 edge stored settings, with the retained
  type/float-bit comparison contract.
- 41 original single-file rejection/same-process-recovery cases.
- 16 composition/equivalence profiles from two unrelated caller directories.
- 32 composition rejection/same-process-recovery cases.
- Protected installed files unchanged and clean review checkout unchanged.

The passing probe contract includes clone/source destruction before use,
occupied output/diagnostic guards and all composition/snapshot owner allocation
failure positions for each valid profile. Per-case counts/logs remain on the
targets; this receipt does not claim separately transferred per-case artifacts.
The callback allocator excludes parser and original temporary detector-map
allocations; no blanket dependency allocation guarantee is made.

The real PAF constructor and retained CLI loader mef_bb_load are used as
references. The numerical recipe/mef_engine is not invoked, and no FITS or
Pycavi reduction runs. Equivalent split settings and selected numeric overrides
retain actual stored precision/units. Shared DAGs, canonical symlink aliases,
nested/scoped overrides, explicit parent resolution of sibling conflicts and
identical no-ops are exercised. Conflicts, forbidden/unused overrides, hidden
invalid child values, unknown keys, bad lists/versions, missing files and
cycle/path/depth/file/list bounds reject before valid same-process recovery.
Canonical pathname caching is not content identity or atomic filesystem capture.

## Retained reports

Relative to the Mac private work directory:

- `build/test-work/m2 native config vlb5hr9f/run-provenance.json`
- `build/test-work/m2 subsets _gzt8lab/run-provenance.json`

Chapman reports resolve through /home1/fselman, relative to
`/home1/fselman/Software/build/wenu-imaging/chapman-m2-subsets-tXQ65FQm`:

- `build/test-work/m2 native config cefuawhx/run-provenance.json`
- `build/test-work/m2 subsets a7u6hpvy/run-provenance.json`

Each work directory retains source.tar, source-commit.txt, source/build trees,
configure.log, build.log, tests.log, protected.json and
inherited-build-environment.json. Preserve every attempt and evidence file.

Received terminal transcript identities (not target-build archive identities):

| Transcript | SHA256 |
|---|---|
| Pasted text(20261030-115704).txt — Mac | f1f4732af43806061a874ab8b6ef0217103f2ab153d51ca53567b9ec3f77ea52 |
| Pasted text(20261030-120127).txt — Chapman4 | 9210ed68b9600275b9aa89516c9d953976a78cd2590ebbfcf360aba9e370ec13 |

## Preservation, review and remaining scope

Mac protected engine, normal executable configuration and installed reduction
module hashes passed. Chapman protected normal executable configuration and
installed reduction module hashes passed. Both checkouts stayed clean at the
tested review implementation. No installed selection was switched.

This paired receipt/current-status update is documentation only. No repeat
build/test, tool/dependency qualification or historical matrix replay is needed.
Owner review precedes explicitly instructed merge/cleanup.

Full domain schemas, normalized runtime unit/source/WAD records, durable hashes/
override histories and complete PAF/CFG migration remain later M2 work. Version 1
remains standalone; version 2 subsets remain in the opt-in interface. No M3–M11
reordering or new numerical model/QC policy is introduced. Optional BPM and
required M6a variances remain unchanged; #133/#144/#75 remain open.
