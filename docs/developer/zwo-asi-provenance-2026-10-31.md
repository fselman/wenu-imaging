# TOML-driven ZWO ASI preparation and Bath provenance

Owner request, 31 October 2026, following the successful ten-representative
Mac copy qualification: replace dataset policy embedded in a Bath-named helper
with a generic ZWO ASI entry point and a TOML configuration. Include provenance
established by Scowcroft et al. (2023), *Physics Education* 58, 035014,
[doi:10.1088/1361-6552/acbf1b](https://doi.org/10.1088/1361-6552/acbf1b).
The owner supplied the complete 14-page PDF (13 article pages plus cover),
`Scowcroft_2023_Phys._Educ._58_035014.pdf`; all extracted pages were available.
Tracks #184; candidate malformed-header reporting correction #187 remains
target-pending. M4 and native PR #186 retain their separate gates.

## Telescope identification from returned Mac headers

The owner-returned read-only inspection reports all 260 FITS files share one
signature: `TELESCOP=SynScan`, `FOCALLEN=1600.0` mm, `APTDIA=200.0` mm,
`SCALE=0.4899625` arcsec/pixel, `PIXSIZE1/2=XPIXSZ/YPIXSZ=3.8` micrometres,
and 1x1 binning. DATE-OBS spans `2022-01-08T22:04:06.108` to
`2022-02-06T19:06:04.613`. Together with paper Table 1, this distinguishes the
StellaLyra RC from the 130/910 mm refractor. This is identification from the
reported acquisition setup, not an independent plate-scale or optics measurement.

The TOML now has optional `[telescope]` name-prefix and complete expected-header
signature checks. Only matching frames receive `HIERARCH WENU PROV TELESCOPE`,
e.g. `BPO StellaLyra RC 8-inch 2022-01-08`. The suffix is the calendar date
recorded by each frame's valid ISO DATE-OBS, with no timezone conversion or
inference of commissioning/build date. It is a descriptive dated setup label,
not a new detector ID or calibration-association key. Preserve original
`TELESCOP=SynScan`, DATE-OBS and all other acquisition cards byte for byte.
Missing/duplicate/invalid dates, mismatched geometry or conflicting derived
provenance block preparation. No current Pycavi grouping policy is changed.

The affected generic suite passes 11/11 in 1.993 s, including two-date copies
and geometry/date/conflict refusal. The legacy shared-copy source is unchanged
from its previous 9/9 run. Log and new exact source hashes are retained beside
the earlier evidence. Actual Mac TOML plan/copy qualification remains pending;
this returned header inspection did not execute the new helper.

## Complete detector-mode header audit

Owner-returned Mac audit inspected every primary-header card name, value and
comment in all 260 frames. Full local inventory retained at
`/Users/fselman/Software/build/wenu-imaging/mac-asi-mode-audit-oox7oh3e/all-primary-headers.json`.
The console reports no explicit detector/readout mode, ADC bit depth, readout
speed, USB-bandwidth, driver, firmware or acquisition-software metadata. All 260
have INSTRUME `ZWO CCD ASI1600MM Pro`, GAIN setting 139.0, OFFSET setting 10.0,
XBINNING/YBINNING 1, BITPIX 16 and BZERO 32768. File sizes and modification times
were preserved. This is owner-returned console evidence; the complete JSON was
not transferred or independently read in the agent workspace.

Record acquisition mode/ADC/readout/software as unknown. FITS unsigned-16 storage
is not evidence of acquisition ADC bit depth or readout mode; gain/offset numbers
are reported acquisition settings without physical-unit conversion. Do not add
inferred mode/gain/RON metadata or change pixels. No code change is needed to
retain these unknowns. The full keyword list additionally includes SITELAT,
SITELONG and OBSERVER, but their values were not printed; inspect those before
asserting absence, filling provenance or assigning precise site coordinates.

## Provenance established by the paper

| Information | Source | Treatment |
|---|---|---|
| Bath Physics Observatory, BPO | Article p. 2, section 1 | `OBSERVAT = 'Bath Physics Observatory'` |
| University of Bath | Affiliations, section 1 | `ORIGIN = 'University of Bath'`, institution of acquisition |
| Paper DOI | Article p. 13 | `HIERARCH WENU PROV PAPER DOI` |
| M51 dataset DOI `10.15125/BATH-01225` | Figure 1(d), data availability, reference 8 | `HIERARCH WENU PROV DATA DOI` |
| ASI1600MM Pro monochrome, 4656 × 3520, 3.8 µm | Section 2, Table 2 | Camera entry and descriptive reference; existing `INSTRUME` checked and preserved |
| StellaLyra 200/1600 mm RC and TS Optics 130/910 mm triplet | Table 1 | Paper alone: reference only; returned headers now support dated WENU telescope provenance |
| EQ6 Pro SynScan mounts, ZWO EFW8 and EAF | Section 2, pp. 5–6 | Descriptive reference only |
| Raspberry Pi 4, Astroberry, INDI, KStars and Ekos | Section 2, p. 4 | Descriptive reference only; no acquisition software/version claims per frame |
| Campus-edge site near sports pitch | Section 2.1 | Descriptive reference only; no invented coordinates or elevation |

`OBSERVAT` is the chosen short FITS keyword for the requested observatory name;
no second competing `OBSERVATORY` card is introduced. The WENU DOI cards are
project-defined provenance, not ESO acquisition identifiers or a standards
compliance claim. The archive DOI is supported by the paper's explicit link
between Figure 1(d)'s M51 data and the archive. Association with the owner's
local Bath tree comes from the supplied dataset context, not an independent
byte-level comparison with an archive download. The paper does not identify
per-frame observers, filter transmission, physical gain/RON,
ADC mode or precise coordinates; these remain unknown. The telescope identification above depends on the returned header signature,
not the paper alone; other historical configurations remain unassigned.

## Interfaces and policy

- New checkout-only entry point: [prepare_zwo_asi.py](../../Pycavi2/tools/prepare_zwo_asi.py).
- Example: [zwo_asi1600mm_bath.toml](../../Pycavi2/config/preparation/zwo_asi1600mm_bath.toml).
- Shared existing bounded header/copy primitives:
  [fits_preparation.py](../../Pycavi2/tools/fits_preparation.py).
- Legacy `prepare_zwo_bath.py` remains compatible, now importing those primitives;
  no Bath policy or filename appears in the generic entry point.

TOML separates `[camera]` identity from `[dataset.expected]` acquisition checks,
`[[rules]]` classification, `[provenance]` cards and `[reference]` descriptive
information. This first entry point supports explicitly configured monochrome,
single-primary 2D images. It is a generic policy interface, not certification of
all ASI models, colour/Bayer acquisition, compressed files or arbitrary layouts.
No dependency was installed or upgraded; `tomllib` requires Python 3.11+.

`plan --config PROFILE --root RAW --report PLAN` reads bounded primary headers
and metadata. Each file includes the proposed DPR/provenance cards and reported
values; the plan includes the full parsed TOML plus its exact byte SHA256.
`apply --config PROFILE --plan PLAN --expected-plan-sha256 SHA --output NEW`
recomputes the complete plan and exact config hash. Even a TOML comment change
invalidates it. For ambiguous flat Light labels, explicit
`--accept-directory-flats` remains required; no physical calibration validation
is inferred. The output must be separate and new; originals are never rewritten.

Only the allowlisted provenance keys may be added from `[provenance]`:
`OBSERVAT`, `ORIGIN`, optional `TELESCOP`/`OBSERVER`, and the two DOI cards.
Existing equal values remain once; conflicts/duplicates block the file.
Optional `[telescope]` checks allow only the eight signature keys recorded above
and derive only `WENU PROV TELESCOPE` from a configured prefix and DATE-OBS.
`INSTRUME` must match an explicit string in the camera entry and is never added
or replaced. Arbitrary structural/pixel/date/ESO programme cards cannot be
injected through provenance. Unknown policy keys are errors. Descriptive
reference fields do not authorize FITS changes. Constants for exposure, filter,
filename prefix, temperature and acquisition settings belong to TOML, not code.

The shared copy routine retains original nonchecksum cards byte for byte,
including existing telescope, camera, dates and labels. New standard short
keywords use ordinary FITS cards; DPR and DOI keys use HIERARCH. The only removals
are stale CHECKSUM/DATASUM. Opaque payload/padding is streamed and independently
hashed unchanged. The manifest preserves effective configuration, exact config
hash, reviewed plan hash, source/prepared/payload hashes and acknowledgement.
A copy failure retains `PREPARATION_INCOMPLETE`; only success changes it to
`PREPARATION_COMPLETE`. No pixel processing, Pycavi/mefpp call, association,
dark scaling, physical gain substitution or installed activation is performed.
Concurrent input edits are unsupported; stat/header checks are not atomic snapshots.

## Verification and evidence

Existing agent environment: Python 3.12.14, Astropy 6.1.7, NumPy 1.26.4;
`/workspace/scratch/555b377cf948/m3-test-env/bin/python`. No package changes.

- Legacy nine-group regression passed 9/9 in 1.067 s after shared-copy extraction.
- Generic nine-group suite initially had one malformed-card reporting error:
  Astropy `VerifyError` escaped the narrowed handler. Corrected under #187;
  affected suite then passed 9/9 in 1.644 s; final reference-table controls
  passed 9/9 in 1.660 s. Failed evidence is retained.
- Generic controls cover ten role/filter groups, exact raw cards/payload and
  decoded unsigned endpoints, provenance conflict/duplicate/equal values,
  config/source staleness, failed-output marker, flat acknowledgement, aliases,
  forbidden/malformed configuration, a second synthetic camera/geometry/path
  policy, unknown/linked inputs, real CLI plan/apply and destination guards.
- Eleven changed-guide local link targets and whitespace checks passed.
- These tests call helper functions/CLI and shared copy primitives on synthetic
  files only. They do not exercise production reduction routines or native C.

Committed logs and source hashes live in
[the evidence directory](fixtures/agent-zwo-asi-provenance-2026-10-31/).
Synthetic fixtures remain at the paths recorded in those logs. No real raw FITS
files were transferred to or edited in this workspace.

Owner-returned previous-helper Intel Mac evidence (source `c81cb86`): nine tests
passed in 1.350 s; complete 260-file plan had BIAS 10 / DARK 10 / OBJECT 196 /
FLAT 44, zero blocked. Original plan SHA256:
`5205619c7951f8f19bd21b9ffd363e4eac0298298f0613b44f6a1d694625e0bb`.
Retained run: `/Users/fselman/Software/build/wenu-imaging/mac-m4-preparation-n_6xa0vf`.
Subsequent ten-copy run:
`/Users/fselman/Software/build/wenu-imaging/mac-m4-copy-check-j8byv11h`, subset SHA256
`eabf9855db653ae95d8cc8744c53e8ab4f970f5ffaeba5b8024f476a6939f9cf`.
All ten original-card/payload/DPR checks and installed-file/raw-metadata/clean-main
preservation passed. These console receipts are owner-returned; the JSON/pixels
were not independently transferred. They qualify the previous classification-only
helper, not the new provenance configuration.

Next: fresh Mac preflight, private export, synthetic controls, new full header-only
plan and representative provenance-copy verification. Chapman qualification is
pending if this helper is used there. No full-tree copy or reduction is authorized
by successful agent tests; preparation success does not establish calibration
applicability, full CMOS support, throughput or scientific acceptance. PRs #183
and #186 remain unchanged; merge/cleanup requires the owner's instruction.
