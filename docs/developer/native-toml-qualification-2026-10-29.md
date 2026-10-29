# Native TOML qualification — Mac and Chapman4

29 October 2026 owner decision: vendor the two tested tomlc17 source files, with the MIT license, exact revision/hash provenance and update policy, in [third_party/tomlc17](../../third_party/tomlc17/README.wenu.md). The approved source import is byte-identical to pinned upstream 4987cf895df61f702d19e3481f34b032ab29ed3a and both qualified host copies. Vendoring is the selected distribution method; build-target/configuration-adapter integration remains the planned implementation stage. Preserve C90 public/numerical contracts, compile the dependency in C99 when integrated, and retain explicit UTF-8 validation/one-time option initialization/shared TOML 1.0 bounds. No production installation, PAF replacement or processing begins from this source import.

29 October 2026. Owner instruction: “Let us include it in the current work.” This adds bounded tomlc17 qualification to PR #135 alongside the completed Python TOML/core-ASDF private trial. It authorizes private source builds/tests and a scoped C99 dependency trial, not production integration, installation, PAF replacement, reductions or a general mefpp language-standard change.

## N4 independent paired receipt and recommendation

29 October 2026: uploaded native evidence from both actual hosts independently inspected; bounded N1–N4 qualification is complete.

| Bundle | Bytes | Manifest files | SHA256 |
|---|---:|---:|---|
| mac-native-toml-evidence.tar.gz | 135023 | 72 | e15b387342bf12f16086814394e58b8c0588977903c3446a3466144218dd932f |
| chapman4-native-toml-evidence.tar.gz | 103957 | 68 | f846da8cb7ecee2b70a3ea52a2ee26f863e134f96f00f882b327b5e886b982c9 |

Both archive identities, safe regular-file membership, no duplicate/traversal paths, exact manifest membership and all 140 member size/hash identities pass. The Mac-only members are N1/sdk.log and three N23 dSYM files (Info.plist, DWARF symbols and x86_64 relocation YAML). They explain the four-file difference. Executables and static libraries are excluded as intended; the Mac archive additionally retains debug-symbol data. No archive regeneration or test rerun is needed.

Independently verified four reports and their N1→N23 links, all 71 command-log hashes/statuses, source/header/license pins, exact test-only bridge/C90 caller/C driver contents, every transferred artifact identity, generated corpus bytes against the prepared fixture definitions and expected typed trees. Native binary/library identities were verified by host runners/collectors and are recorded in reports; those payloads were not independently re-read on the agent because they remain on their hosts.

The logs confirm explicit Xcode Apple Clang 15 on Intel Mac and devtoolset GCC 10.2.1 on Chapman4, parser/bridge C99, strict-C90 caller, -pedantic-errors, and /usr/bin/ar. Compile/link logs are empty on both hosts. Mac linked runtime is libSystem; Chapman links the system libm/libc/loader, with no missing dependency reported. No Mesa/MPI compiler wrapper is selected. Clean baseline HEADs and unchanged before/after Git and production package metadata agree with the declared target states.

N2 independently reconstructed six expected typed trees (including signed zero, Unicode, numeric limits and date/time/timezone normalization), checked twelve negative diagnostics and zero tracked allocation counts, and verified every case input identity. Both semantic digests equal `40b47916247e105606bcaaac47a893871edc4e37f8f05f87b490267dc696edb9`. The signed-64 overflow controls use an explicit interoperability range check on the Python side; they are not tomllib syntax failures.

N3 cycle logs/report agree on twenty cycles / 60 parses per host, zero outstanding parser allocations. Each host records all 119 valid-input and 120 partial-invalid injection positions consumed/rejected, no fallback successes and zero outstanding allocations. The reviewed harness checks recovery status, equivalent semantics for any successful fallback, and a valid parse after each injected case. Recorded preservation flags are true; installation/production activation are false. This is retained-evidence review, not another target execution.

### Recommendation for owner review

