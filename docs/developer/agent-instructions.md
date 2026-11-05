## Actual all32 dependency admission complete — 5 November 2026

Owner reports source0a87c99 receipt8/8 and complete_dependency_plan at
ocam-linearity-preparation-plan-KSBh9ZXu. All6preservation guards true.
All32detectors:20flats+10bias inputs; preserved masters retain9accepted for
CCD69/74/77/84/85,10for27others. No real corrected ROI processing yet.
Reuse exact saved plan/source and d25b106 qualified native build; do not repeat
admission/qualification/bias construction. Next new corrected-ROI execution for
CCD65 via prepare_detector, then remaining31after verifying execution; reuse
completed CCD65. Separate diagnostics/plots then owner inspection before models.
No new scientific/noise choice, fit, install, merge or cleanup. See [receipt](evidence/linearity-preparation-2026-11-05/mac-dependency-admission-receipt.md).

## Receipt-control macOS path correction — 5 November 2026 (#242)

Actual dc7807a retry stopped before admission: two positive JSON tests expected
/var temporary paths while the locator correctly resolves /private/var. Six
negative controls passed; qualified source/binary/runtime/checkout preserved.
Retain plan-GtN3wq9D and earlier plan-vrhso3qw. Tests now expect canonical paths
and exercise directory aliases; agent8/8 passed under a symlinked temp root.
Runner prints failed control logs immediately. Production receipt locator and
all numerical/FITS/common-QC code unchanged. Next retry8receipt checks+all32
metadata admission through the new exact runner, reusing d25b106 native build.
No broad gate/native execution/FITS opens/image hashes/install/merge/cleanup.
Actual Mac test correction and all32 admission remain pending. See #242/#241.

## Bias receipt compatibility correction — 5 November 2026 (#241)

Actual all32 metadata admission stopped before the first detector because CCD65
uses local outer-execution.json with preservation.inputs, not the batch's
source_preservation/overall-execution.json schema. Owner confirms pilot5 guards
and batch8 guards all true, matching first-bias digest; batch before/after equal.
New metadata-only locator validates both real schemas and selected-master identity,
rejects failed/missing/ambiguous receipts. Agent8 JSON checks +1 synthetic recipe
case pass. Numerical/FITS/QC code unchanged; reuse actual d25b106 Mac native build.
Actual corrected all32 admission remains pending via retry_linearity_admission.py:
8 new receipt checks only, then metadata plan, no FITS opens/image hashes/native
execution/rebuild/broad gate replay. Preserve failed plan-vrhso3qw. Report unchecked
preservation as null, not false. No real corrected ROI archive, model, install,
merge or cleanup. See [correction status](linearity-bias-receipt-compatibility-2026-11-05.md).

## Actual Mac recipe/ASDF gate passed — 5 November 2026

Owner reports mac-linearity-recipe-rSGbf1Mq passed3native CTests in49.14s
and the required17Python controls, all4preservation guards true. Reuse its
retained source/build/private QC runtime; do not repeat qualification.
Read saved qualification.json source_revision before the next action (fetch
head62fce1f only repairs footprint mode; fetch output is not source proof).
Next admit all32 preserved master/sample dependencies through the qualified
TOML-led service and save a metadata-only plan; no FITS reads or image hashing.
Then new corrected ROI ASDF, separate diagnostics/plots, owner inspection before
physical modelling. No master rebuild, separate singleton extraction, install,
merge or cleanup. See [actual receipt](evidence/linearity-preparation-2026-11-05/mac-recipe-receipt.md).

## Linearity recipe/ASDF integration candidate — 5 November 2026

Owner supplied existing master/sample metadata after actual d8bf560 Mac gate.
Preserved32 masters and32sample ASDF/3200rows/1088records are dependencies.
New recipe composes TOMLs, explicit FITS/overscan services and common ASDF;
validates corrected-master snapshot/memberships, replays direct sites within
new ROI pass, retains30frame ordered traces/detector and frozen source graph.
Legacy bias QC null hashes resolve from completed bias outer receipt, not a new
historical baseline. Agent3native+6TOML+11recipe/ASDF controls pass. Three-page
LaTeX/PDF guide updated and visually checked. Actual Mac integration gate next:
Pycavi2/tests/qualify_linearity_recipe_mac.py (3native+17Python,4guards).
Reuse old overscan gate; do not repeat bias generation or a separate singleton
campaign. No real corrected ROI products, fit, installation, merge or cleanup.
See [integration status](linearity-recipe-integration-2026-11-05.md).

## Actual Mac overscan gate passed - 5 November 2026

Owner returned d8bf5608c73b3aee8b5411b3193f4184bd0f7b5a qualification passed at
mac-linearity-prepare-5QEzvc2c. Native4/4 in5.91s plus required6TOML+5viewer
controls; checkout, installed_files and exported_source all true. Reuse exact
retained source/build; do not replay this gate. See [receipt](evidence/linearity-preparation-2026-11-05/mac-receipt.md).

Next is the authorized FITS/linearity-recipe/ASDF integration, using detector and
processing TOMLs, existing corrected masters/memberships and direct-site archive.
Read existing metadata first; no repeated bias generation, singleton extraction,
old gate, physical fit, installation, merge or cleanup. Full corrected ROI ASDF
products do not exist yet. Earlier pending-Mac statements below are historical.

## TOML-led overscan preparation implemented; Mac gate pending - 5 November 2026

Owner reviewed the detailed design at5b3a493 and instructed implementation.
New shared TOML resolver freezes detector/processing inputs and validates sample
versus full-band geometry, controls and ROIs. Processing TOML adds explicit
numerical schema1 controls. Viewer reuses that resolver. New C17 frame/pair
preparation services reuse existing row correction, preserve native rounding,
subtract a corrected master once, retain ordered row traces and measure corrected
ROIs on the original common raw population. Existing raw/sample/bias behavior
is preserved; all ten bias construction remains in the existing bias recipe.

Agent4native+6TOML+5viewer controls passed, including128persistent owner-failure
positions per43/44-read fixture. LaTeX/PDF kernel guide:2pages, visually checked,
no overfull boxes. Actual Mac qualification remains pending via
Pycavi2/tests/qualify_linearity_prepare_mac.py. No observations or new corrected
ASDF products exist yet. After this overscan gate, complete FITS/recipe/ASDF
integration and direct-site/master provenance before any real corrected pass or
physical modelling. Reuse completed earlier archives/gates; do not merge,
install, provision dependencies or clean retained evidence.
See [status](linearity-preparation-2026-11-05.md). This supersedes older design-review-pending wording below.

## Resume 5 November 2026 -- actual ratio run complete; overscan next

Read [the current handoff](handoffs/resume-2026-11-05.md)
before resuming. It supersedes earlier pending ratio-gate/run statements.
Actual c33c6ce Mac qualification passed20/20, all4guards, retained
mac-roi-ratio-pxzzz0v6. Real ratio ASDF complete at
ocam-roi-ratio-3fjfywj0:32detectors,640rows, all5outerguards. Do not repeat.
Owner inspected ratio plot and reports effects generally +/-0.0005 or below
(axis units must be confirmed; normalized deviation0.0005=0.05%). Exact HTML
run path/receipt has not been pasted; locate existing viewer receipts rather
than regenerating. Current data have NO overscan correction. Owner's priority
is consistent overscan subtraction in ALL bias/flat frames, preserving row
dependence and master-bias consistency. Audit/reuse existing routine, finalize
and review exact estimator/geometry/edges before implementation. Then NEW full
ROI measurements -> ASDF diagnostics -> plots -> inspection before physical
modelling. Preserve originals/runtime/source; no overnight execution, old gate
replay, installation, merge or cleanup. Details and exact paths in handoff.

## Same-exposure ROI ratio and overscan requirement — 4 November 2026

Owner requires overscan subtraction in ALL bias/flat frames: observed row ramp
near the output settles after a few hundred rows. Preserve the row dependence;
a single global level must not be substituted without evidence. Use consistent
overscan treatment of master-bias inputs and flats, avoiding double subtraction.
The spatial pattern is evidence to inspect, not proof of a physical shutter term.
Final ratio design: docs/developer/design/roi-ratio-asdf-v1.md. Compute
near_readout/parallel_far for each exact exposure/member from existing stored
original ROI signals. Save raw ratio, arithmetic reference mean (BOTH signals
15000..35000ADU inclusive), normalized ratio, percentage departure, membership,
units, stage and frozen lineage in NEW ASDF. No scientific math in plotting.
Plot saved ratio vs numerator signal or time using shared axes/cursor.

Current archive is raw_pair_bias_subtracted_without_overscan; ratio HTML must
say so. This increment does not perform an image remeasurement or claim an
overscan-corrected ROI archive. Next perform the consistent all-frame overscan
ROI measurement pass, with its own explicit reviewed estimator/edge handling,
then recompute these diagnostics and compare before any physical modelling.
Do not mix the corrected singleton pilot with full ROI means. Preserve all inputs.

Actual b8dfd40 Mac gate passed30/30, all4guards, retained mac-shared-plot-w2slb5vp.
Actual separate15000..35000ADU line-ASDF computation complete at
ocam-residual-asdf-15000-35000-hwolegq7:32products,160ROI summaries,3200rows,
all5outerguards. Repeated pasted logs are one run; do not repeat these gates.
New agent ratio8, viewer9 and dispatch3 pass; JavaScript ratio controls pass.
Actual Mac ratio gate and640-row real ratio publication remain pending.
Use qualify_roi_ratio_mac.py: reuse unchanged qualified common/numerical modules,
run only changed ratio8+viewer9 and3dispatch checks. Then compute ratio ASDF;
render independently. No dependency provisioning, installation, merge or cleanup.
Mathematical implementation guide: roi-ratio-guide-v1.tex and compiled PDF.
Earlier entries below are historical where superseded.

## Shared plot axes/cursor; proposed middle reference interval — 4 November 2026

Owner requests modular reusable plotting. Use tools/qc-plot-inspection.js for
all HTML plot axis helpers/crosshair/x-y readout; plots supply bounds/units only.
Static Matplotlib plots use pycavi_plot_axes.py. Both read the one maintained
config/plotting/signal-axis-v1.json: ticks every10000ADU, final65535. Full display
extent does not imply measured coverage. Apply to absolute signal axes only,
not residual/rate axes. Keep negative measurements visible. Raw saturation
exclusion65534ADU is unchanged. Cursor returns continuous plot coordinates, not
an interpolated curve or a new measurement; exact point inspection stays separate.
No fitting/scientific derived-value math in plotting/browser code.

Owner clarifies Bonn shutter/no assumed spatial correction. Do not interpret
focal-plane differences as spatial shutter timing in this sequence. Owner proposes
15000..35000ADU as the next diagnostic reference interval: pass explicit
--fit-signal-min15000 and --fit-signal-max35000 in the next separate compute run,
record them in ASDF, retain every outside-range point. Do not alter previous data,
fits or archives, and do not silently switch an existing all-range fit.

Agent shared-module/actual-JS checks, viewer9 and pair/plot9 passed; static PNG
inspected. The full new computation-ASDF/plot Mac gate is pending (previous
6acd3b10 command has not returned). New qualify_plot_inspection_mac.py covers
pending storage9+changed static9+viewer9, with3runner checks, avoiding native/
common-header rebuild/replay. Real32diagnostic ASDF and new cursor viewer pending.
No physical shutter/linearity model, installation, merge or cleanup.
See docs/developer/shared-plot-inspection-2026-11-04.md; prior entries are history.

## Computations and curves must be saved in ASDF before plotting — 4 November 2026

Owner explicitly requires computational/plotting separation. Controlling final
design: docs/developer/design/linearity-residual-asdf-v2.md. This supersedes
browser-side OLS in v1. Pure Python service computes the already approved
unweighted/free-intercept diagnostic; a separate command writes per-detector
ASDF with settings, coefficients, all predictions/residuals/rates, units and
frozen source links through the unchanged common QC factory/writer/reader.
Original measurement ASDF stays immutable. Changing limits needs a fresh compute
run; HTML only reads saved diagnostics, with read-only saved fit limits and
interactive presentation controls. No fitting/prediction/residual/rate math in
HTML. No physical shutter/amplifier correction is authorized.

Actual interim residual viewer completed at ocam-residual-viewer-fes7vt_w with
all5preservation checks. Retain it. Sourcef2a15c7 Mac qualifier passed2runner+
8viewer tests, all4guards, mac-residual-viewer-tmpq60uq; retain the earlier failed
run too. These old gates need no repetition. New storage9 and reader/viewer9
checks pass here, including analytical cases, separate command, exact ASDF
round-trip/relocation, source digests, no overwrite and fitter-disabled reads.
Actual HTML JS shows stored residual values verbatim. Mac separation qualifier
and real32-detector computation/ASDF publication remain pending. No old native/
ASDF matrix replay, image reads, measurement rerun, install/merge/cleanup.
Mathematical guide maintained as LaTeX and compiled PDF v2. Earlier entries are
historical where superseded. See docs/developer/linearity-residual-asdf-2026-11-04.md.

## Residual computation saved to ASDF before plotting — 4 November 2026

Owner explicitly requires computations separate from plotting and diagnostic
curves stored in ASDF. Controlling final design: design/linearity-residual-asdf-v2.md.
This supersedes browser-side OLS in v1. Keep ordinary unweighted free-intercept
fits and all sample/interval/null definitions. Python pure computation service;
common QC factory/writer for immutable per-detector ASDF: settings, fit summaries,
all predictions/residuals/rates, units and frozen source pair graph. Completion
index carries product digests and source preservation. New interval -> new run.
HTML only reads saved diagnostic curves, never refits/recomputes; fit settings
read-only. Existing raw pair and corrected sample archives stay immutable.
Computation command compute-pair-residuals.py is distinct from view-pair-qc.py
with --diagnostics. No common writer/schema change or raw FITS read. Guide v2 is
LaTeX plus compiled PDF. Actual Mac separated-computation gate/persistence pending.

Interim f2a15c7 actual Mac gate passed2runner+8viewer checks (0.031s/12.199s),
all4guards. Interim residual viewer ocam-residual-viewer-fes7vt_w completed with
all5guards. Preserve it as history; it is not the final separated-ASDF product.
No physical shutter/amplifier correction, flat-field adoption, merge/install or
cleanup. Earlier browser-computation instructions are superseded by this entry.

## Owner-approved straight-line residual diagnostic — 4 November 2026

Owner inspected the real signal/time viewer and approved per-detector/ROI
straight-line detrending as an exploratory display. Final approved design:
design/linearity-residual-display-v1.md (under docs/developer). Fit unweighted
S=a+b*t with a free intercept; retain all individual exposures, exact sources,
nulls and outside-fit-range points. Explicit ADU fit limits; residual x=original
signal or time, y=percent (positive prediction only) or ADU. Add S/t versus time;
a constant shutter offset is absorbed by the line and gives a fractional delta/t
rate effect. No physical shutter estimate or amplifier correction is authorized.

Actual32-detector signal/time viewer complete at Pictures/OCAM/wenu-imaging/
ocam-signal-time-viewer-wrwn42uk:1600pair rows,3200exposure/ROI rows,160bias rows,
all5preservation checks true. Actual56b7f48 Mac display gate17/17 passed with
all4guards (mac-signal-time-j4ke56uy). Do not repeat old gates or extraction.
New residual module is display-only JS embedded into existing HTML; derived JSON
export saves settings/OLS summaries/rows/source refs; authoritative ASDF untouched.
Agent8analytical groups,8Python viewer controls and actual-script JS checks pass;
browser rendering not claimed (known socket restriction). Mac residual gate and
fresh real-data residual viewer pending. Guide is LaTeX plus compiled PDF.
No physical model, flat-field change, merge/install/cleanup. Earlier entries are
historical where superseded. This permission is limited to diagnostic line fits.

## Signal/time display candidate; ASDF header Mac gate passed — 4 November 2026

Actual source1a422b99 Mac ASDF comments passed27/27 (shared13 2.308s, pair9
17.066s, sample5 6.637s), all5preservation guards true, retained at
mac-asdf-comments-moofbx58. Do not repeat that gate without relevant changes.
Signal/time display now projects existing ASDF pair member means/times without
remeasurement. Preserve exact member/asset/HDU/input index/source row/population;
inspection ordered by acquisition index/ROI, curves by exposure time. Third PNG,
exact derived JSON and offline mosaic metric added. Null/negative data preserved.
Agent pair9/viewer8 and actual-script JS logic checks pass; Chromium launch
blocked by socket restrictions, browser layout NOT claimed. Mac display gate
and real32CCD viewer pending. Use qualify_signal_time_mac.py, then generate from
retained pair ASDF. No raw reads/extraction/fit/model/noise choices/merge/install/
cleanup. Owner must inspect all data and instruct modelling before it begins.
See linearity-signal-time-display-2026-11-04.md. Earlier statuses are historical.

## Owner narrows linearity roadmap: display all data before modelling — 4 November 2026

Controlling roadmap: docs/developer/linearity-roadmap-v3-2026-11-04.md (#236/#235).
Owner explicitly supersedes v2's broad collection redesign. Existing raw-pair
ASDF contains individual signal1/signal2 and exact first/second exposure times;
use these for the signal-versus-time extension alongside existing variance/gain
plots. Preserve their raw-pair, bias-subtracted, no-overscan processing definition
and common pair population. Do not call corrected individual-site pixels ROI
means. Extract only any genuinely missing stage/measurement through existing code.
No new full statistics/noise-evidence campaign is prerequisite for the third plot.

Immediate sequence: reuse archived measurements; expose 20 exposures x 5 ROIs x
32 detectors (3200 entries), both pair members separately; add signal/time display
and exact value/source inspection beside existing gain/variance mosaic. Plot/HTML
creation remains separate from recipes. ALL measurements must be saved/displayed
and inspected by the owner before their instruction to begin modelling. No new
fit, shutter estimate, coefficients, model-dependent cuts or covariance study now.

Shared QC writer now adds a few descriptive # lines after ASDF's mandatory header
for newly written files: purpose, filename, operation, content and structured-QC
location. Semantic records/digests and frozen references are unchanged. Existing
archives stay immutable/readable; no in-place editing or forced regeneration.
Agent ASDF6 checks: shared13/13 (0.863s), pair9/9 (7.138s), sample5/5 (6.028s).
Initial new header fixture used the bias-only adapter with a generic operation;
corrected the fixture to use QcRecipe, then all pass. No scientific numerical
code, real FITS reads, new measurements or actual-Mac acceptance claimed.
No merge, install, cleanup or model selection. Later mathematical guides remain
LaTeX plus matching compiled PDF after reviewed design and completed code.

Earlier dated entries below are history where superseded by this instruction.

## Owner revises roadmap: full exposure statistics first — 4 November 2026

Owner explicitly directs collecting mean signal and variances from all exposures,
ordered by detector, saving ASDF, THEN exploring models/parameters. New roadmap:
linearity-roadmap-v2-2026-11-04.md. It supersedes the narrow unaccepted Stage8v1
site-only next-step scope; preserve that earlier design as history. This is a
roadmap revision, not implementation or approved statistical model selection.

For current32detectors,30frames (20flat+10bias),5existing fullROIs:4800exposure/ROI
records with raw/corrected stages, mean/sample variance and pixel/exclusion counts;
1600flat-pair/ROI records with exact common populations and stage-specific variance.
Keep raw biasRON, master membership, scan evidence and existing160-site samples.
Retain cubic signal moments so Q(mean) is never used as mean(Q). Individual-image
spatial variance and pair-difference variance are distinct, not automatic weights.
All valid levels stored; later model cuts/settings do not alter collection.

One integrated collection+ASDF job after a reviewed complete contract and focused
qualification; fit experiments read immutable ASDF and save separate model/results.
Do not add repeated extraction/saving stages around parameter changes. New guide
policy also requires LaTeX.tex plus matching compiledPDF maintained in parallel,
after completed scientific implementation based on previously reviewed design.
No C/Python service change, new tests/observations/fit/installation/merge/cleanup
in this roadmap-only increment. #236 open; original archive remains preserved.

## Stage8 noise-evidence design ready for human review — 4 November 2026

Owner said Proceed with the roadmap. Under the new owner documentation policy,
scientific subroutines need a finalized human-reviewed design before implementation
and a mathematical guide tied to final code after completion (references where
appropriate). This Stage8 design candidate is prepared, not yet reviewed/accepted:
linearity-noise-evidence-design-v1-2026-11-04.md. No new scientific code/tests or
observational reads run in this step; do not call the proposed checks passing.

Concrete source findings: approved160 sites occupy96 distinct raw rows. Enabled
overscan widths are43 for16detectors and44 for16; low10/high10 rejection leaves
23/24 reads. Current10-frame master uses lower-middle fifth order statistic;
9-frame master also fifth. Preserve exact native estimator/rounding, not a generic
mean-of-middle median. Design captures10bias+20flat site values and scan reads,
scalar160-master and3200-flat replay, original memberships and physical source keys.
Expected4800site rows,2880scan estimates,125280scan reads,160master rows;63 image
inputs guarded before/after. No old recipe rerun, model/MC/weights/range/fit chosen.

Review complete design before implementing the new service/file adapter/ASDF.
Final mathematical guide follows completed implementation, not a substitute for
that earlier review. Existing archives and qualified software stay intact;
#236 open. No install, merge, cleanup or new user-host processing for this review.

## Actual corrected-sample ASDF archive complete — 4 November 2026

Qualified0ce05fcd source persisted all32 detector products,3200 rows and1088
shared ASDF records at Pictures/OCAM/wenu-imaging/ocam-corrected-sample-asdf-xm1ngkg_/
persistence. Inner statuscomplete; outer complete_for_owner_inspection. All5
preservation checks true: checkout, installed_files, exported_source,
private_qc_runtime, native_evidence. Native source tables, master QC graph and
runtime preserved; no observation reread, image hash or measurement rerun.
Data preparation/archive stage is complete.3200 admitted,0missing,160/160 sites.
Do not repeat source exports, qualification, extraction or ASDF conversion.

Next substantive gate is empirical noise/covariance and the real joint correction
fit. Reuse the agreed uncertainty policy in linearity-uncertainty-review-2026-11-03.md:
measurement first, actual trimmed scan and median master estimator propagation,
fixed covariance within a fit, outer sensitivity for estimated weights. Current
raw pair variance is not automatically corrected independent variance; same-master
cancellation prevents estimating shared master uncertainty from pair differences.
No distribution/pooling/MC settings, interval or identity weights selected.
Review needed same-site bias/scan evidence before choosing a model; retain within-
block correlations and require justified independence across the3noise blocks.
One common shutter parameter remains global; amplifier response coefficients
remain separate. No coefficients fitted/applied, plots/HTML, install/merge/cleanup.
#236 stays open. See corrected-sample-asdf-2026-11-04.md for actual archive receipt.

## Actual Mac corrected-sample ASDF gate passed — 4 November 2026

Actual0ce05fcd2c10519cf0a6726df2083cda55a4bf5a passed5/5 in8.938s at
/Users/fselman/Software/build/wenu-imaging/mac-sample-asdf-2bqdfrlp.
All4preservation guards true (checkout/install/exported source/private runtime).
Use that exact qualified source/privateASDF6 runtime for actual persistence of
ocam-linearity-samples-28h0jxnr into a fresh Pictures directory. Expected32products,
3200rows,1088records; actual persistence pending. Native/table evidence remains
frozen; no observations opened or image hashes/measurements/qualification repeated.

This receipt changes metadata only; no Mac fetch, rebuild or installation needed.
The conversion can run from the existing qualified copy, with normal checkout,
installed/source/runtime/native-evidence protections and a retained outer receipt.
No noise/covariance/interval/fit/correction choices. Preserve all evidence/runtime;
#236 stays open. See corrected-sample-asdf-2026-11-04.md. No merge/cleanup.

## All160 sites admitted; corrected-sample ASDF candidate — 4 November 2026

Owner's saved-table hash review confirms3200 admitted,0missing,160/160 sites,
100 samples perCCD. Rounded corrected-pixel coverage934.2..53381.5ADU (maxCCD86).
No fit/nonlinearity interval inferred. Do not repeat extraction/image hashes/Cgate.

New pycavi_sample_qc +persist-linearity-samples.py reuse unchanged common ASDF
factory/reader/traversal, freezing native text+typed rows+units/availability and
frame population, physical site/frame sources, sampling/configuration/provenance.
Import master QC graph semantically unchanged with accepted/rejected memberships.
34 records perCCD (expected1088total); originals not reopened or changed. Missing
None, negative signals preserved. Noise unavailable, covariance/fit interval/
coefficientsNone, fit not performed. No scientific weighting/model choices.

Agent5new ASDF metadata checks pass5.250s, FITS/network forbidden, including exact
roundtrip/relocation/master memberships and typed/unit/origin/noise/counter/cohort/
conflict/frozen-link refusals. ActualMac five-check gate pending via
qualify_sample_qc_mac.py; no old suite/native build/install. Actual ASDF sample
persistence pending after target gate; no plots/HTML/fit/correction/merge/cleanup.
See corrected-sample-asdf-2026-11-04.md. #236 open; approval to proceed persists.

## Actual all32 corrected singleton extraction complete — 4 November 2026

Actual Mac controller efebadf42bf6de6f03638ddb69af68254810ae97 completed at
Pictures/OCAM/wenu-imaging/ocam-linearity-samples-28h0jxnr. All32 detectors,
3200 site/frame rows, complete_for_owner_inspection. All8guards true: shared_images,
frozen_metadata, products, checkout, installed_files, native_source, qc_source,
private_qc_runtime. All53 selected image files verified before/after. New4metadata
controls passed0.016s,1ASDF admission fixture2.902s; all32 real master QC chains
verified with9/10 memberships retained for69/74/77/84/85 and10/10 for others.

Do not repeat extraction/qualification or raw FITS hashing without a new reason.
3200 is the retained row count, not a claim all observations were admitted. Next
read only saved native TSVs after checking their retained output hashes; summarize
admitted/missing sites and corrected signal coverage. Availability/coverage not
yet returned. Source/FITS arrays need not be reopened for that review. Native
transports still need final shared ASDF candidate publication. No noise/MC/fit
interval, weighting, fitted correction or calibration acceptance chosen. Preserve
all runs/builds/runtime; no install/merge/cleanup. #236 stays open. See
ocam-linearity-sample-batch-2026-11-04.md for receipt and provenance limits.

## Actual Mac singleton command passed; serial extraction ready — 4 November 2026

Actual f560d67 Mac C17 gate passed2/2 in8.28s at mac-sample-command-1iwkve9e:
new extraction6.67s, affected pair command1.60s. All3preservation guards true;
metadata singleton preparation succeeded. Do not repeat this native gate or rebuild.

New run_ocam_linearity_samples.py admits completed all32 masters/actual memberships,
shared ASDF frozen links/configuration/identity and original per-file flat/BPM maps.
Uses approved160 sites,20 original frames,32 serial qualified native commands.
Hashes53 selected images (20flats+BPM+32masters) once before/after the whole batch;
current full stat/hash equality and8outer preservation guards required. Original65
has no saved historical whole-FITS digest: verify approved path/HDU/semantic QC,
then establish a new explicit whole-file baseline; never claim historical bytes
verified from QC alone. Other31 masters compare saved full-byte hashes.

Agent4metadata controls0.006s plus1real-ASDF fixture1.662s pass; only these new
controls run onMac before extraction. Existing qualified C/QC modules unchanged.
Native100rows per detector preserve missing sites, exact physical coordinates and
original frame order. Native TSVs are intermediate, not final ASDF products.
Actual all32 extraction pending. No noise/MC/fit interval, coefficient acceptance,
weights, correction, plotting/HTML, install/merge/cleanup. See
ocam-linearity-sample-batch-2026-11-04.md. #236 open; sampling approval persists.

## Owner-approved 160-site pilot; extraction command candidate — 4 November 2026

Owner accepted the sampling proposal with “Yes, proceed.” Approved160 physical
sites are in omegacam-linearity-pilot-sites.json; review-only proposal stays as
history. Sampling only: no noise/MC/interval/fit/calibration choice inferred.
Metadata preparer validates profiles/identities/slot/readout-centre/raw crops and
writes32 five-singleton transports. Agent all32 preparation and4 changed-input
refusals passed; no FITS opened. Keep master accepted memberships9/10 or10/10.

New mefpp_sample_extract reuses unchanged bound-file/sample/scan/master kernels,
shared raw-selection parser, singleton ROIs and explicit active master/HDU. It
exports original-frame/site rows, missing as blank with not_admitted, frame
population diagnostics and noise unavailable. No raw-bias remeasurement, means,
pair averaging, hidden lamp/fit/noise policy. Full-finite API transport bounds
are not a science interval. Native transport completion is not an overall receipt.

Agent C17 command checks2/2 in1.03s; changed extension-master case recheck0.63s;
normal mefpp builds. ActualMac focused2-command gate pending via
qualify_sample_command_mac.py; compare unchanged kernels to passed aa5427c gate.
Do not rerun old noise/numerical matrices. Actual extraction controller, source/
master-lineage guards, final ASDF publication and real noise/correction fit still
pending; approval does not require another sampling question after qualification.
See linearity-singleton-extraction-2026-11-04.md. No install/merge/cleanup.

## All32 master signals complete; fit population choice pending — 4 November 2026

Actual remaining31 bias batch d84568b completed at
Pictures/OCAM/wenu-imaging/linearity-bias-batch-05ijf_sx; masters.json indexes32
signal candidates incl original65. Five controls pass; all8preservation guards true.
69/74/77/84/85 accepted9/10, others10/10 under unchanged legacy rule. Preserve each
accepted membership for conditional uncertainty; master variance still unavailable.
Do not rerun masters or qualifiers without relevant changes.

Next obstacle is the dense direct-pixel fitter's population size (~41.9M sites in
full5ROIs*32CCD). A review-only160-site proposal is prepared: one central physical
pixel per ROI,32detectors, at most3200 flat observations and225joint parameters
with ONE global shutter offset. Raw/active coordinates and reflection tie-break
are explicit and metadata-checked. NOT adopted or executed. Owner sampling choice
needed before extraction; never substitute ROI means or silently choose quiet
replacement pixels. See linearity-fit-sampling-proposal-2026-11-04.md and config/
characterization/omegacam-linearity-pilot-sites-proposal.json. Noise/distribution/
MC/fit interval options remain unselected; no identity weights to force a fit.
#236 open. Keep all existing data/runtime; no install/merge/cleanup.

