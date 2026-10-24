# CN Ori paired-filter pilot proposal

Status: Fernando approved the four historical numerical values on 22 October
2026 and authorized proceeding with input/BPM provenance checks. PAF
application, input staging and links are now verified on chapman3; the first
native bias run and exact historical pixel comparison pass. The latest evidence below supersedes earlier
pending-check notes retained as implementation history.
Fernando requires NB_659 and an associated r_SDSS set because the narrow-band
photometric calibration has particular behavior. This proposal concerns
instrumental preprocessing first; photometric validation must treat each filter
separately and is not established by successful engine execution.

## Candidate inputs

### NB_659 sky and combined-flat functional results

The NB_659 sky and combined master flat were produced at niceness 10; both
contain all 32 named detectors and finite pixels. The sky flat reproduces the
historical pixels exactly. The combined flat differs in 15,604 pixels across
18 detectors, the same detectors with changed BPM pixels. The largest absolute
difference is 0.08831357955932617 on ESO_CCD_#90; do not dismiss local differences
based on their small fraction of the mosaic.

A read-only spatial check used the actual staged kernel half-size 4 (9x9 square
support) and the project BPM versus historical split masks. Every changed MFF
pixel is inside the corresponding changed-mask influence footprint; zero lie
outside it. Together with exact bias, dome and sky reproduction and the native
BPM-aware smoothing code, this strongly supports the changed BPM as the cause.
It is not a controlled rerun with identical BPM input or independent scientific
quality certification. No production image-processing algorithm was changed.
The records are `sky-mff-comparison.json` and `mff-bpm-footprint.json` in the
staged NB_659 sky partition. The functional pilot may proceed with this recorded
input difference; scientific mask/calibration validation remains deferred.

### Functional-test threshold override authorized

Chapman3 follow-up: the failed 45,000 attempt is preserved at
`calib/dome/574184/r_SDSS/2017-03-14T09:41:34/failed-45000-20261022T143505694348Z/`.
The local PAF was changed to 55,000 with minimum accepted count still five;
`functional-override.json` records the new PAF hash and purpose. The rerun
confirmed niceness 10 and produced a complete MEF dome flat with all 32 named
detector images and finite pixels. There is no historical r_SDSS dome reference.
This is a functional pass, not a calibration-quality certification. The override
does not change sky-flat thresholds or the baseline project PAF hash.

Fernando clarified that this stage is functional testing and authorized raising
the dome upper frame threshold to 55,000 for the failed r_SDSS dome test.
Keep the production minimum of five accepted frames; lowering it to three
would not remedy the observed zero accepted frames. Do not select additional
adjacent-night dome inputs now. Apply this as a recorded local override in the
r_SDSS dome partition's PAF, preserving the failed 45,000 attempt and leaving
the canonical/native configuration and the NB_659 historical comparison intact.
The original project manifest PAF hash describes the initial baseline; the new
attempt must record its own PAF hash and explicit override.

At the 45,000 threshold, the r_SDSS run wrote only 25 image extensions (26 HDUs)
through ESO_CCD_#85. At extension 26, the logged frame-rejection statistics for
all five inputs were 45,056.1 to 45,063.5, above the upper limit; native errors
reported zero accepted frames and aborted dome production. The Python wrapper
misreported success because it ignored the process exit code and searched only
case-sensitive `Error` text in the log. That separate runner defect remains
unfixed. Preserve logs, partial master, command, provenance, list and PAF before
rerunning. Raising this frame-selection threshold does not establish pixel
linearity or calibration quality; do not claim historical equivalence for the
new functional attempt.

### Completed bias and NB_659 dome checks

All three selected bias masters have been produced. March 9 and March 11 match
historical pixels exactly over all 32 detectors; the March 14 bias passes named
detector and finite-pixel checks but has no historical master for comparison.
All three candidate bias products are 1,070,729,280 bytes. The NB_659 dome master
is 1,070,732,160 bytes and also matches historical pixels exactly across all 32
detectors, with zero mean/RMS/maximum differences and finite pixels. Units are
unspecified in both versions of the compared products. The dome run confirmed
Python niceness 10. These results do not certify calibration quality.

