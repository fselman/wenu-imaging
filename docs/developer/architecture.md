# Architecture

mefpp owns standalone native reduction: recipe configuration and input admission,
image processing, FITS products and ASDF QC/provenance. Pycavi may coordinate
workflows and inspect products, but is an optional client. No external runtime,
preparation command or generated-bindings file is a user prerequisite for running
a mefpp recipe. External astrometry.net, Source-Extractor, SCAMP and SWarp retain
their own roles. Bundled qfits/Eclipse provide native FITS and image services.

## Command and configuration contract

The public recipe executable is `mefpp_recipe`; its command shape is
`mefpp_recipe CATEGORY OPERATION --config RECIPE.toml [options]`.
The native command reads the recipe and its referenced project, detector, and
classified observation-list files. These four files define the target native
configuration contract. The implementation owns internally derived requests.
Help is hierarchical, requires no data/configuration and performs no processing:

```
mefpp --help
mefpp_recipe cal --help
mefpp_recipe sci --help
mefpp_recipe cal bpm-linearity --help
mefpp_recipe cal linearity --help
mefpp_recipe cal bias --help
```

Top-level help names the recipe command; calibration help lists operations;
operation help describes inputs, options, defaults and outputs. Guides show native
Unix commands only, without `nice` or environment-specific wrapper commands.
Existing executable aliases and stored producer identities remain compatibility
contracts during migration; they do not define the new public interface.

One native catalogue supplies command dispatch and help for all recipes.
`cal` contains bias, BPM/linearity, linearity, BPM, dark, fringes, domeff, skyff
and mff; `sci` contains pp. Entries still awaiting migration are explicitly
pending and refuse execution. Register future recipes in this catalogue; keep
their processing in their own readable entry points.

Project TOML owns raw, calibration, reduced, work and log roots; its directory is
orchestration. Recipes reference it without repeating roots. Raw observations
and input calibrations are read-only; controls belong in orchestration and outputs,
private work and logs below reduced. Use fresh destinations. Retain test
outputs and logs only through verification or active diagnosis. Preserve the
designated legacy reductions as comparison references and record a concise
comparison summary in the PR. Test workspaces have no permanent archive.
Keep reduction purpose, ordered recipe and product/compliance profile distinct.
Logical detector ID, input HDU, configuration slot and output ordinal are separate
explicit bindings; do not infer them from array position.

### Four-file native configuration

| File | Responsibility |
| --- | --- |
| Project TOML | Project identity and directory roots. Its directory is orchestration and may have any name. Use a separate orchestration and reduced root for each test project. Recipes for the same project and software version share those roots. |
| Detector TOML | Shared instrument and readout catalogue, including detector IDs, native slots, default HDUs, geometry, and enabled or disabled status. Use `wfi-1x1.toml` and `ocam-1x1.toml` for the respective profiles. Keep disabled detectors in the catalogue with explicit status. |
| Recipe TOML | References to the project, detector catalogue and observation list, plus processing policy, detector selection and explicit calibration product references. Detector sections may hold recipe-specific settings, such as measurement ROIs and sites or a calibration HDU override. Shared detector definitions belong in the detector catalogue. |
| Observation list (`.list`) | Ordered rows of absolute FITS path, tab, and `DPR.TYPE`. The recipe references the list by absolute path. |

Raw observations and explicitly selected calibration FITS products are data inputs.
The four-file contract requires no separate native settings or processing-profile
TOML. During migration, move settings according to their ownership and preserve
effective values. Legacy formats remain compatibility inputs.

The shared TOML loader takes an explicit path and returns an owned, typed
document with its source path and bytes. It preserves the TOML values as
written. Field names, required keys, defaults, units, path resolution and
processing choices are interpreted by the recipe or by the project and detector
adapters it calls. Those adapters convert the document into the domain-specific
C structures used by the processing services.

### Dependency checking: later development

Implement and validate individual recipes first, starting with BPM/linearity.
Each checks its direct inputs and reports absent prerequisites; it does not
automatically launch other recipes. Implement the shared dependency checker
after the individual recipes, using their established input/output contracts.

The later checker applies the same rule to every required calibration: reuse an
explicit compatible reduced product, or plan its construction from an explicit
nonempty input list. Resolve the complete dependency chain before processing.
Report all requirements for which neither a product nor a usable list exists.
If the chain is complete but products need construction, announce every required
additional reduction and request permission for that plan before starting it.
Refusal or absent confirmation starts no additional reductions. Optional inputs
remain governed by the individual recipe's declared policy.

For MFF, resolve dome and sky independently: each may be a saved flat or a raw
flat list. Reuse supplied products; build only missing components after permission,
then combine them with the existing MFF algorithm. Validate detector/HDU, filter,
binning, readout and geometry compatibility and preserve input lineage. These are
target requirements; the checker and MFF execution are not implemented yet.

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
and Mac evidence. Native schema-2 admission and the unified command/help catalogue
are implemented and passed the complete synthetic Mac gate. A bounded
supplied-mask/QC-off CCD65 direct CLI run reproduces the saved reference
measurements. Earlier no-mask CCD65 saved-product and Viewer checks passed. The classified-list
interface and fresh WFI and OCAM workflows passed on the Mac. The four-file
configuration migration remains open. Scientific QC and selection are separate.
Historical binding compilation is compatibility only. See the [roadmap](roadmap.md).
Configuration resources under `docs/architecture/proposed/` retain their existing
paths; their older designs do not override this architecture or current owner decisions.

## Shared processing-list contract

BPM/linearity and bias use an absolute path in recipe `inputs.list`. Each row
contains an absolute FITS path and `DPR.TYPE`. The list directory is configurable.
The recipe owns processing policy and explicit
reduced calibration bindings, not observation filenames or pair assignments.
Project TOML owns roots. Native admission derives flat pairs from classification
and header exposure times; missing/ambiguous groups are refused. Dependencies
are reduced products only; reducing dependency lists is deferred. Optional raw
BIAS rows are diagnostic processing inputs, never a request to construct a master.
With a flats-only list, bias-pair RON/gain are unavailable; ROI/pair/site measurements
continue. Recipe-specific rectangular ROIs and named individual-pixel sites
belong to the recipe. Preserve list/classification/order/bindings in ASDF.
Old inline recipes and unclassified bias lists are compatibility only.
