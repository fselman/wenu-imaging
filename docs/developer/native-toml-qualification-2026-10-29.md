# Native TOML qualification — Mac and Chapman4

29 October 2026. Owner instruction: “Let us include it in the current work.” This adds bounded tomlc17 qualification to PR #135 alongside the completed Python TOML/core-ASDF private trial. It authorizes private source builds/tests and a scoped C99 dependency trial, not production integration, installation, PAF replacement, reductions or a general mefpp language-standard change.

## Pinned source and boundary

Upstream: https://github.com/cktan/tomlc17

Commit: `4987cf895df61f702d19e3481f34b032ab29ed3a`; tree `98f788830aafede6d520efdffc172c316cae4e2b`. Reviewed immutable README, header, implementation, Makefile, options and MIT license. Source bytes match upstream Git blob identities.

| File | SHA256 |
|---|---|
| src/tomlc17.c | 7476923b6c9b8f0858b82b63ed6107f57448882983390e70c31327f7d3e2a362 |
| src/tomlc17.h | 29c0909092f4b23c7edce705167064f4a90548db5334b4aa2cd95d7ad801adb9 |
| LICENSE | f949d0976f85076c96fc5122f0632b5a1b806d8b2badbe968c42c97230e6e79e |

Upstream describes a TOML 1.1 parser compatible with C99. Its public header includes stdbool.h/stdint.h and exposes bool/int64_t types; it must not be included in a strict C90-facing public interface. The proposed production shape remains a pinned static dependency behind a small typed configuration adapter; parser objects do not escape into numerical services or mefppy. This is a design and qualification target, not an implemented adapter.

The agreed exception covers building the external dependency in C99 mode. A test-only C99 bridge may consume its header so a separate strict-C90 caller can test the intended boundary. Existing mefpp/qfits and public contracts retain the C90 baseline. Any production adapter compilation exception must be reported explicitly with the measured boundary result before integration; this trial does not silently expand the source baseline.

Upstream options documentation says toml_set_option is not thread-safe and should be called once at initialization. Qualification must inspect configuration/allocator state and keep options fixed before parsing. Independent processes and same-process concurrent parsing are distinct claims; passing sequential parsing does not establish thread safety. Future parallel workers must not change global options concurrently.

## Bounded sequence and acceptance

1. **N0 — actual-host preflight.** Read exact Mac/Chapman4 checkout, Python, compiler/tool versions, compiler paths, SDK/libc and selected build environment variables. No compile/install. The Python build banner is not evidence of the native compiler. Keep system tools and working environments unchanged.
2. **N1 — private compilation and C90 boundary.** Fetch the exact source/license into fresh private directories, verify hashes, compile a static library using an actually inventoried compiler in explicit C99 mode. Compile a separate caller with strict C90 diagnostics through a test bridge and link/run it. Capture compiler version, commands, logs, flags, source/binary identities and linked runtime dependencies. Neither a compiler path nor agent-host success qualifies Mac/Chapman. A controlled compile-only C17 lane may use an already qualified compiler; do not install a compiler or widen the matrix automatically.
3. **N2 — parser agreement and errors.** Run the same bounded synthetic TOML 1.0 corpus through tomlc17 and Python 3.11 tomllib on both hosts; compare typed semantic values, not formatting. Include tables, dotted keys, arrays/arrays of tables, quoted Unicode and paths with spaces, booleans, signed integers, floating point and date/time fields relevant to the planned configuration. Reject duplicate keys, malformed documents, invalid UTF-8 and overflow; verify useful errors and subsequent successful parsing after a failed parse. Distinguish parser grammar from Wenu domain validation (unknown keys, ranges, required values). TOML 1.1 features accepted by the C parser remain outside the proposed shared configuration language; selecting/enforcing the production dialect is a separate adapter requirement. This bounded corpus is not a claim of complete TOML conformance.
4. **N3 — ownership and failure cleanup.** Exercise repeated parse/free of successful and rejected tiny documents, allocator accounting and bounded allocation-failure controls using the documented allocator interface. Verify no surviving test-owned allocations, no invalid cleanup and preserved input/cwd. Use qualified host diagnostics when available; a missing sanitizer is an explicit limit, not grounds for system upgrades or repeated matrices. Keep allocator/global configuration initialization isolated and fixed. Do not assume that returning an error proves cleanup.
5. **N4 — paired receipt and adoption review.** Inspect reports/logs and identical typed semantic results from actual Mac and Chapman4, confirm no production/environment/checkout changes, record compiler/C90 boundary/diagnostic limits, then present the dependency decision. Native parser adoption and M2 production integration remain explicit later decisions. Other Chapman hosts need their own qualification or justified equivalence evidence.

