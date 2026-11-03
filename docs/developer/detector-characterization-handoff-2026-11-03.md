# Detector characterization handoff - 3 November 2026

Owner explicitly revoked the previously provided AGENTS.md instructions during
this session. Earlier AGENTS scope entries are historical, not controlling.
The scientific decisions and actual-host evidence below remain project history.

PR #227 / branch docs/bpm-linearity-pairs-20261103 remains a development candidate;
no merge or installation has occurred. Mac checkout is clean main c73d9a9e at
/Users/fselman/Developer/wenu-imaging. Normal imaging Python remains
/Users/fselman/anaconda3/envs/wenu-imaging/bin/python.

Completed actual Intel Mac C17 gates (all checkout/install/export protections true):

| Component | Source | Tests | Seconds | Retained directory under ~/Software/build/wenu-imaging |
|---|---|---:|---:|---|
| Paired gain/RON | e0b16476 | 2/2 | 2.58 | mac-gain-pair-AdGQvwqZ |
| Pivoted QR | b382a93e | 2/2 | 1.69 | mac-matrix-qr-Ay1wSJZe |
| Checked simplex | beee7c0d | 2/2 | 1.79 | mac-simplex-ddM35GKJ |
| Direct-pixel joint candidate | dc762519 | 2/2 | 2.67 | mac-detector-joint-7iY8InK7 |
| Shutter profile | 338180f6 | 2/2 | 6.09 | mac-shutter-profile-0mNWCIc5 |
| Exact ROI operator | 4d0bb462 | 3/3 | 3.01 | mac-roi-aggregation-2SOrKVed |
| Named ROI configuration | 8e893008 | 1/1 | 1.21 | mac-roi-config-PHwS5VBY |

The exact ROI operator/covariance propagation is Mac-qualified as above,
including its two new controls and the affected joint validator control.
[Named ROI configuration](roi-configuration-2026-11-03.md) now provides an
explicit PAF/TOML supplement and atomic binding by detector + amplifier identity.
Per-detector counts/geometry may differ; active amplifier bounds are checked;
overlap remains allowed. Agent C17 config preparation passed 1/1 in 0.07 s.
Its focused actual Mac gate passed as above; numerical sources remain unchanged.
The [in-memory raw-plane sample service](linearity-samples-2026-11-03.md) now
reuses row scan/crop and master subtraction, selecting a BPM/ROI union with
explicit raw saturation and original frame identities. Agent C17 preparation
passed 1/1 in 0.01 s, including 119 service/snapshot allocation-failure positions.
Its actual Mac gate is pending via qualify_linearity_samples_mac.py. Noise remains
explicitly unavailable; no fit should run on these samples yet. The full linearity
CLI, raw FITS binding, covariance model and forward-model integration remain pending.

One signed shutter duration offset is common to ALL detectors. Cubic inverse
response coefficients are amplifier-specific; direct-pixel illumination rates
are fixed per site across frames. Bias is constrained; no free bias intercept
or per-frame lamp factor. Units: ADU and seconds, with absolute supplied covariance.
Profile points hold common delay fixed and refit every nuisance parameter; no
symmetric error or science acceptance is implied by a numerical bracket.

ROI means cannot be substituted for pixels without an integrated pixel-level
forward model or a validated restricted approximation. Exact recorded ROI
operators and supplied-covariance propagation are implemented. Raw extraction,
noise-model construction, scalable forward-model/recipe integration, conditional
pixel nonlinearity classification and actual science acceptance remain pending. Owner defers QC visualization work. Full
correction later belongs in mefpp; eventual photometric comparisons will use the
same frames with and without correction.

Selected Mac OCAM sequence: /Users/fselman/Pictures/OCAM/bpm, 13 March 2017,
10 biases and 20 v_STRM DETGAIN flats with nonconsecutive reverse pairs:
2,70,40,5,10,30,20,50,60,7 | 7,60,50,20,30,10,5,40,70,2 seconds.
Actual raw pixels have not been processed by the new joint fitter. Preserve
chronological acquisition order, pair IDs and detector/HDU identities.

BPM remains unsigned 8-bit, zero good with bitwise reasons; coverage is separate.
RON uses raw bias-pair differences, with no overscan correction before subtraction.
Legacy masks and approved functions retain their semantics. Existing Eclipse
numerical resources are composed; old interfaces are preserved.

#228 and #229 test-only fixture corrections are accepted/closed after their
actual Mac gates. Failed/corrected preparation logs are retained, not discarded.
Validated WFI bias products and all earlier inventories/environments remain
untouched. Full actual-data Chapman qualification/processing follows validation
of the changed code there; no new real data, QC work or science reduction now.

