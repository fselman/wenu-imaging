# Direct-pixel joint response candidate - 3 November 2026

The owner authorized proceeding after the actual Mac checked optimizer gate at
beee7c0d passed native_simplex/native_simplex_allocation 2/2 in 1.79 s. Evidence:
`/Users/fselman/Software/build/wenu-imaging/mac-simplex-ddM35GKJ`.
Checkout, installed files and exported source were preserved; main remains clean
at c73d9a9e. Earlier gain/RON and QR qualifications remain retained and unreplayed.

## Scope and scientific boundary

This first implementation of `detector_joint_response_fit_checked` composes the
reviewed Eclipse checked simplex and QR building blocks for DIRECT PIXEL samples.
It is a numerical fit candidate service, not the complete recipe or an accepted
linearity calibration. There is deliberately no accepted-calibration status.
Shutter profiles, instrument coverage acceptance, exact/validated ROI aggregation,
input measurement/covariance preparation and file/recipe publication remain later
increments. Do not pass ROI means as pixels or silently approximate them. No new
illumination-shape assumption or arbitrary per-frame lamp factor is introduced.

The accepted scientific model is unchanged: the amplifier inverse-response cubic
maps the measured signal to illumination rate times (input duration + delta).
The leading linear coefficient is one; there is no free additive bias intercept.
Delta is one signed duration offset shared by ALL detectors/amplifiers and every
accepted sample. Positive delta means increased effective duration. A separate
positive illumination rate is fitted for each identified physical pixel, held
constant across that pixel's exposures. Rates are not fitted independently per
exposure. Amplifier quadratic/cubic coefficients remain separate.

## Input and result contract

`detector_joint.h` is included by detector.h. The borrowed problem supplies:

- Amplifier identities (detector ID and amplifier ID) and full permitted signal
  intervals; each ID must be nonempty, NUL-terminated within 64 bytes, without
  truncation. Intervals are in bias-subtracted ADU.
- Physical sites, each mapped to one amplifier and active 1-based pixel x/y.
  Duplicate physical site definitions are rejected.
- Accepted observations with site index, original input-frame index, positive
  duration in an explicitly established seconds convention, and signal in ADU.
  The same input index must have the same duration across sites. Duplicate
  observations for the same pixel and input frame are rejected. Original input
  identity/order is retained; no consecutive-pair assumption or sorting.
- Fixed absolute measurement-covariance factor H, where C=H H-transpose: either
  positive diagonal (M by 1) or explicitly lower triangular (M by M), finite and
  with positive diagonal. Upper entries must be zero. No implicit diagonalization
  or jitter. Shared bias/reference correlations must be included or observations
  made independent by the caller; this service does not estimate covariance.
- Caller-declared scales, finite bounds and physical starting simplexes. Parameter
  order is delta; rate for each site; then quadratic/cubic coefficients for each
  amplifier. Positive rates and effective durations are checked on evaluation.

Admission is external: callers must establish common instrument/readout settings,
constrained bias, BPM-selected populations, finite/saturation/coverage cuts, time
convention and covariance provenance. This prototype performs no FITS selection
and silently rejects no admitted sample. An out-of-interval input is an error.
It sets no per-pixel BPM bits. Later per-pixel residual tests remain separate from
correctable amplifier response and from missing coverage.

The model checks the response derivative at both signal-interval endpoints and
its interior quadratic vertex, when present. It rejects a nonmonotonic interval
before bracketed bisection. Targets must remain inside the same branch; neither
clipping nor extrapolation is used. Inversion iteration and absolute ADU bracket
width limits are explicit. Numerical inversion failure aborts rather than posing
as a measured detector defect.

The objective is the squared length of H-inverse times observed-minus-predicted
residuals. Forward triangular solves preserve every supplied covariance term.
After declared starts converge and agree at caller-selected parameter/cost
limits, analytic residual derivatives are whitened and passed to checked pivoted
QR with the recorded parameter scales. Rank/conditioning checks are explicit.
Triangular solves form the local physical covariance, reversing column pivots
and scales; no normal equations or reduced-chi-square rescaling is used.
The QR linear correction is diagnostic and is not applied as an extra fit step.

Return 0 publishes CANDIDATE, UNCONVERGED, RANK_UNAVAILABLE,
CONDITION_UNAVAILABLE, COVERAGE_UNAVAILABLE or STARTS_INCONSISTENT. These are
numerical states only. The caller must not interpret CANDIDATE as scientific
acceptance. Unavailable covariance remains NULL; insufficient coverage has no
invented fitted parameters or residuals. An empty/occupied output owner remains
unchanged on invalid input, allocation or hard numerical failure (return -1).
`detector_joint_result_del` frees all nested owners.

The result retains copied site/amplifier/input identities, each start's optimizer
result and counts, physical bounds/scales, numerical options, exact supplied H,
unwhitened residuals and local QR/covariance when available. It remains inspectable
after borrowed input destruction. This dense reference implementation uses
O(MP + P squared) working storage plus supplied/retained covariance storage and
is qualified only on compact synthetic problems. It is not a full-mosaic pixel
throughput implementation; scalable ROI/measurement preparation remains open.

## Preparation checks and test correction

Agent GCC C17 Release preparation passed exactly native_detector_joint and
native_detector_joint_allocation, 2/2 in 0.62 s. Normal mefpp also builds. The
final new wrapper source is warning-free; dependency warnings remain retained.
The Mac qualifier's Python syntax was checked. Actual Mac joint-candidate
qualification is pending.

Twenty synthetic measurements span ten NON-monotonic durations at two physical
pixels in two detectors/amplifiers. An independent Newton generator creates data
with distinct amplifier cubics and shared offsets -0.15, 0 and +0.20 seconds.
Two declared starts recover the known parameters. Diagonal and full correlated
covariance cases use finite differences of the independent generator to verify
the analytic derivatives, whitening, pivot/scaling reversal and physical
covariance through an independent matrix identity. Further checks cover start
inconsistency, limited budgets, insufficient signal span, numerical conditioning,
rank, identical-time degeneracy, invalid covariance, duplicate pixel/frame inputs,
inconsistent frame durations, out-of-interval signals, inversion exhaustion and
an interior nonmonotonic derivative despite positive endpoints. Inputs and
occupied outputs remain unchanged. All 47 allocation positions were exercised
with single and persistent NULL returns; qfits resource identities were preserved.

Issue #229 records a test-fixture correction: the new identical-time rank test
initially used loose optimizer tolerances with two inconsistent starting costs,
so the correct earlier STARTS_INCONSISTENT status prevented reaching QR. The
rank-isolation fixture now declares one start; a separate two-start test retains
start-consistency coverage. Production numerical behavior was not changed for
that correction. Failed CTest and targeted rc=0/status=5 diagnostics are retained
beside the corrected passing logs. Keep #229 open until actual Mac acceptance.

The focused Mac runner exports exact fetched source, builds the two new controls
and normal mefpp, verifies exact CTest inventory and protects checkout/installed
files/exported source. No unchanged gain/QR/simplex replay, observations,
installation, activation, merge, cleanup or science-correction publication.
