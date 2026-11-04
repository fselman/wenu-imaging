# ASDF comments qualification and signal/time display — 4 November 2026

## Actual Mac receipt

Source `1a422b99fe7e2a722a0875700054de7bb58161c8` passed on the owner's Intel Mac:
13 shared checks in 2.308 s, 9 pair checks in 17.066 s, and 5 sample checks in
6.637 s. Retained run:
`/Users/fselman/Software/build/wenu-imaging/mac-asdf-comments-moofbx58`.
Qualification passed; all five preservation checks true: checkout,
installed_files, exported_source, private_qc_runtime and prior_qualification.
This qualifies new descriptive ASDF headers; old archives remain untouched.
No repeated header qualification is needed without a relevant change.

## Display extension

Existing pair ASDF stores both exposure means and times. The new display-only
projection exposes each member with its original input index, asset/HDU, ROI,
exposure time, signal, common-pair population, original table row index and all
original pair fields. It sorts the inspection table by original acquisition
index and ROI. Signal/time curves sort by exposure time with original input index
as the tie-breaker. Neither operation changes measurements or averages members.

`plot-pair-qc.py` now adds `signal_vs_exposure_time.png` and exact series/source
values in `plots.json`, alongside the two existing plots. `view-pair-qc.py` adds
Signal vs exposure time to the offline mosaic, with both members, detector/ROI
selection, full-value inspection and a derived `qc-data.json` for all panels.
Second members have open markers in the viewer. The ASDF records remain the
measurement authority; JSON/PNG/HTML are derived inspection products.

Signals are raw-pair bias-subtracted ROI means without overscan correction, on
the pair-common accepted pixel population. They are not the separately archived
corrected individual pixels. Nulls remain unavailable and stay in inspection
rows. No signal range, noise model, weighting, fit or shutter estimate is added.

## Agent validation and pending Mac gate

Nine pair-ASDF/plot checks passed (6.872 s); eight viewer/projection checks passed
(8.233 s). They use synthetic transports/ASDF with network and FITS access forbidden.
They check exact member signals/times/identities, acquisition ordering distinct
from time ordering, nulls, signed zero/negative signals, unchanged source rows,
geometry, broken references and three static plots.

Dependency-free execution of the real viewer JavaScript passed metric switching,
ROI filtering, member/source selection and missing/null/negative states. This
checks JavaScript/SVG generation using a minimal DOM, not browser rendering.
Chromium launch failed because this environment forbids its socket creation;
no browser interaction/layout success is claimed. The expanded Playwright test
is retained for an environment that permits Chromium.

`qualify_signal_time_mac.py` prepares the focused 9+8 metadata/display check on
the Mac, reusing the now-qualified common writer and private ASDF runtime. Actual
Mac acceptance of the display extension and real-data viewer generation remain
pending. After that, generate a fresh viewer from the existing all32 pair-ASDF
batch, preserve all source archives and show the owner all 3,200 exposure/ROI
entries, together with pair variance/gain data. Do not rerun pixel extraction.

No modelling until the owner inspects the complete data and instructs that it
begin. No merge, installation or cleanup. Refs #227, #235, #236.