The first native run produced
`calib/bias/574184/2017-03-11T09:21:33/OCAM_MB_1x1.fits` (1,070,729,280 bytes).
Comparison with the historical `OMEGACAM_MB_1x1.fits` found 33 HDUs in each,
identical detector-name ordering and dimensions, finite pixels throughout all
32 detector arrays, zero differing pixels and zero maximum/RMS differences.
Both products lack primary and detector BUNIT cards: zero unit-header
differences means shared missing metadata, not established physical units.
The result is historical reproducibility evidence, not independent scientific
quality certification. The saved comparison is `bias-comparison.json` in the
new bias partition. Later dome results are recorded in the milestone above;
no sky or science reduction is established yet.

Latest chapman3 preparation evidence: all 60 distinct inputs total 32.22 GiB;
detector EXTNAME ordering matches the installed MEF BPM across all 60 inputs.
The preserved dependency inventory is
`/home/fselman/wenu-pilot-manifest.p0y2ven1/manifest.json`.
All nine lists and approved PAFs are staged in the isolated project, with a
project `pilot-manifest.json`. All nine BPM links and ten calibration links are
verified. The copied project BPM matches the installed source, passes the
legacy-aware preflight, and the installed source checksum is unchanged.
The workspace PAF backup is `omegacam.paf.backup-20261022-095059-005728`.

Fernando agreed to the first bounded run: the ten-input shared science bias
partition dated 2017-03-11T09:21:33, followed by detector/shape/units/finite-pixel
checks and initially exact numerical pixel comparison. He clarified that the
old master is merely a product of previous reductions, not independently
validated truth. Treat it as a historical reproducibility comparison. Investigate
differences before continuing dependent reductions; equality does not establish
scientific quality. A calibration-product QC library is deferred until the
currently planned wenu-imaging work is complete (see roadmap).

Historical root: `/home/fselman/omegacam/testing/reduced/`.
The paths below are relative to that root; their existing lists define the
candidate inputs. Never regenerate their associations by silently picking
different dates. Preserve raw files, old products and old configuration.

| Role | Partition | Listed frames |
|---|---|---:|
| Science, NB_659 | science/CN_Ori_055207p790_m052500p5/NB_659/2017-03-11T01:24:08 | 5 |
| Science, r_SDSS | science/CN_Ori_055207p790_m052500p5/r_SDSS/2017-03-11T01:24:08 | 5 |
| Shared science bias | calibs/bias/574184/2017-03-11T09:21:33 | 10 |
| NB_659 flat bias | calibs/bias/574184/2017-03-09T09:40:35 | 10 |
| r_SDSS flat bias | calibs/bias/574184/2017-03-14T09:41:34 | 10 |
| Dome, NB_659 | calibs/dome/574184/NB_659/2017-03-09T09:40:35 | 5 |
| Dome, r_SDSS | calibs/dome/574184/r_SDSS/2017-03-14T09:41:34 | 5 |
| Sky, NB_659 | calibs/sky/200253598/NB_659/2017-03-08T23:14:31 | 5 |
| Sky, r_SDSS | calibs/sky/200253584/r_SDSS/2017-03-13T23:12:13 | 5 |

This totals 60 list entries across nine partitions when the shared science
bias list is counted once. The follow-up inventory verifies path uniqueness and primary-header
filter/type/binning/exposure metadata. Total size and image-payload integrity
have not yet been checked.
The three r_SDSS flat-calibration lists (20 entries) have all inputs present.
Follow-up on chapman3 confirmed all 60 listed inputs are distinct and their
primary headers are readable, with expected frame types/filters and 1x1 binning.
All five NB_659 science exposures are 480 seconds and all five r_SDSS science
exposures are 80 seconds. This does not certify image payloads or associations.
All five r_SDSS science exposures are 80 seconds and all five NB_659 science
exposures are 480 seconds; the three bias sets have zero exposure time.

## Available comparison products

The NB_659 tree has five `_pre.fits` files plus linked existing bias, dome,
sky and combined-flat products. Their identity, normalization stage, BPM
provenance and scientific trust still require characterization. Existing
primary sample headers lack BUNIT, while current Python normalization writes
e-/s. Compare the same processing stage and never normalize the old products
in place. The short historical mefpp logs show startup, not completion evidence.

