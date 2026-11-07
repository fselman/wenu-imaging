# Paired conversion gain and raw-pair RON: implementation candidate

## Actual Mac acceptance - 3 November 2026

Fernando returned actual e0b1647649515aa203932876887b6dff5983871f success:
native_gain_pair and native_gain_pair_allocation passed2/2 in 2.58 s.
Retained /Users/fselman/Software/build/wenu-imaging/mac-gain-pair-AdGQvwqZ.
QUALIFICATION passed; checkout/installed_files/exported_source all true.
Issue #228's corrected test-only oracle is accepted and closed. This qualifies
the paired helper on the Mac, not full characterization or real-data science.
The next [joint numerical interface review](joint-shutter-linearity-interface-2026-11-03.pdf)
proposes checked Eclipse extensions before implementation. Earlier pending
Mac statements below are historical preparation status; retain their evidence.

3 November 2026. Owner authorized the reviewed Eclipse addition.
Design: [typeset formula review](bpm-linearity-pair-increment-2026-11-03.pdf).
PR #227; this is a software candidate, not real-detector characterization.

## Behavior

Eclipse detector.c/detector.h now provide detector_gain_pair_checked.
It composes image_getstats_masked_checked and image_pair_stats_checked and
does not replace the established statistics, relative-response or linearity APIs.
Inputs are immutable active crops from four raw physical-ADU images, without
overscan correction. The caller establishes detector/readout identity and
supplies saturation/range/BPM selection. Coordinates are inclusive and one-based.

One common finite population is used for all four means and both differences.
Original ROI counts partition into BPM-excluded, nonfinite-excluded and valid;
BPM exclusion takes precedence. Child image statistics describe the derived
common map, so their exclusion counts do not replace the original partition.

The output contains the four image statistics, both difference statistics,
raw-bias RON, optional scaled RON-MAD, full difference variances, their
difference, bias-subtracted levels and pair conversion gain in electrons/ADU.
The fractional mismatch diagnostic is explicitly
2*abs(signal_first-signal_second)/(signal_first+signal_second), available only
when both bias-subtracted signals are positive. No mismatch cutoff is selected.

Fewer than two pixels or nonpositive gain numerator/denominator produce an
explicit unavailable state, not a nominal measured zero. RON remains available
when gain is unavailable if sufficient bias-pair samples exist. Invalid
arguments/selection/ROI/aliasing, allocation failure and arithmetic overflow
return error with caller output unchanged. The result owns no allocations.
No centering, rescaling, clipping, curve fitting, reference gain interval,
scientific threshold or persistent BPM classification is added.

## Preparation evidence

Agent Linux GCC C17 Release build: new gain_pair_probe and
gain_pair_allocation_probe plus normal mefpp link passed. The final two focused
CTest entries pass 2/2 in 0.11 s; this is NOT actual Mac or Chapman acceptance.

- Independent four-pixel formula example gives gain90 and RONsqrt(1/3).
- Common masks, nonfinite pixels, one-based ROIs and zero/one-sample states.
- Nonpositive denominator/signal, malformed options/maps/geometry, output alias
  and finite operands overflowing the stored difference.
- Pair swapping and median-centering invariance; curved synthetic sequences
  retain distinct pair gains and the full/half-variance factor of two.
- Existing mef_operation_run scaffold with explicit nonconsecutive pair indices,
  success/failure ordering and cleanup.
- Reuses the existing test-only Eclipse NULL-return seams and qfits resource
  accounting: all40 allocation positions fail singly and persistently, with
  unchanged inputs/output and no surviving tracked allocations.

Initial configuration omitted the existing opt-in adapter switch, so the target
was absent; corrected configuration enables MEFPP_BUILD_BIAS_ADAPTER=ON.
The initial two-pixel ROI test expected45 in error; independent arithmetic is
180/(8-2)=30. Production formula unchanged. Failed logs are retained; issue#228
tracks the corrected test oracle through actual Mac acceptance.
The actual Mac qualifier passes Python syntax inspection only.

## Actual Mac gate

Pycavi2/tests/qualify_gain_pair_mac.py runs under the normal installed imaging
Python, not private QC Python, with niceness>=10. It exports an exact fetched
Git revision to a fresh retained directory, preserving clean accepted main,
installed reduction module/configured engine/configuration and exported sources.
It uses the selected Apple Clang/SDK, CMake/CTest, ar/ranlib/make and two jobs.

Build only the two new probes plus normal mefpp; run only
native_gain_pair and native_gain_pair_allocation after checking their exact
CTest inventory. No unchanged historical matrix, original data, ASDF writing,
installation, production activation or checkout switch. Each build/test has a
retained log; qualification.json records commands and preservation even on failure.
Actual Mac execution remains pending owner-returned evidence.

This increment does not connect a new scientific CLI or serialize new products.
Sequence-level gain fitting, joint mosaic shutter/linearity, per-pixel residual
flagging, real OCAM/WFI work and later with/without correction photometry remain
subsequent scoped work. No merge or branch deletion is authorized.

