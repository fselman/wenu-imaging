# Pycavi: thin notebooks and configuration-driven scripts

Review: 21 October 2026, source baseline
`d17784d9603065f22773c2fbbd29a8d13e4a0d60`. Fernando clarified the intended
architecture: notebooks should contain few lines calling libraries, while
remaining editable for learning/exploration; Python scripts and configuration
files should offer the same processing without interactive notebook execution.
WFI must be included throughout, alongside OmegaCAM. No implementation changed.

## Existing strengths

The original design is substantially present. `pycavi_instrument.Instrument`
loads instrument-specific configuration and extension/gain maps; both WFI and
OmegaCAM CFG/PAF resources exist. Association/reduction, astrometry, astromatic
integration, photometric calibration, Chebyshev/Kriging and catalogue modules
already perform much of the work. Shared functions should be reused, not replaced
by a new reduction engine. Editable notebooks and disk-backed project directories
are suitable interfaces for understanding and inspecting data.

Recent pilot evidence covers OmegaCAM with historical native tools. Chebyshev
model export/plotting and catalogue creation/repeat protection were repaired and
have ten focused regressions. This is not full pipeline or WFI validation.

## Where implementation differs from the intended design

### Notebooks remain partly implementation code

Nonblank, non-comment code lines counted across all code cells (not a measure
of scientific complexity or a target quota):

| Notebook | Lines | Responsibility still visible in notebook |
|---|---:|---|
| 00 project setup | 18 | GUI invocation and configuration display |
| 01 partitioning | 33 | Configuration unpacking and partition creation |
| 03 reduction | 117 | Calibration dependency traversal, selection and sequencing |
| 05 SCAMP | 144 | Extraction/SCAMP settings, directory work, loops and execution |
| 06 SWarp | 127 | Group selection, preparation, settings and coaddition orchestration |
| 07 photometric calibration | 72 | Project selection and calibration invocation |
| 07b photometric QC | 119 | Extraction/selection/diagnostics orchestration |
| 08a Chebyshev | 177 | Sampling, fitting, diagnostics and output handling |
| 08b Kriging | 218 | Sampling, model/diagnostic orchestration |
| 09 catalogue | 212 | Catalogue construction, matching, headers, model choice and corrected copies |
| 0 WFI calibration selection | 206 | Two classes, table cleaning and calibration-selection algorithm |

Keep meaningful parameter choices and inspection/plots visible, but move stable
scientific implementation and filesystem sequencing into callable functions.
Few lines per meaningful operation is the goal, not one opaque command hiding
everything. Expert exploration can still call lower-level routines.

07c identifies itself as obsolete; 09 testing contains 46 code cells and about
786 non-comment lines, including duplicate function definitions. These are not
additional supported production paths. Establish a clearly documented production
notebook sequence and retain exploratory examples separately without silently
deleting user work. Kriging is not certified by the Chebyshev pilot.

### Script interface has drifted

Five files exist under `pycavi/scripts`, but the installed entry points register
only `pycavi_setup` and `pycavi_setastro`; reduction-script entries are commented
out and the explicit package list does not include the scripts directory.

- Script 01 imports the old `mefpp_associate_reduction` name, has personal paths
  and invokes current classes/functions using obsolete signatures, for example
  `PartitionsTree()` without the current required arguments.
- Script 02 imports `mefpp_solve`, duplicates a solve loop and fixes OmegaCAM
  prefixes/filter choices instead of using one shared instrument-driven path.
- Scripts 03/04 import `mefpp_astromatic`; script 05 imports `zp_calibration` and
  embeds its own extraction configuration/workflow. These are old names not the
  current installed `pycavi.pycavi` modules.

This source review establishes drift, not a successful or attempted production
run of the legacy scripts. Do not advertise script/notebook equivalence yet.

### Configuration is incomplete as an execution contract

Project and instrument CFG/PAF files already exist, but many extraction/SCAMP/
SWarp, selection, model and photometric choices are set in notebook cells.
Executable selection is separate in `~/.pycavi`; notebook 03 confuses the mefpp
executable path with an installation prefix. Personal paths, cwd assumptions and
sys.path edits also impede a headless installed run.

`ZPCalibration.__init__` performs copying, processing and header writes, rather
than only constructing configuration/state; it can return early when an output
exists. Shared stage wrappers should make actions and repeat behavior explicit,
without requiring an immediate rewrite of that class.

## WFI is a required path, not an OmegaCAM parameter variant

Retain WFI's eight configured image extensions and per-extension gain-key map,
`FLAT,SCREEN` dome frames, WFI standard-frame classification, filter identities
and La Silla provenance. Do not replace these with OmegaCAM's 32-extension or
Paranal assumptions. The WFI configuration contains a stale comment suggesting
only two valid chips, although all eight are enabled; document/validate actual
input layouts instead of using that comment as a detector policy.

Specific WFI work:

1. Extract `ExecutionBlock_WFI`, `CalExp_WFI`, `reform_df` and
   `select_calibrations` from the WFI notebook into an installed library module.
   Expose one selection call to notebooks and scripts. Preserve template-block
   grouping, date/filter criteria, minimum frame counts and aggregation defaults
   initially. Record selected dataset identifiers and reasons.