The associated r_SDSS sky/master-flat, dome and flat-calibration bias products
are absent despite the input lists being present. Rebuild them in the new
project rather than repair or write into the historical tree. They cannot be
used as historical product references. Do not imply numerical equivalence for
r_SDSS without a suitable independent reference or agreed validation method.

## Concrete PAF proposal

`omegacam-historical-numerics.proposed.paf` is a review copy of the current
packaged OmegaCAM PAF with exactly these four value substitutions:

| Key | Current | Proposed |
|---|---:|---:|
| MEF.DOMEFF.FRAMETHR.HI | 55000 | 45000 |
| MEF.SKYFF.FRAMETHR.HI | 55000 | 45000 |
| MEF.SKYFF.FRAMETHR.LO | 7000 | 10000 |
| MEF.KERN.HSIZE | 7 | 4 |

Those values match Fernando's historical science-PAF comparison. All other
current settings, OCAM product naming and header mappings remain byte-for-byte
unchanged. This controls the identified numerical parameter differences; it
does not recreate the old mefpp binary, prove matching BPMs, validate every PAF
field, or establish complete scientific equivalence. In particular, existing
curly-quote metadata values are retained for review, not silently repaired.
The canonical packaged PAF and installed native configuration are unchanged.

## BPM comparison evidence

Fernando confirmed that MEF BPM support was intentional. The installed
`OCAM_BPM_1x1.fits` contains an empty primary HDU and 32 uint8 image extensions;
the historical directory contains 32 primary-image files of the same dimensions
(2044 by 4091 pixels). In the candidate pairing of historical file number with
installed extension number, 14 pairs match exactly and 18 differ. There are
1,428 changed pixels in total: 1,391 in extension 14 (`ESO_CCD_#90`) and 37
across the other changed pairs. Both versions contain only zero and one values.
Historical detector identifiers are absent in the inspected headers; the near
identity supports the candidate order. Raw/MEF extension-name ordering has since
been checked for all ten selected science exposures, as recorded below. The cause of the content changes is unknown; do not describe these as
merely repackaging, silently revert the MEF mask, or modify either source mask.

Read-only source tracing confirms native MEF loading through `pixelmap_loadext`
in `mefpp2/ins/mef/recipes/mefpp.c`. Pycavi copies the MEF static mask but its
reduction preflight still globs per-detector `OCAM_BPM_??.fits` names and accepts
an empty match set. This is an identified preflight defect, not a proposed
reversion to split masks. The focused correction described below is implemented locally; chapman3
installation and verification are pending. The installed native binary's source
identity remains unverified.

Further chapman3 checks confirmed exact extension-name ordering between the MEF
BPM and all ten selected raw science exposures. Extension 14 has 1,390 changes
from zero to one and one from one to zero, within FITS coordinates x=753..1063,
y=12..3400; the first ten reported changes lie at x=1063, y=12..21. This suggests
a column-related difference but does not establish its full geometry or cause.
Repository `pixelmap_loadext` treats zero as bad and nonzero as good, so these
changes alter pixel acceptance. They must not be dismissed on global fraction
alone or attributed to the Python environment.

An additional read-only finding in `link_bpm`: creation of the destination link
is guarded by the source mask *not* existing, so a source mask that already
exists can leave a missing destination uncreated. A focused proposal is to
correct MEF link creation and replace legacy split-file preflight with explicit
MEF presence/layout checks and failure-path tests. Fernando approved this focused correction; implementation and validation are
recorded below. Native engines and mask pixels are preserved.

## Execution boundaries and next approval

The baseline PAF choice is approved for the separate test workspace. Before
executing a pilot, complete the input/BPM/configuration
manifest, establish stage-specific reference comparisons and numerical
tolerances with Fernando, and confirm the test project has no conflicting
outputs. These are outstanding prerequisites, not a claim that the pilot is
ready to run. Use existing library functions and the existing serial mefpp;
do not create an alternate scientific implementation.

