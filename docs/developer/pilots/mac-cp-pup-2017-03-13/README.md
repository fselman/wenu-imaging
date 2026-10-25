# Intel Mac CP Pup functional pilot — 24–25 October 2026

## Acceptance boundary

Fernando reported passing isolated installed-library/native checks for selected
paths corresponding to notebooks 03–09 on MC02VV0HPHTDG: one 20 s OmegaCAM
exposure of CP Pup in r_SDSS, with 32 detectors. These were staged runners
calling production routines, not execution/acceptance of the entire notebook
orchestration. Terminal reports and their on-Mac JSON records are the evidence;
the agent did not access the Mac filesystem directly.

Scientific tuning, independent accuracy, flux/error consistency, full-dataset
processing and Phase 3 compliance are not accepted by these checks.
No additional processing is authorized by this record.

Mac project root: /Users/fselman/Developer/wenu-imaging.
Evidence root below: /Users/fselman/Pictures/OCAM.
Source used for the later checks: fe64df6b1b21c62acc7c47c201df61dfc6ace536
(branch fix/import-banner, stacked on docs/test-explanations).
Earlier stages used the preceding installed code; the verified wheel difference
for the banner installation was only pycavi/pycavi/__init__.py.
The historical chapman3 functional fixes were merged into main at
0591ba0ea8fe93ff727bf06c275d0d9a1416c8d7; PRs #57/#60 remain separate delivery
work. This document does not merge them or synchronize a user's checkout.

## Environment and installed tools

