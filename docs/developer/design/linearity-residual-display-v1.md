# Approved diagnostic straight-line residual display, v1

4 November 2026. The owner reviewed the proposed ordinary unweighted,
free-intercept line per detector/ROI and instructed: "Proceed with this."
This final collection/display-level design precedes implementation. It authorizes
exploratory detrending of already saved data, not a physical shutter/response fit.

For every detector/ROI use both individual pair members. Default fit interval:
all available original mean signals. An explicit inclusive min/max ADU interval
can restrict the reference-line fit. Keep ALL original data displayed and retained,
including outside-interval points, with per-point fit membership. ROI visibility
must not change the fit of another ROI. No automatic outlier rejection or weights.

Fit S=a+b*t by centered ordinary least squares. Require two available observations
and at least two distinct exposure times; otherwise mark unavailable. Report
intercept ADU, slope ADU/s, number fitted, actual time/signal ranges and status.
A numerical overflow or invalid fit interval is unavailable, never zero/NaN.

Predict a+b*t for every available exposure of that ROI, including points outside
the fit interval. Residual ADU is S-prediction; percentage is 100*residual/prediction
only when prediction>0. Preserve original source identity, member, acquisition
index, common-pair population and original table row. Null signals remain null.
Add an S/t count-rate diagnostic for t>0; zero-time rates remain unavailable.

HTML adds residuals with x=original signal ADU (default) or exposure time, and
y=percentage (default) or ADU. Show a zero reference, all32 detectors, per-ROI
selection, exact point inspection and a fit summary. Also expose count rate versus
time so short-exposure structure can be inspected. Recompute only derived browser
values when fit limits change. An explicit JSON download saves the configuration,
per-ROI fits and derived rows with authoritative ASDF source references; it is
not an ASDF calibration and does not modify measurements. Label all as diagnostics.

A common constant shutter error is absorbed by the free intercept: a=A*delta,
b=A. Its fractional effect in S/t is delta/t. Straight-line residuals alone cannot
estimate it. Residual bias, lamp variations and curvature can also produce structure.
Do not infer a physical shutter result or adopt amplifier coefficients.

Implement the arithmetic in one dependency-free JavaScript module, embedded in
the standalone HTML by the existing generator. Validate against analytical lines,
known curved samples, restricted intervals with retained extrapolated points,
constant-time/rank failure, null/negative/zero data and input immutability.
Exercise actual viewer JS switching and inspection; reuse unchanged Python
measurement/ASDF tests rather than repeating them. Browser rendering remains a
separate actual-Mac visual check. No FITS reads/extraction, flat-field change,
ASDF rewrite, new statistical noise model, merge, install or cleanup.

After implementation maintain the mathematical/implementation guide as LaTeX
plus matching compiled PDF. This simple OLS formula needs no sophisticated solver.
