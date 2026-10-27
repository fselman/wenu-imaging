# Stage 2 memory and ownership qualification — 27 October 2026

Status: preparation and source inventory; no new diagnostic workload has run.
Baseline: merged main e29a6201f01200708dc55c3439434a640cdc9ed0.
Tracking: #75 (context ownership / broader memory gate), #74 where applicable;
completed bounded repair #90. This plan implements the agreed Stage 2 sequence
in roadmap revision 1.6; it does not change that sequence.

## Current position and boundary

PRs #93/#95 integrated calibration/normalization evidence and regression tests.
PR #96 repaired the proportional BPM cleanup and preserved inspected Mac and
Chapman3 evidence. Both user checkouts are clean on the baseline main; the
associated merged branch was deleted on GitHub and both hosts. All evidence
archives/run directories and working installations remain preserved.

The bounded serial build/install and calibration/science comparison records form
the regression baseline, not universal platform/scientific certification.
#90 is closed. #75 remains open: the earlier context-owner correction was merged
and has functional failure-path acceptance, but the declared ownership/leak
suite is not complete. Do not treat its original duplicate-destruction finding
as a new uncorrected source finding without checking the merged implementation.
#91 mask/weight propagation and #13 BPM integration remain separate open work.

This change prepares the matrix and reconciles status only. No numerical,
allocator, CMake, Pycavi, configuration, installation or scientific default change
is part of this delivery. Subsequent execution must stay within the rows below,
use Mac development first and unchanged deliverable verification on Chapman3,
and preserve the 0.5–1.5 BPM bounds and shared mosaic normalization.
Do not start representation prototypes, extraction, new calibration algorithms,
mask/weight adapter implementation, package upgrades or production reprocessing.

## Initial ownership inventory

Source observations at the baseline; this is not a complete ownership proof.
An intended owner must be checked against every success/error/repeat path before
it is accepted. Unpaired allocations found during that work require a distinct
existing/new defect ticket and a bounded reproducer, not an unrelated refactor.

| Object / boundary | Observed source / intended lifetime | Qualification still required |
|---|---|---|
| Published mef_bb | mefpp.c main calls mef_bb_load, borrows it into mef_engine, then calls mef_bb_del once | Verify every engine return and nested failure preserves that owner |
| Unpublished mef_bb | mef_bb_new_from_paf uses zero-initialized construction and fail cleanup; parser rejects options before publishing | Early/late failure and allocation failures must release only initialized members |
| Context members | mefp_lib.c mef_bb_del releases configuration strings, CCD and statistics arrays | Field-by-field construction/reassignment/destruction map; account for aliases and per-element arrays |
| Images | src/iproc/image_handling.c image_del frees data then structure | Distinguish owned images from borrowed views/planes; reject duplicate destruction |
| Cubes and planes | cube_handling.c distinguishes cube_del, cube_del_contents and cube_del_shallow | Trace plane adoption/replacement and partial cubes; do not mix full/shallow destruction |
| BPM regression results | detector.c robust producer returns three images; proportional producer returns two; mef_build_bpm now releases the valid entries | #90 bounded checks accepted; repeated calls, other failures and temporary headers/lists still need Stage 2 coverage |
| Returned calibration/BPM products | mef_build_cal, mef_build_bpm and mef_ff_combine return objects consumed by recipe/driver | Trace ownership transfer on success, NULL/error paths and replacement |
| Frame lists | src/iproc/framelist.c framelist_del releases names/type arrays and list state | Loading, early returns and nested split/calibration paths |
| FITS headers and string values | qfits5/src/fits_h.c header access/copy/destruction; recipe/common code stores and duplicates values | Classify borrowed header strings versus owned copies and invalidation on mutation/destruction |
| qfits cache | qfits5/src/cache.c registers qfits_cache_purge with atexit and exposes explicit purge | Measure before/after controlled purge and at process exit; separate bounded retention from lost ownership |
| xmemory allocations / mappings | qfits5/include/xmemory.h redirects allocation/free/strdup; xmemory.c implements modes, registration and mapped storage | Prove diagnostic coverage of the actual mode, remaining registrations and repeated growth |
| Split/output resources | mef_split and mef_engine manage lists, headers, temporary outputs and file operations | Partial-write/publication failure, handles/mappings and truthful exit status |

