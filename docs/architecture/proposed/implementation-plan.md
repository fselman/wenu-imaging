# mefpp refactor implementation plan — proposal

31 October M3 is owner accepted/closed and PR #178 merged at
6c4b0f0eff639da8dbef890f0df10f86c70bb0ee; owner-returned Mac and Chapman4
cleanup confirms clean main, merged review branch removal and protected installs
preserved. Owner instructed M4 review and inclusion of `~/Pictures/ZWO_Bath/`.
The [M4 interface/fixture review](../../developer/m4-interface-fixture-review-2026-10-31.md) tracks #182:
independent detector/HDU maps, optional selectors, scaling, selection/reference
context and an astrophotography profile within existing visual-purpose vocabulary.
Returned Bath inventory samples 256/260 FITS: primary images, unsigned-16 scaling,
explicit flat-role ambiguity and 30 s dark/32 s light mismatch. Four headers remain
uninspected; no raw report/pixels independently audited. This is documentation and
source review, not M4 C implementation, reduction, profile activation or generic
CMOS acceptance. Review interfaces/fixtures before code; preserve original gates,
Pycavi grouping ownership, all evidence and installed environments. Earlier pending
M3 receipts below retain their historical scope.

31 October [summary/alignment paired receipt](../../developer/m3-summary-paired-results-2026-10-31.md): source
fc4b26cd1a1eed828a88d818fcdbb7912a2acbe2 passed 24/24 on selected Intel Mac
(6.938 s) and representative Chapman4 (3.563 s), with installed files and clean
main preserved. Direct real --summary displays five aligned CN Ori exposure rows,
retaining warnings and the missing historical flat reference without a wrapper.
The owner-requested interface addition is qualified; M3 closure is recommended
for owner acceptance, then separately instructed merge/cleanup and M4 review.
Documentation-only receipt: no executable change, test replay, install or host sync.
Earlier pending/held notes retain their stated historical scopes.

31 October owner requested [direct --summary output and aligned titles](../../developer/m3-inspector-summary-2026-10-31.md)
before M3 closure. Compact exposure rows/diagnostic counts now need no wrapper;
detailed tables also use measured spaces. Agent suite passes 24/24; actual Mac,
then representative Chapman presentation qualification remains pending. Prior
22-group reader and real-tree evidence stay valid; no reader/C/scientific change.
PR #178 stays draft for the added interface gate. No installation or activation;
owner acceptance/merge-clean precedes M4 review.

31 October #180 [corrected paired and real-tree receipt](../../developer/m3-eso-header-paired-results-2026-10-31.md): source
f7967fd1ee93f2a5a1a4faa227cadd460c054fa5 passed 22/22 on selected Intel Mac
(4.788 s) and representative Chapman4 (2.405 s), with installed files and clean
main preserved. Actual CN Ori redisplay now retains all five 80 s r_SDSS headers,
33 HDUs each, while retaining 36 warnings and one separate missing master-flat
reference. The original-scope M3 closure recommendation is reinstated for owner
acceptance; PR #178 is ready. No test replay/install/host sync for this receipt.
Separate owner merge/cleanup precedes M4 review; earlier held/pending notes are
historical. #181 remains a separate suffix-convention follow-up.

31 October subsequent actual-tree finding #180: nonstandard ESO telemetry
caused strict inspector verification to discard otherwise readable HDU metadata.
The [bounded correction](../../developer/m3-eso-header-inspection-2026-10-31.md) retains diagnostics and readable fields,
with no fixes to source files or image reads. New regression fails before; agent
corrected suite passes 22/22. Corrected Mac/Chapman qualification and repeated
bounded Chapman tree display remain pending. Hold the earlier M3 closure
recommendation and PR #178 in draft; preserve all earlier evidence. No native,
scientific, installation or M4 work. Earlier 21-group receipts retain their scope.

31 October M3 inspector [paired qualification](../../developer/m3-inspector-stages-paired-results-2026-10-31.md): exact source
0d8f2978a4ef4c78c47f1526b48e03d77351c024 passed all 21 groups on selected Intel
Mac (4.639 s) and representative Chapman4 (2.702 s), with installed module,
configured engine/configuration and clean main 3a61df6 preserved. The
[final original-scope M3 review](../../developer/m3-final-closure-review-2026-10-31.md) recommends milestone closure: the
inspector gap is resolved alongside accepted native paths. Owner acceptance and
separate merge/cleanup remain pending; then review M4 detector/layout interfaces.
This receipt is documentation only: no test replay, installation or host sync.
Earlier pending/gap notes retain their historical source/evidence contexts.

31 October owner authorized completing the remaining original M3 inspector work.
[Stage-view candidate](../../developer/m3-inspector-stages-2026-10-31.md) adds evidence-linked calibration/preprocessing/
normalization/WCS views and shared pure client conventions. Agent final 21/21
checks pass; initial test-only oracle #179 failure is preserved. Selected Mac,
then representative Chapman 21-group qualification remains pending; #159/M3 and
#179 stay open. No C code, numerical tuning, installation or normal activation.
Use exact private exports and protected-host runner; no historical matrix replay.
Cumulative closure precedes M4 implementation; merge/cleanup needs owner acceptance.

31 October cumulative review at accepted main 3a61df6: [original M3 checklist](../../developer/m3-cumulative-review-2026-10-31.md)
retains #159/M3 open. Native explicit paths have paired acceptance; the original
associated-calibration/preprocessing/normalization/WCS inspector overview remains
incomplete. Complete that bounded read-only integration before closure; no new
timing/debugging or historical test campaign is a prerequisite. [M4 readiness](../../developer/m4-readiness-review-2026-10-31.md)
is preparatory review only, with no implementation or milestone advance. Preserve
ESO OB/template/exposure metadata distinctions; grouping/association belongs in
Pycavi, while mefpp processes selected lists with compatibility checks. Review
only: no native/Python code, execution, installation or merge/cleanup. Earlier
increment receipts retain their original scopes and evidence.

30 October paired native safety receipt: selected-tool Intel Mac and representative
shared Chapman4 private optimized C90 builds and all four contracts passed 4/4
at 87ed266a109741c4998bfc8c978d07c9306f0091 (32.74 s / 20.77 s). Protected
installed module/engine/configuration and clean review checkouts stayed unchanged.
[Paired results](../../developer/native-safety-paired-results-2026-10-30.md) qualify the bounded #144/#171/#172/#174/#175/#176/#177
corrections; PR #173 is ready for owner review. #74 retains unqualified legacy
facilities; #125/#128, unresolved #116 and full M3/#159 remain separate. No real
OOM, broad leak/concurrency, RTD display or scientific/installed activation claim.
Preserve failed/corrected runs, manifests and tools. This documentation receipt
needs no functional replay; synchronize review checkouts, then await owner review.
Separate owner instruction precedes merge/cleanup. Earlier target-pending notes
below are historical within this qualified batch.

