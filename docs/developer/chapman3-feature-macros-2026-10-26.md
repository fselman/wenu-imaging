# Chapman3 legacy-glibc build correction — 26 October 2026

Issue: #89. Parent: 81a2f742ad439245739601444e7ffe70cb119037.
Status: actual Chapman3 C90/C17 build, installed failure and direct CN Ori
checks passed at source 805e6c63. Installed corrected Pycavi imports/failure
regressions and four two-filter/C90/C17 observational comparisons also passed. See [current acceptance](chapman3-native-acceptance-2026-10-26.md) for
returned target evidence, reviewed timing differences and relocation maps.
Earlier pending statements below describe the preceding implementation phase.

## Actual target evidence

Fernando reports Chapman3 x86_64/CentOS 7/glibc 2.17, Git 2.34.1, clean checkout
at /home1/fselman/Software/wenu-imaging (logical home /home/fselman).
The existing imaging Python is 3.11.14. Existing system GCC 4.8.5, Clang 3.4.2
and CMake/CTest 2.8.12.2 were retained.

Available devtoolset-10 GCC 10.2.1 was selected without a compiler upgrade.
The official CMake 3.29.6 Linux x86_64 archive was downloaded to a fresh private
directory and checked against Kitware's release checksum list:
28fef61e64840b784da6db35218fd3ae179ff8bf0be1c8a9d075d6185a0e4fdc.
Private CMake and existing GCC passed a synthetic C90/C17 configure/build/CTest
probe, including explicit language flags and 64-bit off_t:
 /home/fselman/wenu-cmake-3.29.6-check-h4i7yr9s/toolchain-check.json.
This is toolchain qualification, not native mefpp acceptance.

The first actual native build used source 81a2f742 and explicit devtoolset
gcc/ar/ranlib/ld.bfd, private CMake and existing funpack. C90 configuration passed;
compilation stopped in Eclipse image_stats.c because M_PI was undeclared.
sys/ipc.h also emitted its feature-selection warning. C17, CTest and installation
were not reached. Protected tools, working Pycavi package and checkout stayed
unchanged. Preserve:
 /home/fselman/wenu-chapman3-native-build-579kejl8/build-c90.log
 /home/fselman/wenu-chapman3-native-build-579kejl8/build-check.json

These are attributed user terminal reports, not agent access to target files.

## Cause and bounded fix

glibc 2.17 predates _DEFAULT_SOURCE. Its math/math.h exposes M_PI under the BSD
or X/Open feature set; include/features.h selects the older BSD/SVID and POSIX
interfaces. An explicit -std=c90 or -std=c17 does not imply the historical
non-strict default header feature set.

CMake now defines the common feature policy once. Linux additionally receives
_BSD_SOURCE=1, _SVID_SOURCE=1 and _POSIX_C_SOURCE=200809L alongside _DEFAULT_SOURCE.
This expresses the intended default library API scope on old and new glibc;
it does not switch to a GNU C language mode. Darwin production definitions stay
_DEFAULT_SOURCE=1 and _DARWIN_C_SOURCE=1, exactly as before.

The same policy is applied before type/header/capability probes and to native
production targets. Linux configuration checks M_PI and shmget early. The Linux
primitive test uses the same policy and checks math constants and System V
shared-memory type availability, without creating/attaching shared memory.
The CTest entry count stays five.

No numerical C implementation, M_PI value, operation order, source lists,
allocator, calibration policy or working installation changes. No hardcoded
constant replacement, system glibc/compiler upgrade or removal of Eclipse code.
This extends the build qualification slice; it does not reopen the broad
component/memory redesign.

## Verification actually performed

Agent Ubuntu GCC 13.3.0/glibc 2.39 diagnostic builds: all actual 100 translation
units compiled/linked in both explicit C90/C17 modes with the compatibility
definitions. The native primitive executable, including Linux platform-header
checks, passed in both modes. Ten native contract methods with each distributed
OCAM/WFI PAF passed in each mode (40 method runs). These use synthetic FITS and
are not WFI observational acceptance. CMake/CTest was unavailable in the agent
session; configuration probes and the actual old-glibc build require target
execution. See fixtures/agent-glibc-feature-verification.json.

Earlier Mac acceptance remains attributed to its tested code commit
4ade8c52027c736a49b65da3bdb31f11b036693b. This Linux-specific change leaves Darwin
production definitions and numerical C sources unchanged; no new Mac run is
claimed.

## Next target gate

Synchronize the review branch after fresh actual-checkout evidence. Reuse the
qualified private CMake/existing devtoolset paths but export the new source into
fresh per-mode directories; preserve the failed attempt. Repeat native C90/C17
configure/build, inspect feature checks/compile definitions and require all five
CTest entries. Only after that gate continue private install, installed failure
checks and representative native/Pycavi observational comparison. Keep #89 and
the larger Stage 1 gate open until actual acceptance.

Primary source references:
- https://github.com/bminor/glibc/blob/glibc-2.17/include/features.h
- https://github.com/bminor/glibc/blob/glibc-2.17/math/math.h
- https://sourceware.org/glibc/manual/latest/html_node/Feature-Test-Macros.html

## Chapman3 build result and workspace location, 26 October 2026

Chapman3 native build acceptance, 26 October 2026: Fernando reports source
805e6c63dea20e7f5e5ade816f6a6ddc90702d86 passed both required M_PI/shmget
configuration checks, 100-unit C90/C17 builds with the declared feature/language
flags, and all five CTest entries per mode. Evidence is
/home/fselman/wenu-chapman3-native-retry-xkuuu6qu/build-check.json and mode logs.
Protected tools, previous failed-run evidence, working Pycavi package and checkout
remained unchanged. This is build/test acceptance only: no installation or
observational reduction ran. Keep installed/native/Pycavi/calibration/memory and
wider Stage 1 gates distinct; no merge or normal selection switch is implied.

Chapman3 workspace location, requested 26 October 2026: put all future
wenu-imaging build/qualification work under ~/Software/build/wenu-imaging/,
not new ~/wenu-* directories. Use tools/ for private tool bundles and archive/
for retired/failed evidence, with task-specific source/build/prefix directories.
Do not blindly move active CMake trees or toolchains: caches/frontend state and
install scripts retain absolute paths. Inventory existing ~/wenu-* directories,
identify active consumers and preserve evidence before relocating finished work.
Use guarded reversible moves; never wildcard-delete runs, packages or data.
This housekeeping request does not authorize Git branch deletion or removal of
working Pycavi/native installations. Preserve original evidence paths in records
and map any relocation explicitly. Existing home runs remain unchanged until
inspected; the just-qualified native retry still needs its install/regression gate.
