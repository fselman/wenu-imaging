# Native build and qualification specification — version 1

Date: 25 October 2026. Status: Stage 0 design, ready for review; no native build
implementation or installation performed by this change.
Documentation parent: ac841cda13daf887b1153bf053b48d68fb574d44.
Related: [roadmap 1.2](mefpp-modernization-roadmap-v1.md),
[current architecture](mefpp-current-architecture.md), #64 and #73.

## Scope and decisions

Define the first build of the existing serial numerical implementation, its
installed payload and the fixtures needed to qualify it. Do not extract the
future component APIs, enable uncalled linearity routines, add dark/fringe
algorithms, change normalization, prune Eclipse, introduce concurrency, or replace
the existing engine. The candidate build must work without historical qfits or
mefpp include/library directories. Existing working installations are rollback
references, never build inputs to the candidate.

### Initial tools

| Item | Initial selection | Evidence / limitation |
|---|---|---|
| Configuration/build description | CMake; initial minimum 3.29 | Actual Mac 3.29.3 passed the synthetic probe. No newest-version requirement; other supported versions still need testing |
| Test entry point | CTest from the same CMake distribution | Actual Mac 3.29.3 ran two nonempty synthetic tests |
| Generator | Unix Makefiles on the initial Mac | /usr/bin/make 3.81 driver passed; verbose recursive commands used Xcode's make path |
| Compiler | Xcode Apple Clang 15, explicit absolute path | Actual strict C90 and C17 synthetic compilation passed |
| Archive tools / SDK | Xcode ar, ranlib and SDK selected through xcrun | Avoid PATH's MESA ar and Conda ranlib/ld selections |
| Native linking | Compiler driver, with selected platform toolchain | Probe linked through clang; actual subordinate linker invocation was not independently traced |
| Linux compiler | Pending compatible isolated modern GCC selection | chapman3 system GCC 4.8.5 / Clang 3.4.2 cannot supply C17 qualification |
| Windows / Apple Silicon | Required later native qualification | No current target build or runtime evidence |

Ninja 1.12.1 exists on the Mac but is not required for the first build. Initial
CMake 3.29 minimum is a bounded selection based on available evidence, not a claim
that every feature needs 3.29. If chapman3 availability justifies a lower minimum,
review that change and test it explicitly rather than silently using older syntax
or upgrading system software. CMake/CTest themselves need a compatible installation
on glibc 2.17; a current downloaded Linux binary is not presumed compatible.

Keep C89/C90 as the portable numerical source baseline and qualify a separate C17
build. CMake target properties must require the selected standard and disable
language extensions where supported. Audit existing GNU/POSIX dependencies and
conformance diagnostics instead of claiming the legacy sources are already strict
C90. Necessary compatibility corrections remain bounded, numerically tested work.
No C++ compiler becomes a mefpp implementation dependency. Compiler-bootstrap C++
requirements, if needed to obtain GCC, belong to toolchain provisioning separately.

## Observed native build and proposed targets

The source lists come from the current tracked Makefiles, not the static-use
subset. Eclipse has 79 archive translation units and qfits 18. Start with those
complete lists: reducing them to the 53/14 object-closure estimate is not part of
this task. The MEF recipe links -leclipse -lqfits -lm; pfits is not on that line.

| Proposed CMake target | Type | Sources / dependencies | Default / install policy |
|---|---|---|---|
| qfits | STATIC library | Current qfits52/Makefile SRCS; future location mefpp2/qfits5; generated qfits configuration | Required; archive remains build-private in runtime-only installation |
| eclipse | STATIC library | Current mefpp2/src/Makefile SRCS; qfits and platform/math dependencies; preserve _ECLIPSE_ and required definitions | Required; archive build-private by default |
| mefpp_common | Internal STATIC library | ins/mef/common/mefp_lib.c and header; Eclipse/qfits usage requirements | Required; no new stable installed library/API promised |
| mefpp | Executable | ins/mef/recipes/mefpp.c; mefpp_common and transitive native dependencies | Required; install bin/mefpp |
| mefpp_resources | Validated resource generation/staging target | Three PAF templates and two distributed compressed BPMs; explicit funpack where needed | Required for a complete runtime install |
| Native test executables | Test targets | Small fixtures calling actual qfits/Eclipse/MEF routines | Included when testing is enabled; tests must not silently disappear |
| Legacy qfits/Eclipse utilities, jitter, pfits, bindings | Separate future/optional targets | Preserve sources/history; audit exact dependencies before enabling | Not required or installed by default in the first candidate |

