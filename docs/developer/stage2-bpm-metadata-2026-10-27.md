# S2-05 populated-metadata ownership qualification — 27 October 2026

Update: [actual Chapman3 metadata evidence is inspected and passes](stage2-bpm-metadata-chapman3-acceptance-2026-10-27.md). Earlier target-pending statements below describe preparation history. Full S2-05/#75 and target external diagnostics remain open.

Update: [actual Mac metadata evidence is inspected and passes](stage2-bpm-metadata-mac-acceptance-2026-10-27.md). Earlier native-Mac-pending statements describe preparation history. Unchanged-driver target verification is prepared but unexecuted; full S2-05 remains open.

Status: prepared, actual native Mac execution pending. Baseline main
`f377642ebfd8a8c0a43a99007f5543af34ff9c54`; tracking broader #75/S2-05.
The earlier first successful-case subset and #109–#112 corrections are merged,
with inspected Mac and Chapman3 evidence. Both user hosts were last reported
clean on that main with the merged branches removed; preserve every original
run/archive/transfer copy and installation.

## Purpose and declared matrix

Exercise previously empty primary metadata values through actual mef_build_bpm
publication after the borrowed-string lifetime correction. Demonstrate first-frame
values survive input-header destruction and that input extension naming, all
unaffected output cards and every accepted mask pixel remain intact. No change
to production .c/.h files, numerical algorithms, thresholds, cache/allocator,
configuration policy, detector handling or installation selection is proposed.
The retained original native C driver and forwarding observer remain unchanged.

Run **16 original/observer pairs / 32 native calls**, in C90/C17 ASan/UBSan and
separate external-leaks lanes, two fixture kinds and robust/proportional flags.
Reuse original source fixtures and known reference masks. The new Python staging
helper derives populated headers deterministically in private case directories;
all six original float image payloads remain byte-for-byte identical. Original
PAF and frame-list bytes remain unchanged. An explicit derivative manifest pins
all 10 staged input hashes and primary/extension metadata values. Original
fixture manifest, original driver and all previously qualified source identities
are checked against the inspected corrected Mac report before new workload.

Primary fields: ORIGIN, TELESCOP, INSTRUME, MJD-OBS, DATE-OBS, configured BINX/BINY.
The first three frames have distinct origin/telescope/instrument/time values so
an accidental last-frame selection cannot pass. Binning stays 1x1, matching the
unchanged fixture geometry. EXTNAME becomes synthetic META_CCD_17, identical
across frames, and must survive into the produced data extension. This is a
metadata lifetime fixture, not new detector-ID semantics or a Phase 3 claim.
The physical HDU order/layout and existing production traversal are untouched.

## Native path and required outputs

The existing driver constructs the PAF context, loads all three input frames,
overscan-corrects/trims them, runs the selected gain regression, normalizes and
thresholds the gain image at existing 0.5–1.5 bounds, saves the actual production
MEF and returned mask, then releases mask/context. The unchanged C observer
records nine resource boundaries plus owner/descriptor contracts and two public
cache purges. Only the Python fixture/orchestration/oracle is new.

Independent Astropy readback must establish:

- The exact accepted 81 reference mask pixels, 79 good / 2 bad, 0/1 polarity,
  9x9 geometry, BITPIX=8 and no scaling for every returned and saved mask.
- Every populated primary metadata value equals the declared first-frame value
  in both output primary and data-extension headers, appears exactly once and
  has the original production comment. Output EXTNAME equals input META_CCD_17,
  appears once in the data extension and is absent from the primary header.
- Ordered keyword/comment sequences match inspected pre-metadata output. Every
  unaffected raw header card is identical to that reference, and all original/
  observer canonical outputs agree. Only the seven declared primary values,
  data EXTNAME and separately recorded generated ORIGFILE may differ from the
  earlier fixture output. Generated raw output hashes remain recorded.
- Declared derived input hashes stay unchanged, both owners balance, all three
  descriptor boundaries retain count/identity, and process-start/each purge has
  zero tracked RAM/mapping/swap state. Intermediate/after-driver state remains
  visible. No ASan/UBSan finding, nonzero native/tool exit or nonzero external
  leaks summary is accepted. Missing observations are findings, not passes.

Each source/build/case/role directory gets provenance before workload under
`~/Software/build/wenu-imaging/mac-stage2-bpm-metadata-*`. Record actual clean
source/commit, tools, inputs, outputs and command logs. Preserve sources/export,
protected engine/configuration, original fixture bytes and both reference reports.
The runner continues all declared cases to retain any functional/resource
findings separately; a confirmed new defect needs its own ticket and bounded
correction. No hidden numerical/header adjustment is permitted to obtain a pass.

## Preparation evidence and handoff

Agent preparation passes Python syntax, all six header-only derivative data-byte
checks, Astropy input-value/geometry readback, all pinned derivative input hashes,
16 constructed output-oracle acceptance cases and 256 deliberate incorrect-value/
unrelated-header rejections. These constructed outputs qualify the checking
logic; they are **not native mefpp results**. A first Python-only constructed
output omitted retained comments; the oracle correctly rejected it. That failed
setup/provenance is preserved; correcting the setup to preserve comments passes,
without weakening the oracle. No native build or constructor ran in the agent
environment. Original native observer/driver/oracle/fixtures/old runners and
production source hashes remain identical to the inspected accepted source.

Actual Mac C90/C17 execution and evidence inspection are next. Prepare unchanged
native-driver/fixture Chapman3 verification only after inspecting that Mac run.
Compatible target external diagnostics remain unresolved; functional/accounting
results cannot waive that independent gate. This increment does not cover a
supplied bias, WFI, multiple extensions, practical failure injection, same-process
repeats or general cache/mmap/swap; those remain agreed pending S2 work. Full
S2-05/#75 stays open. No departure from scope/order/coverage/exit criteria is
approved, no S2-06 advance follows merely from this fixture subset, and mandatory
review before Stage 2A/component extraction remains. No merge/branch deletion,
installation, Pycavi changes or observational reprocessing is authorized here.
