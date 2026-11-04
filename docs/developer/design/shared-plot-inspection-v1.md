# Shared plot inspection module, v1

4 November2026. Owner requests modular plotting components reusable across plots,
signal ticks every10000ADU through65535, and an x/y cursor. These are presentation
operations only. All scientific curves/fit settings remain separately computed
and saved in ASDF. Owner proposes15000..35000ADU for the next diagnostic reference
fit. Record/use that explicit interval in the next computation run, not in browser
code or by retroactively changing an existing result. Bonn shutter clarification
is accepted as the working instrument assumption; do not infer spatial timing
structure from the current plots.

One JSON signal-axis specification is shared by HTML and static plots. Apply it
to absolute signal ADU axes, horizontal or vertical, not residual ADU or rates.
Ticks0,10000,...60000,65535. Display extent includes the full16-bit scale while
retaining negative/out-of-range data if present; measured curves end at observed
points. The raw saturation exclusion65534ADU is unchanged. State this distinction.
Small mosaic tiles retain all tick marks but may thin numeric labels to avoid
collisions. Full detail plots show every count label.

A dependency-free generic JavaScript module supplies tick/range helpers, coordinate
inversion and cursor binding. Plot producers provide SVG viewport/plot margins,
axis bounds/labels/units and a readout destination. The cursor draws a crosshair
and reports continuous plot x/y coordinates; it does not interpolate a scientific
curve, choose a nearest measurement or refit. Exact stored point inspection remains
separate. Bind through the same module for mosaic and enlarged plots and support
pointer movement/exit. No remote assets. Exported PNGs retain static ticks; cursor
interaction is provided by HTML/SVG, not embedded into raster files.

Static Matplotlib axes use one shared Python helper reading the same JSON spec.
Do not duplicate tick values/limits in each plot implementation. Existing HTML
embeds the generic module and spec into a standalone document. Validate tick
sequence/endpoints, negative-data preservation, inverse-coordinate center/edges,
outside-axes handling, binding/readout, source-value preservation and existing
metric/ROI/point interactions. Record browser-rendering limits honestly.
