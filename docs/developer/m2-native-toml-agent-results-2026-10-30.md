# M2 first native TOML increment — agent receipt — 30 October 2026

The [compatibility-reader contract](../architecture/proposed/m2/native-compatibility-reader.md)
is implemented behind the existing opt-in configuration-probe flag. M1 is
owner-accepted/closed at merged PR #146, main
`7d8da6b96b7b744a51e3847522a727e3f510c6f2`. Fresh returned Mac evidence matches
that clean main and selected Python; no Mac mutation/test is claimed here.

Agent GCC 13.3 / Linux x86_64 / glibc 2.39 checks passed:

| Lane | Actual checks | Result |
|---|---|---|
| C90 core / C99 parser-shim CMake | Both probes, normal engine link, native_config_toml | Pass; CTest 0.79 s |
| C17 core / C99 parser-shim CMake | Both probes, native_config_toml | Pass; CTest 0.78 s |
| C90 core / C99 parser-shim with ASan+UBSan | Direct reader/parser/snapshot/probe, same contract against uninstrumented actual PAF reference | Pass; leak detection disabled |

Every lane compared 585 OCAM and 249 WFI settings with actual legacy PAF
constructor snapshots and the reviewed M1 baseline. The 249-value edge fixture
covers stored signed zero and escaped UTF-8 text. Each valid profile passed
111 returned-snapshot allocation failures, source/parser destruction before
dump, independent clone and occupied-output/diagnostic guards. Forty-one
invalid inputs failed before valid same-process recovery and complete-value
comparison. These are configuration tests, not astronomical reductions.

[Retained reports, compile modes and hashes](fixtures/agent-m2-native-toml-2026-10-30/README.md)
identify actual commands and source/probe/parser inputs. CMake compile commands
confirm C90/C17 for mapping/probe and C99 only for parser/private shim. Optional
source inventory contains parser source/header/license/upstream provenance.
Unmodified parser identities match upstream.json. Normal C90 mefpp links only
mefpp_common/Eclipse/qfits/math; existing legacy recipe warnings remain, with
no warning-free claim. Python here was 3.12.14; actual target 3.11.14 is pending.

No Mac/Chapman builds, target sanitizers, installation, normal-engine activation,
FITS I/O, new numerical/QC policy, ASDF persistence or complete-M2 acceptance.
The callback allocator covers returned snapshot ownership only. No whole-parser
OOM, LSan, reentrancy, thread-safety or safe-Python-host claim; #144 stays open.

Next: guarded review-branch synchronization on the verified Mac, then fresh
private C90 build and focused native_config_toml check with the canonical selected
tools; one representative shared Chapman check after its fresh preflight. Reuse
the already qualified tools/dependency; do not repeat the historical matrix.
Remaining M2 domains/composition/override/unit/source/migration work stays in M2;
other numerical extraction stays M5/M6. Owner review precedes any instructed
merge/cleanup. Preserve all user evidence and installed selections.
