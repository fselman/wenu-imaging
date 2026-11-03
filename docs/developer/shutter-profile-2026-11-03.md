# Common shutter profile - 3 November 2026

`detector_joint_shutter_profile_checked` adds the conditional shutter-profile
step described in Section 5 of the reviewed joint shutter/linearity PDF. It
composes the Mac-qualified direct-pixel joint fitter and checked Eclipse simplex;
it does not introduce another optimizer or change the covariance/objective.
The existing candidate API retains its behavior. Profile diagnostics still do
not constitute an accepted detector calibration.

## Caller-controlled request

The profile service first obtains the free common-delay candidate with
`detector_joint_response_fit_checked`. If that candidate is unavailable because
of coverage, convergence, rank, conditioning or start consistency, the profile
returns BASE_UNAVAILABLE with the full owned base diagnostics.

The caller supplies a strictly increasing finite delay grid in seconds, wholly
inside the existing common-delay bounds. At least two grid points are required;
the free minimum acts as an additional inside anchor when needed. No grid is
selected, expanded or interpolated automatically. All detectors still contribute
to the same delay parameter, and all original observations retain the same fixed
absolute covariance factor.

For EACH grid point and EACH declared start, supply a physical nuisance simplex
with P rows by P-1 columns: the original parameter order with common delta removed.
Blocks are point-major then start-major. Illumination rates and all amplifier
quadratic/cubic coefficients are refitted while that grid delay stays fixed.
There is no independent detector delay, free bias intercept, per-frame lamp factor,
implicit previous-grid warm start or coefficient clipping.

The request explicitly selects optimizer budget and spread/rank tolerances, a
positive chi-square-rise threshold, an absolute cost-comparison tolerance and a
shutter-bound proximity tolerance in seconds. The service assigns no confidence
percentage to the threshold. Its statistical interpretation and absolute noise
model must be justified by the caller; sampling a profile does not establish
confidence coverage or a global minimum between unsearched grid points.

## Availability and retained results

Every declared initial vertex is checked with the same full joint objective.
An infeasible initial model makes its grid point INADMISSIBLE; it is not replaced
with an invented zero or infinite profile cost. Hard arithmetic or inversion
failures abort atomically. Invalid input/geometry or allocation failure likewise
returns -1 with the caller's empty/occupied output unchanged.

Each point requires all declared starts to converge and agree under the existing
parameter/cost consistency criteria. A valid free-fit nuisance vector, evaluated
at that fixed delay, supplies a further feasible upper cost bound. If a conditional
fit is worse than that known feasible point beyond the explicit absolute tolerance,
it is inconsistent. This diagnostic does not silently add a new optimizer start.

The result owns the free candidate/provenance, exact grid and initial nuisance
simplexes, each conditional optimizer result, best-start indices, valid costs,
cost rises, feasible reference costs and per-point statuses. It retains request
options and total base/profile optimizer attempt/callback counts. Extra model
preflight calls are recorded separately and do not consume optimizer budgets.
Unavailable scalar slots are internal NaNs with explicit statuses, never valid
measurements; a future serializer must omit unavailable numeric values rather
than publish zero or NaN as measured QC.

Overall states distinguish:

- BASE_UNAVAILABLE: the free joint fit did not reach candidate status.
- INCOMPLETE: a requested point lacks a valid, converged, consistent conditional fit.
- INCONSISTENT_MINIMUM: a conditional cost is below the free minimum beyond the
  declared tolerance; the free fit must be reconsidered.
- GRID_UNBRACKETED: the chosen rise is not crossed on both sides within the grid.
- BOUNDARY_LIMITED: the free shutter minimum is at/near its declared shutter bound,
  or a missing crossing reaches a physical shutter bound on the supplied grid.
- FLAT_ON_GRID: all sampled costs INCLUDING the free minimum differ by at most
  the absolute comparison tolerance, with no two-sided crossing. This says
  nothing about delays outside the grid. A boundary-limited state may also carry
  the flat_on_grid flag.
- DISCONNECTED: sampled points re-enter the threshold region beyond a crossing.
- BRACKETED: threshold crossings are bracketed on both sides on the declared
  grid under the requested bounds, starts and objective convention.

For BRACKETED, the result reports grid indices for the inside/outside points of
each crossing. An inside index -1 names the free minimum as the inside anchor.
No symmetric uncertainty, interpolated interval or accepted-calibration state is
manufactured. Conditional nuisance bounds and optimizer bound flags remain part
of the retained fits; BRACKETED does not certify an unconstrained/global nuisance
minimum or validate the instrument calibration. The existing full monotonicity,
positive-duration/rate, inversion and covariance checks remain active.

`detector_joint_profile_result_del` releases the base result and every nested
owner. Inputs stay immutable, and the result remains inspectable after borrowed
inputs are destroyed.

## Verification and practical starting-point limitation

Preparation on the agent's GCC C17 Release build passed exactly
native_shutter_profile and native_shutter_profile_allocation, 2/2 in 2.91 s.
Normal mefpp builds. The final new profile source and probes have no new warnings.
The focused Mac runner's Python syntax was checked; actual Mac profile gate is
pending. No unchanged named gain/QR/simplex/joint tests are replayed: the new
composition controls exercise the reused components through profile calls.

Independent Newton-generated two-detector data use different amplifier cubics and
common delays -0.15, 0 and +0.20 s. The profile refits all six nuisance parameters
with two declared starts. Tests recover the known minimum, cross the requested
rise on both sides and demonstrate lower conditional costs than keeping the free
nuisance values fixed. The inherited finite-difference covariance identity checks
the free-fit derivatives/covariance. Cases also cover weak-data flat profiles,
physical shutter bounds, too-short grid range for the requested rise, budget
exhaustion, unavailable base fit, inadmissible conditional initial models,
malformed grid/threshold, an inferior free minimum, immutable inputs and occupied
output owners. All 97 allocation positions were checked for single and persistent
NULL returns, preserving nested qfits owners/resources.

Retained development diagnostics demonstrate why multiple starts matter. A broad
conditional starting simplex converged near a cubic coefficient bound with a
worse cost than another start. The adapter correctly returned INCOMPLETE rather
than an interval. A second overly anisotropic free simplex under tight shutter
bounds correctly returned BASE_UNAVAILABLE through start inconsistency. The
bracketing fixtures use compact, explicitly supplied starts around their known
synthetic solution and a 0.001-second grid spacing; no consistency or production
convergence criterion was relaxed. These fixture values are not instrument
processing defaults. Broad-start/boundary diagnostics are retained with the
passing logs, and automatic robust starting-point preparation is not claimed.

## Actual-host state and next work

The previous direct-pixel candidate dc762519 passed the actual Mac C17 gate:
2/2 in 2.67 s at
`/Users/fselman/Software/build/wenu-imaging/mac-detector-joint-7iY8InK7`.
Checkout, installed files and exported source were preserved; main remained
clean at c73d9a9e. The test-only rank fixture issue #229 is accepted and closed.
Earlier gain/RON, QR and optimizer evidence remains retained and unchanged.

Next: actual Mac profile qualification, then validated ROI/pixel aggregation and
measurement/covariance preparation, followed by recipe/file publication and
changed-code Chapman qualification before full actual-data work there. Do not
pass broad ROI means as single pixels. No observations, installation, activation,
merge or cleanup accompany this increment.
