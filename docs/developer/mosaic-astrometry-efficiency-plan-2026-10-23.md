# Mosaic astrometry and catalogue reuse: planned efficiency work

Fernando requested this roadmap addition on 23 October 2026 during the existing
notebook walkthrough. This records intended future work, not an implementation
or a validated instrument-stability claim. The walkthrough continues unchanged;
do not interrupt or alter the running nine-exposure solve. Implementations belong
to the agreed Pycavi and subsequent mefpp stages, with their existing approval
boundaries. No SExtractor settings, native code, image headers or calibration
policy have been changed by this plan.

## 1. A single SExtractor measurement pass and catalogue reuse

The requirement is to remove repeated SExtractor work from the workflow and
reuse its measurements. Inventory the calls in notebooks 05, 07 and 09 and their
library paths, including measurement columns, detection/deblending thresholds,
apertures, flags, saturation/gain assumptions, images and model dependencies.
Define one canonical extraction with the union of required measurements;
select appropriate subsets for astrometry, photometry and later catalogues.

The extraction unit must be explicit: one run per distinct image/pixel product,
not one detector catalogue shared by unrelated exposures. Exposure images and
SWarp coadds contain different pixels and noise; using the same measurement table
for both needs a scientifically defined alternative, not silent reuse. Record
any genuinely separate coadd detection/measurement requirement before agreeing
the implementation. The current notebook-05 threshold of 10 and notebook-09
threshold of 5 cannot simply be assumed equivalent; test a unified extraction
and downstream selections against the present outputs.

Key reuse by image/pixel identity, detector identity, extraction configuration,
engine version, required columns and relevant calibration inputs. An existing
filename is not sufficient. Header-only WCS refinement should update/derive sky
coordinates from retained detector coordinates and carry photometric calibration
as metadata/derived columns where valid, without rerunning pixel measurement.
Invalidate reuse when pixels or measurement-relevant inputs change. Examine
Astrometry.net's existing source-list input support so sparse solving can reuse
the same detections rather than introduce another independent detection pass.

## 2. A reusable per-filter focal-plane baseline

Use well-constrained image sets to establish the detector geometry and distortion
baseline for each instrument/filter and applicable configuration. Treat stability
as a hypothesis to measure over nights, pointing, rotator/configuration changes
and other recorded conditions. Specify validity intervals, model version, source
data and acceptance residuals. Keep per-detector placement, rotation, scale and
distortion; a common RA/Dec shift alone is not a full focal-plane model.

Propagate the accepted baseline back to the mefpp header-writing stage, so its
science products already contain the appropriate initial WCS, adjusted for each
exposure's pointing. Trace existing mefpp WCS/configuration capabilities first.
Map detectors by validated chip identity (e.g. EXTNAME), never by an unchecked MEF
ordinal. This depends on the separately recorded native detector-identity audit.
Document WCS convention and distortion compatibility across mefpp, Astropy,
Astrometry.net, SCAMP and SWarp, along with baseline provenance in headers.
Prevent stale baseline selection and double application of pointing corrections.
WCS header insertion must preserve science pixels, units and normalization.

## 3. Solve only 1, 2 or 3 detectors for exposure pointing

Once a baseline is validated, choose a small subset of usable detectors for
`solve-field`, estimate the exposure offset, and propagate the correction to the
full focal plane. Compare one-, two- and three-detector strategies, considering
source density, sky coverage, saturation/crowding, detector separation and failed
chips. Test whether a pointing-only correction suffices; measure rotation, scale
or distortion changes rather than absorbing them into a spurious translation.

Retain SCAMP refinement and validation as appropriate. Define confidence tests
and explicit fallback to more detectors/full solving when the baseline or sparse
offset estimate fails. Quietly reusing a bad offset is not an optimization.
No fixed detector choice, translation-only policy or acceptance tolerance has
been approved yet. Benchmark wall time and actual SExtractor/solver invocation
counts, as well as residuals, against the current full-detector baseline.

Both methods need astrometric reference information, in different forms.
Astrometry.net uses its indexed star patterns; the sparse-detector plan retains
the existing local index installation for those initial solves. SCAMP matches
source catalogues using an approximate input WCS and a reference star catalogue,
retrieved through VizieR or supplied as a local FILE catalogue. It does not use
Astrometry.net's index files. A static focal-plane baseline does not remove the
need to anchor the exposure pointing to the sky. Availability, release/epoch and
provenance of the reference catalogue and indexes remain explicit requirements.

