# Actual Mac and real-product validation — 7 November 2026

Owner ran the selected-build qualification at native revision f95cc9b333be9e53d2695d77d643906ce06222ab. All build, clipping, mask-policy, clipped/reason/limit/legacy profiles, shared-policy and four-product FITS/ASDF gates passed. Receipt: `scalar-qc-qualification-c17/clipped-ron-project-bpm-f95cc9b333be/qualification.json`. Subsequent owner-run identity check matched the executable SHA256 to that receipt. No native rebuild is required for the comparator changes below.

Real normal-directory run completed all 32 detectors and ten raw inputs with explicit all selection, unchanged structural binary BPM (1 good), raw pair 0/1, 5-sigma low/high and maximum 10 iterations. Product: `/Users/fselman/Pictures/OCAM/test_recipes/reduced/cal/bias/CMDP.2026-11-07T21:05:44.919Z.001.{fits,asdf,log}`. Processing backup, console and preservation receipt are under `test_recipes/orchestration/bias-clipped-ron-real-qwhqwlq6/`. Raw and earlier-product identities were unchanged.

Owner-reported read-only real QC check passed the ASDF schema and all **97,157** FITS/ASDF scalar/context comparisons. All 32 clipped RON estimates are available and converged in two or three passes. They span 1.92924 ADU (#66) to 2.51573 ADU (#95); existing MAD remains 2.09671 ADU. No scientific interpretation beyond the measured comparison is implied.

The saved comparator now has opt-in `--allow-clipped-ron-additions`: exactly sixteen named measurement additions, six exact processing-policy fields, matching header groups and complete native FITS/ASDF mapping. Every reference measurement/value/definition/source and input QC remains strict. Existing un-clipped RON cannot be exempted. Only exact own-product identities are normalized. Four agent comparator-control tests passed; the actual real-master pixel/legacy-QC comparison is the next gate. The default comparator behavior stays strict. `--source-root` selects the matching schema/registry from the retained mutable source without modifying it. Comparator-only commits do not change the native producer revision or call for a relink.

Earlier pending-Mac statements below are historical and superseded by this owner-reported qualification. Full receipts/log archives have not been uploaded to the agent environment. No merge, installation, cleanup or further reduction was performed.

---

# Optional bias clipping and shared project BPM policy

Implementation for issue #284. Owner-reported actual Mac qualification and the full 32-detector run passed on 7 November 2026; final retained-master pixel/QC comparison is pending. The owner authorized sigma clipping, selectable zero-good reason masks, project-wide processing TOML policy and efficient processing. The reviewed contract is [the design](design/bias-clipping-project-bpm-v1.md); the mathematical guide is maintained in [LaTeX](mathematics/mefpp/bias-clipped-ron.tex) and [PDF](mathematics/mefpp/bias-clipped-ron.pdf).

## Configuration

No new detector CLI blocks are needed. The invocation remains the existing launcher or native `cal bias --config /absolute/bias-recipe.toml --bias /absolute/bias.list --output-dir /absolute/reduced/cal/bias`. The recipe envelope still supplies paths, HDUs and geometry. The *shared numerical processing TOML referenced by its `settings` field* supplies the following optional fields inside its existing `[native]` table (schema 1 or 2):

```toml
"BPM.ENCODING" = "reason8"
"BPM.BAD_WHEN" = "nonzero"
"BPM.REJECT_BITS" = 255
"BPM.REGISTRY" = "WENU_BPM_V1"
"QC.RON.CLIP.ENABLED" = 1
"QC.RON.CLIP.LOW" = 5.0
"QC.RON.CLIP.HIGH" = 5.0
"QC.RON.CLIP.MAX_ITERATIONS" = 10
```

These are fields within the existing table, not another `[native]` declaration. Use the actual BPM registry; the reader refuses missing/mismatched REASON8 metadata. Existing structural masks are binary and must stay binary. For the retained structural OmegaCAM mask use only:

```toml
"BPM.ENCODING" = "binary"
"BPM.BAD_WHEN" = "zero"
```

The opposite binary polarity uses `"nonzero"`. REASON8 supports all byte values and preserves reason bits; `reject_bits=255` accepts exactly zero. Explicit lower rejection masks use the existing `(flags & reject_bits)==0` rule. Neither encoding is guessed. Remove per-detector `bpm_good_value` when using a reason policy. An identical binary legacy value is tolerated; conflicting values fail before product creation. Entirely absent groups preserve legacy snapshots and behavior. Explicit clipping enabled=0 keeps the chosen settings in provenance and runs the old statistics path. Clipping needs an explicit raw RON pair.

Schema 3 uses the same native fields through its registered typed descriptors:

```toml
[processing.bpm]
encoding = { value = "reason8", unit = "none" }
bad_when = { value = "nonzero", unit = "none" }
reject_bits = { value = 255, unit = "1" }
registry = { value = "WENU_BPM_V1", unit = "none" }
[processing.ron_clip]
enabled = { value = 1, unit = "1" }
sigma_low = { value = 5.0, unit = "1" }
sigma_high = { value = 5.0, unit = "1" }
max_iterations = { value = 10, unit = "count" }
```

This supplements a complete existing schema-3 document with `[processing] schema_version=1`. Composition uses the shared reader and frozen source metadata. Policy is stored in the immutable configuration and cloned with it, never in mutable process-global state. It is not independently overridable per detector. Existing native BPM and linearity preparation consumers reject contradictory explicit mask choices. Installed legacy Eclipse commands that do not read project TOML retain their old input interface; generic internal maps are not reinterpreted. The old one-detector JSON adapter refuses clipped/reason policies it cannot publish faithfully; the native standalone recipe implements them.

## Output

`read_noise.clipped` is separate from `read_noise` and `read_noise.mad`. It uses the same selected raw pair, before any scan correction, and becomes unavailable for insufficient retained samples or nonconvergence. Final mean/median/stdev, retained/BPM/nonfinite/low/high counts, iteration count, convergence, thresholds and limit have distinct additive FITS/ASDF mappings. The clipped definition carries `median_centered_monotone_sigma`; FITS carries `CLIP=MEDSIG`. Legacy cards retain their meanings and values.

The typed processing snapshot records complete BPM interpretation. Additive scalars record encoding (1 binary, 2 REASON8), zero/nonzero polarity and rejection bits; REASON8 also records `extensions.bpm_registry` and `ESO MPP QC BPM REG`. It does not mislabel a reason mask as binary `bpm.good_value`. Schema 2.0.0 accepts the new optional registry extension without weakening existing requirements. Updated readers/schema are required for this additive extension.

## Agent checks actually executed

- Sixteen changed C translation units passed strict C17 syntax with `-Wall -Wextra -Werror -pedantic-errors`; the external ASDF headers were treated as system headers, matching their third-party status.
- Actual C/UBSan clipping probe passed 300 independently sorted oracle cases, mask/nonfinite accounting, averaged even medians, constant populations, asymmetric cuts, iteration limits, invalid options and input/output immutability.
- Native FITS ingestion passed identical normalized selections for both binary polarities and REASON8 bytes 0/1/2/128/255; strict binary reinterpretation and wrong registry were refused. Exact-byte helpers were reused.
- Four existing actual bias QC/lifetime profiles and opt-in actual-kernel clipped, reason-policy and nonconverged-limit FITS profiles passed. Full native ASDF execution was not substituted or claimed.
- Thirty-six processing-policy cases passed native/domain equivalence, unchanged legacy field values, invalid/partial group refusal, clone lifetime and allocator-failure checks.
- Shared domain regression passed eleven typed/document/lifetime profiles and twenty-five unit/domain rejection/recovery cases; catalogue has 151 required compatibility templates plus eight optional processing fields.
- Schema meta-validation, changed Python syntax and whitespace checks passed. The two-page PDF was compiled from its LaTeX source and visually inspected.

Detector-sized synthetic pair: 2048 x 4100 pixels, two iterations, 67,174,400 scratch bytes, 0.531234 CPU seconds in the instrumented agent executable. This is one synthetic agent-host observation, not Mac performance acceptance. The buffer is allocated once and compacted in place, without per-iteration allocation, image copying, sorting or I/O. Wirth selection has typical linear work, not a claimed worst-case bound.

Retained preparation failures were test harness issues: duplicate source on first linker command, a sentinel substituted for a complete TOML fixture, and an incorrect CLI-probe dispatch for the first broader configuration regression. Corrected invocations passed. The initial LaTeX environment lacked generated formats/font maps; a private scratch format and explicit installed font maps produced the reviewed PDF. No project/Mac dependencies were installed.

## Next actual Mac gate

`mefpp2/tests/qualify_bias_clipping_mac.py --repository /Users/fselman/Developer/wenu-imaging --revision FULL_CANDIDATE --preflight` checks the selected source/build/cache/tools without writes. It expects clean main de3c5f3 and the selected configured baseline 3cae0756. Review that output before the mutation run. The mutation mode retains the old recipe, cache and changed source files, changes only the revision cache entry, and rebuilds affected existing targets in the same build. Its bounded tests use tiny synthetic FITS fixtures and the real native writer with independent Astropy/ASDF verification. No observational raw files, retained products, installed recipe or orchestration configuration are changed. The helper performs no fresh `cmake -S/-B`, clean or dependency build/export. A selected-build mismatch stops that gate.

The four-product Mac recipe contract is prepared, Python-syntax checked, and **not executed here** because this environment has neither the qualified native ASDF runtime nor Astropy. It checks equivalent mask encodings, clipping enabled/disabled, exact legacy reference pixels/cards, independent NumPy clipped values, complete FITS/ASDF mapping, producer revision, configuration snapshot and four conflicting per-detector refusals. Do not close #284, merge, rerun observations or install based on agent checks alone.
