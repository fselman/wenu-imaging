# Native qualification and roadmap decision — 26 October 2026

Owner: Fernando Selman. Baseline: merged main
2ace67a08f4b5bd916d270b91afa3c6db62f4dff.
Evidence below is Fernando's returned terminal output and supplied transcripts,
not agent access to the actual Mac/Chapman3 JSON files. No new reduction,
installation or normal engine selection occurred in this documentation update.

## Agreed scope and sequencing

Finish the bounded serial qualification, then Stage 2 memory/ownership checks.
After Stage 2, stop for a review with Fernando before Stage 2A representation
prototypes or component extraction. Start an early audit of applicable ESO Phase 3
instructions as requirements work alongside current qualification; use its gap
matrix to inform changes from design onward. The audit and profile implementation
remain pending. ESO_Phase3 is a proposed named reduction/product profile; other
profiles can follow. Keep scientific correctness common to all profiles.

Develop corrections and test drivers on the Mac; verify unchanged deliverables
on Chapman3. Future work directories are ~/Software/build/wenu-imaging/;
permanent Chapman3 CMake/CTest are ~/opt/cmake-3.29.6/bin/.
Do not confuse fselman/wenu with fselman/wenu-imaging.

## Integration and current baseline

PRs #72, #77, #78, #79, #81 and #88 were merged in dependency order.
Main 2ace67a has tree ea2978a41fab5dad91e13f5ea9aadcbde1aad072,
equal to the qualified native-failure-contract head c7907fe tree.
Fernando reported Mac and Chapman3 synchronization to main and deletion of the
six merged branches. Earlier instructions/statuses saying merge/cleanup remain
pending are historical. No reinstall is required for documentation-only changes.

## Bounded gate ledger

| Gate | Actual reported evidence | Remaining limitation |
|---|---|---|
| Mac/Chapman3 C90/C17 build and private installation | Existing native and installation acceptance records; installed failure tests passed | Other platforms and broader memory suite pending |
| Installed Pycavi and direct science | CP Pup on Mac and selected CN Ori NB_659/r_SDSS on Chapman3 passed exact finite 32-detector comparisons | Selected functional paths; not independent scientific/Phase 3 acceptance |
| Chapman3 bias construction | Both language modes exact finite pixels; only reviewed version/generated-name header changes | Representative March 11 fixture, not every calibration |
| Chapman3 dome construction | Both filters/modes exact finite pixels; complete version/generated-name review | r_SDSS uses the recorded 55000 functional dome limit; no new tuning |
| Chapman3 SKYFF/MFF construction | Eight products exact finite pixels across all 32 detectors; reviewed raw header changes only | Existing project-BPM reference reproduction, not independent calibration quality |
| Shared dome/sky normalization | Both platforms, both modes, both detector orders: 2592 pixels per platform exactly match independent expectations | Direct mef_build_cal fixture; not a general covariance/variance or full pipeline test |
| Historical BPM identity | Mac reference and CP Pup project have identical binary masks, detector order/geometry and valid header counts | Downstream exclusion remains unqualified |
| Native BPM construction | Mac C90/C17 robust reconstruction: every mask pixel matches history; C17 also matches C90; only generated ORIGFILE differs | Mac robust mode only; threshold quality, proportional mode and downstream exclusion remain open |
| Downstream mask/weight propagation | Saved Mac settings use NONE; installed SExtractor/SWarp tests retain flagged signals with NONE and exclude them with MAP_WEIGHT; native detector-1 BPM toggles leave science pixels unchanged in C90/C17 | #91 open; cross-stage mapping, adapters and Chapman3 verification pending |
| Proportional BPM cleanup | Source contract mismatch confirmed; separate #90 opened | No returned actual-target sanitizer reproduction or correction acceptance |
| Stage 2 memory/ownership | Some focused cleanup/status repairs passed earlier tests | #75/#90 and broader declared memory suite remain open |

## Exact retained calibration and normalization evidence

Chapman3:
- ~/Software/build/wenu-imaging/chapman3-bias-native-prjulwmp/
  bias-run-record.json, bias-output-comparison.json, bias-header-review.json.
