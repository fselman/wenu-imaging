# Working on wenu-imaging

## Scope and current state

Pycavi coordinates astronomical reduction; mefpp performs native processing with
bundled qfits/Eclipse. Work in this monorepo, not the historical component repos.
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
Pycavi admits historical metadata, authors frozen bindings, invokes one native
recipe and independently reads its products. Select either the native_recipe
TOML form or the retained per-stage form, never both. Native recipe selection
requires its own Mac ASDF/ownership gate and comparison with the CCD65 pilot.
An explicit assembly section selects the reference detector for final MEF/QC. Final assembly
passed the synthetic Mac gate at 6f3eaaf. The per-stage CCD65 pilot passed exact
saved-product checks and visual plot inspection; the new in-process recipe is
not yet Mac-qualified or selected. Historical calibrations may be bound to byte-identical copies under
reduced/cal through explicit recipe source/path/SHA256 entries. Preserve original
ASDF/handoff records and verify copied bytes against their frozen fingerprints. Reuse the existing
numerical services and recipe directory contract.
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
The migration is pending; see the required detector flow in
docs/developer/design/common-recipe-coordinator-v1.md. Preserve stopped run
native-32-wm3xnsso (26 completed detectors; CCD87 preparation saved). Do not relax
pair-quality criteria or repeat completed detector work to bypass the failure.

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

Keep very few concise permanent documents. Maintain current guides, not a diary.
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
redeclaring raw, calibration, output, work or log roots. Reuse the existing project
composition reader and its relative-path rules. The project TOML resides in
orchestration, output maps to reduced, and calibration/work/logs remain below it.
Run recipe tests with their working directory in orchestration. Keep configurations,
lists and requests there, observational inputs in raw, and products, logs, private
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
