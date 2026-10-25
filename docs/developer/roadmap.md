# wenu-imaging roadmap

Native roadmap revision 1.2, 25 October 2026: retain C89/C90 as the portable C
source baseline and explicitly qualify compilation and behavior in C17 mode.
C17 is a compatibility target, not a new source-feature baseline. Inventory
legacy/dependency extensions and isolate platform APIs; do not claim existing
strict compliance. Newer facilities need a reviewed exception. C23 checks are
optional. Mac compiler support is distinct from unperformed mefpp tests;
chapman3's inventoried GCC 4.8.5/Clang 3.4.2 cannot provide the C17 lane. Qualify
an isolated compatible compiler without implicitly replacing system tools or
upgrading glibc. This clarification authorizes documentation, not installation.

Roadmap v1 revision 1.1, 25 October 2026: extend data review to JWST, Roman,
Rubin, ELT and publicly documented future ESO archive plans, distinguishing
adopted standards from proposals/unknowns. Native Apple Silicon arm64 build/install
and functional acceptance is required; Rosetta is not acceptance. Extend the
parallel design assessment to optional threads within detectors and optional GPU
backends only after profiling/equivalence evidence, retaining a portable ANSI-C
CPU baseline, global resource limits and shared mosaic normalization. This is
planning authorization, not permission to add threading/GPU dependencies or run
new workloads. No accelerator backend or hardware purchase is selected.

Data-representation review added to native roadmap v1, 25 October 2026: insert
stage 2A immediately after memory qualification and before component contracts.
Review current accepted formats/metadata models and in-memory structures,
including FITS, HDF5, ASDF and Zarr, without preselecting a replacement. Preserve
FITS ingestion/interchange and originals; compare actual performance/fidelity
and ANSI-C/platform/dependency costs. Any new backend needs a separate reviewed
migration and renewed memory checks. See the version-1 native roadmap.

## Native modernization roadmap version 1 — 25 October 2026

The first [native roadmap](mefpp-modernization-roadmap-v1.md) records Fernando's
revised priorities, completion gates, proposed tools, component/calibration
contracts, platform requirements and revision procedure. Its companion
[current architecture](mefpp-current-architecture.md) describes observed mefpp
structure separately from the target design. These are review documents; no
implementation or target install is authorized by their publication.

Planning order: reproducible serial build/install (Mac, then chapman3), memory
correctness, components/new calibration services, single-detector CCD support,
parallel mosaics, native Windows qualification and CMOS services last. Windows
portability begins with the build design. Preserve common mosaic normalization;
include shutter/gain/RON characterization, measured/default science metadata
and fringe construction with separate Python subtraction. Earlier stages below
remain the wider project context; the dated native sequence controls this newly
prioritized work and does not close Python, science or Phase 3 gates.

## Architecture audit and full roadmap before native modification, 25 October 2026

Fernando explicitly requires the [native architecture audit](native-architecture-audit-2026-10-25.md)
before a full roadmap, and that roadmap before implementation. This supersedes
starting the qfits move/build fixes immediately after the installation audit.
#73 tracks the architecture/modern-practice assessment and Eclipse usage map.
The audit includes 99 compile-only analysis units and static symbol/call
evidence: Eclipse 79 built units, 33 potential-call units and 53 conservative
object-closure units; qfits 18/12/14. These are agent Linux analysis results,
not target linking/runtime coverage or authorization to delete code.

The requested future component candidates are bias, BPM, non-linearity
determination and application, dome flat, sky flat, master flat and science
processing, with shared detector/image/FITS/configuration/QC/provenance services.
Existing functions provide partial foundations; non-linearity routines exist
in Eclipse but are not reached by the current mefpp workflow.
The next deliverable after audit review is the full roadmap: explicit component
contracts and dependency decisions, build/install options, behavior-preservation
tests and Mac-first/chapman3 acceptance. No framework/language rewrite, API,
scientific dependency order or component implementation is selected yet.

Keep #64/#65–#71 installation work and new #74–#76 source findings recorded,
but make no native source/layout/build/installed-selection changes until the
roadmap is reviewed and agreed. The earlier installation-first sequence below
remains the background objective, subject to this new review gate.

## Approved reordering: mefpp/qfits installation audit first, 25 October 2026

