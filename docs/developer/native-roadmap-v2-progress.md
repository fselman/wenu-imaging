# Frozen roadmap v2 progress ledger

Next-stage direction approved, 29 October 2026: [amendment v2.9](native-roadmap-amendment-v2.9-2026-10-29.md) authorizes analysis/design of mefpp subroutines, typed TOML configuration subsets, ASDF processing metadata referencing FITS-resident images, parallel-ready and single-detector interfaces, notebooks 01/03 and an optional mefppy Python library. See the [initial source analysis](mefpp-refactor-analysis-2026-10-29.md). TOML/ASDF-with-FITS is now the owner-selected design direction; exact schemas/adapters/bindings and directory layout remain proposals. Read-only larger Chapman inventory is pending actual-host evidence; do not assume its reductions are complete. No production implementation, installation, data migration or reduction rerun begins from this analysis. Stage 2/2.1 stay accepted; other exploratory WISDG/retrieval/layout ideas remain unadopted.

Stage 2.1 endpoint revised by owner, 29 October 2026: [immutable amendment v2.8](native-roadmap-amendment-v2.8-2026-10-29.md) makes the gate **current mefpp/Pycavi reduction through notebook 04: native calibration/science preprocessing, Python normalization, solve-field and WCS-corrected MEF assembly**. Keep one filter and at most five equal-integration-time science exposures per instrument; all three WFI partitions are authorized for the same five exposures in total. Notebook 05 extraction/SCAMP, SWarp, photometric/illumination work, downstream QC and final catalogues are outside Stage 2.1 and deferred to later workflow work. Older v2.7/full-chain completion wording is historical and superseded; do not reopen it as a closure requirement.

Both bounded instrument sets have now passed the Stage 2.1 functional endpoint on the Intel Mac: native preprocessing, Python normalization, solve-field and WCS-corrected MEFs. OCAM: five r_SDSS exposures at 20 s, one partition, 160 solved detector images. WFI: five BB#B/99_ESO842 exposures at 89.9177 s across three partitions, 40 solved detector images. Pixel/input preservation checks passed. See the [returned-result receipt](stage2-1-functional-results-2026-10-29.md) for evidence paths and limits. The owner accepted Stage 2.1 on 29 October 2026 and authorized merging PR #130 and cleaning its merged branch. Next substantive work is Stage 2A review; preserve all baseline products and evidence. Preserve the failed first WFI SCAMP attempt outside this gate; #30/#131 remain open for later production work. No scientific/Phase 3 certification or automatic Stage 2A/refactoring is claimed.

Controlling contract: [frozen roadmap v2.0](native-roadmap-frozen-v2.0-2026-10-28.md), with [owner-requested amendment v2.1](native-roadmap-amendment-v2.1-2026-10-28.md). The amended campaign cap is 19 planned native launches. [Approved v2.2](native-roadmap-amendment-v2.2-2026-10-28.md) separately permits one four-array cleanup and two tiny validations; the two-round limit remains exhausted.
This ledger may update status and evidence links. It must not add requirements,
rows, launches, repair rounds or completion gates. Amendments are separate files.

| Fixed item | Status | Evidence / limitation |
|---|---|---|
| Owner acceptance of concrete frozen proposal | Accepted 28 October 2026 | Fernando: "proceed", after v2.1 request; see acceptance record |
| Prior accepted build/context/parser/split/BPM work | Accepted and preserved | Main b0061b55b9ff8dc2d185c3c403c5119a25b606a5; PRs #115/#117 and earlier receipts |
| One input inventory/reference lock | Locked; header inventory and selected-content report inspected | WFI at /Users/fselman/Pictures/WFI; 11 reported SHA256 identities and fixed lists; see integrated runner record |
| F1 integrated tiny OmegaCAM | Accepted at 9242174: all three Mac lanes | Archived exact FITS and diagnostic logs independently checked; inherited at later source |
| F2 integrated selected WFI | Accepted at f5afd08: all three Mac lanes after filename correction | Six products/eight detectors; host pixel/header reports agree, archived diagnostics pass; large FITS stay on Mac |
| F3 five fixed failure cases | Accepted bounded F3; full archive inspected | Ten final failure roles and two exact smokes; 539 files / 35 logs / six builds verified; historical #127/#129 failures preserved |
| F4 fixed same-process repetition | Accepted; archive independently inspected | One process, warmup + ten cycles; 66 exact products / 132 detector arrays, zero cleaned resources and stable descriptors |
| F5 compact Chapman3 regression | Accepted; full archive independently inspected | 94 files / six logs, exact C17/C90 products and metadata, owners/accounting/descriptors; no target external-memory qualification |
| Final C90 compatibility checkpoint | Accepted Mac C90 compile/link at b93ffda | Actual -std=c90, AppleClang 15; six archive files / 389 source inputs verified; existing warnings retained, no processing rerun |
| Correction/retest budget | 2/2 consumed; approved v2.2–v2.5 exceptions consumed | Final 19 planned + 10 retests = 29 actual; no engine launches remain; no automatic repair/retry |
| #116 disposition | Open | Original descriptor identity mismatch remains unattributed/non-reproduced |
| Target external diagnostics | Limitation remains open | Accepted v2.0 removes it as an automatic block to the Mac-led campaign |
| Final Stage 2 owner disposition | Accepted bounded closure; Phase 3 deferred | #116 open/unresolved/deferred by owner; no additional runs, scientific/archive acceptance or automatic implementation |

