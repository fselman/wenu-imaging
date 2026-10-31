# Preparing raw imaging data

Owner-requested admission rule, 31 October 2026: raw observations must carry
reviewed observation category, exposure type and observing technique before
entering the Pycavi/mefpp reduction workflow. Preparation is separate from the
C numerical kernels and from calibration association. Track
[#184](https://github.com/fselman/wenu-imaging/issues/184), alongside
[M4 detector/layout review](developer/m4-interface-fixture-review-2026-10-31.md).
The new helper implements preparation only; global CLI/C enforcement is not yet
implemented, and these cards alone do not establish processing readiness.

## Practical inputs and generated dataset TOML

The owner-approved [simple-input interface](developer/asi-simple-inputs-2026-10-31.md)
uses separate reusable observatory/camera TOMLs and a small directory-name map.
Exposure/settings/filenames are discovered from headers. Directory role/filter
components work in either order; dome, sky and unspecified flats remain distinct.
FILTER is header-first and checked against a directory label when present;
missing filters can be proposed from a directory, otherwise remain unknown.
The detailed dataset TOML is generated output for review and exact-plan copying.
The [uploaded camera manual](manuals/cameras/ASI1600_Manual_EN_V1.5.pdf) is retained
unchanged and referenced by the camera input. Agent controls pass 9+11+12; actual
Mac qualification of this new interface is pending. The explicit-profile interface
below remains qualified at its recorded revision and available for compatibility.
Partitioning is deferred; no change to native C or calibration selection is made.

## ESO definitions and actual FITS names

Reviewed source: [ESO Data Interface Control Document, ESO-044156, version 8,
5 March 2025](standards/eso/ESO-044156_8_Data_Interface_Control_Document.pdf)
([official source](https://archive.eso.org/cms/tools-documentation/dicb/ESO-044156_8_Data_Interface_Control_Document.pdf)),
section 4.4.2.1, pages 37–40, Tables 9–11; the official
[DICB index](https://archive.eso.org/cms/tools-documentation/eso-data-interface-control.html)
identifies this version as current at review. These are raw-observation
classification concepts, not detector identities or reduction recipes.

| DICB notation | Meaning | Actual primary-header card name |
|---|---|---|
| `DPR.CATG` | Observation purpose/category | `HIERARCH ESO DPR CATG` |
| `DPR.TYPE` | Kind of exposure | `HIERARCH ESO DPR TYPE` |
| `DPR.TECH` | Observing technique | `HIERARCH ESO DPR TECH` |

Category values are `SCIENCE`, `CALIB`, `ACQUISITION`, `TECHNICAL`, `TEST`, or
`OTHER`. Types include `OBJECT`, `BIAS`, `DARK`, and `FLAT`; imaging technique
is `IMAGE`. Type/technique may contain comma-separated general-to-specific
qualifiers, without spaces; their tables are examples, not exhaustive enums.
Use `FLAT,SKY` or `FLAT,DOME` only with evidence of the illumination source.
Using observations in software tests does not change their acquisition purpose
to `TEST`. In Astropy, access these cards as `header['ESO DPR TYPE']`, etc.;
do not insert competing dotted or abbreviated spellings.

Processed calibration/science products have a different contract: section
4.7.1, pages 50–51, specifies `PRO` metadata and excludes `DPR` cards for the
ESO-generated products it covers. This preparation rule concerns raw inputs;
do not stamp raw classifications onto master products or mistake three added
cards for complete DICB/ESO Phase 3 compliance. Preserve non-ESO origin and all
acquisition metadata; never invent an ESO programme, OB or template.

## TOML-driven ZWO ASI preparation

The current candidate is [prepare_zwo_asi.py](../Pycavi2/tools/prepare_zwo_asi.py),
with the [Bath TOML entry](../Pycavi2/config/preparation/zwo_asi1600mm_bath.toml).
Supply `--config` to both `plan` and `apply`. Camera identity, acquisition checks,
directory roles and provenance are explicit configuration, rather than embedded
Bath policy. Existing `INSTRUME` is checked and preserved. `OBSERVAT`, `ORIGIN`
and paper/data DOI cards are proposed only in new copies; conflicting existing
values block preparation. Exact TOML bytes and effective settings are bound to
the reviewed plan and manifest. See [the provenance contract and paper evidence](developer/zwo-asi-provenance-2026-10-31.md)
for keyword mappings, unknowns, allowlisted fields and qualification limits.

The paper documents two telescope systems; the subsequently returned uniform
200/1600 mm header signature identifies the StellaLyra RC for all 260 frames.
The TOML now checks that signature and adds a dated `WENU PROV TELESCOPE` label,
preserving original `TELESCOP=SynScan`. Observer, site coordinates and software
versions remain unknown. Descriptive equipment references remain
in TOML/manifest. The interface currently supports configured monochrome primary
images; arbitrary ASI models/colour layouts remain unqualified.

Legacy commands below describe the previously qualified Bath-specific helper.
Its nine controls and the new eleven TOML/provenance controls pass in the agent
environment; actual Mac qualification of the TOML path is pending. The previous
Mac full 260-file plan and ten-copy qualification passed, with original files,
installed components and clean main preserved. Do not reuse a legacy plan with
the new tool: create and review a fresh plan including provenance.

## Initial Bath/ASI1600MM Pro mapping

Use [prepare_zwo_bath.py](../Pycavi2/tools/prepare_zwo_bath.py), a checkout-only
dataset helper using the existing Python/Astropy environment. It calls neither
Pycavi processing routines nor mefpp. This is not a generic ZWO camera importer.
All three proposed cards are placed in the primary header of prepared copies.

| Exact relative directory | DPR.TYPE | DPR.CATG | DPR.TECH | Supporting check |
|---|---|---|---|---|
| `Bias/` | `BIAS` | `CALIB` | `IMAGE` | Bias frame labels; 0.000032 s |
| `Darks/` | `DARK` | `CALIB` | `IMAGE` | Dark frame labels; 30 s |
| `Blue/`, `Green/`, `Red/`, `Luminance/` | `OBJECT` | `SCIENCE` | `IMAGE` | Light labels; matching filter; 32 s; expected filename form |
| `Flats/Blue/`, `Flats/Green/`, `Flats/Red/`, `Flats/Luminance/` | `FLAT` | `CALIB` | `IMAGE` | Matching filter, short exposure and filename; Light labels explicitly flagged |

Flat exposure expectations are respectively 0.035, 0.055, 0.100 and 0.018 s.
These are this dataset's reviewed header patterns, not universal classification
thresholds. The known `Light`/`Light Frame` flat labels are preserved verbatim;
they require `--accept-directory-flats` at copy time after the plan is reviewed.
That acknowledgement records a deliberate directory-role declaration, not
proof that the illumination is uniform or the image is a physically valid flat.
A Bias/Dark label in a flat directory remains a blocking contradiction.

Other checks before adding cards:

- Require the exact reported camera string `ZWO CCD ASI1600MM Pro`, one full
  primary image, 4656 by 3520 pixels, 1 by 1 binning, `BITPIX=16`, `BSCALE=1`,
  `BZERO=32768`, camera setting `GAIN=139`, and `OFFSET=10`.
- Compare directory, filename exposure, `EXPTIME`, optional `EXPOSURE`, filter
  and both `FRAME`/`IMAGETYP`. Require finite recorded temperature; report values
  differing from -5 C without imposing a new calibration tolerance.
- Reject unknown FITS directories/names, symlinks/nonregular inputs, duplicate
  selected cards, conflicting existing DPR values/aliases, Bayer metadata,
  truncated/extra payload or additional HDUs. Identical existing DPR cards stay.
- Inspect all discovered FITS candidates, not just the earlier 256/260 sample.
  Ignore/report ZIP and other non-FITS files; do not unpack archives or classify
  their contents. File enumeration is limited to 10000 and primary headers to
  256 KiB. Compressed FITS are blocked by this narrow helper.

These are lightweight consistency checks, not image analysis. Directory and
filename labels share an origin and are not independent scientific evidence.
They cannot establish an optically dark exposure, flat-field illumination,
linearity, saturation, dark-current scaling or applicability of calibrations.
Unfamiliar files need a revised explicit dataset policy; do not broaden acceptance
or ignore errors just to make the batch pass.

## Review, prepare copies, verify

1. Run the helper's `plan` subcommand with `--root` set to the original Bath
   directory and `--report` pointing to a new JSON file outside it. This reads
   headers/stat only and changes no source FITS file. It reports every proposed
   classification, original labels, warnings, errors, file identity and primary
   header digest. A nonzero status means blocked inputs; retain the report.
2. Review the mapping and warnings, especially flat roles and temperature
   exceptions. The console prints the report's SHA256; record that exact value.
   Do not hand-edit the plan to evade checks. Classification errors require
   source-evidence/policy review and a new plan.
3. Run `apply` with `--plan`, `--expected-plan-sha256`, and a new `--output`
   directory separate from raw inputs. If needed, explicitly pass
   `--accept-directory-flats`. Apply repeats inventory/rules/source identity
   checks before writing, then creates classified copies in the same relative
   layout. It never updates originals or overwrites a prepared tree.
4. Apply preserves original nonchecksum primary cards byte for byte, including
   original labels, filters, dates/OB/template metadata and scaling. It inserts
   only missing DPR cards and a preparation HISTORY tag. Original primary
   CHECKSUM/DATASUM cards are omitted from copies to avoid stale integrity claims;
   the manifest records this. No new FITS checksum is asserted.
5. Every byte after the original primary header, including data padding, is copied
   unchanged and independently SHA256-checked in the result. The manifest records
   source/prepared file hashes, payload digest, reviewed plan, acknowledgements
   and removed checksum names. Source stat is rechecked; header growth/padding
   may move the payload offset but cannot change its bytes.
6. Only a completed tree with `PREPARATION_COMPLETE` and
   `preparation-manifest.json` is eligible for later input review. Any failure
   retains the partial tree marked `PREPARATION_INCOMPLETE`; do not feed it to
   the pipeline. Successful preparation does not launch a reduction.

The plan uses header hashes and device/inode/size/mtime/mode, not a whole-dataset
pixel snapshot. Do not modify inputs concurrently; preserved/reset timestamps
cannot make this an atomic snapshot. Apply streams raw bytes for copying/hashing,
but never interprets pixel arrays or changes units/numerical values. It requires
space for a separate prepared dataset. It does not copy ZIP archives.

## Camera manual and remaining calibration choices

Reviewed [official ZWO ASI1600 manual, revision 1.5, August 2021](https://i.zwoastro.com/zwo-website/manuals/ASI1600_Manual_EN_V1.5.pdf):
section 2/page 4 identifies the MM Pro as a cooled monochrome model with Panasonic
MN34230ALJ; section 4/page 6 gives 4656 by 3520, 3.8 micrometre pixels and rolling
shutter; section 6.6/page 12 describes 10/12-bit ADC modes. Model names matter:
this is not the user's ASI585MC or an arbitrary `ASIxxxx` device.

Inference for preparation: unsigned-16 FITS encoding does not prove acquisition
ADC mode, bit alignment or a saturation threshold. Do not shift/requantize pixels,
infer a Bayer pattern or manufacture physical gain/read-noise values. The manual
does not establish this acquisition software's FITS `GAIN=139` units. Keep raw
settings and unknowns; characterize later under the relevant service/noise gates.
For a rolling-shutter camera, a dark classification describes an optically dark
acquisition; this helper cannot verify the camera was covered from its headers.

Bath's 30 s darks versus 32 s science and short flats need explicit calibration
decisions before use. Do not scale darks, substitute temperature tolerances or
subtract bias twice as part of classification. Single-primary/no-scan service
readiness remains pending in M4/M5; required uncertainty remains M6a; grouping and
calibration association stay in Pycavi. Raw classification is an admission
requirement, not authorization to change numerical algorithms or scientific policy.

## Qualification status

The helper has focused synthetic controls for directory roles, header conflicts,
plan staleness, source/destination protection, header growth, preserved opaque
payload/scaling and incomplete-output markers. See
[test_zwo_bath_preparation.py](../Pycavi2/tests/test_zwo_bath_preparation.py).
Agent results and actual-target status are recorded in the corresponding
[M4 preparation receipt](developer/m4-preparation-helper-2026-10-31.md).
Previous-helper actual Mac full-dataset plan and ten representative-copy checks passed;
new TOML/provenance target checks remain pending. No installed activation follows
from agent tests. See the provenance contract linked above for the dated receipts.
