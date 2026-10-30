# Developer documentation

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

[M1 cumulative closure review](m1-closure-review-2026-10-29.md): requirement checklist, native-to-WAD units/status crosswalk, accepted evidence and original M2 handoff. Closure recommended, owner decision pending; documentation only, with no repeated execution or activation.

M1 first concrete operation: [bias service](../architecture/proposed/m1/bias-service.md) and [grouped command/service mapping](../architecture/proposed/command-line-services.md). Agent synthetic numerical/ownership and focused regressions pass; actual Mac/representative Chapman C90 CMake builds and all five focused tests pass 5/5. See the [paired bias receipt](m1-bias-paired-results-2026-10-29.md); ready for owner review with no rebuild for this documentation receipt. Eclipse dependency OOM source finding #144 remains open; no installation or astronomical-data reduction.

M1 current increment: [explicit file/list request adapter](../architecture/proposed/m1/file-list-requests.md) joins ordered legacy list members to a declared base and consumes a supplied detector/asset catalogue, preserving duplicates and explicit BPM omission. Agent checks pass; actual Intel Mac/representative Chapman private C90 CMake builds and all four focused tests pass 4/4, including 51 CLI cases and seventeen input cases from two directories each. See the [paired receipt](m1-inputs-paired-results-2026-10-29.md). Ready for owner review; target C17/sanitizers remain unclaimed. Normal CLI routing and the first numerical service remain next; no installation or reduction ran.

M1 current increment: [resolved calibration roles and explicit per-detector BPM choices](../architecture/proposed/m1/resolved-calibration-bindings.md). Added owned descriptor validation/context copying; agent C90/C17, sanitizer and CLI regression checks pass. Actual Mac/shared Chapman private C90 builds and three focused tests now pass 3/3, including 51 CLI cases each; see the [paired receipt](m1-bindings-paired-results-2026-10-29.md). Ready for owner review. Connection to I/O/numerical services remains pending; no processing, installation or complete-M1 claim.

Current owner addition: [optional input BPMs throughout the chain; required variances from M6a](../architecture/proposed/bpm-variance-policy.md). The policy updates the target/WAD/template/roadmap and records existing wrapper blockers; no production behavior changed. PR #140 is accepted/merged at 6a4d4d8ec078a3360a5a743845dcbe752cbc84bd with Mac/shared Chapman synchronized and clean; the M1 resolved-operation bridge and concrete service remain next.

M1 next increment: [legacy CLI compatibility capture](../architecture/proposed/m1/cli-compatibility.md), including diagnostic bounds defect #139 and retained failure/correction evidence. Agent checks pass; actual Mac/shared Chapman checks pending.

M1 next increment: [owned request/context/result/error lifecycles](../architecture/proposed/m1/runtime-lifecycles.md), following accepted PR #137. Agent checks pass; new actual Mac/shared Chapman checks are pending.

Mandatory host selection: [Selected project tools — Mac and shared Chapman installations](selected-tools.md). Use the recorded absolute paths; consult the shared private-tool record before considering replacements or workarounds. Chapman3/4 are copycat hosts: no repeated per-host tool checks are needed.

M0/M0a prepared for review: [WAD/project contract package](../architecture/proposed/m0-m0a/README.md), synthetic linked examples, native ownership sketch and expanded source migration ledger. Thirteen negative controls pass in the agent environment; no native/ASDF/FITS execution. Source-only CLI finding --ksize is tracked separately as #133. Mac development, chapman4 later qualification; accepted main 0fa9eaf remains the host baseline.

WAD and ASDF project design: [Wenu Attribute Dictionary / ProcessingProject](../architecture/proposed/wad-processing-project.md), [revised target diagram](../architecture/proposed/pycavi-mefpp.md) and [M0a / updated milestones](../architecture/proposed/implementation-plan.md). Owner-directed documentation update, 29 October 2026; implementation remains pending.

Refactor delivery proposal: [detailed implementation milestones](../architecture/proposed/implementation-plan.md), covering the serial first pass, graph-ready records, optional mefppy and later parallel/incremental execution. No implementation starts from this proposal.

