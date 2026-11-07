# Linearity uncertainties: agreed measurement policy — 3 November 2026

**Owner agreed to all three policy points on 3 November 2026.** The covariance assembler and FITS adapter are software
qualified on the Mac. A numerical factor is not a measured instrument noise model.
This note records the agreed measurement/propagation policy; no default noise
distribution, fit range, simulation count or scientific threshold is selected in
code by publishing it. No real frames have been processed by the new fitter.

## What the source establishes

The controlling November 2 design and November 3 numerical review require raw
bias-pair RON, ordinary variance for gain, explicit sample populations, one common
shutter offset, and covariance held fixed during each optimization. A
parameter-dependent variance model needs its own likelihood/weight-update review.

The actual bias kernel first rejects complete frames using their active means,
then calls cube_avg_median: the result is a median at each physical pixel.
It is not an arithmetic mean. Read-noise variance divided by accepted-frame count
therefore cannot simply be assigned as its variance. Uncertainty must correspond
to the estimator that actually produced the calibration. Source:
mefpp2/ins/mef/common/mef_bias_kernel.c and src/iproc/cube2image.c.

The applied row correction uses a trimmed average of electronic scan reads through
function1d_average_reject_checked. The dispersion of row corrections is not by
itself their measurement error: some variation may be the real bias drift the
correction is meant to remove. Sorting/rejection and the actual kept count matter.
Do not introduce a sum/count mismatch or a generic RON-squared/kept-count formula
as an unreviewed substitute for this estimator.

## Recommended first measurement pass

Use the existing paired gain/RON statistics and explicit FITS/BPM/ROI admission.
Keep each original pair, signal level, detector/amplifier, region, accepted pixel
count and exclusion decision. Produce a small numerical measurement table, without
a calibration fit, photometric correction or QC visualization project.

| Measurement | Data and method | Interpretation |
|---|---|---|
| Raw RON | Ordinary variance of a raw bias-pair difference, divided by two, then square root | ADU noise diagnostic; no overscan correction before differencing |
| Noise versus signal | Half the ordinary variance of each raw matched flat-pair difference, alongside its bias-referenced mean signal | Empirical total raw variance per signal level, ADU squared |
| Pair consistency | Separate means and spatial difference structure for both members | Lamp/offset/structure evidence; no forced matching or lamp factors |
| Electronic structure | Bias-pair and electronic-scan residual structure by physical row/amplifier | Tests the independent-pixel premise needed for component separation |

The same master cancels from a difference of two flats when the same physical
pixels and subtraction are used. Pair differences therefore cannot measure the
master's shared uncertainty. They also cannot, with only two frames at a level,
identify an arbitrary temporal distribution for each individual pixel. Pooling
across an ROI/amplifier is an explicit local-homogeneity assumption, not a measured
per-pixel noise map.

The ordinary sample variance already subtracts the difference image's mean in
its definition. That does not authorize changing either exposure, forcing its
median to zero for model fitting, or dividing it by a fitted lamp factor. A
lamp mismatch combined with spatial response structure can still inflate the
pair variance. Such a pair needs an explicit suitability decision.

Keep the measured variance-versus-signal curve. A signal-dependent pair gain is
a diagnostic, not permission to choose a different gain independently at every
pixel. A reference conversion gain can be estimated from the slope over a
reviewed photon-transfer interval. Neither one arbitrary point nor the entire
possibly nonlinear range is silently selected. Empirical raw variance is not
automatically the independent component of corrected-signal covariance.

## Agreed propagation after that pass

1. Establish a detector/amplifier noise model supported by the measurements.
   Record any pooling, distribution and spatial/row-correlation assumptions.
   Gaussian independent reads are a possible test model, not an automatic default.
   Preserve the reported raw RON; separate common modes before also adding them
   as independent covariance contributions, to avoid double counting.
2. Hold the reviewed frame membership, BPM selections, ROIs and fit-admitted
   populations fixed. Propagate the chosen model through the actual scan estimator
   and the actual median stack using reproducible Monte Carlo realizations.
   No replacement arithmetic-mean master or different scan rejection is introduced.
3. Treat each simulated master error as ONE shared calibration realization across
   all flats. Its uncertainty already includes the scans of the bias exposures;
   those scan errors must not be added a second time as flat scan noise.
   Flat scan errors describe the separate correction applied to each flat.
