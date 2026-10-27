# S2-04 split I/O/publication ownership baseline — 27 October 2026

Latest: [controlled Mac cache attribution accepted; unchanged-driver target verification prepared](stage2-split-mac-acceptance-2026-10-27.md). Earlier pending-control statements below describe the retained prior attempts.

Latest: [repaired observer evidence inspected and controlled cache attribution prepared](stage2-split-observed-evidence-2026-10-27.md). The baseline has 80 functional passes and 64 retained-state findings; its cache-attribution extension is not executed. Earlier preparation/scan statements below are historical.

Current status: [first Mac baseline inspected; test-only observer repair prepared](stage2-split-baseline-evidence-2026-10-27.md). The numbered-range descriptor scan described below belongs to the original attempt and is superseded by actual descriptor enumeration in #106; no production policy changes.

Status: prepared; actual Mac native compilation/execution pending. Tracking:
#75. Baseline main f042b38d4018af28e04e20134fc8f2b375c489e4 contains merged
S2-03 PRs #102/#104. Both user clones are clean on that main, the merged
branches are removed, and all original runs/archives/installations are preserved.
#103 is closed. Broader Stage 2 remains open.

## Scope and actual production path

Exercise unchanged `main`, `mef_bb_load`, `mef_engine`, `mef_split`, frame-list,
qfits header/cache and xmemory services on synthetic two-extension FITS input.
No Pycavi methods, calibration construction, observational reduction, detector
identity redesign, production allocator change or installation is involved.
Use the original `failure_contract.py` card/header/mosaic generator unchanged
in the retained fixture helper; do not run its deleting TemporaryDirectory suite.

Ten variants per instrument, OCAM/WFI, C90/C17 and two Mac diagnostic lanes
produce **80 case pairs / 160 native invocations**, four private builds.
Each pair has separate ordinary/observer working directories with identical
input bytes so one invocation cannot overwrite another's products/evidence.

| Variant | Declared output / failure contract |
|---|---|
| Valid relative input | Two exact reference detector outputs; exit 0 |
| Valid absolute input | Same products and exit |
| Explicit PAF pathname with spaces | Same products without a cwd PAF |
| One-entry input list | Same products; actual frame-list acquisition/release |
| Missing input | Controlled exit 1, named-input diagnostic, no products |
| Non-FITS input | Controlled exit 1, FITS diagnostic, no products |
| Invalid first-extension geometry | Controlled exit 1, geometry diagnostic, no products |
| Truncated first-extension data | Header retained, advertised pixels absent; exit 1/data diagnostic, no products |
| Blocked publication of second extension | Exit 1/publication diagnostic; first output preserved, existing second-output directory/sentinel unchanged |
| File-size-limited write | 4096-byte soft limit, SIGXFSZ ignored; exit 1/output diagnostic, no final products or temporary residue |

The two reference arrays are 3x2 signed 16-bit pixels, +1..+6 and -1..-6.
Independent raw FITS readback checks length/block padding, SIMPLE/BITPIX/NAXIS,
dimensions, OBJECT/EXTNAME, absence of introduced scaling, exact big-endian
pixels and zero data padding. Ordinary/observer output hashes must also agree.
This preserves the established split contract, not a complete FITS or scientific
certification. Earlier completed extensions remain after a later failure; no
new transaction/rollback or regular-file overwrite policy is introduced.

## Resource observation and diagnostics

The split probe follows the same recipe-reference observation approach as the
qualified S2-03 probe, forwarding calls to the unchanged common-library
constructor/destructor. It records one returned context and one recipe
destruction per invocation, actual CLI status and no live owner at return.
Partial construction internals remain unmodified.

The probe snapshots qfits registrations before CLI entry and after return,
including RAM bytes, mapped-file/reference counts and swap bytes if present.
It enumerates actual open file descriptors using F_GETFD/fstat, excluding and
closing only its own enumeration descriptor; no qfits allocation is acquired.
Count and identity fingerprint must match at return.
The recorded identity covers descriptor number/flags, device, inode and mode,
not file size/content. Unsupported/incomplete descriptor observation fails;
actual descriptor enumeration works independently of the changed soft limit (#106).
This detects changes across the call; it is not a syscall-by-syscall lifetime proof.

Instrumented builds use the qualified ASan/UBSan settings. Separate uninstrumented
builds run the observer under the installed qualified `leaks -atExit` tool.
qfits mode 2 and max pointers 2000000 remain unchanged. The file-size limit is
applied to the ordinary child only; the observer applies it around the actual
CLI call and restores it before exit-time leak observation. No parent shell,
normal installation or unrelated process limit is changed.

**No explicit cache purge in this baseline.** qfits caches header offsets and
may retain registered allocations until exit. Record these as unattributed
return-state findings pending evidence-based attribution; do not label them
lost memory or silently exclude them. A functional split pass cannot override
unexplained resource findings. Controlled cache attribution remains part of the
declared Stage 2 obligations; this increment does not certify general mmap/swap,
cache or repeated-stage behavior from a single synthetic split.

## Evidence and pass/fail reporting

Create per-run/source/build/case/role provenance before workloads under
`~/Software/build/wenu-imaging/mac-stage2-split-baseline-*`. Retain every original
log, staged input/sentinel, output and failed/interrupted attempt. The runner
records functional status separately from resource/memory findings and overall
execution completeness. No incomplete, crashed or diagnostic-producing case passes.
Do not change expected pixels, outputs or failure policy merely to obtain a pass.

Inputs/sentinels, source/export/checkout, selected installed engine and user
configuration hashes must remain unchanged. No incomplete temporary files or
unexpected outputs may remain. Successful cases need exact declared products;
error cases need truthful exits and their declared partial-output behavior.
Memory/descriptor acceptance additionally requires accounted state and no
unexplained instrumentation or external leak finding.

Agent preparation checks passed: Python syntax, unchanged original FITS-generator
AST, 40 instrument/case/role fixture preparations, paired input identities,
independent FITS readback and rejection of deliberately changed pixels, zero and
mapped allocator-status parsing, and whitespace checks. No native Mac or target
test is claimed by those Python checks. The actual Mac run comes first; inspect
its returned evidence before preparing unchanged native driver/helper verification
on Chapman3, keeping its compatible external-diagnostic gap explicit.

Next rows remain S2-05/06 calibration ownership, S2-07 additional recipes,
S2-08 practical injection, S2-09 repeated stages, S2-10 cache lifetimes and
conditional S2-11 wrapper checks. #75/Stage 2 remains open. The early Phase 3
audit is pending; mandatory review still precedes Stage 2A or extraction.
