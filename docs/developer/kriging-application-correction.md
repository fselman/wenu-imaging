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

## Chapman3 acceptance, 24 October 2026

Installed commit `298d2867c21fa2734874e1562ff28696147f7d06` passed five source
and five installed application regressions, five source and five installed null-
writer regressions, ten package/resource checks, pip check, installed-byte
comparisons and normal production import. Records:
`~/wenu-kriging-application-ovjpq15v`; wheel SHA256
`c7dbccd5c28390575bfe881aaad5f3660127fbb6b37427cbf8e24006a8a1a467`.

Both immutable existing 50x50 models passed actual-catalogue coordinate bounds
and direct cubic evaluation, then application on a fresh baseline copy in
`~/omegacam/testing/wenu-imaging-test/notebook09-kriging-s0e1demx`.
Output `CN_Ori_merged_catalogue_krigging.fits` SHA256:
`6243227b5bd2c3a0284cf241e63143eaef7ad9f53f3d64ee0b6a056df90d03bf`.

| Check | r_SDSS | NB_659 |
|---|---|---|
| Correction range, mag | -0.32640609129568454..0.05940208323192967 | -0.1155740390260677..0.2952581212052823 |
| Maximum node error, mag | 1.1744235992030769e-6 | 1.0308744892887712e-6 |
| Node residual L2 | 3.2364028544213193e-6 | 5.044140983330427e-6 |
| Inherited solver bound L2 | 5.159906969485474e-6 | 7.4717868173828954e-6 |

All 16459 rows, 3718 exact int64 IDs and 12741 null masks survive. The four
selected magnitude fields per filter match direct cubic predictions at native
stored precision. Unrelated column bytes/masks, full extension metadata, model
basename/digest provenance and repeat-call byte identity pass. Baseline,
Chebyshev output and saved grids remain unchanged. No extraction, new query,
image correction or refit occurred. `started.json`/`output-check.json` retain
inputs/checks; `cubic-check-arrays.npz` SHA256 is
`33581508091aaf6c1545d6aa8990d2c4c46acbeae0711025784b5e948e29c98d`.

#48 closed after its correction/evidence comment. PR #52 remains unmerged,
stacked on #50/#47/#45/#43. The existing catalogue QC plots subsequently passed (below). Functional agreement with cubic saved-grid evaluation does
not accept the model scientifically or prove equivalence to the continuous
Kriging predictor; independent accuracy/flux-error questions remain separate.

## Actual catalogue QC passed

`~/omegacam/testing/wenu-imaging-test/notebook09-kriging-qc-saittxaz` contains a
fresh staged Kriging catalogue and all four expected `create_catalogue_checkplots`
PNGs. Each image was verified and decoded; source and staged catalogue hashes
remain `6243227b5bd2c3a0284cf241e63143eaef7ad9f53f3d64ee0b6a056df90d03bf`.
Parameters retain the existing `mag_petro_r_sdss` versus `r_SDSS_gaia` comparison,
reference magnitude 13..17. `started.json` and `output-check.json` retain call,
paths, image dimensions/hashes and source digest. No new query, extraction, refit
or further correction occurred.

Together with the eight unchanged-input baseline/Chebyshev QC PNGs in
`notebook09-qc-h6o98cy8`, this accepts selected functional plot generation for
all three catalogues. Images were decoded, not scientifically/visually graded.
Complete notebook discovery/selection, live SkyMapper comparison, Mac execution,
independent accuracy and Phase 3 validation are not established. #51 remains
deferred for missing-column inputs; current requested columns were present.
