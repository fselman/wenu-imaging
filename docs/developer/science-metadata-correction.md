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
actual extraction/assembly paths with native solver execution mocked. Native
science coaddition and installed-wheel acceptance on chapman3 are still pending.
Keep #25 open until that evidence is recorded. Preserve the diagnostic coadd at
`~/omegacam/testing/wenu-imaging-test/notebook06-r_SDSS-B128-20pm51ir`.


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
