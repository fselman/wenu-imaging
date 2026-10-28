# S2-05 populated-metadata Mac acceptance — 27 October 2026

Update: [actual Chapman3 metadata evidence is inspected and passes](stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md). Earlier target-pending statements below describe preparation history. Full S2-05/#75 and target external diagnostics remain open.

Actual clean source `c6a7a2bf05f8962cd9db4d72989b420f10159406`, branch
`test/stage2-bpm-metadata`, Intel Mac MC02VV0HPHTDG. All **16 pairs / 32 native
calls** pass across C90/C17 ASan/UBSan and separate external-leaks builds. This
supersedes earlier metadata-Mac-pending statements; actual target execution is
pending. Production .c/.h, original native driver/observer and scientific inputs'
image payloads are unchanged from the integrated cleanup source.

## Independently verified results

All returned/production masks preserve all 81 accepted #90 pixels, 79 good /
2 bad, 0/1 polarity, 9x9 geometry, BITPIX=8, existing 0.5–1.5 thresholds and QC
counts. Both retained/known-response fixtures and robust/proportional flags pass.
Actual output primary and data-extension headers retain declared first-frame
ORIGIN, TELESCOP, INSTRUME, MJD-OBS, DATE-OBS and 1x1 binning exactly once; data
EXTNAME is META_CCD_17 and the primary has no EXTNAME. Distinct later-frame
origin/instrument/telescope/time metadata do not replace first-frame values.

Every ordered keyword/comment sequence matches inspected pre-metadata output.
Every unaffected raw header card is identical; only the seven declared primary
values, data EXTNAME and separately recorded generated ORIGFILE differ from
those earlier fixtures. Original/observer canonical outputs match exactly.
Complete raw output hashes are recorded. Each actual staged input hash matches
the derivative manifest, and all 96 staged frame payload comparisons (three
per native role) are byte-identical to the original immutable images. Astropy
input-header readback independently confirms all declared per-frame values.

Every context/mask owner marker balances. All 48 driver/purge descriptor
boundaries preserve count and identity; before/after descriptor limits remain
explicit in native logs. No ASan/UBSan diagnostic occurs; eight separate external
leaks summaries report zero unreachable blocks/bytes. After driver return,
15 RAM allocations / 132 bytes remain as cache state; the first purge releases
them. All RAM pointers/bytes, mapped files/references and swap bytes are zero
after both purges in every case. Nine resource boundaries per observer are
retained and checked against raw native logs, not only report PASS labels.

All command exits/log hashes, selected exported/repository source hashes and
private diagnostic CMake wiring match records. Four builds retain
XMEMORY_MODE=2 / XMEMORY_MAXPTRS=2000000. Sources/export/checkout, selected
installed engine/configuration and both accepted reference reports remain
unchanged. No installation or observational processing occurred.

## Evidence retained

Original run `~/Software/build/wenu-imaging/mac-stage2-bpm-metadata-otkhabux/`.
Archive `mac-stage2-bpm-metadata-evidence.tar.gz`, SHA256
`d2789d5236654640cf8513389667a9d3f7de9af3fa99b1c93b28ff50774d28e3`.
Persistent attachment `libfile_829755c483888191aad200969cf443a2`.
All **372 archive identities** verified (371 manifest entries plus manifest).
Report SHA256:
`26868de58bd3a5c05c82304620d00549b79b2de605bd7bffcbeccd4faa9c308d`.
Full report/manifest, independent inspection provenance and four build identities
are retained under `fixtures/mac-stage2-bpm-metadata-2026-10-27/`. All older
failed/corrected/target evidence remains preserved. Original source .h files,
shared types/ownership declarations and retained probes were not changed.

## Unchanged-driver target preparation and remaining gates

`mefpp2/tests/qualify_bpm_metadata_chapman3.py` is prepared for C90/C17 target
functional/qfits-accounting verification, **8 pairs / 16 native calls**. It pins
this Mac report, all selected native/fixture/oracle identities and exact derived
inputs. Masks, metadata, ordered canonical headers and staged inputs must match
Mac exactly; ownership, descriptor and both zero-purge contracts remain required.
Agent preparation passes Python syntax, source identities, eight reference-case
mappings and actual-Mac-product oracle readback. No target native build/run has
occurred. Compatible target external diagnostics remain an independent open gate;
no uninstrumented accounting result waives it.

This is populated-metadata successful-case qualification for OmegaCAM with
bias=NULL and one extension. Supplied bias, WFI, multiple extensions, remaining
shared-helper coverage, practical failure injection, same-process repetition
and general cache/mmap/swap remain applicable pending S2 work. Full S2-05/#75
stays open; no departure or reduced gate, S2-06 advance, merge/deletion or
installation is authorized. Preserve all runs/archives/installations and the
mandatory review before Stage 2A/component extraction.
