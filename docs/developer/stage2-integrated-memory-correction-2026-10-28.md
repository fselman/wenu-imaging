# Inspected integrated memory finding and final repair — 28 October 2026

This is the second and final globally permitted correction round under frozen
roadmap v2.0/v2.1, in PR #120. Issues #122–#124 remain open pending actual Mac
verification. No new workloads, changed expectations, installation or merge.

The supplied `integrated-campaign-evidence.tar.gz` has SHA256
`bd27d7c67ab55f80b9e6927b904560b6c1a01b289b7d5976e95894bbcc7ff6a0`.
All 141 manifest file identities and all command-log identities verify. Both
corrected F1 ordinary and instrumented products independently pass exact tiny
known answers, detector mapping, all six categories and the complete ordered
canonical-header comparison; they match each other. Inputs and selected installed
files remain preserved in the reports. This verifies #121 numerically on the Mac;
its final target regression and wider campaign acceptance remain pending.

The instrumented process and native driver returned zero. Its context count is
one constructed / one destroyed; six calibration calls, two BPM calls, two
combined-flat calls and two science loads match the declared sequence. Product
owners reach zero with no mismatch. Exact per-fd identities remain unchanged at
driver return and both purges. No ASan/UBSan finding was reported.

The memory gate correctly fails: after driver return there are 5,932 registrations /
205,015 bytes; the first purge removes 85 cache registrations / 998 bytes. Both
purges then leave exactly **5,847 RAM allocations / 204,017 bytes**, with zero
mapped files, mapping references and swap bytes. External leaks has not executed;
zero tracked-resource acceptance has not been achieved.

## Source attribution and bounded changes

| Issue | Source-confirmed missing release | Retained evidence / repair |
|---|---|---|
| #122 | Published primary/extension headers in `mef_save`; overwritten extension and Phase3 headers in `mef_get_headers_for`; auxiliary primary in `mef_header_ext`; allocated getter filenames | Hundreds of entries appear around each publication; final inventory includes 1,399 56-byte header nodes and 694 81-byte raw lines. Destroy after copy/write or transfer returned-header ownership; clean incomplete local assembly. |
| #123 | Per-frame `pixval_double`; two scaled-bias image operands in combined flat | Exactly twenty 648-byte double buffers (12,960 bytes), plus four image structs and four pixel arrays (1,360 bytes), match stage/extension boundaries. Free scratch after its last calculation and image temporaries after subtraction. |
| #124 | Validation lists/filter copies/partition replacements, configured BPM name replaced by CLI, engine extension labels, frame-name elements/scan/statistic arrays, engine BPM list/extension vector and context provenance IDs | Context/pre-stage/science clusters agree with these ownership omissions. Release on replacement and after publication, clear pointers, and release outstanding per-extension work from the context destructor. |

The inventory provides pointer sizes and boundaries, not allocation call stacks;
not every retained pointer is independently attributed to an exact source line.
The source omissions themselves are explicit. `framelist_firstname` returns a
**borrowed static buffer**: the patch does not free that value. Only validation's
single-FITS fallback creates an owned first-name copy. FITS insertion/merge copies
card values, so input headers are released only after those copies have completed.

A small `mef_bb_clear_work` helper releases context-owned frame-name elements,
scan/statistic arrays and the extension label after the final product publication,
and from final context destruction if work remains. Arrays are zero-initialized
so partial name-list acquisition can be destroyed safely; released fields are set
to NULL. Generated product IDs remain alive for all dependent header references
and are released on replacement/final context cleanup. No generic allocator sweep
or forced purge is used to conceal ownership.

Pixel operations, their order, thresholds, flat normalization, masks and header
values/order are unchanged. Historical installed engines and scientific products
are untouched. The corrected ordinary F1 result from f0242b2 becomes an additional
exact product/metadata reference, alongside the independent known answers.

## Final-round continuation

The resume guard verifies the reviewed correction-round-1 report, both prior case
input/product identities, all command logs, installed identities and the original
ancestor-report hash. It creates a separate `correction-round-2` directory under
the original campaign and preserves both earlier attempts. Only the two reviewed
parents are supported; a third correction attempt is explicitly rejected.

Round 2 reruns the failed instrumented F1 and one ordinary successful-workflow
smoke. Ordinary runs first to establish a current control and must match the
retained corrected ordinary result exactly. Remaining F1 leaks and F2 roles are
previously unrun planned entries, not another campaign. Any finding stops dependent
cases. Current counts are two planned launches, one correction retry, three actual
engine launches and one round consumed. If all F1/F2 roles then pass, counts become
six planned, three correction retries, nine actual launches and two rounds consumed.
F3–F5 retain their existing position and budget. No third repair round is implied.

## Checks and limits

Agent Linux C90/C17 syntax-only checks of the common library and included-recipe
observer pass, including implicit-declaration and incompatible-pointer checks.
Three existing format-security warnings remain. Python compilation and guard
controls pass: preserving the parent, rejecting altered logs/reset/duplicate or
advanced attempts, correct final-round counters, and refusal of a third round.
The guard test mocks product readback only for its constructed parent; actual
archive products were independently read and verified without that mock.

No native engine executed in the agent environment. Actual corrected Mac memory,
external leaks, observational WFI and F3–F5 acceptance are pending. The final stable
Mac C90 build and compact Chapman3 C17/C90 pair remain required. #116 remains open.

See [inspection result](fixtures/agent-integrated-memory-correction-2026-10-28/inspection-result.json)
and [preparation record](fixtures/agent-integrated-memory-correction-2026-10-28/run-provenance.json).
