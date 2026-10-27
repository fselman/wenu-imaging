# S2-05 Chapman3 BPM acceptance — 27 October 2026

Actual clean target source `df216ca15a378f782aa7a7443f7e6d763e343611`, branch
`fix/112-bpm-owned-resources`, Linux chapman3.sc.eso.org. GCC 10.2.1 and CMake
3.29.6 build unchanged Mac-qualified native sources, original driver, observer,
fixtures and output oracle in C90/C17. This supersedes earlier target-pending
statements. Acceptance is limited to the declared successful BPM fixture subset.

## Functional and accounting results

All **8 original/observer pairs / 16 native calls** pass. Independent FITS readback
of every target role matches the corresponding corrected Mac role and older
accepted #90 mask reference: all 81 pixels, 79 good / 2 bad, 0/1 polarity, 9x9
geometry, BITPIX=8, extension identity, threshold and QC headers. Canonical saved
header cards and input hashes match Mac exactly. Only generated ORIGFILE values
are excluded from header equality and are separately recorded; raw output hashes
are retained. Ordinary/observer complete output sets agree in every case.

All eight context/mask contracts balance. Descriptor identity and count remain
3 to 3 at all 24 driver/purge boundaries. The observed descriptor soft limit
changes from 1024 to 4096 (hard limit 4096), retained explicitly. Nine resource
snapshots are verified per observer. After native driver return, 15 RAM
allocations / 132 bytes remain as cache state; first purge releases them. All
RAM pointer/byte, mapped-file/reference and swap fields are zero after both
purges in every case. No incomplete observation or suppressed finding remains.

All 23 commands complete with exit status zero; raw log hashes match. Both
compile-command inventories are uninstrumented, matching the declared target
lane. qfits XMEMORY_MODE=2 / XMEMORY_MAXPTRS=2000000 and production cache policy
are unchanged. Sources/export/checkout, protected selected engine/configuration,
corrected Mac report and older accepted reference remain unchanged. No install
or observational processing occurred.

This is **target functional and qfits-accounting acceptance**, not external
sanitizer/leak-tool acceptance. Compatible target external diagnostics remain an
independent open gate; old GCC 4.8 runtimes were not substituted for GCC 10.
[Mac acceptance](stage2-bpm-mac-acceptance-2026-10-27.md) separately establishes
C90/C17 ASan/UBSan, external-leaks and accounting results for 16 Mac pairs.

## Evidence and transfer

Original target directory:
`~/Software/build/wenu-imaging/chapman3-stage2-bpm-x9qnwvvo/`.
Archive `chapman3-stage2-bpm-evidence.tar.gz`, SHA256
`fdb62b7074f77feada39578c86a692e14a68a2ebc7b723c49bf1831ce53aa8b4`.
Mac transfer directory:
`~/Software/build/wenu-imaging/chapman3-bpm-transfer-DKVOeNxw/`;
the user verified the copied archive hash before attachment.
Persistent attachment `libfile_1956b527ade081919a7aef73cf884728`.
All **200 member identities** verified (199 manifest entries plus manifest), all
16 role input/output sets independently read and compared, native/resource/
descriptor logs checked and selected exported sources matched to Mac-qualified
repository bytes. Report SHA256:
`3a0440fed82afa0f4578de782e0567dcbd0e97bd548e50551e7ac494522e0cf8`.
Report, full transfer manifest, two build identities and independent inspection
provenance are committed under `fixtures/chapman3-stage2-bpm-2026-10-27/`.

## Current S2 position

The focused corrections for #109–#112 now have inspected Mac diagnostic and
Chapman3 functional/accounting evidence for these cases. PR #108 retains the
failed baseline; stacked PR #113 contains the correction and corrected evidence.
Both await review/integration; issues remain open pending integration. This
acceptance does not itself authorize merge, branch deletion or run cleanup.

The successful OmegaCAM, bias=NULL, single-extension fixture subset is accepted.
Full S2-05 and #75/S2 are still open: populated optional metadata, WFI, additional
extensions/non-NULL bias and shared-helper other-recipe coverage remain to be
qualified, alongside applicable practical failure injection, same-process
repeat and general cache/mmap/swap gates. Do not advance to S2-06 on the premise
that this first subset completes S2-05. No departure or reduced completion gate
is approved. Preserve all failed/corrected/target runs, archives, transfer copies
and installations. Departures require prior agreement; early Phase 3 audit and
mandatory review before Stage 2A/component extraction remain pending.
