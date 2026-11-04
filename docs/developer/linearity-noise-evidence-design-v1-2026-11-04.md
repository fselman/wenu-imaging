# Linearity Stage 8: bounded noise-evidence service — design candidate v1

4 November 2026. **Ready for owner review; not yet accepted or implemented.**
Issue #236, draft PR227. This specifies the next measurement service. It does
not select a stochastic noise model, estimate final covariance, run Monte Carlo
or fit correction coefficients. Once reviewed, retain this version; substantive
changes need a recorded amendment before dependent implementation.

## 1. Design and mathematical-guide lifecycle

Apply the owner's new scientific-subroutine policy: complete and human-review
the design before implementation; after the subroutine is complete, write its
mathematical guide from that reviewed design, explaining equations, assumptions,
units, numerical conventions, limitations and the connection to actual functions
and data structures, with algorithm references where appropriate. This document
is the design candidate for that review, not a claim of approval or a finished
post-implementation guide. No new scientific C/Python routine is written by it.

The existing accepted uncertainty policy remains controlling:
[linearity-uncertainty-review-2026-11-03.md](linearity-uncertainty-review-2026-11-03.md).
Measurement precedes model choice. Raw RON, ordinary pair variance and original
frame order stay unchanged. A future specified model propagates through actual
scan and median operations; covariance stays fixed within each fit, with a
separate sensitivity/outer propagation for uncertainty in estimated weights.

## 2. Completed baseline and purpose

All32 detectors have master-bias candidates, raw pair/gain/RON diagnostics and
3200 admitted corrected observations from160 approved physical sites through20
original flats. The corrected observations are saved in1088 shared ASDF records
at ocam-corrected-sample-asdf-xm1ngkg_/persistence. Do not repeat those recipes,
change those products or replace selected pixels. The joint numerical fitter is
qualified for supplied covariance; a measured instrument covariance is missing.

Acquire the additional bias/scan evidence that existing saved summaries omit.
The data must let us examine temporal bias variation, physical electronic-read
structure, shared scan corrections, and the actual selected median master before
choosing independence, pooling/distribution assumptions or simulation parameters.
It must not turn raw scan scatter or total raw-pair variance into an uncertainty
estimate by naming it so. This stage produces replayable evidence, not weights.

## 3. Fixed observations, population and coordinates

Use exactly the same normal/ordered OmegaCAM1x1 configuration, all32 detector/
amplifier identities, approved160 active/raw site coordinates,20 original flats,
10 original biases, structural BPM1=good and32 existing active masters. Preserve
independent saved per-file HDU maps and native geometry slots; no HDU=slot rule.
All coordinates are inclusive FITS1-based; arrays remain unrotated.

Biases retain original inventory indices0..9 and explicit role bias. Flats retain
original indices10..29, actual header durations and nonconsecutive pair IDs.
Do not infer a role from a duration or invent bias pairs. The original first-two
raw RON inputs remain unchanged. Bias exposure metadata may be zero; preserve it
using an explicit role-aware reader. Existing positive-flat-time services are
not relaxed to accept biases. Reject ambiguous/nonfinite/negative header times;
flat times must remain positive. No exposure rounding or lamp normalization.

Read all10 bias frames for evidence, including the frame rejected by a particular
master. Preserve that detector's existing accepted/rejected decision. Reconstruct
its master only from its recorded accepted members; never rerun mean rejection
or replace9/10 by10/10. CCD69/74/77/84/85 each have9 accepted frames; others10.
The BPM remains an active-pixel qualification, never an electronic-scan mask.
Retain values and eligibility flags rather than silently changing membership.

The approved sites occupy3 distinct physical rows per detector,96 rows total.
For example:

| Detector | Active rows | Corresponding raw rows |
|---|---|---|
| CCD65 |384,2045,3707|388,2049,3711|
| CCD96 |385,2047,3708|489,2151,3812|

A scan trace is collected once for a frame/detector/amplifier/row even when two
sites share it. Reference that shared trace from both site rows. Preserve frame
and physical read position so correlations between pixels, rows, outputs and
exposures can be examined later; independence is not assumed by this export.

## 4. Exact scan estimator and pixel arithmetic

For the enabled electronic reads v in a selected row, sort the n values and
reject the configured l lowest and h highest values. Mathematically,

    T(v) = pix[ sum(v_(k), k=l+1..n-h) / (n-l-h) ].

