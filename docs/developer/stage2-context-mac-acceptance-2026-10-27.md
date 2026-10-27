# Corrected context cleanup: Mac acceptance — 27 October 2026

Issue #99, PR #101; bounded Stage 2 S2-02 acceptance only.
Actual clean Mac source: 6efb77ac258579a8f2c699b9c34b982045a46637,
fix/99-context-owned-strings. Chapman3 acceptance is pending.

The uploaded archive SHA256 computed during inspection is
64b4d21cd8213a2f847de5eae46acb6b880547037367e515f25cf58e5238b450.
All 175 member sizes/hashes verified against its transfer manifest.
The agent independently inspected all 48 original case logs and reports,
all recorded command/log hashes and zero exits, staged PAF bytes, reference
baseline identity, tested source and the four actual build records.

## Actual outcomes

All 48 cases pass across explicit C90/C17, instrumented/leaks-accounting lanes,
OCAM/WFI PAFs and the six original variants. Every constructor success/rejection
expectation matches the failed baseline. All staged PAF input hashes and reported
context configuration fingerprints are exactly unchanged.

Allocator state is zero pointers/zero bytes at process start, after initialization,
after every destruction/rejected construction and at the final boundary,
including all three same-process construct/destroy calls. Original logs show no
address/undefined diagnostic failure. All 24 uninstrumented leaks cases report
zero unreachable blocks/bytes and exit zero. The former 24 failing cases now pass;
finding_cases=0 and execution_complete=true. No suppression or cache purge
was introduced to obtain this result.

| Original defect path | Failed baseline per call | Corrected final ownership |
|---|---|---|
| Valid context construction/destruction | 29 pointers / 550 bytes retained | zero / zero |
| Three same-process calls | grows to 87 / 1650 | zero after each call |
| Late MEF.SATMAX rejection | 29 / 550 retained | zero / zero |
| Early/geometry/invalid-count rejection | zero / zero | zero / zero |

The corrected exported C unit matches the baseline outside mef_bb_del.
Inside it, exactly 29 missing owned-member release sites were added.
The C diagnostic driver is byte-identical to the baseline. Constructor source,
original PAFs, allocator policy and numerical processing remain unchanged.
The Python orchestration adds corrected-phase provenance and automatic baseline
input/context comparison; it does not change the native case matrix.

## Preservation and limits

[Corrected report](fixtures/mac-stage2-context-corrected-2026-10-27/run-provenance.json),
four build records and the complete 175-file transfer manifest are committed.
The full original archive, including logs/source/PAFs and a byte-identical copy
of the reference baseline report, is retained as Library file
libfile_ee8048d51eb08191af3859110fdc1372.
Fernando retains the corrected Mac run and archive:
~/Software/build/wenu-imaging/mac-stage2-context-corrected-87a1olms/.
The [failed baseline](stage2-context-baseline-evidence-2026-10-27.md) remains
separately preserved; no run-directory deletion or relocation is authorized.

Actual-host records and collection checks report unchanged selected engine,
configuration, source/checkout and original baseline report. The agent inspected
uploaded files, not the live Mac filesystem. No installation, engine selection
switch, image processing or observational rerun occurred.

This accepts the declared normal/partial context cleanup and short three-call
repeat behavior on this Mac configuration, not the full Stage 2 ownership suite.
It does not qualify mef_engine error paths, images/cubes/headers/lists, cache
lifetimes, allocation failure injection, longer repeated stage calls or mmap/swap.
#99 remains open until target evidence is linked; #75 remains broader and open.
Chapman3 must verify unchanged native driver and fixture/context expectations
in C90/C17. Its unavailable compatible diagnostic-runtime lane remains an
explicit gap, not a passing sanitizer check. No merge or cleanup is performed
by this evidence-only acceptance update.
