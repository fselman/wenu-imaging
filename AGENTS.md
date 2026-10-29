# wenu-imaging

29 October M1 runtime increment ready for bounded review: returned Mac and representative Chapman4 C90 CMake probe builds and both focused tests passed 2/2. See [paired runtime receipt](docs/developer/m1-runtime-paired-results-2026-10-29.md) for exact revisions, evidence and limits. No target C17/sanitizer or scientific-processing claim; preserve all private runs. Legacy CLI/list/save-flag/override adapters and one concrete operation remain subsequent M1 work. No duplicate Chapman/tool checks or further runs for this receipt. No merge or cleanup without owner instruction.

29 October next M1 increment authorized: owner instructed “Proceed” after PR #137 acceptance/merge and clean Mac/shared Chapman main 1d991a22a39d6133ab19721b7bb3a6dd11394264. [Owned runtime lifecycles](docs/architecture/proposed/m1/runtime-lifecycles.md) implement copied request descriptors, independent config/request contexts, result/error owners and explicit unsupported execution. Agent strict C90/C17, 268 transient/persistent allocation positions, ownership/independence and synthetic override controls pass; actual Mac/representative Chapman checks are pending. The normal CLI/numerical engine is untouched; legacy binding/override adapters and one concrete numerical operation remain subsequent M1 work. Preserve installed tools/evidence; no repeated shared-host tool qualification, processing, installation, merge or cleanup.

29 October M1 configuration increment ready for bounded review: returned Intel Mac and representative Chapman4 C90 CMake configure/probe builds and focused native_config_snapshot CTest passed. See [paired target receipt](docs/developer/m1-config-paired-results-2026-10-29.md). Both instrument maps, edge cases and ownership/failure controls pass; preserve all private builds and earlier evidence. No new processing, installation, scientific/QC behavior or complete-M1 acceptance. Request/context/result/error lifecycle and CLI-override capture remain subsequent M1 work. Chapman3/4 share one qualified tool environment; no duplicated host/tool checks. No merge or cleanup without owner instruction.

Owner-mandated tool selection, 29 October 2026: read [Selected project tools](docs/developer/selected-tools.md) before preparing host commands or builds. Always select the documented Mac/Chapman tools by absolute path, including CMake/CTest, compiler, Python, make/ar/ranlib and Mac SDK; do not infer availability from PATH or inherit the MPI/Mesa compiler selection. Consult the recorded private installations before proposing replacements, upgrades or manual build workarounds; never silently fall back. Chapman hosts are owner-confirmed identical and share home directories: reuse ~/opt/cmake-3.29.6/bin/{cmake,ctest} and the shared Python environment, with explicit devtoolset-10 GCC. Their CMake/CTest 3.29.6 paths/hashes are confirmed on Chapman4; system CMake 2.8.12.2 is not selected. The owner explicitly says Chapman3/4 are copycat: no further per-host tool availability/version/hash/ABI checks or duplicate qualification are needed; use the recorded tools directly. A new task's Chapman verification runs once on a representative Chapman host. Preserve global PATH/login files, production environments, external-executable configurations and accepted evidence. Use fresh task build directories and record actual execution host; shared tools do not imply every test ran on every host.

Production dependency gate, 29 October 2026: owner confirms the older Chapman machines are the main production systems. See [TOML/ASDF Chapman qualification](docs/developer/toml-asdf-chapman-qualification-2026-10-29.md). New parser/ASDF packages and their transitive dependencies must qualify on actual Chapman as well as Mac before adoption; Mac-only success is insufficient. Start with read-only chapman4 package/tool preflight, then a private constrained candidate, offline/interchange checks and explicit adoption evidence. Preserve working environments; no implicit NumPy/Astropy/compiler/C-standard upgrades. M0/M0a review package PR #134 is accepted/merged at b5bfd910614a786b95a598cb6295989c9f6602d6; remaining dependency/schema/effective-setting decisions are open. Development remains Mac, production qualification Chapman.

M0/M0a preparation, 29 October 2026: owner instructed "Proceed" after both hosts reached clean main 0fa9eaf157359a93f2a9196f6fff05dc3e96e220. [Contract review package](docs/architecture/proposed/m0-m0a/README.md) contains WAD/project sketches, 25 synthetic records, native boundary/ownership draft, source configuration ledger and focused checks. Development is on the Intel Mac; chapman4 is retained for later qualification. This increment is documentation/review fixtures only; M0/M0a contract acceptance and parser/schema/effective-setting choices remain pending, with no production/native/notebook changes, installation or reduction. CLI --ksize source finding is tracked separately as #133; do not repair it implicitly. PR #132 is already merged and both hosts were synchronized/cleaned; preserve all evidence and frozen amendments.

WAD/project direction approved for documentation, 29 October 2026: owner instructed "Proceed" after the Wenu Attribute Dictionary and ASDF processing-project proposals. See [WAD and ProcessingProject](docs/architecture/proposed/wad-processing-project.md), [target architecture revision 4](docs/architecture/proposed/pycavi-mefpp.md) and [implementation plan version 3](docs/architecture/proposed/implementation-plan.md). WAD defines shared data contracts; ASDF persists evolving project revisions, exact-version plans and run/product records; FITS retains pixels and TOML remains editable configuration. M0a establishes the minimal WAD/project foundation before native interfaces are finalized; M7 implements persistence and M8/M9 use the shared project service. Include the M3 inspector and M6a–M6d variance/linearity/dark/fringe scope already recorded. Concrete schemas/APIs/layout, implementation and numerical qualification remain pending; no production package, migration, installation, processing, merge or branch cleanup starts from this documentation update. Automatic cascades and parallel execution remain later passes. This supersedes earlier exploratory-only wording only for these owner-directed design elements; frozen amendments and accepted baselines remain unchanged.

Next-stage direction approved, 29 October 2026: [amendment v2.9](docs/developer/native-roadmap-amendment-v2.9-2026-10-29.md) authorizes analysis/design of mefpp subroutines, typed TOML configuration subsets, ASDF processing metadata referencing FITS-resident images, parallel-ready and single-detector interfaces, notebooks 01/03 and an optional mefppy Python library. See the [initial source analysis](docs/developer/mefpp-refactor-analysis-2026-10-29.md). TOML/ASDF-with-FITS is now the owner-selected design direction; exact schemas/adapters/bindings and directory layout remain proposals. Read-only larger Chapman inventory is pending actual-host evidence; do not assume its reductions are complete. No production implementation, installation, data migration or reduction rerun begins from this analysis. Stage 2/2.1 stay accepted; other exploratory WISDG/retrieval/layout ideas remain unadopted.

Stage 2.1 endpoint revised by owner, 29 October 2026: [immutable amendment v2.8](docs/developer/native-roadmap-amendment-v2.8-2026-10-29.md) makes the gate **current mefpp/Pycavi reduction through notebook 04: native calibration/science preprocessing, Python normalization, solve-field and WCS-corrected MEF assembly**. Keep one filter and at most five equal-integration-time science exposures per instrument; all three WFI partitions are authorized for the same five exposures in total. Notebook 05 extraction/SCAMP, SWarp, photometric/illumination work, downstream QC and final catalogues are outside Stage 2.1 and deferred to later workflow work. Older v2.7/full-chain completion wording is historical and superseded; do not reopen it as a closure requirement.

Both bounded instrument sets have now passed the Stage 2.1 functional endpoint on the Intel Mac: native preprocessing, Python normalization, solve-field and WCS-corrected MEFs. OCAM: five r_SDSS exposures at 20 s, one partition, 160 solved detector images. WFI: five BB#B/99_ESO842 exposures at 89.9177 s across three partitions, 40 solved detector images. Pixel/input preservation checks passed. See the [returned-result receipt](docs/developer/stage2-1-functional-results-2026-10-29.md) for evidence paths and limits. The owner accepted Stage 2.1 on 29 October 2026 and authorized merging PR #130 and cleaning its merged branch. Next substantive work is Stage 2A review; preserve all baseline products and evidence. Preserve the failed first WFI SCAMP attempt outside this gate; #30/#131 remain open for later production work. No scientific/Phase 3 certification or automatic Stage 2A/refactoring is claimed.

