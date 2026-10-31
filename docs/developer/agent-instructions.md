# wenu-imaging agent instructions

31 October owner approves [practical ASI preparation inputs](asi-simple-inputs-2026-10-31.md):
reusable observatory/camera TOMLs and directory role/filter names generate the
detailed dataset TOML; no manual exposure/gain/offset/temperature/filename rules.
Role/filter directories work in either order. Header-first filters are checked
against directory labels; missing filters can be proposed, unknowns stay unknown.
Dome/sky/unspecified flats remain distinct, conflicts block and flat-Light labels
still require acknowledgement. Agent 9+11+12 controls pass; actual Mac new-interface
qualification is pending. Prior explicit-interface Mac 20 controls/full 260 plan/
ten-copy passes at 7bf1c824 remain valid for that version. Uploaded manual saved
unchanged under docs/manuals/cameras, facts sourced without inferring acquisition
mode/physical gain. Preserve originals/installations and native boundaries;
partitioning is deferred. No automatic merge, reduction, installation or M4 closure.

31 October owner authorizes [generic TOML-driven ZWO ASI preparation](zwo-asi-provenance-2026-10-31.md)
after previous-helper actual Mac 260-file plan and ten-copy checks passed.
The generic entry point separates camera/dataset rules and sourced provenance;
existing INSTRUME/original cards/payload remain, conflicts block preparation.
Bath Physics Observatory/institution and paper/data DOI are configured. Returned
260-frame 200/1600 mm header signature identifies the StellaLyra RC; configured
checks add a dated WENU telescope label while preserving TELESCOP=SynScan.
Observer, coordinates and software versions stay unknown.
Agent legacy 9/9 and current generic 11/11 pass; candidate #187 parse-error
reporting is fixed but target-pending. Fresh Mac provenance plan/copy checks remain
pending. No reduction, installation, native changes, M4 closure or automatic
merge/cleanup; original review/helper PR #183 and native PR #186 stay unchanged.
Earlier pending statements retain historical scope.

31 October owner clarification: identifying native Windows obstacles is
informational preparation for a possible later port. It must not affect Mac/Linux
design, introduce Windows-driven adapters/abstractions or overhead, or block their
acceptance. If Windows is ported later, that version receives the required adapters
then. Preserve efficient native Mac/Linux facilities and the no-speed-penalty
refactoring requirement. This supersedes any earlier Windows wording suggesting
current Mac/Linux design restrictions; no source changes or tests are needed.

31 October owner makes native speed/efficiency preservation an explicit
refactoring requirement and requests early native-Windows difficulty identification.
The [performance/portability contract](native-performance-portability-contract-2026-10-31.md)
requires no reproducible same-workload slowdown, with wall/CPU time, memory and I/O
compared on matched optimized builds; no percentage penalty is preapproved.
Concrete source barriers include the Windows build guard, qfits mapping/swap,
FITS stream/offset handling, Unix path/permission assumptions and Eclipse OS helpers.
This is source/design review only: no benchmark, Windows build or portability patch.
Apply at changed native boundaries and cumulative acceptance; retain existing
Windows sequencing, C90/numerical behavior, all evidence and working installations.

31 October owner added raw-input DPR.TYPE/CATG/TECH preparation to M4 review.
The [data preparation guide](../data-preparation.md) reviews official ESO DICB v8
and ZWO ASI1600 manual rev1.5. Dataset-specific Python helper #184 proposes Bath
directory roles with header checks, then writes explicit reviewed-plan copies
with unchanged payload bytes; originals stay untouched. Nine synthetic agent
controls pass, including conflict/stale-plan refusal, header growth/scaling and
incomplete-copy handling. Actual Mac full 260-file dry run/copy verification is
pending. No C numerical changes, reduction, install, generic CMOS qualification
or automatic classification/association policy is introduced. PR #183 remains a
draft review with an explicitly authorized preparation helper; preserve M4 gates.

31 October M3 is owner accepted/closed and PR #178 merged at
6c4b0f0eff639da8dbef890f0df10f86c70bb0ee; owner-returned Mac and Chapman4
cleanup confirms clean main, merged review branch removal and protected installs
preserved. Owner instructed M4 review and inclusion of `~/Pictures/ZWO_Bath/`.
The [M4 interface/fixture review](m4-interface-fixture-review-2026-10-31.md) tracks #182:
independent detector/HDU maps, optional selectors, scaling, selection/reference
context and an astrophotography profile within existing visual-purpose vocabulary.
Returned Bath inventory samples 256/260 FITS: primary images, unsigned-16 scaling,
explicit flat-role ambiguity and 30 s dark/32 s light mismatch. Four headers remain
uninspected; no raw report/pixels independently audited. This is documentation and
source review, not M4 C implementation, reduction, profile activation or generic
CMOS acceptance. Review interfaces/fixtures before code; preserve original gates,
Pycavi grouping ownership, all evidence and installed environments. Earlier pending
M3 receipts below retain their historical scope.

31 October [summary/alignment paired receipt](m3-summary-paired-results-2026-10-31.md): source
fc4b26cd1a1eed828a88d818fcdbb7912a2acbe2 passed 24/24 on selected Intel Mac
(6.938 s) and representative Chapman4 (3.563 s), with installed files and clean
main preserved. Direct real --summary displays five aligned CN Ori exposure rows,
retaining warnings and the missing historical flat reference without a wrapper.
The owner-requested interface addition is qualified; M3 closure is recommended
for owner acceptance, then separately instructed merge/cleanup and M4 review.
Documentation-only receipt: no executable change, test replay, install or host sync.
Earlier pending/held notes retain their stated historical scopes.

31 October owner requested [direct --summary output and aligned titles](m3-inspector-summary-2026-10-31.md)
before M3 closure. Compact exposure rows/diagnostic counts now need no wrapper;
detailed tables also use measured spaces. Agent suite passes 24/24; actual Mac,
then representative Chapman presentation qualification remains pending. Prior
22-group reader and real-tree evidence stay valid; no reader/C/scientific change.
PR #178 stays draft for the added interface gate. No installation or activation;
owner acceptance/merge-clean precedes M4 review.

31 October #180 [corrected paired and real-tree receipt](m3-eso-header-paired-results-2026-10-31.md): source
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
The [bounded correction](m3-eso-header-inspection-2026-10-31.md) retains diagnostics and readable fields,
with no fixes to source files or image reads. New regression fails before; agent
corrected suite passes 22/22. Corrected Mac/Chapman qualification and repeated
bounded Chapman tree display remain pending. Hold the earlier M3 closure
recommendation and PR #178 in draft; preserve all earlier evidence. No native,
scientific, installation or M4 work. Earlier 21-group receipts retain their scope.

31 October M3 inspector [paired qualification](m3-inspector-stages-paired-results-2026-10-31.md): exact source
0d8f2978a4ef4c78c47f1526b48e03d77351c024 passed all 21 groups on selected Intel
Mac (4.639 s) and representative Chapman4 (2.702 s), with installed module,
configured engine/configuration and clean main 3a61df6 preserved. The
[final original-scope M3 review](m3-final-closure-review-2026-10-31.md) recommends milestone closure: the
inspector gap is resolved alongside accepted native paths. Owner acceptance and
separate merge/cleanup remain pending; then review M4 detector/layout interfaces.
This receipt is documentation only: no test replay, installation or host sync.
Earlier pending/gap notes retain their historical source/evidence contexts.

31 October owner authorized completing the remaining original M3 inspector work.
[Stage-view candidate](m3-inspector-stages-2026-10-31.md) adds evidence-linked calibration/preprocessing/
normalization/WCS views and shared pure client conventions. Agent final 21/21
checks pass; initial test-only oracle #179 failure is preserved. Selected Mac,
then representative Chapman 21-group qualification remains pending; #159/M3 and
#179 stay open. No C code, numerical tuning, installation or normal activation.
Use exact private exports and protected-host runner; no historical matrix replay.
Cumulative closure precedes M4 implementation; merge/cleanup needs owner acceptance.

31 October cumulative review at accepted main 3a61df6: [original M3 checklist](m3-cumulative-review-2026-10-31.md)
retains #159/M3 open. Native explicit paths have paired acceptance; the original
associated-calibration/preprocessing/normalization/WCS inspector overview remains
incomplete. Complete that bounded read-only integration before closure; no new
timing/debugging or historical test campaign is a prerequisite. [M4 readiness](m4-readiness-review-2026-10-31.md)
is preparatory review only, with no implementation or milestone advance. Preserve
ESO OB/template/exposure metadata distinctions; grouping/association belongs in
Pycavi, while mefpp processes selected lists with compatibility checks. Review
only: no native/Python code, execution, installation or merge/cleanup. Earlier
increment receipts retain their original scopes and evidence.

30 October paired native safety receipt: selected-tool Intel Mac and representative
shared Chapman4 private optimized C90 builds and all four contracts passed 4/4
at 87ed266a109741c4998bfc8c978d07c9306f0091 (32.74 s / 20.77 s). Protected
installed module/engine/configuration and clean review checkouts stayed unchanged.
[Paired results](native-safety-paired-results-2026-10-30.md) qualify the bounded #144/#171/#172/#174/#175/#176/#177
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
[Correction/evidence](native-format-prototypes-2026-10-30.md) includes existing qerror.h and makes implicit
declarations fatal for the probe. Corrected agent C90/C17/scoped ASan format
checks pass 1/1 each; production/other contracts unchanged. Actual corrected Mac
then Chapman four-test qualification remains pending; keep applicable issues
open and PR #173 draft. Use the new correction manifest, preserve the failed Mac
run and all earlier evidence. No install, automatic merge/cleanup or matrix replay.

30 October owner authorized batching reachable #74 fixes with #144 in draft
PR #173 before target handoff. [Complete format/buffer inventory](native-format-safety.md) distinguishes inherited
message/newline (#174), timestamp, conditional RTD, header-merge (#176), keyword
and filename corrections from new probe-input mistake #175. Agent final C90/C17
four-contract batches pass 4/4; scoped address/UB format/allocation/swap checks
pass 3/3. [Agent receipt](native-format-safety-agent-results-2026-10-30.md) retains failures, exact origins/hashes and limits.
Actual selected-tool Mac/representative Chapman combined four-test qualification
is pending; applicable tickets stay open. #74 also retains unqualified gnuplot/
FITS-table facilities; #125/#128 remain separate. No real OOM, broad leak, RTD
operation, numerical/scientific or installed activation claim. One combined host
handoff replaces the earlier two-test handoff; preserve all tools/installations/
evidence and separate #144 commit. No automatic merge/cleanup or matrix replay.

30 October owner authorized #144 after accepted/merged PR #170 at clean main
e2460fb72bdbe69f92c7da8994a81d21928569b5. [Bias dependency failure correction](eclipse-allocation-failures.md)
checks inherited image/cube, crop, overscan scratch and final QC allocations;
#171 separately records inherited borrowed-cube destruction/ignored status.
The shared kernel and active native overscan callers propagate failure. Agent
C90/C17 allocation/native-path CTests pass 2/2; scoped ASan/UBSan allocation suite
passes 1/1. [Agent receipt](eclipse-allocation-agent-results-2026-10-30.md) retains original failures and new test setup #172.
Actual selected-tool Mac/representative Chapman checks remain pending; keep
#144/#171/#172 open. Global qfits fatal RAM/swap policy is unchanged; no real OOM,
LeakSanitizer, complete-engine memory or scientific acceptance. Full M3/#159 and
other recorded limits remain separate. Preserve tools/installations/all evidence;
no historical matrix replay, automatic merge/cleanup or configured activation.

30 October paired qfits swap receipt: selected-tool Intel Mac and representative
shared Chapman4 optimized private C90 builds and both focused CTests passed 2/2
at 471f42e19e304e16872291172535e855a2f826d9. Protected installed files and clean
review checkouts stayed unchanged. See [paired results](qfits-swap-paired-results-2026-10-30.md).
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
[paired results](m3-native-paths-paired-results-2026-10-30.md). The actual C engine passed the native path contract
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
review checkouts stayed unchanged. See [paired results](m3-project-inspection-paired-results-2026-10-30.md).
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
correction/evidence](m3-inspection-canonical-fixtures-2026-10-30.md) resolves generated fixture identity and adds
an explicit alias regression; inspector/resolver/installed code are unchanged.
Agent reproduced all three failures and corrected 15/15 checks pass through an
aliased work-parent. Corrected Mac/Chapman verification remains pending; preserve
both target attempts. Chapman protected files passed but final checkout verification
did not run after failure. PR #161 stays draft; #159/#160/#162 remain open for their
applicable gates. No test-gate weakening, installation or automatic merge/cleanup.

30 October M2 is owner-accepted/closed after merged PR #158 and clean Mac/shared
Chapman main b872c8f44c1b54982069a3f94735da492a9dd739; owner instructed Proceed at M3.
The [first M3 increment](m3-project-inspection.md) adds explicit path-base primitives and a
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
[recommend original-scope M2 closure](m2-final-closure-review-2026-10-30.md). The #155 project/native
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
and clean review checkouts stayed unchanged. See [paired results](m2-project-composition-paired-results-2026-10-30.md).
The #155 configuration integration correction is target-qualified and ready for
owner review in PR #157. Full M2 closure remains a cumulative review/owner decision;
no M3, ASDF publication, numerical processing, installation or automatic merge.
Preserve selected tools and all evidence; this receipt needs no test replay.
Earlier target-pending notes below are historical. Separate owner instruction
precedes merge/cleanup.

30 October owner accepted/merged PR #156 and instructed merge, clean, and
proceed. At baseline ea35197a7f074ac1c44289e7bcc94336f92d6681, the next original-M2
increment implements [project/native composition](../architecture/proposed/m2/project-composition.md) for #155. Project
envelope 2 composes reusable complete domain-v1 declarations; complete version-1
projects remain supported. The shared CLI/library loader uses the qualified C
resolver for complete/split/local native references and validates readout against
resolved settings, retaining all source texts/hashes/edges and domain origins.
Project conflicts fail (empty project override allowlist); numeric overrides stay
native. Agent focused C90 checks passed 2/2, including 18 primary profiles and 24
composition rejection/recovery cases. Actual Mac/representative Chapman checks
are pending. Native C/catalogs, installed software, numerical algorithms and
milestone order are unchanged; no M3 execution or ASDF publication. See
[agent receipt](m2-project-composition-agent-results-2026-10-30.md). #155/full M2 closure remain open pending target/owner
review. Preserve accepted evidence; no historical matrix/tool replay or automatic
merge/cleanup. The earlier closure review retains its original as-is baseline.

