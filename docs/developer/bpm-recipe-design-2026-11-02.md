# BPM recipe design for review — version 1.0

2 November 2026. Source baseline: f42b7507d170a36ef67c171c12a0a0e2f6f3d246.
**Design only: no BPM implementation, numerical change, test execution or
installation is authorized by publication of this document.** Fernando requested
adapting `mef_build_bpm` to the new template and reviewing the final design first.

## 1. Purpose and proposed scope

Extract the existing BPM construction into a callable, owned-result operation
and one complete command, using the same native operation template and common
ASDF QC/completion path as bias. Preserve the existing response-fitting and
thresholding algorithms. An existing-BPM load is a calibration selection, not
an alternative meaning of the create command.

The first increment handles one explicitly selected detector per invocation,
with raw primary-image or independently mapped MEF inputs, equivalent complete
PAF/TOML settings, and an explicitly selected or omitted master bias/prior BPM.
No image discovery, brightness sorting, exposure-time normalization, automatic
frame selection, mosaic assembly, new threshold model, variance propagation or
automatic two-pass bias/BPM workflow is included. Raw input order is preserved.
A prior BPM never substitutes for actually computing a new mask.

## 2. What the existing code actually does

| Existing stage/resource | Behavior to retain |
|---|---|
| `mef_build_bpm`, mefp_lib.c:2546–2904 | Load cube; scan-correct and trim; optionally subtract the selected bias; choose configured fit; normalize response; threshold; write mask and provenance |
| `mef_cube_overscan_correction` / `mef_overscan_correction` | Configured scan regions and low/high sample rejection; detector BPM is not applicable to electronic scan samples |
| `cube_sub_im` | Subtract the already selected active-area master bias, without gain conversion |
| `cube_create_gainmap_robust`, detector.c:79 | For each frame compute its active-plane median; fit each pixel against those medians with the existing slope-plus-intercept fitter; return three images |
| `cube_create_gainmap_proportional`, detector.c:184 | Use the same frame-median reference; compute median(pixel/reference) for a zero-intercept response; return two images |
| `image_normalize(..., NORM_MEAN)` | Divide the fitted response by its arithmetic mean, retaining current pixel precision/order and the existing zero-mean guard |
| `image_threshold2pixelmap` | Good iff lower < normalized response < upper; equality at either boundary is bad; Eclipse polarity 1=good, 0=bad |

The fit abscissa is measured frame intensity, not EXPTIME. Input sequence need
not be sorted or monotonically illuminated. The quantity called gain here is
**relative pixel response**, dimensionless; it is not an electrons/ADU gain
measurement. Both current OmegaCAM/WFI configurations select robust fitting.
Their existing response intervals are respectively (0.5,1.5) and (0.5,2.0).
These are existing settings to preserve, not newly proposed detector limits.

The legacy constructor mixes calculation and FITS side effects. Calling it whole
inside a calculate callback would write a file too early. Its numerical body
must therefore be extracted once into a shared kernel used by BOTH the legacy
entry and the new typed service. Do not copy the algorithm into a second recipe.
Keep the old public entry's behavior, including legacy publication, during migration.

## 3. Three decisions proposed for review

### A. Prior BPM: use it for reference measurements, still test every pixel

Recommendation: when a prior BPM is explicitly supplied, use its good active
pixels for frame-reference medians, response normalization and applicable QC.
Still fit and classify every detector pixel, including previously bad pixels.
Do not erase/interpolate them or force the new output mask to inherit old flags.
Save old/new transitions for review: good→good, good→bad, bad→good, bad→bad.
With no prior BPM, use all active pixels as the present builder does.

This implements the owner's preference to use available BPMs in measurements
without preventing detection or reassessment of defects. It changes reference
selection when a mask excludes pixels and therefore needs explicit acceptance.
It does NOT silently AND old/new masks; permanent inheritance is a separate policy.

Reference fitting medians must retain the legacy order-statistic convention,
including even samples. An all-good prior mask must reproduce omission exactly.
Use existing `image_getstats_opts` semantics for the masked reference median;
QC's separately labelled checked mean/median/stdev/MAD remains as reviewed for
bias. Do not silently substitute QC's averaged-even median in the fit reference.
The initial reference region remains the whole active plane, not the flat
normalization rectangle or a new implicit ROI.

### B. Master bias: preserve explicit omission for robust; require it for proportional

