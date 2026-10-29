# mefpp refactor — initial source analysis and design proposal

29 October 2026: see the [original architecture diagram](../architecture/original/pycavi-mefpp.md) and [target architecture proposal](../architecture/proposed/pycavi-mefpp.md). The proposed execution contract resolves inputs, calibrations, configuration and output/work destinations explicitly, without changing the caller's working directory or implicitly searching for files. Existing cwd-dependent behavior remains unchanged; this is design for discussion.

Date: 29 October 2026. Source baseline: main 22a32d39463a73ab32d2ba9d811f949198852902.
Scope: [owner amendment v2.9](native-roadmap-amendment-v2.9-2026-10-29.md).
Status: source analysis complete for the boundaries below; design proposed for review. Chapman4's compact science-partition census and workspace/project configuration relationship are now recorded; effective override mapping and target dependency/binding qualification remain pending. No production software or datasets changed.

## Decisions versus proposals

The owner selected subroutine decomposition, TOML configuration subsets, ASDF processing metadata with FITS-resident images, parallel-ready/single-detector design, notebook 01/03 analysis and mefppy evaluation. Exact public names, schema granularity, parser/binding choice, lifecycle and directory layout below are proposals.

The 28 October conversation synthesis was read as background. Its useful configuration-first sequence, detector identity/order and selection/status distinctions inform this proposal. Its previously exploratory ASDF direction is superseded by the owner's 29 October instruction. Other exploratory storage/retrieval/GUI/Python-replacement ideas remain unadopted.

## Current boundaries, checked in the accepted source

| Boundary | Actual source evidence | Consequence for extraction |
|---|---|---|
| CLI/context | mefpp.c:134 mef_bb_load selects PAF, then overrides via getopt; main:1438 initializes Eclipse and propagates engine status | Keep parsing/CLI initialization outside callable kernels; preserve recent status/cleanup repairs |
| Shared state | mefp_lib.h:57 mef_bb combines settings, paths, detector selection, statistics, scan measurements and frame names | Split immutable configuration, explicit request, per-detector work and result ownership |
| Serial engine | mefpp.c:367 mef_engine validates sets, allocates cross-detector statistics, loops xtnum, constructs/loads calibrations and processes science | Extract control flow and numerical kernels separately |
| Configuration | mefp_lib.c:80 mef_bb_new_from_paf; Pycavi Instrument also reads CFG and five output prefixes from PAF | Converting only the native reader would leave Python dependent on PAF |
| Partitioning | notebook 01 cell 5 calls PartitionsTree; constructor creates directories/lists/markers/links and selects calibrations | Separate inventory/plan from materialization; record association reasons before execution |
| Reduction orchestration | notebook 03 cells 3–4 discover list files, select numeric indices, rebuild dependencies, run wrappers and normalize | Provide one plan/execution library shared by notebook and scripts; retain interactive selection |
| Native output | mef_save creates primary header when xtnum==1; recipe appends science extensions to common output | Existing writer cannot simply be called concurrently per detector |
| Normalization | mefpp_normalize_science computes mean configured gain and updates images in place | Preserve numerical behavior, but make correction state explicit to prevent double application |

The older current-architecture document is a 25 October historical snapshot: qfits is now bundled, the build frontend exists, and main now propagates status. Do not reclassify its repaired findings as current defects.

### Partitioning and association

PartitionsTree groups bias by OB ID/start, flats by OB ID/filter/start and science/standards by target/filter/start. select_nearest_calib uses nearest time within the configured function windows (science bias 10 days, several flat links 30 days), and filter matching for non-bias classes. These are current selection semantics, not independently validated calibration policy.

Paths encode metadata: ExposuresPartition.getFilter/getOBstart split directory components; associateBias/Dome/Sky/MFF recover dependencies from symlinks. Missing files may be intentional unbuilt products. Notebook 03's empty idx_selected means all partitions, with selection based on discovery order rather than stable IDs. Local mefpp.paf takes precedence and can retain partition-specific overrides.

Propose stable observation, group, calibration, task and product identifiers in ASDF; treat current directories/lists/links as an import/export adapter. Do not move the existing data or adopt a shallow layout as part of this analysis. Preserve original filter names separately from sanitized path names, chronological/pair order, programme/OB/template identifiers when present, and the reasons for selected/rejected calibration candidates. Missing metadata stays missing. Current grouping and any proposed new scientific grouping must be distinguishable and compared before changing selection.