This chooses CMake target organization, not a refactoring of scientific functions.
Archive/export names already consumed externally must not be renamed silently.
Optional legacy programs are unsupported by the initial minimal candidate unless
explicitly selected and separately built/tested; their source is not deleted.
Static qfits/Eclipse copies belong to this source build, not find_library matches
from /opt/local, /usr/local, historical install directories or a Conda environment.
Use compiler-driver linking, discovered platform math requirements and explicit
usage requirements instead of a hardcoded raw ld shared-library recipe.

## Configuration generation and clean-build rules

- Generate host configuration in the binary tree. Inventory every sysconf output
  macro/flag and map it to a compiler/capability check or an explicit fixed policy.
  Preserve numerical/memory policy; do not change qfits memory mode as cleanup.
- Account for byte order, type sizes, CHAR_BIT, large-file behavior, relevant headers,
  library functions and OS services. Fail clearly for required missing capabilities;
  optional conditional interfaces need documented disablement and coverage.
- Ensure generated headers actually win. qfits src/config.h and Eclipse
  src/include/config.h are tracked. Quoted includes can search the source header's
  directory before binary include directories. Merely adding a binary include
  directory first is insufficient. Use a reviewed generated-header name/include
  boundary or another explicit source-layout mechanism, with dependency tests.
- Do not regenerate files inside the checkout, consume config.make.orig or use
  tracked e_setup binaries. No configure-time compile/download writes to source.
- Select compiler/SDK/architecture at initial configuration, cache the selection
  and require a fresh binary directory for a changed toolchain. Capture full
  compile/link commands; do not inherit unidentified CFLAGS/CPATH/LIBRARY_PATH.
- Compiler changes and C90/C17 builds use separate binary directories. Installation
  never guesses which build is intended. Keep serial build/runtime initially;
  qualify parallel build dependencies separately from detector parallelism.

## Installed payload and resource ownership

The first candidate uses a fresh user-owned prefix. No mutation of ~/.eclipse-rc,
~/.pycavi, an existing prefix or Pycavi engine selection is implicit in install.
An explicit switch after target acceptance is a separate recorded operation.

| Installed destination, relative to prefix | Payload and policy |
|---|---|
| bin/mefpp | Newly built executable (mefpp.exe on Windows when qualified) |
| config/mefpp.paf, config/omegacam.paf, config/wfi.paf | Preserve the initial Pycavi-compatible layout; package templates, not automatic overwrites of user-edited project PAFs |
| static_cal/OCAM_BPM_1x1.fits | Verified uncompressed distributed OCAM mask |
| static_cal/WFI_BPM_1x1.fits | Verified uncompressed distributed WFI mask |
| share/mefpp/licenses/mefpp-LICENSE and qfits-LICENSE | Original component license texts and required notices, with explicit source mapping |
| share/mefpp/build-manifest.json | Source commit/tree, selected options, compiler/tool/SDK identity, source/resource hashes, generated configuration identity, expected installed files and applicable component version strings |

The static resource path remains compatible initially. A later layout change
must update/discover Pycavi resource paths together. Do not include source FITS
observations, astrometry indexes, third-party engines, Python environments,
legacy commands or development headers/archives in the runtime default payload.
Developer payload can be a separately reviewed option; it is not needed to run
mefpp. No promise of a supported ABI for those internal libraries is introduced.

BPM decompression must use an explicit identified executable, fresh binary-tree
outputs, nonzero-error handling and actual FITS content checks. It must not run
bare funpack over an existing installation or silently replace user data.
Record compressed-source and uncompressed-content hashes without guessing that
a historical mask equals the current distributed one. Repeated installation and
staging must preserve existing modified files or fail visibly; no silent overwrite.

