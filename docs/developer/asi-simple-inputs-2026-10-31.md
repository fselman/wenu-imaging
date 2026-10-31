# Practical ASI preparation inputs and generated dataset TOML

Owner-approved simplification, 31 October 2026, follows the qualified explicit
profile in PR #188 at `7bf1c8247a025ed3a927c21520edde186698fe0d` (#184).
The owner found frame-specific exposure/settings/filename rules impractical to
edit. Reusable observatory and camera inputs plus dataset directory names now
produce the detailed dataset TOML automatically. Data partitioning and its
additional metadata remain deferred. This changes preparation only, not Pycavi
association, native services, calibration arithmetic or the M4 acceptance gates.

## Inputs you maintain

| Input | Purpose | Example |
|---|---|---|
| Observatory TOML | Observatory, institution, optional telescope and source reference | [bath_observatory.toml](../../Pycavi2/config/preparation/bath_observatory.toml) |
| Camera TOML | Model aliases and documented hardware facts/capabilities | [zwo_asi1600mm_pro.toml](../../Pycavi2/config/preparation/zwo_asi1600mm_pro.toml) |
| Directory TOML | Recognized role/filter directory names, optional dataset DOI | [bath_directories.toml](../../Pycavi2/config/preparation/bath_directories.toml) |

The observatory input is reusable between nights. The camera input is reusable
between sites/datasets. Neither contains a particular exposure time, gain setting,
offset, temperature or filename pattern. Only schema, model/native dimensions,
pixel size and documented monochrome layout are required in the camera input;
sensor/shutter/manual/capabilities remain sourced descriptions. The current
implementation accepts 2D single-primary monochrome images within the native
camera dimensions, including smaller valid arrays; colour/Bayer, compressed files,
extra HDUs and arbitrary camera workflows remain unqualified. Full-frame versus
ROI/binning calibration applicability is not decided here.

The uploaded ASI1600 manual is saved unchanged in
[docs/manuals/cameras](../manuals/cameras/README.md), including its original
copyright notices. The camera input points to that copy and its exact SHA256.
Reviewed manual revision 1.5, August 2021: section 2/p4 identifies the MM Pro's
Panasonic MN34230ALJ sensor and monochrome/cooled variant; section 4/p6 gives
4656x3520, 3.8 micrometre pixels and rolling shutter. Section 6.6/p12 documents
10/12-bit ADC capabilities; section 6.7 discusses digital hardware/software
binning. The model and specification pages were also visually inspected.
Capabilities are not per-exposure settings. No ADC-depth card, inferred mode,
physical e-/ADU gain or read noise is manufactured from FITS storage/gain labels.

## Directory roles work in either order

Only recognized components **below the supplied dataset root** are considered;
matching is case-insensitive. Unrecognized components can name targets/nights
without becoming processing partitions. Exact configured aliases map to one
role or filter; no filename parsing or spelling guessing is performed.

| Paths | Result |
|---|---|
| `Flats/Blue/a.fits`, `Blue/Flats/a.fits` | FLAT, Blue |
| `DomeFlats/Blue/a.fits`, `Blue/DomeFlats/a.fits` | FLAT,DOME, Blue |
| `SkyFlats/Red/a.fits`, `Red/SkyFlats/a.fits` | FLAT,SKY, Red |
| `Science/a.fits` with FILTER=Blue | OBJECT, existing Blue filter |
| `Blue/a.fits` with recognized Light labels | OBJECT from header, Blue checked |
| `Bias/Darks/a.fits` or `Blue/Red/a.fits` | Blocked as contradictory |

Generic `Flats` never implies dome or sky illumination. A generic FLAT marker
can coexist with one more specific dome/sky marker; two incompatible roles
remain blocked. Header FRAME/IMAGETYP/DPR labels are checked against each other
and directory roles. Directory-declared flats retaining Light labels still
require explicit `--accept-directory-flats` at copy time. The acknowledgement
preserves the labels and records the declaration, not physical flat quality.
Existing conflicting DPR cards are never silently refined/overwritten.

## Filter precedence

| Existing FILTER | Recognized directory filter | Action |
|---|---|---|
| Present | Absent | Use header value |
| Present | Matches | Keep exact existing card |
| Present | Conflicts | Block and report |
| Missing | Present | Propose new FILTER card |
| Missing | Absent | Record unknown; do not guess |

An explicitly declared alias may map a directory token to a canonical label.
The same alias map is used when comparing a recognized header alias; original
header spelling is preserved. Unknown nonempty header labels remain usable
when no directory filter contradicts them. Empty or duplicate FILTER cards need
review. Filter checks apply to bias/dark frames too if a recognized filter
directory is present; filter never changes their bias/dark exposure role.

## Generated output and copy contract