29 October 2026: see the [original architecture diagram](../architecture/original/pycavi-mefpp.md) and [target architecture proposal](../architecture/proposed/pycavi-mefpp.md). The proposed execution contract resolves inputs, calibrations, configuration and output/work destinations explicitly, without changing the caller's working directory or implicitly searching for files. Existing cwd-dependent behavior remains unchanged; this is design for discussion.

Next-stage direction approved, 29 October 2026: [amendment v2.9](native-roadmap-amendment-v2.9-2026-10-29.md) authorizes analysis/design of mefpp subroutines, typed TOML configuration subsets, ASDF processing metadata referencing FITS-resident images, parallel-ready and single-detector interfaces, notebooks 01/03 and an optional mefppy Python library. See the [initial source analysis](mefpp-refactor-analysis-2026-10-29.md). TOML/ASDF-with-FITS is now the owner-selected design direction; exact schemas/adapters/bindings and directory layout remain proposals. Read-only larger Chapman inventory is pending actual-host evidence; do not assume its reductions are complete. No production implementation, installation, data migration or reduction rerun begins from this analysis. Stage 2/2.1 stay accepted; other exploratory WISDG/retrieval/layout ideas remain unadopted.

Stage 2.1 endpoint revised by owner, 29 October 2026: [immutable amendment v2.8](native-roadmap-amendment-v2.8-2026-10-29.md) makes the gate **current mefpp/Pycavi reduction through notebook 04: native calibration/science preprocessing, Python normalization, solve-field and WCS-corrected MEF assembly**. Keep one filter and at most five equal-integration-time science exposures per instrument; all three WFI partitions are authorized for the same five exposures in total. Notebook 05 extraction/SCAMP, SWarp, photometric/illumination work, downstream QC and final catalogues are outside Stage 2.1 and deferred to later workflow work. Older v2.7/full-chain completion wording is historical and superseded; do not reopen it as a closure requirement.

Both bounded instrument sets have now passed the Stage 2.1 functional endpoint on the Intel Mac: native preprocessing, Python normalization, solve-field and WCS-corrected MEFs. OCAM: five r_SDSS exposures at 20 s, one partition, 160 solved detector images. WFI: five BB#B/99_ESO842 exposures at 89.9177 s across three partitions, 40 solved detector images. Pixel/input preservation checks passed. See the [returned-result receipt](stage2-1-functional-results-2026-10-29.md) for evidence paths and limits. The owner accepted Stage 2.1 on 29 October 2026 and authorized merging PR #130 and cleaning its merged branch. Next substantive work is Stage 2A review; preserve all baseline products and evidence. Preserve the failed first WFI SCAMP attempt outside this gate; #30/#131 remain open for later production work. No scientific/Phase 3 certification or automatic Stage 2A/refactoring is claimed.

Current S2-05 continuation, 28 October 2026: [supplied-bias BPM ownership gate prepared](stage2-bpm-supplied-bias-2026-10-28.md) from synchronized main bf1c6afe0063ae62833efd04a9109ae5a3982cef after merged PR #114. Separate synthetic driver/observer and additive float32 fixtures preserve production source and accepted exact masks/metadata; Python-only preparation checks pass, actual Mac execution pending. Retain failed/corrected preparation and every earlier run/archive/installation. Chapman3 workloads remain paused pending host/hardware status from the latest handoff. Full S2-05/#75, WFI/multiple extensions and applicable error/repeat/cache/target external diagnostic gates stay open. No departure, S2-06 advance, merge or branch deletion approved; mandatory review before Stage 2A/extraction remains. Earlier PR #114 pending statements are historical.


Latest S2-05: PR #114 populated-metadata qualification approved for integration and merged-branch cleanup; [Mac/Chapman3 evidence](stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md) retained. Full S2-05/#75 and target external diagnostics stay open; runs/installations preserved.

