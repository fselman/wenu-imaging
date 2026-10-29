# Final integrated campaign owner review

Stage 2.1 endpoint revised by owner, 29 October 2026: [immutable amendment v2.8](native-roadmap-amendment-v2.8-2026-10-29.md) makes the gate **current mefpp/Pycavi reduction through notebook 04: native calibration/science preprocessing, Python normalization, solve-field and WCS-corrected MEF assembly**. Keep one filter and at most five equal-integration-time science exposures per instrument; all three WFI partitions are authorized for the same five exposures in total. Notebook 05 extraction/SCAMP, SWarp, photometric/illumination work, downstream QC and final catalogues are outside Stage 2.1 and deferred to later workflow work. Older v2.7/full-chain completion wording is historical and superseded; do not reopen it as a closure requirement.

Both bounded instrument sets have now passed the Stage 2.1 functional endpoint on the Intel Mac: native preprocessing, Python normalization, solve-field and WCS-corrected MEFs. OCAM: five r_SDSS exposures at 20 s, one partition, 160 solved detector images. WFI: five BB#B/99_ESO842 exposures at 89.9177 s across three partitions, 40 solved detector images. Pixel/input preservation checks passed. See the [returned-result receipt](stage2-1-functional-results-2026-10-29.md) for evidence paths and limits. The owner accepted Stage 2.1 on 29 October 2026 and authorized merging PR #130 and cleaning its merged branch. Next substantive work is Stage 2A review; preserve all baseline products and evidence. Preserve the failed first WFI SCAMP attempt outside this gate; #30/#131 remain open for later production work. No scientific/Phase 3 certification or automatic Stage 2A/refactoring is claimed.

**Owner disposition accepted:** after reviewing #116, the owner instructed to leave it for now and finish the current work in a clean state for tomorrow. The bounded Stage 2 campaign is accepted with #116 open/unresolved and the named testing limitations retained. No additional engine runs or repairs are planned. Phase 3 planning is deferred and is not a closure gate. Integration and clean-checkout handoff follow the current wrap-up instruction.

## Fixed results

| Fixed item | Final disposition | Evidence |
|---|---|---|
| Prior accepted work and input lock | Reused/preserved | Frozen roadmap v2 and accepted eleven-file WFI lock |
| F1 tiny integrated OmegaCAM | Accepted Mac ordinary/instrumented/leaks | [F1/F2 receipt](stage2-integrated-f1-f2-acceptance-2026-10-28.md); exact independently reread products |
| F2 selected real WFI | Accepted Mac ordinary/instrumented/leaks | Same receipt; host-verified cross-lane arrays/metadata, large FITS retained Mac-side |
| F3 five fixed failures | Accepted ten final roles plus two exact smokes; failed history preserved | [F3 receipt](stage2-integrated-f3-acceptance-2026-10-28.md) |
| F4 same-process repetition | Accepted warmup + ten cycles in one process | [F4 receipt](stage2-integrated-f4-acceptance-2026-10-28.md) |
| Final Mac C90 compile/link | Accepted; no runtime replay | [C90 receipt](stage2-final-c90-mac-acceptance-2026-10-28.md) |
| F5 final Chapman C17/C90 | Accepted one complete tiny workflow per mode | [F5 receipt](stage2-integrated-f5-acceptance-2026-10-28.md) |

Counts are **19/19 planned + 10 separately recorded retests = 29 actual launches**. General correction rounds stay 2/2; specifically authorized v2.2–v2.5 exceptions are recorded separately and consumed. No frozen file/amendment was edited in place. No installed engine/package selection changed; raw frames, originals, all failed/successful runs and transfers remain preserved.

## Named residuals and boundaries

- **#116 unresolved/nonreproduced:** original same-count descriptor identity change remains unattributed. Later exact descriptor passes, including F4/F5, do not explain it. Keep OPEN; no whitelist, waiver or further blind repetition. Requested owner decision: accept it as a named residual for the bounded Stage 2 exit, or declare Stage 2 blocked and specify a separately bounded attribution task.
- **Target external diagnostics:** final Chapman evidence is functional/internal accounting/owners/descriptors only. External sanitizer/leaks qualification there was intentionally excluded by the accepted frozen roadmap, not newly performed or silently claimed.
- **Workload limits:** controlled tiny failure points/repetition and selected WFI data, not every allocator fallback, large-file mmap/swap stress, detector combination or filter. No claim that all possible native paths are leak-free.
- **Compiler/library debt:** retained warnings remain. qfits long-value safety/CONTINUE (#125) and lower-level publication checks (#128) remain deferred; these are not absorbed into this campaign. ESO Phase 3 itself does not support CONTINUE under the currently linked v8 standard; see the matrix.
- **Evidence boundaries:** large WFI arrays were host-verified; F5 and final C90 binaries remain on their hosts with host-verified hashes. Uploaded tiny products/logs were independently reread. No new wrapper/notebook or scientific/Phase 3 acceptance is claimed; wrapper code/cwd contract was not redesigned by these native fixes.

The bounded corrections #121 overscan, #122 header/name owners, #123 flat temporaries and #124 context/metadata owners meet their requested Mac plus final C90/Chapman checks. Correction/evidence comments precede their closure and the bounded context-ownership ticket #75 closure. #126/#127/#129 were already closed after verified evidence. #116 remains open; accepted bounds do not establish harmlessness or resolve its original cause.

## Closure and tomorrow handoff

Owner has chosen to finish the bounded work with #116 deferred. Preserve the named limitations above; no further descriptor campaign is scheduled. Phase 3 documentation/validation is future release work, not part of this wrap-up. The unpublished draft matrix is not included in this delivery. Frozen contract files remain unchanged; numbered amendment v2.6 records the accepted disposition/deferral.

Integrate PR #119 then #120, verify final main tree equals the accepted closure tree, and synchronize both actual host checkouts by guarded fast-forward. Remove only exact merged roadmap/campaign branches with ancestry/tip checks. Preserve every run, archive, raw frame, build, installation and selected configuration. No reinstallation or processing rerun.

Tomorrow begins from clean synchronized main after returned host verification. Next roadmap topic is the planned Stage 2A data-representation/configuration review; begin no implementation/extraction automatically. Carry forward the agreed format-independent configuration, detector identity, reduction/recipe/product profile distinctions and shallow metadata-driven disk layout. Phase 3 stays deferred. #116 remains open/unresolved, qfits #125/#128 and existing warnings remain explicit future debt.

Historical subsequent owner addition (endpoint superseded by v2.8): amendment v2.7 inserts Stage 2.1 full current mefpp/Pycavi OCAM and WFI processing before Stage 2A. Thus the immediate next task is the bounded full-workflow baseline preparation, not representation/refactoring. Completed Stage 2 remains accepted without rerun; Phase 3 remains deferred.
