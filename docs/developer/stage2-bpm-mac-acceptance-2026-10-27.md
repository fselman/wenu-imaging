# S2-05 corrected Mac BPM acceptance — 27 October 2026

Update: [Chapman3 evidence is inspected and passes the bounded functional/accounting gate](stage2-bpm-chapman3-acceptance-2026-10-27.md). Earlier target-pending statements below describe preparation history. Full S2-05 and compatible target external diagnostics remain open.

The bounded corrected Mac gate passes at clean commit
`21ea905ff90d94a29cbe174c69674afef5d487eb`, branch
`fix/112-bpm-owned-resources`, Intel Mac MC02VV0HPHTDG. This supersedes earlier
Mac-pending statements; actual Chapman3 verification remains pending.

## Observed results

All **16 pairs / 32 native calls** completed across C90/C17 ASan/UBSan and separate
external-leaks builds, using unchanged accepted driver, observer, independent
FITS oracle and fixtures. Both retained/known-response fixtures and robust/
proportional constructors pass. Every returned and production mask preserves
all 81 accepted pixels (79 good / 2 bad), binary polarity, geometry, storage,
extension identity, thresholds and QC counts. Every canonical saved-header card
and input hash matches its exact failed-baseline role. Generated ORIGFILE values
remain separately recorded; they are the only excluded header field. Full raw
output hashes are retained.

All context/mask markers balance, all 48 descriptor boundaries preserve count
and identity, no ASan/UBSan diagnostic occurs and all eight external leaks
summaries report zero unreachable blocks/bytes. After native driver return,
**15 RAM allocations / 132 bytes** remain as cache state. The first existing
public cache purge releases these; all 16 cases have zero RAM pointers/bytes,
mapped files/references and swap bytes after both first and second purge.
The earlier 140 allocations / 4472 bytes are no longer present after purge.
Production cleanup policy and allocator/cache sources/settings are unchanged.

Independent archive inspection verifies all 369 member identities (368 manifest
entries plus manifest), all 32 role input/output sets and exact comparisons to
both the inspected failed S2-05 baseline and accepted #90 references. Native raw
logs, nine resource snapshots per observer, all command/log hashes, selected
source identities and diagnostic CMake wiring match their records. All four
build identities retain XMEMORY_MODE=2 and XMEMORY_MAXPTRS=2000000. Original and
exported sources, checkout, selected engine/configuration and both reference
reports remain unchanged. No installation or observational processing occurred.

## Retained evidence

Original directory:
`~/Software/build/wenu-imaging/mac-stage2-bpm-corrected-boxhw5eq/`.
Archive `mac-stage2-bpm-corrected-evidence.tar.gz`, SHA256
`145cd80fc5289e48ffa9b572ed7b1cd24d573c2c3e52bdb07268d5efabe947ee`.
Persistent attachment `libfile_8dde9b15c3fc819189dc347005f2fbd0`.
Report SHA256:
`abb8e8d00cd93796b3b5684ca34d6c1214faaaf056f1936239a07e92c27127a5`.
Report, full transfer manifest, inspection provenance and four build identities
are retained in `fixtures/mac-stage2-bpm-corrected-2026-10-27/`.
The [failed baseline](stage2-bpm-baseline-evidence-2026-10-27.md), exact source/size
attribution and all original runs/archives remain preserved.

## Target preparation and limits

`mefpp2/tests/qualify_bpm_ownership_chapman3.py` is prepared for unchanged native
driver/observer/fixtures/oracle and production sources on Chapman3 C90/C17.
It pins this inspected Mac report and every Mac-selected source identity, builds
private uninstrumented original/observer executables and runs **8 pairs / 16
native calls**. Masks, canonical header cards and inputs must match Mac exactly;
owner, descriptor and both zero-purge resource contracts remain mandatory.
Target external diagnostic tools are unavailable in the qualified environment;
this is functional/qfits accounting only, with that independent gap still open.
Actual target execution has not occurred. Agent checks are Python syntax,
reference/source/fixture identities, case mapping, oracle readback and whitespace;
no native target execution is claimed.

Tickets #109–#112 stay open for target verification. This suite covers successful
OmegaCAM construction, bias=NULL and one extension. Populated optional metadata,
WFI, additional extensions/non-NULL bias, shared helpers in other recipes,
practical failure injection, same-process repeats and general cache/mmap/swap
remain applicable pending S2 work. Neither this first subset nor the target
functional lane completes S2-05 or broad #75/S2. No departure or reduced gate is
approved. Preserve all evidence/installations; prior agreement is required for
departures and mandatory review still precedes Stage 2A/component extraction.
No merge, branch deletion or run cleanup is authorized.
