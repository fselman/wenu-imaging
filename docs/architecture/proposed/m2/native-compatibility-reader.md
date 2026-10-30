# M2 first increment — native TOML compatibility reader

30 October paired M2 target receipt: Intel Mac and representative Chapman4 private
C90 builds (normal engine and both probes) and native_config_toml passed at
b0ea0897ff2b5257eaf3bae0029b14a11a8f7152: all 585 OCAM / 249 WFI /
249 edge settings and 41 rejection/recovery cases. Protected files/checkouts
stayed unchanged. See [paired results](../../../developer/m2-native-toml-paired-results-2026-10-30.md). Ready for bounded owner review;
full M2 composition/override/unit/source/migration work remains pending. No test
replay or installation is needed for this documentation update. Earlier pending
target notes below are historical. Merge/cleanup requires owner instruction.


30 October 2026. Resume from owner-accepted M1 closure / merged PR #146,
main `7d8da6b96b7b744a51e3847522a727e3f510c6f2`. The October 29 handoff records
clean synchronized Mac/shared Chapman checkouts. Fresh Mac evidence on October 30
confirms the expected main, clean status and selected Python 3.11.14.

## Purpose and boundary

Establish one native TOML-to-immutable-config boundary before reusable subset
composition. This is a bounded **first M2 increment**, not M2 completion or the
final domain schema. PAF remains the active engine configuration. Remaining M2
work is listed below; the original M3–M11 order is unchanged.

`mef_config_from_toml` produces the same owned `mef_config` as the accepted PAF
snapshot path. It reads a complete versioned native compatibility envelope:

```toml
schema_version = 1

[native]
"MEF.NCHIPS" = 8
"MEF.INSTRUMENT" = "WFI"
# All other mapped settings are required; this fragment alone is invalid.
"MEF.BIAS.KAPPA1" = 5.0
"MEF.CCD.GAIN.CHIP1" = 2.0
```

The key vocabulary is deliberately the existing mapped PAF-key catalog, including
`.CHIPn` selectors. It is an import/inspection boundary, not a second set of
scientific defaults or an adopted public WAD schema. Product/header strings in
this envelope do not constitute a product profile. Reduction profile, ordered
recipe and product profile remain distinct in the target domain schema.

Every one of 137 global settings and 14 settings per configured detector is
required, with no fallback/default search. Unknown keys/tables, missing settings,
wrong version, duplicate definitions (even identical TOML duplicates), unsupported
TOML types, NUL-containing keys/strings, nonfinite numbers and C storage overflow
fail. Integer, real and string types are explicit: a float field uses `2.0`, not
`2` or `"2.0"`; integer flags are retained as integers, not boolean coercions.
Only storage/domain validation is added; there are no new scientific gain/noise,
geometry, rejection or quality cuts. Detector count is positive and bounded by
the supplied field count and allocation arithmetic before use.

## Units and precision

The envelope uses the existing native numeric conventions, documented in the
[M1 closure crosswalk](../../../developer/m1-closure-review-2026-10-29.md).
No unit scaling, new normalization or correction occurs here.

| Native setting family | Compatibility convention |
|---|---|
| Detector scan/crop, reference pixels, median region, kernel size | Existing pixel/index and endpoint conventions; unchanged |
| Bias/flat signal thresholds, saturation level | Raw ADU, with original field-specific semantics |
| Kappa / pixel-sigma rejection | Dimensionless multiples in the retained algorithm |
| BPM gain ratios and saturation fraction | Dimensionless |
| Configured detector gain / RON | Electrons per ADU / electrons; configured assumptions, not measured QC |
| Detector CRVAL / CRPIX | Legacy WCS degrees / pixels, preserving original conventions |
| Count/flag parameters and header/prefix strings | Original integers / exact strings |

Binary32 settings narrow exactly once from the TOML real value to native float.
Binary64 settings retain the TOML double. The test emitter starts from actual
stored PAF snapshot bits and emits round-trippable decimal values; therefore the
five legacy double fields loaded through float retain their narrowed bits. Raw
PAF decimal spelling must not be copied naively into a double TOML setting.
Signed zero and UTF-8/control/quote/backslash text are preserved.

## Ownership, errors and language boundary

The public internal header is C90. Call `mef_config_toml_initialize()` once in a
serial startup phase, then pass an explicit configuration pathname to the reader.
Initialization is idempotent but not atomic. It installs UTF-8 checking with the
parser's default allocator once; no per-request global option mutation occurs.
No concurrent parsing/option changes, thread safety or Python-host qualification
is claimed. Do not initialize while another parser caller holds live objects.