2. Make archive CSV locations and raw-input paths explicit; current notebook uses
   personal paths and `../data/...` CSVs that setup does not install into the
   orchestration directory. Existing four WFI query tables are historical data,
   not a current general archive service. Validate their schemas and identities.
3. Audit selector edge cases before changes: equal time-distance dictionary keys
   can replace one another; empty selection reaches index zero of an empty list;
   blanket dropna can discard usable rows; detector mode is not established by
   the archive grouping. These are source findings, not a new real-data test.
4. WFI preselection may use TPL START because archival OB metadata is unavailable,
   while the general Exposure path expects configured OBS START/ID and other
   keys. Verify historical WFI headers and define explicit valid mappings or
   alternatives. Do not synthesize misleading observation provenance.
5. Notebook 09 writes telescope ESO-VST and instrument OMEGACAM. Obtain these from
   validated instrument/project/input metadata for WFI as well as OmegaCAM.
6. Photometric code includes generic/Johnson-Cousins and WFI-related filter
   mappings, but those tables alone do not establish correctness for every WFI
   passband. Verify physical filter-to-reference-band mappings, AB/Vega choices,
   transformations, pivot wavelengths and zeropoints using a WFI reference set.
7. `extinction_coeff` currently supplies a Paranal curve and otherwise None.
   Audit actual call sites and WFI use, then define scientifically supported
   La Silla handling; do not silently substitute Paranal or invent coefficients.
8. `ZPCalibration` contains an initial fixed [10000:10100,10000:10100] QC slice,
   notwithstanding instrument-configured QC regions. Make relevant sampling
   instrument/shape aware and cover WFI/small images. This is an identified
   assumption, not a demonstrated failure on a newly run WFI coadd.

WFI users who already have appropriate raw calibrations should not be forced
through archive preselection. Cover both WFI preselection and ordinary reduction,
including standard fields as well as science targets. A representative real WFI
regression dataset and accepted comparison tolerances remain to be chosen.

## Proposed common library interface

Add a small stage/orchestration layer around existing routines, with one loader
and validator for project, instrument and execution options. A stage accepts
explicit settings and selections and returns structured results: input/output
paths, selections/associations, status, measurements, diagnostics and provenance.
Plotting functions consume those results without requiring a notebook kernel.

Both frontends use that same layer:

- Notebook: load settings; inspect inputs/associations; edit a few meaningful
  parameters; call a stage; inspect tables/images/QC. Allow optional overrides
  and record the effective settings used for each run.
- Script/CLI: load the same settings; optionally override explicit options;
  invoke the same stages; write logs/QC/results and return meaningful exit codes.
  Support one stage at a time and the full dependency-respecting sequence.

Illustrative interface only, not existing executable code:

```python
project = load_project("config/pycavi.cfg")
plan = plan_reduction(project, targets=["chosen_target"])
display(plan.associations)
result = reduce(project, plan=plan)
```

The CLI should expose equivalent configuration/selection, not execute notebooks
behind the scenes and not implement a second reduction algorithm. API names and
the exact CLI spelling are to be selected during focused implementation.

Use the existing CFG/PAF format first. Separate project selections, instrument
physics/metadata, external-engine settings and execution resources, but combine
and validate them once. Distinguish defaults from run overrides and record the
resolved values. No new workflow framework or library upgrade is required.

Make Tk optional at import; headless scripts must not create windows or require
IPython display. Remove cwd/sys.path dependencies from supported frontends.
Repair command/worker failure reporting and output ownership before extending
parallel execution. The same library task scheduling serves both interfaces;
retain a serial mode for scientific comparisons.

## Minimal sequence and acceptance

1. Repair ordinary installation/resources and environment declarations, keeping
   current dependency ceilings and working environments. Explicitly include WFI.
2. Establish configuration loading/validation and stage results; wrap existing
   functions. Start with WFI selection and partitioning/association, then reduction,
   astrometry, coaddition, calibration/QC, illumination and catalogue creation.
3. Thin the production notebooks while retaining readable parameter/inspection
   cells. Do not change algorithms or thresholds while moving their location.
4. Replace unsupported legacy script paths with thin installed commands calling
   those same stage functions. Preserve historical scripts as clearly identified
   references until callers are checked; avoid maintaining two implementations.
5. Validate notebook-versus-script equivalence for OmegaCAM and WFI: same inputs,
   settings, calibration selections, relevant measurements and products within
   agreed tolerances. Exercise fresh kernels, headless runs, cwd independence,
   overrides, failures, restart and one-/multi-filter/standard-field cases.
6. Build single-node parallelism on the shared task boundaries, with serial/parallel
   comparisons for both instruments. Detector generalization follows the separate
   audit; mefpp implementation remains after the Pycavi milestone.

These are staged changes to finish the existing design, not a wholesale rewrite.
Phase 3 metadata/validation is a separate output stage (issue #9). Broader
photometric/astrometric science findings remain #7/#8. Portability is #10 and
detector/concurrency planning is #12. No libraries or engines are upgraded here.