## Scope of test explanations

N1–N3 will exercise tomlc17 parsing, lookup and release APIs through test-only glue, plus tomllib for the comparison oracle. No Pycavi reduction methods, mefpp scientific routines or native astronomy tools run. Inputs are synthetic configuration bytes; expected outputs are a private library/test executable, typed result records, diagnostic logs and provenance. Acceptance requires matching expected types/values, declared negative cases rejected, clean ownership controls, a successful C90 caller boundary and preserved originals/environments. Explain each prepared bounded runner before its actual execution; stop on unexpected findings rather than automatically patching upstream or retrying.

## Actual compiler inventory and N1 preparation

Owner-returned preflight confirms clean Mac main b5bfd910614a786b95a598cb6295989c9f6602d6 and clean Chapman4 main 0fa9eaf157359a93f2a9196f6fff05dc3e96e220, both using their expected Python 3.11.14 environments. Mac: Apple Clang 15.0.0 (clang-1500.1.0.2.5), SDK /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk, CMake 3.29.3 and Make 3.81. MacPorts GCC 13.2 is available; PATH also resolves GCC/ar to Mesa SDK tools. /usr/bin/gcc --version timed out after 15 seconds; its cause is not diagnosed or repaired by this work. Do not retry it for this trial.

Chapman4: GCC 10.2.1 at /opt/rh/devtoolset-10/root/usr/bin/gcc is present; system GCC is 4.8.5, CMake 2.8.12.2, Make 3.82, glibc 2.17. Inherited CC points to /usr/lib64/openmpi/bin/mpicc. The Python GCC 14.3 build banner is not the selected compiler.

Prepared `probes/qualify_native_toml_n1.py` uses explicit Xcode Clang 15 on Mac and devtoolset GCC 10.2.1 on Chapman4, /usr/bin/ar, and direct compiler commands (no CMake requirement). Compiler child processes have a controlled PATH, explicit SDK on Mac, and ignore inherited CC/build/include/linker environment overrides. Mesa and MPI wrappers are not selected. It records selected compiler/archiver identities, version, actual commands, logs, source/library/executable hashes and linked runtime information.

N1 test purpose/actions: in a fresh private directory, fetch three pinned upstream files, verify exact hashes, build a static parser with -std=c99 and -pedantic-errors, build a test-only C99 bridge, compile a separate C90 caller with -std=c90 and -pedantic-errors, then link/run it. The synthetic positive TOML has gain=2.1 and detectors=8 at an absolute path with spaces; the returned values/types must match tomllib. Missing and malformed files must produce a nonempty diagnostic with exit 1. These are minimal N1 error smokes, not the N2 corpus or N3 ownership qualification. No mefpp/Pycavi routines or scientific/native astronomy tools run.

Expected outputs: retained source/license, generated test-only header/bridge/caller, static archive, objects, executable, three tiny parse-smoke logs, linked-runtime output and run-provenance.json. Pass requires successful strict language-mode compilation/linking, exact typed result, declared error exits, no unresolved linked runtime, source/fixture/cwd preservation and unchanged recorded production package metadata and checkout. Runner is one-use per host and stops on the first unexpected result; preserve failures rather than automatically retrying.

Agent Linux GCC 13.3.0 checks passed: pinned parser strict-C99 compilation, bridge strict-C99 compilation, caller strict-C90 compilation, archive/link, positive/missing/malformed controls. Runner syntax/wrong-host guard passed. These do not qualify the target compilers. Actual N1 Mac/Chapman execution is pending; N2/N3 remain unrun. Runner SHA256: a80abf72d094d3cb00175172699eaccb35f1543822f4274f49515008a98f1273.

## Current evidence and next action

Agent source review and SHA256/Git-blob identity checks passed. Read-only preflight helper `probes/native_toml_tool_preflight.py` passed syntax and wrong-host rejection. It only invokes version/read-only Git queries and records known compiler candidates, recording PATH-discovered Mesa SDK tools without selecting them for the native build. Target compiler inventory is now returned above. Native target compilation, boundary behavior, broader parser agreement and ownership checks remain pending. Do not reuse the completed ASDF tests as evidence for this native dependency and do not rerun them for this addition.
