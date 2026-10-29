# One WFI input selection — 28 October 2026

The supplied inventory archive verifies SHA256
`1d6a1fceff33ae558b3779805136fe3a58c9fb6979555f051c3d799983999624`,
persistent attachment `libfile_b0d46fc730d0819184a9d945632d260b`.
Its report SHA256 is
`6b98aac7a649dcfde328965aeb159f9ffa7540859ece7eaef0f26beb5e1ad5fb`.
All 272 records are inspected; zero header errors and source-stat preservation
are reported. This is header evidence, not pixel/illumination or content-hash proof.

## Fixed representative F2 selection

Use only Orion B-band (`BB#B/99_ESO842`), 1x1 binning, normal readout, raw 2142x4128
geometry and all eight original extensions. Dates are 9–11 December 2001.
Extension order is retained exactly: CHIP1, CHIP2, CHIP3, CHIP4, CHIP8, CHIP7,
CHIP6, CHIP5 (last OUT2). There is no renumbering or assumed physical-chip sort.

| Recipe input | Frames | Selection |
|---|---:|---|
| Bias | 3 | First three B-band bias frames from 10 December |
| BPM | 3 | First B-band screen flat from 9 December and first two from 10 December |
| Dome | 3 | First three B-band screen flats from 10 December |
| Sky | 3 | First three B-band twilight flats from 11 December |
| Science | 1 | First B-band Trapezium-core exposure from 11 December |

The two shared BPM/dome frames are immutable inputs reused by the existing
sequence; there are 11 unique raw files, 1.45 GiB total. Exact paths/stat identities
and all selected header records are declared in
`mefpp2/tests/fixtures/integrated-campaign/wfi-selection.json`.

The existing robust gain-map constructor explicitly supports twilight or lamp
sequences, fitting each pixel against the frame median rather than EXPTIME.
The selected BPM list spans nominal exposures about 9.88 and 7.37 seconds.
Actual useful intensity separation must still be checked from the selected
pixel samples; exposure times alone are not proof of illumination levels.
There is no demand for another dedicated linearity dataset or a new BPM algorithm.

The unchanged committed WFI PAF has minimum counts 3/3/3 for bias/dome/sky.
It is the declared F2 configuration, SHA256
`7d7a7bde5edac6d593727c5eef2a08007b84f48a7e2a7d8bdec811e4b399990c`.
Its original thresholds, robust flag, geometry, noise/gain settings and metadata
policies remain unchanged. No cross-filter mixing, 2003 BPM/master input, Doradus
duplicate alias or 2x2 frame is selected. This remains functional/memory regression,
not independent scientific calibration or Phase 3 certification.

## One selected-input identity/readiness lock

`lock_wfi_campaign_inputs.py` checks the pinned inventory and PAF, confirms each
selected file's size/mtime/inode against inventory, hashes each selected file once
and reads small physical-pixel sections per extension. It records sample/overscan
medians as readiness diagnostics, preserves all source files, stages only list/
configuration/report files and creates one compact report archive. It does not
run mefpp, apply a calibration or select substitute files. Stat/read failures
are collected together. A blocked lock yields one complete report, not a new search.

The sampled signal preview is not the production overscan algorithm or a calibrated
BPM. Review the returned levels before declaring the selection ready. The full
native output comparison/reference definitions are locked before the diagnostic
campaign. Both frozen contract files remain unchanged. Native launches consumed:
0 of 19; correction rounds consumed: 0 of 2.

Python syntax, all selected header mappings/role counts, original PAF keys and
physical unsigned-16-bit section scaling/preservation pass preparation checks.
Actual selected raw content identities and intensity samples are still pending.
