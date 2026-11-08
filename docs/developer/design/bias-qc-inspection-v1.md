# Bias QC inspection v1 — approved scope, 7 November 2026

Owner accepted a small first calibration QC view after completing the bias
recipe. This is inspection of stored measurements, not a scientific estimator.
The prior viewer/database hold is superseded only for this bounded view (#282).

- Enumerate top-level product ASDF files in an explicitly selected directory.
  Open/schema-validate each once with the existing qualified ASDF interpreter;
  retain detached scalar measurements and metadata in the generated page.
- Display all stored master and embedded-input scalar measurements by product
  and detector, including unavailable states/reasons, units, complete definitions,
  source references, configuration indices and source/output HDUs. Array-valued
  measurements are listed by name/count; their contents are outside this first
  scalar view. Product metadata includes selected header cards, configuration
  snapshots, memberships and calibration references.
- Product selection highlights its rows and diamond plot markers while other
  products remain circles. Scope/detector/measurement/search/pagination controls
  operate solely on the already-loaded page data; there is no per-selection
  ASDF/FITS/raw read, server or network dependency.
- Plot stored finite measured numbers against detector categories. Definition
  groups include measurement name, unit, stage, method and the full region/mask
  definition; they never mix distinct units/methods/populations silently. Sample
  count remains visible per point. No averaging, fitting, thresholds, error bars
  or QC acceptance decision. Small categorical offsets separate overlapping
  products/inputs and are labeled as display offsets, not measurements.
- Show stored product creation time explicitly as creation time. No master
  observation epoch, JD conversion/aggregation or time-trend inference. An
  ordered raw-location-sequence digest flags shared inputs; this is a grouping
  of stored identities, not a content hash or proof of scientific equivalence.
- Invalid/unrecognized products are listed visibly; a partial page reports an
  incomplete collection and CLI exit 2. Source changes during reading abort.
  Empty/no-valid input writes no page. Existing output pages are not overwritten;
  require the user-selected output parent to exist, outside reduced products.

The self-contained HTML is a derived inspection snapshot. It is not a new
authoritative QC database, persistent harvesting cache or recipe product. A new
generation deliberately harvests again; toggling selectors/reopening this saved
page does not. Future refresh/history/storage policy remains undecided.

Reuse the native product schema and qc-plot-inspection.js cursor binding; do not
reuse the experiment-specific linearity viewer's ROI/gain model. The external
viewer uses Python/ASDF plus HTML/JS, like the independent comparator. Native
C/libasdf recipe, configurations, products and installation remain unchanged.

Qualification: detached projection/one-read/error/immutability controls and JS
definition/filter/zero/missing/pagination checks on synthetic stored metadata;
actual retained-ASDF generation and browser review on Mac. Synthetic tests are
not a claim of actual native-ASDF or browser acceptance. No new dependency,
scientific subroutine, mathematical guide change, build or reduction is needed.

## Owner-approved refinement after clipped RON acceptance

Default to seven common master parameters: clipped RON, raw RON, MAD RON, master mean, median, RMS and high-offset count. Embedded-input defaults show raw/corrected mean/RMS and scan median/RMS. An explicit All stored parameters control reveals the complete scalar collection; nothing is removed from harvesting or the page data. Prefer clipped RON on initial load when stored, while preserving a deliberate measurement selection during filtering.

A master overview displays those values side by side for every product/detector. Clipped RON is prominent; absence in an older product is Not stored, distinct from a stored unavailable diagnostic or numeric zero. Used/rejected frame counts summarize existing participation metadata, explicitly labeled as membership counts, without recalculating statistics or introducing synthetic QC measurements. Missing membership is Not recorded.

Retain all products on selection and visibly identify shared ordered raw-input sequences as repeated reductions rather than independent historical measurements. These are stored path identities, not hashes of image contents. Cache immutable definition keys, filtered row collections and overview projections in memory. Product selection never reopens ASDF; each generation deliberately reads each product once. JD, persistent harvesting/database policy and scientific acceptance thresholds remain deferred.
