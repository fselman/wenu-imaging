# Architecture

mefpp owns standalone native reduction: recipe configuration and input admission,
image processing, FITS products and ASDF QC/provenance. Pycavi may coordinate
workflows and inspect products, but is an optional client. No external runtime,
preparation command or generated-bindings file is a user prerequisite for running
a mefpp recipe. External astrometry.net, Source-Extractor, SCAMP and SWarp retain
their own roles. Bundled qfits/Eclipse provide native FITS and image services.

## Command and configuration contract

The public recipe executable is `mefpp_recipe`; its command shape is
`mefpp_recipe cal OPERATION --config RECIPE.toml [options]`.
The native command reads the recipe and its referenced project/settings/input
files. Internally derived requests are owned by the native implementation.
Help is hierarchical, requires no data/configuration and performs no processing:

```
mefpp --help
mefpp_recipe cal --help
mefpp_recipe cal bpm-linearity --help
mefpp_recipe cal linearity --help
mefpp_recipe cal bias --help
```

Top-level help names the recipe command; calibration help lists operations;
operation help describes inputs, options, defaults and outputs. Guides show native
Unix commands only, without `nice` or environment-specific wrapper commands.
Existing executable aliases and stored producer identities remain compatibility
contracts during migration; they do not define the new public interface.

Project TOML owns raw, calibration, reduced, work and log roots; its directory is
orchestration. Recipes reference it without repeating roots. Raw observations
and input calibrations are read-only; controls belong in orchestration and outputs,
private work and logs below reduced. Use fresh destinations and retain failures.
Keep reduction purpose, ordered recipe and product/compliance profile distinct.
Logical detector ID, input HDU, configuration slot and output ordinal are separate
explicit bindings; do not infer them from array position.

## Processing and publication

Native services use typed configuration/request/context/result owners. The inner
lifecycle is validate, load, calculate, optional publish, cleanup. High-level
recipes follow the [common template](native-operation-recipe-template.md) and bias
example, showing the processing order in readable calls. Reuse services without
forcing collective operations into independent per-detector calculations.

BPM/linearity reads each detector's calibrations and raw planes once, captures
raw-only evidence, corrects/trims once and retains one owned processed cube.
A supplied BPM skips creation, explicitly logged; otherwise robust BPM fitting
borrows that cube. Subsequent linearity ROI/pair/site measurements borrow the same
cube before release. Full-file integrity hashing remains separate I/O. Linearity
is measurement only. See the [detector contract](design/common-recipe-coordinator-v1.md).

Final image products retain MEF structure. The shared native writer publishes
ASDF QC/provenance; completion requires no downstream client. QC availability,
masks, populations and arithmetic are scientific contracts. Analysis and viewers
consume saved measurements without reprocessing inputs. Suitability assessments
must not erase evidence or masquerade as scientific acceptance.

## Implementation status

Bias is accepted. The BPM/linearity shared-cube processing has focused numerical
and Mac evidence, but its public interface is incomplete: native recipe-only
admission and the unified command/help hierarchy must replace the current binding
compiler prerequisite before standalone acceptance. See the [roadmap](roadmap.md).
Configuration resources under `docs/architecture/proposed/` retain their existing
paths; their older designs do not override this architecture or current owner decisions.