Current evidence: [F1 overscan finding and bounded correction](stage2-integrated-overscan-correction-2026-10-28.md). Remaining rows are unrun, not failed.

Latest evidence: [inspected memory finding and final correction](stage2-integrated-memory-correction-2026-10-28.md).

Final-round terminal result (user-reported, full evidence not yet inspected): source 3e60e8cbf198bd786dd1929e48e60f5c066be854; correction-round-2/run-provenance.json; F1 ordinary passed, F1 instrumented stopped on both post-purge resource gates. External leaks and all later rows remain unrun. Read-only residual inspection and a bounded owner decision remain pending.

Fernando approved the concrete four-release / two-validation exception with "proceed" after identifying the modified native file. Residual is user-reported 4 allocations / 32 bytes with balanced owners and all preservation flags true. Native exception verification remains pending.

Latest: [approved BPM provenance correction](native-roadmap-amendment-v2.3-2026-10-28.md), #126. Deferred qfits CONTINUE and writer safety is #125; no qfits implementation in this increment. Earlier terminal statements above are historical.

[One-use F2 continuation prepared](stage2-bpm-filename-resume-2026-10-28.md): Python controls pass; no native launches. Preserve F1 as inherited at source 9242174. Maximum one F2 retest plus its two originally unrun diagnostic roles; successful cumulative count 12 (6 planned + 6 retests), 2/2 general rounds unchanged.

Latest accepted status: [integrated F1/F2 evidence receipt](stage2-integrated-f1-f2-acceptance-2026-10-28.md). Archive 0ee502ce: 416 files / 52 logs verified; F1 FITS reread, WFI host reports and all memory/descriptor/leaks logs accepted with explicit transfer limitations. Earlier blocked/pending F1/F2 statements above are historical. Next fixed row F3; no extra native launch during receipt.

[F3 one-use runner prepared](stage2-integrated-f3-preparation-2026-10-28.md), no production changes or native launches. At most ten originally planned cases; current total remains 12, potential total after F3 is 22. Stop at first finding with the exhausted repair budget unchanged.

Latest blocker: [F3 publication false-success and bounded decision](stage2-integrated-f3-publication-blocker-2026-10-28.md), #127. No correction/retry or later-row execution occurred; current actual count 17. Four F3 roles reportedly pass; remaining five are unrun, not failed.

[Approved v2.4 publication repair/resume prepared](stage2-integrated-publication-repair-2026-10-28.md). Agent syntax/helper/guard checks pass, no recipe launch. Actual corrected F3 execution is pending at 17 cumulative launches. Prior blocked decision above is superseded only for this exact approved exception; later findings still stop without automatic repair.

Latest: [cube-allocation #129 blocked decision](stage2-integrated-f3-cube-blocker-2026-10-28.md). UBSan confirms injected NULL dereference at 2e3969c; publication validations and context failure lanes reportedly pass. No new native source change or launch during diagnosis. Proposed two-file repair/two added retests is not approved.

[Approved v2.5 cube repair/resume prepared](stage2-integrated-cube-repair-2026-10-28.md). User authorized exact two-C-file/two-retest proposal; agent syntax/owner/guard checks pass, recipe launches 0. Current cumulative count remains 23; no further repair/retry beyond this one-use exception.

Latest controlling status: [F3 archive accepted](stage2-integrated-f3-acceptance-2026-10-28.md), [F4 prepared](stage2-integrated-f4-preparation-2026-10-28.md). Current 26 actual; after F4 27, after paired F5 at most 29. Preparation/receipt consumed zero native launches. Earlier pending/blocked statements are historical; no frozen contract bytes changed.

Latest controlling status: [F4 accepted](stage2-integrated-f4-acceptance-2026-10-28.md), all 421 archive identities checked. Current 27 actual; only final Mac C90 build, two compact F5 launches and owner/Phase 3 review remain. Receipt consumes zero launches and requires no host sync.

Latest: [final Mac C90 accepted](stage2-final-c90-mac-acceptance-2026-10-28.md); counts unchanged at 27 actual. Next compact Chapman pair, then final owner/Phase 3 review. Older pending-C90 statements are historical.

Latest: [F5 prepared](stage2-integrated-f5-preparation-2026-10-28.md) following actual clean Chapman preflight. Python preparation checks pass, target execution remains pending at 27 actual. Only two fixed native launches and final owner/Phase 3 review remain.

Latest controlling status: [F5 accepted](stage2-integrated-f5-acceptance-2026-10-28.md); [final owner-review decision](stage2-integrated-owner-review-2026-10-28.md) ready; Phase 3 is deferred by the later owner disposition. Final count 19/19 planned, 29 actual. No further runs or automatic scope expansion. The owner subsequently accepted bounded closure with #116 deferred (v2.6); older pending statements are historical.

Controlling owner disposition: [v2.6](native-roadmap-amendment-v2.6-2026-10-28.md) accepts bounded Stage 2 closure with #116 open/unresolved/deferred; Phase 3 is deferred outside this gate. Finish integration and guarded clean-main handoff; no engine reruns.

Historical owner addition after accepted closure (endpoint now superseded by v2.8): [v2.7 Stage 2.1](native-roadmap-amendment-v2.7-2026-10-28.md) adds full current mefpp/Pycavi reductions for one OCAM and one WFI dataset before Stage 2A. This separate planned functional baseline does not add rows/launches to the completed 19/19 Stage 2 campaign. No processing starts with publication; both hosts remain clean main.
