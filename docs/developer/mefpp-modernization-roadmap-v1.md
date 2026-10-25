# mefpp modernization roadmap — version 1

Date: 25 October 2026. Revision: 1.4. Status: first roadmap, amended for review.
Documentation baseline: b2867c1da3ae4567cc7168c2f0ca13021aea2f33.
Owner: Fernando Selman; canonical development repository: fselman/wenu-imaging.

## Purpose and decision status

Make the existing native system reproducibly buildable and installable, establish
memory correctness, review data standards and representation, and only then
reorganize its functionality. Retain ANSI C,
scientific behavior, instrument information and the working installations during
qualification. The target architecture and this roadmap are living documents:
revise them when evidence changes, recording the reason, affected gate and approval.
Publication of version 1 authorizes no implementation, install, merge or rerun.

The [current architecture](mefpp-current-architecture.md) is an observed baseline;
the design below is a proposal. See the [installation audit](native-installation-audit-2026-10-25.md)
and [architecture audit](native-architecture-audit-2026-10-25.md) for evidence.
Tracking parents: #64 (build/install) and #73 (architecture/roadmap).

### Requirements established by Fernando

- Clean build/install on the Intel Mac first, then chapman3, without relying on
  a historically installed mefpp or qfits. Bundle one qfits source copy under mefpp.
- Investigate and correct memory leaks and invalid memory use before component
  extraction. Preserve the current serial algorithm baseline through these phases.
- Components for BPM, linearity/shutter/gain/RON, bias, dark, dome/sky/master flats,
  fringe-frame determination and science preprocessing.
- Stage 4 must create per-pixel frame variances and propagate them through
  calibration and science processing, with explicit units, masks and provenance.
- Preserve common mosaic flat normalization and relative detector response. This
  encodes acquisition information; independent per-detector renormalization is
  not an optimization and is not authorized.
- Support single detectors, followed by safe parallel mosaic reductions within
  one node. Native Windows build/install is a requirement, designed in early.
- CMOS-specific reduction services are the final functional extension, preceded
  by a detector/readout-mode review. Keep scientific parameter tuning deferred.

## Sequence and review gates

| Stage | Deliverable | Completion gate |
|---|---|---|
| 0 | Toolchain/build decision and qualification fixtures | Review the selected tools, platform matrix, invariants and bounded first implementation |
| 1 | Clean serial build and installation | Fresh source and private-prefix installed tests on Mac, then chapman3; no historical native dependency |
| 2 | Memory and failure correctness | No unexplained memory diagnostics or leaks on the declared normal/error/repeat suite; cleanup and status tests pass |
| 2A | Data standards, storage and representation audit | Reviewed format-neutral data contract and retain/adopt decision before component interfaces are fixed |
| 3 | Component contracts and extraction of existing behavior | Serial legacy/component comparisons pass with agreed tolerances; ownership, metadata and normalization preserved |
| 4 | Calibration services and frame variances | Linearity/shutter/gain/RON, dark, fringes and variance creation/propagation have defined products and separately qualified methods |
| 5 | Single-detector CCD service | Primary-image and single-extension layouts, geometry and calibration behavior pass dedicated tests |
| 6 | Parallel mosaic service | Serial/parallel equivalence, resource limits, failure isolation and restart tests pass |
| 6A | Optional accelerator assessment | Profiled CPU/thread/GPU comparison and explicit adopt/defer decision; CPU fallback retained |
| 7 | Native platform completion | Native Apple Silicon and Windows build/install and supported serial/parallel suite on actual targets; remaining Ubuntu qualification recorded |
| 8 | CMOS review and services | Camera/mode-specific acquisition, calibration, timing, masks and uncertainty contracts reviewed and tested |

Windows portability checks begin in stages 0–1; stage 7 is full target acceptance,
not permission to defer all platform design until then. Native Apple Silicon is a required support target, alongside Intel Mac, chapman3,
Windows and Ubuntu; record real target results with pending status until tested.
No dates or throughput promises are assigned before representative measurements.

## Stage 0 — Select tools and freeze the comparison baseline

**Recommendation for review:** CMake for configuration, dependency targets and
installation, with CTest as the test entry point. Use generated Unix Makefiles
initially where the existing make is suitable; Ninja may be selected explicitly
rather than becoming an unnoticed dependency. Use a stable, recorded CMake
version compatible with macOS 13.7.8; do not require the newest release by default.

| Choice | Benefit | Cost / decision |
|---|---|---|
| Repair existing configure/sysconf/Make | Smaller initial build-system change; familiar tools | Must repair probes, tool propagation, dependency graph, staging and Windows assumptions ourselves |
| CMake + CTest (recommended) | Compiler/capability probes, target dependencies, out-of-source builds, install/test integration and Windows generators | New build dependency and migration verification; framework does not fix algorithms or OS-specific code |