### Detector identity, shared normalization and publication

The current recipe enumerates extensions from 1..nchips or one positive xtnum. Calibration/science loaders use numeric HDUs, and the inspected science path logs EXTNAME comparisons. That does not establish detector-ID-based matching. This is the existing detector-identity audit requirement, not a newly qualified layout capability.

Use a per-file map: physical hdu_index, EXTNAME/EXTVER where applicable, detector_id, amplifier_id, original order, shape, geometry and units. Resolve calibration and configuration by detector identity, retaining physical HDU index as location. A primary image uses HDU 0 without inventing an EXTNAME or indexing ccd[-1]. Explicit configuration must resolve ambiguous/missing identity. Handle duplicate/unknown/missing IDs before arithmetic. Keep operational health, run selection and processing result as separate fields; do not renumber remaining detectors.

mef_build_cal uses dome_median[0]/sky_median[0] to preserve the common flat reference; mef_ff_combine mutates input arrays. Extracting one detector per worker without passing the same normalization reference can change science. Define a reference-statistic barrier and an immutable normalization result, preserve legacy reference selection first, then permit only separately reviewed alternatives.

Workers should produce isolated detector results. One coordinator owns ordered MEF assembly and publishes the ASDF product state after FITS completion and validation. Use unique attempt outputs and atomic publication where supported; crash recovery must distinguish temporary, partial, validated and published products. ASDF metadata and FITS cannot be assumed to form a single filesystem transaction. A partial FITS file or zero exit alone is not completion.

## Proposed configuration model and TOML subsets

First define one validated, serialization-independent C configuration model; retain the existing PAF adapter as the regression bridge. TOML and PAF must map to the same effective values before changing processing. Do not split PAF into temporary partial files. The migration inventory groups current template keys, not proof that every key is used on every execution.

