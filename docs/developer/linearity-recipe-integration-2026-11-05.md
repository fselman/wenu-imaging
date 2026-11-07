# TOML-led linearity recipe and ASDF integration

5 November 2026. Refs #235, #236; draft PR #227.

## Executive summary

The preparation recipe now composes the qualified overscan kernels, explicit FITS
binding, preserved master and direct-site dependencies, and the common ASDF
writer. Detector and processing TOMLs select all active numerical settings. The
master's immutable typed snapshot supplies compatibility/header fields only;
scan/trim/stack conflicts fail before processing.

Agent checks passed: three focused native CTests (file adapter with corrected
preparation and allocation controls, new preparation command, existing singleton
command), six TOML controls and eleven integrated recipe/ASDF controls. The latter
include analytical tiny FITS, source/membership verification, complete native-to-
ASDF publication, relocation without original native evidence, and refusal to
start a physical fit with unavailable uncertainty inputs. This is synthetic
agent qualification; actual Mac integration qualification and real corrected ROI
publication remain pending. Existing d8bf560 Mac overscan qualification stays
accepted and must not be repeated.

## Owner metadata received

The Mac receipt confirms passed d8bf560 native4/Python11 and all three guards,
retained at `mac-linearity-prepare-5QEzvc2c`. The direct-site extraction is complete
for32 detectors/3200 rows, all eight preservation guards true. Preserved sample
ASDF is complete at `ocam-corrected-sample-asdf-xm1ngkg_/persistence`:32 products,
3200 rows,1088 records; CCD65 digest
`d597a5eee67b3bcc1fdc30e36e09fd8bfcafe93f0864224699843078988ffb34`.
The master catalogue status is `candidate_signal_products`, count32.
CCD65 and CCD81 each retain all ten accepted bias inputs,20 flats and five direct
sites. Native slot0/CCD65 flat HDU1 and slot8/CCD81 flat HDU9 are independent
bindings; both master products are HDU1. Raw/active row offsets differ and remain
explicit. These receipts are metadata evidence, not a new corrected ROI run.

## Entry points and retained information

- `pycavi_linearity_recipe.preparation_dependencies`: metadata-only admission of
  sample/master graph, original handoff, snapshot and memberships. Legacy bias QC
  has null image hashes; the completed local bias outer receipt supplies those
  original fingerprints. No invented or newly substituted historical baseline.
- `prepare_detector`: fingerprints immutable inputs before/after native execution,
  verifies executable/metadata identity, then publishes one detector through the
  existing common ASDF owner/writer/reader.
- `mefpp_linearity_prepare_command`: corrects all supplied biases for ordered
  traces and streams flat pairs through `mef_linearity_from_files`; reuses the
  preserved corrected master once. Direct-site values are checked against the
  saved archive within this new ROI pass, without a separate extraction job.
- `pycavi_linearity_preparation_qc`: corrected per-exposure ROI statistics, raw pair
  diagnostics/common populations, ordered row corrections, direct-site replay,
  source graph and frozen native transports. Relative frozen inputs allow
  relocated ASDF reads without original raw/native directories.
- `tools/prepare-linearity.py`: explicit per-detector command; defaults to metadata
  admission only. `--execute` calls that same preparation recipe in a fresh empty
  retained directory. Batch orchestration can compose this per-detector service.

Noise/covariance is explicitly unavailable; no physical model is fitted and no
scientific acceptance is asserted. Changing later models reads saved ASDF.
Plotting remains separate. Existing products are not overwritten or regenerated.

## Qualification and next step

`Pycavi2/tests/qualify_linearity_recipe_mac.py` exports exact fetched source to a
private run, uses C17 and the retained qualified ASDF6 runtime without dependency
provisioning, runs three native plus seventeen Python checks, and verifies checkout,
installed files, exported source and private QC runtime preservation. No real
observations or old kernel gate replay. Full LaTeX and matching three-page PDF:
[linearity-preparation-guide-v1.tex](linearity-preparation-guide-v1.tex),
[linearity-preparation-guide-v1.pdf](linearity-preparation-guide-v1.pdf).

After actual Mac qualification, admit all32 real dependencies before a corrected
ROI pass. Preserve existing masters and direct-site archives; create a new
preparation ASDF archive, then separate saved diagnostics and plots for owner
inspection. No physical fitting, installation, merge or cleanup is authorized.
