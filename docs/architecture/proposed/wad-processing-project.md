# Wenu Attribute Dictionary and ASDF processing projects

Design direction recorded 29 October 2026; version 1. Owner instructed "Proceed" after reviewing WAD and the ASDF processing-project proposal. This authorizes this architecture/roadmap update. Concrete schemas, APIs, packaging and numerical implementation remain pending milestones, not installed capabilities.

See the [target architecture](pycavi-mefpp.md) and [implementation plan](implementation-plan.md). Existing accepted Stage 2/2.1 evidence and original files remain unchanged.

## Executive summary

WAD is the common vocabulary and schema contract for observations, detectors/images, calibrations, associations, processing requests/results and products. It also defines a ProcessingProject: the persistent scientific workspace through which users inspect data, propose associations, select a plan, run processing and find products.

ASDF serializes project and scientific records. FITS retains signal, variance and mask arrays, including MEF and single-detector layouts. TOML remains editable processing configuration; each execution plan preserves the resolved settings actually selected. WAD defines meaning and structure, while resolvers, association services and numerical routines implement behavior.

An evolving project points to exact-version records and plans. A frozen plan never silently adopts new data, calibration or settings. The initial implementation is manually initiated and serial; later impact analysis and cascades use these records without changing this distinction.

## 1. Responsibility boundaries

| Layer | Responsibility |
|---|---|
| WAD | Names, meanings, types, units/conventions, required fields, schema versions, authority/source rules and reference contracts |
| Data-model layer | Shared typed view of records, validation and adapters; used by notebooks, commands and serializers |
| ASDF adapter | Read/write records, schema/tag compatibility and packaged schema resolution |
| FITS resolver/I/O | Resolve locations and detector/HDU selectors; check layout and declared integrity; read/write arrays |
| TOML loader | Compose settings and declared overrides into an immutable effective configuration |
| Project service | Load project revisions, resolve record references, validate updates and coordinate publication/recovery |
| Association planner | Apply recorded compatibility/selection rules and freeze decisions and group membership |
| Executor/native services | Execute exact requests; report attempts/results; perform numerical operations |
| Future impact service | Re-evaluate affected associations and propose bounded work when inputs/policies change |

WAD is not a calibration selector, image-processing algorithm, database or task scheduler. Schema validity does not prove file availability, calibration applicability or scientific correctness.

Initially maintain the WAD definitions within the monorepo with independent schema versions. No separate repository, public package name, dependency framework or generated C ABI is selected. Package schema resources with supported readers so ordinary offline use does not depend on live schema URLs.

## 2. Record domains

| Record | Minimum contract |
|---|---|
| ProcessingProject | Stable project ID, revision and parent revision; purpose/profiles; location bindings; inventory/group/association references; configuration sources; plan/run/product references; selection/retention policy references |
| Observation/asset | Acquisition identity and original metadata evidence; logical/content identities; locations and availability; classification and verification level |
| Detector/image reference | Detector/amplifier ID; geometry, shape/type, signal units and correction state; explicit FITS selectors for signal/variance/masks |
| Calibration/model | Type, exact version, construction inputs, preparation state, applicability, validity, units/scaling/model convention, uncertainty and quality assessments |
| Group/association | Stable group definition and exact ordered membership; policy version, candidates, selected versions, reasons and overrides |
| ExecutionPlan | Exact source project revision, frozen inputs/associations/settings/software requirements, finite task DAG and expected outputs |
| Run/attempt/result | Plan identity, actual software/environment/resource information, task attempts, diagnostics, outcomes and exact published-product references |
| Product/assessment | Exact parents; detector coverage, FITS references, units/variance/masks/WCS/correction state; validation and publication state; scoped quality information |

A logical asset ID, record version, schema version, content identity, project revision and task/attempt ID serve different purposes. Do not substitute a filename or modification time for these identities.

The image contract must represent primary-HDU, one-extension and MEF inputs without forcing each observation into a separate file. Signal, variance and mask selectors belong to a detector identity, not an assumed extension number shared by every calibration.

## 3. Metadata authority and validation

Preserve original instrument keywords/cards alongside normalized WAD attributes and the mapping version. Separate raw reported values, configured assumptions, characterized calibration values and values derived by processing. Record the effective value selected for a request and why; never relabel a configured gain as measured or silently overwrite contradictory evidence.

Specify missing, unknown, not applicable, not requested, approximate and failed states deliberately. Missing variance is not zero variance. A stored product can be valid for its frozen inputs while no longer selected by the evolving project.

Validate at separate levels:

1. Schema: structure, supported versions, required attributes, types and declared units/conventions.
2. Reference/I/O: IDs, locations, file availability, detector mapping, layout and declared integrity checks.
3. Plan: exact-version dependency consistency, applicability, correction order/state and no executable cycles.
4. Numerical/scientific: algorithm-specific comparisons and calibration/model qualification.
5. Product profile: output and archive/compliance requirements, separately assessed.

Use primitives, mappings and lists for most metadata; qualify any richer tagged type and its cross-language reader requirements. Keep the C core independent of ASDF object internals. Validate typed native requests at their boundary as well as validating serialized records; documentation alone does not enforce the contract.

## 4. Project, plan and run lifecycle

