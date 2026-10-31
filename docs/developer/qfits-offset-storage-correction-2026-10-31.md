# qfits temporary offset storage correction — 31 October 2026

The prior matched comparison completed all sixteen calls on Mac and Chapman with
exact product agreement and preservation. Mac medians were near parity; Chapman
candidate wall medians were 1.026416 (OmegaCAM) and 1.041726 (WFI), with mixed and
variable CPU ratios. Performance acceptance remains open; no automatic percentage
allowance or conclusion that the difference is merely noise was adopted.

## Inspection before any repeat

The owner returned the retained Chapman absolute timings and load averages.
[Console record](fixtures/agent-qfits-offset-storage-2026-10-31/chapman-prior-console.json)
preserves the printed precision and original results SHA256. It is not a copy
of the full host JSON. Recorded load averages span 0.02–0.25; they do not support
attributing the result to sustained heavy host load, though they cannot rule out
short scheduling/frequency effects. CPU differences still require investigation.

The existing [science writer](../../mefpp2/ins/mef/recipes/mefpp.c) calls sleep(1)
after generating ORIGFILE to avoid name collisions. That source is unchanged
between the reference and candidate. It accounts for the common roughly one-second
non-CPU component. The delay is retained in end-to-end timing; naming behavior is
not changed for this comparison, and the delay does not explain extra candidate CPU.

## Source-confirmed avoidable allocation (#197)

The qfits reuse patch introduced two temporary heap allocations on every cache
discovery, sized to the requested HDU limit even for primary/8/32-detector files.
The original implementation used two 128-entry stack buffers. This is avoidable
allocation/data traffic under the existing performance contract, independently
of whether it explains the measured ratios.

Correction restores two stack buffers for ordinary counts. Temporary offset
storage grows only when an actual additional HDU exceeds capacity, with checked
growth capped by max_hdus. Completed entries are copied, prior dynamic storage
is freed, and both successful and failed exits free only owned dynamic buffers.
The legacy maximum, pre-write bounds, integer/header budgets, transactional cache
publication and existing reader/plane/numerical paths remain unchanged. No checks
are removed. There is no claim yet that this resolves the observed timing excess.

## Verification and target handoff

The discovery contract now includes 300 extensions, exercising multiple growth
steps as well as exact/short count and header budgets, known offsets, duplicates,
overflow/sparse refusal and immutable tiny fixtures. Existing layout, bias and
native-path controls retain their expected arrays and metadata.

| Agent check | Result |
|---|---|
| C90 discovery/layout/bias/native paths | 4/4, 23.64 s |
| C17 same four contracts | 4/4, 24.75 s |
| Scoped ASan/UBSan discovery/layout/bias | 3/3, 8.92 s |

[Logs/source receipt](fixtures/agent-qfits-offset-storage-2026-10-31/receipt.json)
retain private builds; no original observation, installation or new benchmark.
Leak detection remains disabled for the previously stated legacy-cache limitation.
The native target runner still performs exactly four synthetic contracts per
C90/C17 lane, using canonical tools and protection snapshots. Actual Mac then
representative Chapman checks for this revised source are pending.

The preparation-only benchmark helper accepts an explicit --candidate-revision
for a newly qualified candidate, checking that exact receipt rather than assuming
the earlier 5e6bd83 source. Default remains the old source for existing use.
Measurement method, launch budget, equivalence rules and no-automatic-acceptance
policy are unchanged. Prior plans/attempts/results are not edited or replayed.
Only after revised functional qualification should the smallest reviewed matched
performance follow-up be selected. #197, performance acceptance and M4 remain open.
