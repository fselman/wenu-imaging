# Linearity data preparation: row overscan and ASDF modelling boundary

5 November 2026. Refs #235/#236; draft PR #227.
Source audited: d921f68150bfb74ae313866154d634596af1a037.
Status: source audit and concrete design for owner review. The owner approved
the sequence and integration goal; this document does not claim review of its
new detailed contract, implementation, tests or actual corrected ROI products.

## Agreed sequence and boundary

First extend the full ROI measurement path to use the supplied detector overscan
parameters consistently for all bias and flat frames. Then integrate preparation
into the linearity recipe using reusable native/Python services. Its durable
output is a complete real-data ASDF preparation archive, consumed by a separate
modelling section. Plotting remains an independent ASDF reader. Model/interval
experiments must not rerun raw preparation. Preserve the completed uncorrected
archive, existing masters, direct-site samples, diagnostics, viewer and runtimes.

The current raw-only command is not a completed calibration recipe.
mef_linearity_raw_from_files deliberately calls raw pair statistics without
overscan or a master. The general mef_linearity_from_files path already calls
mef_linearity_samples for scan/master-corrected direct pixels, but its optional
pair measurements retain their original raw definition. Do not change those
definitions silently or label ROI averages as physical pixel observations.

## Audited reuse

| Responsibility | Existing source/function |
|---|---|
| Resolve supplied detector settings | mef_config_bias_settings |
| Correct each raw row, then crop | mef_overscan_correction / mef_overscan_correction_masked in mefp_lib.c |
| Scan trimmed mean | function1d_average_reject_checked in function_1d.c |
| Correct all bias inputs before frame admission/stacking | mef_cal_bias |
| Master median stack | mef_bias_stack_masked / cube_avg_median / median_pixelvalue |
| Correct flat before master subtraction | mef_linearity_samples |
| Explicit independent file/HDU binding | existing M4 loaders and mef_linearity_*_files adapters |
| Ordinary masked ROI and pair statistics | image_getstats_masked_checked / image_pair_stats_checked |
| Common immutable QC ASDF | existing QcRecipe factory, writer, reader and traversal |
| Diagnostic residuals and ROI ratios | existing separate Python computation modules |
| Physical correction fit | detector_linearity_fit_checked; no real fit in preparation |

Native signal arithmetic stays in C17. Python resolves/orchestrates, freezes
provenance and publishes ASDF; it must not implement another overscan estimator.

## Supplied geometry and exact estimator

Use the selected configuration slot and independently bound detector identity,
not HDU ordinal as a configuration index. Freeze the effective configuration and
its hash. The reviewed canonical OmegaCAM PAF hash is
709d65acdeea6c889ed1468cbb3966d5de93ec654ee030032a096ca12624333f.
Revalidate that effective settings agree with the retained actual-machine
receipts before observational execution. Report unresolved header/configuration
conflicts; do not infer or silently overwrite geometry.

For this selected normal/ordered 1x1 configuration, prescan is disabled,
overscan enabled, and rejection is 10 low and 10 high reads:

| Native slots, one-based | Raw FITS x bounds, inclusive | Reads | Kept |
|---|---|---:|---:|
| 1–8, 17–24 | 2100–2142 | 43 | 23 |
| 9–16, 25–32 | 5–48 | 44 | 24 |

These are configured image coordinates, not newly verified hardware amplifier
identities. Preserve unrotated raw coordinates and the existing instrument
mapping. Do not infer physical readout direction from which scan band is used.
Retain each ROI's exact raw and active row interval so the owner can assess
whether it covers or dilutes the observed ramp.

For each raw frame f and row y, take the configured electronic reads v, sort a
copy, reject l lowest and h highest, and compute

    O_f(y) = pix( sum(v_sorted[l : n-h]) / (n-l-h) ).
    U_f(x,y) = pix(D_f(x,y) - O_f(y)).

The sum/division uses double in function1d_average_reject_checked; pix is the
build's native pixelvalue conversion. The existing row subtraction rounds back
to native pixels. Keep that arithmetic and order exactly.

