# Run provenance and evidence retention

Agreed with Fernando Selman, 26 October 2026. Applies to wenu-imaging on the
Mac and Chapman3. The separate wenu project and ~/wenu-output are outside scope.

## Directory ownership and provenance

Create new build, test and qualification work under
~/Software/build/wenu-imaging/<task>/, never directly under the home directory.
Each newly created build, test or generated-output directory must contain
run-provenance.json. Nested run directories may reference a shared parent
manifest for common details, but each has its own record identifying its role
and tested source. Do not add files to original observational input directories.

Write provenance when creating the directory, before running its workload.
Update status atomically on completion/failure; an interrupted run stays
incomplete or running until reconciled. Preserve previous attempts instead of
overwriting their evidence.

Record schema_version, project/repository identity, run ID, directory role,
purpose, UTC creation/update times, host/platform, commands, status, retention
role, related directories, and input/output identities or linked manifests.
For each tested component record repository, branch, exact commit, dirty state
and any patch/source-snapshot identity needed to reproduce uncommitted sources.
Keep the orchestration checkout distinct from the actually tested installed
payload or exported source. Record installed engine/module hashes and native
build manifests where relevant. A branch name alone is insufficient.

Use null plus an explanation for unavailable historical branch/commit/dirty
state. Never infer a historical branch from the current checkout. Record a
detached HEAD explicitly. External dependencies without Git identity use a
version, source/archive hash and build options; do not invent a branch for SCAMP.
Do not store credentials or unrelated private configuration in provenance.

Status values: running, passed, failed, incomplete.
Retention roles: disposable, acceptance_evidence, active_installation,
unique_data. Multiple roles are permitted. An active installation cannot become
disposable merely because its development branch merged.

For historical directories, add a separately identified retrospective record
only from recoverable evidence. Preserve existing records and their original
paths, linking relocation journals. Do not claim that missing provenance was
known at run time.

## Evidence preservation is a merge gate

Before requesting or performing merge, review each associated run directory:
identify unique data, required acceptance evidence, active installations and
other consumers. Commit a reviewed acceptance summary, relevant commands and
provenance, limitations, and the useful machine-readable test reports to the
branch. Retain enough detail to inspect what actually passed and reproduce the
test; a terminal PASS label or PR conversation alone is not the durable record.
Distinguish user-returned evidence from files directly inspected by the agent.

Keep large FITS products, raw observational data and unsuitable/private binary
content outside Git. Commit a manifest with identities, sizes, cryptographic
hashes, stable retained locations, retention responsibility and reproduction
instructions. Verify the retained copies before accepting the gate. A manifest
pointing only to the temporary directory being deleted does not preserve data.
Do not put an entire temporary tree into Git as a substitute for reviewing it.
If required material remains unpreserved, keep the branch/PR open and record the
specific gap; do not merge first and plan to recover the evidence later.

After integration, verify that main contains the evidence records and required
commits (or reviewed equivalent content for a squash) before deleting the branch.
Merge, branch deletion and data-directory deletion remain distinct authorized
actions. These rules do not authorize automatic merge or deletion.

## Directory cleanup after integration

A merged branch marks associated directories as candidates for review, not safe
to delete automatically. Recheck provenance, preservation of unique data and
required evidence, selected executable/module/resource paths, open files and
active consumers. Retained scientific inputs and accepted final products are
not branch-scoped disposable output. Do not interrupt jobs or remove working
installations for cleanup.

Record the cleanup decision, preservation references and exact directory list.
Prefer reversible archival relocation first; retain original-to-new path maps.
Absolute paths in CMake trees, virtual environments or compiled resources may
prevent execution after relocation. Verify relocated runtime payloads separately
and use fresh directories for future builds. Permanent reusable installations
may use ~/opt/<versioned-name>/, with their build/evidence under the imaging root.

This policy does not certify retrospective evidence completeness or authorize
backfilling every old directory without inspecting its records.
