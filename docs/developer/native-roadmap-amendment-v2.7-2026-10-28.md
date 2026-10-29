# Frozen roadmap amendment v2.7 — full current-workflow baseline

Date: 28 October 2026 (Chile; 29 October UTC).

Authorization: the owner requested a stage between Stage 2 and Stage 2A: full processing of one OCAM and one WFI dataset with the current mefpp and Pycavi. Name this **Stage 2.1 — Full current-workflow OCAM/WFI processing**. This is an approved roadmap addition, not a processing launch tonight.

## Revised order

Stage 2 accepted bounded memory/ownership campaign → **Stage 2.1 full current-workflow processing** → Stage 2A representation review → Stage 3 contracts/extraction → remaining stages unchanged.

The completed Stage 2 ledger stays 19 planned + 10 retests = 29 actual; #116 stays open/unresolved/deferred, and Phase 3 remains deferred. Stage 2.1 is a separate end-to-end functional baseline, not another memory matrix or reopening of BPM qualification. Frozen v2.0 and amendments v2.1–v2.6 remain byte-identical.

## Stage 2.1 deliverable and boundary

Produce one complete current-workflow reduction for each instrument and one concise baseline/acceptance report, retaining raw/calibration identities, exact software/configuration versions, commands/logs, intermediate/final products and QC summaries. These are comparison references before any data-model migration, component extraction or new calibration method.

Use the current qualified mefpp implementation (accepted native source integrated at main e41525e) and the current Pycavi implementation, with exact revisions and actual executable/package paths pinned before processing. An unchanged system-selected historical executable must not silently substitute for the current qualified source. If a private candidate installation is needed, plan it explicitly while preserving the selected installation/configuration and rollback path. Pin external tools; no upgrades or numerical/refactoring changes are part of this stage.

1. **One preparation/inventory pass:** inspect the actual current notebooks/scripts and select one complete OCAM dataset and one complete WFI dataset. Freeze the intended exposure/filter groups, necessary calibrations, applicability/configuration, host/tool versions and expected product checklist before launches. Full processing covers every exposure/group in the selected dataset, not merely one science exposure. Report missing essential inputs once; do not invent replacements or expand dataset searches indefinitely.
2. **Process both datasets through the existing full supported chain:** calibration association and construction/application as implemented; native preprocessing plus Python normalization; astrometry, source extraction and SCAMP refinement; SWarp resampling/coaddition; supported photometric calibration, QC and final catalogues. Inventory determines the actual applicable notebook path and options. Record whether each BPM/calibration is generated or supplied; static-mask copying must not be described as new BPM generation. No new method or automatic tuning is added to fill a current capability gap.
3. **Review and freeze the two baselines:** verify intended workflow completion and expected product coverage, detector/filter associations, geometry/WCS and units at handoffs, status/logs, input preservation and usable QC reports. Report suspicious numerical/scientific results and incomplete steps honestly. This is functional end-to-end verification and baseline establishment, not automatic scientific or Phase 3 certification.

Use fresh isolated output directories and preserve earlier products/archives/installations. Select the execution host(s) from actual data/tool/resource availability; no duplicated full-workflow host/compiler/sanitizer matrix is required. Batch jobs retain niceness >=10 and controlled numerical-tool threads. Do not repeat the Stage 2 diagnostic suite. Unexpected failures stop dependent processing and receive an explicit bounded disposition; no automatic repair/retest campaign or scope expansion.

Completion gate: both selected datasets finish their agreed current-workflow product checklist, the evidence/baseline report is reviewed, and any blocking findings are resolved or explicitly accepted. Then Stage 2A review may begin; no representation/refactoring implementation starts automatically. ASDF/WISDG and related architecture ideas remain exploratory.

This documentation amendment starts no processing, installation, engine switch, merge or branch deletion. Both user hosts can remain clean on their current main while it is reviewed.
