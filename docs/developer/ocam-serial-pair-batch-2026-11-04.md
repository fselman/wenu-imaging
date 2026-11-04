# Remaining OCAM raw-pair batch — 4 November 2026

Issue #234; draft PR #227. Owner authorizes proceeding after actual CCD65 native
measurements and ASDF/plots completed. This increment prepares and orchestrates
31 additional detectors; the real batch has not run. No scientific policy changes.

## Contract

`tools/run-ocam-pair-batch.py` prepares all 31 selections and plans in a fresh
retained directory. It admits the completed CCD65 receipt, approved header review,
verified structural-BPM preparation, reference ASDF tables and plot fingerprints.
It checks the qualified binary against the reference receipt. It does not hash or
read observation pixels during preparation. All 20 flats keep acquisition order,
input indices and nonconsecutive pair membership. The first two approved biases,
65534 raw-ADU digital boundary, binary BPM 1=good and resource ceilings stay fixed.
Per-file saved identity maps supply flat/bias/BPM HDUs independently of native slots.
TOML geometry supplies five ROIs per detector, including reflected upper-half ROIs.
The CCD65 measurement and ASDF records are linked and reused, never repeated.

One-use `--execute-prepared` verifies the manifest and frozen configuration,
metadata, reference evidence and binary. It fingerprints the 23 common image
files once before native processing and matches their reference CCD65 whole-file
hashes. One qualified native process runs at a time, releases its planes on exit,
and writes its own log, native transport and pending receipt. Native source stays
512092fa3180653f165f744a1ba7d9991e251f03. No Python pixel estimator is introduced.

The first native error, missing marker, malformed table or changed source stops
progress. Partial files/logs remain. After successful initial admission, the batch
attempts one final shared hash pass even on native failure. Exact hashes and stat
identities must match before final source preservation is asserted. This verifies
the native interval; it is not a file lock. No pending detector may publish ASDF.
After all native results and shared verification pass, normal per-detector native
receipts retain shared frozen inputs, output hashes and parent verification link.

The unchanged common QC/pair bridge publishes 25 ASDF records per detector and
verifies native text, typed precision, bindings, units, unavailable values and
frozen links. The unchanged ASDF-only plotter generates gain and variance plots.
ASDF/plot failure leaves the batch failed even when native measurements succeeded.
Final metadata fingerprints and cheap image stat checks cover the subsequent
metadata-only stage; there is no third image hash pass and no per-detector image
rehashing. The original CCD65 reference remains unchanged.

## Verification and target sequence

Twelve agent orchestration checks pass in 5.262s. These use tiny generated source
bytes and supplied native table transports, with fake child invocations. They are
not native numerical qualification or actual Mac acceptance. They cover all-31
prepare-only plans, independent mappings/order/limits, serial staging, exactly two
shared image hash calls, genuine per-detector ASDF publication, native/marker/table
failure, initial/final source changes, identical-byte stat changes, metadata
changes, one-use execution and ASDF failure. Existing numerical and 21 ASDF/plot
checks are not replayed.

`Pycavi2/tests/qualify_ocam_pair_batch_mac.py` exports an exact fetched revision
under Software/build, runs only these twelve controls in the retained private
ASDF6 environment, and checks module byte identity and package versions against
passed actual Mac gate `mac-pair-asdf-i7rw5asm` at serializer9f5a35fd. It protects
clean main, installations, exported source and private runtime. No C build, package
installation, raw observation access or full numerical matrix. Actual Mac gate
is pending. Inspect that receipt before real prepare-only invocation, then inspect
the 31-detector manifest before execution. Prior owner approval covers the same
scientific choices; no repeat scientific approval is required.

Retain successful CCD65 native `ccd65-raw-pairs-bpmfixed-zfs377ok`, ASDF/plots
`ccd65-pair-qc-2bz8baok`, original and structural BPM, both failed native attempts,
and all required builds/runtime. New real batch belongs under Pictures/OCAM/
wenu-imaging with its README and receipts. No overwrite/resume/cleanup/install/
merge. Keep #234 open until actual batch and preservation/ASDF receipts pass.

HTML mosaic implementation follows detector-wide data, using ASDF values and
maintained geometry. Higher-signal sequence search, scientific fits, gain interval,
normalization, uncertainty/noise/covariance policy remain deferred.
