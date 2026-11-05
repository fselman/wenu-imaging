# Actual Mac corrected ROI archive complete: all32 detectors

5 November 2026. Owner-returned full console log, checked for complete detector
coverage and terminal status. Controller7ad545d857f8d505a137d25cc5f5ff06208107da;
preparation source0a87c995fd170a40df21845aad711d59238ed7fd; native qualification
source d25b10650bcb5a0a3132cdee3f32e2867ee9f3ff.

## Result and retained locations

BATCH:complete_for_owner_inspection. PRODUCTS:32 NEW:31 REUSED:1.
Retained batch:
`/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-corrected-roi-batch-NrHHb3bT`.
Completion index:
`index.json`. Full outer evidence:
`overall-execution.json`.

CCD65 was verified/reused from
`/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-corrected-roi-CCD65-t6e6o_zg/asdf/linearity-preparation.asdf`,
digest `c12434f5c3bc2fc204968d565819157d4f24f37f20e19b44ff4633451b07549a`.
The remaining31 products are under per-detector CCD directories/asdf. Each ASDF
freezes its own original QC graph and native transports; the batch index points
to all32 including the reused CCD65 location.

Three new callback-only orchestration controls passed on the Mac, followed by
actual serial preparation. The full log contains exactly31 distinct COMPLETED
entries, matching CCD66..CCD96, with100 exposure/ROI rows each. CCD65 contributes
the already verified100. No traceback or failed-batch marker occurs.

| Saved preparation content | Per detector | All32 |
|---|---:|---:|
| Individual exposure/ROI rows |100|3200|
| Pair/ROI records |50|1600|
| Direct-site rows/replay checks |100|3200|
| Detector/frame correction traces |30|960|

The raw sequence has30 unique exposures (10bias+20flat); the960 traces are
per-detector/frame combinations, not960 unique raw images. Counts are enforced
by the accepted preparation service and serial controller. ASDF stage is
scan_corrected_master_bias_subtracted. Noise/covariance remains unavailable;
physical fitting and scientific calibration acceptance remain unperformed.

## Preservation

All11 terminal preservation guards are true:
checkout, installed_files, qualified_source, preparation_source,
private_qc_runtime, native_binary, saved_plan, reused_pilot, controller,
completed_products, images.

Final shared-image verification covered63 input files:30 raw exposures,
32 preserved master products and the selected structural BPM. Existing master
memberships remain9accepted for CCD69/74/77/84/85 and10for the other27. All supplied
bias inputs were prepared for traces without rebuilding the existing masters.
Raw files, earlier uncorrected pair archives, earlier corrected direct-site
archive, diagnostics, failed plans, source/build/runtime and CCD65 remain retained.

Full user console: [mac-corrected-roi-batch-console.log](mac-corrected-roi-batch-console.log).
The human-visible result is actual Mac functional/data-preparation completion,
not a physical correction fit, noise-model acceptance or publication-ready
calibration acceptance.

## Resume from the archive; no preparation replay

The reviewed measurement-preparation/ASDF boundary is now implemented and has
real products for all32detectors. Do not repeat qualification, dependency
admission, master construction, CCD65 or remaining31 preparation, input-image
hash passes or source exports solely to reconstruct this completed stage.

Next use the completion index and saved corrected preparation ASDF to compute
separate diagnostic products and render plots for owner inspection. Reuse the
previously approved diagnostic straight-line/ratio definitions and explicit
15000..35000ADU reference interval where applicable; retain original samples and
outside-interval values. If a reader bridge is needed, adapt it without raw-image
access or another estimator. Earlier no-overscan diagnostic archives stay immutable
and distinctly labelled for comparison.

Do not conflate ROI means with the individual pixel observations used by the
physical response model. The model section consumes prepared ASDF; absent absolute
noise/covariance remains explicit. Owner inspection and instruction precede
physical modelling. No installation, merge, cleanup or new uncertainty/model
choices follow automatically from this completed archive.
