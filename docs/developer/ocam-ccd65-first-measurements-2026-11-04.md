# First actual OCAM CCD65 raw-pair measurements — 4 November 2026

Owner-returned receipt, not an agent rerun. Native qualified source:
512092fa3180653f165f744a1ba7d9991e251f03. Retained run:
/Users/fselman/Pictures/OCAM/wenu-imaging/ccd65-raw-pairs-bpmfixed-zfs377ok.

## Completion and preservation

measurement/execution.json reports complete_for_owner_inspection, detector
ESO_CCD_#65/output L, five ROIs, native exit0, one detector processed,50 pairs.tsv
rows and5 bias-ron.tsv rows. All30 final source fingerprints match. Outer checkout,
installed_files and exported_source checks pass. Owner then verified the full
pairs.tsv output hash and returned all50 compact rows without raw rereading.
This is numerical execution/inspection evidence, not fitted scientific calibration.
No gain interval, noise distribution, covariance or all-detector fit is selected.

Selection retains first two raw biases, >=65534ADU exclusion,1=good binary BPM,
ten nonconsecutive acquisition-order flat pairs and five reviewed ROIs. Only BPM
path/asset changes to the byte-verified structural copy, with lineage.json recording
the original. No scan correction precedes these raw-pair statistics; ordinary
variance is authoritative and MAD is diagnostic. No normalization/median-zeroing.

## Owner-returned diagnostic summary

| ROI | Raw bias RON,ADU | Bias difference mean,ADU | Valid pixels |
|---|---:|---:|---:|
| near_readout |1.974218|-3.812283|262144|
| serial_far |1.971490|-3.815113|262144|
| parallel_far |2.028334|-3.869883|262141|
| far_corner |2.228890|-3.861133|262143|
| center |2.147637|-3.874359|262144|

Bias difference median is-4ADU; raw difference MAD is2ADU and MAD-based RON is
2.096713ADU for all five regions. Possible uncorrected spatial contributions have not been separated; no detector
fault or distribution is inferred.

All50 rows have arithmetic_available gain; no nonfinite or saturation exclusions.
BPM exclusions are consistently0,0,3,1,0 across the five named ROIs. Fractional
pair mismatch ranges0.000151752 to0.00718366 (0.0152%-0.7184%).

| Exposure,s | Minimum point gain over five ROIs,e/ADU | Maximum,e/ADU | near_readout S/t,ADU/s |
|---|---:|---:|---:|
|2|2.27332|2.30985|474.619|
|5|2.29837|2.31218|475.444|
|7|2.25685|2.31920|476.247|
|10|2.28686|2.32495|476.134|
|20|2.31721|2.33524|477.020|
|30|2.33126|2.34650|477.697|
|40|2.34792|2.37558|478.225|
|50|2.36886|2.38664|479.482|
|60|2.38251|2.42611|480.173|
|70|2.40995|2.42500|480.024|

This table summarizes rounded owner-returned values; original full precision
remains in retained native tables. Ranges are descriptive, not pooled estimates.
Near-readout diagnostic gain increases4.899% from5 to70s; S/t increases1.139%
from2 to70s. The data show signal dependence, not its unique cause or a validated
fit interval. Response/timing/illumination contributions remain to be separated.
Do not accept one averaged instrument gain or choose fit/uncertainty policies from
arithmetic_available alone. No uncertainty/significance estimate is assigned here.

## Closed admission defects and retention

#231 EXTNAME alias repair: actual Mac512092fa passed2/2 in5.56s at
mac-extname-binding-it2gdv4q with all guards true; real flat/bias binding succeeds.
#232 legacy BPM counts: actual helper7/7 in0.382s, retained
/Users/fselman/Pictures/OCAM/wenu-imaging/legacy-bpm-structure-b1h9egzp.
All64 missing structural cards were added across32 detectors; existing cards,
stored pixels/padding and source preservation pass. No mask values recalculated.
Original SHA256:d7aeb7d6041fd2e03d48785298b338ba61860e145a08a4aeb29e0fc9b5a13532.
Copy SHA256:a22a6b8f478feb43f541f972a1567de962652c916d823eef68be1354e472de7a.
Keep that derivative while referenced by this and future runs; original BPM stays
unchanged. Both issues are closed for their bounded target-qualified corrections.

Keep failed ccd65-raw-pairs-p0sxrc40 and ccd65-raw-pairs-extname-w5wjs5pr,
successful run, review, compatibility copy and qualified builds until the agreed
branch-closeout retention review. No automatic deletion. PR227 remains draft;
no merge, installation, activation or other-detector measurement has occurred.

Next: discuss extending raw measurements to remaining detectors and interpreting
the gain trend before scientific fitting decisions. A future batch must fingerprint
the common raw set once rather than32 full repeated passes and run detectors serially.
This documentation receipt requires no source sync, native rebuild or test replay
on either user host. Main remains clean c73d9a9e.