`mef_config_toml.c` stays C90/C17. Only unmodified pinned `tomlc17.c` and its
small private `mef_toml_bridge.c` shim compile as C99 in a separate static target.
The shim exposes no C99/library types through its C90 boundary. This makes the
parser-specific glue exception explicit for review; it does not upgrade core
source requirements. Both new targets are confined to
`MEFPP_BUILD_CONFIG_PROBES=ON`, default OFF. They are neither linked into the
normal `mefpp` executable nor installed. Normal runtime adoption remains pending
paired target acceptance and subsequent M2 integration review.

Parser documents own their trees. The C90 mapping borrows parser strings only
while the existing M1 constructor copies them. Temporary detector storage and the
parser tree are released on success/failure before return. The caller starts its
output at NULL; occupied handles are preserved. Optional diagnostics are copied
into caller storage. Allocator callbacks apply to the returned M1 snapshot only,
not parser or temporary allocations. No dependency-wide OOM guarantee is made.
No context exit/abort, cwd mutation, environment rewrite, installation or product
publication is introduced by the reader.

The compatibility grammar is a deliberate TOML 1.0 subset: `[native]` with typed
scalar entries, single-line basic/literal strings and standard 1.0 escapes.
Multiline strings, inline/native dotted-table construction and 1.1 escape
additions are rejected. This is not full TOML conformance certification or the
final composition grammar. Configuration inputs must be seekable and at most
4 MiB; read/size/open failures return IO status. Relative explicit filenames
retain ordinary file-open meaning; containing-file subset resolution is later
M2 work and this reader never changes cwd.

## Focused acceptance check

`config_toml_snapshot` exercises the new reader, `mef_config_from_legacy`, config
clone/dump/destruction, argument/initialization/occupied-output guards and every
returned-snapshot allocation failure. It never invokes the recipe or Pycavi.

`native_config_toml` / `tests/config_toml_contract.py`:

1. Run the real `config_paf_snapshot` / `mef_bb_new_from_paf` on source OCAM/WFI
   PAFs whose hashes match the accepted input lock; compare every stored setting
   with the reviewed M1 baseline independently of TOML.
2. Emit TOML from the actual stored values, parse it with Python `tomllib`, then
   use the native reader and compare the complete JSON dumps, including exact
   float object bits. Preserve source PAF bytes and conversion-source/hash
   evidence in the private test directory. WFI identical PAF duplicates and six
   unconsumed keys are retained in that original text, not silently migrated.
3. Run a 249-field signed-zero/escaped-text fixture and ownership checks, including
   111 injected returned-snapshot allocation positions per valid profile.
4. Reject 41 malformed/missing/type/range/NUL/UTF-8/size/version cases; each is
   followed by a valid read in the same process and full-value comparison.
   Use filenames with spaces and an unrelated caller directory.
5. Retain commands/logs, host/platform, source/probe/parser hashes and counts in
   `run-provenance.json`. The two full converted instrument examples remain
   private generated test artifacts, not installed configuration templates.

The emitter is a test helper, not a public migration tool or a replacement PAF
parser. Conflicting PAF duplicate detection/import resolution is still pending;
the unchanged legacy constructor is not tightened implicitly.

Build `config_paf_snapshot` and `config_toml_snapshot`, then select
`ctest -R '^native_config_toml$'`. Use the selected actual-host tools, fresh source
exports/builds and priority rules. No resource decompression/install or FITS read
is required. Do not rerun the historical Stage 2 or M1 scientific/memory matrix.
Agent C90/C17 and scoped sanitizer checks are reported separately from actual
Intel Mac/representative Chapman acceptance, which is pending.

## Remaining M2 gate

Implement the versioned project/composition, instrument/detector, association,
processing, recipe, execution, quality and product/profile domains; containing-
file path bases and reusable references; cycle/conflict/unknown-key diagnostics;
explicit override allowlist and precedence; full normalized value/unit/source
provenance consistent with WAD; complete source-text/hash/duplicate migration
records; retained local/CLI override equivalence; one immutable effective config
for CLI/library plans. The compatibility envelope alone meets none of these
unimplemented composition/persistence gates. ASDF persistence remains M7.

No calibration routine is brought forward, no new QC estimator is chosen,
optional BPM / required M6a variances are unchanged, and #133/#144/#75 remain
open. Target checks, owner review and any merge/cleanup are separate steps.
