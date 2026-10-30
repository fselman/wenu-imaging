# qfits swap correction — agent results, 30 October 2026

Subsequent status: [paired Mac/Chapman qualification](qfits-swap-paired-results-2026-10-30.md) passed 2/2 on each at published source 471f42e19e304e16872291172535e855a2f826d9. This original agent receipt retains its pre-target evidence and limits; target-pending entries below are historical.

Owner authorized resolving #164 after accepted/merged PR #167 and clean
Mac/shared Chapman main `d8f855106edda9639d6a0ad4b2ba2af964a11b84`.
Branch: `fix/qfits-swap-files`. See [the contract](qfits-swap-files.md) and
[raw retained evidence](fixtures/agent-qfits-swap-2026-10-30/README.md).
Actual selected-tool Mac and representative Chapman verification is pending;
#164/#168/#169 remain open. Full M3/#159 and #125/#144 remain separate.

## Purpose and changes

qfits creates fallback files with explicit 0600 mode and exclusive creation,
checks sizes/truncation/writes/mapping, unlinks created storage before publishing
its pointer, and releases registered mappings/descriptors without sweeping
unowned names. Existing serial mode 2, the two-million-pointer table, MAP_PRIVATE,
RAM allocation and numerical algorithms remain unchanged. Short writes complete
and EINTR is retried; unrecoverable errors retain a failed process result.

The old sweep could remove unowned collision paths (#168). Its cleanup now visits
live owned swap entries, shared with free/fdealloc. Unmap failure during explicit
release retains its registration for exit cleanup. Close is never blindly retried;
a close error may occur after the descriptor is already released. Explicit release
failure is fatal; normal exit cleanup logs errors and performs best-effort release.
No user installation/configuration, observation, catalog or production environment
was altered; no normal configured executable was activated.

## Actual agent checks

All use private GCC 13.3.0, CMake/CTest 3.29.6, selected `/usr/bin/gcc`, ar/ranlib/make,
and private test Python 3.12.14. The new swap driver is Python standard-library
only. The existing native path test uses private NumPy 1.26.4/Astropy 6.1.7 within
project bounds. Source was uncommitted for private builds; build-info honestly
records unknown revision. Final source/test hashes identify exactly what ran.
The build-info inventory is configure-time evidence, predating final edits.

| Lane/action | Expected/actual result |
|---|---|
| Original cleanup reproduction | Exit 1: unowned sentinel was removed by original cleanup |
| Original optimized fortify compile | Exit 1: missing O_CREAT mode rejected |
| Corrected C90, `-O1 -D_FORTIFY_SOURCE=2` | Normal mefpp + probe build; both focused CTests 2/2, 23.39 s |
| Corrected C17, same optimization/fortify | Same 2/2, 22.20 s |
| Corrected C90 optimized ASan/UBSan + fortify | Normal engine + probe build; all forced-swap controls 1/1, 0.72 s |
| Actual selected-tool Intel Mac / representative Chapman | Pending private C90 build and both focused tests |

The actual allocator source is compiled into the isolated probe with local malloc
and POSIX syscall seams. Successful operations use real OS storage and mapping;
selected failures are injected locally without filling disks or exhausting memory.
There is no production fault-injection interface or alternative allocator. The
normal executable links the corrected qfits library without these test seams.

`native_qfits_swap` passes twenty cases: RAM, boundary allocations, normal exit,
explicit SIGTERM after successful allocation, realloc, interrupted/short writes,
open/truncate/write/zero-write/map/unlink failures, file/symlink collisions,
unowned exit-cleanup names, size/registration overflow and unmap/close failures.
Successful allocation checks zero bytes, actual owner-only file mode, unlinked
mapped backing, data patterns and free/fdealloc accounting. Other RAM/swap data
remain intact before cleanup. Its exit observer checks registered swap counts,
logical bytes, retained RAM and descriptor state in its bounded 0..255 range.
The SIGTERM case intentionally has no exit observer and checks no named swap
survives after a successful allocation. Process termination during construction
before unlink is outside this guarantee.

The write recovery controls require their injected fault actually to fire.
All named syscall-failure controls require a failed process and post-cleanup
resource/data checks; unrelated crashes are not accepted as failure handling.
The close seam returns an error after actually closing, testing why retry is
unsafe. The unmap seam fails once during explicit free so exit cleanup observes
the retained owner. Persistent/multiple kernel/cleanup failures and real global
low-memory pressure are not claimed qualified by this bounded matrix.

`native_explicit_paths` passes the actual C engine's 16 positive profiles and
14 controlled rejections, with tiny OmegaCAM/WFI calibration/science/split
products, independent known arrays, exact legacy pixels/relevant FITS metadata,
and preserved inputs/calibrations/caller dirs. No production Pycavi routine or
real observation is called. The accepted CLI matrix is not replayed because its
loader did not change. No historical platform/dependency matrix is replayed.

The initial new probe failed its realloc retained-pattern observer (#169): after
correctly verifying newly grown bytes were zero, it extended the all-0xa5 oracle
without filling those bytes. The corrected probe initializes them only after the
zero assertion. Original copy/zero/owner assertions are preserved; the original
failed log and raw diagnostic remain in the evidence folder.

## Limits and handoff

ASan/UBSan uses `-O1 -D_FORTIFY_SOURCE=2 -g -fsanitize=address,undefined
-fno-omit-frame-pointer`, address/undefined checks halt on error, and leak detection
is explicitly disabled. The known container LeakSanitizer /proc/task failure is
retained in the earlier native-path evidence; it is not replayed or represented
as fixed here. The former optimized compile failure now passes, unlike the prior
O0 workaround. This is not full-dependency LeakSanitizer, OOM, threading, scientific
or complete-M3 acceptance; #144 remains open.

Next: exact-source export, selected-tool private C90 normal-engine/probe builds,
and native_qfits_swap/native_explicit_paths on Mac and one representative shared
Chapman host. Guard/protect the actual installed nested reduction module,
configuration and selected engine; verify checkout preservation even on failure.
Preserve failed/successful attempts and the qualified tools. Do not install,
activate the new engine, close issues, merge or clean without applicable gates
and owner instruction. No change to current JSON policy or milestone order.
