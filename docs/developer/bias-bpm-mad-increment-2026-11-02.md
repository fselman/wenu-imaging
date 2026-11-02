# Bias BPM and MAD numerical increment — 2 November 2026

This increment implements the announced Eclipse checked statistics and opt-in
bias numerical service. It follows the source/semantics audit in
[bias-qc-eclipse-reuse-review-2026-11-02.md](bias-qc-eclipse-reuse-review-2026-11-02.md).

## Reuse and public contracts

- `double_median_mad_checked` in Eclipse `src/math/dstats.c` composes the existing
  `double_kth_smallest` order statistic. Input is unchanged; even medians average
  the central two values. It returns raw MAD, with no implicit Gaussian scaling.
  Legacy median and mean-absolute-deviation functions remain unchanged.
- `image_getstats_masked_checked` in `src/iproc/image_stats.c` reuses
  `image_getstats_opts` for mean and sample standard deviation (N-1), with an
  explicit strict inclusive FITS ROI and Eclipse BPM polarity 1=good/0=excluded.
  It records region/BPM-excluded/nonfinite-excluded/valid counts. BPM exclusion
  takes precedence in the count partition. No clipping or interpolation occurs.
  Empty samples have unavailable levels; fewer than two have unavailable stdev.
  Zero MAD is a valid value. Output is unchanged on error.
- `image_pair_stats_checked` composes existing `image_sub`, map copying and
  `pixelmap_binary_AND`; independent maps select their good-pixel intersection.
  No correction or RON scaling is hidden in the generic function.
- Scoped allocation guards in existing statistics/subtraction/map constructors,
  copying and extraction support these checked compositions. Remaining wider
  dependency allocation qualification is tracked in #144, which stays open.

## Bias service

`mef_cal_bias_measurements` accepts explicit options without extending the old
input struct. The old `mef_cal_bias` entry remains a wrapper with legacy behavior.
The new options require either a raw-coordinate Eclipse BPM matching the selected
MEF_CAL_BPM request, or NULL with explicit request omission. Geometry, polarity
and metadata contradictions fail; there is no guessed file/HDU/polarity mapping.

The supplied BPM selects scan correction samples, corrected-frame means used
for frame rejection, and raw-active/corrected-active/master measurements. Existing
scan rejection counts and median stacking arithmetic are reused. Too few good
scan samples fail rather than falling back to contaminated samples. Output
pixels are not interpolated or replaced using the BPM. Bias input validation
still requires finite raw pixels, even if masked; the generic statistics helper
separately supports reporting nonfinite exclusions.

Per-frame scan/raw/corrected records and master masked/unmasked records are owned
by the result. Standard deviation is the ordinary good-pixel estimator; MAD is
optional. If requested, RON uses explicitly indexed distinct RAW input frames,
subtracts before any overscan correction and measures the active region:
`stdev(B1-B2)/sqrt(2)` in ADU, with optional `1.4826*MAD(B1-B2)/sqrt(2)`.
There is no gain conversion or automatic pair choice.

High-offset diagnostics use master median + positive configurable k times
1.4826*MAD (owner initial choice k=5). They record threshold, count and an
active-coordinate location map, including known bad master pixels. This map
uses 1=flagged, explicitly not good-pixel BPM polarity. Zero-MAD thresholds
are marked degenerate. These diagnostics never create or apply a new BPM.

## Verification and limits

Agent-side GCC 13.3, optimized C17: four focused CTest contracts passed, zero
failures, 4.20 seconds: native_measurement_stats, native_bias_service,
native_bias_files and native_eclipse_allocation. The final bias service and
allocation probes exercise both OmegaCAM and WFI configuration snapshots.

Known answers independently cover even medians/MAD, sample variance, masked
outliers, ROI and count partitions, nonfinite values, empty/singleton samples,
input immutability, pair-map intersection and unchanged outputs on errors.
The bias fixture uses row-dependent raw pedestals to distinguish raw RON from
corrected-pair RON. It verifies masked scan correction and frame rejection,
known-defect high-offset locations, optional/unavailable QC, metadata/geometry/
scan exhaustion errors, result lifetimes and each new owner allocation failure.
Existing exact legacy profiles, file publication and dependency failure sweeps
also pass. The first attempt retained a test expectation error and a Python
without Astropy; corrected evidence uses the existing preparation environment.
This is agent evidence, not Intel Mac or scientific/observational acceptance.

The existing protected Mac runner has `--measurements` to rebuild C17 and run
exactly these four contracts in a fresh private source/build export. No install,
ASDF dependency provisioning, old unchanged ASDF tests or Chapman replay follows.
Actual Mac result is pending. Existing broader Eclipse global allocator limits
remain; no whole-library OOM, sanitizer or leak-tool qualification is claimed.

Next integration work remains explicit FITS BPM loading/selector/polarity binding,
native QC-to-shared-ASDF handoff, and reuse across other recipes and BPM creation.
No CLI flags, production activation or automatic two-pass BPM algorithm are
claimed by this numerical-service increment.
