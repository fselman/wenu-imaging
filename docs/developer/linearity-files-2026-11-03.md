# Explicit FITS linearity admission — 3 November 2026

`mef_linearity_from_files` connects supplied, already bound FITS planes to the
qualified raw-plane sample service. It checks the supplied sources and metadata,
loads the selected detector planes with the existing M4 loaders, then reuses the
same scan/crop, bias subtraction and pixel admission. It does not discover files,
infer pairs from filename order, estimate uncertainties or fit a calibration.
No actual OCAM files have been processed in this increment.

## Explicit source selection

The caller supplies one bound map and image reference per flat. Each reference
asserts its asset ID, detector ID, resolved path and zero-based HDU. The adapter
requires one selected detector per map and checks that the reference and binding
agree. Detector ID, configured amplifier identity and configuration-detector index
remain separate from file/HDU order. An amplifier identity reported in the bound
header must agree with the selected amplifier; an absent reported identity remains
an explicit configured claim, not a hardware verification.

Every raw binding must match the configured active crop, ADU unit, readout context
and binning. The selected bias and optional BPM must have compatible active
geometry/readout/binning and be active-only planes with active origin (1,1).
Primary-image and MEF-extension inputs may be mixed. Unselected extensions are not
used as science samples. Duplicate raw assets, original indices or path/HDU pairs
are rejected, as is reuse of a raw source as a selected calibration. Bias and BPM
cannot share the same asset or selected path/HDU.

The adapter checks metadata before pixel loading. It reuses the BPM adapter's
exact path/HDU/binding check and exact positive exposure-header parser. Those
functions were moved unchanged to `mef_file_metadata_internal.h`, not rewritten.
The positive-number parser rejects missing/duplicate cards, nonfinite or invalid
values and accepts the existing Fortran D exponent convention. It does not choose
an instrument's exposure keyword: the caller supplies the full qfits spelling
and explicit header HDU, independently of the image HDU.

This is not raw classification or association. DPR.TYPE, instrument identity and
which calibrations belong to a run must be resolved upstream. A configured
readout claim is not independently measured electronics behavior. Multiple
amplifiers inside one HDU still need explicit splitting/coordinate mapping;
this first adapter loads one resolved amplifier plane per call.

## Pairing without adjacency or rounding

Every flat carries an explicit pair ID and original input index. Each pair ID
must occur exactly twice, wherever its members appear in the supplied order.
The two exact header integration times must differ by no more than a caller-set
nonnegative tolerance in seconds. There is no default tolerance, exposure
rounding, pair sorting or adjacent-frame assumption. Original frame order, asset
ID, input index, HDU, pair ID and exact times are retained in the sample result.

A tolerance admits a pair; it does not replace either time with a common value.
It also does not assess lamp stability or certify coverage of a linearity/gain
curve. No lamp factor, exposure-normalized image or fit-range decision is created.

## BPM encodings

The mask encoding must be explicitly one of omitted, REASON8, or legacy binary.
REASON8 uses the existing exact byte loader, matching MASKENC/MASKREG and the
caller-selected reject bits. Binary uses the existing M4 binary loader with an
explicit good value of 0 or 1; it becomes an Eclipse selection (1=good).

The in-memory sample interface now accepts that binary map as an alternative to
byte flags. Supplying both is an error. Binary masks do not acquire invented
reason bits, and the result separately records bpm_binary_supplied. Reject bits
apply to byte flags only; binary rejection follows the declared polarity.
Both encodings count rejected active pixels as BPM exclusions. Neither encoding
masks electronic scans. The raw-ADU saturation cut and nonfinite admission rules
are unchanged. Per-frame sample maps remain supported by the in-memory service;
this initial FITS adapter does not accept separate per-frame mask files.

The adapter's sample template supplies configuration, amplifier identity/index,
named bound ROIs, saturation and software ceilings. Its raw/frame/master/BPM/
per-frame sample pointers must be NULL, and bpm_count zero, because the adapter
loads these sources itself. It rejects occupied payload fields rather than
silently overwriting them. No output FITS or ASDF is published.

## Source records and ownership

