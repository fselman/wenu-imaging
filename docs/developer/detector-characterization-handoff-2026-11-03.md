# Detector characterization handoff - 3 November 2026

Owner explicitly revoked the previously provided AGENTS.md instructions during
this session. Earlier AGENTS scope entries are historical, not controlling.
The scientific decisions and actual-host evidence below remain project history.

PR #227 / branch docs/bpm-linearity-pairs-20261103 remains a development candidate;
no merge or installation has occurred. Mac checkout is clean main c73d9a9e at
/Users/fselman/Developer/wenu-imaging. Normal imaging Python remains
/Users/fselman/anaconda3/envs/wenu-imaging/bin/python.

Completed actual Intel Mac C17 gates (all checkout/install/export protections true):

| Component | Source | Tests | Seconds | Retained directory under ~/Software/build/wenu-imaging |
|---|---|---:|---:|---|
| Paired gain/RON | e0b16476 | 2/2 | 2.58 | mac-gain-pair-AdGQvwqZ |
| Pivoted QR | b382a93e | 2/2 | 1.69 | mac-matrix-qr-Ay1wSJZe |
| Checked simplex | beee7c0d | 2/2 | 1.79 | mac-simplex-ddM35GKJ |
| Direct-pixel joint candidate | dc762519 | 2/2 | 2.67 | mac-detector-joint-7iY8InK7 |
| Shutter profile | 338180f6 | 2/2 | 6.09 | mac-shutter-profile-0mNWCIc5 |
| Exact ROI operator | 4d0bb462 | 3/3 | 3.01 | mac-roi-aggregation-2SOrKVed |
| Named ROI configuration | 8e893008 | 1/1 | 1.21 | mac-roi-config-PHwS5VBY |
| Raw-plane sample admission | 88e29306 | 1/1 | 1.05 total | mac-linearity-samples-fRlf0Hgk |
| Explicit covariance assembly | c381168b | 4/4 | 3.69 | mac-detector-noise-z4pHBH0H |
| FITS admission and affected callers | 10027f1e | 3/3 | 20.91 | mac-linearity-files-nF68I1UL |
| Raw pair measurements and FITS composition | 37e11f4f | 2/2 | 34.99 | mac-linearity-pairs-UI4rv05W |

The exact ROI operator/covariance propagation is Mac-qualified as above,
including its two new controls and the affected joint validator control.
[Named ROI configuration](roi-configuration-2026-11-03.md) now provides an
explicit PAF/TOML supplement and atomic binding by detector + amplifier identity.
Per-detector counts/geometry may differ; active amplifier bounds are checked;
overlap remains allowed. Agent C17 config preparation passed 1/1 in 0.07 s.
Its focused actual Mac gate passed as above; numerical sources remain unchanged.
The [in-memory raw-plane sample service](linearity-samples-2026-11-03.md) now
reuses row scan/crop and master subtraction, selecting a BPM/ROI union with
explicit raw saturation and original frame identities. Agent C17 preparation
passed 1/1 in 0.01 s, including 119 service/snapshot allocation-failure positions.
Its actual Mac gate passed as above (1.04 s test, 1.05 s total). Noise remains
explicitly unavailable; no fit should run on these samples yet. The full linearity
CLI, justified noise estimates and forward-model integration
remain pending. [Explicit covariance assembly](detector-noise-2026-11-03.md)
now combines supplied independent pixel, shared master and named row-scan blocks
using existing QR with a recorded observation permutation. Blocks must be
caller-established independent; no gain/variance is estimated or defaulted.
Agent C17 4/4 in 0.36 s passed, including all 33 single/persistent allocation
positions and affected ROI/joint controls. Actual Mac covariance gate passed as above; no real-data fit or installation.
[Explicit FITS admission](linearity-files-2026-11-03.md) now connects supplied
M4 path/HDU/detector/calibration maps to sample preparation, reads exact header
times, validates nonconsecutive declared pairs and preserves binary/reason BPM
semantics. Agent C17 2/2 in 3.31 s passed, including 14 FITS cases, the existing
BPM C caller and 132 adapter/sample/snapshot allocation failures. Full existing
BPM Python suite subsequently passed on the actual Mac as above (agent lacks
Astropy). The gate selected new files + affected sample/BPM tests.
No uncertainties, actual OCAM fit or product publication yet.

