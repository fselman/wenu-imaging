# Acceptance tests by recipe

The primary acceptance suite is small, uses representative real observations,
and is organized by recipe. Its purpose is to show that a new installation or
software change preserves accepted products. It is not an exhaustive test of
every internal function or a requirement to add a test for every small bug.

## Cases and comparisons

| Recipe | Representative case | Required comparisons |
|---|---|---|
| Bias | Agreed OmegaCAM and WFI bias sets, declared BPM/median/measurement policies | Master pixels; detector/HDU mapping; essential FITS headers; ASDF input membership, QC and provenance |
| BPM | Agreed bias/flat calibration sets and mask policy | Mask pixels/reason bits, geometry, calibration identity and QC |
| Flat | Agreed filter/readout sets and accepted calibrations | Pixels, normalization, masks, detector coverage and QC |
| Science | A small agreed set of calibrated exposures per supported instrument | Reduced pixels, calibration use, exposure/units, WCS where applicable and QC |
| Full chain | A few fixed representative observing sequences | Inter-recipe dependencies and final images/catalogues, including agreed astrometric/photometric quantities |

Use at least one case per supported recipe/instrument. Choose additional modes
only for scientifically distinct behavior. The matrix is the target acceptance
contract: it does not claim that every row is already automated or qualified.

Keep raw inputs and accepted products read-only and outside the checkout. For
each case declare input/configuration identities, reference products, invocation,
expected outputs, allowed metadata differences and numerical tolerances. Use exact
comparison when behavior should be unchanged; agree tolerances before testing when
needed. Never refresh the baseline or widen tolerances just to pass a failure.

Run candidates in fresh product directories. Check zero exit, output completeness,
pixels, MEF structure, detector mapping, important headers and ASDF QC/provenance.
Compare numerical arrays and scientific metadata rather than whole FITS file bytes,
which can differ in agreed timestamps or checksums. Report differences explicitly.

File-based recipe tests run with the working directory set to orchestration.
Keep TOMLs, input lists and requests there; raw observations remain read-only in
raw. Products, logs, private work and execution receipts belong under reduced;
existing calibration dependencies remain read-only under reduced/cal. Synthetic
file-integration fixtures use this same separation. Pure numerical unit checks
may use in-memory arrays. The native linearity-preparation command case exercises
this layout with preserved input fingerprints and unchanged analytical expectations.

The public BPM/linearity contract is
`mefpp_recipe cal bpm-linearity --config RECIPE.toml [--qc true|false]`.
The native command must admit the recipe/project/settings/ordered inputs directly,
without a separate preparation command or generated-bindings prerequisite. The
current feature branch does not yet meet that interface; do not describe the
OCAM/WFI authoring templates as standalone runnable recipes before it does.
Project TOML owns roots and relative resolution; its directory is orchestration.
The recipe's `run` is relative to reduced. Controls remain in orchestration;
products, receipts, work and logs stay below their declared reduced roots.

Acceptance includes help with no files or processing: `mefpp --help`,
`mefpp_recipe cal --help`, and operation help for `bias`, `linearity` and
`bpm-linearity`. Help must identify inputs, options, defaults and outputs. Then
check direct recipe execution from orchestration, fresh-output refusal, input
preservation, supplied-mask skip, both QC modes, one ingest/correction per detector
plane, and independent FITS/ASDF comparison. Reuse passed saved-product evidence;
repeat numerical reductions only for affected behavior or unresolved differences.

The existing native `cal bpm` adapter can publish through the same C ASDF writer
as bias when built with the retained libasdf option. `--native-asdf` selects a
sidecar sharing the final FITS basename without downstream completion;
`--qc-record` remains available for retained controllers. Its primary BPM image
and diagnostic HDUs are preserved. Typed common QC retains original input/HDU
order, participation and available/unavailable statistics; the complete existing
native BPM context is embedded in ASDF. Primary-image QC is explicit and limited
to one detector, while the MEF mapping contract remains unchanged.

`native_bpm_product_qc` checks actual native results on generated FITS, including
excluded frames, reason-bit/binary/omitted priors, MAD off and immutable inputs.
The optional `bpm_native_asdf_probe` and `bpm_native_qc_contract.py --asdf-python
... --adapter ...` additionally exercise the existing library writer and production
CLI with an independent reader. Focused native ASDF and supplied-mask CCD65
checks have passed on Mac; standalone native admission and new controls still
require their affected gates. The retained-cache Mac
qualification helper is `tools/qualify-bpm-native-qc-mac.py`; it refuses unknown
cached source edits, restores source/cache/adapter before testing private candidates,
and leaves the selected bias producer and launchers unchanged.

## When to run

- A recipe change: affected recipe cases and dependent cases when appropriate.
- A shared processing change: affected recipes/instruments plus the relevant chain.
- A new installation: the complete supported primary suite and a few chain cases.
- A documentation-only change: relevant link/dependency checks, no reduction replay.

Retain a limited set of cheap focused checks where they protect important behavior
that representative data miss (for example median conventions, detector mapping,
no-clobber or a meaningful failure boundary). Small helper fixes do not automatically
need a permanent test. Existing focused tests remain available; running every old
qualification matrix is not the default acceptance procedure.

## Current coverage

The native bias recipe has passed the selected Mac synthetic FITS/ASDF gate and
has a read-only real-product comparator:
[`tools/compare-bias-products.py`](../tools/compare-bias-products.py). Earlier actual
OmegaCAM/WFI comparisons are recorded in issues/PRs. The representative full-chain
references include OmegaCAM CP Pup/CN Ori and WFI Trapezium work; these names alone
do not define a reproducible automated suite. The first
[OmegaCAM bias case](../tests/acceptance/bias/omegacam.toml) records host-confirmed
configuration hashes, ordered-input-list identity, the average-median reference
and selected executable. The selected Mac candidate completed all 32 detectors
with zero exit and passed the reference comparison: exact pixels, no added QC
cards, ASDF schema/configuration and product/input QC mapping. Comparison used
the corrected own-product identity handling; checked files remained unchanged.
This is a real-data regression result for this case, not independent validation
of every scientific estimator.

The owner accepted the [WFI bias case](../tests/acceptance/bias/wfi.toml).
The same executable completed all eight detectors with WFI configuration only;
the average-median product passed ASDF schema, exact recipe snapshot, ordered
input membership and FITS/QC mapping checks. A diagnostic changing only the even
median convention to `lower` reproduced every pixel of the retained WFI master
exactly, explaining the differences from the average-median product. Keep these
two conventions distinct: the retained master is a lower-median pixel reference,
not an average-median or historical-QC reference. Its older provenance lacks the
configuration snapshot needed by the current full comparator. Content
fingerprints and historical WFI QC equivalence remain open.

Use issue/PR summaries for results: what ran, which executable/configuration,
pass/fail and material differences. Routine build logs, per-attempt receipts and
historical replay scripts do not belong in permanent documentation.

New bias recipes default to MAD off. Explicit `mad = true` remains an opt-in;
the archived acceptance configurations retain their recorded measurement policy.
Clipped RON follows its separate settings. With MAD off, MAD scatter/RON and
MAD-based hot-pixel diagnostics are explicitly unavailable, not zero.
