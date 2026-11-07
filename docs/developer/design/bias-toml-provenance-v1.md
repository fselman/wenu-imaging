# Bias recipe TOML and selected FITS provenance — 7 November 2026

Owner-directed bounded finish to bias: transfer a small configurable set of
primary and detector header keywords to product ASDF, support one-detector
products, remove the repeated detector CLI arguments, and process all detectors
by default (also explicit all) or an explicit ID subset. No QC viewer/database,
new estimator, JD aggregation, raw mutation or installation.

A recipe TOML (bias_recipe_schema_version=1) references the existing numerical
native TOML through settings. This is a small orchestration envelope, not a
replacement settings parser; existing native TOML/PAF command behavior remains
available. Paths for settings and BPMs resolve relative to the recipe TOML;
CLI input/output paths keep their invocation-directory meaning.

The root bias table holds common binding defaults, MAD/RON choices and optional
reference_detector. A detector table array is the authoritative complete catalogue
with IDs, independent zero-based configuration indices and per-input HDU(s).
Omitted bias.detectors means all catalogue entries; detectors="all" is explicit,
or detectors is a nonempty unique ID array. CLI --detectors accepts all or a
comma-separated explicit ID list; no detector-per-extension CLI is needed.
Reject unknown/duplicate IDs and ambiguous mixed CLI/TOML binding declarations.
Selected output order follows catalogue order. An omitted reference uses the
first selected detector; an explicit reference outside the selection fails.

One entry works exactly like many. Explicit HDU 0 (primary image), HDU 1
(single image extension), and multiple named extensions use the existing layout
and bias adapter. Optional expected_extname assertions check raw names without
requiring logical detector IDs to equal extension names. Final detector data
remain output extensions 1..N with explicit detector IDs.

The provenance table has primary and detector string lists (at most 16 unique
keywords each). Read only these cards from the completed final FITS, once before
native ASDF publication. Retain role, actual product HDU, detector ID, canonical
keyword, presence, typed scalar value, original FITS value/comment/card. Missing
cards have null value/card and explicit missing status. Unsupported scalar
syntax retains its literal rather than silently converting it. No unit/time
conversion and no raw pixel access. Primary keys are captured once; detector
keys once per selected output detector, including a one-detector product.

Store this optional block in qc.provenance.fits_headers, together with the
recipe TOML path and frozen text in provenance.recipe_configuration. Extend the
existing application v2 schema with optional metadata only; old products and
legacy calls omit these blocks unchanged. Existing QC values, contexts and FITS
cards remain unchanged. Caller captures bounded headers; the common native ASDF
writer still does not load images or discover files.

Focused checks: default/explicit all, explicit subsets and refusals, relative
paths, one primary/one extension/two extension fixtures, selected FITS/ASDF
values and missing keys, copied card identity, native memory/readback and
independent ASDF schema verification, unchanged numerical/QC/reference pixels.
Reuse existing selected Mac source/build/cache/tools; build affected existing
targets only. Actual Mac acceptance remains required before completion claims.
