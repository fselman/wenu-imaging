# Explicit detector covariance assembly — 3 November 2026

`detector_noise_assemble_checked` adds a reusable Eclipse numerical component for
combining **supplied** uncertainty contributions. It does not estimate gain,
read noise, master uncertainty or scan-estimator uncertainty from observations.
It does not fit a calibration or declare one scientifically acceptable.

The distinction matters: after subtracting one master bias from many exposures,
its error is shared. Likewise every pixel corrected with the same row scan value
shares that correction's error. Treating all corrected pixels as independent
would lose this information. The new component preserves the supplied structure.

## Explicit inputs and scope

Inputs are already fit-admitted physical-pixel samples with detector/amplifier,
active pixel, original frame index, integration time and signal identities. The
existing sample-identity validator is factored from the full measurement/noise
validator, without changing the established joint/ROI contracts. The new component
requires its input noise_factor to be NULL: an existing factor is never silently
ignored. Empty sample sets are not accepted here; the earlier admission service
retains those as an explicit empty result.

The caller supplies three blocks:

| Contribution | Supplied quantity | Units | Mapping |
|---|---|---|---|
| Independent sample noise | One nonnegative variance per observation | ADU squared | That observation only |
| Selected master-bias error | A factor with one row per physical site | ADU | Same site across all exposures |
| Applied row-scan error | A factor with one row per named correction group | ADU | Original frame index + amplifier index + active row |

For a supplied factor F, its covariance is F Fᵀ. Master factors can describe
correlations between different physical sites. Scan factors can describe
correlations between rows, amplifiers or exposures. Factors need not be square
or triangular. Every element must be finite, and all dimensions are checked.
They describe the error in the **actual applied correction**, not raw electronic
pixel scatter. In particular, no formula divides raw RON by the number of retained
scan pixels to invent uncertainty for the trimmed/order-statistic correction.

**This version requires the three blocks to be mutually independent**, explicitly
asserted through independent_components=1. Within-block correlations are preserved;
correlations between independent sample noise, the master and the scan are outside
this bounded model. For example, independence cannot be assumed if the master
uses the same bias observations being measured. Another model is required when
these blocks are correlated. The component cannot verify this scientific premise
from array values, and does not silently approximate an unsupported case.

A master factor is mandatory even if the caller has established a known-zero
master uncertainty; zero must be supplied explicitly. Applied scan correction
requires named groups and their factor, with every observation matching one
group exactly. Duplicate group identities are rejected. An explicit no-scan case
requires scan_applied=0, zero groups and NULL group/factor. Unused valid groups
are allowed, for example a full detector scan model with only a subset of rows
selected. There is no absent-means-zero fallback.

## Assembly and numerical factor

The independent block becomes a diagonal latent factor containing square roots
of the supplied variances. The master factor is repeated using physical site
identity; the scan factor is repeated using named correction identity. Both
correction coefficients are −1 because the corrections are subtracted.

The combined latent factor G yields covariance C = G Gᵀ. Equivalently:

```text
C = independent covariance + shared master covariance + shared scan covariance
```

This is exact for the supplied additive, mutually independent block model. No
Gaussian-noise claim, variance estimate, covariance shrinkage, jitter, implicit
regularization or gain selection follows from this algebra.

The existing checked column-pivoted QR routine operates on Gᵀ. Its recorded
permutation and upper triangular factor yield a lower covariance factor with
positive diagonal. No new Cholesky implementation or competing factorizer is
introduced. The QR zero right-hand side is a factorization aid, not a data fit.
Caller-selected rank tolerance and maximum factor condition are retained. The
condition diagnostic is the existing triangular 1-norm condition of R, not the
2-norm condition of the full covariance.

Covariance, source components and original observations remain in original order.
The lower factor instead uses QR order. On READY only, the result supplies:

- factor_to_observation: whitening-row index to original observation index;
- ordered_observation: matching original identities/signals in that order;
- noise_factor: the positive-diagonal lower factor in the same order;
- detector_noise_measurements: a borrowed view pairing those rows and factor.

Predictions and Jacobian rows must use that **same** order. Reordering the factor
alone is incorrect. No site, amplifier or frame identity is relabelled. ROI
aggregation can consume this paired view and retains its own frame-identity maps.

