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

## Chapman3 acceptance, 24 October 2026

Installed commit `a57ec108a3c15540a7f74b9aa726d0c3d88d5f7c` passed five source
and five installed regressions, ten installed-package/resource checks and pip
check in `~/wenu-catalogue-integers-jbpixqeh`. Catalogue, Gaia helper, zpcal and
Kriging module bytes match source. A normal full production import/crossmatch
also preserved the synthetic ID and missing mask. Wheel SHA256
`16d5d8cbab5abd785fd07c056c2066b1264f5eca8612997cd462d41096e42c1f`.

The fresh notebook 09 functional runner completed exit code 0 in
`~/omegacam/testing/wenu-imaging-test/notebook09-catalogue-95xc1kyz`:

| Check | Result |
|---|---|
| r_SDSS extraction | 17682 rows |
| NB_659 extraction | 17937 rows |
| Paired-filter rows after existing cleaning | 16459 |
| Gaia reference rows | 6245 |
| Rows with Gaia IDs/positions | 3718 |
| Distinct assigned Gaia IDs | 3718 |
| Exact int64 IDs, reference-position agreement and FITS masks | Pass |
| SOURCE_ID_gaia FITS format | K |
| Original/staged image and reference hashes | Unchanged |

`CN_Ori_merged_catalogue.fits` SHA256:
`bb2cd9b91969470ea5d917ec0489c02beff0dc8f3db4dd0b9205d315c41b2171`.
Native extraction catalogue SHA256s: r_SDSS
`66a16c2357f1f6dd8e3da5a298f82b19da1df44a8ac95b9e0465820b3bcd58c1`;
NB_659 `0b050c902e0880fca316f56de962d8039c103ffba55a059a38b487a3e88364a5`.
The saved runner calls the installed Pycavi extraction/matching/cleaning libraries
with existing notebook settings (including error scaling), single native thread
and niceness 10. The second/last filter's recovered raw Gaia cache supplies the
reference, matching the notebook's current selection order. The diagnostic runner
does not execute the complete notebook discovery/selection orchestration.

#46 was closed after its correction/evidence comment. PR #47 is unmerged and
stacked on #45/#43. No new reference query, calibration, model fit or illumination
correction occurred. Counts are functional row/match accounting, not completeness
or independent science/Phase 3 validation. Preserve this baseline for subsequent
correction on fresh copies. The separate catalogue Kriging application has a
confirmed edge/grid-coordinate failure (#48); it is not the corrected #41 reader.
