# Raw-pair measurements through shared ASDF QC — 4 November 2026

Issue #233, draft PR #227. Owner approved persistence first, full-precision plots,
then detector-wide measurements. This increment serializes an already-completed
native measurement; it does not reread raw FITS or run an estimator/fit.

## Common representation

Use QcRecipe, write_record, read_record and traverse_records. Common QC1.1 adds
TSV product filenames and explicit table_name selectors, retaining actual FITS HDUs
for image records and measurement origins. Raw inputs remain FITS. QC1.0 image
records remain readable with current validation; qc-schema-1.0.0.json is retained
unchanged, and qc-schema-1.1.0.json is packaged through the existing resource glob.
No fictitious FITS product or HDU0 is assigned to a table. ASDF library6.0.0 and
file standard1.6.0 are unchanged; no dependency update is requested.

A completed CCD65 run produces25 records:23 input bindings (20 flats,2 raw biases,
1 selected BPM) plus pairs.asdf and bias-ron.asdf. Products have their actual TSV
identity/hash/location and contain typed full-precision rows with explicit units,
availability, original array indices/pair IDs/exact times, ROI active/raw coordinates,
counts/exclusions, readout/binning/mask policy, source bindings and settings. Exposure
times remain table metadata with the explicit exposure-key/header-HDU selection;
they are not mislabelled as ROI pixel measurements. Native
TSV text and SHA256 are retained alongside typed values, so exact byte and binary64
roundtrip are checkable. Unavailable values remain null with their native reason;
no point-gain availability implies scientific acceptance. Uncertainty/covariance
remain explicitly unavailable. Common measurements carry stage/method/region/count
and actual input image/HDU origins; table selectors carry no HDU.

Pairs link all23 leaves; bias-RON links only two biases and selected BPM. Leaves
record their frozen measurement-time fingerprint/binding, not invented individual
frame QC. No leaf generation/reassessment of the selected BPM is claimed. Relative
frozen links remain traversable after moving the full QC directory. Source file
locations remain original provenance, not automatic I/O requests.

## Admission and publication

Require complete_for_owner_inspection, raw_pair_measurements mode, native exit0,
source preservation and one processed detector. Validate the native completion
marker, output hashes/sizes/row counts, frozen selection hash, detector/amplifier/
configuration slot, ROI bounds/order, acquisition-order nonconsecutive pairs, exact
asset/HDU/original-index bindings and settings. Reject malformed/reordered columns,
nonfinite numbers, invalid counts/availability states and conflicting structural-BPM
lineage. Read only bounded small metadata/tables; reuse the original native receipt's
raw source fingerprints without reopening or rehashing images. This is persistence
of verified historical measurements, not current-image reassessment.

Assemble/seal records before publication; preflight basename conflicts. Publish
immutable common leaves then products, read them back, verify digests, typed/text
identity and frozen traversal. Check all small native evidence remains unchanged.
A fresh destination is required. Later errors may retain completed leaves and
truthful failed persistence receipts; there is no multi-file atomicity or silent
resume. Original native execution.json is never edited or upgraded by postprocessing.

Native producer/revision is retained separately from the serializer's exact source
revision. Native configuration, original receipt/selection/ROI/plan fingerprints,
mask derivation lineage and frozen source identities are stored in product extensions.
Common row measurements and typed extension tables are checked for agreement when
read; plots have one stored value authority.

## Commands

Run tools/persist-pair-qc.py with the retained qualified ASDF Python:

    --measurement-run ABSOLUTE_COMPLETED_RUN/measurement
    --run FRESH_EMPTY_PERSISTENCE_DIRECTORY
    --assessment-id EXPLICIT_ASSESSMENT
    --created-at TIMEZONE_TIMESTAMP
    --source-revision EXACT_SERIALIZER_COMMIT

It writes records/*.asdf and persistence.json. It has no native execution mode.
After successful persistence run tools/plot-pair-qc.py:

    --pairs-asdf PERSISTENCE_DIRECTORY/records/pairs.asdf
    --output-directory FRESH_EMPTY_PLOT_DIRECTORY

The plotter reads validated ASDF and frozen input records only. It creates gain
versus signal and single-flat variance versus signal PNGs, plus a derived plots.json
with exact plotted coordinates, included/excluded table rows and source digests.
The PNGs/plot JSON are derived views, not a competing measurement authority.
Lines connect measured points, unavailable points remain explicitly excluded,
and no regression, uncertainty estimate, fit interval or scientific cut is added.
Plots use full binary64 values, replacing the provisional rounded-chat figures.

## Validation and target gate

Agent ASDF6 metadata checks:12 shared-QC controls pass in0.777s;9 pair-persistence/
plot controls pass in6.283s. They cover binary64/signed-zero and exact native text
roundtrip, units/states/origins, backward QC1.0 image reading, truthful unavailable
values, failed/tampered evidence, schema/count/binding/order refusal, structural
BPM lineage refusal, no overwrite, frozen traversal/relocation and ASDF-only plots.
Raw FITS access and network operations are forbidden in the pair tests. Plotting
succeeds after original native evidence is moved away; plotted coordinates match
saved values exactly. Previously generated tiny native TSV output is also admitted
by the parser without rebuilding/rerunning native software. These are preparation
checks, not actual Mac acceptance or observational persistence.

Pycavi2/tests/qualify_pair_qc_mac.py exports exact source, uses the normal installed
imaging Python for guards and retained private ASDF6 Python for12+9 checks. It
protects clean main c73d9a9e, installed files, exported source and retained QC runtime.
No dependency provisioning/install, native build, pixel processing or old C17/C90
matrix. Actual Mac gate is pending. Inspect it before persisting the completed real
run under Pictures/OCAM/wenu-imaging with purpose/retention README. Keep all original
runs, structural BPM copy and required runtimes.

## Remaining work

After actual Mac qualification: persist existing CCD65 full-precision tables,
regenerate both plots from saved ASDF, inspect receipts, then prepare a serial
remaining-detector batch that freezes shared input hashes once. Automatic linking
of persistence into batch completion remains part of that future orchestration;
the qualified native-only runner is not silently changed here. Fitting, gain
interval/noise/covariance policy and near-saturation sequence search stay deferred.
The owner's [HTML mosaic viewer requirements](qc-mosaic-viewer-requirements-2026-11-04.md)
are recorded now for implementation after detector-wide data. No fit, production
activation, merge or cleanup accompanies this increment.
