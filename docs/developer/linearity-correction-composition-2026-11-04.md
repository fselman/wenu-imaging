# Joint correction-curve composition — 4 November 2026

Issue#236, draft PR227. Owner explicitly directs continuing the correction-producing
linearity recipe. Raw pair/gain/variance tables are diagnostics, not the final
pixel-response calibration. Preserve independent plotting/HTML stages and defer
left-edge recipe navigation until linearity completion.

## New numerical recipe boundary

`detector_linearity_fit_checked` composes the already qualified supplied-covariance
assembler and joint shutter-profile fitter. It accepts fit-admitted, corrected
DIRECT PIXEL samples, explicit independent/master/scan covariance components,
scientific provenance identifiers, bounds/scales/starts and profile request.
It estimates no noise model, gain, distribution, uncertainty floor or fit interval.
No ROI mean is treated as a pixel and no frame-dependent illumination is added.

The covariance service's QR permutation is essential: the wrapper obtains the
ordered observations AND corresponding absolute factor through the existing
borrowed measurements view, then passes them together to the joint/profile fit.
Original physical sites and original input-frame indices remain unchanged. One
signed shutter offset is common to all admitted detectors. The supplied covariance
is fixed throughout the free fit and every conditional shutter-profile refit.

Only a numerical joint CANDIDATE with a BRACKETED shutter profile exposes owned
amplifier curves. For bias-subtracted ADU signal S:

    S_linear = S + c2*S^2 + c3*S^3

The leading coefficient is exactly one and there is no additive bias intercept.
Coefficients c2/c3 have units ADU^-1/ADU^-2. The result retains one common delta
in seconds; per-amplifier identity, coefficients, declared inversion/monotonic
interval, actual observed signal extent and local conditional covariance in
order [delta,c2,c3]. The full physical covariance, including cross-amplifier terms,
all site/frame identities, numerical options, free/profile starts, supplied noise
components, QR permutation and factors remain in the owned nested results.
Declared model bounds do not imply empirical coverage or accepted extrapolation.

Explicit NOISE_UNAVAILABLE, FIT_UNAVAILABLE and PROFILE_UNAVAILABLE states retain
available diagnostics but expose zero curves, a NULL curve pointer and NaN common
delta. Missing covariance/provenance/profile inputs, hard errors and allocation
failures leave the output owner unchanged. All inputs remain borrowed/immutable;
results survive their destruction. There is no scientific-acceptance status.
Legacy detector_linearity_fit and all existing noise/joint/optimizer/QR numerical
sources remain unchanged. New API lives in detector_linearity_fit.h.

## Validation

Agent GCC C17 Release: native_linearity_fit passes0.44s and
native_linearity_fit_allocation passes0.34s;2/2 in0.78s total. Normal mefpp builds.
Dependency warnings remain; new composition source is warning-free. See retained
LastTest.log in evidence/linearity-fit-composition-2026-11-04/agent-c17-tests.log.

Synthetic data reuse the independent Newton generator at two distinct physical
pixels/amplifiers, ten non-monotonic exposure durations, and three signed shutter
offsets. Explicit heteroscedastic independent noise, shared cross-site master
noise and correlated scan errors force a nonidentity QR observation order.
Checks establish coefficient/offset recovery and correction of independently
generated signals; identity/factor permutation matching, conditional covariance
extraction, declared versus observed range separation, immutable inputs, detached
owners, occupied-output refusal, rank/condition/coverage/profile unavailability,
missing scientific inputs and hard profile failures. Both new composition-owned
allocation positions are failed singly and persistently with complete qfits owner
accounting. Existing dependency allocation/numerical suites are qualified and are
not replayed; the new probe does not claim to inject their internal allocations.

Focused actual Mac qualification is pending via qualify_linearity_fit_mac.py.
It first verifies unchanged noise/joint/QR/optimizer/shared-validator bytes against
passed c381168b mac-detector-noise-z4pHBH0H, then builds normal mefpp plus exactly
the two new probes and runs only those two C17 controls. Preserve checkout,
installed files and exported source; no activation, package installation, old
matrix, observation processing or scientific calibration follows from this gate.

## Remaining recipe work

This is an in-memory composition boundary, not a completed FITS-to-calibration
CLI or an actual-data correction. It has not fitted the32-detector sequence.
Next connect bounded corrected-sample preparation and independently established
noise/correction provenance, preserving one GLOBAL shutter offset across the
selected detectors; do not fit detectors separately and combine their delays.
The dense reference fitter cannot accept millions of pixel parameters as though
it were a demonstrated full-mosaic solver. Explicit compact physical samples or
a reviewed scalable forward model are still required; ROI means are not a shortcut.

The agreed noise-model review/propagation through actual trimmed scan and median
master operations remains necessary. No distribution/pooling rule, simulation
count/seed, fit interval or reference gain is chosen. Shared master noise cannot
be estimated from flat differences alone or assigned RON^2/N for a median stack.
Raw row scatter is not scan-estimator uncertainty. Real-data noise-model choices
and suitable coverage must be established before publishing actual coefficients.

Persist candidate curves, absolute covariance, fit/profile state, provenance and
explicit validity limits through shared ASDF when the run/publication boundary is
added; a numerical candidate is never silently accepted for pixel correction.
Later application belongs in mefpp with interval guards and provenance. Full
photometric comparison and higher-signal coverage are separate later validation.
Keep existing32-detector measurements/ASDF/HTML and all required runtimes unchanged.
No install, merge, cleanup, pixel correction or forced real-data fit is authorized
by this numerical qualification.
