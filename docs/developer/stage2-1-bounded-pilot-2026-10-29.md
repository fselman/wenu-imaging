# Stage 2.1 bounded functional pilot — 29 October 2026

## Owner scope and disposition

The owner explicitly limits today's pre-refactoring test of current software to one filter per instrument and at most five science exposures of identical integration time within each set. Different integration times between instruments are allowed. This dated instruction controls today's work over older full-dataset launch wording. Keep the broader Stage 2.1 roadmap recorded; today's bounded pilot does not by itself establish full-dataset completion or authorize expanding beyond these selections.

Use existing configured WFI gains, as expressly authorized. Do not turn this functional test into a scientific gain audit, invent new calibration methods, or repeat Stage 2 diagnostics. Later, once wenu-imaging works properly, the first reductions will be linearity frames and biases to determine BPMs, RONs and gains, with derived values injected into product headers. That future calibration work is recorded direction, not today's implementation.

## Science selection

OCAM CP Pup: r_SDSS, five exposures at EXPTIME=20 s, from /Users/fselman/Pictures/OCAM/raw_files/CPPup_raw:
- OMEGA.2017-03-13T02:35:52.825.fits
- OMEGA.2017-03-13T02:36:57.286.fits
- OMEGA.2017-03-13T02:38:02.286.fits
- OMEGA.2017-03-13T02:39:07.286.fits
- OMEGA.2017-03-13T02:40:12.356.fits

WFI Trapezium-core: BB#B/99_ESO842, five exposures at EXPTIME=89.9177 s, from /Users/fselman/Pictures/WFI/raw_orion/sci:
- WFI.2001-12-11T02:01:24.777.fits
- WFI.2001-12-11T02:08:04.470.fits
- WFI.2001-12-11T02:14:31.809.fits
- WFI.2001-12-11T07:20:51.824.fits
- WFI.2001-12-11T08:45:41.017.fits

Filename and DATE-OBS millisecond differences are retained as observed; do not rename originals. Keep required bias/dome/sky calibration inputs; the five-exposure cap applies to science. Raw-input hashes, associations, execution settings and expected product coverage must be frozen before native reductions.

## Current software and configuration

Actual Mac checkout is clean main e41525ed318f81e8b9ba9e6df538b4cb6758dc1f. Private installation at /Users/fselman/Software/build/wenu-imaging/mac-stage2-1-install-rBleOnWB was built from that revision using the supported configure/make/install interface in C17; runtime resources are included. Native manifest verification and byte comparisons of all 23 installed Python source files passed. The historical installation/global configuration and checkout were verified unchanged. No observational processing has run.

Private mefpp SHA256: 5acd03bc33f1413e475c71130af9f4d7bb81e9547092417fbec6f2b1a44e8d01.
Use the existing dedicated Python environment and private Python target directory, with the private executable configuration; no dependency upgrades or global selection changes.

Raw WFI CONAD values are zero for six detectors in all 47 inventoried science frames (#131). Owner-authorized disposition: use native configured product GAIN values through an explicit private WFI instrument gain-key mapping. Verify the actual native-to-Python header handoff; do not alter raw headers or silently infer missing values. Retain configured detector mapping and the existing mosaic normalization calculation. #131 remains open until this functional handoff is verified, without a historical/scientific calibration audit.

Current notebook BPM handling copies supplied bundled static masks; record them as supplied, not newly generated. The 39-file OCAM compatibility check passed. WFI calibration metadata checks passed for 65 files; the full science Exposure reader checks were not reached because the earlier preflight gain assertion stopped them. Recheck only the selected five under the authorized gain disposition, without replaying unrelated matrices.

## Execution and acceptance

Prepare fresh isolated project/output directories. Exercise current library paths underlying the notebooks: partition/associate, calibration construction/application, native science preprocessing and Python normalization, astrometry/extraction/SCAMP, SWarp, and supported photometric/QC/catalogue stages. Freeze an applicable product checklist; report existing capability gaps explicitly instead of adding algorithms or tuning.

Batch niceness >=10; controlled numerical/external-tool threads; stop dependent processing on unexpected failures for bounded disposition. Preserve all raw files, prior products, evidence, installations and global configuration. Record hashes, commands/logs and products as a pre-refactoring functional baseline. No scientific or Phase 3 certification, automatic representation/refactoring work, duplicate platform/compiler campaign, or extra science exposure/filter is authorized.

Stage 2 remains accepted at 19 planned + 10 retests = 29 actual; #116 and Phase 3 remain deferred. This planning record merges no PR and changes no user checkout.