| Proposed TOML subset | Contents / ownership |
|---|---|
| project.toml | Composition root, explicit subset references, project locations and run selection defaults |
| instrument.toml | Instrument identity, keyword mappings, detector IDs/geometry/readout descriptions and documented fallback gain/RON |
| association.toml | Frame classification, grouping keys, calibration applicability/time windows and deterministic selection rules |
| processing.toml | Overscan/trim, frame/pixel rejection, combine/smoothing/saturation parameters and normalization policy |
| recipe.toml | Requested operations, ordering/dependencies, calibration build/reuse and normalization placement |
| execution.toml | Engine/backend/tool selection, process/thread/memory/I/O limits, temporary/output ownership and logging |
| quality.toml | Explicit acceptance/QC criteria; keep diagnostic flags separate from exclusions |
| product.toml | Output layout/naming/header mappings, required associations and delivery requirements |
| profiles/*.toml | Distinct reduction-policy and product-profile definitions referenced explicitly; recipe remains separate |

These are domains, not a requirement to create nine files for every project. Reusable instrument files can be referenced by a small project entry point; split only where ownership, reuse or independent versioning warrants it. Measured calibration values are ASDF calibration products, not silently edited static defaults.

TOML composition is application policy: define explicit file roles, version compatibility, path base, cycle detection and conflict rules. Recommend defaults followed by explicit project overrides and explicit run overrides, with an allowlist of overridable fields. Reject conflicting definitions, unknown scientific keys and nonfinite/range-invalid values; report each effective value's source. Never silently merge detector arrays by list position or select a file from cwd.

Freeze supported TOML syntax against actual parser/Python/platform capability. Python 3.11 provides tomllib reading, not writing. A native C parser must be audited for language requirements, license, dependencies, numeric behavior, diagnostics and Mac/Chapman support before selection. Do not impose a new C language baseline to acquire a parser.

Illustrative composition only, syntactically checked with tomllib; not an implemented API:

```toml
schema_version = "0.1"
[configuration]
instrument = "instruments/omegacam.toml"
association = "association.toml"
processing = "processing.toml"
recipe = "recipes/legacy-preprocess.toml"
execution = "execution.toml"
product = "products/legacy-mef.toml"

[selection]
group_ids = ["science-group-001"]
```

Migration rules: inventory PAF keys, CFG mappings, CLI switches, implicit defaults and local overrides; map them to typed fields with units/ranges/source location; compare effective PAF/TOML configurations field-by-field. Preserve actual historical defaults and coercions explicitly before reviewing changes. Archive original text/hash and converter version; never claim that a generic text substitution is a safe PAF converter.

The [initial template inventory](mefpp-refactor-paf-inventory-2026-10-29.md) covers 591 OCAM entries and 257 WFI entries across 157 key families. WFI has 255 unique keys: the two repeated master-bias metadata keys have identical values. The importer must report repetitions and distinguish identical duplicates from conflicting overrides; no runtime error or correction is claimed from these occurrences. This inventory does not yet map all CFG/CLI/live-partition settings.

## ASDF document with external FITS images

ASDF is the structured description; image pixels remain in MEF FITS or ordinary FITS. No existing image is embedded, converted or renamed by this proposal.

| Entity | Required information |
|---|---|
| Document | Schema version, identity, revision/parent, base URI and creator/software identity |
| Observation | Original dataset/file identity, instrument, acquisition metadata and ordered detector references |
| FITS asset | URI/location(s), content identity, size, validation state and original-header preservation reference |
| Detector image | Detector ID, HDU index/name/version, shape, storage/physical dtype, scaling, units, geometry and correction state |
| Calibration | Role, input IDs, detector/readout/filter applicability, validity, measured/default provenance and uncertainty status |
| Group/association | Ordered members, selection policy/version, candidate/selection/rejection reasons and explicit dependencies |
| Configuration snapshot | Effective settings, subset contents or durable immutable references, hashes and override provenance |
| Task/attempt | Inputs/config/software identities, resource policy, command/backend, timestamps, status and diagnostic/product references |
| Product | Input lineage, FITS references, detector coverage, processing state, validation and publication status |
| Quality/uncertainty | Mask semantics, variance availability/units, covariance model/version or explicitly unknown state |

Propose a dataset index referencing per-run/per-product records instead of every worker rewriting one large shared ASDF file. This preserves a complete logical description without assuming a single ever-growing physical file. Granularity remains subject to Chapman dataset scale evidence.

A resolver must interpret relative paths against the containing document, support explicit relocation roots, check identity and HDU/detector/shape/type/scaling compatibility, and distinguish unavailable assets from corrupt/incompatible ones. Resolve EXTNAME ambiguity explicitly. A changed hash or stale reference is not permission to silently bind a new file. Keep runtime resolution local/offline unless future retrieval is separately authorized.

The ASDF externalarray type can hold a file URI, array target, type and shape, but its reference implementation does not validate or resolve external files. Define our resolver and schema; choose a standard externalarray plus companion metadata or a small versioned custom type after compatibility testing. Do not confuse an ASDF reference with pixel loading or accept plain YAML as ASDF.

FITS remains authoritative for stored image bytes and original acquisition cards; ASDF records normalized semantics, associations and processing history. Derived FITS headers must agree with the ASDF product description. Specify conflict policy and round-trip preservation of FITS cards, WCS and time rather than maintaining two silently divergent authorities. Complete metadata in ASDF does not remove FITS interoperability or the deferred qfits long-string obligation (#125).

### Who reads/writes ASDF?

| Option | Benefit | Qualification cost / open question |
|---|---|---|
| Python coordinator using ASDF; typed C requests | Keeps schemas/associations out of numerical kernels; natural notebook/mefppy integration | Define standalone CLI use and a validated request boundary without an accidental second authoritative configuration |
| Native adapter using libasdf | Standalone native access to the document | Actual C standard/dependencies, schema/tag support, platform build, ownership/error behavior and interoperability must be qualified |
| Both adapters over the same logical contract | Supports both interfaces | Prevent divergent validation/defaults; extra maintenance and cross-reader tests |

Official ASDF documentation now identifies libasdf as a C implementation with incomplete feature coverage. Native ASDF is therefore a real option to evaluate, not something to reject by assuming only Python/C++ exists. No adapter is selected or installed. Initial recommendation for review: keep the numerical C core independent of ASDF and evaluate Python-owned orchestration first, with native libasdf as the explicit standalone alternative.

## Subroutine/state decomposition

| Proposed boundary | Existing anchor | Input/output contract |
|---|---|---|
| Configuration adapters/validation | mef_bb_new_from_paf, mef_bb_load | Owned parsed inputs -> immutable validated config; no processing side effects |
| Asset and detector inventory | mef_valid_subset, header/load helpers | Explicit image references -> checked detector layouts/applicability |
| Calibration constructors | mef_build_cal, mef_build_bpm | Ordered input references/config -> owned detector calibration and diagnostics |
| Master-flat service | mef_ff_combine, mef_image_filter_flat | Explicit calibration ownership + shared reference -> owned flat |
| Detector science service | Inline mef_engine block | Inputs/calibrations/config -> processed image(s), state and QC |
| Normalization adapter | Python mefpp_normalize_science | Current explicit mean gain/exposure factor -> pixels/units/state once |
| Output writer | mef_save, mef_hdrpix_dump, recipe header code | Ordered detector results -> validated FITS asset |
| Coordinator | mef_engine + notebook 03 dependency cascade | Plan -> per-task results and published provenance |

Keep immutable config separate from run request, detector work buffers, calibration handles and results. Each allocator has one documented destruction function and failure path. Public headers expose small opaque handles or versioned plain descriptors, not mef_bb layout or Eclipse/qfits internals. Status includes stage/detector/product context and owns diagnostic strings predictably. Logging/cancellation hooks must not terminate the Python host. Audit initialization, allocator/cache/static-buffer state before promising reentrancy.

A file-reference-first interface can reuse native FITS I/O without promising zero-copy. A later array view needs dtype/endian/stride/shape/units, read-only versus mutable ownership and release semantics. No silent float precision conversion or new variance algorithms during equivalence extraction.

## Notebook redesign and mefppy

Notebook 01 should inspect inputs, show proposed groups/associations, accept explicit selection/overrides and save a validated plan. Separate its inventory, plan and filesystem-materialization operations so rerunning inspection does not recreate or alter the reduction arena. Keep science grouping and calibration selection distinct.

Notebook 03 should load the saved plan, display required tasks/build-or-reuse decisions, allow selecting one group, then call the shared executor. Preserve the ability to build calibrations first and inspect them before science. Record partial failures without replaying passed work; reuse requires compatible inputs/config/software policy plus verified outputs, not existence alone. Existing notebook04/other clients must continue consuming the retained FITS products; this refactor does not authorize downstream reruns.

mefppy is an optional Python client of the same native library, not an additional scientific implementation. Do not wrap main(argc, argv) as the public API. Compare:

- CFFI compiled API mode: compiler-checked native boundary and maintainable small C API, with a new packaging dependency to qualify.
- CPython extension: direct Python/buffer integration, with explicit interpreter/ABI and build maintenance.
- ctypes: lightweight ABI access for a narrow opaque-handle API, but declarations/lifetimes and ABI errors require care.
- CLI backend: retained diagnostic/compatibility path, with explicit commands/status/results.

Binding selection waits for the C contract. Test repeated calls in one interpreter, failure cleanup without process exit, Python-owned/borrowed memory lifetimes, cancellation, packaging outside the checkout, and CLI/library result equivalence. Releasing the GIL is not evidence of native thread safety. Start future parallelism with isolated processes; define spawned-worker context creation and never share raw native pointers across workers. Caches/logging/output ownership still require review.

## Proposed implementation increments, after design review

1. Complete Chapman read-only inventory and PAF/CFG/CLI/effective-default map; agree data contract, configuration roles and ASDF ownership.
2. Extract typed configuration/state boundaries with the existing PAF adapter; preserve CLI and serial behavior.
3. Add TOML subsets/resolution/validation and PAF-vs-TOML configuration equivalence.
4. Add ASDF/FITS resolver and read-only legacy-directory importer; validate references without rewriting data.
5. Separate notebook planning/execution into shared routines and serialize associations; preserve current selection first.
6. Extract one calibration/science/writer service at a time, including .h contracts and targeted ownership/status checks.
7. Qualify primary-image and single-extension layouts plus detector-ID selection and deterministic MEF assembly.
8. Decide and qualify mefppy over the same C services.
9. Implement bounded parallel execution only after serial equivalence, shared-reference barriers and process/output ownership are established.

These are ordered proposals, not a new unbounded implementation authorization. Reuse Stage 2.1 baselines; agree the smallest relevant checks at each change, rather than replaying the full Stage 2 campaign. New variance/calibration algorithms remain Stage 4 scope.

## Chapman evidence and remaining inventory

The [actual Chapman4 inventory and compact census](mefpp-refactor-chapman4-inventory-2026-10-29.md) record the requested ~/omegacam/testing and ~/fits roots. The later census found 205 historical science partitions / 963 list memberships across 42 target directories and two newer test partitions / ten memberships. The original recursive calibration/link scan remains partial; the compact science-list pass had no reported limits/errors at its specified depth. Known historical root from the recorded pilot: /home/fselman/omegacam/testing/reduced. A larger project may be elsewhere; first collect actual host/Git/environment evidence, root/config discovery and immediate directory listings. Then run a bounded metadata inventory of selected roots.

For each partition record list membership, link targets/broken links, local effective configuration/overrides, expected versus present products, sizes and stage reports/logs. Distinguish raw, native-preprocessed, normalized, detector-solved, assembled-WCS and later-tool states. Product presence establishes only a candidate state; a WCS label or all expected filenames does not establish validated completion. Sample FITS headers first; do not hash/read every large pixel array, follow directory symlinks recursively, repair links, delete partial files or resume jobs. Record unknown or contradictory state.

The inventory informs schema size/granularity, shared-calibration reuse, naming collisions, incomplete attempts, restart semantics and relocation needs. The actual directory scan is now observed on chapman4; no pipeline workload, header/pixel validation or complete reduction result is established. Its 181 absent link targets can include planned unbuilt calibrations, so do not repair them automatically.

### Workspace, project and attempt separation confirmed

The workflow config lives under ~/omegacam/workflows/wenu-imaging-test/config while its explicit project_dir points to ~/omegacam/testing/wenu-imaging-test. Raw assets live through ~/fits on /gluster. Therefore the TOML composition root must not assume that cwd, config location, reduction outputs and raw storage share a root. Relative configuration references should have a defined containing-file base; asset locations need an explicit project/storage resolver.

The newer project has stage-specific notebook run directories and pre-normalization backups. A canonical WCS path being absent cannot erase their history or establish an unrun stage. Model task attempts and product locations independently. The larger legacy tree is useful as an unexecuted association/import fixture, not an instruction to reduce all remaining members.

## Checks performed and limits

Inspected current C/header sources, notebook 00/01/03 cells, Python association/instrument code and OCAM/WFI templates. Built a reproducible key-family inventory and checked the illustrative TOML syntax. These are source/document checks, not native execution, dependency qualification, ASDF round-trip validation or scientific acceptance. No compiler/memory matrix, reduction, parser installation or target mutation was run. Chapman4's partial recursive inventory and later compact census were parsed and reconciled. Historical science rows total 205 partitions / 963 memberships, with ten matching local preprocessed files and 953 expected names absent at those locations. The newer project has two groups / ten matching preprocessed files. Exact effective local settings remain pending; a further broad dataset scan is unnecessary for the present design.

## Primary references checked 29 October 2026

- [TOML 1.0 specification](https://toml.io/en/v1.0.0) and [Python 3.11 tomllib](https://docs.python.org/3.11/library/tomllib.html).
- [ASDF ExternalArrayReference](https://www.asdf-format.org/projects/asdf/en/stable/api/asdf.ExternalArrayReference.html) and [core external-array schema](https://www.asdf-format.org/projects/asdf-standard/en/1.0.2/generated/stsci.edu/asdf/core/externalarray-1.0.0.html).
- [Official ASDF C implementation overview](https://www.asdf-format.org/en/latest/implementations/asdf-c.html).
- [CFFI overview](https://cffi.readthedocs.io/en/stable/overview.html) and [CPython extension interface](https://docs.python.org/3.11/extending/extending.html).

Dependency versions, standard revisions and platform feasibility must be pinned during the selected adapter qualification; these references do not certify current Mac/Chapman compatibility.

