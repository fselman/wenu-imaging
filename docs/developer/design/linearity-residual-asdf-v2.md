## Corrected preparation source extension — 5 November 2026

The reviewed formulas, unweighted free-intercept policy and explicit
15000..35000ADU next-run interval are unchanged. The completed corrected
preparation ASDF is now an additional source. A shared lossless reader projects
its stored per-exposure ROI signals, variance, pair member/asset/HDU/index and
common populations. It does not recompute a mean or load an image/native table.
New diagnostics freeze the complete preparation source graph and retain
source_kind=preparation, measurement_stage=scan_corrected_master_bias_subtracted
and a generic source_measurement_digest. The source_pair_digest field remains a
compatibility alias to that same source record, not a claim of raw-pair stage.
Readers verify kind and stage against the actual source. Existing raw-pair
archives/readers remain supported and immutable. Plotting uses saved curves.

# Residual computation and display separation, v2

4 November 2026. Owner instruction: keep computations separate from plotting;
store the diagnostic curves in ASDF. This supersedes browser-side fitting in v1.
The approved unweighted, free-intercept model and null/interval rules are unchanged.
This final design precedes the implementation change; no new physical model is
selected. The existing browser implementation is an interim historical version.

Compute centered OLS once from saved original per-exposure ROI means and times,
using Python math.fsum for sums. Save each detector's settings, five ROI fit
summaries, all predictions/residuals in ADU and percent, rates, eligibility flags,
original samples and physical/source identities. Outside-fit-range points stay.
Use the existing common QcRecipe/writer/reader, with a named owned extension and
units. Emit a genuine full-precision derived TSV plus its ASDF sidecar, retaining
local frozen copies of the original pair QC graph (not FITS images). No schema
or common-writer change. Never edit existing measurement or diagnostic archives.

A separate compute command accepts original pair ASDF or the completed32-detector
batch, fit limits and a new empty destination. One ASDF per detector, plus a
completion index with record digests/input fingerprints. Exact round-trip and
source-preservation checks are required. Failed runs remain incomplete, not resumed
or overwritten. A different fit interval requires a new computation/output run.

The independent HTML generator reads original measurements and these completed
ASDF diagnostics, validates identities/configurations/source digests, and embeds
saved curves. It contains no regression, prediction, residual or rate computation.
Detector/ROI, axes and display-unit controls remain interactive. Fit limits and
summaries are read-only saved values. JSON download exports saved results only.
Without saved diagnostics the original variance/gain/signal-time views remain
available, but residual/rate views explicitly say no saved diagnostic supplied.

Test independent analytical solutions and edge cases for the Python service;
verify ASDF round-trip, relocation/frozen graph, source/identity tamper rejection,
conflicts and identical saved rows consumed by HTML. Prove HTML uses deliberately
supplied stored residuals and cannot refit on axis changes. No raw images, noise
model, physical shutter result, amplifier correction, merge or installation.
Update the mathematical guide as paired LaTeX/compiled PDF after implementation.