## CCD65 bias pilot complete; remaining31 batch ready — 4 November 2026

Actual pilot c93dcd9 at linearity-bias-CCD65-epw82wy3 completed native FITS+ASDF,
10/10 accepted, all5preservation guards true. Raw mean274.0559..278.0642ADU becomes
corrected mean0.031444..0.084165ADU. This is not scan-estimator uncertainty or known
master variance. Preserve pilot and qualified022cf368 adapter/current shared QC.
Attachment155309 shows output pasted into Bash (command-not-found), not a second
bias recipe run; new guards check the actual retained state before processing.

Remaining31 serial controller reuses pilot recipe choices, independent header/HDU
maps and native geometry slots. Shared10bias+BPM full hashes once before/after
whole batch; original65 reused. Per-detector native/ASDF completions remain
provisional until outer batch source/product/preservation guards pass. Source
image hashes live in outer receipt; existing ASDF mapper fields remain unchanged.
Five new focused stdlib control checks pass and run onMac before processing;
no old numerical/ASDF matrix, build, install, plotting or HTML. Actual batch pending.
Successful masters.json indexes32 signal candidates and required outer receipt;
variance remains unavailable. Real noise model/corrected samples/curve fit still
pending. See ocam-linearity-bias-batch-2026-11-04.md. #236 open; no merge/cleanup.

## ROI review complete; real bias dependency pilot next — 4 November 2026

ASDF-only32 detector review completed at linearity-noise-review-ru0k1h1j, all5
guards true. Coverage extends to52529.9ADU (CCD85), not onlyCCD65's38574.9.
Targeted ROI review linearity-roi-review-nnvscgpb completed, all6guards true.
High ordinary RON is localized in75/82/86/96; MAD-RON2.09671 everywhere is a
quantized2ADU difference MAD, not proof of equal noise. No RON replacement,
auto-rejection, temporal-noise diagnosis or lamp normalization. Largest69/87/88
mismatches are2s;88 has5 saturated exclusions only in parallel_far/30s.

Next bounded dependency is a real CCD65 scan-corrected median-bias pilot from the
10 inventoried biases using the existing qualified022cf368 native bias adapter,
canonical PAF and explicit structural BPM1=good. Keep first2 RAW RON pair. Existing
scan/stack/rejection and high-sigma5 diagnostic settings unchanged. Controller
run_ocam_linearity_bias.py prepares new outputs/whole-file preservation guards;
current qualified shared ASDF backend, no plotting/HTML, rebuild or new test suite.
Pilot pending, master variance explicitly unavailable; no Gaussian/MC/fit interval
or coefficients selected. Inspect actual pilot before corrected-sample use. See
ocam-linearity-bias-pilot-2026-11-04.md. #236 open; no install/merge/cleanup.

## Actual Mac correction composition accepted — 4 November 2026

Source aa5427c actual Intel Mac C17 gate passed native_linearity_fit2.16s and
native_linearity_fit_allocation1.36s:2/2 in3.54s. Retain
/Users/fselman/Software/build/wenu-imaging/mac-linearity-fit-psb7nup5.
Checkout/installed_files/exported_source all preserved. Qualified unchanged
noise/joint/QR/optimizer kernels reused; normal mefpp built without installation.
Do not repeat this gate without relevant changes. This qualifies synthetic
correction-candidate composition only, not real fitted coefficients.

#236 stays open: connect bounded corrected physical samples, establish the real
noise model/scan-estimator/median-master covariance, and add recipe/ASDF candidate
publication. The supplied ASDF-only32-detector noise review has not yet returned;
request that evidence before silently choosing gain/fit range/distribution/pooling
or simulation parameters. No real fit, correction activation, accepted calibration,
installation, merge or cleanup. Keep plotting/HTML separate from recipe execution.
See linearity-correction-composition-2026-11-04.md and #236 receipt.

## Correction-producing linearity composition candidate — 4 November 2026

Owner says proceed with the pixel-response correction curve. #236 now adds an
in-memory C17 composition: explicit corrected direct pixels + justified supplied
noise -> QR-ordered measurements/factor -> joint global shutter profile -> owned
amplifier cubic inverse-response curves and conditional covariance. Preserve ONE
common delta, physical site/frame identities, actual coverage versus declared
interval, full cross-amplifier covariance and provenance. No ROI-as-pixel shortcut.
Missing noise/provenance/profile inputs fail; unavailable numerical gates expose
no curves. No noise distribution/gain/interval/MC defaults or science acceptance.

Agent two new C17 checks pass2/2 in0.78s; normal mefpp builds. They test known signed
offsets, distinct amplifier cubics, correlated noise/nonidentity QR order, owned
curve extraction, unavailability and both new allocation positions. Existing
qualified kernels unchanged and not retested. Actual Mac gate pending via
qualify_linearity_fit_mac.py, matching kernel bytes to passed c381168b noise gate.
No actual32-detector coefficients fitted, FITS recipe/publication or correction
activation yet; bounded/scalable corrected samples and established noise model
remain before real run. Plot/HTML stages remain separate; recipe navigation later.
See linearity-correction-composition-2026-11-04.md. No install/merge/cleanup.

## Project-local QC and independent presentation — owner decision, 4 November 2026

Owner says the HTML viewer looks good. Actual Mac viewer metadata gate aecce5c
passed7 checks in11.064s at mac-pair-qc-viewer-n3dsjk5f; all four protection guards
true. Real viewer visual feedback is positive; final generation receipt/guards
have not yet been pasted, so do not invent their status or close#235 on that basis.

Finish the linearity script before the next HTML navigation change. Then add a
left-edge recipe selector: bias, BPM, linearity, dark, dome flats, sky flats,
master flats, science, WCS, zero points, illumination; grow it as recipes develop.
Keep plotting/HTML generation an independent stage from recipe execution, reading
persisted shared ASDF QC. Regenerating a presentation must not rerun recipes or
pixel measurements. QC is per project initially; later add a reference QC database
through the data-source layer, retaining assessment identities/configuration/units/
stage/provenance. No database technology, reference-selection/threshold policy,
implementation of all recipes, file relocation or scientific defaults chosen.
See qc-mosaic-viewer-requirements-2026-11-04.md. This is a documentation-only decision;
no repeat qualification, install, merge, cleanup or source sync on Mac is needed.

## All32 OCAM complete; offline QC mosaic candidate — 4 November 2026

Actual Mac batch ef4d1e2d at Pictures/OCAM/wenu-imaging/ocam-raw-pairs-serial-nx_j6g1j/batch
completed31 native/ASDF/plot detectors; CCD65 reused. Status complete_for_owner_inspection,
source_preservation true, two shared hash passes/image, error null. Outer checkout,
installed/exported/private-runtime/reference protections all true. #234 closed.
No rerun needed. Keep batch, reference65, BPMs, builds and private QC environment.

#235 implements offline geometry-driven ASDF QC HTML: gain/variance mosaic tiles,
click/keyboard detector selection, enlarged plot/ROI toggles, full point values,
counts/availability/raw RON/provenance and maintained footprint SVG. Reads validated
ASDF and small receipts/TOMLs only; no raw FITS/native TSV open, estimator or fit.
Seven new agent metadata controls pass8.661s; JS syntax passes. Agent Chromium launch
blocked by local socket permission, so browser interaction/rendering is pending,
not passed. Actual Mac focused metadata gate via qualify_pair_viewer_mac.py then
real HTML generation/visual inspection pending. Reuse unchanged ASDF/native gates;
no installation, rebuild, scientific default, merge or cleanup. See
qc-mosaic-viewer-2026-11-04.md; PR227 remains draft.

## Remaining OCAM serial batch candidate — 4 November 2026

Owner says proceed after completed CCD65 ASDF/plots. Issue#234 tracks remaining31.
New one-use batch prepares identity-mapped selections/geometry ROIs, reuses CCD65,
and runs qualified native512092fa serially. Hash23 common image files once before
and once after the whole native interval, matching frozen CCD65 hashes. Pending
native receipts cannot publish ASDF before shared verification. Then unchanged
common ASDF bridge/plotter preserve full precision per detector. Stop first failure;
retain truthful failed/pending evidence, never auto-resume or overwrite.

Twelve agent orchestration controls pass in5.262s, including all31 metadata-only
preparation, independent mappings, shared hash counts, failures/source changes,
one-use execution and genuine ASDF publication from supplied transports. These
are not numerical/actual Mac acceptance. Actual Mac focused qualification pending
via qualify_ocam_pair_batch_mac.py; reuse prior21 ASDF/plot gates only after exact
module identity/package-version comparison with passed mac-pair-asdf-i7rw5asm.
No native rebuild, observation access, dependency installation or old matrix.
After Mac gate inspect real prepare-only31 manifest, then execute same approved
science choices without repeat approval. Real batch not run. PR227 stays draft;
no fit/merge/install/cleanup. Keep prior runs/BPMs/private runtime. Geometry HTML
mosaic follows detector-wide data. See ocam-serial-pair-batch-2026-11-04.md.

## Actual Mac ASDF persistence and plots completed — 4 November 2026

Actual source9f5a35fd qualification passed12 shared-QC checks in1.648s and9 pair/
plot checks in18.061s. Retain /Users/fselman/Software/build/wenu-imaging/mac-pair-asdf-i7rw5asm;
checkout/installed/exported source/private QC runtime all preserved. No rerun needed.

Real postprocessing retained at
/Users/fselman/Pictures/OCAM/wenu-imaging/ccd65-pair-qc-2bz8baok:
complete_for_owner_inspection,25 ASDF records, exact roundtrip, metadata preserved,
50 pairs rows and5 bias-RON rows. Both plots regenerated from saved full-precision
ASDF only. No raw FITS opened/pixels remeasured. Final outer guards all true:
checkout,installed_files,exported_source,private_qc_runtime,native_evidence.
Serializer9f5a35fd/native512092fa remain distinct. Canonical saved measurements:
asdf/records/pairs.asdf digest
b69f0a0eaacccb4680de74c207e215c413c313e76a28fd423ec792248c786bb2;
asdf/records/bias-ron.asdf digest
6a4e5320b5439626241353918cd949be0a4c0a96286c0173ae8d1d1a4cfe73de.
These are semantic QC digests, not whole-file hashes. Retain both ASDF/plot trees
and original native transport/evidence; common QC1.1/file ASDF1.6 is qualified.
#233 closed for bounded persistence/roundtrip/plot acceptance. PR227 stays draft.

Next prepare remaining31-detector serial orchestration, reusing inspected CCD65
and qualified512092fa native command, hashing shared input set once per batch
(before/after, not32 full passes). Persist each detector through qualified shared
ASDF and derive plots from saved records. The planned geometry-driven HTML mosaic
comes after detector-wide data. No batch has run yet; no scientific fit/gain
interval/noise/covariance policy is selected. Higher-signal sequence search is
deferred. Keep original BPM, structural copy, failed runs and needed runtimes.
No installation, merge or cleanup. Receipt-only documentation needs no user-host
source sync or repeated tests. See raw-pair-asdf-2026-11-04.md.

## Raw-pair ASDF persistence and future mosaic viewer — 4 November 2026

Owner instructed proceeding with ASDF persistence of the already-completed CCD65
run before expanding to remaining detectors. Preserve full native precision; do not
repeat pixel measurements. Shared QC1.1 extends only tabular product identity:
explicit table_name selectors for TSV products, real hdu_index for FITS; no fictitious
HDU. Existing QC1.0 FITS records remain readable; the1.0 schema resource stays intact.
Use common QcRecipe/write_record/read_record/traverse_records for all records.
New raw-pair adapter freezes native tables/units/availability/origins/settings,
receipt/configuration and explicit structural-BPM lineage, publishes per-input
binding records plus pairs.asdf/bias-ron.asdf, and verifies exact roundtrip.
No per-frame statistics or accepted gain is invented from pair measurements.

Agent metadata checks pass12 shared+9 pair/plot controls; existing tiny native TSV
outputs also parse without rerunning native code. Actual Mac gate pending via
qualify_pair_qc_mac.py, using retained private ASDF6 runtime and protected normal
imaging Python. No installation, upgrade, native build or old numerical matrix.
After inspected Mac gate, persist existing ccd65-raw-pairs-bpmfixed-zfs377ok tables
and regenerate both plots from ASDF only in a fresh Pictures purpose directory.
Do not use rounded chat values for authoritative plots. No raw FITS reread.

Owner requests eventual HTML QC mosaic based on the maintained geometry viewer:
choose gain/variance on mosaic tiles, click detector for enlarged selectable-ROI
plots, read full-precision ASDF and show availability/exclusions/provenance. Record
requirements now; implement after detector-wide data. HTML is the initial format;
revisit only as needs develop. Higher-illumination sequence search/near-saturation
characterization and gain/shutter fitting remain deferred. Existing five CCD65
windows reach only~39kADU mean signal. No all31-detector run, fit, merge or cleanup
is launched by this persistence increment. See raw-pair-asdf-2026-11-04.md and
qc-mosaic-viewer-requirements-2026-11-04.md in docs/developer.

## CCD65 real measurements completed — 4 November 2026

First actual raw-pair run succeeded with qualified native512092fa and the explicit
verified structural BPM copy. Retain
/Users/fselman/Pictures/OCAM/wenu-imaging/ccd65-raw-pairs-bpmfixed-zfs377ok.
execution.json: complete_for_owner_inspection, native exit0,1 detector,5 ROIs,
50 pair rows,5 bias-RON rows; final30 source fingerprints unchanged. Outer
checkout/installed/exported source all preserved. Owner verified full pair-table
output hash in a subsequent read-only report. No rerun required.

All50 rows have arithmetic_available gain, no nonfinite/saturation exclusions,
and constant per-ROI populations:262144 except parallel_far262141/far_corner262143.
Raw bias RON ADU: near1.974218,serial_far1.971490,parallel_far2.028334,
far_corner2.228890,center2.147637. Raw bias differences have median-4ADU;
MAD-based RON2.096713ADU throughout. These are diagnostics, not accepted gain.
Point gains trend upward with signal: five-ROI ranges5s2.298-2.312,20s2.317-2.335,
40s2.348-2.376,70s2.410-2.425e/ADU. Near-readout gain increases4.90% from5s to70s;
S/t increases1.14% from2s to70s. These do not identify a unique response/shutter/
illumination cause. No fitting interval/noise/covariance policy is selected.

Actual Mac structural-copy helper passed7 tests in0.382s;64 cards added across32
CCDs, all existing cards and stored payload preserved. Retain
Pictures/OCAM/wenu-imaging/legacy-bpm-structure-b1h9egzp while measurements reference
it. Original SHA d7aeb7d6041fd2e03d48785298b338ba61860e145a08a4aeb29e0fc9b5a13532;
copy a22a6b8f478feb43f541f972a1567de962652c916d823eef68be1354e472de7a.
#231/#232 are target-verified and closed; PR227 remains draft/unmerged. Keep original
BPM,both failed attempts and retained qualification builds. Approved bias/saturation/
polarity choices remain settled. Next discuss detector-wide measurements and the
response-dependent gain before choosing fit policies. No automatic31-detector run,
fit, installation, merge or cleanup. See ocam-ccd65-first-measurements-2026-11-04.md.

## Legacy OCAM BPM structural-copy preparation — 4 November 2026

Actual Mac #231 repair qualification at512092fa passed native_pair_command/native_layout
2/2 in5.56s, retained mac-extname-binding-it2gdv4q; checkout/install/export all preserved.
Real retry retained Pictures/OCAM/wenu-imaging/ccd65-raw-pairs-extname-w5wjs5pr:
all flat/bias bindings pass, BPM discovery fails before pixel loads. All three
outer preservation checks pass; final runner source checking was not reached.
Owner supplied read-only33-HDU BPM header receipt: empty primary,32 BITPIX8
2044x4091 IMAGE extensions with exact identities but missing PCOUNT/GCOUNT.
Strict rejection is correct; track legacy malformed input separately as #232.

Prepare an explicit derivative with missing PCOUNT=0/GCOUNT=1 only, using
prepare-legacy-bpm-copy.py. Keep global native validation unchanged and source
BPM untouched. It streams original stored data/padding, verifies every existing
header card and data byte, source hash against the failed run's frozen fingerprint,
and full source preservation. Seven agent synthetic checks pass in0.166s; actual
Mac preparation remains pending. No native rebuild or old numerical gate replay.
Then inspect preparation receipt before deriving a selection referencing the copy
and retrying CCD65. Approved biases,65534 ADU boundary and BPM1=good remain settled.
Keep both failed real attempts and original BPM; no fit/install/merge/cleanup.
See docs/developer/ocam-legacy-bpm-copy-2026-11-04.md.

## CCD65 first real attempt and EXTNAME repair — 4 November 2026

Owner explicitly approved both proposed raw biases, exclusion >=65534 ADU and
legacy binary BPM 1=good. Do not request these choices again. Initial cross-session
stat admission stopped before output creation because all 31 device numbers changed
16777222 -> 16777223; inode/size/mtime_ns/mode all matched. The corrected launch
records that exact transition without rewriting the earlier review and establishes
fresh full runner fingerprints.

Actual Mac attempt retained at
/Users/fselman/Pictures/OCAM/wenu-imaging/ccd65-raw-pairs-p0sxrc40/measurement:
failed, native exit1, first flat binding, no completed tables. Checkout and installed
files preserved; runner final source-preservation check was not reached. Source
tracing confirms #231: identity_key=EXTNAME was rejected as a duplicate configured
selector before pixel loads. NULL-free messages are separate cleanup diagnostics.

Bounded #231 repair supports one EXTNAME card in both extname/identity fields,
retains duplicate-physical-card rejection and all other mapping checks, and reports
layout error detail. New synthetic native layout and OCAM-style command regressions
both fail before and pass after repair (agent C17 2/2,1.04s). Exact table equality,
unsigned scaling, absent-BUNIT ADU fallback, HIERARCH selectors, identity mismatch,
duplicate card and immutable fixtures are checked. Actual Mac repair gate pending:
qualify_pair_command_mac.py --layout-alias; builds command/layout_probe, runs only
native_layout/native_pair_command. Preserve old build and failed run; no raw-data
retry until this gate is inspected. No install, fit, merge or cleanup.
See docs/developer/ocam-extname-binding-repair-2026-11-04.md.

## Branch closeout: build-directory review — owner instruction, 3 November 2026


## Resume checkpoint — end of 3 November 2026

Owner stops for tonight and asks for cross-chat continuity. Resume wenu-imaging
from this checkpoint and docs/developer/detector-characterization-handoff-2026-11-03.md.
The companion resume artifact is wenu-imaging-resume-2026-11-03.txt. Do not mix
this work with fselman/wenu charts/catalogues or the Raspberry Pi chat.

Actual Mac C17 command/runner gate passed at 6e75a7bf322583e0aeaca50e1ff786b70cd259f3:
pair_runner_orchestration/native_pair_command 2/2 in 3.04 s, retained
/Users/fselman/Software/build/wenu-imaging/mac-pair-command-mv3iAx5L.
All checkout/installed_files/exported_source preservation checks true.
Protected Mac checkout remains clean main c73d9a9e3a631fbbb2346beaa3c150c110a60343.

Corrected exact-byte PAF fingerprint at 8736e16: canonical OCAM PAF SHA256 is
709d65acdeea6c889ed1468cbb3966d5de93ec654ee030032a096ca12624333f.
An earlier local copy omitted three final-comment trailing spaces; no parameter
difference. Strict hash checking remains. Use corrected processing TOML with
unchanged qualified native code; do not rebuild/replay passed gates just for this.

Owner-returned real saved-header review passed: 30 files x 32 outputs, unchanged
source stat identities, BITPIX16/BSCALE1/BZERO32768/BUNIT absent. Retained
/Users/fselman/Pictures/OCAM/wenu-imaging/first-pair-review-So47zUsK.
Its selection-proposed.toml targets ESO_CCD_#65/L, five ROIs, 50 pair rows,
206467604 loaded pixels. No real pixel measurement or fit has run.

Three scientific choices were explicitly requested but remain unanswered:
first two biases (2017-03-13 09:50:05.624 and 09:50:48.373), raw exclusion
at/above65534 ADU, legacy binary BPM 1=good. Resolve that pending choice once;
do not infer approval from the successful metadata receipt or tonight's save.
After agreement, reuse the qualified retained command and current corrected
configuration to prepare/execute the first detector under Pictures/OCAM/wenu-imaging,
preserving original files and all ten nonconsecutive flat pairs in acquisition
order. No lamp normalization, median-zeroing, fitting, gain interval selection
or estimated covariance is part of this first raw measurement.

Maintain footprint viewer with TOML changes. Real comparison products belong in
purpose-named Pictures/OCAM/wenu-imaging or Pictures/WFI/wenu-imaging directories
with purpose/deletion README. At branch merge/cleanup, review build directories
and reasons/disposition with owner; protect needed runtimes and comparison data.
Do not merge or delete branches/builds merely to save this checkpoint. Existing
draft PR #227 and branch docs/bpm-linearity-pairs-20261103 remain open.

## Detector footprint viewer maintenance — owner direction, 3 November 2026

Fernando inspected both generated Mac mosaics from source 50e52a9055fb1a761119abf529433a32dc2816dc and reports that both look OK. Review outputs:
- OCAM: /Users/fselman/Pictures/OCAM/wenu-imaging/detector-geometry-review-iE8SBsHq/footprints.html
- WFI: /Users/fselman/Pictures/WFI/wenu-imaging/detector-geometry-review-5qloSBd2/footprints.html

Maintain tools/detector-footprint.py and tools/view-detector-footprints.sh as the detector and processing TOMLs evolve. Any change to their schemas, geometry, detector/output identities, scan/crop/ROI coordinates or configuration composition must update the viewer and affected regression checks in the same change. Keep the diagrams driven by the configuration used for inspection; do not let separate hard-coded geometry or a stale visualization-only schema drift from future authoritative TOMLs. When production TOML schemas/readers replace these reference schemas, adapt or share their interpretation and retire duplicated profiles. Preserve explicit coordinate systems, nominal illuminated versus retained areas, scan bands versus selected samples, mosaic placement and schematic amplifier-marker semantics. Regenerate affected views and record visual review when geometry changes. This acceptance confirms the displayed layout; it does not authorize numerical reduction or scientifically validate candidate ROIs. See docs/developer/detector-footprint-viewer-2026-11-03.md.


Whenever work is finished by merging and cleaning a branch that created build
directories, review those directories with Fernando as part of that closeout.
Do not leave the review for an unspecified later cleanup.

- Identify each build directory created by the branch and its disk usage.
- Propose whether it can be erased. For every directory that must be kept,
  explain the specific reason: required runtime dependency, unfinished validation,
  unique evidence or another concrete continuing need. State when that reason
  will cease to apply and the directory can be erased.
- Data needed for future comparison must first be placed in an appropriately
  named subdirectory of ~/Pictures/OCAM/wenu-imaging or
  ~/Pictures/WFI/wenu-imaging. Each dataset subdirectory must contain a README.md
  explaining why the data is needed and when it can be erased. Update active
  references and record the new locations.
- Present the concrete retention/deletion proposal for review together, then
  perform the agreed cleanup and record its outcome. Do not assume that branch
  deletion also settles retention of its build directories.
- State any remaining retained directories and reasons in the final handoff.
  Never retain an entire large build tree solely because it once held comparison
  data or because cleanup was not considered.

This is a closeout/retention requirement, not a requirement to rerun tests.
Existing required engines/environments must remain usable until their actual
dependencies have been resolved.

## Mac optimizer accepted; direct-pixel joint candidate - 3 November 2026

Actual Mac beee7c0d passed native_simplex/native_simplex_allocation 2/2 in 1.79 s
at /Users/fselman/Software/build/wenu-imaging/mac-simplex-ddM35GKJ. All three
preservation checks passed; clean main c73d9a9e remains unchanged.
Owner authorized the joint wrapper next. First increment fits compact DIRECT
PIXEL samples only: one common signed all-detector delta, per-pixel illumination
rates, amplifier cubics, supplied fixed covariance, analytic derivatives,
multiple declared starts and qualified Eclipse optimizer/QR. Candidate status is
NOT science acceptance. No unvalidated ROI-mean substitution, new lamp factor,
BPM classification, fit-range default or production publication.
Agent C17 two new controls pass 2/2 in 0.62 s; all 47 single/persistent allocation
positions preserve qfits owners. Normal mefpp builds. #229 corrects only the
rank-isolation test fixture; keep open until actual Mac gate. Actual Mac joint
candidate gate pending: qualify_detector_joint_mac.py. Profiles, instrument
coverage acceptance, validated aggregation/covariance preparation and scalable
measurement/recipe integration remain next. No unchanged helper replay or
observations/install/merge/cleanup.
See [candidate record](detector-joint-candidate-2026-11-03.md).

## Mac QR accepted; checked optimizer candidate - 3 November 2026

Actual Mac b382a93e passed native_matrix_qr/native_matrix_qr_allocation 2/2 in
1.69 s at /Users/fselman/Software/build/wenu-imaging/mac-matrix-qr-Ay1wSJZe.
All three preservation checks passed and main remains clean at c73d9a9e.
Owner authorized the reviewed checked optimizer next. minimize_checked extends
Eclipse optimization with context/validity/bounds/scaling, exact attempt budget,
both spread tests and owned results; qualified QR checks initial simplex rank.
Legacy minimize/min_test unchanged. Agent C17 two focused checks pass 2/2 in
0.14 s, all 19 single/persistent allocation positions and hard callback cleanup;
normal mefpp builds. Actual Mac optimizer gate pending: qualify_simplex_mac.py.
No unchanged QR/gain replay or observations/install/merge/cleanup. Joint detector
wrapper/common signed all-detector shutter/covariance inputs remain later work.
See [optimizer record](simplex-implementation-2026-11-03.md).

## Checked QR candidate - 3 November 2026

Owner authorized proceeding after all-detector shared shutter and teaching review
at 1b1823bf. First implementation is matrix_leastsq_qr_checked in Eclipse matrix:
pivoted Householder QR, explicit scaling/rank/condition, immutable inputs and
owned diagnostic result. Legacy least-squares/API/allocation paths preserved.
Agent C17 two focused controls pass 2/2 in 0.04 s; ten single/persistent allocation
failure positions preserve qfits owners. Normal mefpp builds. Actual Mac QR gate
is pending; use qualify_matrix_qr_mac.py, protecting clean main/install/export.
No unchanged gain/RON replay. Checked optimizer and joint detector wrapper remain
later reviewed increments; no real-data processing/install/merge/cleanup.
See [QR implementation](matrix-qr-implementation-2026-11-03.md).

## Mac paired gain/RON accepted; joint interface review - 3 November 2026

Actual Mac e0b16476 passed2/2 C17 controls in 2.58 s at
/Users/fselman/Software/build/wenu-imaging/mac-gain-pair-AdGQvwqZ,
with checkout/installed_files/exported_source preserved. Test-only oracle#228
is accepted/closed. No unchanged test replay or real-data claim.
Owner requests the joint shutter/linearity numerical interface review next.
The source-grounded PDF/LaTeX proposal extends Eclipse optimization/matrix
modules for checked bounded simplex and rank-aware pivoted QR, then a detector
wrapper using one signed mosaic offset and amplifier curves. These additions
are proposed BEFORE implementation; no new numerical source in this increment.
ROI aggregation and covariance inputs remain explicit prerequisites.
See [review](joint-shutter-linearity-interface-2026-11-03.md).

## Paired gain/RON implementation candidate - 3 November 2026

