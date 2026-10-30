# M2 third increment — typed native domains and owned source records

30 October 2026. Owner accepted/merged/cleaned PR #148; Mac and shared Chapman
main are clean at `7e665da170e2e1af9f96a97e9f5bc2f6ebcfeef5`. Owner instructed
“Proceed” with versioned native domains, types/units/sources and complete OCAM/WFI
examples, retaining exact settings and distinct reduction/recipe/product profiles.

## Bounded result

Add input schema version 3 with native domain schema version 1 for **instrument /
detector, processing and product mappings**. This covers the same 151 getter
templates, expanded to 585 OCAM and 249 WFI settings. It does not define every
future project/association/recipe/execution/quality/profile domain or complete M2.
Legacy input versions 1 and 2 remain supported and keep their previous shape.

The [complete field catalog](typed-field-catalog.json) and native
`mef_config_domains.def` explicitly map each legacy key to its domain path,
storage type, canonical unit and role. They contain no numerical defaults.
Catalog/type coverage is checked against the retained M1 source/getter registry.
Each declared domain has its own schema_version=1; future versions require an
explicit contract change rather than silently reinterpreting fields.

An actual passing [WFI local example](examples/wfi/local.toml):

```toml
schema_version = 3
include = ["entry.toml"]
override_keys = ["processing.bias_kappa1", "processing.scanrej_min", "processing.scanrej_max"]

[processing]
schema_version = 1
bias_kappa1 = { value = 0.123456789012345, unit = "1" }
scanrej_min = { value = 2, unit = "count" }
scanrej_max = { value = 3, unit = "count" }
```

The entry point includes reusable instrument, processing and product files. These
names and the number of files are examples, not a mandatory directory layout.
Every leaf is a `value` / `unit` descriptor. The schema determines its native
storage type; TOML scalar types are checked without coercion. Domain versions,
known containers, leaf names, descriptor members and units are strict. Unknown
or empty unknown containers fail rather than disappearing during flattening.

## Types, units, identity and profiles

| Quantity | Canonical unit | Preservation |
|---|---|---|
| Detector/frame/rejected-sample counts | count | Native int32; no float/bool/string coercion |
| Flags and relative/sigma multipliers | 1 | Existing int32/float32/float64 according to catalog |
| Scan/crop/reference pixel/median region/kernel quantities | pixel | Original native type and index/endpoint conventions |
| Flat thresholds / saturation level | adu | Existing configured signal convention |
| Configured detector gain | electron/adu | Configured assumption, not measured gain |
| Configured detector RON | electron | Configured assumption, not a QC estimator |
| Detector CRVAL defaults | degree | Original narrowed/configured values; no WCS reinterpretation |
| Header/naming/identity strings | none | Exact original UTF-8/control/quote bytes |

Canonical spellings are deliberately strict. Alternate units are rejected; this
increment does not scale units or add scientific cuts. Scan/crop records retain
the FITS one-based inclusive convention; median-region metadata has a distinct
native-index role. Other conventions remain as documented in the M1 crosswalk.
The five legacy double fields narrowed through float are emitted from actual
stored values, not naively reparsed from the original PAF decimals.

`instrument.detectors.CHIPn` denotes the existing positive canonical legacy chip
ordinal, **not** an invented physical detector/asset ID or a general FITS/HDU
mapping. Actual single-detector/layout support remains M4/later acceptance.

Product fields represent header mappings and naming defaults, including existing
Phase 3 strings. They do not certify a compliant product or select an execution
recipe. `product.header.recipe_key` is a FITS mapping, not the ordered recipe.
Reduction profile (purpose), ordered recipe and product profile (requirements)
remain separate concepts. No fictitious profile defaults are inserted. Their
future domains are deliberately not accepted as aliases for product mappings.

## Composition

The [accepted composition policy](native-subset-composition.md) is retained:
containing-file paths, canonical-path caching, local explicit overrides, no
implicit last-include-wins, scoped declarations, conflict/cycle diagnostics and
resource bounds. A version 3 graph includes version 3 files; version 2 graphs
continue to include version 2 files. Mixed namespace/unit formats reject.

