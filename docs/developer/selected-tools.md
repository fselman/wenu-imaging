# Selected project tools — Mac and shared Chapman installations

Owner instruction, 29 October 2026: always select the tools already chosen for
wenu-imaging. This file is the canonical selection record. Read it before
preparing host commands, native builds, tests, installation or dependency work.

## Mandatory selection rules

31 October M4 runner correction (#193): these are executable **invocation paths**.
Do not substitute a symlink's resolved target for the selected command: tools
such as ar/ranlib may dispatch by their invoked basename. Record canonical
target/hash separately as provenance. The selected Mac archiver and ranlib stay
`/usr/bin/ar` and `/usr/bin/ranlib`; xcrun discovery is not a replacement selection.
The first M4 qualifier incorrectly dereferenced supplied Xcode entry points and
failed in static archiving before tests. Retain that failed run; use this record
directly for the corrected task, without another PATH/tool-discovery gate.

1. Use absolute tool paths from the tables below. Do not select tools through
   PATH, a bare `cmake`/`ctest`/`cc`/`gcc`/`python`, Conda activation alone,
   or an inherited `CC`. In particular, Chapman system CMake 2.8.12.2, its
   GCC 4.8.5 and the inherited OpenMPI compiler wrapper are not the selected
   project build tools. Mesa SDK gcc/ar on the Mac are not selected either.
2. Consult this record of private installations before proposing a new download,
   installation, compiler upgrade, manual build workaround or tool replacement.
   An old version returned by `command -v` says nothing about the private tools.
   Chapman3 and Chapman4 are owner-confirmed copycat hosts with shared homes:
   do not add per-host availability, version, hash or ABI checks, reinstallations
   or repeated qualification for these already selected tools. Use them directly.
   If normal task execution fails, report the failure; never silently fall back.
3. Use explicit CMake compiler, archiver, ranlib and make-program arguments,
   the selected Python interpreter, and the Mac SDK/architecture. Record selected
   paths and reuse the established identities in provenance; do not introduce
   redundant tool-check commands as a new gate. Use a fresh build directory
   or source export, rather than reusing a cache configured with other tools.
4. Inspect inherited build variables. Do not let CC/CXX/CFLAGS/CPPFLAGS/LDFLAGS,
   a toolchain file or an old cache silently select another compiler or flags.
   Pass the reviewed values explicitly for the task. Do not edit login startup
   files, global PATH, Conda packages or the user's MPI environment to achieve
   selection.
5. Keep ANSI C90 as the default source/build mode; C17 is the explicitly
   requested compatibility lane. The parser's private C99 qualification does
   not authorize a C-standard upgrade of mefpp. Do not repeat accepted platform
   matrices or dependency tests merely to select the already qualified tools.
   A task's new Chapman verification runs once on a representative Chapman host;
   do not duplicate it on Chapman3 and Chapman4 as separate platform environments.
6. Lower batch build/test priority with `nice -n 10`; leave interactive
   notebooks at normal priority. Use the task's reviewed parallelism (currently
   two build jobs for bounded native checks), not every CPU visible on a host.

## Intel Mac — development

Host: MC02VV0HPHTDG, macOS 13.7.8, x86_64. Repository:
`/Users/fselman/Developer/wenu-imaging`.

| Tool | Selected absolute path | Recorded identity |
|---|---|---|
| Python | `/Users/fselman/anaconda3/envs/wenu-imaging/bin/python` | Conda-forge Python 3.11.14; do not use base Python |
| C compiler | `/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang` | Apple Clang 15.0.0, clang-1500.1.0.2.5 |
| CMake | `/opt/local/bin/cmake` | 3.29.3 |
| CTest | `/opt/local/bin/ctest` | Companion to selected MacPorts CMake; used in returned Mac M1 check |
| Make | `/usr/bin/make` | GNU Make 3.81 |
| Archiver | `/usr/bin/ar` | Apple system tool; bypass Mesa SDK ar |
| Ranlib | `/usr/bin/ranlib` | Apple system companion |
| SDK | `/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk` | Explicit SDK used by accepted private native checks |