4. Form covariance factors with all modeled within-block correlations retained.
   The current three-block assembler requires independence between independent
   sample noise, master error and flat scan error. If the evidence/model has
   cross-block correlations, extend that contract or use an appropriate joint
   latent model; do not force the current independence assertion to succeed.
5. Freeze the resulting covariance for one joint fit. Report local/profile
   uncertainties as conditional on these estimated weights, accepted data and
   chosen noise model. Uncertainty in estimated noise parameters needs a separate
   outer propagation/sensitivity assessment; it is not included by the existing
   fixed-covariance Jacobian calculation or repaired by reduced-chi-squared scaling.

The Monte Carlo proposal propagates a specified model through the existing
operations; it does not make that input model empirically established. Simulation
count, generator/seed, convergence criterion, finite-sample behavior and resource
limits must be explicit and recorded before implementation. Failed realizations
cannot be silently discarded or redrawn until a preferred answer appears.

A whole-frame bootstrap of the accepted bias ensemble could be a sensitivity
check because it keeps pixels/rows together. With ten source biases it has
limited information; many resamples do not create additional independent bias
exposures. It is not selected as a validated replacement for the measurement
model. Likewise, a sample covariance of ten original noise vectors has rank at
most nine; a large unconstrained pixel covariance cannot be learned from that
ensemble alone. Any conditional choice to freeze acceptance excludes the
uncertainty of the acceptance/selection decision itself and must be labelled.

## Instrument epoch matters

ESO's OmegaCAM read-noise history records occasional RON increases in CCD_69 and
CCD_77 from October 2016. This predates our March 2017 sequence, making those
hardware identities relevant checks. It does NOT establish that these particular
frames are affected. Match hardware header identities, not HDU ordinals. Later
video-board replacements or detector failures must not be pooled into a 2017
noise reference without checking epoch/readout compatibility.

ESO documents the same ten paired exposure levels and v_STRM filter as the
selected sequence. That supports the sequence's intended monitoring role, not
acceptance of every pair or a constant-gain assumption over all levels.

## Review decision and implementation boundary

Owner-approved policy: **measurement first, empirical signal dependence retained,
then conditional model propagation through the real correction/median operations,
with fixed covariance during each fit and outer repeated fits to assess weight
uncertainty**. The owner first approved measurement and estimator propagation,
then approved the fixed-covariance point after clarification. A specific noise
distribution, pooling rule, simulation count/seed or threshold is still not chosen.
The [raw-pair measurement increment](linearity-pair-measurements-2026-11-03.md)
reuses qualified numerical resources; simulation support still requires its own
interface and known-answer review. No whole-mosaic dense fit, actual-data launch, new correction,
product publication, package installation, merge or cleanup follows from this note.

## Source references

- [Controlling formula design](detector-characterization-design-2026-11-02.tex).
- [Fixed-covariance numerical review](joint-shutter-linearity-interface-2026-11-03.tex), sections 2–3 and 5.
- [IRAF findgain](https://iraf.readthedocs.io/en/latest/tasks/noao/obsutil/findgain.html): paired raw-flat/bias method and its statistical assumptions. Wenu retains its own reviewed masks/no-implicit-clipping policy.
- [ESO OmegaCAM gain/linearity monitoring](https://www.eso.org/observing/dfo/quality/OMEGACAM/qc/gain_qc1.html): template levels/filter and gain monitoring. Its existing full-range pipeline description is not adopted as our fit-range decision.
- [ESO OmegaCAM read noise and history](https://www.eso.org/observing/dfo/quality/OMEGACAM/qc/readnoise_qc1.html): raw-pair RON and dated instrument events.
- [JCGM 101:2008, BIPM](https://www.bipm.org/en/doi/10.59161/jcgm101-2008): propagation of input probability distributions through a measurement model using Monte Carlo. This is methodological support, not detector-specific validation.
- [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html): resampling a statistic with common indices for paired arrays. This reference does not add a dependency or validate the proposed bias bootstrap.

Sources checked 3 November 2026. The statistical policy above is Wenu's agreed policy,
not a claim that ESO/IRAF/BIPM prescribe this particular Wenu implementation.

