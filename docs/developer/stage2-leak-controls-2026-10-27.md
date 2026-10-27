# Mac leak/accounting tool controls — 27 October 2026

Status: Mac C90/C17 controls accepted from inspected evidence at db6af6a1888e6abbe65fd4ac177f1e890d3a952a. See [actual results and limitations](stage2-tool-controls-acceptance-2026-10-27.md). The declared expectations below are retained as the test contract; broader application qualification remains pending.
Stacked on the Stage 2 preparation in PR #97. Tracking #75.
No production allocator, numerical code, installation or scientific default is changed.

## Reused evidence and installed tool contract

Fernando's retained toolcheck metadata at
~/Software/build/wenu-imaging/mac-memory-toolcheck-2tk86jc0/run-provenance.json
reports C90/C17 ASan/UBSan controls through system and qfits RAM allocation:
clean controls exit zero; bounds/lifetime/duplicate-release and signed-overflow
controls exit the configured diagnostic status. This is returned metadata,
not a new rerun or an independently re-inspected archive of those logs.
Leak detection was disabled. Mapped/swap paths are explicitly unqualified.
Do not repeat these controls solely because the roadmap documentation changed.
Preserve the original driver, provenance and logs before accepting the full Stage 2 gate.

The actual Mac's installed leaks(1) documentation was returned and inspected:
leaks -quiet -atExit -- command launches a command and scans it at exit,
normally setting MallocStackLogging=lite. Exit zero means no unreachable blocks
found, one means leaks found, greater than one means a tool error.
Writable globals/registers/stacks form reachability roots. Thus a registered
xmemory block can remain allocated while leaks reports no unreachable block.
This statement is about reachability semantics, not accepted application ownership.

## Declared new controls

Compile leak_controls.c plus unchanged qfits5/src/xmemory.c and its header with
the existing Apple Clang/SDK in explicit C90 and C17, -O0 -g, no sanitizer.
Retain XMEMORY_MODE=2, XMEMORY_MAXPTRS=2000000 and XMEMORY_DEBUG=0.
Each case is a separate fresh process/work directory. There is no Pycavi,
Eclipse image reduction, catalogue access, installation or observational work.

| Control per mode | Allocation action | Expected leaks result | Expected final qfits accounting |
|---|---|---|---|
| system-clean | Allocate, initialize and free 8192 system bytes | zero leaks, exit 0 | zero pointers / zero bytes |
| system-unreachable | Deliberately abandon an 8192-byte diagnostic allocation, clear the local and overwrite old stack scratch | at least one block / 8192 bytes, exit 1 | zero / zero |
| system-rooted | Retain 8192 system bytes through an explicit global | zero unreachable blocks, exit 0 | zero / zero |
| qfits-clean | Allocate 8192 bytes through xmemory_malloc, then xmemory_free | zero leaks, exit 0 | zero / zero; intermediate snapshot must show one / 8192 |
| qfits-registered | Allocate through xmemory_malloc and drop the caller pointer while the qfits table retains it | zero unreachable blocks, exit 0 | one pointer / 8192 bytes; intermediate snapshot also one / 8192 |

These expected controls are hypotheses to qualify on the actual Mac.
A failure to detect the unreachable system control is a failed qualification,
not permission to assume the allocator/library is leak-free. Other unexpected
findings also fail the attempt and are retained; no exclusion/suppression is added.
The rooted and qfits-registered controls deliberately retain memory to demonstrate
that no unreachable block is not the same claim as no outstanding ownership.

The driver calls xmemory_status at explicit initial/allocated/final boundaries.
At XMEMORY_DEBUG=0, an empty status section means the source's zero-cell early
return; the harness requires both boundary markers, checks the initial zero state
and validates the nonzero allocation snapshot before crediting a zero after free.
No production cache purge is inserted, and this control does not load qfits FITS
caches. Application cache/lifetime and repeated-call qualification remains later.

Child environment sets MallocStackLogging=lite and MallocScribble=1.
Sanitizer options and inherited DYLD injection/library overrides are removed only
from these disposable child environments and recorded. No shell/profile/system
environment or normal engine configuration changes. Full logs stay in the run;
chat output contains parsed counts, not raw address/backtrace dumps.

## Execution and acceptance

Use qualify_mac_leaks.py with the explicit existing Xcode compiler and SDK.
Launch with nice -n 10 from a clean delivered branch using the existing Mac
anaconda3 interpreter. It creates independent work under
~/Software/build/wenu-imaging/mac-stage2-leak-controls-*/ and writes provenance
before compilation/execution. The root report records source and tool hashes,
compiler/OS inventory logs, flags, environment, each exit and diagnostic/accounting
summary, and protected selected-engine/configuration hashes.

Pass means all ten cases (five per language mode) behave as declared and source,
checkout and protected files remain unchanged. This qualifies the observed
RAM control/tool configuration only. No application leak-clean or Stage 2
completion claim follows. The qfits reachability blind spot must remain explicit.
Unsupported mmap/swap and Chapman3 memory tooling remain gaps in the Stage 2 matrix.

Keep all failed/interrupted/successful attempts until evidence review.
Do not merge or delete branches/run directories as a consequence of writing or
passing these controls. No package installation or compatible-runtime provisioning
is part of this candidate.
