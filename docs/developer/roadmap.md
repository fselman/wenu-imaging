# Current priorities

1. Finish the standalone native BPM/linearity interface using the accepted bias
   template. `mefpp_recipe cal bpm-linearity --config RECIPE.toml` must admit its
   inputs and run without an external preparation stage or generated-bindings
   prerequisite. Preserve the shared processed cube and existing estimators.
2. Implement hierarchical help: `mefpp --help`, `mefpp_recipe cal --help`, and
   operation help for `bias`, `linearity` and `bpm-linearity`. Help requires no
   observation/configuration and lists inputs, options, defaults and outputs.
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

Bias and the shared-cube source are owner-accepted; acceptance does not establish
completion of the standalone BPM/linearity interface. Directory reorganization
remains deferred until BPM/linearity development finishes. CCD68/90 residuals,
the viewer Update service, physical linearity correction and cross-talk remain
deferred. Noise/uncertainty and new fitting policies require scientific review.

Mac Intel is the current development/reference host. Preserve CentOS 7/Chapman
compatibility; Apple Silicon and Ubuntu coverage remain future work. Phase 3 is
a product-profile requirement. Work details and unresolved defects belong in
issues/PRs, not chronological additions to this roadmap.
