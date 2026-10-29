# Stage 2.1 functional results — 29 October 2026

## Result and evidence level

Both bounded sets passed current mefpp/Pycavi processing through notebook 04 on Intel Mac MC02VV0HPHTDG, macOS 13.7.8. This records user-returned actual-host terminal results and the checks performed by the supplied launchers. Large FITS products and full JSON reports remain on the Mac; they have not been independently downloaded and re-read by the agent. The owner accepted Stage 2.1 on 29 October 2026 and explicitly authorized merging PR #130 and cleaning its merged branch. This closes the amended functional gate; scientific/Phase 3 certification remains separate.

The endpoint is controlled by immutable amendment v2.8. No new scope or acceptance requirement is added, and no frozen roadmap/amendment is edited.

| Instrument | Science set | Partitions | WCS MEFs | Solved detector images |
|---|---|---:|---:|---:|
| OCAM / CP Pup | r_SDSS; 5 × 20 s | 1 | 5 | 160 |
| WFI / Trapezium-core | BB#B/99_ESO842; 5 × 89.9177 s | 3 | 5 | 40 |

## Software and retained evidence

Tested source: e41525ed318f81e8b9ba9e6df538b4cb6758dc1f.
Private installation/root: /Users/fselman/Software/build/wenu-imaging/mac-stage2-1-install-rBleOnWB.
Project root below it: pilot-5-per-instrument.

Private mefpp SHA256: 5acd03bc33f1413e475c71130af9f4d7bb81e9547092417fbec6f2b1a44e8d01.
Python: /Users/fselman/anaconda3/envs/wenu-imaging/bin/python, private installed package selected through PYTHONPATH.
solve-field: /usr/local/Cellar/astrometry-net/0.95_2/bin/solve-field.
solve-field SHA256: 52f02377de0d9808ed8e338d319ec3074fb3e9e2c6da461f8104611bae0b3150.

Retained report paths relative to the project root:

- omegacam/native-stage.json — native-stage-passed; five science products, two bias partitions, one dome and one sky partition; 34 raw-input hashes unchanged.
- omegacam/normalized/normalization-report.json — normalization-passed; five exposures / 32 detectors each; native products unchanged.
- omegacam/normalized/astrometry-report.json — astrometry-passed; five WCS MEFs / 160 solved detector images; normalized input hashes and pixels preserved.
- wfi/native-stage.json — original stopped verifier retained; it incorrectly required generic GAIN after successful native processing.
- wfi/native-inspection.json — subsequent passing pixel/preservation inspection of all five products / 40 detectors and 36 raw-input hashes.
- wfi/normalized/normalization-report.json — passing configured-gain working-copy normalization; native products unchanged.
- wfi/normalized/astrometry-report.json — five WCS MEFs / 40 solved detectors; pixels and normalized inputs preserved.

Logs remain in each project's logs directory and each normalized/logs directory, with per-detector solve-field commands/logs under the exposure solve directories. Original input locks, native products, normalized products, WCS MEFs, private installations and failed history are retained. Terminal evidence was returned in the Work conversation, including Pasted text(7).txt (OCAM normalization) and Pasted text(8).txt (OCAM astrometry).

## Exercised behavior and checks

Existing Pycavi association/native reduction functions constructed and applied required bias/dome/sky/master-flat calibrations and preprocessed the selected science frames. BPMs were supplied static masks, not newly characterized masks.

Normalization used mefpp_normalize_science with apply_light_corr=False on separate copies. OCAM used its configured detector CONAD headers; WFI used the explicitly owner-authorized PAF gains inserted as generic GAIN in working copies, preserving original ESO cards. Full detector pixels were checked against the current mean-gain/exposure-time scaling; units, exposure times, finite pixels and original-product hashes passed.

Astrometry used run_solve_field with two workers and the pinned executable, followed by create_wcs_frame only after all configured detector solutions existed and had finite celestial WCS transforms. Assembled MEFs were checked for detector coverage, WCS validity, units/exposure times and exact pixel preservation. These are functional checks, not an independent astrometric residual or photometric quality audit.

## Boundaries and next step

Stage 2 remains separately accepted at 19 planned + 10 retests = 29 actual launches. Stage 2.1 observational processing does not alter those campaign counters. No memory/compiler matrix was repeated.

The failed first WFI SCAMP attempt is retained outside Stage 2.1. No SCAMP retry, SWarp, photometry, illumination, downstream QC or final catalogue is required by this gate. #30 remains open for SCAMP failure propagation; #131 remains open for the production gain-header contract. #116 remains deferred. Scientific validation, Phase 3 certification and future bias/linearity characterization are separate work.

Owner disposition: Stage 2.1 accepted; merge PR #130 and clean its exact merged branch, then synchronize clean user checkouts with guarded fast-forwards. Preserve all data, reports, builds and installations. Next substantive topic is Stage 2A review. No installation switch, Stage 2A implementation, refactoring or repeated reduction is authorized by this closure.
