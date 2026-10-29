# Architecture documents

- [Original Pycavi/mefpp architecture](original/pycavi-mefpp.md): source-based pre-refactor snapshot at accepted main 22a32d39463a73ab32d2ba9d811f949198852902, including the current diagram and working-directory behavior. [Mermaid source](original/pycavi-mefpp.mmd).
- [Proposed target architecture](proposed/pycavi-mefpp.md): revision-4 executive summary and diagram: WAD, ASDF processing projects, explicit paths, versioned dependency/association graph and future incremental reprocessing. First-pass records are separated from deferred trigger/cascade execution. [Mermaid source](proposed/pycavi-mefpp.mmd).
- [WAD and ASDF processing projects](proposed/wad-processing-project.md): common schemas, project/plan/run lifecycle, metadata authority, offline resources and publication/recovery contracts.
- [Implementation plan](proposed/implementation-plan.md): detailed first-pass milestones, gates/rollback and later parallel/incremental passes.
- [Detailed refactor analysis](../developer/mefpp-refactor-analysis-2026-10-29.md), [PAF inventory](../developer/mefpp-refactor-paf-inventory-2026-10-29.md) and [Chapman4 evidence](../developer/mefpp-refactor-chapman4-inventory-2026-10-29.md).

"Original" is a dated observed baseline. "Proposed" is an unimplemented design; publication does not approve its detailed interfaces or start refactoring.