Recommendation: robust mode accepts an explicitly selected master bias or
explicit omission, preserving the current useful intercept-fitting route.
Proportional mode requires a selected matching master bias in this initial raw-
input interface, because its zero-intercept model assumes bias has been removed.
This is a proposed admission restriction: the old function permits NULL in both
modes. Do not implement it without review. An already corrected-input route would
need its own explicit correction/geometry contract and is outside this first scope.

The request records selected/omitted bias distinctly; there is no PAF filename
fallback or automatic dependency construction. A supplied bias must describe the
same detector, readout, binning, active geometry and ADU scale. It is already an
active-area calibration and must not be scan-corrected or trimmed again.

### C. Minimum/degenerate inputs: fail explicitly instead of inventing a fit

Recommendation: at least three raw illumination frames. The legacy gain-map
constructors do not enforce this minimum, so this is a proposed new admission
rule, not an existing guarantee. Robust fits additionally need nonzero reference
intensity leverage; proportional fits need usable nonzero reference intensities.
Reference values must be finite; do not silently drop a zero-level frame or use
the proportional fitter's 1e30 placeholder as an acceptable calibration result.

No new minimum level-span, saturation, clipping or residual cutoff is proposed.
Save intensity range/counts for review. Fail a whole attempt on unusable
reference selection, nonfinite calculation or normalization failure. Do not
silently create an all-good/all-bad product. A valid, fully computed all-bad mask
from configured thresholds is different: retain it with its actual QC counts.

## 4. Native operation and ownership

Proposed internal names follow bias: `mef_cal_bpm`, `mef_bpm_input`,
`mef_bpm_result`, `mef_bpm_from_files`, `mef_bpm_files_execute`, and
`mef_bpm_result_destroy`. Names/signatures remain proposals, not an installed ABI.
Use existing `MEF_OP_CAL_BPM` and resolved calibration roles; distinguish prior
input BPM from the newly generated output. No new generic scientific dispatcher.

| Template phase | Concrete BPM responsibility |
|---|---|
| Validate | Explicit inputs/calibration choices, config fit mode/thresholds, one detector, independent physical HDU/config index/output ordinal, units/readout/binning/geometry, finite parameters and required metadata; reject conflicts before pixels where possible |
| Load | Reuse M4 layout/binding/plane loader and explicit BPM loader; own temporary handles; input paths/order remain immutable; no raw staging copies |
| Calculate | Copy working planes; scan-correct/trim using existing rejection; subtract optional selected bias; fit using existing Eclipse maths; normalize and threshold; collect pending typed result/QC; no disk output |
| Publish | Build one mask MEF and shared QC records; exclusive new destinations, checked writes/close/padding; transfer result only after requested native publication succeeds |
| Cleanup | Release partial temporary cubes/images/headers on every path; never borrowed input/config/calibration owners; no deletion of completed earlier products |
| Complete command | Same native→common-ASDF→verified-links sequence as bias; phase-aware receipt; success only after every required output verifies |

The result owns the binary mask, normalized response, mode-appropriate intercept
and fit diagnostic, copied request/configuration origin and ordered QC records.
Keep these image owners reusable through the C API; do not discard diagnostics
immediately as the legacy caller does. Initial command publishes the mask FITS
and QC summaries, not automatic full-size response/intercept/residual images.
Additional diagnostic image products would require explicit output paths/scope.

Robust and proportional outputs have different shapes: three versus two image
pointers. Preserve #90's corrected cleanup and expose named result views so a
caller cannot confuse the proportional residual with an intercept. Missing
intercept is unavailable, not a zero-valued image. Outputs/errors start NULL;
failed calls transfer no partial result. Caller-owned arrays remain unchanged.
Generic Eclipse globals remain serial/non-reentrant; no new threading claim.

## 5. Existing resources and genuinely missing extensions

No new regression/normalization/threshold algorithm is needed. Two small generic
Eclipse extensions are proposed for review before implementation:

1. **Checked, optionally BPM-aware gain-map entry** in detector.c/header. Factor
   the existing constructors' shared scaffolding so it can compute masked
   reference medians while calling the same `fit_slope_robust`/`fit_proportional`.
   Preserve the unmasked arithmetic/median order and both historical APIs.
   Return reference levels and explicit result count/ownership; validate shape,
   usable levels and allocation/nonfinite failures; leave outputs unchanged on
   error. Do not implement a second fitter or new per-pixel rejection method.