Owner reviewed the formula/PDF clarification and authorized implementation.
Eclipse detector_gain_pair_checked composes existing masked/pair statistics over
one common finite population. Raw active crops, no scan correction; explicit
unavailability/error/alias guards, immutable inputs and no silent gain interval.
Agent C17 two new controls pass2/2 in0.11s, including40 single/persistent allocation
failure positions and existing operation-template pairing. Test oracle#228 was
corrected; actual Mac C17 gate is next and pending. Use normal imaging Python
with qualify_gain_pair_mac.py, protecting clean accepted main/install/export;
no unchanged replay, real data, production activation or merge. Joint linearity/
shared shutter and per-pixel flagging remain subsequent work. See
[implementation record](gain-pair-implementation-2026-11-03.md).

# wenu-imaging agent instructions

## End-of-day WFI bias handoff — 2 November 2026

Owner visually reviewed the eight-detector WFI master as OK. Actual Mac mosaic
run `/Users/fselman/Software/build/wenu-imaging/wfi-bias-mosaic-IkxQQ7Uz`
completed seven new detector operations, reused inspected CHIP1, verified lossless
assembly/common ASDF links and all four preservation controls. Main remains
clean at47123ee. Chapman BPM e6f70e1 passed12/12 in72.12s (earlier pending notes
below are historical). New BPM software is qualified, but real WFI BPM has not run.

**Next session starts by reviewing the ESO WFI Manual and published detector
behaviour**, using documentation appropriate to these2003 observations/readout.
Do not start QC investigation, visualization or new processing before that review.
CHIP7 RON30.1997 vs MAD3.1451 and large master dispersions, especially CHIP6,
are retained observations, not diagnosed faults or accepted detector properties.
QC work is deferred; follow the owner's sequencing.

Historical overscan reconciliation is issue#226, linked to completed#121:
all ten old medians match the erroneous22-sample sum divided by23. Keep the
corrected23-sample mean and preserve old products. No more investigation required
for this comparison now. DS9 helper is `tools/ds9-mosaic.sh FILE.fits`.
Owner authorized merge/cleanup. PR#209 merged at8846bbae; PR#225 was retargeted
to main and merged ate0a236cc. Verified final BPM head0441a792 is an ancestor of
main, with no file differences. Branch deletion and host synchronization are
being handed off through exact-tip guarded shell commands (connector has no
branch-deletion capability). Preserve all retained products/environments.
No installation/production activation or full science reduction is authorized.
Full handoff: [2 November handoff](handoff-2026-11-02.md).


## Chapman BPM preflight stopped on changed QC; corrected gate - 2 November 2026

Owner returned b6b5fea early stop at Shared QC changed in
/home1/fselman/Software/build/wenu-imaging/chapman-bpm-complete-h64m4l9x.
No export/build/tests/install ran; no formal final preservation receipt exists.
Retain the failed attempt. Review against actual prior4417d7d shows schema
unchanged, but common QC gained owned extensions/bias-MAD metrics and tests gained
extension lifecycle checks. Those sources are already Mac-qualified022cf368.
The earlier runner incorrectly treated old QC acceptance as reusable unchanged.

Corrected runner verifies old export against its own Git source, records old/new
QC digests, and runs current shared_qc_asdf (ten checks) alongside the eleven
changed-code native/BPM entries: expected12/12. Dependency environment/external
library evidence stays reused; no Conda/install/C interchange replay. Four guard
controls plus ten current agent QC checks pass; actual Chapman retry pending.
Native/build/QC sources remain identical to Mac022cf368, so no new Mac replay.
Same seven preservation controls and protected07d2733 checkout; fresh run only.
See [corrected Chapman gate](bpm-chapman-qualification-2026-11-02.md).


## Actual Mac BPM completion passed; Chapman changed-code gate next - 2 November 2026

Fernando returned actual 022cf3683fe47d4de6a7acac1e3799cb49201d40 Mac success:
native_bias_files/native_bpm_completion 2/2 in18.63s, retained
/Users/fselman/Software/build/wenu-imaging/mac-bpm-complete-Ia5qliwa.
All four preservation checks passed; main clean. He authorizes proceeding to
Chapman validation before actual WFI/OmegaCAM data.

qualify_bpm_chapman.py exports exact fetched BPM source while preserving known
clean Chapman bias checkout07d27330555712ef6bf59a068a578b450e89b4a3. It verifies
native/build/QC tree identity against the Mac-qualified022cf368 source, uses the
selected GCC10/C17/tools and retained ASDF Python, then runs eleven changed-code
measurement/bias/BPM/layout/publication/completion contracts. Reuse prior passed
Chapman dependency/QC evidence; no Conda, shared10/C-interchange replay, tool
rediscovery, source change, install/activation, merge or real data yet. Protect
checkout/installed files/packages/private Python/external prefix/export/old receipt.
Only runner/docs change, so no unchanged Mac replay. Actual Chapman gate pending.
See [Chapman BPM gate](bpm-chapman-qualification-2026-11-02.md).


## Actual Mac publication passed; complete BPM command candidate - 2 November 2026

Fernando returned 00ee1491930ec8d77968cb4b137c48ac60ce0502 Mac C17 success:
service/files/publication 3/3 in 20.81 s, retained
/Users/fselman/Software/build/wenu-imaging/mac-bpm-publication-Ev9dMXuD.
All four preservation checks passed; protected main stayed clean.

Next candidate connects cal bpm to the existing mefpp_m5 command entry and common
ASDF completion wrapper. Explicit per-flat path/HDU/pair TSV, selected active
master bias, optional encoded prior, active ROIs and caller thresholds; no new
numerical algorithm/default. Zero success only after FITS, common ASDF and frozen
links verify; failures retain truthful execution receipts/completed artifacts.
Primary BPM remains unsigned 8-bit; binary priors require NEW mode and retain
separate selection. --bpm-complete uses retained qualified QC Python, rebuilding
mefpp_m5/mefpp and running only complete BPM plus affected bias command contracts.
Earlier response/service/file/publication gates remain retained. Mac command gate
pending, then changed-code Chapman qualification before actual WFI/OmegaCAM data.
No install/activation/merge. Full gain/RON/linearity/shared signed shutter remains
pending. See [command completion](bpm-command-completion-2026-11-02.md).


## Actual Mac file input passed; publication candidate next - 2 November 2026

Fernando returned 328c50ef518c76a66791f0a398321848b84413aa Mac C17 success:
native_bpm_service/native_bpm_files, 8.07 s total. Retained
/Users/fselman/Software/build/wenu-imaging/mac-bpm-files-sEzWKwiU.
Installed files, checkout and exported source all preserved; main stayed clean.

Next candidate adds checked integer-HDU output in Eclipse (existing qfits integer
conversion), exclusive native BPM publication and pycavi_bpm_qc using the common
unchanged QcRecipe/schema/ASDF writer. Primary reasons remain unsigned 8-bit;
coverage, sample counts and prior information are distinct extensions. Explicit
NEW/COMBINED modes: combined legacy binary reasons are unavailable, never
invented. Full HIERARCH spellings; no Phase3 assertion. Result now owns its exact
configuration snapshot for publication after context destruction. --bpm-publish
requires the retained qualified ASDF Python and checks its preservation, running
new publication plus affected file/service contracts only. CLI/whole-command
completion and joint linearity/shutter/gain/RON remain later. Validate on Chapman
before actual WFI/OmegaCAM data. No install/merge; see [publication record](bpm-publication-2026-11-02.md).


## Actual Mac service passed; bound BPM inputs next - 2 November 2026

Fernando returned the pinned 970bdfb9ad232df353aab18c7a1cd2f0957c737e Mac
service gate: native_operation_template/native_bpm_service both passed (1.72 s).
Retained /Users/fselman/Software/build/wenu-imaging/mac-bpm-service-AUUCnlyT;
installed_files/checkout/exported_source all true; clean main unchanged.

Next candidate adds mef_bpm_from_files: explicit bound paths/HDUs/configuration,
header exposure key/HDU, pair IDs, prior encoding/coordinates, physical raw ADU
saturation and caller-selected margin/span/pair thresholds. Saturated or otherwise
reference-empty frames are now explicitly excluded with original-index mapping;
per-pixel coverage stays separate from 8-bit reason flags. Quick admission needs
five usable pairs at five times and five measured paired levels. No automatic
threshold defaults, time normalization or changed fitter. The service changed
for sample cuts: --bpm-files runs file admission and affected service only.
Publication, CLI/common ASDF completion, gain/RON and joint linearity/shutter are
still next. Mac preparation/quick gate, then changed-code Chapman validation and
actual data tests; no install/merge. See [file record](bpm-file-input-2026-11-02.md).


## Typed BPM service candidate; Mac core accepted - 2 November 2026

Fernando returned the pinned 14e9bb68ffe58f765576413063e0c99a6cfb311e
Mac response gate: native_measurement_stats and native_bpm_response both passed
(4.22 s). Retained /Users/fselman/Software/build/wenu-imaging/mac-bpm-response-rMPj2sY4;
installed_files/checkout/exported_source all true; checkout remains clean main.
This is actual Mac core evidence, not full BPM recipe/scientific acceptance.

Next candidate adds the typed in-memory mef_cal_bpm service using the shared
operation template, configured scan/crop, selected active master bias and the
unchanged response core. Explicit binary/reason priors; byte reasons preserved;
coverage separate. No detector BPM touches electronic scans. No scan mode uses
existing crop only. Acquisition pairing/saturation admission, file CLI, ASDF
publication, gain/RON and joint shutter/linearity remain later increments.
Run only --bpm-service's new service and operation-template Mac contracts; do
not replay unchanged response/measurement or old ASDF gates. Validate changed
code on Chapman before full real WFI/OmegaCAM tests there. No install/merge.
See [service record](bpm-service-2026-11-02.md).


## Detector-characterization implementation authorized - 2 November 2026

Fernando requests proceeding after reviewing the formula design. The current
specification is [design PDF](detector-characterization-design-2026-11-02.pdf)
and its matching [LaTeX source](detector-characterization-design-2026-11-02.tex).
It supersedes the earlier BPM v1.0 proposal where they differ. Keep BPM unsigned
8-bit (0=no detected reasons, nonzero bitwise reasons), separate coverage and
legacy Eclipse 1=good selection. First develop the reusable quick-BPM core;
full linearity uses one signed mosaic shutter duration offset, not free per-chip
intercepts. CMOS initially uses the same mechanism; specialized CMOS timing waits
for full characterization data. Development/quick C17 tests: Mac; validate changes
on Chapman before full actual WFI/OmegaCAM data tests there. Agent synthetic checks
are preparation evidence, not either target acceptance. No installation/merge.
Announce checked Eclipse interface additions before implementing; preserve legacy
fitters, diagnostic units, medians and mask semantics. Previous scope entries below
are historical, including the earlier design-only hold and Mac-only test scope.


## BPM design review only — 2 November 2026

Owner requests designing the new BPM recipe from existing mef_build_bpm, using
the completed bias template, then reviewing the final design before implementation.
See [BPM design v1.0](bpm-recipe-design-2026-11-02.md). Proposed mask/
bias/admission choices and checked Eclipse extensions are not yet accepted.
No new BPM source, numerical routine, test run, install or activation in this
increment. Bias qualification is retained. #224 records the robust/proportional
fit-diagnostic documentation/units mismatch; do not silently change the fitter.


## Finish bias first, then create BPM — 2 November 2026

Owner clarification: bias is the only new recipe implemented. The new BPM recipe
is still TBD; it must follow the template after bias completion. Do not treat
other new recipes or a two-pass bias/BPM workflow as already implemented.

Actual Mac eeacca3 qualification passed6/6 C17/native-ASDF contracts in22.31s,
retained mac-bpm-asdf-TGJPe5t1, with installed/checkout/source/QC controls preserved.
Active-only detector BPM policy is qualified; electronic scan BPM is not
applicable. Existing scan rejection remains independent of detector masks.

The final bias completion command now chains the existing native operation and
shared ASDF writer, verifies frozen references and reports success only for the
whole operation. Native source and C17 binaries are unchanged. Six agent completion
cases and seven reuse guards also passed the actual Mac completion gate at
ce36197, retained mac-bias-complete-x0Z4JupT; all five protections passed. Reuse verified eeacca3 native evidence/binary; do not rebuild or replay
the six unchanged contracts. See [bias completion](bias-recipe-completion-2026-11-02.md).
After that gate, continue the new BPM contract/source review following the same
template. No unreviewed estimator/threshold, new BPM generation, two-pass workflow,
production activation, merge or installation is part of current bias closure.

## HIERARCH dispatch boundary, 2 November 2026

