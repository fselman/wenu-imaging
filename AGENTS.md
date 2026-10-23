# wenu-imaging

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

The original audit is historical evidence, not the current agent policy.

Scope clarification, 21 October 2026: package wenu-imaging and debug/improve
Pycavi first; do not upgrade Python libraries or external engines yet. Audit
single-detector support and all opportunities for single-node parallel work.
mefpp implementation follows the Pycavi milestone. See the dated scope update
in the developer instructions and roadmap.