Here pix is conversion to the build's native pixelvalue type. The sum is
accumulated in double by function1d_average_reject_checked, then converted to
pixelvalue. Reuse that routine; do not write another trimmed-mean estimator.
Record enabled band bounds, scan width, l/h, retained count and returned value.
The helper copies its input; preserve the original scan reads in physical order.

Canonical PAF SHA256 is
709d65acdeea6c889ed1468cbb3966d5de93ec654ee030032a096ca12624333f.
It enables overscan only and rejects10 low/10 high values. Sixteen detectors use
43 reads (23 kept); sixteen use44 reads (24 kept). Bounds, not an assumed common
width, determine these counts. No new scan sigma clipping or saturation exclusion
is introduced: the existing finite-read/order-rejection policy stays unchanged.
Do not mark particular tied physical reads as retained/rejected when the native
helper supplies no such identity contract. Export all reads plus the estimator
and rejection counts; repeated values at a boundary remain replayable.

For a selected raw active pixel D_p in a row with correction T_y, retain

    U_p = pix(D_p - T_y),
    S_p = pix(U_p - B_p)                 [flat replay only].

Preserve the intermediate native rounding and the actual loaded FITS scaling.
Do not combine both subtractions into a different double expression. Record the
pixelvalue representation/build information. Compare diagnostic flat replay with
the already archived3200 native corrected values exactly on the same build;
there is no invented tolerance or automatic adjustment if a value differs.

BPM/saturation/finite/admission flags are recorded with raw and intermediate
values. Bias U values are diagnostic scan-corrected biases, not flat signals or
independent observations of a master constructed from those same frames. A bad
value is explicit; no nearby site, row or exposure is substituted. Invalid scan
inputs or inability to reproduce the required calibration state stop the run.

## 5. Exact median-master replay

Let A_a be the recorded accepted-bias membership for amplifier a. The existing
master at a selected site is

    B_p = M_Eclipse({ U_pk : k in A_a }).

Reuse median_pixelvalue on an owned copy of that site's accepted timeline; it
modifies its input. cube_avg_median uses this same routine. For this dataset:

| Accepted frames | Existing estimator |
|---|---|
|9|fifth ordered value (one-based)|
|10|fifth ordered value: lower of the two middle values|

The ten-frame estimator is not the average of the middle two. Preserve this
legacy convention; changing it would be a separate scientific/numerical change.
At160 sites,25 have9 accepted inputs and135 have10. A scalar replay at those
sites must equal the stored master pixel under native precision. Do not rebuild
or rewrite the full master image. A mismatch is a finding and stops dependent
work; do not select a different median convention to hide it.

Replayed master values are consistency evidence, not estimates of Var(B_p).
Raw RON²/N is not assigned to a median. Its noise distribution and covariance
still require a justified model and propagation through this exact estimator.

## 6. Native evidence products

The exact counts below follow from the approved metadata; they are expectations
for this dataset, not new generic scientific minimums.

| Transport | Expected rows | Contents |
|---|---:|---|
|site_samples.tsv|4800|160sites × (10bias+20flat): original role/index/asset/HDU/time, detector/amplifier/slot, source ROI, active/raw coordinates, raw pixel, shared scan-trace key, scan-corrected value, recorded master membership and eligibility flags; flat replay value and link to archived sample|
|scan_reads.tsv|125280|all enabled raw electronic reads for selected rows, physical scan x/y, band, source frame and shared trace key; no detector BPM applied|
|scan_estimates.tsv|2880|96distinct rows ×30frames: native estimator value, bounds, supplied/kept counts and low/high rejection counts; no claimed standard error|
|master_replay.tsv|160|selected master pixel, exact scalar replay, accepted count/membership and equality state|

Counts deduplicate common site rows, never the actual reads used by an estimator.
The scan-read total is 16×3×30×43 +16×3×30×44. Site rows comprise1600 bias and3200
flat records. Retain role-specific nullable fields instead of inventing a bias
pair ID or positive exposure. The master-replay membership stays explicit.

Native metadata also includes effective configuration, original identity/HDU
bindings, actual pixel type, original membership, source artifact hashes and a
completion marker. A native marker alone is not overall source-preservation proof.
Use full-precision numerical transport, explicit schema versions, units and
availability. Shared ASDF is the saved representation after global source checks,
through the existing common factory/writer/reader/traversal; native tables remain
retained intermediate transports. Original corrected-sample ASDF is immutable.
Plots and HTML are independent later consumers, not measurement side effects.

