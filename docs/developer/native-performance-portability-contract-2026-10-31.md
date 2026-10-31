# Native performance preservation and Windows preparation

Owner contract clarification, 31 October 2026, during [M4 #182](https://github.com/fselman/wenu-imaging/issues/182)
review in [PR #183](https://github.com/fselman/wenu-imaging/pull/183): mefpp is fast
and efficient and refactoring must preserve that performance. Identify code that
will complicate eventual native Windows migration while reviewing each boundary.
Source-review baseline: `e448c9b2ff1af8191c4f2cff654322da86a8ce26`; native files
are unchanged from accepted main `6c4b0f0eff639da8dbef890f0df10f86c70bb0ee`.

This is a cross-cutting acceptance requirement for M4 and subsequent refactoring,
not a new milestone, platform port, optimization campaign or authorization to
change algorithms. Existing native Windows stage remains later; identify barriers
now as information for a possible later port. Windows obstacles must not constrain
the Mac/Linux design or acceptance. No performance measurements or native Windows
compilation were performed for this document.

## Owner clarification: Windows notes do not govern Mac/Linux design

Windows identification is informational preparation only. Design and optimize the
Mac/Linux versions for their actual requirements, retaining their efficient native
facilities. Do not introduce Windows-driven abstractions, fallback I/O, dependencies,
runtime indirection or design restrictions into the current refactor. A Windows
obstacle is not a Mac/Linux blocker or an acceptance gate.

If a native Windows port is undertaken, implement and qualify adapters for that
version then. The register below records where that later work is likely needed;
its migration suggestions apply to that future port, not to current Mac/Linux
implementation. The no-speed-penalty requirement remains fully in force.

## Performance contract

1. Preserve speed and efficiency for equivalent native reductions. A reproducible
   slowdown caused by refactoring is a regression to fix before acceptance. No
   automatic 5%, 10% or other slowdown allowance is adopted. Ambiguous/noisy timing
   is inconclusive, not evidence of no penalty. Any unavoidable tradeoff needs an
   explicit owner decision with measurements; it cannot be silently accepted.
2. Keep numerical loops in C and preserve precision, algorithms, rejection/order,
   correction state and required validation. Reuse the existing efficient FITS
   and memory paths where qualified; do not introduce avoidable full-image copies,
   conversions, rereads, intermediate files or per-pixel interface/metadata work.
   Retain the copies required by read-only input ownership and numerical behavior;
   removing required checks or ownership safety is not a performance remedy.
3. Resolve metadata/configuration/layout once per applicable input/request and
   reuse the validated immutable view. Check identity on actual open/use as needed;
   no stale cross-request cache is authorized. Bound detector/channel lookups and
   keep file opening, parsing and verbose logging outside numerical inner loops.
4. Track wall time, user/system CPU time, peak resident memory and relevant I/O
   volume/temporary disk use. Treat avoidable extra allocation/data traffic as
   efficiency regressions even if a warm cache temporarily hides their time cost.
   Improved parallel throughput cannot excuse a serial-path regression.
5. Distinguish same-functionality refactoring from newly required work such as
   variance propagation. Compare equivalent operation sets and report incremental
   feature cost separately. This distinction is not a waiver for refactoring
   overhead. Report one-time raw preparation/copy/hash costs separately and include
   them in the end-to-end cost accounting; do not hide work outside native timings.

### Bounded comparison protocol to prepare with changed C code

- Freeze an exact accepted reference and candidate, identical selected inputs,
  calibrations/configuration, output requirements, compiler/optimization mode,
  dependencies, hardware, storage location and resource/thread settings. Use
  private optimized serial builds, not sanitizer/debug timings. Do not replace a
  production installation or alter/drop products to improve the comparison.
- Check pixel/metadata equivalence first. Use the representative existing OCAM/WFI
  fixture appropriate to the changed service. For primary-image support use the
  equivalent extracted-detector/mosaic context; do not compare different workloads
  or an unsupported legacy Bath workflow and call it a speed result.
- Plan a small alternating reference/candidate series (initially three pairs,
  after one separately recorded warm-up per executable where appropriate).
  Record all results, launch boundaries, cache policy and host load. Compare paired
  ratios plus spread; retain outliers and state any invalidated run with reason.
  Do not flush shared-host caches or create load without a separate decision.
- If a result is slower beyond observed noise, investigate the affected path and
  fix it. If noise prevents a conclusion, report that limit and choose the smallest
  informative follow-up; do not broaden automatically into a historical matrix.
  The exact noise assessment/measurement script is reviewed before execution.
- Include startup/layout/I/O/publication in native end-to-end timings, with stage
  measurements to locate overhead. State which service functions and adapters
  actually ran, output equivalence, memory/I/O changes and remaining limits.
  Existing test-suite durations are not native throughput evidence.

M4/M5 changed-boundary qualification should carry this evidence when comparable
execution exists; cumulative M11 acceptance includes the same requirement. Where
only descriptor metadata is implemented, keep numerical speed qualification
explicitly pending. No benchmark is launched by this planning amendment.

## Native Windows difficulty register

Source findings below identify current dependencies/assumptions, not reproduced
Windows runtime failures. Core build/FITS paths take priority over optional tools.
Source membership in a static library is not proof that every function is called
by a selected reduction; compile/link barriers and runtime reachability are distinct.

| Priority / area | Concrete source location and observation | Migration consideration |
|---|---|---|
| Core build gate | [mefpp2/CMakeLists.txt](../../mefpp2/CMakeLists.txt), WIN32 fatal rejection and Linux/Darwin allowlist; required POSIX headers, mmap/munmap, 64-bit off_t and Linux feature macros | Real capability/platform adapters and native compiler checks are needed before removing guards. Changing a platform name cannot establish support. Preserve C90 source baseline and separate C17 compatibility lane. |
| Core file mapping / swap | [qfits xmemory.c](../../mefpp2/qfits5/src/xmemory.c), xmemory initialization/allocation/free/falloc: getpagesize, ftruncate, mmap/munmap, descriptors and unlink of a live mapped swap file | Specify equivalent mapping, page/alignment, cleanup and temporary-file lifetime semantics. Keep the efficient Mac/Linux implementation; qualify a Windows backend without turning all platforms into slower buffered-copy paths. Preserve #164/#168 ownership fixes. |
| Core FITS I/O / large files | [qfits pixio.c](../../mefpp2/qfits5/src/pixio.c), mapped falloc and stdio paths, fopen r/a, fseek offsets and binary stdout; [cache.c](../../mefpp2/qfits5/src/cache.c), fseek-based header/block traversal; [simple.c](../../mefpp2/qfits5/src/simple.c), mmap header access | Review explicit binary stream modes, large-file offsets/size arithmetic and cache behavior under the selected native CRT. Test payload bytes and large offsets; do not assume C long, off_t and pointer widths are interchangeable. No Windows corruption result is claimed here. |
| Core path contracts | [mef_paths.c](../../mefpp2/ins/mef/common/mef_paths.c), resolve/directory/readable/reserve; [mef_input_request.c](../../mefpp2/ins/mef/common/mef_input_request.c), absolute; [mef_runtime.c](../../mefpp2/ins/mef/common/mef_runtime.c), absolute_path | Current absolute checks require leading slash; resolution uses realpath, PATH_MAX, stat/lstat, access, Unix permission bits, slash concatenation and exclusive open. Define drive/UNC, separator, Unicode, alias/case and non-overwrite semantics at an OS boundary. Do not scatter those assumptions into M4 numerical services. |
| Build dependency / optional display | [Eclipse source list](../../mefpp2/cmake/EclipseSources.cmake) includes [image_handling.c](../../mefpp2/src/iproc/image_handling.c), [image_rtd.c](../../mefpp2/src/iproc/image_rtd.c) and [rtd_i.c](../../mefpp2/src/unix/rtd_i.c): System V shared memory and socket/process interfaces | Trace actual RTD/shared-memory use separately from core FITS images. An optional feature may need an explicit supported/unsupported adapter or build selection; do not prune required functions or infer absence from one test. |
| Dependency file locking | [filelock.c](../../mefpp2/src/unix/filelock.c), fopen_lock/fclose_lock: fileno, fcntl locks and sleep/retry | Define locking/timeout/handle behavior for native Windows before changing callers. Preserve failure reporting and avoid extra polling on ordinary native I/O. Runtime use in the reduction under review still needs tracing. |
| Dependency shell/process utilities | [gnuplot_i.c](../../mefpp2/src/unix/gnuplot_i.c), popen/pclose and mkstemp; [pid_i.c](../../mefpp2/src/unix/pid_i.c), kill and ps shell command; [filesys.c](../../mefpp2/src/unix/filesys.c), df through popen; [show.c](../../mefpp2/src/unix/show.c), system | Separate required CLI behavior from optional plotting/display/system helpers. Review argument quoting, process exit propagation, temporary paths and executable discovery; no shell/process launch belongs inside a detector arithmetic kernel. |
| Dependency clock/user/host services | [t_iso8601.c](../../mefpp2/src/unix/t_iso8601.c), gettimeofday; [t_stamp.c](../../mefpp2/src/unix/t_stamp.c), timestamp/identity helpers; [userid.c](../../mefpp2/src/unix/userid.c), Unix identity | Keep acquisition times separate from generated log/product timestamps. Choose platform services without changing science time meaning; avoid new shared mutable buffers in future concurrent calls. |
| Frontends / application boundary | [root configure](../../configure), [mefpp2 configure](../../mefpp2/configure), shell/make entry points; Pycavi process priority/launch plus external astronomy engines are separate layers | Native CMake can be a build boundary, but current shell-front-end availability and resources still need a native distribution decision. WSL is not native Windows acceptance; mefpp support does not establish the entire Pycavi/external-tool application stack. |

For future port changes, record the affected interface/callers, whether the path
is required or optional, proposed adapter/feature disposition, data/ownership/error
semantics and tests still needed. Do not perform speculative fixes in unrelated
dependency files while extracting a numerical subroutine. Existing Unix-specific
support is an acknowledged platform limitation, not a reason to reopen accepted
Mac/Linux numerical results or repeat their past campaigns.

## M4 design consequences and status

Keep layout/identity discovery and file opening at the I/O boundary; detector
kernels receive validated planes/configuration and retain efficient array access.
Carry only required metadata through request/result ownership. Review any new
full-frame allocation/read, persistent cache or OS call for its Mac/Linux purpose
and performance cost. Windows findings may be recorded without changing that
design. Windows-specific adapters belong to a later port, if undertaken.

Documentation/source review only: no compiler probe, build, benchmark, profile,
observation reduction, dependency upgrade, Windows execution or installation ran.
Actual performance preservation remains unmeasured until the changed native path
is compared. This amendment does not move Windows ahead of the existing roadmap
or authorize replacing mefpp's C numerical implementation.
