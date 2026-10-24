# Saved Kriging reader and QC bindings (#41/#42)

During the 24 October 2026 chapman3 walkthrough, both 08b fits, finite grid/QC
checks and exact FITS serialization passed in `notebook08b-kriging-4_ssz0f9`.
The subsequent reader check found #41: interpolation axes used
`linspace(0,NAXIS,NAXIS)`, while physical pixels were scaled onto 0..NAXIS-1.
Thus querying the stored grid's own sample coordinates did not recover its values.

The corrected reader uses physical axes from 1 to ORIG_W/ORIG_H, inclusive,
with sample counts from the actual stored NAXIS1/NAXIS2. It retains linear
RegularGridInterpolator, its default rejection outside those physical axes,
(y,x) data orientation and the five-item return interface. Returned mesh axes
now also follow actual stored dimensions, including rectangular grids.
No FITS grids, fitted variogram parameters or science data are changed.

Notebook 08c also passes corrected residuals in coordinate positions in its two
QC plotting calls (#42). Explicit keyword bindings correct those calls without
changing residual definitions, selection or fitting. Loop scope (#37) and the
08a experimental nonlinearity cell (#38) remain separate unresolved issues.

## Evidence before correction

An agent execution of the actual reader body with mocked FITS I/O, a 5x5 grid
and non-square 301x151 physical extent reproduced a 0.12 mag sample error for
z=0.001*x+0.002*y. Real-file fixtures are used in the regression tests below.

Chapman3 actual saved grid nodes confirmed:

| Filter | Maximum absolute reader error (mag) | RMS reader error (mag) |
| --- | --- | --- |
| r_SDSS | 0.2660547882330937 | 0.008861636419445162 |
| NB_659 | 0.11493764664251095 | 0.010644478529680819 |

The r_SDSS worst sample at (4887.673469387755,15297.163265306122) stores
-0.32810569860761546 but returns -0.06205091037452178. NB_659 at
(8269.408163265305,16910.714285714286) stores 0.13144962055105242 but returns
0.016511973908541467. Original FITS grids exactly matched 08b saved arrays;
source models and arrays retained their hashes. This defect affects values,
not merely display. No image or catalogue correction has been applied.

## Acceptance

Five focused regressions execute the actual source/installed reader body with
real temporary FITS files, excluding unrelated fitting imports. They verify all
sample nodes/endpoints, rectangular stored grids and physical extents, analytic
affine interior and scalar results, out-of-image rejection, and exact input bytes.
The actual two notebook calls are executed against the real library signatures
with bodies replaced by bound-argument capture; distinct residual and coordinate
arrays catch silent argument swaps. These are functional mapping/binding tests,
not Kriging scientific fitting validation.

Chapman3 must verify both existing saved grids without refitting, test the corrected
08c plotting path and preserve source hashes. Record correction/verification in
each ticket before closing #41/#42. Linear interpolation between a coarse saved
grid and the continuous Kriging predictor is a separate approximation question;
correct grid-node recovery does not establish independent model accuracy.


Agent validation: five focused regressions passed from source. An isolated
wheel installation passed the same five tests against its reader/notebook and
ten installed-package/resource checks (15 total). Records:
`/tmp/wenu-kriging-readback-check-uo_din5m`. The test environment used Python 3.12,
NumPy 1.26.4, Astropy 6.1.7 and SciPy 1.17.0. Kriging fitting imports/plot bodies
are not exercised by these isolated tests; chapman3 fitting/import qualification
was performed separately. Notebook JSON/code syntax, local links and whitespace
checks passed. No chapman dependency or observational product was changed.
Target corrected reader/plot checks remain pending; #41/#42 stay open.
