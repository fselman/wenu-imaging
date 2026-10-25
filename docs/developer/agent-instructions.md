# wenu-imaging agent instructions

## Explain every functional and result-verification test, 25 October 2026

Fernando requires an explanation before every functional test and every test
that verifies results, including preflight checks, synthetic checks, installed
package checks, observational runs and read-only output checks. Give the
explanation before the command group or agent execution, not only when asked.
Keep it concise and specific to the test being proposed:

- State the purpose, inputs and settings, actions performed, and whether the
  test processes data, queries a service, writes outputs or only reads results.
- Name the actual Pycavi modules and subroutines/methods exercised, including
  relevant indirect calls and native programs. Distinguish production routines
  from orchestration and verification helpers; do not imply that a helper's
  independent calculation exercises a production implementation.
- State expected outputs, pass criteria and the test's limits. Distinguish
  wrapper completion, native execution, output integrity and scientific
  validation. Do not claim coverage of routines that the test does not call.
- After execution, explain what actually ran, what passed or failed, evidence
  and remaining limitations. Clearly identify checks still pending; a launch
  or zero wrapper exit code alone is not acceptance of the outputs.

These explanations do not authorize scientific tuning, broader validation,
extra processing or changes outside the currently approved task.

## Current authorized integration/cleanup, 24 October 2026

Fernando instructed merge and cleanup of the five qualified PRs #43, #45, #47,
#50 and #52. Integrate them into main in dependency order, retargeting stacked
PRs as their predecessors merge. Preserve all qualified heads/acceptance records;
verify every head is an ancestor and the final main tree equals the integrated
head. Cleanup only these merged branches with expected-tip and ancestry checks.
Obtain current actual chapman3 checkout evidence before local sync/cleanup and
provide guarded commands automatically. No reinstall, processing, query or
refit is required. This authorization does not close scientific/orchestration/
export/Mac gates or deferred #51; earlier handoffs below are historical.

## Current functional walkthrough handoff, 24 October 2026

The selected isolated OmegaCAM functional paths through notebook 09 passed:
baseline, Chebyshev and cubic Kriging applications, and twelve existing QC PNGs
across baseline/two corrected catalogues. Kriging QC records are in
notebook09-kriging-qc-saittxaz; all original/staged catalogue hashes remain
unchanged. #48 is closed after correction/installed/actual-copy evidence.
No independent scientific/model acceptance, complete notebook orchestration,
SkyMapper query, Mac qualification or Phase 3 compliance is claimed. #37/#38,
#51 and broader scientific/native/export gaps remain open. Preserve all inputs,
models, baseline and corrected outputs. PRs #43/#45/#47/#50/#52 are unmerged;
merging/cleanup needs the corresponding user instruction. Earlier handoffs below
are historical. Do not start a new implementation/refactor/query merely because
these selected functional checks passed.

## Current Kriging application coordinate correction, 24 October 2026

The existing before/after catalogue QC call generated and decoded all eight PNGs
without changing either source/staged catalogue (notebook09-qc-h6o98cy8). Address
#48 next: application axes must use the stored physical 1..ORIG_W/H endpoints,
actual grid shape and (y,x) orientation. Preserve cubic interpolation/default
solver, strict bounds, correction sign, null-safe writer and guards. No use of
the linear reader as a substitute, new model, refit or reference query. Test
source/installed behavior, then fresh target copies; keep #48 open until target
acceptance. #51 is deferred and does not affect the valid current QC inputs.
Earlier handoffs below are historical.

## Current notebook 09 QC handoff, 24 October 2026

Chebyshev application passed in notebook09-chebyshev-6xb3rgu1 with the existing
saved models: all expected magnitude changes, unchanged unrelated columns and
complete FITS extension metadata, 3718 exact IDs and 12741 missing masks, correct
provenance and byte-identical repeat calls. Baseline/model hashes are unchanged.
#49 is closed after source/installed and actual-copy evidence. Resume existing
catalogue QC on fresh staged baseline/corrected copies so fixed plot filenames
do not overwrite prior outputs. Keep current plot/reference settings and distinguish
functional generation from independent scientific acceptance. No new reference
query or fit; #48's separate Kriging application grid remains open. PRs #43/#45/
#47/#50 are unmerged. Earlier handoffs below are historical.