Latest S2-05: [populated metadata accepted on Mac and Chapman3](stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md); PR #114 awaits integration, full S2-05/#75 and target external diagnostics stay open.

Latest S2-05: [populated metadata verified on Mac; target checks prepared](stage2-bpm-metadata-mac-acceptance-2026-10-27.md). Full S2-05 and target external diagnostics remain open.

Next S2-05: [populated-metadata ownership checks prepared](stage2-bpm-metadata-2026-10-27.md), unchanged native code/pixels; actual Mac execution pending.

Latest S2-05: PR #108 baseline and PR #113 ownership correction approved for integration and merged-branch cleanup; [Mac/Chapman3 acceptance](stage2-bpm-chapman3-acceptance-2026-10-27.md) retained. Full S2-05/#75 and target external diagnostics remain open; preserve runs/installations.

Latest S2-05: [bounded BPM correction verified on Mac and Chapman3](stage2-bpm-chapman3-acceptance-2026-10-27.md); exact FITS products and ownership/accounting pass. PR stack awaits integration; full S2-05 and target external diagnostics remain open.

Latest S2-05: [corrected Mac BPM gate accepted; target runner prepared](stage2-bpm-mac-acceptance-2026-10-27.md). Exact products preserved, double-purge resources zero; target execution and broader S2 remain pending.

