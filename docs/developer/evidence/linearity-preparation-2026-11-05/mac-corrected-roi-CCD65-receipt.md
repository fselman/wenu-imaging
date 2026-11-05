# Actual Mac CCD65 corrected ROI preparation

5 November 2026. Owner-returned actual real-data execution receipt.

Retained run:
`/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-corrected-roi-CCD65-t6e6o_zg`.

PREPARATION:complete_for_owner_inspection. All eight preservation checks true:
checkout, installed_files, qualified_source, preparation_source, private_qc_runtime,
native_binary, saved_plan, images.

Product:
`asdf/linearity-preparation.asdf`.
Digest:
`c12434f5c3bc2fc204968d565819157d4f24f37f20e19b44ff4633451b07549a`.
Detector:ESO_CCD_#65; pair/ROI records50; exposure/ROI rows100; direct-site rows100;
trace_frames30; noise_state:unavailable. These are preparation measurements, not
an accepted physical calibration or fit. Existing corrected master reused.

Source0a87c995fd170a40df21845aad711d59238ed7fd from the saved all32 plan at
ocam-linearity-preparation-plan-KSBh9ZXu. Native build remains actual-Mac-qualified
d25b106 at mac-linearity-recipe-rSGbf1Mq/build-c17. Do not repeat CCD65 extraction,
master construction, full dependency admission or old qualification.

Next: remaining31 serial calls to the same prepare_detector service, with the
completed CCD65 product verified/reused in the final32product index. The batch
controller verifies exact sources/binary, preserves per-detector image guards,
and checks the union of input images and completed products at batch end.
Three callback-only orchestration controls passed in0.004s: unique cohort and
CCD65 reuse, serial complete coverage, fail-stop on bad or incomplete results.
The Mac launch runs those three new controls, then real preparation; no native
rebuild or broad gate replay. Actual remaining31 execution remains pending.

No estimator or uncertainty policy changes. Noise/covariance remains unavailable;
no physical fit, plotting, installation, merge or cleanup. Independent saved
ASDF diagnostics/plots and owner inspection follow the completed corrected archive.
