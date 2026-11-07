# Bias scalar QC in FITS and ASDF — proposed mapping v1

Status: owner accepted the mapping and instructed implementation, 6 November
2026. Native implementation is prepared; actual Mac qualification is pending.
The owner approved retaining legacy FITS QC and adding new scalar diagnostics
to both formats. Existing products remain unchanged.

## Evidence and scope

The completed real mosaic CMDP.2026-11-06T19:22:15.014Z.001 has 32 detectors and
ten embedded raw inputs. Owner-run read-only checks found:

- All 864 legacy keyword groups (27 per detector) exactly match the retained
  reference masters indexed by linearity-bias-batch-05ijf_sx/masters.json.
- All 704 corresponding FITS/ASDF comparisons agree within the legacy FITS
  six-decimal rounding interval.
- These checks establish metadata agreement, not independent pixel equivalence.

Use the existing measurement records from mef_bias_product_qc.c as the common
source. Do not recalculate statistics for either serialization. Preserve legacy
cards, their values, comments, selection and six-decimal formatting. Additive
cards must never relabel legacy statistics as BPM-selected statistics.

## Naming and identification

All keyword names in the tables omit the leading HIERARCH. New diagnostic
keywords use the prefix `ESO MPP QC`. Proposed extension-level `ESO MPP QC MAPVER`
is the string `bias-scalar/1`. It identifies this mapping, independently of the
ASDF schema version. Detector identity remains `ESO DET CHIP ID`; HDU order is
not identity. A mapping change that alters a keyword's meaning requires a new
mapping version.

Definitions shared by a sample group are encoded once per group. Per-input
groups use `FRAMEiii`, where iii is original_index + 1, padded to at least three
digits. This matches the legacy input order and does not renumber accepted
frames after rejection. The mapping must accept more than three digits without
truncation or collisions; field-length preflight remains required.

## Existing cards preserved

| FITS keyword | Existing ASDF source |
|---|---|
| ESO MPP QC FRMEDIAN | legacy.product_median |
| ESO MPP QC FRSTDEV | legacy.product_stdev |
| ESO MPP BIAS AVG1 | legacy.frame_mean_average |
| ESO MPP BIAS SIG1 | legacy.frame_mean_sigma |
| ESO MPP BIAS FRMTHRLO | legacy.rejection_low |
| ESO MPP BIAS FRMTHRHI | legacy.rejection_high |
| ESO MPP BIAS KAPPA1 | Existing effective rejection setting |
| ESO MPP QC FRAMEiii SCAN MEDIAN | Input scan_correction.median |
| ESO MPP QC FRAMEiii SCAN STDEV | Input scan_correction.stdev |

`ESO MPP BIAS` is the retained OmegaCAM configured prefix, not a new hard-coded
replacement for the configurable legacy prefix. KAPPA1 is already in FITS and
the effective configuration; adding a named ASDF scalar for it needs an explicit
additive schema review, rather than assuming it already exists among measurements.

## Statistical group expansion

For every row below, expand all eight suffixes in the next table.

| FITS group after ESO MPP QC | ASDF measurement prefix | Record scope |
|---|---|---|
| MAST | master | Product detector |
| UMAS | master_unmasked | Product detector |
| DIFF | raw_difference | Product detector |
| FRAMEiii RAW | raw_active | Embedded input detector |
| FRAMEiii CORR | corrected_active | Embedded input detector |
| FRAMEiii PRES | prescan | Embedded input detector |
| FRAMEiii OVER | overscan | Embedded input detector |

| FITS suffix | ASDF suffix | Unit / definition |
|---|---|---|
| MEAN | mean | ADU; arithmetic mean |
| MED | median | ADU; averaged central pair for even sample count |
| STD | stdev | ADU; sample standard deviation, denominator n-1 |
| SMAD | scaled_mad | ADU; 1.4826 times median absolute deviation |
| NPIX | region_pixels | count; pixels in region |
| NBPM | bpm_excluded | count; BPM exclusions |
| NNF | nonfinite_excluded | count; nonfinite exclusions |
| NVAL | valid_pixels | count; admitted finite pixels |

MAST and UMAS retain their actual sample definitions; MAST is not assumed to
have a BPM if none was supplied. PRES and OVER are scan samples, with BPM not
applicable. DIFF is the specified raw pair before corrections. No clipping or
different dispersion estimator is introduced.

## Other scalar measurements

All FITS names below follow `ESO MPP QC `.

| FITS name | ASDF measurement | Unit |
|---|---|---|
| RON STD | read_noise | ADU |
| RON MAD | read_noise.mad | ADU |
| HOT N | pixels.hot | count |
| HOT THR | pixels.hot.threshold | ADU |
| HOT K | pixels.hot.sigma | dimensionless |
| HOT DEGEN | pixels.hot.threshold_degenerate | count, existing 0/1 flag |
| REQ MAD | recipe.mad_requested | count, existing 0/1 flag |
| REQ PAIR | recipe.ron_pair_requested | count, existing 0/1 flag |
| BPM GOOD | bpm.good_value | count |
| BPM ACTIVE | bpm.active_coordinates | count, existing 0/1 flag |
| VAR | variance | ADU2; presently unavailable |
| FRAMEiii SCAN PRES | scan_correction.prescan_used | count, existing 0/1 flag |
| FRAMEiii SCAN OVER | scan_correction.overscan_used | count, existing 0/1 flag |
| FRAMEiii SCAN NLO | scan_correction.rejected_low | count; configured row rejection |
| FRAMEiii SCAN NHI | scan_correction.rejected_high | count; configured row rejection |

