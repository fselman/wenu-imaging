# qfits swap correction — paired results, 30 October 2026

Selected-tool Intel Mac and representative shared Chapman4 passed private
optimized C90 builds and both affected CTests at
`471f42e19e304e16872291172535e855a2f826d9`, tree
`4bfd7d469501fc687f5261a4aab692f275f57c0a`, in PR #170. Protected installed
files and clean review checkouts stayed unchanged. The bounded correction is
ready for owner review; full M3 remains open under #159.

See [the correction contract](qfits-swap-files.md) and retained
[agent results](qfits-swap-agent-results-2026-10-30.md). The missing O_CREAT mode
(#164), unowned-path exit cleanup (#168) and probe realloc oracle (#169) have
passed their applicable agent and actual target gates. Record correction/paired
evidence comments before closing these bounded defects. This is not full
allocator/dependency OOM, LeakSanitizer or scientific acceptance.

## Returned actual target results

| Target | Forced swap | Native path regression | Total |
|---|---:|---:|---:|
| Intel Mac MC02VV0HPHTDG | Passed, 1.76 s | Passed, 26.37 s | 2/2, 28.14 s |
| Shared Chapman4 | Passed, 0.24 s | Passed, 19.45 s | 2/2, 19.70 s |

Retained private work directories:

- Mac: `/Users/fselman/Software/build/wenu-imaging/mac-qfits-swap-g03oro0r`
- Chapman4: `/home1/fselman/Software/build/wenu-imaging/chapman-qfits-swap-g7vrzzu_`

Each contains export/extract/configure/build/test-inventory/tests logs,
run-provenance.json and private exported source/build/fixture directories.
These are owner-returned console results from the guarded command groups.
Raw host files remain at these locations and have not been downloaded or
independently reread by the agent. Times identify attempts, not benchmarks.

The groups guarded OS/hostname, resolved repository, origin fetch/push, branch,
exact HEAD, upstream and clean state. They exported tracked source at the exact
revision and selected the established absolute compiler, CMake/CTest, Python,
make/ar/ranlib paths; the Mac used explicit SDK and x86_64. Both built C90 Debug
with `-O1 -D_FORTIFY_SOURCE=2`, two jobs, niceness 10 and numerical thread limits
of one. Inherited build-selection variables were removed for child commands.
The normal mefpp and qfits_swap_probe were built with resources disabled and no
installation. Test inventory required exactly native_qfits_swap and
native_explicit_paths before running them. No compiler/dependency requalification,
historical matrix or target C17/sanitizer replay was added.

## What passed

The new test compiles actual qfits allocator source with probe-local malloc and
POSIX syscall seams, preserving mode 2 and the two-million-pointer table. It uses
real successful file/descriptor/write/mmap calls, plus bounded injected outcomes
without exhausting memory or filling disks. No production fault API or substitute
allocator is used. The normal executable links ordinary corrected qfits.

Twenty cases cover normal RAM, swap size boundaries/zero bytes, actual 0600
creation under permissive umask, unlinked live backing, normal free/fdealloc/exit,
retained RAM and swap contents, realloc copy/extension, scratch selection,
interrupted/short-write recovery, open/truncate/write/zero-write/map/unlink
failures, real file/symlink collisions, unowned cleanup sentinels, size/registration
overflow and unmap/close failure handling. The explicit SIGTERM case terminates
after successful allocation and checks no owned name survives; it does not run
atexit observers. Ordinary cases observe counters and descriptors in the bounded
0..255 range after cleanup, with untouched unowned sentinel data/modes/mtimes.
The close error is modeled after actual close; the one-shot unmap error during
explicit free leaves its registration for exit cleanup. These are bounded
single-fault controls, not a universal guarantee for persistent/multiple errors
or process death during construction before unlink.

The native regression calls actual mefpp C processing and existing numerical
routines on tiny OmegaCAM/WFI bias/BPM/dome/sky/master-flat/science/split fixtures.
Its 16 positive profiles/14 controlled rejections retain exact legacy pixels and
relevant FITS cards/order, independent known arrays and protected inputs/callers.
No production Pycavi method or real observation dataset is processed. The Python
drivers create and verify private fixtures only; no scientific tuning is implied.

Host protection discovers the actual installed nested reduction module and reads
the selected engine from [Paths] mefpp in the actual configuration. Both hosts
returned PASS for installed module/configuration/engine resolved identities,
bytes, modes and mtimes, and for the complete checkout state remaining unchanged.
Chapman canonical /home1 paths are retained; locale/home aliases were not changed.

## Status and limits

PR #170 is ready for bounded owner review. #164/#168/#169 are target-qualified
and closed after their correction/evidence comments. Original full M3/#159,
long FITS strings #125 and wider Eclipse allocation-failure propagation #144
remain open. Earlier agent results retain the explicit container LeakSanitizer
limitation; passing focused address/undefined checks are not whole-dependency
leak/OOM or thread-safety acceptance. RAM-first/MAP_PRIVATE/serial policy, table
size, numerical algorithms, catalog values and user installations are unchanged.

This receipt changes documentation only; tested code/tests are unchanged and
need no replay. Preserve all original/corrected evidence and selected tools.
Owner review and separate merge/cleanup instruction remain required. No install,
configured-engine activation, new JSON policy or milestone reordering follows.
