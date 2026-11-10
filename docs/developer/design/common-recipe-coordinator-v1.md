# Common native recipe coordinator

## Public command and admission

The entry point is `mefpp_recipe cal bpm-linearity --config RECIPE.toml`, following
the bias template. The native command reads the recipe, referenced project and
settings, ordered observations, calibration bindings and detector mappings itself.
No external preparation command or generated-bindings prerequisite is exposed to
the user. Historical sample archives are comparison/provenance evidence; the
current external archive-to-bindings compiler is not the final native interface.
Do not disguise that dependency behind a renamed launcher.

Help follows `mefpp --help`, `mefpp_recipe cal --help`, and operation-specific
`mefpp_recipe cal OPERATION --help` for `bias`, `linearity` and `bpm-linearity`.
Help performs no data processing, requires no files and reports inputs, options,
defaults and outputs. Guides contain concise native Unix commands without `nice`.
Project TOML owns directory roots. Recipes reference it and select operations,
controls and inputs without redeclaring raw/reduced roots.

## Required BPM/linearity detector flow

The shared-cube source is owner-accepted. Its supplied-mask path has Mac ASDF
and exact CCD65 comparison evidence; explicit archived-mask omission and new
controls retain their separate qualification requirements. The standalone command
interface remains unfinished.

1. Admit ordered input identities, geometry, fixed calibrations and requested steps.
2. Read each required detector image plane once. Capture requested raw-only QC,
   scan traces and saturation/nonfinite validity during ingestion. Apply row scan
   correction, bias subtraction when applicable and trimming exactly once, with
   the existing arithmetic and rounding. Store the active images in one owned
   processed cube, retaining original frame/pair/HDU mappings.
3. If an input BPM is supplied, skip BPM creation and log `input_bpm_supplied`.
   Otherwise borrow the cube for robust response fitting and candidate BPM
   creation. Publish the detector BPM FITS and measured QC ASDF.
4. Borrow that same unmodified cube for linearity curves, ROI, pair-difference
   and direct-site measurements. Publish their native ASDF and provenance.
5. Release the cube after all requested detector steps; continue to the next
   detector. Final MEFs are assembled from saved detector products.

The detector coordinator owns the cube; calculation services borrow it. Neither
service reopens input images or repeats correction. Corrected-image disk staging
is not a substitute for sharing the cube. Load calibrations once per detector;
do not reload reference biases per flat pair. Reusing the existing file adapters
unchanged cannot satisfy this contract.

Raw-only evidence must be retained before it is lost. The implementation keeps raw
flats and two reference biases until pair measurements finish; other bias planes
are released after their traces are captured. Preserve the established
common raw four-plane population for pair statistics and the distinct direct-site
population. Do not silently drop raw QC or change its membership. Fingerprinting should eventually share ingestion reads. Currently one full-file
SHA256 pass before and after the batch remains for content-preservation evidence.
Therefore only numerical image ingestion/correction is read-once qualified;
total disk I/O is not. Do not remove preservation checks or claim otherwise.

Pair consistency, signal span and scientific suitability are recorded analysis
assessments. They must not erase measured evidence or stop the remaining detector
measurements. Structural/I/O failures remain processing errors. The 2% criterion
is unchanged; no automatic new fitting population is introduced. A candidate
failing suitability criteria is not an accepted calibration.

The new BPM is an output. Preserve the admitted prior mask for measurement
populations until an explicit alternative ROI mask policy is selected. BPM
creation is optional and does not control availability of linearity measurements.

Qualification must count actual selected-plane loads and corrections, prove one
ingest/correction per input, compare cube values and measurements with references,
and cover BPM requested/omitted and unsuitable-pair cases. Preserve the 26 completed
detector products and CCD87 preparation from the stopped 32-detector run.

Recipe `[preparation] input_bpm` explicitly selects `archived` (default) or
`omitted`. The latter omits only the current input mask and triggers candidate
creation, without modifying the archived samples, master or its historical mask
lineage. The processing TOML's mask encoding describes supplied masks; explicit
recipe omission does not alter other processing settings. Drop unused mask-copy
bindings from that recipe. Exclude the omitted mask from current payload loads
and integrity dependencies, while retaining the frozen historical QC graph.

Saved reading validates the effective selection against that graph and declared
policy. With omission, ROI populations can change; do not claim exact historical
ROI replay. Previously admitted direct-site values must remain exact. Newly
admitted sites are decoded from current native transports and reported separately,
never replaced with old unavailable values. Source archives remain unchanged.

The `qc` recipe boolean defaults to true; trailing `--qc true/false` overrides it.
False disables optional BPM full-frame diagnostics and MAD, while preserving
requested ROI means/variances, pair/direct-site measurements and provenance.
Supplied calibrations remain fixed. The historical archive admission currently
requires a verified master bias; absence is not replaced with an invented zero
calibration. All-supplied-mask runs publish measurement ASDFs and no BPM MEF.

## Shared structure and implementation boundary

Use the [common template](../native-operation-recipe-template.md) and accepted
bias entry point: initialize/start, prepare/admit/begin, detector loop,
verify/publish/complete, finish/destroy. Keep the recipe readable in two pages,
at most three, with meaningful calls and spaced comments. Supporting modules
expose mechanics rather than hiding the whole processing flow in one helper.
`mef_recipe_run` owns shared run resources; typed operation state owns inputs
and results. Services retain validate/load/calculate/optional-publish/cleanup.

The public command dispatcher only selects an operation. It must not replace
scientific services with a generic callback framework or route detector steps
through external commands. The inner calculations, fixed prior populations,
rounding, masks and native ASDF writer remain unchanged during interface work.
Bias needs no cross-detector balancing; later collective recipes may need it.

The generated-bindings requirement and operation-specific executable names in
the feature branch are implementation gaps. Complete native recipe-only admission
and the public command/help hierarchy before standalone OCAM/WFI acceptance.
Keep accepted installations and compatibility identities intact. Source review,
focused numerical/ownership/ASDF checks and the owner's terminal-run acceptance
are distinct gates. Directory reorganization remains deferred.
