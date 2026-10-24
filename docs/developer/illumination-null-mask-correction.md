# Preserve FITS null metadata during catalogue illumination correction

24 October 2026, [#49](https://github.com/fselman/wenu-imaging/issues/49).
The verified notebook 09 baseline contains 16459 rows, 3718 exact Gaia IDs and
12741 missing Gaia IDs. Before launching any observational correction, a real
synthetic FITS check found that both correction writers discarded integer-null
metadata. They converted `hdul[1].data` (a FITS_rec exposing stored placeholders)
to an Astropy Table, then replaced the whole HDU array. TNULL=999999 disappeared;
a masked ID became an unmasked value 999999. This is distinct from #46's float
coercion and #44's missing query IDs. The actual baseline remains unchanged.

Both writers now modify only existing magnitude field arrays in place. Integer
fields, TNULL/TFORM/TUNIT and the table structure remain intact. Existing numerical
predictions, correction sign, selected magnitude columns, native float rounding,
model digests and repeat guards are unchanged. No coordinates, reference IDs,
other data columns or scientific methods are modified. The independent Kriging
application grid/bounds defect #48 remains open; the writer correction does not
make that interpolation path accepted.

Five focused source and five isolated installed-wheel regressions passed, plus
ten installed-package/resource checks. Agent records:
`/tmp/wenu-illumination-null-check-fi8gtrii`. Tests execute the actual writer,
loading and provenance-helper bodies with real temporary FITS files; only model
parsing/prediction is mocked deterministically. They verify both writers, signed
64-bit masked IDs, other masked integer fields, unchanged complete extension
headers and unrelated column bytes, expected float32/float64 magnitude changes,
two sequential filter updates, repeat-call byte identity, changed-model rejection,
original-copy preservation and an unrelated image HDU. Installed source bytes
match the tested module. These tests do not establish model/interpolation accuracy
or execute the complete production import/native/science workflow.

## Chapman3 acceptance, 24 October 2026

Installed commit `f391cb9784a27d5f7a146c46fc367a33bb24439d` passed five source
and five installed actual-writer/helper regressions, ten package/resource checks,
pip check, installed-byte comparisons and a normal production module import.
Records: `~/wenu-illumination-nulls-as6bl9ya`; wheel SHA256
`acbd313cd06db24d0a8cb2a0f00e3371ce9e56375b279b0c99f0c6d42cf041fc`.

Actual application of the two previously verified Chebyshev models passed in
`~/omegacam/testing/wenu-imaging-test/notebook09-chebyshev-6xb3rgu1`.
The fresh `CN_Ori_merged_catalogue_chebyshev.fits` SHA256 is
`b11b932dea2a3be6dc43fb1cbf16e9a75e33d5840b16ef1c5326e8d99a4782fa`.
Local `started.json` and `output-check.json` record inputs, models and checks:

- All 16459 rows, 3718 exact signed-64-bit Gaia IDs and 12741 missing-ID masks
  survive. Every unrelated column's bytes/masks and complete extension header
  (including TFORM/TNULL) are unchanged.
- `mag_auto`, `mag_best`, `mag_iso` and `mag_petro` for each filter equal the
  existing prediction added at the original stored dtype. r_SDSS corrections
  range -0.06993422013034695..0.12204147436745853 mag; NB_659 corrections range
  -0.06566804102931004..0.08266183760929577 mag.
- Per-filter model basename/hash and baseline INPSHA/INPFILE provenance pass;
  each repeated application returns 0 with a byte-identical catalogue.
- Baseline and saved-model hashes remain unchanged. No extraction, new query,
  image correction, calibration or refit occurred.

#49 closed after its correction/evidence comment. PR #50 remains unmerged and
stacked on #47/#45/#43. Tests of both writer bodies plus actual Chebyshev output
accept the writer repair; observational Kriging interpolation is not accepted
and #48 remains open. Numerical/scientific accuracy and the existing magnitude-
only versus unchanged flux/error convention remain separate #8/#9 questions.
Next: functional catalogue QC on isolated baseline/corrected copies, with existing
plot settings and no model refitting or new reference query.
