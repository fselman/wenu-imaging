# Common recipe coordinator: conditionally approved structural amendment

Owner direction, 8 November 2026, within issue #292: the short bias recipe must
come from the common recipe template so that subsequent recipes share its
structure. The high-level file should normally occupy two readable pages and
at most three. Comments need visible blank lines around them. This is the design
amendment for the next structural pass, conditionally approved implementation scope; final source acceptance is pending.

## Build on both existing template layers

`mefpp2/ins/mef/common/mef_operation_template.h/.c` already implements the shared
operation lifecycle: validate, load, calculate, optionally publish, always clean
up temporary owners. `docs/developer/native-operation-recipe-template.md` is its
current companion scaffold. The historical M1 typed service scaffold lives under
`docs/architecture/proposed/m1/mef_operation_template.*.txt`; it explicitly
separates result validation and scientific QC before ownership transfer.

The 864-line bias command is an outer coordinator around those services. Its
argument handling, resource management, binding and publication mechanics have
accumulated outside the small operation template. Improving only the inner
callback runner cannot make that outer command short. Amend the common scaffold
at both levels and make bias the first implementation of the resulting pattern;
do not create an unrelated bias-only coordinator architecture.

## Common high-level structure

| Phase | Shared responsibility | Recipe-specific authority |
|---|---|---|
| Prepare run | Capture invocation, load settings, establish paths/log/provenance, initialize safely destructible owners | Operation identity and explicit required settings |
| Admit inputs | Resolve ordered catalogue and detector/HDU bindings; enforce no-clobber and declared dependencies | Scientific applicability, minimum inputs and calibration requirements |
| Execute declared processing | Coordinate the existing operation services and bounded resource lifetime | Typed calculation and processing order, including any required collective step |
| Verify results and QC | Check declared coverage, structural completeness and stored QC availability | Estimators, populations, scientific decisions and any already approved acceptance cuts |
| Publish products | Reuse header, assembly and QC-writing services with truthful declared commit boundaries | Product profile, metadata authority and operation-specific outputs |
| Finish or fail | Report status and release owners once; retain required evidence/private work on failure | Operation-specific retained results and diagnostics |

These are common responsibilities, not six newly added runtime callbacks. The conditionally approved C interfaces and module boundaries appear below. Reuse the
existing configuration/request/context/result separation, status/error machinery,
operation runner, product-path services, detector binding and MEF/QC services.
Use small shared run-resource state and operation-specific typed payloads; do not
recreate a giant universal state object or a new dispatch framework.

The visible recipe file selects and orders these phases, checks statuses and
contains only the needed recipe-specific orchestration. Supporting implementations
live in appropriately scoped modules, with names that make the calls intelligible.
Moving the entire long command into one opaque function does not satisfy the goal.
The initial target is roughly 100–150 normally formatted lines for that file,
including useful comments and error handling, not a universal C module limit.

## Preserve scientific differences

A common shape does not require all recipes to calculate independent detector
products. The execution phase must preserve shared mosaic flat normalization,
collective fits, calibration dependencies and explicit uncertainty/QC contracts
when those operations are implemented. Bias presently has no cross-detector
balancing; do not infer that other recipes share this property. No linearity
model or collective numerical implementation is authorized by this amendment.

In the existing operation runner, the calculation callback may already populate
QC in its typed result. Result/QC verification must not silently recompute those
measurements, change their populations or invent quality cuts. Publication and
ownership rules remain explicit; no multi-file transaction, automatic retry,
implicit input discovery or new scientific default is introduced.

## Source presentation

Put a blank line before and after a stand-alone explanatory block comment,
including a source-guide landmark. The file boundary needs no preceding blank
line. Short inline ownership annotations may remain inline where clearer.
Comments and spacing mark paragraphs; ordinary statements do not each need labels.

Keep a few stable scientific-stage labels in the appropriate service. A shared
landmark occurs once in the shared implementation and may be referenced by
several guides; recipe-specific landmarks use their operation prefix. Keep the
LaTeX/PDF guide's file/routine/identifier references synchronized during extraction.

## Implementation/review boundary

The outer bias command now implements these phases in 60 readable lines, with
support in `mef_bias_recipe_prepare.c`, `mef_bias_recipe_inputs.c`,
`mef_bias_recipe_process.c` and `mef_bias_recipe_products.c`. Shared run mechanics
live in `mef_recipe_run.h/.c`. Final owner source review and bounded selected-Mac
qualification remain pending. Preserve b833aca7 and existing products/evidence.
No observational rerun, installation or resumption of linearity is authorized.

## Conditional implementation contract — 8 November 2026

The owner conditionally approved proceeding and requires seeing the finished
source before final acceptance. The outer coordinator calls prepare, admit,
begin, per-detector processing, verify, publish, complete, and finish directly.
`mef_recipe_run` owns only shared paths, start time, log and private workspace;
`mef_bias_recipe` owns bias configuration, input bindings, assembly and QC.
Focused prepare/input/process/product modules implement those phases. The inner
operation runner and scientific service remain unchanged. No new dispatcher or
scientific policy is introduced. The draft stays unmerged.

After this refactor, consolidate superseded documentation and entry points in a
separate cleanup. Shipped source comments must describe behavior or reference an
immutable design revision or GitHub issue, never a temporary development stage.
Legacy executable and stored producer identifiers need an explicit compatibility
migration before renaming; retain them during this behavior-preserving extraction.
