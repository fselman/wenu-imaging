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
