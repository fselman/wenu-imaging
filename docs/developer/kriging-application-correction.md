# Kriging catalogue application coordinates

24 October 2026, [#48](https://github.com/fselman/wenu-imaging/issues/48).
The catalogue application is separate from the linear saved-grid reader fixed
in #41. Its old cubic interpolator used sample axes `arange(N)/N` with catalogue
positions divided by original image dimensions, so the last stored sample was
below 1 while valid upper-edge catalogue positions mapped to 1. Actual-function
synthetic FITS execution rejected a valid upper-right pixel before updating any
catalogue. Rectangular grids also exposed reversed axis lengths/orientation.

Use the stored model's physical sample endpoints: x = linspace(1, ORIG_W, m),
y = linspace(1, ORIG_H, n) for an n-row/m-column grid; interpolate with axes (y,x)
and raw physical catalogue coordinates. These axes match notebook 08b's grid
construction and the corrected reader's coordinate convention. Retain **cubic**
interpolation, its default solver/tolerances and strict bounds. Do not substitute
the reader's linear method, extrapolate, refit or change model parameters. The
correction sign, selected magnitude columns, null-safe field writer and model
provenance/repeat guards stay unchanged.

Five new regressions execute actual application/helper bodies with real temporary
FITS, tables and SciPy cubic interpolation (no prediction mocks). They cover
non-square fields and rectangular grids, all four physical corners and affine
interior values, nonlinear sample nodes, legacy square grids, outside-extent
rejection without catalogue modification, both float32/64 magnitude fields,
exact int64 IDs/null masks, unchanged unrelated columns/extension headers/model
bytes, repeat no-op and changed-model rejection. Affine predictions agree to
1e-12 mag. Nonlinear node checks respect the existing cubic iterative solver's
L2 residual criterion; an initial too-tight pointwise threshold was investigated,
not met by changing the production solver. In the synthetic agent example the
maximum node error is 5.4606e-6 mag, residual norm 1.2092e-5 versus the default
relative convergence bound 1.3518e-5. This differs from bit-exact linear-node
readback and is not an independent scientific accuracy measurement.

The five application regressions and five existing null-writer regressions pass
from source and an isolated installed wheel; ten package/resource checks pass.
Agent records: `/tmp/wenu-kriging-application-check-pi3cae62` (including final-wheel
logs). Unrelated fitting imports are excluded by actual-function-body isolation;
normal production import, full target environment and actual saved-model
application still require chapman3 verification. No dependencies were upgraded.

Keep #48 open pending target installed checks, exact model/grid and catalogue
coordinate preflight, then application on a fresh baseline copy and verification
against direct cubic evaluation. Preserve baseline, Chebyshev copy, images and
saved grids; check all masks/unrelated columns/metadata, model digests and repeat
byte identity. A successful functional application does not accept the fitted
surface, coarse-grid fidelity, photometry, astrometry or flux/error consistency.
No observational Kriging correction has launched.