One signed shutter duration offset is common to ALL detectors. Cubic inverse
response coefficients are amplifier-specific; direct-pixel illumination rates
are fixed per site across frames. Bias is constrained; no free bias intercept
or per-frame lamp factor. Units: ADU and seconds, with absolute supplied covariance.
Profile points hold common delay fixed and refit every nuisance parameter; no
symmetric error or science acceptance is implied by a numerical bracket.

ROI means cannot be substituted for pixels without an integrated pixel-level
forward model or a validated restricted approximation. Exact recorded ROI
operators and supplied-covariance propagation are implemented. Raw extraction
for explicit single-amplifier bindings is now implemented. Justified noise-model
construction, scalable forward-model/recipe integration, conditional
pixel nonlinearity classification and actual science acceptance remain pending. Owner defers QC visualization work. Full
correction later belongs in mefpp; eventual photometric comparisons will use the
same frames with and without correction.

Selected Mac OCAM sequence: /Users/fselman/Pictures/OCAM/bpm, 13 March 2017,
10 biases and 20 v_STRM DETGAIN flats with nonconsecutive reverse pairs:
2,70,40,5,10,30,20,50,60,7 | 7,60,50,20,30,10,5,40,70,2 seconds.
Actual raw pixels have not been processed by the new joint fitter. Preserve
chronological acquisition order, pair IDs and detector/HDU identities.

BPM remains unsigned 8-bit, zero good with bitwise reasons; coverage is separate.
RON uses raw bias-pair differences, with no overscan correction before subtraction.
Legacy masks and approved functions retain their semantics. Existing Eclipse
numerical resources are composed; old interfaces are preserved.

#228 and #229 test-only fixture corrections are accepted/closed after their
actual Mac gates. Failed/corrected preparation logs are retained, not discarded.
Validated WFI bias products and all earlier inventories/environments remain
untouched. Full actual-data Chapman qualification/processing follows validation
of the changed code there; no new real data, QC work or science reduction now.


## Agreed uncertainty policy and current increment

[Agreed uncertainty policy](linearity-uncertainty-review-2026-11-03.md): first
measure raw bias RON and flat-pair variance versus signal in explicit populations;
then propagate a justified noise model through the actual trimmed-row correction
and median master, conditional on reviewed selections and with covariance fixed
within each fit. The median master is not assigned mean-stack variance RON^2/N.
No distribution, fit range, simulation count or stochastic estimator is adopted
without the owner's scientific review. ESO reports October 2016 intermittent
RON increases in CCD_69/77, relevant checks for our March 2017 sequence, not proof
that the selected exposures are affected. Hardware identities/readout/epoch must
be matched. The owner approved measurement first and propagation through the actual estimators,
then approved covariance fixed within each fit with outer repeated fits for its
uncertainty. No default distribution or simulation parameters were approved.

[Raw pair/ROI measurements](linearity-pair-measurements-2026-11-03.md) now compose
the qualified gain/RON kernel with optional FITS admission of two explicit raw
biases. A separate bias-only RON population remains visible beside the common
four-plane population used by each flat pair. Agent C17 focused preparation passes;
actual Mac qualification passed 2/2 in 34.99 s at 37e11f4f, retained
mac-linearity-pairs-UI4rv05W. native_linearity_files passed in 34.03 s and
native_linearity_pairs in 0.94 s. Checkout, installed files and exported source
preservation are all true; the Mac remains clean main c73d9a9e. No real data, noise-model fit, Monte Carlo,
installation, merge or scientific acceptance follows from this increment.



## Current real-sequence preparation

Owner instructed proceeding after the pair gate and confirmed
/Users/fselman/Pictures/OCAM/bpm. Owner-returned dfits/fitsort evidence confirms
all selected 30 files have OBS.ID 574184, with the previously selected ten biases
and twenty flats. The [header preparation helper](ocam-pair-preparation-2026-11-03.md)
saves sequence/pair membership, independent HDU identities, configuration claims,
scan geometry declarations, diagnostics and bounded unselected FITS candidates.
Agent preparation-policy tests pass 3/3; actual Mac header inventory remains
pending. BPM/ROI/saturation/bias-pair/amplifier-readout selections are recorded
as unresolved, so no real pixel measurement or fit is launched yet.



