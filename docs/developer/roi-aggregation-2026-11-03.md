# Exact ROI operator and covariance propagation - 3 November 2026

`detector_roi_aggregate_checked` adds a reusable Eclipse ROI operator in
`src/iproc/detector_roi.c`. The inputs are already admitted direct pixel
measurements, identities, active dimensions, ROI rectangles and the supplied
absolute pixel-noise covariance factor. This is not a raw FITS extraction step,
a noise estimator or a new ROI illumination model. Existing joint/profile APIs
and their scientific candidate-only behavior remain intact.

## Recorded populations and identities

Each ROI has a unique ID, amplifier identity and inclusive FITS active-coordinate
rectangle. The caller supplies active width/height for every amplifier; invalid
bounds are refused, not clamped. Multiple ROIs per amplifier/detector may overlap.
Electronic scans are outside this active-pixel contract.

The existing joint measurement validator is extracted into one private shared
header, `src/iproc/detector_measurements_internal.h`, for reuse by the joint fitter
and ROI operator. It checks finite admitted signals, consistent frame durations,
unique physical sites, unique pixel/frame observations, identities and the exact
positive-diagonal/lower-triangular noise-factor contract. Source observations
are never duplicated to create a larger apparent input population.

Output rows preserve ROI order, then original frame first-appearance order. No
chronological sorting, consecutive-pair assumption or detector/HDU reordering
is introduced. Each row retains original input index, duration, member count,
mean and sparse membership references to the source observations. Empty ROI/frame
combinations stay present with count zero and unavailable (NaN) mean. They are
omitted from numerical matrices through an explicit active-to-presentation map.

The result separately records geometric ROI-overlap pairs, distinct observations
shared by multiple ROI rows, the distinct union of selected observations in
source order, and its distinct physical-site count. Geometric overlap does not
imply statistical duplication in every exposure: admitted populations may differ
because of upstream masks/saturation/coverage selection, and that difference is
retained rather than normalized away.

## Exact linear operator, not a mean-pixel approximation

For a fixed recorded population, the operator A gives every member weight
1/member_count. Means reuse Eclipse `double_avg` on private double-valued scratch
arrays, preserving input precision and avoiding a float image round trip. No
new clipping, median estimator, frame scaling or pixel rejection is selected.

Optional M-by-K pixel vectors can contain model predictions, Jacobian columns
or other explicitly identified quantities. Every column receives exactly the
same population and arithmetic weights as the observed mean. Pixel predictions
must be calculated BEFORE this projection. The operator does not authorize
applying a nonlinear response to an ROI mean as if it were one physical pixel.
ROI output uses its own type and cannot substitute for a detector_joint_site.

If the supplied source noise factor is H (absolute covariance C=H H-transpose),
the operator constructs B=A H and aggregate covariance B B-transpose. Thus
shared pixel measurements, shared master-bias errors and any other correlations
already present in H are carried through exactly for the fixed memberships.
Unknown noise is not estimated from spatial scatter or replaced with a unit
variance. Raw measurement/noise construction remains a separate pending stage.

No new Cholesky or competing factorizer is added. Qualified checked pivoted QR
of B-transpose supplies rank and a lower covariance factor in a recorded row
permutation. Signs are adjusted by column so the factor has positive diagonal,
without changing covariance. For more aggregate rows than source measurements,
QR of B supplies rank diagnostics only; a full-rank aggregate factor is impossible.
Duplicate/redundant ROIs can therefore return numerical rank unavailability.
No diagonal jitter, hidden regularization or assumption of independent ROI means
is used. The covariance itself remains inspectable even when its factor is
unavailable. Caller-selected rank/condition limits are explicit.

The lower factor's whitening row i corresponds to the presentation row:

```
active = factor_to_active[i]
presentation_row = active_to_row[active]
```

Observed means, predictions and Jacobian rows must all use that same permutation.
The reported covariance and projected vectors retain original active-row order.
The QR's zero right-hand side is only a computational factorization aid; its
solution is not a measured detector parameter.

## Independent synthetic checks

Four physical pixels are observed in two frames with deliberately unsorted input
indices. Three ROIs use pixels {1,2}, {2,3} and {4}. Each source pixel has variance
4 ADU squared; the correlated case adds covariance 1 between exposures of the
same pixel, representing a shared master-bias uncertainty.

| Quantity | Expected covariance, ADU squared |
|---|---:|
| Two-pixel ROI mean variance | 2 |
| Overlapping two-pixel ROI means, same exposure | 1 |
| Same two-pixel ROI mean, across exposures | 0.5 |
| Overlapping ROI means, across exposures | 0.25 |
| Single-pixel ROI variance | 4 |

These are fixture values, not instrument measurements or processing defaults.
The tests also demonstrate that averaging a nonlinear toy transform differs from
transforming the mean, reconstruct the covariance from the positive lower factor
using its actual pivot permutation, check projected vector columns, retain empty
rows, exercise partial per-exposure pixel exclusion and separate equal coordinates
on different detector/amplifier identities. Duplicate ROIs and more rows than
source samples produce singular covariance diagnostics. Invalid geometry, duplicate
inputs, invalid covariance, nonfinite vectors, occupied output and resource-limit
errors remain atomic.

Agent GCC C17 Release preparation passed 3/3 in 0.28 s: the two new ROI controls
plus the affected joint numerical control for the extracted shared validator.
All 41 allocation positions passed single and persistent NULL-return tests with
nested qfits owners/resources and inputs preserved. Singular and empty successful
results also release every owner. Normal mefpp builds; the final new sources/probes
have no new warnings. The Mac runner's Python syntax is checked. Actual Mac ROI
qualification subsequently passed at 4d0bb462: 3/3 in 3.01 s, retained at
`/Users/fselman/Software/build/wenu-imaging/mac-roi-aggregation-2SOrKVed`.
Checkout, installed files and exported source were all preserved; main stayed
clean c73d9a9e. These are software checks, not science acceptance.

## Ownership, resource scope and remaining integration

The result owns input identity/dimension/noise snapshots, ROI rows, membership and
union maps, projected vectors, latent/covariance factors and QR diagnostics.
`detector_roi_result_del` releases every nested allocation. Return 0 includes
READY, EMPTY, covariance-rank-unavailable and covariance-condition-unavailable;
READY describes the operator only, not science acceptance. Unavailable factors
remain NULL. Invalid input, allocation or nonfinite arithmetic returns -1 with
caller output unchanged. Inputs remain immutable. Dense per-matrix element limits
are explicit; this reference operator is not claimed as a full-mosaic throughput
implementation. Unavailable internal means must be omitted by future serialization,
not published as measured zero or NaN.

The focused Mac runner selects only the new ROI entries and the affected joint
control. No unrelated gain/QR/optimizer/profile gate replay, observations,
installation, activation, merge or cleanup. Next are raw sample extraction,
noise/covariance construction and integration of the recorded operator with a
validated pixel-level forward model. Do not silently feed these ROI means into
the current direct-pixel fitter.

The previous shutter-profile gate at 338180f6 passed actual Mac C17 2/2 in 6.09 s,
retained at
`/Users/fselman/Software/build/wenu-imaging/mac-shutter-profile-0mNWCIc5`.
Checkout, installed files and exported source were preserved; main stayed clean
at c73d9a9e. Earlier qualified components and #228/#229 closure remain unchanged.


Named per-detector/amplifier configuration is now implemented as a separate
[PAF/TOML supplement](roi-configuration-2026-11-03.md); its actual Mac gate
is pending. Raw extraction and forward-model integration remain separate.