The inventory specifically does not declare every NULL return, strdup, header or
frame-list allocation safe. A table entry is a review obligation, not a passing
test. No newly confirmed distinct defect is asserted by this planning document.

## Diagnostic coverage before interpreting application results

The production CMake target currently fixes qfits XMEMORY_MODE=2 and
XMEMORY_MAXPTRS=2000000. Source inspection confirms the allocation table retains
pointer registrations, and xmemory_status reports outstanding counts/bytes.
A leak tool's reachability classification can therefore differ from the
application's ownership contract. This is a reason to qualify the tool with the
real wrapper and inspect allocator accounting, not evidence that all live
registrations are intentional caches or all retained blocks are leaks.

Mac address/undefined instrumentation already detected #90's invalid access;
corrected C90/C17 cases passed. Mac leak detection was disabled in those runs.
The earlier tool-control directory is
~/Software/build/wenu-imaging/mac-memory-toolcheck-2tk86jc0/; inspect its original
provenance/results before crediting controls. Its existence is not a leak-tool
qualification. No full Stage 2 leak result has been returned.

Chapman3 GCC 10.2.1 and CMake 3.29.6 are established. Compatible GCC 10 diagnostic
runtimes were not found in the inspected locations; compiler lookups returned
bare names. Its eight #90 runs were uninstrumented functional checks. Listed
GCC 4.8 libraries were not substituted. Do not call the target memory-clean or
install/upgrade runtimes as a hidden prerequisite.

First execution increment:
1. Read the retained Mac tool-control report and inventory available platform
   leak tooling without installing anything.
2. Define and record independent positive/negative controls through both ordinary
   allocation and the actual xmemory wrapper, in separate disposable processes.
3. Demonstrate the tool distinguishes the selected invalid-lifetime and leak
   controls from balanced-allocation controls in C90/C17.
4. Record exact flags, allocator mode, observed coverage and unsupported cases.
   Only then run application ownership rows under the qualified configuration.

Use production-mode accounting plus compatible external diagnostics as the
primary lane. A separately isolated mode-0/native-allocator diagnostic lane is
only a proposed comparison if wrapper reachability obscures findings; it would
need explicit build wiring and paired output checks before use. Do not silently
change production mode or stack conflicting -D flags. Diagnostic-lane results
alone cannot qualify production mode 2. Source tracing / allocator counts are
not substitutes for an unavailable target leak detector.

## Declared test matrix

Every row starts pending unless the limited existing evidence is stated.
For each row, announce purpose, input, actual native methods/tools and expected
outputs before execution; put corresponding section comments in its driver.
The core matrix calls native routines, not Pycavi, unless explicitly stated.

| ID | Input and native path | Required observation / pass criteria |
|---|---|---|
| S2-00 | Source, tool, fixture and selected installation manifests | Exact branch/commit/dirty identity, protected hashes, allocator mode and diagnostic build identities; no hidden source patch |
| S2-01 | Balanced and known-invalid allocation/lifetime/leak controls, ordinary allocator and xmemory | Tool behavior demonstrated per C90/C17; failures detected, balanced controls clean; unsupported coverage explicitly blocked |
| S2-02 | Valid OCAM/WFI PAF and early/late missing/invalid required keys; mef_bb_new_from_paf / mef_bb_del | Construction/destruction and partial construction have declared owners, no unexplained live allocations or diagnostics |
| S2-03 | Existing failure_contract.py case semantics: mef_bb_load/main/mef_engine | Information-only paths, parser rejection and engine validation errors have correct exits and one context destruction; retain diagnostics per case |
| S2-04 | Synthetic valid/missing/corrupt split input and blocked output/publication; mef_split / mef_engine | Exact reference pixels/headers on success, failure propagates, no leaked file/mapping/list/header ownership or overwritten protected output |
| S2-05 | Qualified retained and controlled BPM fixtures, both regression producers; mef_build_bpm | Preserve every Mac-qualified mask pixel/extension/count and 0.5–1.5 thresholds; inspect all temporary ownership; #90 invalid-access subset already accepted |
| S2-06 | Shared-normalization fixtures in both detector orders, dome/sky; mef_build_cal | Preserve exact existing expected pixels and shared reference; inspect intermediate cubes/images and borrowed planes |
| S2-07 | Small staged bias, sky/master-flat and science paths through actual recipe/common functions | Add uncovered ownership paths with declared known output expectations before execution; retain existing baseline semantics |
| S2-08 | Practical allocation and I/O failure points in reviewed paths | Release only acquired resources and retain truthful failure; injection mechanism must be scoped/recorded and not change numerical behavior |
| S2-09 | Same-process repeated constructor/stage calls; proposed counts 1, 2, 10, 50 after fixed warmup | Per-object live ownership accounted at each boundary; no unexplained per-call growth or stale aliases; RSS alone is insufficient |
| S2-10 | Explicit controlled qfits cache purge plus normal process exit | Attribute cache state and allocator registrations; distinguish bounded cache retention, reachable abandoned blocks and genuinely released resources |
| S2-11 | Actual installed-wrapper error propagation after relevant corrections only | Reuse established Pycavi mefpp_reduce_science / run_commands exit/cwd contracts; trigger only for affected changes, not every planning update |

