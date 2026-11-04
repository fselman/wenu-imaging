# Corrected singleton samples in shared ASDF — 4 November 2026

## Returned availability review

The owner returned a hash-verified review of the completed
ocam-linearity-samples-28h0jxnr native tables:3200 admitted,0 missing,160/160 sites
with data. Each of the32 detectors has100 admitted samples from5 physical sites
through20 original flats. Rounded corrected-pixel coverage is934.2–53381.5ADU,
with the highest returned sample inCCD86. These ranges describe individual
scan/master-corrected pixels; they do not establish a fit interval, saturation or
nonlinearity threshold. Full precision remains in the native transports.

No extraction, raw FITS hashing or native qualification needs repeating.

## New persistence stage

`pycavi_sample_qc.py` and `tools/persist-linearity-samples.py` map the completed
batch to the existing common QcRecipe/write_record/read_record/traverse_records.
Common schema/writer, ASDF runtime and extraction kernels are unchanged.
The adapter requires a completed all32/3200-row receipt with all8guards true,
recorded53-image before/after equality and exact frozen plan/controller metadata.
It reuses the completed controller's table-admission routine after byte comparison.
It validates saved native files against their recorded hashes, original physical
coordinates/ROI and frame order, population counters and master QC frozen links.
It opens only small metadata/TSV/ASDF files. Source FITS file fingerprints are
recorded evidence from extraction, never newly measured/current hashes.

For each detector,34 shared ASDF records are written into its own subtree:
20 flat input bindings,1 BPM binding,12 semantically identical records copied from
the existing master-bias QC graph (10 raw biases+BPM+master), and1 samples product.
The input bindings make no new individual-frame reassessment claim. The imported
master graph preserves original assessment identities/digests, measurements and
used/rejected memberships; it is written through the common serializer, not
claimed byte-identical ASDF. Original input locations remain provenance, while
local frozen links allow relocation without opening originals.

`samples.asdf` uses an explicit corrected_samples table selector, not a fake FITS
HDU. Its shared characterization contains each corrected signal inADU, original
flat/master/BPM source IDs and actual HDUs, active/raw physical pixel coordinates,
source ROI, original input index and native processing stage. Its recipe extension
retains full-precision typed rows, exact native text and digest, units, admission
and unavailable states, frame population counters with exact native text/hash,
effective native configuration and the sampling policy/approval snapshot from
before extraction. Sampling-context flags are historical metadata, not a claim
that no samples have since been measured. Missing samples stayNone/unavailable;
negative admitted signals remain numbers. Typed/core/native representations are
cross-checked. No ROI means, pair averaging, gain conversion or numerical fit.

The product retains the original completed batch receipt path/hash/guards,
native/controller/serializer revisions and recorded master fingerprint/digest.
The original65 historical whole-FITS hash limit remains explicit; its new
extraction-time fingerprint is preserved. Noise remains unavailable, covariance
and fit intervalNone, fit not performed, correction coefficientsNone and science
acceptancefalse. No identity weighting, noise distribution or MC settings chosen.

A successful all32 publication would contain1088 records and3200 rows. Only the
new persistence.json plus successful source checks establish completion of this
stage. A failure retains partial records/logs and cannot silently resume or
overwrite. Immutable observations, original native/QC products and runtimes stay
in place. Native transport and ASDF-stage revisions remain distinct. Plotting and
HTML remain independent consumers; no presentation is regenerated here.

## Verification and target handoff

Agent five new metadata/ASDF controls passed5/5 in5.250s using the retained ASDF6
packages, with FITS opens and network forbidden. They cover exact signal/text/
typed/core roundtrip, negative/missing values, actual rejected bias membership,
frozen graph traversal and relocation, changed transport/master/cohort refusal,
typed/unit/measurement/coordinate/noise/population tampering, output conflicts
and broken frozen references. Existing common backend and numerical tests are
reused; no old matrix, native build, new dependencies or installations.

`qualify_sample_qc_mac.py` prepares an exact uninstalled source export, compares
shared modules and package versions to the passed retained ASDF gate, verifies
the extraction-admission code bytes against the completed real run, and runs only
these five new checks in the retained privateASDF6 environment. Checkout,
installed files, exported source and private runtime protections must all pass.
It reads only the real run's receipt/controller metadata, never real images or
sample tables; test tables and records are synthetic. Actual Mac qualification
and actual sample ASDF persistence remain pending. Neither this implementation
nor its qualification runs the actual persistence or fits correction coefficients.

After target qualification, persist the retained completed batch without raw
FITS/native measurement reruns. Then establish the missing scientific noise/
covariance and interval decisions before any real correction fit. #236 and draft
PR227 stay open; no merge, installation, correction activation or cleanup.
