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

## Measurements and notation

The calculation uses **two flat-field exposures and two bias exposures** from
the same detector and readout configuration. A pair means two exposures at the
same integration time; they need not be consecutive in the acquisition sequence.

An ROI (region of interest) is the rectangular detector area being measured.
The **same accepted pixels** must be used for every mean and difference below.
A pixel is accepted only when selected by the BPM and finite in all four images.
The recipe also excludes samples outside the explicitly selected saturation and
signal limits. There is no automatic clipping.

| Symbol | Meaning | Unit |
|---|---|---|
| $p$ | Position of a pixel within the ROI | Pixel coordinate |
| $G$ | Set of accepted pixel positions, common to all four images | — |
| $N$ | Number of pixels in $G$; at least two are needed for a variance | Pixels |
| $F_{1,p}$, $F_{2,p}$ | Raw values at pixel $p$ in the first and second flat exposures | ADU |
| $B_{1,p}$, $B_{2,p}$ | Raw values at pixel $p$ in the first and second bias exposures | ADU |
| $z_p$ | Any image or difference value at pixel $p$ | ADU |
| $\bar z$ | Arithmetic mean of $z_p$ over $G$ | ADU |
| $v(z)$ | Sample variance of $z_p$ over $G$, with denominator $N-1$ | $\mathrm{ADU}^{2}$ |
| $\Delta F_p$ | Flat-pair difference, $F_{1,p}-F_{2,p}$ | ADU |
| $\Delta B_p$ | Bias-pair difference, $B_{1,p}-B_{2,p}$ | ADU |
| $g$ | Conversion gain: number of electrons corresponding to one ADU | $\mathrm{electrons}/\mathrm{ADU}$ |
| $\mathrm{RON}_{\mathrm{ADU}}$ | Readout noise of one exposure, expressed in ADU | ADU |
| $\operatorname{MAD}(z)$ | Median absolute deviation from the median of $z_p$, over $G$ | ADU |

The subscript in $\mathrm{RON}_{\mathrm{ADU}}$ is the complete unit label
“ADU”; it is not a product of variables. Bars above image names, such as
$\bar F_1$, mean averages over the common set $G$.

## Formulas to implement

### Mean and sample variance

For any image or difference $z$:

$$
\bar z = \frac{1}{N}\sum_{p\in G} z_p ,
\qquad
v(z) = \frac{1}{N-1}\sum_{p\in G}(z_p-\bar z)^2 .
$$

The variance measures the scatter after removing the arithmetic mean.
All means and variances below use this same definition and pixel population.

### Readout noise from the raw bias pair

Form the difference of the two raw biases:

$$
\Delta B_p = B_{1,p}-B_{2,p}.
$$

For independent exposures with equal readout-noise variance, the difference
contains twice the variance of one exposure. Therefore:

$$
\boxed{\mathrm{RON}_{\mathrm{ADU}}
       = \sqrt{\frac{v(\Delta B)}{2}} } .
$$

**No overscan correction is applied before this subtraction**, preserving the
previously agreed raw-pair measurement without scan-correction correlations.

The optional robust diagnostic is:

$$
\operatorname{MAD}(z)
 = \operatorname{median}_{p\in G}
   \left|z_p-\operatorname{median}_{q\in G}(z_q)\right| ,
$$

$$
\mathrm{RON}_{\mathrm{MAD}}
 = \frac{1.4826}{\sqrt{2}}\,\operatorname{MAD}(\Delta B).
$$

Here $q$ is just a second pixel index used to express the inner median.
The factor 1.4826 puts MAD on the standard-deviation scale for a Gaussian
distribution. The MAD estimate is reported separately; it does not replace
ordinary variance in the conversion-gain calculation.

### Conversion gain from flat and bias pairs

Form the raw flat-pair difference:

$$
\Delta F_p=F_{1,p}-F_{2,p}.
$$

The conversion gain is:

$$
\boxed{
g =
\frac{\bar F_1+\bar F_2-\bar B_1-\bar B_2}
     {v(\Delta F)-v(\Delta B)}
}
\quad [\mathrm{electrons}/\mathrm{ADU}] .
$$

The numerator is the sum of the two flat signals after removing the estimated
bias levels. The denominator removes the readout-noise contribution from the
flat-difference variance. The relation assumes photon shot noise, compatible
flat illumination patterns and operation within the accepted linear signal
range. Both numerator and denominator must be positive for a reported gain.

Use raw flat differences over the same accepted pixels, without scan correction,
for this first photon-transfer estimator. Bias removal in the numerator uses
the four image means. Changes in electronic structure between exposures remain
an admission concern; this routine does not model or correct arbitrary drift.

### Median centering and controlled lamps

Let $D_p=\Delta F_p$ and let $m$ be its median over $G$:

$$
m=\operatorname{median}_{p\in G}(D_p),
\qquad D'_p=D_p-m.
$$

Subtracting this one constant makes the median of the difference zero, but:

