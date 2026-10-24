# wenu-imaging

Defect tracking, approved 23 October 2026: create a GitHub issue for each
distinct defect found, checking for an existing ticket first. Record evidence,
scope and acceptance criteria; link the fix and verification in a correction
comment before closing it. Keep unresolved native causes and pending target
qualification open. See the canonical developer instructions.

Current task, 24 October 2026: notebook 09 baseline construction passed on
chapman3 (16459 paired rows, 3718 distinct exact Gaia IDs); #46 is closed after
installed/actual-output checks. Preserve the baseline and all inputs. Continue
functional illumination application only on fresh copies, with explicit saved
models and existing settings; no scientific model acceptance is implied.
Separate Kriging application coordinate defect #48 remains open. PRs #43/#45/#47
are unmerged; no calibration/refitting, new policy or dependency upgrades.

Latest scope, 23 October 2026: finish and document chapman3 dependency
qualification before the Pycavi workflow audit. Aim to align Mac versions where
practical. Python future-proofing follows the agreed five points, not this gate.
See the controlling dated updates in the developer instructions and roadmap.

Read and follow [the developer agent instructions](docs/developer/agent-instructions.md)
before work in this workspace or its component directories. Also read the
[architecture](docs/developer/architecture.md) and [roadmap](docs/developer/roadmap.md).

The immediate goal is an OmegaCAM reduction set for ESO Phase 3 submission.
Multiprocessing is within one node; mefpp remains serial for this milestone.
Component implementation changes require authorization for the relevant stage.

Before user-facing terminal commands, follow the machine/repository guards in
the developer instructions. Fernando works on Mac/wenu and chapman3/wenu-imaging
in parallel. Batch reduction launches must use niceness >=10; the interactive
Jupyter server/kernel stays at niceness 0 (23 October clarification).
Before changing either user's cloned wenu-imaging checkout or its installation,
obtain current Git/environment evidence from that actual computer; an agent's
checkout is not evidence of the user's local state. See the canonical policy.

After every push or merge, automatically provide the applicable complete,
guarded synchronization/verification commands and any authorized cleanup steps.
Give one command group at a time and inspect the user's result before dependent
operations. Distinguish agent-workspace, GitHub, chapman3 and Mac status; never
claim that remote delivery synchronized a user's clone. Follow the canonical
[delivery handoff rules](docs/developer/agent-instructions.md#delivery-handoff-and-local-synchronization).

The original audit is historical evidence, not the current agent policy.

Scope clarification, 21 October 2026: package wenu-imaging and debug/improve
Pycavi first; do not upgrade Python libraries or external engines yet. Audit
single-detector support and all opportunities for single-node parallel work.
mefpp implementation follows the Pycavi milestone. See the dated scope update
in the developer instructions and roadmap.
