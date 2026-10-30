# qfits private swap files — correction candidate

30 October 2026. Owner authorized resolving #164 after accepted/merged PR #167,
main `d8f855106edda9639d6a0ad4b2ba2af964a11b84`. The adjacent unowned-path cleanup
finding is #168; a development probe-oracle correction is #169.

## Behavior and ownership

When the existing mode-2 allocator cannot obtain RAM (or its existing Linux
allocation-limit policy selects fallback), it creates private disk-backed memory.
The correction supplies the missing creation mode, uses `O_CREAT | O_EXCL` and
owner-only `0600` permissions, and removes the old world-writable fchmod. A
pre-existing file or symlink causes controlled allocation failure without being
opened, overwritten, or removed. The effective mode may be more restrictive
under the caller's umask; it is never widened to group/other access.

Swap length and registration arithmetic are bounded before opening. The file is
sized with checked ftruncate; existing zero-fill writes are retained, with short
writes completed, EINTR retried, and zero-progress/hard errors rejected. mmap
retains MAP_PRIVATE and the existing logical allocation/accounting model.

After mapping, the created name is unlinked before the pointer is published.
Its open descriptor/mapping keeps the storage alive until release. This also
allows safe scratch-directory changes after all live swaps are released. A
process terminated after successful allocation has no named swap left behind.
Termination during the brief create/write/map/unlink construction window is not
covered by that guarantee; this is POSIX named-file creation, not a new anonymous
storage backend. Named files from an interrupted construction are retained
attempt evidence, not automatically swept later.

Normal free, fdealloc and exit cleanup use one registered-owner release helper.
Exit cleanup visits live swap entries only, with a fast return when none exist;
it no longer deletes all generated names. It is an ordinary atexit handler, not
an async-signal handler. This prevents cleanup from deleting files it never
created, including stale names and collision sentinels (#168).

A failed munmap keeps its registration available for exit cleanup. A close error
is reported and never blindly retried because close may already have released
the descriptor. Explicit release failures terminate with a nonzero status;
normal exit cleanup reports errors and continues best-effort cleanup. Allocation
failures retain the existing fatal policy, cleaning acquired construction
resources and reporting cleanup failures. Process teardown is the final OS
resource backstop. No universal guarantee is made for persistent/multiple kernel
or filesystem cleanup failures. Global serial state and other allocator APIs
are unchanged; there is no new production fault-injection switch.

RAM numerical processing, source configuration catalogs, the two-million-entry
table, memory mode, MAP_PRIVATE policy and working installations are preserved.
This does not redesign real OS swapping, memory budgeting, huge allocations,
thread safety, or broader Eclipse failure propagation (#144).

## Focused qualification

See [agent results](qfits-swap-agent-results-2026-10-30.md). New CTest
`native_qfits_swap` uses `qfits_swap_probe`, which compiles the actual allocator
source with local malloc/POSIX syscall seams, the same mode/table size, and no
alternative implementation. Python only orchestrates bounded child processes.
All physical storage and successful syscalls use the real OS; injected outcomes
exercise selected error branches without exhausting RAM or filling a disk.

Twenty cases cover ordinary RAM, allocation boundaries, zero-filled storage,
0600 permissions under a permissive umask, free/fdealloc, retained allocations,
realloc copy/zero-fill, scratch selection, normal exit, explicit SIGTERM after
successful allocation, interrupted/short writes, open/truncate/write/map/unlink
failures, collision files/symlinks, unowned cleanup names, overflow guards, and
unmap/close failure handling. Cases run from unrelated private caller dirs with
scratch paths containing spaces. The exit observer checks ownership counters,
retained RAM, and descriptor state within its documented 0..255 observation
range. The explicit termination case relies on OS teardown and checks absence
of owned named files; it does not run atexit observers.

The close fault models an error returned after a real successful close; it
specifically guards against retrying an already released descriptor. The unmap
fault occurs once during explicit release, allowing exit cleanup to exercise the
retained registration. This bounded single-fault matrix is not proof against
all possible simultaneous, permanent, or real low-memory kernel failures.

The affected regression remains `native_explicit_paths`: real mefpp calibration,
science and split processing on tiny OmegaCAM/WFI fixtures, with exact legacy
pixels/relevant metadata and preserved inputs/callers. No production Pycavi
method or observation dataset is exercised. No scientific tuning is authorized.

Build the normal executable and qfits_swap_probe privately with the selected
Mac/Chapman tools; run only native_qfits_swap and native_explicit_paths. C90 is
the default; agent C17 and optimized fortify/ASan/UBSan lanes qualify compatibility
and the affected allocator. Actual selected-tool Mac and representative shared
Chapman C90 verification remains pending. Keep #164/#168/#169 open until their
target gates pass, then record correction evidence before closing. Owner review
precedes merge/cleanup; no install or configured-engine activation follows.
