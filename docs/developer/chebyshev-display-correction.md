# Notebook 08a Chebyshev display (#39)

The 24 October chapman3 functional run exported and read back full degree-(5,5)
models correctly. Notebook 08a then sampled the model at stars and used a cubic
RBF to display a 50x50 grid. This second interpolation/extrapolation differs from
the saved correction, so its plot can conceal or change spatial structure.

The focused correction evaluates `chebyshev_2d_eval` directly on `grid_x, grid_y`
and transposes once for the plotting convention. The output label is `direct`
instead of `rbf`; historical files are not overwritten. Selection, fit weights,
degree, coefficient export, residual calculations and science pixels are unchanged.
This is a display-only correction, not a change to the correction model.

## Target evidence before correction

Records: `~/omegacam/testing/wenu-imaging-test/notebook08a-chebyshev-6jhubdcu`,
per-filter `output-check.json`, saved models and `fit-check-arrays.npz`.
The largest full-grid discrepancies were 0.34560477828999714 mag for r_SDSS
and 0.14580108007390305 for NB_659, at (1,1), outside the fitting-star hull.
Both coadd weight maps have zero weight at that corner. Weight-map hashes were
verified before a nearest-pixel sampling diagnostic at the existing grid points.

Both filters had 2108 positive-weight samples, 392 zero-weight samples,
2079 covered samples inside the star hull and 29 covered samples outside it.
For r_SDSS the inside/outside maximum display discrepancies were
0.011159357622271639 / 0.03813792104632245 mag; for NB_659 they were
0.006491932062335129 / 0.014195503929991062. Thus the misleading display affects
covered samples too. These are grid samples, not a full pixelwise coverage audit.
Direct-polynomial ranges in covered/inside samples were [-0.0050024807812135575,
0.11348423453958029] mag for r_SDSS and [-0.05618139986681717,
0.0748009229895501] for NB_659. Coverage does not prove model validity or justify
extrapolation. Scientific edge/uncertainty/independent validation remains separate.

## Acceptance

Regression checks execute the actual notebook display assignment against an
independent NumPy evaluation on a non-square grid/field with asymmetric and
highest-order terms, verify saved-model readback across the grid, and require
consistent direct output naming without a second interpolation call.
Chapman3 acceptance required fresh plots from saved models/arrays without
refitting or changing source files, and agreement of the plotted grid with direct
and serialized evaluation. That verification is complete below and #39 is closed
with a correction comment. #37/#38 remain separate unresolved notebook issues;
this patch does not claim clean end-to-end notebook execution.


Agent validation: three focused source regressions passed. A clean wheel in an
isolated installation passed those same three regressions against its packaged
notebook and ten installed-package/resource checks (13 total). Records:
`/tmp/wenu-direct-display-check-a04pgfhh`. Tests used Python 3.12, NumPy 1.26.4,
Astropy 6.1.7 and isolated SymPy 1.14.0/mpmath 1.3.0; no chapman environment
or dependency was changed. Notebook JSON/code syntax, local links and
`git diff --check` passed. Chapman3 target plotting subsequently passed; see the acceptance below.


## Chapman3 acceptance, 24 October 2026

Commit e233096fb3f42e6fdb73dd0bc64d6933defeef42 was installed and verified.
Records `~/wenu-chebyshev-display-qcxk2ph6` show three source regressions,
three installed display regressions, ten packaging/resource tests and pip check
passing. Wheel SHA256:
`1e0fa5cc5dc2fc74c16d34c2ab9cf5916f89a15e824bb00d09c162fbcdd095e2`.
Installed notebook SHA256:
`dc2497b313a1cca38efce1ff8a0d7a51020a11e0575f21517fa8bbfca90f719b`.

Fresh target plots were generated at `notebook08a-direct-ppzkqpm0` under the
pilot project, using the actual installed grid assignment and existing saved
coefficients. No model was refitted. `output-check.json` records both results;
PNG decoding and source model/array/check-record hashes passed. Each grid is
50x50 and explicitly includes full-field extrapolation in its plot title.

| Filter | Max difference vs serialized evaluation (mag) | Max difference vs independent NumPy (mag) |
| --- | --- | --- |
| r_SDSS | 1.5265566588595902e-16 | 1.6653345369377348e-16 |
| NB_659 | 1.0581813203458523e-16 | 8.326672684688674e-17 |

r_SDSS figure SHA256:
`ebb2ad767c01e8a9109d818e0f8fcb83ca0cd1a8f0b2059d2000e73f229fd56c`;
direct-grid SHA256:
`5f61c1d8e68381438e7aac3e59d18e84695a3178e5a457ef36efaf98a2cf6e5f`.
NB_659 figure SHA256:
`b7d89dd459607971ccc10d08d0d2f0ae7b1c303279db7775a8c16ba72a3703c7`;
direct-grid SHA256:
`1f34f5cec297d8b2b22f8540a0046db4f0e43dc1812d13864ea227fd8e6d1c80`.
Historical models/RBF plots remain unchanged. Fernando also viewed shared-scale
before/after and difference maps restricted to sampled positive-weight positions.
#39 was closed after the correction/evidence comment. This accepts the display
correction, not scientific extrapolation or full notebook control flow.
