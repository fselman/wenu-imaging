# S2-05 two-extension Mac acceptance and target plan — 28 October 2026

Update: [complete target evidence is inspected](stage2-bpm-multiext-chapman3-acceptance-2026-10-28.md); all 16 Chapman3 pairs pass their declared functional/accounting gates. Earlier target-pending statements below are historical. Full S2-05/#75, #116 and target external diagnostics remain open.

The complete Mac evidence for tested clean source
`cea3e927f0392d8ec6c97cd40afbac2878aca03f` is independently inspected. This accepts
only the declared two-extension synthetic OmegaCAM/WFI BPM ownership slice.
Full S2-05/#75, unresolved/non-reproduced #116 and compatible target external
diagnostics remain open. The target runner is prepared; no Chapman3 run has
occurred. There is no S2-06 advance, production change, install, merge or branch
cleanup authorization.

## Evidence and integrity

Original Mac run:
`/Users/fselman/Software/build/wenu-imaging/mac-stage2-bpm-multiext-yb3etszi`.

| Evidence | SHA256 / retained identity |
|---|---|
| Original archive, 1,259 verified file identities plus manifest | `d2756d00d3dab708efbd8f40e02337a90b51e98514f2ad0ee87793eaa88ec428` |
| Four-log supplement, all original report hashes verified | `9ecc8af68712842d817cb29f9a9bbe4111acffa087c24e9fae2efda6fb46f1ed` |
| Original run report | `95c9c352f8a92ba97d4cfc20e1b3341a4548c1b954e404c3c952967ec0efa430` |
| Persistent original attachment | `libfile_883fd91133b48191adba6243707eac53` |
| Persistent supplement attachment | `libfile_dae395394c5c81919e9138a90851f75e` |

The archives remain in the Mac transfer directory
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-multiext-transfer-nslolo23/`.
All original runs, build intermediates, archives, transfer copies, raw data and
normal installations remain preserved.

Issue #118 records an agent packaging-command defect: a starts-with-build filter
mistook four root-level build log files for build-directory contents. Original
files were intact. The supplement recovered exactly those files and each SHA256
matches the already-inspected report. No rebuild or native rerun occurred.
Future filtering must apply the build-directory rule only when the relative path
has more than one component. The reusable `package_bpm_multiext_evidence.py` now applies that directory-only rule and requires every recorded command log before archiving. Both original and supplemental evidence are retained;
the completed inspection verifies all 79 command logs and successful exits.

## Independent acceptance results

32 ordinary/observer pairs, 64 native roles: C90/C17 × instrument
OmegaCAM/WFI × retained/known-response × robust/proportional × ASan/UBSan and
separate uninstrumented external-leaks lanes. Every process constructs the two
extensions sequentially in one context with NULL bias and the unchanged
0.5–1.5 test thresholds. This covers create/append behavior, not all detectors or
observational WFI, error injection, general cache/mmap/swap lifetimes or S2-09.

Verified from actual files and raw logs:

- 20,736 returned/saved mask pixel comparisons across both extensions; exact
  parent/mirrored masks, detector order, binary polarity/counts, BITPIX 8 and no
  scaling. Complete ordered canonical headers agree with declared transformations
  of the accepted metadata reference. ORIGFILE is recorded separately and shared
  by the primary and both extensions. Paired roles and all modes/lanes agree.
- 192 staged frame checks / 384 input-extension checks preserve declared headers,
  original first-extension payloads, mirrored science in extension two, unchanged
  overscan and padding. Both instrument PAFs are byte-identical to committed files.
- All 37 selected source identities match the source export and repository;
  diagnostic CMake wiring, native executable hashes and output/log hashes verify.
- Four 101-unit compile inventories show explicit C90/C17, AppleClang
  15.0.0.15000100, CMake 3.29.3, x86_64 and production allocator mode 2 with
  2,000,000 maximum registrations. Instrumentation is present only in its lane.
- One context constructed/destroyed and two masks built/released per observer;
  no live owner or mismatch. All 384 allocator boundaries match the reports;
  process start and both purges reach zero in every case.
- All 96 post-call/purge descriptor boundaries preserve exact identities;
  per-fd values recompute the reported signatures. No descriptor was excluded.
- All 16 external-leaks summaries report zero blocks/bytes. No ASan/UBSan finding
  appears. Build logs show successful completion of both executables in every
  lane and no compiler/linker error. These are not warning-free builds: legacy
  warnings remain, plus four bounded new test `sprintf` deprecation locations
  in each instrumented build. They format fixed prefixes and extension indices
  1–2 into 32/64-byte arrays; no qualified driver was changed to silence them.
- All six reported source/export/reference/checkout/protected-file preservation
  checks are true. Normal installations and observational files were not changed.

Full report, input transfer manifest, selected observer logs, four build-info
records, independent verifier/results and supplemental build-log review are under
`fixtures/mac-stage2-bpm-multiext-inspected-2026-10-28/`. The complete raw evidence
is retained in the two attachments; no source tracing alone substitutes for it.

## Unchanged-driver Chapman3 verification

Prepare 16 ordinary/observer target pairs: C90/C17 × both instruments × both
fixtures × both regression flags. Reuse all 37 selected Mac source identities,
including native driver/observer, fixture generator and output oracle unchanged.
Stage exact declared input identities. Pin the inspected Mac report and match
all target outputs to the corresponding Mac uninstrumented/leaks role, retaining
ORIGFILE separately. Keep the accepted single-extension metadata report pinned
as the exact header-transformation anchor.

Use existing qualified GCC 10.2.1 and CMake 3.29.6 with private builds, mode 2,
no sanitizer flags, nice >=10 and library thread caps 1. Keep both mask owners,
all twelve allocator observations, zero process-start/double-purge resources,
complete per-fd identities and original descriptor gates. Stop on any finding,
retain failed/incomplete provenance and inspect before further cases. Preserve
selected configuration/engine, source export, all reference reports and checkout.

This is functional/qfits-accounting verification only. Compatible target external
diagnostics remain an explicit required gap; neither Mac acceptance nor a future
successful target run waives it or attributes #116. Obtain fresh actual-host
hostname/OS/root/remotes/branch/HEAD/upstream/clean/Python evidence before target
mutation, then inspect returned native evidence before target acceptance.

Fernando also identified actual WFI calibrations/science at
`/Users/fselman/Pictures/WFI`. A read-only inventory remains pending. Those raw
files and the Chapman linearity data are not inputs to this synthetic suite and
have not been accessed or qualified here.

Preparation verification: Python syntax/help and wrong-host rejection pass; all 37 Mac-selected source identities remain exact, and all 16 target case mappings / 32 corresponding Mac role products pass read-only oracle verification. This is target orchestration preparation, not native target execution.
