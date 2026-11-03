# One-detector raw pair command and orchestration

This connects the actual-Mac-qualified raw file adapter and TSV exporters to an
expert native command and a small Python runner. It performs raw measurements,
not a gain/linearity/shutter fit or corrected sample construction.

## Boundaries

`mefpp_pair_measure NATIVE.paf SELECTED-ROIS.toml PLAN.tsv EMPTY-OUTPUT-DIRECTORY`
reads a bounded explicit plan and the existing named ROI TOML reader. It binds one
detector/amplifier, verifies the declared processing crop against the native PAF,
asserts raw dimensions against the detector profile, independently binds every
path/HDU/header identity and reuses the existing raw-file service. The native
command writes pairs.tsv, bias-ron.tsv and configuration.json, checking flush/close,
then writes command.complete. Existing output directories containing files are
refused, and files are opened exclusively. Any failure is nonzero; partial files
remain for diagnosis and are not asserted to be a completed measurement run.

The internal TSV plan is generated, not a new human configuration format. Version
raw-pair-plan-v1 requires exactly one of each of its 25 named settings and explicit
flat/bias/optional BPM records. There are no scientific defaults. It rejects
unknown/duplicate/missing keys, negative/overflow/nonfinite numbers, ambiguous
mask declarations and conflicting crop/raw dimensions. Limits are 1 MiB plan,
64 flats, two biases, at most one BPM, 128 HDUs per file and 1 MiB header catalogue
per source. ROI capacity remains 4096; pixel and pair-row ceilings are explicit.

`tools/run-pair-measurements.py` reads the reviewed detector and processing TOMLs
plus a separate execution-selection TOML. It checks their instrument/binning,
validates their geometry through the maintained footprint loader, selects only
this detector's ROIs, and verifies the processing profile's native-PAF SHA256.
It writes the selected ROI TOML and plan, keeping identity and acquisition order.
It runs one native child process, and never implements the numerical estimator in
Python. Detector processing must remain serial: release the native process's
planes before the next detector. No automatic all-detector launch is added here.

## Explicit selection file

Selection schema v1 requires these top-level values:

- selection_schema_version=1, detector, readout_id, bin_x, bin_y;
- raw_saturation_adu, pair_time_tolerance_s, max_loaded_pixels, max_rows;
- with_mad (true/false), reject_bits and exposure_hdu;
- header_keys table: identity, amplifier, bin_x, bin_y, exposure;
- flat tables: absolute path, original hdu, stable asset, original index, pair;
- exactly two bias tables: absolute path, original hdu, stable asset;
- bpm table: encoding='omitted', or encoding='binary' with path/hdu/asset and
  explicit good_value, or encoding='reason8' with path/hdu/asset and registry.

Header key values use full qfits spellings, including HIERARCH for long ESO keys.
The selected output's actual manufacturer key must be used (e.g. WFI OUT2 for
its R output); no output-number inference from mosaic position is performed.
Unknown selection fields are rejected. Distinct source asset IDs, file/HDU inode
references and original flat indices are checked. Pair IDs must occur exactly
twice. The native service reads the exact exposure times from the specified
header/HDU and applies only the explicit pair-time tolerance.

No real OCAM selection file is supplied yet: the full output/readout-header
review, raw saturation and two raw biases remain explicit pending selections.
The legacy binary BPM polarity must also be declared. The readout ID is a caller
claim; primary clock/readout/classification cards still require admission/review
before real execution. Identity/output evidence and array geometry checks do not
by themselves establish the hardware mode or raw bias classification.

## Prepare, execute and retain

Use Python 3.11+ (or tomli for earlier Python). All runner logic uses the standard
library and the maintained footprint loader. The source revision is an explicit
caller-supplied 40-character Git revision; the binary's actual SHA256 is recorded
separately, not falsely inferred from that revision label.

```sh
python3 -B tools/run-pair-measurements.py \
  --detectors config/detectors/omegacam-1x1.toml \
  --processing config/processing/omegacam-characterization.toml \
  --selection /absolute/path/to/reviewed-selection.toml \
  --native-paf mefpp2/ins/mef/config/omegacam.paf \
  --command /absolute/path/to/build/mefpp2/mefpp_pair_measure \
  --source-revision EXACT_40_CHARACTER_REVISION \
  --run /absolute/path/to/fresh-empty-review-directory
```

Without --execute the status is prepared_not_executed, no native child is launched
and detectors_processed is zero. Add --execute only after input admission and
selections are complete. On success, native exit/marker and parsed table row
counts must agree, and source fingerprints must remain unchanged before the
status becomes complete_for_owner_inspection. On failure execution.json says
failed and records the error; partial files/logs are retained. execution.json is
the authoritative overall receipt: a native marker alone does not establish that
the final source-preservation checks passed.

Before/after SHA256, inode/device, size and nanosecond modification/change-time
fingerprints cover resolved source observations, binary, native/visual/selection
configurations and orchestration code. This detects changes; it is not a source
lock. Raw hash I/O is substantial: use one detector for the first real inspection.
A future batch orchestration should freeze/hash the common observation set once
for the complete batch rather than repeatedly hashing it per detector. No original
file permissions are changed, and raw observations are never copied or deleted.

Use a purpose-named subdirectory of ~/Pictures/OCAM/wenu-imaging or the WFI
equivalent for real measurement runs. The runner always supplies a README stating
purpose and deletion conditions, including for failures. Compilation and tiny
synthetic tests stay under build. Owner review of build-directory disposition
remains required at branch merge/cleanup.

## Validation

Agent C17 preparation passes native_pair_command and pair_runner_orchestration
2/2, total 0.65 s. The command tests
four complete mask modes, repeated-output preservation and 11 refused plans.
The orchestration test prepares without execution, runs the actual native child,
checks source fingerprints and both tables, and refuses a stale PAF fingerprint
with a failed receipt/README and no native execution. All observations are tiny
generated fixtures; no real source dataset is processed.

Pycavi2/tests/qualify_pair_command_mac.py builds only mefpp_pair_measure, inventories
exactly those two tests, and runs them under the established actual-Mac C17,
clean-main and installed/exported-source preservation guards. Actual Mac gate is
pending. No installation or activation of this development command is requested.
