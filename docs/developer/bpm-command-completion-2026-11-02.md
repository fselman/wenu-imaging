# BPM command and whole-operation completion

Actual Mac completion returned at 022cf3683fe47d4de6a7acac1e3799cb49201d40:
2/2 contracts passed in18.63s, retained mac-bpm-complete-Ia5qliwa, all four
preservation checks true and main clean. This supersedes pending-Mac statements
below for that exact revision. Continue the [Chapman changed-code gate](bpm-chapman-qualification-2026-11-02.md)
before actual calibration data tests.

## Qualified basis

Actual Mac revision 00ee1491930ec8d77968cb4b137c48ac60ce0502 passed
native_bpm_service/native_bpm_files/native_bpm_publication in 20.81 s. Evidence:
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-publication-Ev9dMXuD`.
Installed files, checkout, exported source and retained qualified QC controls were
preserved; protected main stayed clean. This qualifies that publication revision,
not the command increment described here. Actual Mac command qualification is
pending.

## Composition and explicit input contract

`mefpp_m5 cal bpm` now dispatches through the existing M5 entry point to a small
BPM adapter. It composes the existing configuration readers, M4 bound image
loader, operation-template request/context, BPM service/file admission and checked
FITS/handoff publisher. It introduces no numerical fitter, scientific threshold
default, discovery or detector-wide mosaic timing assumption.

The command processes one explicitly identified/configured detector at a time.
Its required flat manifest has three tab-separated fields per line:

| Field | Meaning |
| --- | --- |
| Absolute FITS path | Physical input identity; spaces allowed, tabs/newlines excluded |
| HDU | Explicit zero-based image HDU; may differ between files |
| Pair ID | Explicit zero-based grouping identifier; quick admission checks pairs |

Every row is an input, with no header or blank rows. Pair IDs must be below the
input count. Limit: 1,024 flats per invocation. No pair is inferred from file order,
name or time. Provisional input still supplies pair IDs but does not claim quick
paired acquisition. The TSV extends the bias command's explicit-list pattern
because each flat needs its own HDU and pair selector; it is not an alternate
configuration or QC format.

The ROI file contains up to 1,024 rows, each four whitespace-separated positive
integers: `xlo xhi ylo yhi`, in one-based inclusive ACTIVE coordinates. The existing
service checks bounds and measures their union, including overlaps without double
counting. Configuration supplies trim/scan geometry, fitting mode and response
thresholds. Exposure-key/header-HDU, saturation, upper fraction, minimum span,
pair tolerance, MAD choice, readout and binning are explicit command options.

A selected ACTIVE master bias and its HDU are required; this command does not
construct a master bias from raw biases. Produce/select it with the bias recipe.
Prior omission or selection is explicit. A selected prior specifies its HDU,
raw/active coordinates, and either reason8 registry/rejection bits or binary good
value (0 or 1). Binary input requires NEW output mode, preserving its selection
without invented reasons. Reason8 can request NEW or supported COMBINED output.
Primary BPM remains unsigned 8-bit, zero meaning no detected reason; coverage and
sample counts remain separate. Detector masks never apply to electronic reads.

## Complete recipe boundary

Run the source module `Pycavi2/pycavi/pycavi/pycavi_bpm_qc.py` with the qualified
ASDF Python. It takes `--native-adapter`, `--receipt`, `--qc-directory`,
`--assessment-id`, then `--` followed by the native `cal bpm` options. The canonical
UTC `--created-at` value is supplied among the native options, so FITS and ASDF
share a single timestamp. The adapter's compiled exact revision supplies source
identity. `mefpp_m5 cal bpm` without options prints the complete native syntax.

The wrapper preflights fresh absolute native destinations and a fresh execution
receipt, existing work/QC directories, unique QC names, schema and ASDF writer.
It fingerprints all flats, selected calibrations, manifest, ROIs, configuration,
adapter and completion module before execution. The command creates a fresh log,
configuration snapshot and internal handoff, invokes the qualified numerical
pipeline, then publishes FITS exclusively. The wrapper validates the handoff,
uses the existing shared ASDF writer, consumes frozen-link traversal, verifies
saved product identity and input fingerprints, and only then emits
`BPM_RECIPE complete` and a complete receipt.

The JSON receipt is execution evidence, not saved QC. Failure records its stage
(preflight/native/qc/verify), native status and error. An existing receipt is
never opened for replacement. Existing FITS/log/configuration/handoff/ASDF files
are never overwritten. A failure after FITS publication retains that FITS and
any completed diagnostic records. No automatic retries, deletion or multi-file
atomicity claim. A native-only zero exit certifies FITS/handoff publication; the
wrapper's zero exit certifies the whole FITS/ASDF operation.

## Verification and next target gate

Preparation runs optimized C17, nice >=10, one BLAS/OpenMP thread. The focused
selection is `native_bpm_completion` plus `native_bias_files`: the entry point now
dispatches both operations, so the established bias command needs a regression
check. Agent preparation passed both contracts in 7.33 s (bias 1.75 s, BPM
completion 5.58 s), with Python syntax/whitespace checks passing and no new-unit
compiler warnings. This is preparation, not target acceptance. Twelve synthetic complete-command cases cover PAF/TOML, both existing fit
modes, quick/provisional admission, selected/omitted priors, both binary good
values, raw/active coordinates, entirely excluded flats, exact byte reasons and
missing coverage, protected output/receipt, wrong HDU, malformed manifest,
unsupported binary combination and a late QC destination conflict. The latter
retains successful FITS but cannot report recipe completion. Physical inputs and
the native adapter remain byte-identical.

`--bpm-complete` in the guarded Mac runner builds only mefpp_m5/mefpp and inventories
exactly these two contracts. It uses the retained ASDF interpreter and compares
its controls before/after, along with installed-file, checkout and exported-source
preservation. Prior component gates remain retained, not replayed. Actual Mac
acceptance is pending. No installation, activation, merge or checkout switch.

After Mac acceptance, validate the changed code on Chapman before full actual
WFI/OmegaCAM tests. Gain/RON, full linearity and the shared signed shutter model
remain future characterization work. The formula PDF/LaTeX and initial CCD-style
CMOS policy are unchanged. This synthetic gate is not observational acceptance.
