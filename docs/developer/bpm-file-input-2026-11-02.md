# BPM bound-file acquisition and signal coverage

## Qualified basis and current scope

Fernando returned actual Mac success for the typed service at
970bdfb9ad232df353aab18c7a1cd2f0957c737e: native_operation_template and
native_bpm_service, 1.72 s total. Retained run:
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-service-AUUCnlyT`.
Installed files, checkout and exported source were preserved; main stayed clean.
The response core at14e9bb6 has separate actual Mac evidence (4.22 s).

This increment adds `mef_bpm_from_files`, composing the existing M4 bound-layout
loader and typed numerical service through the operation template. It is an
in-memory result from real FITS I/O, not yet a published recipe product or CLI.
The PDF/LaTeX design and the initial CCD mechanism for CMOS remain unchanged.

## Explicit acquisition and metadata admission

- One detector per call; every request path, original HDU, optional EXTNAME/VER,
  configuration slot, unit, readout/binning and active geometry must match its
  supplied bound map. Bias and prior roles/maps are explicit. No discovery or
  PAF-default mask fallback. Independent physical selectors may mix primary and
  MEF images in one sequence. Duplicate physical image references are rejected.
- Read a caller-selected exposure-time keyword at an explicit header HDU.
  Require exactly one finite positive numeric card; missing, duplicate or
  malformed values fail, without searching another header/keyword.
- Quick mode requires at least ten flats grouped by explicit pair IDs, exactly
  two flats per ID with identical integration times, and at least five times.
- After signal cuts, require at least five complete usable pairs at five
  distinct times and five distinct measured pair levels. Pair level for this
  admission diagnostic is the mean of the two reference medians. An unmatched
  leftover frame cannot supply a missing paired level. Actual fitting still
  uses individual measured frame medians, never integration-time normalization.
- Provisional mode requires two distinct usable measured levels. It is labelled
  provisional; no linearity, gain or RON result is invented.
- Maximum fractional within-pair signal difference and minimum reference-signal
  span are caller-supplied parameters, recorded in QC. Pair mismatch is
  `abs(x1-x2)/((x1+x2)/2)` for positive measured reference levels.

## Saturation, frame exclusion and coverage

Raw saturation is a physical ADU value, consistently including any FITS scaling.
The upper accepted fraction is explicit, in (0,1]. For corrected signal s at a
pixel, the local usable saturation is

    usable = saturation_raw - (raw - s)

because `raw - s` includes the actual scan subtraction plus selected master bias.
Accept only unsaturated raw samples with positive usable range and

    s < upper_fraction * usable

alongside finite data and any explicit external sample selection. This composes
existing sample maps; it introduces no fitter or clipping estimator. Electronic
scan samples never receive the detector BPM.

Record saturated, margin-excluded, externally excluded and nonfinite counts;
reference sample counts and included/excluded frame state; original indices for
every fitted reference level; and the median reference fraction `s/usable` for
each usable frame. Overlapping ROIs contribute their union, without duplicate
pixels. Quick-mode span is max minus min of the complete-pair mean reference
fractions; provisional mode uses individual frames. A lone frame cannot rescue
the minimum paired signal span.

Entire frames with no usable reference pixels are explicitly excluded, retaining
their provenance and counts. At least two usable frames remain necessary for the
numerical service. Existing service tests are updated for this deliberate change
from failing whenever any one reference plane was empty. The Eclipse core itself
and its legacy constructors are unchanged. Missing per-pixel fits remain
unavailable, not certified good or assigned a fabricated defect bit.

## Prior masks and owned results

Support explicit reason8 versus binary polarity and explicit raw versus active
coordinates. Raw priors are cropped using the configured active rectangle;
there is no dimension-based guessing. Reason masks require BITPIX=8, unity
scaling, MASKENC=REASON8 and the supplied registry tag. Binary masks reuse the
existing strict selected-HDU loader. Calibration geometry/readout compatibility
uses M4. Caller freezes files/maps during the call; this is not a snapshot lock.

Return the service result plus owned exposure times, pair IDs, ROI coordinates,
selected thresholds and admission diagnostics. These survive destruction of the
context, maps and caller descriptors. All temporary images/masks are cleaned on
failure; no output result transfers until acquisition and coverage checks pass.
No FITS/QC product is written by this boundary.

## Preparation tests and focused Mac gate

Purpose: verify actual C selected-plane I/O and acquisition/saturation composition
before publication. Inputs: generated tiny FITS arrays and actual WFI/OmegaCAM
configuration snapshots, with explicit synthetic geometry overrides. No actual
astronomical observations or installed products are used.

Actions/pass criteria: 22 bound-FITS cases cover both fit modes/instruments,
mixed primary/MEF images (with a deliberately wrong extra detector HDU), both
prior coordinate systems and binary polarities, bit preservation, provisional
two-flat admission, high-response pixel margin/saturation counts, entire
reference-empty frames, exposure/pair/registry/readout errors, lamp disagreement,
narrow span, insufficient levels and partial pairs that must not rescue the
required number or signal span of complete illumination levels. Inputs and configuration hashes
must stay unchanged; output diagnostics have independent known answers. Logs and
generated inputs are retained. The affected service's ownership/failure controls
also run because its sample selection changed.

Agent optimized C17/GCC13.3: native_bpm_service and native_bpm_files passed
(3.05 s total), with Python syntax/whitespace checks and no new-unit warnings.
An initial fixture assertion incorrectly counted a deliberately low-response
pixel as saturated; it was corrected to the independently expected 23 saturated
pixels and zero usable reference pixels. No scientific threshold changed.

The --bpm-files private Mac gate builds only bpm_files_probe/bpm_service_probe,
inventories exactly native_bpm_files/native_bpm_service and checks installed
files, checkout and exported-source preservation. The unchanged core, general
measurement and ASDF gates are not replayed. Actual Mac qualification of this
increment is pending; Chapman/real-data acceptance follows later.

The test fixtures explicitly choose upper_fraction=0.85, minimum_span=0.15 and
pair tolerance=0.02 to exercise the checks. These are test choices, not hidden
production defaults or newly accepted instrument thresholds.

Next: exclusive checked FITS publication, file CLI/common ASDF completion using
the bias template, then joint linearity/shared shutter work. Installation,
activation and merging remain outside scope.
