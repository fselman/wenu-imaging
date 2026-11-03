# BPM/linearity development: paired conversion gain increment

Date: 3 November 2026. Status: exact numerical interface proposed for owner review.
Base: c73d9a9e3a631fbbb2346beaa3c150c110a60343.
This advances the accepted 2 November formula design; no new numerical source
is implemented by this review. Existing qualified bias/BPM execution remains available.

## Current owner decisions

- Continue BPM/linearity recipe development. QC investigation and visualization
  remain deferred.
- The eventual linearity correction is applied in mefpp. Later validation reduces
  the SAME science frames with and without that correction and compares them in
  the photometric calibration notebook. That experiment is not this increment.
- Use the selected Mac OmegaCAM sequence below. Nonconsecutive members are paired
  explicitly; chronological order and acquisition times remain unchanged.
- Controlled lamps support testing small pair mismatches; do not infer perfectly
  constant illumination or introduce unrestricted per-exposure lamp parameters.
- Keep the unsigned 8-bit reason BPM, independent coverage, reusable Eclipse
  numerical services, and the completed bias recipe orchestration template.

## Source reuse review

Reviewed main's Eclipse sources and the existing BPM service:

| Existing resource | Actual role | Reuse decision |
|---|---|---|
| src/iproc/image_stats.c: image_getstats_masked_checked | Finite, BPM-selected ROI mean, median, sample standard deviation and optional MAD | Reuse for four-frame means and counts |
| src/iproc/image_stats.c: image_pair_stats_checked | Pair difference, intersected maps, checked regional statistics | Reuse for flat and RAW-bias differences |
| src/iproc/detector.c: cube_create_gainmap_robust / proportional | Relative pixel response against measured frame level | Retain for response BPM; not conversion gain in electrons/ADU |
| src/iproc/detector.c: detector_linearity_fit | Per-pixel time polynomial in signal, no constant term; diagnostic is mean squared time residual | Preserve legacy API; insufficient for the shared signed shutter model |
| src/iproc/detector.c: cube_correct_detlin | In-place cubic using b/a and c/a | Potential later correction primitive; explicit coefficient conversion and validity checks required |
| src/math/fit_curve.c and matrix.c | Polynomial/linear fits and normal-equation least squares | Retain scaffolding; no joint constrained covariance fit is supplied |

The current BPM service already handles active ROIs and explicit sample maps.
File admission already carries pair identifiers. No replacement FITS reader,
statistics implementation, BPM response fitter or acquisition-order sorting is needed.

## First proposed new Eclipse routine

Proposed public interface in the detector module:

```c
int detector_gain_pair_checked(
    const image_t *flat_first, const image_t *flat_second,
    const image_t *bias_first, const image_t *bias_second,
    const pixelmap *selection, const int *zone,
    int with_mad, detector_gain_pair_result *out);
```

The corresponding result contains the four masked level statistics, flat and
bias difference statistics, the common valid/excluded counts, bias-subtracted
pair signals, fractional pair mismatch, difference median, conversion gain and
RAW-pair RON, with explicit availability/reason fields.

All four inputs are raw physical ADU planes with the same detector/readout,
binning, dimensions and raw-to-active mapping. The ROI is a one-based inclusive
active-pixel rectangle; pass active crops without applying scan correction.
The recipe composes the existing crop operation. The optional selection is an
explicit Eclipse 1=good view, not the eight-bit reason array. The routine
intersects that population with finite samples in ALL four planes before any
statistics. Saturation and permitted fit-range admission belong to the caller's
explicit sample selection; no silent clipping or automatic thresholds.

For that identical population G, use the accepted formulas:

```math
v(z) = sum_G (z - mean_G(z))^2 / (N_G - 1)
RON_ADU = sqrt(v(B1-B2)/2)
g = (mean(F1)+mean(F2)-mean(B1)-mean(B2))
    / (v(F1-F2)-v(B1-B2))
```

Units: means, medians and RON in ADU; variances in ADU squared; g in
electrons/ADU. Optional RON-MAD is 1.4826*MAD(B1-B2)/sqrt(2), a separate
diagnostic. Gain always uses ordinary sample variance.

No overscan subtraction is applied to RAW bias differences. Using raw flat
differences on the same population also avoids introducing scan-estimation
covariance into this first photon-transfer estimator. Pair-level bias-corrected
signals are derived from the four means, not silently from scan-corrected flats.
Spatially varying electronic changes remain a limitation/admission concern;
this is not an arbitrary electronic drift correction.

### Median centering and controlled lamps

