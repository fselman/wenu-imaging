# Integrated Stage 2 preparation — 28 October 2026

Owner accepted frozen v2.0 plus v2.1. Fixed F1–F5 campaign cap: 19 planned native
launches and two global correction/retest rounds. Preparation has started;
**native launches consumed: 0; correction rounds consumed: 0**. No merge or
installation change is authorized. Use one campaign branch/PR, not one per recipe.

## Actual WFI inventory

`inventory_wfi_campaign.py` reads `/Users/fselman/Pictures/WFI` on the qualified
Mac under its existing Anaconda Python. It inspects FITS primary/extension headers
and file statistics without accessing pixel arrays, running the engine, selecting
calibrations, modifying originals or hashing every raw payload. It records type,
filter, binning, readout, exposure/time and extension geometry. File-stat identities
must remain unchanged. Directory symlinks are not followed. Gzip files receive a
primary-header-only preview to avoid full sequential decompression; selected-file
geometry is checked at the single input-lock step. All errors/missing keys remain
in the report rather than triggering automatic data substitutions.

Fresh retained provenance precedes the scan. The inventory produces one compact
archive with readback/hash verification. Exact selected input content hashes and
one coherent group are locked after this actual-host report is inspected. No F2
processing starts before that lock; all missing inputs will be reported together.

## Tiny integrated fixture A

`prepare_integrated_campaign_fixture.py` prepares two distinguishable synthetic
extensions: 3 bias, 3 BPM, 5 dome, 5 sky and 1 science MEFs. The production PAF is
preserved; a staged derivative changes only declared tiny geometry/region/kernel
settings, two detectors and the already accepted test BPM bounds/robust flag.
Overscan is 10. Bias levels -1/0/1 ensure nonzero clipping width and median zero.
Detector responses are 1 and 2; flat construction preserves their shared reference.
BPM sentinels mirror between extensions. Science is 1000 times detector response.

Independent Python input checks pass for all 17 files / 34 extensions, the median
zero bias, response ratio 2, expected 79-good-pixel masks, and analytic corrected
science 1000. Known-answer expectations are bias zero, normalized dome/sky/combined
flat 1 and 2, mirrored masks and science 1000 in both extensions. This is fixture
preparation, not native algorithm/output or memory acceptance. Native oracle and
observer/harness wiring remain in preparation.

The engine trace confirms existing `mef_engine` already invokes `mef_build_cal`
for bias/dome/sky, `mef_build_bpm`, `mef_ff_combine`, science correction and save
sequentially by extension. The campaign will observe those calls and cleanup,
retaining intentionally live calibrations between stages. Native processing and
failure injections have not run. No numerical source correction is made here.

Update: all 272 actual WFI header/stat records are inspected with zero header errors and reported source-stat preservation. The fixed selection is 11 unique Orion B-band files, all 1x1/normal/eight matching extensions, using 3 bias, 3 BPM, 3 dome, 3 sky and 1 science input. Two BPM frames also appear in the dome list. Exact selected-file hashes and small physical-pixel readiness samples await the Mac input-lock helper; no native launch has occurred. See stage2-wfi-input-selection-2026-10-28.md.
