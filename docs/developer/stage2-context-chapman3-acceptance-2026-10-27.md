# Context cleanup: Chapman3 acceptance — 27 October 2026

Issue #99 / correction PR #101; bounded Stage 2 S2-02 only.
Actual target source: 596cc1022e533f7910d7aae0c32dfe736fae9167,
clean fix/99-context-owned-strings on chapman3.sc.eso.org.
See [corrected Mac acceptance](stage2-context-mac-acceptance-2026-10-27.md)
and [inspected failed baseline](stage2-context-baseline-evidence-2026-10-27.md).

## Independent target evidence review

Archive SHA256:
cfa07380e8ed4d932f3302513ce2262f582decf2c10b805f95f6c735c4786613.
All 93 member sizes/hashes match its transfer manifest. The agent independently
inspected every native context case/report/log, input PAF and accounting boundary,
the two build records and source identities. All recorded commands exit zero.

All 24 C90/C17 × OCAM/WFI × six-variant cases pass. Input PAF hashes,
constructor success/rejection contracts and configuration fingerprints match the
corresponding accepted uninstrumented Mac cases exactly. All process-start,
post-initialization, per-call and final allocation states are zero pointers /
zero bytes, including three same-process calls and late MEF.SATMAX rejection.
No unexpected result or outstanding ownership is hidden by a passing CLI exit.

Every recorded native/header/allocator/PAF/C-driver source byte matches the Mac
reference snapshot. The accepted Mac report copied into the archive is
byte-identical to the independently uploaded corrected Mac report.
Existing GCC 10.2.1 and CMake 3.29.6 build reports confirm explicit C90/C17,
-O0 -g and qfits memory mode 2 with 2000000 maximum registrations.
Python's build compiler is not the native compiler selected for these builds.

## Acceptance boundary

The original constructor/destructor retained exactly the 29 omitted owned
configuration strings / 550 bytes per context, growing to 87 / 1650 after three
calls. The minimal 29-release correction now returns to zero for the declared
normal and rejected-construction cases on both hosts, with unchanged context
values and fixture bytes. The native production change remains confined to
mef_bb_del; no numerical, metadata-content or allocator-policy change was made.

Mac acceptance includes address/undefined diagnostics and separate external
leak/accounting checks in the declared RAM context suite. Chapman3 evidence is
uninstrumented functional verification plus qfits bookkeeping only. No target
sanitizer or external leak-tool coverage is claimed. Its compatible diagnostic-
runtime gap remains explicit in the broader Stage 2 plan.

This satisfies #99's bounded corrected cleanup and unchanged-driver/fixture
target acceptance. Closing #99 records verified correction, not integration of
PR #101. It does not close #75, Stage 2 or scientific/platform/export gates.
mef_engine/CLI failure ownership, other object lifetimes, cache growth, allocation
failure injection, longer repeated stages and mmap/swap remain separate work.
The mandatory review before Stage 2A/extraction still applies.

## Preservation and next work

The [target run report](fixtures/chapman3-stage2-context-2026-10-27/run-provenance.json),
two build records and full 93-file transfer manifest are committed with this
record. The complete uploaded archive with logs/source/PAFs and Mac reference
is retained as Library file libfile_7a379c7179048191841c2f2aabef824b.

Fernando retains the target run and archive:
~/Software/build/wenu-imaging/chapman3-stage2-context-phnx8_z2/.
The transfer command targeted a hash-checked Mac copy under
~/Software/build/wenu-imaging/mac-stage2-context-corrected-87a1olms/.
Both original failed and corrected Mac runs remain separately preserved.
Do not delete, relocate or overwrite these directories or working installations.

Actual-host reports and collection checks record unchanged selected engine,
configuration, source/checkout and Mac reference. The agent inspected uploaded
snapshots, not live host files. No installation, normal selection switch,
image processing or observational rerun occurred.

Integration order for the stack is #97, #98, #100, #101. Merge and Git branch
cleanup require their applicable instruction; no merge or deletion is performed
by this evidence update. After integration, the next declared application
increment is S2-03: CLI/parser/engine failure ownership with retained diagnostics.
No new application stage is executed by this acceptance record.
