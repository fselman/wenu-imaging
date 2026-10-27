# S2-05 Mac BPM baseline findings — 27 October 2026

Actual clean source `e3c6b463724725b7afb601b7cc0ebe28e24e161a`, branch
`test/stage2-bpm-ownership`, Intel Mac MC02VV0HPHTDG. All 16 pairs / 32 native
invocations completed across C90/C17 ASan/UBSan and separate external leaks.
Every functional case passes with exact accepted 81 mask pixels, 79 good / 2 bad
counts, 0.5–1.5 thresholds, storage/extension identity, and original/observer
header agreement except recorded generated ORIGFILE. All staged inputs and
reference files remain unchanged. Production code was unchanged in this run.

All context/mask owner markers and 48 descriptor boundaries pass. Original
native logs have no ASan/UBSan finding; eight external leaks summaries report
zero unreachable blocks/bytes. Nevertheless, **all 16 observers retain 140 RAM
registrations / 4472 bytes after each cache purge**. No mapped files/references
or swap bytes remain. qfits's global pointer table preserves reachability; a
zero external leaks summary is therefore not evidence of release. The runner
correctly fails the resource gate and preserves the full state.

## Source attribution and defect tickets

| Owned resources without final release | Allocations | Bytes in this fixture | Ticket |
|---|---:|---:|---|
| Cube loader's three-entry frame list | 7 | 124 | #109 |
| Three nine-element double overscan arrays | 3 | 216 | #110 |
| Internally created default header in returned-mask dump | 23 | 462 | #111 |
| BPM publication frame list, input primary/extension headers, temporary metadata/output-name copies and context-owned generated BPM name | 107 | 3670 | #112 |
| Total | 140 | 4472 | #75 parent gate |

The ledger combines source-owned lifetimes with independent reconstruction of
input FITS card string lengths and the inspected Mac ABI structure/element sizes.
Its complete allocation-size multiset equals the original postpurge pointer
listing in all 16 cases; it is not an allocation-stack-trace claim. The
allocation-attribution record retains method, ABI assumptions and totals.

`mef_cube_load` owns the frame list, while its sole source callee currently
frees it only on extension-consistency failure and borrows it elsewhere.
Unconditional caller cleanup therefore also needs removal of that inconsistent
callee destruction to avoid a new double free. Overscan's double array is dead
after double_rms. pixelmap_dump must release its own default header but retain
caller-provided fextra. qfits header insertion copies its value, so publication
can borrow input-header fields until their owning header is destroyed; DATE-OBS
needs its own copy until the later insertion. The heap output-filename result
needs release after copying, and the context must release its owned orig_bpm.

No correction has been native-tested. Tickets #109–#112 stay open pending
corrected actual Mac and unchanged-driver target verification. Shared helper
changes require retaining broader calibration/science and error-path limits;
this fixture suite does not certify all users of those helpers.

## Evidence retained

Original directory:
`~/Software/build/wenu-imaging/mac-stage2-bpm-baseline-mng3l1cq/`.
Archive `mac-stage2-bpm-baseline-evidence.tar.gz`, SHA256
`9e54fff6b0cabc247623e55d20920bef0b914effdca48fc60bae9f98cf01ae67`.
Persistent attachment `libfile_b964fe58d85081918db20275e0750ffc`.
All **367 identities** verified (366 manifest entries plus manifest), all 32
role directories independently checked, raw output/input/source/log hashes
verified, and all numerical products compared to the accepted #90 reference.
The baseline report SHA256 is
`9013c15f23698bede23afea593e98a768aa3ac1d0a2fd3c6696a2252501a785c`.
Selected source files and full per-build source hash lists retain the tested
identities; pixelmaps.c's original identity is in those build lists. Reports,
build identities, full transfer manifest, inspection and attribution summaries
are committed under `fixtures/mac-stage2-bpm-baseline-2026-10-27/`.

Sources/export/checkout, selected engine/configuration and accepted reference
hashes remain unchanged. No installation or observational processing ran.
Preserve the complete failed baseline and all earlier evidence/installations.
S2-05, broader #75, target external diagnostics and remaining S2 gates stay open.
S2-06 follows S2-05; departures require prior agreement and mandatory review
still precedes Stage 2A/extraction. No merge/deletion/cleanup is implied.
