# Developer documentation

Working agreement and scope accepted by Fernando Selman on 20 October 2026.
Updated for the subsequent decision to consolidate into one repository.

| Document | Purpose |
|---|---|
| [Agent instructions](agent-instructions.md) | Current shared working rules and scientific invariants |
| [Architecture](architecture.md) | Existing components, interfaces and agreed direction |
| [Migration](migration.md) | Repository consolidation, checks and merge requirements |
| [Roadmap](roadmap.md) | Platform priorities, operational OmegaCAM delivery and later capabilities |
| [Original audit, 20 October 2026](audit-2026-10-20.md) | Original source-based findings and historical proposals, preserved unchanged |

The immediate goal is a scientifically validated reduction of a medium-sized
OmegaCAM dataset, prepared for submission as ESO Phase 3 products. Dataset
inventory and precise product/validation requirements remain to be established.

Current multiprocessing is within a single node. mefpp does not implement
multiprocessing and remains serial for the operational milestone. Later work
includes mefpp multiprocessing and reductions from single CCD and single CMOS
detectors, after wenu-imaging works correctly.

The audit predates acceptance and subsequent scope clarifications. Its references
to proposed instructions, pending decisions and earlier document locations are
historical. Use the current agent instructions and roadmap for present scope.
Preserve the audit rather than rewriting what was reported at that baseline.

The root `AGENTS.md` is an entry point to the canonical policy in this directory;
it keeps these instructions discoverable when an agent opens the monorepo workspace.