## 7. Proposed implementation boundary and reuse map

Names below are proposed interfaces, not existing functions or implemented code.

| Boundary | Proposed responsibility | Existing implementation reused |
|---|---|---|
|mef_noise_evidence_collect, internal C17 service|one borrowed raw plane, bound configuration/identity, explicit frame role and selected sites; return owned site/scan evidence without modifying the raw plane|mef_config_bias_settings; function1d_average_reject_checked; existing pixelvalue arithmetic|
|master replay helper|consume copied selected timelines and fixed recorded membership; compare with borrowed master pixels|median_pixelvalue; cube_avg_median convention; no new stack algorithm|
|mefpp_noise_evidence, opt-in native command|explicit per-detector source plans and role-aware times, selected plane loading, sequential service calls and native transports|M4 layout/binding/loading; existing PAF/ROI readers and compatible raw-selection transport helpers|
|serial project controller|derive inputs from completed metadata/ASDF and independent header maps; guard source files/products; stop first failure|completed raw/bias/sample run receipts and existing single-use serial/fingerprint patterns|
|noise-evidence ASDF adapter|typed/native/core consistency, units/identities, frozen master and sample provenance|unchanged QcRecipe/write_record/read_record/traverse_records|

The proposed service signature is

    mef_status mef_noise_evidence_collect(
        const mef_noise_evidence_request *, const mef_allocator *,
        mef_noise_evidence_result **out);

Its request contains a borrowed raw image, active master/BPM views, configuration
and resolved detector/slot identity; one explicitly typed frame descriptor
(role, original index/asset/HDU, header seconds and membership state); five
approved site descriptors; explicit row/read/result limits; and the expected
flat samples when role=flat. The result owns copied identity/role/site/scan
metadata, raw/intermediate native values, shared-row references, flags and replay
states. Bias membership is included/excluded; flat membership is not_applicable,
not a false rejection. Bias flat-replay fields are unavailable, not numerical0.
All frame descriptors and bounds are caller-supplied; the service chooses none.
The file caller retains only the50 corrected-bias scalars per detector needed
for its five membership-conditioned median replays while streaming frames.

The four native table kinds above also define four per-detector ASDF table
products with explicit table selectors. Reuse local frozen copies/references to
the existing master and corrected-sample QC graphs; a bias rejected by the old
master can still be used as diagnostic input without changing its old master
participation. Share input records within the new assessment instead of rebuilding
source QC. The adapter preserves each table's native text/hash, typed values,
units, role-specific availability, trace identity and recorded membership. This
requires no common-schema change or new QC factory.

The native file request retains the existing20-flat raw-selection plan and
supplies a separate explicit ten-bias membership table, master references and
the frozen expected-flat sample table for replay validation.
The first-two raw-bias references must match their recorded RON provenance. Do
not alter the old two-bias raw-pair parser or its numerical services merely to
accept ten biases. Each new source binds independently; no fabricated ordinal
mapping. The planned bias-role reader accepts zero without weakening the existing
positive-time flat contract. Missing/duplicate cards and incompatible binding fail.

One detector at a time and one raw plane at a time: retain its master/BPM while
streaming30 raw frames. Do not allocate a30-plane cube or all32 detectors. The
current logical pixel ceiling for raw+active master+BPM is25728808 pixels, derived
from2144×4200 and two2044×4091 active planes. This counts logical loaded pixels,
not total process memory or dependency scratch. Record actual pixel type and
explicit output-row/owner budgets; do not claim global dependency-OOM coverage.

Inputs remain borrowed/immutable; service results own the evidence after inputs
are released. Reject occupied output owners, invalid dimensions/duplicate sites,
invalid role/time, invalid membership/scan bounds and inconsistent references.
Partial failures expose no completed owner and free new service-owned allocations.
Existing Eclipse/qfits allocation policies remain outside a new broad safety claim.

## 8. Source admission and one-use execution

There are63 unique image inputs:30 raw frames,32 existing masters and the same
structural BPM. Compare full-file hashes with the completed bias/raw/sample
receipts before starting and verify current stat+hash equality after the whole
serial operation. All32 master hashes now have the fresh baseline established
by the completed native sample batch; preserve the older65 historical-hash limit
as provenance. This is new diagnostic evidence, not a repeat of completed recipes.