RON STD = sample stdev(raw difference)/sqrt(2); RON MAD =
1.4826 MAD(raw difference)/sqrt(2), with the same recorded pair and mask.
HOT N counts all master pixels above the threshold derived from the selected
master median plus HOT K times its scaled MAD. Its count is an unmasked
diagnostic when a BPM is supplied; it is not a count restricted to good pixels.
HOT THR uses the actual recorded mask definition. Keep the existing degenerate
threshold flag. Do not infer it from rounded values.

## Context, states and harvesting

- Each new scalar key K has companion `K S`, with `measured` or `unavailable`,
  matching the ASDF status. For unavailable values, omit K and add `K R` with
  a versioned compact reason code. Zero is a valid measurement, never a sentinel.
  Reason codes expand to the exact ASDF reason strings. Unexpected nonfinite
  measured values are a serialization error, not silently changed to unavailable.
- Existing legacy cards remain untouched. Their known measured semantics come
  from the mapping; no legacy reformatting is needed for this proposal.
- Group context records actual stage, mask policy, mask record ID, region bounds,
  coordinate convention and sample counts. Units and methods fixed by this
  version are defined in the mapping; any variable method needs a context code.
  Use compact context suffixes STG, MASK, BPMID, X1, X2, Y1, Y2, COORD and NSAMP.
  The schema source orders bounds as x1,x2,y1,y2; the writer must copy actual
  values and never infer them from output image dimensions.
- RON context explicitly refers to DIFF; HOT N/THR have separate mask/sample
  context where their definitions differ. Sharing context is allowed only when
  all relevant definition fields are equal.
- Each FRAMEiii has ID = embedded record_id, HDU = actual source HDU, USE = used
  or rejected, and WHY = a compact rejection reason when rejected. Add detector
  CONFIG, BINX, BINY and READID context and RON I1/I2 original input indices.
  A rejected stacking input can still be a deliberately selected RON pair member;
  harvesting must preserve these separate roles.
- The mapping implementation must enumerate context and reason codes in a
  machine-readable registry. Long readout IDs, reasons, paths and header-length
  limits require preflight; no truncation is allowed. Full paths, configuration
  snapshots and ancestry remain in ASDF. FITS includes a same-product ASDF
  basename link and product identifier, with matching ASDF product identity.
- Every scalar is emitted from the same existing record with enough significant
  decimal digits to round-trip its stored binary64 value. Counts and 0/1 flags
  remain integral. New values must use a legal exponent spelling accepted by the
  FITS reader. Legacy six-decimal fields keep their established precision.
- Arrays pixels.hot.x and pixels.hot.y remain ASDF-only. An empty coordinate set
  is not equivalent to unavailable hot-pixel counting. Absence of a mapping
  version means legacy-only: never manufacture missing modern measurements.
- Harvested ASDF is a derived diagnostic record, with provenance identifying
  FITS-header extraction and any unavailable original context. It is not claimed
  to reproduce the complete original ASDF, its arrays or ancestry.

The implemented registry is `mefpp2/ins/mef/common/mef_bias_qc_fits.def`.
It enumerates every mapped measurement and exact stage/method/reason code.
Sample groups share region/stage/mask/source context; each scalar additionally
records NSAMP, UNIT and METHOD when present. Other scalars carry their own
context. Clipping=none and nonfinite=excluded are fixed by this mapping and
verified before serialization. The emitted FITS product link uses the basename
of the original absolute ASDF product identity. All new card lengths are
preflighted against the actual qfits rendering, including its 29-column minimum
keyword padding and doubled quotes. A selected field that cannot fit is refused.
The native probe can emit eight complete example headers; the focused Mac gate
parses those exact bytes independently with Astropy.

## Native integration and focused acceptance

The coordinator currently writes temporary per-detector FITS products before
final ASDF assembly. Adapt the metadata-writing boundary so each completed
detector's common measurement record supplies its additive FITS cards and the
final ASDF representation before its arrays are released. Reuse existing native
header, QC and MEF assembly facilities; do not patch published products or add a
second statistics pass. Retain exclusive publication/failure preservation.

Acceptance must check legacy cards and image payloads unchanged; complete scalar
mapping in both outputs; round-trip precision; optional MAD/pair/BPM omissions;
zero versus unavailable; rejected-input/RON independence; hot-count mask context;
field-length refusal; and FITS-only harvesting with honest missing-context status.
Use the retained tiny fixtures rather than rerunning real masters during design.
Actual Mac qualification follows implementation. Existing raw data, reference
masters and the completed mosaic stay untouched.
