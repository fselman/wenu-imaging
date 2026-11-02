# Bias BPM files and shared ASDF QC handoff — 2 November 2026

This increment connects the numerical bias service to explicitly selected FITS
BPMs and the existing common ASDF writer. It is opt-in and does not install or
activate a production recipe. Actual Mac acceptance is pending.

## Owner correction: detector pixels versus electronic scan samples

The detector BPM applies only to the active image area. ESO prescan/overscan
samples are empty electronic reads, not corresponding physical detector pixels.
A detector BPM is therefore **not applicable** to those regions, regardless of
whether its FITS array happens to have raw-frame dimensions. The bias service
always calls the existing scan correction without a detector mask and retains
its configured sample rejection. Scan QC also uses no detector BPM; saved
measurement definitions explicitly say `not_applicable`, not `unavailable`.

This supersedes the scan-masking behavior implemented in a20d776. That revision's
Mac 4/4 C17 receipt (13.43s, mac-bpm-mad-LNMslJOz) remains valid evidence of the
then-implemented code, not scientific approval of the superseded scan policy.
The new known-answer fixture proves that even a raw-sized BPM labelling every
scan position bad cannot change scan correction or exclude scan measurements.

## Reused implementation

- `mef_layout_load_bpm` composes the existing selected-HDU `mef_layout_load`
  (and its qfits/Eclipse pixel loading, scaling and file identity checks) with
  `image_threshold2pixelmap`. Explicit good-value 0 or 1 is normalized to
  Eclipse's 1=good. Only integer selected HDUs (BITPIX 8/16/32) and binary
  physical pixel values are supported. No bit-field guess, nonzero shortcut,
  nonfinite pixel or implicit polarity conversion is accepted.
- A raw-sized BPM must match raw geometry; an active-sized BPM must match the
  configured trim rectangle. The latter is embedded with explicit offsets for
  the existing service API. Scan padding is never used as detector mask evidence.
  Readout/binning/active geometry compatibility reuses the existing layout map.
- `pixelmap_loadext` was reviewed but is unsuitable: its type check uses the
  primary header rather than the selected extension (#222, source finding,
  unresolved), and its documented nonzero conversion lacks strict polarity.
  No second FITS parser or new numerical estimator was added.
- `mef_bias_files_execute_measurements` uses the same validate/load/calculate/
  publish/cleanup template and FITS publisher as the old file adapter. Old
  entry points remain wrappers with unchanged default behavior.
- `pycavi_bias_qc.publish_handoff` supplies values and definitions to the existing
  BiasQcRecipe/QcRecipe, schema, seal/write/read/traverse path. There is one ASDF
  serializer. The new common `add_extension` obeys copied-owner/sealed-state
  rules rather than letting adapters mutate a builder's private tree.

## Explicit command interfaces

The opt-in native `mefpp_m5 cal bias` keeps all existing required arguments.
Numerical handoff adds `--measurements yes --mad yes|no`, optional explicit
zero-based `--ron-first INDEX --ron-second INDEX`, and optional positive
`--high-sigma K` (initial owner choice/default 5). RON pairs must be distinct
indices and distinct named files. No automatic pair selection or gain conversion.

`--input-bpm omitted` remains supported. Selection instead supplies an absolute
FITS path plus `--bpm-hdu N --bpm-good-value 0|1 --bpm-coordinates raw|active`.
`--bpm-expected-extname NAME` is an optional independent assertion. A conflicting
selector, unsupported encoding, geometry mismatch or extra BPM arguments with
explicit omission fail. Required detector/readout/binning/configuration selectors
are preserved; raw/active geometry is declared, never guessed from dimensions.
The BPM unit is the explicit `mask` fallback when BUNIT is absent; conflicting
present BUNIT fails the existing binding contract.

`--qc-record` is an exclusively created internal JSON handoff, not canonical
saved QC. It contains version 1, native producer/build revision, selectors,
ordered inputs and participation, raw/corrected/scan/master measurements,
raw-pair RON, the existing scan-correction profile median/sample stdev and row
counts (distinct from raw scan-pixel scatter), high-offset locations, BPM binding
and the effective configuration
object serialized directly from the native context. The separate configuration
snapshot must agree with that object before ASDF publication. JSON parsing
rejects duplicate keys, incomplete/failed records, invalid counts/availability,
nonfinite values, contradictory scan masking, invalid pairs and locations.

