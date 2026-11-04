# Separate residual computation, ASDF storage and plotting

4 November 2026. Owner instruction supersedes browser-side arithmetic in v1.
The approved model is unchanged: ordinary unweighted free-intercept line per ROI,
all available individual exposures by default, explicit optional signal limits.
No physical shutter or amplifier correction is fitted or applied.

## Real-data state

Interim residual HTML at `/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-residual-viewer-fes7vt_w`
completed with all five preservation guards true. Retain it. Corrected qualifier
sourcef2a15c7 passed2runner checks (0.031s) and8viewer checks (12.199s), all four
guards; retained mac-residual-viewer-tmpq60uq. Earlier failed mac-residual-viewer-9xkac0fq
is history, not a data failure. No actual new diagnostic ASDF run is claimed yet.

## Completed implementation

- `pycavi_residuals.py`: pure centered OLS with math.fsum; no file I/O or plotting.
- `pycavi_residual_qc.py`: unchanged common QC lifecycle; an actual derived TSV and
  its ASDF sidecar per detector. The owned line_residual_diagnostic extension
  stores configuration, ROI coefficients/centers/validity, every original sample,
  prediction, residual ADU/percent, count rate, membership flags and units.
  Frozen local original pair QC graphs accompany new sidecars; original archives
  and source images are not changed. Records/digests round-trip exactly.
- `compute-pair-residuals.py`: separate offline computation command, single pair
  ASDF or completed batch; explicit limits, exact producer revision, fresh output.
  A completed index identifies detector products and freezes their record digests.
  No image access, plotting or HTML creation. Failures stay retained/incomplete.
- `view-pair-qc.py --diagnostics INDEX`: independent plotting, validating saved
  diagnostic identities, source links, config and record digests. It never calls
  the fitter. The HTML has no computational module: switches change presentation
  only. Fit limits are read-only saved settings; changing them needs new ASDF.
  Without diagnostics, original measurement views remain and missing curves are
  explicit. JSON export is a copy of saved results, not a computation.
- `pycavi_pair_products.py`: shared unchanged batch-metadata admission extracted
  from the viewer so computational code does not import plotting code.

## Verification and pending target work

Nine computation/storage tests and nine viewer tests passed in the agent environment.
They include analytical solutions, null/signed/negative/zero/rank cases, restricted
reference intervals retaining outside points, independent ROIs/large time origins,
exact round-trip/relocation, frozen links, wrong source/digest refusal, command
completion without plots and refusal to overwrite. Disabled fitter checks prove
read/render cannot recompute. Actual embedded JS checks use a deliberately supplied
saved residual value verbatim, preserve source identity, and expose no fit-range
change handler. Network and FITS access are forbidden in the Python controls.
An initial order-dependent configuration digest failed round-trip; corrected to
canonical sorted UTF-8 JSON before hashing, without changing common QC code.

Mac `qualify_residual_asdf_mac.py` prepares the affected9+9 checks, reusing the
passed private runtime/common QC and preserving checkout/install/source/runtime.
Then run one real32-detector computation: expected32diagnostic products,
160ROI fit summaries and3200sample/curve rows. Generation of HTML from those saved
ASDF diagnostics follows independently. No new measurement/extraction or existing
archive rewrite is needed. Do not repeat prior native/header/pair gates.

Final design: [v2](design/linearity-residual-asdf-v2.md). Mathematical implementation
explanation: [LaTeX](linearity-residual-asdf-guide-v2.tex) and matching compiled
[PDF](linearity-residual-asdf-guide-v2.pdf). v1 is retained as historical.
No merge, installation, cleanup or physical model choice. Refs #227/#235/#236.