CMake selection arguments (add the task's source/build paths, flags and options):

```bash
-DCMAKE_C_COMPILER=/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang
-DCMAKE_AR=/usr/bin/ar
-DCMAKE_RANLIB=/usr/bin/ranlib
-DCMAKE_MAKE_PROGRAM=/usr/bin/make
-DCMAKE_OSX_SYSROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
-DCMAKE_OSX_ARCHITECTURES=x86_64
-DPython3_EXECUTABLE=/Users/fselman/anaconda3/envs/wenu-imaging/bin/python
-DMEFPP_C_STANDARD=90
```

Use `-G "Unix Makefiles"` for these reviewed Make-based builds. MacPorts
`/opt/local/bin/gcc-mp-13` was inventoried but is not the default selected lane;
do not switch to it automatically. The CTest companion selection is established; no extra standalone version check
is required for tool selection. The returned M1 output did not print that version.

## Chapman hosts — shared production installation

The owner confirms that the Chapman machines are the same and share home
directories. The following paths therefore name shared installations, not
independent environments to reinstall for each hostname. `/home/fselman`
resolves to `/home1/fselman` in the returned Chapman evidence.

Repository: `/home1/fselman/Software/wenu-imaging`.

| Tool | Selected absolute path | Recorded identity |
|---|---|---|
| Python | `/home/fselman/.conda/envs/wenu-imaging/bin/python` | Conda-forge Python 3.11.14 |
| C compiler | `/opt/rh/devtoolset-10/root/usr/bin/gcc` | GCC 10.2.1, Red Hat 10.2.1-11 |
| CMake | `/home/fselman/opt/cmake-3.29.6/bin/cmake` | 3.29.6; shared private installation |
| CTest | `/home/fselman/opt/cmake-3.29.6/bin/ctest` | 3.29.6; shared private installation |
| Make | `/usr/bin/make` | GNU Make 3.82 |
| Archiver | `/usr/bin/ar` | GNU binutils 2.27-44.base.el7_9.1 |
| Ranlib | `/usr/bin/ranlib` | System binutils companion |

CMake/CTest were qualified previously on Chapman3 and confirmed executable on
Chapman4 on 29 October 2026. The owner explicitly instructed that no further
checks between these copycat hosts are needed. Chapman4 returned these resolved paths and SHA256s:

| Executable | Resolved path | SHA256 |
|---|---|---|
| CMake | `/home1/fselman/opt/cmake-3.29.6/bin/cmake` | `4a6c99a21c507cd35f51acd017e995a562eb6e5e23218b0cc96e91543c4fa953` |
| CTest | `/home1/fselman/opt/cmake-3.29.6/bin/ctest` | `480bbe71f45fb1ad8186df33db14c405b9556dc495e45a6b687c6736d0bb471d` |

CMake selection arguments:

```bash
-DCMAKE_C_COMPILER=/opt/rh/devtoolset-10/root/usr/bin/gcc
-DCMAKE_AR=/usr/bin/ar
-DCMAKE_RANLIB=/usr/bin/ranlib
-DCMAKE_MAKE_PROGRAM=/usr/bin/make
-DPython3_EXECUTABLE=/home/fselman/.conda/envs/wenu-imaging/bin/python
-DMEFPP_C_STANDARD=90
```

Use the selected absolute CMake and CTest paths and `-G "Unix Makefiles"`.
The observed `CC=/usr/lib64/openmpi/bin/mpicc` must not select the compiler
for these serial builds; leave the user's environment intact and override
selection explicitly in the command. A shared installation is not a claim that
every processing test has run on every Chapman hostname. Record the actual host
for each execution and reuse the common environment qualification. No further
Chapman3-versus-Chapman4 tool checks are needed. New task-specific verification
is separate from rechecking existing tools; do not duplicate it solely by hostname.

## Workspaces, dependencies and science executables

Permanent reusable tools belong beneath `~/opt/`; fresh builds, private
qualification prefixes and retained evidence belong beneath
`~/Software/build/wenu-imaging/`, with tool evidence under `tools/` and retired
runs under `archive/`. Archived build trees contain historical absolute paths
and are evidence, not reusable active builds. Do not relocate active tools or
build caches as an incidental cleanup.

The selected C TOML implementation is the pinned, MIT-licensed copy under
`third_party/tomlc17/`, with `upstream.json` and `README.wenu.md`. Do not fetch
latest upstream or select a system TOML library implicitly. Python 3.11 provides
`tomllib`. ASDF 6.0.0 / asdf-standard 1.5.0 and their constrained closure passed
private paired qualification; that is not an instruction to activate/install
them into the normal Conda environments. Follow the
[dependency gate and adoption status](toml-asdf-chapman-qualification-2026-10-29.md).

External science executables are selected by the applicable explicit
`pycavi_astrosoft.cfg`, including private per-run configurations. Read and record
that selection instead of choosing same-named executables on PATH. Preserve the
user's existing configuration and installed engine. On the Mac, the recorded
normal configuration is `/Users/fselman/.pycavi/pycavi_astrosoft.cfg`, selecting:

| Program | Recorded Mac configured executable |
|---|---|
| mefpp | `/Users/fselman/opt/local/mefpp/bin/mefpp` |
| solve-field | `/usr/local/Cellar/astrometry-net/0.95_2/bin/solve-field` |
| Source Extractor | `/opt/local/bin/source-extractor` |
| SCAMP | `/Users/fselman/opt/scamp-2.10.0-wenu-imaging/bin/scamp` |
| SWarp | `/opt/local/bin/swarp` |

These paths are recorded selections, not authority to overwrite a newer explicit
project configuration or install/switch a candidate automatically. Obtain Chapman
science-executable paths from its applicable configuration rather than copying
Mac paths or inventing cluster locations. A source refactor does not authorize
upgrading external astronomy programs.

## Evidence and current correction

- [Permanent Chapman tool installation and qualification](chapman3-native-acceptance-2026-10-26.md).
- Returned Chapman4 preflight: Linux EL7 x86_64 / glibc 2.17, shared Python,
  GCC 10.2.1 and the CMake/CTest identities above.
- Returned Mac M1 private C90 CMake build and focused CTest passed at
  `5d660b9dfc15aada9b4bdeef5bce998f6b36fe9e`, under
  `/Users/fselman/Software/build/wenu-imaging/mac-m1-config-eKZqE79j`.
  Its test report is `build/test-work/m1-config-hjhrbyzp/run-provenance.json`.
  This is returned terminal evidence, not an independently transferred archive.
- The earlier PATH-only Chapman4 preflight found system CMake 2.8.12.2.
  Interpreting that as a need for a new tool or direct-compiler workaround was
  incorrect. The workaround was not published; use the shared CMake/CTest.
  The subsequent Chapman4 private C90 configure/probe build and focused CTest
  passed at e5c3aba6e6b35530f528eb4942e54bd8e3b47884; see the
  [paired M1 receipt](m1-config-paired-results-2026-10-29.md). No recheck of
  the shared tools or duplicate Chapman3 execution is needed.
