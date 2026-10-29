# Frozen roadmap amendment v2.8 — Stage 2.1 ends at notebook 04

Date: 29 October 2026 (Chile).

Authorization: the owner explicitly requested that Stage 2.1 stop at the mefpp reductions through the Pycavi notebooks up to and including solve-field and correction of the WCS. This amendment supersedes v2.7's downstream-processing completion requirements; frozen v2.0 and amendments v2.1–v2.7 remain byte-identical.

## Revised scope and order

Accepted Stage 2 → **Stage 2.1 current mefpp/Pycavi reductions through notebook 04 (solve-field and WCS-corrected MEF assembly)** → Stage 2A representation review → Stage 3 contracts/extraction. Stage completion does not automatically authorize representation changes or refactoring implementation.

Keep the owner's bounded selection: one filter per instrument, at most five science exposures of identical integration time within each instrument's set. The current selections are five OCAM CP Pup r_SDSS exposures at 20 s and five WFI Trapezium B exposures at 89.9177 s. The owner explicitly authorized all three WFI science partitions; the limit is five exposures in total, not five per partition. Keep required calibration frames separately from the science cap.

## Included work and final products

1. Lock software, instrument/PAF settings, science/calibration inputs, associations, host/resources and intended outputs.
2. Exercise the existing notebook-00/01 setup and partition/association paths and notebook-03 library routines for supported calibration construction/application and native science preprocessing. Record supplied BPMs honestly; current Python BPM handling copies the bundled static mask.
3. Apply the existing Python science normalization. Use the owner-authorized configured WFI gains through documented metadata preparation in separate working copies; preserve original raw headers and native products. Do not derive new gains/RON/BPMs or conduct a scientific calibration audit for this baseline.
4. Exercise notebook-04 library calls: extract detectors, run Astrometry.net solve-field, then create the WCS-corrected science MEFs from the solved detectors.

**Final Stage 2.1 science products are the five WCS-corrected MEFs per instrument**, with retained calibration/preprocessed/normalized products and a concise baseline report. Require intended exposure/detector coverage, actual detector solutions, finite WCS checks, preserved pixel values across WCS assembly and retained input/configuration identities. Functional checks do not certify astrometric accuracy or scientific/Phase 3 readiness.

## Outside the Stage 2.1 completion gate

Notebook 05 source extraction/SCAMP refinement, notebook 06 SWarp/resampling/coaddition, and notebooks 07–09 photometric calibration, illumination modeling, downstream QC and final catalogues are deferred to later workflow work. They remain project capabilities/backlog; their completion, VizieR access and correction of the SCAMP wrapper are not Stage 2.1 prerequisites. No new stage number, downstream execution or implementation is selected by this amendment.

The stopped first-exposure SCAMP attempt and completed first-exposure SExtractor catalogue remain preserved historical evidence outside this boundary. Do not retry SCAMP, regenerate successful earlier products, switch reference release or repair #30 merely to close Stage 2.1.

## Status at the scope change

Actual Mac software source is e41525ed318f81e8b9ba9e6df538b4cb6758dc1f, with private installation /Users/fselman/Software/build/wenu-imaging/mac-stage2-1-install-rBleOnWB. Both project preparations passed; raw-input locks contain 34 OCAM inputs (29 calibration + five science) and 36 WFI inputs (31 calibration + five science).

WFI: native products passed five-MEF/40-detector pixel checks and all 36 original input hashes. Configured gains were supplied only in separate working-copy headers from the existing WFI PAF; mean gain 2.125 e-/ADU. Actual unchanged normalization passed full pixel-scaling and metadata checks, preserving native files. Astrometry passed five WCS MEFs / 40 detector solutions, finite WCS checks, exact pixel preservation and unchanged normalized inputs. Evidence is user-host terminal output and retained JSON/logs; large FITS files have not been independently transferred/reread by the agent.

WFI project: /Users/fselman/Software/build/wenu-imaging/mac-stage2-1-install-rBleOnWB/pilot-5-per-instrument/wfi. Its normalized/normalization-report.json and normalized/astrometry-report.json record passing statuses. native-stage.json retains the original failed generic-GAIN verifier; native-inspection.json supplies the later successful pixel/input-preservation check. Preserve both histories.

OCAM: prepared with one science partition; native runner was supplied but its actual execution/result has not been returned in this chat. Do not claim OCAM completion, repeat it blindly, or close the whole Stage 2.1 from WFI alone. Obtain existing OCAM result/status and complete only missing work through notebook 04.

The first WFI SCAMP attempt stopped on a VizieR connection timeout; the wrapper's false-success message is recorded under #30. #131 retains the production gain-header contract finding; the owner-authorized functional workaround passed. Both remain recorded outside this stage's endpoint; no source correction or scientific calibration is claimed.

## Completion and preservation

Stage 2.1 closes after both bounded instrument sets meet the notebook-04 product/checklist and their concise baseline/evidence review is complete. No downstream catalogue/coadd or full raw-collection reduction is required. Existing successes are reused with their exact source/settings/evidence; do not repeat the Stage 2 memory/host/compiler/sanitizer matrix.

Preserve all raw files, failed/successful reports, intermediate/final products, archives, installations and global configuration. Batch niceness >=10 and controlled threads remain required. Stage 2 stays accepted at 19 planned + 10 retests = 29 actual. #116 and Phase 3 remain deferred. Later, once wenu-imaging works properly, bias and linearity reductions will determine BPMs, RONs and gains for injection into product headers; that future calibration implementation is not part of this amendment.

This documentation change launches no processing, performs no merge or checkout synchronization, and does not start Stage 2A automatically.