The existing routine processes EVERY raw row independently, including the first
and last raw rows, then crops using the supplied inclusive trim rectangle.
There is no smoothing, polynomial, interpolation, adjacent-row window,
endpoint extrapolation or replacement by a global level. Active row y maps to
raw row y + trim_y_min - 1. First and last active rows use their own raw-row
estimates. Prescan remains disabled for this dataset; a generic optional policy
does not authorize changing the supplied setting.

The active-pixel BPM is not applied to electronic scan reads. Use the existing
unmasked scan path. Reject invalid geometry, too few retained reads and nonfinite
enabled scan samples before correction. No new sigma clipping, scan saturation
cut or tied-read membership rule. Missing/incompatible required overscan fails.

The legacy routine mutates its image and temporarily adjusts geometry to C
indexing. Call it only on private image/configuration copies. Preserve borrowed
raw planes and the immutable resolved configuration, on success and failure.

## Bias and master consistency

All ten original bias inputs receive the SAME configured row correction before
the existing frame rejection and median stack. For the comparison run, reuse
the already completed scan-corrected masters only after their hashes, geometry,
effective scan settings and per-frame/accepted membership provenance match.
A missing or incompatible dependency stops preparation; do not repair it by
treating an uncorrected master as corrected or recorrecting an active master.

The existing accepted membership is authoritative for this comparison:
CCD69/74/77/84/85 have nine accepted frames; the others have ten.
If a later complete recipe builds a fresh master using the existing bias recipe,
retain all ten input decisions and compare the deterministic result/membership
with the preserved reference. An unexpected difference stops downstream work.
Do not silently force membership or change rejection thresholds.

At each active pixel p,

    B_p = existing_median({ pix(D_bp - O_b(y_p)) : b accepted }),
    S_fp = pix(U_fp - B_p).

Nine accepted inputs use the fifth ordered value; ten use the lower-middle
fifth ordered value, not the average of the two middle values. Preserve the
separate native roundings. The master has already had its input scans removed:
subtract it ONCE from each corrected flat, with no second scan correction
applied to the master. Bias diagnostics may retain U; bias inputs are not
calibrated by subtracting their own master for the physical fit.

## Full ROI measurements and direct samples

Retain the existing 20 flat exposures, exact times, pair/member/input identities,
five full ROIs per detector, independently bound HDUs, original raw saturation
threshold 65534 ADU and declared BPM polarity/reject bits. No new range cuts,
lamp normalization, frame averaging or scientific outlier selection.

For each pair/ROI, freeze the original common raw eligibility population:
BPM, nonfinite values and saturation retain their existing meanings/precedence.
Measure corrected means of BOTH members on that same population, preserving
their individual identities. Record count and exclusions. Also retain ordinary
sample spatial variances of each corrected member, the corrected pair-difference
mean and sample variance, and half that difference variance as a separately
defined diagnostic. N<2 makes sample variance unavailable, not zero.
A nonfinite corrected value on a previously admitted raw site is a failure,
not a silent population change. Do not reuse detector_gain_pair_checked on
master-subtracted flats and thereby subtract a bias level a second time.

Keep the old raw bias-only RON and raw paired gain/variance products with their
original processing stages. Corrected pair-difference variance and per-image
spatial variance are separate measured quantities; neither automatically becomes
an independent noise weight or a newly accepted gain calibration. A shared master
cancels algebraically from a flat difference; native-rounding effects remain.
No RON²/N assignment to a median or invented scan uncertainty.

Physical response fitting continues to use the explicit 160 approved direct
sites and 3200 individual corrected pixel observations, never ROI means.
Reuse their completed archive when its full source/master/settings lineage is
compatible. The new full-ROI path must compare native corrected values at those
sites with the archived values while their frames are already in memory; require
exact same-build agreement, or stop and investigate. Do not substitute nearby
pixels or use the unaccepted broader noise-evidence campaign as a prerequisite.

## Correction evidence and ASDF preparation products

Retain an ordered row-correction trace per detector/frame: raw row index,
native O_f(y), configured strip bounds, supplied/retained count and l/h.
Capture the existing scan estimates before the legacy routine sorts scan_line
for its QC median. A backwards-compatible optional trace output may expose
these values; it must share the same arithmetic implementation and leave legacy
callers/results unchanged. Do not replace the routine with a Python replay.
Do not collect all individual scan reads or start a new noise campaign here.
For already completed bias masters, new trace evidence is gathered from immutable
bias inputs using the same routine; preserve the originals and verify consistency
with recorded bias QC and membership. A later integrated recipe retains these
traces during its normal bias preparation rather than performing a separate pass.

