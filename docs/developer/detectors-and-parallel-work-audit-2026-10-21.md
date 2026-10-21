# Single-detector support and single-node parallel work: initial audit

21 October 2026. Read-only Pycavi source audit at
`d17784d9603065f22773c2fbbd29a8d13e4a0d60`. No detector/concurrency implementation
or benchmark was performed. Current priority is packaging and Pycavi improvement
with existing libraries. mefpp implementation comes afterward. This document
identifies concrete assumptions and defines the next audit/implementation work;
it is not a complete C-engine audit or a claim of general detector support.

## Single detector: confirmed assumptions

- `Instrument` reads a configured extension count and names, then builds the
  valid-extension/gain mapping. That is a useful existing abstraction: some
  loops already scale down to one configured extension. Do not replace all
  instrument handling just because OmegaCAM has 32 CCDs and WFI has eight.
- `file_format` is read, but the distributed OmegaCAM configuration explicitly
  says only MEF is implemented. No completed primary-image SINGLE path was
  established. A one-chip camera, one image HDU and one amplifier are different
  concepts; a single physical sensor may still use multiple readout extensions.
- `Exposure` expects observation/category/template/target/detector metadata via
  configured primary-header keys. A non-ESO instrument cannot be supported by
  changing extension count alone. Define explicit mappings/required fields and
  justified alternatives; do not invent ESO programme or observation identifiers.
- `mefpp_normalize_science` obtains gains from named extension headers, divides
  by the configured valid count and updates extension arrays in place using the
  average gain/exposure. Primary-array images are not covered by that path as
  written. Preserve existing mosaic average-gain semantics until separately
  reviewed; new single-detector behavior must define units and avoid duplicate
  normalization. Repeated/in-place normalization also needs restart safeguards.
- `run_solve_field` extracts each configured image extension into a temporary
  image. `create_wcs_frame` always creates an empty PrimaryHDU plus ImageHDUs;
  output layout therefore needs an explicit policy for single-chip input.
- OmegaCAM light-concentration functions guard on instrument name and require
  instrument-specific geometry. Do not apply those corrections to a new CCD/CMOS.
- Configured image-QC sections around pixel 10000 can exceed a small detector.
  Derive valid bounds or require appropriate instrument settings.
- Mask/BPM, bias/dome/sky/master-flat selection and the mefpp PAF interface are
  tied to the current reduction sequence. A dark/readout-mode/exposure/temperature
  model and optional calibration steps have not been established for new cameras.

### Target design to audit

Reuse Instrument with an explicit mapping from detector identity to science HDU,
metadata HDU(s), amplifier geometry, gain, noise and saturation. Cover primary
2D FITS, one image extension, multiple amplifiers and existing mosaics. Keep the
observation metadata mapping separate from storage layout and detector physics.

CCD and CMOS must be qualified separately. Audit overscan availability, bias vs
dark treatment, gain/read noise per mode, nonlinear response, saturation,
bad-pixel masks, dark/amp glow and any required spatial noise information. These
are questions to establish from camera data/specifications, not assumptions that
every CMOS requires every correction. Do not force cosmetic MEF wrapping as a
substitute for a valid detector/calibration model.

Use synthetic primary-image/one-extension/multi-extension fixtures for metadata,
layout and bookkeeping, then real identified CCD/CMOS data for scientific
validation. Device identity and representative data are still pending.

## Pipeline task opportunities

The goal is to parallelize every suitable independent task on a single node,
preserving the dependency graph and scientific operations.

