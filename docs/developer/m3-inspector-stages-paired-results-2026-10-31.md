# M3 inspector stages — paired target results, 31 October 2026

Both selected Intel Mac and representative shared Chapman4 passed all 21 focused
groups at PR #178 source `0d8f2978a4ef4c78c47f1526b48e03d77351c024`, tree
`7239d8feb2e1908db7122aefbde0c612d5e86c37`. Both report successful installed
module, configured engine/configuration and checkout preservation. The source
was exported privately; both actual checkouts remained clean main at
`3a61df627edfdbb1ef43cc3c956dff74bd28c066`.

| Target | Result | Suite time | Retained export | Retained qualification |
|---|---|---:|---|---|
| Intel Mac MC02VV0HPHTDG | 21/21 passed | 4.639 s | `/Users/fselman/Software/build/wenu-imaging/mac-m3-inspector-export-tkpybeb5` | `/Users/fselman/Software/build/wenu-imaging/mac-m3-inspector-stages-7pja0rq0` |
| Shared Chapman4 | 21/21 passed | 2.702 s | `/home1/fselman/Software/build/wenu-imaging/chapman-m3-inspector-export-fbxshw8c` | `/home1/fselman/Software/build/wenu-imaging/chapman-m3-inspector-stages-3ltn5tsz` |

Suite evidence subdirectories are `m3 project inspection ys0gbftx` (Mac) and
`m3 project inspection piwxcru2` (Chapman). Export directories retain source.tar,
source-export.json, source and qualification.log. Qualification directories
retain tests.log, run-provenance.json and synthetic fixtures; the suite's nested
run-provenance.json records its environment and results. Times identify runs,
not performance benchmarks.

## Actual source/tool/protection contract

Each owner-run command guarded OS/hostname, canonical repository, selected
imaging Python environment, branch/full baseline SHA/upstream, clean state and
fetch/push origins before fetching. FETCH_HEAD was required to equal the full
tested revision. A fresh git archive and source hash record were retained without
switching or writing the working checkout. Work ran at niceness10 with numerical
thread limits of one; no C toolchain qualification or installation occurred.

The exported standard-library runner compared thirteen selected source files to
their exact git objects. It discovered the installed nested reduction module via
package search locations and unique canonical rglob matches, required it inside
the selected environment, and read the configured engine from actual [Paths]
mefpp with ConfigParser(interpolation=None). Before/after SHA256/modes/mtimes and
canonical identities protected module, engine/configuration and checkout, with
preservation in the runner's finally path. The returned successful console
receipts explicitly include those protection assertions and bootstrap clean-main
verification.

Evidence level: owner-returned terminal output inspected in this conversation.
Full raw target files have not been transferred or independently reread by the
agent; do not upgrade this receipt into an archive/hash audit. Do not infer
unreported target dependency versions from the agent environment.

## Functional contract and limits

The actual focused suite calls PathResolver, inspect_project and CLI, existing
ConfigParser/Astropy header reading and shared pure product conventions. It
retains all 15 prior groups and adds six groups for stage views, shared/unbuilt
calibrations, conflicting roles, ambiguous basenames, missing/unknown bases,
exposure filtering, bounded stage coverage and client equivalence. Inspector-only
controls trap image-array access and check bytes/modes/mtimes/cwd preservation.

The client equivalence group executes actual original and updated
mefpp_normalize_science/create_wcs_frame bodies on tiny synthetic float32 images,
using existing metadata routines. Arrays and relevant header cards agree exactly;
generated CHECKSUM/DATASUM cards are excluded. This group writes private tiny
products; it is distinct from the metadata-only inspector controls. It does not
qualify full installed imports, run_py4_solve orchestration or an external solver.

Original reference bodies, initial oracle failure #179, corrected/final agent
receipts and source hashes remain in the [candidate record](m3-inspector-stages-2026-10-31.md).
The corrected float32 oracle and original/updated client comparisons now pass
both actual target gates. #179 meets its bounded correction criteria; record this
evidence before closing it. Keep the failed run and all successful runs.

HIERARCH VerifyWarnings from the existing LIGHTCOR behavior and deliberate
conflicting-category fixture remain visible on both targets. Chapman's known
LC_CTYPE startup warning is nonfatal and was not repaired globally. No signal,
failed test or preservation failure appears in either returned receipt.

No native engine, solver, observation, package/tool install, configured activation
or original data change occurred. Header/category/unit/name claims remain
reported or expected evidence, never proof of successful normalization/WCS or
validated/published processing. No physical detector, scientific, Phase 3,
whole-engine memory/concurrency or full survey qualification is implied.

## Disposition

This paired gate completes the changed inspector boundary. The
[final cumulative M3 review](m3-final-closure-review-2026-10-31.md) maps it and the
previous accepted native receipts to the original M3 scope. Recommend owner M3
acceptance; PR #178 is ready for review. This documentation receipt changes no
tested code and needs no test replay or user-host synchronization. Merge and
branch cleanup remain separate owner instructions.