Actual OCAM header preparation passed at a9bdb160 on the Mac, retained
mac-ocam-pair-preparation-XqbLTbCy. All 30 selected files have 32 image detectors,
2144 x 4200 raw pixels and stable identity/HDU layouts. The one unselected file
is OCAM_BPM_1x1.fits, 33 HDUs, with no primary DPR.TYPE/ESO PRO CATG reported.
Checkout/install/export and raw stat preservation passed. This is header evidence,
not calibration compatibility or pixel acceptance.

Important label correction: the preparation helper called .cfg entry order
configuration_detector. The actual native PAF indexes CHIPn by original extension
n (mefp_lib.c/mefpp.c), whereas the Python .cfg lists #96 first but it is in HDU32.
The helper now calls that source field python_config_entry and leaves the native
configuration_detector null. All native_binding_validated flags remain false;
no real numerical run used these claims. Three policy checks pass after correction.
Do not rerun the unchanged 31-header inventory merely to rename this field.
Review the saved raw/amplifier/readout/scan cards and candidate BPM values next.


## Comparison data storage and cleanup

Owner instruction of 3 November: all data needed for future comparisons goes
under an appropriately named subdirectory of ~/Pictures/OCAM/wenu-imaging or
~/Pictures/WFI/wenu-imaging. Each subdirectory needs a README stating why it is
needed and when it can be erased. See [retention rule](comparison-data-retention.md).
Existing required comparison products still under build paths need relocation
and reference updates; no move has yet been executed.

Owner-returned Mac cleanup receipts: three generated large-file FITS fixtures
removed (synthetic-cleanup-t3ltzrf1.json), then 320 OmegaCAM astrometry detector
intermediates removed (pilot-intermediate-cleanup-wjzqseu2.json). The latter were
removed without pixel comparison at the owner's direction. Full MEFs and small
WCS/catalogue/log files were retained by the command. Last returned free space:
59.65 GiB, roughly 14 GiB recovered across these two imaging cleanup steps.
Raw observations, current WFI/OCAM calibrations and required runtimes remain
outside the cleanup selection. Further bulk deletion is not implied.


## Resumed OCAM preparation: exact ROI identities

Resumption exposed #230: the named ROI reader/binder rejected # in actual
ESO_CCD_# detector identities. The bounded grammar correction and PAF/TOML
exact-identity regression now pass agent C17 native_roi_config 1/1 in 0.08 s;
actual Mac gate is pending via qualify_roi_identity_mac.py. No numerical changes
or actual-data measurement. See [compatibility/evidence](roi-eso-identity-2026-11-03.md).

The owner-returned BPM check shows all 32 active 2044 x 4091 planes are unsigned
8-bit binary 0/1, without registry/encoding cards or nonfinite pixels. First
raw bias/flat primary cards agree on normal readout/speed, ordered mosaic, 1x1,
32 outputs; the first two printed chip headers report manufacturer output L.
Complete per-detector identity/readout binding, reviewed ROIs, raw saturation and
bias pair still precede real measurement. Retained observational comparison data
must follow the new Pictures/instrument retention rule and per-dataset README.



## Actual Mac exact-identity qualification

Owner returned f02eb695 native_roi_config pass 1/1 in 1.26 s, total 1.27 s,
retained mac-roi-identity-8xg2xMCO. All checkout/installed_files/exported_source
preservation checks true; clean main remains unchanged. #230 closed with the
correction and actual-host receipt. Earlier pending #230 notes above are historical.
ROI/bias-pair/saturation selections and full instrument bindings remain the next
scientific preparation, with actual measurement/fit still pending.


## Owner-supplied mosaic: readout-oriented ROI configuration

Owner supplied ocam_field_geometry_for_HC.png and instructed defining analogous
ROIs using the mosaic and PAF illuminated/scan regions. The explicit blue CHIP
numbers resolve the selected sequence's logical-detector/native-PAF association,
independent of Python .cfg order. The period-96 ESO manual confirms lower-half
bottom/left output geometry and 180-degree upper-half rotation, manufacturer L
output throughout. Actual image arrays/BPM remain unrotated; only ROI bounds are
reflected. [Geometry and profile](ocam-readout-rois-2026-11-03.md) records formulas,
32 identity/slot/mosaic positions and five 512x512 ROI proposals per detector.
The four corner boxes are inset 128 pixels, plus a central box; all are editable
per detector. The common readout-relative pattern yields 160 unique bounded,
nonoverlapping rectangles, validated with TOML roundtrip and two named mirror
examples. PAF/TOML supplements and geometry JSON are under config/characterization.
This is configuration preparation, no actual-data measurement/fit acceptance.
Complete output-header admission, saturation and raw-bias-pair choices remain
before launch. Future comparison products follow the Pictures/instrument rule.


