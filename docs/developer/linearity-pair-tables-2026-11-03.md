# Raw pair measurement table export — 3 November 2026

The next small step toward the OCAM measurement runner is a native export boundary
for the already qualified raw-pair results. It adds no numerical algorithm and
changes no existing measurement, scan correction, mask selection or calibration.

`mef_linearity_pairs_export.h` provides two caller-stream writers:

- `mef_linearity_pairs_write_tsv`: one row per nonconsecutive flat pair and ROI,
  in existing pair first-appearance order then configured ROI order.
- `mef_linearity_bias_write_tsv`: one row per ROI for the separately selected
  raw-bias-only RON population, rather than repeating it as independent estimates.

Both take an immutable qualified `mef_linearity_pairs_result`. They retain detector,
amplifier, configuration slot, ROI identity, active and raw bounds, two raw bias
asset IDs/HDUs, mask status/reject bits, raw saturation and pair-time tolerance.
Flat rows also retain each input asset, original input-array identifier, HDU and
exact exposure time. Region/BPM/nonfinite/saturation/valid counts remain separate.

Levels and RON are in ADU; variances in ADU squared. The bias-difference MAD
column is unscaled; RON-MAD uses the existing Gaussian-equivalent scaling divided
by sqrt(2). The table distinguishes raw
flat-difference variance from its half-variance per exposure, and likewise for the
bias pair. It includes the individual flat/bias means, two bias-referenced signals,
mean signal, fractional mismatch, matched-population RON/MAD and diagnostic point
gain. `arithmetic_available` means only that the existing arithmetic returned a
value: it does not select the instrument gain or a scientifically suitable signal
interval. Bias-only RON uses its own population; it need not equal matched RON.

Raw measurements precede all overscan correction, trimming, master subtraction,
lamp scaling or centering. The existing service translates each active ROI into
raw coordinates; the exporter simply writes its results. No difference is forced
to zero median. The two raw biases are reused across rows; those measurements are
correlated, and overlapping ROIs would also correlate. No fitted uncertainty,
independence claim, covariance estimate or linearity correction is introduced.

## Serialization and publication contract

Schema version is 1. Column names carry units. Boolean availability columns are
explicit; unavailable numeric entries are blank. A real measured zero remains
numeric zero. Finite values use 17 significant digits and require a decimal-point
locale; the writer refuses another numeric locale without changing global locale.
Text backslashes, tabs, newlines and carriage returns are escaped as `\\`, `\t`,
`\n`, `\r`; other ASCII controls use `\xHH`. Split TSV fields first, then decode
text columns. This prevents filenames/identifiers from creating false rows.

The caller owns streams and result. The writers neither allocate new owners nor
close streams; they flush to expose buffered I/O failure. They return MEF_ERR_INPUT,
MEF_ERR_IO or MEF_ERR_COMPUTATION rather than reporting success for failed output.
A failed stream may contain partial data and must be discarded. Freezing inputs,
recording resolved paths/readout identities/source hashes, exclusive files and
atomic publication belong to the forthcoming runner. These tables are diagnostic
exports, not ASDF QC records or fitted calibration products.

## Validation and next boundary

Agent C17 preparation: native_linearity_pairs_export and affected
native_linearity_pairs pass 2/2, total 0.07 s. The export contract parses actual
native output and verifies known signal/variance/gain/RON values, pair order,
exact ESO detector identity, raw bounds, text escaping, population partition,
valid zero bias difference versus unavailable variance, and stream failure.

`Pycavi2/tests/qualify_linearity_pairs_export_mac.py` exports exact fetched source
and builds only the two probes. It inventories and runs exactly these two tests,
with clean accepted main, installed files and exported source preserved. Actual
Mac qualification is pending. No repeated FITS-admission test matrix is needed
for this stream-only addition; the raw file loader has not changed.

After that gate, implement the bounded per-detector real-data admission/runner and
receipt/publication around the existing native services. Use the reviewed TOML
geometry and ROI profile, bind all output/readout headers, and explicitly select
raw saturation, binary BPM polarity and a distinct raw bias pair. Do not quietly
choose them. Actual observational results belong under a purpose-named directory
in ~/Pictures/OCAM/wenu-imaging with a README explaining retention/deletion, not in
build directories. No real-data execution or fit is claimed by this step.
