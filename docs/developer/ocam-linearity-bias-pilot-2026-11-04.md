# CCD65 bias dependency for the linearity recipe — 4 November 2026

Issue#236. Returned ROI review at
Pictures/OCAM/wenu-imaging/linearity-roi-review-nnvscgpb completed with all six
preservation checks true. Large ordinary RON is localized in75.parallel_far,
82.near_readout,86.parallel_far and96.parallel_far. Each shown MAD-RON is exactly
1.4826*2/sqrt(2), reflecting a2ADU difference MAD. For integer-valued differences
this coarse statistic does not prove equal noise or identify the extra variance.
Do not replace ordinary variance with MAD, zero the differences, reject ROIs or
infer temporal RON instability from this single pair. CCD95 ordinary RON is~2.5
across all ROIs. CCD69/77 historical flags alone do not establish a current issue.
The largest69/87/88 mismatch rows are all2s; additive offsets, illumination and
spatial structure are not identified separately. CCD88 has5 saturation exclusions
only in parallel_far/30s at mean18374ADU, not whole-frame saturation.

The next necessary corrected-sample dependency is a scan-corrected median master
bias. `Pycavi2/tools/run_ocam_linearity_bias.py` runs one bounded real CCD65 pilot,
using all ten saved-inventory biases (all independently bound toHDU1/native slot0),
canonical OmegaCAM PAF and the explicit verified structural BPM with1=good. The
first two chronological biases remain the RAW RON pair; they are not replaced.
Existing scan rejection10low/10high, frame thresholds0..1000ADU, stack kappa2 and
minimum3 accepted frames are printed and retained unchanged. high_sigma5 is the
previously established bias-QC diagnostic setting; it does not reject pixels or
modify a BPM. No new scientific rejection/normalization/noise setting is chosen.

Reuse the actual Mac-qualified complete bias adapter022cf368 at
mac-bpm-complete-Ia5qliwa/build-c17/mefpp2/mefpp_m5, verifying its original passing
qualification and exact binary hash. There is no rebuild/new test matrix. The
bias-to-ASDF mapper is byte-identical to its qualified022cf368 source. The common
ASDF backend comes from actual passed aecce5c viewer/shared-QC export, preserving
currentQC1.1/fileASDF1.6 and retainedASDF6 private runtime. No plots/HTML are made.
The numerical bias recipe is reused, not rewritten into Python.

The controller is an operational guard/orchestrator patterned on the accepted
real WFI bias run. Python AST syntax passes; no new numerical estimator is added.
The actual OCAM pilot remains pending and is its bounded integration inspection,
not a claim that the ten-frame result is already scientifically accepted.

The exact controller is exported into a fresh Pictures purpose directory. Admit
protected clean main, qualified source/runtime, exact saved-header review anchored
to the completedCCD65 lineage, unchanged raw inode/size/mtime/mode, independent
HDU bindings and structural-copy proof. Freeze whole-file hashes/stat identities
of all ten raw biases and the mask before/after; first two and BPM must match the
previous admitted hashes. Retain native arguments, logs/configuration/handoff,
FITS candidate, common per-input/product ASDF, recipe receipt and overall guard
receipt. Preserve checkout/install/export/private runtime and all sources. Stop
on conflict/failure; no overwrite/retry/cleanup. Inputs are not locked.

The output is a master SIGNAL candidate with actual frame/scan QC and explicit
unavailable variance, not a noise model. Do not assignRON²/N to a median master.
No actual linearity coefficients, statistical distribution, pooling, simulation
count/seed, scientific fit interval or correction acceptance is introduced. Inspect
the resulting per-frame scan/active levels, frame admission and master before
using it in bounded corrected-sample/noise propagation. Preserve the all32 raw
measurements, ASDF, viewer and previous builds. Subsequent plotting/HTML remains a
separate presentation stage. No install, merge or correction activation.
