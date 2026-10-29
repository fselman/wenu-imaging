# Optional input BPMs and required variance support

Owner direction, 29 October 2026, after accepted/merged PR #140:
permit an input bad-pixel map to be omitted throughout the processing chain;
do not make variance processing optional when it is introduced at M6a.

This records the contract for the next implementation increments. It does not
change today's production wrappers or engine, activate a new reduction mode, or
claim that mask-free operation has been qualified. Baseline source:
`6a4d4d8ec078a3360a5a743845dcbe752cbc84bd`; Mac/shared Chapman are clean there.

## Different responsibilities

An input BPM identifies detector defects according to a selected calibration.
It is separate from an operation's generated validity/rejection/saturation flags
and from pixel variance. Omitting a BPM must not disable existing pixel rejection,
saturation checks, invalid arithmetic handling or result validation. It does not
assert that every pixel is good or that variance is zero.

| Input state | Required behavior |
|---|---|
| BPM explicitly omitted | Continue without input-BPM masking; retain the decision and report no BPM applied |
| BPM explicitly selected | Resolve and validate it before use; retain exact identity and detector coverage |
| Selected BPM missing, unreadable or incompatible | Fail the affected operation; never downgrade silently to omitted |
| BPM validated, operation not yet executed | Report selected/validated, not applied |
| BPM creation explicitly requested | Require a valid BPM output on success; an input BPM is not a prerequisite for creating the first BPM |

Absence must be an explicit request/association state, not inferred from a
missing file, empty string, broken symlink or a failed load. A configured default
path is a selection until explicitly omitted; legacy PAF defaults must not
silently defeat the choice or turn a failed selected input into omission.
Exact CLI/TOML spellings and C field layouts are settled in their implementing
increments. Do not overload a filename sentinel such as "none".

Validate a supplied BPM's selected detector identities, dimensions, geometry,
HDU selectors and declared pixel/mask convention against the images it will
serve. Missing coverage is an error unless an explicit per-detector omission
was frozen in the request. Different detectors or exposures may have different
selections, but no partially applied map may be reported as full coverage.
Do not substitute extension ordinal for detector identity.

Generated quality/validity masks can still be required by a particular operation.
They are not an implicit all-good replacement for an omitted calibration BPM.
An output BPM produced by mef_cal_bpm is also distinct from an input BPM used
while constructing another calibration.

## Scope across the chain

| Layer or stage | Required allowance and record |
|---|---|
| M1 request/context/result and first extracted operation | Carry selected/omitted input-BPM state and actual application outcome; keep explicit ownership, errors and success-only handoff |
| M2 TOML/PAF adapters | Preserve explicit omission and selection through precedence resolution; do not discover a default mask after omission |
| M3 paths and project inspector | Omission is not a missing dependency; a broken selected reference is. Show BPM status and variance capability separately |
| M4 detector/layout layer | Resolve supplied mask coverage independently; permit explicit detector omission; retain internally generated validity information |
| M5 calibration builders, including bias and BPM | Permit construction without a pre-existing BPM; preserve algorithms in supplied-BPM equivalence cases and qualify new no-BPM paths |
| M5a qc | Record which BPM, if any, a metric used. A metric with a genuinely mask-dependent definition is unavailable or unsupported under its declared contract; never invent an all-good measurement or silent estimator switch |
| M6 science processing and product writer | No unconditional BPM read/link/header reference when omitted; retain generated flags and provenance; supplied invalid BPM fails |
| M6a variance and M6b–M6d new calibrations | Optional BPM does not disable uncertainty initialization, propagation, calibration uncertainty or validity handling |
| M7 WAD/ASDF plan/run/product | Persist omission, selection, coverage, actual outcome and uncertainty source; do not emit a dangling FITS selector or invented BPM identity |
| M8 partition/association notebook 01 | Permit groups without a BPM association and do not create mandatory BPM links or construction tasks merely to proceed |
| M9 reduction notebook 03 | Pass the same frozen choice to native work; no copying/checking a nonexistent omitted BPM |
| Later Python stages and M10 mefppy | Consume the same state; omit input-BPM masking when requested while preserving required variance and generated validity/weight rules |

Optional input BPM support applies to all owner-selected services:
mef_cal_bias, mef_cal_bpm, mef_cal_dark, mef_cal_fringes, mef_cal_linearity,
mef_cal_domeff, mef_cal_skyff, mef_cal_mff and mef_sci_pp. This does not make
other calibration inputs optional, change scientific association policy, or
guarantee that each external program already supports the requested mode.

