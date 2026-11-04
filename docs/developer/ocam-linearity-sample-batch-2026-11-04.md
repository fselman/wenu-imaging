# Approved OCAM singleton extraction batch — 4 November 2026

## Actual real-data completion receipt

Controller efebadf42bf6de6f03638ddb69af68254810ae97 completed on the actual Intel
Mac at /Users/fselman/Pictures/OCAM/wenu-imaging/ocam-linearity-samples-28h0jxnr.
Status complete_for_owner_inspection,32 detectors,3200 retained site/frame rows.
All eight preservation checks passed: shared_images, frozen_metadata, products,
checkout, installed_files, native_source, qc_source and private_qc_runtime.
All53 selected input images were checked before and after the serial extraction.
New metadata controls passed4/4 in0.016s; the ASDF admission fixture passed1/1 in
2.902s. Actual all32 master ASDF chains verified. CCD69/74/77/84/85 retain9/10
accepted bias inputs, all other masters10/10. No master/pair/RON recipe rerun.

This count includes explicit unavailable rows; it does not prove3200 admitted
observations or160 usable sites. The next review reads saved samples.tsv files
and checks their completed-run output hashes before reporting availability and
corrected signal ranges. No raw FITS read, hashing, extraction or old qualification
needs repeating for that review. Its results are not yet available. Native
transports remain intermediate; final shared ASDF sample publication and the
justified noise/covariance model, fit interval and actual correction fit remain.
The original65 historical-byte provenance limit below remains explicit; this
completed batch establishes and preserves its new byte baseline. No historical
FITS hash is invented. Keep all products/receipts and prior evidence.

The pending-extraction statements below describe the prepared increment before
this actual completion receipt; they are superseded by this section.

## Actual Mac command qualification

Source f560d67a23a6ede62ff6b8fccd755349456c10f6 passed on Intel Mac at
`/Users/fselman/Software/build/wenu-imaging/mac-sample-command-1iwkve9e`.
Singleton transports prepared; C17 configure/build succeeded. Exactly two focused
checks passed: native_sample_command 6.67s and affected native_pair_command 1.60s,
2/2 in 8.28s. Checkout, installed_files and exported_source guards all true.
Unchanged extraction/layout/scan kernels matched the retained aa5427c gate.
Binary hashes are retained in qualification.json. Do not rerun this C gate for
the Python orchestration increment below; no native kernels or build files change.

## Serial real-data controller

`Pycavi2/tools/run_ocam_linearity_samples.py` runs the approved 160 physical sites
as 32 sequential detector commands, five singleton sites through all 20 original
flats. Native mefpp_sample_extract reuses the qualified scan/master service.
Original indices, HDUs, pair identities and header exposure times are retained;
no pair averaging, pixel replacement, ROI means, lamp normalization or new
rejection settings. Master bias/RON/raw-pair recipes are not rerun.

Use the completed all32 signal catalog at linearity-bias-batch-05ijf_sx/masters.json
and original65 at linearity-bias-CCD65-epw82wy3. Admit the original31 master-byte
fingerprints, completed outer receipts and QC semantic digests. Compare all32
master handoffs, independent reviewed bias/BPM HDUs, native slots, readout/binning,
output HDU1, exact configuration snapshot/QC identity and source membership.
The unchanged private shared ASDF reader/traversal verifies all frozen links;
actual9/10 versus10/10 accepted memberships remain explicit. Source FITS are not
opened by that metadata admission.

Original65 does not have a recorded historical whole-FITS hash in its pilot
receipt. Do not imply that semantic QC proves its historical pixel bytes. Admit
its approved product path/HDU, retained semantic QC digest and recorded native
configuration/lineage, then establish a fresh full-file hash before this batch
and compare it after. The plan records this provenance limit explicitly. Other31
master FITS compare with the retained full-file fingerprints before processing.

Reuse each detector's original raw selection/plan transport. Regenerate it with
the unchanged qualified preparation functions and compare exactly, using saved
per-file header identity maps rather than HDU=native slot. Keep the full original
ROI profile unchanged; singleton transports are separate derived metadata.

Hash 53 selected image files once before and once after the entire extraction:
20 original flats, one structural BPM and 32 active masters. Flat/BPM hashes must
match the completed CCD65 raw measurement; master31 hashes match the completed
bias batch, and original65 gets the explicitly new baseline above. Compare full
stat+hash identities within this batch. The two raw-bias references remain in the
legacy plan transport but are not opened/hashed or remeasured by this operation.
Whole-source before/after verification is not a filesystem lock.

Frozen metadata includes source receipts, independent mappings, native plans,
master handoffs/configurations, ASDF leaves/products, controller/checks and
qualified binary. Preserve normal checkout/installations, qualified native/QC
source and private runtime. Native source kernels match the passed f560d67 gate;
ASDF6.0.0 / asdf-standard1.5.0 remain selected. No installation or package update.
All native commands inherit niceness>=10 and run serially. Selected plane loading
still uses the existing per-detector resource budget, not a total-memory claim.

Each detector exports100 site/frame rows, including not_admitted entries, for3200
rows across32 detectors. Admit exact column/schema/identity/coordinates and
original frame/ROI order; require finite exact header times, finite admitted ADU,
empty unavailable cells and consistent whole-active/per-site population counters.
Negative corrected values are valid transports, not auto-rejected. Missing sites
stay missing. A native marker/child result is provisional until all32 results,
all source/metadata/output checks and eight outer preservation guards pass.
First error stops later detectors and retains all partial evidence. No resume,
overwrite or cleanup. Run only in a fresh retained Pictures directory.

Outputs: top-level plan.json, master QC validation/log, singleton metadata,
per-detector native transports/logs, overall-execution.json and README. Native
TSVs are intermediate transports, not final shared ASDF characterization products.
No new ASDF publication, plots/HTML, weights/noise model, fit interval, fitted
coefficients, science acceptance or pixel correction is performed. The native
API's finite transport-domain bounds are not an accepted inversion interval.
Noise/covariance and final recipe/ASDF candidate publication remain later work.

## New controller checks

Agent four standard-library checks pass in0.006s: complete catalog/original65
reuse, wrong/duplicate identity/path/HDU and failed preservation refusals, exact
physical site/frame admission with negative and missing values, counters/schema,
and two shared image passes/change refusal. One new ASDF admission fixture passes
in1.662s with the existing ASDF6 packages: nine-of-ten membership, semantic digest,
configuration/selectors, frozen references and refusal of changed participation
or corrupt leaf, with FITS opens forbidden. The initial corrupt-leaf test expected
the narrower QcError; ASDF correctly raised ValueError. Only that test expectation
was corrected; no QC/backend/native change or bypass was introduced.

Those five new controls run on the Mac before any real source-image hashing or
native extraction, using normal Python for metadata controls and the retained
private ASDF runtime for the QC fixture. No old numerical/ASDF matrix or C rebuild.
Actual all32 extraction is pending. Inspect its overall receipt and sample
availability before selecting the remaining noise/covariance and fit policies.
#236 and draft PR227 stay open. Retain all previous data, builds and runtime.
