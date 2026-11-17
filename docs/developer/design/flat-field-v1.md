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

## Native flat preparation

Apply this sequence to each raw dome or sky exposure:

1. Subtract the overscan and trim to the active detector area.
2. If requested, subtract the matching overscan-corrected, trimmed master bias
   in ADU.
3. Reserved for future dark subtraction in ADU, before measuring the
   normalization median. This could support CMOS detectors operated near room
   temperature. The first implementation leaves this step inactive and exposes
   no dark input or option.
4. Measure the normalization median on the prepared exposure and divide by it.
   Median-stack the normalized exposures using the detector reference scaling
   described below.

Record the per-exposure normalization medians, the final master median, and
whether bias was applied. When applied, record the master-bias identity. The
combiner uses dome and sky masters as prepared. If the requested policy requires
bias-corrected flats, verify that status before accepting a supplied master.
Use the raw list to rebuild a master whose correction status cannot be
established.

### Component publication and combination

For each detector, retain the dome and sky master planes in memory until the
combined plane is complete. Stage each newly built component for publication
from its original plane. Publish the unsmoothed sky master as its own FITS/ASDF
product. Give the combiner a working copy of the sky plane for the in-place
division by the dome, then smooth the sky-to-dome ratio and multiply by the
dome. Use the resident planes for combination without rereading staged
products.

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
  behavior, and operation order of the ratio, smoothing and multiplication.
  Use working buffers for the mutable inputs.
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
messages. The table gives the built sky's header value. A paired replay with `--biassub` would characterize the legacy scaled-bias
path separately from native bias-before-normalization.


### Supplied-master command

`mefpp_recipe cal mff --config RECIPE.toml` combines two prepared normalized
master MEFs, with an optional active-area binary BPM. See the
[example configuration](../../../config/recipes/mff.example.toml). The recipe
binds enabled detector IDs independently in each master, checks the declared
instrument, filter, category, and compatible detector geometry, and requires an
explicit smoothing radius and reference detector. Configuration and each
input's SHA-256 and source HDU bindings travel with the product. The input files
are used as prepared. There is no bias operation at this entry point.

This route publishes the combined product from supplied masters.

### Single-detector dome qualification

`cal domeff` now accepts the classified dome exposure list, project TOML,
detector profile and explicit stack settings. The
[WFI example](../../../config/recipes/wfi-domeff.example.toml) selects
`WIN1.CHIP1.OUT1` as the normalization reference and sole output.
WFI screen exposures carry the original `FLAT,SCREEN` classification.
The legacy dome builder applied scan correction and trimming before
normalization and did not subtract the supplied master bias at that stage.
The first native comparison uses the same bias-off policy and compares with
the corresponding detector in the retained dome product.

The recipe resolves the detector HDU independently in every exposure.
Its FITS/ASDF product records the admitted files, source HDUs, exposure
participation and normalization medians. A synthetic CLI check exercised
scan correction, trimming, reordered HDUs, frame rejection, physical pixels
and validated QC records through a capture writer. On the Intel Mac using
the C17 Release build at `af5fcdc`, `native_domeff` passed in 2.69 s
with the native ASDF writer and independent reader. The real-data replay
from the five WFI Trapezium exposures in dome partition `100123319` wrote
FITS, ASDF and log products. All 8,374,268 physical pixels of
`WIN1.CHIP1.OUT1` matched the retained legacy master exactly. A second
replay with the same build used the five OmegaCAM CP Pup `r_SDSS` dome
exposures in partition `574184` and wrote FITS, ASDF and log products.
All 8,362,004 physical pixels of `ESO_CCD_#65` matched the retained legacy
master exactly.

### Full-mosaic dome qualification

Set `[flat].detector = "all"` to stack every enabled detector in the
profile and publish one MEF and one ASDF. Native slot 1 is the legacy
illumination reference. Compute it first, retain its mean frame
normalization in ADU and use it as the denominator of each detector's
illumination ratio inside the existing stack kernel. Publish in catalogue
order independently of processing order or raw HDU position. Resolve and
fingerprint each observation once during admission, verify its fingerprint
again before publication, and release each corrected cube and master plane
after staging that detector. The ASDF records the reference ID and preserves
per-detector exposure participation and source HDUs.

On the Intel Mac, the C17 Release build at `f3fab5f` passed
`native_domeff` in 3.56 s. The synthetic mosaic case checks reference scaling
with unequal illumination and distinct participation, a catalogue that
places the reference second, and swapped raw HDUs.

| Bias-off dome replay | Detectors | Physical pixels compared | Differences |
| --- | ---: | ---: | ---: |
| WFI Trapezium `100123319` | 8 | 66,994,144 | 0 |
| OmegaCAM CP Pup `574184` | 32 | 267,584,128 | 0 |

For both retained comparisons, the ASDF FITS digest, recipe snapshot, and
detector-to-output-HDU map verified.

### Native sky flats