Historical Stage 2.1 addition, 28 October 2026 (endpoint superseded by v2.8): [immutable amendment v2.7](docs/developer/native-roadmap-amendment-v2.7-2026-10-28.md) inserts full processing of one complete OCAM dataset and one complete WFI dataset with current mefpp/Pycavi before Stage 2A. New order: accepted Stage 2 → **Stage 2.1 full current-workflow baseline** → Stage 2A review → extraction. One inventory/input/software lock, both existing complete supported reduction chains, retained outputs/QC and one baseline report; no new algorithm, format migration, automatic tuning, repeated memory matrix or duplicated platform run. Stage 2 stays accepted at 19/19 planned, 29 actual; #116 open/deferred, Phase 3 deferred. Planning only tonight; both user checkouts stay clean on main, no processing/installation/sync needed to review. Exploratory ASDF/WISDG/layout ideas are not adopted requirements.

Owner wrap-up accepted, 28 October 2026: owner instructed to leave #116 for now and finish clean for tomorrow. [Immutable v2.6](docs/developer/native-roadmap-amendment-v2.6-2026-10-28.md) records bounded Stage 2 acceptance with #116 OPEN/unresolved/deferred, named testing limits retained, and Phase 3 deferred outside this closure gate. [Final receipt/review](docs/developer/stage2-integrated-owner-review-2026-10-28.md) records all F1–F5 plus final C90 accepted: 19/19 planned + 10 retests = 29 actual, no further engine runs. Finish verified defect comments/closure, integrate PR #119 then #120, guard final-tree/host fast-forwards and remove only exact merged branches; preserve all raw data/runs/archives/builds/installations/configuration. No reinstall, new matrix/repair or automatic Stage 2A implementation. Tomorrow next topic: Stage 2A review after clean-main verification. This current instruction supersedes older pending-approval/Phase 3 closure-gate statements.

F5 accepted / final owner review ready, 28 October 2026: [F5 receipt](docs/developer/stage2-integrated-f5-acceptance-2026-10-28.md) independently verifies 94 files, six logs, both 391-entry source inventories, 12 exact products / 24 arrays, zero cleaned resources and stable descriptors. Fixed F1–F5 plus final Mac C90 are accepted/reused; **19/19 planned + 10 retests = 29 actual**, general rounds 2/2. No further engine runs planned. [Final owner decision](docs/developer/stage2-integrated-owner-review-2026-10-28.md) is complete; the later owner disposition below/above accepts bounded closure and defers Phase 3. #121–#124 meet bounded verification; comment before closure. #75/#116 remain open; #125/#128 deferred. No sync/rebuild/rerun needed for receipt, no automatic repair/new matrix/merge/deletion/installation/Stage 2A advance.

F5 prepared, 28 October 2026: actual Chapman preflight confirms clean main b0061b5 and qualified GCC10.2.1/CMake3.29.6/Python environment. [Final compact paired runner](docs/developer/stage2-integrated-f5-preparation-2026-10-28.md) prepares explicit C17/C90 builds and exactly one unchanged tiny integrated workflow per mode, pinned exact Mac products/metadata plus owner/accounting/descriptors. Python real-log/fixture/guard controls pass; target native execution pending, no native C/header changes or agent recipe launches. Current 17 planned + 10 retests = 27 actual; maximum after F5 19/19 and 29 actual, general rounds 2/2. One-use, stop at first finding; no extra matrix, external target diagnostics, automatic repair/retry, installation, merge or deletion. Then final owner/Phase 3 gap review; #116 unresolved, #125/#128 deferred.

Final Mac C90 accepted, 28 October 2026: [compile/link receipt](docs/developer/stage2-final-c90-mac-acceptance-2026-10-28.md) verifies six archive files, actual -std=c90 / AppleClang 15 / Darwin x86_64, successful final link and independently reconstructed 389-input source inventory. 66 retained warnings, no new warning messages versus prior C90; no warning-free claim. Binary stays Mac with host-verified hash. No native execution/installation; counts remain 17 planned + 10 retests = 27 actual, general rounds 2/2. Next compact Chapman3 C17/C90 pair and owner/Phase 3 gap review. Obtain actual Chapman host/Git state before its checkout mutation. Docs-only receipt needs no Mac sync/rebuild. No automatic repair/new matrix/merge/deletion/installation; #116 unresolved, #125/#128 deferred, #121–#124 await final disposition.

F4 accepted, 28 October 2026: [independent receipt](docs/developer/stage2-integrated-f4-acceptance-2026-10-28.md) verifies all 421 files, eleven same-process cycles, 66 exact products / 132 detector arrays, balanced owners, zero start/double-purge resources and stable descriptors. Current 17 planned + 10 retests = 27 actual; general rounds 2/2. Native source remains 68f0a04 (harness b93ffda). Next one final Mac C90 build without processing, paired compact Chapman3 C17/C90, then owner/Phase 3 gap review. Docs-only receipt needs no host sync/rerun; no automatic repair, new matrix, installation, merge or deletion. #116 unresolved; #125/#128 deferred; #121–#124 await final checkpoint. Earlier F4-pending statements are historical.

F3 accepted / F4 prepared, 28 October 2026: [independent F3 receipt](docs/developer/stage2-integrated-f3-acceptance-2026-10-28.md) verifies all 539 files, 35 logs, six builds, ten final failure roles and two exact tiny smokes; both historical failures remain preserved. #127/#129 meet bounded acceptance; #121–#124 await final checkpoint, #125/#128 deferred, #116 unresolved. Current 16 planned + 10 retests = 26 actual, general rounds 2/2. [Fixed F4](docs/developer/stage2-integrated-f4-preparation-2026-10-28.md) is prepared with Python guards/parser/fixture controls passed, actual Mac execution pending: reuse the qualified 68f0a04 instrumented binary for one warmup plus ten cycles in one process / one original planned launch. Native source unchanged; no rebuild, automatic repair/retry, new matrix, installation, merge or deletion. Then final Mac C90 build, paired compact Chapman3 C17/C90 and owner/Phase 3 gap review. Older pending/blocker paragraphs below are historical where superseded.

Approved cube exception v2.5, 28 October 2026: Fernando responded "authorized" to the two-C-file/two-added-retest proposal for #129. See [immutable amendment](docs/developer/native-roadmap-amendment-v2.5-2026-10-28.md) and [prepared repair/resume](docs/developer/stage2-integrated-cube-repair-2026-10-28.md). Cube constructor NULL/partial-owner guards and loaded-image cleanup are prepared; no header/recipe/qfits changes. C90/C17 syntax/actual constructor-loader controls and Python guards pass; Mac verification pending. One-use cube retry, exact successful tiny smoke, then the one original unrun cube leak role only if both pass. Current 23 actual; maximum after F3 26, general rounds stay 2/2. Preserve all evidence; no automatic repair/retry, new matrix, merge/deletion or installation.

