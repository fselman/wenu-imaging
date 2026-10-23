# Future provisional photometry and explicit calibration methods

Fernando requested this future roadmap item on 23 October 2026 while reviewing
the transition from notebook 05 to SWarp. This is a design requirement for later
work, not authorization to implement a new calibration path during the current
functional walkthrough. Preserve the agreed notebook/Pycavi/mefpp sequence and
qualify any dependency changes separately.

## Current scientific path remains the baseline

Notebook 03 normalizes detector images by average gain/exposure time to e-/s.
Notebook 04 supplies initial astrometry. Notebook 05 measures sources with
SExtractor and refines astrometry with SCAMP; the PAPI default is
`SOLVE_PHOTOM=N`. Its SExtractor `MAG_ZEROPOINT=25` is a measurement convention,
not an observed photometric calibration. Notebook 06 resamples/coadds through
SWarp. Notebook 07 calls `ZPCalibration`, which measures reference-star apertures
using Photutils, estimates a zero point, converts mosaic pixels to
erg/s/cm^2/Angstrom and writes MAGZP/calibration metadata. The notebook currently
selects Gaia; NB_659 reference magnitudes use the existing r/i colour relation.
Notebooks 07b/c and 08 characterize residuals/illumination; notebook 09 uses the
Pycavi-calibrated MAGZP in SExtractor and applies selected catalogue corrections.
This source trace is not scientific validation of those later stages.

SWarp 2.38.0 explicitly replaces a zero input flux scale with 1.0 and warns
(`src/field.c`, check following `readfitsinfo_field`). That accommodates the
zero FLXSCALE cards emitted by the present astrometry-only SCAMP runs. Do not
enable SCAMP photometry, rewrite the headers or introduce new scaling to avoid
that warning. Confirm actual handling in the pending native SWarp run.

## Intended future capability

1. **Astromatic photometric processing.** Define which source measurements and
   relative photometric harmonization are performed by SExtractor/SCAMP, and
   which module supplies the provisional absolute scale and its later
   refinement. An Astromatic relative solution must not silently be described as
   an independently calibrated absolute zero point. Reuse the planned canonical
   source measurements; avoid a second independent extraction implementation.
2. **Instrument calibration module.** Estimate and version a provisional model
   for telescope/instrument, filter and focal-plane/detector identity. Specify
   the reference photometric system, input DN units, gain/exposure convention,
   spatial terms, validity interval and uncertainties. Distinguish persistent
   detector response from time-dependent throughput, atmospheric extinction and
   exposure-to-exposure transparency. Determine the model and required inputs
   during design rather than assuming one permanent zero point suffices.
3. **Provisional flux scale.** Convert the declared input units to a documented
   provisional scale, preserving a recoverable measurement baseline. Decide
   explicitly whether the scale is applied to pixels or carried as metadata/
   catalogue transformations. Track cumulative and incremental factors so gain,
   exposure normalization, flat/illumination response and photometric correction
   are each applied once. Never imply raw ADU, e-/s and calibrated physical flux
   are interchangeable DNs. Provisional products must be labelled provisional.
4. **Explicit refinement method.** Configuration and output provenance must
   identify the method and reference release, not merely `Gaia`. Required
   choices include Gaia DR2, Gaia DR3 (with its actual photometry product, such
   as GSPC synthetic photometry), standard-star calibration, and explicitly
   defined other methods. These are alternatives to qualify, not claims of
   interchangeable bandpasses or currently implemented selectors. Record the
   reference catalogue/version, magnitude system, transformations, standard-star
   observations where relevant, selections, aperture/model choices, extinction
   treatment and calibration input identifiers. Gaia DR2 does not imply the
   existence of the DR3 GSPC synthetic bands. Keep astrometric and photometric
   reference selections separate; Gaia DR2 astrometry with DR3 photometric
   refinement can be an explicit configuration rather than a contradiction.
5. **Refinement and QC.** Retain provisional and refined solutions, their
   relationship, uncertainties and residuals by exposure/filter/detector.
   Define validity, minimum reference coverage, failure/fallback and acceptance
   criteria before production adoption. Do not silently replace a failed method
   with another catalogue. Test spatial, magnitude and colour residuals and
   provisional-to-refined consistency on broadband and narrow-band cases.

## Implementation boundary and acceptance

Place reusable calibration logic in the appropriate shared Pycavi library
module, with thin notebook/configuration-driven callers. Define the exact module
boundary after the existing workflow has been exercised and audited. If native
mefpp headers later carry the instrument model, implement that only in its
authorized stage. Retain the present Pycavi calibration path as a comparison
baseline until the new path has been explicitly accepted.

Acceptance must cover named methods/releases, units and cumulative factors,
idempotent application, provenance, detector-name mapping, validity/fallback,
held-out/reference comparisons and unchanged astrometric/pixel handling where
no photometric change is intended. Scientific tolerances and the implementation
order remain to be agreed. No new photometric algorithm, native engine upgrade
or calibration switch was implemented by recording this plan.

Sources inspected: the repository notebooks 03 through 09,
`pycavi_associate_reduction.mefpp_normalize_science`, PAPI SCAMP/SWarp defaults,
`pycavi_astromatic_tools`, `pycavi_zpcal.ZPCalibration` and catalogue correction
functions. Native compatibility reference:
[SWarp 2.38.0 field.c](https://github.com/astromatic/swarp/blob/2.38.0/src/field.c).