## Reviewed footprints and native measurement-table export

Owner inspected both 50e52a9 Mac footprint mosaics and reports both look OK.
Viewer maintenance as TOMLs evolve is recorded in both agent instruction files at
7191f14. Visual layout acceptance does not silently choose raw saturation or bias
pair, or validate ROI scientific suitability.

The next measurement-runner boundary adds allocation-free native TSV writers for
qualified raw pair/ROI and separate bias-only RON results. Preserve all identities,
pair order, original indices/HDUs/times, raw/active bounds, mask/exclusion counts,
units, available zeros and explicitly unavailable fields. No numerical change,
lamp normalization, centering, correction, fitted gain interval or uncertainty
model. See [table contract](linearity-pair-tables-2026-11-03.md).

Agent C17 export and affected pair service pass 2/2 in 0.07 s. A focused exact-source
Mac qualifier builds only two probes and runs exactly these two tests, preserving
checkout/install/export. Actual Mac gate remains pending. No real raw-pixel run
has been launched. After that gate, continue bounded per-detector admission and
measurement orchestration; output/readout headers, explicit raw saturation, binary
BPM polarity and raw-bias pair precede launch. Future observational results go to
Pictures/OCAM/wenu-imaging with purpose/deletion README. Branch-created build
directories still need owner disposition review at merge/cleanup.

## Actual Mac export qualification passed

Fernando returned the exact-source 7a47dc0fc7d6bb197223e3abc1be811bf3313fd8
Mac C17 receipt on 3 November 2026. Retained run:
/Users/fselman/Software/build/wenu-imaging/mac-pair-export-hDj5WASm.

native_linearity_pairs_export passed in 1.35 s and native_linearity_pairs in
1.00 s: 2/2 passed, total elapsed 2.36 s. QUALIFICATION passed; checkout,
installed_files and exported_source preservation all true. The user checkout
remains on clean main tracking origin/main. This qualifies synthetic native
table export and the affected pair service; no actual OCAM measurement, fitted
gain/linearity/shutter solution, installation or merge is claimed.

Next: bounded per-detector real-file admission and measurement orchestration,
using the already qualified native measurement/export services and reviewed
geometry. Complete all per-output header/readout bindings and explicit raw
saturation, legacy binary BPM polarity and distinct raw bias pair before launch.
Preserve acquisition order and the existing nonconsecutive pairs. Observational
outputs go under Pictures/OCAM/wenu-imaging with a purpose/deletion README.
No unchanged export or earlier numerical test replay is needed for a
documentation-only receipt update. Review branch-created build directories
with the owner at merge/cleanup.

## Raw-only file admission candidate

The first diagnostic measurement pass now has its own typed file admission path,
mef_linearity_raw_from_files, with no master-bias dependency or corrected dense
fit-sample construction. Explicit M4 path/HDU/identity/readout/unit/binding and
resource checks precede loads; the existing raw-pair service and qualified TSV
writers supply the measurements and export. The owner returned the preceding
table-export Mac gate passed 2/2 in 2.36 s at 7a47dc0; no changes to those numerical
or exporter sources are needed here.

Agent C17 raw-only admission passes 20 tiny FITS cases and 130 persistent
file/service owner allocation failures, 1/1 in 4.76 s total. Each case deletes its
generated master before the call; source hashes are preserved, pair order/times
and detached bindings checked, and known raw signal/RON exported after input
owners are gone. See [raw-only admission](linearity-raw-files-2026-11-03.md).

Focused actual Mac qualifier builds only raw-file and table-export probes and
runs native_linearity_raw_files plus native_linearity_pairs_export. Actual Mac
gate pending. Command/plan orchestration is still to follow that gate; no real
pixel run or scientific fit has occurred. Full output-header binding, explicit
raw saturation, binary BPM polarity and raw-bias-pair selection still precede
actual OCAM execution. Pictures retention and owner build-disposition review
remain in force.

## Actual Mac raw-only admission qualification passed