The intended dependency order is the three bias partitions, then the two dome
partitions, then the two sky/combined-flat partitions, then the two science
partitions. Capture pre-normalization products for like-stage comparison before
calling the existing Python normalization once on fresh outputs. BPM handling
and its provenance must be resolved explicitly; this proposal does not replace
the requirement to integrate normal BPM construction, nor authorize a new BPM
algorithm. Astrometry/coaddition/photometry follow their own verified inputs.

This draft does not authorize the larger notebook/script refactor, a native
software upgrade, bulk reduction or Phase 3 submission.


## Focused Python correction and local verification

`pycavi_associate_reduction.py` now creates missing MEF links regardless of
whether the source has already been staged, preserves correct existing links,
and rejects conflicting destination files/links. Correct staging links may
remain dangling until the static mask is copied. Each of the four reduction
runners calls a shared MEF preflight that rejects missing/broken targets,
unreadable FITS files, a nonempty primary HDU, incorrect extension counts,
non-image/non-2D/non-integer extensions, missing/duplicate EXTNAME values and
missing configured active chip names. The check reads headers, not pixel arrays;
it does not certify pixel quality or reorder extensions. No notebook or native
source changes are included.

Local Python 3.12 validation with NumPy 1.26.4 and Astropy 6.1.7: eight new BPM
tests and ten existing scientific regressions pass. The two key regressions
reproduce the old link-creation and false-success defects against the previous
module. A fresh wheel passes ten installed-package checks outside the checkout;
all eight BPM tests also pass against the wheel-installed module. Native calls
are mocked in runner tests; this is not evidence of successful real reduction.
Chapman3 subsequently installed commit 3f5c102 and passed all ten packaging
checks and eighteen source regressions. Its actual installed MEF failed the
new strict FITS verification because PCOUNT/GCOUNT are absent in all 32 image
extensions; these cards were not inspected in the earlier header inventory.
The previous successful pixel reads do not establish full FITS conformance.

The follow-up preflight retains strict verification but supplies missing
PCOUNT=0/GCOUNT=1 in read-only, in-memory image headers only and logs an explicit
legacy warning after verification succeeds. It rejects explicitly nonstandard
group values and other structural errors. It never writes those defaults or
changes pixels in the source file. Regression fixtures directly remove cards
from FITS header bytes (both blanked slots and compact headers), reproducing the
real failure rather than relying only on standards-compliant Astropy output.
Tests compare file bytes before/after, require the warning and confirm that
other FITS errors still fail. Native header assembly is recorded as a separate
mefpp audit TODO, not repaired here. Revalidation of the actual chapman3 MEF
with this follow-up remains pending.

Follow-up local validation: all 21 source regressions pass (11 BPM plus 10
existing scientific tests). A clean rebuilt wheel passes 10 installed-package
checks and all 11 BPM tests against its installed module outside the checkout.
These use local Python 3.12/Astropy 6.1.7 and disposable masks; they do not
substitute for the pending chapman3 actual-mask check.

