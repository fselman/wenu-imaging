# Catalogue execution repair, 21 October 2026

Fernando authorized this stage after the read-only notebook 09 audit in
[issue 5](https://github.com/fselman/wenu-imaging/issues/5).
Baseline: `bf31205de8e8df01ee5187cf007f4205478811e8` (merged Chebyshev repair).

## Repairs

- Stack coordinate arrays consistently before taking their arithmetic mean.
  One filter now works; two filters retain their prior averaging behavior;
  three or more filters no longer transpose the accumulation incorrectly.
  This retains the existing arithmetic RA/Dec convention; spherical averaging
  and wrap-around handling are not introduced here.
- Check stored `ILLCORnn` values case-insensitively instead of comparing the
  keyword name to the band. This shared guard covers Chebyshev and Kriging.
- Record each applied model's basename in `ILFILEnn` and its SHA-256 digest in
  `ILHASHnn`, alongside the existing `ILLCORnn` band. Short FITS keyword names
  accommodate a complete 64-character digest. These are processing provenance,
  not a claim of ESO-standard metadata compliance.
- Skip an already-corrected band without writing. If its recorded digest differs
  from the selected model, raise an error requiring an uncorrected baseline.
  Legacy band markers without a digest also prevent reapplication; their model
  identity cannot be recovered or certified. Do not use them to validate a new
  model.
- Create the SExtractor working directory without referencing an undefined
  target name or suppressing real directory errors. Fix target catalogue path
  construction in `prepare_to_sextract` so its skip/redo checks use the actual
  `.cat` filename. This helper is shared; real external extraction remains a
  separate native validation step.
- Use independent enumerated object/filter indices. Correct catalogue timestamp
  formatting to include minutes. Default to preserving an existing merged
  baseline unless `redo_catalogue=True` is explicitly selected.
- Require one explicitly selected model path per target/filter in notebook 09.
  Candidate discovery is informational, never automatic selection or sequential
  application of every matching model file. External model locations, including
  the pilot verification directory, are supported.
- Apply correction to a separate `*_merged_catalogue_chebyshev.fits` (or
  `*_merged_catalogue_krigging.fits`) copy. Record baseline digest/name as
  `INPSHA`/`INPFILE`; reject reuse if the baseline has changed. Subsequent notebook
  validation/plots use the explicitly produced corrected catalogue list.

The public correction functions still operate in place on the supplied path;
the notebook supplies the separate copy. Direct callers must likewise pass a
disposable copy if they need to preserve their baseline. Do not run two writers
on the same catalogue concurrently; locking is not added by this patch.

## Scientific boundaries

The CSV/model residual convention is `reference magnitude - measured magnitude`.
The existing catalogue correction is therefore `measured magnitude + model`.
Tests verify this sign. Image pixels are not modified. Flux columns, magnitude
uncertainties, reference columns, detection thresholds, extraction zero point,
gain and existing error scaling remain unchanged. A magnitude-only corrected
catalogue must not be presented as having correspondingly corrected flux columns.

The source uses `MAGZP` from the calibrated image. This repair does not establish
that `GAIN=1` and subsequent uncertainty scaling are scientifically adequate for
physically scaled coadd pixels, or that aperture-fit residuals transfer without
bias to SExtractor AUTO/PETRO magnitudes. Those need scientific validation with
the pilot data before a final catalogue is accepted.

## Validation

Run from the repository root in the wenu-imaging Python environment:

```bash
python -m unittest discover -s Pycavi2/tests -v
```

Ten offline regressions pass on the Linux development host: the four existing
Chebyshev tests plus six catalogue tests. Disposable FITS files exercise:

- Single-, two- and three-filter coordinate combination, row filtering and
  preservation of the existing uncertainty scaling.
- Known-model correction sign, untouched flux/reference/error columns, saved
  model identity, byte-identical repeat skip and changed-model rejection.
- Legacy mixed-case correction markers and the shared Kriging repeat guard.
  A constant square Kriging map tests this guard; it does not validate arbitrary
  Kriging grid geometry or interpolation accuracy.
- Correct catalogue skip/redo paths.
- Execution of the actual notebook creation and correction cells using real
  Astropy tables/FITS and catalogue functions. Only the external extraction
  stage is mocked. A fresh namespace creates the working directory; selection
  of a second target works; baselines remain byte-identical; absent model choices
  and changed baselines are rejected.

Notebook code cells parse and `git diff --check` passes. Development-host checks
do not certify full macOS execution, real SExtractor output, scientific quality
or Phase 3 compatibility. Re-run these tests on the Mac after merge, then run
notebook 09 against an isolated copy of the pilot calibration working directory.

## Verified Mac Chebyshev products feeding this stage

Fernando's regenerated 08a products contain 36 coefficients and both six-term
bases. Re-fitting the uploaded CSV with the notebook's 12–18 magnitude selection
selects 2350 stars, rank 36. Maximum coefficient difference between the refit and
Mac export is `3.64e-17`; maximum model difference at calibration-star positions
is `1.25e-16` mag. Explicit evaluation also agrees with NumPy's independent
Chebyshev evaluator to `1.25e-16` mag over a 61-by-59 grid including corners.
Mac clipped scatter is 0.0325 mag before versus 0.0162 mag after, with corrected
mean -0.0051 mag. This follows the earlier withheld-star validation, but uses a
different magnitude selection and is not an independent absolute calibration.

## Remaining audit work

No changes here to crossmatch uniqueness, string/integer reference columns,
Gaia source-ID precision, arithmetic RA wrap-around, catalogue completeness,
proper-motion epochs, flux/error consistency, sentinel magnitudes, coadd noise,
external service availability, or hardcoded instrument metadata. Kriging geometry
and notebook 08b/08c are separate work. Existing outputs are not regenerated,
corrected, released or submitted by this code change.
