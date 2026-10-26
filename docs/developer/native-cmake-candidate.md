# Native CMake candidate — 25 October 2026

First bounded stage-1 implementation, based on build specification commit
4141b513482ac00db0f8c096d3c0c3c106e2fd38. This is a review candidate, not a
qualified replacement for Fernando's installed engine.

## What changed

| Area | Candidate behavior |
|---|---|
| Source ownership | Move the complete qfits52 tree to mefpp2/qfits5; preserve original contents/licenses except four configuration-header includes |
| Build graph | Static qfits (18 sources), Eclipse (79), MEF/common and mefpp, plus a test executable; no external historical archives |
| Configuration | Binary-tree platform headers with distinct names/guards; type sizes, byte order, required POSIX services and 64-bit off_t checked |
| Language | Explicit C90 or C17; extensions disabled in target language selection; dependency POSIX calls remain |
| Recipe | Seven line comments converted to block comments (#80); executable C tokens unchanged |
| Legacy configure | mefpp2/configure delegates to CMake and returns its status; old recursive make/sysconf paths are retained as historical, unsupported entry points |
| Runtime payload | Fresh-prefix executable, three PAFs, two decompressed masks, original licenses and hash/build provenance |
| Safety | Missing/conflicting files and symlink paths rejected before copying; identical repeats and Unix DESTDIR supported |

See [build instructions and exact test boundaries](../../mefpp2/README.cmake.md).
The portable-C source baseline, serial runtime, shared mosaic normalization,
qfits memory mode and numerical algorithms are unchanged. This does not implement
memory fixes, new calibration services, threading or GPU support.

The old audit/current-architecture documents describe the pre-candidate layout.
For this candidate the dependency graph remains qfits -> Eclipse -> MEF/common ->
mefpp, but qfits is nested and CMake owns the build. No stable installed C API or
shared-library ABI is introduced. Optional utilities and other Eclipse recipes
remain source-only; no archive source pruning took place.

## Checks actually executed in the agent workspace

Linux x86_64, GCC 13.3.0 and disposable CMake/CTest 3.29.6, serial/niceness 10:

- Both actual-source C90 and C17 configurations built 100 translation units:
  18 qfits + 79 Eclipse + common + recipe + test. Verbose compile commands use
  -std=c90 or -std=c17. Existing warnings remain, including #74; no strict
  whole-dependency ISO-conformance or memory-safety claim is made.
- Three CTest entries per mode passed: native_primitives, native_cli_usage and
  native_install_contract. The last entry contains five cases; resources are
  synthetic byte fixtures, not certified OCAM/WFI masks.
- Invalid compiler and invalid language-mode configurations returned nonzero.
- Lexical comparison across 11 changed C/header files confirmed unchanged C
  tokens after the intended generated-header substitution, ignoring comments
  and whitespace. This supports the no-algorithm-change scope; it is not a
  substitute for target numerical equivalence.

[Machine-readable agent summary](fixtures/agent-native-cmake-verification.json)
records this scope. Resources were OFF for agent builds; complete runtime
installation was deliberately not claimed. No actual Mac, chapman3 or observational
processing was performed by the agent. Local build logs remain workspace evidence;
no remote CI result is asserted by this report.

## Actual-Mac observational fixture evidence

Fernando provided full hashes, native command/PAF and source/staged associations.
[External-data manifest](fixtures/mac-cp-pup-native.json) records raw exposure,
prebuilt masters/BPM/PAF, historical engine, native output and separate Python-
normalized output. FITS observations are not committed. The staged BPM is not an
explicit command-line argument in the historical invocation; staging alone does
not establish its use in science arithmetic. This anchor does not exercise master
calibration construction. Recheck hashes immediately before a future candidate run.

## Remaining gates and immediate handoff

1. Sync this review candidate to the inspected clean Intel Mac checkout using
   SSH over port 443. No merge, branch cleanup or reinstall is implied.
2. Export fresh sources and build C90/C17 with explicit Xcode tools, SDK, fresh
   build directories and private prefixes. Run nonempty CTest suites. Decompress
   both actual distributed BPMs with an identified funpack and independently
   inspect their FITS contents. Verify install manifest, repeated installation
   and staging without selecting the engine in Pycavi.
3. Only after build/install checks, prepare the immutable observational anchor
   copies and compare all native detector pixels/metadata with the historical
   reference. No reduction is launched by this delivery.
4. Add remaining small fixture coverage F1–F5, calibration-building and WFI
   evidence; qualify the installed wrapper and native failure paths. Issues
   #71/#75/#76 remain unresolved; zero exit is insufficient acceptance.
5. Qualify the compatible chapman3 toolchain and repeat the agreed checks there.
   Windows, Apple Silicon and memory qualification remain separate pending gates.

Stage 1 stays open. The next Mac command group is synchronization only; inspect
its output before giving the dependent build/install qualification group.

## First Intel Mac attempt and installer correction (#82)

Fernando reports /Users/fselman/wenu-mac-native-build-6v088xmj at source
8af83052b0f169f18411047b7d0ffa94cb32b4e8: C90 configuration/build passed,
as did native_primitives and native_cli_usage. Four of five installation cases
failed because macOS temporary directories pass through /var, a normal ancestor
symlink. The script stopped at that gate; C17 and independent BPM pixel checks
were not executed. Nothing was installed by the qualification runner.

The correction resolves ancestors outside the requested installation prefix;
links at the prefix itself and inside its payload remain rejected. The runtime
prefix recorded in provenance is retained, without the DESTDIR staging root.
Two regression cases add an external ancestor alias with a not-yet-created
parent, and an explicitly linked prefix. All seven installation cases plus the
native tests pass under agent Linux for both existing C90/C17 build directories.
This changes installer/tests/docs only; native C sources are unchanged. Actual
Mac rerun remains pending, and #82 stays open until its target acceptance.

## Intel Mac C90 acceptance and C17 inline correction (#83)

Fernando reports /Users/fselman/wenu-mac-native-build-9lgbhxqn at revision
e1f4bedb93aa21cb4b1fd96ced490a78407987c4: C90 configure/build, all three
CTest entries (including seven installer cases) and complete OCAM/WFI BPM
comparisons passed. This supplies the actual-Mac installer regression evidence
for #82. C17 configured but linking mefpp failed with 45 duplicate symbols,
including toupper and ___inline_signbitd. C17 tests/BPM checks were not run;
no actual runtime installation or observation processing took place.

local_types.h defined inline as an empty macro even in C17, where it is a
language keyword. This can alter subsequently included system definitions and
is consistent with the Mac link errors. Restrict the legacy fallback to pre-C99
modes; keep the existing C90 path. Do not suppress duplicate symbols or change
inline semantics with a linker/compiler workaround.

The native primitive test now rejects a leaked inline macro in C99+ and checks
ctype/math integration after Eclipse includes using toupper/fabs. Agent Linux
GCC 13.3 C17 compilation failed with this regression and the old header, then
actual-source C90/C17 builds and three CTest entries per mode passed after the
correction. This is a preprocessor compatibility change, not numerical refactoring.
Actual Mac C17 link/CTest/BPM acceptance and renewed C90 checks remain pending.
Preserve both previous attempt directories as evidence.

## Qualified Intel Mac build/resources/private installs

At source 41c8e6a544c1bc5122dc558e0c8cc7904214e1d0, Fernando reports both
C90/C17 builds/tests, complete BPM pixel/checksum checks and real private runtime
installation/repeat/installed CLI/C17 staging passed. See the
[acceptance record](native-mac-build-install-acceptance.md) for exact evidence,
resource hashes and remaining gates. This supersedes the pending Intel Mac
build/install statuses in the historical attempts above; observational and
chapman3 qualification are still pending. Main and the selected engine are unchanged.

## Failure-handling follow-up, 26 October 2026

The focused failure/configuration correction adds the nonempty CTest entry
`native_failure_contract`; run it in both C90/C17 builds. Existing private Mac
engines and normal selection remain unchanged. Source regression checks passed;
rebuilt target build/install, installed-wrapper and observational acceptance remain
pending. See [the correction record](native-failure-correction-2026-10-26.md).

## Bounded Mac correction acceptance, 26 October 2026

Mac correction acceptance, 26 October 2026: Fernando reports source
4ade8c52027c736a49b65da3bdb31f11b036693b passed fresh C90/C17 configure/make,
all five CTest entries per mode, both private runtime installations and installed
failure suites, isolated Python imports/five wrapper regressions, and complete
CP Pup direct and corrected-wrapper comparisons in both modes. All 32 detector
arrays are exact/finite, with matching structure and only generated primary
ORIGFILE timestamp differences in raw headers. Protected engines, input files,
Python packages and checkout remained unchanged. See
[the correction record](native-failure-correction-2026-10-26.md).
This is bounded Intel Mac acceptance using prebuilt calibrations. Stage 1 stays
open for calibration-building fixtures and Chapman3; WFI observational, memory,
other platform and scientific/Phase 3 gates remain open. Keep #75's broader
ownership/memory gate and the applicable linked target requirements open.
No normal engine/package switch, merge or cleanup has been performed. Documentation-
only acceptance updates need no reinstall or repeated processing.
