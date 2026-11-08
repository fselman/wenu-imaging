# Architecture

Pycavi owns orchestration, configuration/association and user workflows. mefpp owns
native image processing; its bundled qfits/Eclipse provide FITS and image services.
External astrometry.net, Source-Extractor, SCAMP and SWarp retain their own roles.

Keep reduction purpose, ordered recipe and product/compliance profile distinct.
Resolve inputs, calibrations, detector mappings and destinations explicitly. Logical
detector ID, input HDU, configuration slot and output ordinal are different concepts.
Do not infer them from array position or silently discover missing dependencies.

Native services use typed configuration/request/context/result boundaries with
explicit ownership. The shared inner operation lifecycle is validate, load,
calculate, optional publish, cleanup. The outer recipe follows the
[common template](native-operation-recipe-template.md). Bias processes detectors
serially; other recipes may require mosaic normalization or collective fits.
Do not force collective operations into independent per-detector calculations.

Final native products retain MEF structure. QC/provenance uses a shared ASDF schema
and native writer; native mefpp does not depend on Pycavi to complete an ASDF product.
QC quantities, masks, missing values and population definitions are scientific
contracts. Plotting reads saved values rather than recalculating them.

Raw inputs are immutable. Work orchestration and reduced products occupy separate
locations. Publication must report truthful completion and preserve failed work.
Concurrent/incremental processing, detector-profile extensions and Phase 3 output
must be implemented under their own agreed scientific/product contracts.

Executable configuration contracts/examples currently remain under
`docs/architecture/proposed/`; Pycavi and configuration checks use them. Moving those
resources into package/test directories is a separate code/resource migration.