Latest S2-05: [ownership correction prepared for #109–#112](stage2-bpm-ownership-correction-2026-10-27.md); failed baseline retained, fresh actual Mac verification pending.

Latest S2-05: [failed Mac baseline inspected and attributed](stage2-bpm-baseline-evidence-2026-10-27.md), #109–#112; numerical checks pass, ownership repair awaits native qualification.

Next S2-05: [BPM ownership baseline prepared](stage2-bpm-ownership-2026-10-27.md), unchanged accepted driver/fixtures, Mac native execution pending.

[Full agreed S2 milestone and current status](stage2-memory-qualification-2026-10-27.md#declared-test-matrix): departures require prior agreement with Fernando and documentation before implementation.

Latest S2-04: [Mac and Chapman3 split/cache acceptance inspected](stage2-split-chapman3-acceptance-2026-10-27.md). All 80 Mac and 40 target pairs pass; PR #105 awaits review/integration. Broader Stage 2 and target external diagnostics remain open.

Latest S2-04: [Mac split/cache acceptance inspected; target runner prepared](stage2-split-mac-acceptance-2026-10-27.md). All 80 pairs pass with controlled cache attribution. Chapman3 verification and broader Stage 2 remain pending.

Latest S2-04: [repaired observer inspected; cache-attribution control prepared](stage2-split-observed-evidence-2026-10-27.md). All 80 functional pairs pass; the resource gate remains failed in 64 cases. Fresh control and target verification pending.

Latest S2-04: [inspected first baseline and descriptor-observer repair (#106)](stage2-split-baseline-evidence-2026-10-27.md); fresh actual-Mac observation remains pending.

Current Stage 2 increment: [S2-04 split ownership baseline](stage2-split-ownership-2026-10-27.md), prepared after S2-03 integration; actual Mac qualification pending.

Latest S2-03: [Mac and Chapman3 bounded correction acceptance](stage2-cli-chapman3-acceptance-2026-10-27.md); PRs #102/#104 await integration.

Latest S2-03: [Mac correction accepted; Chapman3 verification prepared](stage2-cli-mac-acceptance-2026-10-27.md).

Current S2-03 correction: [bounded getopt name matching (#103)](stage2-getopt-correction-2026-10-27.md), prepared for actual Mac verification; failed baseline remains retained.

Current Stage 2 increment: [S2-03 CLI ownership baseline](stage2-cli-ownership-2026-10-27.md), Mac baseline completed with parser defect #103; [inspected failed evidence](stage2-cli-baseline-evidence-2026-10-27.md) is retained after integration of #97/#98/#100/#101.

Current Stage 2 acceptance, 27 October 2026: [context cleanup #99 is verified](stage2-context-chapman3-acceptance-2026-10-27.md) on Mac C90/C17 (48 cases) and Chapman3 C90/C17 (24 functional/accounting cases). Tool controls, failed baseline and corrected evidence are retained. PR stack #97/#98/#100/#101 awaits integration. #75 and the remaining Stage 2 normal/error/repeat, cache, allocation-failure and mapped/swap gates stay open; Chapman3 sanitizer/leak-tool coverage is not claimed. Next after integration is S2-03 CLI/parser/engine failure ownership, not Stage 2A/extraction. Keep run directories, archives and installations preserved. This status supersedes earlier pending context-cleanup statements below.


Next: [Stage 2 memory/ownership matrix](stage2-memory-qualification-2026-10-27.md). #90 is resolved; broader #75 and leak qualification remain open.

BPM cleanup #90, 27 October 2026: [Mac instrumented acceptance](bpm-cleanup-acceptance-2026-10-27.md) and [Chapman3 target acceptance](bpm-cleanup-chapman3-acceptance-2026-10-27.md) are verified; PR #96 is merged. Broader memory/scientific gates remain open.

For ordinary installation, use the [short user guide](../installation.md).
This directory contains development policy, detailed procedures and evidence.
The latest dated policy/acceptance record controls; old audits remain historical.

## Current work and policy

- [Agent instructions](agent-instructions.md)
- [Overall roadmap](roadmap.md)
- [Native modernization roadmap](mefpp-modernization-roadmap-v1.md)
- [Current native candidate and remaining gates](native-cmake-candidate.md)

## Installation and portability

- [Native build/install/qualification guide](native-installation.md)
- [Configure/make frontend status and target gate](native-frontend.md)
- [Detailed Python installation and packaging](installation.md)
- [Intel Mac native build/install acceptance](native-mac-build-install-acceptance.md)
- [Mac/Linux package-manager assessment](native-distribution-options.md)
- [Pycavi portability audit](pycavi-portability-audit-2026-10-21.md)
- [External tools and library options](external-tools-and-library-options-2026-10-21.md)

## Architecture and native design

- [Overall architecture](architecture.md)
- [Current mefpp architecture](mefpp-current-architecture.md)
- [Native build specification](native-build-specification-v1.md)
- [Native architecture audit](native-architecture-audit-2026-10-25.md)
- [Native installation audit](native-installation-audit-2026-10-25.md)
- [Single-detector/parallel audit](detectors-and-parallel-work-audit-2026-10-21.md)
- [Thin notebooks and script interface review](pycavi-two-interface-review-2026-10-21.md)

## Workflow evidence and corrections

- [Mac CP Pup pilot](pilots/mac-cp-pup-2017-03-13/README.md)
- [chapman3 CN Ori pilot](pilots/chapman3-cn-ori-2017-03-11/README.md)
- [Chebyshev correction and pilot](chebyshev-repair-2026-10-21.md)
- [Catalogue execution correction](catalogue-repair-2026-10-21.md)
- [Gaia IDs](gaia-source-id-correction.md)
- [Catalogue integer IDs](catalogue-integer-correction.md)
- [Illumination null masks](illumination-null-mask-correction.md)
- [Kriging readback](kriging-readback-correction.md)
- [Kriging application](kriging-application-correction.md)

## Historical background

- [Original audit, 20 October 2026](audit-2026-10-20.md)
- [Previous Mac installation/workflow](mac-installation-history-2026-10-20.md)
- [Repository migration](migration.md)

This is the first navigation reorganization. Before moving dated files into
physical subdirectories, inventory and update their inbound links, AGENTS and
guide references together; preserve stable entry points. New developer documents
must be added to the appropriate topic, not appended as an undifferentiated list.

The immediate scientific goal remains OmegaCAM products for ESO Phase 3.
Functional acceptance, scientific validation and archive compliance are distinct.
Native mefpp remains serial; later threading/accelerators follow reviewed gates.

- [Native configuration/failure correction and 26 October evidence](native-failure-correction-2026-10-26.md).
