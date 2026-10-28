# S2-05 populated-metadata Chapman3 acceptance — 27 October 2026

Integration update: Fernando authorized merging PR #114 and cleaning only its merged branch after verifying main ancestry and evidence. Earlier integration-pending/no-merge-authorization statements below are historical; all broader S2 gates and run/installation preservation requirements remain in force.

Actual clean source `b9530c8cfcf60db1aa583571f279b80757952da2`, branch
`test/stage2-bpm-metadata`, Linux chapman3.sc.eso.org. GCC 10.2.1 and CMake
3.29.6 build unchanged Mac-qualified native production sources, original driver,
observer, fixture stager and independent metadata oracle in C90/C17. All **8
original/observer pairs / 16 native calls** pass. This supersedes older target-
pending statements for this populated-metadata increment.

## Independently verified native results

All actual returned/production masks match accepted #90 and inspected Mac
references for every one of 81 pixels, 79 good / 2 bad, binary polarity, 9x9
geometry, unsigned BITPIX=8, no scaling and existing 0.5–1.5 thresholds/QC counts.
Both fixture kinds and robust/proportional constructors pass in both standards.

All 16 target role output dictionaries match their corrected Mac metadata roles
exactly: primary and data-extension first-frame ORIGIN, TELESCOP, INSTRUME,
MJD-OBS, DATE-OBS and 1x1 binning appear once; data EXTNAME is META_CCD_17 and
primary EXTNAME is absent. Distinct later-frame metadata are not substituted.
Ordered saved header cards match Mac exactly except separately recorded generated
ORIGFILE. Independent readback also verifies every unaffected raw card and ordered
keyword/comment sequence against the pre-metadata reference. Raw output hashes
and generated values remain recorded. Original/observer output sets agree.

Staged input hashes match declared derivatives and Mac exactly. All 48 staged
frame payload comparisons (three per native role) are byte-identical to original
accepted images; input headers independently match declared per-frame values.
No production .c/.h, shared interface, original native observer/driver, metadata
oracle or source fixture changed for target verification.

Every context/mask owner contract balances. Descriptor count/identity remains
3 to 3 at all 24 driver/purge boundaries; before/after limits are explicitly
retained. Nine resource boundaries per observer are checked against raw logs.
After native driver return, 15 RAM allocations / 132 bytes remain as cache state.
The first public purge releases them; all RAM pointers/bytes, mapped files/
references and swap bytes are zero after both purges in every case.

All 23 commands exit zero and log hashes match. Both compile-command inventories
are uninstrumented as declared; qfits XMEMORY_MODE=2 and XMEMORY_MAXPTRS=2000000
remain unchanged. This is target **functional/qfits-accounting acceptance**, not
external sanitizer/leak-tool acceptance. Compatible target external diagnostics
remain an independent open gate. Mac separately passed ASan/UBSan and eight
external-leaks summaries across 16 pairs; see [Mac acceptance](stage2-bpm-metadata-mac-acceptance-2026-10-27.md).

## Retained evidence

Original run:
`~/Software/build/wenu-imaging/chapman3-stage2-bpm-metadata-p8__ggrf/`.
Archive `chapman3-stage2-bpm-metadata-evidence.tar.gz`, SHA256
`6c73e30d674d63748f0b25bcba00e90291b90805c8bf10a12d77aaa696ee3a59`.
Mac transfer directory:
`~/Software/build/wenu-imaging/chapman3-bpm-metadata-transfer-1ZPHKzye/`;
user verified copied archive hash before attachment. Persistent attachment
`libfile_85350abc84f88191a17ad3c75d149882`.
All **203 member identities** verified (202 manifest entries plus manifest), all
16 role input/output sets independently read and compared, source/command/log/
resource identities checked. Report SHA256:
`e493a3d4c9f163cb0bf5ca366b8460b668143b7495c05ede7460a9730d586268`.
Report, full transfer manifest, two build identities and independent inspection
provenance are committed under `fixtures/chapman3-stage2-bpm-metadata-2026-10-27/`.
The earlier attachment with 200 members/hash fdb62b70 was the already accepted
previous BPM cleanup archive, not admitted as metadata evidence. Both attachments
are preserved; the correct 203-member archive supplies this acceptance.

Sources/export/checkout, selected installed engine/configuration, accepted Mac
metadata report and older mask reference remain unchanged. No installation,
observational processing or production patch occurred. Preserve all earlier
failed/corrected/target runs, archives, transfer copies and normal installations.

## Full S2 position

Populated-metadata successful-case ownership is now accepted on Mac and Chapman3
within the declared OmegaCAM, bias=NULL, single-extension subset. PR #114 awaits
review/integration; no merge, branch deletion or run cleanup is authorized.
Full S2-05/#75 remains open for supplied bias, WFI/multiple extensions, remaining
shared-helper coverage and applicable practical failure/repeat/general cache/
mmap/swap gates. Target compatible external diagnostics remain unresolved.
No departure or weaker gate or advance to S2-06 is approved. Prior agreement
is required for departures, and mandatory review before Stage 2A/component
extraction remains. The early Phase 3 audit is still pending.
