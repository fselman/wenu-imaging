# M2 native TOML compatibility reader — paired target results — 30 October 2026

## Status and evidence boundary

Intel Mac and representative Chapman4 private C90 CMake builds and the focused
native_config_toml test passed at implementation commit
`b0ea0897ff2b5257eaf3bae0029b14a11a8f7152` (PR #147).
Normal mefpp and both configuration probes linked successfully on each target.
Protected installed files and both review checkouts passed preservation checks.

This first M2 increment is ready for bounded owner review. It does not complete
M2, activate TOML in the normal engine, or implement the final domain schema.
The [reader contract](../architecture/proposed/m2/native-compatibility-reader.md)
and [agent receipt](m2-native-toml-agent-results-2026-10-30.md) define the scope.

Evidence is owner-returned terminal output inspected in Work chat, not an
independently transferred/hash-audited target-build archive. Target logs and
per-case reports remain in their private work directories. No target C17,
sanitizer/LSan, parser-wide OOM, thread-safety, safe-Python-host, scientific or
complete-pipeline acceptance is claimed. Existing legacy compiler warnings
remain; this is not a warning-free build or a new warning-baseline audit.

## Actual target builds

| Target | Selected tools | Private work directory |
|---|---|---|
| Intel Mac MC02VV0HPHTDG, macOS 13.7.8 | Apple Clang 15, /opt/local/bin/cmake and ctest, explicit Mac SDK/x86_64, /usr/bin/make/ar/ranlib, selected Python 3.11.14 | /Users/fselman/Software/build/wenu-imaging/mac-m2-toml-082WjZGk |
| Chapman4, EL7 x86_64 shared home | /opt/rh/devtoolset-10/root/usr/bin/gcc 10.2.1, private CMake/CTest 3.29.6, /usr/bin/make/ar/ranlib, selected Python 3.11.14 | /home/fselman/Software/build/wenu-imaging/chapman-m2-toml-ur5dxaIY |

Fresh git-archive exports, Debug/C90, resources OFF, config probes ON, two jobs,
nice 10. Inherited compiler/build selections were recorded and cleared only in
the task subshell; the user environment and login files were preserved.
Targets: mefpp, config_paf_snapshot, config_toml_snapshot.
The parser/private shim retain the explicit C99 target exception; the native
mapping/core keep C90. Target logs confirm selected compiler/Python and target
completion; this receipt is not an independent audit of target compile_commands.

Chapman3/4 share the owner-qualified tools and homes. Only representative
Chapman4 ran this increment; no duplicate Chapman3 qualification is needed.
The known SSH LC_CTYPE warning was nonfatal and no locale files were changed.

## Focused test results

| Contract | Mac | Chapman4 |
|---|---|---|
| native_config_toml | 1/1 passed, 4.14 s | 1/1 passed, 2.27 s |
| OCAM actual PAF/TOML settings | 585 exact stored values | 585 exact stored values |
| WFI actual PAF/TOML settings | 249 exact stored values | 249 exact stored values |
| Signed-zero/escaped-text edge fixture | 249 exact stored values | 249 exact stored values |
| Invalid-input rejection and same-process recovery | 41 cases passed | 41 cases passed |
| Protected files / clean checkout | Passed | Passed |

The real mef_bb_new_from_paf/config_paf_snapshot path was compared with the M1
baseline, then its actual stored values were emitted as TOML and read into the
same immutable mef_config. Comparisons include explicit types and floating
object bits, not only rounded diagnostic text. The passing contract also covers
Python tomllib syntax agreement, parser/source destruction before config use,
independent clone, occupied output/diagnostic guards and every returned-snapshot
allocation failure (111 positions per valid profile). Per-case logs remain on
the target; the uploaded terminal summaries report the complete contract pass.

The callback allocator covers returned snapshot owners, not all parser/temp or
retained dependency allocations. No numerical recipe, FITS reader, Pycavi
reduction routine, calibration selection or new QC estimator ran. The normal
engine was linked but not executed. The compatibility test emitter is not a
public PAF migration tool; original PAF text/duplicate evidence remains retained.

## Retained target reports

- Mac: `build/test-work/m2 native config zf9402ld/run-provenance.json`.
- Chapman4, resolved shared-home path:
  `/home1/fselman/Software/build/wenu-imaging/chapman-m2-toml-ur5dxaIY/build/test-work/m2 native config oonwj_lw/run-provenance.json`.

Both work directories retain source.tar, source-commit.txt, exported source,
build tree, configure.log, build.log, tests.log, protected.json and
inherited-build-environment.json. Preserve all attempts and evidence.

Returned terminal transcript identities, for traceability only:

| Returned transcript | SHA256 |
|---|---|
| Pasted text(20261030-111343).txt — Mac | e0aaffd4fc3992716a4f3f32961af44659e29df5b9f1f3230bafa934f5ddebd8 |
| Pasted text(20261030-111915).txt — Chapman4 | 403e9a1a7a7657591f76d2dad0eeb42873520021c7a6328359835eca1c6b125d |

These hashes identify the received text, not original target-build archives.

## Preservation and next step

Mac: protected installed engine, normal executable configuration and installed
reduction module hashes passed. Chapman: protected normal executable
configuration and installed reduction module hashes passed. Both review
checkouts remained clean/unchanged at the tested implementation. Nothing was
installed or activated.

This receipt/current-status update changes documentation only; no repeat build,
test, tool/dependency qualification or historical matrix replay is required.
Review the first M2 compatibility increment, then merge/clean only on explicit
owner instruction. Reusable domain schemas/composition, containing-file bases,
cycle/conflict handling, override allowlist/precedence, full runtime unit/source
provenance and complete migration/duplicate policy remain later M2 work.
Other numerical extraction stays M5/M6; optional BPM and required M6a variances
are unchanged. #133/#144/#75 remain open. Preserve accepted M1 closure and all
prior results.