Use explicit full `HIERARCH ESO ...` names at the qfits boundary. Astropy's
stripped `ESO ...` names are not interchangeable: bundled qfits can accept one
in memory but silently truncate it on output (#223). Dotted shortFITS omits the
ESO prefix (`DPR.CATG`, not `ESO.DPR.CATG`); prefix findmatch does not expand it.
Keep PAF keys separate. See [the source/probe review](hierarch-keyword-review-2026-11-02.md).
The fixture now requests HIERARCH explicitly; all17 FITS files are byte-identical
with no conversion warnings. Native source is unchanged. #125 long-string safety
remains separate; no native library fix or target replay is implied.

## Eclipse reuse and reviewed extensions

Owner instruction, 2 November 2026: use the existing Eclipse resources whenever
suitable, across all recipes and processing measurements/checks.

1. Before implementing functionality, inspect the relevant Eclipse modules,
   public headers, documentation and existing callers/tests. Check actual
   semantics, including estimator, BPM polarity, region coordinates, units,
   numeric types, mutation and ownership; a similar name is not sufficient.
2. Reuse a suitable routine, or compose existing primitives, before adding code.
   Do not duplicate library functionality inside recipes, Python helpers or
   serializers merely for convenience.
3. If functionality is genuinely missing, describe the gap, existing alternatives,
   proposed interface, callers and edge/error behavior to Fernando for review
   BEFORE implementation. Announce every proposed new routine beforehand;
   extend Eclipse only within the reviewed scope.
4. Put general-purpose extensions in the appropriate Eclipse module so other
   recipes can reuse them. Inspect the maths modules and reuse their scaffolding.
   Follow the current library's data structures, signatures, allocation/free
   conventions, error reporting, documentation and build organization.
5. Preserve existing APIs and behavior unless a change has been explicitly
   reviewed. Update matching public headers, documentation and build lists as
   applicable. Add independent known-answer/error checks for new behavior and
   affected callers using the current selected tools/test policy.
6. Keep measurement algorithms separate from recipe orchestration and ASDF
   serialization. Reuse BPM-aware routines when available; a new estimator must
   support the reviewed sample/region/mask contract rather than introduce a
   competing recipe-specific implementation.

2 November owner QC decisions and reuse policy: RON must use two RAW bias
frames, with NO overscan correction before subtraction, to avoid correction-
induced correlations. Keep ADU units and explicit origins/stage/region. Approved
QC stages: active area before correction, after overscan/trimming, and master.
Approved estimators: mean+median, sample stdev (N-1), 1.4826*MAD, valid/excluded
counts and no implicit clipping. High-offset master pixels use configurable
k=5 initially; save threshold/count/locations without automatic masking.
Before any new numerical implementation, inspect existing Eclipse routines;
reuse them, and announce any genuinely needed addition beforehand. New
general-purpose routines belong in Eclipse and follow its existing API,
allocation/error/docs/test conventions and maths-module scaffolding. Never
duplicate a suitable existing routine. Audit at07d2733 reviewed49 math/iproc
sources: raw difference/sample stdev/medians already exist; sampled-window RON
also exists but differs from full-region stdev. image_median_stat computes MEAN
absolute deviation, not MAD. Only a general checked MAD helper is proposed,
not implemented; see the bias-QC Eclipse reuse review. No native/ASDF source or
scientific processing changes accompany this decision/audit record.

2 November requested Chapman gate COMPLETE at
4417d7d159d08afcff2fbb8518fc90c3f4c84e29. Owner-reviewed
chapman-m5-asdf16-resume-U4vTGDyf reports all three ASDF1.6.0 C/Python
interchange controls passed; ten QC controls and installed libasdf0.3.0 reused
from verified449220c evidence. C17 native_operation_template/native_bias_files/
native_layout/native_bias_service/native_explicit_paths all5/5 pass (40.20s).
Complete private normal runtime install has9 manifest payload files, all
hash/installed-engine/CLI checks passed. Six outer and three native preservation
checks passed; production engine/packages/config and retained prefixes unchanged.
Keep mefpp_m5 as opt-in build executable. #219 nested insertion and #221 optional
Float16 header limitations remain open; qualified consumer workarounds are
required, not upstream repairs. No unchanged test replay, new host/C90 matrix,
scientific QC acceptance, merge/cleanup or production activation follows.
Next review remains numerical QC definitions/native-to-ASDF handoff.

2 November Chapman progress/correction #221: at449220c, retained
chapman-m5-asdf16-retry-ZES69RYi, actual Conda/platform/solve/install/package
inventory and all ten shared QC controls passed under real glibc2.17.
GCC10.2.1 then rejected optional _Float16 declaration in packaged libasdf0.3
headers. All six preservation checks passed; no interchange/native install ran.
Test-only asdf_probe_compat.h loads config then omits the unused optional
Float16 declaration only with an explicit Chapman consumer flag. No installed
header/library/compiler change or public structure/numeric conversion is made.
GCC13 C17 probe syntax both modes and ndarray layout comparison pass; synthetic
reuse guard passes. GCC10 runtime remains pending. Retry --reuse-run verifies
old reports/package build/QC source identity and resumes without Conda or QC
replay. Keep upstream header limitation #221 and nested insertion #219 open.
No production activation, merge, cleanup, C90 or second-host matrix.

2 November Chapman runner correction #220: first attempt at59cb940,
chapman-m5-asdf16-wEY4w9AQ, failed on unsupported --no-plugins before dependency
solve/install or functional tests. All five preservation checks passed.
Do not upgrade Conda or infer ASDF/glibc incompatibility from this CLI error.
Corrected runner records Conda version and global/create help, uses only
advertised plugin/solver flags and permits classic-only legacy releases.
Retain real linux-64/glibc2.17 checks and every failed attempt; use a fresh retry.
Five agent guard/capability tests pass; actual target qualification remains
pending. No production activation, engine change, merge or cleanup.

2 November owner explicitly authorizes Chapman qualification before further
bias/QC work because subsequent work depends on ASDF standard/libraries. This
supersedes the earlier no-Chapman-replay boundary for this one representative
Chapman4 increment only; use C17, not a C90/host matrix. Actual target is clean
candidate feat/m5-bias-template-20261102 after main fast-forward to47123eed.
Retained Python ASDF6.0.0/asdf-standard1.5.0/NumPy1.26.4/Astropy6.1.7 is reused.
Selected GCC10.2.1 and CMake/CTest3.29.6 stay unchanged. External libasdf0.3.0
is planned/installed in a new private prefix under actual CentOS7/glibc2.17;
never fake platform limits. Follow
[the Chapman gate](m5-asdf-chapman-qualification-2026-11-02.md).
The gate runs ten shared QC controls, three C/Python interchange controls,
five native C17 contracts and complete private normal-runtime install/hash/CLI
checks. Bias adapter remains opt-in in its build, not normal installed payload.
Two agent guard controls and syntax pass; actual Chapman execution is pending.
No production activation, observation processing, merge or cleanup.

2 November external ASDF Mac qualification COMPLETE at
6395745dd3e55f90c63ae90f28238eae436c6468. Retained
mac-asdf16-mapping-DmvnvXZJ reports all three C17/Python interchange controls
passed: metadata/null/float64, Python uncompressed/zlib arrays, shared-QC
content/frozen links. Standard1.6.0; external libasdf0.3.0; Python asdf6.0.0,
asdf-standard1.5.0, NumPy1.26.4. Ten earlier QC contracts reused after exact
source/evidence checks. No network attempts or dependency provisioning in retry.
Retained prefix, checkout, installed files and exported source preserved.
This is bounded synthetic interchange, not general ASDF conformance, numerical
QC/scientific validation or production integration. Keep upstream nested-path
limitation #219 open; direct mapping workaround is qualified in this consumer.
External library remains selected; bundling deferred. Do not replay unchanged
Mac tests or start Chapman/C90/bias work automatically. Review native QC
definitions/handoff and owner acceptance next; no merge/cleanup or activation.

2 November #219 diagnostic receipt: actual Intel Mac mac-asdf-nested-Kll2GMfs
isolates libasdf 0.3.0 nested-sibling insertion failure (code5, missing readback).
Flat writes and direct mapping construction/attachment/get all return0 and
read back12.5. Prefix/checkout preservation passed. Use the verified mapping
API in the synthetic interchange consumer, preserving exact metadata/array/QC
checks. External library is unchanged; its limitation remains open. Agent GCC
C17 syntax check against pinned public headers passes (synthetic config only,
no linking/runtime claim). Reuse ten QC controls and installed external prefix;
full three-control Mac interchange remains pending. No production activation,
upstream patch/upgrade, C90/bias/Chapman replay, merge or cleanup.

2 November external ASDF runtime receipt (#219): at 33f16555, actual Mac
mac-asdf16-external-dFpUmHsz compiled/linked/started the C17 probe successfully.
The first write stopped adding measurement/value after measurement/unit succeeded;
all ten unchanged QC controls were reused and outer preservation passed.
Do not call native interchange qualified. Pinned upstream source suggests a
nested-parent insertion defect, not yet isolated on target. Run the bounded
flat/nested/direct-mapping diagnostic before choosing a workaround or library
change. Keep external libasdf, all evidence and installed engines unchanged.
The diagnostic's Python syntax is checked; its C/API execution is target-pending.

2 November owner decision: use external libasdf for now; defer bundling into
mefpp (#218). This supersedes the intervening bundling proposal. External native
libasdf and Python asdf remain distinct dependencies. Retry #217 uses explicit
prefix include/library/rpath and requests pkgconf system paths, reusing the
installed 0.3.0 trial in mac-asdf16-streams-o8KPDcUm after checking its revision,
passed preservation/provisioning and package metadata. Fingerprint the retained
prefix before/after; no repeated Conda solve/install or ten unchanged QC tests.
Three synthetic prefix regression tests pass; actual Mac C17/Python interchange
remains pending. Preserve all attempts, working engines and checkout; no merge,
cleanup, production activation or Chapman run in this increment.

2 November ASDF logging correction #216: retry mac-asdf16-retry-9NFYFeVP
confirmed real __osx=13.7.8/classic solver and reused passed QC sources/evidence,
but Conda 24.11.3 still emits a libmamba startup warning. Mixed stderr/stdout
broke JSON parsing before solve/install/compile. Separate retained stdout/stderr
logs and parse stdout only; never discard warnings or ignore nonzero exits.
Two agent stdlib subprocess logging regressions pass; actual native Mac retry
and Chapman remain pending. Preserve both attempts and reuse the original ten
passed QC contracts; no installed Conda repair, production activation or merge.


2 November Mac ASDF receipt/correction: shared QC standard-1.6 contracts passed
10/10 in 1.607 s at 0840f031, retained mac-asdf16-qTH3ZFNB. Native trial failed at
Conda dry-run solve, before installation/compilation/interchange; all preservation
checks passed. #215 corrects only private provisioning: classic solver, external
plugins disabled, pkgconf, and CONDA_OVERRIDE_OSX set solely to real sw_vers
13.7.8 (verified before solve), never an invented/newer OS or glibc override.
This narrowly supersedes prior no-OS-override wording. Retry with fresh run and
--reuse-qc-run only after pinned module/schema/test identity and original passed
sub-gate/preservation checks; do not repeat unchanged QC tests. Keep the failed
attempt, base Conda, installed engines, checkout and all evidence untouched.
Native/Chapman qualification remains pending; no production adoption/merge.


2 November owner-authorized ASDF 1.6 increment: target file/core standard 1.6.0
using retained Python asdf 6.0.0 / asdf-standard package 1.5.0. Qualify pinned
libasdf 0.3.0 in a fresh private prefix with one C17 consumer and bounded C/Python
metadata/array/shared-QC interchange, Mac first; Chapman compatibility remains a
separate pending gate. See docs/developer/libasdf16-private-qualification-2026-11-02.md
and #214. This supersedes earlier no-dependency-trial wording only for this
private qualification. No production environment/engine changes, observation
processing, C90 duplicate, bias replay, merge or cleanup. Do not claim target
success before inspecting actual evidence; retain failed attempts and manifests.


2 November shared QC decision/implementation: ASDF is the adopted common saved
QC representation, with a per-input record and a separate product record whose
file identity/characterization precedes ordered frozen input references. Replace
`.fits` by `.asdf`; do not append `.fits.asdf`, overwrite conflicts or infer
compressed-file identity. All recipes share QcRecipe/schema/validation/ASDF writer
and local traversal; BiasQcRecipe restricts quantities to ADU/counts. See
`docs/developer/shared-qc-asdf-2026-11-02.md`. This opt-in Python integration layer
is prepared, target-pending, with no native arithmetic/normal activation changes.
Do not silently choose level/RMS methods/regions, hot-pixel thresholds or RON pairs;
actual numerical extraction and standalone CLI handoff remain to be reviewed.
Use retained qualified private Mac ASDF 6.0.0 environment for the new metadata-only
checks; no installation, dependency/native trial replay or Chapman duplicate.

2 November template lessons: before the next native recipe, read
`docs/developer/native-operation-recipe-template.md` and follow the annotated
`mef_operation_steps` contract. Preserve explicit detector/HDU/config/output
mapping and coverage-aware metadata comparisons; reuse qualified header paths
without indexing deleted qfits headers (#212). Define diagnostics, scientific QC,
decisions and saved representation separately with Fernando. Bias's provisional
JSON is not a default for later recipes. Template updates are comments/scaffold
only; tested execution order and bias arithmetic are unchanged. Current target
bias qualification passed at native 2803786dc2358f1cfdf641c262db6fe95a46bb05;
QC/persistence design acceptance and PR #209 merge remain pending.

2 November owner clarification and first M5 candidate: current tests use C17 only
on the Intel Mac, without duplicate C90 or Chapman runs. Consider Chapman only
for individual workloads exceeding Mac memory. Preserve C90-compatible source;
source preparation/GitHub delivery remain allowed. Fernando explicitly requires
a reusable template subroutine: `mef_operation_run` now supplies shared validate,
load, calculate, publish and cleanup orchestration, with bias as its first concrete
adapter. The opt-in one-detector PAF/TOML file-to-product candidate is prepared;
actual Mac C17 checks remain pending. No installation, observation processing,
merge or cleanup. Earlier paired-language/host statements are historical where
superseded. See the current M5 bias-template record for scope and limits.

1 November owner-comment revision: architecture review version 3 incorporates
standalone TOML use within an ASDF environment without a native ASDF dependency;
immutable input files with no deletion/staging copies and disk writes only for
outputs/logs; distinct clipping, flat-selection and linearity limits; explicit
const_level and future robust ramp_up/ramp_down sky-flat methods; correct stack
memory accounting; one processing TOML per recipe as a target capability; and
a configurable filename instrument label using OCAM. Ramp fitting is a separate
scientific increment after legacy sky-flat extraction, not an M5 numerical change.
The commented Word original is retained; revised Word/source documents are for
review in draft PR #208. No native execution/installation or merge/cleanup yet.


1 November owner update for the current refactoring cycle: use actual Intel Mac
C17 for native implementation and iterative affected checks. After the agreed
candidate is ready, perform consolidated Mac C90 compatibility, then representative
shared Chapman verification. Preserve C90-compatible core source and selected tools;
do not repeat paired-language/Chapman matrices for every intermediate edit.
Finish the first bias adapter with PAF, connect the existing TOML reader immediately
next, and repeat bias with equivalent TOML settings before subsequent builders.
The architecture review now includes proposed command/request examples and a Word
review copy for owner comments. Examples are not implemented CLI/schema contracts.

1 November owner requests discussion and a source-grounded architecture/roadmap
review before M5 implementation. See [the current/target architecture review](mefpp-architecture-review-2026-11-01.md).
It records dual individual/full-recipe invocation, configurable CMDP/SMDP creation
identities, common calibration storage, explicit normalization/reload metadata,
FITS keyword authority and later dark/linearity/fringe/process extensions.
New source findings #204–#207 are recorded, not fixed or runtime-reproduced.
This is a design proposal, not accepted new interfaces, numerical corrections,
TOML production activation or parallel execution. No install/reduction/test replay,
merge or cleanup follows from this audit. Earlier M5 sequencing notes retain
historical scope; the current owner discussion precedes implementation.

1 November [installed large-file real-data receipt](large-file-installed-real-data-2026-11-01.md): PR #200 was
owner-accepted/merged at a240829; #195/#201 closed and branch cleanup completed.
New separate optimized C90 runtimes from a240829 are installed on actual Intel
Mac and shared Chapman. CP Pup r_SDSS (Mac) and CN Ori NB_659/r_SDSS (Chapman4)
pass all 32 detector pixels exactly and finite, with raw headers matching except
primary ORIGFILE, against fresh pre-large-file native 5b251831 builds.
The first Mac comparison used a reference predating accepted #121 and remains
failed evidence; raw-scan calculations reproduce old/new scan medians 32/32.
Normal engines/configurations, protected inputs/products and clean checkouts
remain unchanged. This is native real-data equivalence with retained calibrations,
not a full Pycavi/scientific/Phase 3 or new >4-GiB/performance claim.
M5 remains paused for owner acceptance of the intervening install/comparison work.
Do not replay unchanged matrices or automatically switch engines, merge/clean
this receipt branch or implement M5. Earlier pending statements below are historical
within their source/date/scope; preserve all original and corrected evidence.

[Large image I/O paired target qualification](large-file-image-io-paired-results-2026-10-31.md) is complete at
native c66b8158: actual Mac C90/C17 four contracts each4/4; representative Chapman
each4/4; each host's single C90 >4-GiB processed MEF independently passes every
pixel/relevant header/scaling/order/padding check. Installed files, clean main
38b27f8 and exported source preserved. Approved IO-0–IO-5 gates have evidence;
IO-6 owner acceptance and explicit merge/cleanup remain next. No new unchanged-
source tests, install, full-size benchmark campaign or M5 code by default.
#195 stays open for acceptance; #201 bounded window correction is target-qualified.
Keep ordinary-plane/count/addressability limits and theoretical-vs-tested size
distinction. Earlier IO-5-pending notes below are historical at their source/date.


Approved large image I/O roadmap v1.0: [IO-0 through IO-4 agent results](large-file-image-io-agent-results-2026-10-31.md).
Fourteen production files and three focused test/runner files implement off_t
positions, checked memory/transfer arithmetic, legacy wrappers and processed
output; numerical types/routines unchanged. C90/C17 focused/ordinary gates and
scoped ASan/UBSan pass. One 4,362,324,480-byte processed MEF has every pixel,
header/scaling/order and padding independently verified. #201 copied-window
count correction is agent-qualified within IO-2, actual-target pending.
Next IO-5: actual Mac then representative Chapman, selected tools, private C90/C17
builds/focused checks and one large C90 processed output per host. No original
observations, installation, extra full matrices or benchmark campaign. Keep
#195/#201 and IO-6 open until target acceptance; no merge/M5 advance yet.
Retain approved gates and amendment control; earlier pending statements below
are historical within their stated scope.


Owner approved large image I/O roadmap v1.0 after reviewing 6f502658.
Execute IO-0 through IO-6 strictly; frozen interfaces/fixtures/resources:
large-file-image-io-io0-plan.md.
No merge/install authorization. Subsequent proposal-pending language is historical.

1 November [large image I/O roadmap v1.0](large-file-image-io-roadmap-v1.md) is PROPOSED,
awaiting owner approval. Owner requires large FITS/MEF reading AND processed
output, without general numerical-type widening. This supersedes the prior
read-only offset proposal. Fourteen production/header/build files, off_t disk
positions, checked size_t memory/transfer lengths, unchanged numerical types
and original-data immutability; stages IO-0 through IO-6 and explicit amendment
control. No implementation/test/install/merge authorization follows merely
from preparing this roadmap. M5 waits for this selected I/O increment.
M4/PR #186 was accepted and merged at 38b27f8; Mac and Chapman returned clean
synchronized main and branch cleanup. Older M4-pending notes are historical.

31 October [bounded M4 closure review](m4-bounded-closure-review-2026-10-31.md)
recommends owner acceptance of the detector/layout foundation, then M5 calibration
decomposition after explicit integration. Native source 5b251831 passes paired
Mac/Chapman C90/C17 four-contract gates and scoped agent sanitizers. Corrected
Chapman16-call performance comparison preserves exact products/inputs/install/
checkout and shows no consistent timing penalty; lower medians are not proof of
general speedup or lower memory. #197 source-specific allocation correction closed;
#195 large-file support and broader full-size/opt-in throughput limits remain.
End this unchanged-source test cycle; no extra matrices/benchmarks by default.
No automatic M4 closure, merge/cleanup, installed activation or M5 code before the
owner's stage decision. Earlier target/performance-pending entries are historical
within their stated source/scope; retain all failed/original/corrected evidence.

31 October [Chapman performance inspection and #197 correction](qfits-offset-storage-correction-2026-10-31.md):
prior sixteen-call products/preservation pass, but timing ratios remain under
review. Recorded load is low; existing sleep(1) protects ORIGFILE names and stays
unchanged. The reuse patch added two avoidable temporary offset heap allocations;
restore original-sized stack buffers and grow only on actual count >128. All
bounds/offset checks, numerical code and int-range limit remain. Agent C90/C17
four contracts and scoped sanitizer three pass, including repeated growth to300.
New selected-tool Mac then Chapman functional gates are pending; no new benchmark
or claim that prior timing variation is explained. Retain all earlier results;
no automatic retry/slowdown allowance, installed activation or M4/M5 closure.

31 October owner accepts [paired qfits-backed M4 behavior](m4-qfits-paired-results-2026-10-31.md)
at 5e6bd83beafa744cd2a3be64b5405083c3ae634b: Mac/representative Chapman each4/4
in C90/C17 with installations, clean main and exports preserved. #194 count bounds
closed; #195 wider-file boundary remains explicit. This is not merge/cleanup or
permanent adoption of the 2 GiB support limit. Next [performance plan](m4-performance-comparison-plan-2026-10-31.md)
uses retained private builds and prepares commands only; sixteen launches planned,
none measured. Review script/plan before execution under the existing contract.
No native changes, observations, installation, repeated tool discovery or automatic
M4 closure/M5 extraction. Earlier target-pending entries below are historical.

31 October owner accepts qfits/Eclipse reuse. The [M4 adapter](m4-qfits-reader-adapter-2026-10-31.md)
removes M4 FITS block/seek parsing, reuses qfits headers/offsets and keeps detector
maps/validation and the Eclipse plane loader. Narrow shared-cache bounds fixes
#194/#195 and single-pass card views preserve legacy APIs. Files above INT_MAX
bytes (just under 2 GiB total) fail explicitly; no 64-bit offset redesign is claimed.
Agent C90/C17 discovery/layout/bias/native-path contracts pass 4/4; scoped sanitizer
discovery plus layout/bias pass, with initial premature-launch log retained (#196,
closed). Old library reproduces both bounds defects with expected diagnostic86.
New four-contract Mac then representative Chapman gates are pending. Use recorded
tools directly; no original observations, installation, performance/M4 closure or
M5 extraction. Earlier review hold applies to the superseded scanner design.

31 October owner challenges the additional native FITS reader and instructs
[existing-reader reuse review](m4-header-reader-reuse-review-2026-10-31.md). qfits already supports primary/extension
headers, order/duplicate preservation and HDU discovery; prefer M4 metadata/maps
above existing qfits/Eclipse I/O. Concrete count/offset gaps #194/#195 are recorded
without fixes or execution. Candidate 2d662b1 passes layout+bias C90/C17 on Mac and
representative Chapman4; #185/#193 closed with paired receipts. Those tests do not
approve the reader design. Keep PR #186/M4 open for the scope decision; hold the
unpublished native audit client and actual-header handoff. No native change,
installation, observation access, new test campaign or M5 extraction in this review.
Earlier target-pending and automatic-next-audit notes below are historical.

31 October resumed [native M4](m4-native-layout-2026-10-31.md) toward subroutine decomposition.
Merged accepted preflight main c4a5ba4 into the candidate without changing native
C sources; resolved status-document conflicts by retaining both histories.
ESO preflight paired/actual-header evidence and Mac/Chapman cleanup are accepted
in PR #192. Agent merged-source C90/C17 layout+bias both pass 2/2 (1.22/1.24 s),
and normal engines link. Private target runner is syntax-checked, not target-run;
selected-tool actual Mac then Chapman qualification remains next. Preserve #185,
M4 #182 and PR #186 pending gates; no install, performance claim or M5 extraction.
Earlier target-pending preflight entries below are historical.

31 October owner accepted M4 interface/fixture review and instructed proceeding.
First [native layout increment](m4-native-layout-2026-10-31.md)
implements opt-in C90 bounded header catalogues, independent detector maps,
selector/unit/active-region/reference checks and existing Eclipse plane loading.
Primary/extension/MEF inputs reach the same existing bias service. Agent optimized
C90/C17 layout+bias and scoped ASan/UBSan checks pass; final affected-layout controls
also pass. New candidate FIFO finding #185 is corrected and remains target-pending.
M4/#182 stays open: actual Mac/Chapman, instrument mapping/integration, original
normalization equivalence and performance gates remain pending. No install, engine
switch or full Bath/CMOS qualification. Windows notes are informational only.
Native work uses feat/m4-native-layout-20261031. Its prerequisite preflight stack
is now merged into main c4a5ba4; retained historical helper receipts stay valid.

31 October owner accepts [ESO data preflight](eso-data-preflight-2026-10-31.md) and explicitly
requires immutable original raw data. Initial OmegaCAM/WFI raw-imaging service
reuses M3's bounded read-only reader and actual instrument configurations; public
preflight writes a separate report outside raw directories, never repairs headers
or writes raw copies. Correct complete metadata needs no additions. Source/HDU
mapping/authority, unknowns and scoped readiness are explicit; no scientific or
payload-integrity acceptance is implied. Agent corrected ESO 10/10 and inspector
24/24 pass. Candidate filter cross-keyword finding #190 fixed, target-pending;
WFI gain issue #131 remains independent, never substituted or repaired. Actual
Mac then representative Chapman/real-input metadata qualification remain pending.
No automatic legacy-pipeline gate, installation, reduction, native/M4 or full WAD
runtime claim. Other adapter/profile integration remains subsequent work.

31 October owner makes [data preflight subordinate to WAD](../architecture/proposed/wad-processing-project.md#data-preflight-under-wad).
WAD governs metadata/authority/assessment/plan contracts; preflight is a shared
read-only ingestion service with instrument adapters, explicit apply writes copies.
Current ASI adapter is not claimed to be a general WAD/ASDF runtime. Current
observatory schema v2 uses a stable telescope name and separate profile_date;
frame DATE-OBS remains original evidence, never part of equipment identity.
Generated dataset notation v3 prevents silent old-plan reinterpretation. Affected
13-group agent suite passes; scoped Mac 13-group/full-header-preflight verification
pending. Preserve earlier 32/260/ten-copy Mac evidence and all existing outputs.
No repeated legacy/native matrix, partitioning, installation, reduction, automatic
merge/cleanup or M4 closure. Earlier dated-name notes are historical.

31 October owner approves [practical ASI preparation inputs](asi-simple-inputs-2026-10-31.md):
reusable observatory/camera TOMLs and directory role/filter names generate the
detailed dataset TOML; no manual exposure/gain/offset/temperature/filename rules.
Role/filter directories work in either order. Header-first filters are checked
against directory labels; missing filters can be proposed, unknowns stay unknown.
Dome/sky/unspecified flats remain distinct, conflicts block and flat-Light labels
still require acknowledgement. Agent 9+11+12 controls pass; actual Mac new-interface
qualification is pending. Prior explicit-interface Mac 20 controls/full 260 plan/
ten-copy passes at 7bf1c824 remain valid for that version. Uploaded manual saved
unchanged under docs/manuals/cameras, facts sourced without inferring acquisition
mode/physical gain. Preserve originals/installations and native boundaries;
partitioning is deferred. No automatic merge, reduction, installation or M4 closure.

31 October owner authorizes [generic TOML-driven ZWO ASI preparation](zwo-asi-provenance-2026-10-31.md)
after previous-helper actual Mac 260-file plan and ten-copy checks passed.
The generic entry point separates camera/dataset rules and sourced provenance;
existing INSTRUME/original cards/payload remain, conflicts block preparation.
Bath Physics Observatory/institution and paper/data DOI are configured. Returned
260-frame 200/1600 mm header signature identifies the StellaLyra RC; configured
checks add a dated WENU telescope label while preserving TELESCOP=SynScan.
Observer, coordinates and software versions stay unknown.
Agent legacy 9/9 and current generic 11/11 pass; candidate #187 parse-error
reporting is fixed but target-pending. Fresh Mac provenance plan/copy checks remain
pending. No reduction, installation, native changes, M4 closure or automatic
merge/cleanup; original review/helper PR #183 and native PR #186 stay unchanged.
Earlier pending statements retain historical scope.

31 October owner clarification: identifying native Windows obstacles is
informational preparation for a possible later port. It must not affect Mac/Linux
design, introduce Windows-driven adapters/abstractions or overhead, or block their
acceptance. If Windows is ported later, that version receives the required adapters
then. Preserve efficient native Mac/Linux facilities and the no-speed-penalty
refactoring requirement. This supersedes any earlier Windows wording suggesting
current Mac/Linux design restrictions; no source changes or tests are needed.

31 October owner makes native speed/efficiency preservation an explicit
refactoring requirement and requests early native-Windows difficulty identification.
The [performance/portability contract](native-performance-portability-contract-2026-10-31.md)
requires no reproducible same-workload slowdown, with wall/CPU time, memory and I/O
compared on matched optimized builds; no percentage penalty is preapproved.
Concrete source barriers include the Windows build guard, qfits mapping/swap,
FITS stream/offset handling, Unix path/permission assumptions and Eclipse OS helpers.
This is source/design review only: no benchmark, Windows build or portability patch.
Apply at changed native boundaries and cumulative acceptance; retain existing
Windows sequencing, C90/numerical behavior, all evidence and working installations.

31 October owner added raw-input DPR.TYPE/CATG/TECH preparation to M4 review.
The [data preparation guide](../data-preparation.md) reviews official ESO DICB v8
and ZWO ASI1600 manual rev1.5. Dataset-specific Python helper #184 proposes Bath
directory roles with header checks, then writes explicit reviewed-plan copies
with unchanged payload bytes; originals stay untouched. Nine synthetic agent
controls pass, including conflict/stale-plan refusal, header growth/scaling and
incomplete-copy handling. Actual Mac full 260-file dry run/copy verification is
pending. No C numerical changes, reduction, install, generic CMOS qualification
or automatic classification/association policy is introduced. PR #183 remains a
draft review with an explicitly authorized preparation helper; preserve M4 gates.

31 October M3 is owner accepted/closed and PR #178 merged at
6c4b0f0eff639da8dbef890f0df10f86c70bb0ee; owner-returned Mac and Chapman4
cleanup confirms clean main, merged review branch removal and protected installs
preserved. Owner instructed M4 review and inclusion of `~/Pictures/ZWO_Bath/`.
The [M4 interface/fixture review](m4-interface-fixture-review-2026-10-31.md) tracks #182:
independent detector/HDU maps, optional selectors, scaling, selection/reference
context and an astrophotography profile within existing visual-purpose vocabulary.
Returned Bath inventory samples 256/260 FITS: primary images, unsigned-16 scaling,
explicit flat-role ambiguity and 30 s dark/32 s light mismatch. Four headers remain
uninspected; no raw report/pixels independently audited. This is documentation and
source review, not M4 C implementation, reduction, profile activation or generic
CMOS acceptance. Review interfaces/fixtures before code; preserve original gates,
Pycavi grouping ownership, all evidence and installed environments. Earlier pending
M3 receipts below retain their historical scope.

31 October [summary/alignment paired receipt](m3-summary-paired-results-2026-10-31.md): source
fc4b26cd1a1eed828a88d818fcdbb7912a2acbe2 passed 24/24 on selected Intel Mac
(6.938 s) and representative Chapman4 (3.563 s), with installed files and clean
main preserved. Direct real --summary displays five aligned CN Ori exposure rows,
retaining warnings and the missing historical flat reference without a wrapper.
The owner-requested interface addition is qualified; M3 closure is recommended
for owner acceptance, then separately instructed merge/cleanup and M4 review.
Documentation-only receipt: no executable change, test replay, install or host sync.
Earlier pending/held notes retain their stated historical scopes.

31 October owner requested [direct --summary output and aligned titles](m3-inspector-summary-2026-10-31.md)
before M3 closure. Compact exposure rows/diagnostic counts now need no wrapper;
detailed tables also use measured spaces. Agent suite passes 24/24; actual Mac,
then representative Chapman presentation qualification remains pending. Prior
22-group reader and real-tree evidence stay valid; no reader/C/scientific change.
PR #178 stays draft for the added interface gate. No installation or activation;
owner acceptance/merge-clean precedes M4 review.

31 October #180 [corrected paired and real-tree receipt](m3-eso-header-paired-results-2026-10-31.md): source
f7967fd1ee93f2a5a1a4faa227cadd460c054fa5 passed 22/22 on selected Intel Mac
(4.788 s) and representative Chapman4 (2.405 s), with installed files and clean
main preserved. Actual CN Ori redisplay now retains all five 80 s r_SDSS headers,
33 HDUs each, while retaining 36 warnings and one separate missing master-flat
reference. The original-scope M3 closure recommendation is reinstated for owner
acceptance; PR #178 is ready. No test replay/install/host sync for this receipt.
Separate owner merge/cleanup precedes M4 review; earlier held/pending notes are
historical. #181 remains a separate suffix-convention follow-up.

31 October subsequent actual-tree finding #180: nonstandard ESO telemetry
caused strict inspector verification to discard otherwise readable HDU metadata.
The [bounded correction](m3-eso-header-inspection-2026-10-31.md) retains diagnostics and readable fields,
with no fixes to source files or image reads. New regression fails before; agent
corrected suite passes 22/22. Corrected Mac/Chapman qualification and repeated
bounded Chapman tree display remain pending. Hold the earlier M3 closure
recommendation and PR #178 in draft; preserve all earlier evidence. No native,
scientific, installation or M4 work. Earlier 21-group receipts retain their scope.

31 October M3 inspector [paired qualification](m3-inspector-stages-paired-results-2026-10-31.md): exact source
0d8f2978a4ef4c78c47f1526b48e03d77351c024 passed all 21 groups on selected Intel
Mac (4.639 s) and representative Chapman4 (2.702 s), with installed module,
configured engine/configuration and clean main 3a61df6 preserved. The
[final original-scope M3 review](m3-final-closure-review-2026-10-31.md) recommends milestone closure: the
inspector gap is resolved alongside accepted native paths. Owner acceptance and
separate merge/cleanup remain pending; then review M4 detector/layout interfaces.
This receipt is documentation only: no test replay, installation or host sync.
Earlier pending/gap notes retain their historical source/evidence contexts.

31 October owner authorized completing the remaining original M3 inspector work.
[Stage-view candidate](m3-inspector-stages-2026-10-31.md) adds evidence-linked calibration/preprocessing/
normalization/WCS views and shared pure client conventions. Agent final 21/21
checks pass; initial test-only oracle #179 failure is preserved. Selected Mac,
then representative Chapman 21-group qualification remains pending; #159/M3 and
#179 stay open. No C code, numerical tuning, installation or normal activation.
Use exact private exports and protected-host runner; no historical matrix replay.
Cumulative closure precedes M4 implementation; merge/cleanup needs owner acceptance.

31 October cumulative review at accepted main 3a61df6: [original M3 checklist](m3-cumulative-review-2026-10-31.md)
retains #159/M3 open. Native explicit paths have paired acceptance; the original
associated-calibration/preprocessing/normalization/WCS inspector overview remains
incomplete. Complete that bounded read-only integration before closure; no new
timing/debugging or historical test campaign is a prerequisite. [M4 readiness](m4-readiness-review-2026-10-31.md)
is preparatory review only, with no implementation or milestone advance. Preserve
ESO OB/template/exposure metadata distinctions; grouping/association belongs in
Pycavi, while mefpp processes selected lists with compatibility checks. Review
only: no native/Python code, execution, installation or merge/cleanup. Earlier
increment receipts retain their original scopes and evidence.

30 October paired native safety receipt: selected-tool Intel Mac and representative
shared Chapman4 private optimized C90 builds and all four contracts passed 4/4
at 87ed266a109741c4998bfc8c978d07c9306f0091 (32.74 s / 20.77 s). Protected
installed module/engine/configuration and clean review checkouts stayed unchanged.
[Paired results](native-safety-paired-results-2026-10-30.md) qualify the bounded #144/#171/#172/#174/#175/#176/#177
corrections; PR #173 is ready for owner review. #74 retains unqualified legacy
facilities; #125/#128, unresolved #116 and full M3/#159 remain separate. No real
OOM, broad leak/concurrency, RTD display or scientific/installed activation claim.
Preserve failed/corrected runs, manifests and tools. This documentation receipt
needs no functional replay; synchronize review checkouts, then await owner review.
Separate owner instruction precedes merge/cleanup. Earlier target-pending notes
below are historical within this qualified batch.

30 October actual Mac #173 batch stopped at b4fe1c6 during new format-probe
compilation: missing private variadic qfits declarations (#177). No functional
test ran; installed module/engine/config and checkout preservation passed.
[Correction/evidence](native-format-prototypes-2026-10-30.md) includes existing qerror.h and makes implicit
declarations fatal for the probe. Corrected agent C90/C17/scoped ASan format
checks pass 1/1 each; production/other contracts unchanged. Actual corrected Mac
then Chapman four-test qualification remains pending; keep applicable issues
open and PR #173 draft. Use the new correction manifest, preserve the failed Mac
run and all earlier evidence. No install, automatic merge/cleanup or matrix replay.

30 October owner authorized batching reachable #74 fixes with #144 in draft
PR #173 before target handoff. [Complete format/buffer inventory](native-format-safety.md) distinguishes inherited
message/newline (#174), timestamp, conditional RTD, header-merge (#176), keyword
and filename corrections from new probe-input mistake #175. Agent final C90/C17
four-contract batches pass 4/4; scoped address/UB format/allocation/swap checks
pass 3/3. [Agent receipt](native-format-safety-agent-results-2026-10-30.md) retains failures, exact origins/hashes and limits.
Actual selected-tool Mac/representative Chapman combined four-test qualification
is pending; applicable tickets stay open. #74 also retains unqualified gnuplot/
FITS-table facilities; #125/#128 remain separate. No real OOM, broad leak, RTD
operation, numerical/scientific or installed activation claim. One combined host
handoff replaces the earlier two-test handoff; preserve all tools/installations/
evidence and separate #144 commit. No automatic merge/cleanup or matrix replay.

30 October owner authorized #144 after accepted/merged PR #170 at clean main
e2460fb72bdbe69f92c7da8994a81d21928569b5. [Bias dependency failure correction](eclipse-allocation-failures.md)
checks inherited image/cube, crop, overscan scratch and final QC allocations;
#171 separately records inherited borrowed-cube destruction/ignored status.
The shared kernel and active native overscan callers propagate failure. Agent
C90/C17 allocation/native-path CTests pass 2/2; scoped ASan/UBSan allocation suite
passes 1/1. [Agent receipt](eclipse-allocation-agent-results-2026-10-30.md) retains original failures and new test setup #172.
Actual selected-tool Mac/representative Chapman checks remain pending; keep
#144/#171/#172 open. Global qfits fatal RAM/swap policy is unchanged; no real OOM,
LeakSanitizer, complete-engine memory or scientific acceptance. Full M3/#159 and
other recorded limits remain separate. Preserve tools/installations/all evidence;
no historical matrix replay, automatic merge/cleanup or configured activation.

30 October paired qfits swap receipt: selected-tool Intel Mac and representative
shared Chapman4 optimized private C90 builds and both focused CTests passed 2/2
at 471f42e19e304e16872291172535e855a2f826d9. Protected installed files and clean
review checkouts stayed unchanged. See [paired results](qfits-swap-paired-results-2026-10-30.md).
The 20-case forced-swap/ownership contract and real native-path regression passed;
#164 missing mode, #168 unowned cleanup and probe-oracle #169 are target-qualified.
PR #170 is ready for bounded owner review. Original M3/#159, long FITS strings
#125 and wider dependency allocation failures #144 remain open. No broad leak,
OOM/thread-safety/scientific or installed activation claim. Preserve all original
and corrected evidence/tools; this documentation-only receipt needs no replay.
Separate owner instruction precedes merge/cleanup. Earlier target-pending notes
below are historical within this qualified correction.

30 October paired native M3 receipt: selected-tool Intel Mac and representative
shared Chapman4 private C90 builds and both focused CTests passed 2/2 at
113156b94fe68f7bf2848c93ecd7451551db2984. Installed reduction module, configured
engine/configuration and clean review checkouts stayed unchanged. See
[paired results](m3-native-paths-paired-results-2026-10-30.md). The actual C engine passed the native path contract
alongside the 51-case CLI regression. #163/#165/#166 corrections are target-qualified;
PR #167 is ready for bounded owner review. Original M3/#159 remains open, as do
#164 swap/O_CREAT, #125 long FITS strings and #144 wider OOM limits. No leak/OOM,
concurrency, scientific, complete-M3 or installed activation claim. Preserve
selected tools and all evidence; this documentation-only receipt needs no test
replay. Owner instruction precedes merge/cleanup. Earlier agent/target-pending
notes below are historical within this qualified scope.

30 October paired M3 inspector receipt: selected-Python Intel Mac and
representative shared Chapman4 passed all 15 grouped controls at
2c820effff393d5ea4e1555439397ef7c7a6cda6; protected installed files and clean
review checkouts stayed unchanged. See [paired results](m3-project-inspection-paired-results-2026-10-30.md).
#160 entry placement and #162 canonical fixture corrections are target-qualified;
retain failed/earlier attempts and the read-only Chapman state confirmation.
PR #161 is ready for bounded owner review; original #159/full M3 execution and
inspection gates remain open. No installation, reduction, new numerical/ASDF
behavior or permanent JSON decision. This receipt changes no tested code and
needs no test replay. Owner instruction precedes merge/cleanup. Earlier draft/
target-pending notes below are historical; preserve tools and all evidence.

30 October M3 target finding: original a1a95c700a7bb7755cf81ac8e2213b3adc754f96
passed 14/14 on Mac, but Chapman returned two fixture failures and one error:
lexical /home expectations contradicted canonical /home1 identities. [#162
correction/evidence](m3-inspection-canonical-fixtures-2026-10-30.md) resolves generated fixture identity and adds
an explicit alias regression; inspector/resolver/installed code are unchanged.
Agent reproduced all three failures and corrected 15/15 checks pass through an
aliased work-parent. Corrected Mac/Chapman verification remains pending; preserve
both target attempts. Chapman protected files passed but final checkout verification
did not run after failure. PR #161 stays draft; #159/#160/#162 remain open for their
applicable gates. No test-gate weakening, installation or automatic merge/cleanup.

30 October M2 is owner-accepted/closed after merged PR #158 and clean Mac/shared
Chapman main b872c8f44c1b54982069a3f94735da492a9dd739; owner instructed Proceed at M3.
The [first M3 increment](m3-project-inspection.md) adds explicit path-base primitives and a
read-only legacy project inspector, with outer-package `pycavi project inspect`
entry, selected CFG/FITS headers, ordered lists, links, diagnostics and bounded
coverage. Agent 14 grouped controls pass; actual selected-Python Mac/representative
Chapman checks remain pending. #159 retains full M3 execution/overview gates; no
M3 completion, numerical routing, installed activation or milestone reordering.
Preserve owner-requested nested import banner (#59); #160 records new inspector
entry correction. Keep existing JSONs for now; metadata export is stdout only,
ASDF stays M7. Follow the plan/good practices and discuss departures first.
Preserve evidence/tools/installations; no historical matrix replay or automatic
merge/cleanup. Earlier M2 acceptance-pending notes below are historical.

30 October final M2 cumulative review after owner-accepted/merged PR #157 and
clean Mac/shared Chapman main 09a7aee4d69f04f5aeef954ff87c39d6f870d2d3:
[recommend original-scope M2 closure](m2-final-closure-review-2026-10-30.md). The #155 project/native
composition gap is resolved; the complete checklist and six paired receipts support
configuration completion. This is a recommendation pending owner milestone
acceptance, not M3 execution. Retain existing JSON outputs for now as explicitly
instructed; human configuration remains TOML, and M7 retains planned ASDF
persistence without a newly invented JSON-removal requirement. Follow the current
plan and good programming practices; discuss proposed departures before
implementation. Source/evidence/documentation review only; preserve selected
tools, installations and all evidence, with no historical test replay. Separate
owner instruction precedes merge/cleanup. Earlier status notes are historical.

30 October paired project/native composition receipt: selected-tool Intel Mac
and representative shared Chapman4 private C90 builds and both affected CTests
passed 2/2 at d0ab19e91b46e6fe6e21c541af99c21ed35029b4. Protected installed files
and clean review checkouts stayed unchanged. See [paired results](m2-project-composition-paired-results-2026-10-30.md).
The #155 configuration integration correction is target-qualified and ready for
owner review in PR #157. Full M2 closure remains a cumulative review/owner decision;
no M3, ASDF publication, numerical processing, installation or automatic merge.
Preserve selected tools and all evidence; this receipt needs no test replay.
Earlier target-pending notes below are historical. Separate owner instruction
precedes merge/cleanup.

30 October owner accepted/merged PR #156 and instructed merge, clean, and
proceed. At baseline ea35197a7f074ac1c44289e7bcc94336f92d6681, the next original-M2
increment implements [project/native composition](../architecture/proposed/m2/project-composition.md) for #155. Project
envelope 2 composes reusable complete domain-v1 declarations; complete version-1
projects remain supported. The shared CLI/library loader uses the qualified C
resolver for complete/split/local native references and validates readout against
resolved settings, retaining all source texts/hashes/edges and domain origins.
Project conflicts fail (empty project override allowlist); numeric overrides stay
native. Agent focused C90 checks passed 2/2, including 18 primary profiles and 24
composition rejection/recovery cases. Actual Mac/representative Chapman checks
are pending. Native C/catalogs, installed software, numerical algorithms and
milestone order are unchanged; no M3 execution or ASDF publication. See
[agent receipt](m2-project-composition-agent-results-2026-10-30.md). #155/full M2 closure remain open pending target/owner
review. Preserve accepted evidence; no historical matrix/tool replay or automatic
merge/cleanup. The earlier closure review retains its original as-is baseline.

30 October cumulative M2 review at accepted merged main
c0bbcc5866b49d64fad6498a029429b35ada9953: keep M2 open. Native configuration
resolution/equivalence, migration and provenance have accepted paired evidence,
but reusable project-domain composition is not connected to the frozen project
loader. The as-is loader still requires inline project domains and one complete
standalone native reference. [Closure review](m2-closure-review-2026-10-30.md) records the original-gate
checklist, accepted chain and [remaining M2 integration #155](https://github.com/fselman/wenu-imaging/issues/155).
Do not infer full M2 closure from native test success or start M3. No source code,
new functional run, installation or numerical processing in this review; preserve
accepted tests/tools/evidence and implement no scope reduction. Owner review and
separate integration instruction remain required for this documentation branch.

30 October paired migration receipt: selected-tool Intel Mac and representative
shared Chapman4 private C90 builds and both focused configuration CTests passed
2/2 at 38f4f4d4bd05c4977f1624fc8737431527bdbe8a. Protected files and clean review
checkouts remained unchanged. See [paired migration results](m2-migration-paired-results-2026-10-30.md). Ready for
bounded owner review; full M2 closure remains a separate cumulative review.
The corrected nested-package protection lookup is target-verified (#154); retain
the first failed handoff attempt. Establish all paths/interfaces from as-is source
and actual host evidence; never guess layouts. No test replay for this documentation
receipt, installation, numerical processing or normal engine activation. Preserve
all evidence/tools and milestone order. Owner instruction precedes merge/cleanup.
Earlier target-pending notes below are historical.

30 October M2 migration implementation after accepted/merged PR #151 and clean
Mac/shared Chapman main a09bec7e6bc0d3fa8d82245db59aaf3063ac0d94: owner authorized
finishing configuration migration. The shared Python API/CLI and opt-in native
configuration bridge now migrate PAF values through the original constructor,
retain PAF/CFG text/hashes and duplicate/conflict records, preserve exact parsed
TOML source graphs/override contributions, and freeze WAD configuration attributes
for CLI/library requests. New examples match all 585 OCAM / 249 WFI stored values
and selected local CLI overrides exactly. CFG values remain explicit compatibility
evidence; no scientific associations/identities or executable plans are invented.
Agent C90/C17 focused checks and scoped ASan/UBSan pass. Actual selected-tool Intel
Mac and representative shared Chapman checks remain pending; full M2 closure needs
those results and owner review. Preserve original PAFs, installed tools/prefixes,
prior evidence and milestone order. No installation, numerical processing,
ordinary engine activation, ASDF publication, merge or cleanup is authorized by
this implementation. See [migration contract](../architecture/proposed/m2/configuration-migration.md) and
[agent receipt](m2-migration-agent-results-2026-10-30.md). Earlier remaining-migration notes are historical within
this implemented boundary.

30 October paired project/readout receipt: Intel Mac and representative shared
Chapman4 selected Python 3.11.14 authoring checks passed at
3769f5196f9be2c2581673f89c61ae2a472167d3: six examples from two caller directories,
66 rejection/recovery cases, immutable sources/recipe order and malformed CLI
controls. Protected installed files/checkouts stayed unchanged. See
[paired results](m2-project-contracts-paired-results-2026-10-30.md). Ready for bounded owner review; full M2 remains open.
No numerical/hardware execution or header-trust qualification is claimed. Preserve
evidence/tools; no rerun for this documentation receipt. Earlier pending-target
notes below are historical. Merge/cleanup requires owner instruction.


30 October next bounded M2 increment after accepted/merged PR #149 and clean
Mac/shared Chapman main ed949cab4f70381a1e187c7be691026c7fecf01c: owner authorized
[remaining project-domain authoring validation](../architecture/proposed/m2/project-contracts/README.md) and
[optional/amplifier-specific overscan](../architecture/proposed/overscan-readout-policy.md). Explicit omission requires no
region, defined geometry can be retained without subtraction, and enabled
subtraction requires valid selected-channel geometry. Distinguish available from
active amplifiers; no physical IDs/hardware counts inferred from legacy ordinals.
Header amplifier/scan values remain reported, unverified evidence; conflicts need
explicit review, not automatic header/config authority.
Python standard-library review validator and six examples only; ordinary native
engine/Pycavi/installation/numerics unchanged. Legacy mapper still needs retained
geometry and one active channel; no geometry-free/multi-amplifier execution claim.
Full M2/WAD/migration integration remains pending. Agent six-example/66-case
authoring checks passed; actual target authoring checks pending; preserve accepted native evidence/tools, no matrix replay. Owner review
precedes separately instructed merge/cleanup.


30 October paired typed-domain receipt: Intel Mac and representative shared
Chapman4 private C90 builds and all three focused TOML tests passed 3/3 at
920dd13251287c07ca9d9e3355e1cb9afcd38370. Exact legacy settings, subset controls,
151 catalog templates, 11 document/lifetime profiles and 25 domain/unit rejection
cases passed. Protected installed files/checkouts stayed unchanged. See
[paired results](m2-typed-domains-paired-results-2026-10-30.md). Ready for bounded owner review; full M2 remains open.
Preserve evidence/tools; no rebuild for this documentation receipt. Earlier
pending-target notes below are historical. Merge/cleanup requires owner instruction.


30 October third M2 increment after accepted/merged/cleaned PR #148 and clean
Mac/shared Chapman main 7e665da170e2e1af9f96a97e9f5bc2f6ebcfeef5: owner instructed
“Proceed” with [typed native domains and sources](../architecture/proposed/m2/typed-domains-and-sources.md). Input version 3 maps
all 151 getter templates into versioned instrument/detector, processing and
product mappings with explicit units, plus an owned immutable settings/source
document. Versions 1/2 remain supported. C90/C17 owns catalog/composition/report
logic; C99 remains parser-specific. Opt-in only; no normal engine/installation or
numerical changes. Full WAD/domain/migration/persistence work remains pending.
Build the normal engine and config_paf_snapshot/config_toml_snapshot/
cli_capture_probe/config_domains_probe; select only the three native_config_toml
compatibility/subset/domain checks. Agent C90/C17 3/3 and scoped sanitizer
checks passed; actual Mac/shared Chapman checks are pending;
preserve selected tools/evidence and do not replay the historical matrix.
No automatic merge/cleanup.

30 October paired subset receipt: Intel Mac and representative Chapman4 private
C90 builds and both focused TOML tests passed 2/2 at
d622bbec7e9784ab9fa6211080cfd4955ff3a08d. Original exact-setting/41-case controls,
16 composition profiles from two directories and 32 rejection/recovery cases
passed. Protected files/checkouts stayed unchanged. See [paired results](m2-toml-subsets-paired-results-2026-10-30.md).
Ready for bounded owner review; full M2 domain/unit/source/migration work remains
pending. This documentation update requires no repeated execution or installation.
Earlier target-pending notes below are historical. Merge/cleanup requires owner
instruction.


30 October next M2 increment after owner-accepted/merged PR #147 and clean
Mac/shared Chapman main 0550fb90215c636cc6b881eb67e221c24b5ed876: owner instructed
“Proceed” with [native subset composition](../architecture/proposed/m2/native-subset-composition.md). Version 2 adds containing-file
includes and explicit per-file numeric overrides, retaining standalone version 1.
Core composition stays C90/C17, parser shim C99; opt-in probes only, no normal
engine/installation or numerical change. Full domain/unit/source/migration work
remains M2. Agent C90/C17 two-test and scoped sanitizer checks passed; actual
Mac/representative Chapman checks for this increment are pending. Build the normal
engine and config_paf_snapshot/config_toml_snapshot/cli_capture_probe; select only
native_config_toml and native_config_toml_subsets. Preserve prior evidence/tools;
no historical matrix replay or automatic merge/cleanup.

30 October paired M2 target receipt: Intel Mac and representative Chapman4 private
C90 builds (normal engine and both probes) and native_config_toml passed at
b0ea0897ff2b5257eaf3bae0029b14a11a8f7152: all 585 OCAM / 249 WFI /
249 edge settings and 41 rejection/recovery cases. Protected files/checkouts
stayed unchanged. See [paired results](m2-native-toml-paired-results-2026-10-30.md). Ready for bounded owner review;
full M2 composition/override/unit/source/migration work remains pending. No test
replay or installation is needed for this documentation update. Earlier pending
target notes below are historical. Merge/cleanup requires owner instruction.


30 October 2026: M1 is owner-accepted and closed following merged PR #146
(`7d8da6b96b7b744a51e3847522a727e3f510c6f2`); the October 29 handoff and fresh
Mac evidence confirm clean main. M2 begins with an opt-in native TOML compatibility
reader producing the existing immutable configuration. Full domain composition,
precedence/unit/source provenance and migration remain subsequent M2 work; no
M3–M11 reordering, installation or processing. See [the M2 reader contract](../architecture/proposed/m2/native-compatibility-reader.md). Earlier pending-M1
notes below are historical. Actual Mac/shared Chapman integration checks pending.

29 October M1 closure review after accepted/merged PR #145 and clean Mac/shared Chapman main bacfa24fce45c0e7957bbc55f9cb6abfc7027219: the cumulative template/config/runtime/CLI/bindings/input/bias evidence supports proposed bounded M1 foundation closure. See [the M1 closure review](m1-closure-review-2026-10-29.md) for the requirement-by-requirement checklist, native-to-WAD conceptual/units/status crosswalk, accepted merge chain and explicit later-milestone boundaries. This is a read-only source/document/evidence review, not new execution or owner milestone acceptance. Reuse the latest paired C90 5/5 results and earlier scoped evidence; no test replay, tool qualification, installation, activation or scientific audit. #144 and wider memory limits remain open; do not claim whole-dependency OOM or thread safety. Preserve optional BPM / required M6a variances. Continue the original order at M2 after owner closure acceptance and authorized integration; other subroutines remain M5/M6, new algorithms at M6b–M6d. Do not start M2 code, merge or cleanup from this review alone.

29 October M1 first bias service ready for bounded owner review: returned Intel Mac and representative Chapman4 private C90 CMake builds (including the normal engine link) and all five focused CTests passed 5/5 at f5858310e505bfc1b137491dc35676b9245ce674. Both passed the eight-profile-per-instrument exact synthetic bias/legacy-FITS bridge contract, configuration/runtime checks, all 51 CLI cases and seventeen input cases from two directories. See [the paired bias-service receipt](m1-bias-paired-results-2026-10-29.md) for exact paths and limits. Protected files and checkouts stayed unchanged. #144 remains open; no target C17/sanitizer, whole-dependency OOM, thread-safety, scientific or complete-M1 claim. Grouped command adapters and general loader/path integration remain subsequent work; required variances stay M6a. Preserve all runs/tools/installations; no duplicate Chapman run or rebuild for this documentation receipt. Owner review precedes explicitly authorized merge/cleanup.

29 October M1 first bias service authorized after accepted PR #143 and clean Mac/shared Chapman main 98454283341a5bbce641119bed686fa56ff9c44b. The C90 mef_cal_bias service copies explicit one-detector raw ADU planes, preserves legacy overscan/trimming, rejection, median stacking and QC through a shared extracted kernel also used by mef_build_cal, and transfers an owned signal/request/QC result only on success. Explicit BPM omission is supported; selected BPM/calibrations, primary layouts and multiple detectors return unsupported. Variance is explicitly unavailable in this pre-M6a lane; required variance propagation remains M6a and new QC/RON estimators remain deferred. Agent C90/C17 and C90 ASan/UBSan exact synthetic service/legacy-FITS-bridge checks pass, as do focused configuration/runtime/51-case CLI/17-case input regressions. Actual Mac/representative Chapman C90 CMake build and five focused tests are pending; do not replay the historical matrix or requalify shared tools. #144 tracks retained Eclipse allocation-failure limitations, with no dependency OOM/thread-safety claim. The owner selected grouped commands such as mefpp cal bias, retaining mef_cal_bias for C; command adapters are subsequent M3–M6 work, not implemented here. No installation, observational reduction, automatic repair/retry, merge or cleanup.

29 October M1 explicit file/list requests ready for bounded review: returned Intel Mac and representative Chapman4 private C90 CMake builds and four focused CTests passed 4/4 at c9f974f680e72de48c6b0af24de3e1887f42a5e8. Both passed all 51 CLI cases and seventeen file/list cases from two unrelated directories, plus configuration/runtime controls. See [paired input-request receipt](m1-inputs-paired-results-2026-10-29.md) for exact paths and limits. No target C17/sanitizer, FITS geometry/applicability, applied-mask, thread-safety or full-M1 claim. Normal CLI/engine discovery and the first numerical service remain subsequent work; required variances stay M6a. Preserve all evidence/installations/tools; no duplicate Chapman test or rebuild for this documentation receipt. Owner review precedes explicit merge/cleanup.

29 October next M1 increment after accepted PR #142 / clean Mac/shared Chapman main 12f555ce4e14df0e292b629d54a3e496b94d8269: [explicit file/list request adapter](../architecture/proposed/m1/file-list-requests.md) reuses the existing Eclipse list parser with an explicit original member base and a supplied selected image catalogue. Ordered duplicate members expand to owned resolved requests; no IDs/HDU selections are invented. Selected files/calibrations must be readable regular files; omitted BPM triggers no lookup. Agent C90/C17 and C90 ASan/UBSan pass 17 cases from two unrelated directories, original-reader comparison and allocation/partial-I/O-failure controls. Actual Mac/representative Chapman CMake build and four focused tests remain pending. Normal CLI/engine discovery, FITS geometry validation, numerical services and M1 completion remain subsequent work; M3/M4 general resolver/layout scope is not claimed. Required variances stay at M6a. Preserve selected tools/evidence/installs; no repeat qualification, processing, automatic merge or cleanup.

29 October M1 resolved calibration/BPM bindings ready for bounded review: returned Intel Mac and representative Chapman4 private C90 CMake builds and all three focused tests passed 3/3, including all 51 CLI cases each, at b3c5948b6c729f396c3f87d441e5da8978b21358. See [paired bindings receipt](m1-bindings-paired-results-2026-10-29.md) for actual paths and limits. The runtime suite includes resolved role/BPM construction, rejection and ownership controls. No target C17/sanitizer, file applicability, applied masks, numerical processing or complete-M1 claim. Required variance support remains M6a. Preserve all runs/tools/installations; no duplicate Chapman execution or rebuild for this receipt. Owner review precedes authorized merge/cleanup; CLI/list integration and a concrete operation remain subsequent work.

29 October next M1 increment after accepted PR #141 / clean Mac/shared Chapman main 30ebe2a148021b2719bb8c5972b678150e86489c: [resolved calibration roles/BPM choices](../architecture/proposed/m1/resolved-calibration-bindings.md) adds an opt-in typed descriptor constructor and preserves its owned role/selection metadata through context cloning. Every input detector explicitly selects or omits BPM; contradictory metadata fails. Agent C90/C17 and C90 ASan/UBSan lifecycle controls pass, including 164 new allocation positions per profile; the 51-case C90 CLI regression also passes. Actual Mac/representative Chapman CMake checks remain pending. This is metadata validation, not file availability/dimensions, applied-mask status, CLI/list resolution or numerical execution; old engine BPM discovery is unchanged. Variances stay required at M6a, not implemented here. M1 remains incomplete; preserve selected tools, all prior evidence and user installations. No repeat tool qualification, processing, automatic merge or cleanup.

29 October owner addition after accepted/merged PR #140 and clean Mac/shared Chapman main 6a4d4d8ec078a3360a5a743845dcbe752cbc84bd: [optional BPM / required variance policy](../architecture/proposed/bpm-variance-policy.md) applies throughout the target chain. Explicitly omitted input BPM permits processing; selected missing/unreadable/incompatible BPM fails, with no fallback or default rediscovery. BPM creation still requires its requested BPM output; generated validity/rejection masks remain distinct. Variances stay at M6a and become required for supported signal/calibration products in the new variance-capable chain; remove its normal variance-off mode. Model-based raw variance initialization is permitted under an explicit qualified contract, not silent omission. Pre-M6a legacy products remain explicitly variance-unavailable. This delivery records policy/source boundaries only, not implemented no-BPM or variance processing. Carry it into the next M1 resolved-operation/concrete-service increment and subsequent notebooks; no installation, processing, repeat tool qualification, merge or cleanup from this update.

29 October M1 CLI capture ready for bounded review: returned Intel Mac and representative Chapman4 private C90 CMake builds and all three focused CTests passed 3/3, including 51 CLI cases each, at 3423aadb15ef6c6b4a48183ae05d4eab8d65673f. See [paired CLI receipt](m1-cli-paired-results-2026-10-29.md). #139 diagnostic bounds correction now has agent sanitizer and actual target verification; retain the original failed sanitizer evidence. #133 remains unchanged. No target C17/sanitizer, processing, installation or complete-M1 claim. Preserve selected tools and all evidence; no duplicate Chapman runs or rebuild for this documentation receipt. Owner review precedes merge/cleanup; resolved-operation integration and a concrete operation remain subsequent M1 work.

29 October M1 CLI compatibility increment authorized after PR #138 acceptance and clean main a58291a1f980fa1563ef89b49e01de4e4d47796c: [legacy CLI capture](../architecture/proposed/m1/cli-compatibility.md) preserves actual-loader bindings, save flags, original argv and effective settings without a second parser or fabricated single-operation/image identities. Agent C90/C17 and post-correction ASan/UBSan pass 51 cases, including twelve retained pilot forms and allocation/lifetime controls. The initial sanitizer run found legacy -d CCD[-1] in mef_bb_dump (#139); the correction is diagnostic bounds only, with original failure retained and target checks pending. #133 --ksize remains unchanged. No normal engine/decoder math, installation, FITS processing, notebook or QC change; M1 remains incomplete and target Mac/representative Chapman verification is next. Preserve all selected tools/evidence; no repeated tool qualification or automatic merge/cleanup.

29 October M1 runtime increment ready for bounded review: returned Mac and representative Chapman4 C90 CMake probe builds and both focused tests passed 2/2. See [paired runtime receipt](m1-runtime-paired-results-2026-10-29.md) for exact revisions, evidence and limits. No target C17/sanitizer or scientific-processing claim; preserve all private runs. Legacy CLI/list/save-flag/override adapters and one concrete operation remain subsequent M1 work. No duplicate Chapman/tool checks or further runs for this receipt. No merge or cleanup without owner instruction.

29 October next M1 increment authorized: owner instructed “Proceed” after PR #137 acceptance/merge and clean Mac/shared Chapman main 1d991a22a39d6133ab19721b7bb3a6dd11394264. [Owned runtime lifecycles](../architecture/proposed/m1/runtime-lifecycles.md) implement copied request descriptors, independent config/request contexts, result/error owners and explicit unsupported execution. Agent strict C90/C17, 268 transient/persistent allocation positions, ownership/independence and synthetic override controls pass; actual Mac/representative Chapman checks are pending. The normal CLI/numerical engine is untouched; legacy binding/override adapters and one concrete numerical operation remain subsequent M1 work. Preserve installed tools/evidence; no repeated shared-host tool qualification, processing, installation, merge or cleanup.

29 October M1 configuration increment ready for bounded review: returned Intel Mac and representative Chapman4 C90 CMake configure/probe builds and focused native_config_snapshot CTest passed. See [paired target receipt](m1-config-paired-results-2026-10-29.md). Both instrument maps, edge cases and ownership/failure controls pass; preserve all private builds and earlier evidence. No new processing, installation, scientific/QC behavior or complete-M1 acceptance. Request/context/result/error lifecycle and CLI-override capture remain subsequent M1 work. Chapman3/4 share one qualified tool environment; no duplicated host/tool checks. No merge or cleanup without owner instruction.

Owner-mandated tool selection, 29 October 2026: read [Selected project tools](selected-tools.md) before preparing host commands or builds. Always select the documented Mac/Chapman tools by absolute path, including CMake/CTest, compiler, Python, make/ar/ranlib and Mac SDK; do not infer availability from PATH or inherit the MPI/Mesa compiler selection. Consult the recorded private installations before proposing replacements, upgrades or manual build workarounds; never silently fall back. Chapman hosts are owner-confirmed identical and share home directories: reuse ~/opt/cmake-3.29.6/bin/{cmake,ctest} and the shared Python environment, with explicit devtoolset-10 GCC. Their CMake/CTest 3.29.6 paths/hashes are confirmed on Chapman4; system CMake 2.8.12.2 is not selected. The owner explicitly says Chapman3/4 are copycat: no further per-host tool availability/version/hash/ABI checks or duplicate qualification are needed; use the recorded tools directly. A new task's Chapman verification runs once on a representative Chapman host. Preserve global PATH/login files, production environments, external-executable configurations and accepted evidence. Use fresh task build directories and record actual execution host; shared tools do not imply every test ran on every host.

Production dependency gate, 29 October 2026: owner confirms the older Chapman machines are the main production systems. See [TOML/ASDF Chapman qualification](toml-asdf-chapman-qualification-2026-10-29.md). New parser/ASDF packages and their transitive dependencies must qualify on actual Chapman as well as Mac before adoption; Mac-only success is insufficient. Start with read-only chapman4 package/tool preflight, then a private constrained candidate, offline/interchange checks and explicit adoption evidence. Preserve working environments; no implicit NumPy/Astropy/compiler/C-standard upgrades. M0/M0a review package PR #134 is accepted/merged at b5bfd910614a786b95a598cb6295989c9f6602d6; remaining dependency/schema/effective-setting decisions are open. Development remains Mac, production qualification Chapman.

M0/M0a preparation, 29 October 2026: owner instructed "Proceed" after both hosts reached clean main 0fa9eaf157359a93f2a9196f6fff05dc3e96e220. [Contract review package](../architecture/proposed/m0-m0a/README.md) contains WAD/project sketches, 25 synthetic records, native boundary/ownership draft, source configuration ledger and focused checks. Development is on the Intel Mac; chapman4 is retained for later qualification. This increment is documentation/review fixtures only; M0/M0a contract acceptance and parser/schema/effective-setting choices remain pending, with no production/native/notebook changes, installation or reduction. CLI --ksize source finding is tracked separately as #133; do not repair it implicitly. PR #132 is already merged and both hosts were synchronized/cleaned; preserve all evidence and frozen amendments.

WAD/project direction approved for documentation, 29 October 2026: owner instructed "Proceed" after the Wenu Attribute Dictionary and ASDF processing-project proposals. See [WAD and ProcessingProject](../architecture/proposed/wad-processing-project.md), [target architecture revision 4](../architecture/proposed/pycavi-mefpp.md) and [implementation plan version 3](../architecture/proposed/implementation-plan.md). WAD defines shared data contracts; ASDF persists evolving project revisions, exact-version plans and run/product records; FITS retains pixels and TOML remains editable configuration. M0a establishes the minimal WAD/project foundation before native interfaces are finalized; M7 implements persistence and M8/M9 use the shared project service. Include the M3 inspector and M6a–M6d variance/linearity/dark/fringe scope already recorded. Concrete schemas/APIs/layout, implementation and numerical qualification remain pending; no production package, migration, installation, processing, merge or branch cleanup starts from this documentation update. Automatic cascades and parallel execution remain later passes. This supersedes earlier exploratory-only wording only for these owner-directed design elements; frozen amendments and accepted baselines remain unchanged.

Next-stage direction approved, 29 October 2026: [amendment v2.9](native-roadmap-amendment-v2.9-2026-10-29.md) authorizes analysis/design of mefpp subroutines, typed TOML configuration subsets, ASDF processing metadata referencing FITS-resident images, parallel-ready and single-detector interfaces, notebooks 01/03 and an optional mefppy Python library. See the [initial source analysis](mefpp-refactor-analysis-2026-10-29.md). TOML/ASDF-with-FITS is now the owner-selected design direction; exact schemas/adapters/bindings and directory layout remain proposals. Read-only larger Chapman inventory is pending actual-host evidence; do not assume its reductions are complete. No production implementation, installation, data migration or reduction rerun begins from this analysis. Stage 2/2.1 stay accepted; other exploratory WISDG/retrieval/layout ideas remain unadopted.

Stage 2.1 endpoint revised by owner, 29 October 2026: [immutable amendment v2.8](native-roadmap-amendment-v2.8-2026-10-29.md) makes the gate **current mefpp/Pycavi reduction through notebook 04: native calibration/science preprocessing, Python normalization, solve-field and WCS-corrected MEF assembly**. Keep one filter and at most five equal-integration-time science exposures per instrument; all three WFI partitions are authorized for the same five exposures in total. Notebook 05 extraction/SCAMP, SWarp, photometric/illumination work, downstream QC and final catalogues are outside Stage 2.1 and deferred to later workflow work. Older v2.7/full-chain completion wording is historical and superseded; do not reopen it as a closure requirement.

Both bounded instrument sets have now passed the Stage 2.1 functional endpoint on the Intel Mac: native preprocessing, Python normalization, solve-field and WCS-corrected MEFs. OCAM: five r_SDSS exposures at 20 s, one partition, 160 solved detector images. WFI: five BB#B/99_ESO842 exposures at 89.9177 s across three partitions, 40 solved detector images. Pixel/input preservation checks passed. See the [returned-result receipt](stage2-1-functional-results-2026-10-29.md) for evidence paths and limits. The owner accepted Stage 2.1 on 29 October 2026 and authorized merging PR #130 and cleaning its merged branch. Next substantive work is Stage 2A review; preserve all baseline products and evidence. Preserve the failed first WFI SCAMP attempt outside this gate; #30/#131 remain open for later production work. No scientific/Phase 3 certification or automatic Stage 2A/refactoring is claimed.

Historical Stage 2.1 addition, 28 October 2026 (endpoint superseded by v2.8): [immutable amendment v2.7](native-roadmap-amendment-v2.7-2026-10-28.md) inserts full processing of one complete OCAM dataset and one complete WFI dataset with current mefpp/Pycavi before Stage 2A. New order: accepted Stage 2 → **Stage 2.1 full current-workflow baseline** → Stage 2A review → extraction. One inventory/input/software lock, both existing complete supported reduction chains, retained outputs/QC and one baseline report; no new algorithm, format migration, automatic tuning, repeated memory matrix or duplicated platform run. Stage 2 stays accepted at 19/19 planned, 29 actual; #116 open/deferred, Phase 3 deferred. Planning only tonight; both user checkouts stay clean on main, no processing/installation/sync needed to review. Exploratory ASDF/WISDG/layout ideas are not adopted requirements.

Owner wrap-up accepted, 28 October 2026: owner instructed to leave #116 for now and finish clean for tomorrow. [Immutable v2.6](native-roadmap-amendment-v2.6-2026-10-28.md) records bounded Stage 2 acceptance with #116 OPEN/unresolved/deferred, named testing limits retained, and Phase 3 deferred outside this closure gate. [Final receipt/review](stage2-integrated-owner-review-2026-10-28.md) records all F1–F5 plus final C90 accepted: 19/19 planned + 10 retests = 29 actual, no further engine runs. Finish verified defect comments/closure, integrate PR #119 then #120, guard final-tree/host fast-forwards and remove only exact merged branches; preserve all raw data/runs/archives/builds/installations/configuration. No reinstall, new matrix/repair or automatic Stage 2A implementation. Tomorrow next topic: Stage 2A review after clean-main verification. This current instruction supersedes older pending-approval/Phase 3 closure-gate statements.

F5 accepted / final owner review ready, 28 October 2026: [F5 receipt](stage2-integrated-f5-acceptance-2026-10-28.md) independently verifies 94 files, six logs, both 391-entry source inventories, 12 exact products / 24 arrays, zero cleaned resources and stable descriptors. Fixed F1–F5 plus final Mac C90 are accepted/reused; **19/19 planned + 10 retests = 29 actual**, general rounds 2/2. No further engine runs planned. [Final owner decision](stage2-integrated-owner-review-2026-10-28.md) is complete; the later owner disposition below/above accepts bounded closure and defers Phase 3. #121–#124 meet bounded verification; comment before closure. #75/#116 remain open; #125/#128 deferred. No sync/rebuild/rerun needed for receipt, no automatic repair/new matrix/merge/deletion/installation/Stage 2A advance.

F5 prepared, 28 October 2026: actual Chapman preflight confirms clean main b0061b5 and qualified GCC10.2.1/CMake3.29.6/Python environment. [Final compact paired runner](stage2-integrated-f5-preparation-2026-10-28.md) prepares explicit C17/C90 builds and exactly one unchanged tiny integrated workflow per mode, pinned exact Mac products/metadata plus owner/accounting/descriptors. Python real-log/fixture/guard controls pass; target native execution pending, no native C/header changes or agent recipe launches. Current 17 planned + 10 retests = 27 actual; maximum after F5 19/19 and 29 actual, general rounds 2/2. One-use, stop at first finding; no extra matrix, external target diagnostics, automatic repair/retry, installation, merge or deletion. Then final owner/Phase 3 gap review; #116 unresolved, #125/#128 deferred.

Final Mac C90 accepted, 28 October 2026: [compile/link receipt](stage2-final-c90-mac-acceptance-2026-10-28.md) verifies six archive files, actual -std=c90 / AppleClang 15 / Darwin x86_64, successful final link and independently reconstructed 389-input source inventory. 66 retained warnings, no new warning messages versus prior C90; no warning-free claim. Binary stays Mac with host-verified hash. No native execution/installation; counts remain 17 planned + 10 retests = 27 actual, general rounds 2/2. Next compact Chapman3 C17/C90 pair and owner/Phase 3 gap review. Obtain actual Chapman host/Git state before its checkout mutation. Docs-only receipt needs no Mac sync/rebuild. No automatic repair/new matrix/merge/deletion/installation; #116 unresolved, #125/#128 deferred, #121–#124 await final disposition.

F4 accepted, 28 October 2026: [independent receipt](stage2-integrated-f4-acceptance-2026-10-28.md) verifies all 421 files, eleven same-process cycles, 66 exact products / 132 detector arrays, balanced owners, zero start/double-purge resources and stable descriptors. Current 17 planned + 10 retests = 27 actual; general rounds 2/2. Native source remains 68f0a04 (harness b93ffda). Next one final Mac C90 build without processing, paired compact Chapman3 C17/C90, then owner/Phase 3 gap review. Docs-only receipt needs no host sync/rerun; no automatic repair, new matrix, installation, merge or deletion. #116 unresolved; #125/#128 deferred; #121–#124 await final checkpoint. Earlier F4-pending statements are historical.

F3 accepted / F4 prepared, 28 October 2026: [independent F3 receipt](stage2-integrated-f3-acceptance-2026-10-28.md) verifies all 539 files, 35 logs, six builds, ten final failure roles and two exact tiny smokes; both historical failures remain preserved. #127/#129 meet bounded acceptance; #121–#124 await final checkpoint, #125/#128 deferred, #116 unresolved. Current 16 planned + 10 retests = 26 actual, general rounds 2/2. [Fixed F4](stage2-integrated-f4-preparation-2026-10-28.md) is prepared with Python guards/parser/fixture controls passed, actual Mac execution pending: reuse the qualified 68f0a04 instrumented binary for one warmup plus ten cycles in one process / one original planned launch. Native source unchanged; no rebuild, automatic repair/retry, new matrix, installation, merge or deletion. Then final Mac C90 build, paired compact Chapman3 C17/C90 and owner/Phase 3 gap review. Older pending/blocker paragraphs below are historical where superseded.

Approved cube exception v2.5, 28 October 2026: Fernando responded "authorized" to the two-C-file/two-added-retest proposal for #129. See [immutable amendment](native-roadmap-amendment-v2.5-2026-10-28.md) and [prepared repair/resume](stage2-integrated-cube-repair-2026-10-28.md). Cube constructor NULL/partial-owner guards and loaded-image cleanup are prepared; no header/recipe/qfits changes. C90/C17 syntax/actual constructor-loader controls and Python guards pass; Mac verification pending. One-use cube retry, exact successful tiny smoke, then the one original unrun cube leak role only if both pass. Current 23 actual; maximum after F3 26, general rounds stay 2/2. Preserve all evidence; no automatic repair/retry, new matrix, merge/deletion or installation.

F3 cube blocker, 28 October 2026: [#129 bounded decision](stage2-integrated-f3-cube-blocker-2026-10-28.md) records UBSan NULL member access after the declared cube injection at actual Mac source 2e3969c. Publication retry/smoke/leaks and both context-allocation lanes reportedly pass; full F3 archives pending. Current 15 planned + 8 retests = 23 actual, general rounds 2/2, v2.4 consumed. Proposed two-C-file NULL/partial-owner cleanup and two added retests require new explicit approval; no change/retry or later-row execution authorized. F1/F2 preserved; #125/#128 deferred, #127 awaits receipt, #116 unresolved.

Approved publication exception v2.4, 28 October 2026: Fernando instructed "Proceed" after the three-file/two-retest proposal and header clarification. See [immutable amendment](native-roadmap-amendment-v2.4-2026-10-28.md) and [prepared repair/resume](stage2-integrated-publication-repair-2026-10-28.md). #127 helper status/cleanup propagation is prepared in mefp_lib.c/.h and mefpp.c; qfits unchanged. C90/C17 syntax/helper units and Python guards pass; actual Mac acceptance pending. Exactly two added retests then five original unrun F3 roles only on success, one-use directory, no automatic retry/other repair. Current 17 actual launches; maximum 24 after F3; general rounds stay 2/2. #125/#128 deferred; no merge/deletion/installation.

F3 blocked, 28 October 2026: [publication-status defect #127](stage2-integrated-f3-publication-blocker-2026-10-28.md) confirmed by actual Mac terminal/read-only evidence at c722310: the master-bias target stays a protected directory, five other products are written, native exit is 0. Missing-list/corrupt-frame pass both lanes (user-reported); full F3 archive pending. Counts 11 planned + 6 retests = 17 actual, 2/2 general rounds; stop dependent work. Three-file publication-status repair and two added retests are proposals only, requiring owner approval/new amendment. No native modification, retry, later-row advance, merge/deletion or installation; preserve F1/F2.

F3 prepared, 28 October 2026: owner instructed "proceed" for the [five fixed failure cases](stage2-integrated-f3-preparation-2026-10-28.md). Test-only scoped context/cube NULL injection lives exclusively in private exports; no production/qfits changes. Python result/injection controls, actual archived-log parser controls and private C90/C17 syntax pass; Mac execution pending, current counters 6 planned + 6 retests = 12 actual, 2/2 general rounds. One-use F3 runner permits at most ten cases and stops on first finding. Preserve accepted F1/F2; no retry, repair, new matrix, merge, deletion or installation.

Integrated F1/F2 accepted, 28 October 2026: [inspected receipt](stage2-integrated-f1-f2-acceptance-2026-10-28.md) verifies archive 0ee502ce, all 416 files and 52 logs. F1 exact archived products and all four diagnostic logs pass; WFI host-verified reports agree exactly across three lanes (large WFI FITS remain on Mac). Both purges have zero resources, descriptors stable, external leaks zero. Counters 6 planned + 6 retests = 12 actual, 2/2 general rounds. #126 meets bounded acceptance; #125 stays deferred, #121–#124 await final checkpoint disposition, #116 unresolved. Next fixed row F3; F4/final C90/compact Chapman3 C17+C90 remain pending. Docs-only receipt needs no host sync/rerun; no merge/deletion/installation.

F2 continuation prepared, 28 October 2026: [one-use handoff](stage2-bpm-filename-resume-2026-10-28.md) validates the approved BPM filename correction without replaying passed F1. One ordinary retry then the two originally unrun diagnostic lanes; old F1 evidence is reverified and explicitly inherited. Python guards pass; Mac runtime remains pending. Current 9 actual launches; maximum 12 after these three cases. Keep general repair rounds 2/2, all gates/preservation active, #125 deferred and #126 open.

Approved BPM filename correction, 28 October 2026: [v2.3 amendment](native-roadmap-amendment-v2.3-2026-10-28.md) records Fernando's explicit caller-side correction in mefp_lib.c; fits_h.c remains unchanged. Immediate #126 and deferred qfits CONTINUE/safety #125 stay open. Agent C90/C17 syntax and basename controls pass; actual Mac retry is pending. User reports F1 all three lanes passed, F2 SIGILL; 4 planned + 5 retests = 9 launches, general repair count 2/2, v2.2 consumed. Preserve evidence; no old F1 resume, new matrix, merge, deletion or installation.

Approved bias-QC exception v2.2, 28 October 2026: Fernando instructed "proceed" for the four missing bias-QC releases in mef_bb_del and two tiny validations, followed by the original unrun campaign only if both pass. See [immutable amendment v2.2](native-roadmap-amendment-v2.2-2026-10-28.md). Keep the general repair count at 2/2; record the exception separately and permit it only once. No changed calculations, expectations, thresholds, further native correction, new matrix, merge or deletion. C90/C17 syntax and Python guard controls pass; actual Mac zero-resource verification is pending.

Integrated F1 memory finding, 28 October 2026: archive bd27d7c6 and all 141 file identities verify. Both corrected ordinary/instrumented products are exact and mutually equal, ownership/descriptors pass; 5847 allocations / 204017 bytes remain after both purges. Source-confirmed header, flat-scratch and per-extension metadata owners are tracked as #122–#124. Their lifetime-only correction and same-campaign final round 2 resume are prepared; actual corrected memory verification remains pending. Current counts: 2 planned launches, 1 correction retry, 3 actual launches, 1 round consumed. No third round, new matrix, changed expectations, merge/deletion or installation. See [final correction record](stage2-integrated-memory-correction-2026-10-28.md).

F1 integrated finding, 28 October 2026: the first ordinary Mac C17 run at fa2e5c2 returned 0 but failed exact known answers. Source tracing attributes the measured 1.111110687 bias offset to the rejected-mean overscan loop skipping one retained sample (#121). The one-line documented-mean correction and guarded same-campaign retry are prepared; actual corrected Mac verification is pending. One planned launch is consumed; global correction round 1/2 is prepared, with no retest executed. Expected arrays, exact gates, original failed evidence, installations and frozen contract bytes remain unchanged. See [bounded correction](stage2-integrated-overscan-correction-2026-10-28.md). No merge/deletion or new test matrix.

Integrated campaign preparation, 28 October 2026: the eleven-file WFI input-lock report is inspected and accepted for the bounded regression. The test-only existing-engine observer and Mac C17 F1/F2 runner are prepared; Python product-reader controls and C90/C17 syntax checks pass, actual native execution remains pending at 0/19 launches and 0/2 global correction rounds. See [integrated runner record](stage2-integrated-runner-2026-10-28.md). Preserve the single campaign pointer, all inputs/evidence/installations, frozen contract bytes and unresolved #116; no automatic retries, merge or branch deletion. F3–F5 remain the existing pending rows.

Frozen roadmap accepted, 28 October 2026: Fernando instructed "proceed" after reviewing v2.0 and requesting amendment v2.1 (paired final Chapman3 C17/C90 regression). The [accepted execution record](native-roadmap-v2-acceptance-2026-10-28.md) activates the frozen contract plus amendment; earlier proposal/pending-acceptance statements are historical. Begin one read-only WFI inventory and one integrated-fixture/harness preparation pass, then the fixed F1–F5 campaign: Mac C17 diagnostics, one final C90 build, paired compact Chapman3 closure, at most 19 planned native launches and two global correction/retest rounds. No new BPM-only matrix, automatic scope expansion, processing before input/reference lock, merge or branch deletion is authorized. Keep the frozen files byte-identical, all prior evidence and installations preserved, and #116 explicitly open pending its final-review disposition.

Owner-requested frozen-roadmap amendment v2.1, 28 October 2026: Fernando explicitly requested a compact final Chapman3 C90 regression together with C17. See [immutable amendment v2.1](native-roadmap-amendment-v2.1-2026-10-28.md). F5 now contains two compact target launches, one per mode; the campaign cap is 19 planned native launches. The original frozen v2.0 file/checksum, one-day preparation checkpoint, two global correction-round limit and all other scope/stopping rules remain unchanged. No build or processing starts from this documentation update.

Frozen simplification proposal requested, 28 October 2026: Fernando requested an immutable, finite roadmap instead of successive BPM matrices. Review [frozen native roadmap v2.0](native-roadmap-frozen-v2.0-2026-10-28.md) and its separate [fixed-row progress ledger](native-roadmap-v2-progress.md). It consolidates calibration/science collection through the existing engine, makes Mac C17 the diagnostic lane, retains one final C90 compatibility build, limits Chapman3 to one compact C17 regression, and caps the declared Stage 2 campaign at 18 planned launches plus at most two scoped correction rounds. Target external diagnostics and #116 remain honestly recorded; no implicit finding closure. The concrete proposal requires owner acceptance before execution; no new workload, merge or deletion starts from publication. Once published, never edit the frozen contract in place: amendments need explicit agreement and a new numbered file. This supersedes neither accepted evidence nor the old rules until that acceptance. Documentation review occurs on GitHub with both user hosts remaining on clean main; no diagnostic reruns or host synchronization are needed to review this document.

Integration authorized, 28 October 2026: Fernando explicitly instructed "merge and clean" for PR #117 after both actual Mac and Chapman3 checkouts were verified clean at 295fbe6844895bd4301ee51befdeb432d3ab8b90. Integrate the accepted two-extension test/evidence increment, synchronize both hosts to merged main by guarded fast-forward, and remove only test/stage2-bpm-wfi-multiext after verifying merge ancestry, exact branch tip and retained evidence. Preserve every run/archive/supplement/transfer/raw WFI or linearity frame/installation. #75/full S2-05, unresolved #116, remaining coverage and compatible target external diagnostics stay open; no S2-06 advance. This supersedes older no-merge/deletion-authorization statements only for PR #117 and this branch.

Current S2-05 two-extension target acceptance, 28 October 2026: [complete Chapman3 evidence inspected](stage2-bpm-multiext-chapman3-acceptance-2026-10-28.md) at 355034606cd6015b9e9abc99744973bf4c081b00. All 911 archive file identities plus manifest and all 39 command logs verify. Sixteen pairs / 32 roles exactly match accepted Mac masks/canonical headers; all 37 Mac-qualified source identities remain unchanged. C90/C17 GCC10.2.1/CMake3.29.6 builds, 192 allocator boundaries, 48 stable descriptor boundaries and zero double-purge resources pass. This accepts only the two-extension synthetic functional/accounting slice; compatible target external diagnostics, full S2-05/#75, unresolved #116 and remaining ownership/error/repeat/cache/mmap/swap gates stay open. Preserve every run/archive/transfer/raw WFI or linearity frame/installation. No S2-06 advance, merge or branch deletion authorized. Raw WFI inventory at /Users/fselman/Pictures/WFI remains pending.

Current S2-05 two-extension Mac acceptance, 28 October 2026: [full Mac evidence inspected](stage2-bpm-multiext-mac-acceptance-2026-10-28.md) at cea3e927f0392d8ec6c97cd40afbac2878aca03f. Both archives verify (1,259 original identities plus four recovered build logs); all 32 pairs / 64 roles preserve exact parent/mirrored masks and ordered metadata. All 79 command logs, four build inventories, 384 allocator and 96 descriptor boundaries and 16 zero-leak summaries verify. The unchanged-native-driver Chapman3 16-pair functional/accounting runner is prepared, not executed. #116 and full S2-05/#75, remaining ownership/error/repeat/cache/mmap/swap and compatible target external diagnostic gates remain open. Preserve all runs, archives, raw WFI/linearity data and installations; no S2-06 advance, merge or branch deletion authorized. Raw WFI inventory at /Users/fselman/Pictures/WFI remains pending.

Current S2-05 continuation, 28 October 2026: Fernando instructed "proceed" after supplied-bias integration at main 664f501fe723a924b6a2395d00f70cba1fb03ab7. Prepare test-only two-extension OmegaCAM/WFI BPM ownership qualification, Mac first, retaining exact accepted mask transforms, metadata, 0.5–1.5 thresholds, per-fd and double-purge gates. No production changes, new algorithms, observational reductions or installations. #116 remains unresolved/open; full S2-05/#75 and target external diagnostics remain open. No S2-06 advance or authorization to merge/delete this new branch. See [the bounded plan](stage2-bpm-wfi-multiext-2026-10-28.md).

Integration authorized, 28 October 2026: Fernando explicitly instructed "merge, sync, and clean" for PR #115 after inspecting Mac and Chapman3 supplied-bias evidence. Integrate the reviewed test/documentation increment, synchronize both hosts by guarded fast-forward, and remove only test/stage2-bpm-supplied-bias after verifying main ancestry and retained evidence. Preserve every run, archive, transfer copy, raw frame and installation. #116, full S2-05/#75, target external diagnostics and remaining coverage stay open; no S2-06 advance. This supersedes earlier no-merge/deletion-authorization statements for this branch only.

Current S2-05 supplied-bias acceptance, 28 October 2026: [Chapman3 full evidence inspected](stage2-bpm-bias-chapman3-acceptance-2026-10-28.md) at 10b3ca8285f886694fd0aa54197b8ba46f9cd1e4. All 225 file identities plus manifest verify; eight target pairs / 16 roles exactly match accepted Mac masks/canonical headers and inputs. Both C90/C17 builds, 23 command logs, owners, 24 post-call descriptor boundaries and double-purge zero-resource states pass. This accepts only the agreed supplied-bias target functional/accounting slice. #116 remains unresolved/open under Fernando's explicit sequencing agreement; full S2-05/#75, WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics remain open. Preserve all runs, archives, transfer copies and installations; no S2-06 advance or merge/deletion authorized.

Agreed #116 disposition, 28 October 2026: Fernando explicitly agreed to [bounded Chapman3 supplied-bias verification](stage2-bpm-bias-chapman3-plan-2026-10-28.md) before original descriptor-cause attribution. Keep #116 OPEN as unresolved/non-reproduced; stop further Mac repetition. Authorize only eight unchanged-driver/fixture C90/C17 target functional/accounting pairs with all current product, owner, descriptor and resource gates active. No gate weakening, compatible-target external diagnostic waiver, full S2-05/#75 closure or S2-06 advance. Stop on any recurrence and retain exact per-fd evidence. Record this agreement before preparing the target runner; preserve all original/diagnostic/repeat runs, transfers and installations. This supersedes earlier no-target-advance statements only for this explicit increment.

Current #116 diagnostic preparation, 28 October 2026: [ten focused fresh-process attempts prepared](stage2-bpm-bias-focused-repeat-2026-10-28.md) using the exact inspected c4912390 C90 instrumented binary and deterministic retained/robust supplied-bias inputs. No build, install, native driver, fixture, production source or gate changes. Python controls and readback of 16 retained logs pass; actual focused Mac execution is pending. Each attempt keeps exact product/resource/descriptor checks and fresh retained provenance. This is not S2-09 or new full-suite acceptance; nonreproduction does not waive #116. All original/diagnostic evidence and installations remain preserved; S2-05/#75, target advance and broader gates stay open.

Current S2-05 evidence inspection, 28 October 2026: [both supplied-bias Mac archives inspected](stage2-bpm-bias-mac-inspection-2026-10-28.md), SHA256 dbe6ba94, all 823 file identities plus manifest verified. All 64 native role products match accepted masks/canonical metadata and each other across the two runs; 94 command logs and 16 zero-leak summaries verified. Diagnostic c4912390 run passes all 16 pairs and 48 post-call descriptor boundaries. Original e7e8fbdc run retains one same-count descriptor identity mismatch with no per-fd attribution; #116 is still unresolved and not waived. This is successful rerun evidence, not full S2-05/#75 acceptance or permission for target/S2-06 advance. Preserve all original/diagnostic runs, transfer archive and installations; mandatory review before Stage 2A/extraction remains.

Current S2-05 finding, 28 October 2026: [supplied-bias descriptor diagnostic](stage2-bpm-bias-descriptor-diagnostic-2026-10-28.md) for #116 follows the retained Mac run at e7e8fbdc: all 16 functional pairs reported passed, one C90 instrumented resource case failed with count 4 to 4 but changed descriptor identity. Tracked resources reach zero after both purges in the inspected case; cause remains unresolved. Test-only per-descriptor detail/parser preparation preserves the existing gate, production sources, fixtures and prior evidence. Parser and C90/C17 syntax checks pass; actual Mac diagnostic rerun remains pending, followed by evidence review before target verification. Preserve the failed run and all installations; full S2-05/#75 and target diagnostics stay open, no weaker gate or S2-06 advance.

Current S2-05 continuation, 28 October 2026: [supplied-bias BPM ownership gate prepared](stage2-bpm-supplied-bias-2026-10-28.md) from synchronized main bf1c6afe0063ae62833efd04a9109ae5a3982cef after merged PR #114. Separate synthetic driver/observer and additive float32 fixtures preserve production source and accepted exact masks/metadata; Python-only preparation checks pass, actual Mac execution pending. Retain failed/corrected preparation and every earlier run/archive/installation. Chapman3 workloads remain paused pending host/hardware status from the latest handoff. Full S2-05/#75, WFI/multiple extensions and applicable error/repeat/cache/target external diagnostic gates stay open. No departure, S2-06 advance, merge or branch deletion approved; mandatory review before Stage 2A/extraction remains. Earlier PR #114 pending statements are historical.


Current S2-05 metadata integration, 27 October 2026: Fernando authorized merging PR #114 and cleaning only its merged test/stage2-bpm-metadata branch after verifying main ancestry/evidence. The [inspected Mac/Chapman3 populated-metadata acceptance](stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md) retains 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs with exact masks/headers, unchanged payloads and zero double-purge resources. Full S2-05/#75, supplied bias/WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics stay open. Preserve all runs, archives, transfer copies and installations. No departure, weaker gate or S2-06 advance approved; mandatory review before Stage 2A/extraction remains. This supersedes older PR #114 integration-pending/no-merge-authorization statements.


Current S2-05 populated-metadata acceptance, 27 October 2026: [Mac and Chapman3 evidence inspected](stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md). All 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs preserve exact masks, first-frame metadata and ordered canonical headers; 203 target archive identities verified, image payloads unchanged. Owners/descriptors and both zero-purge states pass. PR #114 awaits review/integration; no merge/deletion authorized. Full S2-05/#75, supplied bias/WFI/multiple extensions, applicable shared-helper/error/repeat/cache gates and compatible target external diagnostics remain open. Preserve all runs/archives/installations; no departure, weaker gate or S2-06 advance is approved. Mandatory review before Stage 2A/extraction remains. This supersedes older populated-metadata target-pending statements.


Current S2-05 populated-metadata Mac acceptance, 27 October 2026: [actual evidence inspected](stage2-bpm-metadata-mac-acceptance-2026-10-27.md) at c6a7a2bf05f8962cd9db4d72989b420f10159406. All 16 pairs / 32 native roles preserve exact reference masks, declared first-frame metadata and ordered/unaffected header cards; 372 archive identities verified, staged image payloads unchanged. Ownership/descriptors, both zero-purge states, ASan/UBSan and eight leak summaries pass. Unchanged native-driver Chapman3 C90/C17 functional/accounting runner is prepared, not executed. Full S2-05/#75, supplied bias/WFI/multiple extensions and applicable shared-helper/error/repeat/cache/target external diagnostic gates remain open. Preserve all evidence/installations; no merge/deletion, departure or S2-06 advance approved. Mandatory review before Stage 2A/extraction remains. This supersedes older metadata-Mac-pending statements.


Current S2-05 continuation, 27 October 2026: [populated FITS metadata gate prepared](stage2-bpm-metadata-2026-10-27.md) from main f377642ebfd8a8c0a43a99007f5543af34ff9c54. Deterministic header-only derivatives preserve accepted image bytes; unchanged native driver/observer and production .c/.h sources. Declare first-frame metadata, ordered comments/unaffected cards, exact masks and ownership/descriptor/double-purge contracts for 16 Mac C90/C17 instrumented/leaks pairs. Agent Python-only fixture/oracle checks pass; actual native Mac/target execution remains pending. Broader S2-05/#75, supplied bias/WFI/multiple extensions and applicable error/repeat/cache/target external diagnostics remain open. Preserve all evidence/installations; no departure, merge/deletion or advance to S2-06 approved. Mandatory review before Stage 2A/extraction remains.


Current S2-05 integration, 27 October 2026: Fernando authorized merge and merged-branch cleanup of PR #108 baseline and PR #113 ownership correction. The [inspected acceptance evidence](stage2-bpm-chapman3-acceptance-2026-10-27.md) preserves exact masks/headers for 16 Mac diagnostic/leaks pairs and 8 Chapman3 functional/accounting pairs, balanced owners/descriptors and zero double-purge resource state. Corrections #109–#112 meet their bounded acceptance criteria and are resolved with integration; broader #75/S2 and full S2-05, compatible target external diagnostics and remaining metadata/WFI/bias/multiextension/shared-helper/error/repeat/cache coverage remain open. Preserve all unique baseline/corrected/target runs, archives, transfer copies and installations. Only the two merged branches may be removed after verifying main ancestry/evidence. No scope departure or advance to S2-06 is approved; mandatory review before Stage 2A/extraction remains. This supersedes older integration-pending/no-merge-authorization statements.


Current S2-05 bounded acceptance, 27 October 2026: [Mac and Chapman3 BPM evidence inspected](stage2-bpm-chapman3-acceptance-2026-10-27.md): 16 Mac diagnostic/leaks pairs and 8 target functional/accounting pairs preserve exact reference masks and canonical headers; ownership/descriptors and both zero-purge states pass. All 200 target archive identities verified, all evidence/installations retained. Corrections #109–#112 await review/integration in PR stack #108/#113; no merge/deletion authorized. Compatible target external diagnostics and broader successful/error/repeat/cache coverage remain open; this first OmegaCAM/bias=NULL/single-extension subset does not complete S2-05 or #75/S2 or authorize advancing to S2-06. No departure is approved; prior agreement and mandatory review before Stage 2A/extraction remain. This supersedes older target-pending statements.


Current S2-05 Mac acceptance, 27 October 2026: [corrected BPM evidence inspected](stage2-bpm-mac-acceptance-2026-10-27.md) at 21ea905ff90d94a29cbe174c69674afef5d487eb: all 16 pairs preserve exact baseline/reference masks and headers; both purge boundaries reach zero, ownership/descriptors and ASan/UBSan/eight leaks summaries pass. All 369 archive identities verified. Unchanged-driver Chapman3 C90/C17 functional/accounting runner is prepared, actual execution pending; compatible target external diagnostics remain open. #109–#112/#75 and broader S2-05/S2 coverage stay open. Preserve failed/corrected evidence, runs and installations; no merge/deletion or departure is authorized. Mandatory review before Stage 2A/extraction remains. This supersedes earlier corrected-Mac-pending statements.


Current S2-05 correction, 27 October 2026: [focused ownership repair prepared](stage2-bpm-ownership-correction-2026-10-27.md) for #109–#112 after the inspected 16-pair failed baseline. Release owned cube frame lists, overscan scratch arrays, default pixelmap headers and BPM publication/context metadata after last use; preserve numerical/FITS behavior and all fixtures. Native observer/oracle unchanged; corrected runner pins exact failed-baseline headers/masks as well as #90 references. Actual corrected Mac and target verification remain pending; tickets and broader #75/S2 stay open. Preserve baseline/runs/installations; no merge/deletion, departure or reduced gate is approved. Mandatory review before Stage 2A/extraction remains.


Current S2-05 finding, 27 October 2026: [Mac baseline inspected](stage2-bpm-baseline-evidence-2026-10-27.md) at e3c6b463724725b7afb601b7cc0ebe28e24e161a: all 16 original/observer pairs pass numerically, but all retain 140 RAM allocations / 4472 bytes after both purges. Source/size attribution identifies #109 cube frame-list ownership, #110 overscan double buffer, #111 default pixelmap header and #112 BPM publication/context metadata. All baseline identities and outputs are verified and retained. Focused ownership repair is prepared for fresh Mac qualification; no corrected native or target acceptance yet. Preserve installations/runs, thresholds and numerical behavior; broader #75/S2, applicable error/repeat/cache gates and target external diagnostics remain open. Departures need prior agreement; review before Stage 2A/extraction remains mandatory.


Current S2-05 increment, 27 October 2026: [BPM ownership baseline prepared](stage2-bpm-ownership-2026-10-27.md) from main 9f09a7d8a9d09c9362c390b9351c2c2d467f986c. S2-04 and the full S2/prior-agreement documentation are integrated; both user clones were clean on that main and merged branches removed. Reuse unchanged #90 driver/fixtures and exact mask references for 16 Mac original/observer pairs across C90/C17 instrumented and separate leaks lanes. Production code/numerical behavior/installations stay unchanged; actual native execution and target verification pending. Retain all evidence and any findings. This is a first bounded S2-05 subset, not complete S2 acceptance or a departure; broader #75, target external diagnostics, S2-06 and remaining gates stay open. Prior agreement is required before departures, and mandatory review still precedes Stage 2A/extraction.


Agreed S2 milestone, 27 October 2026: the [full S2-00–S2-11 table](stage2-memory-qualification-2026-10-27.md#declared-test-matrix) records current bounded status after integration of PR #105. S2-05 BPM ownership is next, followed by S2-06 calibration ownership. Departures from the agreed S2 scope, row order, required coverage or completion criteria must be agreed with Fernando in advance and recorded before implementation. This includes deferring, omitting, substituting or weakening a gate. An unavailable tool or a proposed bounded milestone does not by itself authorize a departure. No departure is approved by this documentation update. Preserve evidence/installations and the mandatory review before Stage 2A/extraction.


Current S2-04 acceptance, 27 October 2026: [Mac and Chapman3 split/cache gates verified](stage2-split-chapman3-acceptance-2026-10-27.md): Mac 80 pairs with ASan/UBSan and separate leaks, target 40 uninstrumented functional/accounting pairs with exact Mac products. Controlled purges attribute all retained states and reach zero; context/descriptor checks pass. All original failed/baseline/control/target runs, archives, transfer copy and installations stay preserved. No production cleanup policy changes. PR #105 awaits review/integration; merge/deletion is not authorized. Next after integration is the bounded S2-05/06 calibration ownership baseline. #75/Stage 2, compatible target external diagnostics, broader injection/repeat/cache/mmap/swap and conditional wrappers remain open; early Phase 3 audit and mandatory review before Stage 2A/extraction still apply. This supersedes older target-pending statements below.


Current S2-04 Mac acceptance, 27 October 2026: [split/cache evidence inspected](stage2-split-mac-acceptance-2026-10-27.md) at 5322bb952e6958a93594692fcf1e96c58fbf800d: all 80 functional pairs pass, all 64 retained RAM states are attributed by controlled cache purge, both purge boundaries reach zero and descriptor identities remain unchanged. ASan/UBSan and 40 external leak summaries are clean. The unchanged-driver Chapman3 functional/accounting runner is prepared, not executed; its external diagnostic gap remains open. No production correction/cleanup-policy change or installation occurred. Preserve all three runs/archives/installations. PR #105 stays draft, #75/Stage 2 and broader repeat/cache/mmap/swap gates remain open; early Phase 3 audit and mandatory review before Stage 2A/extraction still apply. This supersedes older cache-control-pending statements below.


Current S2-04 update, 27 October 2026: [repaired Mac observer evidence inspected](stage2-split-observed-evidence-2026-10-27.md) at 97c086aaf301e7ae782c23ec9d67de1427351a8b: 80 functional pairs and descriptor/context observations pass; 64 cache-candidate RAM states keep the resource gate failed. #106 is verified on Mac; Linux observation remains untested. A test-only controlled double-purge check is prepared, not executed; no production cleanup policy changes. Preserve both runs/archives/installations. PR #105 remains draft; #75/Stage 2, target verification, broader repeat/cache/mmap/swap, early Phase 3 audit and mandatory review before Stage 2A/extraction remain open. This supersedes older observer-rerun-pending statements below.


Current S2-04 baseline, 27 October 2026: [first Mac run inspected](stage2-split-baseline-evidence-2026-10-27.md) completed 80 pairs; all ordinary functional contracts and actual paired output sets pass, but descriptor-observer completion fails (#106). A test-only enumeration/diagnostic repair is prepared; actual rerun pending. Sixty-four five-allocation RAM states match cache-size candidates but remain visible pending controlled attribution. No production fix, memory acceptance or target verification is claimed. Preserve all evidence/runs/installations; #75/Stage 2 remains open and mandatory review before Stage 2A/extraction still applies. This supersedes earlier S2-04 unexecuted statements below.

Current Stage 2 increment, 27 October 2026: PRs #102/#104 are merged; Mac and Chapman3 are clean on main f042b38d4018af28e04e20134fc8f2b375c489e4 and merged branches are removed. S2-03/#103 is verified. [S2-04 split I/O/publication ownership](stage2-split-ownership-2026-10-27.md) is prepared, not executed: retained synthetic output/failure checks plus context, allocator/mapping and descriptor observations, Mac first. Preserve all baseline/corrected evidence, runs and installations. #75, remaining Stage 2 gates and target compatible external diagnostics stay open; the early Phase 3 audit and mandatory review before Stage 2A/extraction remain pending. This supersedes older pending-integration statements below.

Current S2-03 acceptance, 27 October 2026: [bounded CLI/parser correction #103 verified](stage2-cli-chapman3-acceptance-2026-10-27.md) on Mac C90/C17 (224 CLI pairs/52 parser checks) and Chapman3 C90/C17 (112 pairs/26 checks, functional/accounting only). Failed baseline, stopped assertion attempt and corrected evidence are retained and inspected. PRs #102/#104 await integration; installations/runs stay preserved. Broader #75/Stage 2 and compatible target external diagnostics remain open. Next after integration is S2-04 split I/O/publication ownership; the early Phase 3 audit and mandatory review before Stage 2A/extraction remain pending. This supersedes older S2-03 target-pending statements below.

Current S2-03 Mac acceptance, 27 October 2026: [the corrected parser/CLI gate](stage2-cli-mac-acceptance-2026-10-27.md) passed all 224 CLI pairs and 52 focused parser checks at 18a196224ba436ae6d68d43b40c25245bbbf50d3. All 930 corrected/stopped-attempt archive identities were verified; failed baseline and stopped assertion attempt stay retained. The unchanged-driver Chapman3 functional/accounting runner is prepared, not executed. #103/#75 remain open; PRs #102/#104 remain unmerged. Preserve installations/runs; broader Stage 2 and compatible target diagnostic-tool coverage remain open. This supersedes older Mac-pending statements below.

Current S2-03 finding, 27 October 2026: the Mac baseline completed 224 CLI pairs with 100 instrumented failures at one bundled getopt name-comparison over-read (#103); all 112 uninstrumented leak/accounting pairs passed. Failed evidence is retained. A [minimal parser correction](stage2-getopt-correction-2026-10-27.md) is prepared; fresh Mac and unchanged Chapman3 verification remain pending. #103/#75 and Stage 2 remain open; preserve installations, baseline and all runs. This supersedes earlier S2-03 not-executed statements below.

Current Stage 2 integration, 27 October 2026: PRs #97/#98/#100/#101 are merged; Mac and Chapman3 are clean on main 9118ffaaec077eefb0d82a50d232721a9d280a3f and the merged branches are removed. All evidence/runs/installations are preserved. S2-02 context cleanup is accepted; S2-03 CLI/parser/engine ownership qualification is now prepared, not executed. See [the bounded S2-03 plan](stage2-cli-ownership-2026-10-27.md). #75, remaining Stage 2 gates and the Chapman3 diagnostic-tool gap stay open. The early Phase 3 audit is pending; mandatory review still precedes Stage 2A/extraction. This supersedes older pending-integration statements below.

Current Stage 2 acceptance, 27 October 2026: [context cleanup #99 is verified](stage2-context-chapman3-acceptance-2026-10-27.md) on Mac C90/C17 (48 cases) and Chapman3 C90/C17 (24 functional/accounting cases). Tool controls, failed baseline and corrected evidence are retained. PR stack #97/#98/#100/#101 awaits integration. #75 and the remaining Stage 2 normal/error/repeat, cache, allocation-failure and mapped/swap gates stay open; Chapman3 sanitizer/leak-tool coverage is not claimed. Next after integration is S2-03 CLI/parser/engine failure ownership, not Stage 2A/extraction. Keep run directories, archives and installations preserved. This status supersedes earlier pending context-cleanup statements below.


Current Stage 2 preparation, 27 October 2026: PRs #93/#95/#96 are merged; main e29a6201f01200708dc55c3439434a640cdc9ed0 contains the inspected normalization and BPM cleanup evidence. #90 is closed; its merged branch is deleted on GitHub, Mac and Chapman3. Both user checkouts are clean on that main. Run directories, archives and selected installations remain preserved. Next is the [Stage 2 ownership and test matrix](stage2-memory-qualification-2026-10-27.md): qualify leak/allocator visibility and the normal/error/repeat suite, Mac first and unchanged drivers/fixtures on Chapman3. #75 remains open; the earlier context-owner correction is already merged, not a new unfixed duplicate-destruction claim. Chapman3 functional #90 checks are not sanitizer acceptance. This preparation launches no build/test/install and changes no production allocator or numerical policy. Stop for the agreed review after Stage 2 before Stage 2A/extraction; the early Phase 3 audit remains pending.


Run provenance and cleanup rule, agreed 26 October 2026: every new build,
test and generated-output directory needs run-provenance.json identifying the
actual tested repository/branch/commit, dirty state, purpose, status and retention
role. New imaging work belongs under ~/Software/build/wenu-imaging/ on both
machines. Review and preserve unique data and required acceptance evidence in
the branch before merge; large external data need verified retained copies and
committed hash/location manifests. Verify evidence reached main before branch
deletion. Merging alone never authorizes deleting run directories or active
installations. Historical unknowns must remain explicit.
See [run provenance and evidence retention](run-provenance-and-retention.md).

Agreed roadmap revision, 26 October 2026: finish the bounded Stage 1
qualification, then Stage 2 memory/ownership qualification, then stop for a review
with Fernando before Stage 2A or component extraction. Start an early requirements
audit of ESO Phase 3 instructions to inform changes from their design, rather
than leaving compliance to final export. Treat ESO_Phase3 as a proposed named
reduction/product profile, with other profiles possible later; no profile engine
or compliance claim exists yet. Preserve common scientific correctness across
profiles. Extend Stage 2A product semantics, Stage 3 interfaces and Stage 4A–4D
characterization/variance/mask/final-product implementation as agreed.
Development and corrections are on the Mac; Chapman3 verifies target behavior.
Keep originals, normal installations and current 0.5–1.5 BPM bounds unchanged.
See [the current decision and qualification ledger](native-qualification-and-roadmap-2026-10-26.md).
Earlier dated pending/merge statements below are historical where superseded.


Chapman3 installed Pycavi acceptance, 26 October 2026: Fernando reports an
isolated wheel/target installation from source 805e6c63dea20e7f5e5ade816f6a6ddc90702d86
passed actual installed imports and all five wrapper failure regressions.
Actual installed Instrument/SciencePartition, copy_paf/check_mef_bpm,
mefpp_reduce_science and run_commands then passed four serial CN Ori runs
(C90/C17, NB_659/r_SDSS). Each selected the correct private engine and restored
cwd. Complete comparisons against the accepted direct-native outputs have exact
finite pixels in all 32 detectors, matching structure/scaling, and raw headers
differ only in generated primary ORIGFILE timestamps; MJD-END matches exactly.
Protected originals, references, staged inputs, installations and normal selections
were unchanged. See the current Chapman3 acceptance record for exact paths.
This completes the bounded installed-wrapper target gate; calibration construction,
broader memory/ownership, WFI/other platforms and scientific/Phase 3 gates remain
open. Review the stacked native PRs for integration; no merge or Git branch
deletion is authorized or performed by recording this result.

[Current acceptance and limits](chapman3-native-acceptance-2026-10-26.md).

Chapman3 installed/native acceptance and workspace completion, 26 October 2026:
Fernando reports source 805e6c63dea20e7f5e5ade816f6a6ddc90702d86 passed complete
private C90/C17 installations, manifest hashes and ten installed native failure
methods per mode. Direct CN Ori NB_659/r_SDSS comparisons passed in both modes:
all 32 detector arrays exact and finite with matching structure/scaling.
Raw headers differ only in generated ORIGFILE and reviewed MJD-END; independent
decimal arithmetic confirms the candidate values, while historical endpoints
match binary32 rounding. #24 stays open because common calibration-header time
variables remain float. The installed corrected Pycavi gate subsequently passed as recorded above;
calibration construction, memory and broader scientific/platform gates remain open.

Permanent reusable CMake/CTest 3.29.6 now live at ~/opt/cmake-3.29.6/bin/;
PATH/system tools are unchanged. Future builds, private qualification prefixes,
logs and retired evidence belong under ~/Software/build/wenu-imaging/.
All home wenu-* runs were reversibly relocated with journals; none remain.
Archived build trees retain historical absolute paths and are evidence only.
No normal engine/package switch, merge or Git branch cleanup occurred.

See [the current Chapman3 acceptance record](chapman3-native-acceptance-2026-10-26.md).

Chapman3 workspace location, requested 26 October 2026: put all future
wenu-imaging build/qualification work under ~/Software/build/wenu-imaging/,
not new ~/wenu-* directories. Use tools/ for private tool bundles and archive/
for retired/failed evidence, with task-specific source/build/prefix directories.
Do not blindly move active CMake trees or toolchains: caches/frontend state and
install scripts retain absolute paths. Inventory existing ~/wenu-* directories,
identify active consumers and preserve evidence before relocating finished work.
Use guarded reversible moves; never wildcard-delete runs, packages or data.
This housekeeping request does not authorize Git branch deletion or removal of
working Pycavi/native installations. Preserve original evidence paths in records
and map any relocation explicitly. Existing home runs remain unchanged until
inspected; the just-qualified native retry still needs its install/regression gate.

Chapman3 native build acceptance, 26 October 2026: Fernando reports source
805e6c63dea20e7f5e5ade816f6a6ddc90702d86 passed both required M_PI/shmget
configuration checks, 100-unit C90/C17 builds with the declared feature/language
flags, and all five CTest entries per mode. Evidence is
/home/fselman/wenu-chapman3-native-retry-xkuuu6qu/build-check.json and mode logs.
Protected tools, previous failed-run evidence, working Pycavi package and checkout
remained unchanged. This is build/test acceptance only: no installation or
observational reduction ran. Keep installed/native/Pycavi/calibration/memory and
wider Stage 1 gates distinct; no merge or normal selection switch is implied.

Chapman3 build portability correction, 26 October 2026 (#89): the first native
C90 build at 81a2f742ad439245739601444e7ffe70cb119037 stopped because glibc 2.17
does not recognize _DEFAULT_SOURCE, leaving M_PI hidden; System V headers also
warned about feature selection. Configuration passed, C17/tests/install were not
reached, and protected tools/working Python package stayed unchanged. Preserve
/home/fselman/wenu-chapman3-native-build-579kejl8 as failed-run evidence.
The bounded fix adds legacy BSD/SVID and POSIX.1-2008 definitions on Linux only,
uses the same definitions for capability probes and native targets, checks
required M_PI/shmget declarations early, and tests Linux header availability in
the native primitive executable. Numerical C files, explicit C90/C17 modes and
Darwin production definitions remain unchanged. Do not hardcode a replacement
M_PI, relax language modes, prune Eclipse or upgrade system glibc/compiler.
Repeat fresh actual Chapman3 builds/tests before installed/observational work.
See [the portability record](chapman3-feature-macros-2026-10-26.md). This does not
invalidate the separately recorded original Mac results at their tested commit;
new Linux target acceptance remains pending until returned actual-host evidence.

Mac correction acceptance, 26 October 2026: Fernando reports source
4ade8c52027c736a49b65da3bdb31f11b036693b passed fresh C90/C17 configure/make,
all five CTest entries per mode, both private runtime installations and installed
failure suites, isolated Python imports/five wrapper regressions, and complete
CP Pup direct and corrected-wrapper comparisons in both modes. All 32 detector
arrays are exact/finite, with matching structure and only generated primary
ORIGFILE timestamp differences in raw headers. Protected engines, input files,
Python packages and checkout remained unchanged. See
[the correction record](native-failure-correction-2026-10-26.md).
This is bounded Intel Mac acceptance using prebuilt calibrations. Stage 1 stays
open for calibration-building fixtures and Chapman3; WFI observational, memory,
other platform and scientific/Phase 3 gates remain open. Keep #75's broader
ownership/memory gate and the applicable linked target requirements open.
No normal engine/package switch, merge or cleanup has been performed. Documentation-
only acceptance updates need no reinstall or repeated processing.

## Change traceability, agreed 26 October 2026

Every code-changing commit must identify the relevant issue(s), explain its
purpose and record AI assistance in an Assisted-by trailer. Include the exact
model identifier only when reliably available; otherwise explicitly record that
it is unavailable. Never invent a model identity. Preserve these fields when
squashing. PR descriptions state scope, verification and remaining limitations.
Source comments explain reasons, assumptions and constraints; add issue references
where useful, without repetitive author/model markers beside every edit.

## Authorized failure correction, 26 October 2026

Fernando approved the described focused correction for #71/#75/#76/#85 and
Pycavi propagation (#86): checked default/explicit PAF loading; informational
requests without configuration; truthful parser/engine/split exits; one owner
for the published context; checked split writes/cleanup; native return-code
handling and cwd restoration in the science wrapper. The necessary PAF query
stale-value guard is #87. Preserve valid conversions, scientific arithmetic,
calibration parameters, shared normalization and current working installations.
See [the correction record](native-failure-correction-2026-10-26.md).
Keep issues open until their actual target gates pass. No merge, normal-engine
switch, full memory qualification or broad refactor is authorized by this item.

Mac normal installation accepted, 25 October 2026: Fernando reports the default
C90 ./configure; make; make install route, optional make check (four CTest entries),
complete installed payload/BPM pixels/checksums/CLI, byte-identical repeat install
and DESTDIR staging passed at source 7c5238f848284033bcef416ec5970a8004550afd.
See [frontend acceptance](native-frontend.md). Close bounded #84; preserve
the private installation at ~/wenu-mac-simple-install.7en8H834/install and the
selected historical engine/configuration. Next is CP Pup read-only preflight,
then isolated native regression; do not repeat installation checks unnecessarily.
No automatic observation run, engine switch, merge or cleanup is authorized.

Simple installation interface, approved 25 October 2026: Fernando requires
./configure; make; make install to remain the normal supported interface.
The new root/component wrappers delegate to CMake, select tools/check prerequisites
and propagate errors; optional make check is developer qualification. See
[frontend status](native-frontend.md). This is current Stage 1 work before
CP Pup comparison. Package-manager evaluation remains deferred. Agent Linux
frontend tests/integration passed with explicitly synthetic resource fixtures;
actual Mac frontend qualification is pending. Preserve existing private installs
and normal engine selection; no observation rerun, merge or cleanup starts here.

Current priority, approved 25 October 2026: Fernando defers pip-versus-Conda/
micromamba packaging as a TODO and resumes the existing native qualification.
See [current next work](roadmap.md) and native roadmap revision 1.4. Next is the
read-only CP Pup fixture/installed-candidate preflight, then isolated native
output comparison and remaining Stage 1 gates. Do not start package-manager
prototypes, provisioning, publication or bulk document moves as a prerequisite.
Preserve the qualified private installs and selected historical engine.

Documentation audience correction, 25 October 2026: Fernando requests a short
[user installation entry point](../installation.md) directly under docs; keep detailed
build/test/install material in [the developer guide](native-installation.md). Maintain
both with installation changes. Group developer navigation by topic; any later
physical move must update inbound links together. Package-manager review is a
proposal, not authorization to install/provision dependencies or publish binaries.
Conda/micromamba is the first recommended user-distribution evaluation; preserve
the existing CMake/CTest build and current working environments.

Maintained installation guide, approved 25 October 2026: Fernando requires
[the native installation guide](native-installation.md) under docs to stay current.
Update it in the same PR as changes to build/install tools, entry points,
platforms, resources/layout, selection, upgrade/rollback or qualification status.
Keep the Python installation hub, root README and build reference linked and
consistent; distinguish tested procedures from pending platform work.

Intel Mac native acceptance, 25 October 2026: Fernando reports C90/C17 native
builds, three CTest entries per mode, exact OCAM/WFI BPM pixels, checksum metadata
accounting, real private installations/repeats/installed CLI and C17 DESTDIR passed
at source 41c8e6a544c1bc5122dc558e0c8cc7904214e1d0. See
[the acceptance record](native-mac-build-install-acceptance.md). Historical engine and configuration
remain selected/unchanged. Observational pixel equivalence, installed wrapper,
calibration/WFI fixtures, failure/memory and chapman3 gates remain pending.
Prepare immutable observational fixtures next; publication starts no reduction,
engine switch, merge or branch cleanup. Earlier pending statuses below are historical.

Stage 4 amendment, 25 October 2026: Fernando requires creation and propagation
of per-pixel frame variances for science and calibration products. Follow
[roadmap revision 1.3](mefpp-modernization-roadmap-v1.md): squared units, masks, gain/RON,
calibration/parameter uncertainties, shared-normalization correlations and
Pycavi/resampling/photometry handoffs, with independent recovery tests. This is
future Stage 4 scope; preserve the current Stage 1 build-only boundary.

## Stage 1 isolated candidate, 25 October 2026

Stage 1 candidate implementation, 25 October 2026: Fernando authorized the isolated
bundled-source CMake build after reviewing stage 0 and reporting actual-Mac
fixture settings. See [candidate status](native-cmake-candidate.md)
and mefpp2/README.cmake.md. qfits is now under mefpp2/qfits5 in this candidate;
retain all 18 qfits and 79 Eclipse archive sources. Numerical algorithms,
allocator policy, existing installations and data remain unchanged. Agent Linux
GCC 13.3/CMake 3.29.6 code-only C90/C17 builds and three CTest entries per mode
passed; this is not Mac/chapman3 qualification. Actual BPM decompression, complete
runtime install and observational pixel equivalence are pending on the Mac.
No engine switch, observation rerun, memory-clean claim, merge or branch deletion
is authorized by this implementation. Earlier audit-only holds below are historical
where superseded by this bounded authorization.

## Stage 0 native build specification, 25 October 2026

Read [native build specification v1](native-build-specification-v1.md): minimum
static qfits -> Eclipse -> MEF/common -> mefpp targets; required PAF/BPM/license/
manifest payload; no optional legacy utilities in the first default candidate.
Retain full archive source lists; no pruning based on reachability. Generated
config headers must actually replace stale tracked include resolution.

Mac synthetic probe in wenu-mac-toolchain-01j1s5dt passed strict C90/C17 static
build/link and 2 CTest checks using explicit Xcode tools and CMake/CTest 3.29.3.
This is not native mefpp qualification. Proposed initial minimum is CMake 3.29;
record a reviewed change if chapman3 constraints justify another version.
Fresh observational manifests, real C90/C17 builds and Linux toolchain evidence
remain pending. The document defines tests/fixtures, not executed native coverage.
Preserve current engines, sources and products; implementation follows the
bounded stage-1 decision after specification review, not this documentation push.

Native roadmap revision 1.2, 25 October 2026: retain C89/C90 as the portable C
source baseline and explicitly qualify compilation and behavior in C17 mode.
C17 is a compatibility target, not a new source-feature baseline. Inventory
legacy/dependency extensions and isolate platform APIs; do not claim existing
strict compliance. Newer facilities need a reviewed exception. C23 checks are
optional. Mac compiler support is distinct from unperformed mefpp tests;
chapman3's inventoried GCC 4.8.5/Clang 3.4.2 cannot provide the C17 lane. Qualify
an isolated compatible compiler without implicitly replacing system tools or
upgrading glibc. This clarification authorizes documentation, not installation.

Roadmap v1 revision 1.1, 25 October 2026: extend data review to JWST, Roman,
Rubin, ELT and publicly documented future ESO archive plans, distinguishing
adopted standards from proposals/unknowns. Native Apple Silicon arm64 build/install
and functional acceptance is required; Rosetta is not acceptance. Extend the
parallel design assessment to optional threads within detectors and optional GPU
backends only after profiling/equivalence evidence, retaining a portable ANSI-C
CPU baseline, global resource limits and shared mosaic normalization. This is
planning authorization, not permission to add threading/GPU dependencies or run
new workloads. No accelerator backend or hardware purchase is selected.

Data-representation review added to native roadmap v1, 25 October 2026: insert
stage 2A immediately after memory qualification and before component contracts.
Review current accepted formats/metadata models and in-memory structures,
including FITS, HDF5, ASDF and Zarr, without preselecting a replacement. Preserve
FITS ingestion/interchange and originals; compare actual performance/fidelity
and ANSI-C/platform/dependency costs. Any new backend needs a separate reviewed
migration and renewed memory checks. See the version-1 native roadmap.

## Native roadmap version 1 and current architecture, 25 October 2026

Fernando authorizes the first roadmap and current-architecture documentation.
Read [roadmap v1](mefpp-modernization-roadmap-v1.md) and
[current mefpp architecture](mefpp-current-architecture.md). This dated planning
update supersedes older sequence descriptions: clean build/install on Intel Mac
then chapman3; memory/ownership/failure qualification; component contracts and
extraction; missing calibration services; single-detector CCD support; safe mosaic
parallelism; native Windows qualification; CMOS services last. Consider Windows
portability from the first build decision. CMake/CTest and component signatures
are recommendations for review, not selected/implemented tools or APIs.

Preserve common mosaic flat normalization and relative detector response.
mefpp_cal_lin is intended to cover non-linearity, shutter errors, gain and RON:
initial bias pairs, randomized integration times with consecutive flat pairs,
full-range acquisition to saturation, valid-range estimators and separate
calibration products. Select compatible measured gain/RON or explicit verified
instrument/mode defaults; record units/status/provenance. ESO CONAD/GAIN mappings
must be explicit. Include fringe-template construction plus separate Python
scaled subtraction. CMOS requires its own camera/mode review and qualification.

The current architecture is observed; target design is provisional. Maintain
version/revision records and discuss material changes before dependent work.
Documentation delivery does not authorize source moves/build changes/installs,
scientific changes, new concurrency, merges or cleanup. Existing tests and
actual-target evidence rules continue to apply.

## Current hold: architecture audit, then full roadmap, 25 October 2026

Fernando now requires an audit of how outdated the native build/organization
is against modern development practices, a diagram of the current structure
and a trace of Eclipse use/non-use. He intends eventual components for bias,
BPM, non-linearity determination/application, dome/sky/master flats and science.
Read [the architecture audit](native-architecture-audit-2026-10-25.md), #73
and its compiler-assisted evidence. It distinguishes potential function paths,
conservative object closure and actual runtime coverage; never label an
unreached function safe to delete or an existing linearity routine qualified.

The full roadmap must follow this audit and be reviewed/agreed before actual
modification work. This supersedes proceeding directly from #64/#72 to qfits
nesting/build fixes. No component move/split, build-system change, dependency/
compiler upgrade, installation, new concurrency or scientific change starts
from the audit alone. Compile-only analysis in disposable agent copies does
not qualify Mac/chapman3 builds or replace native runtime/scientific tests.

Preserve the two static-library boundaries and algorithm baselines while
assessing options. A modular C library and thin command interfaces are possible;
do not assume separate processes/repositories, a language rewrite or CMake is
already chosen. The roadmap must define stage contracts, ownership, detector
identity, units, masks, uncertainty/QC/provenance, error/restart and equivalence
gates. Source findings #74/#75/#76 remain uncorrected; existing installation/
native issues stay open. Later scientific parameter tuning remains deferred.

## Current authorized native installation audit, 25 October 2026

Fernando changed the order: bring roadmap point 5 forward, beginning with an
audit of mefpp/qfits installation and moving qfits under mefpp. Prioritize
Intel Mac clean build/install qualification, then chapman3. Read
[native installation audit](native-installation-audit-2026-10-25.md) and #64.
Initial audit probes are agent-host fixture evidence, not target qualification;
#65–#71 remain open. Proposed source location is mefpp2/qfits5, one canonical
copy, with retained APIs/licenses and explicit qfits -> Eclipse -> mefpp order.
The initial audit changes no native source layout/build or installed engine.

This explicit direction supersedes older deferral of all native work until
notebook/Python refactoring only for the bounded build/install task. The next
target action is read-only Mac compiler/resource/checkout inventory. Subsequent
corrections must be scoped to installation, preserve numerical behavior and
working native selections, use fresh source copies/private prefixes and record
actual compiler/archive/resource provenance. Do not upgrade compilers/libraries,
add native concurrency, change detector/science algorithms, or silently expand
into the complete mefpp audit. Mac acceptance precedes chapman3; an agent Linux
build is neither. Existing #23/#24/#13 and runtime finding #71 are separate
bounds; a successful exit alone never establishes native scientific success.

Resume remaining notebook/config-script/Python-audit work after this task;
scientific parameter tuning stays deferred until all fields are reduced.
PRs #57/#60/#63 are merged; the old review-branch wording below is historical.
Retain fresh actual-target guards and matching test explanations/comments.
No target install/source move is claimed by documentation delivery.

## Current Mac functional acceptance and handoff, 25 October 2026

Selected installed-library paths corresponding to notebooks 03–09 passed on
MC02VV0HPHTDG for one 20 s CP Pup r_SDSS exposure (32 detectors), including
plotting-enabled SCAMP, both illumination models, saved-grid readback, exact-ID
catalogues, two separate magnitude-only corrections and twelve decoded QC PNGs.
See [the Mac pilot](pilots/mac-cp-pup-2017-03-13/README.md) for evidence, hashes,
actual routines, settings and limits. Preserve all originals and accepted outputs.
Do not describe this as full notebook orchestration, multi-exposure stacking,
multi-filter Mac acceptance or scientific validation.

#61 closed as a bounded investigation: unchanged stars/parameters reproduce
the first-run equivalent solution within the observed numerical precision;
there is no externally imposed target zero point and no new algorithm/factor
change. Repeated flux scaling/serialization limits remain explicitly recorded.
#62 remains open for parameter-domain investigation; current Gaussian negative
RANGE and historical candidate fixed nugget ~0.015 are evidence, not approved
defaults. Fernando deferred scientific tuning until all fields are reduced.
SCAMP astrometry DR2 and calibration DR3/GSPC must not be conflated.

The current task is acceptance/roadmap documentation, not further processing.
Continue the agreed thin-notebook, derived configuration-script, used-library
audit, then mefpp sequence only within a separately agreed bounded next task.
Mac multi-exposure/filter checks, other platforms, WFI, native gaps and Phase 3
remain open. Earlier 24 October integration handoffs are historical: the five
qualified branches were merged/cleaned at main0591ba0. PRs #57/#60 and the Mac
acceptance documentation remain separate review branches; do not merge/delete
them without instruction. Obtain fresh actual Mac Git/environment evidence
before any synchronization or installation. Docs-only delivery needs no reinstall.

## Explain every functional and result-verification test, 25 October 2026

Fernando requires an explanation before every functional test and every test
that verifies results, including preflight checks, synthetic checks, installed
package checks, observational runs and read-only output checks. Give the
explanation before the command group or agent execution, not only when asked.
Keep it concise and specific to the test being proposed:

- State the purpose, inputs and settings, actions performed, and whether the
  test processes data, queries a service, writes outputs or only reads results.
- Name the actual Pycavi modules and subroutines/methods exercised, including
  relevant indirect calls and native programs. Distinguish production routines
  from orchestration and verification helpers; do not imply that a helper's
  independent calculation exercises a production implementation.
- State expected outputs, pass criteria and the test's limits. Distinguish
  wrapper completion, native execution, output integrity and scientific
  validation. Do not claim coverage of routines that the test does not call.
- After execution, explain what actually ran, what passed or failed, evidence
  and remaining limitations. Clearly identify checks still pending; a launch
  or zero wrapper exit code alone is not acceptance of the outputs.

In every testing script or copy-and-paste command group prepared or revised by
the agent, put short comments immediately before the relevant sections identifying
the tests or verification actions performed there. Use matching short names or
labels in the preceding user-facing explanation so the correspondence is easy
to follow. Every announced test/action must have a counterpart comment and
implementing code; every commented test/action must appear in the explanation
and match what its code actually does. Include preparation, guards, queries,
processing, output checks and preservation checks when those actions are part
of the test. Comments should explain sections, not narrate every code line.

Before supplying or executing a test, review the explanation, section comments
and executable code together for omissions or mismatches in both directions.
Do not silently reuse an uncommented older runner: add the matching comments in
a fresh test copy while preserving the original and its processing behavior.
Label launch-only steps and checks deferred to a later script explicitly; do not
describe a future output check as executed by the launch script.

These explanations do not authorize scientific tuning, broader validation,
extra processing or changes outside the currently approved task.

## Current authorized integration/cleanup, 24 October 2026

Fernando instructed merge and cleanup of the five qualified PRs #43, #45, #47,
#50 and #52. Integrate them into main in dependency order, retargeting stacked
PRs as their predecessors merge. Preserve all qualified heads/acceptance records;
verify every head is an ancestor and the final main tree equals the integrated
head. Cleanup only these merged branches with expected-tip and ancestry checks.
Obtain current actual chapman3 checkout evidence before local sync/cleanup and
provide guarded commands automatically. No reinstall, processing, query or
refit is required. This authorization does not close scientific/orchestration/
export/Mac gates or deferred #51; earlier handoffs below are historical.

## Current functional walkthrough handoff, 24 October 2026

The selected isolated OmegaCAM functional paths through notebook 09 passed:
baseline, Chebyshev and cubic Kriging applications, and twelve existing QC PNGs
across baseline/two corrected catalogues. Kriging QC records are in
notebook09-kriging-qc-saittxaz; all original/staged catalogue hashes remain
unchanged. #48 is closed after correction/installed/actual-copy evidence.
No independent scientific/model acceptance, complete notebook orchestration,
SkyMapper query, Mac qualification or Phase 3 compliance is claimed. #37/#38,
#51 and broader scientific/native/export gaps remain open. Preserve all inputs,
models, baseline and corrected outputs. PRs #43/#45/#47/#50/#52 are unmerged;
merging/cleanup needs the corresponding user instruction. Earlier handoffs below
are historical. Do not start a new implementation/refactor/query merely because
these selected functional checks passed.

## Current Kriging application coordinate correction, 24 October 2026

The existing before/after catalogue QC call generated and decoded all eight PNGs
without changing either source/staged catalogue (notebook09-qc-h6o98cy8). Address
#48 next: application axes must use the stored physical 1..ORIG_W/H endpoints,
actual grid shape and (y,x) orientation. Preserve cubic interpolation/default
solver, strict bounds, correction sign, null-safe writer and guards. No use of
the linear reader as a substitute, new model, refit or reference query. Test
source/installed behavior, then fresh target copies; keep #48 open until target
acceptance. #51 is deferred and does not affect the valid current QC inputs.
Earlier handoffs below are historical.

## Current notebook 09 QC handoff, 24 October 2026

Chebyshev application passed in notebook09-chebyshev-6xb3rgu1 with the existing
saved models: all expected magnitude changes, unchanged unrelated columns and
complete FITS extension metadata, 3718 exact IDs and 12741 missing masks, correct
provenance and byte-identical repeat calls. Baseline/model hashes are unchanged.
#49 is closed after source/installed and actual-copy evidence. Resume existing
catalogue QC on fresh staged baseline/corrected copies so fixed plot filenames
do not overwrite prior outputs. Keep current plot/reference settings and distinguish
functional generation from independent scientific acceptance. No new reference
query or fit; #48's separate Kriging application grid remains open. PRs #43/#45/
#47/#50 are unmerged. Earlier handoffs below are historical.

## Current notebook 09 baseline handoff, 24 October 2026

Baseline construction passed on chapman3 in notebook09-catalogue-95xc1kyz:
16459 paired-filter rows and 3718 distinct exact int64 Gaia associations, with
FITS null masks and all input hashes preserved. #46 is closed after correction,
installed tests and actual-output verification. Preserve baseline catalogue and
recovered references; continue functional correction only on fresh copies with
explicit saved models. Existing default Chebyshev application is distinct from
scientific model acceptance. Separate Kriging application coordinates fail at
valid edges (#48); do not treat corrected reader #41 as correcting that function.
PRs #43/#45/#47 remain unmerged; no new query, calibration, fitting or scientific
policy change. Earlier handoffs below are historical.

## Current catalogue handoff, 24 October 2026

#44 correction and bounded identity recovery passed chapman3 acceptance: four
raw/clean CSVs, zero coordinate differences, exact int64 CSV/Table/FITS round
trips, unchanged non-ID fields and original hashes. Resume notebook 09 with
fresh recovered catalogues under gaia-id-recovery-jh763zwi/recovered/catalogues;
do not replace historic calibration provenance or rerun calibration/models.
#41/#42 reader/08c checks also passed. PRs #43/#45 remain unmerged. Earlier
handoffs below are historical; independent science accuracy remains open.

## Current reader correction, 24 October 2026

Both 08b fits/grid serialization/QC passed. Target 08c diagnostics confirmed
#41 reader coordinate mapping errors despite exact saved grids; #42 records
misordered plotting arguments. Correct only reader axes and explicit plotting
bindings, preserving the linear method and immutable models. Verify existing
saved grids and fresh plots without refitting; keep #41/#42 open until target
verification. No science-image/catalogue correction, model/selection changes or
upgrades. Earlier dated handoffs below are historical; #37/#38 stay open.

## Current handoff, 24 October 2026

Fernando requested merging and cleaning the completed Chebyshev display work
before launching Kriging. #39 is closed after target plot/grid verification
without refitting. Notebook 08b imports/source identity and input selection
passed preflight: 583 r_SDSS and 580 NB_659 unique positions, no subsampling.
No variogram, Kriging fit or correction has run. Keep existing notebook settings
explicit, including its cleared clipping mask and four-pixel-offset diagnostic;
that diagnostic is not independent validation. Preserve all prior products and
leave #37/#38 and scientific accuracy/saturation investigations open.
The earlier dated handoffs below are historical.

## Current handoff, 23 October 2026

Both filters passed notebook 07 functional calibration checks on chapman3.
Fernando authorized merge/cleanup of completed branches, then a pause until
notebook 07b QC. Reuse the verified calibrated products and recorded queries;
do not rerun calibration. The r_SDSS saturation repair and installed writer
passed target verification (#33 closed). Keep #35/#36 scientific saturation
investigations, native #23/#24, independent accuracy and Mac qualification open.
The earlier walkthrough directions below record the agreed scope/history.

## Latest notebook walkthrough direction, 23 October 2026

Fernando declined the proposed standalone lunar/site-data check and explicitly
instructed continuing through the whole notebook sequence before deciding further
work. Resume the existing isolated OmegaCAM functional walkthrough at notebook
04, then SCAMP, SWarp and zpcal. Defer lunar/site-data to zpcal. This direction
supersedes the earlier requirement to close every dependency check before this
walkthrough; it does not accept the entire dependency baseline or authorize
general refactoring, replacement implementations or the systematic library/mefpp
audits. Preserve existing code/data/settings and use the established machine,
output-isolation and priority guards. Record actual results and resolve unexpected
failures before dependent stages. See the roadmap for the current boundary.

## Current approved metadata correction, 23 October 2026

Fernando approved the bounded Pycavi correction in #25: authoritative science
metadata at detector extraction/assembly, precise exposure endpoints, and
all-input coadd timing with total integration separate from native equivalent
exposure/gain. Preserve pixels, reuse solved WCS in fresh copies, and leave
native mefpp implementation (#23/#24) deferred. Continue the existing functional
notebook sequence through zpcal on chapman3, then retest on Mac. This supersedes
the older dependency-gate stop for this walkthrough; it does not authorize new
photometry functionality, broad refactoring or upgrades.

## Controlling dependency gate, 23 October 2026

Fernando clarified that dependency establishment and documentation on chapman3
come before the Pycavi workflow audit. Inventory Python packages, native engines,
resources, installation/build details, configuration, evidence and limitations.
Aim to align the Mac versions after capturing its actual imaging environment;
do not change either platform merely to force identical inventories. Diagnostic
wrappers calling existing functions are dependency evidence, not validation of
the complete orchestration or authorization to replace it. Keep the agreed
five-point sequence in roadmap.md. Future-proof Python only after those five
points are complete and the software works well, under a separately agreed plan.
The local Astrometry.net 0.98 installation was explicitly approved; this is not
blanket authorization for other engine or library upgrades. See the dated
chapman3 dependency inventory for current evidence and outstanding checks.

Status: accepted working agreement, with scope clarified by Fernando Selman on
20 October 2026. This is the canonical developer policy; the root AGENTS.md
directs agents here.

## Machine guards and process priority, 22 October 2026

### Actual user checkout verification, 23 October 2026

Before changing Git state or the installed wenu-imaging package on Fernando's
Mac or chapman3, inspect that computer's actual clone. Obtain fresh OS/hostname,
resolved checkout root, origin fetch/push URLs, branch, HEAD, upstream, full
`git status --porcelain` and interpreter/prefix evidence. Do this before fetch,
pull, switch, merge, reset, commit, push, cleanup or installation commands.
Do not substitute the agent workspace's state, yesterday's terminal output or a
directory name for this evidence. Use guards matching the established target;
preserve local edits and discuss unexpected branch/origin/divergence before
mutating it. A fetch changes Git references too. Do not assume the Mac imaging
clone is the separate Mac wenu clone. No Git software upgrade is authorized.

Fernando authorized the bounded remote-notebook launcher in
`Pycavi2/tools/start_remote_notebook.py` on 23 October. It starts the existing
chapman3 notebook workflow; it does not expand the reduction/refactoring scope.

Fernando develops on his Mac (wenu) and chapman3 (wenu-imaging) in parallel.
Every copy-and-paste command block must state its intended machine/project and
start with an automatic OS/hostname guard before any other work, including
environment activation, imports, Git operations, installs or file writes.
Do not rely on the displayed shell prompt or a previous block's successful check.
Group the block in a subshell so a guard failure stops that block without
closing the user's interactive terminal or SSH session.

For the current chapman3 imaging pilot, use this guard:

```bash
(
test "$(uname -s):$(hostname -s)" = "Linux:chapman3" || {
    echo "STOP: run this block on chapman3 for wenu-imaging." >&2
    exit 1
}
# Intended commands follow here.
)
```

The known Mac is MC02VV0HPHTDG (Darwin); the parallel wenu checkout is
`/Users/fselman/odrive/Dropbox/software/wenu`. The current chapman3 imaging
checkout is `$HOME/Software/wenu-imaging`. These are distinct projects. For
repository operations, additionally check the actual Git root, origin repository
and expected branch before modifying/fetching/installing; hostname alone cannot
distinguish checkouts. For Python processing, also check the resolved interpreter
prefix against the intended environment before scientific imports. The current
chapman3 prefix is `$HOME/.conda/envs/wenu-imaging`. Use the explicitly selected
target for future Mac imaging validation rather than requiring Linux for every
wenu-imaging task. Do not silently update a failed guard to match the current
terminal or infer the correct project from a directory's basename.

Future reduction launches must use `nice -n 10` on the Python parent so native
child processes inherit the lower CPU priority. Retain existing thread/resource
limits. Do not renice, restart or otherwise disturb an already running job
without instruction. The first pilot bias was already running when Fernando
requested this priority convention; it was left running as instructed.

Priority clarification approved 23 October: the Jupyter server and interactive
kernel run at normal niceness 0. Only batch processes and their descendants run
at niceness >=10. Launch scripts through `Pycavi2/tools/run_batch.py` in a
separate process, or use the existing `nice -n 10` terminal pattern. Never call
`os.nice`/`os.setpriority` in the interactive kernel to lower batch priority;
that also lowers later interaction. Direct heavy notebook-cell computations or
existing library calls do not automatically pass through the helper. Explicitly
launch those workloads in a batch process when using this priority split. Do not
claim all existing notebook runners were changed by this launcher utility.

These are instructions for preparing commands, not authorization for a new CLI,
host migration, workflow refactor or scheduler change.

## Packaging-stage authorization, 21 October 2026

Fernando authorized the packaging implementation, preserving the current
scientific dependencies and engines. **Any deviation from the roadmap must be
discussed with him and approved before proceeding.** Packaging validation does
not replace the later systematic Pycavi Python library audit or mefpp audit.
See installation.md for actual checks and pending platform gates.

### Bounded roadmap execution

Before implementation, identify the currently approved bounded task, its intended
result, scope limits, prerequisites and acceptance gate. A general "proceed"
applies to the task just discussed, not unmentioned stages or pending backlog.
If an extra item, new package/capability, scientific policy change, scope expansion
or changed order is needed, stop that affected implementation; read-only
assessment may continue. Discuss the concrete need, alternatives, consequences
and acceptance gate with Fernando, obtain explicit agreement and document the
agreed change in roadmap.md before implementing it. Keep proposals, partial
results and accepted completion distinct. Passing dependency checks does not
authorize starting the workflow audit. Routine choices and necessary fixes
inside the already approved boundary do not require repeated permission.

## Scope update, 21 October 2026

### Latest sequencing clarification

Fernando subsequently revised the proposed refactoring order:

1. Retire the historical `.py` reduction scripts; do not port their obsolete
   implementations. Streamline the notebooks using the existing libraries.
2. Once the notebook workflow is thin, provide runnable Python scripts driven
   by configuration files from that workflow, calling the same library routines.
3. Audit the library routines actually used by those notebooks systematically.
   Existing targeted fixes/tests do not establish that other routines are sound.
   Keep refactoring equivalence checks while thinning; the full scientific
   library audit follows the thin-notebook stage.
4. Audit mefpp after the Python-library audit. Read-only tracing of an existing
   native capability may inform the plan without starting the full C audit.

Keep packaging and Mac/Linux OmegaCAM execution as immediate prerequisites.
Postpone WFI implementation and dedicated validation until wenu-imaging works on
Mac and Linux. WFI remains a retained requirement; preserve its files/history and
record shared-code risks, but do not let WFI-specific work lead the current phase.
No Python/library/engine upgrades or backend replacements are authorized now.

BPM generation must be part of normal calibration creation, not permanently
defined as copying a static installed mask. Trace and validate the existing
mefpp construction path first, including required inputs, dependency order,
detector mapping, mask convention, thresholds, provenance and reuse rules.
Do not invent new BPM algorithms or silently change the working pilot products.

This clarification supersedes earlier suggestions to repair the legacy scripts
or begin implementation with WFI calibration preselection. Keep notebook/script
logic shared and preserve the single-node parallelism objective.

Fernando clarified the order of work after the portability audit:

- The immediate deliverable is properly packaged wenu-imaging with robust
  installed resources, explicit dependencies and reproducible installation.
  Debug and improve Pycavi before moving on to mefpp implementation.
- Do not upgrade Python libraries, Python itself, external astronomy engines,
  or replace backends in this stage. Prior modern-library probes are audit
  evidence only. Future compatibility means maintained interfaces, packaging,
  tests and recorded constraints now, with upgrades qualified separately later.
  Correctly declaring existing runtime imports is distinct from selecting a
  new library or upgrading the working environment.
- Audit single-chip CCD and CMOS requirements now, including primary-image and
  one-extension FITS layouts and detector-specific calibration/noise behavior.
  Audit findings do not establish implemented detector support.
- Audit every pipeline stage for single-node concurrency, aiming to parallelize
  every independent task where resource use and scientific dependencies permit.
  Cover exposure, detector, target/filter and independent QC work; coordinate
  outer processes and inner executable/BLAS threads within one node allocation.
- Dependency barriers and exclusive ownership of outputs remain mandatory.
  Joint fits and coadds may have parallel internals but cannot be replaced by
  independent per-frame results without preserving their scientific definition.
- Keep the present mefpp behavior for the packaging/Pycavi milestone. The later
  mefpp audit must consider both concurrent independent invocations and internal
  C parallelism rather than assuming one is automatically safe or sufficient.

This dated update controls the sequencing where earlier future-work paragraphs
differ. It does not authorize a broad rewrite, premature backend replacement,
archive submission or merging a proposal without instruction.

### Two user interfaces and WFI coverage

Fernando's intended design is thin, editable notebooks for learning and inspecting
data, plus Python scripts/configuration for repeatable headless processing. Both
must call the same library stage functions; do not maintain separate scientific
implementations or implement the script path by executing notebooks. Keep useful
parameter choices and inspection visible in notebooks. Retain WFI in the design,
but defer WFI implementation and validation as specified above, including its
calibration preselection, filter/metadata conventions and standards.
See [the two-interface review](pycavi-two-interface-review-2026-10-21.md).

## Purpose and scope

wenu-imaging coordinates Pycavi2 (Python), mefpp2 (ANSI C with embedded Eclipse),
and qfits52 (ANSI C FITS support) for WFI and OmegaCAM image reduction.
Maintain one canonical wenu-imaging repository containing the three components
as ordinary directories. Preserve the separate Python and C build/interface
boundaries; repository consolidation is not an algorithm rewrite.

The immediate delivery is a medium-sized OmegaCAM reduction set prepared for
submission as ESO Phase 3 science data products. Prioritize a reliable,
scientifically validated production path over new detector support or mefpp
parallelization. Data volume, filters and programme identifiers remain to be
inventoried; do not invent a size or throughput target.

The developer documentation and roadmap direction are accepted. The current
work is to record them and characterize the unchanged baseline. Documentation
in the parent repository may be maintained within the agreed scope. Changes to
component source, notebooks, scientific defaults, packaging, build scripts and component interfaces
require Fernando's explicit approval of an implementation stage. Publishing a
documentation proposal does not approve that stage. Do not merge a proposal
without instruction.

## Read first

- `docs/developer/architecture.md`: existing boundaries, baseline and open decisions.
- `docs/developer/roadmap.md`: platform requirements, phases and acceptance criteria.
- Any component-specific instructions before working inside a component directory.

Shared rules apply to work launched from this parent workspace. A component may
later need a concise local AGENTS.md for standalone work; creating those files
is a separate documentation change in the corresponding component directory.

## Platform priorities

- Urgent: macOS Intel and a Linux cluster whose distribution is pending.
- Required afterward: macOS Apple Silicon and Ubuntu Linux.
- The first identified machine runs macOS 13.7.8 (22H730), x86_64,
  Python 3.11.7 and Apple Clang 15.0.0 (clang-1500.1.0.2.5).
- These are requirements and reported environment facts, not validated support.
  Cluster distribution, scheduler, resource limits, Python/compiler versions
  and filesystem characteristics remain unknown. The execution model is confirmed:
  multiprocessing within a single node.

## Evidence and scientific preservation

Record exact repository commits, environment, commands and results. Distinguish
source observations, reproduced failures, inferred risks and open questions.
Do not describe syntax checks, skipped tests, an editable install or Linux-only
results as evidence of full installation, scientific correctness or macOS support.

Preserve algorithms, pixel units/precision, gain and exposure normalization,
FITS scaling and headers, extension/BPM mapping, calibration selection,
rejection thresholds, weights, photometric transformations and illumination
defaults unless separately approved. Record out-of-scope defects rather than
silently fixing them. Investigate unexpected numerical differences before
continuing dependent work.

Use immutable observational inputs and fresh output directories. Establish trusted
OmegaCAM reference products and comparison tolerances with Fernando first;
retain WFI regression coverage as changes affect shared code. Single-CCD and
single-CMOS support are future requirements, not established capabilities.
Never test by modifying original observational data or an existing working
installation. Builds and setup commands that generate files must use disposable
copies and a separate installation prefix during characterization.

## Minimal-change discipline

### Defect tickets, approved 23 October 2026

Open a GitHub issue for every distinct defect found. Search existing issues
first and update the matching ticket rather than duplicating it. Separate
confirmed failures, source findings and hypotheses. Record reproduction/evidence,
affected stage/platform, scope, acceptance criteria and relevant dependencies.
Link implementation commits/PRs to their tickets. An issue does not authorize
out-of-scope implementation or a change in scientific policy.

After correcting a defect, add a correction comment explaining the change,
commit/PR (or environmental remedy), tests and target verification actually
performed, and remaining limitations. Then close the ticket when its acceptance
criteria are met. Do not equate a written patch with target qualification, or
closure with a merged PR. Keep a native root-cause ticket open when only a
Python mitigation has been verified; link the separate mitigation ticket.
Retrospectively record defects corrected during the current walkthrough and
their existing evidence. Track subsequent findings the same way without asking
Fernando to repeat this authorization.

Trace and reuse existing functions before adding replacements. Prefer focused
refactoring and compatibility fixes. No broad rewrite, module relocation,
additional repository restructuring, workflow engine, build-system migration, dependency upgrade
campaign or unrelated cleanup without an explicit decision.

Treat repository names, Python distribution/import names, executables and C
library names as separate interfaces. The new parent name does not authorize
renaming `pycavi`, `mefpp`, qfits APIs or their installed resources.

External astronomy programs remain separately managed dependencies unless a
later decision changes that arrangement. Record and validate versions/paths;
do not vendor upstream source, download large index sets, or install system-wide
software as a side effect of an audit.

## Parallel processing and cluster work

The confirmed cluster model is multiprocessing within a single node. Distinguish
Python processes, threads inside external executables and the scheduler's
allocation. Multi-node/MPI support is outside the current scope. Do not assume a
scheduler brand, containers, root access or compute-node network access.

mefpp currently runs serially: it does not implement multiprocessing. Keep that
behavior for the initial operational OmegaCAM milestone. Do not introduce internal
parallelism or concurrent mefpp invocations merely because the pipeline supports
parallel astrometry. A mefpp multiprocessing design comes only after wenu-imaging
works correctly, with separate approval and equivalence/race/memory tests.

Once implementation is approved, respect allocated CPUs and memory rather than
the total resources visible on a node. Account for process-by-thread
oversubscription. Validate worker failure propagation, temporary/output path
isolation and restart behavior. Preserve scientific results when changing
concurrency. Record unknown cluster details without blocking independent Intel
Mac documentation and analysis.

## Git and review

Preserve attribution, license notices, history and unrelated local work. Use
focused branches. Inspect component status before checkout/update operations;
never discard local changes or overwrite an existing working installation.
The imported component histories remain available as ancestors of the monorepo.

After authorization, commit component changes in wenu-imaging. Cross-component
fixes may share a focused commit when they implement one agreed change.
The former component repositories remain historical references; do not push
ongoing development to them or to their original upstream projects.
Do not merge, delete branches, tag or release without instruction.

### PR executive summaries and Work chat — approved 28 October 2026

Every PR, including drafts and documentation-only PRs, must begin its description
with a concise executive summary for Fernando. State the purpose/problem, main
changes, checks actually passed, pending verification or material risks, and the
current status/next step. Distinguish prepared fixes from verified behavior and
functional success from memory or scientific acceptance. Keep implementation
details and full evidence below the summary.

Automatically display the same complete executive summary in the Work chat when
creating a PR or materially updating its scope, findings, validation or readiness;
include its link and current commit. Do not require Fernando to ask for it. Keep
the PR summary and chat summary consistent with the latest evidence. This reporting
rule adds no tests, host synchronization, execution gates or approval steps.

### Delivery handoff and local synchronization

These six rules were approved by Fernando on 23 October 2026, adapting the
applicable delivery procedure from `fselman/wenu` to this separate project.

1. **Automatic handoff.** After every push or merge, provide complete commands
   for synchronizing the applicable user computer, verifying its resulting
   commit and performing any authorized cleanup. Include this handoff without
   waiting for Fernando to ask. A pushed review branch and merged main require
   different commands; use the actual delivered ref and full expected SHA.
   When fresh local evidence is missing, provide the read-only preflight group
   immediately and explain which sync/cleanup group follows its review.
2. **Fresh target evidence.** Follow the existing actual-checkout verification
   rule before changing the user's clone or installation: hostname/OS, resolved
   checkout, origin fetch/push URLs, branch, HEAD, upstream, full working-tree
   status and Python environment. Never substitute agent-workspace evidence.
   Inspect returned output before dependent mutations and discuss unexpected
   differences. A failed guard is a stop, not permission to repair another host.
3. **Safe sync and authorized cleanup.** Use fast-forward updates and preserve
   local edits and unrelated branches. Verify ancestry before deleting an
   explicitly authorized merged branch; protect remote deletion against an
   unexpected changed tip. Do not force-reset, discard edits or delete branches
   just because a new task starts. Distinguish cleanup in the agent workspace,
   GitHub, chapman3 and Mac. Detect single-branch clones and explicitly fetch the
   delivered branch; explain any necessary change to their tracking configuration.
   If authentication fails, report the incomplete action without changing user
   credentials or requiring a graphical prompt/X11. Offer the applicable GitHub
   UI operation, then prune and verify after the user confirms completion.
4. **Complete command groups.** State the intended machine/project. Supply every
   command copy/paste ready in chat, with the OS/hostname guard first, exact
   verified checkout and applicable branch/SHA/clean/upstream checks. Use a
   subshell with fail-fast handling or equivalent dependent `&&` chaining; guard
   failure must stop the entire group without closing the user's terminal.
   Give one group at a time, then inspect its output before dependent operations.
   Respect normal notebook priority and lowered batch priority where applicable.
5. **Explicit delivery status.** Report branch/full commit or merge commit, PR,
   checks actually executed, remaining platform acceptance and any incomplete
   cleanup. Do not call written or unexecuted tests passing. Remote delivery
   does not synchronize the user's checkout, reinstall its wheel or update an
   already running kernel; state which of these actions actually occurred.
6. **Roadmap control.** Apply the bounded roadmap-execution rules above. Discuss
   and document changes of scope/order before implementation. Dependency
   qualification does not implicitly approve workflow refactoring, scientific
   changes or Python future-proofing. Publication of a plan is not acceptance
   of its pending implementation stages.

Use a dedicated branch and PR for the authorized item. Approval to implement
these instructions does not by itself authorize merging or deleting that new
branch; require the corresponding explicit instruction. Once a merge/cleanup
is explicitly authorized and its gates pass, do not request the same approval
again. Prefer the GitHub connector for repository delivery; user commands are
for their local synchronization/acceptance, not manual source editing on the
agent's behalf.

Report the problem addressed, changed files, checks actually run, unresolved
limitations and next decision. Keep working instructions and approved decisions
current as the project moves between phases.

## Delivery scope and future work

For the current OmegaCAM dataset, retain inputs and record processing versions,
configuration, calibrations, QC and product provenance. Scientific validation and
Phase 3 format/provenance validation are separate acceptance criteria. Verify the
applicable official ESO standard and validation tools when defining the exact
submission products; existing header-writing code alone proves no compliance.
Prepare a product inventory and release description. Archive submission and
publication remain actions requiring Fernando's explicit instruction.

After the operational OmegaCAM milestone, plan native mefpp multiprocessing and
support for single-CCD and single-CMOS reductions as separate work items. Audit
format assumptions and detector-specific calibration/noise behavior before
claiming single-detector support. Neither future item may delay the urgent
OmegaCAM production path without an explicit scope decision.
