# M2 configuration migration and immutable requests

30 October paired migration receipt: selected-tool Intel Mac and representative
shared Chapman4 private C90 builds and both focused configuration CTests passed
2/2 at 38f4f4d4bd05c4977f1624fc8737431527bdbe8a. Protected files and clean review
checkouts remained unchanged. See [paired migration results](../../../developer/m2-migration-paired-results-2026-10-30.md). Ready for
bounded owner review; full M2 closure remains a separate cumulative review.
The corrected nested-package protection lookup is target-verified (#154); retain
the first failed handoff attempt. Establish all paths/interfaces from as-is source
and actual host evidence; never guess layouts. No test replay for this documentation
receipt, installation, numerical processing or normal engine activation. Preserve
all evidence/tools and milestone order. Owner instruction precedes merge/cleanup.
Earlier target-pending notes below are historical.

30 October 2026. Owner authorized finishing M2 configuration migration after
accepted/merged PR #151 and clean Mac/shared Chapman main
`a09bec7e6bc0d3fa8d82245db59aaf3063ac0d94`. Tracked in [#152](https://github.com/fselman/wenu-imaging/issues/152).

## Implemented configuration boundary

`Pycavi2/pycavi/pycavi/pycavi_configuration.py` supplies one standard-library
Python API and CLI. Both use the opt-in `mef_config_read` native executable.
The actual PAF constructor supplies effective values; Python does not reimplement
its numeric conversions, derive defaults, or change scientific cuts. Every PAF
migration is rendered as complete typed domain version 3, loaded by the native
TOML reader and compared exactly, including integer/string values and floating
storage bits. PAF and ordinary mefpp/Pycavi remain supported and unchanged.

| Entry | Result |
|---|---|
| `ConfigurationMigration.migrate_paf(path, resolutions=..., cfg_files=...)` / `migrate-paf` | Complete native TOML plus immutable configuration containing original PAF/CFG text, hashes, occurrence/conflict ledger and exact conversion provenance |
| `ConfigurationMigration.load_toml(path)` / `freeze-toml` | Native-validated effective configuration, winning sources and complete frozen source graph |
| `ConfigurationMigration.load_project(path)` / `freeze-project` | Reuses the accepted project validator and validates its captured standalone native reference with the C reader; separate reduction purpose, ordered recipe and product requirements are retained |
| `ConfigurationMigration.restore(path)` | Checks a saved configuration's source hashes, closed generated representation, native catalog coverage and content identity without reopening original source files |
| `FrozenConfiguration.as_dict()` / `.plan_fragment()` | Independent copies; configuration portion of a future plan, with `execution_ready=false`, never an executable task graph |

The `source_root` and absolute `native_reader` arguments are explicit. This is a
source-checkout/private-build interface; schemas/resources are not newly installed
or discovered on PATH. Calling an API or loading a file never changes cwd. CLI
outputs go only to a new, explicitly supplied directory.

## PAF occurrence and conflict rules

Every PAF entry retains its exact line, literal and source text. Identical duplicate
WFI `MEF.MASTER.BIAS.KEY` and `.COMMENT` entries remain distinct occurrences;
there is no silent deduplication in provenance. Different literals require an
explicit key-to-original-line selection (`--resolve KEY=LINE`). Neither first nor
last occurrence silently wins a conflict. Even numerically similar but lexically
different repeated values require review; no Python number parser decides they
are scientifically interchangeable.

The selected occurrences are copied into a private temporary PAF. The original
file is never rewritten. The unchanged constructor decodes that private copy.
Missing required fields, unknown vocabulary, unsupported/ambiguous lexical syntax,
unused/invalid resolutions, NULs and legacy-unsafe long lines fail before conversion.
A migration resource ceiling of 4096 configured detectors is explicit, not a new
instrument default. Semicolons inside quoted strings and noncanonical indented
entries need review instead of a guessed reinterpretation of qfits behavior.
Known unconsumed PAF fields are retained as such; they do not become invented
native settings. New catalogued CHIP ordinals can be represented, but extra
ordinals outside the configured count remain visibly unconsumed.

## CFG evidence and authority

Explicit `--instrument-cfg` and `--project-cfg` retain original bytes and the
existing ConfigParser raw/interpolated strings. Instrument inline-comment behavior
matches `Instrument.read_config`; project interpolation matches
`read_pycavi_config`. The migration ledger checks vocabulary and labels destinations
(project roots/metadata, instrument/detector, association metadata, execution).
Unknown sections/options, duplicates, malformed interpolation and DEFAULT
inheritance fail instead of producing an unreviewed policy.

These values are `retained-not-executed` compatibility evidence, not a second
native defaults table. Empty legacy roots stay empty. No filename becomes an asset
ID, no directory grouping becomes an association decision and no CFG path is
silently adopted as authority over the explicitly supplied PAF. The explicit PAF
argument is the selected source; `Data.mefpp_paf` remains a retained legacy default.
A project authoring contract must explicitly supply roots/profile/recipe/asset
choices; migration does not fabricate the missing scientific identities. Legacy
bare-directory `mefpp.cfg` is not a `[Paths]` executable configuration and is not
silently converted into one. Automatic project creation/association and replacing
legacy CFG consumers belong to M7–M9.

## Frozen native provenance

The C parser owner now retains the exact UTF-8 bytes it parsed, including CRLF.
Before parser/bundle destruction, the document copies source text, ordered includes,
resolved include targets, explicit override declarations and every local definition
with its source line/key. Winning-field metadata remains backward-compatible.
Python hashes these frozen bytes, not a later read of mutable TOML, and links each
winning field to its source SHA256. Source graphs retain losing and identical
contributions as well as parent overrides. Resolved edges preserve the actual
symlink targets used during loading. C itself continues to report
`source_hash_state=not-recorded`; hashing belongs to the Python record, not a false
claim that the native serializer computes SHA256.

The configuration and its metadata are owned serialized bytes. Caller edits,
source edits/deletion and later overrides cannot redefine an existing record.
Multi-file acquisition is not an atomic filesystem snapshot: the graph records
what was actually read. Immutable successful records are not live views of a
project. The bridge executable's hash and migration-contract hashes are recorded;
record identities include provenance paths/tool identities and therefore need not
be the same across hosts even when all scientific settings agree exactly.

## WAD validation scope and publication

The shared API checks native catalog completeness, types/storage/units and the
WAD review catalog's configuration attributes (`settings`, `sources`,
`compatibility`), then assigns a content-derived record identity/version.
`wad_validation=configuration-attributes-checked` is deliberately scoped. Project
records retain their existing unresolved-reference, unverified-header and
not-validated product-compliance states. This does not assert full WAD image/task
validation, FITS applicability, execution readiness or a production ASDF schema.
Those integrated records/readers remain in their original milestones.

The CLI writes `configuration.json`, `plan-configuration.json` and, for migration,
`configuration.toml`. A final `COMPLETE.json` records all payload hashes. An existing
output directory is refused. Interrupted publication may leave an incomplete new
directory without the receipt; this is not a multi-file transaction or a durable
project revision. Originals, earlier attempts and installed prefixes are preserved.

## Examples and use

[OmegaCAM](migration-examples/omegacam.toml) and
[WFI](migration-examples/wfi.toml) were generated by the public migration API.
[Conversion evidence](migration-examples/conversion-evidence.json) retains original
PAF/CFG text and hashes, all occurrences, selected values, duplicate records and
exact native stored-value comparisons. These are source templates, not recovered
private observation projects or recommendations for scientific parameter choices.

With a qualified private build (substitute explicit absolute paths):

```bash
/absolute/python -B /absolute/checkout/Pycavi2/pycavi/pycavi/pycavi_configuration.py \
  --source-root /absolute/checkout --native-reader /absolute/private-build/mef_config_read \
  migrate-paf /absolute/chosen/mefpp.paf \
  --instrument-cfg /absolute/chosen/instrument.cfg \
  --project-cfg /absolute/chosen/pycavi.cfg --output /absolute/new-migration-directory
```

This is interface documentation, not a request to migrate a private observation
project now. Mac/Chapman commands use the canonical selected tools and the guarded
handoff, with fresh private builds and protected-file checks.

## Focused acceptance and remaining gates

Build the ordinary `mefpp` link plus `mef_config_read`, `config_domains_probe`,
`config_paf_snapshot` and `cli_capture_probe`, with resources disabled and
`MEFPP_BUILD_CONFIG_PROBES=ON`. Select only
`^native_config_(migration|toml_domains)$`. The existing domain test covers changed
native document allocation/clone/stream-error paths. The new migration test uses
real source PAF/CLI constructors, no FITS or numerical engine, and checks:

- all 585 OmegaCAM and 249 WFI settings, selected local overrides and both identical
  WFI duplicates;
- CLI/library equality from two unrelated caller directories and no-clobber receipts;
- original PAF/CFG provenance, explicit conflicting-occurrence resolution and unchanged inputs;
- source/caller independence, restored saved records, tampering rejection, CRLF,
  sibling conflicts, parent overrides and resolved symlink edges;
- native project reference integration without merging the three profile concepts;
- unknown/missing fields, wrong units/types, cycles, invalid numbers, bad resolutions,
  CFG failures and malformed CLI output preservation.

Agent C90/C17 and scoped sanitizer results are in the
[agent receipt](../../../developer/m2-migration-agent-results-2026-10-30.md).
Actual selected-tool Intel Mac and representative shared Chapman verification is
pending. Full M2 closure requires those results and owner review. There is no
ordinary engine activation, general dispatcher, ASDF project publication, numerical
optional/multi-amplifier implementation, new variance algorithm or M3–M11 reordering.
