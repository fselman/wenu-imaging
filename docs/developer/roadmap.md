# Current priorities

1. Complete observational BPM/linearity qualification using the accepted bias
   template. `mefpp_recipe cal bpm-linearity --config RECIPE.toml` must admit its
   inputs and run without an external preparation stage or generated-bindings
   prerequisite. The complete synthetic Mac gate and bounded supplied-mask CCD65
   comparison and earlier no-mask saved-product/Viewer checks passed. Next:
   qualify the shared classified-list interface on the Mac, then review broader
   detector/instrument coverage. Preserve the cube and existing estimators.
2. Preserve validated hierarchical help and the shared catalogue for every recipe:
   `mefpp --help`, `mefpp_recipe CATEGORY --help`, and operation help. Categories
   include `cal` and `sci`; unmigrated entries are pending and refuse execution.
   Help requires no observation/configuration and lists implemented inputs,
   options, defaults and outputs. Keep migration separate from registration.
3. Align the concise LaTeX/PDF guide and OCAM/WFI recipe TOMLs with that actual
   interface. Begin with an executive summary; show native commands without
   `nice`. Project TOML owns directory roots. Complete actual instrument bindings
   before describing a template as runnable; WFI linearity inputs remain unverified.
4. Qualify the affected native admission, help, ownership and ASDF paths, then
   let the owner execute the agreed observational tests from orchestration.
   Preserve raw data, accepted bias products and the stopped 32-detector run.
   Distinguish completed processing, recorded suitability and owner acceptance.
5. Complete the small recipe-based primary acceptance suite and operational
   OCAM/WFI workflows. Continue later recipes with the same readable template;
   add collective operations only where their scientific contracts require them.
   Each individual recipe validates its direct inputs without automatically
   launching another recipe.
6. After the individual recipes are developed and validated, implement the
   shared dependency checker. For every required calibration, resolve a saved
   product or explicit input list. Report missing sources together; announce
   all additional reductions and request permission before executing the plan.
   MFF uses the same rule independently for its dome and sky components.

Bias and the shared-cube source are owner-accepted; acceptance does not establish
qualification of the new standalone BPM/linearity interface. Directory reorganization
remains deferred until BPM/linearity development finishes. CCD68/90 residuals,
the viewer Update service, physical linearity correction and cross-talk remain
deferred. Noise/uncertainty and new fitting policies require scientific review.

Mac Intel is the current development/reference host. Preserve CentOS 7/Chapman
compatibility; Apple Silicon and Ubuntu coverage remain future work. Phase 3 is
a product-profile requirement. Work details and unresolved defects belong in
issues/PRs, not chronological additions to this roadmap.

## Shared processing-list contract

BPM/linearity and bias use recipe `inputs.list`, referencing an ordered text list
of `path<TAB>DPR.TYPE` observations. The recipe owns processing policy and explicit
reduced calibration bindings, not observation filenames or pair assignments.
Project TOML owns roots. Native admission derives flat pairs from classification
and header exposure times; missing/ambiguous groups are refused. Dependencies
are reduced products only; reducing dependency lists is deferred. Optional raw
BIAS rows are diagnostic processing inputs, never a request to construct a master.
With a flats-only list, bias-pair RON/gain are unavailable; ROI/pair/site measurements
continue. Rectangular ROIs belong to the processing profile; direct sites are
named individual pixels. Preserve list/classification/order/bindings in ASDF.
Old inline recipes and unclassified bias lists are compatibility only. The new
classified-list interface needs Mac qualification before selection/acceptance.
