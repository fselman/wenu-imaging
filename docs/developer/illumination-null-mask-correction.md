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

Chapman3 installation and fresh corrected-catalogue checks are pending. Keep #49
open until target IDs/null counts, every unrelated column/header and baseline/model
hashes survive correction with expected numerical changes and repeat guards.
Use the already verified Chebyshev files for functional testing on a fresh copy;
no recalibration/refit or scientific model acceptance follows. Preserve the
baseline catalogue and images. PRs #43/#45/#47 remain unmerged prerequisites.
