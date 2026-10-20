# Repository consolidation

The initial wenu-imaging repository used three Git submodules. The migration
replaces those references with ordinary source directories at the same names:
Pycavi2, mefpp2 and qfits52. No algorithms, filenames or build interfaces are changed.

Each selected component history is merged without squashing. The merge commit
has the original component commit as an ancestor, retaining its original author,
committer, message and commit identity. The component tree is inserted under its
new directory and checked for exact Git tree equality. Historical files retain
their original paths in old commits; following a file's history across the import
may require inspecting the original component commit directly.

The selected versions are the audited main-branch commits recorded in
architecture.md. Other branches and tag names are not imported. They remain in
the original repositories, which must be retained until separately reviewed.
No original repository is deleted, archived, rewritten or pushed to by the script.

The migration runs in a fresh sibling checkout on refactor/monorepo-import.
Existing Mac clones and their uncommitted or unpushed work are not imported or
modified. Any such work must be reviewed separately before removing old clones.
The script's optional push publishes only the new migration branch, not main.

Verification covers commit ancestry, directory tree equality, absence of remaining
gitlinks and clean status. These checks prove repository migration properties;
they do not prove that the software builds, runs or produces correct reductions.
The developer documentation includes the original audit unchanged and records
single-node pipeline multiprocessing, serial mefpp and the immediate OmegaCAM
Phase 3 milestone. Later work includes mefpp multiprocessing and single CCD/CMOS.

Review the migration before merging. Use a normal merge or fast-forward merge.
Do not squash or rebase this migration: that would discard or rewrite the imported
history. After merging, use a fresh ordinary clone without recursive submodules.
Switching the old populated submodule checkout directly to the monorepo can leave
nested Git metadata and should be avoided until it is separately cleaned safely.

A future release may archive the original component repositories once history,
release references and any unpushed local work have been reviewed. Deletion is
not required to operate or distribute the monorepo.