S2-03/04 must reuse existing failure semantics without blindly running a helper
that deletes its TemporaryDirectory evidence. Prepare retention/provenance-aware
orchestration before execution. Existing functional PASS labels do not imply
instrumented/retained coverage for these rows.

S2-07 begins with bounded synthetic fixtures. Existing observational acceptance
is retained comparison evidence; no expensive calibration/science rerun is
needed merely to refresh documentation. If a later discovered fix affects actual
pixels/headers, define its relevant comparison gate before that processing.

Repeated independent CLI invocations do not satisfy S2-09: process exit can
conceal retained state. Same-process harnesses must reset or reconstruct only
the intended context, use one writer per output, avoid fixed-name collisions,
and distinguish first-call cache initialization from repeat growth.
Practical failure injection and repeated-call harnesses are to be prepared on
the Mac; Chapman3 receives unchanged qualified drivers/fixture bytes.

## Host matrix and reporting

| Host / lane | Present evidence | Stage 2 status |
|---|---|---|
| Intel Mac C90/C17 address/undefined checks | #90 reproduction/correction accepted; selected prior failure behavior accepted | Broader normal/error/repeat suite and leak visibility pending |
| Intel Mac leak and allocator accounting | No accepted leak run; qfits tracking can retain reachability roots | Qualify controls/tool and baseline accounting first |
| Chapman3 C90/C17 functional regression | GCC 10.2.1, CMake 3.29.6; exact #90 mask agreement | Reuse unchanged drivers after Mac qualification |
| Chapman3 compatible memory/leak diagnostic lane | GCC 10 runtimes not located in inspected paths | Explicit tooling gap; do not report Stage 2 complete while unresolved |

For every new test/build/output directory, create run-provenance.json before
workload execution under ~/Software/build/wenu-imaging/. Record creation/update
times, purpose, status, tested source, tool versions/hashes, allocator mode,
flags, control case, input/output and log identities, exit status/signal,
retention role and parent/related evidence. Retain failed and interrupted attempts.
Keep full logs in evidence; return concise diagnostic summaries in chat.

Classify findings as invalid access/lifetime, lost allocation, still-registered
ownership, expected bounded cache or unresolved. Explain every exclusion and
tool limitation; do not suppress findings merely to obtain zero warnings.
Record each distinct defect in an existing/new issue before its bounded repair.
Keep scientific arrays, FITS structure/scaling, extension identity, masks,
thresholds and shared normalization in the relevant output comparison.

## Exit gate and mandatory review

Stage 2 passes only for a declared supported suite/configuration with:
- Qualified controls showing what the diagnostics observe.
- Accounted object lifetimes, no unexplained diagnostics/leaks/monotonic growth.
- Correct error propagation and partial-result cleanup.
- Unchanged relevant numerical/metadata contracts.
- Retained inspected actual-host evidence and explicit remaining platform limits.

An unresolved required host/tooling lane remains a gap, not an implicit waiver.
#75 closes only when its documented applicable ownership/memory criteria are met.
After Stage 2, present the evidence, open defects and early Phase 3 gap matrix
for review before Stage 2A representation work or Stage 3 extraction.

The early ESO Phase 3 requirements audit is allowed alongside qualification but
has not been performed here. Its eventual matrix must identify official
versioned requirements, product applicability and pipeline/design gaps; do not
infer compliance from existing FITS keywords. #91 implementation, variance/
covariance work and ESO_Phase3 profile code remain in their agreed later stages.
