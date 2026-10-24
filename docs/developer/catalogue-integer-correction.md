# Notebook 09 crossmatch integer precision

24 October 2026, [#46](https://github.com/fselman/wenu-imaging/issues/46).
After #44 restored exact Gaia identifiers, preflight of the next production
call found a second conversion: `crossmatch_catalogues` allocated float64 arrays
for every column from the shorter catalogue. Actual-function-body reproduction
changed int64 ID `3022567708255397889` to `3022567708255397888`. This confirms a
production mechanism for the floating catalogue-ID risk noted in broader Phase 3
issue #9; no observational catalogue was created during this reproduction.

Integer columns now retain their original dtype and use a masked value for
unmatched rows. Existing source masks, column units/description/metadata survive.
Floating columns keep float64 arrays with NaN for unmatched rows. The longer
catalogue remains the output anchor, including current ties and order. Matching
still uses the same nearest-neighbour routine, default one-arcsecond threshold,
strict less-than comparison and current allowance of repeated associations. This
is not a matching-uniqueness or scientific-policy change.

Notebook 09 imports and uses `read_gaia_csv` for the existing raw query cache,
so empty/invalid/rounded textual IDs fail before matching. It does not query Gaia,
choose an illumination model, change SExtractor settings or recalibrate an image.
Existing recovered caches and science products remain untouched.

Five focused regressions passed from source and from an isolated installed wheel;
ten installed-package/resource checks passed. Agent evidence:
`/tmp/wenu-catalogue-integer-check-lntd5ihz`. Tests execute the actual crossmatch
function body with real Astropy coordinates/tables/FITS, excluding unrelated
module imports. They cover both input orders, longer-table integer IDs, exact
large shorter-table IDs, existing/new masks, signed/unsigned dtypes, matching
inside/outside the same radius, unchanged float/coordinate results and inputs,
column metadata and FITS missing-value/ID round trips. Notebook AST checks verify
the actual cache-reader call/import; installed notebook/module bytes match source.
No native extraction, live query or observational matching occurred in these tests.

Keep #46 open pending chapman3 installed checks and exact IDs in the fresh actual
notebook 09 catalogue. Use the already verified recovered Gaia files, staged
coadd copies and existing Pycavi libraries. Retain original hashes and catalogue
row/match accounting; no independent photometric/astrometric or Phase 3 claim
follows from functional construction. PRs #43/#45 are unmerged prerequisites.