F3 cube blocker, 28 October 2026: [#129 bounded decision](docs/developer/stage2-integrated-f3-cube-blocker-2026-10-28.md) records UBSan NULL member access after the declared cube injection at actual Mac source 2e3969c. Publication retry/smoke/leaks and both context-allocation lanes reportedly pass; full F3 archives pending. Current 15 planned + 8 retests = 23 actual, general rounds 2/2, v2.4 consumed. Proposed two-C-file NULL/partial-owner cleanup and two added retests require new explicit approval; no change/retry or later-row execution authorized. F1/F2 preserved; #125/#128 deferred, #127 awaits receipt, #116 unresolved.

Approved publication exception v2.4, 28 October 2026: Fernando instructed "Proceed" after the three-file/two-retest proposal and header clarification. See [immutable amendment](docs/developer/native-roadmap-amendment-v2.4-2026-10-28.md) and [prepared repair/resume](docs/developer/stage2-integrated-publication-repair-2026-10-28.md). #127 helper status/cleanup propagation is prepared in mefp_lib.c/.h and mefpp.c; qfits unchanged. C90/C17 syntax/helper units and Python guards pass; actual Mac acceptance pending. Exactly two added retests then five original unrun F3 roles only on success, one-use directory, no automatic retry/other repair. Current 17 actual launches; maximum 24 after F3; general rounds stay 2/2. #125/#128 deferred; no merge/deletion/installation.

F3 blocked, 28 October 2026: [publication-status defect #127](docs/developer/stage2-integrated-f3-publication-blocker-2026-10-28.md) confirmed by actual Mac terminal/read-only evidence at c722310: the master-bias target stays a protected directory, five other products are written, native exit is 0. Missing-list/corrupt-frame pass both lanes (user-reported); full F3 archive pending. Counts 11 planned + 6 retests = 17 actual, 2/2 general rounds; stop dependent work. Three-file publication-status repair and two added retests are proposals only, requiring owner approval/new amendment. No native modification, retry, later-row advance, merge/deletion or installation; preserve F1/F2.

F3 prepared, 28 October 2026: owner instructed "proceed" for the [five fixed failure cases](docs/developer/stage2-integrated-f3-preparation-2026-10-28.md). Test-only scoped context/cube NULL injection lives exclusively in private exports; no production/qfits changes. Python result/injection controls, actual archived-log parser controls and private C90/C17 syntax pass; Mac execution pending, current counters 6 planned + 6 retests = 12 actual, 2/2 general rounds. One-use F3 runner permits at most ten cases and stops on first finding. Preserve accepted F1/F2; no retry, repair, new matrix, merge, deletion or installation.

Integrated F1/F2 accepted, 28 October 2026: [inspected receipt](docs/developer/stage2-integrated-f1-f2-acceptance-2026-10-28.md) verifies archive 0ee502ce, all 416 files and 52 logs. F1 exact archived products and all four diagnostic logs pass; WFI host-verified reports agree exactly across three lanes (large WFI FITS remain on Mac). Both purges have zero resources, descriptors stable, external leaks zero. Counters 6 planned + 6 retests = 12 actual, 2/2 general rounds. #126 meets bounded acceptance; #125 stays deferred, #121–#124 await final checkpoint disposition, #116 unresolved. Next fixed row F3; F4/final C90/compact Chapman3 C17+C90 remain pending. Docs-only receipt needs no host sync/rerun; no merge/deletion/installation.

F2 continuation prepared, 28 October 2026: [one-use handoff](docs/developer/stage2-bpm-filename-resume-2026-10-28.md) validates the approved BPM filename correction without replaying passed F1. One ordinary retry then the two originally unrun diagnostic lanes; old F1 evidence is reverified and explicitly inherited. Python guards pass; Mac runtime remains pending. Current 9 actual launches; maximum 12 after these three cases. Keep general repair rounds 2/2, all gates/preservation active, #125 deferred and #126 open.

Approved BPM filename correction, 28 October 2026: [v2.3 amendment](docs/developer/native-roadmap-amendment-v2.3-2026-10-28.md) records Fernando's explicit caller-side correction in mefp_lib.c; fits_h.c remains unchanged. Immediate #126 and deferred qfits CONTINUE/safety #125 stay open. Agent C90/C17 syntax and basename controls pass; actual Mac retry is pending. User reports F1 all three lanes passed, F2 SIGILL; 4 planned + 5 retests = 9 launches, general repair count 2/2, v2.2 consumed. Preserve evidence; no old F1 resume, new matrix, merge, deletion or installation.

Approved bias-QC exception v2.2, 28 October 2026: Fernando instructed "proceed" for the four missing bias-QC releases in mef_bb_del and two tiny validations, followed by the original unrun campaign only if both pass. See [immutable amendment v2.2](docs/developer/native-roadmap-amendment-v2.2-2026-10-28.md). Keep the general repair count at 2/2; record the exception separately and permit it only once. No changed calculations, expectations, thresholds, further native correction, new matrix, merge or deletion. C90/C17 syntax and Python guard controls pass; actual Mac zero-resource verification is pending.

PR reporting, approved 28 October 2026: every PR must begin with a concise executive summary and automatically display that summary in Work chat on creation or material updates. Cover purpose, main changes, verified checks, pending risks/verification and next step; link the PR and identify its commit. See [the canonical rule](docs/developer/agent-instructions.md#pr-executive-summaries-and-work-chat--approved-28-october-2026).

Integrated F1 memory finding, 28 October 2026: archive bd27d7c6 and all 141 file identities verify. Both corrected ordinary/instrumented products are exact and mutually equal, ownership/descriptors pass; 5847 allocations / 204017 bytes remain after both purges. Source-confirmed header, flat-scratch and per-extension metadata owners are tracked as #122–#124. Their lifetime-only correction and same-campaign final round 2 resume are prepared; actual corrected memory verification remains pending. Current counts: 2 planned launches, 1 correction retry, 3 actual launches, 1 round consumed. No third round, new matrix, changed expectations, merge/deletion or installation. See [final correction record](docs/developer/stage2-integrated-memory-correction-2026-10-28.md).

F1 integrated finding, 28 October 2026: the first ordinary Mac C17 run at fa2e5c2 returned 0 but failed exact known answers. Source tracing attributes the measured 1.111110687 bias offset to the rejected-mean overscan loop skipping one retained sample (#121). The one-line documented-mean correction and guarded same-campaign retry are prepared; actual corrected Mac verification is pending. One planned launch is consumed; global correction round 1/2 is prepared, with no retest executed. Expected arrays, exact gates, original failed evidence, installations and frozen contract bytes remain unchanged. See [bounded correction](docs/developer/stage2-integrated-overscan-correction-2026-10-28.md). No merge/deletion or new test matrix.

Integrated campaign preparation, 28 October 2026: the eleven-file WFI input-lock report is inspected and accepted for the bounded regression. The test-only existing-engine observer and Mac C17 F1/F2 runner are prepared; Python product-reader controls and C90/C17 syntax checks pass, actual native execution remains pending at 0/19 launches and 0/2 global correction rounds. See [integrated runner record](docs/developer/stage2-integrated-runner-2026-10-28.md). Preserve the single campaign pointer, all inputs/evidence/installations, frozen contract bytes and unresolved #116; no automatic retries, merge or branch deletion. F3–F5 remain the existing pending rows.

Frozen roadmap accepted, 28 October 2026: Fernando instructed "proceed" after reviewing v2.0 and requesting amendment v2.1 (paired final Chapman3 C17/C90 regression). The [accepted execution record](docs/developer/native-roadmap-v2-acceptance-2026-10-28.md) activates the frozen contract plus amendment; earlier proposal/pending-acceptance statements are historical. Begin one read-only WFI inventory and one integrated-fixture/harness preparation pass, then the fixed F1–F5 campaign: Mac C17 diagnostics, one final C90 build, paired compact Chapman3 closure, at most 19 planned native launches and two global correction/retest rounds. No new BPM-only matrix, automatic scope expansion, processing before input/reference lock, merge or branch deletion is authorized. Keep the frozen files byte-identical, all prior evidence and installations preserved, and #116 explicitly open pending its final-review disposition.

Owner-requested frozen-roadmap amendment v2.1, 28 October 2026: Fernando explicitly requested a compact final Chapman3 C90 regression together with C17. See [immutable amendment v2.1](docs/developer/native-roadmap-amendment-v2.1-2026-10-28.md). F5 now contains two compact target launches, one per mode; the campaign cap is 19 planned native launches. The original frozen v2.0 file/checksum, one-day preparation checkpoint, two global correction-round limit and all other scope/stopping rules remain unchanged. No build or processing starts from this documentation update.

Frozen simplification proposal requested, 28 October 2026: Fernando requested an immutable, finite roadmap instead of successive BPM matrices. Review [frozen native roadmap v2.0](docs/developer/native-roadmap-frozen-v2.0-2026-10-28.md) and its separate [fixed-row progress ledger](docs/developer/native-roadmap-v2-progress.md). It consolidates calibration/science collection through the existing engine, makes Mac C17 the diagnostic lane, retains one final C90 compatibility build, limits Chapman3 to one compact C17 regression, and caps the declared Stage 2 campaign at 18 planned launches plus at most two scoped correction rounds. Target external diagnostics and #116 remain honestly recorded; no implicit finding closure. The concrete proposal requires owner acceptance before execution; no new workload, merge or deletion starts from publication. Once published, never edit the frozen contract in place: amendments need explicit agreement and a new numbered file. This supersedes neither accepted evidence nor the old rules until that acceptance. Documentation review occurs on GitHub with both user hosts remaining on clean main; no diagnostic reruns or host synchronization are needed to review this document.

Integration authorized, 28 October 2026: Fernando explicitly instructed "merge and clean" for PR #117 after both actual Mac and Chapman3 checkouts were verified clean at 295fbe6844895bd4301ee51befdeb432d3ab8b90. Integrate the accepted two-extension test/evidence increment, synchronize both hosts to merged main by guarded fast-forward, and remove only test/stage2-bpm-wfi-multiext after verifying merge ancestry, exact branch tip and retained evidence. Preserve every run/archive/supplement/transfer/raw WFI or linearity frame/installation. #75/full S2-05, unresolved #116, remaining coverage and compatible target external diagnostics stay open; no S2-06 advance. This supersedes older no-merge/deletion-authorization statements only for PR #117 and this branch.

Current S2-05 two-extension target acceptance, 28 October 2026: [complete Chapman3 evidence inspected](docs/developer/stage2-bpm-multiext-chapman3-acceptance-2026-10-28.md) at 355034606cd6015b9e9abc99744973bf4c081b00. All 911 archive file identities plus manifest and all 39 command logs verify. Sixteen pairs / 32 roles exactly match accepted Mac masks/canonical headers; all 37 Mac-qualified source identities remain unchanged. C90/C17 GCC10.2.1/CMake3.29.6 builds, 192 allocator boundaries, 48 stable descriptor boundaries and zero double-purge resources pass. This accepts only the two-extension synthetic functional/accounting slice; compatible target external diagnostics, full S2-05/#75, unresolved #116 and remaining ownership/error/repeat/cache/mmap/swap gates stay open. Preserve every run/archive/transfer/raw WFI or linearity frame/installation. No S2-06 advance, merge or branch deletion authorized. Raw WFI inventory at /Users/fselman/Pictures/WFI remains pending.

Current S2-05 two-extension Mac acceptance, 28 October 2026: [full Mac evidence inspected](docs/developer/stage2-bpm-multiext-mac-acceptance-2026-10-28.md) at cea3e927f0392d8ec6c97cd40afbac2878aca03f. Both archives verify (1,259 original identities plus four recovered build logs); all 32 pairs / 64 roles preserve exact parent/mirrored masks and ordered metadata. All 79 command logs, four build inventories, 384 allocator and 96 descriptor boundaries and 16 zero-leak summaries verify. The unchanged-native-driver Chapman3 16-pair functional/accounting runner is prepared, not executed. #116 and full S2-05/#75, remaining ownership/error/repeat/cache/mmap/swap and compatible target external diagnostic gates remain open. Preserve all runs, archives, raw WFI/linearity data and installations; no S2-06 advance, merge or branch deletion authorized. Raw WFI inventory at /Users/fselman/Pictures/WFI remains pending.

Current S2-05 continuation, 28 October 2026: Fernando instructed "proceed" after supplied-bias integration at main 664f501fe723a924b6a2395d00f70cba1fb03ab7. Prepare test-only two-extension OmegaCAM/WFI BPM ownership qualification, Mac first, retaining exact accepted mask transforms, metadata, 0.5–1.5 thresholds, per-fd and double-purge gates. No production changes, new algorithms, observational reductions or installations. #116 remains unresolved/open; full S2-05/#75 and target external diagnostics remain open. No S2-06 advance or authorization to merge/delete this new branch. See [the bounded plan](docs/developer/stage2-bpm-wfi-multiext-2026-10-28.md).

Integration authorized, 28 October 2026: Fernando explicitly instructed "merge, sync, and clean" for PR #115 after inspecting Mac and Chapman3 supplied-bias evidence. Integrate the reviewed test/documentation increment, synchronize both hosts by guarded fast-forward, and remove only test/stage2-bpm-supplied-bias after verifying main ancestry and retained evidence. Preserve every run, archive, transfer copy, raw frame and installation. #116, full S2-05/#75, target external diagnostics and remaining coverage stay open; no S2-06 advance. This supersedes earlier no-merge/deletion-authorization statements for this branch only.

Current S2-05 supplied-bias acceptance, 28 October 2026: [Chapman3 full evidence inspected](docs/developer/stage2-bpm-bias-chapman3-acceptance-2026-10-28.md) at 10b3ca8285f886694fd0aa54197b8ba46f9cd1e4. All 225 file identities plus manifest verify; eight target pairs / 16 roles exactly match accepted Mac masks/canonical headers and inputs. Both C90/C17 builds, 23 command logs, owners, 24 post-call descriptor boundaries and double-purge zero-resource states pass. This accepts only the agreed supplied-bias target functional/accounting slice. #116 remains unresolved/open under Fernando's explicit sequencing agreement; full S2-05/#75, WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics remain open. Preserve all runs, archives, transfer copies and installations; no S2-06 advance or merge/deletion authorized.

Agreed #116 disposition, 28 October 2026: Fernando explicitly agreed to [bounded Chapman3 supplied-bias verification](docs/developer/stage2-bpm-bias-chapman3-plan-2026-10-28.md) before original descriptor-cause attribution. Keep #116 OPEN as unresolved/non-reproduced; stop further Mac repetition. Authorize only eight unchanged-driver/fixture C90/C17 target functional/accounting pairs with all current product, owner, descriptor and resource gates active. No gate weakening, compatible-target external diagnostic waiver, full S2-05/#75 closure or S2-06 advance. Stop on any recurrence and retain exact per-fd evidence. Record this agreement before preparing the target runner; preserve all original/diagnostic/repeat runs, transfers and installations. This supersedes earlier no-target-advance statements only for this explicit increment.

Current #116 diagnostic preparation, 28 October 2026: [ten focused fresh-process attempts prepared](docs/developer/stage2-bpm-bias-focused-repeat-2026-10-28.md) using the exact inspected c4912390 C90 instrumented binary and deterministic retained/robust supplied-bias inputs. No build, install, native driver, fixture, production source or gate changes. Python controls and readback of 16 retained logs pass; actual focused Mac execution is pending. Each attempt keeps exact product/resource/descriptor checks and fresh retained provenance. This is not S2-09 or new full-suite acceptance; nonreproduction does not waive #116. All original/diagnostic evidence and installations remain preserved; S2-05/#75, target advance and broader gates stay open.

Current S2-05 evidence inspection, 28 October 2026: [both supplied-bias Mac archives inspected](docs/developer/stage2-bpm-bias-mac-inspection-2026-10-28.md), SHA256 dbe6ba94, all 823 file identities plus manifest verified. All 64 native role products match accepted masks/canonical metadata and each other across the two runs; 94 command logs and 16 zero-leak summaries verified. Diagnostic c4912390 run passes all 16 pairs and 48 post-call descriptor boundaries. Original e7e8fbdc run retains one same-count descriptor identity mismatch with no per-fd attribution; #116 is still unresolved and not waived. This is successful rerun evidence, not full S2-05/#75 acceptance or permission for target/S2-06 advance. Preserve all original/diagnostic runs, transfer archive and installations; mandatory review before Stage 2A/extraction remains.

Current S2-05 finding, 28 October 2026: [supplied-bias descriptor diagnostic](docs/developer/stage2-bpm-bias-descriptor-diagnostic-2026-10-28.md) for #116 follows the retained Mac run at e7e8fbdc: all 16 functional pairs reported passed, one C90 instrumented resource case failed with count 4 to 4 but changed descriptor identity. Tracked resources reach zero after both purges in the inspected case; cause remains unresolved. Test-only per-descriptor detail/parser preparation preserves the existing gate, production sources, fixtures and prior evidence. Parser and C90/C17 syntax checks pass; actual Mac diagnostic rerun remains pending, followed by evidence review before target verification. Preserve the failed run and all installations; full S2-05/#75 and target diagnostics stay open, no weaker gate or S2-06 advance.

Current S2-05 continuation, 28 October 2026: [supplied-bias BPM ownership gate prepared](docs/developer/stage2-bpm-supplied-bias-2026-10-28.md) from synchronized main bf1c6afe0063ae62833efd04a9109ae5a3982cef after merged PR #114. Separate synthetic driver/observer and additive float32 fixtures preserve production source and accepted exact masks/metadata; Python-only preparation checks pass, actual Mac execution pending. Retain failed/corrected preparation and every earlier run/archive/installation. Chapman3 workloads remain paused pending host/hardware status from the latest handoff. Full S2-05/#75, WFI/multiple extensions and applicable error/repeat/cache/target external diagnostic gates stay open. No departure, S2-06 advance, merge or branch deletion approved; mandatory review before Stage 2A/extraction remains. Earlier PR #114 pending statements are historical.


Current S2-05 metadata integration, 27 October 2026: Fernando authorized merging PR #114 and cleaning only its merged test/stage2-bpm-metadata branch after verifying main ancestry/evidence. The [inspected Mac/Chapman3 populated-metadata acceptance](docs/developer/stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md) retains 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs with exact masks/headers, unchanged payloads and zero double-purge resources. Full S2-05/#75, supplied bias/WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics stay open. Preserve all runs, archives, transfer copies and installations. No departure, weaker gate or S2-06 advance approved; mandatory review before Stage 2A/extraction remains. This supersedes older PR #114 integration-pending/no-merge-authorization statements.


Current S2-05 populated-metadata acceptance, 27 October 2026: [Mac and Chapman3 evidence inspected](docs/developer/stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md). All 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs preserve exact masks, first-frame metadata and ordered canonical headers; 203 target archive identities verified, image payloads unchanged. Owners/descriptors and both zero-purge states pass. PR #114 awaits review/integration; no merge/deletion authorized. Full S2-05/#75, supplied bias/WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics remain open. Preserve all runs/archives/installations; no departure, weaker gate or S2-06 advance is approved. Mandatory review before Stage 2A/extraction remains. This supersedes older populated-metadata target-pending statements.


Current S2-05 populated-metadata Mac acceptance, 27 October 2026: [actual evidence inspected](docs/developer/stage2-bpm-metadata-mac-acceptance-2026-10-27.md) at c6a7a2bf05f8962cd9db4d72989b420f10159406. All 16 pairs / 32 native roles preserve exact reference masks, declared first-frame metadata and ordered/unaffected header cards; 372 archive identities verified, staged image payloads unchanged. Ownership/descriptors, both zero-purge states, ASan/UBSan and eight leak summaries pass. Unchanged native-driver Chapman3 C90/C17 functional/accounting runner is prepared, not executed. Full S2-05/#75, supplied bias/WFI/multiple extensions and applicable shared-helper/error/repeat/cache/target external diagnostic gates remain open. Preserve all evidence/installations; no merge/deletion, departure or S2-06 advance approved. Mandatory review before Stage 2A/extraction remains. This supersedes older metadata-Mac-pending statements.


Current S2-05 continuation, 27 October 2026: [populated FITS metadata gate prepared](docs/developer/stage2-bpm-metadata-2026-10-27.md) from main f377642ebfd8a8c0a43a99007f5543af34ff9c54. Deterministic header-only derivatives preserve accepted image bytes; unchanged native driver/observer and production .c/.h sources. Declare first-frame metadata, ordered comments/unaffected cards, exact masks and ownership/descriptor/double-purge contracts for 16 Mac C90/C17 instrumented/leaks pairs. Agent Python-only fixture/oracle checks pass; actual native Mac/target execution remains pending. Broader S2-05/#75, supplied bias/WFI/multiple extensions and applicable error/repeat/cache/target external diagnostics remain open. Preserve all evidence/installations; no departure, merge/deletion or advance to S2-06 approved. Mandatory review before Stage 2A/extraction remains.


Current S2-05 integration, 27 October 2026: Fernando authorized merge and merged-branch cleanup of PR #108 baseline and PR #113 ownership correction. The [inspected acceptance evidence](docs/developer/stage2-bpm-chapman3-acceptance-2026-10-27.md) preserves exact masks/headers for 16 Mac diagnostic/leaks pairs and 8 Chapman3 functional/accounting pairs, balanced owners/descriptors and zero double-purge resource state. Corrections #109–#112 meet their bounded acceptance criteria and are resolved with integration; broader #75/S2 and full S2-05, compatible target external diagnostics and remaining metadata/WFI/bias/multiextension/shared-helper/error/repeat/cache coverage remain open. Preserve all unique baseline/corrected/target runs, archives, transfer copies and installations. Only the two merged branches may be removed after verifying main ancestry/evidence. No scope departure or advance to S2-06 is approved; mandatory review before Stage 2A/extraction remains. This supersedes older integration-pending/no-merge-authorization statements.


Current S2-05 bounded acceptance, 27 October 2026: [Mac and Chapman3 BPM evidence inspected](docs/developer/stage2-bpm-chapman3-acceptance-2026-10-27.md): 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs preserve exact reference masks and canonical headers; ownership/descriptors and both zero-purge states pass. All 200 target archive identities verified, all evidence/installations retained. Corrections #109–#112 await review/integration in PR stack #108/#113; no merge/deletion authorized. Compatible target external diagnostics and broader successful/error/repeat/cache coverage remain open; this first OmegaCAM/bias=NULL/single-extension subset does not complete S2-05 or #75/S2 or authorize advancing to S2-06. No departure is approved; prior agreement and mandatory review before Stage 2A/extraction remain. This supersedes older target-pending statements.


Current S2-05 Mac acceptance, 27 October 2026: [corrected BPM evidence inspected](docs/developer/stage2-bpm-mac-acceptance-2026-10-27.md) at 21ea905ff90d94a29cbe174c69674afef5d487eb: all 16 pairs preserve exact baseline/reference masks and headers; both purge boundaries reach zero, ownership/descriptors and ASan/UBSan/eight leaks summaries pass. All 369 archive identities verified. Unchanged-driver Chapman3 C90/C17 functional/accounting runner is prepared, actual execution pending; compatible target external diagnostics remain open. #109–#112/#75 and broader S2-05/S2 coverage stay open. Preserve failed/corrected evidence, runs and installations; no merge/deletion or departure is authorized. Mandatory review before Stage 2A/extraction remains. This supersedes earlier corrected-Mac-pending statements.


Current S2-05 correction, 27 October 2026: [focused ownership repair prepared](docs/developer/stage2-bpm-ownership-correction-2026-10-27.md) for #109–#112 after the inspected 16-pair failed baseline. Release owned cube frame lists, overscan scratch arrays, default pixelmap headers and BPM publication/context metadata after last use; preserve numerical/FITS behavior and all fixtures. Native observer/oracle unchanged; corrected runner pins exact failed-baseline headers/masks as well as #90 references. Actual corrected Mac and target verification remain pending; tickets and broader #75/S2 stay open. Preserve baseline/runs/installations; no merge/deletion, departure or reduced gate is approved. Mandatory review before Stage 2A/extraction remains.


Current S2-05 finding, 27 October 2026: [Mac baseline inspected](docs/developer/stage2-bpm-baseline-evidence-2026-10-27.md) at e3c6b463724725b7afb601b7cc0ebe28e24e161a: all 16 original/observer pairs pass numerically, but all retain 140 RAM allocations / 4472 bytes after both purges. Source/size attribution identifies #109 cube frame-list ownership, #110 overscan double buffer, #111 default pixelmap header and #112 BPM publication/context metadata. All baseline identities and outputs are verified and retained. Focused ownership repair is prepared for fresh Mac qualification; no corrected native or target acceptance yet. Preserve installations/runs, thresholds and numerical behavior; broader #75/S2, applicable error/repeat/cache gates and target external diagnostics remain open. Departures need prior agreement; review before Stage 2A/extraction remains mandatory.


Current S2-05 increment, 27 October 2026: [BPM ownership baseline prepared](docs/developer/stage2-bpm-ownership-2026-10-27.md) from main 9f09a7d8a9d09c9362c390b9351c2c2d467f986c. S2-04 and the full S2/prior-agreement documentation are integrated; both user clones were clean on that main and merged branches removed. Reuse unchanged #90 driver/fixtures and exact mask references for 16 Mac original/observer pairs across C90/C17 instrumented and separate leaks lanes. Production code/numerical behavior/installations stay unchanged; actual native execution and target verification pending. Retain all evidence and any findings. This is a first bounded S2-05 subset, not complete S2 acceptance or a departure; broader #75, target external diagnostics, S2-06 and remaining gates stay open. Prior agreement is required before departures, and mandatory review still precedes Stage 2A/extraction.


Agreed S2 milestone, 27 October 2026: the [full S2-00–S2-11 table](docs/developer/stage2-memory-qualification-2026-10-27.md#declared-test-matrix) records current bounded status after integration of PR #105. S2-05 BPM ownership is next, followed by S2-06 calibration ownership. Departures from the agreed S2 scope, row order, required coverage or completion criteria must be agreed with Fernando in advance and recorded before implementation. This includes deferring, omitting, substituting or weakening a gate. An unavailable tool or a proposed bounded milestone does not by itself authorize a departure. No departure is approved by this documentation update. Preserve evidence/installations and the mandatory review before Stage 2A/extraction.


Current S2-04 acceptance, 27 October 2026: [Mac and Chapman3 split/cache gates verified](docs/developer/stage2-split-chapman3-acceptance-2026-10-27.md): Mac 80 pairs with ASan/UBSan and separate leaks, target 40 uninstrumented functional/accounting pairs with exact Mac products. Controlled purges attribute all retained states and reach zero; context/descriptor checks pass. All original failed/baseline/control/target runs, archives, transfer copy and installations stay preserved. No production cleanup policy changes. PR #105 awaits review/integration; merge/deletion is not authorized. Next after integration is the bounded S2-05/06 calibration ownership baseline. #75/Stage 2, compatible target external diagnostics, broader injection/repeat/cache/mmap/swap and conditional wrappers remain open; early Phase 3 audit and mandatory review before Stage 2A/extraction still apply. This supersedes older target-pending statements below.


Current S2-04 Mac acceptance, 27 October 2026: [split/cache evidence inspected](docs/developer/stage2-split-mac-acceptance-2026-10-27.md) at 5322bb952e6958a93594692fcf1e96c58fbf800d: all 80 functional pairs pass, all 64 retained RAM states are attributed by controlled cache purge, both purge boundaries reach zero and descriptor identities remain unchanged. ASan/UBSan and 40 external leak summaries are clean. The unchanged-driver Chapman3 functional/accounting runner is prepared, not executed; its external diagnostic gap remains open. No production correction/cleanup-policy change or installation occurred. Preserve all three runs/archives/installations. PR #105 stays draft, #75/Stage 2 and broader repeat/cache/mmap/swap gates remain open; early Phase 3 audit and mandatory review before Stage 2A/extraction still apply. This supersedes older cache-control-pending statements below.


Current S2-04 update, 27 October 2026: [repaired Mac observer evidence inspected](docs/developer/stage2-split-observed-evidence-2026-10-27.md) at 97c086aaf301e7ae782c23ec9d67de1427351a8b: 80 functional pairs and descriptor/context observations pass; 64 cache-candidate RAM states keep the resource gate failed. #106 is verified on Mac; Linux observation remains untested. A test-only controlled double-purge check is prepared, not executed; no production cleanup policy changes. Preserve both runs/archives/installations. PR #105 remains draft; #75/Stage 2, target verification, broader repeat/cache/mmap/swap, early Phase 3 audit and mandatory review before Stage 2A/extraction remain open. This supersedes older observer-rerun-pending statements below.


Current S2-04 baseline, 27 October 2026: [first Mac run inspected](docs/developer/stage2-split-baseline-evidence-2026-10-27.md) completed 80 pairs; all ordinary functional contracts and actual paired output sets pass, but descriptor-observer completion fails (#106). A test-only enumeration/diagnostic repair is prepared; actual rerun pending. Sixty-four five-allocation RAM states match cache-size candidates but remain visible pending controlled attribution. No production fix, memory acceptance or target verification is claimed. Preserve all evidence/runs/installations; #75/Stage 2 remains open and mandatory review before Stage 2A/extraction still applies. This supersedes earlier S2-04 unexecuted statements below.

Current Stage 2 increment, 27 October 2026: PRs #102/#104 are merged; Mac and Chapman3 are clean on main f042b38d4018af28e04e20134fc8f2b375c489e4 and merged branches are removed. S2-03/#103 is verified. [S2-04 split I/O/publication ownership](docs/developer/stage2-split-ownership-2026-10-27.md) is prepared, not executed: retained synthetic output/failure checks plus context, allocator/mapping and descriptor observations, Mac first. Preserve all baseline/corrected evidence, runs and installations. #75, remaining Stage 2 gates and target compatible external diagnostics stay open; the early Phase 3 audit and mandatory review before Stage 2A/extraction remain pending. This supersedes older pending-integration statements below.

Current S2-03 acceptance, 27 October 2026: [bounded CLI/parser correction #103 verified](docs/developer/stage2-cli-chapman3-acceptance-2026-10-27.md) on Mac C90/C17 (224 CLI pairs/52 parser checks) and Chapman3 C90/C17 (112 pairs/26 checks, functional/accounting only). Failed baseline, stopped assertion attempt and corrected evidence are retained and inspected. PRs #102/#104 await integration; installations/runs stay preserved. Broader #75/Stage 2 and compatible target external diagnostics remain open. Next after integration is S2-04 split I/O/publication ownership; the early Phase 3 audit and mandatory review before Stage 2A/extraction remain pending. This supersedes older S2-03 target-pending statements below.

Current S2-03 Mac acceptance, 27 October 2026: [the corrected parser/CLI gate](docs/developer/stage2-cli-mac-acceptance-2026-10-27.md) passed all 224 CLI pairs and 52 focused parser checks at 18a196224ba436ae6d68d43b40c25245bbbf50d3. All 930 corrected/stopped-attempt archive identities were verified; failed baseline and stopped assertion attempt stay retained. The unchanged-driver Chapman3 functional/accounting runner is prepared, not executed. #103/#75 remain open; PRs #102/#104 remain unmerged. Preserve installations/runs; broader Stage 2 and compatible target diagnostic-tool coverage remain open. This supersedes older Mac-pending statements below.

Current S2-03 finding, 27 October 2026: the Mac baseline completed 224 CLI pairs with 100 instrumented failures at one bundled getopt name-comparison over-read (#103); all 112 uninstrumented leak/accounting pairs passed. Failed evidence is retained. A [minimal parser correction](docs/developer/stage2-getopt-correction-2026-10-27.md) is prepared; fresh Mac and unchanged Chapman3 verification remain pending. #103/#75 and Stage 2 remain open; preserve installations, baseline and all runs. This supersedes earlier S2-03 not-executed statements below.

Current Stage 2 integration, 27 October 2026: PRs #97/#98/#100/#101 are merged; Mac and Chapman3 are clean on main 9118ffaaec077eefb0d82a50d232721a9d280a3f and the merged branches are removed. All evidence/runs/installations are preserved. S2-02 context cleanup is accepted; S2-03 CLI/parser/engine ownership qualification is now prepared, not executed. See [the bounded S2-03 plan](docs/developer/stage2-cli-ownership-2026-10-27.md). #75, remaining Stage 2 gates and the Chapman3 diagnostic-tool gap stay open. The early Phase 3 audit is pending; mandatory review still precedes Stage 2A/extraction. This supersedes older pending-integration statements below.

Current Stage 2 acceptance, 27 October 2026: [context cleanup #99 is verified](docs/developer/stage2-context-chapman3-acceptance-2026-10-27.md) on Mac C90/C17 (48 cases) and Chapman3 C90/C17 (24 functional/accounting cases). Tool controls, failed baseline and corrected evidence are retained. PR stack #97/#98/#100/#101 awaits integration. #75 and the remaining Stage 2 normal/error/repeat, cache, allocation-failure and mapped/swap gates stay open; Chapman3 sanitizer/leak-tool coverage is not claimed. Next after integration is S2-03 CLI/parser/engine failure ownership, not Stage 2A/extraction. Keep run directories, archives and installations preserved. This status supersedes earlier pending context-cleanup statements below.


Current Stage 2 preparation, 27 October 2026: PRs #93/#95/#96 are merged; main e29a6201f01200708dc55c3439434a640cdc9ed0 contains the inspected normalization and BPM cleanup evidence. #90 is closed; its merged branch is deleted on GitHub, Mac and Chapman3. Both user checkouts are clean on that main. Run directories, archives and selected installations remain preserved. Next is the [Stage 2 ownership and test matrix](docs/developer/stage2-memory-qualification-2026-10-27.md): qualify leak/allocator visibility and the normal/error/repeat suite, Mac first and unchanged drivers/fixtures on Chapman3. #75 remains open; the earlier context-owner correction is already merged, not a new unfixed duplicate-destruction claim. Chapman3 functional #90 checks are not sanitizer acceptance. This preparation launches no build/test/install and changes no production allocator or numerical policy. Stop for the agreed review after Stage 2 before Stage 2A/extraction; the early Phase 3 audit remains pending.


Run provenance and cleanup rule, agreed 26 October 2026: every new build,
test and generated-output directory needs run-provenance.json identifying the
actual tested repository/branch/commit, dirty state, purpose, status and retention
role. New imaging work belongs under ~/Software/build/wenu-imaging/ on both
machines. Review and preserve unique data and required acceptance evidence in
the branch before merge; large external data need verified retained copies and
committed hash/location manifests. Verify evidence reached main before branch
deletion. Merging alone never authorizes deleting run directories or active
installations. Historical unknowns must remain explicit.
See [run provenance and evidence retention](docs/developer/run-provenance-and-retention.md).

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
See [the current decision and qualification ledger](docs/developer/native-qualification-and-roadmap-2026-10-26.md).
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

[Current acceptance and limits](docs/developer/chapman3-native-acceptance-2026-10-26.md).

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

See [the current Chapman3 acceptance record](docs/developer/chapman3-native-acceptance-2026-10-26.md).

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
See [the portability record](docs/developer/chapman3-feature-macros-2026-10-26.md). This does not
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
[the correction record](docs/developer/native-failure-correction-2026-10-26.md).
This is bounded Intel Mac acceptance using prebuilt calibrations. Stage 1 stays
open for calibration-building fixtures and Chapman3; WFI observational, memory,
other platform and scientific/Phase 3 gates remain open. Keep #75's broader
ownership/memory gate and the applicable linked target requirements open.
No normal engine/package switch, merge or cleanup has been performed. Documentation-
only acceptance updates need no reinstall or repeated processing.

Latest scope, 26 October 2026: implement the approved bounded failure/configuration/
ownership and Pycavi propagation correction (#71/#75/#76/#85/#86/#87). Follow
the canonical developer instructions and correction record. Every code-changing
commit requires issue references and an Assisted-by trailer with verified model
identity or an explicit unavailable marker. Use source comments for technical
reasons, not repetitive authorship tags. Earlier dated handoffs are historical
where superseded; target acceptance, merge and engine selection remain separate.

Mac normal installation accepted, 25 October 2026: Fernando reports the default
C90 ./configure; make; make install route, optional make check (four CTest entries),
complete installed payload/BPM pixels/checksums/CLI, byte-identical repeat install
and DESTDIR staging passed at source 7c5238f848284033bcef416ec5970a8004550afd.
See [frontend acceptance](docs/developer/native-frontend.md). Close bounded #84; preserve
the private installation at ~/wenu-mac-simple-install.7en8H834/install and the
selected historical engine/configuration. Next is CP Pup read-only preflight,
then isolated native regression; do not repeat installation checks unnecessarily.
No automatic observation run, engine switch, merge or cleanup is authorized.

Simple installation interface, approved 25 October 2026: Fernando requires
./configure; make; make install to remain the normal supported interface.
The new root/component wrappers delegate to CMake, select tools/check prerequisites
and propagate errors; optional make check is developer qualification. See
[frontend status](docs/developer/native-frontend.md). This is current Stage 1 work before
CP Pup comparison. Package-manager evaluation remains deferred. Agent Linux
frontend tests/integration passed with explicitly synthetic resource fixtures;
actual Mac frontend qualification is pending. Preserve existing private installs
and normal engine selection; no observation rerun, merge or cleanup starts here.

Current priority, approved 25 October 2026: Fernando defers pip-versus-Conda/
micromamba packaging as a TODO and resumes the existing native qualification.
See [current next work](docs/developer/roadmap.md) and native roadmap revision 1.4. Next is the
read-only CP Pup fixture/installed-candidate preflight, then isolated native
output comparison and remaining Stage 1 gates. Do not start package-manager
prototypes, provisioning, publication or bulk document moves as a prerequisite.
Preserve the qualified private installs and selected historical engine.

Documentation audience correction, 25 October 2026: Fernando requests a short
[user installation entry point](docs/installation.md) directly under docs; keep detailed
build/test/install material in [the developer guide](docs/developer/native-installation.md). Maintain
both with installation changes. Group developer navigation by topic; any later
physical move must update inbound links together. Package-manager review is a
proposal, not authorization to install/provision dependencies or publish binaries.
Conda/micromamba is the first recommended user-distribution evaluation; preserve
the existing CMake/CTest build and current working environments.

Maintained installation guide, approved 25 October 2026: Fernando requires
[the native installation guide](docs/developer/native-installation.md) under docs to stay current.
Update it in the same PR as changes to build/install tools, entry points,
platforms, resources/layout, selection, upgrade/rollback or qualification status.
Keep the Python installation hub, root README and build reference linked and
consistent; distinguish tested procedures from pending platform work.

Intel Mac native acceptance, 25 October 2026: Fernando reports C90/C17 native
builds, three CTest entries per mode, exact OCAM/WFI BPM pixels, checksum metadata
accounting, real private installations/repeats/installed CLI and C17 DESTDIR passed
at source 41c8e6a544c1bc5122dc558e0c8cc7904214e1d0. See
[the acceptance record](docs/developer/native-mac-build-install-acceptance.md). Historical engine and configuration
remain selected/unchanged. Observational pixel equivalence, installed wrapper,
calibration/WFI fixtures, failure/memory and chapman3 gates remain pending.
Prepare immutable observational fixtures next; publication starts no reduction,
engine switch, merge or branch cleanup. Earlier pending statuses below are historical.

Stage 4 amendment, 25 October 2026: Fernando requires creation and propagation
of per-pixel frame variances for science and calibration products. Follow
[roadmap revision 1.3](docs/developer/mefpp-modernization-roadmap-v1.md): squared units, masks, gain/RON,
calibration/parameter uncertainties, shared-normalization correlations and
Pycavi/resampling/photometry handoffs, with independent recovery tests. This is
future Stage 4 scope; preserve the current Stage 1 build-only boundary.

Stage 1 candidate implementation, 25 October 2026: Fernando authorized the isolated
bundled-source CMake build after reviewing stage 0 and reporting actual-Mac
fixture settings. See [candidate status](docs/developer/native-cmake-candidate.md)
and mefpp2/README.cmake.md. qfits is now under mefpp2/qfits5 in this candidate;
retain all 18 qfits and 79 Eclipse archive sources. Numerical algorithms,
allocator policy, existing installations and data remain unchanged. Agent Linux
GCC 13.3/CMake 3.29.6 code-only C90/C17 builds and three CTest entries per mode
passed; this is not Mac/chapman3 qualification. Actual BPM decompression, complete
runtime install and observational pixel equivalence are pending on the Mac.
No engine switch, observation rerun, memory-clean claim, merge or branch deletion
is authorized by this implementation. Earlier audit-only holds below are historical
where superseded by this bounded authorization.

Stage 0 native build specification, 25 October 2026: read
[the specification](docs/developer/native-build-specification-v1.md) before
implementation. It defines the minimum static target graph, runtime payload,
fixtures and pending gates. Mac synthetic C90/C17 CMake/CTest probe passed;
real native builds, fixture manifests and chapman3 toolchain remain pending.
Initial candidate tools: CMake/CTest 3.29, Unix Makefiles, explicit Xcode tools.
No native source/build/install change is made by this documentation delivery.

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

Current roadmap version 1, 25 October 2026: Fernando authorized documenting
[the native roadmap](docs/developer/mefpp-modernization-roadmap-v1.md) and
[current mefpp architecture](docs/developer/mefpp-current-architecture.md).
These supersede older sequencing descriptions for planning: clean build/install
Mac then chapman3, memory correctness, component extraction/new calibrations,
single detectors, parallel mosaics, native Windows qualification, CMOS last.
Windows portability is considered from the start. Preserve shared mosaic flat
normalization and distinguish acquisition gain/RON from processed effective values.
CMake/CTest and API names remain proposals; no implementation or install starts
from publication. Review/version the plan as evidence changes. Earlier dated
instructions below are historical where they conflict with this planning update.

Current hold before native modifications, 25 October 2026: Fernando requires
an expanded architecture/modern-practice/Eclipse-usage audit first, then a full
roadmap for review before any implementation. See
[the architecture audit](docs/developer/native-architecture-audit-2026-10-25.md)
and #73. Do not proceed directly from installation audit #64/#72 to moving
qfits, fixing builds or extracting components. Bias/BPM/non-linearity/dome/sky/
master-flat/science components are design candidates, not approved changes.
Current work is audit evidence/diagrams only; preserve source and installations.

Current scope override, 25 October 2026: Fernando explicitly brings point 5
forward for a mefpp/qfits build and installation audit, Intel Mac first and
chapman3 second, with qfits to move under mefpp. See
[the native installation audit](docs/developer/native-installation-audit-2026-10-25.md)
and #64. First audit is read-only source review/disposable fixture probes;
native source migration and target build/install acceptance remain pending.
This overrides earlier native-work deferral only for the bounded installation
task. Preserve existing engines/data; no numerical changes, upgrades, new
runtime parallelism or scientific tuning. Follow the latest canonical scope.

Current Mac handoff, 25 October 2026: selected installed-library paths for one
CP Pup r_SDSS exposure (32 detectors) passed through notebooks 03–09, including
both model applications and twelve catalogue QC PNGs. See
[the Mac pilot](docs/developer/pilots/mac-cp-pup-2017-03-13/README.md).
This is not full notebook orchestration, multi-exposure/filter Mac acceptance or
scientific validation. #62 parameter investigation and scientific tuning wait
until the agreed later stage after all fields are reduced. Current work records
acceptance/roadmap only; preserve outputs, and do not start refactoring, reruns,
upgrades or merge/cleanup without the applicable instruction. Earlier dated
handoffs below are historical; follow the newest canonical instructions.

Test explanations, approved 25 October 2026: before every functional test or
result-verification test, explain its purpose, inputs, actions, the actual
Pycavi subroutines/methods and native tools exercised, and expected outputs and
pass criteria. Distinguish processing from read-only verification and functional
success from scientific validation. In testing scripts and command groups, add
short comments identifying each test section; the announced tests and script
comments must correspond in both directions. Report actual results and
limitations after execution. See the canonical developer instructions.

Defect tracking, approved 23 October 2026: create a GitHub issue for each
distinct defect found, checking for an existing ticket first. Record evidence,
scope and acceptance criteria; link the fix and verification in a correction
comment before closing it. Keep unresolved native causes and pending target
qualification open. See the canonical developer instructions.

Current integration handoff, 24 October 2026: Fernando authorized merge and
cleanup of qualified PRs #43/#45/#47/#50/#52, in that dependency order. Preserve
all qualified commits and verify the final main tree against this integrated
head, then remove only merged branches with ancestry/tip checks. Synchronize
chapman3 from its inspected clean checkout; no reinstall or reduction rerun.
Selected functional paths through notebook 09 and twelve QC PNGs passed.
Scientific/orchestration/export/Mac gaps and #51 remain open. This instruction
authorizes integration/cleanup only, not further processing or unrelated fixes.

Latest scope, 23 October 2026: finish and document chapman3 dependency
qualification before the Pycavi workflow audit. Aim to align Mac versions where
practical. Python future-proofing follows the agreed five points, not this gate.
See the controlling dated updates in the developer instructions and roadmap.

Read and follow [the developer agent instructions](docs/developer/agent-instructions.md)
before work in this workspace or its component directories. Also read the
[architecture](docs/developer/architecture.md) and [roadmap](docs/developer/roadmap.md).

The immediate goal is an OmegaCAM reduction set for ESO Phase 3 submission.
Multiprocessing is within one node; mefpp remains serial for this milestone.
Component implementation changes require authorization for the relevant stage.

Before user-facing terminal commands, follow the machine/repository guards in
the developer instructions. Fernando works on Mac/wenu and chapman3/wenu-imaging
in parallel. Batch reduction launches must use niceness >=10; the interactive
Jupyter server/kernel stays at niceness 0 (23 October clarification).
Before changing either user's cloned wenu-imaging checkout or its installation,
obtain current Git/environment evidence from that actual computer; an agent's
checkout is not evidence of the user's local state. See the canonical policy.

After every push or merge, automatically provide the applicable complete,
guarded synchronization/verification commands and any authorized cleanup steps.
Give one command group at a time and inspect the user's result before dependent
operations. Distinguish agent-workspace, GitHub, chapman3 and Mac status; never
claim that remote delivery synchronized a user's clone. Follow the canonical
[delivery handoff rules](docs/developer/agent-instructions.md#delivery-handoff-and-local-synchronization).

The original audit is historical evidence, not the current agent policy.

Scope clarification, 21 October 2026: package wenu-imaging and debug/improve
Pycavi first; do not upgrade Python libraries or external engines yet. Audit
single-detector support and all opportunities for single-node parallel work.
mefpp implementation follows the Pycavi milestone. See the dated scope update
in the developer instructions and roadmap.
