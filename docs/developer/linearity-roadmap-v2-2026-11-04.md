# Revised linearity roadmap v2 — collect first, fit afterward

**Superseded by [roadmap v3](linearity-roadmap-v3-2026-11-04.md).** The owner
clarified that existing ROI pair measurements supply most of the recipe; the
immediate extension is signal versus exposure time and complete data display
before modelling. The broad collection redesign below is historical, not current.

4 November 2026. Revised in response to the owner's instruction: extract mean
signals and variances from all exposures, order the measurements by detector,
save them in ASDF, and explore models/parameters afterward. This is a roadmap
revision, not an implemented collection recipe or an adopted statistical model.
It supersedes the narrow next-step scope in the unaccepted Stage8 v1 noise-evidence
design. That file stays as review history; its valid estimator/provenance findings
carry forward into one revised complete collection contract before code.

## 1. Overall sequence

**Collect measurements once → save the complete measurement dataset in ASDF →
explore models/parameters repeatedly → validate/publish calibration → visualize
independently.** Model experiments do not invoke the collection recipe. Noise
model selection is analysis of the saved measurements, not a prerequisite for
collecting mean signals, variances and estimator evidence.

## 2. Collection scope and ordering

For this project, all exposures means the20 flats and10 biases in the admitted
sequence. Cover all32 detectors and the five existing full ROIs per detector;
keep windows separate. The160 individual sites already archived complement these
ROI summaries; they are not the sole population of the revised collection pass.

Expose a deterministic detector-first view: physical detector ID65..96, then
original acquisition index, then stable ROI ID. Preserve native slot, actual HDU,
original frame/pair ID and timestamp as explicit fields; none follows from row
position. Exposure duration is a separate sortable analysis coordinate, not a
reason to overwrite the acquisition order. All10 biases remain represented,
including a bias rejected by its detector's master. Keep that recorded membership.

The principal exposure/ROI table has32×30×5 = **4800 records**, each containing
explicit processing-stage statistics. These4800 region records are distinct from
the4800 individual-site/bias/flat records proposed in the earlier narrow design.

## 3. One complete measurement dataset

| Saved component | Contents and stage |
|---|---|
|Exposure and binding index|detector/amplifier, original frame ID/index, role, timestamp, exact header exposure, pair ID, actual HDU, readout/binning, physical ROI bounds and source hashes|
|Per-exposure ROI statistics|mean signal inADU, ordinary sample variance inADU², standard deviation, valid pixel count and exclusion counts; raw and configured corrected stages identified separately|
|Flat processing stages|raw; scan-corrected; scan-corrected and master-bias-subtracted. Keep these distinct so the variance definition and processing are recoverable|
|Bias processing stages|raw and scan-corrected, plus original master participation. Bias exposure may be zero; do not force the positive-flat-time interface or discard rejected-master frames|
|Matched pair statistics|both members' levels/times/identities, variance of their pixelwise difference and half that variance, exact common pixel population and mismatch diagnostics. Retain raw and corrected stages distinctly; reuse existing raw results only when definitions/populations match|
|Master-bias evidence|existing master/QC graph, accepted frame IDs, per-ROI summaries, selected-site bias timelines, actual median convention and shared-calibration identity|
|Scan evidence|configured bands/rejection and applied row-correction profiles for rows contributing to ROI statistics; retain the bounded raw scan traces at the approved sites, with physical row/read positions and shared-row identities|
|Individual signal samples|the existing full-precision3200 corrected flat observations at160 sites, linked without changing their values or physical identities|
|Aggregation support|first, second and third noncentral moments of signal over each declared corrected ROI population, for evaluating the planned cubic's regional mean consistently|
|Provenance and availability|estimator definitions, units, coordinate systems, masks/reject bits, raw saturation exclusion, counts, nullable/unavailable states, configuration/source versions and frozen links|

The20-flat sequence supplies10pairs×32detectors×5ROIs = **1600 pair/ROI records**,
with processing stages explicit. Ordinary raw bias-pair RON remains separately
identified with its original two raw exposures. Every pair statistic records its
actual common accepted pixel population, which need not equal either exposure's
individual population. Do not silently compare unlike populations.

For any declared population of N valid pixels,

    mean = sum(S_i)/N,
    sample variance = sum((S_i - mean)^2)/(N-1).

Mean is unavailable atN=0; variance atN<2. Missing values areNone, not zero.
Spatial variance within one exposure includes illumination structure, pixel
response and other effects; it is not automatically independent temporal noise.
Pair-difference variance is a separately labelled measurement used to diagnose
noise. Its interpretation/pooling and later use as fit weights are model choices.