Fernando reports the current SCAMP setup needs initial positions within roughly
1–2 arcsec, motivating the initial Astrometry.net solve. Record and reproduce
that setup-specific observation. SCAMP supports pattern matching of coordinate
shifts, rotation and scale; do not describe 1–2 arcsec as a universal SCAMP limit.
Trace MATCH, POSITION_MAXERR, CROSSID_RADIUS, input WCS and selected mosaic model
before attributing the observed limitation to the program itself.

## 4. Review SCAMP mosaic geometry and SWarp settings separately

The recalled focal-plane option is **SCAMP** `MOSAIC_TYPE=FIX_FOCALPLANE`;
it is present in the PAPI wrapper and selected by notebook 05. It is not a SWarp
projection/resampling parameter. Compare the installed SCAMP version's relevant
modes (`FIX_FOCALPLANE`, `UNCHANGED`, `SAME_CRVAL`, `SHARE_PROJAXIS`, `LOOSE`) and
their actual effects on an externally established baseline. Parameter names alone
do not prove that geometry/distortion coefficients remain fixed. Establish which
parts of the model SCAMP may change and how a reference image set is reused.

| SWarp setting group | Existing source baseline / decision to review |
|---|---|
| Output coordinates/projection | Notebook 06 uses `CELESTIAL_TYPE=NATIVE`, `PROJECTION_TYPE=TAN`. Validate the intended common sky frame and WCS convention. |
| Output grid | Wrapper defaults `CENTER_TYPE=ALL`, `PIXELSCALE_TYPE=MEDIAN`, automatic size. Decide explicit shared centre, pixel scale, orientation and size where aligned multi-filter products are required. |
| Resampling | Wrapper `RESAMPLING_TYPE=LANCZOS3`, notebook `PROJECTION_ERR=0.001`. Compare PSF, astrometry, flux conservation, correlated noise and runtime before selecting changes. |
| Flux and weights | Trace `FSCALASTRO_TYPE` (wrapper `FIXED`), `FSCALE_KEYWORD`, gain/exposure conventions, `FLXSCALE`, weight interpretation, invalid pixels and saturation. Prevent duplicate scale/zero-point application. |
| Background/combination | Notebook uses median combination and background settings, with two output branches. Verify the actual effective parameters and scientific purpose rather than infer behavior from output filenames. |

No SWarp parameter set is universally established by stable detector geometry.
The output grid and photometric/noise conventions are separate choices from
the instrument focal-plane calibration. Preserve present settings while they
are evaluated; changing them requires the usual scientific equivalence review.

## 5. QC against the baseline carried in mefpp headers

Provide a QC script through the same shared library used by notebooks. Compare
each derived solution with the selected baseline plus its estimated pointing
correction. Separate whole-exposure offset/rotation/scale from chip-specific and
spatially structured residuals. Compare sky mappings over a detector grid and
matched sources; differences in raw WCS coefficients alone are not a sufficient
metric when projections or reference points differ.

Report detector identity, filter, baseline ID/validity, source counts, spatial
coverage, robust residual/bias statistics, residual maps, rejected matches,
missing/failed detectors and unconstrained modes. Compare to independent
reference/held-out data where possible so QC does not merely reproduce its own
fitted baseline. Track trends and flag coherent geometry changes. Agree warning,
failure and fallback thresholds with Fernando from measured residuals and the
science requirements, not arbitrary defaults. This is astrometric baseline QC;
the separately deferred general calibration-product QC library is unchanged.

## Acceptance and implementation boundary

- Preserve the current full-detector solution path as the comparison/fallback.
- Verify catalogue reuse under header-only changes, changed pixels/settings,
  missing columns and interrupted runs; do not silently rerun or reuse stale data.
- Verify baseline provenance, filter/configuration selection and detector-name
  matching, including permuted/missing/duplicate extensions.
- Compare sparse solutions with full-detector and independent reference results
  across representative fields/conditions; include failures and outliers.
- Show reduced extraction/solver counts and runtime without degrading the agreed
  astrometric/photometric performance. Functional finite-WCS checks alone cannot
  demonstrate this equivalence.
- Implement native header propagation during the authorized mefpp stage; this
  roadmap request does not authorize modifying the installed native binary now.

Source anchors: current notebooks 05/06/07/09, `pycavi_astromatic_tools.py`,
`pycavi_zpcal.py`, `papi_scamp.py`, `papi_swarp.py`, and the later native WCS audit.
Primary references:
[SCAMP usage/header interfaces](https://scamp.readthedocs.io/en/latest/Using.html),
[SCAMP matching capabilities](https://scamp.readthedocs.io/en/latest/Introduction.html),
[SCAMP 2.10.0 parameters](https://github.com/astromatic/scamp/blob/2.10.0/src/preflist.h),
and [SWarp](https://www.astromatic.net/software/swarp/).
