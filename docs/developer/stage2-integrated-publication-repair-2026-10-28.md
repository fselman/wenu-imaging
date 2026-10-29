# Approved publication-status repair and one-use F3 resume

28 October 2026. Fernando approved the three-file repair and two added retests with "Proceed" after clarification of the matching header declarations. Immutable amendment v2.4 records the exact exception; v2.0–v2.3 remain unchanged. General repair rounds remain exhausted at 2/2; this is a separate one-use publication exception for #127.

## Native change

Only mefp_lib.c, mefp_lib.h and mefpp.c change. mef_save and mef_hdrpix_dump now return int (0 success, -1 failure). The helper checks file opening, qfits header status, stream error/flush/close, available pixel status and expected byte growth. It writes the same zero FITS padding through checked caller-side write/flush/close operations, avoiding the legacy void padding function. qfits source and calculations are unchanged; BPP_DEFAULT remains the output storage policy as before.

All four calibration publication calls and both science header/pixel publication calls propagate failure. A publication-only cleanup label releases owned local headers, lists, science cube, calibration/mask objects, labels and extension list before returning failure to the existing main/context destructor. Released local pointers are nulled to keep later publication-error cleanup safe. Other failure classes are not repaired or rerouted in this increment. Partial outputs and the protected target remain retained; failed requested publication stops dependent processing.

Legacy qfits_pixdump still hides some write/close results; expected byte growth detects truncation but is not universal delayed-I/O error detection. Deferred #128 records that library issue; #125 remains the separate deferred CONTINUE/long-value issue. Neither qfits change nor new fault matrix is included. No successful numerical/metadata policy is changed, and no full filesystem-failure coverage is claimed.

## Exact resume

qualify_integrated_failures_mac.py --resume-publication admits only the known F3-failures report at c722310, four passed roles plus blocked-output instrumented false success, unchanged blocker/five partial outputs, all preservation flags and counters 11 planned + 6 retests = 17 actual. It rehashes prior logs/inputs/products and reparses the original diagnostics; verifies the source diff is confined to the three approved native files and their recorded hashes; and checks the immutable v2.4 hash. The old F3 attempt is not overwritten. A fresh v2.4-publication directory and active-pointer guard permit only one attempt.

Execution order is fixed: blocked-output instrumented retry; one successful tiny instrumented publication smoke; blocked-output leaks; context allocation instrumented/leaks; cube allocation instrumented/leaks. The smoke retains the accepted F1 input/expected identities, exact arrays and ordered canonical metadata, with all success diagnostics. Blocked-output retests must now stop before dependent products are created and preserve the directory/marker. Both success/failure resource/descriptor/leaks gates stay active. Any finding stops the remaining roles, without automatic repair or second retry.

Cost: exactly two added retests plus at most five originally unrun F3 roles. On seven passes counters become 16 planned + 8 retests = 24 actual, with general rounds still 2/2 and the publication exception recorded separately. F4/final Mac C90/compact Chapman3 C17+C90 retain original order and scope. No F1/F2 or raw-WFI repetition, installation, merge or branch deletion.

## Preparation evidence and limits

C90/C17 syntax of common, recipe and actual observer pass. An actual-publication-helper unit linked from the common object passes in C90/C17 using controlled qfits stubs: success and exact controlled bytes, preserved blocked directory, invalid header, header error, pixel error, silent short pixel write, and flush/close error. These helper units are not recipe execution or Mac/qfits qualification. Python parent/result/injection controls and syntax pass; real-log parser controls remain from F3 preparation. Evidence/source identities are in fixtures/agent-publication-repair-2026-10-28/. Existing format-security warnings remain. Actual Mac corrected native and cleanup acceptance is pending; full original F3 archive has not yet been inspected. #127 stays open until reviewed target evidence.
