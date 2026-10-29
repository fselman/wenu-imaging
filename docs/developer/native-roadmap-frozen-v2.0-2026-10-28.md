# Frozen native roadmap v2.0 — 28 October 2026

Owner: Fernando Selman. Project: `fselman/wenu-imaging`.
Baseline: merged main `b0061b55b9ff8dc2d185c3c403c5119a25b606a5`.
Status: frozen proposal prepared at Fernando's request; execution awaits acceptance
of this concrete plan. This publication authorizes no processing or merge.

## 1. Freeze and authority

Fernando requested an immutable roadmap after two days of incremental BPM work.
This version replaces the execution rules of native roadmap v1.6 and the old
S2-00–S2-11 matrix where they conflict with the simplifications below. The earlier
scientific requirements and accepted evidence remain valid.

Once published, **never edit this file in place**. Its companion SHA256 identifies
its exact bytes. A change needs Fernando's explicit agreement and a separately
numbered amendment identifying the changed row, reason, cost and effect on closure.
Finding another possible test combination is not such agreement. Progress belongs
in the separate fixed-row ledger, not in this frozen contract. The agent cannot
add prerequisites, reopen accepted work, increase counts, change order or extend
the correction budget on its own.

This freeze prevents scope drift; it does not turn an observed failure into a pass.
An actual blocker produces a bounded decision report, not indefinite qualification.

## 2. What is already accepted

Preserve the existing serial build/install, tool controls, context/parser/split
checks, numerical/shared-normalization references, and inspected BPM ownership,
metadata, supplied-bias and two-extension OmegaCAM/WFI evidence. PR #117 is merged;
both user hosts are clean on the baseline above. No new BPM-only campaign is planned.

Old accepted tests are reused rather than rerun to refresh dates or documentation.
#116 remains unresolved/non-reproduced. #75/full Stage 2 is not yet complete.
Existing archives, supplements, transfer copies, installations and raw data remain
unchanged. Actual WFI files at `/Users/fselman/Pictures/WFI` have not been inventoried.

## 3. Simplified platform and language policy

- **Mac C17 is the main functional and memory-diagnostic lane.** Build the current
  production allocator configuration with ASan/UBSan, and a separate uninstrumented
  build for the qualified Mac external leak tool. These are two diagnostic runs
  of one integrated workflow, not separate calibration projects.
- **C89/C90 source compatibility is retained.** Perform one C90 compile/build at
  the final stable native-code checkpoint; no duplicated C90 functional or memory
  matrix. If native source is unchanged, existing accepted C90 evidence is sufficient.
- **Chapman3 gets one compact C17 combined-workflow regression at Stage 2 closure.**
  Verify GCC/Linux build, exact products, ownership/accounting and error status.
  No raw-WFI dataset transfer and no duplication of the Mac diagnostic matrix.
  Later target reruns require a relevant portability change or a milestone boundary.
- Compatible external memory diagnostics on Chapman3 remain an explicitly recorded
  limitation, **not a requirement to repeat the Mac suite or a prerequisite for
  completing the declared Mac-led Stage 2 campaign**. Do not claim target external
  memory qualification. A GNU/Linux-specific observed failure remains a blocker.
- Do not upgrade libraries, compilers, allocators or engines as hidden prerequisites.
  Existing qualified tool controls stand unless their actual configuration changes.

These are explicit amendments to the earlier two-language/two-host repetition
policy and target external-diagnostic exit gate; they are not claims that the old
missing target diagnostics have been supplied.

## 4. One input lock, then one finite Stage 2 campaign

**One read-only inventory and fixture/reference preparation pass.** Fix exactly:

A. One tiny synthetic OmegaCAM dataset with two distinguishable extensions,
   exercising bias, BPM, dome, sky and combined-flat construction, plus one science
   application. Declare expected arrays/headers and shared-normalization invariants.
   Reuse the retained numerical fixtures wherever applicable.
B. One representative WFI dataset selected from the Mac raw collection: one
   coherent filter/binning/readout group, all eight detector extensions and the
   minimum frame counts required by the unchanged recipe settings. Lock bias,
   BPM/linearity, dome, sky and one science-exposure list. This is a representative
   regression, not full-field scientific or Phase 3 validation.

