# M3 processing-stage inspector completion — candidate, 31 October 2026

Subsequent [paired inspector qualification](m3-inspector-stages-paired-results-2026-10-31.md)
passed 21/21 on both actual hosts at 0d8f2978a4ef4c78c47f1526b48e03d77351c024.
The [final cumulative review](m3-final-closure-review-2026-10-31.md) recommends M3
closure pending owner acceptance. Earlier gap/target-pending statements below
retain their original baseline context. No M4 implementation starts here.

Owner authorized completing the remaining original M3 inspector boundary after
the [cumulative review](m3-cumulative-review-2026-10-31.md), before M4 review.
Refs #159 and new test-only #179. Based on PR #178 review head
`70321b6958d0459812f199eba9e169c6c362c8f3`, accepted native baseline main
`3a61df627edfdbb1ef43cc3c956dff74bd28c066`.

**Implemented and agent-qualified: 21/21 focused groups. Actual selected Intel
Mac and representative Chapman qualification remains pending. Keep M3/#159 open
until those results and the cumulative closure decision.** No native code,
scientific arithmetic, grouping/association policy or installation is changed.

## Views and authority

`inspect_project` now returns bounded `stages` in addition to its unchanged legacy
membership/link/header evidence. The table shows calibration roles, per-exposure
preprocessing, normalization and WCS records. `--stage` selects these roles;
`--exposure PATH` selects one resolved input path, including its raw membership
and derived stage rows. Columns include role, relationship and completion state.

| Evidence | Meaning and limit |
|---|---|
| Symlink in a partition | Declared reference, including a broken link; role comes from unambiguous producer list role or product-category cards, not nearest-time calibration selection |
| Product category in a primary header | Reported product role, not independent validation; conflicting category/producer evidence is diagnosed without choosing a winner |
| Raw list member -> `_pre.fits` and WCS location | Expected legacy location only, explicitly `identity_verified=false`; an existing candidate is not proof it was produced from that member |
| Normalization | Shares the preprocessed file because existing Pycavi updates it in place. Primary BUNIT/ONEADU are retained evidence; expected unit is reported, not proof of correct scaling or exactly-once processing |
| WCS candidate | Existing headers are shown, not a new astrometric/solver validation; even a plausible name/header does not certify solved detectors |
| Logs and toreduce markers | Partition-scoped uninterpreted attempt evidence, never an exposure-specific successful/published result |
| No selected calibration evidence | Explicit not-declared/unresolved state; omitted BPM is not made mandatory and no selection is invented |

All legacy stage completion remains unknown, validation not established and
publication unknown in the absence of independently qualified result evidence.
This explicitly distinguishes expected/unbuilt, unavailable, conflicting and
existing-unverified locations without fabricating validated/published records.
M7 will supply durable ProcessingProject/result records; no new receipt format or
project store is added merely to make a legacy inspection claim completion.

Distinct input paths with the same product stem are ambiguous: no exposure gets
an arbitrarily chosen product. Relative members without an original base retain
unknown paths. Unsupported compressed/non-FITS input conventions are not guessed.
Stage records, header access and assets use explicit limits and report truncation.
Shared canonical assets remain deduplicated; membership/link edges remain ordered.

## Reuse rather than a second reduction implementation

New `pycavi_product_paths.py` contains pure legacy product-location conventions
and the existing normalized-unit literal. The production normalization routine
uses that shared literal; `run_py4_solve` and `create_wcs_frame` use the shared
WCS location helper. Their scientific calculations, metadata routines, output
bases and overwrite behavior are unchanged. Native preprocessing naming is
traced to the existing C writer, not a new C implementation.

`pycavi_inspection_stages.py` composes the existing inspector's bounded list/link
and header records. It does not instantiate PartitionsTree, choose calibrations,
call the reduction wrappers, import their heavy dependencies, run a solver or
infer ESO OB/template grouping. Original exposure, OB and template times/IDs are
read-only metadata; none is substituted for another.

## Agent verification and preserved failure

The extended [focused contract](../../Pycavi2/tests/project_inspection_contract.py)
retains the original 15 groups and adds six groups for missing/existing stages,
shared/unbuilt calibration links, category conflicts, ambiguous inputs, exposure
views, limits and existing-client equivalence. Inspector-only tests trap pixel
access and check bytes/modes/mtimes/cwd and unrelated-caller agreement.

The client equivalence group executes actual original and updated
`mefpp_normalize_science`/`create_wcs_frame` function bodies against tiny synthetic
float32 detectors, using existing science metadata routines. Exact output arrays
and relevant FITS cards agree; generated checksum cards are excluded. Original
function bodies are retained unchanged from accepted main 3a61df6 in a test-only
fixture with provenance. This is not a replacement scientific algorithm, full
installed-package import, solver execution or observational qualification.

Initial run: 20/21 passed; #179 records the new expected-array oracle's integer
promotion, before updated-client comparison completed. Correcting the expected
ramp to float32 preserves exact equality; no production arithmetic/tolerance
changed. Corrected suite passed 21/21; final category/default-view changes passed
21/21 in 3.237 s. Existing private agent Python/NumPy/Astropy were reused, with
niceness10 and bounded numerical threads; no installation occurred.

[Retained logs, receipts and source hashes](fixtures/agent-m3-inspector-stages-2026-10-31/README.md)
include the failed attempt and both passing attempts. Target gates remain open;
agent results do not establish actual Mac/Chapman behavior.

## One bounded actual-host campaign

Use selected imaging Python on the actual Intel Mac first, then representative
shared Chapman4. Keep user checkouts clean on main. Fetch this exact branch/head
and export a git archive into a fresh retained build directory; do not install or
switch the configured package/engine. Run
`Pycavi2/tests/qualify_inspection_stages.py` from that export at niceness10.

The standard-library host runner guards OS/hostname/root/origins, clean main and
upstream, selected interpreter/prefix and exact export source identities. It
discovers the actual installed nested reduction module through package search
locations and reads the actual configured engine using ConfigParser with
interpolation disabled. Before/after hashes/modes/mtimes protect that module,
engine/configuration and checkout on success and test failure. It retains
tests.log, the suite's private fixtures and run-provenance.json. No C build,
native/solver launch, observational read or historical matrix is needed.

After both 21-group target receipts pass, update the cumulative M3 review against
the original checklist. Owner acceptance precedes merge/cleanup. Only then close
M3 and proceed to the already prepared original M4 detector/layout review. Existing
#23/#24/#116/#125/#128 and unrelated backlog retain their separate scope.