Keep existing source/native/ASDF/configuration/runtime evidence frozen. Retain
all partial outputs/logs on failure; no retry, overwrite, silent resume or repair.
Only after all32 results, exact master/flat replay and source/metadata/checkout/
installation/runtime checks pass may this new evidence be saved with an overall
completion receipt. Do not manufacture current source preservation from recorded
hashes alone; this operation really reads additional original diagnostic pixels.
Run the batch at niceness>=10. No parallel detectors, installation, merge or cleanup.

## 9. Interpretation and next scientific decision

The products are sufficient to inspect the missing primitive observations; they
are not sufficient by themselves to identify an arbitrary instrument noise model.
Inspect physical read-position structure, temporal/site differences, common-row
signals, outliers and consistency with the existing ordinary RON/pair curves.
All descriptive populations and conditioning must be stated. Preserve raw values;
centering used inside a stated diagnostic must not alter the fit observations.

No gain, Gaussian distribution, homogeneity pooling, independent-pixel/row model,
noise floor, block-independence assertion, covariance matrix, bootstrap or Monte
Carlo count/generator/seed/convergence rule is selected here. Two flats per level
do not establish an arbitrary per-pixel temporal distribution. Ten biases do not
supply a full unconstrained160-site covariance; a common ten-vector sample
covariance has rank at most9 (nine accepted vectors: at most8). Pairwise deletion
across differing memberships is not silently used to create a covariance matrix.

The downstream contract remains

    C = D + P_b F_b F_b^T P_b^T + P_s F_s F_s^T P_s^T.

The current assembler accepts arbitrary within-master and within-scan correlations,
but requires justified independence across the three blocks. Bias scans are
already part of the simulated master error; do not add them again as flat scan
noise. If cross-block dependence matters, revise the model/contract explicitly.
No unit weights or RON²/N shortcut. No real curve or shutter fit runs in Stage8.

## 10. Focused acceptance plan before real observations

Propose exactly three new focused control groups; these are written test purposes,
not implemented or passing tests. Do not replay unchanged old matrices.

1. **Native service and ownership:** independent hand-calculated43/44-read trimmed
   means (23/24 kept), ties and invalid bounds, immutable raw inputs, shared-row
   deduplication, role-aware zero bias time, actual9/10 median convention, staged
   rounding and exact old-path replay. Fail each new owner allocation singly and
   persistently; outputs remain unoccupied and new owners fully released.
2. **Explicit file/command integration:** generated small FITS with independent
   HDUs, both scan-width/orientation/crop cases, actual roles/membership and known
   master/flat samples; exact table counts/precision/origins. Refuse wrong/duplicate
   binding, malformed/nonfinite scan, bad master/replay, aliasing, source mutation,
   budget failures and output conflicts. Completion marker only on full success.
3. **Shared ASDF adapter:** synthetic evidence only, FITS/network opens forbidden;
   exact native/typed/core roundtrip, zero versus unavailable, units/physical
   identities/membership, shared trace references, relocation and changed/cohort/
   frozen-link/conflict refusals. Common schema and writer stay unchanged.

Run these focused checks in the agent workspace, then the actual Mac C17/private
ASDF environment once. Compare unchanged reused source bytes to retained gates.
Inspect that receipt before the one-use63-image real evidence batch. The approved
source files/population/algorithms remain unchanged. Actual execution, diagnostics
and resulting noise-model review follow; none has occurred in this design step.

## 11. Mathematical-guide deliverable after implementation

After the new subroutine is complete and qualified, write a guide derived from
this accepted design and the actual code. Map the scan, staged subtraction and
order-statistic equations to function/file names and argument/result fields;
explain physical coordinate/role/membership keys, units, precision, evidence
versus inference, ownership/failure states and validation examples. Link actual
acceptance receipts and limitations. Verify and cite primary algorithm references
where appropriate; preserve the legacy algorithm attributions (median.c documents
its selection algorithm and source). The guide must describe the final code,
not a proposed algorithm that diverged during implementation.

## 12. Owner review requested

Review the bounded evidence scope, exact legacy scan/lower-median conventions,
63-image source/read budget, four native tables/expected counts, replay/failure
contract, three focused acceptance groups and guide lifecycle. Acceptance of this
design authorizes implementation of that evidence stage, not selection of a noise
distribution, simulations, calibration interval or production correction curves.