For a cubic Q(S)=S+c2*S²+c3*S³, regional means obey

    mean(Q(S)) = mean(S) + c2*mean(S²) + c3*mean(S³).

Saving the moments preserves this calculation. Do not substitute Q(mean(S)) for
mean(Q(S)). The existing direct-pixel fitter still consumes physical-site samples;
a regional model needs its own declared forward/uncertainty treatment. Means and
variances do not encode arbitrary pixel distributions. The saved dataset supports
the planned PTC/regional diagnostics and direct-site model experiments; originals
remain the source for future models requiring additional information.

Collection retains all valid measured levels. Model-specific signal ranges,
fit exclusions, pooling, weights and likelihood settings are applied afterward,
recorded per fit, without editing the measurement dataset. Existing BPM/finite/
raw saturation admission stays explicit. Do not pre-filter the collected data
using an unchosen fit interval or silently normalize lamp mismatches.

## 4. Revised staged roadmap and position

| Stage | Deliverable | Current position |
|---|---|---|
|1. Preserve admitted inputs and existing results|reviewed32-detector geometry/bindings,30exposures,32masters, raw pair/RON diagnostics and3200 corrected-site samples saved in ASDF|Complete; reuse these products|
|2. Finalize the full collection contract|one reviewed design covering all per-exposure ROI statistics, pairs, bias/scan evidence, aggregation moments and the shared ASDF dataset|NEXT; replace the earlier site-only next-step scope|
|3. Implement and qualify the collection recipe|reused native statistics/correction services and common ASDF factory, with focused new numerical/transport/serialization checks in one integrated qualification|Pending; no old unrelated matrices|
|4. Run one complete collection-and-save job|one guarded project operation reads the admitted exposures, collects missing measurements and saves/verifies the complete detector-ordered ASDF dataset|Pending; collection ends with usable ASDF, not another manual saving stage|
|5. Inspect and experiment from ASDF|select regions/levels; inspect exposure order, illumination, signal/variance and bias/scan behavior; try noise/covariance models, weighting, fit ranges and numerical parameters|After4; no FITS reread for experiments supported by the saved dataset|
|6. Fit and validate calibration candidates|one global signed shutter offset and separate amplifier response coefficients; assess residuals, monotonicity, rank/conditioning, profile identifiability and uncertainty sensitivity; save each candidate/run/configuration in ASDF|Pending; qualified numerical core already exists|
|7. Apply and validate the selected calibration|guard measured validity intervals, apply detector response/time correction with masks/provenance and uncertainty propagation, validate independent data before adoption|Later; no automatic activation|

Each stage5/6 run references an immutable measurement dataset and has its own
model/parameter record and results. A fit result being unavailable does not mean
that valid measured statistics should be absent from ASDF. The software may
expose multiple experiments without designating one scientifically accepted model.
Unsupported likelihood/correlation structure still needs a reviewed implementation;
no silent identity weighting or change to the one-global-shutter requirement.

## 5. Execution and documentation discipline

One collection entry point owns native extraction, source checks, shared ASDF
saving and the overall completion receipt. Native transport files are retained
internal evidence; the user does not run a separate recipe just to populate ASDF.
Reuse existing masters, archived samples and compatible diagnostics. Newly missing
ROI statistics and scan evidence are collected in one additional source pass.
Do not rebuild masters, repeat raw RON recipes or recollect data when changing a fit.
Stop on failure and retain partial evidence; never silently resume or overwrite.

The revised final design must specify bounded scan-profile storage, exact table
schemas/precision/ASDF references, streaming resource limits and the focused test
inventory before implementation. It carries forward the actual43/44-read trimmed
scan estimator (23/24 kept after10/10 rejection), original9/10-frame membership
and native lower-middle median convention. No stochastic model/MC defaults are
needed to collect these measurements. Choosing a model and propagating it through
those estimators follows in stages5/6 under the existing uncertainty policy.

After each scientific subroutine is complete, write its mathematical guide based
on its previously human-reviewed final design. Author the guide in **LaTeX (.tex)
and maintain its corresponding compiled PDF in parallel**, with equations,
assumptions, units, algorithm references where appropriate and explicit mappings
to source functions/data structures and actual validation evidence.

Plots and HTML remain separate stages consuming saved measurements or fit results.
The existing gain/variance mosaic remains available; extend fit/residual/shutter
plots as results become available. Add the requested recipe-navigation sidebar
after the linearity recipe. QC remains project-local; reference database,
per-pixel coefficient maps, broader sampling/higher-signal sequences and production
qualification on Chapman are later extensions, not prerequisites for this
collection-first organization. No merge, installation or cleanup is implied.
