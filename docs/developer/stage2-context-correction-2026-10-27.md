# Context-owned string cleanup correction — 27 October 2026

Issue #99; Stage 2 S2-02 / broader #75. Mac correction accepted; Chapman3 target acceptance pending. See [inspected Mac results](stage2-context-mac-acceptance-2026-10-27.md).
Stacked on the inspected unchanged baseline in PR #100.

## Demonstrated defect and bounded change

The inspected baseline completes all 48 native context-result contracts but
fails memory acceptance in 24 cases. Valid construction/destruction and late
PAF rejection retain 29 allocations / 550 bytes per call, identically in
OCAM/WFI, C90/C17 and both diagnostic lanes. Three same-process calls grow
through 29/550, 58/1100, 87/1650. Early rejection returns to zero.
See [retained baseline and attribution](stage2-context-baseline-evidence-2026-10-27.md).

The omission inventory accounts exactly for those 29 independently duplicated
strings: 27 Phase 3 configuration members plus master_flat_key/comment.
Their original PAF values including NUL terminators sum to 550 bytes per
instrument. Their uses do not transfer ownership away from the context.

Add only the missing NULL-guarded member releases inside mef_bb_del, in the
same style as existing member cleanup. A context rejected partway through
construction is zero-initialized, so only successfully acquired members are
released. No new allocation, field, helper/API or ownership transfer is added.
Existing releases remain single, and the caller still destroys published
contexts once.

The constructor, configuration values/quoting, producers, arithmetic, thresholds,
allocator policy, FITS products and selected installations are unchanged.
No metadata-content cleanup, scientific tuning or image rerun belongs in this fix.

## Corrected Mac verification

Keep the C driver and OCAM/WFI PAF bytes unchanged. Repeat the same 48 cases
and the same four private builds on the Mac:
C90/C17 × instrumented/uninstrumented leaks-accounting × OCAM/WFI × six variants.
Expected context creation/rejection and per-call configuration fingerprints
remain exactly as in the original baseline. Allocator ownership after every
call and at final cleanup must return to the recorded initial baseline.
No unexplained invalid-access/UB or unreachable leak is acceptable.

The Python orchestration gains only phase/provenance labelling and an explicit
comparison against the reviewed baseline report. For corrected execution use
--phase corrected and --compare-baseline pointing to the original run report.
The input report must byte-match the committed inspected report before execution.
It is rehashed on completion; no original report/input/output may be overwritten.
All 48 staged PAF hashes, constructor contracts and configuration fingerprints
must match the corresponding baseline case. Any discrepancy fails qualification.

New corrected work is created under
~/Software/build/wenu-imaging/mac-stage2-context-corrected-*/.
Every new build/test/source directory has provenance before workload execution.
Preserve logs and failed attempts; the original failed baseline remains untouched.
The script name qualify_context_baseline.py is retained to reuse its matrix;
the --phase field and actual tested commit identify the corrected attempt.

The original candidate preparation reviewed source ownership/byte attribution,
exactly 29 added guarded releases restricted to mef_bb_del, and Python syntax.
Actual corrected Mac execution has since passed all 48 cases; the linked
acceptance record preserves the independently inspected runtime evidence.
Chapman3 target verification remains pending.

## Target gate and remaining scope

After inspecting corrected Mac evidence, verify the unchanged C driver and
fixture/context-result expectations on Chapman3 in C90/C17. Its compatible
memory-tooling gap remains explicit; functional/accounting evidence must not
be described as sanitizer coverage. Preserve both working installations.
No automatic install or normal-engine selection follows this source correction.

Keep #99 open until corrected actual-host evidence and its bounded acceptance
are linked. Keep #75 and broader Stage 2 cache, image/cube/list/header, allocation
failure, full repeated-stage and mapped/swap qualification open. No Stage 2A
representation or component extraction starts from this correction.
