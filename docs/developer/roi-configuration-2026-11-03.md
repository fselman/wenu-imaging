# Named detector ROI configuration — 3 November 2026

Each detector can have its own number, names, positions and sizes of regions.
Each region also identifies its output amplifier. Two detectors may both call
an amplifier OUT1: the detector name and amplifier name together select it.
Changing the order of detectors or FITS extensions must not change that selection.

This increment implements an opt-in configuration supplement and checked binding
into the existing `detector_roi` array. It does not yet add a full linearity CLI,
read raw pixels, select real OCAM regions, or fit ROI means as physical pixels.
The unchanged exact ROI operator handles the bound rectangles and their overlap.
A validated pixel-level forward model and raw-noise construction are still needed.

## File formats

Supply an explicit path and format, `paf` or `toml`, to
`mef_roi_config_read`. There is no default filename, inherited region, automatic
whole-detector fallback, include composition or override precedence. This is a
separate, versioned characterization supplement; the existing complete legacy
PAF and TOML v1/v2/v3 settings schemas are unchanged. It reuses qfits PAF queries
and the already bundled tomlc17 parser, rather than creating another value parser.

Example TOML with **synthetic coordinates**, not chosen OCAM regions:

```toml
roi_schema_version = 1

[[roi]]
id = "CHIP1.center"
detector = "CHIP1"
amplifier = "OUT1"
xmin = 1
xmax = 40
ymin = 1
ymax = 60

[[roi]]
id = "CHIP8.center"
detector = "CHIP8"
amplifier = "OUT1"
xmin = 10
xmax = 70
ymin = 20
ymax = 80
```

Equivalent PAF:

```text
PAF.HDR.START;
PAF.HDR.END;
MEF.ROI.VERSION 1;
MEF.ROI.COUNT 2;
MEF.ROI.1.ID "CHIP1.center";
MEF.ROI.1.DETECTOR "CHIP1";
MEF.ROI.1.AMPLIFIER "OUT1";
MEF.ROI.1.X.MIN 1;
MEF.ROI.1.X.MAX 40;
MEF.ROI.1.Y.MIN 1;
MEF.ROI.1.Y.MAX 60;
MEF.ROI.2.ID "CHIP8.center";
MEF.ROI.2.DETECTOR "CHIP8";
MEF.ROI.2.AMPLIFIER "OUT1";
MEF.ROI.2.X.MIN 10;
MEF.ROI.2.X.MAX 70;
MEF.ROI.2.Y.MIN 20;
MEF.ROI.2.Y.MAX 80;
```

The seven fields in each entry are required. Bounds are exact integers, in
inclusive FITS 1-based **active amplifier-local pixels**; electronic scans are
excluded. Each rectangle must fit inside the active width and height supplied by
the caller's verified amplifier geometry. A detector-coordinate rectangle crossing
an amplifier boundary must first be split and transformed explicitly; this reader
does not guess that transformation. No science thresholds or signal ranges live
in this file.

Region IDs are globally unique, 1–63 ASCII letters/digits or `._:-` (including
detector/amplifier names in the region ID is recommended). Detector and amplifier
names follow the same character/length restriction. Case is significant. Up to
4096 entries and 1 MiB of source text are allowed as software resource bounds.
Different regions may overlap; overlap does not create independent measurements.

PAF body keys use canonical positive decimal ordinals, one unindented key per
line, semicolon terminated; blank/comment lines and standard PAF header cards
are allowed. Repeated or unknown body keys are rejected before qfits queries,
which otherwise return the first match. TOML rejects repeated definitions through
the existing parser; exact field counts and required names reject unknown keys.
Neither format accepts fractional bounds, embedded NULs, empty identities,
repeated region IDs, reversed bounds or an unknown schema version.

## Native interface and ownership

`mef_roi_config_read` returns an owned immutable snapshot of named entries and
exact source bytes. Initialize the existing TOML parser once, serially, before
TOML reads. `mef_roi_config_source` and `mef_roi_config_count` inspect that snapshot;
`mef_roi_config_destroy` releases it. The optional existing `mef_allocator`
controls snapshot allocations, not dependency-parser allocations.

`mef_roi_config_bind` receives the actual named amplifier list and active
width/height for each member. It resolves both identities, checks geometry and
writes a caller-owned `detector_roi` array for `detector_roi_problem.roi`.
Rebind if the amplifier list is reordered: the numerical amplifier indices refer
only to that list. Unknown names, duplicate detector/amplifier pairs, inadequate
output capacity or out-of-bounds rectangles fail before changing any output or
its count. Input identity/geometry is borrowed and unchanged. The existing ROI
aggregation service subsequently owns its own copies. Not every amplifier must
have a region; no missing coverage is invented.

No file is reopened during binding, even if the original source was removed.
PAF loading checks the final file bytes against its frozen source after qfits
queries. This is serial configuration loading, not a concurrent mutable-file API.
No engine execution, FITS access, native statistics change, ASDF creation or
installation is performed by these interfaces.

## Qualification

Agent GCC C17 Release preparation: `native_roi_config` passed 1/1 in 0.07 s;
normal `mefpp` builds. Synthetic controls compare PAF/TOML results for three
regions, including two overlapping regions on one detector and one on another.
They check reordered identities, equal amplifier names on different detectors,
unknown detector/amplifier names, duplicate input identities, insufficient
capacity, bounds, malformed schemas and all three snapshot allocation failures.
Outputs/count remain unchanged on binding failures; source removal does not
invalidate the snapshot; custom allocator live counts return to zero.
The Mac qualifier's Python syntax is checked. These are software preparation
results; actual Mac qualification of this new layer remains pending.

Run `Pycavi2/tests/qualify_roi_config_mac.py` from an exact exported revision in
a fresh retained directory, using normal imaging Python and niceness 10. It
builds the new config probe plus normal `mefpp`, runs only `native_roi_config`,
and checks checkout, installed-file and exported-source preservation. Previous
numerical gates are reused because their source and behavior are unchanged.

The preceding exact ROI operator at 4d0bb46228dab9719b7c903e3082710b3cc333f1
passed actual Mac 3/3 in 3.01 s, retained at
`/Users/fselman/Software/build/wenu-imaging/mac-roi-aggregation-2SOrKVed`.
All three preservation checks passed; checkout stayed clean main c73d9a9e.
PR #227 remains unmerged; no installation or real-data processing is implied.
