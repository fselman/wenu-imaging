# BPM polarity and reason-byte impact audit — 7 November 2026

## Finding

Owner requested a whole bundled Eclipse/mefpp review before extending bias
sigma-clipping and selectable BPM polarity. This is a static source audit only,
pinned to merged main de3c5f3c29d792b57569beaf154fe088e47c0ba5. No production
code, defaults, products, configurations, builds or installations were changed.

The required zero-good 8-bit reason representation ALREADY EXISTS in modern
mefpp BPM and linearity services. The standalone bias recipe currently uses a
strict binary-only path and does not expose it. Extend/reuse the reason-byte
boundary rather than inventing a competing representation or reversing every
Eclipse pixelmap. Earlier discussion of bpm_good_value described the bias
recipe's binary path, not the capabilities of all mefpp services.

There are three distinct contracts:

| Object | Existing meaning | Preservation rule |
|---|---|---|
| Legacy external BPM | zero excluded; any nonzero becomes selected in pixelmap_load/ext | Preserve existing behavior unless a caller explicitly selects another encoding |
| Modern binary external BPM | only physical 0/1 allowed; explicit binary_good_value 0 or 1 | Reject nonbinary values; normalize to selection |
| REASON8 external/internal reason array | 0 means no detected reasons; 1..255 encode one or more reasons | Preserve exact unsigned bytes and bit registry; do not binarize the authoritative array |
| Eclipse pixelmap / selection / validity map | binary 1=selected/usable/foreground, 0=excluded/background | This is an algorithmic Boolean mask, not a reason-byte BPM |

For a reason mask F and explicit reject bits R, existing code computes

    selected[p] = ((F[p] & R) == 0)

R=255 rejects every nonzero reason byte and makes external zero the only
accepted value. Selecting fewer bits can deliberately accept a nonzero byte
whose flags are ignored; zero then means no reasons, not guaranteed measured
coverage or valid calibration. Fit/coverage and other selections are combined
separately. This distinction already exists in the BPM service and publication.

## Search coverage and limits

Production C/header search indexed 52 files with literal pixelmap/binpix/
PIXELMAP references and 24 additional mask policy/metadata/reason files (76
total). The reproducible keyword expression, matching line numbers and full
file SHA256 values are in evidence/bpm-polarity-impact-2026-11-07/source-inventory.json.
Load/save call sites and direct zero/one, truth-value and bitwise consumers were
then inspected by family below. This is not an assertion that 76 files all
need edits, nor a runtime coverage proof. Tests were searched for existing
contracts but no tests/builds/reductions were executed for this audit.

qfits5 was separately searched: no pixelmap/BPM semantic references found;
it transports headers/data and should not choose mask polarity. ins/pfits has
BPM product/category names without pixel-value interpretation. Python/Pycavi
callers and external installed Eclipse versions are outside this C-source audit;
their declarations must be considered when changing a public format/default.

## External loading boundaries — where changes belong

| File / functions | Source behavior | Needed for zero-good reason BPMs |
|---|---|---|
| src/iproc/pixelmaps.c: pixelmap_load, pixelmap_loadext | Integer FITS loaded as an image; only zero is set to excluded; all nonzero values map to 1. Reasons are irreversibly lost in returned map. | Do not feed REASON8 here. Add/select an explicit reason-aware load path at the caller; retain legacy loader behavior for old callers. |
| ins/mef/common/mef_layout.c: mef_layout_load_bpm | Requires good_value in {0,1}, integer HDU and every physical pixel exactly 0 or 1; converts chosen good value to 1. | Binary zero-good already supported. For reason bytes reuse a separate exact-byte path, or add a new explicitly typed loader; do not merely relax the binary validation. |
| src/iproc/pixelmap_flags8.c/.h | Exact 0..255 conversion, exact-byte FITS reader/writer, explicit reject_bits-to-selection helper. | Reuse. Loader currently requires BITPIX=8, unity physical scaling, MASKENC=REASON8 and matching MASKREG. Arbitrary old files lacking this metadata are not silently accepted. |
| ins/mef/recipes/mefpp_bias_recipe.c | Validates bpm-good-value (0|1), calls binary layout loader, embeds active mask if necessary, passes normalized selection to service. | Expose encoding/registry/reject bits, load exact reason bytes, preserve them and derive the Boolean selection. Keep geometry/extension checks. |
| ins/mef/common/mef_bias_recipe_config.c/.h and config/recipes/omegacam-bias.example.toml | TOML expands binary good-value/HDU/coordinates into current parser. Example uses good=1. | Add explicit input mask encoding/policy and validate mutually exclusive binary polarity versus reason-bit fields. Keep external recipe call short. Do not silently reinterpret existing configs. |
| ins/mef/recipes/mefpp_bias_adapter.c | Earlier single-detector adapter also calls binary layout loader. | Needs the same option if that adapter is to accept reason masks; otherwise explicitly retain binary-only contract. |
| ins/mef/recipes/mefpp.c | Legacy all-in-one engine directly calls pixelmap_loadext for existing BPM. | Must select reason-aware loader/normalization here before legacy flat/correction consumers can use a zero-good reason BPM. Standalone bias changes alone do not upgrade this engine. |
| src/jitter/jcalib.c; src/main/deadpix.c; src/main/stcube.c | Independently call legacy pixelmap_load. | Explicit encoding option/conversion required if these standalone programs must accept the new files. They do not inherit bias recipe options. |