## Variances: later, but required

M1–M6 legacy equivalence work can still run without newly implemented variances.
Those products must be labelled variance unavailable/legacy; this does not
postpone M6a or qualify a completed variance-capable chain.

From M6a onward, the new chain must create and propagate variance for supported
signal-bearing science and calibration images. A raw exposure need not already
contain a variance plane: a declared, qualified initialization model can provide
it using explicit gain/RON, units and noise assumptions. This is distinct from
silently skipping variance. If neither valid supplied variance nor the required
model/parameters is available, fail before claiming a complete uncertainty result.

No normal variance-off mode belongs in the new variance-capable chain. Historical
signal-only execution may remain an explicitly separate compatibility/reference
path for extraction comparisons; it cannot pass that chain's completion gate.
A missing, malformed or incompatible selected variance cannot become zero,
an all-one weight, a fabricated plane, or an optional-BPM-style omission.

Propagate calibration uncertainty, normalization and response effects with
declared squared units, validity and correlation/approximation limits. Invalid
pixels must be explicitly flagged; do not invent their uncertainties. An inverse
variance weight is a derived representation with stated conventions, not a
substitute for an unknown uncertainty model.

A boolean/integer BPM is not itself a signal plane requiring a meaningless
"variance of the mask". Linearity/model coefficients and QC measurements need
their appropriate uncertainty contracts, rather than automatically attaching a
pixel-variance plane to every record. Exact estimators and covariance support
remain separate numerical decisions at their recorded milestones.

WCS header-only correction preserves variance arrays; actual resampling and
fringe subtraction must propagate their uncertainties under the later declared
contracts. Unsupported propagation must be explicit, not reported as complete.

## Source observations at the baseline

These are source observations, not executed no-BPM reductions or newly corrected
defects:

- `Pycavi2/pycavi/pycavi/pycavi_associate_reduction.py`:
  PartitionsTree.link_bpm raises when no BPM partition exists (lines 240–260).
  check_mef_bpm raises on a missing/broken path (973–1022). The bias/dome/sky/science
  wrappers call that check unconditionally (1044, 1098, 1156, 1233) and include
  BPM availability in launch conditions. This must become conditional on the
  explicit selection when those paths are adapted, not a broad caught exception.
- `mefpp2/ins/mef/recipes/mefpp.c`: BPM discovery/reading occurs at 582–608
  and construction/reading at 691–778; parts are conditional, but this is not
  proof that the entire engine supports omission. Default discovery and later
  header references must be traced before a no-BPM operation is connected.
- `mef_runtime.h/.c`: current M1 descriptors allow zero calibration references
  and perform metadata copying only; they have no typed BPM/variance roles.
  mef_execute remains unsupported. Accepting a descriptor without calibrations
  is not proof of mask-free numerical processing.
- The implementation plan's former M6a variance-disabled compatibility wording
  is superseded for the new chain by this owner decision. Keep old baseline
  products and frozen historical evidence unchanged.

## Bounded implementation gates

At each affected increment, qualify both omission and valid supplied-BPM cases;
retain legacy supplied-BPM equivalence. Negative controls include explicit
missing/unreadable BPM, wrong dimensions/detector/HDU mapping and partial
coverage. Confirm no fallback, no reads/links/tasks for omitted BPM and truthful
per-detector outcome/provenance. Repeating all historical reductions is not a
prerequisite.

Before M6a completion, qualify initialization from an explicit model versus
supplied variance, propagation with and without a BPM, required missing-noise
failure, invalid variance, squared-unit mapping, masks, shared uncertainties
and exactly-once normalization. A variance-off request must not yield a complete
new-chain product. Define analytic expected values before those numerical tests.

QC absence and generated validity are checked independently from BPM selection.
CLI, notebooks and later mefppy must agree on the same choices. Use fresh tiny
fixtures and existing selected Mac/representative Chapman tools at the
implementing stage; no tool requalification or production reruns for this
documentation update.

## Current delivery and next work

This update changes documentation/contracts only. Review consisted of tracing
the baseline source boundaries and reconciling the target, milestones, template
guidance and WAD text. No C/Python behavior, package, schema, parser or notebook
was changed; no runtime/ASDF/FITS/variance/no-BPM test is claimed.

Proceed with the M1 resolved-operation bridge and first concrete operation,
carrying this policy from their design onward. Do not add a temporary mandatory
BPM or variance-off convention that later stages would have to undo.
