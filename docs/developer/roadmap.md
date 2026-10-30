# wenu-imaging roadmap

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

29 October M1 implementation increment: owner instructed “Proceed” with best programming practices. The [owned configuration snapshot](../architecture/proposed/m1/config-snapshot.md) implements isolated typed config copying/lifecycle and deterministic inspection, with agent C90/C17 units, allocation controls and real PAF-constructor comparisons passed. Intel Mac/Chapman and full CMake checks remain pending. M1 remains in progress: request/context/result lifecycles and later numerical extraction are not implemented; no engine/installed payload/notebook/scientific/QC change. Earlier pending-native wording below records the preceding receipt.

29 October M1 start: owner instructed “next” after PR #136 acceptance/merge and clean Mac main 7341c895e9e1eb7008915e1e2cf961532b7eb8a6. First lock [retained OCAM/WFI text configuration/command inputs](m1-effective-input-baseline-2026-10-29.md), then map effective settings and implement typed state/lifecycle helpers through the PAF adapter. The prepared collector does not read FITS, execute native processing, install packages or change science/QC definitions. Actual target collection/interpretation and native implementation remain pending; preserve accepted runs and completed dependency qualification.

29 October owner naming/QC requirement: calibration creation entry points are mef_cal_bias, mef_cal_bpm, mef_cal_dark, mef_cal_fringes, mef_cal_linearity, mef_cal_domeff, mef_cal_skyff and mef_cal_mff; requested calibration application/science preprocessing is mef_sci_pp. Add an explicit qc stage (M5a) and shared QC result conventions to the M1 template. Bias examples are mean level, RON and overscan mean level; numerical definitions, required inputs, regions, units/estimators, aggregation and thresholds are TBD. Preserve required intermediate/overscan information. No new quality rejection, automatic characterization/header injection or numerical algorithms are implemented by this contract update. See [the template and service names](../architecture/proposed/m1/README.md).

29 October owner requirement: M1 must first provide a [common ANSI C90 subroutine template](../architecture/proposed/m1/README.md) that subsequent modules reuse. Standardize context/result/error/status conventions, validation/calculation separation, explicit ownership and one cleanup path; keep numerical payloads operation-specific and use optional callbacks only where needed. The prepared scaffold reuses accepted M0 types and passes strict-C90 syntax checking on the agent; helper implementations, lifecycle tests and actual Mac/Chapman runtime remain the M1 gate. No numerical extraction, new global state or universal dispatch framework is introduced by this review template.

29 October 2026 owner decision: vendor the two tested tomlc17 source files, with the MIT license, exact revision/hash provenance and update policy, in [third_party/tomlc17](../../third_party/tomlc17/README.wenu.md). The approved source import is byte-identical to pinned upstream 4987cf895df61f702d19e3481f34b032ab29ed3a and both qualified host copies. Vendoring is the selected distribution method; build-target/configuration-adapter integration remains the planned implementation stage. Preserve C90 public/numerical contracts, compile the dependency in C99 when integrated, and retain explicit UTF-8 validation/one-time option initialization/shared TOML 1.0 bounds. No production installation, PAF replacement or processing begins from this source import.