The project is an evolving workspace. It references observations, overlapping scientific groups, selected associations and previous plans/runs/products. Records are not inferred from directory depth. Workspace, raw storage, shared calibrations, scratch and output roots can be distinct.

A plan freezes a particular project revision plus exact group membership, association decisions, effective settings and software requirements. A run records actual execution and attempts. Plan content is immutable; attempt outcomes are separate records. Retrying creates a new attempt, and altered inputs/settings require a new plan. Actual software that fails the plan's recorded compatibility requirement cannot silently satisfy that plan.

Changing TOML affects future resolved settings. Old plans retain snapshots or immutable recoverable references; a mutable pathname/hash alone is insufficient if the old content cannot be recovered.

Projects may pin accepted selections or follow explicit eligibility queries. Even a following project's running plan uses frozen versions. New arrivals first become inventory candidates; they do not automatically replace a selected calibration or launch numerical work.

The full relationship graph can have back-references. Freeze only producer/consumer processing edges into each finite task DAG. Scientific iterations require successive versions and separate bounds/convergence rules.

## 5. Small project entry point and distributed records

A project entry document is a compact manifest, not one giant recursive ASDF object containing all pixels, logs and historical runs. Reference records by stable ID plus explicit document/location bindings; serialize relationships as references rather than recursively expanding cycles.

Illustrative grouping only; filenames, directory names and granularity are not frozen:

- project.asdf: entry point referencing the active immutable project revision and related records.
- config/: editable TOML sources.
- records/: project revisions, observations, calibrations, associations, plans, runs and products.
- products/: new FITS outputs when local storage is appropriate.

Raw data and shared calibrations may remain outside this tree. Read-only legacy inspection does not create this layout or move existing files. ASDF child-document and FITS references use containing-document bases or declared root bindings; legacy lists retain their recorded original base.

Location-only changes update bindings without changing pixel identity. Unknown identity is reported as unverified; locating a different file with the same basename is not successful resolution.

## 6. Publication and recovery

Initially one project coordinator publishes revisions and updates the entry manifest. Workers, when later enabled, return isolated attempts/results rather than editing shared project state.

Write/validate products and durable records before advancing the visible project revision. A failed/interrupted publication must retain its attempt and not advertise an incomplete product as complete. Use same-filesystem staging/rename where applicable; ASDF and multiple FITS files do not form an automatic transaction.

The writer checks the expected parent revision before advancing the project entry point. Concurrent stale updates must be rejected or explicitly reconciled, not silently overwrite newer project state. The exact locking/durability protocol is specified and tested in M7/M9; no distributed database transaction is promised.

Do not delete old products or failed attempts as a side effect of updating a project. Retention/release/export policy is explicit. Relocation/export must account for referenced external documents, FITS, configuration snapshots and supported schema resources.

## 7. Shared clients

Notebook 00 selects/opens the project and configuration. Notebook 01 inventories candidates and reviews groups/association proposals. Notebook 03 inspects and executes a chosen frozen plan. Headless commands use the same library services.

The M3 inspector supports legacy trees first, then the WAD/ASDF project: project overview, target/filter/exposure tables, detector coverage, calibration dependencies, task/attempt outcomes and product locations. Summary/drill-down views and metadata-only access must expose incomplete scans, unresolved references and unverified status.

The inspector has no private calibration-selection implementation and does not modify project state. An explicit registration/update command is separate from read-only inspection. Notebook 04 consumes products through their FITS references; no replacement solver or implicit repeat normalization.

## 8. Roadmap and acceptance

M0a defines a small WAD foundation before the native types are finalized: one science exposure, detector mapping, selected calibrations, ordered group, association decision, project revision, plan and product/result examples. Schemas/contracts and examples grow with services rather than requiring a complete future mission dictionary.

M1–M6d align native/configuration/numerical interfaces with those contracts. M7 adds ASDF/FITS persistence and the project service; M8/M9 make shared planning and execution use it; M10 evaluates the same native contracts for mefppy. M11 checks cumulative consistency and migration.

Required focused controls include offline schema resolution, old-version handling, exact-plan stability after project updates, configured/measured metadata distinction, relocation, missing variance/references, read-only inspection, interrupted publication and stale-writer rejection. These are proposed checks, not executed tests.

Automatic monitoring, general invalidation, process parallelism and cascades remain later P/G passes. No ASDF/WAD runtime, migration, installation or science processing starts from this design document.

## 9. Roman inspiration and project-specific choices

The design borrows the shared-schema principle described by the [Roman data-model introduction](https://roman-datamodels.readthedocs.io/en/latest/roman_datamodels/datamodels/introduction.html), the schema/Python separation, and [RAD versioning](https://rad.readthedocs.io/en/latest/versioning.html). These sources were reviewed on 29 October 2026. Roman's [ASDF rationale](https://roman-docs.stsci.edu/data-handbook/wfi-data-levels-and-products/asdf-format-information) supports structured metadata and selective array access.

Our external FITS references, ProcessingProject records and future cascade plans are wenu-imaging proposals. They are not claims that Roman supplies this project service or scheduler. No Roman schema, package or instrument-specific numerical policy is adopted by this document.

## Status

Architecture direction recorded; exact schema vocabulary, tag namespace, packaging, project revision protocol, migration compatibility and numerical acceptance remain concrete milestone decisions. Original architecture and frozen roadmap amendments are unchanged.
