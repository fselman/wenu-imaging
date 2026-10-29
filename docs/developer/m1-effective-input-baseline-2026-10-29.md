# M1 start: retained effective-configuration inputs

29 October 2026. After accepted/merged PR #136, owner instructed “next.” Begin M1 with a bounded text-input lock of the accepted OCAM/WFI pilot before changing native configuration/state ownership. Main baseline: 7341c895e9e1eb7008915e1e2cf961532b7eb8a6. The accepted C90 template, exact service names and qc/M5a contract apply; numerical QC definitions remain TBD.

## Independent receipt and source/log mapping — 29 October 2026

Uploaded archive `mac-m1-effective-inputs.tar.gz`: 924691 bytes, SHA256 `3a6519ff91e31e69ace2f34126085d9c936d487222135acc4a86281809615a81`. Verified safe regular-file/no-duplicate/no-traversal membership, all 90 manifest members (89 retained text files plus input-lock.json), exact size/hash/source links, and recorded source/checkout preservation. No FITS or native executable was opened/executed during agent interpretation.

The collector's displayed “partition_pafs” totals of 10/12 include five config-resource PAFs in each project. Executed partition evidence is five OCAM local PAFs/commands and seven WFI local PAFs/commands. These local PAFs all equal their project instrument PAF and the captured current repository instrument PAF. There is no observed partition override in these twelve retained command cases. Two additional WFI calibration-list directories have no matching command/PAF in this snapshot; do not invent a run history or launch reductions to fill it.

| Instrument | Detectors | Executed partition records | Constructor keys per record | Diagnostic comparisons | Science list sizes |
|---|---:|---:|---:|---:|---|
| OmegaCAM | 32 | 5 | 585 | 2925 | 5 in one partition |
| WFI | 8 | 7 | 249 | 1743 | 3 + 1 + 1 |

Verified all 4,668 constructor key/value diagnostic comparisons without mismatch or missing keys. Current source has 151 getter templates (137 global, 14 per chip), all mapped to legacy destination/storage/conversion plus a proposed immutable-owner domain. WFI's repeated MEF.MASTER.BIAS.KEY and .COMMENT have identical values and remain recorded as two occurrences each. Six PAF keys per instrument are not read by this constructor; retain them as compatibility evidence rather than declaring them invalid or deleting them.

All eight captured repository CFG/PAF identities match current Git source. The constructor/header/CLI/qfits PAF decoder Git identities are identical at private-install source e41525ed318f81e8b9ba9e6df538b4cb6758dc1f and current main 7341c895e9e1eb7008915e1e2cf961532b7eb8a6. Retained commands name the isolated native engine, while the current user executable CFG still selects the historical installed engine; this distinction is preserved, not changed. CLI uses only file/list/output bindings and save flags here; no numeric CLI override appears. All commands use the legacy cwd-default mefpp.paf and none specifies --pafname.

The WFI native-stage.json intentionally preserves the earlier checker stop on missing GAIN. Its retained native-inspection report has no failures and all detector pixel checks true; later normalization/astrometry reports record success. Preserve that historical failure and #131; it is not a new native reduction failure or a reason to reopen accepted Stage 2.1 or rerun processing.

### Typed mapping and remaining runtime proof

[Source/log-derived baseline](../architecture/proposed/m1/effective-settings-baseline.json) contains the 151-site registry, two profile/value models, twelve CLI/request records and ordered list membership. [Typed-state split](../architecture/proposed/m1/typed-state-split.md) distinguishes immutable config/default product mappings, request overrides, mutable work and owned results/qc.

The finite analyzer `probes/analyze_m1_effective_inputs.py` verifies this exact archive/current-source identities and reconstructs the observed text form of qfits first-key/ASCII-quote handling. It is not a replacement PAF decoder. Numeric model values preserve explicit integer conversion and float-temporary narrowing, including five double fields loaded through float. Logs round numeric values; model values are source-derived, not measured full-precision runtime values. Field roles/layouts remain design guidance until implemented.