- ~/Software/build/wenu-imaging/chapman3-dome-native-tk9l_c16/
  dome-run-record.json, dome-output-comparison.json.
- ~/Software/build/wenu-imaging/chapman3-sky-mff-native-fotiqam6/
  sky-mff-run-record.json, sky-mff-output-comparison.json.
- ~/Software/build/wenu-imaging/chapman3-shared-normalization-wd701qfx/
  normalization-check.json.

Mac:
- ~/Software/build/wenu-imaging/mac-shared-normalization-hpvn6d8s/
  normalization-check.json and shared-normalization-mac-qualified.tar.gz.
- Transferred archive SHA256:
  16f0bba19bb09e2f3d8e8626b8f4c4d5d51c3b7d2aec9b29e9a84b8e8e2afa7a.
  Chapman3 verified the same archive before building its driver.

Bias/dome/SKYFF version header changes are PROCSOFT and recipe RECVERS
mefpp-2.0.0 to mefpp-2.0.3, plus generated ORIGFILE. Each MFF also updates
MSKY in all 33 HDUs to the corresponding newly generated SKYFF identifier.
No unexplained reported raw header differences remain for these comparisons.
Calibration MJD-END precision remains a known separate issue #24, unchanged by
this reproduction work. Version-label consistency remains separate (#69).

## BPM fixtures, provenance and actual masking gap

Mac data: ~/Pictures/OCAM/bpm/.
The retained bpm.list has 30 inputs: 10 zero-second bias frames and 20
FLAT,DOME,DETGAIN exposures, paired at 2, 5, 7, 10, 20, 30, 40, 50, 60 and
70 seconds. Preserve listed order. Header template is OMEGACAM_img_cal_gain;
do not rename this as a confirmed distinct linearity template.

PAF SHA256: 709d65acdeea6c889ed1468cbb3966d5de93ec654ee030032a096ca12624333f.
Robust BPM mode PROPFLAG=0 and normalized-response thresholds 0.5–1.5
are confirmed in configuration/log/reference headers. Good response is strictly
inside those bounds in the current threshold routine. Preserve these settings
for reproduction; suitability is a separate calibration-quality question.

Historical BPM:
~/Pictures/OCAM/bpm/OCAM_BPM_1x1.fits
SHA256 d7aeb7d6041fd2e03d48785298b338ba61860e145a08a4aeb29e0fc9b5a13532.

CP Pup project BPM:
~/Pictures/OCAM/CPPup-wenu-imaging-test/static_calib/bpm/OCAM_BPM_1x1.fits
SHA256 bcc5e05e63f275b3b0e4d2de0b4b21f315691cca717bdd80fcd010bf5ca324bd.

All 32 arrays match exactly, with 0=bad and 1=good, no other values.
34122 bad pixels comprise 0.012751877420771385 percent of the mosaic; actual
counts match each extension's headers. Full non-pixel differences between these
two files have not been reviewed. A different file hash is not pixel inequality.

Native BPM routines fit pixel signal against frame median to measure relative
response; that slope is not electronic conversion gain in e-/ADU.
Eclipse detector.c also contains separate non-linearity fit/application routines,
but current BPM construction does not invoke those separate services.
The log prints 'bias subtracting BPM cube' even when its bias argument is NULL;
the exact historical command line remains unavailable. A complete log has 32 BPM
stages starting at Part 1, with no bias stage or bias-load evidence. Fernando's
subsequent isolated reconstruction without a separate master bias reproduced
all historical mask pixels in both language modes. This establishes a reproducible
invocation, not recovery of the unavailable original command line.

The inspected native path uses the mask to exclude neighbors while filtering
the sky/dome ratio. Native science subtraction/division does not apply a science
exclusion mask directly. Actual saved CP Pup configurations show:
- SWARP.conf: WEIGHT_TYPE NONE, empty WEIGHT_IMAGE/WEIGHT_THRESH,
  COMBINE_TYPE MEDIAN, RESAMPLING_TYPE LANCZOS3, RESCALE_WEIGHTS Y.
- Ten py-sextractor.sex records: WEIGHT_TYPE NONE; WEIGHT_IMAGE weight.fits
  and FLAG_IMAGE flag.fits are configured names, not evidence of BPM exclusion.
  MASK_TYPE CORRECT is not a substitute for supplying detector exclusions.
- The inventory found one final SWarp output weight file. Its existence alone
  does not establish propagated physical variance or BPM-aware input weighting.

Track the bounded propagation gap in #91 and proportional two-pointer cleanup
defect in #90. Broader BPM generation/integration remains #13. No source
correction, threshold change or sentinel test was performed by those read-only
inventories. The subsequent isolated observational BPM reconstruction is recorded below.

## Next bounded work and review boundary

1. Robust BPM reconstruction on the Mac is accepted as recorded below. Retain
   its inputs, run records and comparisons; do not repeat the expensive builds.
2. Finish the masking audit with a bounded known-flagged-pixel/unflagged-control
   test. Record behavior and requirements; this does not implement all variances.
3. Retain the successful shared-normalization driver as a permanent regression.
4. Keep this ledger current and perform the declared Stage 2 memory suite,
   including #90. Preserve selected installations and original products.
5. Review with Fernando after Stage 2: remaining findings, early ESO Phase 3
   requirements/gaps, product/profile contract, priorities and next authorized scope.

Do not declare full Stage 1, scientific calibration quality, WFI observational,
new platform or Phase 3 acceptance from these bounded results. Do not begin
Stage 2A implementation or component extraction automatically at Stage 2 completion.


## Mac robust BPM reconstruction acceptance

Fernando returned complete C90 and C17 run/comparison output on 26 October 2026.
This is attributed actual-host evidence; the agent has not read the host JSON
files directly. Source checkout was main 7e8b771f196c71283280bb35181515da45670684
(documentation-only successor of 2ace67a); installed native source was
4ade8c52027c736a49b65da3bdb31f11b036693b, separately qualified in both modes.

Work: ~/Software/build/wenu-imaging/mac-bpm-native-4fv4236r/.
Records: bpm-run-record.json, bpm-c90-comparison.json,
bpm-c17-run-record.json and bpm-c17-comparison.json.
Independent staged copies preserved all 30 inputs in their original order and
the original PAF. Both serial commands were mefpp --bpm bpm.list, without a
separate --bias argument; overscan/trim and robust 0.5–1.5 settings were retained.
The ten raw bias frames remained regression inputs. Native mef_build_bpm uses
the Eclipse robust response fit; this does not qualify its proportional branch.

Both runs exited zero and wrote 267822720-byte products. All 32 detector masks
match history exactly, including all 34122 zero-valued bad pixels, binary values,
geometry/order and actual header counts. C17 also matches C90 exactly.
The complete raw-header comparison finds only ORIGFILE in all 33 HDUs:
historical CMDP.OMEGACAM.2024-08-09T10:04:30.087.fits becomes
CMDP.OMEGACAM.2026-10-26T15:40:21.100.fits (C90) or
CMDP.OMEGACAM.2026-10-26T16:42:47.772.fits (C17).
These generated identifiers are reviewed and accepted. Protected files remained
unchanged. No current project mask or selected engine was replaced.

This accepts historical robust-mask reproduction on this Intel Mac. It does not
validate the loose response thresholds, electronic gain/RON, non-linearity,
downstream exclusion, proportional cleanup, memory safety or Phase 3 products.
Issues #13, #90 and #91 remain open.

## Next masking sentinel: test contract, not an executed result

Prepare on the Mac, preserving production code and normal configurations.
Use fresh disposable fixtures and the actual installed routines/tools, recording
their paths, hashes, configuration and commands. First inventory available
SExtractor/SWarp and installed Pycavi wrapper locations; do not install or upgrade.

Use paired identical science fixtures with known flagged and unflagged control
coordinates, deliberately asymmetric positions to detect axis/extension mistakes,
and a baseline without the injected signal. Keep the injected amplitude below
saturation/non-linearity limits and record that choice. For a native probe,
change only a disposable BPM between good/bad states, leaving science, bias and
flat fixed; distinguish the direct science path from BPM-aware flat smoothing.
Then exercise the production extraction/coadd wrapper path with current NONE
weight settings. Report whether sentinel contributions survive, rather than
requiring an exclusion pass from a known unweighted configuration.

A separate explicit diagnostic input mask/weight experiment may demonstrate tool
capability, but must be labeled separately from current pipeline behavior.
Include a zero-weight flagged sentinel, a nonzero-weight control and a clean
reference contribution at the same sky position for coaddition. Check catalogue
detections/flags and output pixels/coverage; quantify interpolation support and
avoid attributing neighboring resampling effects to a coordinate error.
A binary usability weight is not a propagated physical inverse variance.

This bounded characterization records #91 behavior and adapter requirements;
it does not silently enable new weights, alter scientific defaults, implement
variance propagation or close #91. Write/qualify the concrete driver on the Mac
before delivering it unchanged for Chapman3 verification.


## Mac extraction and coaddition masking characterization

Fernando returned actual installed-wrapper test results on 26 October 2026.
These are disposable synthetic fixtures, not a change to the observational
pipeline or evidence of automatic BPM propagation.

SExtractor: ~/Software/build/wenu-imaging/mac-extraction-mask-_sf3gj63/
extraction-mask-check.json. Installed papi_sextractor.SExtractor.run selected
source-extractor. Both NONE cases detected the flagged source and unflagged
control, with identical catalogues despite different input weight maps.
Explicit MAP_WEIGHT with INTERP_TYPE NONE excluded the flagged source while
retaining the control. The synthetic zero-weight region came from a binary
usability mask; no electronic gain or physical variance was estimated.

SWarp: ~/Software/build/wenu-imaging/mac-swarp-mask-nkfoopz_/
swarp-mask-check.json. Installed papi_swarp.SWarp.run invoked
/opt/local/bin/swarp in four serial one-thread cases: NONE/all-good,
NONE/masked, MAP_WEIGHT/masked and clean-reference-only. Median combination
and Lanczos3 resampling were retained; background subtraction was disabled to
isolate masking, and RESCALE_WEIGHTS Y was recorded. Identical-grid two-exposure
fixtures used asymmetric flagged/control positions and a clean contribution.

The two NONE output images and weights matched exactly. At the flagged center,
NONE retained +100 relative to the clean reference; MAP_WEIGHT matched the clean
reference exactly, with positive output weight minimum 0.25679343938827515.
The unflagged control retained +100 with either weighting configuration, with
MAP_WEIGHT output weight minimum 0.5135354399681091. These output weights are
diagnostic tool products, not independently calibrated inverse variances.
Protected files and input fixtures remained unchanged.

This confirms the characterized exclusion gap with NONE and explicit binary
weight capability in each installed tool. It does not establish pixel-scale
single-defect behavior, shifted-grid/interpolation footprints, native science
masking, detector-to-WCS mask transformations, full notebook orchestration,
automatic BPM adapters, physical variance or Chapman3 acceptance.
#91 remains open. Next isolate native science BPM toggling with fixed science,
bias and prebuilt flat inputs; do not rebuild those calibrations or alter the
normal selected mask. Keep the broader cross-stage mapping and Stage 2 gates open.


## Mac workspace cleanup and permanent SCAMP acceptance

Fernando returned verified relocation and selection results on 26 October 2026.
All thirteen home-level wenu-mac-* directories were identified as imaging
development/dependency work. ~/wenu-output and both development checkouts were
preserved. No directories were deleted; no home-level wenu-mac-* items remain.

Current retained locations:
- ~/Software/build/wenu-imaging/mac-native-qualification-u021mf2l/
  contains the unchanged qualified prefix-c90 and prefix-c17 payloads.
- ~/Software/build/wenu-imaging/mac-python-qualification-trbc6ykz/
  contains the isolated corrected Python installation and its evidence.
- ~/Software/build/wenu-imaging/archive/mac-home-runs-zffi3ocd/
  contains ten retired runs and the original relocation journal.
- ~/Software/build/wenu-imaging/mac-relocation-nnbsx1fy/relocation.json
  reports status verified for these three relocations, with contents manifests.
  Original absolute paths in historical records remain unchanged.

SCAMP was rebuilt from existing local 2.10.0 source with the previously recorded
options and a permanent prefix ~/opt/scamp-2.10.0-wenu-imaging/.
Build record: mac-scamp-permanent-t1z9pz70/build-check.json under the imaging root.
Version/default stylesheet/dependencies passed; the old-prefix stylesheet URI
was replaced by the permanent compiled location. The old engine and selection
remained unchanged during build/testing.

The repeated offline 100-source single-detector FILE-reference fit recovered
all compared previous WCS coefficients exactly and generated FGROUPS PDF output
with checked PDF framing. Visual rendering and independent scientific accuracy
were not established. Record:
mac-scamp-permanent-test-2fznyl5p/run-provenance.json under the imaging root.
No observational reduction or live catalogue query ran.

Selection was subsequently changed to
~/opt/scamp-2.10.0-wenu-imaging/bin/scamp, and the old build was archived at
~/Software/build/wenu-imaging/archive/mac-scamp-build-offrbigl/.
All archived files/symlink targets were verified against the pre-move inventory.
Configuration backup and operation provenance:
mac-scamp-selection-bisr1_4f/run-provenance.json under the imaging root.
An already-running notebook may need to reload a cached executable selection.

These are attributed actual-Mac returned results, not direct agent inspection
of the host reports. Build/test/installation provenance was added explicitly as
retrospective where appropriate. Preserve/recover the useful host reports and
manifests under the evidence-before-merge rule; this summary does not certify
that all required reports have been imported or that cleanup gates are complete.
No merge or branch deletion is implied. The native science BPM toggle test
remains pending and must use the relocated native prefixes.


## Mac native direct-science BPM toggle result

Fernando returned four successful native runs from
~/Software/build/wenu-imaging/mac-native-mask-v4bcn1hy/.
Record: native-mask-check.json; root/inputs/masks/runs and each run have
run-provenance.json. Native payload source 4ade8c52027c736a49b65da3bdb31f11b036693b
was verified in both relocated C90/C17 prefixes.

One selected CP Pup raw exposure, its bias and prebuilt master flat were fixed.
The command explicitly selected detector 1 (ESO_CCD_#65) and supplied a BPM.
A disposable mask variant changed two previously good pixels from 1 to 0,
retaining an unflagged control. Count cards were updated and edited FITS
checksums verified. Astropy HIERARCH warnings concerned the long count keyword
names in the copied mask; no original FITS file was edited.

C90 original versus edited mask: zero unequal detector output pixels.
C17 original versus edited mask: zero unequal detector output pixels.
C90 versus C17 original-mask outputs: zero unequal detector output pixels.
All samples were identical across the four runs:
- flagged_a: 168.7005157470703
- flagged_b: 170.7981719970703
- control: 180.66717529296875

This characterizes the missing direct science exclusion for this detector and
fixed-prebuilt-flat path, consistent with the source trace through mef_engine,
pixelmap_loadext, overscan/trim, bias subtraction and flat division.
It does not test the BPM-aware flat-building/smoothing path, every detector,
individual-pixel resampling support or full notebook/mask coordinate propagation.

Together with the separate SExtractor/SWarp sentinels, this establishes the
bounded masking characterization; it does not implement the #91 correction.
Keep #91 open. No science/variance/mask representation choice or changed
production weighting policy follows automatically. Required actual-host JSON
reports must still be collected, reviewed and committed before accepting the
evidence-preservation merge gate; reported terminal summaries are not a claim
that this ingestion has happened. No new reduction is needed to collect them.


## Imported actual-host evidence

Fernando supplied the Mac acceptance bundle; all 32 manifest file entries and
archive SHA256 verified. The exact reports, collection provenance, small SCAMP
synthetic fixtures and plot are now retained in
[the reviewed evidence directory](fixtures/mac-acceptance-2026-10-26/README.md).
The review independently reconciles BPM report hashes/header changes and SCAMP
header coefficients, and records the stale native provenance status_note without
altering the original bytes. These imported files are stronger evidence than the
earlier terminal-only attribution. Host processing was not rerun by the agent.

The supplied Mac report set is preserved, but external large-data/log retention
and permanent normalization-driver coverage remain separate. This import neither
authorizes run-directory deletion nor asserts complete Stage 1/memory/Phase 3
acceptance. Keep PR #93 and the unresolved implementation gates open for review.
