# Current priorities

1. Complete observational BPM/linearity qualification using the accepted bias
   template. `mefpp_recipe cal bpm-linearity --config RECIPE.toml` must admit its
   inputs and run without an external preparation stage or generated-bindings
   prerequisite. The complete synthetic Mac gate and bounded supplied-mask CCD65
   comparison and earlier no-mask saved-product/Viewer checks passed. The shared
   classified-list workflows passed on the Mac for WFI and OCAM. Next, complete
   the four-file configuration migration. Preserve the cube and estimators.
2. Preserve validated hierarchical help and the shared catalogue for every recipe:
   `mefpp --help`, `mefpp_recipe CATEGORY --help`, and operation help. Categories
   include `cal` and `sci`; unmigrated entries are pending and refuse execution.
   Help requires no observation/configuration and lists implemented inputs,
   options, defaults and outputs. Keep migration separate from registration.
3. Align the concise LaTeX/PDF guide and OCAM/WFI recipe TOMLs with that actual
   interface. Begin with an executive summary; show native commands without
   `nice`. Project TOML owns directory roots. Complete actual instrument bindings
   before describing a template as runnable.
4. Qualify the affected native admission, help, ownership and ASDF paths, then
   let the owner execute the agreed observational tests from orchestration.
   Preserve raw data and designated legacy comparison products. Record the
   comparison summary in the PR and retire temporary test workspaces after
   verification or diagnosis. Distinguish completion, suitability and acceptance.
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

Bias and the shared-cube source are owner-accepted. Fresh-project workflow checks
passed on Mac. Final configuration migration and scientific acceptance are
separate milestones. CCD68/90 residuals,
the viewer Update service, physical linearity correction and cross-talk remain
deferred. Noise/uncertainty and new fitting policies require scientific review.

Mac Intel is the current development/reference host. Preserve CentOS 7/Chapman
compatibility; Apple Silicon and Ubuntu coverage remain future work. Phase 3 is
a product-profile requirement. Work details and unresolved defects belong in
issues/PRs, not chronological additions to this roadmap.

## Shared configuration migration for bias and BPM/linearity

1. **Share TOML loading.** The caller supplies each path. The shared loader
   returns a typed document and its source path. Project and recipe readers
   interpret the fields and build named C structures for their callers.
   Preserve project composition, existing input formats, and provenance.
   Compare effective requests before changing the file layout.
2. **Share detector-profile reading.** Read the duplicated bias detector
   bindings from `wfi-1x1.toml` and `ocam-1x1.toml`, including explicit disabled
   detector status. Keep detector selection, detector-specific recipe parameters
   and calibration bindings with the recipe. Migrate separate native settings and
   processing profiles into their owning detector or recipe TOML. The native
   target is project TOML, detector TOML, recipe TOML and a classified `.list`.
   Retain support for existing formats during the transition.
3. **Qualify the migration.** Compare detector identities, configuration slots,
   FITS HDUs, calibration bindings, and effective settings against the qualified
   bias and BPM/linearity cases. Verify numerical equivalence. The owner will
   inspect all C files added or changed by the migration. Use descriptive names,
   consistent spacing, blank lines between logical steps, and properly hyphenated
   comments that explain intent, ownership, and scientific choices.

The four-file form is implemented for bias and BPM/linearity. Local checks
compare the complete effective settings of both WFI and OmegaCAM examples with
their checked-in baselines. Synthetic workflow checks cover compatibility and
execution with standalone settings files absent. Intel Mac production ASDF
and real-input qualification of the four-file form remain open.

Add ASDF configuration loading when a concrete input requires it. The
reduction-profile selector and dependency checker remain later work.

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
