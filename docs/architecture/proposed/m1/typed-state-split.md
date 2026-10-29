# M1 typed-state split — retained-source mapping

Baseline: accepted main `7341c895e9e1eb7008915e1e2cf961532b7eb8a6`. The neighboring generated [effective-settings-baseline.json](effective-settings-baseline.json) maps every current constructor getter to its legacy destination, storage type, conversion and proposed owner domain. These domain names are implementation guidance, not new public WAD properties or a frozen ABI.

| Owner | Evidence/examples | Preservation rule |
|---|---|---|
| Immutable instrument/detector config | nchips; configured RON/gain; prescan/overscan/crop regions; configured reference pixels/WCS defaults | Typed per-detector records; retain exact legacy conversions and mapping. Configured values remain configured, not measured QC. |
| Immutable algorithm config | bias/BPM/dome/sky parameters; scan/pixel rejection; median region; saturation/kernel settings | Preserve values, conversion precision and defaults. M1 does not tune parameters or repair --ksize (#133). |
| Product/header mapping config | 100 constructor key/comment/value sites; five output-prefix defaults | Preserve original strings and metadata mappings. Do not silently normalize quote forms or infer Phase 3 correctness. |
| Request | PAF selection, file/list bindings, save flags, explicit CLI overrides and ordered list members | Snapshot separately from defaults; resolve containing/caller path bases explicitly in later M3. Existing pilot CLI remains cwd-dependent. |
| Mutable work context | Traversal index/name, loaded FITS metadata, frame-name arrays, scan statistics and temporary image/cube handles currently mixed in mef_bb | Track lifetime and mutability explicitly; do not move these into immutable config merely because they share a legacy struct. Constructors/partial cleanup must use the accepted common template. |
| Owned result and qc | Completed product identities, correction state, diagnostics and declared measurements/availability | Result/error must survive context destruction. QC definitions remain TBD; do not invent a RON estimator or automatically update configured gain/RON/header values. |

## Precision and decoder behavior to preserve

The current constructor has 151 getter templates: 137 global and 14 per-chip. They expand to 585 key reads for 32-chip OmegaCAM and 249 for eight-chip WFI. All have mapped legacy destinations; the two example PAFs provide every required key.

Kind codes are validation categories, not the destination C type. In particular, five parameters stored in double fields first pass through a float temporary: MEF.BIAS.KAPPA1, MEF.DOMEFF.FRAMETHR.LO/HI and MEF.SKYFF.FRAMETHR.LO/HI. A future adapter must copy the effective legacy value, not silently parse the original decimal directly into double. Some integer destinations use atoi, others use atof followed by integer conversion; detector CRVAL values use an integer conversion before storage in float fields. These facts are compatibility requirements, not approval to tighten or improve them.

qfits_paf_query uses the first matching key, trims trailing whitespace and strips only a matching pair of ASCII double quotes. Retain original UTF-8 bytes and all duplicate occurrences as evidence. WFI repeats MEF.MASTER.BIAS.KEY and .COMMENT with identical values. Six keys in each PAF are not read by this constructor; the JSON lists them. “Not read by constructor” is not an instruction to discard them or a claim that every other consumer was audited.

Constructor diagnostics use rounded decimal formatting. All 4,668 logged getter values across twelve retained commands agree with the finite source-derived model. Modeled binary32/full stored values in the JSON are deductions from source conversions, not full-precision measurements extracted from logs. A dedicated legacy/adapted normalized dump must establish runtime equality during implementation; do not run the old -d CLI as a supposedly dump-only command, because it can continue into the engine.

The eight captured repository configuration files match the current source Git identities. All executed partition PAFs equal their project instrument PAF and repository instrument PAF. Captured native commands have file/list/output bindings and save flags, with no numeric CLI overrides. The first typed adapter can therefore cover these actual cases without inventing local-override science settings; synthetic override/invalid/partial-construction controls still belong to M1 qualification.

## Implementation sequence

1. Implement small owned configuration/request/context/result/error lifecycle helpers with explicit partial-construction cleanup, using the accepted C90 template and service naming. Public payload/ABI details remain provisional.
2. Keep the existing PAF reader active. Add a compatibility snapshot/adapter that preserves existing constructor conversions and request overrides; avoid a second independent set of defaults.
3. Emit normalized settings from the retained legacy and adapted objects, including per-detector values, prefix/header mappings, request bindings and sources. Compare field by field at full stored precision on tiny configuration-only controls; never enter mef_engine for a settings check.
4. Verify copied/borrowed lifetimes, invalid/occupied output handles, allocation failure and result/error lifetime after context destruction. Qualify the changed paths on actual Mac/Chapman, without replaying the historical reduction matrix.
5. Integrate one boundary at a time; numerical extraction, new variance/linearity/dark/fringe models, QC estimators and TOML configuration integration retain their separate milestones.

This receipt changes no native source, mathematics, installed configuration, calibration association or accepted product.

## Implementation status

The first [owned config snapshot](config-snapshot.md) now copies constructor-mapped settings with independent lifetimes, an internal typed detector array, per-object allocation and deterministic bit-preserving inspection. It remains opt-in and outside the numerical engine. Request/context/result ownership and CLI-override capture remain pending M1 work; no numerical service or TOML migration is implemented.