30 October cumulative M2 review at accepted merged main
c0bbcc5866b49d64fad6498a029429b35ada9953: keep M2 open. Native configuration
resolution/equivalence, migration and provenance have accepted paired evidence,
but reusable project-domain composition is not connected to the frozen project
loader. The as-is loader still requires inline project domains and one complete
standalone native reference. [Closure review](m2-closure-review-2026-10-30.md) records the original-gate
checklist, accepted chain and [remaining M2 integration #155](https://github.com/fselman/wenu-imaging/issues/155).
Do not infer full M2 closure from native test success or start M3. No source code,
new functional run, installation or numerical processing in this review; preserve
accepted tests/tools/evidence and implement no scope reduction. Owner review and
separate integration instruction remain required for this documentation branch.

30 October paired migration receipt: selected-tool Intel Mac and representative
shared Chapman4 private C90 builds and both focused configuration CTests passed
2/2 at 38f4f4d4bd05c4977f1624fc8737431527bdbe8a. Protected files and clean review
checkouts remained unchanged. See [paired migration results](m2-migration-paired-results-2026-10-30.md). Ready for
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
this implementation. See [migration contract](../architecture/proposed/m2/configuration-migration.md) and
[agent receipt](m2-migration-agent-results-2026-10-30.md). Earlier remaining-migration notes are historical within
this implemented boundary.

30 October paired project/readout receipt: Intel Mac and representative shared
Chapman4 selected Python 3.11.14 authoring checks passed at
3769f5196f9be2c2581673f89c61ae2a472167d3: six examples from two caller directories,
66 rejection/recovery cases, immutable sources/recipe order and malformed CLI
controls. Protected installed files/checkouts stayed unchanged. See
[paired results](m2-project-contracts-paired-results-2026-10-30.md). Ready for bounded owner review; full M2 remains open.
No numerical/hardware execution or header-trust qualification is claimed. Preserve
evidence/tools; no rerun for this documentation receipt. Earlier pending-target
notes below are historical. Merge/cleanup requires owner instruction.


30 October next bounded M2 increment after accepted/merged PR #149 and clean
Mac/shared Chapman main ed949cab4f70381a1e187c7be691026c7fecf01c: owner authorized
[remaining project-domain authoring validation](../architecture/proposed/m2/project-contracts/README.md) and
[optional/amplifier-specific overscan](../architecture/proposed/overscan-readout-policy.md). Explicit omission requires no
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
[paired results](m2-typed-domains-paired-results-2026-10-30.md). Ready for bounded owner review; full M2 remains open.
Preserve evidence/tools; no rebuild for this documentation receipt. Earlier
pending-target notes below are historical. Merge/cleanup requires owner instruction.


30 October third M2 increment after accepted/merged/cleaned PR #148 and clean
Mac/shared Chapman main 7e665da170e2e1af9f96a97e9f5bc2f6ebcfeef5: owner instructed
“Proceed” with [typed native domains and sources](../architecture/proposed/m2/typed-domains-and-sources.md). Input version 3 maps
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
passed. Protected files/checkouts stayed unchanged. See [paired results](m2-toml-subsets-paired-results-2026-10-30.md).
Ready for bounded owner review; full M2 domain/unit/source/migration work remains
pending. This documentation update requires no repeated execution or installation.
Earlier target-pending notes below are historical. Merge/cleanup requires owner
instruction.


30 October next M2 increment after owner-accepted/merged PR #147 and clean
Mac/shared Chapman main 0550fb90215c636cc6b881eb67e221c24b5ed876: owner instructed
“Proceed” with [native subset composition](../architecture/proposed/m2/native-subset-composition.md). Version 2 adds containing-file
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
stayed unchanged. See [paired results](m2-native-toml-paired-results-2026-10-30.md). Ready for bounded owner review;
full M2 composition/override/unit/source/migration work remains pending. No test
replay or installation is needed for this documentation update. Earlier pending
target notes below are historical. Merge/cleanup requires owner instruction.


30 October 2026: M1 is owner-accepted and closed following merged PR #146
(`7d8da6b96b7b744a51e3847522a727e3f510c6f2`); the October 29 handoff and fresh
Mac evidence confirm clean main. M2 begins with an opt-in native TOML compatibility
reader producing the existing immutable configuration. Full domain composition,
precedence/unit/source provenance and migration remain subsequent M2 work; no
M3–M11 reordering, installation or processing. See [the M2 reader contract](../architecture/proposed/m2/native-compatibility-reader.md). Earlier pending-M1
notes below are historical. Actual Mac/shared Chapman integration checks pending.

29 October M1 closure review after accepted/merged PR #145 and clean Mac/shared Chapman main bacfa24fce45c0e7957bbc55f9cb6abfc7027219: the cumulative template/config/runtime/CLI/bindings/input/bias evidence supports proposed bounded M1 foundation closure. See [the M1 closure review](m1-closure-review-2026-10-29.md) for the requirement-by-requirement checklist, native-to-WAD conceptual/units/status crosswalk, accepted merge chain and explicit later-milestone boundaries. This is a read-only source/document/evidence review, not new execution or owner milestone acceptance. Reuse the latest paired C90 5/5 results and earlier scoped evidence; no test replay, tool qualification, installation, activation or scientific audit. #144 and wider memory limits remain open; do not claim whole-dependency OOM or thread safety. Preserve optional BPM / required M6a variances. Continue the original order at M2 after owner closure acceptance and authorized integration; other subroutines remain M5/M6, new algorithms at M6b–M6d. Do not start M2 code, merge or cleanup from this review alone.

29 October M1 first bias service ready for bounded owner review: returned Intel Mac and representative Chapman4 private C90 CMake builds (including the normal engine link) and all five focused CTests passed 5/5 at f5858310e505bfc1b137491dc35676b9245ce674. Both passed the eight-profile-per-instrument exact synthetic bias/legacy-FITS bridge contract, configuration/runtime checks, all 51 CLI cases and seventeen input cases from two directories. See [the paired bias-service receipt](m1-bias-paired-results-2026-10-29.md) for exact paths and limits. Protected files and checkouts stayed unchanged. #144 remains open; no target C17/sanitizer, whole-dependency OOM, thread-safety, scientific or complete-M1 claim. Grouped command adapters and general loader/path integration remain subsequent work; required variances stay M6a. Preserve all runs/tools/installations; no duplicate Chapman run or rebuild for this documentation receipt. Owner review precedes explicitly authorized merge/cleanup.

29 October M1 first bias service authorized after accepted PR #143 and clean Mac/shared Chapman main 98454283341a5bbce641119bed686fa56ff9c44b. The C90 mef_cal_bias service copies explicit one-detector raw ADU planes, preserves legacy overscan/trimming, rejection, median stacking and QC through a shared extracted kernel also used by mef_build_cal, and transfers an owned signal/request/QC result only on success. Explicit BPM omission is supported; selected BPM/calibrations, primary layouts and multiple detectors return unsupported. Variance is explicitly unavailable in this pre-M6a lane; required variance propagation remains M6a and new QC/RON estimators remain deferred. Agent C90/C17 and C90 ASan/UBSan exact synthetic service/legacy-FITS-bridge checks pass, as do focused configuration/runtime/51-case CLI/17-case input regressions. Actual Mac/representative Chapman C90 CMake build and five focused tests are pending; do not replay the historical matrix or requalify shared tools. #144 tracks retained Eclipse allocation-failure limitations, with no dependency OOM/thread-safety claim. The owner selected grouped commands such as mefpp cal bias, retaining mef_cal_bias for C; command adapters are subsequent M3–M6 work, not implemented here. No installation, observational reduction, automatic repair/retry, merge or cleanup.

29 October M1 explicit file/list requests ready for bounded review: returned Intel Mac and representative Chapman4 private C90 CMake builds and four focused CTests passed 4/4 at c9f974f680e72de48c6b0af24de3e1887f42a5e8. Both passed all 51 CLI cases and seventeen file/list cases from two unrelated directories, plus configuration/runtime controls. See [paired input-request receipt](m1-inputs-paired-results-2026-10-29.md) for exact paths and limits. No target C17/sanitizer, FITS geometry/applicability, applied-mask, thread-safety or full-M1 claim. Normal CLI/engine discovery and the first numerical service remain subsequent work; required variances stay M6a. Preserve all evidence/installations/tools; no duplicate Chapman test or rebuild for this documentation receipt. Owner review precedes explicit merge/cleanup.

29 October next M1 increment after accepted PR #142 / clean Mac/shared Chapman main 12f555ce4e14df0e292b629d54a3e496b94d8269: [explicit file/list request adapter](../architecture/proposed/m1/file-list-requests.md) reuses the existing Eclipse list parser with an explicit original member base and a supplied selected image catalogue. Ordered duplicate members expand to owned resolved requests; no IDs/HDU selections are invented. Selected files/calibrations must be readable regular files; omitted BPM triggers no lookup. Agent C90/C17 and C90 ASan/UBSan pass 17 cases from two unrelated directories, original-reader comparison and allocation/partial-I/O-failure controls. Actual Mac/representative Chapman CMake build and four focused tests remain pending. Normal CLI/engine discovery, FITS geometry validation, numerical services and M1 completion remain subsequent work; M3/M4 general resolver/layout scope is not claimed. Required variances stay at M6a. Preserve selected tools/evidence/installs; no repeat qualification, processing, automatic merge or cleanup.

29 October M1 resolved calibration/BPM bindings ready for bounded review: returned Intel Mac and representative Chapman4 private C90 CMake builds and all three focused tests passed 3/3, including all 51 CLI cases each, at b3c5948b6c729f396c3f87d441e5da8978b21358. See [paired bindings receipt](m1-bindings-paired-results-2026-10-29.md) for actual paths and limits. The runtime suite includes resolved role/BPM construction, rejection and ownership controls. No target C17/sanitizer, file applicability, applied masks, numerical processing or complete-M1 claim. Required variance support remains M6a. Preserve all runs/tools/installations; no duplicate Chapman execution or rebuild for this receipt. Owner review precedes authorized merge/cleanup; CLI/list integration and a concrete operation remain subsequent work.

29 October next M1 increment after accepted PR #141 / clean Mac/shared Chapman main 30ebe2a148021b2719bb8c5972b678150e86489c: [resolved calibration roles/BPM choices](../architecture/proposed/m1/resolved-calibration-bindings.md) adds an opt-in typed descriptor constructor and preserves its owned role/selection metadata through context cloning. Every input detector explicitly selects or omits BPM; contradictory metadata fails. Agent C90/C17 and C90 ASan/UBSan lifecycle controls pass, including 164 new allocation positions per profile; the 51-case C90 CLI regression also passes. Actual Mac/representative Chapman CMake checks remain pending. This is metadata validation, not file availability/dimensions, applied-mask status, CLI/list resolution or numerical execution; old engine BPM discovery is unchanged. Variances stay required at M6a, not implemented here. M1 remains incomplete; preserve selected tools, all prior evidence and user installations. No repeat tool qualification, processing, automatic merge or cleanup.

29 October owner addition after accepted/merged PR #140 and clean Mac/shared Chapman main 6a4d4d8ec078a3360a5a743845dcbe752cbc84bd: [optional BPM / required variance policy](../architecture/proposed/bpm-variance-policy.md) applies throughout the target chain. Explicitly omitted input BPM permits processing; selected missing/unreadable/incompatible BPM fails, with no fallback or default rediscovery. BPM creation still requires its requested BPM output; generated validity/rejection masks remain distinct. Variances stay at M6a and become required for supported signal/calibration products in the new variance-capable chain; remove its normal variance-off mode. Model-based raw variance initialization is permitted under an explicit qualified contract, not silent omission. Pre-M6a legacy products remain explicitly variance-unavailable. This delivery records policy/source boundaries only, not implemented no-BPM or variance processing. Carry it into the next M1 resolved-operation/concrete-service increment and subsequent notebooks; no installation, processing, repeat tool qualification, merge or cleanup from this update.

29 October M1 CLI capture ready for bounded review: returned Intel Mac and representative Chapman4 private C90 CMake builds and all three focused CTests passed 3/3, including 51 CLI cases each, at 3423aadb15ef6c6b4a48183ae05d4eab8d65673f. See [paired CLI receipt](m1-cli-paired-results-2026-10-29.md). #139 diagnostic bounds correction now has agent sanitizer and actual target verification; retain the original failed sanitizer evidence. #133 remains unchanged. No target C17/sanitizer, processing, installation or complete-M1 claim. Preserve selected tools and all evidence; no duplicate Chapman runs or rebuild for this documentation receipt. Owner review precedes merge/cleanup; resolved-operation integration and a concrete operation remain subsequent M1 work.

29 October M1 CLI compatibility increment authorized after PR #138 acceptance and clean main a58291a1f980fa1563ef89b49e01de4e4d47796c: [legacy CLI capture](../architecture/proposed/m1/cli-compatibility.md) preserves actual-loader bindings, save flags, original argv and effective settings without a second parser or fabricated single-operation/image identities. Agent C90/C17 and post-correction ASan/UBSan pass 51 cases, including twelve retained pilot forms and allocation/lifetime controls. The initial sanitizer run found legacy -d CCD[-1] in mef_bb_dump (#139); the correction is diagnostic bounds only, with original failure retained and target checks pending. #133 --ksize remains unchanged. No normal engine/decoder math, installation, FITS processing, notebook or QC change; M1 remains incomplete and target Mac/representative Chapman verification is next. Preserve all selected tools/evidence; no repeated tool qualification or automatic merge/cleanup.

29 October M1 runtime increment ready for bounded review: returned Mac and representative Chapman4 C90 CMake probe builds and both focused tests passed 2/2. See [paired runtime receipt](m1-runtime-paired-results-2026-10-29.md) for exact revisions, evidence and limits. No target C17/sanitizer or scientific-processing claim; preserve all private runs. Legacy CLI/list/save-flag/override adapters and one concrete operation remain subsequent M1 work. No duplicate Chapman/tool checks or further runs for this receipt. No merge or cleanup without owner instruction.

29 October next M1 increment authorized: owner instructed “Proceed” after PR #137 acceptance/merge and clean Mac/shared Chapman main 1d991a22a39d6133ab19721b7bb3a6dd11394264. [Owned runtime lifecycles](../architecture/proposed/m1/runtime-lifecycles.md) implement copied request descriptors, independent config/request contexts, result/error owners and explicit unsupported execution. Agent strict C90/C17, 268 transient/persistent allocation positions, ownership/independence and synthetic override controls pass; actual Mac/representative Chapman checks are pending. The normal CLI/numerical engine is untouched; legacy binding/override adapters and one concrete numerical operation remain subsequent M1 work. Preserve installed tools/evidence; no repeated shared-host tool qualification, processing, installation, merge or cleanup.

29 October M1 configuration increment ready for bounded review: returned Intel Mac and representative Chapman4 C90 CMake configure/probe builds and focused native_config_snapshot CTest passed. See [paired target receipt](m1-config-paired-results-2026-10-29.md). Both instrument maps, edge cases and ownership/failure controls pass; preserve all private builds and earlier evidence. No new processing, installation, scientific/QC behavior or complete-M1 acceptance. Request/context/result/error lifecycle and CLI-override capture remain subsequent M1 work. Chapman3/4 share one qualified tool environment; no duplicated host/tool checks. No merge or cleanup without owner instruction.

Owner-mandated tool selection, 29 October 2026: read [Selected project tools](selected-tools.md) before preparing host commands or builds. Always select the documented Mac/Chapman tools by absolute path, including CMake/CTest, compiler, Python, make/ar/ranlib and Mac SDK; do not infer availability from PATH or inherit the MPI/Mesa compiler selection. Consult the recorded private installations before proposing replacements, upgrades or manual build workarounds; never silently fall back. Chapman hosts are owner-confirmed identical and share home directories: reuse ~/opt/cmake-3.29.6/bin/{cmake,ctest} and the shared Python environment, with explicit devtoolset-10 GCC. Their CMake/CTest 3.29.6 paths/hashes are confirmed on Chapman4; system CMake 2.8.12.2 is not selected. The owner explicitly says Chapman3/4 are copycat: no further per-host tool availability/version/hash/ABI checks or duplicate qualification are needed; use the recorded tools directly. A new task's Chapman verification runs once on a representative Chapman host. Preserve global PATH/login files, production environments, external-executable configurations and accepted evidence. Use fresh task build directories and record actual execution host; shared tools do not imply every test ran on every host.

Production dependency gate, 29 October 2026: owner confirms the older Chapman machines are the main production systems. See [TOML/ASDF Chapman qualification](toml-asdf-chapman-qualification-2026-10-29.md). New parser/ASDF packages and their transitive dependencies must qualify on actual Chapman as well as Mac before adoption; Mac-only success is insufficient. Start with read-only chapman4 package/tool preflight, then a private constrained candidate, offline/interchange checks and explicit adoption evidence. Preserve working environments; no implicit NumPy/Astropy/compiler/C-standard upgrades. M0/M0a review package PR #134 is accepted/merged at b5bfd910614a786b95a598cb6295989c9f6602d6; remaining dependency/schema/effective-setting decisions are open. Development remains Mac, production qualification Chapman.

M0/M0a preparation, 29 October 2026: owner instructed "Proceed" after both hosts reached clean main 0fa9eaf157359a93f2a9196f6fff05dc3e96e220. [Contract review package](../architecture/proposed/m0-m0a/README.md) contains WAD/project sketches, 25 synthetic records, native boundary/ownership draft, source configuration ledger and focused checks. Development is on the Intel Mac; chapman4 is retained for later qualification. This increment is documentation/review fixtures only; M0/M0a contract acceptance and parser/schema/effective-setting choices remain pending, with no production/native/notebook changes, installation or reduction. CLI --ksize source finding is tracked separately as #133; do not repair it implicitly. PR #132 is already merged and both hosts were synchronized/cleaned; preserve all evidence and frozen amendments.

WAD/project direction approved for documentation, 29 October 2026: owner instructed "Proceed" after the Wenu Attribute Dictionary and ASDF processing-project proposals. See [WAD and ProcessingProject](../architecture/proposed/wad-processing-project.md), [target architecture revision 4](../architecture/proposed/pycavi-mefpp.md) and [implementation plan version 3](../architecture/proposed/implementation-plan.md). WAD defines shared data contracts; ASDF persists evolving project revisions, exact-version plans and run/product records; FITS retains pixels and TOML remains editable configuration. M0a establishes the minimal WAD/project foundation before native interfaces are finalized; M7 implements persistence and M8/M9 use the shared project service. Include the M3 inspector and M6a–M6d variance/linearity/dark/fringe scope already recorded. Concrete schemas/APIs/layout, implementation and numerical qualification remain pending; no production package, migration, installation, processing, merge or branch cleanup starts from this documentation update. Automatic cascades and parallel execution remain later passes. This supersedes earlier exploratory-only wording only for these owner-directed design elements; frozen amendments and accepted baselines remain unchanged.

Next-stage direction approved, 29 October 2026: [amendment v2.9](native-roadmap-amendment-v2.9-2026-10-29.md) authorizes analysis/design of mefpp subroutines, typed TOML configuration subsets, ASDF processing metadata referencing FITS-resident images, parallel-ready and single-detector interfaces, notebooks 01/03 and an optional mefppy Python library. See the [initial source analysis](mefpp-refactor-analysis-2026-10-29.md). TOML/ASDF-with-FITS is now the owner-selected design direction; exact schemas/adapters/bindings and directory layout remain proposals. Read-only larger Chapman inventory is pending actual-host evidence; do not assume its reductions are complete. No production implementation, installation, data migration or reduction rerun begins from this analysis. Stage 2/2.1 stay accepted; other exploratory WISDG/retrieval/layout ideas remain unadopted.

Stage 2.1 endpoint revised by owner, 29 October 2026: [immutable amendment v2.8](native-roadmap-amendment-v2.8-2026-10-29.md) makes the gate **current mefpp/Pycavi reduction through notebook 04: native calibration/science preprocessing, Python normalization, solve-field and WCS-corrected MEF assembly**. Keep one filter and at most five equal-integration-time science exposures per instrument; all three WFI partitions are authorized for the same five exposures in total. Notebook 05 extraction/SCAMP, SWarp, photometric/illumination work, downstream QC and final catalogues are outside Stage 2.1 and deferred to later workflow work. Older v2.7/full-chain completion wording is historical and superseded; do not reopen it as a closure requirement.

Both bounded instrument sets have now passed the Stage 2.1 functional endpoint on the Intel Mac: native preprocessing, Python normalization, solve-field and WCS-corrected MEFs. OCAM: five r_SDSS exposures at 20 s, one partition, 160 solved detector images. WFI: five BB#B/99_ESO842 exposures at 89.9177 s across three partitions, 40 solved detector images. Pixel/input preservation checks passed. See the [returned-result receipt](stage2-1-functional-results-2026-10-29.md) for evidence paths and limits. The owner accepted Stage 2.1 on 29 October 2026 and authorized merging PR #130 and cleaning its merged branch. Next substantive work is Stage 2A review; preserve all baseline products and evidence. Preserve the failed first WFI SCAMP attempt outside this gate; #30/#131 remain open for later production work. No scientific/Phase 3 certification or automatic Stage 2A/refactoring is claimed.

Historical Stage 2.1 addition, 28 October 2026 (endpoint superseded by v2.8): [immutable amendment v2.7](native-roadmap-amendment-v2.7-2026-10-28.md) inserts full processing of one complete OCAM dataset and one complete WFI dataset with current mefpp/Pycavi before Stage 2A. New order: accepted Stage 2 → **Stage 2.1 full current-workflow baseline** → Stage 2A review → extraction. One inventory/input/software lock, both existing complete supported reduction chains, retained outputs/QC and one baseline report; no new algorithm, format migration, automatic tuning, repeated memory matrix or duplicated platform run. Stage 2 stays accepted at 19/19 planned, 29 actual; #116 open/deferred, Phase 3 deferred. Planning only tonight; both user checkouts stay clean on main, no processing/installation/sync needed to review. Exploratory ASDF/WISDG/layout ideas are not adopted requirements.

Owner wrap-up accepted, 28 October 2026: owner instructed to leave #116 for now and finish clean for tomorrow. [Immutable v2.6](native-roadmap-amendment-v2.6-2026-10-28.md) records bounded Stage 2 acceptance with #116 OPEN/unresolved/deferred, named testing limits retained, and Phase 3 deferred outside this closure gate. [Final receipt/review](stage2-integrated-owner-review-2026-10-28.md) records all F1–F5 plus final C90 accepted: 19/19 planned + 10 retests = 29 actual, no further engine runs. Finish verified defect comments/closure, integrate PR #119 then #120, guard final-tree/host fast-forwards and remove only exact merged branches; preserve all raw data/runs/archives/builds/installations/configuration. No reinstall, new matrix/repair or automatic Stage 2A implementation. Tomorrow next topic: Stage 2A review after clean-main verification. This current instruction supersedes older pending-approval/Phase 3 closure-gate statements.

F5 accepted / final owner review ready, 28 October 2026: [F5 receipt](stage2-integrated-f5-acceptance-2026-10-28.md) independently verifies 94 files, six logs, both 391-entry source inventories, 12 exact products / 24 arrays, zero cleaned resources and stable descriptors. Fixed F1–F5 plus final Mac C90 are accepted/reused; **19/19 planned + 10 retests = 29 actual**, general rounds 2/2. No further engine runs planned. [Final owner decision](stage2-integrated-owner-review-2026-10-28.md) is complete; the later owner disposition below/above accepts bounded closure and defers Phase 3. #121–#124 meet bounded verification; comment before closure. #75/#116 remain open; #125/#128 deferred. No sync/rebuild/rerun needed for receipt, no automatic repair/new matrix/merge/deletion/installation/Stage 2A advance.

F5 prepared, 28 October 2026: actual Chapman preflight confirms clean main b0061b5 and qualified GCC10.2.1/CMake3.29.6/Python environment. [Final compact paired runner](stage2-integrated-f5-preparation-2026-10-28.md) prepares explicit C17/C90 builds and exactly one unchanged tiny integrated workflow per mode, pinned exact Mac products/metadata plus owner/accounting/descriptors. Python real-log/fixture/guard controls pass; target native execution pending, no native C/header changes or agent recipe launches. Current 17 planned + 10 retests = 27 actual; maximum after F5 19/19 and 29 actual, general rounds 2/2. One-use, stop at first finding; no extra matrix, external target diagnostics, automatic repair/retry, installation, merge or deletion. Then final owner/Phase 3 gap review; #116 unresolved, #125/#128 deferred.

Final Mac C90 accepted, 28 October 2026: [compile/link receipt](stage2-final-c90-mac-acceptance-2026-10-28.md) verifies six archive files, actual -std=c90 / AppleClang 15 / Darwin x86_64, successful final link and independently reconstructed 389-input source inventory. 66 retained warnings, no new warning messages versus prior C90; no warning-free claim. Binary stays Mac with host-verified hash. No native execution/installation; counts remain 17 planned + 10 retests = 27 actual, general rounds 2/2. Next compact Chapman3 C17/C90 pair and owner/Phase 3 gap review. Obtain actual Chapman host/Git state before its checkout mutation. Docs-only receipt needs no Mac sync/rebuild. No automatic repair/new matrix/merge/deletion/installation; #116 unresolved, #125/#128 deferred, #121–#124 await final disposition.

F4 accepted, 28 October 2026: [independent receipt](stage2-integrated-f4-acceptance-2026-10-28.md) verifies all 421 files, eleven same-process cycles, 66 exact products / 132 detector arrays, balanced owners, zero start/double-purge resources and stable descriptors. Current 17 planned + 10 retests = 27 actual; general rounds 2/2. Native source remains 68f0a04 (harness b93ffda). Next one final Mac C90 build without processing, paired compact Chapman3 C17/C90, then owner/Phase 3 gap review. Docs-only receipt needs no host sync/rerun; no automatic repair, new matrix, installation, merge or deletion. #116 unresolved; #125/#128 deferred; #121–#124 await final checkpoint. Earlier F4-pending statements are historical.

F3 accepted / F4 prepared, 28 October 2026: [independent F3 receipt](stage2-integrated-f3-acceptance-2026-10-28.md) verifies all 539 files, 35 logs, six builds, ten final failure roles and two exact tiny smokes; both historical failures remain preserved. #127/#129 meet bounded acceptance; #121–#124 await final checkpoint, #125/#128 deferred, #116 unresolved. Current 16 planned + 10 retests = 26 actual, general rounds 2/2. [Fixed F4](stage2-integrated-f4-preparation-2026-10-28.md) is prepared with Python guards/parser/fixture controls passed, actual Mac execution pending: reuse the qualified 68f0a04 instrumented binary for one warmup plus ten cycles in one process / one original planned launch. Native source unchanged; no rebuild, automatic repair/retry, new matrix, installation, merge or deletion. Then final Mac C90 build, paired compact Chapman3 C17/C90 and owner/Phase 3 gap review. Older pending/blocker paragraphs below are historical where superseded.

Approved cube exception v2.5, 28 October 2026: Fernando responded "authorized" to the two-C-file/two-added-retest proposal for #129. See [immutable amendment](native-roadmap-amendment-v2.5-2026-10-28.md) and [prepared repair/resume](stage2-integrated-cube-repair-2026-10-28.md). Cube constructor NULL/partial-owner guards and loaded-image cleanup are prepared; no header/recipe/qfits changes. C90/C17 syntax/actual constructor-loader controls and Python guards pass; Mac verification pending. One-use cube retry, exact successful tiny smoke, then the one original unrun cube leak role only if both pass. Current 23 actual; maximum after F3 26, general rounds stay 2/2. Preserve all evidence; no automatic repair/retry, new matrix, merge/deletion or installation.

F3 cube blocker, 28 October 2026: [#129 bounded decision](stage2-integrated-f3-cube-blocker-2026-10-28.md) records UBSan NULL member access after the declared cube injection at actual Mac source 2e3969c. Publication retry/smoke/leaks and both context-allocation lanes reportedly pass; full F3 archives pending. Current 15 planned + 8 retests = 23 actual, general rounds 2/2, v2.4 consumed. Proposed two-C-file NULL/partial-owner cleanup and two added retests require new explicit approval; no change/retry or later-row execution authorized. F1/F2 preserved; #125/#128 deferred, #127 awaits receipt, #116 unresolved.

Approved publication exception v2.4, 28 October 2026: Fernando instructed "Proceed" after the three-file/two-retest proposal and header clarification. See [immutable amendment](native-roadmap-amendment-v2.4-2026-10-28.md) and [prepared repair/resume](stage2-integrated-publication-repair-2026-10-28.md). #127 helper status/cleanup propagation is prepared in mefp_lib.c/.h and mefpp.c; qfits unchanged. C90/C17 syntax/helper units and Python guards pass; actual Mac acceptance pending. Exactly two added retests then five original unrun F3 roles only on success, one-use directory, no automatic retry/other repair. Current 17 actual launches; maximum 24 after F3; general rounds stay 2/2. #125/#128 deferred; no merge/deletion/installation.

F3 blocked, 28 October 2026: [publication-status defect #127](stage2-integrated-f3-publication-blocker-2026-10-28.md) confirmed by actual Mac terminal/read-only evidence at c722310: the master-bias target stays a protected directory, five other products are written, native exit is 0. Missing-list/corrupt-frame pass both lanes (user-reported); full F3 archive pending. Counts 11 planned + 6 retests = 17 actual, 2/2 general rounds; stop dependent work. Three-file publication-status repair and two added retests are proposals only, requiring owner approval/new amendment. No native modification, retry, later-row advance, merge/deletion or installation; preserve F1/F2.

F3 prepared, 28 October 2026: owner instructed "proceed" for the [five fixed failure cases](stage2-integrated-f3-preparation-2026-10-28.md). Test-only scoped context/cube NULL injection lives exclusively in private exports; no production/qfits changes. Python result/injection controls, actual archived-log parser controls and private C90/C17 syntax pass; Mac execution pending, current counters 6 planned + 6 retests = 12 actual, 2/2 general rounds. One-use F3 runner permits at most ten cases and stops on first finding. Preserve accepted F1/F2; no retry, repair, new matrix, merge, deletion or installation.

Integrated F1/F2 accepted, 28 October 2026: [inspected receipt](stage2-integrated-f1-f2-acceptance-2026-10-28.md) verifies archive 0ee502ce, all 416 files and 52 logs. F1 exact archived products and all four diagnostic logs pass; WFI host-verified reports agree exactly across three lanes (large WFI FITS remain on Mac). Both purges have zero resources, descriptors stable, external leaks zero. Counters 6 planned + 6 retests = 12 actual, 2/2 general rounds. #126 meets bounded acceptance; #125 stays deferred, #121–#124 await final checkpoint disposition, #116 unresolved. Next fixed row F3; F4/final C90/compact Chapman3 C17+C90 remain pending. Docs-only receipt needs no host sync/rerun; no merge/deletion/installation.

F2 continuation prepared, 28 October 2026: [one-use handoff](stage2-bpm-filename-resume-2026-10-28.md) validates the approved BPM filename correction without replaying passed F1. One ordinary retry then the two originally unrun diagnostic lanes; old F1 evidence is reverified and explicitly inherited. Python guards pass; Mac runtime remains pending. Current 9 actual launches; maximum 12 after these three cases. Keep general repair rounds 2/2, all gates/preservation active, #125 deferred and #126 open.

Approved BPM filename correction, 28 October 2026: [v2.3 amendment](native-roadmap-amendment-v2.3-2026-10-28.md) records Fernando's explicit caller-side correction in mefp_lib.c; fits_h.c remains unchanged. Immediate #126 and deferred qfits CONTINUE/safety #125 stay open. Agent C90/C17 syntax and basename controls pass; actual Mac retry is pending. User reports F1 all three lanes passed, F2 SIGILL; 4 planned + 5 retests = 9 launches, general repair count 2/2, v2.2 consumed. Preserve evidence; no old F1 resume, new matrix, merge, deletion or installation.

Approved bias-QC exception v2.2, 28 October 2026: Fernando instructed "proceed" for the four missing bias-QC releases in mef_bb_del and two tiny validations, followed by the original unrun campaign only if both pass. See [immutable amendment v2.2](native-roadmap-amendment-v2.2-2026-10-28.md). Keep the general repair count at 2/2; record the exception separately and permit it only once. No changed calculations, expectations, thresholds, further native correction, new matrix, merge or deletion. C90/C17 syntax and Python guard controls pass; actual Mac zero-resource verification is pending.

Integrated F1 memory finding, 28 October 2026: archive bd27d7c6 and all 141 file identities verify. Both corrected ordinary/instrumented products are exact and mutually equal, ownership/descriptors pass; 5847 allocations / 204017 bytes remain after both purges. Source-confirmed header, flat-scratch and per-extension metadata owners are tracked as #122–#124. Their lifetime-only correction and same-campaign final round 2 resume are prepared; actual corrected memory verification remains pending. Current counts: 2 planned launches, 1 correction retry, 3 actual launches, 1 round consumed. No third round, new matrix, changed expectations, merge/deletion or installation. See [final correction record](stage2-integrated-memory-correction-2026-10-28.md).

F1 integrated finding, 28 October 2026: the first ordinary Mac C17 run at fa2e5c2 returned 0 but failed exact known answers. Source tracing attributes the measured 1.111110687 bias offset to the rejected-mean overscan loop skipping one retained sample (#121). The one-line documented-mean correction and guarded same-campaign retry are prepared; actual corrected Mac verification is pending. One planned launch is consumed; global correction round 1/2 is prepared, with no retest executed. Expected arrays, exact gates, original failed evidence, installations and frozen contract bytes remain unchanged. See [bounded correction](stage2-integrated-overscan-correction-2026-10-28.md). No merge/deletion or new test matrix.

Integrated campaign preparation, 28 October 2026: the eleven-file WFI input-lock report is inspected and accepted for the bounded regression. The test-only existing-engine observer and Mac C17 F1/F2 runner are prepared; Python product-reader controls and C90/C17 syntax checks pass, actual native execution remains pending at 0/19 launches and 0/2 global correction rounds. See [integrated runner record](stage2-integrated-runner-2026-10-28.md). Preserve the single campaign pointer, all inputs/evidence/installations, frozen contract bytes and unresolved #116; no automatic retries, merge or branch deletion. F3–F5 remain the existing pending rows.

Frozen roadmap accepted, 28 October 2026: Fernando instructed "proceed" after reviewing v2.0 and requesting amendment v2.1 (paired final Chapman3 C17/C90 regression). The [accepted execution record](native-roadmap-v2-acceptance-2026-10-28.md) activates the frozen contract plus amendment; earlier proposal/pending-acceptance statements are historical. Begin one read-only WFI inventory and one integrated-fixture/harness preparation pass, then the fixed F1–F5 campaign: Mac C17 diagnostics, one final C90 build, paired compact Chapman3 closure, at most 19 planned native launches and two global correction/retest rounds. No new BPM-only matrix, automatic scope expansion, processing before input/reference lock, merge or branch deletion is authorized. Keep the frozen files byte-identical, all prior evidence and installations preserved, and #116 explicitly open pending its final-review disposition.

Owner-requested frozen-roadmap amendment v2.1, 28 October 2026: Fernando explicitly requested a compact final Chapman3 C90 regression together with C17. See [immutable amendment v2.1](native-roadmap-amendment-v2.1-2026-10-28.md). F5 now contains two compact target launches, one per mode; the campaign cap is 19 planned native launches. The original frozen v2.0 file/checksum, one-day preparation checkpoint, two global correction-round limit and all other scope/stopping rules remain unchanged. No build or processing starts from this documentation update.

Frozen simplification proposal requested, 28 October 2026: Fernando requested an immutable, finite roadmap instead of successive BPM matrices. Review [frozen native roadmap v2.0](native-roadmap-frozen-v2.0-2026-10-28.md) and its separate [fixed-row progress ledger](native-roadmap-v2-progress.md). It consolidates calibration/science collection through the existing engine, makes Mac C17 the diagnostic lane, retains one final C90 compatibility build, limits Chapman3 to one compact C17 regression, and caps the declared Stage 2 campaign at 18 planned launches plus at most two scoped correction rounds. Target external diagnostics and #116 remain honestly recorded; no implicit finding closure. The concrete proposal requires owner acceptance before execution; no new workload, merge or deletion starts from publication. Once published, never edit the frozen contract in place: amendments need explicit agreement and a new numbered file. This supersedes neither accepted evidence nor the old rules until that acceptance. Documentation review occurs on GitHub with both user hosts remaining on clean main; no diagnostic reruns or host synchronization are needed to review this document.

Integration authorized, 28 October 2026: Fernando explicitly instructed "merge and clean" for PR #117 after both actual Mac and Chapman3 checkouts were verified clean at 295fbe6844895bd4301ee51befdeb432d3ab8b90. Integrate the accepted two-extension test/evidence increment, synchronize both hosts to merged main by guarded fast-forward, and remove only test/stage2-bpm-wfi-multiext after verifying merge ancestry, exact branch tip and retained evidence. Preserve every run/archive/supplement/transfer/raw WFI or linearity frame/installation. #75/full S2-05, unresolved #116, remaining coverage and compatible target external diagnostics stay open; no S2-06 advance. This supersedes older no-merge/deletion-authorization statements only for PR #117 and this branch.

Current S2-05 two-extension target acceptance, 28 October 2026: [complete Chapman3 evidence inspected](stage2-bpm-multiext-chapman3-acceptance-2026-10-28.md) at 355034606cd6015b9e9abc99744973bf4c081b00. All 911 archive file identities plus manifest and all 39 command logs verify. Sixteen pairs / 32 roles exactly match accepted Mac masks/canonical headers; all 37 Mac-qualified source identities remain unchanged. C90/C17 GCC10.2.1/CMake3.29.6 builds, 192 allocator boundaries, 48 stable descriptor boundaries and zero double-purge resources pass. This accepts only the two-extension synthetic functional/accounting slice; compatible target external diagnostics, full S2-05/#75, unresolved #116 and remaining ownership/error/repeat/cache/mmap/swap gates stay open. Preserve every run/archive/transfer/raw WFI or linearity frame/installation. No S2-06 advance, merge or branch deletion authorized. Raw WFI inventory at /Users/fselman/Pictures/WFI remains pending.

Current S2-05 two-extension Mac acceptance, 28 October 2026: [full Mac evidence inspected](stage2-bpm-multiext-mac-acceptance-2026-10-28.md) at cea3e927f0392d8ec6c97cd40afbac2878aca03f. Both archives verify (1,259 original identities plus four recovered build logs); all 32 pairs / 64 roles preserve exact parent/mirrored masks and ordered metadata. All 79 command logs, four build inventories, 384 allocator and 96 descriptor boundaries and 16 zero-leak summaries verify. The unchanged-native-driver Chapman3 16-pair functional/accounting runner is prepared, not executed. #116 and full S2-05/#75, remaining ownership/error/repeat/cache/mmap/swap and compatible target external diagnostic gates remain open. Preserve all runs, archives, raw WFI/linearity data and installations; no S2-06 advance, merge or branch deletion authorized. Raw WFI inventory at /Users/fselman/Pictures/WFI remains pending.

Current S2-05 continuation, 28 October 2026: Fernando instructed "proceed" after supplied-bias integration at main 664f501fe723a924b6a2395d00f70cba1fb03ab7. Prepare test-only two-extension OmegaCAM/WFI BPM ownership qualification, Mac first, retaining exact accepted mask transforms, metadata, 0.5–1.5 thresholds, per-fd and double-purge gates. No production changes, new algorithms, observational reductions or installations. #116 remains unresolved/open; full S2-05/#75 and target external diagnostics remain open. No S2-06 advance or authorization to merge/delete this new branch. See [the bounded plan](stage2-bpm-wfi-multiext-2026-10-28.md).

Integration authorized, 28 October 2026: Fernando explicitly instructed "merge, sync, and clean" for PR #115 after inspecting Mac and Chapman3 supplied-bias evidence. Integrate the reviewed test/documentation increment, synchronize both hosts by guarded fast-forward, and remove only test/stage2-bpm-supplied-bias after verifying main ancestry and retained evidence. Preserve every run, archive, transfer copy, raw frame and installation. #116, full S2-05/#75, target external diagnostics and remaining coverage stay open; no S2-06 advance. This supersedes earlier no-merge/deletion-authorization statements for this branch only.

Current S2-05 supplied-bias acceptance, 28 October 2026: [Chapman3 full evidence inspected](stage2-bpm-bias-chapman3-acceptance-2026-10-28.md) at 10b3ca8285f886694fd0aa54197b8ba46f9cd1e4. All 225 file identities plus manifest verify; eight target pairs / 16 roles exactly match accepted Mac masks/canonical headers and inputs. Both C90/C17 builds, 23 command logs, owners, 24 post-call descriptor boundaries and double-purge zero-resource states pass. This accepts only the agreed supplied-bias target functional/accounting slice. #116 remains unresolved/open under Fernando's explicit sequencing agreement; full S2-05/#75, WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics remain open. Preserve all runs, archives, transfer copies and installations; no S2-06 advance or merge/deletion authorized.

Agreed #116 disposition, 28 October 2026: Fernando explicitly agreed to [bounded Chapman3 supplied-bias verification](stage2-bpm-bias-chapman3-plan-2026-10-28.md) before original descriptor-cause attribution. Keep #116 OPEN as unresolved/non-reproduced; stop further Mac repetition. Authorize only eight unchanged-driver/fixture C90/C17 target functional/accounting pairs with all current product, owner, descriptor and resource gates active. No gate weakening, compatible-target external diagnostic waiver, full S2-05/#75 closure or S2-06 advance. Stop on any recurrence and retain exact per-fd evidence. Record this agreement before preparing the target runner; preserve all original/diagnostic/repeat runs, transfers and installations. This supersedes earlier no-target-advance statements only for this explicit increment.

Current #116 diagnostic preparation, 28 October 2026: [ten focused fresh-process attempts prepared](stage2-bpm-bias-focused-repeat-2026-10-28.md) using the exact inspected c4912390 C90 instrumented binary and deterministic retained/robust supplied-bias inputs. No build, install, native driver, fixture, production source or gate changes. Python controls and readback of 16 retained logs pass; actual focused Mac execution is pending. Each attempt keeps exact product/resource/descriptor checks and fresh retained provenance. This is not S2-09 or new full-suite acceptance; nonreproduction does not waive #116. All original/diagnostic evidence and installations remain preserved; S2-05/#75, target advance and broader gates stay open.

Current S2-05 evidence inspection, 28 October 2026: [both supplied-bias Mac archives inspected](stage2-bpm-bias-mac-inspection-2026-10-28.md), SHA256 dbe6ba94, all 823 file identities plus manifest verified. All 64 native role products match accepted masks/canonical metadata and each other across the two runs; 94 command logs and 16 zero-leak summaries verified. Diagnostic c4912390 run passes all 16 pairs and 48 post-call descriptor boundaries. Original e7e8fbdc run retains one same-count descriptor identity mismatch with no per-fd attribution; #116 is still unresolved and not waived. This is successful rerun evidence, not full S2-05/#75 acceptance or permission for target/S2-06 advance. Preserve all original/diagnostic runs, transfer archive and installations; mandatory review before Stage 2A/extraction remains.

Current S2-05 finding, 28 October 2026: [supplied-bias descriptor diagnostic](stage2-bpm-bias-descriptor-diagnostic-2026-10-28.md) for #116 follows the retained Mac run at e7e8fbdc: all 16 functional pairs reported passed, one C90 instrumented resource case failed with count 4 to 4 but changed descriptor identity. Tracked resources reach zero after both purges in the inspected case; cause remains unresolved. Test-only per-descriptor detail/parser preparation preserves the existing gate, production sources, fixtures and prior evidence. Parser and C90/C17 syntax checks pass; actual Mac diagnostic rerun remains pending, followed by evidence review before target verification. Preserve the failed run and all installations; full S2-05/#75 and target diagnostics stay open, no weaker gate or S2-06 advance.

Current S2-05 continuation, 28 October 2026: [supplied-bias BPM ownership gate prepared](stage2-bpm-supplied-bias-2026-10-28.md) from synchronized main bf1c6afe0063ae62833efd04a9109ae5a3982cef after merged PR #114. Separate synthetic driver/observer and additive float32 fixtures preserve production source and accepted exact masks/metadata; Python-only preparation checks pass, actual Mac execution pending. Retain failed/corrected preparation and every earlier run/archive/installation. Chapman3 workloads remain paused pending host/hardware status from the latest handoff. Full S2-05/#75, WFI/multiple extensions and applicable error/repeat/cache/target external diagnostic gates stay open. No departure, S2-06 advance, merge or branch deletion approved; mandatory review before Stage 2A/extraction remains. Earlier PR #114 pending statements are historical.


Current S2-05 metadata integration, 27 October 2026: Fernando authorized merging PR #114 and cleaning only its merged test/stage2-bpm-metadata branch after verifying main ancestry/evidence. The [inspected Mac/Chapman3 populated-metadata acceptance](stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md) retains 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs with exact masks/headers, unchanged payloads and zero double-purge resources. Full S2-05/#75, supplied bias/WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics stay open. Preserve all runs, archives, transfer copies and installations. No departure, weaker gate or S2-06 advance approved; mandatory review before Stage 2A/extraction remains. This supersedes older PR #114 integration-pending/no-merge-authorization statements.


Current S2-05 populated-metadata acceptance, 27 October 2026: [Mac and Chapman3 evidence inspected](stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md). All 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs preserve exact masks, first-frame metadata and ordered canonical headers; 203 target archive identities verified, image payloads unchanged. Owners/descriptors and both zero-purge states pass. PR #114 awaits review/integration; no merge/deletion authorized. Full S2-05/#75, supplied bias/WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics remain open. Preserve all runs/archives/installations; no departure, weaker gate or S2-06 advance is approved. Mandatory review before Stage 2A/extraction remains. This supersedes older populated-metadata target-pending statements.


Current S2-05 populated-metadata Mac acceptance, 27 October 2026: [actual evidence inspected](stage2-bpm-metadata-mac-acceptance-2026-10-27.md) at c6a7a2bf05f8962cd9db4d72989b420f10159406. All 16 pairs / 32 native roles preserve exact reference masks, declared first-frame metadata and ordered/unaffected header cards; 372 archive identities verified, staged image payloads unchanged. Ownership/descriptors, both zero-purge states, ASan/UBSan and eight leak summaries pass. Unchanged native-driver Chapman3 C90/C17 functional/accounting runner is prepared, not executed. Full S2-05/#75, supplied bias/WFI/multiple extensions and applicable shared-helper/error/repeat/cache/target external diagnostic gates remain open. Preserve all evidence/installations; no merge/deletion, departure or S2-06 advance approved. Mandatory review before Stage 2A/extraction remains. This supersedes older metadata-Mac-pending statements.


Current S2-05 continuation, 27 October 2026: [populated FITS metadata gate prepared](stage2-bpm-metadata-2026-10-27.md) from main f377642ebfd8a8c0a43a99007f5543af34ff9c54. Deterministic header-only derivatives preserve accepted image bytes; unchanged native driver/observer and production .c/.h sources. Declare first-frame metadata, ordered comments/unaffected cards, exact masks and ownership/descriptor/double-purge contracts for 16 Mac C90/C17 instrumented/leaks pairs. Agent Python-only fixture/oracle checks pass; actual native Mac/target execution remains pending. Broader S2-05/#75, supplied bias/WFI/multiple extensions and applicable error/repeat/cache/target external diagnostics remain open. Preserve all evidence/installations; no departure, merge/deletion or advance to S2-06 approved. Mandatory review before Stage 2A/extraction remains.


Current S2-05 integration, 27 October 2026: Fernando authorized merge and merged-branch cleanup of PR #108 baseline and PR #113 ownership correction. The [inspected acceptance evidence](stage2-bpm-chapman3-acceptance-2026-10-27.md) preserves exact masks/headers for 16 Mac diagnostic/leaks pairs and 8 Chapman3 functional/accounting pairs, balanced owners/descriptors and zero double-purge resource state. Corrections #109–#112 meet their bounded acceptance criteria and are resolved with integration; broader #75/S2 and full S2-05, compatible target external diagnostics and remaining metadata/WFI/bias/multiextension/shared-helper/error/repeat/cache coverage remain open. Preserve all unique baseline/corrected/target runs, archives, transfer copies and installations. Only the two merged branches may be removed after verifying main ancestry/evidence. No scope departure or advance to S2-06 is approved; mandatory review before Stage 2A/extraction remains. This supersedes older integration-pending/no-merge-authorization statements.


Current S2-05 bounded acceptance, 27 October 2026: [Mac and Chapman3 BPM evidence inspected](stage2-bpm-chapman3-acceptance-2026-10-27.md): 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs preserve exact reference masks and canonical headers; ownership/descriptors and both zero-purge states pass. All 200 target archive identities verified, all evidence/installations retained. Corrections #109–#112 await review/integration in PR stack #108/#113; no merge/deletion authorized. Compatible target external diagnostics and broader successful/error/repeat/cache coverage remain open; this first OmegaCAM/bias=NULL/single-extension subset does not complete S2-05 or #75/S2 or authorize advancing to S2-06. No departure is approved; prior agreement and mandatory review before Stage 2A/extraction remain. This supersedes older target-pending statements.


Current S2-05 Mac acceptance, 27 October 2026: [corrected BPM evidence inspected](stage2-bpm-mac-acceptance-2026-10-27.md) at 21ea905ff90d94a29cbe174c69674afef5d487eb: all 16 pairs preserve exact baseline/reference masks and headers; both purge boundaries reach zero, ownership/descriptors and ASan/UBSan/eight leaks summaries pass. All 369 archive identities verified. Unchanged-driver Chapman3 C90/C17 functional/accounting runner is prepared, actual execution pending; compatible target external diagnostics remain open. #109–#112/#75 and broader S2-05/S2 coverage stay open. Preserve failed/corrected evidence, runs and installations; no merge/deletion or departure is authorized. Mandatory review before Stage 2A/extraction remains. This supersedes earlier corrected-Mac-pending statements.


Current S2-05 correction, 27 October 2026: [focused ownership repair prepared](stage2-bpm-ownership-correction-2026-10-27.md) for #109–#112 after the inspected 16-pair failed baseline. Release owned cube frame lists, overscan scratch arrays, default pixelmap headers and BPM publication/context metadata after last use; preserve numerical/FITS behavior and all fixtures. Native observer/oracle unchanged; corrected runner pins exact failed-baseline headers/masks as well as #90 references. Actual corrected Mac and target verification remain pending; tickets and broader #75/S2 stay open. Preserve baseline/runs/installations; no merge/deletion, departure or reduced gate is approved. Mandatory review before Stage 2A/extraction remains.


Current S2-05 finding, 27 October 2026: [Mac baseline inspected](stage2-bpm-baseline-evidence-2026-10-27.md) at e3c6b463724725b7afb601b7cc0ebe28e24e161a: all 16 original/observer pairs pass numerically, but all retain 140 RAM allocations / 4472 bytes after both purges. Source/size attribution identifies #109 cube frame-list ownership, #110 overscan double buffer, #111 default pixelmap header and #112 BPM publication/context metadata. All baseline identities and outputs are verified and retained. Focused ownership repair is prepared for fresh Mac qualification; no corrected native or target acceptance yet. Preserve installations/runs, thresholds and numerical behavior; broader #75/S2, applicable error/repeat/cache gates and target external diagnostics remain open. Departures need prior agreement; review before Stage 2A/extraction remains mandatory.


Current S2-05 increment, 27 October 2026: [BPM ownership baseline prepared](stage2-bpm-ownership-2026-10-27.md) from main 9f09a7d8a9d09c9362c390b9351c2c2d467f986c. S2-04 and the full S2/prior-agreement documentation are integrated; both user clones were clean on that main and merged branches removed. Reuse unchanged #90 driver/fixtures and exact mask references for 16 Mac original/observer pairs across C90/C17 instrumented and separate leaks lanes. Production code/numerical behavior/installations stay unchanged; actual native execution and target verification pending. Retain all evidence and any findings. This is a first bounded S2-05 subset, not complete S2 acceptance or a departure; broader #75, target external diagnostics, S2-06 and remaining gates stay open. Prior agreement is required before departures, and mandatory review still precedes Stage 2A/extraction.


Agreed S2 milestone, 27 October 2026: the [full S2-00–S2-11 table](stage2-memory-qualification-2026-10-27.md#declared-test-matrix) records current bounded status after integration of PR #105. S2-05 BPM ownership is next, followed by S2-06 calibration ownership. Departures from the agreed S2 scope, row order, required coverage or completion criteria must be agreed with Fernando in advance and recorded before implementation. This includes deferring, omitting, substituting or weakening a gate. An unavailable tool or a proposed bounded milestone does not by itself authorize a departure. No departure is approved by this documentation update. Preserve evidence/installations and the mandatory review before Stage 2A/extraction.


Current S2-04 acceptance, 27 October 2026: [Mac and Chapman3 split/cache gates verified](stage2-split-chapman3-acceptance-2026-10-27.md): Mac 80 pairs with ASan/UBSan and separate leaks, target 40 uninstrumented functional/accounting pairs with exact Mac products. Controlled purges attribute all retained states and reach zero; context/descriptor checks pass. All original failed/baseline/control/target runs, archives, transfer copy and installations stay preserved. No production cleanup policy changes. PR #105 awaits review/integration; merge/deletion is not authorized. Next after integration is the bounded S2-05/06 calibration ownership baseline. #75/Stage 2, compatible target external diagnostics, broader injection/repeat/cache/mmap/swap and conditional wrappers remain open; early Phase 3 audit and mandatory review before Stage 2A/extraction still apply. This supersedes older target-pending statements below.


Current S2-04 Mac acceptance, 27 October 2026: [split/cache evidence inspected](stage2-split-mac-acceptance-2026-10-27.md) at 5322bb952e6958a93594692fcf1e96c58fbf800d: all 80 functional pairs pass, all 64 retained RAM states are attributed by controlled cache purge, both purge boundaries reach zero and descriptor identities remain unchanged. ASan/UBSan and 40 external leak summaries are clean. The unchanged-driver Chapman3 functional/accounting runner is prepared, not executed; its external diagnostic gap remains open. No production correction/cleanup-policy change or installation occurred. Preserve all three runs/archives/installations. PR #105 stays draft, #75/Stage 2 and broader repeat/cache/mmap/swap gates remain open; early Phase 3 audit and mandatory review before Stage 2A/extraction still apply. This supersedes older cache-control-pending statements below.


Current S2-04 update, 27 October 2026: [repaired Mac observer evidence inspected](stage2-split-observed-evidence-2026-10-27.md) at 97c086aaf301e7ae782c23ec9d67de1427351a8b: 80 functional pairs and descriptor/context observations pass; 64 cache-candidate RAM states keep the resource gate failed. #106 is verified on Mac; Linux observation remains untested. A test-only controlled double-purge check is prepared, not executed; no production cleanup policy changes. Preserve both runs/archives/installations. PR #105 remains draft; #75/Stage 2, target verification, broader repeat/cache/mmap/swap, early Phase 3 audit and mandatory review before Stage 2A/extraction remain open. This supersedes older observer-rerun-pending statements below.


Current S2-04 baseline, 27 October 2026: [first Mac run inspected](stage2-split-baseline-evidence-2026-10-27.md) completed 80 pairs; all ordinary functional contracts and actual paired output sets pass, but descriptor-observer completion fails (#106). A test-only enumeration/diagnostic repair is prepared; actual rerun pending. Sixty-four five-allocation RAM states match cache-size candidates but remain visible pending controlled attribution. No production fix, memory acceptance or target verification is claimed. Preserve all evidence/runs/installations; #75/Stage 2 remains open and mandatory review before Stage 2A/extraction still applies. This supersedes earlier S2-04 unexecuted statements below.

Current Stage 2 increment, 27 October 2026: PRs #102/#104 are merged; Mac and Chapman3 are clean on main f042b38d4018af28e04e20134fc8f2b375c489e4 and merged branches are removed. S2-03/#103 is verified. [S2-04 split I/O/publication ownership](stage2-split-ownership-2026-10-27.md) is prepared, not executed: retained synthetic output/failure checks plus context, allocator/mapping and descriptor observations, Mac first. Preserve all baseline/corrected evidence, runs and installations. #75, remaining Stage 2 gates and target compatible external diagnostics stay open; the early Phase 3 audit and mandatory review before Stage 2A/extraction remain pending. This supersedes older pending-integration statements below.

Current S2-03 acceptance, 27 October 2026: [bounded CLI/parser correction #103 verified](stage2-cli-chapman3-acceptance-2026-10-27.md) on Mac C90/C17 (224 CLI pairs/52 parser checks) and Chapman3 C90/C17 (112 pairs/26 checks, functional/accounting only). Failed baseline, stopped assertion attempt and corrected evidence are retained and inspected. PRs #102/#104 await integration; installations/runs stay preserved. Broader #75/Stage 2 and compatible target external diagnostics remain open. Next after integration is S2-04 split I/O/publication ownership; the early Phase 3 audit and mandatory review before Stage 2A/extraction remain pending. This supersedes older S2-03 target-pending statements below.

Current S2-03 Mac acceptance, 27 October 2026: [the corrected parser/CLI gate](stage2-cli-mac-acceptance-2026-10-27.md) passed all 224 CLI pairs and 52 focused parser checks at 18a196224ba436ae6d68d43b40c25245bbbf50d3. All 930 corrected/stopped-attempt archive identities were verified; failed baseline and stopped assertion attempt stay retained. The unchanged-driver Chapman3 functional/accounting runner is prepared, not executed. #103/#75 remain open; PRs #102/#104 remain unmerged. Preserve installations/runs; broader Stage 2 and compatible target diagnostic-tool coverage remain open. This supersedes older Mac-pending statements below.

Current S2-03 finding, 27 October 2026: the Mac baseline completed 224 CLI pairs with 100 instrumented failures at one bundled getopt name-comparison over-read (#103); all 112 uninstrumented leak/accounting pairs passed. Failed evidence is retained. A [minimal parser correction](stage2-getopt-correction-2026-10-27.md) is prepared; fresh Mac and unchanged Chapman3 verification remain pending. #103/#75 and Stage 2 remain open; preserve installations, baseline and all runs. This supersedes earlier S2-03 not-executed statements below.

Current Stage 2 integration, 27 October 2026: PRs #97/#98/#100/#101 are merged; Mac and Chapman3 are clean on main 9118ffaaec077eefb0d82a50d232721a9d280a3f and the merged branches are removed. All evidence/runs/installations are preserved. S2-02 context cleanup is accepted; S2-03 CLI/parser/engine ownership qualification is now prepared, not executed. See [the bounded S2-03 plan](stage2-cli-ownership-2026-10-27.md). #75, remaining Stage 2 gates and the Chapman3 diagnostic-tool gap stay open. The early Phase 3 audit is pending; mandatory review still precedes Stage 2A/extraction. This supersedes older pending-integration statements below.

Current Stage 2 acceptance, 27 October 2026: [context cleanup #99 is verified](stage2-context-chapman3-acceptance-2026-10-27.md) on Mac C90/C17 (48 cases) and Chapman3 C90/C17 (24 functional/accounting cases). Tool controls, failed baseline and corrected evidence are retained. PR stack #97/#98/#100/#101 awaits integration. #75 and the remaining Stage 2 normal/error/repeat, cache, allocation-failure and mapped/swap gates stay open; Chapman3 sanitizer/leak-tool coverage is not claimed. Next after integration is S2-03 CLI/parser/engine failure ownership, not Stage 2A/extraction. Keep run directories, archives and installations preserved. This status supersedes earlier pending context-cleanup statements below.


Current Stage 2 preparation, 27 October 2026: PRs #93/#95/#96 are merged; main e29a6201f01200708dc55c3439434a640cdc9ed0 contains the inspected normalization and BPM cleanup evidence. #90 is closed; its merged branch is deleted on GitHub, Mac and Chapman3. Both user checkouts are clean on that main. Run directories, archives and selected installations remain preserved. Next is the [Stage 2 ownership and test matrix](stage2-memory-qualification-2026-10-27.md): qualify leak/allocator visibility and the normal/error/repeat suite, Mac first and unchanged drivers/fixtures on Chapman3. #75 remains open; the earlier context-owner correction is already merged, not a new unfixed duplicate-destruction claim. Chapman3 functional #90 checks are not sanitizer acceptance. This preparation launches no build/test/install and changes no production allocator or numerical policy. Stop for the agreed review after Stage 2 before Stage 2A/extraction; the early Phase 3 audit remains pending.


Run provenance and cleanup rule, agreed 26 October 2026: every new build,
test and generated-output directory needs run-provenance.json identifying the
actual tested repository/branch/commit, dirty state, purpose, status and retention
role. New imaging work belongs under ~/Software/build/wenu-imaging/ on both
machines. Review and preserve unique data and required acceptance evidence in
the branch before merge; large external data need verified retained copies and
committed hash/location manifests. Verify evidence reached main before branch
deletion. Merging alone never authorizes deleting run directories or active
installations. Historical unknowns must remain explicit.
See [run provenance and evidence retention](run-provenance-and-retention.md).

Agreed roadmap revision, 26 October 2026: finish the bounded Stage 1
qualification, then Stage 2 memory/ownership qualification, then stop for a review
with Fernando before Stage 2A or component extraction. Start an early requirements
audit of ESO Phase 3 instructions to inform changes from their design, rather
than leaving compliance to final export. Treat ESO_Phase3 as a proposed named
reduction/product profile, with other profiles possible later; no profile engine
or compliance claim exists yet. Preserve common scientific correctness across
profiles. Extend Stage 2A product semantics, Stage 3 interfaces and Stage 4A–4D
characterization/variance/mask/final-product implementation as agreed.
Development and corrections are on the Mac; Chapman3 verifies target behavior.
Keep originals, normal installations and current 0.5–1.5 BPM bounds unchanged.
See [the current decision and qualification ledger](native-qualification-and-roadmap-2026-10-26.md).
Earlier dated pending/merge statements below are historical where superseded.


Chapman3 installed Pycavi acceptance, 26 October 2026: Fernando reports an
isolated wheel/target installation from source 805e6c63dea20e7f5e5ade816f6a6ddc90702d86
passed actual installed imports and all five wrapper failure regressions.
Actual installed Instrument/SciencePartition, copy_paf/check_mef_bpm,
mefpp_reduce_science and run_commands then passed four serial CN Ori runs
(C90/C17, NB_659/r_SDSS). Each selected the correct private engine and restored
cwd. Complete comparisons against the accepted direct-native outputs have exact
finite pixels in all 32 detectors, matching structure/scaling, and raw headers
differ only in generated primary ORIGFILE timestamps; MJD-END matches exactly.
Protected originals, references, staged inputs, installations and normal selections
were unchanged. See the current Chapman3 acceptance record for exact paths.
This completes the bounded installed-wrapper target gate; calibration construction,
broader memory/ownership, WFI/other platforms and scientific/Phase 3 gates remain
open. Review the stacked native PRs for integration; no merge or Git branch
deletion is authorized or performed by recording this result.

[Current acceptance and limits](chapman3-native-acceptance-2026-10-26.md).

Chapman3 installed/native acceptance and workspace completion, 26 October 2026:
Fernando reports source 805e6c63dea20e7f5e5ade816f6a6ddc90702d86 passed complete
private C90/C17 installations, manifest hashes and ten installed native failure
methods per mode. Direct CN Ori NB_659/r_SDSS comparisons passed in both modes:
all 32 detector arrays exact and finite with matching structure/scaling.
Raw headers differ only in generated ORIGFILE and reviewed MJD-END; independent
decimal arithmetic confirms the candidate values, while historical endpoints
match binary32 rounding. #24 stays open because common calibration-header time
variables remain float. The installed corrected Pycavi gate subsequently passed as recorded above;
calibration construction, memory and broader scientific/platform gates remain open.

Permanent reusable CMake/CTest 3.29.6 now live at ~/opt/cmake-3.29.6/bin/;
PATH/system tools are unchanged. Future builds, private qualification prefixes,
logs and retired evidence belong under ~/Software/build/wenu-imaging/.
All home wenu-* runs were reversibly relocated with journals; none remain.
Archived build trees retain historical absolute paths and are evidence only.
No normal engine/package switch, merge or Git branch cleanup occurred.

See [the current Chapman3 acceptance record](chapman3-native-acceptance-2026-10-26.md).

Chapman3 workspace location, requested 26 October 2026: put all future
wenu-imaging build/qualification work under ~/Software/build/wenu-imaging/,
not new ~/wenu-* directories. Use tools/ for private tool bundles and archive/
for retired/failed evidence, with task-specific source/build/prefix directories.
Do not blindly move active CMake trees or toolchains: caches/frontend state and
install scripts retain absolute paths. Inventory existing ~/wenu-* directories,
identify active consumers and preserve evidence before relocating finished work.
Use guarded reversible moves; never wildcard-delete runs, packages or data.
This housekeeping request does not authorize Git branch deletion or removal of
working Pycavi/native installations. Preserve original evidence paths in records
and map any relocation explicitly. Existing home runs remain unchanged until
inspected; the just-qualified native retry still needs its install/regression gate.

Chapman3 native build acceptance, 26 October 2026: Fernando reports source
805e6c63dea20e7f5e5ade816f6a6ddc90702d86 passed both required M_PI/shmget
configuration checks, 100-unit C90/C17 builds with the declared feature/language
flags, and all five CTest entries per mode. Evidence is
/home/fselman/wenu-chapman3-native-retry-xkuuu6qu/build-check.json and mode logs.
Protected tools, previous failed-run evidence, working Pycavi package and checkout
remained unchanged. This is build/test acceptance only: no installation or
observational reduction ran. Keep installed/native/Pycavi/calibration/memory and
wider Stage 1 gates distinct; no merge or normal selection switch is implied.

Chapman3 build portability correction, 26 October 2026 (#89): the first native
C90 build at 81a2f742ad439245739601444e7ffe70cb119037 stopped because glibc 2.17
does not recognize _DEFAULT_SOURCE, leaving M_PI hidden; System V headers also
warned about feature selection. Configuration passed, C17/tests/install were not
reached, and protected tools/working Python package stayed unchanged. Preserve
/home/fselman/wenu-chapman3-native-build-579kejl8 as failed-run evidence.
The bounded fix adds legacy BSD/SVID and POSIX.1-2008 definitions on Linux only,
uses the same definitions for capability probes and native targets, checks
required M_PI/shmget declarations early, and tests Linux header availability in
the native primitive executable. Numerical C files, explicit C90/C17 modes and
Darwin production definitions remain unchanged. Do not hardcode a replacement
M_PI, relax language modes, prune Eclipse or upgrade system glibc/compiler.
Repeat fresh actual Chapman3 builds/tests before installed/observational work.
See [the portability record](chapman3-feature-macros-2026-10-26.md). This does not
invalidate the separately recorded original Mac results at their tested commit;
new Linux target acceptance remains pending until returned actual-host evidence.

Mac correction acceptance, 26 October 2026: Fernando reports source
4ade8c52027c736a49b65da3bdb31f11b036693b passed fresh C90/C17 configure/make,
all five CTest entries per mode, both private runtime installations and installed
failure suites, isolated Python imports/five wrapper regressions, and complete
CP Pup direct and corrected-wrapper comparisons in both modes. All 32 detector
arrays are exact/finite, with matching structure and only generated primary
ORIGFILE timestamp differences in raw headers. Protected engines, input files,
Python packages and checkout remained unchanged. See
[the correction record](native-failure-correction-2026-10-26.md).
This is bounded Intel Mac acceptance using prebuilt calibrations. Stage 1 stays
open for calibration-building fixtures and Chapman3; WFI observational, memory,
other platform and scientific/Phase 3 gates remain open. Keep #75's broader
ownership/memory gate and the applicable linked target requirements open.
No normal engine/package switch, merge or cleanup has been performed. Documentation-
only acceptance updates need no reinstall or repeated processing.

## Change traceability, agreed 26 October 2026

Every code-changing commit must identify the relevant issue(s), explain its
purpose and record AI assistance in an Assisted-by trailer. Include the exact
model identifier only when reliably available; otherwise explicitly record that
it is unavailable. Never invent a model identity. Preserve these fields when
squashing. PR descriptions state scope, verification and remaining limitations.
Source comments explain reasons, assumptions and constraints; add issue references
where useful, without repetitive author/model markers beside every edit.

## Authorized failure correction, 26 October 2026

Fernando approved the described focused correction for #71/#75/#76/#85 and
Pycavi propagation (#86): checked default/explicit PAF loading; informational
requests without configuration; truthful parser/engine/split exits; one owner
for the published context; checked split writes/cleanup; native return-code
handling and cwd restoration in the science wrapper. The necessary PAF query
stale-value guard is #87. Preserve valid conversions, scientific arithmetic,
calibration parameters, shared normalization and current working installations.
See [the correction record](native-failure-correction-2026-10-26.md).
Keep issues open until their actual target gates pass. No merge, normal-engine
switch, full memory qualification or broad refactor is authorized by this item.

Mac normal installation accepted, 25 October 2026: Fernando reports the default
C90 ./configure; make; make install route, optional make check (four CTest entries),
complete installed payload/BPM pixels/checksums/CLI, byte-identical repeat install
and DESTDIR staging passed at source 7c5238f848284033bcef416ec5970a8004550afd.
See [frontend acceptance](native-frontend.md). Close bounded #84; preserve
the private installation at ~/wenu-mac-simple-install.7en8H834/install and the
selected historical engine/configuration. Next is CP Pup read-only preflight,
then isolated native regression; do not repeat installation checks unnecessarily.
No automatic observation run, engine switch, merge or cleanup is authorized.

Simple installation interface, approved 25 October 2026: Fernando requires
./configure; make; make install to remain the normal supported interface.
The new root/component wrappers delegate to CMake, select tools/check prerequisites
and propagate errors; optional make check is developer qualification. See
[frontend status](native-frontend.md). This is current Stage 1 work before
CP Pup comparison. Package-manager evaluation remains deferred. Agent Linux
frontend tests/integration passed with explicitly synthetic resource fixtures;
actual Mac frontend qualification is pending. Preserve existing private installs
and normal engine selection; no observation rerun, merge or cleanup starts here.

Current priority, approved 25 October 2026: Fernando defers pip-versus-Conda/
micromamba packaging as a TODO and resumes the existing native qualification.
See [current next work](roadmap.md) and native roadmap revision 1.4. Next is the
read-only CP Pup fixture/installed-candidate preflight, then isolated native
output comparison and remaining Stage 1 gates. Do not start package-manager
prototypes, provisioning, publication or bulk document moves as a prerequisite.
Preserve the qualified private installs and selected historical engine.

Documentation audience correction, 25 October 2026: Fernando requests a short
[user installation entry point](../installation.md) directly under docs; keep detailed
build/test/install material in [the developer guide](native-installation.md). Maintain
both with installation changes. Group developer navigation by topic; any later
physical move must update inbound links together. Package-manager review is a
proposal, not authorization to install/provision dependencies or publish binaries.
Conda/micromamba is the first recommended user-distribution evaluation; preserve
the existing CMake/CTest build and current working environments.

Maintained installation guide, approved 25 October 2026: Fernando requires
[the native installation guide](native-installation.md) under docs to stay current.
Update it in the same PR as changes to build/install tools, entry points,
platforms, resources/layout, selection, upgrade/rollback or qualification status.
Keep the Python installation hub, root README and build reference linked and
consistent; distinguish tested procedures from pending platform work.

Intel Mac native acceptance, 25 October 2026: Fernando reports C90/C17 native
builds, three CTest entries per mode, exact OCAM/WFI BPM pixels, checksum metadata
accounting, real private installations/repeats/installed CLI and C17 DESTDIR passed
at source 41c8e6a544c1bc5122dc558e0c8cc7904214e1d0. See
[the acceptance record](native-mac-build-install-acceptance.md). Historical engine and configuration
remain selected/unchanged. Observational pixel equivalence, installed wrapper,
calibration/WFI fixtures, failure/memory and chapman3 gates remain pending.
Prepare immutable observational fixtures next; publication starts no reduction,
engine switch, merge or branch cleanup. Earlier pending statuses below are historical.

Stage 4 amendment, 25 October 2026: Fernando requires creation and propagation
of per-pixel frame variances for science and calibration products. Follow
[roadmap revision 1.3](mefpp-modernization-roadmap-v1.md): squared units, masks, gain/RON,
calibration/parameter uncertainties, shared-normalization correlations and
Pycavi/resampling/photometry handoffs, with independent recovery tests. This is
future Stage 4 scope; preserve the current Stage 1 build-only boundary.

## Stage 1 isolated candidate, 25 October 2026

Stage 1 candidate implementation, 25 October 2026: Fernando authorized the isolated
bundled-source CMake build after reviewing stage 0 and reporting actual-Mac
fixture settings. See [candidate status](native-cmake-candidate.md)
and mefpp2/README.cmake.md. qfits is now under mefpp2/qfits5 in this candidate;
retain all 18 qfits and 79 Eclipse archive sources. Numerical algorithms,
allocator policy, existing installations and data remain unchanged. Agent Linux
GCC 13.3/CMake 3.29.6 code-only C90/C17 builds and three CTest entries per mode
passed; this is not Mac/chapman3 qualification. Actual BPM decompression, complete
runtime install and observational pixel equivalence are pending on the Mac.
No engine switch, observation rerun, memory-clean claim, merge or branch deletion
is authorized by this implementation. Earlier audit-only holds below are historical
where superseded by this bounded authorization.

## Stage 0 native build specification, 25 October 2026

Read [native build specification v1](native-build-specification-v1.md): minimum
static qfits -> Eclipse -> MEF/common -> mefpp targets; required PAF/BPM/license/
manifest payload; no optional legacy utilities in the first default candidate.
Retain full archive source lists; no pruning based on reachability. Generated
config headers must actually replace stale tracked include resolution.

Mac synthetic probe in wenu-mac-toolchain-01j1s5dt passed strict C90/C17 static
build/link and 2 CTest checks using explicit Xcode tools and CMake/CTest 3.29.3.
This is not native mefpp qualification. Proposed initial minimum is CMake 3.29;
record a reviewed change if chapman3 constraints justify another version.
Fresh observational manifests, real C90/C17 builds and Linux toolchain evidence
remain pending. The document defines tests/fixtures, not executed native coverage.
Preserve current engines, sources and products; implementation follows the
bounded stage-1 decision after specification review, not this documentation push.

Native roadmap revision 1.2, 25 October 2026: retain C89/C90 as the portable C
source baseline and explicitly qualify compilation and behavior in C17 mode.
C17 is a compatibility target, not a new source-feature baseline. Inventory
legacy/dependency extensions and isolate platform APIs; do not claim existing
strict compliance. Newer facilities need a reviewed exception. C23 checks are
optional. Mac compiler support is distinct from unperformed mefpp tests;
chapman3's inventoried GCC 4.8.5/Clang 3.4.2 cannot provide the C17 lane. Qualify
an isolated compatible compiler without implicitly replacing system tools or
upgrading glibc. This clarification authorizes documentation, not installation.

Roadmap v1 revision 1.1, 25 October 2026: extend data review to JWST, Roman,
Rubin, ELT and publicly documented future ESO archive plans, distinguishing
adopted standards from proposals/unknowns. Native Apple Silicon arm64 build/install
and functional acceptance is required; Rosetta is not acceptance. Extend the
parallel design assessment to optional threads within detectors and optional GPU
backends only after profiling/equivalence evidence, retaining a portable ANSI-C
CPU baseline, global resource limits and shared mosaic normalization. This is
planning authorization, not permission to add threading/GPU dependencies or run
new workloads. No accelerator backend or hardware purchase is selected.

Data-representation review added to native roadmap v1, 25 October 2026: insert
stage 2A immediately after memory qualification and before component contracts.
Review current accepted formats/metadata models and in-memory structures,
including FITS, HDF5, ASDF and Zarr, without preselecting a replacement. Preserve
FITS ingestion/interchange and originals; compare actual performance/fidelity
and ANSI-C/platform/dependency costs. Any new backend needs a separate reviewed
migration and renewed memory checks. See the version-1 native roadmap.

## Native roadmap version 1 and current architecture, 25 October 2026

Fernando authorizes the first roadmap and current-architecture documentation.
Read [roadmap v1](mefpp-modernization-roadmap-v1.md) and
[current mefpp architecture](mefpp-current-architecture.md). This dated planning
update supersedes older sequence descriptions: clean build/install on Intel Mac
then chapman3; memory/ownership/failure qualification; component contracts and
extraction; missing calibration services; single-detector CCD support; safe mosaic
parallelism; native Windows qualification; CMOS services last. Consider Windows
portability from the first build decision. CMake/CTest and component signatures
are recommendations for review, not selected/implemented tools or APIs.

Preserve common mosaic flat normalization and relative detector response.
mefpp_cal_lin is intended to cover non-linearity, shutter errors, gain and RON:
initial bias pairs, randomized integration times with consecutive flat pairs,
full-range acquisition to saturation, valid-range estimators and separate
calibration products. Select compatible measured gain/RON or explicit verified
instrument/mode defaults; record units/status/provenance. ESO CONAD/GAIN mappings
must be explicit. Include fringe-template construction plus separate Python
scaled subtraction. CMOS requires its own camera/mode review and qualification.

The current architecture is observed; target design is provisional. Maintain
version/revision records and discuss material changes before dependent work.
Documentation delivery does not authorize source moves/build changes/installs,
scientific changes, new concurrency, merges or cleanup. Existing tests and
actual-target evidence rules continue to apply.

## Current hold: architecture audit, then full roadmap, 25 October 2026

Fernando now requires an audit of how outdated the native build/organization
is against modern development practices, a diagram of the current structure
and a trace of Eclipse use/non-use. He intends eventual components for bias,
BPM, non-linearity determination/application, dome/sky/master flats and science.
Read [the architecture audit](native-architecture-audit-2026-10-25.md), #73
and its compiler-assisted evidence. It distinguishes potential function paths,
conservative object closure and actual runtime coverage; never label an
unreached function safe to delete or an existing linearity routine qualified.

The full roadmap must follow this audit and be reviewed/agreed before actual
modification work. This supersedes proceeding directly from #64/#72 to qfits
nesting/build fixes. No component move/split, build-system change, dependency/
compiler upgrade, installation, new concurrency or scientific change starts
from the audit alone. Compile-only analysis in disposable agent copies does
not qualify Mac/chapman3 builds or replace native runtime/scientific tests.

Preserve the two static-library boundaries and algorithm baselines while
assessing options. A modular C library and thin command interfaces are possible;
do not assume separate processes/repositories, a language rewrite or CMake is
already chosen. The roadmap must define stage contracts, ownership, detector
identity, units, masks, uncertainty/QC/provenance, error/restart and equivalence
gates. Source findings #74/#75/#76 remain uncorrected; existing installation/
native issues stay open. Later scientific parameter tuning remains deferred.

## Current authorized native installation audit, 25 October 2026

Fernando changed the order: bring roadmap point 5 forward, beginning with an
audit of mefpp/qfits installation and moving qfits under mefpp. Prioritize
Intel Mac clean build/install qualification, then chapman3. Read
[native installation audit](native-installation-audit-2026-10-25.md) and #64.
Initial audit probes are agent-host fixture evidence, not target qualification;
#65–#71 remain open. Proposed source location is mefpp2/qfits5, one canonical
copy, with retained APIs/licenses and explicit qfits -> Eclipse -> mefpp order.
The initial audit changes no native source layout/build or installed engine.

This explicit direction supersedes older deferral of all native work until
notebook/Python refactoring only for the bounded build/install task. The next
target action is read-only Mac compiler/resource/checkout inventory. Subsequent
corrections must be scoped to installation, preserve numerical behavior and
working native selections, use fresh source copies/private prefixes and record
actual compiler/archive/resource provenance. Do not upgrade compilers/libraries,
add native concurrency, change detector/science algorithms, or silently expand
into the complete mefpp audit. Mac acceptance precedes chapman3; an agent Linux
build is neither. Existing #23/#24/#13 and runtime finding #71 are separate
bounds; a successful exit alone never establishes native scientific success.

Resume remaining notebook/config-script/Python-audit work after this task;
scientific parameter tuning stays deferred until all fields are reduced.
PRs #57/#60/#63 are merged; the old review-branch wording below is historical.
Retain fresh actual-target guards and matching test explanations/comments.
No target install/source move is claimed by documentation delivery.

## Current Mac functional acceptance and handoff, 25 October 2026

Selected installed-library paths corresponding to notebooks 03–09 passed on
MC02VV0HPHTDG for one 20 s CP Pup r_SDSS exposure (32 detectors), including
plotting-enabled SCAMP, both illumination models, saved-grid readback, exact-ID
catalogues, two separate magnitude-only corrections and twelve decoded QC PNGs.
See [the Mac pilot](pilots/mac-cp-pup-2017-03-13/README.md) for evidence, hashes,
actual routines, settings and limits. Preserve all originals and accepted outputs.
Do not describe this as full notebook orchestration, multi-exposure stacking,
multi-filter Mac acceptance or scientific validation.

#61 closed as a bounded investigation: unchanged stars/parameters reproduce
the first-run equivalent solution within the observed numerical precision;
there is no externally imposed target zero point and no new algorithm/factor
change. Repeated flux scaling/serialization limits remain explicitly recorded.
#62 remains open for parameter-domain investigation; current Gaussian negative
RANGE and historical candidate fixed nugget ~0.015 are evidence, not approved
defaults. Fernando deferred scientific tuning until all fields are reduced.
SCAMP astrometry DR2 and calibration DR3/GSPC must not be conflated.

The current task is acceptance/roadmap documentation, not further processing.
Continue the agreed thin-notebook, derived configuration-script, used-library
audit, then mefpp sequence only within a separately agreed bounded next task.
Mac multi-exposure/filter checks, other platforms, WFI, native gaps and Phase 3
remain open. Earlier 24 October integration handoffs are historical: the five
qualified branches were merged/cleaned at main0591ba0. PRs #57/#60 and the Mac
acceptance documentation remain separate review branches; do not merge/delete
them without instruction. Obtain fresh actual Mac Git/environment evidence
before any synchronization or installation. Docs-only delivery needs no reinstall.

## Explain every functional and result-verification test, 25 October 2026

Fernando requires an explanation before every functional test and every test
that verifies results, including preflight checks, synthetic checks, installed
package checks, observational runs and read-only output checks. Give the
explanation before the command group or agent execution, not only when asked.
Keep it concise and specific to the test being proposed:

- State the purpose, inputs and settings, actions performed, and whether the
  test processes data, queries a service, writes outputs or only reads results.
- Name the actual Pycavi modules and subroutines/methods exercised, including
  relevant indirect calls and native programs. Distinguish production routines
  from orchestration and verification helpers; do not imply that a helper's
  independent calculation exercises a production implementation.
- State expected outputs, pass criteria and the test's limits. Distinguish
  wrapper completion, native execution, output integrity and scientific
  validation. Do not claim coverage of routines that the test does not call.
- After execution, explain what actually ran, what passed or failed, evidence
  and remaining limitations. Clearly identify checks still pending; a launch
  or zero wrapper exit code alone is not acceptance of the outputs.

In every testing script or copy-and-paste command group prepared or revised by
the agent, put short comments immediately before the relevant sections identifying
the tests or verification actions performed there. Use matching short names or
labels in the preceding user-facing explanation so the correspondence is easy
to follow. Every announced test/action must have a counterpart comment and
implementing code; every commented test/action must appear in the explanation
and match what its code actually does. Include preparation, guards, queries,
processing, output checks and preservation checks when those actions are part
of the test. Comments should explain sections, not narrate every code line.

Before supplying or executing a test, review the explanation, section comments
and executable code together for omissions or mismatches in both directions.
Do not silently reuse an uncommented older runner: add the matching comments in
a fresh test copy while preserving the original and its processing behavior.
Label launch-only steps and checks deferred to a later script explicitly; do not
describe a future output check as executed by the launch script.

These explanations do not authorize scientific tuning, broader validation,
extra processing or changes outside the currently approved task.

## Current authorized integration/cleanup, 24 October 2026

Fernando instructed merge and cleanup of the five qualified PRs #43, #45, #47,
#50 and #52. Integrate them into main in dependency order, retargeting stacked
PRs as their predecessors merge. Preserve all qualified heads/acceptance records;
verify every head is an ancestor and the final main tree equals the integrated
head. Cleanup only these merged branches with expected-tip and ancestry checks.
Obtain current actual chapman3 checkout evidence before local sync/cleanup and
provide guarded commands automatically. No reinstall, processing, query or
refit is required. This authorization does not close scientific/orchestration/
export/Mac gates or deferred #51; earlier handoffs below are historical.

## Current functional walkthrough handoff, 24 October 2026

The selected isolated OmegaCAM functional paths through notebook 09 passed:
baseline, Chebyshev and cubic Kriging applications, and twelve existing QC PNGs
across baseline/two corrected catalogues. Kriging QC records are in
notebook09-kriging-qc-saittxaz; all original/staged catalogue hashes remain
unchanged. #48 is closed after correction/installed/actual-copy evidence.
No independent scientific/model acceptance, complete notebook orchestration,
SkyMapper query, Mac qualification or Phase 3 compliance is claimed. #37/#38,
#51 and broader scientific/native/export gaps remain open. Preserve all inputs,
models, baseline and corrected outputs. PRs #43/#45/#47/#50/#52 are unmerged;
merging/cleanup needs the corresponding user instruction. Earlier handoffs below
are historical. Do not start a new implementation/refactor/query merely because
these selected functional checks passed.

## Current Kriging application coordinate correction, 24 October 2026

The existing before/after catalogue QC call generated and decoded all eight PNGs
without changing either source/staged catalogue (notebook09-qc-h6o98cy8). Address
#48 next: application axes must use the stored physical 1..ORIG_W/H endpoints,
actual grid shape and (y,x) orientation. Preserve cubic interpolation/default
solver, strict bounds, correction sign, null-safe writer and guards. No use of
the linear reader as a substitute, new model, refit or reference query. Test
source/installed behavior, then fresh target copies; keep #48 open until target
acceptance. #51 is deferred and does not affect the valid current QC inputs.
Earlier handoffs below are historical.

## Current notebook 09 QC handoff, 24 October 2026

Chebyshev application passed in notebook09-chebyshev-6xb3rgu1 with the existing
saved models: all expected magnitude changes, unchanged unrelated columns and
complete FITS extension metadata, 3718 exact IDs and 12741 missing masks, correct
provenance and byte-identical repeat calls. Baseline/model hashes are unchanged.
#49 is closed after source/installed and actual-copy evidence. Resume existing
catalogue QC on fresh staged baseline/corrected copies so fixed plot filenames
do not overwrite prior outputs. Keep current plot/reference settings and distinguish
functional generation from independent scientific acceptance. No new reference
query or fit; #48's separate Kriging application grid remains open. PRs #43/#45/
#47/#50 are unmerged. Earlier handoffs below are historical.

## Current notebook 09 baseline handoff, 24 October 2026

Baseline construction passed on chapman3 in notebook09-catalogue-95xc1kyz:
16459 paired-filter rows and 3718 distinct exact int64 Gaia associations, with
FITS null masks and all input hashes preserved. #46 is closed after correction,
installed tests and actual-output verification. Preserve baseline catalogue and
recovered references; continue functional correction only on fresh copies with
explicit saved models. Existing default Chebyshev application is distinct from
scientific model acceptance. Separate Kriging application coordinates fail at
valid edges (#48); do not treat corrected reader #41 as correcting that function.
PRs #43/#45/#47 remain unmerged; no new query, calibration, fitting or scientific
policy change. Earlier handoffs below are historical.

## Current catalogue handoff, 24 October 2026

#44 correction and bounded identity recovery passed chapman3 acceptance: four
raw/clean CSVs, zero coordinate differences, exact int64 CSV/Table/FITS round
trips, unchanged non-ID fields and original hashes. Resume notebook 09 with
fresh recovered catalogues under gaia-id-recovery-jh763zwi/recovered/catalogues;
do not replace historic calibration provenance or rerun calibration/models.
#41/#42 reader/08c checks also passed. PRs #43/#45 remain unmerged. Earlier
handoffs below are historical; independent science accuracy remains open.

## Current reader correction, 24 October 2026

Both 08b fits/grid serialization/QC passed. Target 08c diagnostics confirmed
#41 reader coordinate mapping errors despite exact saved grids; #42 records
misordered plotting arguments. Correct only reader axes and explicit plotting
bindings, preserving the linear method and immutable models. Verify existing
saved grids and fresh plots without refitting; keep #41/#42 open until target
verification. No science-image/catalogue correction, model/selection changes or
upgrades. Earlier dated handoffs below are historical; #37/#38 stay open.

## Current handoff, 24 October 2026

Fernando requested merging and cleaning the completed Chebyshev display work
before launching Kriging. #39 is closed after target plot/grid verification
without refitting. Notebook 08b imports/source identity and input selection
passed preflight: 583 r_SDSS and 580 NB_659 unique positions, no subsampling.
No variogram, Kriging fit or correction has run. Keep existing notebook settings
explicit, including its cleared clipping mask and four-pixel-offset diagnostic;
that diagnostic is not independent validation. Preserve all prior products and
leave #37/#38 and scientific accuracy/saturation investigations open.
The earlier dated handoffs below are historical.

## Current handoff, 23 October 2026

Both filters passed notebook 07 functional calibration checks on chapman3.
Fernando authorized merge/cleanup of completed branches, then a pause until
notebook 07b QC. Reuse the verified calibrated products and recorded queries;
do not rerun calibration. The r_SDSS saturation repair and installed writer
passed target verification (#33 closed). Keep #35/#36 scientific saturation
investigations, native #23/#24, independent accuracy and Mac qualification open.
The earlier walkthrough directions below record the agreed scope/history.

## Latest notebook walkthrough direction, 23 October 2026

Fernando declined the proposed standalone lunar/site-data check and explicitly
instructed continuing through the whole notebook sequence before deciding further
work. Resume the existing isolated OmegaCAM functional walkthrough at notebook
04, then SCAMP, SWarp and zpcal. Defer lunar/site-data to zpcal. This direction
supersedes the earlier requirement to close every dependency check before this
walkthrough; it does not accept the entire dependency baseline or authorize
general refactoring, replacement implementations or the systematic library/mefpp
audits. Preserve existing code/data/settings and use the established machine,
output-isolation and priority guards. Record actual results and resolve unexpected
failures before dependent stages. See the roadmap for the current boundary.

## Current approved metadata correction, 23 October 2026

Fernando approved the bounded Pycavi correction in #25: authoritative science
metadata at detector extraction/assembly, precise exposure endpoints, and
all-input coadd timing with total integration separate from native equivalent
exposure/gain. Preserve pixels, reuse solved WCS in fresh copies, and leave
native mefpp implementation (#23/#24) deferred. Continue the existing functional
notebook sequence through zpcal on chapman3, then retest on Mac. This supersedes
the older dependency-gate stop for this walkthrough; it does not authorize new
photometry functionality, broad refactoring or upgrades.

## Controlling dependency gate, 23 October 2026

Fernando clarified that dependency establishment and documentation on chapman3
come before the Pycavi workflow audit. Inventory Python packages, native engines,
resources, installation/build details, configuration, evidence and limitations.
Aim to align the Mac versions after capturing its actual imaging environment;
do not change either platform merely to force identical inventories. Diagnostic
wrappers calling existing functions are dependency evidence, not validation of
the complete orchestration or authorization to replace it. Keep the agreed
five-point sequence in roadmap.md. Future-proof Python only after those five
points are complete and the software works well, under a separately agreed plan.
The local Astrometry.net 0.98 installation was explicitly approved; this is not
blanket authorization for other engine or library upgrades. See the dated
chapman3 dependency inventory for current evidence and outstanding checks.

Status: accepted working agreement, with scope clarified by Fernando Selman on
20 October 2026. This is the canonical developer policy; the root AGENTS.md
directs agents here.

## Machine guards and process priority, 22 October 2026

### Actual user checkout verification, 23 October 2026

Before changing Git state or the installed wenu-imaging package on Fernando's
Mac or chapman3, inspect that computer's actual clone. Obtain fresh OS/hostname,
resolved checkout root, origin fetch/push URLs, branch, HEAD, upstream, full
`git status --porcelain` and interpreter/prefix evidence. Do this before fetch,
pull, switch, merge, reset, commit, push, cleanup or installation commands.
Do not substitute the agent workspace's state, yesterday's terminal output or a
directory name for this evidence. Use guards matching the established target;
preserve local edits and discuss unexpected branch/origin/divergence before
mutating it. A fetch changes Git references too. Do not assume the Mac imaging
clone is the separate Mac wenu clone. No Git software upgrade is authorized.

Fernando authorized the bounded remote-notebook launcher in
`Pycavi2/tools/start_remote_notebook.py` on 23 October. It starts the existing
chapman3 notebook workflow; it does not expand the reduction/refactoring scope.

Fernando develops on his Mac (wenu) and chapman3 (wenu-imaging) in parallel.
Every copy-and-paste command block must state its intended machine/project and
start with an automatic OS/hostname guard before any other work, including
environment activation, imports, Git operations, installs or file writes.
Do not rely on the displayed shell prompt or a previous block's successful check.
Group the block in a subshell so a guard failure stops that block without
closing the user's interactive terminal or SSH session.

For the current chapman3 imaging pilot, use this guard:

```bash
(
test "$(uname -s):$(hostname -s)" = "Linux:chapman3" || {
    echo "STOP: run this block on chapman3 for wenu-imaging." >&2
    exit 1
}
# Intended commands follow here.
)
```

The known Mac is MC02VV0HPHTDG (Darwin); the parallel wenu checkout is
`/Users/fselman/odrive/Dropbox/software/wenu`. The current chapman3 imaging
checkout is `$HOME/Software/wenu-imaging`. These are distinct projects. For
repository operations, additionally check the actual Git root, origin repository
and expected branch before modifying/fetching/installing; hostname alone cannot
distinguish checkouts. For Python processing, also check the resolved interpreter
prefix against the intended environment before scientific imports. The current
chapman3 prefix is `$HOME/.conda/envs/wenu-imaging`. Use the explicitly selected
target for future Mac imaging validation rather than requiring Linux for every
wenu-imaging task. Do not silently update a failed guard to match the current
terminal or infer the correct project from a directory's basename.

Future reduction launches must use `nice -n 10` on the Python parent so native
child processes inherit the lower CPU priority. Retain existing thread/resource
limits. Do not renice, restart or otherwise disturb an already running job
without instruction. The first pilot bias was already running when Fernando
requested this priority convention; it was left running as instructed.

Priority clarification approved 23 October: the Jupyter server and interactive
kernel run at normal niceness 0. Only batch processes and their descendants run
at niceness >=10. Launch scripts through `Pycavi2/tools/run_batch.py` in a
separate process, or use the existing `nice -n 10` terminal pattern. Never call
`os.nice`/`os.setpriority` in the interactive kernel to lower batch priority;
that also lowers later interaction. Direct heavy notebook-cell computations or
existing library calls do not automatically pass through the helper. Explicitly
launch those workloads in a batch process when using this priority split. Do not
claim all existing notebook runners were changed by this launcher utility.

These are instructions for preparing commands, not authorization for a new CLI,
host migration, workflow refactor or scheduler change.

## Packaging-stage authorization, 21 October 2026

Fernando authorized the packaging implementation, preserving the current
scientific dependencies and engines. **Any deviation from the roadmap must be
discussed with him and approved before proceeding.** Packaging validation does
not replace the later systematic Pycavi Python library audit or mefpp audit.
See installation.md for actual checks and pending platform gates.

### Bounded roadmap execution

Before implementation, identify the currently approved bounded task, its intended
result, scope limits, prerequisites and acceptance gate. A general "proceed"
applies to the task just discussed, not unmentioned stages or pending backlog.
If an extra item, new package/capability, scientific policy change, scope expansion
or changed order is needed, stop that affected implementation; read-only
assessment may continue. Discuss the concrete need, alternatives, consequences
and acceptance gate with Fernando, obtain explicit agreement and document the
agreed change in roadmap.md before implementing it. Keep proposals, partial
results and accepted completion distinct. Passing dependency checks does not
authorize starting the workflow audit. Routine choices and necessary fixes
inside the already approved boundary do not require repeated permission.

## Scope update, 21 October 2026

### Latest sequencing clarification

Fernando subsequently revised the proposed refactoring order:

1. Retire the historical `.py` reduction scripts; do not port their obsolete
   implementations. Streamline the notebooks using the existing libraries.
2. Once the notebook workflow is thin, provide runnable Python scripts driven
   by configuration files from that workflow, calling the same library routines.
3. Audit the library routines actually used by those notebooks systematically.
   Existing targeted fixes/tests do not establish that other routines are sound.
   Keep refactoring equivalence checks while thinning; the full scientific
   library audit follows the thin-notebook stage.
4. Audit mefpp after the Python-library audit. Read-only tracing of an existing
   native capability may inform the plan without starting the full C audit.

Keep packaging and Mac/Linux OmegaCAM execution as immediate prerequisites.
Postpone WFI implementation and dedicated validation until wenu-imaging works on
Mac and Linux. WFI remains a retained requirement; preserve its files/history and
record shared-code risks, but do not let WFI-specific work lead the current phase.
No Python/library/engine upgrades or backend replacements are authorized now.

BPM generation must be part of normal calibration creation, not permanently
defined as copying a static installed mask. Trace and validate the existing
mefpp construction path first, including required inputs, dependency order,
detector mapping, mask convention, thresholds, provenance and reuse rules.
Do not invent new BPM algorithms or silently change the working pilot products.

This clarification supersedes earlier suggestions to repair the legacy scripts
or begin implementation with WFI calibration preselection. Keep notebook/script
logic shared and preserve the single-node parallelism objective.

Fernando clarified the order of work after the portability audit:

- The immediate deliverable is properly packaged wenu-imaging with robust
  installed resources, explicit dependencies and reproducible installation.
  Debug and improve Pycavi before moving on to mefpp implementation.
- Do not upgrade Python libraries, Python itself, external astronomy engines,
  or replace backends in this stage. Prior modern-library probes are audit
  evidence only. Future compatibility means maintained interfaces, packaging,
  tests and recorded constraints now, with upgrades qualified separately later.
  Correctly declaring existing runtime imports is distinct from selecting a
  new library or upgrading the working environment.
- Audit single-chip CCD and CMOS requirements now, including primary-image and
  one-extension FITS layouts and detector-specific calibration/noise behavior.
  Audit findings do not establish implemented detector support.
- Audit every pipeline stage for single-node concurrency, aiming to parallelize
  every independent task where resource use and scientific dependencies permit.
  Cover exposure, detector, target/filter and independent QC work; coordinate
  outer processes and inner executable/BLAS threads within one node allocation.
- Dependency barriers and exclusive ownership of outputs remain mandatory.
  Joint fits and coadds may have parallel internals but cannot be replaced by
  independent per-frame results without preserving their scientific definition.
- Keep the present mefpp behavior for the packaging/Pycavi milestone. The later
  mefpp audit must consider both concurrent independent invocations and internal
  C parallelism rather than assuming one is automatically safe or sufficient.

This dated update controls the sequencing where earlier future-work paragraphs
differ. It does not authorize a broad rewrite, premature backend replacement,
archive submission or merging a proposal without instruction.

### Two user interfaces and WFI coverage

Fernando's intended design is thin, editable notebooks for learning and inspecting
data, plus Python scripts/configuration for repeatable headless processing. Both
must call the same library stage functions; do not maintain separate scientific
implementations or implement the script path by executing notebooks. Keep useful
parameter choices and inspection visible in notebooks. Retain WFI in the design,
but defer WFI implementation and validation as specified above, including its
calibration preselection, filter/metadata conventions and standards.
See [the two-interface review](pycavi-two-interface-review-2026-10-21.md).

## Purpose and scope

wenu-imaging coordinates Pycavi2 (Python), mefpp2 (ANSI C with embedded Eclipse),
and qfits52 (ANSI C FITS support) for WFI and OmegaCAM image reduction.
Maintain one canonical wenu-imaging repository containing the three components
as ordinary directories. Preserve the separate Python and C build/interface
boundaries; repository consolidation is not an algorithm rewrite.

The immediate delivery is a medium-sized OmegaCAM reduction set prepared for
submission as ESO Phase 3 science data products. Prioritize a reliable,
scientifically validated production path over new detector support or mefpp
parallelization. Data volume, filters and programme identifiers remain to be
inventoried; do not invent a size or throughput target.

The developer documentation and roadmap direction are accepted. The current
work is to record them and characterize the unchanged baseline. Documentation
in the parent repository may be maintained within the agreed scope. Changes to
component source, notebooks, scientific defaults, packaging, build scripts and component interfaces
require Fernando's explicit approval of an implementation stage. Publishing a
documentation proposal does not approve that stage. Do not merge a proposal
without instruction.

## Read first

- `docs/developer/architecture.md`: existing boundaries, baseline and open decisions.
- `docs/developer/roadmap.md`: platform requirements, phases and acceptance criteria.
- Any component-specific instructions before working inside a component directory.

Shared rules apply to work launched from this parent workspace. A component may
later need a concise local AGENTS.md for standalone work; creating those files
is a separate documentation change in the corresponding component directory.

## Platform priorities

- Urgent: macOS Intel and a Linux cluster whose distribution is pending.
- Required afterward: macOS Apple Silicon and Ubuntu Linux.
- The first identified machine runs macOS 13.7.8 (22H730), x86_64,
  Python 3.11.7 and Apple Clang 15.0.0 (clang-1500.1.0.2.5).
- These are requirements and reported environment facts, not validated support.
  Cluster distribution, scheduler, resource limits, Python/compiler versions
  and filesystem characteristics remain unknown. The execution model is confirmed:
  multiprocessing within a single node.

## Evidence and scientific preservation

Record exact repository commits, environment, commands and results. Distinguish
source observations, reproduced failures, inferred risks and open questions.
Do not describe syntax checks, skipped tests, an editable install or Linux-only
results as evidence of full installation, scientific correctness or macOS support.

Preserve algorithms, pixel units/precision, gain and exposure normalization,
FITS scaling and headers, extension/BPM mapping, calibration selection,
rejection thresholds, weights, photometric transformations and illumination
defaults unless separately approved. Record out-of-scope defects rather than
silently fixing them. Investigate unexpected numerical differences before
continuing dependent work.

Use immutable observational inputs and fresh output directories. Establish trusted
OmegaCAM reference products and comparison tolerances with Fernando first;
retain WFI regression coverage as changes affect shared code. Single-CCD and
single-CMOS support are future requirements, not established capabilities.
Never test by modifying original observational data or an existing working
installation. Builds and setup commands that generate files must use disposable
copies and a separate installation prefix during characterization.

## Minimal-change discipline

### Defect tickets, approved 23 October 2026

Open a GitHub issue for every distinct defect found. Search existing issues
first and update the matching ticket rather than duplicating it. Separate
confirmed failures, source findings and hypotheses. Record reproduction/evidence,
affected stage/platform, scope, acceptance criteria and relevant dependencies.
Link implementation commits/PRs to their tickets. An issue does not authorize
out-of-scope implementation or a change in scientific policy.

After correcting a defect, add a correction comment explaining the change,
commit/PR (or environmental remedy), tests and target verification actually
performed, and remaining limitations. Then close the ticket when its acceptance
criteria are met. Do not equate a written patch with target qualification, or
closure with a merged PR. Keep a native root-cause ticket open when only a
Python mitigation has been verified; link the separate mitigation ticket.
Retrospectively record defects corrected during the current walkthrough and
their existing evidence. Track subsequent findings the same way without asking
Fernando to repeat this authorization.

Trace and reuse existing functions before adding replacements. Prefer focused
refactoring and compatibility fixes. No broad rewrite, module relocation,
additional repository restructuring, workflow engine, build-system migration, dependency upgrade
campaign or unrelated cleanup without an explicit decision.

Treat repository names, Python distribution/import names, executables and C
library names as separate interfaces. The new parent name does not authorize
renaming `pycavi`, `mefpp`, qfits APIs or their installed resources.

External astronomy programs remain separately managed dependencies unless a
later decision changes that arrangement. Record and validate versions/paths;
do not vendor upstream source, download large index sets, or install system-wide
software as a side effect of an audit.

## Parallel processing and cluster work

The confirmed cluster model is multiprocessing within a single node. Distinguish
Python processes, threads inside external executables and the scheduler's
allocation. Multi-node/MPI support is outside the current scope. Do not assume a
scheduler brand, containers, root access or compute-node network access.

mefpp currently runs serially: it does not implement multiprocessing. Keep that
behavior for the initial operational OmegaCAM milestone. Do not introduce internal
parallelism or concurrent mefpp invocations merely because the pipeline supports
parallel astrometry. A mefpp multiprocessing design comes only after wenu-imaging
works correctly, with separate approval and equivalence/race/memory tests.

Once implementation is approved, respect allocated CPUs and memory rather than
the total resources visible on a node. Account for process-by-thread
oversubscription. Validate worker failure propagation, temporary/output path
isolation and restart behavior. Preserve scientific results when changing
concurrency. Record unknown cluster details without blocking independent Intel
Mac documentation and analysis.

## Git and review

Preserve attribution, license notices, history and unrelated local work. Use
focused branches. Inspect component status before checkout/update operations;
never discard local changes or overwrite an existing working installation.
The imported component histories remain available as ancestors of the monorepo.

After authorization, commit component changes in wenu-imaging. Cross-component
fixes may share a focused commit when they implement one agreed change.
The former component repositories remain historical references; do not push
ongoing development to them or to their original upstream projects.
Do not merge, delete branches, tag or release without instruction.

### PR executive summaries and Work chat — approved 28 October 2026

Every PR, including drafts and documentation-only PRs, must begin its description
with a concise executive summary for Fernando. State the purpose/problem, main
changes, checks actually passed, pending verification or material risks, and the
current status/next step. Distinguish prepared fixes from verified behavior and
functional success from memory or scientific acceptance. Keep implementation
details and full evidence below the summary.

Automatically display the same complete executive summary in the Work chat when
creating a PR or materially updating its scope, findings, validation or readiness;
include its link and current commit. Do not require Fernando to ask for it. Keep
the PR summary and chat summary consistent with the latest evidence. This reporting
rule adds no tests, host synchronization, execution gates or approval steps.

### Delivery handoff and local synchronization

These six rules were approved by Fernando on 23 October 2026, adapting the
applicable delivery procedure from `fselman/wenu` to this separate project.

1. **Automatic handoff.** After every push or merge, provide complete commands
   for synchronizing the applicable user computer, verifying its resulting
   commit and performing any authorized cleanup. Include this handoff without
   waiting for Fernando to ask. A pushed review branch and merged main require
   different commands; use the actual delivered ref and full expected SHA.
   When fresh local evidence is missing, provide the read-only preflight group
   immediately and explain which sync/cleanup group follows its review.
2. **Fresh target evidence.** Follow the existing actual-checkout verification
   rule before changing the user's clone or installation: hostname/OS, resolved
   checkout, origin fetch/push URLs, branch, HEAD, upstream, full working-tree
   status and Python environment. Never substitute agent-workspace evidence.
   Inspect returned output before dependent mutations and discuss unexpected
   differences. A failed guard is a stop, not permission to repair another host.
3. **Safe sync and authorized cleanup.** Use fast-forward updates and preserve
   local edits and unrelated branches. Verify ancestry before deleting an
   explicitly authorized merged branch; protect remote deletion against an
   unexpected changed tip. Do not force-reset, discard edits or delete branches
   just because a new task starts. Distinguish cleanup in the agent workspace,
   GitHub, chapman3 and Mac. Detect single-branch clones and explicitly fetch the
   delivered branch; explain any necessary change to their tracking configuration.
   If authentication fails, report the incomplete action without changing user
   credentials or requiring a graphical prompt/X11. Offer the applicable GitHub
   UI operation, then prune and verify after the user confirms completion.
4. **Complete command groups.** State the intended machine/project. Supply every
   command copy/paste ready in chat, with the OS/hostname guard first, exact
   verified checkout and applicable branch/SHA/clean/upstream checks. Use a
   subshell with fail-fast handling or equivalent dependent `&&` chaining; guard
   failure must stop the entire group without closing the user's terminal.
   Give one group at a time, then inspect its output before dependent operations.
   Respect normal notebook priority and lowered batch priority where applicable.
5. **Explicit delivery status.** Report branch/full commit or merge commit, PR,
   checks actually executed, remaining platform acceptance and any incomplete
   cleanup. Do not call written or unexecuted tests passing. Remote delivery
   does not synchronize the user's checkout, reinstall its wheel or update an
   already running kernel; state which of these actions actually occurred.
6. **Roadmap control.** Apply the bounded roadmap-execution rules above. Discuss
   and document changes of scope/order before implementation. Dependency
   qualification does not implicitly approve workflow refactoring, scientific
   changes or Python future-proofing. Publication of a plan is not acceptance
   of its pending implementation stages.

Use a dedicated branch and PR for the authorized item. Approval to implement
these instructions does not by itself authorize merging or deleting that new
branch; require the corresponding explicit instruction. Once a merge/cleanup
is explicitly authorized and its gates pass, do not request the same approval
again. Prefer the GitHub connector for repository delivery; user commands are
for their local synchronization/acceptance, not manual source editing on the
agent's behalf.

Report the problem addressed, changed files, checks actually run, unresolved
limitations and next decision. Keep working instructions and approved decisions
current as the project moves between phases.

## Delivery scope and future work

For the current OmegaCAM dataset, retain inputs and record processing versions,
configuration, calibrations, QC and product provenance. Scientific validation and
Phase 3 format/provenance validation are separate acceptance criteria. Verify the
applicable official ESO standard and validation tools when defining the exact
submission products; existing header-writing code alone proves no compliance.
Prepare a product inventory and release description. Archive submission and
publication remain actions requiring Fernando's explicit instruction.

After the operational OmegaCAM milestone, plan native mefpp multiprocessing and
support for single-CCD and single-CMOS reductions as separate work items. Audit
format assumptions and detector-specific calibration/noise behavior before
claiming single-detector support. Neither future item may delay the urgent
OmegaCAM production path without an explicit scope decision.