Use new project-local ASDF products through the unchanged shared QC machinery.
New recipe-specific owned extensions carry the trace and corrected ROI rows,
native numerical text/typed transport where applicable, units, availability,
definitions, identities, population, full effective settings, producer revision
and frozen source/master references. No plotting inside the recipe.
One complete index/manifest joins these products with existing immutable raw
diagnostics, master/input QC and compatible direct-site ASDF. A portable archive
freezes the required dependency graph, not external absolute paths alone.

Expected real-data coverage: 32 detectors; 1600 corrected pair/ROI rows;
3200 corrected exposure/ROI measurements; 3200 direct-site observations with
160 physical sites; all ten bias input decisions per detector and their master
memberships. Trace counts follow actual admitted raw heights, not a fabricated
common height. Keep 160 old bias-only ROI diagnostic rows as linked raw-stage
evidence. Each component has an explicit stage and units.

Distinguish preparation completeness from modelling readiness. Complete data
may still declare NOISE_UNAVAILABLE. Preserve unavailable covariance/noise
components and their reason; do not invent weights to make a fit run.
The model section validates data definitions and required scientific inputs
from the saved manifest before calling existing fitting services. All model
experiments save separate settings/results against a fixed preparation digest.

## Recipe integration after overscan qualification

Add a preparation section to the linearity recipe which calls the existing
bias, corrected-measurement, selected-pixel and shared-ASDF services through
explicit typed boundaries. Thin command entry points call that same section.
Do not retain competing scientific implementations in standalone scripts.

The preparation section resolves inputs/configuration; verifies or creates its
bias dependency; corrects/measures one detector at a time; checks site replay;
publishes a fresh ASDF graph and complete manifest only after preservation checks.
Existing compatible preparation can be reopened read-only by exact digest;
incompatible requests require a new output destination. Modelling takes the
manifest as input and does not reread raw FITS. No real physical model selection,
covariance campaign or curve adoption is authorized by this preparation work.

Retain actual max-loaded-pixel and owned-result budgets. One detector is active
at a time; do not increase the existing whole-batch memory ceiling silently.
No all-detector cube, detector parallelism, installation or dependency changes.
All real batch work runs at niceness >=10. Keep partial failure evidence and
never overwrite completed products or silently retry/resume.

## Focused qualification and review gate

Before implementation the owner reviews this exact contract, especially row
edges, reuse of corrected masters, corrected ROI populations/statistics, trace
retention and the ASDF/model boundary.

Then explain and run only focused changed-code checks:
1. Native synthetic known answers for both 43/44-read strips and their 10/10
   rejection; first/last raw and active rows; nonconstant row ramps; supplied
   crops; native staged rounding; corrected-master single subtraction; exact
   old-path direct-site agreement; immutable inputs/configuration and failures.
2. Synthetic independently reordered FITS bindings and fixed raw masks;
   per-member means/variances and pair statistics on the declared population;
   all bias decisions; trace row order/count; bad geometry/nonfinite scan,
   wrong master/stage, limits, aliases and partial-output refusals.
3. Shared-ASDF roundtrip/relocation and manifest completeness; null versus zero,
   units/stages/lineage/digests; model-reader rejection of incompatible data and
   explicit unavailable noise; plotting with computation disabled.

Each test announcement must identify functions, inputs and expected answers.
Reuse byte-identical prior qualification; no replay of old matrices. Actual
Intel Mac changed-code qualification precedes one protected real full-ROI pass.
No actual Mac receipt or preservation success is claimed until returned.
Recover the existing ratio viewer receipt without regeneration as an independent
read-only record; its absence does not justify rerunning prior measurements.

After implementation and qualification, maintain the mathematical guide in
LaTeX plus matching compiled, visually checked PDF, tied to final functions,
equations and actual acceptance evidence. No scientific implementation,
new tests, raw processing, model fit, merge, install or cleanup occurred in
preparing this design.