Record exact file identities, configuration, output/reference definitions and
comparison rules **before diagnostic processing**. Use an isolated ordinary C17
control from the same frozen source when an accepted observational reference is
absent; it checks instrumentation equivalence, not independent scientific truth.
Synthetic known-answer expectations supply the independent numerical checks.
No retrospective tolerance changes are permitted.

Use one selected configuration per dataset. Reuse the accepted robust/proportional BPM evidence; do not create another regression-mode cross-product. Fixture A retains its declared synthetic thresholds; dataset B retains its frozen project configuration. Do not tune observational settings to reproduce synthetic masks.

Missing essential inputs produce one explicit missing-input report. Stop that
blocked dataset; do not search indefinitely, invent calibration substitutes,
change thresholds or silently substitute another dataset. A substitute needs a
recorded owner decision, not another automatically expanding campaign.

### Fixed execution matrix

| ID | Workload | New native launches at most | Completion requirement |
|---|---|---:|---|
| F1 | Tiny OmegaCAM integrated workflow: ordinary C17 control, ASan/UBSan, separate external-leaks lane | 3 | All calibration products and one science result meet declared expectations; lifetimes and diagnostics pass |
| F2 | Selected WFI integrated workflow: the same three lanes | 3 | Same product/ownership checks; correct eight-detector mapping and unchanged control products |
| F3 | Five fixed failures on the tiny fixture, each under ASan/UBSan and external leaks | 10 | Truthful failure, acquired resources released, protected files preserved; no unexplained diagnostic |
| F4 | Tiny integrated workflow repeated in one C17 instrumented process after one fixed warmup; observe completed cycles 1, 2 and 10 | 1 | No unexplained per-cycle live allocation/mapping/descriptor growth, stale ownership or numerical drift |
| F5 | Compact C17 Chapman3 integrated regression using fixture A | 1 | Exact Mac reference products; target build/status/ownership/accounting checks pass |

**Total: at most 18 planned native test launches**, including controls and failure
runs, excluding compilation and qualified evidence reused from earlier work.
A launch may process the full recipe sequence; F4 is one process containing its
warmup and ten measured cycles. Do not repeat the raw WFI workflow ten times.
Use a fresh context and separate output location for each measured tiny-fixture cycle; account for any intentionally persistent state at the same cleaned boundary.

The five F3 failures are fixed: missing calibration list; corrupt selected frame;
blocked output publication; one early context-allocation failure; one allocation
failure while constructing an intermediate cube/image. Reuse already accepted
checks when they meet the exact contract. Injection is test-only, scoped to the
selected allocations and recorded before running; no exhaustive allocation sweep.

F1/F2 use the real existing `mef_engine` sequence: for each selected extension,
bias → BPM → dome → sky → combined master flat, with the science application in
the same invocation where supported by the existing recipe. This is an observation
harness around current behavior, not a new calibration implementation. Overlapping
S2-05/06/07 evidence is collected together. F3/F4 cover the scheduled failure/repeat
rows; they do not become new prerequisites before the integrated run can begin.

## 5. Memory and output pass criteria

Observe before/after stage boundaries, extension completion, final context cleanup
and two controlled qfits cache purges. Keep the original pre-purge state. Account
for deliberately live bias/flat/mask objects between stages: **zero is required
only at declared fully cleaned boundaries**, not while products are still owned.

Require legal ownership and release, no ASan/UBSan findings, zero external leaks
on the exercised Mac lanes, stable unexplained-resource counts/descriptors and
zero tracked resources at the declared final purge boundaries. Explain any cache
retention explicitly. RSS alone is not the leak test. Compare every declared
product and retain the common mosaic normalization, existing units, mask semantics,
thresholds and metadata contracts. Preserve the existing numerical algorithms.

F4 measures a fixed cleaned boundary after each cycle; retain actual allocations,
bytes, mappings, swap and descriptor identities at cycles 1/2/10. No growth is
hidden by process exit. General large-file mmap/swap stress and every possible
allocator fallback are outside this finite campaign; state the limits honestly.
The controlled cache/mapping checks satisfy the declared bounded S2-10 scope.

Repeat installed-wrapper propagation only if a correction changes its exit/cwd
contract (conditional S2-11). That contingency must be reported before it runs;
it is not permission to restart wrapper or notebook qualification wholesale.

## 6. Hard stop, repair budget and final decision

