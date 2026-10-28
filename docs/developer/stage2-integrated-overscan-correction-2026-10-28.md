# F1 overscan finding and correction round 1 — 28 October 2026

Issue [#121](https://github.com/fselman/wenu-imaging/issues/121), within PR #120.
This is a demonstrated defect on a declared integrated path and a bounded repair
under frozen roadmap v2.0/v2.1. No expected arrays, tolerance, thresholds, raw
selection, calibration method or campaign rows change. No merge or installation.

## Retained actual-Mac finding

Source `fa2e5c2f508e18d18981b8e987b86cc4a411c1df`; run
`/Users/fselman/Software/build/wenu-imaging/mac-stage2-integrated-du1sqj06`.
All three C17 builds completed. F1 ordinary returned native exit 0 but failed the
independent exact dome-extension-2 comparison. Only one planned engine launch ran;
ASan/UBSan, external leaks and F2 did not execute. The user supplied read-only
product statistics and reported all staged input hashes unchanged. The original
archive has not been uploaded or independently inspected in full by the agent.

Both bias extensions are constant `1.1111106872558594`, instead of zero. Dome
extension 2 is `1.9999432563781738`; sky extension 2 is `1.999907374382019`.
Combined flats and science show propagated offsets; science is
`1000.0925903320312` / `1000.0926513671875`, instead of 1000. Both BPM arrays
match exactly. The FITS HIERARCH keyword warnings are informational.

## Cause and minimal correction

`function1d_average_reject` in `mefpp2/src/math/function_1d.c` sorts the scan
samples, starts summation at `pix_low+1`, but divides by
`npix-pix_high-pix_low`. Its documented zero-based retained interval starts at
`pix_low`: the current loop skips one retained value without adjusting the divisor.
Its only in-tree C caller is `mef_overscan_correction` in the common MEF library.

For F1's nine overscan pixels, all 10, with zero rejection, the old implementation
sums eight values and divides by nine. Subtracting that float32 estimate leaves
exactly the observed 1.111110687 offset. This explains a real implementation error,
not a rounding tolerance issue or a wrong expected bias. With a nonzero configured
rejection count the same loop/divisor inconsistency remains relevant.

The correction changes only the loop start to `pix_low`, restoring the documented
trimmed mean. Rejection policy and subsequent calculations are unchanged. Old
working installations and historical scientific products remain untouched. This
native source change activates the existing final C90 build checkpoint; the final
compact Chapman3 C17/C90 pair remains at its original position.

## Same-campaign retry and budgets

The explicit `--resume-correction` path accepts only the reviewed original report,
source, one failed F1 ordinary role and expected finding. It checks the active
campaign pointer, protected installed identities, prior preservation flags, all
retained command-log hashes and original fixture-input identities. A separate
`correction-round-1` directory preserves every original file. Duplicate/advanced
attempts are rejected; neither deleting the old run nor restarting the campaign
counter is part of the procedure.

The corrected ordinary F1 run is one correction retest. The unrun F1 diagnostic
lanes and F2 roles remain their existing planned launches. Reports distinguish
planned launches (cap 19), correction retests, total actual engine launches and
global correction rounds (cap 2). Round 1 is consumed when resume begins. If the
six roles pass, cumulative counts are six planned launches plus one correction
retest, seven actual launches, and one correction round. Any finding stops the
remaining dependent roles; there is no automatic second correction or new matrix.

New F1 staged input/expected-array hashes must equal the original failed attempt.
The original report's hash is retained and rechecked after the retry. F3–F5 remain
pending in the same campaign; no full Stage 2 acceptance is asserted.

## Preparation checks and pending acceptance

Agent Linux C90/C17 syntax-only compilation of the changed arithmetic file passed,
without diagnostics. Python compilation and constructed resume-guard checks pass:
existing-pointer resets, altered original logs, duplicate correction directories
and already-advanced pointers are rejected; the reviewed parent is preserved
byte-for-byte. These checks execute no native engine and are not numerical Mac
acceptance. The unchanged F1 known answers and remaining fixed diagnostic lanes
must validate the correction on the actual Mac. #121 remains open.

See [preparation provenance](fixtures/agent-integrated-overscan-correction-2026-10-28/run-provenance.json).