The public [prepare_zwo_asi.py](../../Pycavi2/tools/prepare_zwo_asi.py) selects the
new interface when `--observatory`, `--camera` or `--directories` is supplied.
The qualified `--config` interface is retained unchanged for old plans/tests.
New implementation lives in
[asi_preparation_profiles.py](../../Pycavi2/tools/asi_preparation_profiles.py),
reusing the bounded scanner and existing byte-copy primitives.

Use `plan` with `--observatory OBS.toml --camera CAMERA.toml --directories DIRS.toml
--root RAW --report DATASET.toml`. The generated dataset TOML is the detailed
**output**, not another input to write by hand. It contains source input paths,
exact input hashes/effective settings, summaries of observed exposures, gain,
offset, temperatures and binning, every frame's reported metadata, unknowns,
original header cards, proposed additions, warnings/errors and source identities.
Generated TOML is parsed back and required to equal the plan before saving.
Variable settings are discovered and retained, not rejected as departures from
one hardcoded dataset profile. Missing optional acquisition settings remain
explicitly unknown. No calibrated reduction readiness is inferred.

`apply` takes those same three input TOMLs, `--plan DATASET.toml`, the exact
`--expected-plan-sha256`, and a separate fresh `--output`. It recomputes the
inventory and input identities, requires zero errors, acknowledges flat-Light
ambiguities where present, and produces copied FITS plus a JSON preparation
manifest. It checks source inventory and re-reads input TOMLs before publishing
the completion marker. A mid-copy configuration edit leaves the incomplete marker.
Concurrent input edits are unsupported; these checks are not atomic snapshots.

Additions include the selected observatory/institution/source DOI, camera model
and documented sensor/shutter if configured, canonical DPR, missing FILTER if
resolved from a directory, and the configured telescope name plus each original
DATE-OBS calendar date. Existing INSTRUME must match configured camera aliases;
if absent it is proposed from the selected camera with a warning. Telescope
aperture/focal length are cross-checked when present; missing geometry is reported
rather than turned into invented acquisition values. Raw TELESCOP/DATE-OBS,
site/observer cards and all other original nonchecksum cards stay unchanged.
Only stale CHECKSUM/DATASUM are removed. Opaque payload bytes, including padding,
are copied and independently SHA256-verified. Failures retain PREPARATION_INCOMPLETE;
only successful checks produce PREPARATION_COMPLETE. No native program runs.

## Evidence and target status

Existing agent environment: Python 3.12.14, Astropy 6.1.7, NumPy 1.26.4;
no package/dependency changes. Three synthetic suites pass:

- Existing Bath helper 9/9 in 1.345 s.
- Existing explicit generic helper 11/11 in 1.957 s.
- New simple input helper 12/12 initially in 0.891 s; final affected suite 12/12
  in 1.862 s after extending source/configuration-change failure controls.

The new controls cover both directory orders, flat subtypes, header-only filters,
filter insertion/unknowns/mismatches across all roles, role/label ambiguity,
variable/missing settings, generated TOML round-trip, independent old-card/payload
and unsigned endpoint verification, flat acknowledgement/matching existing DPR,
source/config/plan changes, interrupted and mid-copy-edited outputs, malformed
cards/duplicates/extra HDUs/links, declarative input validation, aliases and public
CLI plan/apply. Only synthetic preparation helpers/copy routines ran; no Pycavi
reduction, native code, observational processing or throughput check.
Logs and exact source identities are retained in
[the evidence directory](fixtures/agent-asi-simple-inputs-2026-10-31/).

[The Mac qualification runner](../../Pycavi2/tests/qualify_asi_simple_profiles.py)
was syntax-checked only. It guards the known Mac/Python/clean-main state, privately
exports pinned helper/test/profile/manual files, verifies the manual hash, runs
the same 32 controls and generates a header-only TOML for all 260 original Bath
frames. It retains source hashes/logs/plan/preservation receipt, without
installing anything, modifying original FITS or preparing observational copies.
Actual Mac execution of this interface remains pending, followed by bounded
representative-copy verification. Chapman qualification is needed if used there.
The prior 20-control/full-plan/ten-copy Mac passes at `7bf1c824` apply to the
previous interface only; their evidence remains retained in PR #188 and the
[provenance contract](zwo-asi-provenance-2026-10-31.md). No historical test campaign
or native M4 replay is required for this preparation-only change. Full-tree copy,
reduction, partitioning, calibration applicability and M4 closure remain separate.

## Retained reference PDFs

Owner-requested local documentation copies are indexed in
[the papers directory](../papers/README.md) (the original Bath article) and
[ESO standards](../standards/eso/README.md) (DICB ESO-044156 version 8).
The PDFs are unchanged; copy identities, source URL/DOI and document version
are recorded by those indexes. This addition changes reference storage/links
only and does not require a preparation or native test replay.
