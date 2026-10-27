# S2-04 repaired Mac observer and cache control — 27 October 2026

## Inspected actual-host evidence

Clean tested source `97c086aaf301e7ae782c23ec9d67de1427351a8b`, branch
`test/stage2-split-ownership`, Intel Mac MC02VV0HPHTDG. All 80 case pairs /
160 native invocations completed. All functional contracts pass, with exact
ordinary/observer output hashes, independent FITS pixels/metadata/padding and
preserved staged inputs/sentinels. Both C90/C17 instrumented and separate
external-leaks lanes are covered for OmegaCAM/WFI synthetic fixtures.

All 80 observers report the expected native exit, one returned context and one
recipe destruction, no owner mismatch/live owner, and matching descriptor
counts/identity. The actual soft descriptor limit changes from 256 to unlimited
(represented by 9223372036854775807), matching unchanged xmemory initialization.
Actual enumeration therefore resolves the original observer defect #106 without
changing production limits. No Linux enumeration acceptance is claimed.

No ASan/UBSan diagnostic occurs in the original native logs. All 40 external
leaks summaries report zero unreachable blocks/bytes. **The resource gate still
fails:** 64 cases retain five RAM registrations; 16 missing/non-FITS cases have
zero. All have zero mapped files/references and swap bytes at return. Retained
bytes exactly equal the filename including NUL plus four integer arrays for
three headers (two in the truncated fixture). Relative cases use 60 bytes,
truncated cases 44; absolute cases use their actual path length. This is a
source-supported cache candidate, not completed cache attribution or a lost
memory claim.

## Retention and verification

Original directory:
`~/Software/build/wenu-imaging/mac-stage2-split-baseline-vtv8n8o_/`.
Archive `mac-stage2-split-observed-evidence.tar.gz`, SHA256
`6eb3014d7adb3ea02fa39e0ef2edd69077953fcc074e15fe0198217187d5e817`.
Persistent attachment `libfile_184625723a988191b734926960394021`.
All 933 file identities verified (932 manifest entries plus manifest), all
160 role directories independently checked, and all raw ownership/descriptor/
allocation/leak logs inspected. Exported source hashes match the delivered
source. Reports, build identities, full transfer manifest and inspection summary
are retained in `fixtures/mac-stage2-split-observed-2026-10-27/`.
The report confirms sources/export/checkout and protected engine/configuration
unchanged. No installation or observational processing ran. Preserve this run
and the earlier failed-observer run in full.

## Next bounded diagnostic: prepared, not executed

The existing runner accepts `--cache-reference` pointing to this retained report.
It requires all production/fixture sources to match that reference; only its
observer and runner may differ. Four fresh C90/C17 diagnostic builds run the
same 80 ordinary/observer pairs and compare inputs, exact products and expected
exits against the retained reference. No output directory is reused.

With this option only, the diagnostic observer records the original after-cli
state, invokes the existing public `qfits_cache_purge`, measures again, invokes
it a second time and measures again. Production main/engine/split/cache/allocator
sources and default CLI behavior remain unchanged. Attribution requires the
original state to match the filename/header-array prediction, then zero RAM,
mapping and swap state after both purges, unchanged descriptor identities at
all boundaries, exact retained products, and clean ASan/UBSan/external leaks.
Unexpected retained state fails; baseline mode still reports its live state as
unattributed. The reference report hash is recorded and checked unchanged.

This is the necessary cache-attribution subcheck within **Stage 2, S2-04 split
I/O/publication ownership**, not general S2-09 repeated-stage or S2-10 cache
lifetime acceptance. Native Mac compilation/execution of this new control is
pending. Chapman3 verification follows inspection of the returned Mac evidence;
its compatible external diagnostic gap remains explicit. S2-05/06 calibration,
additional recipes, broader injection/repeats/cache/mmap/swap and conditional
wrapper checks remain open under #75. The early ESO Phase 3 audit and mandatory
review before Stage 2A/extraction remain pending. PR #105 stays draft/unmerged.
