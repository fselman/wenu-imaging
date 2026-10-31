# M4 interface and fixture review — 31 October 2026

Review for [M4 #182](https://github.com/fselman/wenu-imaging/issues/182), after
owner acceptance/merge of M3 through [PR #178](https://github.com/fselman/wenu-imaging/pull/178).
Baseline main: `6c4b0f0eff639da8dbef890f0df10f86c70bb0ee`.
Owner-returned Mac and Chapman4 commands confirm clean main at that commit,
merged review branch cleanup, retained evidence and unchanged protected installed
module/engine/configuration. M3 #159 is completed. Earlier pending M3 notes are
historical receipts, not current gates.

The owner instructed M4 review and inclusion of `~/Pictures/ZWO_Bath/` for
single-detector support and the astrophotography profile. This document proposes
concrete interfaces and fixtures for review. No runtime implementation,
installation, engine activation, reduction or new scientific policy is supplied.
The original [M4 scope](../architecture/proposed/implementation-plan.md#m4--detector-identity-and-image-layout-layer)
and [readiness review](m4-readiness-review-2026-10-31.md) remain the foundation.

Subsequent owner addition: raw inputs must carry reviewed DPR.TYPE/CATG/TECH
before pipeline admission. The [data preparation guide](../data-preparation.md)
reviews ESO DICB v8 and the actual camera manual; #184 adds a dataset-specific
Python plan/copy helper with consistency checks, outside C numerical processing.
This explicitly authorized helper is an addition to this review PR, not M4 C
implementation, automatic classification policy inside mefpp or generic CMOS
acceptance. Actual-target preparation qualification remains pending.

## Returned Bath header evidence

Source: owner-pasted output from the read-only Mac inventory in this Work chat.
Retained full report on the Mac:
`/Users/fselman/Software/build/wenu-imaging/mac-m4-zwo-inventory-0we7sgup/report.json`.
Neither raw frames nor that JSON report have been independently transferred or
audited here. No archive contents, dataset paper, pixel values, photometry or
detector noise model were inspected. The eight non-FITS files comprise seven
ZIP files and one file without a suffix; their contents remain unknown.

- Root: `/Users/fselman/Pictures/ZWO_Bath`.
- 268 regular files inventoried; 260 `.fits` candidates; 256 headers sampled
  round-robin across directories. Four FITS remain uninspected; sampled counts
  below are not complete dataset totals.
- Every sampled file reports one `PrimaryHDU`, index 0, `NAXIS=2`, dimensions
  4656 by 3520, `BITPIX=16`, `BSCALE=1`, `BZERO=32768`, binning 1 by 1.
- Reported camera string: `ZWO CCD ASI1600MM Pro`; telescope: `SynScan`.
  `GAIN=139.0`, `OFFSET=10.0`; 252 samples report `CCD-TEMP=-5.0`, four `-4.5`.
- No selected EXTNAME/EXTVER, BUNIT, physical serial or Bayer-pattern card was
  displayed. Absence of these selected cards does not establish full hardware
  identity, amplifier layout, physical gain, signal units or colour processing.
- Zero sampled reader warnings/errors. The script compared original file
  device/inode/size/mtime/mode before/after; no pixel reads or content hashes.
  This is bounded header evidence, not FITS/pixel/scientific qualification.

| Location / reported role | Sample count | Reported filter | Exposure (s) | Temperature exception |
|---|---:|---|---:|---|
| `Bias/`, Bias Frame | 10 | Ha | 0.000032 | One at -4.5 C |
| `Darks/`, Dark Frame | 10 | Ha | 30 | None displayed |
| `Blue/`, Light Frame | 16 | Blue | 32 | None displayed |
| `Green/`, Light Frame | 16 | Green | 32 | None displayed |
| `Red/`, Light Frame | 16 | Red | 32 | None displayed |
| `Luminance/`, Light Frame | 144 | Luminance | 32 | One at -4.5 C |
| `Flats/Blue/`, Light Frame | 10 | Blue | 0.035 | None displayed |
| `Flats/Green/`, Light Frame | 10 | Green | 0.055 | None displayed |
| `Flats/Red/`, Light Frame | 10 | Red | 0.100 | One at -4.5 C |
| `Flats/Luminance/`, Light Frame | 14 | Luminance | 0.018 | One at -4.5 C |

Flat roles require an explicit project declaration: their headers say Light
Frame. Retain both declared role and raw contradictory/incomplete metadata;
directory/filename clues are review evidence, not an association algorithm.
The Ha filter labels in bias/dark files do not prescribe filter-based selection.
The 30 s darks are not demonstrated substitutes for the 32 s lights or the
short flats. Do not silently scale dark current, remove bias twice or apply an
unqualified temperature tolerance. `GAIN=139` remains a reported camera setting
with unresolved physical units; do not treat it as electrons/ADU. No saturation
or linearity threshold follows from BITPIX/BZERO or the storage range.

## Proposed C interface responsibilities

Reuse internal C90 `mef_status`, allocator, request/context/result/error patterns.
Function/type names below describe proposed responsibilities, not existing APIs
or a frozen ABI. Update associated `.h` and `.c` files together when implemented.

| Boundary | Proposed input/output and ownership | Required behavior |
|---|---|---|
| Layout discovery, proposed `mef_layout_read` | Absolute resolved path and explicit resource limits; owned opaque catalogue, independently owned optional error | Read bounded FITS headers without pixels or source modification. Catalogue every HDU's physical order, kind, dimensions/type/scaling and optional name/version/unit evidence. Non-image HDUs stay distinguishable. |
| Identity binding, proposed `mef_layout_bind` | Borrowed catalogue and explicit configured/header mapping; owned validated bindings | Separate stable logical detector ID, optional verified physical ID, amplifier/channel mapping and file-local selectors. Preserve authority/conflicts. Single primary image uses an explicit configured logical ID; do not fabricate hardware identity or an extension. |
| Request compatibility | Existing resolved science/calibration role lists plus independently bound layouts/configuration | Resolve each file separately. Compare detector identity and required geometry/readout/unit/correction state before arithmetic. Never pair by shared ordinal or choose calibrations. |
| Plane loading and dispatch | Validated file-local binding; owned working plane to existing detector service | Decode FITS scaling exactly once, then use the same service for HDU 0, one-extension and mosaic inputs. No fictitious mosaic or alternate Python numerical implementation. |

Owned outputs start NULL, occupied outputs are rejected intact, failed calls
transfer no partial catalogue/plane, and destructors accept NULL. Views borrow
from their owner. Diagnostic allocation failure must not replace authoritative
status. No new global mutable mapping, cwd changes, implicit file discovery or
installed ABI exposure is proposed. Header discovery does not certify that the
subsequent pixel payload is readable; the loader must check its own I/O.

### Descriptor details to agree

1. Keep asset identity, logical detector identity, optional physical identity,
   amplifier/channel identity and file-local HDU index distinct. OCAM/WFI use
   explicitly documented qualified mappings with recorded source authority;
   EXTNAME or configured ordinal alone does not verify hardware identity.
   Bath may use a configured logical key such as `bath:detector-1`, explicitly
   physical-identity-unknown. Identical model/shape is not sufficient to identify
   detectors across unrelated cameras or files.
2. Optional selector presence is explicit: HDU index is nonnegative; EXTNAME
   and EXTVER are independently present/absent. Any supplied selectors must
   identify the same HDU; an absent card is not synthesized. The current
   `mef_image_ref` contract couples EXTNAME to positive EXTVER; retain its existing
   callers through an explicit adapter and introduce a reviewed extended layout
   descriptor, rather than silently changing the old sentinel meaning.
3. Record original dimensions, BITPIX, BSCALE/BZERO and unit evidence separately
   from decoded working-plane type/unit/correction state. Preserve source cards.
   No BUNIT means unknown at discovery; a later explicitly sourced input-unit
   declaration is required wherever numerical compatibility needs it.
4. Keep detector health, requested output selection and actual result status
   separate. Initial output order follows selected science bindings in original
   science-file HDU order; calibration order cannot reorder science. Excluded
   detectors retain IDs and positions in the selection/result records.
5. Normalization reference identity/context is separately declared. A detector
   omitted from output may still supply required reference data. Missing required
   context fails; do not select another detector, mean gain or normalization
   convention. A one-detector profile still explicitly states its normalization
   policy; it does not inherit mosaic mean-gain arithmetic by accident.
6. Bounds cover HDUs/cards/header bytes/dimensions and allocation multiplication.
   Nonstandard unrelated header cards must not silently erase otherwise readable
   selected metadata (the M3 #180 lesson). Invalid required fields or ambiguous
   identity are explicit failures before arithmetic, with retained diagnostics.

## Astrophotography profile review

Use existing authoring vocabulary where possible: proposed reduction-profile ID
`bath:astrophotography`, `purpose="visual"`. The current project schema accepts
`scientific` and `visual`; adding a new purpose enum is unnecessary. Keep the
ordered recipe and product profile independently identified. These are review
declarations, not a runnable validated project or an implementation of a profile
engine. Existing project execution remains disabled at this authoring boundary.

| Concern | Proposed Bath declaration / unresolved choice |
|---|---|
| Input layout | One explicitly mapped logical detector, primary HDU 0, full reported shape; independent calibration bindings |
| Readout | Preserve binning, camera GAIN/OFFSET and temperature evidence. Physical conversion/noise model and tolerances remain unqualified. No amplifier geometry invented. |
| Recipe | Explicit calibration steps/roles and correction state. Flat role declarations required; dark exposure/temperature applicability and bias-dark treatment need review before numerical use. |
| Scan/trim | No scan-region evidence was returned. Never invent scan columns. A confirmed no-scan mode must state no subtraction and an explicit active region; full-frame region is a proposal pending metadata/documentation review. |
| Colour/filter | Preserve Blue/Green/Red/Luminance labels as supplied passbands. No Gaia transformation, filter transmission curve, Bayer operation or RGB combination is inferred. |
| Normalization | Explicit reference and unit transitions; no automatic mean-gain/exposure normalization borrowed from OCAM |
| Cosmetic operations | No automatic interpolation, denoising, background removal, stretching or colour balancing from selecting visual purpose; future steps remain explicit and provenance-bearing |
| Products and uncertainty | Separate numerical FITS products from future display products. No ESO Phase 3 compliance claim. Required variance initialization/propagation stays at M6a for the new chain, also for visual purpose; earlier signal-only layout controls are explicitly variance-unavailable. |

The currently extracted `mef_cal_bias` rejects primary HDU 0. In addition,
`validate` computes scan_width from enabled prescan/overscan then rejects
`rejection[0] >= scan_width`; both scan flags disabled therefore fail even with
zero rejected samples. This is a source-observed limit of the initial CCD/MEF
service, not a reproduced Bath reduction failure. Removing only the primary-HDU
guard cannot establish a usable no-scan calibration workflow. Keep this visible
in #182/#12; review the existing correction/trim kernel before the applicable
service increment. No numerical bypass or replacement is implemented here.

## Owner addition: native speed and Windows design review

The [cross-cutting performance/portability contract](native-performance-portability-contract-2026-10-31.md)
requires preserving mefpp speed and efficiency during refactoring, with no
preapproved slowdown allowance. Prepare matched optimized serial comparisons when
this native boundary becomes executable; retain numerical equivalence, necessary
checks and input ownership. Record wall/CPU time, memory and I/O and distinguish
measurement noise from regressions. Earlier helper/test durations are not native
performance evidence. No benchmark is launched by this review amendment.

Keep layout discovery/identity validation at the I/O boundary and reuse its owned
immutable view. Avoid repeated header scans, unnecessary image copies/conversions
or OS/metadata calls in pixel loops. Current Windows obstacles are explicitly
registered at build, FITS mapping/swap/stream, path and optional dependency resource
boundaries. Do not expose POSIX paths/handles in the detector arithmetic contract.
Windows implementation remains at its original later stage; preserve efficient
Mac/Linux behavior while preparing the eventual adapters.

## Proposed bounded fixtures and gates

These are planned checks, not executed tests. Use small synthetic arrays for
arithmetic/ownership controls; retain observational data unchanged. Announce
exact called production functions, inputs/output paths and pass criteria before
implementation tests, with matching script comments per agent instructions.

| Fixture | Required result | Scope |
|---|---|---|
| Two/three detector science; differently shuffled bias/flat/BPM HDUs | Independent file bindings produce known identity-matched pixels and unchanged science order | Original M4 gate |
| Duplicate/missing/unknown IDs; index/name/version conflict; non-image target | Controlled diagnostic and no arithmetic/partial published product | Original M4 gate plus selector-presence cases |
| One detector stored in primary HDU, unnamed/named one-extension and mosaic member | Same decoded plane and same detector service result, supplied equivalent calibration/reference context | Original M4 gate; absent EXTVER is explicit |
| Unsigned-16 storage control including raw signed endpoints | BITPIX16/BSCALE1/BZERO32768 decodes exactly once to 0..65535; headers retain original meaning | M4 scaling gate; not a detector ADC/saturation claim |
| Selected subset, excluded reference detector | Stable IDs/order; qualified supplied reference retained, otherwise controlled failure | Original M4 normalization gate |
| Allocation/read/truncated payload failures | No transferred partial result, no source writes, balanced owners; valid next call succeeds | Changed C boundary ownership controls |
| Bath primary-header representatives: bias, dark, four lights and four declared flats | Actual header/layout binding and raw metadata preserved, explicit roles, unknown physical IDs/units retained | Additive real single-detector layout fixture, not CMOS science acceptance |
| Bath no-scan bias/science calibration workflow | Requires separately reviewed service readiness/configuration and applicable calibration/noise policies first | Later applicable service/chain gates; do not substitute for original M4 tiny controls |

For real layout tests select named representative files from the retained report,
including the -4.5 C exception as metadata rather than an automatic rejection.
Hash only selected required observational inputs before a later pixel test;
do not copy the full dataset or ZIP archives into git. Four unsampled headers
must be inspected before claiming complete dataset coverage, but need not delay
this interface review or tiny fixture preparation. No entire-dataset reduction
or new acceptance campaign is proposed.

## Review conclusion and next decision

The current foundation is suitable for the original M4 layout/identity increment,
with the above selector/scaling/ownership contracts made explicit. Include Bath
as real primary-image evidence alongside OCAM/WFI mappings and tiny synthetic
layout equivalence controls. It does not replace them or enlarge M4 into generic
CMOS, dark modeling or display processing qualification.

Owner review of the proposed interfaces, science-order output rule, configured
Bath logical identity and profile boundaries precedes C implementation. A first
implementation can discover/bind layouts and qualify tiny controls while retaining
the legacy adapter; full Bath calibration readiness must be reported separately.
No new compiler/dependency/installation or Stage 2/2.1 replay is needed for this
documentation review. Later changed C boundaries need focused agent C90/C17 and
appropriate ownership checks, then selected Mac and representative Chapman
qualification, preserving all prior evidence and working installations.

ESO OB start, template start and shutter-open exposure start remain distinct,
with their original IDs and authority. Grouping and calibration association
belong in Pycavi's general system (M8); mefpp receives selected lists and performs
basic compatibility checks. M5/M6 services, M6a variance, M7 persistence, M8
association, M9 execution and M10 binding keep their original sequence and gates.