$$
v(D')=v(D),
\qquad
\operatorname{MAD}(D')=\operatorname{MAD}(D).
$$

Thus your proposed centering changes the displayed zero point, not the measured
variance or MAD. No extra centering estimator or input mutation is needed.
Retain the original difference median and the two bias-subtracted flat levels
as pair-consistency diagnostics. A multiplicative lamp change can leave a
spatial response pattern after median centering; no automatic rescaling is added.
The original uncentered levels remain available for the later linearity fit.

## Proposed Eclipse interface

This is the C entry point for the measurements defined above:

```c
int detector_gain_pair_checked(
    const image_t *flat_first, const image_t *flat_second,
    const image_t *bias_first, const image_t *bias_second,
    const pixelmap *selection, const int *zone,
    int with_mad, detector_gain_pair_result *out);
```

- The four image arguments supply the flat pair and the raw bias pair.
- `selection` is the optional common good-pixel map in Eclipse's
  existing convention: 1 means accepted, 0 means excluded.
- `zone` supplies the ROI boundaries, inclusive and counted from 1.
- `with_mad` requests the additional robust diagnostic.
- `out` receives the measurements, counts and availability/reason fields.

All four inputs have the same detector/readout, binning, dimensions and
raw-to-active mapping. The recipe uses the existing crop operation to provide
active-pixel images without scan subtraction. The selection is an explicit
binary Eclipse view, not the eight-bit reason array.

The result retains the four image-level statistics, both difference statistics,
the common valid/excluded counts, bias-subtracted pair signals, pair-mismatch
diagnostics, conversion gain and raw-pair RON.

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

## A small synthetic example for checking the arithmetic

“Four-pixel fixture” meant **four artificial images, each containing only four
pixels**. It did not mean four real OCAM exposures or a recommended measurement
area. The four pixel positions are the same in every artificial image. All
sixteen values below are invented for a simple software test.

| Pixel position $p$ | First flat $F_{1,p}$ | Second flat $F_{2,p}$ | First bias $B_{1,p}$ | Second bias $B_{2,p}$ |
|---|---:|---:|---:|---:|
| 1 | 101 | 99 | 11 | 10 |
| 2 | 99 | 101 | 9 | 10 |
| 3 | 100 | 100 | 10 | 10 |
| 4 | 100 | 100 | 10 | 10 |

All entries are in ADU. All four positions are accepted, so $N=4$.
The four image means are:

$$
\bar F_1=\bar F_2=100\ \mathrm{ADU},
\qquad
\bar B_1=\bar B_2=10\ \mathrm{ADU}.
$$

The pair differences, in pixel order, are:

$$
\Delta F=(2,-2,0,0)\ \mathrm{ADU},
\qquad
\Delta B=(1,-1,0,0)\ \mathrm{ADU}.
$$

Both difference means are zero. With the sample-variance denominator $N-1=3$:

$$
v(\Delta F)=\frac{2^2+(-2)^2+0^2+0^2}{3}
           =\frac{8}{3}\ \mathrm{ADU}^{2},
$$

$$
v(\Delta B)=\frac{1^2+(-1)^2+0^2+0^2}{3}
           =\frac{2}{3}\ \mathrm{ADU}^{2}.
$$

The expected software-test results are therefore:

$$
g=\frac{100+100-10-10}{8/3-2/3}
  =90\ \mathrm{electrons}/\mathrm{ADU},
$$

$$
\mathrm{RON}_{\mathrm{ADU}}
 =\sqrt{\frac{2/3}{2}}
 =\sqrt{\frac{1}{3}}\ \mathrm{ADU}
 \simeq0.57735\ \mathrm{ADU}.
$$

These deliberately simple numbers make errors in subtraction, the $N-1$
denominator or the factor of two easy to detect. **They are not expected OCAM
gain/noise values and do not validate the physical method on real observations.**

## Focused acceptance to prepare after interface review

Before execution, announce the inputs, functions, actions and pass criteria.

1. Recover the independently calculated results in the synthetic example above.
2. Verify that BPM exclusions and nonfinite samples select exactly the same
   population for all means and both variances. Check ROI coordinates and counts.
3. Swap the members of either pair: gain and RON must be unchanged, while
   the corresponding difference median changes sign. Verify separately that
   subtracting a constant leaves variance and MAD unchanged.
4. Check constant images, too few accepted pixels, nonpositive gain denominators
   and invalid maps. Report unavailable values or errors as appropriate; preserve
   caller output on error and never modify the inputs.
5. Exercise the new call through the existing operation template using synthetic
   pairs whose members are not consecutive. Check failure handling and cleanup.
6. Run focused Mac C17 checks first and validate the changed path on Chapman
   afterward. Do not repeat unchanged qualification matrices or alter production
   installations or original data.

## Connection to the full linearity design

The earlier [formula guide (PDF)](detector-characterization-design-2026-11-02.pdf)
and [LaTeX source](detector-characterization-design-2026-11-02.tex) remain the
controlling design. This increment implements only its paired gain/RON part.

The later shared shutter and linearity fit retains:

$$
Q_a(s)=s+c_{2,a}s^2+c_{3,a}s^3,
\qquad
Q_a(s_{rj})=L_r(t_j+\delta).
$$

| Symbol | Meaning | Unit |
|---|---|---|
| $a$ | Amplifier, or pixel in the later per-pixel mode | Identifier |
| $r$ | Analysis region | Identifier |
| $j$ | Exposure | Index |
| $s$ | Bias-subtracted measured signal | ADU |
| $s_{rj}$ | Signal for region $r$ and exposure $j$, subject to the guide's pixel-model/aggregation rule | ADU |
| $Q_a(s)$ | Linearized signal for model $a$ | ADU |
| $c_{2,a}$ | Quadratic coefficient of the inverse response | $\mathrm{ADU}^{-1}$ |
| $c_{3,a}$ | Cubic coefficient of the inverse response | $\mathrm{ADU}^{-2}$ |
| $L_r$ | Constant linearized illumination rate in region $r$ | ADU/s |
| $t_j$ | Exposure duration established from the declared input-time convention | s |
| $\delta$ | One signed duration offset shared by the mosaic; positive means longer exposure | s |

The effective duration is $t_j+\delta>0$. Keep the guide's monotonicity,
validated signal bounds, rank, conditioning, covariance and aggregation
requirements. No independent per-chip shutter offsets or unrestricted lamp-drift
parameters are introduced. The exact joint numerical interface is a later review.

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
