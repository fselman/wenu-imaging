# Frozen roadmap amendment v2.2 — bias-QC cleanup exception

Owner: Fernando Selman. Approved 28 October 2026 by "proceed" following the
explicit proposal to release four bias-QC arrays and allow two tiny validation
runs, then continue the original remaining campaign only if both pass.

The frozen v2.0 contract and v2.1 amendment remain byte-identical. Their two global
repair rounds are exhausted and remain exhausted. This separately numbered,
one-time exception permits only:

1. Four releases in `mefpp2/ins/mef/common/mefp_lib.c`, `mef_bb_del()`:
   `bias_framethr_lo`, `bias_framethr_hi`, `bias_avg1`, `bias_sig1`.
   These context-owned per-detector float arrays have no final release. Their
   four two-float allocations match the user-reported residual four allocations /
   32 bytes after both purges. No calculations, expectations or tolerances change.
2. One tiny ordinary C17 workflow validation and one tiny ASan/UBSan validation,
   in that order, within the same preserved campaign. No retry of this exception.
3. Continuation of the already declared, previously unrun campaign rows only if
   both validations pass. All existing product/metadata/owner/resource/descriptor
   gates remain active. A finding stops dependent execution and requires a new
   explicit decision; this exception authorizes no further native correction.

The additional cost is exactly two native validation launches (compilation is
excluded as before). The planned campaign cap stays 19; the completed repair
round count stays 2/2. Record this exception separately, with a one-use guard.
At authorization: two planned launches plus three correction retries equal five
actual launches. If the exception and remaining F1/F2 roles pass: six planned,
five additional correction/exception validations, eleven actual launches.
F3–F5, the final C90 checkpoint and final owner review retain their original order.

Preserve all three existing attempts, raw inputs, expected arrays, configuration,
reports, archives and selected installations. This amendment authorizes neither
merge nor branch deletion. Publication or syntax checks do not establish corrected
Mac memory acceptance. #124 and Stage 2 remain open pending execution/review.