Fernando explicitly brings point 5 forward now: audit mefpp and qfits build/
installation, establish a reproducible Intel Mac build/install first, then
chapman3, and move qfits under mefpp. The first deliverable is the
[native installation audit](native-installation-audit-2026-10-25.md), tracking
[#64](https://github.com/fselman/wenu-imaging/issues/64) and findings #65–#71.
The report records source inspection and disposable agent-host probes, not a
successful target build. No source layout/algorithm or working installation
was changed by this audit.

Current sequence: read-only Mac compiler/install inventory -> bounded bundled
qfits/build/install correction -> isolated Mac build/install/smoke acceptance ->
chapman3 inventory and corresponding acceptance -> resume the remaining
thin-notebook/config-script/Python-audit stages. This overrides earlier
instructions to defer all native work until after those stages only for the
bounded installation task; the full numerical/detector/scientific mefpp audit
does not automatically begin. Preserve the working engines, source history,
licenses, configs, static masks and all accepted reduction data.
Recommended destination is mefpp2/qfits5 with one canonical qfits source copy
and explicit qfits -> Eclipse -> mefpp build dependencies. A bare directory move
is insufficient; prefix/staging, failure propagation, compiler selection,
resources, clean rebuilds and real checks must be qualified.

No compiler/library upgrades, runtime parallelization or scientific tuning is
included. Target changes are isolated until accepted and explicitly selected.
The prior thin-notebook-first handoff below is historical where it conflicts
with this user-approved reordering. PRs #57/#60/#63 are merged and cleaned;
Mac main was verified at 2cd54c1206ccb7b68b2eb0a5f70d9b28f1188cde.

## Intel Mac selected functional paths 03–09 accepted, 25 October 2026

The [CP Pup Mac pilot](pilots/mac-cp-pup-2017-03-13/README.md) records installed
functional checks for one 20 s r_SDSS exposure and 32 detectors, through native
reduction/normalization, solves, SCAMP (eight PDFs), single-exposure SWarp,
DR3/GSPC calibration, 07b, both model fits/readback, catalogue applications and
twelve decoded catalogue QC PNGs. Baseline: 47543 rows, 14654 exact Gaia
associations / 14652 distinct IDs, with 32889 missing masks. Both correction
writers preserve masks/unrelated data and have byte-identical repeat calls.
Source/settings, product hashes, record paths and per-stage limits are linked.

This accepts selected installed-library paths, not full notebook orchestration
or all Mac/platform/science gates. #56/#59 are target-qualified and closed;
#61 is a closed investigation of first-solution repeatability/rounding, not a
new correction or arbitrary-repeat convergence claim. #62 remains open with
the current negative Gaussian RANGE and historical fixed-nugget ~0.015 feedback.
Scientific tuning waits until all fields are reduced; no new defaults or
model ranking are accepted. SCAMP's DR2 astrometric reference is distinct from
the DR3/GSPC photometric calibration.

Next: record/review/integrate qualified changes when instructed, then agree the
next bounded software task under the existing thin-notebook -> shared-library
scripts -> Python-library audit -> mefpp sequence. Multi-exposure/multi-filter
Mac acceptance remains pending; inventory and agree any next dataset run before
launching it. No refactor, processing, upgrade, merge or cleanup is authorized
by the documentation update. Independent accuracy, flux/error consistency,
#37/#38/#51, native gaps, WFI, other platforms and Phase 3 remain separate.
The dated 24 October sections below are historical: PRs #43/#45/#47/#50/#52
were merged and cleaned on main0591ba0; PRs #57/#60 remain separate review work.

## Authorized merge/cleanup handoff, 24 October 2026

Fernando authorized integrating the five qualified PRs into main in order:
#43 reader/08c bindings, #45 Gaia identity recovery, #47 crossmatch integer IDs,
#50 FITS null-preserving illumination writes and #52 cubic Kriging application.
The last head carries all acceptance/QC evidence. Verify final main tree/ancestry,
then delete only those merged branches and synchronize the inspected chapman3
checkout. The existing installed wheel already matches the qualified code; no
reinstall or data processing is needed. This is integration/cleanup authorization,
not scientific/model acceptance, full orchestration, Mac or Phase 3 qualification.
Deferred #51 and broader open investigations remain open; older handoffs below
are historical.

## Selected OmegaCAM functional paths through notebook 09 passed, 24 October 2026

Kriging application and its four existing QC PNGs passed, completing baseline/
Chebyshev/Kriging functional catalogue checks for this isolated pilot. Twelve
QC PNGs across the three catalogues were generated and decoded; all original
and staged catalogue hashes remain unchanged. #48 is closed; code remains
298d2867c21fa2734874e1562ff28696147f7d06. No new query/refit/image correction
or independent scientific/model acceptance occurred. Evidence:
notebook09-kriging-qc-saittxaz/output-check.json and the application records below.
PRs #43/#45/#47/#50/#52 are qualified, unmerged and available for review; no merge
or cleanup has been authorized for these branches. Mac testing, independent
accuracy/uncertainty, SkyMapper comparison review, complete notebook orchestration
(#37/#38), native metadata and Phase 3 work remain separate. #51 is a deferred
nonblocking guard finding. Earlier plans below are historical.

## Kriging application accepted; catalogue QC next, 24 October 2026

#48 is closed after installed and actual-model application acceptance. Fresh
notebook09-kriging-s0e1demx retains 16459 rows, 3718 exact IDs/12741 null masks,
all unrelated columns/metadata and repeat-call byte identity. Direct cubic
predictions and inherited default solver bounds pass for both unchanged 50x50
grids; baseline/Chebyshev/models are unchanged. Finish existing QC plots on a
fresh staged Kriging catalogue with unchanged r_SDSS/Gaia settings. This is
functional verification, not independent scientific or continuous-predictor
validation. #51 is deferred. PRs #43/#45/#47/#50/#52 remain unmerged; earlier
plans below are historical.

## Current Kriging catalogue application coordinate fix, 24 October 2026

Chebyshev application and all eight before/after QC PNGs passed; inputs remain
unchanged in notebook09-qc-h6o98cy8. Address confirmed #48 as the next focused
functional correction: use the stored physical 1..ORIG_W/H sample axes in the
Kriging catalogue application with correct (y,x) orientation and actual grid
shape. Retain cubic interpolation, its default solver, strict bounds, sign,
models, null-preserving writer and repeat/provenance guards. Do not substitute
the linear 08c reader or refit. Source/installed tests precede fresh target
catalogue application. #51 is deferred because current QC inputs are valid.

## Chebyshev application accepted; catalogue QC next, 24 October 2026

#49 passed installed and actual fresh-catalogue verification and is closed.
notebook09-chebyshev-6xb3rgu1 retains all 16459 rows, 3718 exact Gaia IDs and
12741 missing-ID masks; only the four expected magnitude columns per filter
changed. All unrelated column bytes/masks, complete extension metadata, model
provenance and repeat-call byte identity passed; baseline/models unchanged.
Continue the existing notebook 09 QC plots on separate staged before/after copies
with default r_SDSS/Gaia comparison settings. No new query/refit or scientific
acceptance. #48 Kriging application grid failure remains open. See
[writer acceptance](illumination-null-mask-correction.md). Earlier plans below
are historical; PRs #43/#45/#47/#50 remain unmerged.
Nonblocking QC missing-column guard finding #51 is recorded for later; check
both requested columns in the pilot preflight and retain valid-input behavior.

## Current illumination null-mask correction, 24 October 2026

Before applying models, correct #49: both catalogue correction writers rebuild
the FITS table and discard TNULL, exposing unmatched Gaia placeholders as IDs.
Update only magnitude field arrays; preserve integer masks, all unrelated data
and column metadata, existing numerical corrections and repeat/provenance
guards. Test actual writer bodies with real FITS, then installed/observational
copies on chapman3. Do not change the separate Kriging grid failure #48. The
verified baseline and all models remain immutable; no observational correction
has launched.

## Notebook 09 baseline acceptance, 24 October 2026

Installed correction and actual catalogue checks passed; #46 is closed. The two
extractions produced 17682 r_SDSS / 17937 NB_659 rows; existing filter matching
and cleaning retained 16459 paired rows. The baseline contains 3718 distinct
Gaia IDs, preserved exactly as int64/FITS K with correct null masks. All images
and reference CSV hashes are unchanged. Evidence: notebook09-catalogue-95xc1kyz
output-check.json. Continue functional illumination application on fresh copies
with explicitly recorded existing models; no refit, new query or independent
science acceptance. Separate Kriging application edge/grid defect #48 is open
and is not fixed by #41. PRs #43/#45/#47 are unmerged. Earlier plans below are
historical. See [the correction record](catalogue-integer-correction.md).

## Current notebook 09 integer-preservation fix, 24 October 2026

#44 recovery passed. Before catalogue construction, fix #46: crossmatch_catalogues
casts every shorter-table column to float64, rounding large IDs. Preserve integer
dtypes with masks for unmatched rows; retain float NaNs, current row anchoring,
nearest-neighbour selection, radius and all scientific settings. Notebook 09 must
use the exact-ID cache reader. Test actual function/notebook, then installed
Chapman3 and fresh observational output. No extraction or matching launched yet.

## Gaia identity acceptance; resume notebook 09, 24 October 2026

#44 is corrected and target-qualified. Installed source/ID regressions (8+8),
packaging/resource checks (10) and pip check passed. One bounded identity-only
query recovered IDs for both raw 6245-row and clean 981-row files per filter,
with maximum separation 0.0 arcsec in every file. Exact int64 CSV/Table/FITS
round trips, unchanged non-ID fields, clean/raw subset membership and original
hashes passed. Evidence: gaia-id-recovery-jh763zwi/identity-output-check.json.
Resume notebook 09 using the fresh recovered catalogue copies. No recalibration,
refitting or science-image change occurred; notebook 09 remains unqualified.
PRs #43/#45 are unmerged. See [the recovery record](gaia-source-id-correction.md).
The prerequisite plan below is historical.

## Current Gaia identity repair before notebook 09, 24 October 2026

08c corrected readback/plot checks passed both filters; #41/#42 are closed with
evidence, PR #43 remains unmerged. Notebook 09 preflight found #44: all 6245
SOURCE_ID values are missing in each production raw Gaia CSV. The production
method discards its ID fields during column removal/reindexing. Fix response
aliasing and exact integer CSV handling without changing query geometry or
photometric processing. Reject invalid legacy identity caches before reuse.
The inspected run directories contain no retained TAP result/job reference.
Prepare one bounded identity-only DR3/GSPC retrieval and traceable one-to-one
matching to existing cached coordinates; preserve every other CSV field and all
originals in fresh copies. Retain query, native result, job ID, mappings and
hashes; reject missing/ambiguous matches and floating identifiers. No catalogue
construction, recalibration, model refitting or science-data correction until
identities are verified. Keep #44 open pending target qualification.


## Current saved-Kriging readback correction, 24 October 2026

Both filters passed 08b fitting, grid serialization and basic plots in isolated
wrappers. The next 08c/readback check confirmed [#41](https://github.com/fselman/wenu-imaging/issues/41):
stored grid nodes are mapped inconsistently by the linear-interpolation reader.
Correct only the mapping to the actual physical sample axes, preserving saved
models and the linear interpolation method. Also correct the two 08c plotting
argument bindings in [#42](https://github.com/fselman/wenu-imaging/issues/42) using
explicit keywords; no fitting/model/selection policy changes. Test boundaries,
rectangular grids/fields, affine interior values, actual notebook call bindings
and unchanged input files, then verify the existing chapman3 models without
refitting. Keep #41/#42 open pending target verification. Notebook loop scope
#37, experimental state #38 and independent scientific validation remain open.
No correction is applied to science images or catalogues in this step.

The previous merge/preflight handoff below is historical.

## Notebook 08a accepted; merge/cleanup before 08b, 24 October 2026

Both filters passed notebook 07b functional QC and the installed 08a fit/export
checks in isolated wrappers. The saved degree-(5,5) polynomial agrees with
readback to roundoff. The notebook instead displays a second cubic RBF surface;
[#39](https://github.com/fselman/wenu-imaging/issues/39) records discrepancies in
positive-weight samples as well as uncovered corners. Correct only the display
to evaluate that same Chebyshev model directly on its grid, preserving fit,
selection, weights, degree and science data. Use a direct-labelled output name
and retain historical RBF products. Verify non-square/asymmetric grid orientation
and all orders, then regenerate fresh plots from saved models without refitting.
Chapman3 verification passed and #39 is closed. No extrapolation policy, new model,
nonlinearity correction or independent-accuracy claim is included. Notebook
last-filter orchestration #37 and experimental undefined-state #38 remain open.
The earlier notebook 07b resume note below is historical.

Fernando requested merge and cleanup of this completed work before notebook 08b.
The [display correction notes](chebyshev-display-correction.md) record source,
installed-wheel and fresh saved-model plot checks, with no refitting. Kriging
preflight passed against installed PyKrige 1.7.3/lmfit 1.3.4: 583 r_SDSS and 580
NB_659 unique positions, so the existing 2000-point limit needs no random subset.
The retained notebook parameters are Gaussian, maxlag 10000 pixels, 200 lags,
lmfit with unfixed nugget and empirical variogram, 50x50 display grid. The 1--20
mag and +/-1 residual selection explicitly clears the sigma-clipping mask.
The existing four-pixel-offset residual diagnostic is not cross-validation.
No variogram or Kriging fit has been launched. Proceed only after merge/cleanup;
no model selection, fitting-policy changes or dependency upgrades are included.

## Resume at notebook 07b QC

On 23 October 2026 Fernando authorized merging completed branches and cleanup,
then pausing until notebook 07b. Both r_SDSS and NB_659 have verified notebook
07 calibrated outputs; no calibration, normalization, solving or extraction
needs repeating. Seven saturation and ten metadata regressions passed against
source and installed wheel on chapman3, plus ten installed-package tests and
pip check. The [pilot record](pilots/chapman3-cn-ori-2017-03-11/README.md) identifies
products, hashes, query evidence and functional limits. #25/#33 are closed with
correction/verification comments; native #23/#24 remain deferred.

Fernando identified MAGSATL as too faint and requested two investigations:
[#35](https://github.com/fselman/wenu-imaging/issues/35) must relate the peak-pixel
threshold to full integrated PSF flux; [#36](https://github.com/fselman/wenu-imaging/issues/36)
must distinguish the stringent flat-field linearity limit from physical detector
saturation and raw ADC clipping throughout masks, catalogues and coaddition.
His recalled 16-bit boundary is 65535 raw DN, to verify per detector/readout; do
not assume it equals the usable linear/full-well limit. Future nonlinearity
correction must preserve raw clipping flags and respect its calibrated range.
These are future investigations, not new corrections in this walkthrough.
Independent photometric accuracy, Phase 3 acceptance and Mac testing remain open.

The sections below retain chronological task decisions and earlier evidence.

## Notebook 07 saturation-unit defect (#33)

The first r_SDSS ZPCalibration finished and passed finite/scaled-pixel,
WCS/timing/source-preservation checks: 981 catalogue rows, 584 usable
calibrators, DN2FLAM=2.10315823839273e-19. Its SATLEVEL remains in e-/s after
BUNIT changes to physical flux units. Trace confirms that parent metadata
appended after conversion overwrites the saturation value; native SATURATE
also remains unscaled. Correct this unit handoff as a necessary focused fix
within the existing functional walkthrough. Preserve the parent-average and
native saturation definitions, cumulative calibration factors and original
pixels/products. Reuse the completed calibration/query in a fresh header-only
copy; do not recalibrate it. Independent saturation/gain modelling and Phase 3
export redesign (#9) remain deferred. Target verification subsequently passed;
#33 is closed. See the correction notes and current handoff above.


## Current metadata correction, 23 October 2026

Fernando approved the bounded correction in [#25](https://github.com/fselman/wenu-imaging/issues/25):
propagate authoritative science exposure metadata into extracted/assembled
detectors, recompute MJD-END at double precision, and derive coadd timing from
all contributing science exposures. Reuse solved WCS and unchanged pixels in
fresh copies; do not repeat normalization, extraction or all-detector solving.
Keep SWarp equivalent EXPTIME/GAIN and scientific settings intact; TEXPTIME
records the sum of exposure times separately. No native rebuild is included.
The underlying native defects #23/#24 stay open for the later mefpp stage.
The immediate objective remains working chapman3 through all notebooks, then
retesting on Mac; no new photometric functionality or dependency upgrades.

The correction passed synthetic regressions, chapman3 installed-package checks
and real-product preservation/coaddition checks in both filters. Issue #25 is
closed with evidence. All four notebook 06 coadds (BACK_SIZE 128 and 2048,
SUBTRACT_BACK=Y, MEDIAN) passed functional checks. Notebook 07 subsequently
passed in both filters; continue at notebook 07b. The misleading second-pass
filename remains #31; independent scientific accuracy is not established.
Native #23/#24 and later Mac retesting remain pending. See [the correction notes](science-metadata-correction.md).

## Notebook 05 executable detection fix, 23 October 2026

The ongoing functional notebook walkthrough reached SExtractor discovery after
all ten notebook 04 pilot exposures passed solving/MEF assembly checks. On
chapman3, `/usr/bin/sex` returns `SExtractor version 2.19.5`; the installed PAPI
wrapper incorrectly requires the alternative spelling `Source Extractor`.
The first extraction block stopped at discovery, before copying an image or
launching extraction. The focused correction accepts both banner spellings,
preserving candidate order, explicit-path selection and the bytes version return
contract. It changes no extraction parameters, dependency versions or engines.
Chapman3 installed-wheel checks subsequently passed: five banner regressions,
ten packaging checks, pip dependency consistency and actual automatic/explicit
SExtractor discovery. Records: `~/wenu-sextractor-fix.19w6fdss`.

The first real extraction then stopped during config generation because the
legacy PAPI config schema does not include the explicitly requested `NTHREADS`.
Route this option through PAPI's existing `ext_config` native-command mechanism
when supplied to the notebook helper, leaving absent-option defaults unchanged.
Six regressions pass in the agent environment, including config generation,
the native command's `-NTHREADS 1` argument and catalogue renaming with the native
execution mocked. The failed working copy is preserved at
`~/omegacam/testing/wenu-imaging-test/notebook05-r_SDSS-28gx2t5e`;
no native extraction was launched. The thread correction was subsequently installed and verified on chapman3;
all ten pilot exposures passed extraction/SCAMP with checked 32-detector outputs.
The two SExtractor defects are closed with evidence in #26/#27.
Preserve existing solved MEFs and continue with a fresh working copy;
do not repeat normalization or solving. The later efficiency plan is not being
implemented by this compatibility fix.

## Controlling sequence clarification, 23 October 2026

Fernando approved a ticket for each defect and a correction/verification comment
before closure. The [walkthrough defect register](walkthrough-defects-2026-10-23.md)
links the current tickets. The approved immediate metadata correction is #25;
the native timestamp and precision causes (#23, #24) remain deferred to the
mefpp stage. Ticket creation does not expand implementation scope.

Future requirement requested by Fernando: [provisional photometry and explicit
calibration methods](provisional-photometry-plan-2026-10-23.md). Plan Astromatic
photometric processing plus an instrument/filter/focal-plane/detector model for
a labelled provisional flux scale, later refined through an explicitly named
method/release (Gaia DR2, Gaia DR3/GSPC, standard stars or another specified
method). Define model validity, units, cumulative factors, provenance and QC;
reuse canonical measurements and prevent double normalization. This is future
work within the agreed Pycavi/mefpp sequence, not implementation now. Continue
the current functional walkthrough with SCAMP photometry disabled and the
existing Pycavi zpcal path. Implementation details and scientific acceptance
criteria require later agreement.

Notebook 05 target evidence: all ten CN Ori pilot exposures now have checked
SExtractor/SCAMP outputs: 32 detector groups and finite sampled WCS per exposure,
XML reports and eight PDFs with basic complete framing, with inputs unchanged.
Jobs were sequential at niceness 10 with one native thread. Two focused wrapper
fixes are on `fix/sextractor-banner` at `1927166644606567b374a23ff5437b248b9b7029`;
six regressions and ten installed-package checks passed on chapman3. Missing
PLplot 5.10.0 plotting data was extracted locally without modifying system
packages. No independent astrometric accuracy or rendered-PDF assessment is
implied. Continue at notebook 06; do not repeat normalization, solving or source
extraction. The pilot README records the evidence paths.

Source tracing confirms the current SCAMP wrapper uses SOLVE_PHOTOM=N and
photometric calibration belongs to Pycavi notebook 07. SWarp 2.38.0 replaces
zero FLXSCALE with unity and warns; verify that behavior in the actual coadd
without enabling SCAMP photometry or rewriting its headers. Notebook 06 has two
passes (BACK_SIZE 128 and 2048), both SUBTRACT_BACK=Y; the second output's
`coadd_nobacksub` label is inconsistent with its settings. Preserve the effective
settings during characterization and resolve naming/scientific policy later.

Notebook 04 target evidence: all ten CN Ori pilot exposures (five r_SDSS and five
NB_659) passed the installed full runner with one worker at niceness 10: 320
successful detector solves, ten assembled MEFs, exact detector-pixel preservation
and unchanged inputs. Records are in the pilot README. This is functional
evidence, not a real-sky accuracy or multiworker-failure assessment. Notebook 05
follow-up results are recorded above; no repeated normalization/solving.

Fernando requested the [mosaic astrometry efficiency plan](mosaic-astrometry-efficiency-plan-2026-10-23.md):
one canonical SExtractor measurement pass with catalogue reuse; a validated
per-filter focal-plane baseline propagated into mefpp headers; only 1–3 detector
solves for exposure pointing; explicit review of SCAMP mosaic and SWarp grid/
resampling/photometric settings; and a QC script monitoring deviations from that
baseline. Define extraction units across exposures/coadds and validate detector
stability, model freedoms, fallback and scientific equivalence before adoption.
The recalled `FIX_FOCALPLANE` is a SCAMP MOSAIC_TYPE, not a SWarp setting.
This is a planned optimization in the existing Pycavi/mefpp sequence, not a
change to the current walkthrough, running jobs or scientific defaults.

Latest user direction: Fernando declined a separate lunar/site-data check now
and instructed continuing through the whole notebook sequence before deciding
what further work is needed. Resume the existing OmegaCAM functional walkthrough
at notebook 04 (astrometric solving), then SCAMP, SWarp and zpcal. Lunar/site-data
belongs to zpcal and remains deferred until that stage. This revises the earlier
dependency-first stopping rule for this walkthrough; it does not declare the
dependency baseline accepted or start general thinning/refactoring, replacement
or the systematic scientific library/mefpp audits. Use the existing installed
library, isolated pilot outputs, explicit worker limits and batch niceness >=10;
keep the interactive kernel at zero. Inspect existing output locations before
running or assembling anything, preserve prior products, and distinguish
individual-solver checks from notebook orchestration and full MEF validation.

After PR #18 merge and verified chapman3 cleanup at `9ee7ff9`, Fernando approved
the read-only [OmegaCAM requirements map](omegacam-dependency-map-2026-10-23.md).
It connects notebook imports/calls to Python/native/data/service requirements
and existing evidence. It identifies remaining Gaia DR3/GSPC, SkyMapper comparison,
lunar/site-data, SCAMP PDF and platform/provenance checks without executing those
paths or changing software. Further bounded checks need defined acceptance
criteria; the dependency gate remains open and the workflow audit has not started.

Fernando explicitly approved proceeding with Gaia DR3 after clarification that
notebook 07 already selects the Gaia DR3/GSPC library path. The approved bounded
task adds an opt-in dependency probe in `Pycavi2/tools`: one anonymous Astroquery
asynchronous join of the existing DR3 and GSPC tables, at most five sources in
a five-arcminute cone near CN Ori. Require the notebook's SDSS-band column
schema, valid matching source identifiers and nearby coordinates, and at least
one usable r/i photometric row. Preserve query, response, units, null counts and
job details. No photometric fitting, production-query change, catalogue migration,
package installation or scientific workflow audit is authorized by this check.
The five-arcminute probe radius is a diagnostic choice, not a production default.

Reported target result: the bounded Gaia DR3/GSPC probe passed on chapman3 at
`9724dd9` with five joined sources, all five usable in r/i, maximum separation
4.367 arcmin and worker exit zero at niceness 10. Three u-band and four
radial-velocity entries were missing and retained as such. Exact query/response
identities are in the dependency inventory. This completes that retrieval probe,
not photometric calibration, production conversion or the overall dependency
gate; no package, saved setting or scientific workflow change was made.

Following acceptance and merge of the offline SCAMP check, Fernando instructed
the bounded live-reference requirement check to proceed. Compare existing and
advertised VizieR routes with tiny capped Gaia DR2 queries, then test SCAMP's own
retrieval/parser in one small field with fitting disabled. Keep this reusable,
explicitly opt-in and separate from deterministic offline checks. Do not change
saved server/catalogue choices, production wrappers or scientific data. A service
probe does not complete the workflow audit or claim real-sky fit accuracy.

Reported chapman3 result: the native live-reference check passed on 23 October
at niceness 10 with one thread, returning three Gaia DR2 positions within
0.511 arcmin and preserving its input. Native reference-table display-format
warnings are retained in the dependency inventory. This completes the bounded
retrieval check, not the complete dependency gate or workflow audit. No saved
server/catalogue choice was changed; Mac/Ubuntu execution remains untested.

Current bounded dependency check: qualify installed SCAMP using a disposable,
synthetic single-detector FITS_LDAC catalogue and local known reference positions.
Exercise catalogue loading and a linear astrometric fit; require finite output,
recovery of the planted WCS displacement, unchanged input catalogues and recorded
commands/results. Reuse the portable dependency-check tool. Do not change Pycavi
wrappers, science data, reference-catalogue selection or live-service settings.
This follows Fernando's instruction to proceed with the SCAMP requirement check;
it does not begin the workflow audit or qualify real-sky accuracy.

Fernando approved the six delivery/synchronization instruction adaptations from
Wenu on 23 October, after chapman3 synchronized to `340347f` and the merged
feature branch was removed locally and remotely. This bounded documentation
item requires automatic delivery handoffs, fresh target evidence, safe sync and
authorized cleanup, complete guarded command groups, explicit delivery status
and strict roadmap control. It changes no processing code, dependency versions
or stage order. See the canonical agent instructions for the operational rules.

Fernando confirmed that the current phase establishes the packages and external
requirements on chapman3, with documented installation and verification evidence.
Complete the dependency acceptance gate before auditing or refactoring the
Pycavi workflow. Aim for the same Python and scientific-package versions on Mac,
recording necessary platform differences rather than assuming a portable lock.

The agreed five points remain: (1) package/establish Mac and Linux OmegaCAM
execution, (2) retire obsolete reduction scripts and thin notebooks, (3) derive
configuration-driven scripts calling the same library, (4) systematically audit
the Pycavi Python library, and (5) audit mefpp. Future-proofing Python follows
completion of those five points and working software, by a separately agreed
compatibility plan. WFI and the calibration-product QC library remain deferred.

Dependency qualification includes separately approved narrow integration fixes
and local Astrometry.net 0.98 installation. Its single-detector and two
32-detector tests call installed Pycavi `solvefield()` through diagnostic wrappers;
they do not validate full notebook orchestration, multiprocessing, MEF assembly
or astrometric accuracy. No replacement assembly implementation is authorized.
See [chapman3 dependencies](chapman3-dependencies-2026-10-23.md) for inventory,
evidence and remaining gate checks. This clarification controls where older
pending statements or sequencing below differ.

## mefpp detector-identity audit TODO, 22 October 2026

Fernando requests verification that reduction associates detector images by
chip identity (for example EXTNAME), rather than assuming the same ordinal
extension in every MEF. He recalls correcting positional matching; its current
status is unresolved. Trace raw inputs, bias, dome/sky/master flats, BPMs and
output assembly, including extension subsets. Distinguish name lookup from
merely logging names while loading by index. Check the existing source/history
and identify the source of the installed chapman3 binary where possible.
Use synthetic MEFs with deliberately permuted extension order to verify either
correct name matching or an explicit failure before processing; also cover
missing, duplicate and unknown chip names. Record this under the later mefpp
audit; no native implementation change is authorized by this TODO. Matching
order in the ten pilot science exposures is evidence for those inputs only.

Also audit native FITS header assembly: the installed chapman3 MEF BPM lacks
PCOUNT/GCOUNT in all 32 image extensions. Identify the writer/source generation,
check other products, and ensure future output meets the applicable FITS
requirements. Do not rewrite the installed mask as a side effect of preflight.

Fernando approved a focused Pycavi MEF BPM linking/preflight correction on
22 October. Keep mask pixels, native engines and notebook logic unchanged;
verify missing/broken links and invalid layouts using disposable FITS fixtures.

## Limited compatibility review authorized, 22 October 2026

Fernando approved bringing a focused part of the Pycavi library audit forward
before further chapman3 dependency installation. Review actual Python/API needs
against the historical environment and current code, preserving environments,
native engines and science data. See the
[compatibility review](python-compatibility-review-2026-10-22.md) for evidence and
pending checks. This authorizes review and isolated diagnostics, not a dependency
version change or the full scientific audit. The remaining stage order holds.
Restore Jupyter execution on chapman3 with Firefox locally on the Mac through an
SSH tunnel after environment validation; this remains pending.

Follow-up evidence on 22 October: the approved isolated Python 3.11 stack passes
pip check, nine initial installed-package tests, ten numerical/catalogue
regressions and nine runtime imports. A named Jupyter kernel and Mac Firefox
connection to chapman3 are verified. Fernando also explicitly approved the
narrow notebook 03 mefpp-prefix adapter and its path-resolution regression;
the corrected local wheel passes ten installed-package tests. Full reduction,
pilot selection and scientific reference comparisons remain pending. This does
not authorize general notebook thinning or scientific changes ahead of schedule.

## Packaging implementation status, 21 October 2026

Fernando authorized the packaging stage and reiterated that any roadmap deviation
must be discussed and approved **before** proceeding. Work is limited to Python
packaging/setup, resource delivery, dependency declarations and executable
configuration, with current scientific versions retained. See
[installation and evidence](installation.md). Mac/cluster acceptance and exact
reference constraints remain pending; do not mark the stage complete from local
Linux smoke tests. Notebook thinning follows this gate, then configuration-driven
scripts, the **Pycavi Python library audit**, and the mefpp audit. WFI work remains
deferred. No later implementation stage is started by this patch.

## Sequencing update, 21 October 2026

Latest clarification from Fernando supersedes the earlier proposals below:
package/establish OmegaCAM execution on Mac and Linux; retire old reduction
scripts and thin notebooks; derive new configuration-driven scripts from that
workflow; systematically audit the notebook-used Python routines; then audit
mefpp. WFI implementation/validation waits for Mac/Linux operation. Preserve WFI
requirements and source. No library/engine upgrades now. BPM creation belongs
to normal calibration production: trace/validate the existing native construction
path and its Python integration, rather than treating static-mask copying as the
final design. Refactoring checks remain necessary before the full library audit.

Fernando clarified the following order after the installation audit:

1. Properly package wenu-imaging using the existing scientific stack; no library,
   Python or external-engine upgrades yet. Validate ordinary wheel/sdist installs,
   installed resources and setup outside the checkout, plus reproducible
   configuration/environment records.
2. Debug and improve Pycavi, preserving and comparing the OmegaCAM pilot and WFI
   behavior. Fix integration and failure reporting before increasing concurrency.
3. Audit single-chip CCD/CMOS support and every single-node parallelization
   opportunity now; use that audit to define focused Pycavi changes. Distinguish
   single-detector data layout from the actual detector noise/calibration model.
4. Once Pycavi is debugged and improved, continue with mefpp's build, detector and
   parallel-execution work. Evaluate independent-process scheduling and internal
   C parallelism separately. Native mefpp behavior is unchanged in earlier steps.
5. Qualify newer libraries and alternative backends later, by a separate decision.

The concurrency goal covers all suitable independent work, not just solve-field.
Allocation, memory, I/O and scientific dependencies determine what can run at the
same time. No multi-node/MPI requirement is introduced. The immediate scientific
delivery remains the OmegaCAM Phase 3 dataset; release quality and format checks
remain necessary alongside packaging and performance work.

Earlier sections below retain their baseline history. This dated update controls
the current sequencing. Detailed source findings and task opportunities are in
[the detector/concurrency audit](detectors-and-parallel-work-audit-2026-10-21.md).

Status: accepted roadmap direction, amended by Fernando on 20 October 2026.
The immediate science delivery is an OmegaCAM dataset for ESO Phase 3 submission.
Component implementation remains limited to separately authorized stages.

## Platform requirements and current evidence

| Target | Priority | Known environment | Validation status |
|---|---|---|---|
| macOS Intel | Urgent; begin here | macOS 13.7.8 (22H730), x86_64, Python 3.11.7, Apple Clang 15.0.0 | Environment reported; build/install/reduction pending |
| Linux cluster, distribution pending | Urgent; define when access is available | Single-node multiprocessing confirmed; distribution pending | Pending identification and validation |
| macOS Apple Silicon | Required afterward | ARM-native target; OS/Python/compiler versions pending | Untested |
| Ubuntu Linux | Required afterward | Release, architecture and toolchain pending | Full build/install/reduction untested |

Intel Mac compiler details:

- `Apple clang version 15.0.0 (clang-1500.1.0.2.5)`
- Target: `x86_64-apple-darwin22.6.0`
- Xcode developer directory: `/Applications/Xcode.app/Contents/Developer`
- Toolchain: `/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin`

The terminal prompt indicated `(base)`; the exact interpreter path, environment
manager configuration and package set have not been collected. Do not modify
that environment to establish the baseline. A separate test environment/prefix
should be agreed before installation attempts.

Ubuntu GCC 13.3.0 syntax checks performed during the initial audit were limited
to both `sysconf.c` files. They do not establish Ubuntu pipeline support.

## Stage 0 — Working agreement and architecture review (accepted)

Deliverables:

- Canonical `docs/developer/agent-instructions.md`, a root AGENTS.md entry point,
  existing architecture, the historical audit and this roadmap.
- Explicit record of accepted decisions and remaining choices.
- Audited component trees and their original histories imported into the monorepo.

Fernando accepted the documentation and roadmap direction and requested the
files under `docs/developer`. The monorepo direction, single-node cluster
model, serial mefpp baseline and urgent OmegaCAM delivery are recorded decisions.
No source fixes are included in this stage.

Remaining details: installation/resource layout; dependency provisioning;
reference data, product types and numerical tolerances. Historical scripts are
unvalidated unless needed for the selected production path. The name wenu-imaging is established; repository consolidation
changes source organization without changing processing code.

## Stage 1 — Characterize unchanged software on Intel macOS

Use disposable copies and separate environments to:

1. Record tools, interpreter path, dependency versions and external executables.
2. Attempt unchanged qfits build/install, then unchanged mefpp build/install
   against that qfits, collecting diagnostics and effective compiler options.
3. Attempt Python wheel/sdist builds and installation outside the source tree.
4. Check installed notebooks, CFG/PAF, headers/libraries and decompressed BPMs.
5. Characterize executable configuration, startup/imports and stage preconditions.

Gate: reproducible commands and logs identify what succeeds and fails on the
reported Intel Mac. Record failures without silently patching the baseline.
Do not assert compatibility merely because configure recognizes Darwin.

## Stage 2 — Establish scientific reference and failure cases

Select a small representative OmegaCAM subset of the intended production set,
including calibrations, BPMs and trusted outputs or a known working installation.
Record data identities, configuration, executable versions and intermediate
stages. Add WFI regression cases where shared behavior is changed; do not make
new detector capabilities a prerequisite for the urgent OmegaCAM delivery.

Agree on comparisons for extension mapping, masks, pixel values/units,
gain/exposure and FITS scaling, QC/header values, WCS residuals, coadds,
photometric calibration and catalogues. Define tolerances and the treatment of
timestamps/header ordering before judging numerical equivalence.

Characterize fresh execution, reruns, missing calibrations, deliberate process
failure and worker failure. Use synthetic FITS cases for small interfaces where
useful; they supplement real-data references.

Gate: agreed datasets, trusted outputs and acceptance criteria. If unchanged
software cannot run, agree how existing trusted products establish the reference.

## Cluster characterization — urgent when access becomes available

Collect distribution/version, architecture, Python/compiler/library versions,
available external astronomy software, scheduler and an example launch script.
The execution model is already confirmed: multiprocessing within one node.
Identify the scheduler's allocation and permitted process/thread settings.
Record CPU/memory allocations, process/thread counts, temporary storage, shared
filesystem behavior, installation permissions and compute-node network access.

Gate: a documented cluster deployment model and resource limits. Do not assume
that multiprocessing.Pool distributes jobs across nodes. Cluster access being
pending does not block independent Intel Mac analysis.

## Stage 3 — Minimal build and installation corrections

Propose focused fixes only after the preceding review gates. Candidate work from
the first audit includes:

- Separate the mefpp executable path from its configuration/BPM locations.
- Resolve missing license/resource declarations and undeclared Python imports.
- Make external program discovery deterministic and consistently applied.
- Correct demonstrated native compiler/configure/install failures while retaining
  existing build machinery where practical.
- Check `funpack` and all resources; report incomplete installation clearly.

Gate: clean installed workflow outside the checkout on the urgent validated
targets, with dependency versions recorded. Scope and validation must be stated
per patch. Do not add a new installer framework or upgrade all dependencies as
an unrelated part of this work.

## Stage 4 — Reliable pipeline execution within one node

Characterize and minimally fix the supported runners: exit status, verbose output,
argument/path handling, restoration of working directory, worker exceptions and
expected output checks. Respect allocated cluster resources and account for
external-program threads as well as Python workers. Keep temporary/output files
isolated when work runs concurrently.

Keep mefpp serial in this milestone. Exercise existing pipeline multiprocessing
and external tools without adding multiprocessing inside mefpp or concurrent
mefpp jobs as an unreviewed optimization.

Gate: failures are visible, allocated limits are respected, and agreed scientific
outputs remain equivalent under the supported single-node settings. No multi-node
or MPI implementation is included.

## Stage 5 — Operational OmegaCAM reduction and Phase 3 preparation

Inventory the medium-sized production dataset before setting performance or disk
capacity expectations: programme IDs, targets, filters, dates, exposures, total
bytes, calibrations and BPMs. Select a pilot subset, inspect all stages, then
process the full selected set on the validated urgent platform(s).

Acceptance evidence must include:

- Reproducible input/calibration/configuration/software identities and processing
  records, with explicit failed or excluded partitions.
- Scientifically reviewed calibration, masks, astrometry, photometry, coadds and
  other agreed products, with QC results and agreed tolerances.
- An inventory of intended submission products and their associations/provenance.
- Review against the applicable ESO Science Data Products Standard and Phase 3
  validation procedures, recording exact versions and validation reports.
- Release documentation describing processing, coverage, quality and limitations.

The existing code's Phase 3 keyword support is a starting point, not a compliance
claim. Confirm product types, metadata and required companion products from the
applicable official documents rather than guessing a universal checklist.
Scientific correctness and technical format validation are separate checks.

Gate: the medium-sized OmegaCAM set is reduced, reviewed and prepared for Phase 3
submission with documented outstanding issues. ESO acceptance is not claimed in
advance. Upload, submission and publication require Fernando's instruction.

Official references to consult when defining and validating the delivery:

- [ESO Phase 3 overview](https://www.eso.org/sci/observing/phase3/overview.html)
- [ESO Science Data Products Standard](https://www.eso.org/sci/observing/phase3/p3sdpstd.pdf)
- [ESO release description guidance](https://www.eso.org/sci/observing/phase3/release_description.html)

## Stage 6 — Required platform completion

Validate native Apple Silicon and the selected Ubuntu release, documenting any
additional differences. Avoid treating Rosetta execution as ARM-native validation.
Run the agreed scientific checks and publish a compatibility matrix with actual
results and exact system commits and recorded component baselines. These remain requirements but do not delay
the urgent OmegaCAM deliverable solely for platform completeness.

Gate: target-specific installation instructions and passing acceptance evidence;
unsupported configurations explicit. Add CI only where authorized and feasible.
Tagging or publishing a release requires instruction.

## Later development — after wenu-imaging works correctly

These are explicit future requirements and have no implementation authorization:

1. **mefpp multiprocessing.** First establish the correct serial baseline. Then
   profile representative work, propose safe process boundaries, evaluate shared
   state and memory/I/O behavior, and validate serial/parallel equivalence and
   failure behavior. Keep this separate from pipeline-level parallel astrometry.
2. **Single CCD reductions.** Audit single-detector FITS/configuration assumptions
   and appropriate bias/dark/flat, gain, saturation and noise handling with
   Fernando; define detector-specific test data and expected results.
3. **Single CMOS reductions.** Determine readout modes and calibration/noise
   requirements from actual detectors/data. Do not treat single CMOS support as
   already implemented or assume every CCD correction applies unchanged.
4. **Calibration-product QC library (Fernando, 22 October 2026).** Develop a
   library for scientific quality control of calibration products after the
   currently planned wenu-imaging work is finished. Keep this deferred; current
   historical-product comparisons establish reproducibility evidence, not
   independent calibration-quality certification. No implementation is started.

Agree their relative order after the operational OmegaCAM milestone. Preserve
instrument configuration boundaries and existing mosaic support when designing
these capabilities.

## Review and completion rules

Each proposal states affected repositories, exact baseline, finding addressed,
files/interfaces changed, scientific invariants, checks and rollback. Cross-component changes should be reviewed together when they implement one
agreed interface correction. A successful
syntax check, no-op `make check`, or editable install is not a release gate.

This roadmap is intentionally sequential at approval boundaries. Independent
documentation and evidence gathering may proceed together; implementation must
remain within the stage Fernando has approved.