30 October actual Mac #173 batch stopped at b4fe1c6 during new format-probe
compilation: missing private variadic qfits declarations (#177). No functional
test ran; installed module/engine/config and checkout preservation passed.
[Correction/evidence](../../developer/native-format-prototypes-2026-10-30.md) includes existing qerror.h and makes implicit
declarations fatal for the probe. Corrected agent C90/C17/scoped ASan format
checks pass 1/1 each; production/other contracts unchanged. Actual corrected Mac
then Chapman four-test qualification remains pending; keep applicable issues
open and PR #173 draft. Use the new correction manifest, preserve the failed Mac
run and all earlier evidence. No install, automatic merge/cleanup or matrix replay.

30 October owner authorized batching reachable #74 fixes with #144 in draft
PR #173 before target handoff. [Complete format/buffer inventory](../../developer/native-format-safety.md) distinguishes inherited
message/newline (#174), timestamp, conditional RTD, header-merge (#176), keyword
and filename corrections from new probe-input mistake #175. Agent final C90/C17
four-contract batches pass 4/4; scoped address/UB format/allocation/swap checks
pass 3/3. [Agent receipt](../../developer/native-format-safety-agent-results-2026-10-30.md) retains failures, exact origins/hashes and limits.
Actual selected-tool Mac/representative Chapman combined four-test qualification
is pending; applicable tickets stay open. #74 also retains unqualified gnuplot/
FITS-table facilities; #125/#128 remain separate. No real OOM, broad leak, RTD
operation, numerical/scientific or installed activation claim. One combined host
handoff replaces the earlier two-test handoff; preserve all tools/installations/
evidence and separate #144 commit. No automatic merge/cleanup or matrix replay.

30 October owner authorized #144 after accepted/merged PR #170 at clean main
e2460fb72bdbe69f92c7da8994a81d21928569b5. [Bias dependency failure correction](../../developer/eclipse-allocation-failures.md)
checks inherited image/cube, crop, overscan scratch and final QC allocations;
#171 separately records inherited borrowed-cube destruction/ignored status.
The shared kernel and active native overscan callers propagate failure. Agent
C90/C17 allocation/native-path CTests pass 2/2; scoped ASan/UBSan allocation suite
passes 1/1. [Agent receipt](../../developer/eclipse-allocation-agent-results-2026-10-30.md) retains original failures and new test setup #172.
Actual selected-tool Mac/representative Chapman checks remain pending; keep
#144/#171/#172 open. Global qfits fatal RAM/swap policy is unchanged; no real OOM,
LeakSanitizer, complete-engine memory or scientific acceptance. Full M3/#159 and
other recorded limits remain separate. Preserve tools/installations/all evidence;
no historical matrix replay, automatic merge/cleanup or configured activation.

30 October paired qfits swap receipt: selected-tool Intel Mac and representative
shared Chapman4 optimized private C90 builds and both focused CTests passed 2/2
at 471f42e19e304e16872291172535e855a2f826d9. Protected installed files and clean
review checkouts stayed unchanged. See [paired results](../../developer/qfits-swap-paired-results-2026-10-30.md).
The 20-case forced-swap/ownership contract and real native-path regression passed;
#164 missing mode, #168 unowned cleanup and probe-oracle #169 are target-qualified.
PR #170 is ready for bounded owner review. Original M3/#159, long FITS strings
#125 and wider dependency allocation failures #144 remain open. No broad leak,
OOM/thread-safety/scientific or installed activation claim. Preserve all original
and corrected evidence/tools; this documentation-only receipt needs no replay.
Separate owner instruction precedes merge/cleanup. Earlier target-pending notes
below are historical within this qualified correction.

30 October paired native M3 receipt: selected-tool Intel Mac and representative
shared Chapman4 private C90 builds and both focused CTests passed 2/2 at
113156b94fe68f7bf2848c93ecd7451551db2984. Installed reduction module, configured
engine/configuration and clean review checkouts stayed unchanged. See
[paired results](../../developer/m3-native-paths-paired-results-2026-10-30.md). The actual C engine passed the native path contract
alongside the 51-case CLI regression. #163/#165/#166 corrections are target-qualified;
PR #167 is ready for bounded owner review. Original M3/#159 remains open, as do
#164 swap/O_CREAT, #125 long FITS strings and #144 wider OOM limits. No leak/OOM,
concurrency, scientific, complete-M3 or installed activation claim. Preserve
selected tools and all evidence; this documentation-only receipt needs no test
replay. Owner instruction precedes merge/cleanup. Earlier agent/target-pending
notes below are historical within this qualified scope.

30 October paired M3 inspector receipt: selected-Python Intel Mac and
representative shared Chapman4 passed all 15 grouped controls at
2c820effff393d5ea4e1555439397ef7c7a6cda6; protected installed files and clean
review checkouts stayed unchanged. See [paired results](../../developer/m3-project-inspection-paired-results-2026-10-30.md).
#160 entry placement and #162 canonical fixture corrections are target-qualified;
retain failed/earlier attempts and the read-only Chapman state confirmation.
PR #161 is ready for bounded owner review; original #159/full M3 execution and
inspection gates remain open. No installation, reduction, new numerical/ASDF
behavior or permanent JSON decision. This receipt changes no tested code and
needs no test replay. Owner instruction precedes merge/cleanup. Earlier draft/
target-pending notes below are historical; preserve tools and all evidence.

30 October M3 target finding: original a1a95c700a7bb7755cf81ac8e2213b3adc754f96
passed 14/14 on Mac, but Chapman returned two fixture failures and one error:
lexical /home expectations contradicted canonical /home1 identities. [#162
correction/evidence](../../developer/m3-inspection-canonical-fixtures-2026-10-30.md) resolves generated fixture identity and adds
an explicit alias regression; inspector/resolver/installed code are unchanged.
Agent reproduced all three failures and corrected 15/15 checks pass through an
aliased work-parent. Corrected Mac/Chapman verification remains pending; preserve
both target attempts. Chapman protected files passed but final checkout verification
did not run after failure. PR #161 stays draft; #159/#160/#162 remain open for their
applicable gates. No test-gate weakening, installation or automatic merge/cleanup.

30 October M2 is owner-accepted/closed after merged PR #158 and clean Mac/shared
Chapman main b872c8f44c1b54982069a3f94735da492a9dd739; owner instructed Proceed at M3.
The [first M3 increment](../../developer/m3-project-inspection.md) adds explicit path-base primitives and a
read-only legacy project inspector, with outer-package `pycavi project inspect`
entry, selected CFG/FITS headers, ordered lists, links, diagnostics and bounded
coverage. Agent 14 grouped controls pass; actual selected-Python Mac/representative
Chapman checks remain pending. #159 retains full M3 execution/overview gates; no
M3 completion, numerical routing, installed activation or milestone reordering.
Preserve owner-requested nested import banner (#59); #160 records new inspector
entry correction. Keep existing JSONs for now; metadata export is stdout only,
ASDF stays M7. Follow the plan/good practices and discuss departures first.
Preserve evidence/tools/installations; no historical matrix replay or automatic
merge/cleanup. Earlier M2 acceptance-pending notes below are historical.

30 October final M2 cumulative review after owner-accepted/merged PR #157 and
clean Mac/shared Chapman main 09a7aee4d69f04f5aeef954ff87c39d6f870d2d3:
[recommend original-scope M2 closure](../../developer/m2-final-closure-review-2026-10-30.md). The #155 project/native
composition gap is resolved; the complete checklist and six paired receipts support
configuration completion. This is a recommendation pending owner milestone
acceptance, not M3 execution. Retain existing JSON outputs for now as explicitly
instructed; human configuration remains TOML, and M7 retains planned ASDF
persistence without a newly invented JSON-removal requirement. Follow the current
plan and good programming practices; discuss proposed departures before
implementation. Source/evidence/documentation review only; preserve selected
tools, installations and all evidence, with no historical test replay. Separate
owner instruction precedes merge/cleanup. Earlier status notes are historical.

30 October paired project/native composition receipt: selected-tool Intel Mac
and representative shared Chapman4 private C90 builds and both affected CTests
passed 2/2 at d0ab19e91b46e6fe6e21c541af99c21ed35029b4. Protected installed files
and clean review checkouts stayed unchanged. See [paired results](../../developer/m2-project-composition-paired-results-2026-10-30.md).
The #155 configuration integration correction is target-qualified and ready for
owner review in PR #157. Full M2 closure remains a cumulative review/owner decision;
no M3, ASDF publication, numerical processing, installation or automatic merge.
Preserve selected tools and all evidence; this receipt needs no test replay.
Earlier target-pending notes below are historical. Separate owner instruction
precedes merge/cleanup.

30 October owner accepted/merged PR #156 and instructed merge, clean, and
proceed. At baseline ea35197a7f074ac1c44289e7bcc94336f92d6681, the next original-M2
increment implements [project/native composition](m2/project-composition.md) for #155. Project
envelope 2 composes reusable complete domain-v1 declarations; complete version-1
projects remain supported. The shared CLI/library loader uses the qualified C
resolver for complete/split/local native references and validates readout against
resolved settings, retaining all source texts/hashes/edges and domain origins.
Project conflicts fail (empty project override allowlist); numeric overrides stay
native. Agent focused C90 checks passed 2/2, including 18 primary profiles and 24
composition rejection/recovery cases. Actual Mac/representative Chapman checks
are pending. Native C/catalogs, installed software, numerical algorithms and
milestone order are unchanged; no M3 execution or ASDF publication. See
[agent receipt](../../developer/m2-project-composition-agent-results-2026-10-30.md). #155/full M2 closure remain open pending target/owner
review. Preserve accepted evidence; no historical matrix/tool replay or automatic
merge/cleanup. The earlier closure review retains its original as-is baseline.

30 October cumulative M2 review at accepted merged main
c0bbcc5866b49d64fad6498a029429b35ada9953: keep M2 open. Native configuration
resolution/equivalence, migration and provenance have accepted paired evidence,
but reusable project-domain composition is not connected to the frozen project
loader. The as-is loader still requires inline project domains and one complete
standalone native reference. [Closure review](../../developer/m2-closure-review-2026-10-30.md) records the original-gate
checklist, accepted chain and [remaining M2 integration #155](https://github.com/fselman/wenu-imaging/issues/155).
Do not infer full M2 closure from native test success or start M3. No source code,
new functional run, installation or numerical processing in this review; preserve
accepted tests/tools/evidence and implement no scope reduction. Owner review and
separate integration instruction remain required for this documentation branch.

30 October paired migration receipt: selected-tool Intel Mac and representative
shared Chapman4 private C90 builds and both focused configuration CTests passed
2/2 at 38f4f4d4bd05c4977f1624fc8737431527bdbe8a. Protected files and clean review
checkouts remained unchanged. See [paired migration results](../../developer/m2-migration-paired-results-2026-10-30.md). Ready for
bounded owner review; full M2 closure remains a separate cumulative review.
The corrected nested-package protection lookup is target-verified (#154); retain
the first failed handoff attempt. Establish all paths/interfaces from as-is source
and actual host evidence; never guess layouts. No test replay for this documentation
receipt, installation, numerical processing or normal engine activation. Preserve
all evidence/tools and milestone order. Owner instruction precedes merge/cleanup.
Earlier target-pending notes below are historical.

30 October M2 migration implementation after accepted/merged PR #151 and clean
Mac/shared Chapman main a09bec7e6bc0d3fa8d82245db59aaf3063ac0d94: owner authorized
finishing configuration migration. The shared Python API/CLI and opt-in native
configuration bridge now migrate PAF values through the original constructor,
retain PAF/CFG text/hashes and duplicate/conflict records, preserve exact parsed
TOML source graphs/override contributions, and freeze WAD configuration attributes
for CLI/library requests. New examples match all 585 OCAM / 249 WFI stored values
and selected local CLI overrides exactly. CFG values remain explicit compatibility
evidence; no scientific associations/identities or executable plans are invented.
Agent C90/C17 focused checks and scoped ASan/UBSan pass. Actual selected-tool Intel
Mac and representative shared Chapman checks remain pending; full M2 closure needs
those results and owner review. Preserve original PAFs, installed tools/prefixes,
prior evidence and milestone order. No installation, numerical processing,
ordinary engine activation, ASDF publication, merge or cleanup is authorized by
this implementation. See [migration contract](m2/configuration-migration.md) and
[agent receipt](../../developer/m2-migration-agent-results-2026-10-30.md). Earlier remaining-migration notes are historical within
this implemented boundary.

30 October paired project/readout receipt: Intel Mac and representative shared
Chapman4 selected Python 3.11.14 authoring checks passed at
3769f5196f9be2c2581673f89c61ae2a472167d3: six examples from two caller directories,
66 rejection/recovery cases, immutable sources/recipe order and malformed CLI
controls. Protected installed files/checkouts stayed unchanged. See
[paired results](../../developer/m2-project-contracts-paired-results-2026-10-30.md). Ready for bounded owner review; full M2 remains open.
No numerical/hardware execution or header-trust qualification is claimed. Preserve
evidence/tools; no rerun for this documentation receipt. Earlier pending-target
notes below are historical. Merge/cleanup requires owner instruction.


30 October next bounded M2 increment after accepted/merged PR #149 and clean
Mac/shared Chapman main ed949cab4f70381a1e187c7be691026c7fecf01c: owner authorized
[remaining project-domain authoring validation](m2/project-contracts/README.md) and
[optional/amplifier-specific overscan](overscan-readout-policy.md). Explicit omission requires no
region, defined geometry can be retained without subtraction, and enabled
subtraction requires valid selected-channel geometry. Distinguish available from
active amplifiers; no physical IDs/hardware counts inferred from legacy ordinals.
Header amplifier/scan values remain reported, unverified evidence; conflicts need
explicit review, not automatic header/config authority.
Python standard-library review validator and six examples only; ordinary native
engine/Pycavi/installation/numerics unchanged. Legacy mapper still needs retained
geometry and one active channel; no geometry-free/multi-amplifier execution claim.
Full M2/WAD/migration integration remains pending. Agent six-example/66-case
authoring checks passed; actual target authoring checks pending; preserve accepted native evidence/tools, no matrix replay. Owner review
precedes separately instructed merge/cleanup.


30 October paired typed-domain receipt: Intel Mac and representative shared
Chapman4 private C90 builds and all three focused TOML tests passed 3/3 at
920dd13251287c07ca9d9e3355e1cb9afcd38370. Exact legacy settings, subset controls,
151 catalog templates, 11 document/lifetime profiles and 25 domain/unit rejection
cases passed. Protected installed files/checkouts stayed unchanged. See
[paired results](../../developer/m2-typed-domains-paired-results-2026-10-30.md). Ready for bounded owner review; full M2 remains open.
Preserve evidence/tools; no rebuild for this documentation receipt. Earlier
pending-target notes below are historical. Merge/cleanup requires owner instruction.


30 October third M2 increment after accepted/merged/cleaned PR #148 and clean
Mac/shared Chapman main 7e665da170e2e1af9f96a97e9f5bc2f6ebcfeef5: owner instructed
“Proceed” with [typed native domains and sources](m2/typed-domains-and-sources.md). Input version 3 maps
all 151 getter templates into versioned instrument/detector, processing and
product mappings with explicit units, plus an owned immutable settings/source
document. Versions 1/2 remain supported. C90/C17 owns catalog/composition/report
logic; C99 remains parser-specific. Opt-in only; no normal engine/installation or
numerical changes. Full WAD/domain/migration/persistence work remains pending.
Build the normal engine and config_paf_snapshot/config_toml_snapshot/
cli_capture_probe/config_domains_probe; select only the three native_config_toml
compatibility/subset/domain checks. Agent C90/C17 3/3 and scoped sanitizer
checks passed; actual Mac/shared Chapman checks are pending;
preserve selected tools/evidence and do not replay the historical matrix.
No automatic merge/cleanup.

30 October paired subset receipt: Intel Mac and representative Chapman4 private
C90 builds and both focused TOML tests passed 2/2 at
d622bbec7e9784ab9fa6211080cfd4955ff3a08d. Original exact-setting/41-case controls,
16 composition profiles from two directories and 32 rejection/recovery cases
passed. Protected files/checkouts stayed unchanged. See [paired results](../../developer/m2-toml-subsets-paired-results-2026-10-30.md).
Ready for bounded owner review; full M2 domain/unit/source/migration work remains
pending. This documentation update requires no repeated execution or installation.
Earlier target-pending notes below are historical. Merge/cleanup requires owner
instruction.


30 October next M2 increment after owner-accepted/merged PR #147 and clean
Mac/shared Chapman main 0550fb90215c636cc6b881eb67e221c24b5ed876: owner instructed
“Proceed” with [native subset composition](m2/native-subset-composition.md). Version 2 adds containing-file
includes and explicit per-file numeric overrides, retaining standalone version 1.
Core composition stays C90/C17, parser shim C99; opt-in probes only, no normal
engine/installation or numerical change. Full domain/unit/source/migration work
remains M2. Agent C90/C17 two-test and scoped sanitizer checks passed; actual
Mac/representative Chapman checks for this increment are pending. Build the normal
engine and config_paf_snapshot/config_toml_snapshot/cli_capture_probe; select only
native_config_toml and native_config_toml_subsets. Preserve prior evidence/tools;
no historical matrix replay or automatic merge/cleanup.

30 October paired M2 target receipt: Intel Mac and representative Chapman4 private
C90 builds (normal engine and both probes) and native_config_toml passed at
b0ea0897ff2b5257eaf3bae0029b14a11a8f7152: all 585 OCAM / 249 WFI /
249 edge settings and 41 rejection/recovery cases. Protected files/checkouts
stayed unchanged. See [paired results](../../developer/m2-native-toml-paired-results-2026-10-30.md). Ready for bounded owner review;
full M2 composition/override/unit/source/migration work remains pending. No test
replay or installation is needed for this documentation update. Earlier pending
target notes below are historical. Merge/cleanup requires owner instruction.


30 October 2026: M1 is owner-accepted and closed following merged PR #146
(`7d8da6b96b7b744a51e3847522a727e3f510c6f2`); the October 29 handoff and fresh
Mac evidence confirm clean main. M2 begins with an opt-in native TOML compatibility
reader producing the existing immutable configuration. Full domain composition,
precedence/unit/source provenance and migration remain subsequent M2 work; no
M3–M11 reordering, installation or processing. See [the M2 reader contract](m2/native-compatibility-reader.md). Earlier pending-M1
notes below are historical. Actual Mac/shared Chapman integration checks pending.

29 October cumulative [M1 closure review](../../developer/m1-closure-review-2026-10-29.md): foundation deliverables and the first concrete operation are implemented and accepted incrementally through PR #145. Closure is recommended with retained limits; owner milestone acceptance remains pending. No milestone is reordered, no test replay is required, and M2 implementation has not begun. Historical preparation statements below retain their original scope.

29 October owner command-line decision: use [grouped native subcommands](command-line-services.md), one executable with `mefpp cal bias` / other `cal` operations and `mefpp sci pp`; retain the accepted C service names. Thin command adapters share the same request/settings/services as optional mefppy. M1 establishes callable operations; M3/M4 establish loaders/paths and M5/M6 connect the applicable commands. The [first bias service](m1/bias-service.md) is now implemented for bounded synthetic qualification; grouped command dispatch is not yet implemented.

29 October owner decision: use the [vendored, pinned tomlc17 source](../../../third_party/tomlc17/README.wenu.md) for the planned native TOML reader. Source import and byte-identity verification are approved now; the static build target and production adapter remain M2 implementation work after their prerequisites. Qualification N1–N4 on Mac/Chapman4 is complete within the recorded limits. This source import does not advance native numerical refactoring or install packages.
29 October owner addition: [bounded native TOML qualification](../../developer/native-toml-qualification-2026-10-29.md) now belongs to the current dependency work. Authorize private Mac/Chapman4 tests of pinned tomlc17 with a scoped C99 dependency exception, strict-C90 caller boundary, shared TOML 1.0 semantics/error controls and ownership checks before production parser adoption. Existing native source/public contracts retain C90; this does not authorize M1/M2 implementation, installation or processing. The completed Python/core-ASDF trial is preserved.

Version 5, 29 October 2026. Planning contract; milestone implementation requires its applicable owner authorization.
Baseline: accepted main 22a32d39463a73ab32d2ba9d811f949198852902.
Design: [target architecture revision 4](pycavi-mefpp.md).
Data contracts: [WAD and ASDF processing projects](wad-processing-project.md).
Evidence: [accepted OCAM/WFI baseline](../../developer/stage2-1-functional-results-2026-10-29.md), [source analysis](../../developer/mefpp-refactor-analysis-2026-10-29.md), [PAF inventory](../../developer/mefpp-refactor-paf-inventory-2026-10-29.md) and [Chapman4 census](../../developer/mefpp-refactor-chapman4-inventory-2026-10-29.md).

## Executive summary

Preparation receipt, 29 October 2026: [M0/M0a contract review package](m0-m0a/README.md) provides the minimal WAD review catalog, linked synthetic project example, native ownership sketch, expanded source ledger and focused verification plan. Status: prepared for review; parser/schema packaging, private effective settings and later numerical choices remain explicit open decisions. No M1 runtime implementation or new processing starts from this receipt.

Deliver one serial, numerically equivalent processing path with typed C configuration, TOML subsets, explicit file/detector references, modular native services and an ASDF-backed Pycavi plan. Replace the prepared-directory requirement without moving raw data or rewriting the scientific algorithms. Include single-detector layouts in the data contract and qualification. Add a readable recursive project inspection command in M3, replacing routine dfits/fitsort inspection. Include explicit numerical milestones M6a–M6d for variance creation/propagation, linearity, dark construction with optional native subtraction, and fringe-frame construction with later Python subtraction. Keep legacy-equivalence checks separate from acceptance of these additions.

WAD supplies common data contracts from M0a. A ProcessingProject is the evolving ASDF-backed scientific workspace; execution plans freeze a project revision, exact memberships/associations and resolved settings, while runs record actual attempts/outcomes. M7 implements persistence for these early contracts rather than first defining them.

The first pass records stable IDs, exact versions, ordered membership, association decisions, typed dependencies, task attempts and product provenance. It executes explicit manually selected plans; automatic change detection, invalidation/cascades and parallel execution are later milestones. mefppy is an optional first-pass deliverable after the native API is stable; its evaluation and API allowance are mandatory.

Use small reviewed increments, maintaining a legacy adapter until the replacement passes the accepted baseline. Each increment has targeted checks and a rollback boundary. Finish with one cumulative OCAM/WFI five-exposure comparison through notebook 04, reusing existing references. Do not repeat the Stage 2 compiler/memory matrix or reduce the large Chapman dataset.

Production dependency gate: [Chapman TOML/ASDF qualification](../../developer/toml-asdf-chapman-qualification-2026-10-29.md). Chapman machines are the main production targets. No new parser/ASDF runtime is adopted on Mac-only evidence; inspect actual target state, qualify the constrained dependency closure privately, and verify interchange/offline operation on both platforms before adoption.

Milestone IDs below organize this refactor; they do not renumber the global roadmap.

## Milestone map

| ID | Deliverable | Depends on | Completion evidence |
|---|---|---|---|
| M0 | Reviewable contracts and bounded verification plan | Existing analysis | Decisions, baseline checklist and unresolved choices recorded |
| M0a | WAD foundation and ProcessingProject contracts | M0 | Small linked record examples, authority/versioning rules and bounded validation checklist |
| M1 | Typed configuration and separated work/result state | M0, M0a | PAF-loaded effective settings/lifecycle equivalence |
| M2 | TOML subsets and deterministic configuration resolution | M1 | PAF/TOML effective-value and rejection checks |
| M3 | Explicit paths and recursive project overview CLI | M1; integrate TOML after M2 | Cwd-independent requests; readable, deterministic project/header/status overview |
| M4 | Detector/layout mapping | M1, M3 | Permuted/subset/primary-image/one-extension controls |
| M5 | Calibration subroutines and shared reference contract | M2–M4 | Legacy-equivalent calibration results and ownership |
| M5a | Explicit qc stage and measurement/result contracts | M5; common conventions in M1 | Declared measurements/availability/provenance; estimators and quality cuts reviewed before numerical implementation |
| M6 | Science subroutines and product writer | M5, M5a | Equivalent native science/results, safe ordered publication |
| M6a | Variance creation and propagation | M4–M6; contracts in M0 | Analytic controls, units, masks and stated covariance limits |
| M6b | Linearity calibration/correction subroutine | M5–M6a | Known-response controls, validity limits and propagated uncertainty |
| M6c | Dark construction and optional mefpp subtraction | M5–M6b | Matched/scaled dark controls; request/off behavior and variance |
| M6d | Fringe-frame construction and Python subtraction interface | M5–M6c | Template/rejection controls and explicit later Python handoff |
| M7 | WAD/ASDF persistence, project service and FITS resolver | M0a, M3–M4; finalized against M5–M6d | Offline round-trip, revision/reference/recovery and graph-version checks |
| M8 | Shared inventory/association planner; notebook 01 | M2, M7 | Legacy associations imported/reproduced and selection explicit |
| M9 | Serial executor; notebook 03 | M6–M8 | Selected dependency plan, truthful results and exactly-once corrections |
| M10 | mefppy decision and optional qualified binding | M6–M7 | Decision record; binding equivalence if adopted |
| M11 | Cumulative first-pass acceptance and migration handoff | M0–M9 including M5a and M6a–M6d; M10 disposition | Both instrument baselines, target checks, documentation and rollback |

Some schema/source work can be developed independently after its prerequisites, but integrate one reviewed boundary at a time. M0a establishes the WAD/project schema contracts early; M7 persistence can be prepared against them before all kernel extraction is complete. Final executable descriptors must agree with the actual native contracts. This dependency flexibility does not authorize concurrent uncontrolled changes or agent delegation.

## M0 — Freeze the contracts and verification boundary

### Work and deliverables

- Approve the split among immutable configuration, explicit request, detector work context and owned result.
- Define IDs/versions for assets, groups, calibration/association records, tasks, attempts and products; classify processing dependencies separately from descriptive graph relationships.
- Specify file-location bases, detector/HDU identity, units/correction state, output ownership, status/error reporting and API/schema compatibility.
- Define signal/variance/mask planes and their FITS references, variance units and initialization source, calibration uncertainty, covariance limitations, linearity validity domains, dark units/scaling/applicability and fringe-template conventions. Freeze recipe order before numerical implementation; later changes must identify which calibrations and products need rebuilding.
- Complete the migration ledger beyond the initial PAF inventory: consumed PAF fields, instrument/project CFG mappings, CLI options, defaults and known partition-local overrides. Record unresolved source-use cases instead of guessing.
- Decide the first implementation's TOML language subset/parser and ASDF ownership boundary. Recommendation: Python owns ASDF planning/resolution initially; native CLI remains independently usable with TOML/FITS. Assess language/license/platform/dependency implications before installing anything.
- Select the smallest synthetic fixtures and existing actual-host reference products for each boundary. No new pixel-quality certification.
- Record actual source/tool/package identity and comparison rules before changed code runs.

### Gate and rollback

A concrete schema/header sketch, migration ledger and test/product checklist are reviewable. Numerical defaults, common normalization, ordering, masks and Python gain/exposure normalization remain unchanged. WAD and ProcessingProject are the owner-selected design names; their public import/package/tag namespace and library dependencies are not selected merely by this plan. M0 modifies documentation/fixtures only; accepted installations and data remain untouched.

## M0a — WAD foundation and ProcessingProject contract

### Work and deliverables

- Establish Wenu Attribute Dictionary (WAD) definitions within the monorepo: vocabulary, meaning, types, units, required/optional/unknown states and schema compatibility. Keep schema versions independent of record/content/software versions.
- Define the smallest linked examples: ProcessingProject revision, observation, detector/image reference, calibration, ordered group, association decision, immutable ExecutionPlan, run/attempt and product/result.
- Record original instrument metadata, versioned normalization mappings and authority/source rules. Configured, raw-reported, characterized and derived values remain distinguishable; conflicts cannot be silently overwritten.
- Separate the evolving project manifest from frozen plan inputs/settings and append-only/versioned attempt/result evidence. Stable logical IDs are independent from physical FITS/HDU locations.
- Specify common configuration/native contract mappings so TOML, Python and C interfaces share semantics without embedding ASDF internals in C or adding an unqualified code-generation tool.
- Define offline distribution of schema resources, explicit old-version/unknown-tag handling and recoverable configuration snapshots.
- Draft the project service API for loading/resolving records, read-only inspection, explicit updates and single-coordinator publication with expected-parent revision checks.
- Record separate schema, reference/I/O, plan, numerical and product-profile validation levels. Specify ownership, storage-unit and covariance limitations for signal/variance/masks.
- Preserve the distinction among reduction profile, ordered recipe and product profile.

### Gate and rollback

Review the small schema/contract sketches and linked examples against OCAM/WFI metadata, a single-detector layout, shared calibrations and a missing/unbuilt product. Declare checks for exact-plan stability after a project/config update, configured-versus-measured values, location aliases and unsupported versions. Do not require modeling every future operation before extraction.

M0a acceptance covers the agreed contract/examples only. It does not qualify an ASDF runtime, create a production WAD package, migrate data or implement numerical processing. Unresolved format/packaging choices remain explicit; preserve legacy data and interfaces.

## Chain-wide BPM and variance rule

Owner addition, 29 October 2026: [input BPMs are optional throughout; variance support is required when introduced at M6a](bpm-variance-policy.md). Explicit omission differs from a selected broken/incompatible mask. Preserve generated validity flags; requested BPM construction still produces a BPM. All request/configuration/association/native/Python/inspection/product layers carry that distinction. This supersedes the former normal variance-disabled compatibility option for the new chain; pre-M6a signal-only legacy comparisons remain explicitly unavailable, not variance-capable acceptance. See the policy's stage matrix and bounded gates.

## M1 — Typed configuration and explicit ownership

### Work and deliverables

- Use the owner-selected entry names in [the service declaration sketch](m1/mef_services.h.txt): mef_cal_bias, mef_cal_bpm, mef_cal_dark, mef_cal_fringes, mef_cal_linearity, mef_cal_domeff, mef_cal_skyff, mef_cal_mff and mef_sci_pp. Establish an explicit qc phase/result convention; concrete QC estimators and thresholds are TBD.
- First deliver a common ANSI-C90 subroutine template and module checklist: consistent context/result/error/status interface, immutable settings/request contract, explicit ownership/partial construction, validation/calculation/postcondition separation, one cleanup path and success-only result transfer. See [the M1 template](m1/README.md). Reuse the pattern across services with operation-specific payloads; do not introduce an inheritance/dispatch framework or duplicate scientific implementations.

- Map native configuration/request/result fields to WAD concepts, with explicit units and status semantics; numerical code need not load ASDF schemas.
- Introduce small C configuration structures and validation independent from PAF/TOML syntax.
- Keep the current PAF reader as an adapter into those structures.
- Separate static instrument/algorithm settings from filenames, detector traversal state, calibration handles, statistics and task results currently mixed in mef_bb.
- Introduce explicit lifecycle/status contracts in .h and .c together. Existing recipe can use a compatibility adapter while extraction progresses.
- Provide a developer-visible normalized settings dump so equivalence is observable.
- Keep CLI parsing, initialization and informational commands out of reusable numerical routines. Use the agreed [grouped command/service mapping](command-line-services.md); private helpers remain internal.
- Carry explicit selected/omitted input-BPM state into the resolved-operation bridge and first service. Validate supplied masks without mandatory loading when omitted; return truthful application status. Reserve required variance source/validity contracts for M6a, without implementing new noise mathematics during extraction.

### Gate

The common template syntax compiles as strict C90; implemented lifecycle helpers must pass success, occupied/invalid output, partial-construction, allocation/processing-failure and independent result/error lifetime controls before numerical modules reuse them. A declaration-only template is not runtime qualification.

OCAM/WFI settings loaded through the old and adapted paths agree field-by-field, including defaults and output metadata mappings. Valid/invalid/partially constructed configurations release owned resources correctly; help/version remain independent of processing data. Targeted lifecycle diagnostics cover changed ownership, not a replay of the full historical matrix.

Cumulative disposition: see the [M1 closure checklist and native/WAD crosswalk](../../developer/m1-closure-review-2026-10-29.md). It reuses accepted evidence and distinguishes the bounded foundation gate from later loader/CLI/schema/numerical work. Owner closure acceptance is pending; this review does not activate the new interfaces or close existing dependency-memory findings.

### Rollback

Retain the legacy reader/engine path and original PAFs. A new type layout is not exposed as the permanent Python ABI.

## M2 — TOML subsets and configuration migration

### Work and deliverables

- Implement versioned domains: project/composition, instrument/detector, association, processing, recipe, execution, quality and product/profile. Keep separate reduction profile, recipe and product profile.
- Permit a small project entry point to reference reusable subsets; do not require eight files where fewer suffice.
- Define containing-file path bases, explicit override precedence/allowlist, unknown-key handling, schema versions and conflict diagnostics.
- Convert OCAM/WFI examples using the migration ledger; retain original text, conversion provenance and source hashes.
- Record identical duplicate PAF entries without silently accepting conflicting definitions.
- Produce one immutable effective configuration for both CLI and library requests, validated against WAD attribute definitions. Preserve resolved values and their sources in the plan; edits to mutable TOML cannot redefine an old run.

### Gate

PAF and TOML produce identical effective scientific settings for both instruments and the selected local override cases. Tests cover missing/unknown keys, types/units/ranges, conflicting definitions, subset cycles and paths with spaces. Parse success alone is insufficient. No thresholds or coercions change accidentally.

### Rollback

PAF remains supported during migration; no temporary splitting of PAF or independent second set of defaults. Removal of PAF occurs only after the integrated replacement is accepted.

## M3 — Explicit paths and project visualization commands

### Work and deliverables

- Route explicit resolved input/list/calibration/configuration paths and output/work/log destinations through CLI adapters, loaders, processing context and writers.
- Resolve user-relative arguments once at invocation; resolve TOML/ASDF references relative to their containing document or declared root binding.
- Import legacy relative lists using the recorded original execution base; flag unknown bases.
- Replace mandatory parent-process/library chdir and implicit local PAF discovery in the new path.
- Keep optional subprocess-private arenas only for unmodified external adapters that need them.
- Prevent output collisions from duplicate input basenames. Preserve established FITS metadata behavior; do not introduce full long paths into unsafe legacy cards as a side effect. Full locations belong in provenance records; deferred qfits #125 remains separately scoped.
- Support different read-only raw/calibration roots and writable output/scratch locations. Relative name handling must not leak into numerical kernels.

### Project overview command

- Add a read-only command, provisional spelling `pycavi project inspect PROJECT_ROOT --recursive`, that recursively reads existing projects and presents an understandable processing sequence rather than an unstructured file listing. Invocation must work from any directory.
- Present WAD attributes through a legacy adapter initially, then through the ASDF ProcessingProject service in M7. Preserve raw values and authority/conflict indicators; inspection never updates project revisions.
- Initially read legacy configuration, science/calibration lists, links and FITS headers; use the same resolved-path rules as execution. Adapt to ASDF records in M7 and the shared inventory/planner in M8 rather than maintaining a second association engine.
- Show project/instrument, target, filter, exposure time, detector coverage, partitions and ordered input membership; show associated bias/BPM/dome/sky/master-flat and later linearity/dark/fringe products, followed by native preprocessing, normalization and WCS products.
- Provide a concise overview plus drill-down by partition, exposure, detector and stage. Include selected header columns and sorting/filtering so this replaces routine dfits/fitsort commands. A table view and machine-readable export support notebooks and later graphical views; exact flags are settled in M0.
- Show counts, resolved locations, shared calibrations, missing/unavailable references, recorded attempts and available completion/failure evidence. Distinguish planned, existing-unverified and validated/published results; do not infer success or historical associations from filenames alone.
- Handle incomplete projects, unreadable headers and dangling links with visible diagnostics. Follow declared references safely, deduplicate shared assets, prevent symlink/graph traversal loops and report any scan limits or incomplete coverage. Default to metadata inspection without reading image arrays, bulk hashing, running reductions or modifying the project.

### Gate

Bounded legacy fixtures cover nested partitions, shared calibrations, missing products, malformed headers and cyclic links; verify stable grouping/order, header values, diagnostic counts, truthful coverage and no project writes. Compare requested header columns with known FITS cards. Later ASDF-backed views must retain these semantics.

The same explicit request launched from two unrelated directories produces equivalent pixels/relevant metadata and leaves cwd unchanged. Cover spaces, duplicate basenames, missing/incompatible inputs, no writes to raw storage and explicit output destinations. A single input-directory option or a hidden chdir wrapper does not meet this milestone.

### Rollback

The legacy arena adapter remains available for comparison. New outputs go to isolated attempts; existing arenas/links are not repaired or moved.

## M4 — Detector identity and image-layout layer

### Work and deliverables

- Represent detector identity, per-file HDU index/name/version, amplifier/geometry, shape/type/scaling, units and original order explicitly.
- Resolve each calibration's detector map independently rather than pairing by ordinal extension.
- Support primary image HDU 0, one image extension and MEF within the I/O descriptor.
- Keep health, user selection and processing result separate; preserve detector IDs when excluding a detector.
- Carry normalization-reference identity separately from selected output detectors. Initially preserve the legacy reference; absence/exclusion must not trigger an unreviewed replacement policy.

### Gate

Tiny controls cover shuffled calibration HDUs, duplicate/missing/unknown IDs, selected subsets and deterministic output order. Primary-HDU and one-extension fixtures reach the same detector processing entry point without requiring a fictitious mosaic. Compare an extracted detector with its mosaic counterpart using the same required shared calibration/normalization context.

### Rollback

Retain the explicit legacy mapping for already qualified fixtures; fail unsupported ambiguous layouts before arithmetic. No claim of generic CMOS qualification follows.

## M5 — Extract calibration services

### Work and deliverables

- Extract mef_cal_bias, mef_cal_bpm, mef_cal_domeff, mef_cal_skyff and mef_cal_mff operations from recipe/control code into callable C services. Connect each to its agreed `mefpp cal ...` thin adapter as the loader/service boundary becomes qualified; preserve legacy invocation during migration.
- Preserve actual algorithms, rejection order, thresholds, precision, masks and metadata.
- Separate loading, computation and publication; expose owned calibration results.
- Make shared dome/sky reference statistics an explicit input/result contract.
- Eliminate hidden input mutation or document controlled ownership transfer, particularly around mef_ff_combine.
- Distinguish native BPM construction from Pycavi's supplied-mask copying. This refactor does not silently change the observational recipe to generate new masks.
- Retain the existing sky/master-flat coupling through a compatibility recipe until separately represented operations are equivalent.

### Gate

Known-answer fixtures reproduce calibration arrays, detector mapping and agreed metadata; shared normalization matches the legacy reference. Relevant constructor/partial-failure/cleanup checks pass. Use existing accepted calibration evidence where unchanged; only exercise new boundaries needed by extraction.

### Rollback

One service per reviewable increment, with legacy/component comparisons. New variance, linearity, dark and fringe numerical capabilities are delivered in M6a–M6d, with separate acceptance from this legacy extraction. Gain/RON characterization retains its own scoped calibration work; configured values remain explicitly identified until replaced by characterized values.

## M5a — Explicit qc stage and measurement contracts

### Work and deliverables

- Define an explicit qc phase for calibration builders and, where applicable, mef_sci_pp. Separate measurement/reporting from structural result validation and any scientific acceptance/rejection policy.
- Carry QC measurements or explicit unavailable/not-requested state in owned results, with units, method/version, source/input selection and configured-versus-measured authority. Final WAD/C field definitions remain review work.
- Retain the required raw/intermediate information before trimming, rejection or release. Bias examples requested by the owner are mean level, RON and overscan mean level; regions, masks, input requirements, estimators, aggregation and thresholds are TBD.
- Implement individual QC estimators only after their numerical definitions and bounded verification are agreed. Do not introduce quality cuts, modify gains/RON/header values, reselection or re-reduction automatically through this reporting stage.
- Extend the common subroutine template with a qc phase; required/optional behavior and failure/partial-output policy must be reviewed before runtime implementation. Add appropriate QC to future linearity/dark/fringe builders at their own milestones.

### Gate and rollback

Review the QC stage and record contracts first. Later chosen estimators require synthetic/reference controls, explicit units/availability, detector/amplifier mapping and provenance before use. An absent measurement must never become a zero noise estimate or an implied quality pass. Preserve legacy numerical results and keep scientific acceptance thresholds unselected until separately agreed.

## M6 — Extract science processing and product publication

### Work and deliverables

- Expose requested calibration application/science preprocessing as mef_sci_pp; extract native science load/scan/trim/bias/flat operations into detector services with explicit calibration and correction-state inputs.
- Return structured result/diagnostic and qc records using M5a conventions; numerical routines cannot terminate the Python host.
- Separate FITS header construction, detector output and deterministic MEF assembly.
- Give each attempt unique temporary outputs; one coordinator owns the final product.
- Define publication/recovery states and prevent accidental overwrite. If scratch and output are on different filesystems, stage into the output filesystem before any same-filesystem atomic rename; do not assume a cross-filesystem rename or ASDF/FITS transaction.
- Keep Python mean-gain/exposure normalization in its current numerical owner during equivalence. State records must prevent a second application.

### Gate

Native science agrees with the legacy path on tiny fixtures and a bounded selected real case for each instrument. Test explicit paths, meaningful metadata/units, ordered complete publication and interrupted output behavior. Failed attempts never appear as published complete products. Exercise only modified failure/ownership paths.

### Rollback

Preserve all prior products and failed attempts. CLI default/installed selection remains unchanged until final acceptance and an explicit activation decision.

## M6a — Variance creation and propagation

### Work and deliverables

- Implement detector-level variance initialization from supplied variance or an explicitly selected noise model using gain/read noise and units. Record assumed versus measured calibration inputs; do not silently manufacture missing uncertainties or interpret missing variance as zero.
- Propagate signal, variance and masks together through trimming, bias/dark subtraction, flat division and gain/exposure scaling. Calibration builders return uncertainty/coverage information using the actual combination and rejection method.
- Account for calibration uncertainty and shared normalization estimates under a declared approximation; preserve references to shared calibration errors. An independent per-pixel variance plane cannot encode all correlations.
- Carry squared signal units, detector/HDU mapping, mask validity, model version and correction state. Pixels remain in FITS, including variance/mask planes or explicitly linked companion FITS; ASDF records their locations and meaning.
- Establish the handoff for later Python fringe subtraction and WCS/resampling stages. WCS header correction preserves pixel variances; actual resampling needs a separately specified covariance treatment.

### Gate and rollback

Use small analytic controls for addition/subtraction, division, scaling, masked/zero-flat cases and representative calibration combinations, plus bounded simulation where estimator uncertainty requires it. Check dimensions, nonnegative finite valid values and exactly-once scaling. Label unavailable or approximate uncertainty honestly. Preserve legacy signal equivalence. The new variance-capable chain requires initialization and propagation; it has no normal variance-off mode. Raw inputs may initialize variance from an explicit qualified noise model; missing required model/parameters or incompatible supplied variance must fail rather than fabricate uncertainty. Pre-M6a/reference signal-only comparisons remain separate, explicitly variance-unavailable, and cannot meet this completion gate. Optional input BPMs do not weaken variance requirements; see [the chain-wide policy](bpm-variance-policy.md).

## M6b — Linearity subroutine and calibration products

### Work and deliverables

- Define a versioned per-detector/amplifier linearity model with input units, valid signal range, reference convention, coefficients/table, calibration provenance and uncertainty.
- Expose linearity calibration/model creation as mef_cal_linearity. Add a private callable C linearity-correction kernel for application through mef_sci_pp; plan a separate calibration-building operation from linearity sequences so fitting and applying the model have distinct contracts.
- Specify the order relative to overscan, bias, dark and flat with the model convention; prepare all calibration inputs consistently and record which correction was applied.
- Propagate variance through the model response and supported model uncertainty. Flag saturated/out-of-domain values; no silent extrapolation.
- Expose explicit recipe/configuration selection and the same operation to optional mefppy.

### Gate and rollback

Known synthetic response curves recover declared reference signals within stated tolerances; cover identity response, detector-specific models, invalid domains and uncertainty behavior. Characterization of real detectors is a separate bounded dataset acceptance, not implied by code acceptance. Disabled correction retains the legacy signal path.

## M6c — Dark creation and optional native subtraction

### Work and deliverables

- Add mef_cal_dark as the callable C dark-construction service with explicit input selection, bias/linearity correction state, detector geometry, exposure, temperature/readout applicability, combination/rejection and output variance/masks.
- Distinguish an exposure-matched master dark from a dark-current rate product; record units and supported scaling. Exposure/temperature scaling is permitted only by the selected validated model, never inferred from a filename.
- Let mefpp subtract the selected dark on explicit request through the recipe/CLI and optional library request. Record applied dark version and any scale; omission/off leaves the compatibility path unchanged.
- Propagate dark uncertainty and relevant scaling uncertainty; reject incompatible or already-applied corrections. Link dark dependencies into associations, plans and future impact analysis.

### Gate and rollback

Controls cover known dark signals, matched exposure, explicitly supported rate scaling, disabled subtraction, missing/incompatible darks and no double subtraction. Check resulting pixels, variance, masks and provenance. Real temperature/exposure modeling requires separate measured qualification; preserve existing products and dark-disabled references.

## M6d — Fringe-frame creation and later Python subtraction

### Work and deliverables

- Add mef_cal_fringes as the callable C fringe-frame construction service using explicitly prepared, compatible input frames. Define source masking, background treatment, normalization, combination/rejection, detector/filter applicability, variance and coverage.
- Preserve ordered membership and preparation state; science-derived templates record their contributing science versions and any shared uncertainty/self-contribution limits.
- Publish the fringe template as FITS with ASDF calibration/provenance references. It is not automatically subtracted by mefpp.
- Specify a separate later Python subtraction operation: select the exact template, estimate or supply the scale, apply subtraction, propagate template/scale uncertainty and masks, and record correction state. Keep construction and subtraction independently selectable and resumable.

### Gate and rollback

Synthetic structured backgrounds and masked sources check template recovery, normalization, coverage and uncertainty. Verify publication and the Python handoff contract without claiming the later subtraction is implemented. Its later acceptance covers scale recovery, residuals, propagated uncertainty and double-application protection. Preserve unsubtracted products; no automatic fringe or iterative scientific policy is introduced.

## M7 — WAD persistence, ASDF project service and FITS resolver

### Work and deliverables

- Qualify the selected ASDF adapter and its transitive dependencies privately on the actual Mac and production Chapman target before adoption; require offline operation/interchange and preserve the working scientific stack.
- Implement the M0a WAD contracts for ProcessingProject revisions, asset/group/calibration/association/task/attempt/product/assessment, stable IDs, exact versions and typed edges. Schemas and native descriptors evolve together with explicit compatibility handling.
- Keep image arrays in FITS/MEF. Implement explicit FITS reference resolution and metadata/layout validation; ASDF external-array references do not themselves resolve files.
- Preserve ordered membership, original card/provenance references, logical versus physical locations and recorded configuration snapshots.
- Implement a small project entry manifest referring to distributed records; keep arrays in FITS and avoid recursively expanding cyclic graph objects into one giant project tree.
- Package required schema resources for offline reading. Define compatibility/migration or explicit refusal for unsupported versions; no implicit live schema download.
- Implement load/resolve/validate and explicit revision publication in a shared project service. Preserve project history; reject stale expected-parent updates and record interrupted publication without claiming a multi-file transaction.
- Persist frozen plans independently of run/attempt outcomes. Store recoverable resolved configuration and software requirements; actual execution identity must satisfy the request's compatibility contract.
- Define serializable native request/result descriptions against WAD. Optional native ASDF adapter remains a separate decision.
- Validate exact-version execution dependencies as a finite DAG, while permitting descriptive graph back-references.
- Reference signal, variance, mask, linearity, dark and fringe products explicitly, including model/scale versions, correction order/state and uncertainty limitations. Extend the M3 inspector to these durable records.
- Represent unavailable/planned, existing-unverified, validated and published products distinctly. Do not require a graph database or change monitor.

### Gate

Synthetic and bounded real metadata records round-trip without losing identity/order/units. Test relocation aliases, missing/mismatched files, duplicate detector selectors, unresolved IDs and true task-dependency cycles. A current plan continues to reference its exact inputs/settings after newer project revisions, TOML edits or calibrations are registered. Controls cover offline schemas, metadata authority conflicts, stale-writer rejection, interrupted project-entry publication and retained history; schema success alone is not scientific validation. No bulk pixel conversion or full-dataset content hashing is required.

### Rollback

ASDF records are additive; original FITS, CFG/PAF, lists/links and existing products remain intact. Retain a documented schema reader/migration boundary for later versions.

## M8 — Shared inventory/association planner and notebook 01

### Work and deliverables

- Use the shared ProcessingProject service and WAD records as the notebook/headless entry point. Separate read-only preview from explicit registration/association updates; preserve prior project revisions.
- Separate explicit-root inventory, classification/grouping, calibration association, selection preview and optional legacy-tree materialization.
- Import existing lists/links and local settings as evidence, preserving line order and original identifiers.
- Include explicit linearity/dark/fringe applicability and selection, with off/unavailable states rather than silently substituting calibrations.
- Reproduce selected historical association decisions before reviewing policy improvements.
- Save group membership snapshots, selected/rejected calibration candidates and selection rationale in ASDF.
- Make notebook 01 call this library; preserve inspectable human selection and overrides.
- Preserve independent workspace, raw-storage and reduction-project roots observed on Chapman4.

### Gate

Import a bounded example with shared calibrations, an unbuilt product and separate workspace/project roots. Its association graph matches the recorded input lists/links. Reading or previewing a plan writes no reduction products; repeated inventory does not silently alter selection. Do not reduce the 963 historical science-list memberships.

### Rollback

Legacy partition import/export remains usable; no directory relocation or new shallow layout is required.

## M9 — Serial executor and notebook 03

### Work and deliverables

- Open an ASDF ProcessingProject and select/freeze a plan from a specific revision; later project edits cannot change the running request.
- Execute an explicitly selected finite dependency plan through the modular native CLI, initially one task at a time.
- Build/reuse decisions are visible; a shared calibration runs once per requested version.
- Keep an explicit choice to build/inspect calibrations before continuing to science.
- Record exact input/config/software identities, task/attempt status, output references and normalization state.
- Make notebook 03 and a configured Python command call the same executor.
- Record product manifests in ASDF after validation; maintain a recoverable single-writer project index.
- Implement only bounded manual resume of an exact plan with validated reusable outputs. No watcher, automatic association change or impact scheduler.

### Gate

Selecting one group runs its dependencies only. A failed calibration stops dependent science; independent completed results remain recorded. Repeating a completed request does not blindly normalize again or overwrite products. Cancellation/interruption produces truthful attempt states. Notebook 04 consumes the resulting FITS outputs through explicit references; its scientific solver is not replaced.

### Rollback

Legacy notebook/library calls remain available for the preserved comparison baseline until the new client is accepted.

## M10 — mefppy feasibility decision and optional first binding

### Required evaluation

- Compare compiled CFFI, a CPython extension and a narrow ctypes boundary against the actual new C API, packaging/platform needs and ownership rules.
- Decide file-based requests first versus borrowed array buffers; do not promise zero-copy prematurely.
- Verify the native code has no unhandled process-exit, global cwd or unsafe cross-call assumptions before hosting it inside Python.
- Document initialization, context lifetime, diagnostics/cancellation, resource release and process isolation.

### If adopted in the first pass

Implement the narrowest binding over the same services as the CLI. Qualify repeated success/failure calls in one interpreter, cleanup, import outside the checkout and CLI/library equivalence. Test actual Mac and the identified Linux target. Releasing the GIL is not thread-safety acceptance.

### Gate and fallback

Record adopt/defer with evidence. A deferred binding does not block the serial CLI-backed first pass, but the native API must remain binding-ready. No permanent public Python exposure of mef_bb/Eclipse/qfits structures.

## M11 — Integrated acceptance and migration handoff

### Work and deliverables

- Run one cumulative candidate pipeline for the accepted five OCAM exposures and five WFI exposures across its three partitions, in fresh isolated outputs, through notebook 04.
- Reuse the accepted input/software records and old outputs as reference; compare new calibration/native/normalization/WCS results at their appropriate boundaries.
- Run separate bounded controls for M6a–M6d and integrate only qualified requested corrections; unchanged legacy comparisons run with new corrections disabled. The accepted Stage 2.1 dataset alone does not validate new calibration models or fringe subtraction in Python.
- Require declared detector coverage, pixel/unit/correction-state equivalence and expected provenance. WCS assembly must preserve its normalized inputs; compare astrometric behavior with an agreed deterministic/functional rule rather than requiring incidental solver metadata/timestamps to be byte-identical.
- Demonstrate actual primary-HDU/one-extension CCD preprocessing through the new services with suitable supplied calibration context; genuine detector-characterization/scientific qualification remains separate.
- Develop/check on Intel Mac and qualify changed interfaces on the actual selected Linux host, currently chapman4. Prior chapman3 evidence is not transferred automatically; collect fresh host/tool/allocation evidence before target changes/workloads.
- Run targeted ownership/error diagnostics for the new context/API/binding paths, not the full exhausted Stage 2 campaign.
- Verify WAD/ASDF round trips and native/client contract consistency, supported-version handling, project relocation/export completeness and preserved exact plans/history. Inspect offline schema resources and configuration snapshot recoverability.
- Publish current/target diagrams, configuration migration guide, installed resources/schema documentation, supported layout/backend matrix, known gaps and rollback procedure.

### Gate

Owner reviews the bounded functional results and actual target limitations. Earlier accepted Stage 2/2.1 evidence remains preserved; new refactor acceptance is a separate result. No scientific/Phase 3 certification or automatic downstream full-survey processing.

### Activation and rollback

Keep candidate prefixes/configuration private during qualification. Switching normal engine/package selection, removing legacy PAF support or retiring compatibility clients requires the concrete accepted migration/activation decision. Do not delete reference products, raw frames or failed history. Git merge/branch cleanup follows the owner's separate instruction.

## Later pass P — Actual process parallelization

After serial acceptance:

1. Profile representative detector operations, memory and I/O using bounded inputs.
2. Qualify immutable shared-reference barriers and isolated worker contexts/temporary paths.
3. Add allocation-aware process workers, ordered single-writer assembly and truthful worker failure/cancellation propagation.
4. Test one versus multiple workers, shared-calibration deduplication, failure isolation, cleanup/restart and serial equivalence.

No MPI, GPU or native-thread safety is assumed. Keep one numerical thread per worker initially and account for external tool threads. Optional threading/accelerators retain their separately reviewed roadmap assessment.

## Later pass G — Incremental association and reprocessing

### G1 — Change registration and advisory impact plans

- Register idempotent observation/calibration/quality/policy/membership changes.
- Find eligible associations even where the new calibration has no existing selected dependency edges.
- Re-evaluate selection and preserve the old decision; compute affected descendants only when effective inputs change.
- Produce an advisory plan with reuse/unavailable-dependency and resource implications; do not launch automatically.

Gate: unchanged selection creates no pixel work; newly selected calibrations affect the correct consumers; location-only changes do not force numerical reruns.

### G2 — Manually approved incremental execution

- Define versioned task signatures and qualified reuse rules.
- Deduplicate shared calibration rebuilds.
- Update combinations after new science arrivals without needlessly reprocessing compatible existing exposures.
- Preserve frozen releases while active projects may follow explicit selection policies.

Gate: demonstrate minimal affected work, exact-version consistency, recovery and preservation of older products on controlled graphs.

### G3 — Optional bounded automatic cascades

- Add explicitly enabled arrival monitoring and execution rules.
- Bound eligible change classes, task counts and CPU/memory/storage consumption.
- Coalesce/deduplicate events and suppress loops caused by the system's own publications.
- Define pause/cancel, owner overrides and audit trails.

Gate: predictable bounded cascades, no infinite event loop or unreviewed scientific association-policy change.

### G4 — Explicit iterative recipes, if separately needed

Represent successive calibration/product versions with stopping criteria, maximum iterations and failure/resource policy. Reject executable cycles. Scientific feedback methods need their own validation; a graph engine alone does not approve a fringe/self-calibration algorithm.

## Working rules across milestones

- Proposals identify concrete scope before code changes. Record distinct defects under existing/new issues and link corrections/verification before closure.
- Every test explanation names actual routines, inputs, outputs/pass criteria and limits.
- Preserve common mosaic normalization, detector identity/order, masks, units and numerical precision; review changes instead of silently accepting differences.
- Use source comments for technical reasons; maintain C headers, build/install documentation and attribution requirements with code changes.
- Keep required C90/C17 compatibility checks appropriate to changed code. Do not add language/library upgrades by implication.
- Batch work respects actual CPU/memory allocation and niceness policy. Interactive notebooks remain normal priority.
- No dates or speedup claims are assigned before implementation scope and representative measurements exist.
