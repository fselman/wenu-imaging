# Direct saved-ASDF viewer, 6 November 2026

Owner agreed to retain the 96 primary products and prepare the viewer before
reviewing recipe design. Base: b3c2bd854b555633e07457c2c58d06f1bd4f8fe6; issue #243.

The corrected viewer admits the existing completed preparation index/receipt,
then reads each selected preparation, residual and ratio ASDF exactly once via
the unchanged common QC reader. The reader retains its ASDF schema and common
record checks. Display checks verify index record digests, selectors, units,
stage, immediate input identities/digests, saved sample correspondence and
geometry. These are product checks, not a fresh calibration-history audit.

Do not open copied input graphs, replay embedded native transports, recompute
fits/ratios, copy provenance trees or hash the whole runtime. Full audit readers
remain unchanged. Measurement/diagnostic publication and the raw viewer path
remain unchanged. Preparation data, indexes and diagnostics are immutable.

Select existing stored rows into the existing plot payload, retaining exact
values, unavailable states, raw gain/RON labels and corrected signal labels.
Only selected product files and small display inputs receive byte fingerprints;
check them again once at publication. Print flushed file-start/file-finish and
render/write progress with elapsed timings, retained in viewer.json.

The existing CLI selects direct loading for --preparation-batch. One explicit
new inspection destination holds HTML, compact JSON and receipt; do not touch
the stopped inspection directory. No persistent cache or recipe restructuring.

Verification: dependency-free injected-record controls exercise selection,
identity/unit/stage/row mismatch refusal, no graph/computation calls, bounded
96-record decoding and progress. Actual ASDF equivalence uses the existing
corrected fixture and deep readers as an independent reference on the retained
Mac ASDF6 runtime. Real-data load timings and owner browser inspection are
required before claiming target performance or completion. No runtime install.
