# Native flat-field recipe design

Status: proposed for scientific and implementation review.

## Entry points and products

Use one coordinator with explicit dome, sky, and combination paths. Each public
entry selects a named result and uses the common recipe lifecycle, detector
bindings, MEF assembly, and native ASDF publication.

| Entry | Inputs | Result |
| --- | --- | --- |
| `cal domeff` | Compatible master dome flat or classified dome exposure list | Master dome flat |
| `cal skyff` | Compatible master sky flat or classified sky exposure list | Master sky flat |
| `cal mff` | Dome and sky supplied independently as a compatible master or a classified exposure list, plus bias and BPM according to the selected processing policy | Combined master flat |

A compatible supplied master is reused and identified in the receipt. A list
requests construction. A required bias may likewise be a compatible master bias
or a classified bias list. The selected path and processing policy determine
whether bias is required. Legacy flat construction and combination apply bias at
different stages than an exposure-by-exposure bias correction would.

Use the [four-file configuration contract](../architecture.md#four-file-native-configuration).
The recipe owns the role and the explicit source choice for each input. A list
uses the absolute path and classification format in the architecture. Validate
the input role, instrument, detector and HDU mappings, filter where applicable,
binning, readout, geometry, and normalization lineage before use.

The first implementation qualifies each processing path with its dependencies
already supplied. The shared planner subsequently enables construction from
lists for dependencies. It resolves the entire graph, deduplicates identical
requests, and reports every missing prerequisite together. It presents the
complete plan and obtains approval before building any additional products.
For example, `cal mff` with a dome master, sky list, and bias list can reuse
the dome, build the bias and sky master, and then combine. Record each generated
product as a dependency with its own FITS/ASDF pair and preserve supplied masters
as read-only inputs. See the [dependency contract](../architecture.md#dependency-checking-later-development).

## Legacy numerical baseline

- **Dome and sky.** `mef_build_cal` in [mefp_lib.c](../../../mefpp2/ins/mef/common/mefp_lib.c)
  applies configured scan correction and trimming before frame admission.
  Frame means must lie strictly between the corresponding dome or sky bounds.
  For each accepted frame, it clips pixels within the configured normalization
  rectangle using the frame mean and a noise scale
  $\sigma = \sqrt{(\mathrm{RON}/g)^2 + \bar I/g}$, where $g$ is the
  configured gain in electrons per ADU. It divides the frame by the median of
  the retained normalization pixels, then takes a temporal median at each pixel.
  It scales the resulting detector flat by the ratio of that detector's mean
  frame normalization level to the reference extension's level. Preserve the
  legacy reference-extension binding, comparison bounds, and median convention.
- **Combination.** `mef_ff_combine` uses the stored or reconstructed reference
  normalization levels. When bias subtraction is enabled, it subtracts
  $B/m_D$ from the dome and $B/m_S$ from the sky before taking their ratio.
  The output is $D'\,\mathcal{S}(S'/D')$, with $\mathcal{S}$ the existing
  smoothing kernel and mask policy. Preserve the denominator handling, edge
  behavior, and operation order. Use working buffers for the mutable inputs.
- **Review before implementation.** Trace reference normalization when a
  component comes from disk, including legacy header or pixel-derived values.
  Check the effect of detector subsets and order. The near-zero frame-median
  branch logs an error with its early return commented out. Establish the
  reference behavior and agree any policy change before changing the port.

## Qualification

Start with the retained WFI Trapezium and OmegaCAM CP Pup datasets. Resolve the
actual component lists, master bias and BPM, detector/filter/readout bindings,
configuration revision, legacy executable, and available reference products on
the qualification host. Pin their identities and hashes before the native
runs. Exact dome, sky, and combined reference paths remain to be established.

Compare dome, sky, and combined products separately. Check accepted frame order
and counts, scan and normalization records, detector/reference mappings, FITS
geometry and scaling, pixels, and native ASDF lineage. Start with exact
numerical comparisons against matching legacy inputs. Investigate differences
before proposing any tolerance. For the planner, exercise both product/list
directions, two lists sharing one bias request, missing or incompatible sources,
and approval or refusal. Compare results built from lists with the same
explicit standalone sequence.
