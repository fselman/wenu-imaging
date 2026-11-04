# Shared plot axes and coordinate inspection

4 November2026. Owner requested this as a reusable component for all plots.
Final presentation design: [shared plot inspection v1](design/shared-plot-inspection-v1.md).

## Components

`config/plotting/signal-axis-v1.json` is the single signal-axis specification.
It defines0,10000,...60000,65535ADU ticks. `tools/qc-plot-inspection.js` exposes
configure, signalRange, signalTicks, coordinateAt and bind. SVG producers supply
viewport/margins/bounds/units via data-inspection. bind handles pointer movement,
screen-to-SVG inversion, crosshair display, unit-bearing readout and pointer exit.
All mosaic/enlarged metric views use the same module, with no independent copies.

`pycavi_plot_axes.py` applies that same JSON to static Matplotlib plots. Absolute
signal axes use the full display range, whether horizontal or vertical. Residual
ADU, percent, variance, gain, time and rate scales retain their own rules. Negative
or out-of-range samples extend the range rather than disappear. Small tiles retain
every tick mark and thin labels; detail plots show all signal labels. Static PNGs
have static ticks; cursor interaction is in HTML/SVG only.

A cursor reads continuous plotting coordinates. It does not interpolate a curve,
select a nearest measurement, estimate uncertainty or perform any scientific
computation. Clicking a point still exposes its exact stored data and source.
Extending the axis to65535 is not a claim of coverage or a new validity range.
The raw saturation exclusion remains65534ADU. Curves stop at measured points.

## Scientific boundary and next interval

Computations remain separate, saved in ASDF, then plotted read-only. The owner
proposes15000..35000ADU for the next reference-line fit. Use explicit computation
flags `--fit-signal-min 15000 --fit-signal-max 35000`; the result records those
limits and preserves outside-interval samples. Existing all-range products remain
unchanged. The Bonn-shutter clarification is accepted as the working instrument
assumption; no spatial shutter correction or physical shutter result is selected.

## Verification and pending Mac work

Agent viewer9/9 (11.330s), pair/plot9/9 (6.163s), shared-module checks and actual
viewer JS checks passed. Checks cover tick/endpoints, negative ranges, cursor
center/edges/outside bounds, screen-coordinate inversion, pointer handlers/units,
exit clearing, existing metric/ROI/source inspection and exact saved residuals.
The static signal/time PNG was visually checked. No browser painting is claimed:
Chromium is blocked by environment sockets. Expanded Playwright cursor tests are
available for a browser-enabled environment.

No result has been returned for the earlier6acd3b10 separation qualifier. The
new qualify_plot_inspection_mac.py covers the pending9 storage checks plus changed
9 static/ASDF plot checks and9 viewer checks, with3 runner checks. It reuses the
passed f2a15c7 common runtime/backend; no native or header matrix replay.
Actual Mac gate,32 real diagnostic ASDF products and independent new viewer remain
pending. Preserve interim ocam-residual-viewer-fes7vt_w (all5guards passed).
No new measurements, physical fit, installation, merge or cleanup.