Support an explicit prefix and Unix DESTDIR staging without recording the staging
root as a runtime prefix. CMake install-manifest support alone is not a safe
uninstaller: any removal helper must constrain paths to this prefix and preserve
modified files. Do not implement a blind recursive delete. Windows staging/path
semantics need their own qualification; do not assume Unix DESTDIR behavior there.

## Regression fixture catalogue and production routines

Fixtures below are defined requirements, not already generated/passing tests.
Small generated fixtures belong with tests and generation recipes; observational
FITS data remain outside Git, with manifests. Each test description/script must
state actual production routines, independent verification helpers and limitations.

| Fixture ID | Inputs and production path | Required checks |
|---|---|---|
| F0 toolchain | Synthetic C kernel/static libraries and executables, CMake/CTest; no mefpp routines | Strict C90/C17 flags, nonempty CTest suite, expected result; already passed on Intel Mac only |
| F1 FITS/PAF primitives | Small generated integer/float FITS/PAF; qfits_header_* APIs, qfitsloader_init/qfits_loadpix/qfits_pixdump and qfits_paf_query PAF access, with exact entry points bound during test implementation | Values/scaling, headers/HIERARCH, extension identity, null/nonfinite handling as supported; independent readback |
| F2 scan/trim | Generated detector geometry with known bias/scans; mef_overscan_correction and mef_cube_overscan_correction | Known output geometry/pixels, scan direction and mapping; reference computed independently |
| F3 calibration combine | Small repeated detector frames; mef_build_cal for bias/dome/sky | Existing selection, rejection and combination behavior; no new algorithms |
| F4 BPM | Controlled response defects and calibration stack; mef_build_bpm with existing Eclipse gain-map path | Mask convention/threshold boundaries and detector mapping; distinguish mask construction from Python static-mask copying |
| F5 mosaic normalization | At least two detectors with unequal flat levels and explicit common reference; mef_build_cal and mef_ff_combine/mef_image_filter_flat | Preserve relative responses and the same common normalization; catch accidental independent unit-median normalization and input mutation |
| F6 native science | Real raw MEF plus matched masters/PAF, through mef_engine and current save/header routines | All detector pixels, structure, units/metadata, geometry, calibration provenance and source preservation |
| F7 installed wrapper | Fresh staged inputs, newly installed executable and resources via Pycavi mefpp_reduce_science | Explicit candidate selection, installed paths, output integrity and unchanged source/configuration; Python normalization checked separately if invoked |
| F8 failure/installation | Missing/bad PAF or input, failed output location, missing tool/resource and repeated/staged install | Nonzero status, useful error, bounded side effects, no false success or overwritten working installation |
| F9 memory/lifecycle | Later stage-2 fixtures for successful, repeated and partial-failure paths | Sanitizer/leak evidence and allocator instrumentation; not implied by stage-1 execution |

F1 names describe API families; bind the exact existing signatures and supported
semantics in the test implementation before announcing executable coverage. No
new FITS library is introduced into production to supply an independent oracle.
Python Astropy may serve as a verification helper in the established environment;
it does not exercise native qfits merely by calculating the expected result.

Do not claim every pipeline builder was exercised by the existing observational
pilot. WFI requires representative dedicated fixtures when shared behavior is
qualified; a tiny one-detector fixture does not establish stage-5 detector support.
Linearity/shutter/gain/RON, dark, fringe and CMOS algorithms are later services,
not requirements to implement inside this build migration.

### Candidate observational anchor on the actual Mac

Use the retained CP Pup 2017-03-13 exposure as the first large functional anchor:

- Raw: /Users/fselman/Pictures/OCAM/raw_files/CPPup_raw/OMEGA.2017-03-13T02:35:52.825.fits.
- Historical staged native reduction: /Users/fselman/Pictures/OCAM/mac-notebook03-one-8nmbomu1.
- Normalized reference: /Users/fselman/Pictures/OCAM/mac-notebook03-normalize-0ydag_rc/science/OMEGA.2017-03-13T02:35:52.825_pre.fits.
  Previously reported SHA256: 92877d2f22280491fc148425d9748a59c1555dd8fd9dc3fc5bfd76e96298d465.