## Existing reason-aware paths — reuse, do not duplicate

- src/iproc/pixelmap_flags8.c: pixelmap_flags8_from_image_checked validates
  exact physical integers in 0..255. pixelmap_flags8_load_checked validates
  header encoding/registry and loads the chosen HDU without legacy binarization.
  pixelmap_flags8_selection_checked makes a separate normalized selection and
  updates its selected-pixel count. pixelmap_flags8_write_checked preserves
  exact bytes with explicit REASON8/registry cards.
- ins/mef/common/mef_bpm_files.c/.h already branches on binary versus FLAGS8,
  preserving the prior reason array and correctly cropping raw/active geometry.
- ins/mef/common/mef_cal_bpm.c/.h preserves prior flags, ORs compatible new
  reasons into a separate combined array, derives rejection-bit selections,
  and combines them with numeric-fit coverage and prior selection. A zero
  reason byte does not imply a usable fit exists.
- src/iproc/detector_response.c/.h produces separate validity/sample maps and
  unsigned reason bytes (e.g. response bits 4 and 8). These are deliberately
  different data objects; do not invert the validity maps when adopting
  zero-good reason bytes.
- ins/mef/common/mef_linearity_files.c/.h and mef_linearity_raw_files.c/.h
  already load BINARY or REASON8 explicitly. mef_linearity_pairs.c,
  mef_linearity_samples.c and mef_linearity_prepare.c choose either
  `(flags[p] & reject_bits)==0` or normalized binary selection==1.
- ins/mef/common/mef_measure_plan_internal.h and the mefpp_pair_measure.c,
  mefpp_sample_extract.c and mefpp_linearity_prepare.c entry points carry
  mask_encoding/good_value/mask_registry/reject_bits. Preserve this existing
  contract and naming consistency when extending bias.
- ins/mef/recipes/mefpp_bpm_adapter.c already exposes --bpm-encoding
  (reason8|binary|omitted), registry, reject bits and binary polarity.

## Algorithmic consumers — no reversal when input is normalized

| Family | Important files / behavior | Consequence of changing internal good to 0 |
|---|---|---|
| Statistics / RON | src/iproc/image_stats.c/.h: both value/median passes skip zero; checked masks accept only 0/1 and collect samples where 1. src/iproc/detector.c combines valid selections and computes pair statistics. | Would reverse sample population, counts and pair-mask intersection. No edit needed when exact raw flags are first converted to selection. |
| Bias service and stack | ins/mef/common/mef_cal_bias.c/.h validates binary masks, derives raw/active masks; mef_bias_kernel.c/.h uses them for frame means and master QC. | Could change frame admission and scientific master results, not just RON. Keep normalized selection and legacy numerics unchanged. |
| Electronic scans and flats | ins/mef/common/mefp_lib.c/.h: masked overscan accepts selection==1; mef_image_filter_flat uses neighboring pixels where mask==1. | Would select defects for scans/filtering. Convert once before entering these algorithms. |
| Repair | src/iproc/dead_pixels.c/.h: image_clean_deadpix copies pixels with mask==1 and replaces others using neighbors with mask==1. cube_arith.c/.h dispatches cube repair. | Would preserve defects and replace good pixels. Keep normalized internal mask. |
| Response and linearity | detector_response.c/.h, detector_joint.h; mef_cal_bpm.c; mef_linearity_pairs/samples/prepare | Binary 1 means valid measurement/selection, distinct from reason byte. Their existing reason8 branch already has external zero-good behavior. |
| Generic map operations | src/iproc/pixelmaps.c/.h and src/include/local_types.h: new maps initialize to all 1, ngoodpix counts selected/nonzero binary pixels, update intersects acceptance, AND combines selections, NOT complements masks, clipping/morphology/crop/shift preserve binary semantics. | A macro swap is insufficient: memset, counts, truth tests and bitwise operations encode literal Boolean values. AND of good selections corresponds to OR of bad-flag sets, so the data types must stay distinct. |
| Object/geometry maps | src/iproc/detect_ks.c, detect_sq.c, intimage.c; generate.c; slitposition.c; src/spectro/spectro_arcs.c, spectro_detect.c; src/main/imgen.c, thresh.c | Here 1 marks foreground/detected/inside shape, not a bad-pixel code. Global reversal would alter detections, connected components, geometry and morphology unrelated to BPM. |

