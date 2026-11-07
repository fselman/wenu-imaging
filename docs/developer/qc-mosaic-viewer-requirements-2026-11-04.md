# Initial HTML QC mosaic viewer — owner direction, 4 November 2026

The existing detector-footprint HTML viewer is the starting point. This records
the accepted direction; no QC mosaic is implemented by the ASDF persistence step.

- Preserve instrument mosaic placement and exact detector/output identity from
  the maintained geometry/processing TOMLs and their shared interpretation. Never
  infer physical CCD identity from FITS HDU order or Python configuration order.
- Select variance versus signal or diagnostic gain versus signal for mosaic tiles.
  Use common axes where useful for detector comparisons and label units/stage.
- Click a detector to enlarge its plots, identify its outputs/ROIs and toggle or
  select ROI curves. Preserve raw/retained coordinate context from configuration.
- Consume validated full-precision ASDF QC records and frozen inputs. Do not
  recalculate estimators, use rounded chat values or make HTML a new data authority.
- Show unavailable/failed/missing data and exclusions distinctly from zero.
  Show acquisition/pair IDs, counts, settings, stage, provenance and source links
  in detail. Arithmetic point-gain availability is not instrument-gain acceptance.
- Keep inspection read-only. No automatic raw rejection, reduction rerun, fitting
  interval or scientific-policy decision through this first viewer.
- Initial delivery should be self-contained offline HTML, consistent with the
  existing geometry viewer. The generator reads ASDF and TOMLs; browser payload
  and indexes are derived and reproducible. Avoid required remote/CDN services.
  Revisit format only when actual interaction/scale needs justify it.

Sequence: ASDF persistence of completed CCD65 -> plots from full precision ->
serial detector-wide measurements with one shared input fingerprint pass ->
initial HTML mosaic. Search for higher-illumination sequences and near-saturation
characterization is deferred. Current CCD65 windows reach about39kADU mean signal;
no display should imply measured coverage to the65534ADU exclusion boundary.

Existing geometry viewer maintenance requirements continue: schema/geometry/ROI/
identity changes update its interpretation and checks in the same change, and
future authoritative schemas must replace duplicate visualization-only profiles.


## Project QC architecture — owner decision, 4 November 2026

Owner reports that the first HTML viewer looks good. Complete the linearity script
before modifying the HTML navigation. This direction records the next increment;
it does not request implementation of every recipe now.

Add a recipe selector at the left edge of the HTML page. Initial navigation scope:
bias, BPM, linearity, dark, dome flats, sky flats, master flats, science, WCS,
zero points and illumination. Extend the system as each recipe is developed.
Unavailable or not-yet-implemented recipe assessments must remain explicit; a
navigation entry must not imply that a recipe ran or has valid QC.

Recipe execution and QC presentation are separate stages:

1. A recipe produces its scientific products and persisted QC measurements with
   the shared ASDF structure, units, availability and provenance.
2. Independent plot/HTML generation reads those saved records and project context
   to create reproducible inspection products. It must be possible to regenerate
   presentation without executing a recipe or repeating pixel measurements.

Keep plot generation and HTML creation as separate tools/modules from recipe
runners. Shared QC readers and presentation helpers may be reused. Navigation is
for inspecting saved recipe assessments; it does not launch recipe execution.
The existing detector mosaic and enlarged plots remain useful within each recipe
view. Recipe-specific panels grow incrementally under the common QC contract.

For now, QC is organized per project. A project-local QC context/index should
identify the recipe assessments, products, input provenance and derived plots/HTML
belonging to that project. Projects remain independently inspectable; no central
QC database or service is required. This decision does not move current retained
instrument data or choose new physical project directories.

Later, augment project QC with a QC database that supplies reference assessments
for comparison. Preserve source assessment/product identities, configuration,
detector/readout/binning, correction stage, units and provenance so comparisons
can be matched appropriately. Database access should extend the QC data-source
layer rather than couple recipe execution to HTML or require rewriting existing
measurements. Reference selection, acceptance thresholds and database technology
remain future decisions; no automatic scientific acceptance is introduced here.
