# M2 reusable project and native configuration composition

30 October 2026. Owner accepted/merged the cumulative review (PR #156,
`ea35197a7f074ac1c44289e7bcc94336f92d6681`) and instructed “merge, clean, and
proceed”. This increment addresses the original M2 integration gap in
[#155](https://github.com/fselman/wenu-imaging/issues/155). It does not start M3.

## One effective configuration

`ConfigurationMigration.load_project` and the existing `freeze-project` CLI now
compose project declarations and call the qualified native resolver on the selected
native configuration. That native reference may be complete, split, or a local
override entry. The previous single-native-file restriction remains in the old
standalone authoring helper, not in the integrated configuration path.

The integrated loader reuses the existing closed authoring catalog and semantic
checks. It validates each local domain's shape before merging, then validates the
complete effective project, profile identities and readout declarations. Native
values, units, coverage and allowed numeric overrides come exclusively from the
existing C reader. The existing readout consistency helper receives a complete
typed view serialized from the **resolved stored native values**, rather than
requiring a complete textual native source file. It still rejects mismatched
geometry or subtraction flags; removing that check is not the integration fix.

All native C source/header files, parser sources, numerical operations and installed
selections are unchanged. The normal engine remains opt-in-independent. CMake only
adds a configuration test; no build/install/ABI target boundary changes.

## Versioned project entry and subsets

Complete project schema version 1 remains supported without project includes.
Project composition envelope version 2 adds one optional `include` array:

```toml
project_schema_version = 2
include = ["../shared/profiles.toml", "instrument.toml"]

[project]
schema_version = 1
id = "review-project:example"
name = "example"
# The complete project domain, including roots, is supplied here or by a subset.
```

Each included project subset has `project_schema_version=2` and may contain zero
or more **complete** domain declarations, plus its own includes. A complete
version-2 file with no includes also works. All domains retain their accepted
schema version 1; the normalized effective authoring view therefore retains
`project_schema_version=1`. Original composition envelope versions remain in
source records. Project envelope versions are distinct from native TOML versions
1/2/3, which remain interpreted by the native reader.

The domains are project, association, reduction_profile, recipe, execution,
quality, product_profile, processing and readout. Several reusable domains can
share one file. There is no eight-file requirement. A partial domain/table merge
is not supported: choose a complete domain subset explicitly.

## Deterministic conflict and path rules

1. Resolve the entry once; each include is relative to its resolved containing
   file (or an explicit absolute path). Symlink aliases use the actual resolved
   source directory, consistent with the existing native/authoring rules. No cwd
   change, environment expansion, glob, calibration discovery or root creation.
2. Only disjoint or identical project-domain definitions may compose. Identical
   definitions coalesce, retaining all contributors and the first equivalent
   origin. Changing include order cannot choose a different effective value.
3. A conflicting project domain fails and names both sources. Project-domain
   override allowlist is explicitly **empty** in this version. Choose one explicit
   domain subset; there is no last-wins or implicit recursive dictionary merge.
4. Identical path-bearing text is compared in its declared scope. Two processing
   blocks referencing `native.toml` from different directories are a conflict if
   they resolve to different native files. Project roots similarly retain the
   directory of the file that declares the project domain, not the entry/caller.
   Raw spellings remain recoverable in the exact source text.
5. The native configuration has its existing explicit numeric override allowlist,
   source history and conflict policy. The project layer neither changes that
   policy nor implements a second numeric/default parser.
6. Unknown envelope/domain fields, unsupported versions, wrong types, duplicate
   include spellings, missing files/domains, semantic conflicts, cycles and resource
   limits fail. Bounds are 4 MiB per source, 64 unique project files, depth below 16
   and at most 64 includes per file. Native graph bounds remain unchanged.

## Frozen values and provenance

The resulting `FrozenConfiguration` is the same shared record used by CLI and
library requests. Its project snapshot now uses notation
`wenu-project-configuration-snapshot-2` and retains:

- the normalized effective domain declarations and resolved roots;
- exact text and SHA256 for every contributing project **and** native file;
- original and resolved include edges, per-file definitions and envelope versions;
- selected project-domain origins, source hashes and all identical contributors;
- the complete native per-field sources, units, override declarations and graph;
- separate purpose, ordered recipe and product profile, with existing authority
  and validation/readiness limits.

The parser/file objects are not live views after return. Caller edits and later
source edits/deletion cannot redefine the record; `restore` requires no reopening
of old sources. Reads of multiple files remain sequential acquisition, not an
atomic filesystem snapshot or a project publication transaction. Versioned ASDF
publication and executable task plans remain at their original milestones.

`execution_ready=false`, unresolved asset references, unverified header evidence
and unvalidated product compliance remain explicit. Configured detector ordinals
are not physical IDs. This does not implement geometry-free or multi-amplifier
numerical execution, new variance rules, association policy or scientific QC cuts.

## Examples and compatibility

[OmegaCAM project](project-composition-examples/omegacam/project.toml) and
[WFI project](project-composition-examples/wfi/project.toml) share one
[profile subset](project-composition-examples/shared/profiles.toml), with separate
instrument/readout declarations. Their native references use the already qualified
local-override graphs. These are review templates, not real dataset selections or
scientific parameter recommendations. Original complete authoring examples remain
valid through the integrated loader; the old standalone `validate_project.py` CLI
keeps its original review-only contract.

The migration CLI syntax is unchanged; `freeze-project` accepts these entry files.
There is no new installed command, dependency or automatic engine selection.
The example fragments above do not supply a complete runnable configuration.

## Focused qualification

Use selected tools and a private C90 build of `mefpp`, `mef_config_read`,
`config_domains_probe`, `config_paf_snapshot` and `cli_capture_probe`. Select only
`^native_config_(migration|project_composition)$` for this increment:

- Existing migration regression retains its 21 rejection/recovery cases and
  both instruments' exact PAF/CLI comparisons, including the original combined
  project cases through the changed library method.
- New project check covers 18 primary profiles: both instruments, full/entry/local
  native references and legacy-complete/version2-complete/split project layouts.
  Two extra native version-1/2 compatibility controls and the committed examples
  also pass. CLI/library equality is checked from two caller directories.
- Twenty-four rejection/recovery controls cover project conflicts, path-base
  ambiguity, unknown/missing fields, envelope/domain versions, types, duplicate
  includes, direct/indirect cycles, symlink loops, graph limits, native units and
  effective native/readout contradictions. Each failure is followed by a valid
  request in the same Python process; native parsing remains process-isolated.
- Shared domains, resolved roots/includes, CRLF, exact source hashes, caller
  mutation, deletion of all private sources and saved-record recovery are checked.
  Failed CLI input creates no output directory. No FITS/engine recipe executes.

See [agent results](../../../developer/m2-project-composition-agent-results-2026-10-30.md).
Agent, selected-tool Intel Mac and representative shared Chapman4 C90 checks
passed 2/2 at d0ab19e91b46e6fe6e21c541af99c21ed35029b4. See
[paired results](../../../developer/m2-project-composition-paired-results-2026-10-30.md).
The #155 correction is qualified for owner review; full M2 closure remains a
cumulative review/owner decision. No new C17/sanitizer run is claimed: native C
and ownership code are unchanged, and accepted evidence is retained. No test
replay is needed for the documentation receipt; merge/cleanup requires instruction.
