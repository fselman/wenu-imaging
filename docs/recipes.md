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
[the recipe configuration reader](../mefpp2/ins/mef/common/mef_bias_recipe_config.c)
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

The native entry point is
[`mefpp_bpm_linearity_recipe.c`](../mefpp2/ins/mef/recipes/mefpp_bpm_linearity_recipe.c).
It follows bias's admission, serial detector loop, verification, publication and
cleanup phases. See the [guide](developer/linearity-preparation-guide-v1.pdf)
and [recipe example](../config/recipes/omegacam-bpm-linearity.example.toml).

The recipe TOML selects `[native_recipe]` with one executable and source revision,
plus an assembly reference detector. Project TOML owns raw, orchestration and
reduced/calibration/work/log roots. Pycavi validates the historical archive/master
bindings and writes explicit frozen native bindings in orchestration; it invokes
one C recipe, then checks saved products and writes the orchestration manifest.
The native recipe calls preparation and BPM in process for each detector, then
joins their final MEF/ASDF. It does not launch Python, a shell or child engines.
Given the authored bindings, it can also run directly from orchestration:

```sh
nice -n 10 mefpp_bpm_linearity_recipe cal bpm-linearity \
  --config bpm-linearity-recipe.toml --bindings RUN/native-bindings.toml
```

Bindings contain explicit native argument vectors and frozen file fingerprints;
they are an admission transport, not a second set of editable scientific policies.
Keep the TOML authoritative and regenerate bindings after changing it. The
existing per-stage recipe form remains readable for retained runs; select either
`native_recipe` or legacy `native`, never both. The new native coordinator needs
its own Mac ASDF gate and observational comparison before selection.

Linearity remains measurement only. Use the same admitted master/prior for both
stages; never feed the candidate mask back into its characterization population.
Native completion requires zero exit, final FITS/ASDF and an input-preservation
receipt. Partial products stay available after failures. The saved QC viewer
reads existing measurements and applies no physical correction.

## Other processing

The legacy mefpp command and Pycavi workflows remain available. Flat and science
processing retain their own dependencies and collective operations. Their
standalone interfaces and real-data acceptance cases must be qualified before
being advertised as completed refactored recipes. Cross-talk remains deferred.