Version 3 override declarations use domain paths. The parser shim normalizes
those paths to the existing native keys, then the unchanged explicit 27-key
allowlist and C90 merge policy apply. Per-detector, detector-count and identity/header/
naming replacements remain forbidden where the existing allowlist forbids them.
Every source descriptor is validated before merging, so a parent cannot hide
an invalid unit/type in a child. Final full-field completeness remains required.

## Owned effective document and sources

The new internal C90 `mef_config_document` owns:

- The same immutable `mef_config` used by existing native services.
- A frozen JSON inspection record for every winning field: native/domain keys,
  storage, unit, role, configured authority, actual canonical source filename,
  parsed value line, input version, declared/inferred-unit origin, inherited
  status and explicit-override status in the source that supplied that value.

`mef_config_document_from_toml`, clone, settings getter, source dump and destroy
have the existing NULL/occupied-output/owned-error-status conventions. The
settings pointer is borrowed only while the document lives. Clone owns both
components independently. Loading parses/composes once; inspection and cloning
never reopen source files. Existing contexts can copy the same settings through
the existing M1 interface; automatic project/plan wiring remains later work.

An inherited field can truthfully have explicit_override=true if its supplying
child made that replacement. Identical definitions coalesce under the accepted
rule; an explicit identical replacement is a no-op with an explicit declaration.
The source record identifies the winner; it is **not** a complete multi-source
merge/override history. Original duplicate PAF occurrences remain in the example
conversion evidence; this is not the final public migration tool.

Values/metadata survive parser/bundle/original-document destruction and edits to
files after loading. Paths are provenance locations, not verified content IDs.
Source content hashes are explicitly `source_hash_state = "not-recorded"` in
runtime records; durable input hashes/history and ASDF/WAD plan serialization
remain later M2/M7 work. Do not edit files while loading: this is not an atomic
filesystem snapshot. Source JSON requires UTF-8 filenames, escapes controls and
quotes, and reports failure rather than misrepresenting invalid byte paths.

The callback allocator covers C90 composition/report/document/config owners and
clones. Parser/private-shim allocations and the original temporary detector map
remain outside it. Ordinary failures clean partial owners and leave outputs NULL.
Dump callers own streams and must check fclose; no reader writes science products.
No blanket OOM, thread-safety, Python-host or reentrancy claim is introduced.

## Implementation and qualification boundary

The descriptor catalog, merge policy, source serialization and document owners
are C90/C17. Only the existing parser-specific shim translates tomlc17 tree types
and version-3 value/unit descriptors in C99. The vendored parser is unchanged;
no C99 type crosses a C90 header. All targets remain opt-in under
MEFPP_BUILD_CONFIG_PROBES=ON, default OFF, and are not installed or linked into
normal mefpp. Normal recipe/numerical/source kernels are unchanged.

Build mefpp, config_paf_snapshot, config_toml_snapshot, cli_capture_probe and
config_domains_probe. Select only `^native_config_toml(_subsets|_domains)?$`.
The existing 41-case compatibility and 16-profile/32-case composition checks
remain. Unsupported-version fixtures now use 4 because 3 is intentionally added.
The new check verifies 151-template storage coverage, exact PAF/CLI settings,
explicit units, frozen/independent source documents, all new C90 allocation
positions, descriptor rejection/recovery and schema/profile separation. It edits
only a private synthetic fixture after loading to demonstrate frozen values.
No FITS, mef_engine, QC algorithm, reduction or installation is exercised.

[Complete OCAM/WFI examples and conversion evidence](examples/README.md) were
copied from a passing actual-constructor/native-domain check. Original PAF text
and SHA256 are retained; this bounded conversion is not full PAF/CFG migration.
The review catalog is not a general JSON Schema/ASDF metaschema or complete WAD
conformance claim. Agent evidence is distinct from pending actual Intel Mac and
one representative shared Chapman qualification with the selected tools.

No historical matrix replay or tool/dependency requalification is required.
Other extraction stays M5/M6; optional BPM, required M6a variances and
#133/#144/#75 limitations remain. Owner review precedes merge/cleanup.
