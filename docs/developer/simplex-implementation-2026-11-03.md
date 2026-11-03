# Checked Eclipse simplex increment - 3 November 2026

Owner authorized proceeding after the actual Mac QR gate at b382a93e passed:
native_matrix_qr and native_matrix_qr_allocation 2/2 in 1.69 s, retained at
`/Users/fselman/Software/build/wenu-imaging/mac-matrix-qr-Ay1wSJZe`.
Checkout, installed files and exported source were preserved; clean main remains
c73d9a9e. No unchanged QR or gain/RON tests are replayed in this increment.

## Implemented contract

`minimize_checked` extends the existing Eclipse optimization module using its
reflection/expansion/contraction/shrink scaffolding. Legacy `minimize` and
`min_test` are unchanged. The old helper cannot supply checked context callbacks,
validity states, bounds, exact budgets or error-atomic ownership; the extension
therefore implements those paths in the same module, not inside a recipe.
`optimization.h` includes the existing doubles header for its public legacy type.
PR #227 tracks the reviewed interface; #75 covers ownership/failure discipline.

The borrowed problem contains dimension, row-major (P+1) by P physical initial
simplex, positive parameter scales, finite lower/upper bounds, a context pointer
and checked cost callback. Every initial vertex must be feasible. The optimizer
searches in dimensionless coordinates but passes physical parameters to the
callback. Bound violations and nonfinite trial coordinates are rejected without
calling the model. There is no clipping. Callback INADMISSIBLE rejects a trial;
ERROR, unknown status, or VALID with a nonfinite/omitted cost aborts atomically.
A rejected shrink vertex leaves its old feasible vertex intact, allowing
nonconvex admissibility without publishing invalid simplex members.

Options explicitly select the maximum evaluation attempts, parameter-spread
limit, objective-spread limit and initial scaled edge-rank tolerance. Reuse
`matrix_leastsq_qr_checked` to check affine independence of the initial simplex;
there is no duplicate rank algorithm or hidden rank threshold. Fixed parameters
must be removed from the fitted parameter vector (lower < upper is required).

Parameter spread is the largest absolute coordinate separation from the best
vertex in dimensionless units. Objective spread is largest minus smallest cost,
divided by max(1, largest absolute vertex cost), computed by division before
subtraction to avoid overflow. Both criteria must pass. All attempted points,
including bound rejects and initial vertices, count toward max_evaluations;
actual callback calls and rejected/bound-rejected counts are recorded separately.
At least P+1 attempts are required in the options. No unlimited rejection loop.

Return 0 publishes an owned result with explicit CONVERGED or EVALUATION_LIMIT
status; callers must inspect status. The result owns best physical parameters,
final scaled simplex and valid costs, spreads, counts, and an exact bound-equality
flag. Reaching a bound or shrinking a simplex does not establish a scientifically
identified solution. Multiple starts, profiles, measurement coverage and joint
Jacobian diagnostics remain the detector wrapper's responsibility.

Invalid input, allocation, initial feasibility/rank, arithmetic or hard callback
failure returns -1 with the empty/occupied caller output unchanged. The dedicated
destructor frees all owned allocations through existing qfits memory accounting.
Borrowed inputs remain unchanged; the output owner is required to be separate
from them. Existing legacy optimizer behavior is preserved.

## Preparation verification and remaining work

Isolated GCC C17 Release build of the two new controls and normal mefpp passed.
Exactly native_simplex/native_simplex_allocation passed 2/2 in 0.14 s. Controls
use independent scaled quadratic and Rosenbrock minima, exact one-dimensional
reflection/expansion/inside/outside contraction expectations, constant-cost
shrink checks, nonconvex model rejection, finite bounds, exact budgets, degenerate
initial geometry, invalid scales/options, hard/nonfinite/unknown callback states,
immutable inputs, occupied output and a legacy known-minimum comparison.

All 19 allocation positions (optimizer and reused QR geometry) were exercised
with single and persistent NULL returns; qfits owners/resources and inputs were
preserved. A hard callback error after initialization also leaves no owned work.
No warning originated in the new optimizer source; legacy/dependency warnings
remain in the retained build log. The Mac runner's Python syntax is checked.
These are preparation results, not actual Mac optimizer acceptance.

`Pycavi2/tests/qualify_simplex_mac.py` reuses the qualified exact-source export,
checkout/install/source guards and retained receipt scaffolding. It builds only
the two focused controls and normal mefpp and selects exactly the two new tests.
Actual Mac optimizer qualification is pending. The joint signal evaluator,
covariance preparation, detector wrapper, common signed shutter fit and per-pixel
nonlinearity classification remain later work under the accepted design. No
observations, install, activation, merge, cleanup or scientific defaults here.