| Stage | Potential concurrent work | Barrier or ownership constraint |
|---|---|---|
| Inventory/header classification | Read independent FITS headers | Deterministic merge/classification and one writer for partition lists/links |
| Master calibrations | Independent detector/mode/epoch partitions | Bias/dome/sky/master dependencies first; no duplicate writer to one master; native engine changes deferred |
| Science reduction | Independent exposures once required masters are complete | Masters immutable; separate working/output paths; current mefpp retained until its later audit |
| Normalization and detector QC | Independent image files; detector calculations where useful | One writer per FITS file, no concurrent HDU updates; normalization applied exactly once |
| Initial astrometry | Independent exposure-detector solves, pooled across exposures | Shared read-only indexes; one node-wide worker budget; assemble only after declared solve status |
| Source extraction | Independent exposure/detector or target-band jobs as required | Unique working files/logs and preserved segmentation/detection semantics |
| SCAMP | Independent fit groups; engine threads within a group | Preserve fit-group definition, reference catalogue/epoch and joint solution; not arbitrary per-CCD split |
| SWarp/coaddition | Independent target/filter groups; engine parallel internals | Shared geometry/weights/background rules and final combining operation retained; memory/I/O limits |
| Photometric calibration | Independent targets/bands; disjoint star-batch measurements where justified | Query/cache ownership, shared model/zeropoint fit and deterministic aggregation |
| Illumination/QC | Independent target-band models and diagnostic products | Same fit/validation samples; no concurrent writers to image/catalogue; bounded fitting/BLAS threads |
| Catalogue/Phase 3 preparation | Independent extraction/validation per output | Cross-band merges, cross-file associations and final manifest depend on completed inputs |

Candidate tasks require profiling before speedup claims. File I/O, very short
tasks, memory limits or a scientific global fit can make additional workers
ineffective. A serial coordination/barrier is not a reason to leave independent
upstream computations serial.

## Current obstacles to safe concurrency

- `run_py4_solve` loops exposures sequentially and creates an extension pool for
  each exposure. This offers detector concurrency but not a shared pool across
  all exposure-detector tasks. Do not nest exposure pools around existing pools.
- Worker AsyncResult is waited on without get(), and the pool is closed without
  explicit join. Repair failure collection/lifecycle before scheduling more work.
- Notebook 04 uses visible CPU count minus two, not an explicit node allocation;
  values also need a positive lower bound. External engine/BLAS threads can
  multiply process counts unless coordinated.
- Reduction, astrometry and astromatic wrappers change process-wide cwd and use
  fixed config/catalogue/log names. Threads sharing those calls are unsafe;
  separate worker processes alone are insufficient if their output directories
  collide. Prefer explicit cwd arguments and task-specific paths at boundaries.
- Partition construction writes shared lists/links; calibration selection and
  association need deterministic orchestration, not workers rewriting one tree.
- FITS updates occur in place. A task owns the complete output file; per-detector
  parallel calculations must return results for one controlled write/assembly.
- Catalogue creation, correction and QC share target directories and filenames.
  Input/config/model digests plus stage status are needed to distinguish completed
  work from a stale file left by a failed process. Existence alone is inadequate.
- Shared catalog queries/cache files and imports with remote-service side effects
  need staging and a single-writer/cache policy before offline cluster execution.
- Calibration/model/linear algebra steps may be memory intensive. The approximately
  382-million-pixel coadd makes copying full arrays to each process expensive;
  audit file-based inputs, read-only memmaps and bounded chunks before adding workers.

## Execution design and acceptance criteria

Use a simple bounded single-node task runner around existing functions rather
than introduce a workflow framework. Each task specifies immutable inputs,
dependencies, owned outputs, working directory, CPU/thread budget and estimated
memory. The coordinator schedules only ready tasks and records success/failure,
configuration identities and resource use. Do not count submitted tasks as
completed products. Publish final outputs only after validation; avoid overwriting
good results with partial files from failed workers.

Audit and test serial-versus-parallel equivalence, worker exceptions and native
exit codes, missing/partial outputs, interruption/restart, duplicated requests,
paths with spaces, spawn/forkserver, low CPU/memory allocations and thread
oversubscription. Preserve stable ordering where it affects numerical reduction.
Define appropriate numerical tolerances with Fernando before real-data promotion;
measure wall time, peak RAM and I/O rather than assume all parallelism is faster.

The native mefpp follow-up must decide whether to parallelize independent process
invocations, per-detector C operations, or both, with the same resource budget.
The Pycavi milestone must leave an explicit interface for that later work without
pretending the current native engine is already multiprocessing or single-CMOS
capable. No multi-node/MPI requirement is introduced.
