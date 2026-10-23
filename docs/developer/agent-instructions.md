# wenu-imaging agent instructions

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
