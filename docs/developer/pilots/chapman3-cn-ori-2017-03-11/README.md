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
The other four r_SDSS and five NB_659 exposures have not yet been run through
this complete runner/assembly path. Earlier 32-detector diagnostic solves for
each filter remain separate evidence and are preserved.
