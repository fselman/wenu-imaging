# Bias product-path foundation, 6 November 2026

## Executive summary

A small native C module now implements the agreed product destination and
filename rules. It prepares matching FITS/ASDF/log paths without creating files,
changing directories, reading images or requiring Python. It is not yet wired
into the bias recipe. The bias arithmetic and existing publishers are unchanged.

Agent strict-C17 output-rule checks pass. Actual Mac compilation, native ASDF
integration, final mosaic MEF assembly and the real-data recipe run remain
pending. This is a foundation increment, not completion of the bias recipe.

The owner's full agreed direction and remaining review boundaries are in
[the design record](design/bias-mef-native-asdf-v1.md). That record supersedes
older assumptions about Python-owned final ASDF, separate per-input sidecars,
final detector files and immediate viewer work for the new bias path.

## Changed boundaries

- mef_product_paths.h/.c: explicit destination selection, output parent
  extraction, generated CMDP/SMDP names, inherited ASDF/log stems, no-clobber
  preflight and UTC timestamp capture/formatting.
- product_paths_probe.c: thin native test driver around the real helper.
- product_paths_contract.py: dependency-free synthetic tests; it compiles the
  helper directly with the caller-selected compiler and records exact argv.

No CMake target, installed engine, numerical source or existing CLI is changed
by this isolated foundation. The new module will be linked when the complete
standalone native publication path is connected. Existing source/build/runtime
qualification and old scientific products are not rerun or changed here.

## Actual agent checks

Eleven output-rule controls passed under /usr/bin/cc with strict C17,
-Wall -Wextra -Werror -pedantic-errors. The final run reported 0.040 s for
controls (not a processing benchmark). The build and test inputs are recorded
in product-paths-results.json in the retained agent test directory.
The fixed-clock controls include second=12/fraction=.340, year rollover and
leap day. Neither ASDF nor image recipe execution occurred.

Git comparison against8dc026e confirmed mef_cal_bias.c, mef_bias_kernel.c,
mef_bias_files.c and mef_operation_template.c unchanged. Patch whitespace
checks passed. Target compiler/ASDF/real-data acceptance remains unclaimed.
Refs #245 and #207. This new helper does not close #207's legacy integration,
header identity, concurrency-reservation or compatibility acceptance.

## Remaining acceptance

Use the retained external libasdf prefix; do not install a dependency to test
this path-only increment. Native QC must contain the agreed product and embedded
input information; a fake/stub writer is not recipe completion. Actual full
mosaic acceptance must launch the real recipe in orchestration, read immutable
raw data and write the MEF/ASDF/log to the explicitly selected products directory.
The final MEF is the published product; detector results are temporary.

The later plot producer writes plots once, then the existing viewer is adapted
with a Bias recipe sidebar and product selector. No viewer changes are included.
