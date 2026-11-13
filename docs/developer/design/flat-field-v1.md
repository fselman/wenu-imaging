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
- **Normalization lineage.** The legacy list path stores the mean of the
  accepted per-frame normalization medians before scaling the stacked flat.
  The legacy FITS path recomputes a median from the loaded normalized detector
  plane. With bias subtraction enabled, the combiner uses the reference slot
  for each component's scale. The retained combined flats exercise a loaded
  dome and a sky built from a list. A two-master replay needs its own legacy
  comparison with both components loaded. Record the origin and units of the
  scale used for each component and test reference detector selection.
- **Near-zero frame median.** The legacy code logs an error at
  `fabs(medval) < 1e-4` and leaves the plane unscaled in the temporal stack.
  It omits that plane from the normalization sum and count. If every plane
  takes that branch, the subsequent normalization divides by zero. Rejecting
  such a stack before publication is a proposed behavior change and requires
  review before implementation.

## Qualification

Use the retained WFI Trapezium and OmegaCAM CP Pup reductions recorded in the
[effective-settings baseline](../../architecture/proposed/m1/effective-settings-baseline.json).
The partitions below identify the calibration sequences. Timestamps are as recorded
in that baseline.

| Dataset | Filter | Dome partition | Sky partitions |
| --- | --- | --- | --- |
| WFI Trapezium | `BB_B_99_ESO842` | `100123319`, 2001-12-10T19:51:55 | `100123337`, 2001-12-11T00:07:12 and `100123366`, 2001-12-11T09:05:21 |
| OmegaCAM CP Pup | `r_SDSS` | `574184`, 2017-03-14T09:41:34 | `200253584`, 2017-03-13T23:12:13 |

### Retained reference products

On the Intel Mac, the validation tree is
`/Users/fselman/Software/build/wenu-imaging/mac-stage2-1-install-rBleOnWB`.
The legacy `native/bin/mefpp` under that root has SHA-256
`5acd03bc33f1413e475c71130af9f4d7bb81e9547092417fbec6f2b1a44e8d01`.
Paths below are relative to its `pilot-5-per-instrument` directory. Each
list checksum identifies the original ordered list.

**WFI dome**

`wfi/calib/dome/100123319/BB_B_99_ESO842/2001-12-10T19:51:55`

- `dome.list` — `767211e33a963738e8c357e5c5c5250364e232b9b85f628299fe93af6b1b31e6`
- `WFI_DOMEFF_BB_B_99_ESO842_1x1.fits` — `cc592e492516131a5e7aa3048269db6f08e0eaefa04859c9c5dfdf97f6757458`
- `mefpp.paf` — `7d7a7bde5edac6d593727c5eef2a08007b84f48a7e2a7d8bdec811e4b399990c`
- `WFI_MB_1x1.fits` — `49103e80ae950e02fd6264ad3e82f3d389a4ebe1173842feabf1e2995c593920`
- `WFI_BPM_1x1.fits` — `b27a5bc40f3239b389835a3964bac88fffc7e61d76ca758d10a43efbe96ac9f2`

**WFI early sky**

`wfi/calib/sky/100123337/BB_B_99_ESO842/2001-12-11T00:07:12`

- `sky.list` — `9f1b3605a396349afa282d05c72609a20f74f39524e7672e92f0775a57a19ba0`
- `WFI_SKYFF_BB_B_99_ESO842_1x1.fits` — `dab281b9c614603a80aa519a2115c3a2a2c345f994914d64391aa0363861db24`
- `WFI_MFF_BB_B_99_ESO842_1x1.fits` — `abaa374adcdf502b2a6cf97f7085a00f1624725c29de97ba301cc86e18c7a539`

**WFI late sky**

`wfi/calib/sky/100123366/BB_B_99_ESO842/2001-12-11T09:05:21`

- `sky.list` — `07e707bb1298aee9648c92836f54d5c3d02753e01b75c3931478b2ca1ceb5310`
- `WFI_SKYFF_BB_B_99_ESO842_1x1.fits` — `a6ba15032d7c2047aca9e24574d54e5e9c8fecfd89efdd691734fbf1eeed7867`
- `WFI_MFF_BB_B_99_ESO842_1x1.fits` — `a3b359701a07814296ce44aedc3d0983765f2ee8bfead901c91bbc9eef15f025`

**OmegaCAM dome**

`omegacam/calib/dome/574184/r_SDSS/2017-03-14T09:41:34`