## Current notebook 09 baseline handoff, 24 October 2026

Baseline construction passed on chapman3 in notebook09-catalogue-95xc1kyz:
16459 paired-filter rows and 3718 distinct exact int64 Gaia associations, with
FITS null masks and all input hashes preserved. #46 is closed after correction,
installed tests and actual-output verification. Preserve baseline catalogue and
recovered references; continue functional correction only on fresh copies with
explicit saved models. Existing default Chebyshev application is distinct from
scientific model acceptance. Separate Kriging application coordinates fail at
valid edges (#48); do not treat corrected reader #41 as correcting that function.
PRs #43/#45/#47 remain unmerged; no new query, calibration, fitting or scientific
policy change. Earlier handoffs below are historical.

## Current catalogue handoff, 24 October 2026

#44 correction and bounded identity recovery passed chapman3 acceptance: four
raw/clean CSVs, zero coordinate differences, exact int64 CSV/Table/FITS round
trips, unchanged non-ID fields and original hashes. Resume notebook 09 with
fresh recovered catalogues under gaia-id-recovery-jh763zwi/recovered/catalogues;
do not replace historic calibration provenance or rerun calibration/models.
#41/#42 reader/08c checks also passed. PRs #43/#45 remain unmerged. Earlier
handoffs below are historical; independent science accuracy remains open.

## Current reader correction, 24 October 2026

Both 08b fits/grid serialization/QC passed. Target 08c diagnostics confirmed
#41 reader coordinate mapping errors despite exact saved grids; #42 records
misordered plotting arguments. Correct only reader axes and explicit plotting
bindings, preserving the linear method and immutable models. Verify existing
saved grids and fresh plots without refitting; keep #41/#42 open until target
verification. No science-image/catalogue correction, model/selection changes or
upgrades. Earlier dated handoffs below are historical; #37/#38 stay open.

## Current handoff, 24 October 2026

Fernando requested merging and cleaning the completed Chebyshev display work
before launching Kriging. #39 is closed after target plot/grid verification
without refitting. Notebook 08b imports/source identity and input selection
passed preflight: 583 r_SDSS and 580 NB_659 unique positions, no subsampling.
No variogram, Kriging fit or correction has run. Keep existing notebook settings
explicit, including its cleared clipping mask and four-pixel-offset diagnostic;
that diagnostic is not independent validation. Preserve all prior products and
leave #37/#38 and scientific accuracy/saturation investigations open.
The earlier dated handoffs below are historical.

## Current handoff, 23 October 2026

Both filters passed notebook 07 functional calibration checks on chapman3.
Fernando authorized merge/cleanup of completed branches, then a pause until
notebook 07b QC. Reuse the verified calibrated products and recorded queries;
do not rerun calibration. The r_SDSS saturation repair and installed writer
passed target verification (#33 closed). Keep #35/#36 scientific saturation
investigations, native #23/#24, independent accuracy and Mac qualification open.
The earlier walkthrough directions below record the agreed scope/history.

## Latest notebook walkthrough direction, 23 October 2026

Fernando declined the proposed standalone lunar/site-data check and explicitly
instructed continuing through the whole notebook sequence before deciding further
work. Resume the existing isolated OmegaCAM functional walkthrough at notebook
04, then SCAMP, SWarp and zpcal. Defer lunar/site-data to zpcal. This direction
supersedes the earlier requirement to close every dependency check before this
walkthrough; it does not accept the entire dependency baseline or authorize
general refactoring, replacement implementations or the systematic library/mefpp
audits. Preserve existing code/data/settings and use the established machine,
output-isolation and priority guards. Record actual results and resolve unexpected
failures before dependent stages. See the roadmap for the current boundary.

## Current approved metadata correction, 23 October 2026

Fernando approved the bounded Pycavi correction in #25: authoritative science
metadata at detector extraction/assembly, precise exposure endpoints, and
all-input coadd timing with total integration separate from native equivalent
exposure/gain. Preserve pixels, reuse solved WCS in fresh copies, and leave
native mefpp implementation (#23/#24) deferred. Continue the existing functional
notebook sequence through zpcal on chapman3, then retest on Mac. This supersedes
the older dependency-gate stop for this walkthrough; it does not authorize new
photometry functionality, broad refactoring or upgrades.

## Controlling dependency gate, 23 October 2026

Fernando clarified that dependency establishment and documentation on chapman3
come before the Pycavi workflow audit. Inventory Python packages, native engines,
resources, installation/build details, configuration, evidence and limitations.
Aim to align the Mac versions after capturing its actual imaging environment;
do not change either platform merely to force identical inventories. Diagnostic
wrappers calling existing functions are dependency evidence, not validation of
the complete orchestration or authorization to replace it. Keep the agreed
five-point sequence in roadmap.md. Future-proof Python only after those five
points are complete and the software works well, under a separately agreed plan.
The local Astrometry.net 0.98 installation was explicitly approved; this is not
blanket authorization for other engine or library upgrades. See the dated
chapman3 dependency inventory for current evidence and outstanding checks.

Status: accepted working agreement, with scope clarified by Fernando Selman on
20 October 2026. This is the canonical developer policy; the root AGENTS.md
directs agents here.

## Machine guards and process priority, 22 October 2026

### Actual user checkout verification, 23 October 2026

Before changing Git state or the installed wenu-imaging package on Fernando's
Mac or chapman3, inspect that computer's actual clone. Obtain fresh OS/hostname,
resolved checkout root, origin fetch/push URLs, branch, HEAD, upstream, full
`git status --porcelain` and interpreter/prefix evidence. Do this before fetch,
pull, switch, merge, reset, commit, push, cleanup or installation commands.
Do not substitute the agent workspace's state, yesterday's terminal output or a
directory name for this evidence. Use guards matching the established target;
preserve local edits and discuss unexpected branch/origin/divergence before
mutating it. A fetch changes Git references too. Do not assume the Mac imaging
clone is the separate Mac wenu clone. No Git software upgrade is authorized.

Fernando authorized the bounded remote-notebook launcher in
`Pycavi2/tools/start_remote_notebook.py` on 23 October. It starts the existing
chapman3 notebook workflow; it does not expand the reduction/refactoring scope.

Fernando develops on his Mac (wenu) and chapman3 (wenu-imaging) in parallel.
Every copy-and-paste command block must state its intended machine/project and
start with an automatic OS/hostname guard before any other work, including
environment activation, imports, Git operations, installs or file writes.
Do not rely on the displayed shell prompt or a previous block's successful check.
Group the block in a subshell so a guard failure stops that block without
closing the user's interactive terminal or SSH session.

For the current chapman3 imaging pilot, use this guard:

```bash
(
test "$(uname -s):$(hostname -s)" = "Linux:chapman3" || {
    echo "STOP: run this block on chapman3 for wenu-imaging." >&2
    exit 1
}
# Intended commands follow here.
)
```

The known Mac is MC02VV0HPHTDG (Darwin); the parallel wenu checkout is
`/Users/fselman/odrive/Dropbox/software/wenu`. The current chapman3 imaging
checkout is `$HOME/Software/wenu-imaging`. These are distinct projects. For
repository operations, additionally check the actual Git root, origin repository
and expected branch before modifying/fetching/installing; hostname alone cannot
distinguish checkouts. For Python processing, also check the resolved interpreter
prefix against the intended environment before scientific imports. The current
chapman3 prefix is `$HOME/.conda/envs/wenu-imaging`. Use the explicitly selected
target for future Mac imaging validation rather than requiring Linux for every
wenu-imaging task. Do not silently update a failed guard to match the current
terminal or infer the correct project from a directory's basename.

Future reduction launches must use `nice -n 10` on the Python parent so native
child processes inherit the lower CPU priority. Retain existing thread/resource
limits. Do not renice, restart or otherwise disturb an already running job
without instruction. The first pilot bias was already running when Fernando
requested this priority convention; it was left running as instructed.

Priority clarification approved 23 October: the Jupyter server and interactive
kernel run at normal niceness 0. Only batch processes and their descendants run
at niceness >=10. Launch scripts through `Pycavi2/tools/run_batch.py` in a
separate process, or use the existing `nice -n 10` terminal pattern. Never call
`os.nice`/`os.setpriority` in the interactive kernel to lower batch priority;
that also lowers later interaction. Direct heavy notebook-cell computations or
existing library calls do not automatically pass through the helper. Explicitly
launch those workloads in a batch process when using this priority split. Do not
claim all existing notebook runners were changed by this launcher utility.

These are instructions for preparing commands, not authorization for a new CLI,
host migration, workflow refactor or scheduler change.

## Packaging-stage authorization, 21 October 2026

Fernando authorized the packaging implementation, preserving the current
scientific dependencies and engines. **Any deviation from the roadmap must be
discussed with him and approved before proceeding.** Packaging validation does
not replace the later systematic Pycavi Python library audit or mefpp audit.
See installation.md for actual checks and pending platform gates.

### Bounded roadmap execution

Before implementation, identify the currently approved bounded task, its intended
result, scope limits, prerequisites and acceptance gate. A general "proceed"
applies to the task just discussed, not unmentioned stages or pending backlog.
If an extra item, new package/capability, scientific policy change, scope expansion
or changed order is needed, stop that affected implementation; read-only
assessment may continue. Discuss the concrete need, alternatives, consequences
and acceptance gate with Fernando, obtain explicit agreement and document the
agreed change in roadmap.md before implementing it. Keep proposals, partial
results and accepted completion distinct. Passing dependency checks does not
authorize starting the workflow audit. Routine choices and necessary fixes
inside the already approved boundary do not require repeated permission.

## Scope update, 21 October 2026

### Latest sequencing clarification

Fernando subsequently revised the proposed refactoring order:

1. Retire the historical `.py` reduction scripts; do not port their obsolete
   implementations. Streamline the notebooks using the existing libraries.
2. Once the notebook workflow is thin, provide runnable Python scripts driven
   by configuration files from that workflow, calling the same library routines.
3. Audit the library routines actually used by those notebooks systematically.
   Existing targeted fixes/tests do not establish that other routines are sound.
   Keep refactoring equivalence checks while thinning; the full scientific
   library audit follows the thin-notebook stage.
4. Audit mefpp after the Python-library audit. Read-only tracing of an existing
   native capability may inform the plan without starting the full C audit.

Keep packaging and Mac/Linux OmegaCAM execution as immediate prerequisites.
Postpone WFI implementation and dedicated validation until wenu-imaging works on
Mac and Linux. WFI remains a retained requirement; preserve its files/history and
record shared-code risks, but do not let WFI-specific work lead the current phase.
No Python/library/engine upgrades or backend replacements are authorized now.

BPM generation must be part of normal calibration creation, not permanently
defined as copying a static installed mask. Trace and validate the existing
mefpp construction path first, including required inputs, dependency order,
detector mapping, mask convention, thresholds, provenance and reuse rules.
Do not invent new BPM algorithms or silently change the working pilot products.

This clarification supersedes earlier suggestions to repair the legacy scripts
or begin implementation with WFI calibration preselection. Keep notebook/script
logic shared and preserve the single-node parallelism objective.

Fernando clarified the order of work after the portability audit:

- The immediate deliverable is properly packaged wenu-imaging with robust
  installed resources, explicit dependencies and reproducible installation.
  Debug and improve Pycavi before moving on to mefpp implementation.
- Do not upgrade Python libraries, Python itself, external astronomy engines,
  or replace backends in this stage. Prior modern-library probes are audit
  evidence only. Future compatibility means maintained interfaces, packaging,
  tests and recorded constraints now, with upgrades qualified separately later.
  Correctly declaring existing runtime imports is distinct from selecting a
  new library or upgrading the working environment.
- Audit single-chip CCD and CMOS requirements now, including primary-image and
  one-extension FITS layouts and detector-specific calibration/noise behavior.
  Audit findings do not establish implemented detector support.
- Audit every pipeline stage for single-node concurrency, aiming to parallelize
  every independent task where resource use and scientific dependencies permit.
  Cover exposure, detector, target/filter and independent QC work; coordinate
  outer processes and inner executable/BLAS threads within one node allocation.
- Dependency barriers and exclusive ownership of outputs remain mandatory.
  Joint fits and coadds may have parallel internals but cannot be replaced by
  independent per-frame results without preserving their scientific definition.
- Keep the present mefpp behavior for the packaging/Pycavi milestone. The later
  mefpp audit must consider both concurrent independent invocations and internal
  C parallelism rather than assuming one is automatically safe or sufficient.

This dated update controls the sequencing where earlier future-work paragraphs
differ. It does not authorize a broad rewrite, premature backend replacement,
archive submission or merging a proposal without instruction.

### Two user interfaces and WFI coverage

Fernando's intended design is thin, editable notebooks for learning and inspecting
data, plus Python scripts/configuration for repeatable headless processing. Both
must call the same library stage functions; do not maintain separate scientific
implementations or implement the script path by executing notebooks. Keep useful
parameter choices and inspection visible in notebooks. Retain WFI in the design,
but defer WFI implementation and validation as specified above, including its
calibration preselection, filter/metadata conventions and standards.
See [the two-interface review](pycavi-two-interface-review-2026-10-21.md).

## Purpose and scope

wenu-imaging coordinates Pycavi2 (Python), mefpp2 (ANSI C with embedded Eclipse),
and qfits52 (ANSI C FITS support) for WFI and OmegaCAM image reduction.
Maintain one canonical wenu-imaging repository containing the three components
as ordinary directories. Preserve the separate Python and C build/interface
boundaries; repository consolidation is not an algorithm rewrite.

The immediate delivery is a medium-sized OmegaCAM reduction set prepared for
submission as ESO Phase 3 science data products. Prioritize a reliable,
scientifically validated production path over new detector support or mefpp
parallelization. Data volume, filters and programme identifiers remain to be
inventoried; do not invent a size or throughput target.

The developer documentation and roadmap direction are accepted. The current
work is to record them and characterize the unchanged baseline. Documentation
in the parent repository may be maintained within the agreed scope. Changes to
component source, notebooks, scientific defaults, packaging, build scripts and component interfaces
require Fernando's explicit approval of an implementation stage. Publishing a
documentation proposal does not approve that stage. Do not merge a proposal
without instruction.

## Read first

- `docs/developer/architecture.md`: existing boundaries, baseline and open decisions.
- `docs/developer/roadmap.md`: platform requirements, phases and acceptance criteria.
- Any component-specific instructions before working inside a component directory.

Shared rules apply to work launched from this parent workspace. A component may
later need a concise local AGENTS.md for standalone work; creating those files
is a separate documentation change in the corresponding component directory.

## Platform priorities

- Urgent: macOS Intel and a Linux cluster whose distribution is pending.
- Required afterward: macOS Apple Silicon and Ubuntu Linux.
- The first identified machine runs macOS 13.7.8 (22H730), x86_64,
  Python 3.11.7 and Apple Clang 15.0.0 (clang-1500.1.0.2.5).
- These are requirements and reported environment facts, not validated support.
  Cluster distribution, scheduler, resource limits, Python/compiler versions
  and filesystem characteristics remain unknown. The execution model is confirmed:
  multiprocessing within a single node.

## Evidence and scientific preservation

Record exact repository commits, environment, commands and results. Distinguish
source observations, reproduced failures, inferred risks and open questions.
Do not describe syntax checks, skipped tests, an editable install or Linux-only
results as evidence of full installation, scientific correctness or macOS support.

Preserve algorithms, pixel units/precision, gain and exposure normalization,
FITS scaling and headers, extension/BPM mapping, calibration selection,
rejection thresholds, weights, photometric transformations and illumination
defaults unless separately approved. Record out-of-scope defects rather than
silently fixing them. Investigate unexpected numerical differences before
continuing dependent work.

Use immutable observational inputs and fresh output directories. Establish trusted
OmegaCAM reference products and comparison tolerances with Fernando first;
retain WFI regression coverage as changes affect shared code. Single-CCD and
single-CMOS support are future requirements, not established capabilities.
Never test by modifying original observational data or an existing working
installation. Builds and setup commands that generate files must use disposable
copies and a separate installation prefix during characterization.

## Minimal-change discipline

### Defect tickets, approved 23 October 2026

Open a GitHub issue for every distinct defect found. Search existing issues
first and update the matching ticket rather than duplicating it. Separate
confirmed failures, source findings and hypotheses. Record reproduction/evidence,
affected stage/platform, scope, acceptance criteria and relevant dependencies.
Link implementation commits/PRs to their tickets. An issue does not authorize
out-of-scope implementation or a change in scientific policy.

After correcting a defect, add a correction comment explaining the change,
commit/PR (or environmental remedy), tests and target verification actually
performed, and remaining limitations. Then close the ticket when its acceptance
criteria are met. Do not equate a written patch with target qualification, or
closure with a merged PR. Keep a native root-cause ticket open when only a
Python mitigation has been verified; link the separate mitigation ticket.
Retrospectively record defects corrected during the current walkthrough and
their existing evidence. Track subsequent findings the same way without asking
Fernando to repeat this authorization.

Trace and reuse existing functions before adding replacements. Prefer focused
refactoring and compatibility fixes. No broad rewrite, module relocation,
additional repository restructuring, workflow engine, build-system migration, dependency upgrade
campaign or unrelated cleanup without an explicit decision.

Treat repository names, Python distribution/import names, executables and C
library names as separate interfaces. The new parent name does not authorize
renaming `pycavi`, `mefpp`, qfits APIs or their installed resources.

External astronomy programs remain separately managed dependencies unless a
later decision changes that arrangement. Record and validate versions/paths;
do not vendor upstream source, download large index sets, or install system-wide
software as a side effect of an audit.

## Parallel processing and cluster work

The confirmed cluster model is multiprocessing within a single node. Distinguish
Python processes, threads inside external executables and the scheduler's
allocation. Multi-node/MPI support is outside the current scope. Do not assume a
scheduler brand, containers, root access or compute-node network access.

mefpp currently runs serially: it does not implement multiprocessing. Keep that
behavior for the initial operational OmegaCAM milestone. Do not introduce internal
parallelism or concurrent mefpp invocations merely because the pipeline supports
parallel astrometry. A mefpp multiprocessing design comes only after wenu-imaging
works correctly, with separate approval and equivalence/race/memory tests.

Once implementation is approved, respect allocated CPUs and memory rather than
the total resources visible on a node. Account for process-by-thread
oversubscription. Validate worker failure propagation, temporary/output path
isolation and restart behavior. Preserve scientific results when changing
concurrency. Record unknown cluster details without blocking independent Intel
Mac documentation and analysis.

## Git and review

Preserve attribution, license notices, history and unrelated local work. Use
focused branches. Inspect component status before checkout/update operations;
never discard local changes or overwrite an existing working installation.
The imported component histories remain available as ancestors of the monorepo.

After authorization, commit component changes in wenu-imaging. Cross-component
fixes may share a focused commit when they implement one agreed change.
The former component repositories remain historical references; do not push
ongoing development to them or to their original upstream projects.
Do not merge, delete branches, tag or release without instruction.

### Delivery handoff and local synchronization

These six rules were approved by Fernando on 23 October 2026, adapting the
applicable delivery procedure from `fselman/wenu` to this separate project.

1. **Automatic handoff.** After every push or merge, provide complete commands
   for synchronizing the applicable user computer, verifying its resulting
   commit and performing any authorized cleanup. Include this handoff without
   waiting for Fernando to ask. A pushed review branch and merged main require
   different commands; use the actual delivered ref and full expected SHA.
   When fresh local evidence is missing, provide the read-only preflight group
   immediately and explain which sync/cleanup group follows its review.
2. **Fresh target evidence.** Follow the existing actual-checkout verification
   rule before changing the user's clone or installation: hostname/OS, resolved
   checkout, origin fetch/push URLs, branch, HEAD, upstream, full working-tree
   status and Python environment. Never substitute agent-workspace evidence.
   Inspect returned output before dependent mutations and discuss unexpected
   differences. A failed guard is a stop, not permission to repair another host.
3. **Safe sync and authorized cleanup.** Use fast-forward updates and preserve
   local edits and unrelated branches. Verify ancestry before deleting an
   explicitly authorized merged branch; protect remote deletion against an
   unexpected changed tip. Do not force-reset, discard edits or delete branches
   just because a new task starts. Distinguish cleanup in the agent workspace,
   GitHub, chapman3 and Mac. Detect single-branch clones and explicitly fetch the
   delivered branch; explain any necessary change to their tracking configuration.
   If authentication fails, report the incomplete action without changing user
   credentials or requiring a graphical prompt/X11. Offer the applicable GitHub
   UI operation, then prune and verify after the user confirms completion.
4. **Complete command groups.** State the intended machine/project. Supply every
   command copy/paste ready in chat, with the OS/hostname guard first, exact
   verified checkout and applicable branch/SHA/clean/upstream checks. Use a
   subshell with fail-fast handling or equivalent dependent `&&` chaining; guard
   failure must stop the entire group without closing the user's terminal.
   Give one group at a time, then inspect its output before dependent operations.
   Respect normal notebook priority and lowered batch priority where applicable.
5. **Explicit delivery status.** Report branch/full commit or merge commit, PR,
   checks actually executed, remaining platform acceptance and any incomplete
   cleanup. Do not call written or unexecuted tests passing. Remote delivery
   does not synchronize the user's checkout, reinstall its wheel or update an
   already running kernel; state which of these actions actually occurred.
6. **Roadmap control.** Apply the bounded roadmap-execution rules above. Discuss
   and document changes of scope/order before implementation. Dependency
   qualification does not implicitly approve workflow refactoring, scientific
   changes or Python future-proofing. Publication of a plan is not acceptance
   of its pending implementation stages.

Use a dedicated branch and PR for the authorized item. Approval to implement
these instructions does not by itself authorize merging or deleting that new
branch; require the corresponding explicit instruction. Once a merge/cleanup
is explicitly authorized and its gates pass, do not request the same approval
again. Prefer the GitHub connector for repository delivery; user commands are
for their local synchronization/acceptance, not manual source editing on the
agent's behalf.

Report the problem addressed, changed files, checks actually run, unresolved
limitations and next decision. Keep working instructions and approved decisions
current as the project moves between phases.

## Delivery scope and future work

For the current OmegaCAM dataset, retain inputs and record processing versions,
configuration, calibrations, QC and product provenance. Scientific validation and
Phase 3 format/provenance validation are separate acceptance criteria. Verify the
applicable official ESO standard and validation tools when defining the exact
submission products; existing header-writing code alone proves no compliance.
Prepare a product inventory and release description. Archive submission and
publication remain actions requiring Fernando's explicit instruction.

After the operational OmegaCAM milestone, plan native mefpp multiprocessing and
support for single-CCD and single-CMOS reductions as separate work items. Audit
format assumptions and detector-specific calibration/noise behavior before
claiming single-detector support. Neither future item may delay the urgent
OmegaCAM production path without an explicit scope decision.