## Output boundaries and QC metadata

- Legacy pixelmap_dump writes normalized binary data and good/bad counts.
  mefp_lib.c:mef_build_bpm constructs in-range-good response selection using
  image_threshold2pixelmap and writes it through this path. src/main/flat.c
  and deadpix.c likewise generate binary selections. Keep their established
  output encoding unless a new output format is explicitly selected.
- mef_bpm_publish.c already publishes exact REASON8 bytes with MASKREG and
  BPMZERO=no_detected_reasons, while SELECTION/PRIORSEL carry SELGOOD=1.
  COVERAGE has its own 0/1/2 meanings. These extensions are not interchangeable.
- Bias QC currently publishes bpm.good_value as a scalar recipe parameter in
  mef_bias_product_qc.c/.h, with declaration/mapping in mef_bias_qc_fits.def,
  mef_bias_qc_fits.c and native ASDF validator/schema. Extending reason masks
  requires explicit encoding/reject bits/registry provenance, not pretending
  a multibit mask is the old binary good_value=0 option. Full flags stay in
  the referenced BPM product; the algorithmic selection must be recorded as
  derived, not substituted for original reasons.
- Update file option/result headers and relevant fixtures/contracts together.
  Existing layout, flags, BPM and linearity tests already cover binary and
  reason-byte branches; extend them for bias and any selected legacy front end.
  This audit did not rerun those gates or qualify a new implementation.

## Immediate modification boundary

1. Specify an explicit mask encoding/polarity/reject-bit contract, retaining
   existing binary calls and using reason8 with reject_bits=255 for the owner's
   zero-good/any-nonzero-bad 8-bit case. Define any needed explicit adapter for
   external reason files lacking native registry/header metadata; do not guess.
2. Reuse exact flags8 loading/selection helpers in the standalone bias file
   boundary; expose corresponding processing TOML fields and retain source
   bytes/HDU/geometry/registry provenance. Binary good=0 remains binary only.
3. Pass only derived binary acceptance masks into existing Eclipse statistics,
   overscan, stacking and repair. Sigma-clipping gets its own temporary rejection
   selection; it must not overwrite the BPM reason bytes or conflate reason bits
   with statistically rejected pixels.
4. Add an explicit adapter at legacy mefpp.c loading if full legacy-engine
   interoperability is wanted now. Jitter/deadpix/stcube are separate consumers;
   either extend their explicit loading options or document them as binary-only.
5. Update QC FITS/ASDF encoding metadata and tests. Test 0,1,2,4,128,255 and
   combined reasons; both binary polarities; selected/ignored reject bits;
   prior-plus-new reasons, coverage exclusions, active/raw coordinates and
   exact unchanged legacy numerical output. Preserve raw/product/evidence files
   and reuse the selected existing C17 build only after implementation approval.

No global inversion of PIXELMAP_0/PIXELMAP_1, no change of generic foreground
semantics, and no automatic replacement/reinterpretation of retained binary BPMs
is required to support the owner's external zero-good reason-mask convention.

## Complete indexed file list

The accompanying source-inventory.json is the complete 76-file static index,
including matching lines and hashes. It is more precise than a claim that every
occurrence is a physical BPM use. Algorithmic maps, reason arrays, format
boundaries and incidental request/category metadata are distinguished above.
