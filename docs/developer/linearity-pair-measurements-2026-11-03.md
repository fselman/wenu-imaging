# Raw pair measurements by amplifier and ROI — 3 November 2026

The owner agreed to measurement first, propagation through the actual trimmed
row-scan estimator and median master, and covariance fixed within each fit with
outer repeated fits to assess uncertainty in the estimated weights. This increment
implements the measurement pass. Noise-model simulations and fitting remain later
work; it introduces no distribution, photon-transfer interval or science threshold.

## What is measured

The existing Eclipse detector_gain_pair_checked routine is reused. For each
explicit two-flat pair and each named amplifier ROI, the result retains the four
raw levels, bias-referenced signal of each flat, mean signal, ordinary variance
of the flat difference divided by two, ordinary variance of the bias difference
divided by two, ordinary RON and arithmetic paired gain when available. The
kernel's mean difference and optional MAD diagnostics are also retained. Signals
and RON are ADU; variances are ADU squared; gain is electrons per ADU.

Every pair uses one common population finite in all four raw planes, within its
ROI and allowed by the supplied BPM and explicit raw saturation boundary. No
scan correction or master subtraction occurs before these differences. The raw
active bounds become a zone in the unchanged raw plane; electronic scans are
outside that zone. No cropping copies or lamp normalization are introduced.

A separate bias-only RON summary is retained for each ROI. It uses the same two
raw biases but does not inherit exclusions caused by the flat pair. This allows
comparison with each pair's matched-population RON when flat saturation or missing
pixels change the gain population. Availability flags distinguish insufficient
population from a measured zero. Finite-input difference overflow fails rather
than silently changing the accepted population.

BPM, nonfinite and saturation exclusions have that precedence. The wrapper retains
supplied-BPM and saturation counts separately; the numerical kernel's derived
selection count includes both BPM and saturation. Reason8 masks use explicit
rejection bits. Legacy binary masks retain declared polarity through the existing
loader, with no invented reason flags. An omitted mask is explicitly recorded.

Pair IDs occur exactly twice and preserve first-appearance order, source array
positions, original input indices, HDUs, asset IDs and exact individual times.
Pairs need not be consecutive. An explicit time tolerance permits header jitter
without changing those times. ROI order, original amplifier indices, active/raw
bounds, identities, configuration snapshot, saturation boundary, tolerance and
resource ceiling survive destruction of the borrowed sources.

## FITS composition and ownership

The optional measure_pairs branch of mef_linearity_from_files requires two
additional explicit raw-bias maps/references and a maximum row count. Both biases
must match raw geometry, detector/amplifier, readout, binning, ADU units and the
selected configuration slot. Duplicate/reused raw, master or mask identities are
rejected. Their pixels count against max_loaded_pixels. The caller supplies their
raw-bias classification; the positive EXPTIME rule for flats is not applied to
biases. Source paths and bindings are copied into the detached result.

Existing flat raw planes and masks are reused before cleanup. Pair measurements
and corrected samples share one atomic result owner: a later failure returns no
partial result. Borrowed pixels and FITS files remain unchanged. Existing callers
leave new options zero/NULL and receive no pair table. The native adapter produces
an in-memory measurement table, not an exported calibration or new CLI product.

## Interpretation and remaining work

Gain availability means the arithmetic can be evaluated, not that the pair is
scientifically suitable. A lamp mismatch or spatial structure may inflate its
variance. No gain interval, variance interpolation, pair suitability cut or
per-pixel variance model is chosen. ROI pooling assumes local homogeneity and
requires review against the measurements. A spatial pair difference cannot
establish arbitrary temporal noise at each pixel from only two exposures.

The same two raw biases are shared across rows. Overlapping ROIs and repeated
bias use make table rows correlated; they are not independent repeated noise
measurements. Pair differences do not measure the shared median master's error.
The corrected samples still have noise_state=MEF_LINEARITY_NOISE_UNAVAILABLE.
Empirical raw variance must not be inserted blindly as independent corrected
sample noise or double-counted with scan/master factors.

Next: explicit real-sequence
measurement orchestration and inspection. Justified distribution/pooling choices,
reproducible estimator propagation, covariance construction and full joint recipe
integration remain pending. No real OCAM data were processed here. No installation,
activation, merge, QC visualization or photometric correction is included.

## Preparation evidence and Mac gate

Agent GCC C17 focused tests passed 2/2 in 15.25 s. The raw numerical probe covers
known answers, nonconsecutive pairs, overlapping ROIs, exact/tolerant times,
raw-bias-only versus flat-selected populations, binary/reason selections,
insufficient populations, finite difference overflow, detached ownership and all
117 persistent service/configuration allocation-failure positions.

The FITS contract now has 22 cases: the previous 14 plus all four mask modes with
raw-pair measurements and raw-bias readout, loaded-pixel limit, row-limit and
identity-conflict refusals. It checks known raw RON, unaffected corrected samples,
source hashes and all 251 persistent adapter/sample/pair/configuration allocation
positions for the reason-mask measurement case. The existing small BPM adapter
control remains in that contract. Normal mefpp and the uninstalled adapter build.
The first added FITS oracle had an incorrect count/variance for its surviving
population; only that expectation was corrected, with failed output retained.

Actual Intel Mac qualification passed at source 37e11f4f5ff3247ba912e2aa8f28240e17b44428:
2/2 in 34.99 s. The owner returned native_linearity_files 34.03 s and
native_linearity_pairs 0.94 s; all checkout/installed_files/exported_source
preservation checks are true and main remains clean. Retained run:
/Users/fselman/Software/build/wenu-imaging/mac-linearity-pairs-UI4rv05W.
This qualifies synthetic behavior on the actual Mac, not real-data science.
The exact-source protected runner is
Pycavi2/tests/qualify_linearity_pairs_mac.py. It builds the new/affected probes,
normal mefpp and the uninstalled adapter, inventories exactly native_linearity_pairs
and native_linearity_files, then runs those two tests. It preserves clean main
c73d9a9e, installed files and exported source. Earlier Mac gates remain recorded;
no unchanged test matrix is replayed.

[Evidence](evidence/linearity-pair-measurements-2026-11-03/README.md).
[Agreed uncertainty policy](linearity-uncertainty-review-2026-11-03.md).
