# Corrected ASDF diagnostics and independent viewing

5 November 2026. Refs #235/#236; draft PR #227.

The completed `ocam-corrected-roi-batch-NrHHb3bT` archive remains the measurement
authority: 32 products, including the reused CCD65 pilot. The new bridge selects
its stored individual corrected ROI means and spatial variances without reopening
images, original native tables, or repeating preparation. It freezes the existing
source ASDF graph and validates detector, stage, digest and exposure identities.

The previously approved unweighted free-intercept line and same-exposure
near_readout/parallel_far ratio algorithms are unchanged. Actual computation will
use the inclusive 15000–35000 ADU interval: individual signals for line membership,
both numerator and denominator for the arithmetic ratio reference. Neither
spatial variance nor pair noise is assigned as uncertainty in a mean. Noise and
covariance remain unavailable; no physical correction or calibration is fitted.

`tools/compute-pair-residuals.py` now accepts `--preparation-asdf` and
`--preparation-batch`. Its saved line ASDF is consumed by the existing separate
`tools/compute-roi-ratios.py`. Only afterwards does `tools/view-pair-qc.py
--preparation-batch` render those saved diagnostics. Readers and plotting do not
refit lines or compute ratios. Mixed raw/corrected measurement mosaics are refused.
Corrected signal/time, count rate and spatial variance are labelled with their
actual stage; retained raw-pair gain and raw bias RON keep explicit raw labels.
Shared signal axes and cursor behavior are reused unchanged.

The residual extension records `source_kind=preparation`, the actual corrected
measurement stage and `source_measurement_digest`. The old `source_pair_digest`
key is a compatibility alias to the measurement source digest. Existing raw-pair
archives remain readable and immutable.

## Validation and next Mac step

Agent validation passed 32 Python controls: 9 residual, 8 ratio, 9 legacy viewer
and 6 corrected integration checks. Analytical corrected signals deliberately
differ from retained raw diagnostic signals. Tests verify known slope/intercept,
residuals, ratios, exact saved values, relocated reading with original support
images/native tables removed, stage tampering and mixed-stage rejection, and
viewing with fitting/ratio computation disabled. Both actual viewer JavaScript
suites pass, including corrected metric sources, labels and shared axes. Browser
painting could not be checked because Chromium socket creation was restricted.

Both mathematical guides have updated LaTeX and matching compiled PDFs. The
unchanged common ASDF, preparation reader, numerical functions, TOML resolver and
shared axes were compared against the qualified d25b106 source.

Actual Mac qualification of this changed integration remains pending through
`Pycavi2/tests/qualify_corrected_diagnostics_mac.py`: 32 Python controls and four
preservation guards, reusing the retained ASDF6 runtime and prior native gate.
Only synthetic support images are used by the new integration fixture. No native
build/execution, dependency installation or observation access is needed.

After that gate, compute new saved diagnostics from the existing all32 index and
then render separately for owner inspection. No actual corrected diagnostic or
viewer run is claimed yet. Do not replay admission, raw image hashing, bias
construction, preparation or earlier qualification. No installation, merge or
cleanup is authorized.
