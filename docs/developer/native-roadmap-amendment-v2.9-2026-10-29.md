# Native roadmap amendment v2.9 — 29 October 2026

## Owner direction and authorization

After accepting Stage 2.1, the owner specified the next refactor direction and instructed "Proceed": split mefpp into subroutines; replace PAF with TOML organized into appropriate subsets; use an ASDF document containing the relevant processing information and FITS locations while retaining images in MEF FITS; design from the start for parallel execution and ordinary single-detector FITS; include the data-partitioning and mefpp-reduction notebooks; evaluate a Python library named mefppy. The owner also suggested examining the larger, possibly incompletely reduced Chapman dataset.

This selects TOML configuration and ASDF metadata with FITS-resident images as the design direction, superseding the earlier open-ended retain/adopt format choice only for this bounded analysis. It does not adopt earlier exploratory WISDG/remote-retrieval/shallow-directory proposals or an exact schema, backend library, binding technology, filesystem migration or scheduler.

## Current authorized work

- Source and notebook analysis at accepted main 22a32d39463a73ab32d2ba9d811f949198852902.
- Proposed normalized configuration model, TOML subsets and conversion rules.
- Proposed ASDF observation/product/calibration/provenance model and external-FITS resolver contract.
- Subroutine boundaries, explicit state/ownership, serial equivalence and future parallel barriers.
- Single-detector and mosaic identity/layout design.
- mefppy feasibility and binding/library packaging comparison.
- Read-only Chapman directory/association/completion inventory, using actual-host evidence; no presumption of complete reduction.
- A staged implementation proposal for review.

No production C/header/Python/notebook edits, dependency installation, reductions, data movement, runtime parallelization, accepted-baseline rerun or numerical/scientific change begins in this analysis. Appropriate .h changes belong in the subsequent implementation plan alongside .c changes.

## Preserved gates

Stage 2 and Stage 2.1 remain accepted. The accepted OCAM/WFI baseline and all failed/successful products/logs/installations remain unchanged. Stage 2A now supplies the concrete refactor design before Stage 3 implementation. New calibration methods/variance services, full downstream processing and Phase 3 certification retain their separately scoped gates. Issues #30, #116, #125, #128 and #131 are not closed by this amendment.

The prior frozen roadmap and amendments v2.0–v2.8 remain byte-identical. This amendment adds no native launch or diagnostic matrix.

See [initial source analysis and design proposal](mefpp-refactor-analysis-2026-10-29.md). Chapman runtime inventory and final interface/library choices remain pending.

