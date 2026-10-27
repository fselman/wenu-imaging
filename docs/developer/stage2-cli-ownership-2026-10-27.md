# S2-03 CLI/parser/engine ownership baseline — 27 October 2026

Status: actual Mac baseline completed and failed in 100 of 224 case pairs.
See [inspected baseline evidence](stage2-cli-baseline-evidence-2026-10-27.md)
and #103. No production correction or S2-03 acceptance is claimed.
Parent gate: #75. Baseline: integrated main
9118ffaaec077eefb0d82a50d232721a9d280a3f. PRs #97/#98/#100/#101 are merged and
their branches removed on GitHub, Mac and Chapman3. Both user clones are clean
on that main; all original runs, archives and installations remain preserved.

## Position in the roadmap

Stage 2 memory/failure correctness is current. S2-01 Mac tool controls and the
bounded S2-02 context gate passed; #99's 29-string cleanup is integrated.
S2-03 now qualifies the CLI ownership boundaries around that context. S2-04
split I/O/publication, S2-05/06 BPM/normalization ownership, S2-07 additional
recipe paths, S2-08 injection, S2-09 repeated stages and S2-10 cache lifetimes
remain open. S2-11 wrapper checks are conditional on affected changes.
The broader #75 gate and Chapman3 compatible diagnostic-tool gap remain open.
The early Phase 3 requirements audit remains pending; the mandatory review
after Stage 2 precedes Stage 2A representation work and Stage 3 extraction.

## Purpose, inputs and actual methods

Use retained independent case directories and both unchanged instrument PAFs.
The ordinary `mefpp` executable and `cli_ownership_probe` both execute the actual
recipe entry point, `mef_bb_load` and relevant `mef_engine` rejection paths.
The common-library constructor/destructor and qfits allocator remain unchanged.
No Pycavi methods, successful split, calibration construction or image processing
run in this increment. No FITS pixel-equivalence claim is made.

The probe includes the unchanged recipe source with only its entry-point name
and recipe constructor/destructor references redirected to observing functions.
It counts successfully returned contexts and recipe destruction calls, checks
owner identity, and forwards directly to the real common-library functions.
Internal partial-construction destruction is observed through allocation accounting,
not counted as a successfully published context. No observer allocates via qfits.

| Case group per instrument | Count | Expected contract |
|---|---:|---|
| Help/version/license without PAF | 3 | Native exit 0, no constructed context |
| No arguments, missing option argument, unknown option | 3 | Native exit 1, no constructed context |
| Missing or malformed PAF | 2 | Native exit 1, PAF diagnostic, no published context |
| Missing count/geometry/final key | 3 | Native exit 1, relevant key diagnostic, no published context |
| Invalid chip counts | 7 | Native exit 1, count diagnostic, no published context |
| Value-less saturation key | 1 | Native exit 1, key diagnostic, no published context |
| Invalid CLI saturation limits | 7 | Native exit 1, saturation diagnostic, one construction/destruction |
| Missing split input | 1 | Native exit 1, missing-input diagnostic, one construction/destruction |
| Science request without calibration names | 1 | Native exit 1, engine validation diagnostic, one construction/destruction |

The first 27 cases reuse `failure_contract.py` semantics. The final case covers
the early missing-calibration check in `mef_engine`; it never reaches image I/O.
There are 28 cases per instrument, two instruments, C90/C17 and two diagnostic
lanes: **224 case pairs / 448 native invocations**, four private builds.

## Expected outputs and acceptance

Run `qualify_cli_ownership.py` on the Mac with niceness >=10. Each build contains
the ordinary executable and observer. Instrumented lanes use the established
ASan/UBSan settings with leak detection disabled; separate uninstrumented lanes
run the observer under the qualified installed `leaks -atExit` tool. Both use
production qfits mode 2 and the 2,000,000-entry registration table.

The ordinary executable must return the declared status and diagnostic. The
observer records the actual recipe return, checks the same status/diagnostic and
expects balanced context ownership. Its own launcher exit is zero to separate
expected native CLI rejection from the external leak-tool status. Missing native
completion markers, crashes and nonzero tool exits cannot pass.

qfits snapshots before CLI entry and after return must both show zero live
registrations/bytes; diagnostics and external unreachable-leak findings must be
absent. Neither explicit cache purge nor atexit allocator cleanup is used to
obtain the post-return snapshot. Any retention is a finding to investigate,
not an exclusion. Every staged PAF must stay byte-identical, and no processing
outputs may appear in a case directory.

`run-provenance.json` precedes each directory's workload. Preserve original logs,
PAFs, build records, exact source/export/wiring hashes and failed/interrupted
attempts under `~/Software/build/wenu-imaging/mac-stage2-cli-baseline-*`.
The runner separately records execution completeness and the memory gate.
Selected configuration/installed engine hashes and checkout/source identities
must remain unchanged. No installation or normal engine selection occurs.

Agent checks: Python syntax, 28 unique case definitions, all 56 instrument/case
PAF preparations and whitespace checks passed. Native build and actual-host
diagnostic outcomes are pending. Inspect the returned Mac evidence before
preparing unchanged-driver/fixture Chapman3 verification; target functional
accounting must not be described as unavailable sanitizer/leak-tool acceptance.