Fernando returned the exact-source 49399e09abaef53ccdae2cf86f9ab996c5469f16
Mac C17 receipt on 3 November 2026. Retained run:
/Users/fselman/Software/build/wenu-imaging/mac-raw-pair-files-uFtyet1s.

native_linearity_raw_files passed in 16.35 s; native_linearity_pairs_export
passed in 1.17 s. Overall 2/2 passed, total elapsed 17.54 s. QUALIFICATION passed,
with checkout, installed_files and exported_source preservation all true.
The user checkout remains clean main tracking origin/main.

The raw-only adapter and its table-export integration are now actual-Mac
qualified. Next is command/plan orchestration around these existing services,
with one detector loaded and released at a time. No raw OCAM observations have
been processed and no gain/linearity/shutter fit, installation or merge occurred.
Full output/readout-header admission and explicit raw saturation, legacy binary
BPM polarity and distinct bias-pair selection still precede real execution.
Observational outputs follow the Pictures/instrument purpose-directory and
README retention rule; build-directory disposition is reviewed with the owner
at branch merge/cleanup. No test replay is needed for this receipt-only update.

## One-detector command and orchestration candidate

The actual-Mac raw-only adapter gate passed at 49399e0 (2/2 in 17.54 s), retained
mac-raw-pair-files-uFtyet1s, with clean main and checkout/install/export preserved.
The next candidate connects it to mefpp_pair_measure and tools/run-pair-measurements.py.
The native command binds the existing ROI TOML, checks explicit plan/native crop
and raw dimensions, invokes qualified measurement/export, creates files exclusively
and emits a completion marker only after close checks.

The Python runner reads the maintained detector/processing TOMLs plus explicit
selection TOML, verifies the native PAF fingerprint, selects one detector's ROIs,
writes the internal bounded plan, fingerprints all source files/code before/after,
and records execution.json, README, logs and tables. Default is preparation only;
--execute is explicit. Status becomes complete_for_owner_inspection only after
native success, expected marker/table counts and source preservation. Failed
attempts retain partial evidence with failed status; the overall receipt is
authoritative even if a native marker exists. No original files are copied,
modified, permission-changed or deleted.

Agent C17 two end-to-end checks pass 2/2 in 0.65 s. Four successful mask modes,
existing-output preservation, 11 refused plans, native child orchestration,
prepare-only status, fingerprints and stale-config refusal are covered using
tiny generated FITS only. Focused actual Mac qualifier builds only the command
and runs native_pair_command plus pair_runner_orchestration. Actual Mac gate
pending. See [command contract](pair-command-2026-11-03.md).

No real OCAM selection has been generated or executed. Complete all selected
output/primary readout-clock/classification admission, explicitly select raw
saturation, two raw biases and binary BPM polarity, then prepare a first-detector
real plan for review. No fitting or instrument-gain acceptance. Real outputs
belong in Pictures/instrument/wenu-imaging with README; owner build-directory
disposition review is required at merge/cleanup. A future batch should hash the
common observation set once for the batch rather than repeat per detector.

## Actual Mac command qualification passed

Fernando returned the exact-source 6e75a7bf322583e0aeaca50e1ff786b70cd259f3
Mac C17 receipt. Retained run:
/Users/fselman/Software/build/wenu-imaging/mac-pair-command-mv3iAx5L.

pair_runner_orchestration passed in 2.08 s; native_pair_command passed in 0.95 s.
Overall 2/2 passed, total elapsed 3.04 s. QUALIFICATION passed and checkout,
installed_files and exported_source preservation are all true. The user checkout
remains clean main tracking origin/main.

The one-detector native command and Python prepare/execute orchestration are now
actual-Mac qualified on synthetic FITS. No real OCAM measurement, fitted gain/
linearity/shutter calibration, installation, merge or cleanup is implied.

Next: complete the selected sequence's full primary/output-header admission,
explicitly select raw saturation, the distinct raw bias pair and legacy binary
BPM polarity, then prepare the first detector's real selection/plan for review.
Use the reviewed detector/processing TOMLs and existing source sequence/pair
inventory, preserving acquisition order and nonconsecutive pairs. Do not invent
these remaining scientific choices or silently execute the prepared plan.

Real run directories belong under Pictures/OCAM/wenu-imaging with purpose/deletion
README. Review branch-created build directories with the owner at merge/cleanup.
This receipt-only update needs no test replay.
