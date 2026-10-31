# Bounded M4 performance comparison plan — 31 October 2026

The owner accepts the paired functional qualification at
`5e6bd83beafa744cd2a3be64b5405083c3ae634b`. PR #186 remains unmerged.
This plan addresses the remaining shared-qfits performance question without
rebuilding qualified tools, reinstalling programs or replaying the test matrix.
The existing whole-file int-offset limit is not adopted as permanent policy.

The [performance contract](native-performance-portability-contract-2026-10-31.md)
requires: “The exact noise assessment/measurement script is reviewed before
execution.” The [prepared script](../../mefpp2/tests/benchmark_native_paths.py)
therefore has separate preparation and execution modes. **No benchmark has run.**

## Frozen comparison

Reuse private optimized serial C90 executables from the actual qualified runs:

| Role | Source | Mac retained run |
|---|---|---|
| Reference | 2d662b148db56b0292ca6ec3ee9bceb1bc463595 | mac-m4-layout-corrected-Ban7s6aY |
| Candidate | 5e6bd83beafa744cd2a3be64b5405083c3ae634b | mac-m4-qfits-reuse-KKXuAs2V |

Both are under `~/Software/build/wenu-imaging`, with executable
`build-c90/mefpp2/mefpp`. Reference normal-engine sources match accepted main
c4a5ba4 for qfits, Eclipse, recipe and linked common/kernel/path sources; the
earlier opt-in M4 scanner is not linked into that engine. This is checked with
the Git revisions rather than treating an arbitrary previous executable as the
reference. Preparation requires passing qualification receipts and matching
Release/C90/O2/compiler/archiver/linker/SDK settings in existing CMake caches.
Those are source/build provenance checks, not another tool-discovery campaign.

Use the same existing tiny OCAM/WFI fixture factory, PAF overrides and explicit
native pipeline arguments as the passing native_paths_contract. Each native call
constructs bias/BPM/dome/sky/master-flat/science products, with fresh output and
scratch directories. Input/configuration files become read-only after generation.
No original observations or installed executable appear in the plan.

## Exact launch budget and equivalence

For each instrument, perform one reference warm-up and one candidate warm-up,
retaining both. Compare all six products before proceeding. Then perform exactly
three measured pairs in the order R/C, C/R, R/C. Total across both instruments:
**16 native launches: four warm-ups and twelve measured calls.** No retries or
extra profiles are automatic. Any error, timeout or pixel/metadata difference
stops the attempt and retains its evidence; an atomic attempt marker prevents
replaying the same plan.

Every output set is compared using the existing products helper: exact pixel
hashes, shapes, data types and FITS cards, with only its already qualified
generated-ID normalization. Do not add a new timestamp/header whitelist to make
results agree. Fixture/source/executable/qualification identities are checked
before and after. Preparation-only examples without matched qualifications
cannot enter execution mode.

## Measurements and interpretation

Use perf_counter around native process launch through exit, including startup,
layout/I/O/computation/publication. Collect process-specific wait4 user/system
CPU, peak RSS and raw I/O block counters. Record load averages before/after each
call, retained output/scratch bytes and separate product-validation elapsed time.
Fixture generation, hashing and validation are outside native timings and named
as separate preparation/validation costs; do not call them free end-to-end work.
No shared-cache flushing, sanitizer timing, parallel native runs or system-wide
load experiment. Use niceness10 and the recorded single-thread resource settings.

For each instrument report every candidate/reference wall and CPU ratio, median
and range, plus RSS/block-count/retained-byte differences. No percentage slowdown
allowance or automatic performance pass is encoded. Consistent slowdown or extra
data traffic requires investigation. Mixed/noisy pairs are inconclusive; inspect
the smallest informative follow-up rather than silently increasing the budget.
Three pairs do not justify a claimed statistical confidence interval. Retain
outliers and failed attempts; do not cherry-pick the fastest observations.

These fixtures target startup/header/I/O/publication overhead of the shared qfits
change. They do not establish full-sized image throughput, opt-in layout-adapter
cost when connected in M5/M6, or peak temporary-disk occupancy. Final retained
bytes and OS block counters are not a measurement of transient disk peak. No
whole-pipeline/scientific/performance acceptance follows merely from completion.

## Current review state

The script's preparation path was exercised on agent synthetic files: sixteen
commands prepared, all attempt directories empty, no native calls/logs/results.
Those agent executable paths were planning examples, not a matched benchmark
pair. Actual-target preparation and measurement/execution-path review remain
pending. This update does not alter native C, qualification inputs or the paired
functional result. The next user handoff prepares a plan only; its hash/commands
are reviewed before any measurement launch.
