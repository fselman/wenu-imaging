# Working on wenu-imaging

## Scope and current state

mefpp provides standalone native recipes with bundled qfits/Eclipse.
Pycavi is an optional workflow client, not a recipe runtime dependency. Work in this monorepo, not the historical component repos.
Use C17 for current native development. Intel Mac is the current qualification
host; retain CentOS 7/Chapman compatibility. Do not upgrade dependencies implicitly.

The owner accepted and selected the Mac-qualified bias producer
ecf41ea347a20058c7eab435eb9d6fb10b5be02f (PRs #300/#301/#303), binary SHA256
3c28e637a07cfa05ec83e18d238115c73e1b77b305b4ed0bf62d2d033e7cdacd.
Both WFI/OCAM launchers select main-bias-jk_5noln/mefpp_bias_recipe under the
retained mac-standalone-bias-SP3Cgdhb build root, with full QC and MAD off.
Preserve the previous 36381892 executable/cache and the b833aca7 backup.
Native BPM and linearity preparation publish through the shared C ASDF writer.
The native BPM/linearity recipe mirrors the bias lifecycle and calls the
existing preparation/BPM services in process, then joins their final MEF/QC.
The feature branch now implements direct native schema-2 TOML admission and the
shared command catalogue. Historical schema-1 compatibility remains available;
external binding compilation is not a prerequisite for the new public command.
The complete synthetic Mac gate passed for native producer
61b95c1ebdbdef988bf202ed33bd8403455a398a: direct TOML admission/default indices,
identity guards, shared-cube ownership, both QC modes, supplied-mask skip,
robust BPM creation, native ASDF and independent saved readers. The earlier
cec9626 supplied-mask/QC-off direct CLI CCD65 run matches the retained reference
in all five decoded measurement groups, with 32 image loads/30 corrections.
The earlier no-mask CCD65 run passed saved-product checks and owner Viewer inspection.
The classified-list and fresh-project workflows passed for WFI and OCAM on
Mac. The four-file configuration migration remains open. Keep the accepted
bias producer and active controls unchanged until selection. Record comparison
summaries in PR #305.
An explicit assembly section selects the reference detector for final MEF/QC.
Historical calibrations may be bound to byte-identical copies under reduced/cal;
preserve original ASDF/handoff lineage and verify copied bytes against frozen
fingerprints. Reuse the existing numerical services and directory contract.
CCD68/90 residual investigation and the viewer Update service remain deferred.
Linearity characterization is measurement only for now; do not apply a linearity
correction. Cross-talk characterization and correction remain deferred. Keep the admitted
prior mask fixed while characterizing a candidate BPM. Hash shared image inputs
at batch boundaries, with per-stage identity checks; do not repeat full-MEF
image hashing for every detector. Real batch execution uses niceness >=10.
Work summaries and completed changes are recorded in GitHub issues and PRs.

The owner has superseded the current two-pass BPM/linearity execution: ingest and
correct each detector image plane once into one owned processed cube; optionally
create/publish its robust-fit BPM and measured QC; then measure linearity/ROIs
from that same cube before release. Raw-only evidence is captured during ingestion.
Downstream services borrow processed planes without input I/O or reprocessing.
Supplied-mask and omitted-mask synthetic paths passed native Mac ASDF checks;
the earlier no-mask CCD65 path also passed independent saved-product and Viewer checks.
The revised classified-list interface still needs its Mac gate. A supplied BPM skips creation and logs the reason. `--qc true/false`
overrides the recipe boolean (default true); false suppresses optional BPM
full-frame QC and MAD without disabling requested linearity measurements.
Native schema 2 requires each detector to declare an input BPM calibration path
or `omitted`. Historical schema 1 retains `[preparation] input_bpm=archived` or
`omitted` compatibility. Omission enables BPM creation while preserving historical
archive and master lineage. Previously admitted direct samples stay exact;
newly admitted samples are reported separately. Do not rewrite archived QC or
claim unchanged ROI populations after mask omission.
Full-file preservation hashing still reads shared inputs before and after the
batch; do not claim total read-once disk I/O. See the detector flow in
docs/developer/design/common-recipe-coordinator-v1.md. Preserve agreed
pair-quality criteria when diagnosing failures.

## Before proposing or changing work

Read this file, docs/developer/architecture.md and docs/developer/roadmap.md before
proposing or implementing a project change. Read the affected recipe's design and
guide as well. Check these against the owner's decisions in the current session;
resolve superseded/conflicting text explicitly rather than treating it as authority
to change the agreed model. Update current documents together when decisions change.

## Native recipe interface

mefpp user documentation and usage messages describe native Unix commands only.
A recipe must be runnable directly from its TOML, following the bias example;
no external interpreter, orchestration package or generated-bindings prerequisite
may be required of the user. Do not hide an implementation dependency by renaming
its launcher or merely removing documentation. Native schema-2 admission reads
the recipe directly; retain the historical binding compiler only for compatibility.
Qualify the new native interface before acceptance. Keep orchestration-specific implementation
and test details in their own component documentation.

The public call is `mefpp_recipe cal bpm-linearity --config RECIPE.toml`.
Use the same native command family for bias and linearity. Required help levels:
`mefpp --help`, `mefpp_recipe cal --help`, and
`mefpp_recipe cal OPERATION --help` for `bias`, `linearity` and `bpm-linearity`.
Help must succeed without configuration or observations and describe supported
options, defaults, inputs and outputs. Do not show `nice` in the guides. Preserve
accepted executables/producer identities as compatibility aliases during migration;
never present the unified interface as complete before it is implemented and tested.

The shared command reserves a place for every existing recipe, including those
not yet migrated. Its shape is `mefpp_recipe CATEGORY OPERATION`; categories
currently include `cal` and `sci`. Maintain one native catalogue for dispatch and
help, covering every operation in `mef_runtime.h`. Pending entries are labelled
and refuse execution without processing. Adding a catalogue entry does not
authorize porting that recipe or changing its science.

Develop and validate the individual recipes before implementing the shared
dependency checker. Finish BPM/linearity first; a catalogue entry does not
authorize dependency orchestration. Individual recipes validate their direct
inputs and report absent prerequisites without launching additional recipes.
The later checker applies to every required calibration: reuse a compatible
reduced product or plan its reduction from an explicit input list. Resolve all
requirements, report all missing products/lists, and obtain permission for the
complete additional reduction plan before execution. See the deferred dependency
contract in docs/developer/architecture.md. The MFF entry remains pending.

## Human-readable implementation

Write for a programmer who understands scientific data processing. Use meaningful
names, visible processing order, ordinary control flow and logical spacing.
High-level recipes should normally fit two readable pages and at most three;
call focused subroutines and reuse the common recipe lifecycle. Do not hide a
whole long recipe in one opaque helper. Put blank lines around standalone
explanatory comments. Use few comments: explain intent, contracts and scientific
choices rather than restating code. Keep a few stable scientific-stage landmarks,
unique in source and mapped by file/routine/ID in the mathematical guide.
Recipe-specific C filenames, helper symbols and types omit redundant `_recipe`.
Mathematical guides begin with a concise executive summary before technical detail.

Source must not cite temporary development steps or build-stage documents.
Use technical explanations, immutable design revisions or GitHub issues. Preserve
compatibility-sensitive command names and stored producer identifiers until an
explicit migration is agreed. Human comprehension is part of acceptance.

## Science and documentation

Agree new scientific algorithms/policies before implementation, with a concise
reviewed design. Maintain the resulting mathematical explanation in LaTeX and PDF,
including equations, nontrivial references and source mapping. Preserve accepted
estimators, populations, units, masks, geometry and evaluation order unless a
scientific change is explicitly approved. Bias/QC measurements remain in ADU.

Maintain one concise canonical guide per recipe, named after the recipe:
`docs/developer/bpm-linearity-guide.tex` and matching PDF for `cal bpm-linearity`.
Keep current recipe explanations there. Existing saved-data analysis and future
model guides remain separate for now; their eventual consolidation is deferred. Keep the documentation index and source
links aligned. Keep very few permanent documents; maintain current guides, not a diary.
Use issue/PR summaries for the problem, decision, correction and validation.
Do not add dated work reports, per-attempt documents, handoffs or log collections
to docs. Remove obsolete material; complete historical reconstruction is not a
requirement. Agent instructions belong here, without duplicate chronological rules.

## Proportionate testing

Follow [recipe acceptance](docs/acceptance.md). The primary suite is small and
organized by recipe, using representative real data and agreed reference products
for supported instruments. A few full-chain cases check recipe integration.
Routine changes run affected recipe cases; installation acceptance runs the
complete primary suite. Compare pixels, FITS structure/mapping/headers, ASDF QC
and provenance with explicit agreed tolerances and permitted metadata differences.
Preserve the designated legacy reductions as comparison references. Keep fresh
test products and logs only through comparison or active diagnosis. Record a
concise comparison summary in the PR. Remove superseded test workspaces once
the references are secured and the results recorded.

Do not automatically add a regression test for every small bug. Retain selective,
cheap checks for important numerical behavior, mapping, ownership or destructive
failure paths when primary cases would miss them. Avoid tests that mirror the
implementation. Explain the purpose, actual inputs/routines and pass criteria
before a functional run. Distinguish implemented coverage from planned coverage,
synthetic from real-data checks, and prepared commands from observed success.

## Safe execution and delivery

Raw observations are read-only. Keep raw, orchestration and product directories
separate; use fresh output directories and preserve accepted reference products.
Project TOML owns shared directory roots; recipes reference it rather than
redeclaring raw, calibration, output, work or log roots. Native project admission
must preserve the shared composition contract and its relative-path rules; an
optional client must not be required to resolve the project first. The project TOML resides in
orchestration, output maps to reduced, and calibration/work/logs remain below it.
Run recipe tests with their working directory in orchestration. Keep configurations and requests there, observational inputs in raw, and
products, logs, private
working files and execution receipts under reduced. Existing calibrations are
read-only dependencies under reduced/cal. Apply the same layout to synthetic
file-integration fixtures; pure in-memory numerical checks need no directory tree.
Do not overwrite an installation or switch the selected engine without instruction.
Reuse the selected build/toolchain/cache; no routine fresh export, reconfigure,
dependency installation or replay of unchanged qualification matrices.

Before changing a user's checkout/build, obtain fresh actual-host evidence:
host/OS, resolved checkout, origin, branch/HEAD/upstream, working-tree status and
Python environment. Inspect it before dependent changes. Commands must form one
copyable, fail-fast subshell, guarded by actual host/path/ref/state. Give one group
at a time and inspect the output. Never discard edits or force-reset a checkout.

Use focused branches/PRs; do not merge, delete branches, tag or release without
owner instruction. Preserve attribution and licenses. Prefer the GitHub connector
for delivery. PRs and chat must state purpose, changes, checks actually passed,
limitations and next step. After remote delivery, provide exact guarded user-sync
commands; when actual-host state is missing, give read-only preflight first.

Do not alter scientific inputs/results, approved baselines or comparison tolerances
as a way to make a failing test pass. Investigate unexpected numerical differences
before continuing dependent work. Do not claim unsupported platform/science status.

## Four-file native configuration and shared processing lists

Follow the [four-file architecture](docs/developer/architecture.md#four-file-native-configuration):
project TOML for identity and roots, detector TOML for shared detector definitions
and enabled or disabled status, recipe TOML for processing choices, and a
classified observation list. Use `wfi-1x1.toml` and `ocam-1x1.toml`. Keep disabled
detectors in the catalogue. Recipe detector sections hold recipe-specific
parameters and calibration overrides. Migrate separate settings and processing
profiles into their owning files without changing effective settings.

The recipe references an absolute path in `inputs.list`. Each `.list` row has an
absolute FITS path, a tab, and `DPR.TYPE`. The list directory is configurable.
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