The explicit Python writer arguments are `--handoff ABS_JSON`,
`--qc-directory EXISTING_DIR`, `--assessment-id ID` and timezone-qualified
`--created-at TIMESTAMP`. Run `Pycavi2/pycavi/pycavi/pycavi_bias_qc.py` with the
retained qualified ASDF interpreter. It never opens a FITS image, recomputes
pixel statistics, selects a BPM/pair or installs dependencies. It maps native
MAD to the agreed 1.4826 scaling, without another median/MAD estimator.

## Saved records and provenance

The common writer creates genuine ASDF file/core standard 1.6.0 records, one
per raw input and a separate product record. Product references freeze ordered
raw participation and the selected BPM's binding record; input roles distinguish
raw biases from the BPM. The BPM record identifies its selected file/HDU and
binding only: it does not pretend to regenerate or scientifically reassess it.
All records share the native producer/revision and effective-configuration
identity. Image digests remain explicitly unavailable, not recomputed by each
recipe; image identity is the explicitly supplied absolute local path.

Saved descriptors retain sample counts, strict FITS regions, BPM state and
methods. Scan masks are not applicable. Corrected measurements remain attached
to their original raw file/HDU with their processing stage. Product RON points
to the two raw input files, never to the master. High-offset locations are
active-area FITS-1-based pairs, include known defects, and are labelled high bias
offset rather than dark current. Zero-MAD threshold degeneracy is retained.
MAD/RON not requested are unavailable, not manufactured zero-valued results.

All records are assembled before writing. Basename collisions, existing outputs
and symlinks fail without overwriting. `.fits` becomes `.asdf`; compressed naming
remains unsupported. Leaves publish first; the product publishes only after
frozen-reference checks. A later I/O failure can leave completed leaves, and a
failed handoff after native FITS publication can leave that completed FITS file;
there is no multi-file atomic transaction or automatic deletion/recovery claim.
Use an explicit fresh assessment destination for another attempt.

## Checks and limits

Agent GCC13.3 optimized C17: native_bias_qc_asdf, shared_qc_asdf,
native_bias_files, native_bias_service, native_layout and native_eclipse_allocation
all pass after their respective affected changes. The shared ASDF contract
contains ten controls, including new extension ownership checks. Final end-to-end
known-answer run passes in about 6s. Agent ASDF6.0.0/asdf-standard1.5.0 uses
NumPy2.5.4/Astropy8.0.2; this is preparation evidence, not target equivalence.
The Mac uses its existing NumPy/Astropy and retained qualified ASDF environment.

Fixtures use 18x9 raw/9x9 active images, both binary polarities, selected primary/
extension BPMs, raw/active/omitted masks, MAD/RON present/absent, row pedestals and
known high-offset locations. Independent NumPy answers check every frame's raw/
corrected statistics, master statistics and raw RON. Tests verify scan independence,
ASDF values/origins/frozen BPM+raw links, relocation, no overwrite, input hashes,
wrong HDU/EXTNAME/geometry/encoding, malformed/failed transport and configuration
mismatch. Network attempts are denied and recorded in both writer and monitor
workers. Initial preparation failures (Python class-scope import and fixture
folder collision) are retained; corrected runs pass.

`qualify_bias_files_mac.py --file-qc --qc-python ...` inventories and runs exactly
these six C17 contracts in a fresh export/build. Native tests use the selected
installed Python; ASDF workers and shared writer tests use the retained private
ASDF Python, so that interpreter needs no new Astropy installation. Version/prefix
and selected metadata/module control hashes are checked before/after, alongside
installed software, checkout and exported source. This is not a full-prefix hash
or whole-library allocation/sanitizer qualification (#144 remains open).
CMake registers ASDF handoff tests only with explicit MEFPP_QC_PYTHON; normal
native builds do not acquire an ASDF/Python runtime dependency.

No external C-library changes, dependency trial replay, Chapman/C90 matrix,
production installation/activation, observation processing or merge is implied.
Next work remains adoption of BPM-aware measurements in other recipes and the
reviewed two-path calibration/BPM workflow; no new BPM thresholds or automatic
scientific acceptance policy is introduced here.
