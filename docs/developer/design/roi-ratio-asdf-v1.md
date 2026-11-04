# Same-exposure ROI ratio, final design v1

4 November2026. Owner approved plotting the previously proposed near-readout /
parallel-far ratio. Compute/save in ASDF separately; plotting remains read-only.
Owner also requires overscan subtraction in all input exposures, motivated by
observed row transients near readout. The current raw-pair archive is explicitly
bias-subtracted without overscan correction. This ratio diagnoses that archive;
it is not relabelled as corrected. A separate consistent overscan-corrected
ROI measurement pass (biases and flats, with existing approved scan estimator)
is the next reduction prerequisite before interpreting a physical correction.
No images are reread or old products replaced in this ratio increment.

For each detector match near_readout and parallel_far by original input index,
asset, HDU, pair ID and member. Require identical exposure time. Never match
only on time or average the two members. Require one row per ROI/exposure and
fail on mismatched/duplicate identities. Retain missing/nonpositive values as
unavailable; a valid ratio requires finite positive signals in both ROIs.

For each matched exposure j, R_j=S_near,j/S_far,j. Use an explicit constant
normalization R_ref equal to the unweighted arithmetic mean of valid individual
R_j for which BOTH signals are within15000..35000ADU, inclusive. Save selected
identities/count and reference value. If no reference exists, retain raw R_j,
mark normalized values unavailable. Save R_j/R_ref and100*(R_j/R_ref-1), both
signals, exact sources/coordinates/pair membership and availability reasons.
This is the mean of individual ratios, not the ratio of averaged signals.
Uncertainties remain unavailable; shared-normalization covariance is not ignored
by inventing error bars or weights. No fit or shutter coefficient is computed.

Read the completed immutable residual-ASDF index, reuse its stored original rows
without recomputing line fits. Write NEW ratio-ASDF products and a completion
index through the unchanged common QC lifecycle, with local frozen copies of
the source graph. Record producer revision, units, stage, method and limits.
A new computation command supports the complete32-detector source; output must
be fresh. Expected20matched exposures per detector,640ratios overall.

The HTML accepts a separate completed ratio index, verifies product/source digests
and identities, and plots saved normalized ratio (default), raw ratio or departure
percent against numerator signal or exposure time. One ratio curve per detector;
other views/ROI selection stay intact. Reuse the shared axes/cursor component.
Show normalization count/interval and uncorrected-stage warning. No division,
normalization or statistics calculation in the browser. Display all matched rows.

Validate analytic constant/spatial-ratio cases, exact member matching, invalid
signals/missing reference, immutable inputs, ASDF roundtrip/relocation/source
mismatch/no-overwrite, and reader/display with numerical computation disabled.
Update LaTeX/PDF guide after implementation. Mac gate and actual ratio-ASDF run
precede real ratio HTML. No physical model, archive rewrite, install or merge.