Adopt pinned tomlc17 `4987cf895df61f702d19e3481f34b032ab29ed3a` as the native TOML dependency for the planned M2 integration on these exact tested Intel Mac/Chapman4 environments, subject to the existing production-adoption decision. Use a static dependency in explicit C99 mode, keep upstream types behind the adapter boundary, enable UTF-8 validation and initialize parser options once before any worker activity. Retain the C90 baseline for numerical/public native contracts. Initial editable configuration should use the shared TOML 1.0 subset and explicit C-compatible integer/domain bounds; production dialect and domain enforcement must be implemented in the adapter rather than inferred from parser acceptance.

The C90 proof is a narrow test interface using double/long/error buffers, not qualification of the entire future typed request/configuration API. C99 test-only glue does not automatically authorize an exception for production adapter compilation. Production integration, PAF migration, installation, scientific equivalence and any broader language-standard exception remain future implementation/review work.

Other Chapman hosts, sanitizer/all-process leak coverage, concurrent parsing/global-option races, full TOML conformance and unsupported production schemas are not qualified by this corpus. The dependency is a reader; no TOML editing/writing capability was qualified. Preserve all evidence and completed Python TOML/ASDF trials. No further runtime test is planned for this bounded trial. Owner acceptance, dependency adoption and merge/cleanup remain pending.

Earlier preparation/pending paragraphs below are chronological history and are superseded by this receipt only for N1–N4 on the two named hosts.

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

## Returned N1 pair and N2/N3 preparation

N1 owner output passes on both actual hosts: Mac `/Users/fselman/Software/build/wenu-imaging/native-toml-n1-MC02VV0HPHTDG-j9uh67in`; Chapman4 `/home1/fselman/Software/build/wenu-imaging/native-toml-n1-chapman4-ggagd64k`. Both report strict-C99 parser/glue build, strict-C90 caller build, static link, positive gain=2.1/detectors=8, missing/malformed-file smokes and linked-runtime checks successful. Production package metadata, checkout and source/fixtures are reported unchanged; installation false. This is returned target evidence, pending independent paired artifact review. No N1 runtime repeat is planned.

Prepared `probes/qualify_native_toml_n23.py` and test-only `probes/native_toml_n23.c` reuse the passed static library. Before building the new test driver, the runner checks the N1 report, protected inputs, compiler/library/executable identities and every N1 command-log identity/status. It uses the same explicit compiler/SDK/environment isolation, fresh private work, one-use marker and preservation reporting; no parser rebuild, reinstall or scientific processing.

N2 has six valid fixture groups (settings/dates/timezones, numeric boundaries/special floats/signed zero, Unicode/quoted/multiline strings, arrays of tables, nested/inline structures, empty input) and twelve negative controls (duplicates, malformed input, signed-64 overflow, invalid date/number/escape/control character and invalid UTF-8). Compare recursive typed values with Python, including timezone/microsecond normalization and signed zero. Important oracle distinction: tomllib accepts arbitrary-size integers; a separate explicit signed-64 interoperability check rejects the two overflow controls. Do not claim these two are tomllib syntax rejections. The fixture contract, C representation and future Wenu domain validation remain distinct.

The C test process enables `check_utf8=true`, installs tracked realloc/free hooks once before parsing, and leaves parser options fixed. Default upstream UTF-8 checking is false; the qualified test configuration must be recorded, not silently generalized to defaults. No concurrent parsing or global-option mutation is exercised.

N3 runs twenty valid/error/valid cycles (60 parses), plus bounded injection at each allocation call observed in one successful larger nested document and one partial-tree parse failure (maximum 256 positions per input). Each injected attempt is released; recovery must reproduce the baseline status, any successful fallback must be semantically equivalent, and a valid parse must then succeed. The tracker rejects unknown/double-free/realloc ownership and requires zero tracked allocations after cleanup. Tracker bookkeeping uses separate libc allocation; this is parser-hook accounting, not all-process leak/sanitizer or race qualification.

