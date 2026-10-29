# Stage 2.1 bounded functional pilot — 29 October 2026

Stage 2.1 endpoint revised by owner, 29 October 2026: [immutable amendment v2.8](native-roadmap-amendment-v2.8-2026-10-29.md) makes the gate **current mefpp/Pycavi reduction through notebook 04: native calibration/science preprocessing, Python normalization, solve-field and WCS-corrected MEF assembly**. Keep one filter and at most five equal-integration-time science exposures per instrument; all three WFI partitions are authorized for the same five exposures in total. Notebook 05 extraction/SCAMP, SWarp, photometric/illumination work, downstream QC and final catalogues are outside Stage 2.1 and deferred to later workflow work. Older v2.7/full-chain completion wording is historical and superseded; do not reopen it as a closure requirement.

Both bounded instrument sets have now passed the Stage 2.1 functional endpoint on the Intel Mac: native preprocessing, Python normalization, solve-field and WCS-corrected MEFs. OCAM: five r_SDSS exposures at 20 s, one partition, 160 solved detector images. WFI: five BB#B/99_ESO842 exposures at 89.9177 s across three partitions, 40 solved detector images. Pixel/input preservation checks passed. See the [returned-result receipt](stage2-1-functional-results-2026-10-29.md) for evidence paths and limits. Processing is complete through notebook 04; owner review/integration remains pending. Preserve the failed first WFI SCAMP attempt outside this gate; #30/#131 remain open for later production work. No scientific/Phase 3 certification or automatic Stage 2A/refactoring is claimed.

## Owner scope and disposition

The owner explicitly limits today's pre-refactoring test of current software to one filter per instrument and at most five science exposures of identical integration time within each set. Different integration times between instruments are allowed. This dated instruction controls today's work over older full-dataset launch wording. The later owner endpoint amendment v2.8 makes reduction through notebook 04 the Stage 2.1 completion gate for these bounded sets; no full raw-collection or downstream workflow completion is required.

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

Actual Mac checkout is clean main e41525ed318f81e8b9ba9e6df538b4cb6758dc1f. Private installation at /Users/fselman/Software/build/wenu-imaging/mac-stage2-1-install-rBleOnWB was built from that revision using the supported configure/make/install interface in C17; runtime resources are included. Native manifest verification and byte comparisons of all 23 installed Python source files passed. The historical installation/global configuration and checkout were verified unchanged. Both instrument sets have since returned passing native, normalization and notebook-04 astrometry results; see the returned-result receipt linked above.

Private mefpp SHA256: 5acd03bc33f1413e475c71130af9f4d7bb81e9547092417fbec6f2b1a44e8d01.
Use the existing dedicated Python environment and private Python target directory, with the private executable configuration; no dependency upgrades or global selection changes.

Raw WFI CONAD values are zero for six detectors in all 47 inventoried science frames (#131). Owner-authorized configured gains were supplied explicitly as generic GAIN cards in separate native-product copies, with private WFI configuration mapping normalization to GAIN. Native science output did not contain generic GAIN: preserve the original failed verifier and the later passing inspection. The actual existing normalization routine passed full scaling and preservation checks; original ESO gain cards remain intact. #131 remains open for the production header contract; the bounded workaround is verified. No historical/scientific gain audit is required.

Current notebook BPM handling copies supplied bundled static masks; record them as supplied, not newly generated. The 39-file OCAM compatibility check passed. WFI preparation subsequently passed for the selected five science exposures and 31 B-filter/bias calibration inputs, with three science partitions. The owner explicitly authorized reducing all three partitions; the total science count remains five.

## Execution and acceptance

Prepare fresh isolated project/output directories. Exercise current library paths underlying notebooks 00/01, 03 and 04: partition/associate, supported calibration construction/application, native science preprocessing, Python normalization, detector solve-field and WCS-corrected MEF assembly. Stop there. Notebook 05 extraction/SCAMP and all subsequent coadd/photometric/illumination/QC/catalogue work are outside this completion gate. Freeze an applicable product checklist; report existing capability gaps explicitly instead of adding algorithms or tuning.

Batch niceness >=10; controlled numerical/external-tool threads; stop dependent processing on unexpected failures for bounded disposition. Preserve all raw files, prior products, evidence, installations and global configuration. Record hashes, commands/logs and products as a pre-refactoring functional baseline. No scientific or Phase 3 certification, automatic representation/refactoring work, duplicate platform/compiler campaign, or extra science exposure/filter is authorized.

Stage 2 remains accepted at 19 planned + 10 retests = 29 actual; #116 and Phase 3 remain deferred. This planning record merges no PR and changes no user checkout.