macOS 13.7.8 (22H730), x86_64; Python 3.11.14 in
/Users/fselman/anaconda3/envs/wenu-imaging. The shell's base environment is
distinct and has the unresolved Conda/libarchive problem (#53).

| Engine | Version / selected executable |
|---|---|
| mefpp | 2.0.0 banner; /Users/fselman/opt/local/mefpp/bin/mefpp |
| Astrometry.net | 0.95; /usr/local/Cellar/astrometry-net/0.95_2/bin/solve-field |
| SExtractor | 2.28.0; /opt/local/bin/source-extractor |
| SWarp | 2.38.0; /opt/local/bin/swarp |
| SCAMP | 2.10.0; /Users/fselman/wenu-mac-scamp-build-offrbigl/install/bin/scamp |

The plotting-enabled SCAMP is a separate build, preserving the older engine.
Binary SHA256: e3b7b3312f08308003c9f4ddb7ec31d03ab7d00aa662ff7073d12cb1382eccaf.
Its offline synthetic FILE-reference fit/PDF test passed; the actual CP Pup
32-detector run produced eight complete PDF files and finite WCS/XML.
Fernando opened all eight; sparse internal diagnostic plots were reported for
the single-exposure fixture with photometric solving disabled (#56 closed).
The selected path is saved with configuration backups; no global engine
replacement is claimed. Astrometric SCAMP references were Gaia DR2; notebook 07
photometric calibration used Gaia DR3/GSPC. These are different stages.

Banner wheel records: /Users/fselman/wenu-mac-import-banner-q6816p2o.
Wheel SHA256: 8b679e7d693e4dba9607eb24ab730f3cadb292705f7fee5eaa65e71fb9379779.
Installed banner, ten package/resource checks, pip check and preserved
configuration/dependency checks passed (#59 closed). PR #60 is unmerged.
Native offline compression/SExtractor/SWarp/SCAMP records:
/Users/fselman/wenu-mac-native.i8htSO5f/checks.
Batch work used niceness 10 and bounded threads; interactive notebook priority
is a separate convention.

## Stage evidence and exercised production paths

Paths in this table are relative to the evidence root above.

| Stage | Production path / checks | Record directory |
|---|---|---|
| 03 reduction | mefpp_reduce_science -> native mefpp; 32 finite nonempty detector images; immutable inputs | mac-notebook03-one-8nmbomu1 |
| 03 normalization | mefpp_normalize_science; 32 detectors, normalization/layout/unit metadata | mac-notebook03-normalize-0ydag_rc |
| 04 astrometry | run_solve_field/solve-field and MEF assembly; 32 solved detectors, finite sampled WCS, unchanged pixels/inputs | mac-notebook04-one-554utah6 |
| 05 extraction | installed SExtractor wrapper; 32 nonempty detector catalogues, required columns | mac-notebook05-one-bu3g2zft |
| 05 SCAMP | prepare_to_scamp, run_scamp_on_target -> plotting-enabled SCAMP; 32 finite WCS, XML, eight PDF frames, preserved data | mac-notebook05-scamp-plots-n5j2o8li |
| 06 mosaic | installed SWarp wrapper and coadd_observation_metadata; all science/weight pixels, sampled matching WCS and timing | mac-notebook06-one-4sv9jy4y |
| 07 calibration | ZPCalibration, photometry, Gaia DR3/GSPC, update_frame; full pixel scaling, sampled WCS/timing, saturation units and exact IDs | mac-notebook07-one-b72vmpsf |
| 07 recalibrations | two fresh-copy cached-reference recalibrations; incremental/cumulative scaling and identities | mac-notebook07-recal-k32wgc3w; mac-notebook07-recal-puomw2t4 |
| 07b QC | extract_calibration, plot_zpcal, filter_data, DS9 regions, illumination export/readback, plot_residuals | mac-notebook07b-qc-qabimqpi |
| 08a | fit_chebyshev, model export/parse/evaluate, direct display versus NumPy, four decoded QC PNGs | mac-notebook08a-chebyshev-w6d3k3cf |
| 08b | kriging_interpolation -> UniversalKriging.execute; finite grid/predictions, save_kriging_model, exact FITS grid readback, decoded variogram PNG | mac-notebook08b-kriging-Fx2ur3FY |
| 08c | get_kriging_interpolation; nodes/corners, independent bilinear values, strict bounds; three production QC plotting routines | mac-notebook08c-readback-3xi4tdqy |
| 09 baseline | prepare_to_sextract, run_sextractor_on_target, load_catalogue, clean_merged_catalogue, read_gaia_csv, crossmatch_catalogues; integer/mask FITS roundtrip | mac-notebook09-catalogue-xBdb5Ux1 |
| 09 corrections | apply_chebyshev_illumination_correction and apply_kriggin_illumination_correction on independent baseline copies | mac-notebook09-corrections-vcw8kp8j |
| 09 QC | create_catalogue_checkplots; four decoded PNGs each for baseline/Chebyshev/Kriging; original and staged catalogues unchanged | mac-notebook09-qc-ht7yqf8_ |

Records for later stages are output-check.json in these directories. Early-stage
logs and verification filenames should be read as actually retained, not inferred
from this table. Normalization, single-exposure mosaic and first-calibration
shapes are not evidence for multi-exposure combination or a physical gain/noise
model. The coadd is 18063 x 18013 pixels with 266669512 positive-weight pixels;
EXPTIME=TEXPTIME=20 s, NCOMBINE=1, and BUNIT=e-/s before calibration.
First calibration conversion factor: 1.9447865825448812e-19; 4340 clean and
30073 raw reference rows. Maximum relative pixel-scaling error:
8.381592349260462e-08.

## Recalibration requirement and bounded diagnosis (#61)

There is no externally prescribed target zero point. The first run determines
the solution; unchanged parameters and stars should reproduce that solution.
Two actual recalibrations used cached Gaia without a new query. The same 4340
catalogue IDs, 2036 initial eligible stars and 1980 reconstructed clipping IDs
were retained. Equivalent first-unit solutions differed from the first by
+9.341687956521127e-7 and -5.175322463912835e-7 mag.

Both incremental factors were 1.0001656837194004. Full-precision Flambda zero
point -21.373820126087985 versus stored MAGZP=-21.374 accounts for the repeated
factor. Two recalibrations accumulated -0.00035974782402821 mag. Pixel and
cumulative-factor bookkeeping passed; #61 closed as a completed investigation,
not a code correction or proof of arbitrary-repeat convergence. No forced-unity
factor or recalibration algorithm change was made.

## Saved illumination models

08a used degree (5,5), 36 coefficients/rank 36 and 1747 selected stars, equal
fitting uncertainties. Serialized predictions were exact in the check; direct
display agreed with NumPy to roundoff. Same-star residuals are diagnostic only.

08b used 1990 stars, no random subset, Gaussian/lmfit, maxlag=10000, nlags=200,
init_kriging=False, empirical variogram enabled, free nugget, 50x50 grid.
Magnitude 1..20 and residual +/-1 cuts retain the notebook's cleared clipping
mask. Four-pixel-offset residuals are not independent validation.
Fitted partial sill=0.0010402053707078787, range=-4166.925618392362,
nugget=0.014448578068720224. Finite numerical execution is distinct from
parameter-domain acceptance. Negative range remains evidence for open #62;
the Gaussian expression squares the range, and the saved model was not altered.
08c node and independent bilinear discrepancies were both zero and all four
outside-extent directions were rejected. Linear saved-grid reading is distinct
from the cubic catalogue application and the continuous Kriging predictor.

Fernando's historical feedback to Lientur confirms Gaussian and suggests
trying fixed nugget around 0.015. It is preserved in #62 as historical candidate
information, not a proved optimum or a new default. Investigation follows the
reduction of all fields. Historical notebooks mention better recovery of
NB_659 quadrant structure; CP Pup model references are a clue, not unique
identification of the run behind the prose. This Mac pilot tests r_SDSS only.

## Catalogue acceptance

The baseline has 47543 detections/rows, image-anchored against 30073 Gaia rows.
14654 rows have exact Gaia IDs; 14652 distinct IDs occur, reflecting the existing
nearest-neighbour matching behavior, not a one-to-one uniqueness policy.
32889 Gaia IDs are missing/masked. No matching-policy change was made.

Both correction outputs preserve all rows, IDs/masks, unrelated column bytes
and full FITS extension header metadata. Only mag_auto_r_sdss, mag_best_r_sdss,
mag_iso_r_sdss and mag_petro_r_sdss change. Model hash provenance and byte-identical
second calls passed. Independent NumPy Chebyshev checks differed by at most
1.9073486328125e-6 mag within the tested 2e-6 tolerance; direct cubic SciPy
predictions matched exactly. Corrections are magnitude-only; flux/error
consistency is outside this acceptance.

Twelve catalogue QC PNGs were generated and decoded with mag_petro_r_sdss
versus r_SDSS_gaia at reference magnitude 13..17. The agent did not claim visual
review of these twelve PNGs. Agg/plt.show warnings did not prevent file creation.

## Immutable product identities

SHA256 values, with paths relative to the evidence root:

| Product | Relative path | SHA256 |
|---|---|---|
| Uncalibrated coadd | mac-notebook06-one-4sv9jy4y/CP_Pup_r_SDSS.coadd.fits | 6c2ac935efd77be7114dccf7310dd7d442354fa8c30fb29e24273a11b7b60ae2 |
| First calibrated image | mac-notebook07-one-b72vmpsf/Calibration_dir/CP_Pup_r_SDSS.coadd.fits | 9519a4cbe83d55afdd0fe1b49ebcc693e01d7c0208009f28f89fb80dc0f5db03 |
| Raw Gaia cache | mac-notebook07-one-b72vmpsf/Calibration_dir/gaia3_qry_CP_Pup_raw.csv | 22db7495d6fbe53d182dbaf633002a78dae693524777b87a000e2d62160dd9c7 |
| Illumination table | mac-notebook07b-qc-qabimqpi/CP_Pup_r_SDSS.coadd.illum.csv | a6285acfa3ab2a3ce0d34b13f6ca1e97e80e584367e3702448bcb5442ce1ba05 |
| Chebyshev model | mac-notebook08a-chebyshev-w6d3k3cf/CP_Pup_r_SDSS.coadd_cheb_5_5_direct_fit_01.chebyshev | e740c139a920dbe37dc14d10410d6f0e707a9a0c6bc7102304b286e633ffd32f |
| Kriging model | mac-notebook08b-kriging-Fx2ur3FY/CP_Pup_r_SDSS.coadd_krige_gaussian_nugget_fit_01.kriging.fits | 9e5ce304b5c0df53b4ece2ca5583cbeccd93e3322c557098c31c40732a8d93aa |
| Baseline catalogue | mac-notebook09-catalogue-xBdb5Ux1/CP_Pup_merged_catalogue.fits | 361b10afb6ccd4f4be7dc7151f685ac21a94d20010f67ad344cf7c6abb263cd3 |
| Chebyshev catalogue | mac-notebook09-corrections-vcw8kp8j/CP_Pup_merged_catalogue_chebyshev.fits | f4942f42e68c645aa44b79119c9c8e980b1feb755f305c13b891f1fa6fe37d06 |
| Kriging catalogue | mac-notebook09-corrections-vcw8kp8j/CP_Pup_merged_catalogue_kriging.fits | 2684ceec05297d3e9c5bb5d7e2ab25f617397716162897e7eae448219277d18a |

## Roadmap handoff

1. Review/integrate the documentation and already qualified small changes only
   when merge/cleanup is instructed; no reinstall follows a docs-only update.
2. Select the next bounded software task under the agreed sequence: thin
   notebooks, derive configuration-driven scripts from shared routines, audit
   used Python libraries, then mefpp; full Python future-proofing remains later.
   Functional pilot success does not itself authorize that implementation.
3. Multi-exposure coaddition and broader target/filter coverage remain acceptance
   gaps on the Mac. Inventory the intended datasets and agree a bounded next run
   before launching it; no automatic full-data rerun.
4. Scientific model/parameter comparisons wait until all fields are reduced,
   as Fernando requested. Preserve #62 historical/current evidence, #58 future
   atmospheric/instrument decomposition, and other deferred issues.
5. Independent scientific validation, WFI, Apple Silicon/Ubuntu, complete notebook
   orchestration (#37/#38), QC guard #51, native failure/metadata work and Phase 3
   delivery remain separate gates. Neither raw NB_659 data discovered on the Mac
   nor the chapman3 two-filter pilot closes these Mac-specific gaps.
