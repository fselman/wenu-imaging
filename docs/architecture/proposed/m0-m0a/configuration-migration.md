# Configuration migration ledger and precedence

Source baseline: accepted main 0fa9eaf157359a93f2a9196f6fff05dc3e96e220. [configuration-ledger.json](configuration-ledger.json) records a source-only snapshot of twelve relevant native/Python/configuration files. Counts: 151 constructor getter sites, 848 PAF template occurrences, 229 project/instrument CFG options and 30 registered native long options. These counts describe text, not independently qualified effective settings.

The [earlier PAF-family inventory](../../../developer/mefpp-refactor-paf-inventory-2026-10-29.md) remains the readable family index: OCAM 591 entries/591 unique; WFI 257 entries/255 unique. The expanded ledger retains every PAF occurrence/value/line rather than deduplicating silently.

## Migration destinations

| Legacy source | Source evidence | Proposed destination / preservation |
|---|---|---|
| PAF instrument/geometry/CCD fields | Constructor getter templates, including CHIP%d expansion | WAD instrument/detector definitions; effective native configuration with explicit detector ID mapping |
| PAF algorithm parameters | mef_bb_new_from_paf getter sites/conversion code | Typed processing configuration; preserve numeric precision, constructor behavior and defaults until reviewed |
| PAF .KEY/.COMMENT/PHASE3 mappings | Template occurrences plus native consumption | Product/header mapping configuration; output profile requirements remain separate from algorithm settings |
| PAF output names | Python Instrument.read_key_from_paf reads five prefix keys as well as native use | Product naming policy; removing only the C PAF reader does not remove Python's PAF dependency |
| Instrument CFG [Project]/[Data] | pycavi_instrument.py, config values | Instrument identity/discovery rules, profile and product naming; do not confuse file-format declarations with implemented layout support |
| Instrument CFG [Primary Keywords] | Exposure metadata and classification getters | Versioned normalized metadata mappings and explicit classification/group/association rules; preserve original cards |
| Instrument CFG [Extension Keywords] | Runtime-generated ext_nn_name/use/gain_key lists | Detector ID/selector/health/selection records; retain native order and amplifier-specific gain-key mapping |
| Project CFG [General] | pycavi_tools.read_pycavi_config | Execution/log settings, not numerical settings |
| Project CFG [Provenance] | Project metadata reads | Project descriptive metadata with provenance; not a substitute for actual software/data identities |
| Project CFG [Directories] | Independent notebook workspace/raw/project roots observed on Chapman | Explicit root bindings and output/work/log locations; path strings never define scientific group identity |
| User executable CFG | load_executable_paths | Execution environment bindings/tool identities; explicit argument then PYCAVI_ASTROSOFT_CONFIG then user default |
| Native CLI | long_options and mef_bb_load switches | Explicit request, recipe choices, numeric overrides or informational commands, with one effective settings record |
| Wrapper/notebook defaults | PartitionsTree association calls, copy_paf_to_dir, selected list/group ordering | Versioned compatibility policy and recorded explicit selections; no replacement nearest-date policy inferred from file names |

The source config/mefpp.cfg file contains bare legacy directory values, not the active user executable configuration. load_executable_paths reads a [Paths] file selected by argument/environment or ~/.pycavi/pycavi_astrosoft.cfg. Actual pinned executable paths/hashes remain in retained host evidence; this package does not replace that file or assume its current contents from a source template.

## Current precedence to preserve explicitly during import

1. copy_paf_to_dir retains an existing partition-local mefpp.paf; otherwise it copies the project instrument PAF, then the engine-prefix instrument PAF fallback. A project edit need not affect an already prepared partition.
2. Native mef_bb_load first chooses --pafname (default mefpp.paf) before constructing the context, then processes CLI overrides. Help/version/license can return before PAF loading.
3. Native numeric/flag/file options modify context fields after PAF loading. The first remaining positional argument overrides the master-flat output name after the option loop; --mffsave has an argument, not just a boolean.
4. Python additionally consumes CFG and five PAF product prefixes, selects lists/calibration dependencies and applies mean-gain/exposure normalization. These must not be merged into a second conflicting set of native defaults.
5. Association time limits are per call: science/std bias 10 days; science/std sky 30 days; bias for sky/dome 30 days; dome for sky 30 days. Record actual filter/mode/time selection and list order; a global "30-day flats" label is insufficient.

This is an import ledger, not a mandate to preserve implicit precedence in the new interface. The target uses explicit subset composition and an override allowlist. Import must report the old effective choice and any conflict before a reviewed migration changes it.

Identical duplicate WFI MEF.MASTER.BIAS.KEY and .COMMENT entries remain reported as distinct source occurrences. A conflicting duplicate requires explicit resolution. Native constructor kind codes are validation/conversion evidence, not final WAD types; integer-like PAF conversions/defaults must be compared at M1/M2 rather than silently tightened by a new parser.

## Source finding tracked separately

[Issue #133](https://github.com/fselman/wenu-imaging/issues/133): --ksize is registered and advertised, but no OPT_KERNELSIZE case exists in the option switches; the processing switch defaults to failure. This is source tracing only, not a new native run. Do not map it to a guessed smoothing algorithm or repair it in the configuration conversion. --xtnum shares the short -x handler; a simple textual case extractor alone misses that destination.

## Completion limits

The ledger covers source occurrences and proposed domains; it does not prove every key is consumed during every operation, nor reconstruct effective parameters from historical private directories. Retained pilot partition-local PAF/CLI bytes and installed configuration snapshots must be read/imported before claiming complete old/new effective-value equivalence. This package requests no broad Chapman scan or new reduction.

C TOML parser/language subset/license/C90 qualification, final field names, local override allowlist, exact decoder behavior and actual-host equivalence remain open M0/M1/M2 decisions. ASDF serialization ownership remains Python initially; no ASDF or TOML dependency is installed by this ledger.
