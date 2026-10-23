# Science metadata boundary correction (#25)

This bounded fix addresses the current chapman3 walkthrough, then must be
retested on Mac. Native mefpp is unchanged. Issues #23/#24 track its separate
calibration-timestamp and binary32 MJD-END defects and remain open.

`pycavi.pycavi.pycavi_metadata` provides the shared header logic. Science primary
MJD-OBS and EXPTIME are authoritative; MJD-END is recomputed using Astropy
Time/TimeDelta in double precision (including UTC leap seconds). Only UTC is
currently accepted; the existing ESO workflow defaults absent TIMESYS to UTC.
No pixel normalization, gain assignment or photometric calibration is performed.

New detector extraction and WCS assembly overlay exposure-level dates, duration,
units, saturation, normalization provenance and object/filter metadata from the
science primary. Detector identity, geometry, WCS and detector gain remain intact.
Existing cached detector files are not silently rewritten or re-solved.

For already assembled solved MEFs, call the installed library in a batch:

```python
from pycavi.pycavi.pycavi_metadata import copy_science_metadata
copy_science_metadata(existing_solved_mef, fresh_destination)
```

This copies the FITS storage before editing headers, preserves BSCALE/BZERO,
recomputes checksums, and refuses an existing destination (including symlinks).
It neither calls solve-field nor reruns SExtractor/SCAMP. Continue using the
already checked native SCAMP .head files; preserve them byte for byte. A
header-only correction does not establish new astrometric accuracy.

SWarp's input list is validated before the native coadd. Postprocessing uses
all input science primaries, with common object/filter/units/origin and distinct
resolved paths required. MJD-OBS/DATE-OBS come from the earliest contributing
exposure; MJD-END is the latest recomputed endpoint. TEXPTIME sums the exposure
durations once per input MEF, not once per detector; NCOMBINE counts MEFs.
The same observation metadata is written to the weight map, without assigning
science BUNIT to weights. Native EXPTIME and GAIN are retained. SWarp describes
EXPTIME as its maximum equivalent exposure; this is not a uniform per-pixel
exposure or an independently validated noise model. See its [user guide,
section 6.9.4](https://raw.githubusercontent.com/astromatic/swarp/legacy_doc/prevdoc/swarp.pdf)
and [2.38.0 output-header implementation](https://github.com/astromatic/swarp/blob/2.38.0/src/header.c).
The earlier coadd's EXPTIME=0 and default-derived gain must not be repaired by
blindly assigning TEXPTIME or a guessed gain. Regenerate a fresh functional
coadd from corrected detector headers with the same scientific settings.

Validation: ten metadata regressions pass from source and from a built wheel
installed outside the checkout. Six existing SExtractor regressions and ten
installed-package checks also pass in the agent Linux/Python 3.12 environment
with Astropy 6.1.7 and NumPy 1.26.4. Synthetic multi-detector fixtures exercise double-precision timing,
unchanged pixels/WCS/detector gain, unsigned FITS storage, checksums, source
preservation, no-overwrite/invalid-input behavior, all-input coadd metadata, and
actual extraction/assembly paths with native solver execution mocked.

Chapman3 installed-wheel and real-product acceptance subsequently passed, as
reported by Fernando. Issue #25 was closed with the correction and verification
comments; PR #32 is still unmerged. Native causes #23/#24 and Mac retesting
remain pending. Preserve the diagnostic coadd at
`~/omegacam/testing/wenu-imaging-test/notebook06-r_SDSS-B128-20pm51ir`.


## Chapman3 acceptance evidence

Code commit: `03a59c55a9be13952c93bf77d2e889f6cca01385`.
Installed verification records: `~/wenu-metadata-check-4j5cdwy1`.
Wheel SHA256: `b390017ff4ca27d01af583ae5941cba8395168b2135dd01ff03037671a92b04f`.
All ten metadata and six SExtractor regressions passed against the source and
installed wheel; ten installed-package checks and pip check passed. Three
installed runtime modules were verified against the source snapshot.

All ten corrected MEFs passed 32-detector pixel-byte, WCS/non-exposure-header,
FITS checksum, source-hash and copied-SCAMP-header preservation checks. No
normalization, solve-field or source extraction was repeated.

| Filter | BACK_SIZE | Records below `~/omegacam/testing/wenu-imaging-test/` | EXPTIME / TEXPTIME (s) |
| --- | --- | --- | --- |
| r_SDSS | 128 | `notebook06-r_SDSS-metadata-_bzh232q` | 400 / 400 |
| NB_659 | 128 | `notebook06-NB_659-metadata-rbp1f48a` | 2400 / 2400 |
| r_SDSS | 2048 | `notebook06-B2048-zslaummd/r_SDSS` | 400 / 400 |
| NB_659 | 2048 | `notebook06-B2048-zslaummd/NB_659` | 2400 / 2400 |

Each directory contains its start record, native/runner logs and
`output-check.json`. The second-pass root contains `completed.json`.
All four coadds passed finite nonempty science data, finite nonnegative weights,
finite sampled celestial WCS, input-hash preservation and science timing checks.
They retain `BUNIT=e-/s`, `NCOMBINE=5` and native equivalent EXPTIME/GAIN.
Both passes used MEDIAN and SUBTRACT_BACK=Y, sequentially at niceness 10 with
one native thread. The second pass's historical `coadd_nobacksub` name remains
misleading (#31); its separately isolated weight map preserves the first pass.

r_SDSS timing: DATE-OBS `2017-03-11T02:14:43.393`, MJD-OBS
`57823.093557795`, MJD-END `57823.100269381925`.
NB_659 timing: DATE-OBS `2017-03-11T01:30:31.026`, MJD-OBS
`57823.062859104`, MJD-END `57823.09271171356`.

First-pass coadd / weight SHA256:

- r_SDSS: `0631d84ccdfba04ee317da57080a397e6be57bedf40758b7c44496525d504b72` /
  `674545b4733103eae16c3fb4f02ec10fde1b40d13f964a1a0b719c0b3952ec22`.
- NB_659: `923725e110614b9702996e17a88b33d3497cb94e73b9b198bfe8db4c3f4a0fae` /
  `2ac2de5d41b1bb0eebfae1fa01a73cf0044193410d2fe782d7bf7d2f1b2a48c2`.

These are reported functional checks, not independent astrometric accuracy,
photometric calibration, a validated gain/noise model or Phase 3 acceptance.
Continue to notebook 07 using its existing Gaia DR3/GSPC Pycavi calibration path;
SCAMP photometry remains disabled. The normal notebook 07 selector takes
`*.coadd.fits`, not the second pass's `*.coadd_nobacksub.fits`.


## Chapman storage context supplied by Fernando

Fernando supplied an older internal Chapman Guide during this work. It describes
chapman3/4 as AMD EPYC 7742 machines with 64 cores/128 threads and 512 GB RAM,
shared home directories exposed through /home symlinks into /home1, /home2 or
/home3, and a distinction between Gluster and newer hardware storage. It warns
that Gluster handles many small files and recursive operations slowly. These
are historical reported details, not a fresh filesystem inventory or an I/O
benchmark. Do not infer that the active home mount is Gluster from this guide.

Shared homes mean separate hostnames do not establish separate output ownership:
never run jobs on different Chapman machines against the same working outputs.
Preserve the chapman3 guard and current niceness/thread limits. No migration,
parallel launch, cleanup, storage mount change or job-directory change is
performed by this metadata correction. Any later I/O optimization must first
identify actual mounts and measure representative operations.