Run `mefpp_recipe cal skyff --config RECIPE.toml` with
`skyff_recipe_schema_version = 1`, an absolute `[inputs].list` of classified
`FLAT,SKY` exposures, and the corresponding legacy sky admission bounds.
The command shares dome detector selection, scan correction, normalization,
stacking and MEF/ASDF publication. It selects the sky stack in the existing
kernel and writes the unsmoothed master with `PRODCATG = CALIB.MASTER_SKY_FLAT`.
The native route currently runs with bias subtraction disabled. Both
single-detector and mosaic sky checks are included in the synthetic contract.

The Intel Mac C17 Release build at `983ffb6` produced the two bias-off
sky mosaics below. Astropy `fitsdiff` 6.1.7 compared the detector extensions
in order at zero absolute and relative pixel tolerance.

| Retained sky replay | Detectors | Pixel differences reported |
| --- | ---: | ---: |
| WFI Trapezium `100123337` | 8 | 0 |
| OmegaCAM CP Pup `200253584` | 32 | 0 |

The FITS header-card counts differ between native and legacy products.
Both ASDF sidecars passed the FITS SHA-256, recipe snapshot and
detector-to-output-HDU mapping checks. Bias-enabled component construction
remains pending.

### Native checks

The `native_flat_stack` analytical test passed on the Intel Mac in a C17 Release
build of `a55713d5c097083469c7a6d0ba0170ce4e3631a7`. It checks optional master-bias
subtraction, frame admission, and per-exposure normalization before stacking.
The expanded `native_flat_stack` test also passed on the Intel Mac (C17 Release,
`3de15b1d3d7fb334ea1333769fd7d16fdef804ca`, 1.62 s). It verifies ratio
smoothing with and without a bad-pixel mask and bytewise preservation of the
original dome and unsmoothed sky detector planes.

A Linux synthetic CLI run verified independently ordered component HDUs, exact
combined FITS pixels, unchanged master files, and rejected a filter mismatch
before output. A capture harness validated the ASDF writer's input records.
On the Intel Mac, `native_mff_masters` passed in 1.29 s using the C17 Release
binary from `a9ab280` and the independent reader check from `3fcda0e`. The
test checked exact FITS pixels, input preservation, ASDF product and input
hashes, calibration roles, and detector-to-source HDU bindings.
### Native two-master results on the Intel Mac

On 2026-11-17, the C17 Release `mefpp_recipe` build from `a9ab280`
combined the retained dome and sky masters for the two cases below. The
comparisons used the pinned two-master legacy replays, matched detector
extensions by identity, and compared physical pixel values after FITS scaling.

| Partition | Detectors | Exact physical pixels | ASDF |
| --- | ---: | ---: | --- |
| WFI Trapezium `100123337` | 8 | 66,994,144 | Verified |
| OmegaCAM CP Pup `200253584` | 32 | 267,584,128 | Verified |

For both cases the independent checks verified the recipe snapshot, output
FITS SHA-256, and the dome, sky and BPM identities and per-detector source
HDU bindings. Both runs used BPM copies with structural FITS header repairs
and verified preservation of the stored mask payloads. The native run for
WFI's late sky partition `100123366` and qualification of list-driven
component construction are outside these two results.

### Bias-off qualification from raw lists to combined flats

On 2026-11-17, the Intel Mac C17 Release build at `983ffb6` ran
`cal mff` with the native mosaic products from `cal domeff` and
`cal skyff` above, plus the prepared instrument BPM. Both runs used
smoothing radius 7 and BPM good value 1.

| Instrument | Dome partition | Sky partition | Detectors | Physical pixels compared | Differences |
| --- | --- | --- | ---: | ---: | ---: |
| WFI Trapezium | `100123319` | `100123337` | 8 | 66,994,144 | 0 |
| OmegaCAM CP Pup | `574184` | `200253584` | 32 | 267,584,128 | 0 |

Astropy `fitsdiff` 6.1.7 reported zero image-data differences against the
pinned two-master legacy replays at zero absolute and relative tolerance.
FITS header-card counts differed. The OmegaCAM legacy replay also emitted
two telemetry-card format warnings. For each native ASDF, an independent
reader verified the output FITS SHA-256, recipe snapshot and output HDU map,
plus the paths, SHA-256 values and detector-to-source-HDU bindings for the
native dome master, native sky master and BPM.

The qualification used three standalone commands. Automatic construction
of missing products from lists and the bias-enabled recipe path still
require qualification.

Compare dome, sky, and combined products separately. Check accepted frame order
and counts, scan and normalization records, detector/reference mappings, FITS
geometry and scaling, pixels, and native ASDF lineage. With bias subtraction off, start with exact numerical comparisons against
matching legacy inputs. With bias subtraction on, first check the arithmetic
independently using flats with different illumination levels and a spatially
varying master bias, then run the real datasets. Investigate differences
before proposing any tolerance. For the planner, exercise both product/list
directions, two lists sharing one bias request, missing or incompatible sources,
and approval or refusal. Compare results built from lists with the same
explicit standalone sequence.
