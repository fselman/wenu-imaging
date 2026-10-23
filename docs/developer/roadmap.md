# wenu-imaging roadmap

## Controlling sequence clarification, 23 October 2026

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