Reference: [Astropy FITS verification](https://docs.astropy.org/en/stable/io/fits/usage/verification.html)
distinguishes permissive input reading from explicit strict verification.

The mefpp detector-identity TODO in `roadmap.md` explicitly requires tracing
name versus ordinal matching across raw/calibration/BPM/output paths, with
permuted-extension regression cases. Its native implementation remains deferred.

## Notebook 04 walkthrough, 23 October 2026

After Fernando instructed continuing through the notebook sequence and deferring
lunar/site-data to zpcal, the installed `pycavi_solve.run_py4_solve()` was exercised
on a fresh independent copy of the first normalized r_SDSS exposure,
`OMEGA.2017-03-11T02:14:43.394_pre.fits`, with one worker at niceness 10 and local
Astrometry.net 0.98. The wrapper called the existing library; no new solving or
assembly implementation was substituted and no installed code was changed.

Fernando reported successful solution markers for all 32 detectors and an
assembled 33-HDU MEF with matching detector names, unchanged pixel shapes/dtypes
and exact detector pixel equality. Sampled celestial WCS coordinates were finite;
primary BUNIT/ONEADU/EXPTIME were preserved, and the original and copied inputs
retained their hashes. This is functional orchestration/assembly evidence, not
real-sky astrometric accuracy or a systematic scientific audit. Only one worker
was exercised; it does not qualify multiworker failure propagation.

Records: `~/omegacam/testing/wenu-imaging-test/notebook04-r_SDSS-t4f5cu78/`
(`runner.log`, `started.json`, `completed.json`). The assembled MEF is beneath
`OMEGA.2017-03-11T02:14:43.394_pre/`, named
`OMEGA.2017-03-11T02:14:43.394_pre_wcs.fits`. Installed solving module SHA256:
`f0a9a17ec84dae4b4e5e9635e2b76ed336ecc7044d50e6a6314e3065f5a447c8`.
Follow-up reported by Fernando: all remaining four r_SDSS and five NB_659
exposures passed the same complete runner/assembly checks, sequentially with
one worker at niceness 10. Records:
`~/omegacam/testing/wenu-imaging-test/notebook04-remaining-s2t7bhf8/`, with the
root `completed.json` linking the nine per-exposure records and the first run.
All ten pilot exposures now have checked assembled MEFs: 320 successful detector
solves in this runner/assembly walkthrough, with exact pixel preservation,
preserved selected primary headers, finite sampled celestial WCS coordinates
and unchanged source/copy hashes. No broad astrometric-accuracy or multiworker
validation follows from these checks. Earlier 32-detector diagnostic solves for
each filter remain separate evidence and are preserved. Continue at notebook
05 using these assembled outputs; do not repeat solving or normalization.

## Notebook 05 reported functional results, 23 October 2026

All ten exposures (five r_SDSS, five NB_659) passed installed SExtractor/SCAMP
functional output checks, sequentially at niceness 10 with NTHREADS=1. Each has
32 LDAC detector groups with required columns and nonzero total detections,
32 finite sampled celestial WCS solutions, a parseable SCAMP XML report and
eight PDFs with valid framing/EOF markers. Images/catalogue inputs were checked
unchanged across the relevant stages. No independent astrometric accuracy,
photometric calibration or rendered-plot acceptance is established here.

Evidence under `~/omegacam/testing/wenu-imaging-test/`:

- First r_SDSS extraction: `notebook05-r_SDSS-j7p7xgf_`.
- First r_SDSS accepted output checks: `notebook05-r_SDSS-scamp-i3mbyoln/scamp-output-check.json`.
- First NB_659 output checks: `notebook05-NB_659-p_o9_0eg/scamp-output-check.json`.
- Remaining eight and combined ten-exposure summary:
  `notebook05-remaining-umptm20a/completed.json`.

The native fit statistics were about 0.0158/0.0159 arcsec for the first r_SDSS
exposure and 0.0127/0.0177 arcsec for the first NB_659 exposure. These are SCAMP
fit residuals, not independent accuracy assessments. Native .head blocks contain
TAN plus 20 PV cards per detector and no SIP cards; input image headers contain
TAN without SIP/PV. Astropy's compatibility warning is retained; its generic SIP
removal wording does not demonstrate SIP cards were actually present. Native
headers were not rewritten by the diagnostic WCS checks.

Focused PAPI integration fixes (banner recognition and explicit NTHREADS via
ext_config) are delivered separately on `fix/sextractor-banner` at
`1927166644606567b374a23ff5437b248b9b7029`. Chapman3 verification records are
`~/wenu-sextractor-fix.19w6fdss` and `~/wenu-sextractor-threads.zug6x2b4`:
six regression tests, ten installed-package tests, pip check and installed-source
identity/native discovery passed. Failed attempts are preserved, not reused.

The first SCAMP attempt aborted during plotting because only plplot-libs was
installed and `/usr/share/plplot5.10.0` was absent. The matching
`plplot-5.10.0-10.el7.x86_64.rpm` was fetched from Fedora's EPEL archive; package
identity and payload digests passed, SHA256
`647b33589603895b9c4ef98d8421cbeeff95098ffa87764af2c04d2ac0a9feed`.
Twenty-one flat plotting data files were extracted to
`~/opt/plplot-data-5.10.0`; evidence and per-file hashes:
`~/wenu-plplot-data.pflmnt42/local-data-manifest.json`. PLPLOT_LIB was scoped to
batch processes. No RPM was installed and system packages were unchanged.
The original aborted output remains under `notebook05-r_SDSS-j7p7xgf_`.
PAPI failed to propagate that native abort; retain this as an unresolved
library-audit issue rather than claiming its failure handling is validated.

Notebook 06 preflight found five inputs per filter, e-/s units, and FLXSCALE=0
in all 320 SCAMP blocks. SCAMP photometric solving is disabled by design;
SWarp 2.38.0 source replaces zero flux scale with unity and warns. At this preflight the native
coadd was pending; the notebook 06 completion record below supersedes that status. Preserve the existing Pycavi zpcal method and defer the
[new provisional photometry plan](../../provisional-photometry-plan-2026-10-23.md)
to future work.

## Notebook 06 functional completion, 23 October 2026

Fernando reported passing coadd checks for r_SDSS and NB_659 using the installed
Pycavi metadata correction (`03a59c55a9be13952c93bf77d2e889f6cca01385`, PR #32).
Both existing notebook passes (BACK_SIZE 128 and 2048) ran sequentially at
niceness 10 with one native thread, MEDIAN and SUBTRACT_BACK=Y. Each used five
corrected 32-detector MEFs with exact pixel/WCS and original-input preservation.
All four coadds passed finite/nonempty science data, nonnegative weights,
sampled celestial WCS, input hashes and timing. r_SDSS records 400 s and NB_659
2400 s in both EXPTIME and TEXPTIME, with NCOMBINE=5 and BUNIT=e-/s.

Records under the pilot project:

- `notebook06-r_SDSS-metadata-_bzh232q` (first pass).
- `notebook06-NB_659-metadata-rbp1f48a` (first pass).
- `notebook06-B2048-zslaummd` (second pass, per-filter records and completed.json).

The [metadata correction notes](../../science-metadata-correction.md) record
installation, timing and first-pass hashes. Issue #25 is closed with correction
and verification comments; native #23/#24 remain open. The historical second
filename says nobacksub despite enabled subtraction (#31 remains open).
Preserve all diagnostic/coadd products and their separate weight maps.
No photometric calibration, independent science accuracy or Mac acceptance is
claimed. Next is notebook 07 preflight; do not repeat earlier processing.


## Notebook 07 first r_SDSS calibration, 23 October 2026

The installed ZPCalibration constructor completed in
`notebook07-r_SDSS-tft0e40n`, with the notebook's Gaia DR3/GSPC parameters.
After a disconnected terminal, runner-returned.json and the final log confirmed
completion and no remaining calibration process. The verification did not rerun
calibration: finite pixels, recorded scale (relative discrepancy <8e-8), sampled
unchanged WCS/timing, 981 catalogue rows/584 usable calibrators and unchanged
source/parent inputs passed. The five exposures total 400 s; legacy calibrated
EXPTIME is 80 s, TEXPTIME 400 s, NCOMBINE 5. This is not independent photometric
accuracy or Phase 3 acceptance. Preserve all results and query files.

A saturation unit mismatch was found despite the successful pixel checks:
SATLEVEL was restored in original e-/s after conversion to physical units.
Issue #33 tracks the focused correction and native SATURATE conversion; see
[the correction notes](../../zpcal-saturation-correction.md). The original
calibration must be reused through a fresh header-only repair, not rerun.


## Notebook 07 acceptance and next-session handoff

Both filters passed the existing installed ZPCalibration path, with the notebook
parameters preserved: magnitude range 10.5--18.5, aperture 5 arcsec, sky annulus
6--9 arcsec, Gaia query radius 0.7 and query magnitude parameters 8--20. These
are functional checks, not independent photometric accuracy or saturation science.

r_SDSS original completed calibration/query records remain in
`notebook07-r_SDSS-tft0e40n`. The unit-only repair is a fresh copy in
`notebook07-r_SDSS-saturation-gnwwuqtu/CN_Ori_r_SDSS.coadd.fits`, with
`output-check.json` alongside it. All pixel bytes and unrelated header cards,
including WCS/timing, are unchanged; FITS checksums passed and originals remain
unchanged. DN2FLAM is 2.10315823839273e-19; corrected SATLEVEL is
3.7003687528143e-16 and SATURATE is 3.6496271310164e-16 in erg/s/cm**2/A.
MAGSATL=17.206 is the existing pixel diagnostic, not a validated point-source
limit (#35/#36). There were 981 catalogue rows and 584 usable calibrators.
Corrected image SHA256:
`347378a8115b168d58ee743b7acc70e47ed915b097b9b6428f8218d326fff4e2`.
No calibration/query was repeated for this repair; #33 is closed with evidence.

NB_659 ran in `notebook07-NB_659-nz_u9xnu` as a detached batch at niceness 10
with thread limits 1. Its `status.json` records exit zero; `output-check.json`
verifies finite pixels and recorded scaling, exact WCS keyword values and sampled
sky coordinates, preserved timing and input hashes, and consistent saturation
units. Output: `Calibration_dir/CN_Ori_NB_659.coadd.fits`, shape 19729 x 18417.
DN2FLAM=2.60156342977624e-18, maximum relative scaling error
7.492641331862997e-08; 981 clean catalogue rows, 582 usable calibrators.
EXPTIME=480 s, TEXPTIME=2400 s, NCOMBINE=5 retain the existing calibration
convention; do not silently substitute total integration for equivalent exposure.
SATLEVEL=7.62879990694798e-16, SATURATE=7.5942006980366e-16; MAGSATL=16.318
has the same unresolved physical interpretation. Image SHA256:
`2ccf319453ff8b18c4cfc9444d8ff40e824b3946241097a88989c3ba0a92d407`.
Clean catalogue SHA256:
`5d466e200ff6e9eaa00b7e206b919b56f1f34c23f3144f869d1447c734b20277`.

The initial NB verifier required identical WCS card text and stopped on numeric
formatting only. The corrected value/sky-coordinate comparisons passed without
image edits or a calibration rerun. DATE-END datfix warnings arose during
read-only WCS parsing from unchanged MJD-END. HIERARCH warnings describe long
ESO keyword serialization, not a failed calibration.

The corrected writer was installed from b3ef4b4b6a0a7017b4446f0cfd24c65662e94dc6.
Chapman3 records `~/wenu-zpcal-saturation-euz_d7e9` show seven saturation and ten
metadata tests passing against source and installed wheel, ten packaging tests,
pip check and exact installed-source identity. Wheel SHA256:
`3e5d78d5095020c5caeca162b9cb742d278c276cfed5cf9a2018825f324e2e34`.

Fernando requested merge/cleanup and a pause until notebook 07b QC. Reuse these
outputs and saved queries. Preserve all earlier products, logs and separate
weight maps. Independent photometric/astrometric accuracy, physical saturation,
Phase 3 acceptance and Mac retesting remain pending.


## Notebook 07b and 08a functional checks, 24 October 2026

07b completed both filters through installed library calls in fresh isolated
copies at `notebook07b-qc-uq8x1s6d`. Both have 981 illumination-table rows, 590
finite frame magnitudes, and all nonfinite measurements excluded from the
reported residual selections. r_SDSS has 334 NaNs and 57 positive infinities;
NB_659 has 335 NaNs and 56 positive infinities. Source images and catalogues
retain their hashes. These invalid measurements remain in the full saved table,
not in the selected finite residuals; they have not all been assigned a cause.

For magnitude 13--17, r_SDSS has 459 selected rows, catalogue-minus-frame mean
0.03584815848214288 and scatter 0.025418532331133052 mag; NB_659 has 437 rows,
mean 0.015571600429506593 and scatter 0.03296354183402808 mag. These use the
calibration reference, not an independent validation catalogue. Each filter
has a QC image, two residual views, region files, `.illum.csv` and output checks.
07c is explicitly obsolete; continue through 08a rather than rerunning 07c.

08a existing fit/export/plot functions were exercised separately for each filter
at `notebook08a-chebyshev-6jhubdcu`, retaining degree (5,5), notebook 12--18 mag,
+/-0.25 residual selection, sigma-3 clipping and original errors/weights. r_SDSS
selected 504 stars and NB_659 516; each fit rank is 36 with 36 coefficients.
Export/readback matches direct polynomial evaluation to 2.220446049250313e-16
and 1.0581813203458523e-16 mag respectively. Same-fitting-star scatter changes
from 0.02729796086936255 to 0.015772353507174916 mag for r_SDSS, and from
0.03432194203231734 to 0.027392507874621 for NB_659. No independent validation
or image/catalogue correction follows from these fits.

The notebook's extra RBF display is a different surface from the saved polynomial.
The [display correction](../../chebyshev-display-correction.md) and #39 record
full-grid and covered-sample discrepancies. Historical plots/coefficients and
fit-check-arrays.npz remain immutable. Separate source issues remain open:
#37 fits only the last selected table in notebook control flow; #38's experimental
nonlinearity cell references undefined prior-kernel state. The diagnostic wrapper
processes each filter using library functions; it is not proof that those notebook
orchestration defects are fixed. No experimental nonlinearity correction ran.


## Display acceptance and pending Kriging, 24 October 2026

The direct display correction passed source/installed tests and regenerated
plot/grid checks from saved models in `notebook08a-direct-ppzkqpm0`, without
refitting or changing science images/catalogues. Source models and arrays are
unchanged. #39 is closed with evidence; [correction notes](../../chebyshev-display-correction.md)
record exact hashes and roundoff agreement. #37/#38 remain open.

08b preflight only: installed Kriging module SHA256
`e9142ec2ed809e0a6b6d8d23f2103d4a53aba11d68d8a7c236b6be6e3629e192`,
byte-identical to checkout source. PyKrige 1.7.3, lmfit 1.3.4, NumPy 1.26.4,
SciPy 1.17.1 and Astropy 6.1.7 imports passed. Its existing 1--20 mag, +/-1
residual selection (clipping mask explicitly cleared) yields 583 r_SDSS and
580 NB_659 positions, all unique; no random subsampling at limit 2000.
Parameters: Gaussian, maxlag 10000, nlags 200, init_kriging=False,
use_empirical_variogram=True, determine_empirical_variogram=True, fit_type=lmfit,
fixed_nugget=None, use_kfold=False, diagnostic offset 4 pixels, 50x50 grid.
These settings are recorded, not scientifically endorsed; the offset diagnostic
is not independent validation. No variogram, Kriging interpolation or correction
has run. Fernando requested merge/cleanup first, then continuation at 08b.


## Notebook 08b completed; saved reader defects, 24 October 2026

Both Gaussian Kriging runs completed in `notebook08b-kriging-4_ssz0f9`, sequential
niceness 10/thread limits 1, using the installed library and preserved settings.
r_SDSS selected 583 stars and NB_659 580. Both saved 50x50 FITS grids exactly
matching live grid arrays, finite correction/variance grids and five decodable
QC PNGs. Source illumination tables and prior check records remained unchanged.
`completed.json` and per-filter `output-check.json`/`kriging-check-arrays.npz`
retain parameters, hashes and diagnostics. No science-data correction occurred.

r_SDSS before scatter 0.03277068409366147 mag and four-pixel-offset residual
scatter 0.00850436182407726; NB_659 0.03649722564773833 -> 0.023369077164626034.
These offset checks are not independent validation and use a different selection
from the Chebyshev checks. NB_659 fitted psill=0.003378462027856533,
range=489.1362908360239 pixels and nugget=0.005894817742894744; model SHA256
`a5dc4409f8d5dfdbff40b4856443417b1394421f8f42e76439ee6b573c424106`,
arrays SHA256 `1df7076d67bd34b2461872fa01b19617719f6084a68a43bfd7415aa92aecb927`.

08c/readback found the [mapping defect](../../kriging-readback-correction.md)
#41 despite exact FITS serialization, plus swapped plotting arguments #42.
The first target diagnostic verified unchanged grids and quantified sample-node
errors before correction; details are in those tickets and correction notes.
Keep existing fits; fix/verify only reader coordinates and plotting bindings.
Notebook loop scope remains #37. Do not infer full notebook execution from
per-filter diagnostic-wrapper success.