- `dome.list` — `71525a00316168cafdb6400638ba24b950d974fc159bb210507777f0d82b752f`
- `OCAM_DOMEFF_r_SDSS_1x1.fits` — `dcefcbeab6a8670a6d1698570c1ea9184a86261e54c6c54876a40b1d5405369c`
- `mefpp.paf` — `709d65acdeea6c889ed1468cbb3966d5de93ec654ee030032a096ca12624333f`
- `OCAM_MB_1x1.fits` — `4297cf8ce8dcc38df7ea134a9ee080a7e640d67563bd27abc6c9b44cc72e8597`
- `OCAM_BPM_1x1.fits` — `5572b31edd209f1bf99d28ebda403af208e9a1807e9a90d13894f292e2bd912a`

**OmegaCAM sky**

`omegacam/calib/sky/200253584/r_SDSS/2017-03-13T23:12:13`

- `sky.list` — `eef0fa51807b4a341ba20590a28d297a3316ed293bf5eea667b5887b0b1413fc`
- `OCAM_SKYFF_r_SDSS_1x1.fits` — `a4228d6496cd7f3eaacef920d71e314166b2887313b401abf4458157db83380a`
- `OCAM_MFF_r_SDSS_1x1.fits` — `05ba46ff9a175039b4d555256d472c28d90ebeac527ea4d08efa417a43798c39`

In each instrument's sky partitions, the staged dome flat, bias, BPM, and
`mefpp.paf` match the corresponding dome partition by SHA-256. The generic
`config/mefpp.paf` files have a different checksum. For OmegaCAM the CP Pup
science master bias also has a different checksum
(`7b848756732aa017b5ece19f5744baacf317309e913b173b51fee07d75994e1f`).
Use the calibration-stage bias for the flat comparisons.

| Science partition | Combined flat matches sky partition |
| --- | --- |
| WFI Trapezium, 2001-12-11T01:59:14 | `100123337` |
| WFI Trapezium, 2001-12-11T07:08:55 | `100123366` |
| WFI Trapezium, 2001-12-11T08:32:20 | `100123366` |
| OmegaCAM CP Pup, 2017-03-13T01:57:49 | `200253584` |

The matches above identify retained files by checksum. Qualification still
requires confirming the raw-list members and detector/HDU and readout bindings
and comparing the numerical outputs.

### Legacy replay with two supplied masters

The Intel Mac replay under
`/Users/fselman/Software/build/wenu-imaging/flat-two-masters.l0MVKW8m`
loaded the retained dome and sky FITS, bias and BPM. It used the same legacy
executable and partition PAFs listed above. The replay command supplied
`--bias` and omitted `--biassub`. In the legacy engine, `--biassub`
enables scaled bias subtraction during combination.

| Replay directory | Output FITS SHA-256 | Detector extensions | Exact physical pixels | Built sky first-HDU FRMEDIAN |
| --- | --- | ---: | ---: | ---: |
| `wfi-100123337` | `0cbb8afd20fc7b286ef6d6fced08114024f836e7036b3be70ddc5df1452c6353` | 8 | 66,994,144 | 12516.014648 |
| `wfi-100123366` | `f35b7e1635d3e0580f8a25017d6d699ab3625b6340981958d8da3b822396d6ff` | 8 | 66,994,144 | 15379.883789 |
| `ocam-200253584` | `30e08e146017e4a499e64a9d04358e61e7c0b3467940976704643da64f41bb23` | 32 | 267,584,128 | 17304.685547 |

The replay filenames are `REPLAY_MFF_BB_B_99_ESO842_1x1.fits` for WFI
and `REPLAY_MFF_r_SDSS_1x1.fits` for OmegaCAM. Each matched its
retained sky-list reference in detector order, image shapes and every physical
pixel after FITS scaling, with zero nonfinite pixels in either product. File
checksums differ. The logs contain neither loaded medians nor bias-subtraction
messages. The table gives the built sky's header value. A paired replay with
`--biassub` on both routes is needed to qualify the scaled-bias path.

### Native checks

Compare dome, sky, and combined products separately. Check accepted frame order
and counts, scan and normalization records, detector/reference mappings, FITS
geometry and scaling, pixels, and native ASDF lineage. Start with exact
numerical comparisons against matching legacy inputs. Investigate differences
before proposing any tolerance. For the planner, exercise both product/list
directions, two lists sharing one bias request, missing or incompatible sources,
and approval or refusal. Compare results built from lists with the same
explicit standalone sequence.
