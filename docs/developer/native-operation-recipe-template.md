# Common recipe template

A high-level recipe should normally fit two readable pages, at most three. It
shows the processing order with meaningful calls; supporting modules expose the
mechanics. Do not compress statements or hide the entire program in one helper.
The [bias coordinator](../../mefpp2/ins/mef/recipes/mefpp_bias_recipe.c) is the first
implementation of this structure.

1. Initialize safely destructible owners and capture the start time once.
2. Prepare configuration and admit all explicit input/detector bindings.
3. Establish run resources after admission.
4. Execute the declared processing, including required collective steps.
5. Verify result coverage and stored QC, then publish products.
6. Report success/failure and release owners; retain required failed work.

`mef_recipe_run.h/.c` manages shared paths, exclusive logs, workspace and reporting.
Recipe-specific typed state owns its configuration, bindings and results. Keep
scientific defaults and policies out of shared run resources. This is direct
orchestration, not a new generic callback dispatcher.

`mef_operation_template.h/.c` supplies the inner validate/load/calculate/optional-
publish/cleanup lifecycle. Each service remains responsible for metadata, result
completeness, ownership and its publication boundary. Calculation may already
populate QC; verification must not silently recompute or change its populations.

Use descriptive names, ordinary flow and logical paragraphs. Give standalone
comments blank lines before/after. A few unique scientific-stage landmarks connect
source file/routine/ID to the LaTeX/PDF explanation. Comments explain intent and
contracts. Source references use immutable designs or issues, not development steps.

Bias needs no cross-detector balancing. Flats or collective fits may need it; share
structure and services without imposing bias's scientific independence on them.
