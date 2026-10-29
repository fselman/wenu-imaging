# Approved cube NULL-handling repair and one-use F3 resume

28 October 2026 (Chile). Fernando responded "authorized" to the two-C-file/two-added-retest proposal. Immutable amendment v2.5 records this exception; old v2.0–v2.4 bytes stay unchanged. General repair rounds remain 2/2, with no broader allocation repair authority.

Native scope is exactly src/iproc/cube_handling.c and ins/mef/common/mefp_lib.c. cube_new checks structure allocation, then plane-list allocation; it frees the partial structure if the latter fails. The MEF loader checks cube_new and releases its already loaded first image before returning NULL. Successful fields/pointers/pixel operations and existing upper framelist/error propagation are unchanged. No .h, recipe or qfits edits are added beyond the inherited publication repair.

## Bounded continuation

--resume-cube accepts only the stopped source-2e3969c v2.4-publication parent with five passed cases then cube-allocation instrumented exit 86/missing return marker, no partial cube outputs, preserved files and counters 15 planned + 8 retests = 23 actual. It verifies old command/input/product hashes, actual retained publication-smoke FITS and diagnostics, the other passed failure diagnostics, and the exact injection/UBSan text in the failed log. The source diff from tested 2e3969c must be confined to the two recorded native file identities. Earlier immutable hashes and v2.5 are checked; a new v2.5-cube-allocation directory and active pointer allow only one attempt.

Order: cube-allocation instrumented retry; one successful tiny instrumented cube-smoke; cube-allocation external leaks. The first must return a clean nonzero native failure with balanced owners, zero post-purge resources and stable descriptors, without a sanitizer error. The second keeps the accepted publication-smoke input/expected identities, every exact array and ordered canonical-header comparison, and all success diagnostics. Only if both pass may the one original unrun external-leaks role run with the same failure gates plus zero external leaks. No other passed F3/F1/F2 roles are repeated. A finding stops immediately; no second attempt or further repair is authorized.

Maximum three new launches: two retests plus one original planned role. Potential F3 counters become 16 planned + 10 retests = 26 actual; general rounds remain 2/2. The original failed attempts and all selected installations/inputs/products stay preserved. F4, final Mac C90, compact Chapman3 C17/C90 and final owner review retain their original scope/order. #129 stays open until actual Mac evidence is reviewed; full F3/v2.4 archive receipt is still pending.

## Agent verification

C90/C17 syntax of both affected units and the actual recipe observer passes. The actual constructor object and exact source MEF-loader excerpt pass controlled C90/C17 owner tests: failed structure, failed plane list, successful dimensions/initial pointers, exactly one loaded-image release on cube failure, balanced allocations and unchanged input pixels. External allocator/image/FITS services are stubs; this is not real qfits, Mac or recipe qualification. Python original and new reviewed-parent/result/injection controls pass, rejecting changed counters, status, preservation, extra outputs or missing exception state. Python syntax and patch whitespace checks pass. Source identities and loader excerpt hash are retained in fixtures/agent-cube-allocation-repair-2026-10-28/.

No recipe engine ran in the agent workspace. Actual corrected failure return/resource cleanup, exact successful smoke and external leaks remain pending on Mac. Existing format-security warnings remain. #125/#128 stay deferred, #116 unresolved; no scientific/Phase3/full Stage 2 acceptance, installation, merge or branch deletion.
