# Recipes and products

Recipes specify the ordered processing; reduction profiles specify scientific or
visual purpose; product profiles specify output/compliance requirements. Keep
these concepts separate. Pycavi orchestrates; native recipes can run independently.

## Bias

The standalone command accepts a recipe TOML, ordered absolute input list and an
existing output directory:

```sh
mefpp_bias_recipe cal bias --config /path/to/bias-recipe.toml \
  --bias /path/to/bias.list --output-dir /path/to/products
```

The TOML must explicitly define settings, detector/configuration/HDU bindings,
readout/binning/amplifier identity, BPM selection and measurement choices. See
[the recipe configuration reader](../mefpp2/ins/mef/common/mef_bias_config.c)
and [scientific guide](developer/bias-recipe-mathematical-guide-v1.pdf) for the
supported contract. A complete `--output FITS` may replace `--output-dir`; supplying
both is refused. Input lists, configuration and outputs resolve explicitly; the
recipe does not discover inputs from an observing directory.

The recipe admits every binding, processes detectors serially, verifies coverage,
assembles the final mosaic FITS and writes native ASDF QC. It corrects scan level,
trims, rejects whole frames and stacks accepted frames with the selected temporal
median convention. Exact zero spread stops with detector/input diagnostics.
The code and scientific guide define estimator and mask details.

Generated products use `CMDP.<recipe-start-time>.001.fits` with `.asdf` and `.log`
siblings. Each final product has one QC sidecar, including input membership and
provenance. Existing destinations are refused; failed work remains available for
inspection. Success requires zero exit and complete products. Stored QC uses ADU.

For read-only product comparisons use
[`compare-bias-products.py`](../tools/compare-bias-products.py) with its `--help`.
The QC viewer reads saved ASDF; plotting does not recompute scientific results.

## BPM / linearity

The single [BPM/linearity guide](developer/bpm-linearity-guide.pdf)
([source](developer/bpm-linearity-guide.tex)) covers the recipe's command,
settings/defaults, detector flow, robust response BPM, measurements, FITS/ASDF
products and QC. The public command contract is:

```sh
mefpp_recipe cal bpm-linearity --config RECIPE.toml --qc false
```

The unified command and direct native recipe admission are unfinished on the
feature branch; this is the agreed interface, not a qualified execution example.
OCAM/WFI TOMLs remain authoring templates until actual bindings and the native
interface are qualified. Project TOML owns roots. The recipe shares one processed
cube per detector, skips BPM creation when a mask is supplied, and records
measurement-only linearity diagnostics. It applies no physical linearity correction.

## Other processing

The legacy mefpp command and Pycavi workflows remain available. Flat and science
processing retain their own dependencies and collective operations. Their
standalone interfaces and real-data acceptance cases must be qualified before
being advertised as completed refactored recipes. Cross-talk remains deferred.
