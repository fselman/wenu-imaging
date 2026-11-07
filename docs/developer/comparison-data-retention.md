# Comparison data retention

Owner instruction, 3 November 2026: data needed for future comparisons must not
remain in build directories. On the Mac, store it in appropriately named
subdirectories of:

- ~/Pictures/OCAM/wenu-imaging/
- ~/Pictures/WFI/wenu-imaging/

Every retained dataset subdirectory must contain a README.md explaining why it is
needed and when it can be erased. Apply this rule to new work and when relocating
existing retained comparison products.

## Naming and contents

Use a name identifying the purpose and observation or creation date, with a
revision/run qualifier when necessary. For example:
~/Pictures/OCAM/wenu-imaging/2017-03-13-cppup-large-file-baseline-<revision>/.
Do not overwrite a different baseline merely because filenames coincide.

Keep the comparison images/calibrations and the metadata needed to interpret
them together. Record original locations and relevant source revisions, commands,
configuration, input identities and reports. Retain accompanying ASDF files and
their required relative-reference layout. Update active consumers to the new
location; document historical build paths rather than silently rewriting evidence.

Build directories hold compilation output and disposable test intermediates.
Before declaring a build directory disposable, extract any data still needed for
comparison to the appropriate instrument directory. Raw observations retain their
existing locations; this rule does not authorize deleting or relocating them.
Installed engines and private Python environments are runtime dependencies, not
comparison datasets; do not discard them as part of a comparison-data move.

## Required dataset README

Each README must state:

1. Purpose: the specific comparison or validation requiring these files.
2. Contents: instrument, target, observation date, processing stage, provenance
   and which files are the reference.
3. Dependencies: scripts/notebooks/reports using the dataset and required
   companion calibrations or ASDF references.
4. Deletion condition: a concrete completion/supersession condition, linked to
   the relevant ticket, acceptance receipt or replacement dataset when available.
5. Current status and last review date, including whether the deletion condition
   has been met.

If the deletion condition is not yet known, state that explicitly and identify
the unresolved comparison; do not treat age or presence under a build path as
proof that needed data can be discarded.

## Existing data requiring relocation review

The current Mac work retains earlier comparison products under build directories,
including the stage-2 pilot, pre-large-file reference/comparison reductions and
the owner-inspected WFI master-bias products. Inventory their live dependencies,
choose descriptive instrument destinations, add the required READMEs and update
active references before considering their former build directories disposable.
This note records the rule and pending relocation; no Mac files have been moved
by this documentation change.
