# M0/M0a contract review package

Prepared 29 October 2026 from accepted main 0fa9eaf157359a93f2a9196f6fff05dc3e96e220. Development target: Intel Mac; later changed-interface qualification: chapman4. This increment contains documentation and synthetic review fixtures only. It does not approve/start M1 native changes or qualify new numerical capabilities.

## Purpose and deliverables

Make the [implementation plan](../implementation-plan.md) and [WAD/project design](../wad-processing-project.md) concrete enough to review before extraction. The package contains:

- [Contract catalog](contract-catalog.json): minimal record kinds/required fields/type notation, version 0.1.0-proposal.
- [Linked project example](project-example.json): 25 synthetic records, including two project/association/calibration versions, one frozen plan and an unstarted run.
- [Native boundary sketch](native-interface.h.txt): proposed opaque C contracts and ownership; not an installed or compiled public header.
- [Configuration migration ledger](configuration-ledger.json) and [interpretation](configuration-migration.md): source occurrences, constructor getter sites, CFG values, CLI fields and unresolved effective settings.
- [Focused verification plan](verification-plan.md) and [read-only fixture checker](check_contract.py).

JSON is used here as an easily reviewed, dependency-free representation of the proposed ASDF tree content. The catalog is explicitly **not** an ASDF metaschema or a general JSON Schema. The checker validates this small review notation and selected semantic invariants; it does not validate ASDF tags, converters, FITS files or real pipeline outputs. A real WAD schema/ASDF adapter is specified/qualified separately in M7. This avoids prematurely selecting an ASDF dependency or tag namespace.

## Proposed contract decisions

| Topic | Proposed rule / review boundary |
|---|---|
| Identity | Stable logical ID plus positive record version; exact record IDs use logical_id@version in this review notation. Public URI/tag syntax is not frozen. |
| Project | One evolving entry point selects an immutable project revision with an explicit parent. References may point back to older plans/products. |
| Plan | Exact project revision, ordered groups/associations, effective settings, task DAG and software requirement; no moving latest references. |
| Run/attempt | Actual execution identity and outcomes are separate from immutable plan content. A retry has a distinct attempt identity; changed request inputs produce a new plan. |
| Software | Record actual source/build/tool identity; the plan must name exact requirements or a separately qualified compatibility rule. |
| Configuration | TOML remains editable; normalized effective values and their sources are recoverable in each plan, not merely a hash of a mutable path. |
| Assets | Logical/content identity is separate from one or more location bindings. Unknown identity is not a verified match. |
| Detector | Stable detector ID is independent of ordinal HDU. Each science/calibration file resolves its own selector. |
| Units | Explicit signal units and squared variance units. Unit strings/conventions are reviewed; C receives normalized numeric values with documented units. |
| Missing values | Unknown/unavailable/not applicable/not requested are explicit; missing variance is never zero variance. |
| Corrections | Requested operations and applied state are distinct. Exactly-once normalization and dark/linearity/fringe state belong to product provenance. |
| Metadata authority | Keep original cards, normalized mappings, configured assumptions and characterized/derived values distinct; record conflicts and selection reasons. |
| Validation | Schema, references/layout, plan applicability, numerical behavior and product-profile compliance are separate gates. |
| Parallel readiness | Immutable requests/config; isolated work/result ownership; shared mosaic normalization is an explicit dependency/reference. No native thread safety is assumed. |
| Publication | One coordinator, expected-parent revision check, validated durable records/products before manifest advance; explicit interruption recovery. |

Paths resolve against their containing document or named root, never an incidental later cwd. Roots for raw, shared calibration, output, work and logs can differ. A scientific kernel neither discovers files nor selects a calibration.

## Reading the example

All identities, filenames, dimensions, calibration choices and gain values are synthetic. No supplied FITS exists or is opened. Assets are marked unavailable, products planned/not verified, and the run/attempt not started. A frozen plan is a reproducible request, not proof it is ready to run.

The science detector is CCD-A at HDU 2; bias uses HDU 1 and flat HDU 3. This demonstrates identity independent of extension order without asserting real detector-layout support. Descriptor variants include HDU 0 and one-extension images; actual FITS resolution remains M4/M7 work.

The original plan points to project:example@1 and association:science@1 selecting calibration:bias@1. Project revision 2 selects bias@2 and retains references to the old plan/run/product. That is legitimate historical provenance: the retained plan does not adopt revision 2's association. The full graph contains project/plan and run/attempt back-references; only task.depends_on defines executable dependencies and is checked for cycles.

A raw-reported gain of zero and a configured gain of 2 electron/adu are both retained. The effective synthetic choice is labeled configured, with a conflict and reason; it is not relabeled measured. This is a metadata-contract example, not a scientific recommendation or alteration of the accepted WFI gains.

The effective recipe represents the existing native scan/trim/bias/flat boundary. New linearity/dark correction is off, variance unavailable and Python normalization not requested for this task. Optional dark subtraction and later Python fringe subtraction remain explicit planned service contracts; no new scientific model is chosen here.

## Native ownership and client boundaries

The proposed C interface separates immutable validated settings, resolved request, mutable execution context, owned result and structured error. Context construction copies request/configuration data needed after return. Caller strings/records are borrowed only during that call. A result must retain anything it needs after context destruction; an error has an independent destruction owner. Partial failure leaves output handles null or valid/destructible, never half-owned.

CLI and optional mefppy adapt to the same services. C sees native structures/paths, not ASDF objects or Python references. File-based requests are the initial boundary; borrowed array buffers and GIL/thread behavior are not implied. Native status is authoritative; no ordinary processing error exits a Python host. .h and .c definitions evolve together when M1 is separately implemented.

The legacy PAF adapter remains available. Python owns the project/ASDF layer initially. A standalone native TOML CLI remains the target, but its C parser/dependency selection is not qualified by these fixtures. Keep C90/C17 and actual target constraints explicit rather than silently choosing a C99-only parser.

Production dependency requirement: [TOML/ASDF Chapman qualification](../../../developer/toml-asdf-chapman-qualification-2026-10-29.md). New dependencies must qualify on actual Chapman before adoption as well as on Mac. PR #134's contract-review package is accepted/merged; runtime/dependency decisions remain open.

## Verification and remaining decisions

Run the local, dependency-free review check with Python 3.11:

```bash
python docs/architecture/proposed/m0-m0a/check_contract.py
```

It reads its neighboring JSON files from any cwd and performs no writes or native launches. See [verification-plan.md](verification-plan.md) for actual scope and future gates. Source-ledger coverage is lexical, not runtime equivalence.

Still open before downstream implementation: the C TOML parser/language subset and license/platform decision; final WAD/ASDF schema/tag packaging; detailed metadata mappings/override allowlist; retained partition-local effective settings; new numerical model conventions/correction order; and exact publication locking/durability mechanism. No algorithm, threshold or scientific association improvement is silently selected by this review.

M0/M0a status: **prepared for contract review**, not accepted implementation completion. M1–M11 remain pending. The accepted Stage 2/2.1 baseline, frozen amendments, current installations and original datasets remain untouched.
