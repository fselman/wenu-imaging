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
Chapman3 acceptance must regenerate fresh plots from the saved models/arrays,
without refitting or changing source files, and confirm the plotted grid agrees
with direct and serialized evaluation. Keep #39 open until that evidence is
recorded in a correction comment. #37/#38 remain separate unresolved notebook
issues; this patch does not claim clean end-to-end notebook execution.


Agent validation: three focused source regressions passed. A clean wheel in an
isolated installation passed those same three regressions against its packaged
notebook and ten installed-package/resource checks (13 total). Records:
`/tmp/wenu-direct-display-check-a04pgfhh`. Tests used Python 3.12, NumPy 1.26.4,
Astropy 6.1.7 and isolated SymPy 1.14.0/mpmath 1.3.0; no chapman environment
or dependency was changed. Notebook JSON/code syntax, local links and
`git diff --check` passed. Chapman3 target plotting remains pending.