For D=F1-F2 and m=median(D), v(D-m)=v(D) and MAD(D-m)=MAD(D).
Therefore zero-median centering needs no new estimator or mutation of input
pixels. Retain m, the two bias-subtracted signal levels and their fractional
mismatch for pair admission. A multiplicative illumination change can leave a
response-pattern residual even after centering; no automatic rescaling is added.
The original uncentered levels remain the inputs for later linearity fitting.

### Errors, ownership and callers

Inputs/maps/ROI are borrowed and immutable; output is caller-owned and has no
owned image allocations. Temporary images/maps use existing Eclipse allocation,
cleanup and error conventions. Invalid dimensions/maps/ROI, invalid options,
allocation failure or nonfinite arithmetic return an error without changing
*out. Fewer than two common samples or nonpositive gain numerator/denominator
produce an explicit unavailable measurement, never a nominal zero gain.
RON can remain available when gain is unavailable. Reject aliasing/invalid output
arguments as specified in the matching header documentation.

The numerical routine reports measurements, not scientific acceptance.
The recipe applies explicit illumination-mismatch/range thresholds and records
the decision. It calls the helper once per configured amplifier/ROI/pair and
records detector identity, sample population, raw origin and estimator.
Overlapping ROI estimates share pixels and are not independent observations.

No new global model fitter, default mismatch tolerance, defect criterion or
uncertainty approximation is approved by this interface review.

## Focused acceptance to prepare after interface review

Before execution, announce the inputs, functions, actions and pass criteria.

1. A four-pixel exact fixture: F1=[101,99,100,100],
   F2=[99,101,100,100], B1=[11,9,10,10], B2=[10,10,10,10].
   Expected flat variance 8/3, bias variance 2/3, g=90 electrons/ADU,
   RON=sqrt(1/3) ADU; compare against independent arithmetic.
2. BPM exclusions and nonfinite samples must use exactly the same common
   population for all means and both variances. Check ROI coordinates and counts.
3. Pair order swaps preserve gain/RON and reverse difference median.
   Additive difference centering preserves variance and MAD.
4. Constant/one-sample/negative-denominator/invalid-map cases report truthful
   unavailability/errors, preserve caller output on error and never mutate inputs.
5. Exercise the new call through the existing operation template on synthetic
   nonconsecutive pairs. Check failures and cleanup at affected allocations.
6. Mac C17 first; changed path on Chapman afterward. No unchanged qualification
   matrix, production installation or original-data mutation.

Full shared shutter/linearity fitting follows as a separate reviewed numerical
interface, with the accepted Q(s)=s+c2*s^2+c3*s^3,
Q(s)=L_r*(t+delta), one mosaic delta, monotonicity, measured bounds, rank,
conditioning and covariance requirements. It must not silently reduce these to
an unconstrained polynomial or independent per-chip shutter offsets.

## Selected Mac OmegaCAM inputs

Root: /Users/fselman/Pictures/OCAM/bpm.
Owner-provided listing; files/pixels have NOT yet been independently inspected
on the Mac. Ten BIAS/r_SDSS exposures precede twenty
FLAT,DOME,DETGAIN/v_STRM exposures on 2017-03-13. Different bias/flat filters
are recorded; detector/readout compatibility still needs header confirmation.

Bias file timestamps (OMEGA.2017-03-13T<timestamp>.fits):
09:50:05.624, 09:50:48.373, 09:51:31.403, 09:52:14.404, 09:52:57.394,
09:53:40.384, 09:54:23.384, 09:55:06.394, 09:55:49.384, 09:56:31.804.

| Pair | Time (s) | First flat timestamp | Second flat timestamp | Chronological flat indices |
|---|---:|---|---|---|
| P02 | 2 | 11:34:43.759 | 11:58:45.683 | 1,20 |
| P70 | 70 | 11:35:30.570 | 11:56:50.383 | 2,19 |
| P40 | 40 | 11:37:25.420 | 11:55:25.563 | 3,18 |
| P05 | 5 | 11:38:50.390 | 11:54:35.393 | 4,17 |
| P10 | 10 | 11:39:40.380 | 11:53:40.483 | 5,16 |
| P30 | 30 | 11:40:35.390 | 11:52:25.393 | 6,15 |
| P20 | 20 | 11:41:50.391 | 11:51:20.392 | 7,14 |
| P50 | 50 | 11:42:55.391 | 11:49:45.392 | 8,13 |
| P60 | 60 | 11:44:30.391 | 11:48:00.392 | 9,12 |
| P07 | 7 | 11:46:16.391 | 11:47:08.392 | 10,11 |

This sequence has ten levels, not the design's representative 22-pair annual
sequence. Do not reject it solely on that count or promise all products:
admit each requested model using its actual rank, usable signal span, saturation
and illumination evidence. Preserve header times; do not assume they are
commanded times or already shutter-corrected.
