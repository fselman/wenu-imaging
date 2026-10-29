# Integrated Mac F1/F2 acceptance — 28 October 2026

The bounded integrated successful-workflow slice is accepted. Actual Mac F1 tiny two-extension OmegaCAM ordinary, ASan/UBSan observer and external-leaks lanes pass at 92421749d8350d9b6438d7b16014555a228f2c5f. F2 fixed eleven-file/eight-extension WFI passes the same three lanes at f5afd08fbfb35a8a50409c92352f9061c92c1f69, after the approved caller-side BPM filename correction. F1 is explicitly inherited, not rerun or attributed to the new source. All six calibration/science categories are present in each accepted lane.

## Evidence and checks

Archive integrated-f1-f2-evidence.tar.gz, SHA256 0ee502ce3380799b67fca89541c824e8664927dd991aee1257900033752fc61d, attachment libfile_5ec3f514eae48191b48740b182e07624. All 416 file identities, archive member set, 52 command-log hashes and five source-attributed attempt reports verify. Native execution history is 12 total launches: 6 planned plus 6 correction/exception retests, general repair rounds 2/2. No native processing ran during inspection.

The archived F1 FITS files were independently reread against unchanged exact expected arrays; all six categories and both ordered extensions pass, and all three lanes' canonical metadata and physical-array hashes agree. Archived F1/F2 logs were independently reparsed through the actual ownership/accounting/descriptor parser; contexts and products balance, both post-purge boundaries contain zero RAM pointers/bytes, mappings/references and swap bytes, exact descriptor identities remain stable, and both external-leaks summaries are zero. Four diagnostic lanes pass. Six build records identify Darwin x86_64 AppleClang 15, C17, CMake 3.29.3, qfits memory mode 2 / 2,000,000 pointer policy; ASan/UBSan symbol logs verify.

F2 reports contain six products and eight ordered detector extensions per role, with exact pixel and canonical-header agreement across ordinary/instrumented/leaks. Source-pinned host verification checked filename-only BPM provenance on primary and all detector HDUs before reporting success. Complete archived console cards show the three expected filenames. stdout/stderr interleave in some console lines; these are not used as a substitute for the host FITS header checks. Raw/checkout/selected installation/prior-report/inherited-evidence preservation flags all pass, and the report/ancestor/log hashes match the transfer. HIERARCH conversion notices are warnings, not failed gates.

## Limits and disposition

Large WFI inputs/products were intentionally not transferred. Their pixels and ordered headers were checked on the Mac by the pinned runner; inspection checks its reports and logs, not a second local read of those large arrays. This is functional/resource qualification, not independent scientific validation or ESO Phase 3 certification. No observational rerun is requested solely to duplicate that check.

Immediate filename defect #126 meets its bounded Mac acceptance criteria; close with correction/evidence reference. qfits arbitrary-long-value safety and CONTINUE capabilities remain open/deferred as #125; fits_h.c is unchanged. #121–#124 have positive Mac verification but remain open for their previously declared final target/checkpoint disposition. #116 remains unresolved/non-reproduced.

F3 five fixed failure-handling cases, F4 fixed same-process cycles, the final Mac C90 compatibility build and F5 compact Chapman3 C17/C90 remain pending in the approved order. No new matrix, correction round, merge, deletion, installation or scientific tuning is authorized by this receipt. The user Mac remains clean at f5afd08; documentation-only delivery requires no host synchronization or diagnostic rerun.

Reproduction: extract the verified attachment to a fresh directory, then run fixtures/mac-integrated-f1-f2-inspected-2026-10-28/verify_f1_f2_evidence.py with --evidence and --result. The fixture directory retains both accepted reports, all six build records, transfer manifest, inspection result and verifier.
