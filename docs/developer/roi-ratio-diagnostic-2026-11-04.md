# Same-exposure readout-side ratio diagnostic

Owner requested 4 November2026. Compare near_readout/parallel_far in each
individual exposure. These regions share x and differ in y. No frame averaging
or pairing by time alone. Save raw ratio, normalized ratio and percent departure
before plotting. Reference is the arithmetic mean of individual ratios where
BOTH signals lie in15000..35000ADU inclusive. Record its members/count/value.
Uncertainties remain unavailable; normalization introduces shared covariance.

`tools/compute-roi-ratios.py --source-index <completed-residual-index> --run <fresh>
--source-revision <40sha>` writes immutable per-detector ASDF through the common
QC lifecycle. It reads stored original ROI measurements without refitting lines
or opening raw FITS/native tables. A fresh completion index freezes sources.
Expected real coverage32detectors*20exposures=640ratios. Invalid signals and
unavailable reference remain explicit. Originals and previous diagnostics stay
unchanged. ASDF includes the shared descriptive comment header.

`tools/view-pair-qc.py --batch <retained-batch> --diagnostics <line-index>
--ratios <ratio-index> --run <fresh>` independently validates and displays saved
values. Ratio is an additional metric with raw/normalized/departure y and
numerator-signal/time x. All plots use the shared axis/cursor module. Open markers
remain second members; source selection shows both complete original ROI rows.
Saved diagnostic JSON also includes the stored ratio product. No division,
normalization or line fitting occurs in HTML.

## Processing stage and next scientific step

The existing measurements are bias-subtracted without overscan. The warning
stays visible. Owner requires subtraction in ALL bias and flat frames because
of the observed readout-side row ramp. Preserve row dependence and consistent
master-bias treatment; do not substitute one global value or double subtract.
The next image-measurement pass needs its exact estimator/edge rules reviewed
and both before/after evidence retained. A ratio trend can arise from additive
bias/overscan mismatch, changing illumination or differential response. A common
multiplicative shutter term cancels only under the stated linear/stable-pattern
assumptions; this diagnostic alone does not identify its physical cause.

## Validation and target status

Agent computation/storage8/8, viewer9/9 and qualifier-dispatch3/3 pass offline.
Coverage: analytical ratios, common-factor cancellation, exact identity/members,
null/nonpositive/reference absence, malformed populations, ASDF roundtrip and
relocation, source/conflict/frozen-link refusal, read without calculator, separate
CLI completion, and display with calculator/fitter disabled. Actual-script JS
checks pass for ratio modes, source precision, axis ticks and shared cursor hooks.
Browser painting is not claimed; Playwright checks supplied. Guide PDF rendered
and visually inspected (2pages; no overfull boxes).

`qualify_roi_ratio_mac.py` reuses actual prior b8dfd40 passed30checks/runtime and
unchanged modules; dispatch3 plus changed ratio8/viewer9 are the next Mac gate.
No dependency install/native rebuild/old matrix replay. Actual Mac gate,640-row
real ratio publication and independent HTML generation are pending. The actual
prior residual ASDF (ocam-residual-asdf-15000-35000-hwolegq7) is complete with
32products/160ROI summaries/3200rows and all5outerpreservation checks. Preserve
it and the prior qualified source/runtime. No physical model, merge or cleanup.
