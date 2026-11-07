# Offline pair-QC mosaic candidate — 4 November 2026

Issue#235, draft PR227. All32 real detectors are now available: actual Mac serial
batch `ocam-raw-pairs-serial-nx_j6g1j/batch` completed31 additional detectors,
reusing CCD65. All native/ASDF/plot stages completed; source_preservation true,
exactly two shared hash passes per image, error null. Outer checkout/install/
export/private-runtime/reference protections all true. #234 is target-complete.
Keep existing native/ASDF evidence and qualified builds/private runtime intact.

`tools/view-pair-qc.py` reads completed batch/publication receipts and validated
shared ASDF products/reference trees only. It uses maintained detector-footprint
TOML loading, mosaic column/row placement, FITS Y inversion and footprint SVG.
It refuses unknown/duplicate identities, differing native slots/output/ROI bounds,
broken frozen references, incomplete batches and altered shared verification.
The generic builder explicitly displays omitted detector records as missing;
real completed-OCAM CLI generation requires all32. No raw FITS or native TSV file
is opened. Full native text already embedded in ASDF remains frozen provenance;
no estimator is recalculated. Source fingerprints cover ASDF/profile/template and
small batch evidence. The generator writes a new derived inspection directory;
viewer.json establishes completion and HTML fingerprint. ASDF stays authoritative.

The self-contained HTML provides variance/gain selection in all mosaic tiles,
common comparison axes, detector buttons/selector, enlarged selected-detector
plot, ROI toggles, full-precision point inspection, availability/exclusion counts,
raw bias-pair RON, footprint/ROI coordinates and source/settings/provenance details.
Tables round for legibility and expose full values through hover/selection.
Unavailable values remain null, visibly distinguished from zero. Signal coverage
comes from saved means; no graph extends to the digital threshold by assumption.
No fit, accepted gain, masking/rejection action, reduction or scientific policy.
No CDN/network requirement. Embedded JSON escapes '<'; untrusted labels use HTML
escaping or textContent. Browser numbers retain binary64 precision.

Seven agent offline ASDF/geometry controls pass in8.661s, with raw FITS access
forbidden. They cover full-precision rows, exact mosaic identities, missing/null
states, profile/slot mismatch, duplicate/unknown detector, broken leaves, changed
inputs, escaping and failed-batch refusal. JavaScript syntax passes Node checking.
Playwright interaction controls are supplied in tools/tests/test_pair_qc_browser.cjs;
agent Chromium launch is blocked by environment socket() permission, so browser
interaction/rendering is NOT claimed passed. Actual browser visual/interaction
inspection remains required on the Mac after generation. Do not install browser
or Node dependencies into the imaging environment just to run those controls.

`Pycavi2/tests/qualify_pair_viewer_mac.py` performs the seven new metadata controls
in retained private ASDF6 runtime. It reuses the passed shared/pair ASDF gate only
after exact unchanged-module/package-version admission and protects checkout,
installation, source export and private runtime. No numerical tests/native rebuild,
observations or dependency installation. Actual Mac viewer gate is pending; then
generate real offline HTML from the retained batch in a fresh Pictures directory,
protecting reference/batch ASDF evidence, and open the saved HTML for inspection.
Keep #235 open until actual viewer is inspected. No merge/install/cleanup.