Numerical rank or conditioning unavailability is a successful diagnostic result,
with covariance and source records still inspectable but no invented factor or
usable measurement view. READY means a numerical factor is available for the
supplied model, not that the uncertainty model or calibration has been accepted.

## Ownership and resource limits

The result owns copies of amplifier/site/observation identities, independent
variances, master and scan factors/groups, group mapping, latent factor, original
covariance, QR diagnostics, permutation and ordered observations/factor when
available. detector_noise_result_del releases every nested owner. Inputs remain
unchanged; invalid input, allocation or nonfinite arithmetic returns −1 with
caller output unchanged. Output must start NULL. The borrowed measurement view
lasts only as long as its owner.

The dense reference implementation uses an explicit per-matrix element ceiling,
with checked size arithmetic before allocation. It is not a full-mosaic memory or
throughput solution. It does not discover files, estimate uncertainties, publish
ASDF/FITS, introduce a new calibration default, install code or merge a branch.
The sample-admission result remains truthfully noise-unavailable until the caller
provides a justified model through this separate interface. There is no automatic
upgrade of that result or hidden fit invocation.

## Independent checks and target gate

A synthetic two-site, two-exposure example supplies independent variance 4 per
observation, master variances 1 and 4, and scan variances 9 and 16 for two named
row corrections. Observations retain deliberately nonchronological indices 8 then
3. Expected covariance (ADU squared), in that original order:

| Observation | Frame 8, pixel 1 | Frame 8, pixel 2 | Frame 3, pixel 1 | Frame 3, pixel 2 |
|---|---:|---:|---:|---:|
| Frame 8, pixel 1 | 14 | 9 | 1 | 0 |
| Frame 8, pixel 2 | 9 | 17 | 0 | 4 |
| Frame 3, pixel 1 | 1 | 0 | 21 | 16 |
| Frame 3, pixel 2 | 0 | 4 | 16 | 24 |

The first QR pivot is original observation 3, so the fixture actually exercises
a nonidentity order. Reconstructing the full covariance from the lower factor
and permutation checks both orientation and signs. An integration control feeds
the paired view into the exact ROI operator: the two-pixel mean variances are
12.25 and 19.25, their cross-exposure covariance is 1.25, and frame-8 covariance
between that mean and pixel 1 is 11.5. These are fixture answers, not OCAM values.

Other controls retain nonzero cross-site master and cross-exposure scan
covariance, explicit no-scan behavior, singular and condition-unavailable results,
missing/invalid components, invalid frame/group identities, resource limits,
nonfinite arithmetic, occupied outputs and owner lifetime. All 33 allocation
positions pass single and persistent NULL-return checks with qfits owner/resource
accounting and input preservation. Unavailable successful results also release
all nested storage.

Agent GCC C17 Release preparation: 4/4 in 0.36 s (two new noise controls plus
existing ROI and joint numerical controls for the factored shared validator).
Normal mefpp builds. New noise source/probe have no new warnings; unchanged qfits
allocator warnings remain in its test scaffold. The Mac qualifier's syntax is
checked. Actual Mac covariance qualification subsequently passed at c381168b,
4/4 in 3.69 s, retained mac-detector-noise-z4pHBH0H with checkout/install/export
preserved and clean main c73d9a9e. The qualifier builds only these four probes and
normal mefpp, exports exact source and checks checkout/install/export preservation.

Previous sample-admission source 88e29306d1ee1f1ec9b7b98522170709d10faa55 passed
actual Mac 1/1: 1.04 s test, 1.05 s total, retained
`/Users/fselman/Software/build/wenu-imaging/mac-linearity-samples-fRlf0Hgk`.
All three preservation checks passed; checkout remained clean main c73d9a9e.
This is the owner's returned terminal receipt, not an independent read of the Mac.

Next are justified uncertainty estimation/selection and raw FITS/metadata binding,
then forward-model/recipe integration. Actual OCAM processing and scientific
validation remain pending. No new observation, QC visualization, installation,
activation or merge is part of this increment.

[Explicit FITS admission](linearity-files-2026-11-03.md) now binds supplied
files to the sample service; its Mac gate is pending. No uncertainty estimates
or actual observations have been added.