The result owns input path and binding snapshots, bias/BPM paths and asset IDs,
calibration bindings, encoding/polarity/registry, exposure keyword/HDU, pair-time
tolerance, loaded-pixel ceiling and the detached numerical sample result.
The sample result owns the immutable configuration and its scan/admission choices.
It survives destruction of caller maps, references, configuration and descriptors.
`mef_linearity_files_destroy` releases these owners. All caller inputs and FITS
headers/payloads remain unchanged; failure leaves the caller output untouched.

Caller-supplied max_loaded_pixels bounds the sum of raw and selected calibration
plane pixels. It is a software input-size ceiling, not a promise about total
resident memory: the existing correction makes private work images and has its
own allocations. max_sites/max_observations retain the sample-service ceilings.
This serial reference adapter is not a full-mosaic throughput implementation.

Sources must remain frozen by the caller while reading. Existing M4 source
identity/load checks are reused; this is not a filesystem snapshot lock or a
cryptographic freeze of every raw file. File digests and frozen ASDF source links
remain later publication responsibilities. Existing dependency allocator/global
behavior is unchanged, with no new thread-safety or dependency-OOM claim.

The sample noise state remains explicitly unavailable. The separately qualified
covariance assembler can combine supplied components, but this adapter does not
estimate them, supply a default gain/variance or automatically invoke a joint fit.

## Synthetic checks and target gate

Agent GCC C17 Release preparation passed 2/2 in 3.31 s: native_linearity_files
and the affected native_linearity_samples. Normal mefpp, the uninstalled command
adapter and all selected probes build; no new warnings were emitted. The new
Python fixture/qualifier syntax is checked.

Fourteen tiny generated-FITS cases exercise primary images and extension HDU 2
(with an unrelated HDU 1), nonconsecutive pair order P0/P1/P1/P0, unsorted original
indices, exact/tolerance-admitted exposure times, omitted/reason/both binary masks,
known corrected samples, row scan subtraction, nonfinite and equality-at-limit
saturation cuts, invalid/missing/duplicate exposure metadata, wrong amplifier,
wrong HDU/readout/pair/registry and input-size rejection. Hashes of every fixture's
header and pixel bytes remain unchanged after each case. All 132 adapter/sample/
configuration-owner allocation positions fail persistently with no output or
leaked custom owners. Inputs/maps remain usable and detached outputs survive
source-descriptor destruction.

The same fixture driver also invokes the existing BPM file probe on a separate
two-exposure primary/MEF fixture, with its independent known response/reason
answers. This exercises the extracted metadata helpers through their previous
caller, not only through the new adapter. The in-memory control additionally
checks mutually exclusive byte/binary inputs and equivalent legacy selection
without invented reasons. Its prior byte-mask controls remain passing.

The agent environment lacks Astropy, so its full existing native_bpm_files
Python suite was not replayed here; the unchanged C caller is exercised by the
standard-library fixture above. The focused actual Mac qualifier runs exactly
native_linearity_files, native_linearity_samples and native_bpm_files using the
normal imaging Python with its already used FITS dependencies. It exports exact
source, builds those probes plus mefpp_m5/mefpp, verifies the test inventory and
protects checkout/installed/exported-source identity. Actual Mac FITS-admission
qualification subsequently passed at 10027f1e: 3/3 in 20.91 s, retained
`/Users/fselman/Software/build/wenu-imaging/mac-linearity-files-nF68I1UL`.
This includes the full affected BPM Python suite; checkout/install/export all
passed and main stayed clean c73d9a9e. No unrelated numerical replay or installation.

The preceding covariance assembly at c381168b7ca00b52b79d947addc483e0cc29e05b
passed actual Mac 4/4 in 3.69 s, retained
`/Users/fselman/Software/build/wenu-imaging/mac-detector-noise-z4pHBH0H`.
Checkout, installed files and exported source all preserved; clean main c73d9a9e.
This records the owner's returned terminal evidence, not independent access to
those retained files.

Next are justified uncertainty estimates/selection, forward-model and complete
recipe/CLI integration, followed by reviewed actual-data tests. No real OCAM fit,
science acceptance, product publication, activation or merge is implied.

The next [uncertainty policy review](linearity-uncertainty-review-2026-11-03.md)
identifies the actual median-master estimator and proposes measurement-first,
conditional propagation with fixed covariance. No new statistical default or
actual-data execution is selected by that proposal.
