# Linearity roadmap v3 — display the measurements before modelling

4 November 2026. Owner-approved sequence, refs #236 and #235.
This replaces v2's proposed broad collection redesign. Existing extraction,
pair statistics, ASDF products and gain/variance displays already provide most
of the required machinery. Extend them; do not restart the recipe.

Latest: actual Mac signal/time qualification17/17 and full real-data viewer
completed (32detectors,1600pair rows,3200exposure/ROI entries,160bias rows), all
preservation checks true. Owner has inspected it and explicitly approved the
[diagnostic residual display](design/linearity-residual-display-v1.md): unweighted
free-intercept lines per detector/ROI, residuals versus original signal/time,
explicit fitting limits, and S/t inspection. This narrowly supersedes the earlier
no-fitting boundary for diagnostic detrending only. Physical shutter/amplifier
correction modelling remains subject to a later owner instruction. Mathematical
implementation guide: [PDF](linearity-residual-display-guide-v1.pdf) and
[LaTeX](linearity-residual-display-guide-v1.tex).

## Current position

All 32 detectors have raw flat-pair diagnostics in ASDF, covering 10 pairs and
five ROIs per detector. Variance versus signal and diagnostic gain versus signal
are already available. The pair tables also retain each member's `first_seconds`
or `second_seconds`, `signal1_adu` or `signal2_adu`, source identity, original
input index and ROI. Thus the average signal versus time can be displayed from
these existing measurements, without rereading FITS or measuring pixels again.

These signals belong to the existing raw-pair processing definition: bias-
subtracted levels without overscan correction, on the pair's common accepted
population. They must not be relabelled as scan/master-bias-corrected ROI means.
The separately archived 3,200 corrected individual-site samples are individual
pixels, not ROI averages. Preserve both products and their distinct definitions.
If an additional corrected ROI stage is needed, add only its missing means
through the existing extraction path, under an explicit processing definition.

## Controlling roadmap

| Step | Work and completion condition | Position |
|---|---|---|
| 1. Reuse the measurements | Preserve existing mean signals, variances, point gains, source bindings, ROI geometry, master products and individual-site archive | Complete foundation |
| 2. Expose signal versus exposure time | Use both members of every pair separately: 20 exposures × 5 ROIs × 32 detectors = 3,200 exposure/ROI entries, retaining original acquisition indices, exact times, processing stage and pair population. Existing ASDF fields remain authoritative; do not average the two members into one point or duplicate measurements in a competing archive | Next, small extension |
| 3. Save and describe the data | Any genuinely missing measurement is added via existing extraction/ASDF machinery; new ASDF files begin with short descriptive comments. Existing immutable archives remain unchanged | Header writer implemented in this increment; data/display extension pending |
| 4. Display all measurements | Add average signal versus exposure time beside existing variance versus signal and gain versus signal. Show all detectors and five ROIs, retain both pair members, permit detector/ROI selection and expose exact values/source identities and unavailable states | Required before modelling |
| 5. Owner inspects the complete data | Deliver the ASDF-backed displays and underlying values for all detectors/ROIs; obtain the owner's instruction to begin modelling after inspection | Mandatory sequencing boundary |
| 6. Develop and explore the model | From the saved data, review the mathematical design and experiment with signal ranges, weighting/noise assumptions and numerical parameters. Target one shared signed shutter error and separate amplifier response curves; preserve each experiment's configuration/results | Deferred until step 5 |
| 7. Validate and apply a selected correction | Assess residuals, identifiability, monotonicity, uncertainty and measured validity; test independent data before adopting pixel correction | Later |

**No new modelling, fitting, shutter estimation, coefficient extraction or
model-dependent data selection before all measurements are saved and displayed
and the owner has inspected them and instructed that modelling begin.** Existing
qualified numerical kernels can remain available; their existence does not
authorize a real-data fit. Do not introduce a new noise-evidence collection
campaign or the v2 4,800-record redesign as a prerequisite for the third plot.

Organize inspection by physical detector/amplifier, original exposure index and
ROI. Exposure time is a separate plotting/sorting coordinate. Show the processing
stage and pair populations explicitly. Preserve missing values as unavailable,
not zero. Pair-difference variance and any individual-image spatial variance
have different meanings; retain the existing definitions. Point gain is a
diagnostic arithmetic value, not an accepted gain calibration.

## ASDF introductory comments

Keep the mandatory ASDF magic/version lines first. Immediately after them, add
a few `#` comment lines describing the sidecar, referenced filename, operation,
and content (pair statistics, bias/RON diagnostics, corrected individual samples
or general detector QC). Direct readers to the structured `qc` tree for units,
definitions, selectors, availability and frozen source links. Comments are
descriptive; the structured record and its semantic digest remain authoritative.

The shared writer now generates these comments for newly written files. ASDF 6
accepts comments in this position but does not serialize its read-only comments
property. The writer inserts them into its metadata-only serialized output before
exclusive publication. Common QC records contain JSON primitives and no binary
array blocks or block offsets. Existing archives are not patched in place,
rehash-rebased or overwritten; legacy uncommented files remain readable.

Agent checks with existing ASDF 6.0.0 passed: 13 shared QC checks in 0.863 s,
9 pair-QC checks in 7.138 s and 5 corrected-sample checks in 6.028 s. An initial
new fixture incorrectly used the bias-only adapter with a generic operation;
corrected the fixture to use QcRecipe, then all checks passed. These are
metadata/ASDF tests, not new scientific or actual-Mac acceptance.

## Separate display stage and later documentation

Plotting and HTML creation consume saved ASDF independently of recipe runs.
The third plot is the immediate display extension. Recipe navigation in the
left sidebar follows completion of linearity. QC stays project-local; a reference
database remains a later addition. No new reference sequence or higher-signal
coverage is required to display the current measurements.

Review the final mathematical design before implementing a new scientific
subroutine. After implementation, maintain its mathematical guide as LaTeX
source with a corresponding compiled PDF, tied to the final implementation.
No merge, installation, cleanup or activation is part of this increment.