Agent checks passed: archive/manifests/source identities, exact project/partition/template comparisons, finite source getter/type coverage, CLI option bindings/list counts, all retained constructor diagnostic comparisons and reproducible model generation. No native rebuild, engine launch or numerical/scientific test occurred. The generated baseline SHA256 is `67fdbabb855f4f0cc2e6f856a57fd5aa3d5d4addbdaaa3cd66bd3c86c969c1f4`.

The baseline prerequisite is now interpreted. Next implement the C90 owned typed configuration/lifecycle snapshot and normalized settings comparison through the existing PAF path, without calling mef_engine or using legacy -d as a dump-only command. Full-precision old/new runtime equality, resource-lifetime controls and actual-host implementation qualification remain pending. No new numerical defaults, QC estimators, metadata repair or TOML runtime path is introduced by this receipt. No further host commands/reductions are required for this text-analysis receipt.

Earlier preparation/collection-pending language below is chronological history and superseded only for this collected/interpreted prerequisite.

## Immediate action and output

Prepared `probes/collect_m1_effective_inputs.py` reads the original private pilot projects under `/Users/fselman/Software/build/wenu-imaging/mac-stage2-1-install-rBleOnWB/pilot-5-per-instrument`, instruments omegacam/wfi. Retain partition/project PAFs, known Pycavi/instrument CFGs, native .list text, mefpp_command.txt, mefpp.log and the parent native-stage logs. Include immediate project JSON reports, normalized normalization/astrometry reports, the private executable configuration, current user executable configuration and repository PAF/CFG comparison templates. The normalized data tree is not traversed. A known retained engine binary is hashed, not executed.

The collector never reads FITS pixels/headers, imports Pycavi/scientific packages, invokes native tools, changes cwd/environment, rebuilds or repeats reductions. It writes one fresh archive outside the projects/checkout, containing original text bytes, an input-lock.json and a size/hash manifest. Report selected text-file identities before/after reading and unchanged checkout. Native/Python installations and observations stay untouched.

Guards: actual Mac/OS, Python prefix/version, clean main/exact HEAD/upstream/origin; finite per-file/aggregate/traversal bounds; regular text bytes only, symlink targets recorded but not followed; retained private engine SHA256 5acd03bc33f1413e475c71130af9f4d7bb81e9547092417fbec6f2b1a44e8d01. Missing optional files and skipped symlinks are explicit. Stop on unexpected required inputs/identity, undecodable/binary text or exceeded bounds rather than silently widening scope.

Agent checks passed: Python syntax, wrong-host rejection before target access/writes, and selector controls showing native PAF/list inputs selected and FITS names excluded. Target collection remains pending. This is text/evidence collection, not functional processing or proof of effective-value equivalence. Expected status: M1-text-input-lock-collected-awaiting-interpretation. Collector SHA256: 87806da616acef0761ace99d8ac59360829470ce5ba09c2d28636ee0ccb832aa.

## Interpretation and following implementation

After independently inspecting the returned bundle, compare original partition-local PAF bytes with project/repository templates; recover actual CLI/list bindings and explicit precedence/defaults using current constructor/option source. Retain duplicate PAF occurrences and source provenance. A last-command file may have overwritten prior invocations; parent logs are supporting evidence, not an assumption that history is complete. Current retained files alone cannot prove they were unchanged throughout every historical operation. Record gaps without rerunning accepted science to fill them.

The existing [migration ledger](../architecture/proposed/m0-m0a/configuration-migration.md) is source/lexical evidence, not a native decoder. Preserve actual integer/float/string conversions, missing-key defaults, product-prefix/header mappings and Pycavi normalization ownership. Do not replace configured gains with characterized values, invent QC estimators, repair #133 or change numerical settings.

Next concrete M1 increment: map the observed settings to configuration/request/context/result ownership; implement lifecycle/status helpers and the normalized settings dump through the existing PAF path. Qualify the accepted template's success/invalid/partial-construction/failure lifetime rules and compare old/adapted effective settings field by field before numerical extraction. TOML reader/build integration remains M2; no new ASDF install or dependency test replay is needed.
