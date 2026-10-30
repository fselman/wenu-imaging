# M2 second increment — native TOML subset composition

30 October paired subset receipt: Intel Mac and representative Chapman4 private
C90 builds and both focused TOML tests passed 2/2 at
d622bbec7e9784ab9fa6211080cfd4955ff3a08d. Original exact-setting/41-case controls,
16 composition profiles from two directories and 32 rejection/recovery cases
passed. Protected files/checkouts stayed unchanged. See [paired results](../../../developer/m2-toml-subsets-paired-results-2026-10-30.md).
Ready for bounded owner review; full M2 domain/unit/source/migration work remains
pending. This documentation update requires no repeated execution or installation.
Earlier target-pending notes below are historical. Merge/cleanup requires owner
instruction.


30 October 2026. Owner accepted/merged PR #147, and Mac/shared Chapman main are
clean at `0550fb90215c636cc6b881eb67e221c24b5ed876`. Owner instructed “Proceed”
with reusable subsets and explicit overrides. This increment preserves the
[first reader's compatibility vocabulary](native-compatibility-reader.md).
It does not complete M2 or adopt the final eight domain schemas.

## Input and result

The existing `mef_config_from_toml` also reads version 2 compatibility documents:

```toml
schema_version = 2
include = ["shared/instrument.toml", "shared/processing.toml", "shared/product.toml"]
override_keys = ["MEF.BIAS.KAPPA1"]

[native]
"MEF.BIAS.KAPPA1" = 0.123456789012345
```

Each included file also uses version 2, with an explicit `[native]` table and
optional `include` / `override_keys` arrays. A subset may be partial or empty;
only the final merged settings must contain exactly the original full native
configuration. Files are not required to follow these example names or this
three-file split. One complete version 2 document is also valid.

Version 1 retains its original standalone shape and complete-configuration gate.
It cannot declare includes/overrides and is not accepted as an included subset.
To reuse an old complete compatibility envelope in a graph, explicitly change
its version to 2; do not silently reinterpret version 1 fragments. PAF remains
the installed engine's active configuration; no default search or public CLI
TOML dispatch is added.

## Composition and precedence

1. Resolve each configuration path once to a canonical absolute pathname.
   Relative includes use the directory of the resolved containing file, including
   when that file was reached through a symlink. Absolute includes are explicit.
   No chdir, environment expansion, search path, glob or observation scan occurs.
2. Validate every file's local key/type/storage domain and override declarations
   before merging its children. Invalid settings cannot be hidden by a later
   replacement. The final detector-count/coverage gate is still the reader's.
3. Combine included settings. Identical definitions coalesce; there is no
   implicit last-file-wins rule. Equality means the same scalar kind and integer
   value, string bytes or binary64 parser bits. Signed zeros differ. Precision
   is not weakened by comparing rounded decimal text or float32 tolerances.
4. Conflicting included definitions fail unless the containing file supplies a
   permitted local replacement and names that key in its own override_keys.
   Such an explicit parent can resolve conflicts between siblings. Reversing
   sibling order cannot select a different scientific value implicitly.
5. Apply the containing file's local settings. A differing inherited value needs
   that file's declaration. Override declarations never authorize a descendant
   or ancestor to replace values silently. Each declaration requires both a
   local value and an inherited value; otherwise it fails. An explicit identical
   replacement is a permitted no-op. Identical undeclared definitions coalesce.
6. Validate final completeness and copy into the original immutable mef_config.
   That object and its clones are independent of files/parser trees thereafter.

Unknown root/native keys, duplicate list entries, empty/NUL/nonstring list
members, wrong versions/types/ranges, missing files and include cycles fail.
Conflicts report the key and both contributing source paths, subject to the
caller's diagnostic capacity. Missing files and path resolution failures return
IO status. Cycle, schema, conflict and resource-policy failures return config
status. Allocation failures in the new C90 owners return memory status.

## Explicit override allowlist

`mef_toml_override_keys.def` explicitly enumerates these 27 current global numeric
settings. Future numeric fields are not automatically added. Detector count,
per-detector parameters, identity/header/prefix strings and unknown keys cannot
be overridden. Select a different explicit instrument/product subset instead.

| Family | Permitted keys |
|---|---|
| Reference pixels | MEF.CORRECT.REFPIXELS, MEF.REFPIX.X, MEF.REFPIX.Y |
| Scans | MEF.USE.PRESCAN, MEF.USE.OVERSCAN, MEF.SCANREJ.MIN, MEF.SCANREJ.MAX |
| Bias | MEF.BIAS.KAPPA1, MEF.BIAS.FRAMENUM.MIN |
| BPM | MEF.BPM.PROPFLAG, MEF.BPM.LGAINTHR, MEF.BPM.HGAINTHR |
| Dome | MEF.DOMEFF.FRAMETHR.LO, MEF.DOMEFF.FRAMETHR.HI, MEF.DOMEFF.FRAMENUM.MIN |
| Sky | MEF.SKYFF.FRAMETHR.LO, MEF.SKYFF.FRAMETHR.HI, MEF.SKYFF.FRAMENUM.MIN |
| Pixel rejection | MEF.PIXREJ.SIGMA.LO, MEF.PIXREJ.SIGMA.HI |
| Median region | MEF.MEDIAN.REG.X1, MEF.MEDIAN.REG.X2, MEF.MEDIAN.REG.Y1, MEF.MEDIAN.REG.Y2 |
| Kernel / saturation | MEF.KERN.HSIZE, MEF.SATLEVEL, MEF.SATMAX |

This is file-composition policy, not a CLI rewrite or new scientific rejection
rule. In particular, #133's --ksize handling remains unchanged. Existing units,
stored types, precision and configured-versus-measured authority remain as in
the first reader. No gain/RON estimator or numerical processing is introduced.

## Implementation, ownership and bounds

`mef_toml_bundle.c` owns the graph/merge policy in C90/C17. The existing private
C99 parser shim only exposes parsed keys, scalar values and composition lists;
no C99/parser type crosses its C90 header. The vendored parser is unchanged.
All targets stay behind MEFPP_BUILD_CONFIG_PROBES=ON, default OFF; no installed
payload or normal-engine link changes.

Each canonical pathname is parsed once per call. Shared dependency graphs and
symlink aliases reuse that call's parsed view; active canonical paths detect
cycles. This is path resolution/caching for explicit configuration references,
not content identity, inode equivalence or M3's general asset resolver.

The callback allocator now covers C90 composition containers/binding arrays as
well as the returned snapshot. Parser allocations and the original temporary
detector map remain outside it. Every partial owner is cleaned on failure;
borrowed parser strings survive until the immutable snapshot has copied them.
No mutable graph survives in the returned configuration. Initialization remains
serial and explicit; no concurrent parsing/thread-safety/Python-host or blanket
OOM claim is made.

Bounds: at most 64 unique canonical files, 16 files along a dependency chain,
64 entries per include/override list, 65,536 effective bindings per subset view,
4 MiB per input file and platform PATH_MAX for resolved/joined paths. These are
explicit reader resource limits, not scientific detector/algorithm thresholds.
The graph is not an atomic filesystem snapshot; files must not be edited while
being loaded. Returned values are owned and frozen, but durable hashes/source
chains, override histories and WAD plan serialization remain subsequent M2/M7
work and are not implied by cached paths.

## Focused checks

The existing native_config_toml regression still checks 585 OCAM / 249 WFI /
249 edge values and 41 rejection/recovery cases. Its unknown-version fixture
now uses version 3 because version 2 is intentionally supported.

The new native_config_toml_subsets check uses the real PAF constructor and
legacy CLI loader (mef_bb_load via cli_capture_probe), not a second Python
conversion model. It checks equivalent split graphs for both instruments,
explicit local/nested replacements, sibling conflict resolution in either
order, shared diamonds, symlink aliases and explicit no-ops. Every valid
profile runs from two unrelated caller directories and exercises all new
composition/snapshot owner allocation positions, output guards and lifetimes.
Rejection/recovery controls cover scoped/forbidden/unused overrides, hidden
invalid settings, unknown keys, bad lists, missing files, cycles/aliases and
path/depth/file/list bounds. No FITS, mef_engine or Pycavi reduction runs.

Build mefpp, config_paf_snapshot, config_toml_snapshot and cli_capture_probe.
Select only `^native_config_toml(_subsets)?$`. Source/probe identities, commands,
logs and results are retained per private attempt. Agent C90/C17 and scoped
sanitizer evidence is distinct from pending actual Mac/representative Chapman
acceptance. No historical matrix replay or tool requalification is needed.

Full domain schemas (project/composition, instrument/detector, association,
processing, recipe, execution, quality, product/profile), runtime unit/source
provenance, complete PAF/CFG migration and conflict policy remain open M2 work.
Reduction profile, ordered recipe and product profile remain distinct. Other
numerical extraction stays M5/M6; optional BPM / required M6a variances and the
existing #133/#144/#75 limits remain. Merge/cleanup requires owner instruction.