Do not maintain two independent canonical build descriptions indefinitely.
Retain the old source snapshot and instructions as comparison evidence while
qualifying the selected replacement. A compatibility configure launcher, if
wanted, must delegate rather than duplicate platform detection logic.

### Language policy: C89/C90 source and C17 compatibility

Retain ANSI C89/C90 as the portable source baseline for code maintained in the
mefpp numerical core. Require explicit C90 and C17 compilation/behavior checks;
C17 is a compatibility target, not permission to introduce C17-only constructs.
This supersedes the conversational recommendation to make C17 the source baseline.
Any newer-language facility requires an explicit reviewed exception or revision.
No language mode change has yet been applied to source/build files.

Use explicit compiler modes (for example -std=c90 and -std=c17 on GCC/Clang),
classify pedantic diagnostics, and inventory existing GNU/vendor extensions.
Do not declare legacy Eclipse/qfits strictly C90-compliant before that audit.
Keep dependency requirements, optional accelerator/OpenMP code and necessary
POSIX/Windows APIs separately documented; isolate exceptions behind interfaces
rather than treating C90 syntax as proof of operating-system portability.
Compiler flags differ on Windows: qualify available conformance diagnostics and
record any inability to enforce a strict C90 mode rather than claiming parity.

Run the same representative numerical, FITS/metadata, failure/cleanup and memory
checks for qualified C90 and C17 builds, with agreed comparison tolerances.
Compilation alone does not establish equivalent behavior. C23 is an optional
forward-compatibility diagnostic lane when available, not a release requirement
or justification for an unapproved compiler upgrade. Revisit the baseline only
when a concrete benefit and complete platform/dependency evidence justify it.

Apple Clang 15 and the reported GNU GCC 13 installations on the Mac support a
C17 language mode; mefpp's own compatibility remains untested. The fresh chapman3
inventory reports CentOS 7 x86_64, glibc 2.17, GCC 4.8.5 and Clang 3.4.2, with no
newer compiler shown by that inventory. Those system compilers cannot serve as
the C17 qualification toolchain. Investigate an isolated compatible toolchain;
do not replace system tools, upgrade glibc or modify the working imaging
environment implicitly. A candidate compiler is not qualified until tested there.

Proposed initial compiler families: Apple Clang on Mac, a verified compatible
modern GCC on chapman3, and MSVC or clang-cl for native Windows. Record compiler,
archiver, linker, SDK/library and build-tool paths/versions per target. C++
implementation, new bindings and unrelated engine upgrades are not prerequisites.

Capture immutable observational and small synthetic fixtures for bias, BPM,
flats and science, including header/unit expectations and detector mapping.
Record source/binary/resource identities. Establish comparison tolerances before
running changed code. The existing Mac one-exposure and chapman3 functional
products are useful evidence, not complete calibration or WFI certification.

## Stage 1 — Build and install the current serial software

1. Move qfits52 to the proposed mefpp2/qfits5 as one canonical source copy,
   retaining history, notices, licenses and public names. Coordinate path/docs
   changes and source identity checks; do not silently replace qfits/Eclipse.
2. Configure from explicit inputs and capability probes: compiler, headers,
   library functions, byte order, type sizes, large-file behavior and required
   OS services. Report unsupported requirements clearly; do not infer capability
   solely from OS strings. Honor selected tools and propagate every failure.
3. Express qfits -> Eclipse -> mefpp dependencies and header/archive relinking.
   Start with static libraries. Separate the required engine/resources from
   optional legacy commands, development libraries and headers.
4. Build outside the source tree, excluding tracked binaries and generated host
   files from compilation decisions. Resolve version provenance without inventing
   an upstream version. No hidden dependency on old include/library prefixes.
5. Provide explicit prefix and staging support, manifest, license installation,
   safe repeat-install behavior and bounded removal. Install PAF templates and
   required BPM resources; identify funpack or avoid runtime decompression by a
   reviewed packaging choice. Never overwrite edited configuration silently.