2. **Status-returning pixelmap writer** in pixelmaps.c/header, based on the
   existing writer. Write the same unsigned 8-bit mask/padding, using borrowed
   explicit headers and explicit create/append intent; report every header,
   byte-write, padding and close failure. Keep the old void entry compatible.

The second gap matters: `pixelmap_dump` is void and cannot establish successful
publication. Bias's `mef_hdrpix_dump` explicitly ignores its bpp argument and
writes BPP_DEFAULT, so passing 8 there would NOT produce the required 8-bit BPM.
Reuse/extract checked output scaffolding where applicable; do not publish a
float mask while claiming BITPIX8 or copy an unchecked writer into the recipe.

BPM-aware normalization can compose existing Eclipse checked mean selection and
`image_cst_op`; it needs no new numerical loop. With no prior mask, preserve the
existing `image_normalize(NORM_MEAN)` path. An all-good prior mask must yield the
same denominator, conversions and output. Reject zero valid reference pixels
without silently reverting to the full image.

Any necessary allocation guards stay scoped to reached helpers and get their
own meaningful failure checks. This is not a broad #144 allocator repair or a
claim of whole-library OOM safety.

## 6. QC quantities, applicability and ASDF

Use `QcRecipe`, the existing schema, writer, reference traversal and completion
receipt. Add a BPM quantity catalogue/adapter, not another serializer. Factor
shared descriptor assembly from bias only where the second real caller needs it;
keep operation-specific definitions separate.

| Quantity/stage | Units and definition |
|---|---|
| Input active raw / scan-corrected / bias-subtracted levels | ADU; labelled mean/median/sample stdev and optional scaled MAD; explicit regions, counts and prior-BPM applicability |
| Scan raw samples and existing row-correction profile | ADU; separate definitions as in bias; detector BPM not applicable |
| Fit reference intensity per original frame | ADU; exact legacy-median convention and selected sample count; preserve input index |
| Fitted and normalized response summaries | Dimensionless; original scale/normalization denominator retained; unmasked and prior-good diagnostics distinguish selection |
| Robust intercept | ADU; only when that model supplies it |
| Robust fit diagnostic | Mean absolute residual in ADU, with an explicit fallback state for the legacy -1 sentinel |
| Proportional fit diagnostic | Mean squared residual in ADU², not variance propagation |
| Final mask counts/fraction | Counts/dimensionless fraction over ALL active pixels; 1=good, 0=bad; strict threshold endpoints recorded |
| Prior/new mask transitions | Counts and optional explicit locations; unavailable when no prior mask exists; no forced inheritance |

The robust metric is NOT the squared error described by several existing comments;
actual `robust_linear_fit` returns average absolute residual and a -1 fallback
sentinel. Proportional mode returns squared residual/N. This source documentation
mismatch is tracked in #224. Do not give them one shared metric name/unit, relabel
the robust diagnostic as MAD, or automatically turn a fallback into a new masking
criterion. Preserve the legacy fitted response/classification while recording it.

A zero robust residual is a valid exact fit. A -1 fallback is an algorithm state,
not a negative measured residual. Do not summarize sentinel values as good data.
This does not add a residual-based rejection threshold. Optional MAD is a QC
choice and does not replace either legacy fitting algorithm.

Final-good-only statistics must never be the sole characterization: keep whole-
response diagnostics and defect counts so a newly generated mask cannot conceal
the defects it just detected. A prior BPM can select reference/QC samples while
all response pixels still receive a fit and output classification.

Per-raw-input and product ASDF files retain file/detector/HDU/configuration/
producer identities, effective parameters, stage/method/counts, original order
and participation. Product references freeze raw assessments plus selected bias
and prior BPM calibration records with explicit roles. Distinguish verified
existing calibration QC from binding-only metadata; do not claim to have
regenerated or scientifically assessed a selected calibration. Keep .asdf naming,
no-overwrite/conflict checks, offline traversal and explicit unavailable states.
Large diagnostic arrays are not silently embedded in scalar QC records.

## 7. FITS publication and provenance lessons

The product is one active-area 8-bit binary mask extension with an empty primary,
BUNIT=mask and explicit 1=good/0=bad semantics, consistent with the current BPM
consumer. Primary-image input and selected MEF input use the same mapping contract.
A primary with no source EXTNAME must not acquire a fictitious source selector;
a configured output name is a product identity, not evidence of an input card.

