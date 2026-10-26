# mefpp / qfits build and installation audit — 25 October 2026

## Authorized change and boundary

Fernando explicitly brought roadmap point 5 forward: establish that mefpp can
be built and installed on Intel macOS, then chapman3, starting with an audit of
the installation procedure. He requests moving qfits into mefpp. This is the
first audit deliverable and migration design, not the source move, build-system
correction, compiler upgrade or replacement of either working installation.
The remaining notebook/Python audit order resumes after this bounded native
installation task; it is not silently cancelled.

Tracking: [#64](https://github.com/fselman/wenu-imaging/issues/64).
Source baseline: main 2cd54c1206ccb7b68b2eb0a5f70d9b28f1188cde.
Native trees (unchanged since the inspected checkout):
mefpp2 8d0bc2a81da4be75b5b5d0017bd0e9e83207e25b;
qfits52 af5c2837c22b66a0388b9ccd866df3eb0ccf1fc3.
Earlier working source/installed Mac reductions prove those selected binaries
execute; they do not prove a clean build/install from this source.

## Current package boundaries

| Layer | Current source | Build/install role |
|---|---|---|
| qfits | qfits52 | ANSI C FITS/header/table/PAF and memory support; libqfits.a by default, optional shared path and ten CLI tools |
| Eclipse | mefpp2/src | libeclipse.a and legacy utilities, linked against qfits and libm |
| pfits | mefpp2/ins/pfits | libpfits.a and a small test target; mefpp recipe's listed link libraries do not include pfits |
| mefpp recipe | mefpp2/ins/mef | mefpp executable, common C routines and PAF/static BPM resources |
| Pycavi | Pycavi2 | Calls installed mefpp; needs selected binary plus config/static_cal resources, not Python qfits bindings |

The ordinary native C path uses a C compiler, POSIX shell, make, ar/linker and
math/system libraries. mefpp installation additionally invokes external funpack
for distributed compressed BPMs. setuptools is listed in legacy mefpp dependency
documentation but is not used in this ordinary C build. qfits_wrap.c uses Python.h
and its historical Python interface is not the supported Pycavi path; porting
that interface is not required for this installation milestone.
No new package manager/framework is needed merely to combine the source trees.

## Current installation procedure and the nesting mismatch

The old installation page describes installing qfits separately, then configuring,
building and installing mefpp; it recommends make -B install and e_setup.
The root mefpp INSTALL instead describes an older general Eclipse distribution.
The defaults /opt/local/qfits5 and /opt/local/eclipse are system-oriented and
inconsistent with the working home-prefix mefpp selection. Some examples use an
en dash instead of the ASCII double dash needed for configure options.

mefpp2/Makefile already contains pkg_qfits5, looking under ./qfits5 and running
configure/make there, but it does not propagate the parent compiler/options/prefix.
mefpp2/sysconf.c searches ./qfits and ../qfits, plus several system prefixes;
it does not automatically search the proposed ./qfits5 or current ../qfits52.
It searches only for include/qfits.h and include/xmemory.h, not a built archive.
An explicit --qfits path bypasses the automatic header check and is converted
with config_abspath without robust failure handling.
Thus a bare directory move can still prompt interactively, select a system copy
or fail later. Dependency selection must become explicit and noninteractive.

## Findings and reproduced evidence

| Finding | Evidence / severity | Tracking |
|---|---|---|
| configure hides failure | Both scripts return 0 after failing compiler stubs or an unsupported OS argument; help attempts to move absent config.h | #65 |
| Recursive failure/dependency graph | Real qfits progs recipe returns 0 after a child make exits 23. Libraries/tools and mefpp package stages lack explicit dependency edges; incremental relinking can miss changed archives | #66 |
| Incomplete install succeeds | Both original install recipes return 0 in isolated fixtures with no built products and install no files. No install build prerequisite or complete manifest | #67 |
| Compiler configuration | CC environment is not selected end-to-end. Forced Darwin/cc qfits generator emits CFLAGS = -g -O3 RELOC = -fPIC on one line, with no separate RELOC assignment | #68 |
| Source artifacts/provenance | Tracked mefpp commands/e_setup is a Mach-O x86_64 binary, rebuilt only by timestamp; tracked config headers identify different OSes; clean handling is insufficient | #69 |
| Empty check target | No shipped qfits test directory; make check returns 0 without tests. No top-level installed-native qualification in mefpp | #70 |
| Runtime exit caution | Source main discards mef_engine's failure result and returns 0. Not runtime-reproduced here; installed acceptance must check actual outputs | #71 |

Additional installation consequences and limits:

- qfits and mefpp configure bootstraps use hard-coded cc/gcc, suppress bootstrap
  diagnostics, forward unquoted $*, ignore sysconf status and can move stale
  generated headers after failure. Compiler/flag environment conventions are
  not consistently honored; command-line make CC overrides are a workaround,
  not a coherent configure contract.
- qfits GCC flags include -Wa,-q on all OSes. The trivial GCC 13.3 Linux probe
  accepted it; no Linux rejection is claimed. A forced Darwin generator test
  on Linux is not a Mac compilation. qfits default static linkage is the
  immediate baseline; optional raw-ld/-shared/.so handling on Mac is unqualified.
- qfits all lists archive targets and progs independently, permitting a parallel
  tool link before its library. mefpp's default lists package stages independently;
  pfits is traversed twice. Library/header dependencies and fresh helper rebuilds
  need review before claiming reliable make -j or incremental rebuilds.
- Installation uses unquoted paths, no DESTDIR, conditional missing-file skips,
  broad wildcards and unrelated sentinels (e.g. 3color controls copying binaries).
  make -B is not an installation design or a substitute for a valid dependency graph.
- mefpp copies compressed BPMs into the destination then runs bare funpack there.
  Availability, failure/partial writes, existing output behavior and repeat
  installation are not controlled. Do not silently overwrite working PAFs/masks.
- No install manifest, bounded uninstall or installation of both license notices
  is defined. Current source permissions allow redistribution subject to their
  retained notices; preserve both mefpp LICENSE and qfits LICENSE when nesting.
- qfits README.md says 5.0.0, imported tag history says 5.0.1, but src/version.c
  reports 5.4.0. The mefpp recipe reports 2.0.0. Resolve identities through
  commits/tree/archive hashes; do not rename versions to reconcile guesses.
- Preserve qfits memory mode, 2000000-pointer default and floating-point/compiler
  semantics initially. Large static memory tables matter to target smoke-test
  resources; changing these limits is not an installation-only correction.
- e_setup can write ~/.eclipse-rc. Do not run it as a hidden install side effect;
  the existing Pycavi binary/resource selections must remain explicit.
- Existing runtime metadata/BPM/detector issues (#23/#24/#13 and detector-identity
  TODO) are not repaired or scientifically accepted by a successful installation.

## Probe execution and limits

The [reproduction script](audits/native-install-2026-10-25/probe.py) ran twelve
bounded probes on the agent Linux x86_64 host using GCC 13.3 and GNU Make 4.3.
It compiles only the small configure bootstrap and a trivial flag-test unit;
it does not build either scientific library or execute a reduction.
Compiler/child failures are deliberate fixtures, not modifications to production.
Install prefixes and all generated files are private temporary directories.
All copied source files were rehashed unchanged.
[Results](audits/native-install-2026-10-25/results.json) and adjacent logs retain
the observed statuses, including the successful Linux assembler-flag probe.
These are baseline reproductions, not regression tests that a future fix should
continue to satisfy, and not target Mac/chapman3 qualification.

To reproduce on a deliberately selected audit host, run probe.py with explicit
--source and --records-parent in fresh scratch. Explain the tested sections
before execution per the agent policy. Do not confuse a reproduced defect
(exit 0 where failure was expected) with a passed production gate.

Historical Mac evidence remains in
[the installation history](mac-installation-history-2026-10-20.md) and
[functional CP Pup pilot](pilots/mac-cp-pup-2017-03-13/README.md).
qfits previously built in disposable Mac compiler trials, but full install
evidence was not supplied there. The selected mefpp binary has partial debug
provenance; its exact linked qfits source identity is unresolved.
No full clean source build/install was performed on the agent, Mac or chapman3
during this first audit.

## Proposed move and installation contract

Recommended source destination: **mefpp2/qfits5**, one canonical copy, retaining
qfits include files, library/tool names and separate license. Keep the public
mefpp executable/import/resource contract; remove the top-level qfits52 copy
when the actual move is implemented, and update live references rather than
duplicating source. Historical pinned-path documentation remains historical.

Recommended build ordering:
qfits static archive (and selected utilities) -> Eclipse archive -> mefpp.
Bundle discovery must select that exact source/build, not silently use a
system archive. Explicit external qfits selection, if retained, must be an
opt-in with validation, recorded identity and target-compatible link checks.

Separate source/build artifacts from the final installation. A staged source
copy is acceptable for the first bounded correction if full out-of-tree support
is not adopted; do not claim --build-dir behavior that has not been implemented.
Support one user-owned prefix and DESTDIR-style staging. The minimum Pycavi
runtime payload should include:

- bin/mefpp.
- config/mefpp.paf, config/omegacam.paf and config/wfi.paf.
- static_cal/OCAM_BPM_1x1.fits and static_cal/WFI_BPM_1x1.fits, verified after
  decompression; retain compressed inputs or provenance by an explicit policy.
- License notices for both source components and an installed manifest recording
  source/tree identity, compiler/flags, platform, archive hashes and resources.

The exact location/name for manifests and optional qfits/Eclipse tools,
developer headers/archives/manuals remains an implementation choice to document.
Do not make general Eclipse utilities or interactive e_setup implicit requirements
for a minimal Pycavi runtime. Preserve any deliberately retained legacy payload
through an explicit option; avoid silently dropping it.

Start with static qfits/Eclipse linkage. macOS otool -L and Linux readelf/ldd
show dynamic dependencies but do not establish the identity of static qfits
objects; retain linker commands and archive identities too.
The existing old prefixes and current Pycavi configuration remain unchanged
until a candidate passes acceptance and Fernando selects it.

## Target sequence and acceptance gates

1. **Mac inventory, read-only:** fresh hostname/Git/prefix evidence; compiler
   paths/versions, Xcode SDK, make/ar/linker, funpack and existing native resource
   identities. Read existing configuration without invoking interactive e_setup.
2. **Bounded correction after this audit:** move qfits, repair the recorded build/
   install interfaces and documentation. No algorithm, dependency-version,
   detector mapping, native concurrency or science-policy change.
3. **Mac clean build:** fresh source/artifact directory, explicit compiler, no
   inherited system qfits, private prefix, full configure/build/link logs.
   A failed attempt stays evidence; no broad compiler relaxation hidden in scripts.
4. **Mac installation checks:** complete manifest, expected executable/PAFs/BPMs,
   correct architecture, link dependencies, installed FITS/PAF smoke checks and
   safe second installation. Negative compiler/build/install checks must fail
   truthfully. No-op make check or zero native exit is insufficient.
5. **Mac bounded functional comparison:** use disposable copies of the accepted
   03 raw/master/BPM/PAF inputs if agreed; verify complete expected detector
   products and preservation, distinguishing software/numerical equivalence
   from scientific revalidation. Do not rebuild all calibration/science data.
6. **chapman3:** inventory its actual compiler/toolchain and repeat the accepted
   build/install/negative/smoke protocol in a fresh user prefix, after Mac gates.
   Do not substitute the agent's Linux host or its GNU versions.
7. Record target results, then explicitly select any new native installation.
   Resume the remaining agreed Pycavi stages; scientific Kriging optimization
   stays deferred until all fields are reduced.

The user's requested roadmap reordering is approved. This initial report does
not claim implementation, successful target builds, completed source migration,
merging, native selection or closure of the listed defects.