Native TOML scope added by owner, 29 October 2026: include pinned tomlc17 qualification in the current dependency work (PR #135). See [native TOML qualification](native-toml-qualification-2026-10-29.md). Private actual-host Mac/Chapman4 builds, TOML 1.0 agreement/error controls, ownership checks and a strict-C90 caller boundary are authorized. The C99 exception is scoped to the external parser dependency and test-only glue; existing native source/public contracts retain C90. Production adapter exceptions/adoption/integration remain explicit later decisions. First collect actual compiler/tool/SDK/libc evidence; no compiler/system/production upgrades, PAF replacement or reductions. Preserve the completed ASDF trial; do not rerun it for this addition.


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

Earlier dated pending statements below are historical where superseded by this update and the linked acceptance records.

Mac robust BPM update, 26 October 2026: C90/C17 reconstruction without a separate
master bias exactly reproduces all historical mask pixels and 34122 bad pixels.
Complete raw-header differences are reviewed generated ORIGFILE values only.
See the [acceptance and next masking-test contract](native-qualification-and-roadmap-2026-10-26.md#mac-robust-bpm-reconstruction-acceptance).
The next bounded task characterizes flagged-pixel exclusion with unflagged
controls; current unweighted configurations are not an exclusion guarantee.
Threshold quality, #90/#91, memory and scientific gates remain open.

## Current agreed sequence and Phase 3 design audit — 26 October 2026

The native roadmap is now [revision 1.6](mefpp-modernization-roadmap-v1.md).
Finish bounded Stage 1 qualification, then Stage 2 memory/ownership; stop for
a review with Fernando after Stage 2 before representation work or component
extraction. Start an early ESO Phase 3 instructions/requirements audit alongside
qualification so upstream processing and metadata changes account for delivery
requirements from their design. Audit output and compliance remain pending.

ESO_Phase3 is a proposed versioned reduction/product profile, allowing other
profiles later. It may constrain upstream processing, products, metadata,
associations and validation; it is not merely output header decoration. Keep
common scientific correctness independent of the chosen profile. No profile
engine, new algorithm, variance implementation or compliance claim is introduced.

Stage 2A defines science/variance/quality, gain/RON and covariance semantics;
Stage 3 preserves those associations across components. Stage 4A–4D implement
detector characterization/metadata, calibration/science uncertainty, mask/weight
adapters and final-product uncertainty, respectively. Preserve background/total
variance distinctions and actual coadd-method uncertainty. Include the later
NB_659/r_SDSS PSF/transmission-aware continuum-subtraction design after its
uncertainty foundation. Packaging and accelerator choices remain deferred.

The [current qualification and decision ledger](native-qualification-and-roadmap-2026-10-26.md)
records merged main/branch cleanup, today's calibration comparisons and shared
normalization, BPM provenance, actual saved unweighted tool configurations, and
remaining #90/#91/#13/#75/#24 gates. Earlier dated pending statuses below are
historical where superseded. Development/corrections are on the Mac; Chapman3
verifies target behavior. No normal installation or engine selection changed.


## Chapman3 installed-wrapper acceptance

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

## Chapman3 current acceptance and permanent tool location

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

## Chapman3 Stage 1 build correction, 26 October 2026

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

## Bounded Intel Mac correction acceptance, 26 October 2026

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

## Current Stage 1 correction, 26 October 2026

Fernando reports exact historical native CP Pup pixels in all 32 detectors for
C90 direct, C90 installed Pycavi wrapper and C17 direct runs; shapes/types/identity
match, raw headers differ only in the generated primary ORIGFILE timestamp,
and protected files remain unchanged. These runs used prebuilt calibrations.
Both language modes then failed the missing-PAF/input/invalid-satmax negative
cases. Stage 1 remains open. Fernando authorized the focused configuration,
exit-status, split-error, context-ownership and Python propagation correction
described in [the correction record](native-failure-correction-2026-10-26.md).
Implement and verify this bounded slice before dependent qualification. Preserve
the working engines and accepted products; Mac rebuilt-candidate/installed checks,
renewed observational comparisons and Chapman3 remain pending. Calibration-building,
memory and wider roadmap gates are not closed by these source tests.

## Current gate: CP Pup native regression preflight — 25 October 2026

The normal Mac C90 installation interface is accepted at source
7c5238f848284033bcef416ec5970a8004550afd: configure/make/install, optional four-entry
CTest suite, exact installed BPM/payload/provenance/CLI, repeat install and
DESTDIR passed. See [frontend acceptance](native-frontend.md). This completes
bounded #84; no more installation tests are needed for that gate.
Next: verify retained raw/master/PAF/native-reference hashes and the installed
candidate, prepare fresh copies, then compare all native detector pixels/metadata.
Historical engine/configuration remain selected/unchanged. Broader Stage 1,
chapman3 and memory gates stay open. Packaging remains a deferred TODO.
Earlier frontend-pending statuses below describe the preceding implementation phase.

## Current priority: finish the normal installation interface — 25 October 2026

Fernando authorizes restoring ./configure; make; make install before the next
CP Pup step. Implement thin root/component frontends over the existing CMake
graph/installer, automatic platform tool selection and clear prerequisite/error
handling. Keep compiler overrides and direct CMake available; developer validation
belongs in optional make check and docs/developer, not the ordinary user route.
[Frontend status](native-frontend.md) records agent evidence and pending actual-Mac
qualification. The native numerical source and working installations are unchanged.
After this frontend gate, resume the CP Pup preflight/comparison and remaining
Stage 1/chapman3 work below. pip-versus-Conda remains a deferred TODO.

## Current next work and deferred packaging TODO — 25 October 2026

Fernando defers the pip-versus-Conda/micromamba decision. Keep it as a TODO:
compare platform wheels and Conda recipes for native mefpp and integration with
Pycavi; assess dependencies, resources/relocation, Mac/Linux artifacts, chapman3
glibc compatibility, fresh-user installation and maintenance before selecting a
distribution route. Local package tests can precede any public hosting decision.
No package prototype, publication or manager installation starts now.

Resume the existing Stage 1 qualification, in this order:

1. Read-only preflight of retained CP Pup raw/master/PAF/native-reference hashes,
   detector layouts and both qualified private installed candidates.
2. Prepare fresh copies, then compare native C90/C17 candidate outputs with the
   historical native output across all detector pixels and relevant metadata.
   Keep Python normalization separate; do not invent tolerances to pass differences.
3. Qualify the installed Pycavi wrapper and remaining relevant fixture/failure
   gates; then repeat build/install qualification on chapman3 with its verified
   compatible toolchain. Do not declare Stage 1 complete from the Mac CLI alone.
4. Memory qualification remains the next major stage after build/install gates.

This is functional regression work, not scientific parameter tuning. Preserve
working engines, configurations and observations; no normal engine switch,
merge or cleanup is implicit. Packaging and physical documentation relocation
do not block the current native comparison.

## User installation and documentation review — 25 October 2026

Fernando requests a short [user installation guide](../installation.md), detailed
procedures under docs/developer, and clearer topical navigation. The native
source-install gate passed on Intel Mac; simple end-user distribution is a
separate Stage 1 usability deliverable. Review
[Mac/Linux package-manager options](native-distribution-options.md), with
pip platform wheels versus Conda/micromamba both deferred for evaluation; no
user-distribution package manager is selected. No recipe, channel, binary publication or new dependency
is selected/installed by this review. Qualify relocation, platform/glibc compatibility
and fresh-user installation before advertising a one-command install.
A physical developer-document move follows an inbound-link inventory; topic-grouped
navigation is the first change. The temporary review pause ended with Fernando's
instruction to defer packaging and resume the current native qualification.

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

## Stage 1 isolated candidate — 25 October 2026

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

## Stage 0 build specification — 25 October 2026

[Native build specification v1](native-build-specification-v1.md) defines the
candidate targets, payload and regression fixtures for roadmap 1.2. Mac synthetic
CMake/CTest 3.29.3 and Xcode Apple Clang 15 passed strict C90/C17 build/link and
2 CTest checks; mefpp was not built, run or installed. Initial candidate minimum
is CMake 3.29, with explicit Xcode tools and Unix Makefiles. Real native source
qualification, observational manifests and compatible chapman3 toolchain remain
pending. Stage 0 is not declared complete by this small synthetic success.

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

## Native modernization roadmap version 1 — 25 October 2026

The first [native roadmap](mefpp-modernization-roadmap-v1.md) records Fernando's
revised priorities, completion gates, proposed tools, component/calibration
contracts, platform requirements and revision procedure. Its companion
[current architecture](mefpp-current-architecture.md) describes observed mefpp
structure separately from the target design. These are review documents; no
implementation or target install is authorized by their publication.

Planning order: reproducible serial build/install (Mac, then chapman3), memory
correctness, components/new calibration services, single-detector CCD support,
parallel mosaics, native Windows qualification and CMOS services last. Windows
portability begins with the build design. Preserve common mosaic normalization;
include shutter/gain/RON characterization, measured/default science metadata
and fringe construction with separate Python subtraction. Earlier stages below
remain the wider project context; the dated native sequence controls this newly
prioritized work and does not close Python, science or Phase 3 gates.

## Architecture audit and full roadmap before native modification, 25 October 2026

Fernando explicitly requires the [native architecture audit](native-architecture-audit-2026-10-25.md)
before a full roadmap, and that roadmap before implementation. This supersedes
starting the qfits move/build fixes immediately after the installation audit.
#73 tracks the architecture/modern-practice assessment and Eclipse usage map.
The audit includes 99 compile-only analysis units and static symbol/call
evidence: Eclipse 79 built units, 33 potential-call units and 53 conservative
object-closure units; qfits 18/12/14. These are agent Linux analysis results,
not target linking/runtime coverage or authorization to delete code.

The requested future component candidates are bias, BPM, non-linearity
determination and application, dome flat, sky flat, master flat and science
processing, with shared detector/image/FITS/configuration/QC/provenance services.
Existing functions provide partial foundations; non-linearity routines exist
in Eclipse but are not reached by the current mefpp workflow.
The next deliverable after audit review is the full roadmap: explicit component
contracts and dependency decisions, build/install options, behavior-preservation
tests and Mac-first/chapman3 acceptance. No framework/language rewrite, API,
scientific dependency order or component implementation is selected yet.

Keep #64/#65–#71 installation work and new #74–#76 source findings recorded,
but make no native source/layout/build/installed-selection changes until the
roadmap is reviewed and agreed. The earlier installation-first sequence below
remains the background objective, subject to this new review gate.

## Approved reordering: mefpp/qfits installation audit first, 25 October 2026

Fernando explicitly brings point 5 forward now: audit mefpp and qfits build/
installation, establish a reproducible Intel Mac build/install first, then
chapman3, and move qfits under mefpp. The first deliverable is the
[native installation audit](native-installation-audit-2026-10-25.md), tracking
[#64](https://github.com/fselman/wenu-imaging/issues/64) and findings #65–#71.
The report records source inspection and disposable agent-host probes, not a
successful target build. No source layout/algorithm or working installation
was changed by this audit.

Current sequence: read-only Mac compiler/install inventory -> bounded bundled
qfits/build/install correction -> isolated Mac build/install/smoke acceptance ->
chapman3 inventory and corresponding acceptance -> resume the remaining
thin-notebook/config-script/Python-audit stages. This overrides earlier
instructions to defer all native work until after those stages only for the
bounded installation task; the full numerical/detector/scientific mefpp audit
does not automatically begin. Preserve the working engines, source history,
licenses, configs, static masks and all accepted reduction data.
Recommended destination is mefpp2/qfits5 with one canonical qfits source copy
and explicit qfits -> Eclipse -> mefpp build dependencies. A bare directory move
is insufficient; prefix/staging, failure propagation, compiler selection,
resources, clean rebuilds and real checks must be qualified.

No compiler/library upgrades, runtime parallelization or scientific tuning is
included. Target changes are isolated until accepted and explicitly selected.
The prior thin-notebook-first handoff below is historical where it conflicts
with this user-approved reordering. PRs #57/#60/#63 are merged and cleaned;
Mac main was verified at 2cd54c1206ccb7b68b2eb0a5f70d9b28f1188cde.

## Intel Mac selected functional paths 03–09 accepted, 25 October 2026

The [CP Pup Mac pilot](pilots/mac-cp-pup-2017-03-13/README.md) records installed
functional checks for one 20 s r_SDSS exposure and 32 detectors, through native
reduction/normalization, solves, SCAMP (eight PDFs), single-exposure SWarp,
DR3/GSPC calibration, 07b, both model fits/readback, catalogue applications and
twelve decoded catalogue QC PNGs. Baseline: 47543 rows, 14654 exact Gaia
associations / 14652 distinct IDs, with 32889 missing masks. Both correction
writers preserve masks/unrelated data and have byte-identical repeat calls.
Source/settings, product hashes, record paths and per-stage limits are linked.

This accepts selected installed-library paths, not full notebook orchestration
or all Mac/platform/science gates. #56/#59 are target-qualified and closed;
#61 is a closed investigation of first-solution repeatability/rounding, not a
new correction or arbitrary-repeat convergence claim. #62 remains open with
the current negative Gaussian RANGE and historical fixed-nugget ~0.015 feedback.
Scientific tuning waits until all fields are reduced; no new defaults or
model ranking are accepted. SCAMP's DR2 astrometric reference is distinct from
the DR3/GSPC photometric calibration.

Next: record/review/integrate qualified changes when instructed, then agree the
next bounded software task under the existing thin-notebook -> shared-library
scripts -> Python-library audit -> mefpp sequence. Multi-exposure/multi-filter
Mac acceptance remains pending; inventory and agree any next dataset run before
launching it. No refactor, processing, upgrade, merge or cleanup is authorized
by the documentation update. Independent accuracy, flux/error consistency,
#37/#38/#51, native gaps, WFI, other platforms and Phase 3 remain separate.
The dated 24 October sections below are historical: PRs #43/#45/#47/#50/#52
were merged and cleaned on main0591ba0; PRs #57/#60 remain separate review work.

## Authorized merge/cleanup handoff, 24 October 2026

Fernando authorized integrating the five qualified PRs into main in order:
#43 reader/08c bindings, #45 Gaia identity recovery, #47 crossmatch integer IDs,
#50 FITS null-preserving illumination writes and #52 cubic Kriging application.
The last head carries all acceptance/QC evidence. Verify final main tree/ancestry,
then delete only those merged branches and synchronize the inspected chapman3
checkout. The existing installed wheel already matches the qualified code; no
reinstall or data processing is needed. This is integration/cleanup authorization,
not scientific/model acceptance, full orchestration, Mac or Phase 3 qualification.
Deferred #51 and broader open investigations remain open; older handoffs below
are historical.

## Selected OmegaCAM functional paths through notebook 09 passed, 24 October 2026

Kriging application and its four existing QC PNGs passed, completing baseline/
Chebyshev/Kriging functional catalogue checks for this isolated pilot. Twelve
QC PNGs across the three catalogues were generated and decoded; all original
and staged catalogue hashes remain unchanged. #48 is closed; code remains
298d2867c21fa2734874e1562ff28696147f7d06. No new query/refit/image correction
or independent scientific/model acceptance occurred. Evidence:
notebook09-kriging-qc-saittxaz/output-check.json and the application records below.
PRs #43/#45/#47/#50/#52 are qualified, unmerged and available for review; no merge
or cleanup has been authorized for these branches. Mac testing, independent
accuracy/uncertainty, SkyMapper comparison review, complete notebook orchestration
(#37/#38), native metadata and Phase 3 work remain separate. #51 is a deferred
nonblocking guard finding. Earlier plans below are historical.

## Kriging application accepted; catalogue QC next, 24 October 2026

#48 is closed after installed and actual-model application acceptance. Fresh
notebook09-kriging-s0e1demx retains 16459 rows, 3718 exact IDs/12741 null masks,
all unrelated columns/metadata and repeat-call byte identity. Direct cubic
predictions and inherited default solver bounds pass for both unchanged 50x50
grids; baseline/Chebyshev/models are unchanged. Finish existing QC plots on a
fresh staged Kriging catalogue with unchanged r_SDSS/Gaia settings. This is
functional verification, not independent scientific or continuous-predictor
validation. #51 is deferred. PRs #43/#45/#47/#50/#52 remain unmerged; earlier
plans below are historical.

## Current Kriging catalogue application coordinate fix, 24 October 2026

Chebyshev application and all eight before/after QC PNGs passed; inputs remain
unchanged in notebook09-qc-h6o98cy8. Address confirmed #48 as the next focused
functional correction: use the stored physical 1..ORIG_W/H sample axes in the
Kriging catalogue application with correct (y,x) orientation and actual grid
shape. Retain cubic interpolation, its default solver, strict bounds, sign,
models, null-preserving writer and repeat/provenance guards. Do not substitute
the linear 08c reader or refit. Source/installed tests precede fresh target
catalogue application. #51 is deferred because current QC inputs are valid.

## Chebyshev application accepted; catalogue QC next, 24 October 2026

#49 passed installed and actual fresh-catalogue verification and is closed.
notebook09-chebyshev-6xb3rgu1 retains all 16459 rows, 3718 exact Gaia IDs and
12741 missing-ID masks; only the four expected magnitude columns per filter
changed. All unrelated column bytes/masks, complete extension metadata, model
provenance and repeat-call byte identity passed; baseline/models unchanged.
Continue the existing notebook 09 QC plots on separate staged before/after copies
with default r_SDSS/Gaia comparison settings. No new query/refit or scientific
acceptance. #48 Kriging application grid failure remains open. See
[writer acceptance](illumination-null-mask-correction.md). Earlier plans below
are historical; PRs #43/#45/#47/#50 remain unmerged.
Nonblocking QC missing-column guard finding #51 is recorded for later; check
both requested columns in the pilot preflight and retain valid-input behavior.

## Current illumination null-mask correction, 24 October 2026

Before applying models, correct #49: both catalogue correction writers rebuild
the FITS table and discard TNULL, exposing unmatched Gaia placeholders as IDs.
Update only magnitude field arrays; preserve integer masks, all unrelated data
and column metadata, existing numerical corrections and repeat/provenance
guards. Test actual writer bodies with real FITS, then installed/observational
copies on chapman3. Do not change the separate Kriging grid failure #48. The
verified baseline and all models remain immutable; no observational correction
has launched.

## Notebook 09 baseline acceptance, 24 October 2026

Installed correction and actual catalogue checks passed; #46 is closed. The two
extractions produced 17682 r_SDSS / 17937 NB_659 rows; existing filter matching
and cleaning retained 16459 paired rows. The baseline contains 3718 distinct
Gaia IDs, preserved exactly as int64/FITS K with correct null masks. All images
and reference CSV hashes are unchanged. Evidence: notebook09-catalogue-95xc1kyz
output-check.json. Continue functional illumination application on fresh copies
with explicitly recorded existing models; no refit, new query or independent
science acceptance. Separate Kriging application edge/grid defect #48 is open
and is not fixed by #41. PRs #43/#45/#47 are unmerged. Earlier plans below are
historical. See [the correction record](catalogue-integer-correction.md).

## Current notebook 09 integer-preservation fix, 24 October 2026

#44 recovery passed. Before catalogue construction, fix #46: crossmatch_catalogues
casts every shorter-table column to float64, rounding large IDs. Preserve integer
dtypes with masks for unmatched rows; retain float NaNs, current row anchoring,
nearest-neighbour selection, radius and all scientific settings. Notebook 09 must
use the exact-ID cache reader. Test actual function/notebook, then installed
Chapman3 and fresh observational output. No extraction or matching launched yet.

## Gaia identity acceptance; resume notebook 09, 24 October 2026

#44 is corrected and target-qualified. Installed source/ID regressions (8+8),
packaging/resource checks (10) and pip check passed. One bounded identity-only
query recovered IDs for both raw 6245-row and clean 981-row files per filter,
with maximum separation 0.0 arcsec in every file. Exact int64 CSV/Table/FITS
round trips, unchanged non-ID fields, clean/raw subset membership and original
hashes passed. Evidence: gaia-id-recovery-jh763zwi/identity-output-check.json.
Resume notebook 09 using the fresh recovered catalogue copies. No recalibration,
refitting or science-image change occurred; notebook 09 remains unqualified.
PRs #43/#45 are unmerged. See [the recovery record](gaia-source-id-correction.md).
The prerequisite plan below is historical.

## Current Gaia identity repair before notebook 09, 24 October 2026

08c corrected readback/plot checks passed both filters; #41/#42 are closed with
evidence, PR #43 remains unmerged. Notebook 09 preflight found #44: all 6245
SOURCE_ID values are missing in each production raw Gaia CSV. The production
method discards its ID fields during column removal/reindexing. Fix response
aliasing and exact integer CSV handling without changing query geometry or
photometric processing. Reject invalid legacy identity caches before reuse.
The inspected run directories contain no retained TAP result/job reference.
Prepare one bounded identity-only DR3/GSPC retrieval and traceable one-to-one
matching to existing cached coordinates; preserve every other CSV field and all
originals in fresh copies. Retain query, native result, job ID, mappings and
hashes; reject missing/ambiguous matches and floating identifiers. No catalogue
construction, recalibration, model refitting or science-data correction until
identities are verified. Keep #44 open pending target qualification.


## Current saved-Kriging readback correction, 24 October 2026

Both filters passed 08b fitting, grid serialization and basic plots in isolated
wrappers. The next 08c/readback check confirmed [#41](https://github.com/fselman/wenu-imaging/issues/41):
stored grid nodes are mapped inconsistently by the linear-interpolation reader.
Correct only the mapping to the actual physical sample axes, preserving saved
models and the linear interpolation method. Also correct the two 08c plotting
argument bindings in [#42](https://github.com/fselman/wenu-imaging/issues/42) using
explicit keywords; no fitting/model/selection policy changes. Test boundaries,
rectangular grids/fields, affine interior values, actual notebook call bindings
and unchanged input files, then verify the existing chapman3 models without
refitting. Keep #41/#42 open pending target verification. Notebook loop scope
#37, experimental state #38 and independent scientific validation remain open.
No correction is applied to science images or catalogues in this step.

The previous merge/preflight handoff below is historical.

## Notebook 08a accepted; merge/cleanup before 08b, 24 October 2026

Both filters passed notebook 07b functional QC and the installed 08a fit/export
checks in isolated wrappers. The saved degree-(5,5) polynomial agrees with
readback to roundoff. The notebook instead displays a second cubic RBF surface;
[#39](https://github.com/fselman/wenu-imaging/issues/39) records discrepancies in
positive-weight samples as well as uncovered corners. Correct only the display
to evaluate that same Chebyshev model directly on its grid, preserving fit,
selection, weights, degree and science data. Use a direct-labelled output name
and retain historical RBF products. Verify non-square/asymmetric grid orientation
and all orders, then regenerate fresh plots from saved models without refitting.
Chapman3 verification passed and #39 is closed. No extrapolation policy, new model,
nonlinearity correction or independent-accuracy claim is included. Notebook
last-filter orchestration #37 and experimental undefined-state #38 remain open.
The earlier notebook 07b resume note below is historical.

Fernando requested merge and cleanup of this completed work before notebook 08b.
The [display correction notes](chebyshev-display-correction.md) record source,
installed-wheel and fresh saved-model plot checks, with no refitting. Kriging
preflight passed against installed PyKrige 1.7.3/lmfit 1.3.4: 583 r_SDSS and 580
NB_659 unique positions, so the existing 2000-point limit needs no random subset.
The retained notebook parameters are Gaussian, maxlag 10000 pixels, 200 lags,
lmfit with unfixed nugget and empirical variogram, 50x50 display grid. The 1--20
mag and +/-1 residual selection explicitly clears the sigma-clipping mask.
The existing four-pixel-offset residual diagnostic is not cross-validation.
No variogram or Kriging fit has been launched. Proceed only after merge/cleanup;
no model selection, fitting-policy changes or dependency upgrades are included.

## Resume at notebook 07b QC

On 23 October 2026 Fernando authorized merging completed branches and cleanup,
then pausing until notebook 07b. Both r_SDSS and NB_659 have verified notebook
07 calibrated outputs; no calibration, normalization, solving or extraction
needs repeating. Seven saturation and ten metadata regressions passed against
source and installed wheel on chapman3, plus ten installed-package tests and
pip check. The [pilot record](pilots/chapman3-cn-ori-2017-03-11/README.md) identifies
products, hashes, query evidence and functional limits. #25/#33 are closed with
correction/verification comments; native #23/#24 remain deferred.

Fernando identified MAGSATL as too faint and requested two investigations:
[#35](https://github.com/fselman/wenu-imaging/issues/35) must relate the peak-pixel
threshold to full integrated PSF flux; [#36](https://github.com/fselman/wenu-imaging/issues/36)
must distinguish the stringent flat-field linearity limit from physical detector
saturation and raw ADC clipping throughout masks, catalogues and coaddition.
His recalled 16-bit boundary is 65535 raw DN, to verify per detector/readout; do
not assume it equals the usable linear/full-well limit. Future nonlinearity
correction must preserve raw clipping flags and respect its calibrated range.
These are future investigations, not new corrections in this walkthrough.
Independent photometric accuracy, Phase 3 acceptance and Mac testing remain open.

The sections below retain chronological task decisions and earlier evidence.

## Notebook 07 saturation-unit defect (#33)

The first r_SDSS ZPCalibration finished and passed finite/scaled-pixel,
WCS/timing/source-preservation checks: 981 catalogue rows, 584 usable
calibrators, DN2FLAM=2.10315823839273e-19. Its SATLEVEL remains in e-/s after
BUNIT changes to physical flux units. Trace confirms that parent metadata
appended after conversion overwrites the saturation value; native SATURATE
also remains unscaled. Correct this unit handoff as a necessary focused fix
within the existing functional walkthrough. Preserve the parent-average and
native saturation definitions, cumulative calibration factors and original
pixels/products. Reuse the completed calibration/query in a fresh header-only
copy; do not recalibrate it. Independent saturation/gain modelling and Phase 3
export redesign (#9) remain deferred. Target verification subsequently passed;
#33 is closed. See the correction notes and current handoff above.


## Current metadata correction, 23 October 2026

Fernando approved the bounded correction in [#25](https://github.com/fselman/wenu-imaging/issues/25):
propagate authoritative science exposure metadata into extracted/assembled
detectors, recompute MJD-END at double precision, and derive coadd timing from
all contributing science exposures. Reuse solved WCS and unchanged pixels in
fresh copies; do not repeat normalization, extraction or all-detector solving.
Keep SWarp equivalent EXPTIME/GAIN and scientific settings intact; TEXPTIME
records the sum of exposure times separately. No native rebuild is included.
The underlying native defects #23/#24 stay open for the later mefpp stage.
The immediate objective remains working chapman3 through all notebooks, then
retesting on Mac; no new photometric functionality or dependency upgrades.

The correction passed synthetic regressions, chapman3 installed-package checks
and real-product preservation/coaddition checks in both filters. Issue #25 is
closed with evidence. All four notebook 06 coadds (BACK_SIZE 128 and 2048,
SUBTRACT_BACK=Y, MEDIAN) passed functional checks. Notebook 07 subsequently
passed in both filters; continue at notebook 07b. The misleading second-pass
filename remains #31; independent scientific accuracy is not established.
Native #23/#24 and later Mac retesting remain pending. See [the correction notes](science-metadata-correction.md).

## Notebook 05 executable detection fix, 23 October 2026

The ongoing functional notebook walkthrough reached SExtractor discovery after
all ten notebook 04 pilot exposures passed solving/MEF assembly checks. On
chapman3, `/usr/bin/sex` returns `SExtractor version 2.19.5`; the installed PAPI
wrapper incorrectly requires the alternative spelling `Source Extractor`.
The first extraction block stopped at discovery, before copying an image or
launching extraction. The focused correction accepts both banner spellings,
preserving candidate order, explicit-path selection and the bytes version return
contract. It changes no extraction parameters, dependency versions or engines.
Chapman3 installed-wheel checks subsequently passed: five banner regressions,
ten packaging checks, pip dependency consistency and actual automatic/explicit
SExtractor discovery. Records: `~/wenu-sextractor-fix.19w6fdss`.

The first real extraction then stopped during config generation because the
legacy PAPI config schema does not include the explicitly requested `NTHREADS`.
Route this option through PAPI's existing `ext_config` native-command mechanism
when supplied to the notebook helper, leaving absent-option defaults unchanged.
Six regressions pass in the agent environment, including config generation,
the native command's `-NTHREADS 1` argument and catalogue renaming with the native
execution mocked. The failed working copy is preserved at
`~/omegacam/testing/wenu-imaging-test/notebook05-r_SDSS-28gx2t5e`;
no native extraction was launched. The thread correction was subsequently installed and verified on chapman3;
all ten pilot exposures passed extraction/SCAMP with checked 32-detector outputs.
The two SExtractor defects are closed with evidence in #26/#27.
Preserve existing solved MEFs and continue with a fresh working copy;
do not repeat normalization or solving. The later efficiency plan is not being
implemented by this compatibility fix.

## Controlling sequence clarification, 23 October 2026

Fernando approved a ticket for each defect and a correction/verification comment
before closure. The [walkthrough defect register](walkthrough-defects-2026-10-23.md)
links the current tickets. The approved immediate metadata correction is #25;
the native timestamp and precision causes (#23, #24) remain deferred to the
mefpp stage. Ticket creation does not expand implementation scope.

Future requirement requested by Fernando: [provisional photometry and explicit
calibration methods](provisional-photometry-plan-2026-10-23.md). Plan Astromatic
photometric processing plus an instrument/filter/focal-plane/detector model for
a labelled provisional flux scale, later refined through an explicitly named
method/release (Gaia DR2, Gaia DR3/GSPC, standard stars or another specified
method). Define model validity, units, cumulative factors, provenance and QC;
reuse canonical measurements and prevent double normalization. This is future
work within the agreed Pycavi/mefpp sequence, not implementation now. Continue
the current functional walkthrough with SCAMP photometry disabled and the
existing Pycavi zpcal path. Implementation details and scientific acceptance
criteria require later agreement.

Notebook 05 target evidence: all ten CN Ori pilot exposures now have checked
SExtractor/SCAMP outputs: 32 detector groups and finite sampled WCS per exposure,
XML reports and eight PDFs with basic complete framing, with inputs unchanged.
Jobs were sequential at niceness 10 with one native thread. Two focused wrapper
fixes are on `fix/sextractor-banner` at `1927166644606567b374a23ff5437b248b9b7029`;
six regressions and ten installed-package checks passed on chapman3. Missing
PLplot 5.10.0 plotting data was extracted locally without modifying system
packages. No independent astrometric accuracy or rendered-PDF assessment is
implied. Continue at notebook 06; do not repeat normalization, solving or source
extraction. The pilot README records the evidence paths.

Source tracing confirms the current SCAMP wrapper uses SOLVE_PHOTOM=N and
photometric calibration belongs to Pycavi notebook 07. SWarp 2.38.0 replaces
zero FLXSCALE with unity and warns; verify that behavior in the actual coadd
without enabling SCAMP photometry or rewriting its headers. Notebook 06 has two
passes (BACK_SIZE 128 and 2048), both SUBTRACT_BACK=Y; the second output's
`coadd_nobacksub` label is inconsistent with its settings. Preserve the effective
settings during characterization and resolve naming/scientific policy later.

Notebook 04 target evidence: all ten CN Ori pilot exposures (five r_SDSS and five
NB_659) passed the installed full runner with one worker at niceness 10: 320
successful detector solves, ten assembled MEFs, exact detector-pixel preservation
and unchanged inputs. Records are in the pilot README. This is functional
evidence, not a real-sky accuracy or multiworker-failure assessment. Notebook 05
follow-up results are recorded above; no repeated normalization/solving.

Fernando requested the [mosaic astrometry efficiency plan](mosaic-astrometry-efficiency-plan-2026-10-23.md):
one canonical SExtractor measurement pass with catalogue reuse; a validated
per-filter focal-plane baseline propagated into mefpp headers; only 1–3 detector
solves for exposure pointing; explicit review of SCAMP mosaic and SWarp grid/
resampling/photometric settings; and a QC script monitoring deviations from that
baseline. Define extraction units across exposures/coadds and validate detector
stability, model freedoms, fallback and scientific equivalence before adoption.
The recalled `FIX_FOCALPLANE` is a SCAMP MOSAIC_TYPE, not a SWarp setting.
This is a planned optimization in the existing Pycavi/mefpp sequence, not a
change to the current walkthrough, running jobs or scientific defaults.

Latest user direction: Fernando declined a separate lunar/site-data check now
and instructed continuing through the whole notebook sequence before deciding
what further work is needed. Resume the existing OmegaCAM functional walkthrough
at notebook 04 (astrometric solving), then SCAMP, SWarp and zpcal. Lunar/site-data
belongs to zpcal and remains deferred until that stage. This revises the earlier
dependency-first stopping rule for this walkthrough; it does not declare the
dependency baseline accepted or start general thinning/refactoring, replacement
or the systematic scientific library/mefpp audits. Use the existing installed
library, isolated pilot outputs, explicit worker limits and batch niceness >=10;
keep the interactive kernel at zero. Inspect existing output locations before
running or assembling anything, preserve prior products, and distinguish
individual-solver checks from notebook orchestration and full MEF validation.

After PR #18 merge and verified chapman3 cleanup at `9ee7ff9`, Fernando approved
the read-only [OmegaCAM requirements map](omegacam-dependency-map-2026-10-23.md).
It connects notebook imports/calls to Python/native/data/service requirements
and existing evidence. It identifies remaining Gaia DR3/GSPC, SkyMapper comparison,
lunar/site-data, SCAMP PDF and platform/provenance checks without executing those
paths or changing software. Further bounded checks need defined acceptance
criteria; the dependency gate remains open and the workflow audit has not started.

Fernando explicitly approved proceeding with Gaia DR3 after clarification that
notebook 07 already selects the Gaia DR3/GSPC library path. The approved bounded
task adds an opt-in dependency probe in `Pycavi2/tools`: one anonymous Astroquery
asynchronous join of the existing DR3 and GSPC tables, at most five sources in
a five-arcminute cone near CN Ori. Require the notebook's SDSS-band column
schema, valid matching source identifiers and nearby coordinates, and at least
one usable r/i photometric row. Preserve query, response, units, null counts and
job details. No photometric fitting, production-query change, catalogue migration,
package installation or scientific workflow audit is authorized by this check.
The five-arcminute probe radius is a diagnostic choice, not a production default.

Reported target result: the bounded Gaia DR3/GSPC probe passed on chapman3 at
`9724dd9` with five joined sources, all five usable in r/i, maximum separation
4.367 arcmin and worker exit zero at niceness 10. Three u-band and four
radial-velocity entries were missing and retained as such. Exact query/response
identities are in the dependency inventory. This completes that retrieval probe,
not photometric calibration, production conversion or the overall dependency
gate; no package, saved setting or scientific workflow change was made.

Following acceptance and merge of the offline SCAMP check, Fernando instructed
the bounded live-reference requirement check to proceed. Compare existing and
advertised VizieR routes with tiny capped Gaia DR2 queries, then test SCAMP's own
retrieval/parser in one small field with fitting disabled. Keep this reusable,
explicitly opt-in and separate from deterministic offline checks. Do not change
saved server/catalogue choices, production wrappers or scientific data. A service
probe does not complete the workflow audit or claim real-sky fit accuracy.

Reported chapman3 result: the native live-reference check passed on 23 October
at niceness 10 with one thread, returning three Gaia DR2 positions within
0.511 arcmin and preserving its input. Native reference-table display-format
warnings are retained in the dependency inventory. This completes the bounded
retrieval check, not the complete dependency gate or workflow audit. No saved
server/catalogue choice was changed; Mac/Ubuntu execution remains untested.

Current bounded dependency check: qualify installed SCAMP using a disposable,
synthetic single-detector FITS_LDAC catalogue and local known reference positions.
Exercise catalogue loading and a linear astrometric fit; require finite output,
recovery of the planted WCS displacement, unchanged input catalogues and recorded
commands/results. Reuse the portable dependency-check tool. Do not change Pycavi
wrappers, science data, reference-catalogue selection or live-service settings.
This follows Fernando's instruction to proceed with the SCAMP requirement check;
it does not begin the workflow audit or qualify real-sky accuracy.

Fernando approved the six delivery/synchronization instruction adaptations from
Wenu on 23 October, after chapman3 synchronized to `340347f` and the merged
feature branch was removed locally and remotely. This bounded documentation
item requires automatic delivery handoffs, fresh target evidence, safe sync and
authorized cleanup, complete guarded command groups, explicit delivery status
and strict roadmap control. It changes no processing code, dependency versions
or stage order. See the canonical agent instructions for the operational rules.

Fernando confirmed that the current phase establishes the packages and external
requirements on chapman3, with documented installation and verification evidence.
Complete the dependency acceptance gate before auditing or refactoring the
Pycavi workflow. Aim for the same Python and scientific-package versions on Mac,
recording necessary platform differences rather than assuming a portable lock.

The agreed five points remain: (1) package/establish Mac and Linux OmegaCAM
execution, (2) retire obsolete reduction scripts and thin notebooks, (3) derive
configuration-driven scripts calling the same library, (4) systematically audit
the Pycavi Python library, and (5) audit mefpp. Future-proofing Python follows
completion of those five points and working software, by a separately agreed
compatibility plan. WFI and the calibration-product QC library remain deferred.

Dependency qualification includes separately approved narrow integration fixes
and local Astrometry.net 0.98 installation. Its single-detector and two
32-detector tests call installed Pycavi `solvefield()` through diagnostic wrappers;
they do not validate full notebook orchestration, multiprocessing, MEF assembly
or astrometric accuracy. No replacement assembly implementation is authorized.
See [chapman3 dependencies](chapman3-dependencies-2026-10-23.md) for inventory,
evidence and remaining gate checks. This clarification controls where older
pending statements or sequencing below differ.

## mefpp detector-identity audit TODO, 22 October 2026

Fernando requests verification that reduction associates detector images by
chip identity (for example EXTNAME), rather than assuming the same ordinal
extension in every MEF. He recalls correcting positional matching; its current
status is unresolved. Trace raw inputs, bias, dome/sky/master flats, BPMs and
output assembly, including extension subsets. Distinguish name lookup from
merely logging names while loading by index. Check the existing source/history
and identify the source of the installed chapman3 binary where possible.
Use synthetic MEFs with deliberately permuted extension order to verify either
correct name matching or an explicit failure before processing; also cover
missing, duplicate and unknown chip names. Record this under the later mefpp
audit; no native implementation change is authorized by this TODO. Matching
order in the ten pilot science exposures is evidence for those inputs only.

Also audit native FITS header assembly: the installed chapman3 MEF BPM lacks
PCOUNT/GCOUNT in all 32 image extensions. Identify the writer/source generation,
check other products, and ensure future output meets the applicable FITS
requirements. Do not rewrite the installed mask as a side effect of preflight.

Fernando approved a focused Pycavi MEF BPM linking/preflight correction on
22 October. Keep mask pixels, native engines and notebook logic unchanged;
verify missing/broken links and invalid layouts using disposable FITS fixtures.

## Limited compatibility review authorized, 22 October 2026

Fernando approved bringing a focused part of the Pycavi library audit forward
before further chapman3 dependency installation. Review actual Python/API needs
against the historical environment and current code, preserving environments,
native engines and science data. See the
[compatibility review](python-compatibility-review-2026-10-22.md) for evidence and
pending checks. This authorizes review and isolated diagnostics, not a dependency
version change or the full scientific audit. The remaining stage order holds.
Restore Jupyter execution on chapman3 with Firefox locally on the Mac through an
SSH tunnel after environment validation; this remains pending.

Follow-up evidence on 22 October: the approved isolated Python 3.11 stack passes
pip check, nine initial installed-package tests, ten numerical/catalogue
regressions and nine runtime imports. A named Jupyter kernel and Mac Firefox
connection to chapman3 are verified. Fernando also explicitly approved the
narrow notebook 03 mefpp-prefix adapter and its path-resolution regression;
the corrected local wheel passes ten installed-package tests. Full reduction,
pilot selection and scientific reference comparisons remain pending. This does
not authorize general notebook thinning or scientific changes ahead of schedule.

## Packaging implementation status, 21 October 2026

Fernando authorized the packaging stage and reiterated that any roadmap deviation
must be discussed and approved **before** proceeding. Work is limited to Python
packaging/setup, resource delivery, dependency declarations and executable
configuration, with current scientific versions retained. See
[installation and evidence](installation.md). Mac/cluster acceptance and exact
reference constraints remain pending; do not mark the stage complete from local
Linux smoke tests. Notebook thinning follows this gate, then configuration-driven
scripts, the **Pycavi Python library audit**, and the mefpp audit. WFI work remains
deferred. No later implementation stage is started by this patch.

## Sequencing update, 21 October 2026

Latest clarification from Fernando supersedes the earlier proposals below:
package/establish OmegaCAM execution on Mac and Linux; retire old reduction
scripts and thin notebooks; derive new configuration-driven scripts from that
workflow; systematically audit the notebook-used Python routines; then audit
mefpp. WFI implementation/validation waits for Mac/Linux operation. Preserve WFI
requirements and source. No library/engine upgrades now. BPM creation belongs
to normal calibration production: trace/validate the existing native construction
path and its Python integration, rather than treating static-mask copying as the
final design. Refactoring checks remain necessary before the full library audit.

Fernando clarified the following order after the installation audit:

1. Properly package wenu-imaging using the existing scientific stack; no library,
   Python or external-engine upgrades yet. Validate ordinary wheel/sdist installs,
   installed resources and setup outside the checkout, plus reproducible
   configuration/environment records.
2. Debug and improve Pycavi, preserving and comparing the OmegaCAM pilot and WFI
   behavior. Fix integration and failure reporting before increasing concurrency.
3. Audit single-chip CCD/CMOS support and every single-node parallelization
   opportunity now; use that audit to define focused Pycavi changes. Distinguish
   single-detector data layout from the actual detector noise/calibration model.
4. Once Pycavi is debugged and improved, continue with mefpp's build, detector and
   parallel-execution work. Evaluate independent-process scheduling and internal
   C parallelism separately. Native mefpp behavior is unchanged in earlier steps.
5. Qualify newer libraries and alternative backends later, by a separate decision.

The concurrency goal covers all suitable independent work, not just solve-field.
Allocation, memory, I/O and scientific dependencies determine what can run at the
same time. No multi-node/MPI requirement is introduced. The immediate scientific
delivery remains the OmegaCAM Phase 3 dataset; release quality and format checks
remain necessary alongside packaging and performance work.

Earlier sections below retain their baseline history. This dated update controls
the current sequencing. Detailed source findings and task opportunities are in
[the detector/concurrency audit](detectors-and-parallel-work-audit-2026-10-21.md).

Status: accepted roadmap direction, amended by Fernando on 20 October 2026.
The immediate science delivery is an OmegaCAM dataset for ESO Phase 3 submission.
Component implementation remains limited to separately authorized stages.

## Platform requirements and current evidence

| Target | Priority | Known environment | Validation status |
|---|---|---|---|
| macOS Intel | Urgent; begin here | macOS 13.7.8 (22H730), x86_64, Python 3.11.7, Apple Clang 15.0.0 | Environment reported; build/install/reduction pending |
| Linux cluster, distribution pending | Urgent; define when access is available | Single-node multiprocessing confirmed; distribution pending | Pending identification and validation |
| macOS Apple Silicon | Required afterward | ARM-native target; OS/Python/compiler versions pending | Untested |
| Ubuntu Linux | Required afterward | Release, architecture and toolchain pending | Full build/install/reduction untested |

Intel Mac compiler details:

- `Apple clang version 15.0.0 (clang-1500.1.0.2.5)`
- Target: `x86_64-apple-darwin22.6.0`
- Xcode developer directory: `/Applications/Xcode.app/Contents/Developer`
- Toolchain: `/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin`

The terminal prompt indicated `(base)`; the exact interpreter path, environment
manager configuration and package set have not been collected. Do not modify
that environment to establish the baseline. A separate test environment/prefix
should be agreed before installation attempts.

Ubuntu GCC 13.3.0 syntax checks performed during the initial audit were limited
to both `sysconf.c` files. They do not establish Ubuntu pipeline support.

## Stage 0 — Working agreement and architecture review (accepted)

Deliverables:

- Canonical `docs/developer/agent-instructions.md`, a root AGENTS.md entry point,
  existing architecture, the historical audit and this roadmap.
- Explicit record of accepted decisions and remaining choices.
- Audited component trees and their original histories imported into the monorepo.

Fernando accepted the documentation and roadmap direction and requested the
files under `docs/developer`. The monorepo direction, single-node cluster
model, serial mefpp baseline and urgent OmegaCAM delivery are recorded decisions.
No source fixes are included in this stage.

Remaining details: installation/resource layout; dependency provisioning;
reference data, product types and numerical tolerances. Historical scripts are
unvalidated unless needed for the selected production path. The name wenu-imaging is established; repository consolidation
changes source organization without changing processing code.

## Stage 1 — Characterize unchanged software on Intel macOS

Use disposable copies and separate environments to:

1. Record tools, interpreter path, dependency versions and external executables.
2. Attempt unchanged qfits build/install, then unchanged mefpp build/install
   against that qfits, collecting diagnostics and effective compiler options.
3. Attempt Python wheel/sdist builds and installation outside the source tree.
4. Check installed notebooks, CFG/PAF, headers/libraries and decompressed BPMs.
5. Characterize executable configuration, startup/imports and stage preconditions.

Gate: reproducible commands and logs identify what succeeds and fails on the
reported Intel Mac. Record failures without silently patching the baseline.
Do not assert compatibility merely because configure recognizes Darwin.

## Stage 2 — Establish scientific reference and failure cases

Select a small representative OmegaCAM subset of the intended production set,
including calibrations, BPMs and trusted outputs or a known working installation.
Record data identities, configuration, executable versions and intermediate
stages. Add WFI regression cases where shared behavior is changed; do not make
new detector capabilities a prerequisite for the urgent OmegaCAM delivery.

Agree on comparisons for extension mapping, masks, pixel values/units,
gain/exposure and FITS scaling, QC/header values, WCS residuals, coadds,
photometric calibration and catalogues. Define tolerances and the treatment of
timestamps/header ordering before judging numerical equivalence.

Characterize fresh execution, reruns, missing calibrations, deliberate process
failure and worker failure. Use synthetic FITS cases for small interfaces where
useful; they supplement real-data references.

Gate: agreed datasets, trusted outputs and acceptance criteria. If unchanged
software cannot run, agree how existing trusted products establish the reference.

## Cluster characterization — urgent when access becomes available

Collect distribution/version, architecture, Python/compiler/library versions,
available external astronomy software, scheduler and an example launch script.
The execution model is already confirmed: multiprocessing within one node.
Identify the scheduler's allocation and permitted process/thread settings.
Record CPU/memory allocations, process/thread counts, temporary storage, shared
filesystem behavior, installation permissions and compute-node network access.

Gate: a documented cluster deployment model and resource limits. Do not assume
that multiprocessing.Pool distributes jobs across nodes. Cluster access being
pending does not block independent Intel Mac analysis.

## Stage 3 — Minimal build and installation corrections

Propose focused fixes only after the preceding review gates. Candidate work from
the first audit includes:

- Separate the mefpp executable path from its configuration/BPM locations.
- Resolve missing license/resource declarations and undeclared Python imports.
- Make external program discovery deterministic and consistently applied.
- Correct demonstrated native compiler/configure/install failures while retaining
  existing build machinery where practical.
- Check `funpack` and all resources; report incomplete installation clearly.

Gate: clean installed workflow outside the checkout on the urgent validated
targets, with dependency versions recorded. Scope and validation must be stated
per patch. Do not add a new installer framework or upgrade all dependencies as
an unrelated part of this work.

## Stage 4 — Reliable pipeline execution within one node

Characterize and minimally fix the supported runners: exit status, verbose output,
argument/path handling, restoration of working directory, worker exceptions and
expected output checks. Respect allocated cluster resources and account for
external-program threads as well as Python workers. Keep temporary/output files
isolated when work runs concurrently.

Keep mefpp serial in this milestone. Exercise existing pipeline multiprocessing
and external tools without adding multiprocessing inside mefpp or concurrent
mefpp jobs as an unreviewed optimization.

Gate: failures are visible, allocated limits are respected, and agreed scientific
outputs remain equivalent under the supported single-node settings. No multi-node
or MPI implementation is included.

## Stage 5 — Operational OmegaCAM reduction and Phase 3 preparation

Inventory the medium-sized production dataset before setting performance or disk
capacity expectations: programme IDs, targets, filters, dates, exposures, total
bytes, calibrations and BPMs. Select a pilot subset, inspect all stages, then
process the full selected set on the validated urgent platform(s).

Acceptance evidence must include:

- Reproducible input/calibration/configuration/software identities and processing
  records, with explicit failed or excluded partitions.
- Scientifically reviewed calibration, masks, astrometry, photometry, coadds and
  other agreed products, with QC results and agreed tolerances.
- An inventory of intended submission products and their associations/provenance.
- Review against the applicable ESO Science Data Products Standard and Phase 3
  validation procedures, recording exact versions and validation reports.
- Release documentation describing processing, coverage, quality and limitations.

The existing code's Phase 3 keyword support is a starting point, not a compliance
claim. Confirm product types, metadata and required companion products from the
applicable official documents rather than guessing a universal checklist.
Scientific correctness and technical format validation are separate checks.

Gate: the medium-sized OmegaCAM set is reduced, reviewed and prepared for Phase 3
submission with documented outstanding issues. ESO acceptance is not claimed in
advance. Upload, submission and publication require Fernando's instruction.

Official references to consult when defining and validating the delivery:

- [ESO Phase 3 overview](https://www.eso.org/sci/observing/phase3/overview.html)
- [ESO Science Data Products Standard](https://www.eso.org/sci/observing/phase3/p3sdpstd.pdf)
- [ESO release description guidance](https://www.eso.org/sci/observing/phase3/release_description.html)

## Stage 6 — Required platform completion

Validate native Apple Silicon and the selected Ubuntu release, documenting any
additional differences. Avoid treating Rosetta execution as ARM-native validation.
Run the agreed scientific checks and publish a compatibility matrix with actual
results and exact system commits and recorded component baselines. These remain requirements but do not delay
the urgent OmegaCAM deliverable solely for platform completeness.

Gate: target-specific installation instructions and passing acceptance evidence;
unsupported configurations explicit. Add CI only where authorized and feasible.
Tagging or publishing a release requires instruction.

## Later development — after wenu-imaging works correctly

These are explicit future requirements and have no implementation authorization:

1. **mefpp multiprocessing.** First establish the correct serial baseline. Then
   profile representative work, propose safe process boundaries, evaluate shared
   state and memory/I/O behavior, and validate serial/parallel equivalence and
   failure behavior. Keep this separate from pipeline-level parallel astrometry.
2. **Single CCD reductions.** Audit single-detector FITS/configuration assumptions
   and appropriate bias/dark/flat, gain, saturation and noise handling with
   Fernando; define detector-specific test data and expected results.
3. **Single CMOS reductions.** Determine readout modes and calibration/noise
   requirements from actual detectors/data. Do not treat single CMOS support as
   already implemented or assume every CCD correction applies unchanged.
4. **Calibration-product QC library (Fernando, 22 October 2026).** Develop a
   library for scientific quality control of calibration products after the
   currently planned wenu-imaging work is finished. Keep this deferred; current
   historical-product comparisons establish reproducibility evidence, not
   independent calibration-quality certification. No implementation is started.

Agree their relative order after the operational OmegaCAM milestone. Preserve
instrument configuration boundaries and existing mosaic support when designing
these capabilities.

## Review and completion rules

Each proposal states affected repositories, exact baseline, finding addressed,
files/interfaces changed, scientific invariants, checks and rollback. Cross-component changes should be reviewed together when they implement one
agreed interface correction. A successful
syntax check, no-op `make check`, or editable install is not a release gate.

This roadmap is intentionally sequential at approval boundaries. Independent
documentation and evidence gathering may proceed together; implementation must
remain within the stage Fernando has approved.

## Chapman3 build result and workspace location, 26 October 2026

Chapman3 native build acceptance, 26 October 2026: Fernando reports source
805e6c63dea20e7f5e5ade816f6a6ddc90702d86 passed both required M_PI/shmget
configuration checks, 100-unit C90/C17 builds with the declared feature/language
flags, and all five CTest entries per mode. Evidence is
/home/fselman/wenu-chapman3-native-retry-xkuuu6qu/build-check.json and mode logs.
Protected tools, previous failed-run evidence, working Pycavi package and checkout
remained unchanged. This is build/test acceptance only: no installation or
observational reduction ran. Keep installed/native/Pycavi/calibration/memory and
wider Stage 1 gates distinct; no merge or normal selection switch is implied.

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