- One preparation pass, with a **one working-day engineering-effort checkpoint**.
  If the inventory/harness cannot be made ready within that effort budget, stop
  and report the concrete obstacle and smallest choice. This is an effort limit,
  not a promise about raw-data runtime or time awaiting user input.
- Execute the fixed campaign once. Retain one consolidated report/archive for the
  campaign; inspect its numerical and diagnostic evidence together. Stop dependent
  cases on an actual failure; preserve failed attempts.
- Permit **at most two correction/retest rounds for the entire Stage 2 milestone**.
  Repair only demonstrated defects in the declared paths; rerun affected failed
  rows and one relevant successful workflow smoke check. Do not repeat the whole
  matrix after each local change. Maintain defect tickets and exact provenance.
- After that budget, deliver one final table: each fixed row accepted, blocked or
  reused with its evidence; named remaining defects; platform limitations; and
  a recommendation. No third repair round, new matrix or silent scope extension.
- #116 gets one explicit disposition at that final review: attributed/resolved
  with evidence, or still open with a concrete decision requested. No further
  blind descriptor-reproduction campaigns. It is never silently closed or waived.
- Stage 2 closes only when the declared rows pass and blockers are resolved, or
  Fernando explicitly accepts named residual limitations. Otherwise report
  **blocked**, with the exact decision required. Do not call blocked work complete.

An untested Cartesian combination, a new compiler warning, another filter or an
extra possible detector permutation does not automatically block closure. A
confirmed defect directly affecting a declared result does. Broader findings
are recorded separately without absorbing their implementation into this campaign.

## 7. Remaining roadmap: fixed order and handoffs

| Stage | Finite deliverable and handoff |
|---|---|
| Current Stage 2 | The fixed F1–F5 campaign and one final owner review above |
| Stage 2 exit review | Present accepted evidence, named defects/limitations and one concise official ESO Phase 3 requirements/gap matrix; obtain Fernando's decision before Stage 2A/extraction |
| 2A | One format/representation decision report: preserve FITS ingestion/export, define the data contract and recommend retain/adopt; no backend prototype or migration without a separate decision |
| 3 | Extract existing behavior behind explicit component/ownership contracts, preserving serial numerical and shared-normalization references |
| 4A | Detector/calibration characterization: response/BPM, gain/RON, linearity, shutter and required dark/fringe methods with provenance |
| 4B | Calibration/science variance creation and propagation |
| 4C | Verified mask/weight propagation through downstream tool interfaces |
| 4D | Final-product uncertainty through extraction/resampling/coaddition/photometry, with explicit covariance approximations |
| 5 | Dedicated single-detector CCD qualification |
| 6 / optional 6A | Safe single-node mosaic parallelism; accelerator assessment only if profiling and an explicit decision justify it |
| 7 | Native Apple Silicon, Ubuntu and Windows build/install/runtime qualification; no Rosetta/WSL substitution for native acceptance |
| 8 | CMOS readout/noise review and separately qualified services |

The urgent scientific goal remains validated OmegaCAM products for ESO Phase 3.
The broader Python workflow/distribution backlog and optional capabilities remain
recorded future work; they are not prerequisites added to the current memory gate.
The brief Stage 2 exit requirements matrix is not the full Stage 2A observatory/
format study and does not authorize variance/profile/backend implementation early.

At each later handoff, define its concrete implementation checklist once, before
execution, within the deliverable above. No later stage starts merely because this
whole-program roadmap exists. Additional scientific policies, features, formats,
profiling projects or platforms need explicit owner agreement.

## 8. Delivery overhead and amendment rules

Explain each workload once, with matching script comments, declared inputs and
pass criteria. A single campaign can have per-stage checkpoints and one report;
it does not need a PR, archive transfer or user confirmation per calibration.
Keep detailed evidence durable and hash-verified; use compact receipts/indexes
rather than repeatedly copying identical large reports. Preserve earlier evidence.

Documentation-only PRs are reviewed on GitHub. **No Mac/Chapman synchronization,
rebuild, reinstall or acceptance rerun is required merely to review a document.**
Keep the user checkouts on clean main; synchronize once after an authorized merge,
or before native execution when the delivered source actually needs it. Give one
complete guarded command group at a time for real host mutations. Preserve the
existing explicit merge/branch-deletion approval rule.

The agent must not turn this version into another living document. Its only
future changes are separate, explicitly approved, numbered amendments. Changing a
status in the fixed-row progress ledger does not amend scope or prove acceptance.
