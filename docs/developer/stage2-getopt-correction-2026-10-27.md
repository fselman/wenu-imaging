# S2-03 bounded parser correction (#103) — 27 October 2026

Status: correction prepared; actual Mac and Chapman3 qualification pending.
Stacked on the inspected failed baseline in PR #102. #103 and the broader #75
gate stay open. No installation or observational processing is requested.

The [retained baseline](stage2-cli-baseline-evidence-2026-10-27.md) contains
100 failing instrumented case pairs, all at the same registered-name comparison
in the bundled Eclipse `src/unix/getopt.c`. The ordinary executable also fails,
so this is independent of the diagnostic observer. The native parser reads past
shorter registered option names while comparing the supplied option's length.

## Minimal repair and preserved behavior

Replace only that name-matching `memcmp` with `strncmp`. Comparing a longer
input against a shorter registered name now stops at the latter's terminating
NUL and rejects the nonmatch. Exact matches and prefixes still use the existing
match-length, exact-match preference and ambiguity logic. Other parser control
flow, return codes and option tables are unchanged. The repair changes no image
arithmetic, PAF configuration, acquisition gain, masks, shared normalization,
allocator policy or installed executable. No sanitizer suppression is added.

The S2-03 observer and all 28 original case definitions remain byte/semantically
unchanged. The orchestration adds a corrected phase, an explicit reviewed-baseline
comparison, the parser source hash and a focused parser regression. It creates a
fresh `mac-stage2-cli-corrected-*` directory rather than modifying the baseline.

## Qualification purpose and execution

Use the actual bundled parser in `getopt_name_probe`, with a deliberately short
registered name preceding longer names. Thirteen checks cover exact matching
after the short name, an exact name winning over a prefix, exact version,
unique/ambiguous prefixes, unknown and longer-than-registered options, equals and
separate required values, missing values, prefix-with-value, short options and
the end-of-options marker. Reset the actual parser between these focused checks.
The harness is RAM-only and performs no image I/O.

Then run the **same 224 CLI case pairs** (448 native invocations), using the
unchanged OCAM/WFI fixtures and observer, across four C90/C17 instrumented/leaks
builds. Each build also executes the 13 parser checks: 52 checks total.
The ordinary CLI and observed entry point must retain expected exits and
diagnostics, balanced ownership and zero qfits registrations at return. Relevant
leak/ASan/UBSan findings fail the gate. The parser regression runs instrumented
in the instrumented builds; its uninstrumented runs are functional checks,
not separate external-leak observations.

The corrected phase requires the original failed report to match the committed
reviewed report exactly. All corrected CLI cases must match the corresponding
passing uninstrumented baseline's arguments, PAF hash, expected/native exit,
ownership contract and final accounting. This uses the passing functional lane
as the semantic reference; it does not reinterpret baseline invalid reads as
passes. A newly exposed finding remains a failure requiring investigation.

Retain the baseline report/archive and all original run directories unchanged.
Preserve every new case/build log and manifest and check sources, exported sources,
selected installed engine, user configuration, checkout and baseline report
hashes after execution. No explicit cache purge, production allocator change or
unreachable-leak exclusion is used. The probe and extra CMake wiring are private
diagnostic targets and are not installed.

Agent validation: Python syntax and unchanged 28-case AST; all 56 PAF mutations;
original observer hash matches the actual Mac baseline; production diff is one
string-comparison call plus its explanatory comment; whitespace checks passed.
Native compilation and the fresh actual-Mac results remain pending. Prepare the
unchanged driver/fixture Chapman3 functional/accounting verification only after
inspecting accepted Mac evidence. Its unavailable compatible sanitizer/leak
tooling remains an explicit broader Stage 2 gap.
