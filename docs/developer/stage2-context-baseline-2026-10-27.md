# S2-02 context baseline — 27 October 2026

Status: diagnostic candidate; actual Mac execution pending.
Stacked on accepted Mac tool-control PR #98 and planning PR #97.
Tracking #75; distinct constructor/destructor omission recorded as #99.

## Purpose and scope

Call the unchanged production mef_bb_new_from_paf and mef_bb_del directly.
Establish context result correctness and allocation ownership at normal and
partial-construction boundaries before any correction. This does not call
mef_engine, read images, reduce observations, run Pycavi or install anything.
It does not repeat the previously qualified tool controls.

Source review found that phase3_prodcatg_val_bpm is duplicated during context
construction but omitted from the destructor. The broader direct-field inventory
also identifies other Phase 3 and master-flat configuration strings whose
allocation/release pairing must be reviewed. #99 records the confirmed example;
do not silently repair it while trying to measure the unchanged baseline.

## Actual test matrix

Four private builds: explicit C90/C17, each with two separate diagnostic lanes:
- Address/undefined instrumentation and qualified qfits accounting, with leak
  detection disabled as in the accepted ASan/UBSan controls.
- Uninstrumented native code launched through installed leaks -quiet -atExit,
  plus the same allocator accounting. No sanitizer is injected into this lane.

Each build executes two configurations (OCAM 32 detectors, WFI 8 detectors)
and six cases, each in an independent process and work directory:

| Case | Staged input | Expected constructor result / calls |
|---|---|---|
| valid-1 | Exact repository PAF bytes | Non-NULL context with expected nchips; destroy once |
| valid-3 | Same exact PAF bytes | Three serial construct/destroy calls in the same process |
| missing-count | Remove the single MEF.NCHIPS key | NULL result; internal partial cleanup |
| missing-geometry | Remove MEF.CROP.Y.MAX.CHIP2 | NULL result after bounded detector-context construction |
| missing-final | Remove MEF.SATMAX | NULL result late in configuration construction |
| invalid-count | Replace MEF.NCHIPS value with junk | NULL result; checked rejection |

Total: 48 independent cases across four builds. The three-call case is a short
context-only diagnostic comparison, not completion of the full S2-09 repeat suite.
Allocation-failure injection, other engine stages, mmap/swap and target execution
are outside this baseline increment.

The caller destroys each non-NULL context once and never destroys a NULL result.
The unchanged constructor owns cleanup before publishing a context.
Valid contexts print their detector count, instrument, proportional flag and
gain bounds for later comparison. No values, defaults or header policy change.

## Accounting and success semantics

Record qfits state before initialization, after eclipse_init, after every
destruction/rejected construction and at the final boundary. The memory
acceptance expectation is return to the pre-construction baseline without
unexplained outstanding ownership or growth. No cache purge, suppression or
extra destructor release is inserted to make the baseline appear clean.

The installed leaks tool may report zero while qfits still holds lost
application-owned registrations. Interpret both observations together, as
demonstrated by the accepted retained-block control. Preserve pointer/byte
counts and the full raw diagnostic logs, but show only concise summaries in chat.

Each case records constructor-contract result, context fingerprints, accounting
snapshots, external leak counts where available, exit status and findings.
Independent cases continue after application findings so the baseline matrix is
retained, while a configuration/build failure stops dependent execution.
No further scientific processing depends on a failed case.

A native expected-rejection result is not an expected memory failure.
A case with outstanding registrations is marked failed even if native execution
and leaks exit zero. At the end, execution_complete can be true while the root
memory status is failed. The script exits nonzero and prints FINDING for affected
cases; this is retained baseline evidence, not a successful memory qualification.
Do not suppress an observed source defect by labelling its reproduction clean.

## Build/source preservation

Export the exact delivered commit into a fresh source directory under
~/Software/build/wenu-imaging/mac-stage2-context-baseline-*/.
Only append a disposable CMake target linking the diagnostic driver with actual
mefpp_common/Eclipse/qfits. Production C units, allocator mode 2, maximum
registrations 2000000 and original repository PAFs remain unchanged.
The report records the source archive and diagnostic wiring hashes.

Create run-provenance.json before each workload, retain input PAF hashes and
per-case reports/logs, and update incomplete/failed status truthfully.
No normal installation/prefix or selected engine/configuration is changed.
Record their hashes before/after along with relevant source and checkout state.

All four builds use the existing explicit Apple Clang/SDK and CMake, not a new
compiler or runtime installation. No actual Mac run has occurred in this delivery.
Python syntax was checked; native behavior and the matrix outcome remain pending.

## Next action after returned evidence

Inspect actual-host reports and pair remaining registrations with the constructor
field/destructor inventory. Reconcile #99 with measured results and define its
minimal release correction and repeat/partial-construction acceptance before
changing production source. Keep #75 and broader Stage 2 gates open.
A later correction requires Mac development and unchanged-driver/fixture
verification on Chapman3; its diagnostic-tooling gap must remain explicit.