- Masters: the prior CPPup-wenu-imaging-test reduction points to bias, sky/master
  flat and BPM products; resolve actual symlink targets and hash them during
  fresh fixture inventory rather than infer a complete association from filenames.
- Prior native output contains 32 finite, nonempty detector images. This is a
  functional baseline, not independent accuracy certification or a new build test.

All paths/hashes above are historical reports to reverify, not a current filesystem
inspection. Before a candidate run, inventory original/staged input hashes,
PAF/arguments, selected engine and native output pixel hashes, detector names and
shapes, resources, timestamps and metadata. Record the native output separately
from Python-normalized output; the listed normalized hash cannot substitute for
native equivalence. User data must remain immutable and runs use fresh copies.
A second representative calibration-building fixture and WFI data still need
identification. chapman3 fixture manifests remain separate from the Mac's paths.

### Comparison policy

Prefer exact identity for discrete metadata, detector mapping, masks and integer
values; compare untouched source/input files by complete hash. Record known
pre-existing defects rather than blessing or silently correcting them.

For scientific pixels compare all finite values, nonfinite locations, per-detector
maximum/summary errors and relevant metadata. Exact pixels are the first expectation
where operation order/precision is unchanged; cross-toolchain differences require
an explicit numerical analysis and agreed absolute/relative tolerances before a
passing result. Do not pick tolerances after seeing a mismatch solely to pass it.
Absolute whole-FITS-file equality is not always appropriate for generated provenance
or header serialization differences; explain any permitted differences separately.

Run C90 and C17 configurations against the same fixture definitions. Memory tests
and external instrument scientific acceptance are separate gates. A zero native
or wrapper exit does not replace product verification. Tests requiring absent
fixtures are visibly pending/skipped and cannot satisfy their acceptance gate.
CTest must error if the expected suite is empty; failures are not swallowed by
shell wrappers. No observational query/download occurs inside normal unit tests.

## Actual Intel Mac toolchain probe evidence

Fernando reported the successful fresh run at:
/Users/fselman/wenu-mac-toolchain-01j1s5dt, with output-check.json plus configure,
build and CTest logs, retained source and compile_commands.json.

- macOS 13.7.8 x86_64; CMake/CTest 3.29.3; AppleClang 15.0.0.15000100.
- Explicit Xcode clang/ar/ranlib/ld paths and active SDK selected; compiler-driver
  linking. Verbose output confirms -std=c90 / -std=c17 and -pedantic-errors.
- Static libraries kernel_90/kernel_17 and executables probe_90/probe_17 built.
  c90_execution and c17_execution both passed; 2/2, no failures.
- Reported repository, saved executable configuration and installed engine hashes
  remained unchanged. Niceness >=10; build/test concurrency one.
- Source SHA/hash manifest for the probe has not been imported into this repository;
  the report is attributed user evidence, not a locally rerun or independently
  inspected target result. No claim that native mefpp or qfits was built/installed.

## Gate ledger and next bounded implementation

| Gate | Current state |
|---|---|
| Mac build tools and strict language-mode synthetic path | Passed within F0 scope, user report above |
| Initial native target graph / payload / fixture definitions | Specified here; implementation pending |
| Candidate source/PAF/resource and observational fixture manifest | Pending fresh actual-Mac inventory |
| CMake/CTest availability and compatible compiler on chapman3 | Pending; OS/compiler inventory recorded in roadmap 1.2 |
| Real native C90/C17 builds and installed functional equivalence | Pending |
| Native memory safety, Windows, Apple Silicon, WFI completeness | Pending |

The next implementation slice, after this specification is reviewed, is the
bounded stage-1 bundled-source/build/configuration/install correction, linked to
#65–#71/#75/#76 as applicable. Keep numerical algorithms and the installed engine
unchanged until a private candidate passes. Do not mark stage 0 fully qualified
while the observational manifest or chapman3 toolchain decision is outstanding.
Prepare those remaining read-only inventories without launching reductions.

## Revision record

| Version | Date | Change |
|---|---|---|
| 1 | 2026-10-25 | Native target graph, runtime payload, fixtures, comparison policy and attributed Mac F0 evidence |