Expected outputs are a new driver executable, synthetic corpus under a path with spaces, expected typed trees, per-case/ownership logs and provenance with semantic digest and preservation checks. Pass requires six valid typed matches, twelve negative rejections with diagnostics, successful cycles/injections/recovery, zero tracked allocations, unchanged N1 evidence/checkout/package metadata/cwd and `N2-N3-passed-awaiting-paired-evidence-review`. Actual API calls are toml_parse_file_ex, toml_seek indirectly in N1 only, toml_free, toml_default_option/toml_set_option and toml_equiv; Python uses tomllib plus explicit test normalization/range checks. No Pycavi/mefpp/scientific routines run.

Agent Linux GCC 13.3 passed strict-C99 driver compilation, all six valid and twelve invalid controls, twenty ownership cycles, and 119 successful-input plus 120 partial-invalid-input allocation injection positions, with valid recovery and zero tracked allocations. Runner syntax and wrong-host guard pass. Target N2/N3 execution remains pending; the local counts are not asserted as target results. No upstream parser repair or production adapter was introduced.

SHA256: runner `2cf03b79d19341d7d916a538bd6a840f6d25fa403f6b2c6cfd373874aa1267e7`; C driver `e2cce1970f42cfa23576828b97d6fa3274e7468681688dbaa3d894972304ac71`.

Earlier preparation status below is historical where superseded by this returned N1 result and prepared N2/N3 step.

## Returned N2/N3 pair and evidence collection

Owner output reports `N2-N3-passed-awaiting-paired-evidence-review` on both actual hosts: Mac `/Users/fselman/Software/build/wenu-imaging/native-toml-n23-MC02VV0HPHTDG-79x2yt3h`; Chapman4 `/home1/fselman/Software/build/wenu-imaging/native-toml-n23-chapman4-zaup3mhq`.

Both semantic digests are `40b47916247e105606bcaaac47a893871edc4e37f8f05f87b490267dc696edb9`. All six valid/twelve invalid cases passed. Each host completed twenty cycles/60 parses with zero outstanding parser allocations; 119 valid-input and 120 partial-invalid allocation positions were injected and rejected, with zero outstanding allocations and valid recovery. Production package metadata, checkout and retained N1 evidence are reported unchanged. This is returned terminal evidence; independent paired artifact review remains pending. Do not rebuild/replay N1/N2/N3 to collect evidence.

Prepared `probes/package_native_toml_evidence.py` verifies the retained reports and their linkage, recorded metadata/preservation, N1 inputs/library/executable identities, all command logs/statuses, every N2/N3 artifact hash, expected typed trees/case inputs, semantic digest, cycles and allocation counts. It writes a fresh archive/manifest per host with reports/logs, synthetic configurations, source/license/test glue and expected trees. Native binaries/static libraries are checked on the host but excluded from transfer; observational data and environments are excluded. Collector uses standard-library byte/JSON inspection only: no compilation, native parser launch, scientific imports or test rerun. Collector syntax and wrong-host rejection passed on the agent; target collection and independent N4 review remain pending.

Collector SHA256: `47658ad4cc7d67d496b908f59b28522519f9819ca278bfd96efb9c06fc51c691`. After collection, return both archive sizes/hashes and upload both exact bundles for paired inspection and the bounded adoption recommendation. Production activation/integration, other Chapman hosts, concurrency and sanitizer/full-process memory qualification remain outside this result.

## Current evidence and next action

Agent source review and SHA256/Git-blob identity checks passed. Read-only preflight helper `probes/native_toml_tool_preflight.py` passed syntax and wrong-host rejection. It only invokes version/read-only Git queries and records known compiler candidates, recording PATH-discovered Mesa SDK tools without selecting them for the native build. Target compiler inventory is now returned above. Native target compilation, boundary behavior, broader parser agreement and ownership checks remain pending. Do not reuse the completed ASDF tests as evidence for this native dependency and do not rerun them for this addition.