Physical HDU, zero-based configuration index and output ordinal remain separate.
Reuse the qualified bias header construction approach, factoring a genuinely
shared construction helper if needed. Do not reuse the old header-delete/index
pattern or assume deleted qfits header counts are correct (#212). All qfits
hierarchical names/prefixes use full HIERARCH names (#223); provenance cards store
bounded basenames, not long paths (#125/#126). Full locations stay in request/QC.

Record actual selected geometry, bias correction and fit/normalization/threshold
settings. Preserve appropriate configured legacy product metadata and compare
matching detector coverage. New explicit BUNIT/polarity cards are declared
metadata differences, not ignored wholesale. No inherited flat/science timestamps,
fabricated acquisition metadata or Phase3 compliance claim. Existing creation-
identity/time limitations remain #207; an exclusive output path is the commit
guarantee, not assumed timestamp uniqueness.

Retain the bias pattern: temporary output assembly in the final directory,
checked completion, then exclusive publication. The one-command operation reports
failure if later ASDF or reference verification fails, retaining completed earlier
files and truthful phase evidence. No automatic retry, cleanup of completed
products, or multi-file atomic transaction is promised.

## 8. Focused acceptance after design approval

No functional tests run for this design. Proposed C17/Mac checks are:

| Control | Independent pass criterion |
|---|---|
| Existing behavior | Both modes and admitted optional-bias routes against the frozen pre-extraction builder/component baseline for the same selected detector; proposed admission changes are tested as explicit rejections, not numerical equivalence; exact response/mask pixels for unmasked compatibility and declared metadata differences only |
| Known response | Synthetic illumination levels with known pixel slopes/intercepts and below/equal/inside/above threshold cases; independently compute expected classification, normalization and fit diagnostics |
| Prior BPM | All-good equals omission exactly; one contaminated reference pixel is excluded from reference measurements, yet still fitted/classified; report all four mask transitions; no valid reference samples fails without fallback |
| Input/configuration | PAF/TOML stored-bit equivalence; missing/incompatible bias/prior BPM, wrong HDU/readout/binning/geometry, finite/degenerate levels, primary/extension/scaled-integer inputs and input immutability |
| Ownership/output | Two/three-map ownership, partial allocation cleanup, returned owners outlive context, checked 8-bit output, failed writes/close, existing file/symlink, no partial success |
| QC/completion | Correct units, fallback/unavailable states, frozen raw+bias+BPM links and locations, independent ASDF/FITS reads, successful complete command and late QC failure retaining completed FITS |

Use existing BPM synthetic scaffolding and retained relevant memory/provenance
lessons; do not restart the completed BPM memory campaign. An exact legacy
comparison must not accidentally compare two wrappers that call the same newly
extracted code; retain a frozen reference/qualified pre-change binary and
independent known answers. Primary inputs unsupported by the old API compare
against known answers and an equivalent explicit MEF reference, not an unsafe
xtnum0 invocation. Preserve the already qualified bias evidence; run only affected
shared checks if implementation actually changes a shared boundary.

Peak memory includes original raw planes AND working trimmed planes, master bias,
prior/result masks, fitted/normalized response/intercept/metric and statistics
scratch. A planning bound is approximately B*F*(R+P)+B*R+6*B*P+2*D*P+3*P+O(F),
where F=frames, R/P=raw/active pixels, B=sizeof(pixelvalue), D=sizeof(double).
This deliberately budgets coexisting owners rather than one output plane; qfits
registrations/process overhead/headroom are additional. Review against actual
Mac memory before a full-size job. Tiny acceptance fixtures stay on the Mac;
no automatic C90/Chapman/performance matrix or real-observation processing.

## 9. Review and implementation sequence

Please review A/B/C above: prior-BPM use without forced inheritance, the bias
requirement for proportional fitting, and the proposed three-frame minimum/
degeneracy policy. Their recommendations are not adopted by this document.
The two proposed Eclipse extensions and their error/ownership contracts are also
presented before implementation, as required by the reuse policy.

After acceptance: extract/share the existing numerical body; add the typed
operation and explicit file/calibration adapters; add the reviewed checked
Eclipse boundaries; connect BPM QC and complete publication through the existing
template. Deliver a coherent recipe increment and focused checks, not a replacement
BPM algorithm or automatic two-pass workflow. No engine activation, install,
merge or unrelated library repair follows merely from accepting this design.