6. Test installed programs/resources from outside the checkout. Verify missing
   inputs/tools, failed configuration/build/install and native processing report
   failure. Correct status/cleanup defects needed for truthful acceptance without
   broad component extraction (#65–#71, #75–#76 as applicable).

Mac first: fresh source/private prefix; record compiler/SDK/archive/resource
identities, run small native and representative reduction tests through the
installed Pycavi wrapper with explicit paths. Preserve the selected old engine.
Then repeat on chapman3 using its actual allocation/filesystem/toolchain. Add
a native arm64 Apple Silicon build/install lane as soon as a target is available;
verify executable/library architecture, SDK/dependencies and installed runtime,
without an accidental Rosetta/x86_64 dependency. Do not assume all newer Macs or
macOS releases pass because the Intel Mac passed. An
agent-host Linux compile is not acceptance of either machine. Select a candidate
as the normal engine only after its target gate; retain rollback information.
Build graph parallelism and runtime detector parallelism are separate questions.

### Deferred TODO — simple user distribution

Fernando defers the pip-versus-Conda/micromamba selection while the current native
qualification continues. Compare a platform-specific mefpp wheel plus the existing
Pycavi wheel against a Conda native recipe/application environment. Review build
and runtime dependencies, resource layout/relocation, platform/OS/glibc constraints,
fresh-user installation, updates/removal and maintenance cost. Retain CMake/CTest
and the portable C core regardless of the distribution route.

Keep this as a Stage 1 distribution-usability TODO before advertising a simple
public installer; it does not block the current CP Pup native regression or
chapman3 build/install qualification. No recipe implementation, package manager
installation, channel/account registration or publication is selected by this TODO.
The short user guide stays under docs; detailed qualification stays under
docs/developer. Physical document relocation follows a separate link inventory.

## Stage 2 — Memory, ownership and failure correctness

Inventory allocation/ownership across the recipe, mef_bb, Eclipse images/cubes,
qfits caches and memory manager. Resolve double cleanup, invalid accesses,
use-after-free, buffer overflows, nonliteral formats and leaks (#74–#75), including
partial-construction/error exits. Define which scope destroys each object.

Use compiler diagnostics and compatible AddressSanitizer/UndefinedBehaviorSanitizer
builds; qualify LeakSanitizer or an appropriate platform leak tool on the actual
compiler/OS. Verify that instrumentation observes the legacy qfits allocator;
consider a supported diagnostic allocator configuration without changing the
production allocation policy silently. Unsupported tooling is a documented gap,
not a passing check. Do not enable all warnings as errors before classification.

Exercise successful calibrations/science, missing/corrupt inputs, rejected
configuration, allocation/I/O failure where practical, repeated stage calls and
cleanup after partial results. Include small known-invalid fixtures to establish
that the selected diagnostic configuration actually detects errors. Assess
retained cache allocations separately from lost allocations and repeated growth.

Gate: no unexplained findings in the declared suite on supported target tooling,
correct exit status/cleanup and equivalent scientific outputs. This is bounded
memory evidence, not proof of absence of leaks in every possible execution.
Broader refactoring waits for this gate. Re-run relevant checks after extraction.

## Stage 2A — Data standards, storage and representation audit

Fernando adds this review immediately after memory qualification and before
component contracts/extraction. New storage may improve intermediate processing,
but no replacement is selected and FITS is not presumed obsolete. Distinguish:
(1) on-disk containers, (2) astronomical metadata/data models, and (3) in-memory
array/state structures. A different container does not supply the scientific
semantics, remove allocation bugs or automatically make concurrent writes safe.

Keep FITS as the ingestion/interchange baseline and preserve original files.
Evaluate retaining FITS throughout against conversion after ingestion to a
reviewed intermediate representation, with FITS export wherever external tools
or product delivery require it. An in-memory abstraction may be sufficient;
conversion of every image is not a prerequisite. ESO Phase 3 output requirements
must be checked separately, not inferred from an internal format choice.

| Candidate | Reason to investigate | Required caution |
|---|---|---|
| FITS / multi-extension FITS | Current instrument/external-tool interoperability and established baseline | Compare subset access, compression, metadata and memory behavior using actual workloads |
| HDF5 | Hierarchical datasets/metadata, chunked arrays and a native C library | Review C language/toolchain requirements, library dependencies, schema, locking and process/thread access modes |
| ASDF | Astronomy-oriented schema-based hierarchical metadata and arrays; relevant WCS/model serialization | Establish suitable C access or Python-owned boundary, schema/plugin availability and interoperability |
| Zarr v3 | Chunked arrays and sharding with multiple language implementations | Verify actual C feature/codec support, shared-filesystem file counts, write ownership and version compatibility |
| Relevant IVOA models | Metadata semantics, discovery/interoperability and provenance review | Distinguish approved Recommendations from drafts/notes; these are not substitute array containers |

### Observatory and archive practices required in the review

Investigate JWST, Roman, Rubin, ELT and public future ESO archive proposals, not
only generic container specifications. For each record source/date/version,
raw/intermediate/delivered product types, metadata/WCS and uncertainty/mask model,
internal abstraction versus physical serialization, adopted versus proposed
status, access patterns and implications for a portable C core/Python client.

Preliminary official-source pointers, checked 25 October 2026 (not the completed
stage-2A audit):

| System | Current documented direction / question for the audit |
|---|---|
| JWST | Pipeline products are predominantly FITS, with ASDF metadata/WCS and some standalone ASDF reference files; study the data-model abstraction rather than treating this as universal FITS replacement |
| Roman | WFI science products use ASDF; inspect schemas, arrays, WCS, calibration provenance and supported implementations. Roman WFI is distinct from ESO's WFI instrument |
| Rubin | Published DP1 raw/deep-coadd images are FITS; Butler abstracts storage/retrieval. Study image/variance/mask objects, dataset identity and storage adapters; Butler is not a file format |
| ELT | Public ICS Data Acquisition manual ESO-396401 v3 (2024-12-11) describes FITS data products; investigate instrument/product-specific requirements instead of inferring all future ELT formats |
| ESO archive evolution | Review current DIC, Phase 3 product standard and public archive/ELT plans; distinguish binding releases, drafts and research proposals |

ESO's DIC page identifies version 8, released 5 March 2025, as the official
version at the time of this check. Current public Phase 3 guidance describes FITS
products. No adopted archive-wide FITS replacement was established by this initial
search. Recheck during the full audit; if future documents/drafts are unavailable,
record that uncertainty rather than inventing policy or contacting ESO without
Fernando's instruction. A new internal representation must not silently change
the delivery format required by ESO or other consumers.

This is a shortlist, not an exhaustive standards audit or a claim of one accepted
successor to FITS. During the review verify current specification status, adoption,
implementations, maintenance, licenses and versions using primary sources. Include
other credible candidates if the evidence warrants; explicitly distinguish
widespread adoption from formal standardization.

Define the format-neutral logical product first: science arrays, variance or
uncertainty, flagged masks, detector/amplifier geometry and identity, acquisition
and effective gain/RON, units, correction state, time/WCS, calibration links,
shared mosaic normalization, QC, provenance and schema versions. Preserve original
FITS cards (including duplicate/commentary cards where needed) alongside parsed
semantics; a dictionary conversion alone must not silently discard information.
Specify array shape/type/strides/endian conventions, missing values, integer nulls,
ownership/lifetime, read-only views, lazy access and chunk/region access needs.
Core arithmetic should not depend on a particular serialized container or Python
object model. Check any proposed dependency against the ANSI-C core requirement.

Use representative OCAM/WFI calibration stacks and science images on the Mac and
chapman3. Compare end-to-end read/compute/write cost, peak memory, size/compression,
per-detector/region access, worker access patterns, metadata fidelity, recovery
and deployment burden. Include conversion overhead and FITS boundaries needed by
SCAMP/SWarp and other clients. Do not infer speed from format descriptions alone;
introduce only separately agreed disposable prototypes/dependencies for benchmarks.

Deliver a standards/adoption matrix, measured comparisons, migration cost/risks,
recommended internal schema/adapters and a retain-FITS/adopt-alternative decision
record. Gate: Fernando reviews the evidence and logical data contract before
component interfaces are fixed. If a new backend is selected, stage its migration
and round-trip/equivalence qualification separately before dependent extraction.
Re-run memory/ownership checks for new adapters/libraries. Do not bundle a storage
migration into a numerical refactor. Retaining FITS is a valid review outcome.

## Stage 3 — Explicit contracts and existing-function extraction

Prefer one modular ANSI-C library, focused headers and a thin compatible CLI.
Components need not be separate repositories, executables or shared libraries.
Keep Pycavi notebooks and configured Python scripts as clients of the same
processing routines; choose subcommands/direct API/bindings only when needed.

| Proposed service | Existing starting point / qualification need |
|---|---|
| mefpp_cal_bias | mef_build_cal(bb, "bias") |
| mefpp_cal_bpm | mef_build_bpm; integrate actual generation rather than only static-mask copying (#13) |
| mefpp_cal_domeff | mef_build_cal(bb, "dome") |
| mefpp_cal_skyff | mef_build_cal(bb, "sky"); disentangle Python's coupled master-flat request |
| mefpp_cal_masterff | mef_ff_combine and mef_image_filter_flat; explicit input mutation and shared normalization |
| mefpp_sci_pp | Extract current inline science block; retain alias cal_sci_pp only if needed for compatibility |
| mefpp_cal_lin | Stage 4: existing uncalled Eclipse fit/application routines are candidates, not a complete qualified service |
| mefpp_cal_dark | Stage 4: establish current usable behavior and intended method before implementation |
| mefpp_cal_fringe | Stage 4: fringe construction; Python application is a separate service |

Every service contract defines detector/amplifier identity, geometry/readout mode,
input units and correction state, immutable versus owned mutable arrays, output
units/products, masks, uncertainty/QC, calibration applicability and provenance,
status/diagnostics, output naming and interrupted/repeated-run behavior. No public
API should require a caller to mutate the whole historical mef_bb correctly.

Separate shared services for configuration, detector mapping, arrays, FITS I/O,
logging/errors and metadata, using the reviewed stage-2A data contract and storage
adapters. Pass explicit state instead of relying on cwd or
hidden static buffers. Preserve original acquisition metadata while distinguishing
processed quantities. Extract one service at a time with before/after comparisons.
Do not delete Eclipse code based on single-root reachability; optional pruning
requires multi-root/instrument coverage and actual target linker evidence.

### Mandatory mosaic and unit invariants

Common flat normalization preserves relative detector response and acquisition
information. Represent its definition, reference detector/statistics and scale
explicitly; compute required shared quantities before independent application.
Do not substitute independent unit-median flats for the present common reference.
Keep detector identity stable if HDU order changes or a detector is unavailable;
missing reference behavior must be an explicit reviewed policy, not a silent swap.

Python currently performs mean-CONAD/exposure normalization after C preprocessing.
Keep that numerical behavior in comparisons and define its future owner before
moving it. Never apply it twice. Preserve ADU/electron/electron-per-second versus
physical-flux distinctions and define propagated variance/mask semantics.

## Stage 4 — Calibration characterization and missing services

### Frame variance creation and propagation

Create variance planes for science exposures and calibration products, per detector
and per amplifier where relevant. Bind their geometry, masks, units and processing
state to the associated image. Define variance in squared image units; distinguish
it explicitly from standard deviation, inverse variance, exposure/coverage maps
and arbitrary weights. Missing uncertainty is flagged as unknown, never silently
represented by zero variance or infinite statistical weight.

Define the initial noise model using compatible measured gain/readout noise
(or the documented default/fallback policy), appropriate Poisson terms and other
identified noise contributions. Specify bias/background treatment, valid signal
range, saturated/bad pixels and handling of negative background-subtracted values.
Keep this distinct from the paired-flat variance estimator used to characterize
detectors: one global gain or sample variance is not a frame variance plane.

Propagate image and calibration uncertainty through overscan/bias/dark subtraction,
non-linearity and shutter corrections, dome/sky/master-flat construction and
application, shared mosaic normalization, gain/exposure/flux scaling, and fringe
template construction and subsequent Python amplitude fitting/subtraction.
Every component must state its propagation rule, independence/covariance
assumptions, rejected-pixel behavior and uncertainty in fitted parameters or
calibration reference quantities. Include correlations introduced by shared
calibrations and mosaic normalization; do not silently assume all pixels or
detectors are independent. Preserve the common flat reference and relative
detector responses.

Use the stage-2A logical data contract and stage-3 component interfaces to carry
science, variance, masks and provenance together. Define the handoff to Pycavi,
resampling/coaddition and photometry, including correlated-noise limitations and
conversion to tool-specific weight maps. A SWarp weight product alone does not
establish propagated physical variance. Storage layout and any covariance
representation remain reviewed design decisions, not a new selected file format.

Acceptance must include independently calculated small fixtures for noise
initialization, subtraction, multiplicative scaling, flat division, calibration
combination and shared normalization; test units, masks, unknown/invalid values
and uncertainty provenance. Assess resampling correlations and validate the
adopted approximation on representative data, with suitable statistical recovery
tests. Document which uncertainty terms are modeled and which remain unsupported.
This is Stage 4 work; it does not add variance algorithms to the current build
migration or claim that existing frames already have qualified variance products.

### Paired flat sequence: linearity, shutter, gain and readout noise

Fernando specifies OCAM/WFI sequences: at least two initial bias exposures;
randomized integration times from low signal to saturation, always two consecutive
flats per integration time. Preserve chronological order and pair membership;
validate metadata rather than sorting by time and blindly pairing files. Historical
template variants may differ and require explicit association rules.

Produce per-detector (and per amplifier where relevant) signal/time and
variance/signal measurements, conversion gain, readout noise, non-linearity and
shutter-error products, with errors, fitting regions and rejected/saturated samples.
Retain full-range exposures for characterization while excluding invalid ranges
from the ordinary gain estimator. Use pair differences to suppress fixed pattern;
handle illumination differences/drift and spatial structure explicitly.

For matched pairs, a useful estimator specification, with g in electrons/ADU, is:
S = (mean(F1)+mean(F2))/2 - mean_bias;
V = (Var(F1-F2)-Var(B1-B2))/2; V approximately S/g in the valid linear region;
RON_e = g sqrt(Var(B1-B2)/2). Define masks, sampling regions, robust estimators,
correlation assumptions and any corrections before adopting the final method.

One public mefpp_cal_lin service can coordinate separate internal estimators for
response non-linearity, shutter timing, gain and RON. Distinguish signal-dependent
response from effective exposure offsets and lamp drift; check identifiability
from the available sequence and request additional calibration data when needed.
Do not force a simultaneous solution the data cannot constrain. Export a shutter
map/model in time units with explicit sign convention and validity. Non-linearity
coefficient direction/order must match the application function; existing degree-4
Eclipse fits cannot simply be fed into a three-coefficient cubic application.

Select compatible measured gain/RON when available; otherwise use a versioned
instrument/detector/readout-mode default table. Reject invalid/incompatible
measurements with an explicit fallback reason. Store selected values, uncertainty,
measured/default status and provenance in science detector extensions, preserving
original values. Default entries must come from verified instrument information,
not fabricated constants. A missing valid measurement and default is a clear error.

For the documented ESO detector-header convention, ESO DET OUTn CONAD is e-/ADU
and ESO DET OUTn GAIN is ADU/e-. ESO QC quantities named gain can use e-/ADU.
Use explicit canonical internal units and per-instrument keyword mappings, never
magnitude-based guesses or a universal interpretation of the word GAIN. Verify
RON keyword units from actual instrument headers/documentation. Keep acquisition
gain/RON distinct from effective values after scaling or coaddition.

### Dark frames

Define matched temperature, exposure, binning and readout configuration, bias
handling, hot-pixel masks, uncertainty and reuse. Establish whether scaling with
exposure is valid for the detector/mode; do not assume it universally. A component
being available does not make dark subtraction mandatory for every instrument.

### Fringe frames and Python application

mefpp_cal_fringe constructs detector/filter/configuration-specific templates from
appropriate blank-sky or dithered science data, masking sources and separating
smooth background. Record normalization, masks/uncertainty/QC and provenance.
Python later determines each exposure's amplitude and subtracts the additive
fringe contribution. Define compatible units, source masks, model validity and
failure diagnostics; do not absorb the fringe template into a multiplicative flat.
The proposed usual placement is after compatible bias/flat corrections and before
resampling/coaddition, but exact ordering relative to other corrections belongs
to the reviewed product contract. Preserve astronomical extended structure.

Gate for new services, including variance creation/propagation: synthetic recovery tests, independent reference checks,
representative instrument data and Fernando's scientific acceptance of methods.
Existing functional notebook success is not this gate. Keep method validation
separate from later scientific parameter optimization across all survey fields.

## Stage 5 — Single-detector CCD support

Support primary-image and one-image-extension FITS through explicit detector
mapping rather than pretending every input has 32 chips. Preserve geometry,
overscan availability, binning, calibration matching, shutter/gain/RON metadata,
units, masks and uncertainty. Compare one extracted mosaic detector with the same
service operating independently. Test complete genuine single-detector datasets;
layout acceptance alone is not a validated CCD reduction. This abstraction feeds
both mosaic workers and the later CMOS service.

## Stage 6 — Parallel mosaic processing

Start with independent worker processes rather than assuming thread-safe Eclipse/
qfits calls. Profile CPU, peak memory and I/O to choose worker limits. One detector
may be a useful work unit, but full-cube calibration combines and shared statistics
still have dependencies. Make reference-normalization computation a barrier;
workers consume immutable calibration and normalization inputs.

Use isolated contexts, temporary paths and outputs, with one writer per file and
a coordinator for final MEF assembly. Keep deterministic detector ordering and
explicit partial-failure policy. Test one and multiple workers, allocation limits,
worker termination, disk/I/O failure, cleanup, resume and avoidance of duplicate
correction. Compare scientific pixels and relevant metadata with the serial
baseline, measuring any floating-point changes against agreed tolerances.

Stay within one node and account for outer processes times internal tool/BLAS
threads. No MPI or new threading requirement is implied. Most arithmetic may be
independent; the current implementation is not thereby already concurrency-safe.

### Threads inside each detector

Evaluate detector processes and intra-detector threads separately. First qualify
one CPU thread per worker; then benchmark representative pure numerical kernels
with controlled threading. Candidate work includes pixel arithmetic, filtering,
per-pixel fits and stack reductions. Use tiling/halos where neighborhood operations
require them. Keep FITS I/O, shared qfits/Eclipse state and final writers outside
threaded regions unless explicitly made and tested thread-safe.

OpenMP is a candidate optional C threading interface, not a selected requirement;
check compiler/runtime support on all targets, especially Apple Clang. Preserve a
serial build without its runtime. Compare workers x threads configurations under
a global CPU/memory budget; external tool/BLAS threads count too. More threads per
detector is not a universal default: memory bandwidth, small tasks, shared cache,
I/O and nested parallelism can limit gains. A single detector or few exposures may
benefit differently from a full mosaic. Require race, reproducibility and failure
checks in addition to speed measurements; memory-leak checks alone do not test races.

## Stage 6A — Optional GPU and accelerator assessment

This is an assessment deliverable, not a GPU implementation commitment or a new
prerequisite for CPU functionality. GPUs are valid scientific computing devices;
benefit and accuracy depend on algorithm, precision, backend and actual hardware.
Profile first. Candidate kernels include repeated large pixel operations,
convolutions/filtering and batched per-pixel fits; small fits, FITS parsing, metadata
and filesystem work are unlikely first targets. Even large simple arithmetic may
be limited by memory traffic rather than computation.

Compare serial/vectorized CPU, detector processes, controlled CPU threads and
selected GPU kernels on the same workloads. Include transfer/conversion, kernel
launch, synchronization, memory allocation and end-to-end I/O costs; measure peak
memory and throughput with the shared mosaic normalization preserved. Unified
memory does not remove bandwidth, synchronization or layout costs.

Keep the portable ANSI-C CPU core mandatory and any accelerator behind a narrow
optional backend. CUDA/NVIDIA and Metal/Apple are different ecosystems; shader or
GPU-specific code is not itself portable ANSI C. Do not introduce C++ as a core
requirement by selecting a backend silently. Investigate alternatives only against
actual supported hardware, toolchains, dependency/licensing and maintenance cost.
No NVIDIA GPU on chapman3 or GPU on the Intel Mac is assumed from existing records.

Define precision per operation, especially accumulation, variance, fitting and
rejection decisions. Verify FP32/FP64 support and throughput on each target; do
not infer double-precision compute from 64-bit integer or address support or from
CPU double support. No automatic FP64-to-FP32 conversion or fast-math change.
Compare pixel/calibration/QC results and selection boundaries against the CPU
reference with reviewed tolerances; deterministic reductions and reproducibility
policy must be explicit. Retain CPU fallback for unavailable/unsupported devices.

Gate: a measured adopt/defer recommendation with scope, precision, platform matrix,
CPU fallback, scientific equivalence and cost. GPU implementation, if worthwhile,
gets its own approved plan and may be deferred without blocking CMOS design or
other CPU-only deliverables. No hardware purchase or GPU dependency is implied.

## Stage 7 — Native Apple Silicon and Windows qualification

Apple Silicon is an explicit supported-platform requirement, not optional GPU
support. Qualify native arm64 source build, bundled libraries/resources, installation,
C/Python boundary and representative serial/single-detector/parallel paths on an
identified current machine/macOS/compiler. Inspect binary/dependency architectures;
Rosetta execution is not arm64 acceptance. Record minimum OS/SDK and tested hardware;
new Apple Silicon generations remain targets to qualify rather than an unbounded
claim of compatibility. CPU-only operation must work without a GPU backend.

### Windows build and installation

Audit paths, process launching, temporary files, permissions, getopt, shell helpers,
Unix sockets/shared memory and other POSIX dependencies. Isolate/disable optional
legacy interfaces explicitly where they are not part of the supported FITS path;
do not remove required functionality silently. Require native compiler/linker,
installed resources, large FITS files, paths with spaces and documented launch/
configuration behavior. WSL execution does not establish native Windows support.

Gate: clean native build/install and representative installed serial/single-detector/
parallel tests on an identified Windows machine, with compiler and OS recorded.
This gate covers mefpp and bundled dependencies. Full Pycavi plus all external
astronomy engines on Windows is a distinct application qualification, not promised
by this native roadmap. Retain pending Apple Silicon/Ubuntu target acceptance.

## Stage 8 — CMOS review and reduction services

First publish a camera/readout-mode-specific review and calibration acquisition
plan. Reuse qualified array/FITS/mask/provenance infrastructure; determine where
CCD assumptions fail. Cover pixel-dependent offsets, gain and read-noise maps,
dark/exposure/temperature behavior, unstable switching pixels, row/column patterns,
gain-channel transitions, non-linearity/saturation, on-camera corrections and
rolling/global exposure timing. These are possible properties, not universal CMOS
features or a reason to apply image denoising to science data without review.

Identify actual cameras, mode metadata, monochrome/colour layout if applicable,
required datasets and target platforms. Define uncertainty propagation and tests
of photometry/timing, then implement bounded services. Do not claim that single-HDU
support or one scalar gain makes the pipeline CMOS-qualified.

## Proposed target relationships — not an implemented API

```mermaid
flowchart TD
    C["Pycavi or thin CLI"] --> R["Stage requests and explicit results"]
    R --> K["Bias, BPM, dark and detector characterization"]
    R --> F["Dome, sky, master-flat and fringe products"]
    K --> S["Science preprocessing"]
    F --> S
    N["Shared mosaic normalization"] --> F
    N --> S
    S --> P["Python fringe scaling and subtraction"]
    K --> U["Shared C services: arrays, detector mapping, FITS, status and provenance"]
    F --> U
    S --> U
    U --> E["Qualified Eclipse kernels"]
    U --> Q["Bundled qfits"]
```

This diagram expresses service relationships, not the final calibration acquisition
DAG or a requirement to run all corrections. Detector-specific validity and
correction-state contracts determine the actual order.

## Acceptance records and change control

For every bounded implementation: identify issue, baseline, affected contracts,
invariants, fixtures, expected results/tolerances, target platforms and rollback.
Before each functional/result test explain purpose, actual production routines,
inputs/actions/outputs/pass criteria and limitations. Script section comments and
those explanations must correspond both ways. Record what actually ran; a zero
wrapper exit, compile-only probe or written test is not product acceptance.

Maintain a platform matrix (pending/pass/fail with exact evidence) and gate ledger.
Measure regressions and resource use only on identified inputs and environments.
Protect raw data, original calibrations, accepted outputs and working installations.
No broad upgrades, new scientific defaults, archive submission or branch cleanup
are implicit in this plan. WFI needs dedicated qualification; OCAM alone is not it.

The wider Pycavi thin-notebook/configured-script/library audit and Phase 3 work
remain in [the overall roadmap](roadmap.md). This native sequence is brought
forward by Fernando's explicit decision; it does not close those other work items.

### Revision procedure

Keep version 1 as the initial design record. For each material revision, increment
version/date and record evidence, decision, affected interfaces/gates and whether
prior acceptance needs repeating. Update this file and the current architecture
when implementation actually changes; do not rewrite a proposed design as if it
were already installed. Discuss scope/order changes before dependent work.

| Version | Date | Change | Status |
|---|---|---|---|
| 1 | 2026-10-25 | Initial build -> memory -> data review -> components -> single-detector -> parallel -> Windows -> CMOS plan, with calibration contracts | Proposed for review; no implementation started |
| 1.1 | 2026-10-25 | Observatory/archive scope for data review; explicit native Apple Silicon acceptance; optional intra-detector threading and GPU assessment | Planning amendment; no implementation or GPU backend selected |
| 1.2 | 2026-10-25 | C89/C90 portable source baseline with explicit C17 compilation and behavior checks; actual chapman3 toolchain constraint | Policy clarification; source compliance and target qualification pending |
| 1.3 | 2026-10-25 | Fernando adds per-pixel frame-variance creation and propagation to Stage 4, including calibration uncertainty, common normalization and downstream handoffs | Planning requirement; no variance implementation or new processing |
| 1.4 | 2026-10-25 | Defer pip-versus-Conda/micromamba distribution evaluation as a TODO; resume current native regression/build-install gates | No package manager selected or package implementation started |

## Primary references informing the design

- [HDF5 model/library](https://support.hdfgroup.org/documentation/hdf5/latest/_intro_h_d_f5.html),
  [ASDF specification](https://asdf-standard.readthedocs.io/),
  [Zarr specifications and implementations](https://zarr.dev/), and
  [IVOA standards/status register](https://www.ivoa.net/documents/). These inform
  the review shortlist; no replacement or performance conclusion is selected.
- [CMake C standard selection](https://cmake.org/cmake/help/latest/prop_tgt/C_STANDARD.html)
  and [generators](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html).
- [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html),
  [LeakSanitizer](https://clang.llvm.org/docs/LeakSanitizer.html) and
  [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html).
- [ESO OmegaCAM detector monitoring](https://www.eso.org/observing/dfo/quality/OMEGACAM/qc/gain_qc1.html)
  and [historical calibration plan](https://www.eso.org/sci/facilities/paranal/instruments/omegacam/doc/DFS-CAL.pdf).
  Template versions differ: Fernando's adjacent randomized pairs are the current
  requirement; do not infer exact ordering from one historical template.
- [Bagnulo et al. 2015, A&A 583 A115](https://www.aanda.org/articles/aa/pdf/2015/11/aa26497-15.pdf):
  explicit discussion of ESO detector-header versus QC gain naming.
- [McDonald Observatory shutter correction](https://mcdonald.utexas.edu/research-facilities/HJST/DIAFI/diafi-shutter-correction).
- [ESO fringing services](https://www.eso.org/sci/software/pyhdrl/pyhdrl-site/user/func/fringe.html)
  and [CFHT fringe construction](https://www.cfht.hawaii.edu/Instruments/Elixir/mkdetrend.html).
- [Alarcon et al. 2023, astronomical IMX455/IMX411 characterization](https://arxiv.org/abs/2302.03700),
  [pixel-dependent CMOS characterization](https://www.nature.com/articles/s41467-022-30907-2)
  and [Andor exposure-mode explanation](https://andor.oxinst.com/learning/view/article/rolling-and-global-shutter).

### Additional primary references for revision 1.1

- [JWST processing products](https://jwst-pipeline.readthedocs.io/en/stable/jwst/data_products/stages.html).
- [Roman ASDF information](https://roman-docs.stsci.edu/data-handbook/wfi-data-levels-and-products/asdf-format-information).
- [Rubin DP1 raw FITS exposures](https://dp1.lsst.io/products/images/raw_exposure.html),
  [deep coadds](https://dp1.lsst.io/products/images/deep_coadd.html) and
  [Butler/pipeline design](https://arxiv.org/abs/2303.03313).
- [ELT ICS Data Acquisition manual, v3](https://ftp.eso.org/pub/elt/documents/ESO-396401-ELT_ICS_Framework_-_Data_Acquisition_-_User_Manual.pdf).
- [ESO Data Interface Control status](https://www.eso.org/cms/tools-documentation/eso-data-interface-control.html)
  and [Phase 3 product guidance](https://support.eso.org/en-US/kb/articles/description-of-reduced-data-products-in-the-eso-science-archive).
- [OpenMP overview](https://www.openmp.org/spec-html/5.2/openmpch1.html),
  [NVIDIA floating-point guidance](https://docs.nvidia.com/cuda/floating-point/index.html)
  and [Apple Metal compute](https://developer.apple.com/metal/).
