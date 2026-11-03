# Raw-plane linearity samples — 3 November 2026

The next bounded recipe component prepares actual pixel samples from borrowed
raw image planes. `mef_linearity_samples` reuses the existing row-by-row scan
correction, cropping and image subtraction. It makes private raw-frame copies,
subtracts the selected active scan-corrected master bias, and admits finite,
unsaturated active pixels selected by the BPM, per-frame mask and union of ROIs.
An overlapping region does not duplicate a measurement or increase sample count.

This is an in-memory service, not a raw FITS reader, complete linearity command,
noise estimator or fitted calibration. No actual OCAM pixels have been processed.
The unchanged fitting interface must not receive this output until a valid
absolute covariance model is attached. No identity/diagonal covariance, empirical
noise floor, gain choice or lamp normalization is inserted to make a fit run.

## Inputs and retained identities

One explicitly resolved amplifier plane is processed per call. The caller supplies
its detector/amplifier identity, its index in the same amplifier list used for
ROI binding, and an independent zero-based configuration-detector index. These
indices are never inferred from an HDU, chip name or input position. The service
selects only that amplifier's named ROIs and validates active dimensions. Multiple
amplifiers in one detector/HDU require an explicit upstream splitting/coordinate
mapping step; this service does not guess one.

Each original frame retains an asset ID, pair ID, zero-based original input index,
zero-based HDU and exact positive integration time. Original frame order remains
unchanged even when indices are not sorted. No exposure rounding, chronological
sorting, adjacency pairing or requirement that pairs be consecutive is introduced.
Pair IDs are retained metadata; acquisition-pair validation and file/reference
resolution remain the later adapter's responsibility. Asset/index duplicates and
invalid/unterminated metadata are rejected.

The master is already in active coordinates and scan-corrected ADU. Dimensions
and finite master values are mandatory; no bias is synthesized. The byte BPM uses
0=good and an explicit reject-bit mask. If absent, omission remains recorded.
Legacy Eclipse binary BPMs must be explicitly converted upstream; polarity is
never guessed. Optional per-frame selections are active Eclipse maps (1=good).
No detector mask removes electronic scan pixels. Electronic scan reads must be
finite, including rows outside the cropped active area, because the existing
correction processes each raw row.

The finite positive raw-ADU saturation limit is explicit. A raw sample equal to
or greater than the limit is rejected BEFORE any interpretation of its corrected
signal. The service does not choose a near-saturation margin or scientific fit
range. Configured scan/crop and selected bias establish the signal, not a free
bias intercept. An explicitly configured no-scan case crops/subtracts only; this
software branch is not a decision to omit overscan from the real WFI/OCAM work.

## Selection and output

Each active pixel receives exactly one population classification, in precedence:

1. Outside the selected ROI union.
2. Rejected by the supplied BPM bits.
3. Rejected by that frame's sample-selection map.
4. Nonfinite raw or corrected signal.
5. Raw signal at/above saturation.
6. Admitted sample.

Thus counts sum to active width times height for every frame. These are admission
counts, not QC acceptance thresholds. Earlier exclusions can conceal a later
condition, so the counters must not be interpreted as independent totals of all
saturated/nonfinite pixels in the full raw frame.

The output owns frame identities, per-frame population counts, selected named ROIs,
active dimensions, copied scan settings and full immutable configuration snapshot.
It retains explicit BPM-supplied/reject-bit and saturation choices. Admitted sites
are unique active pixels in row-major order; observations retain caller frame
order followed by row-major pixel order. Sites with no admitted observations are
removed and observation site indices are remapped. Empty successful output has
zero site/observation counts; it is not a zero-valued exposure or a calibration.
Result-local amplifier indices are zero; the original amplifier-list index and
named identity remain separately recorded.

`mef_linearity_samples_destroy` releases all returned owners. Inputs remain
borrowed/immutable during the call; neither frames nor master nor masks are owned
by the result. The result does not retain full corrected images or masks, nor
resolve asset IDs to paths or frozen ASDF references; the later file adapter must
preserve those sources. Caller-supplied max_sites/max_observations bound software
resources. max_sites bounds the potential BPM-selected ROI union, even if some
sites later have no observations. Observations are allocated only up to the
explicit limit and exceeding that limit fails without publishing partial output.
This serial reference service is not claimed as a full-mosaic performance result.

## Covariance remains unavailable

`noise_state` is explicitly `MEF_LINEARITY_NOISE_UNAVAILABLE`. There is no noise
factor and no convenience conversion to `detector_measurements`. The selected
master's shared error, row-scan correction uncertainty/correlation and pixel
photon/read-noise model still need to be represented and justified. The earlier
ROI operator will propagate a supplied valid model; it cannot invent one.
Likewise ROI means cannot replace physical pixels in the direct-pixel fitter.

## Synthetic qualification and next host gate

Agent GCC C17 Release preparation passed `native_linearity_samples`, 1/1 in
0.01 s. The normal mefpp target builds; the new service/probe compile without new
warnings. A two-frame 6-by-4 synthetic raw image has varying row scan levels and
a 4-by-2 active area. The known answer independently specifies seven corrected
samples over five physical sites, preserving original indices 8 then 3, times
2 then 5 seconds and explicit HDU/pair identities. Two overlapping rectangles
select their union; a byte BPM, per-frame selection, a NaN and equality-at-limit
saturation exercise distinct admission categories. Exact sample values test
row-dependent subtraction and master removal, not just matching another wrapper.

Controls also cover atomic occupied outputs, duplicate frame indices, observation
and site resource exhaustion, nonfinite electronic scan input, fully empty
admission, configured crop-only processing, input preservation and result lifetime
after metadata/configuration/images are destroyed. All 119 service/configuration
snapshot allocation positions are failed persistently; every owner is released.
This allocator test does not claim new fault injection into unchanged Eclipse
image/scan internals, whose existing controls remain separate.

The prepared `Pycavi2/tests/qualify_linearity_samples_mac.py` exports exact source,
builds the new probe and normal mefpp, runs only native_linearity_samples, and
checks checkout, installed files and exported-source preservation. Its syntax is
checked. Actual Mac sample-admission qualification subsequently passed at 88e29306:
1/1, 1.04 s test / 1.05 s total, retained mac-linearity-samples-fRlf0Hgk,
with all three preservation checks true and clean main c73d9a9e. No unchanged
numerical/configuration gates are replayed. Raw FITS binding, noise construction,
forward-model fitting, publication, actual OCAM results and science acceptance
remain subsequent work. No installation, activation or merge.

The previous named ROI-configuration gate at
8e8930086262e7406378519da4379a0cdb3a2d9b passed actual Mac C17 1/1 in 1.21 s,
retained `/Users/fselman/Software/build/wenu-imaging/mac-roi-config-PHwS5VBY`.
Checkout, installed files and exported source all preserved; clean main c73d9a9e.

[Explicit covariance assembly](detector-noise-2026-11-03.md) now combines supplied
components; it does not estimate them or automatically attach noise to these
samples. Its actual Mac gate remains pending.

The [FITS admission increment](linearity-files-2026-11-03.md) adds an explicit
legacy binary BPM alternative to the sample API. Both byte+binary together are
rejected. Binary stays an Eclipse selection, with separate bpm_binary_supplied
provenance and no invented reasons; original byte/admission arithmetic is retained.
The affected sample control is rerun in that increment; its Mac gate is pending.
