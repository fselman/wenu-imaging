# Quick BPM development: checked response and byte-mask core

## Actual Mac qualification returned

Revision 14e9bb68ffe58f765576413063e0c99a6cfb311e passed the private C17
native_measurement_stats and native_bpm_response contracts on MC02VV0HPHTDG
(2.11 s each, total 4.22 s). Retained evidence:
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-response-rMPj2sY4`.
Installed files, checkout and exported source were preserved; clean main remained
at its protected baseline. This supersedes the pending-Mac statements in the
original preparation record below for that exact revision only. Full recipe,
Chapman and scientific validation remain pending. The typed service is the next
increment; see [its record](bpm-service-2026-11-02.md).


Fernando authorized development after the formula review. The consolidated
[PDF](detector-characterization-design-2026-11-02.pdf) and matching
[LaTeX](detector-characterization-design-2026-11-02.tex) are retained in this folder.
CMOS initially uses the CCD mechanism. BPM storage is unsigned 8-bit; development
and quick tests run on Mac, followed by changed-code validation and full actual-data
tests on Chapman. No scientific characterization, install or merge is claimed.

## This increment

`cube_response_checked` is a reusable Eclipse adapter around existing
`fit_slope_robust`, `fit_proportional`, `median_pixelvalue` and `image_cst_op`.
The old constructors and mef_build_bpm are untouched and remain the independent
legacy references. No new regression algorithm is introduced. Per-plane sample
maps can carry externally established saturation/validity decisions; this core
does not choose saturation thresholds, parse exposure-time headers or pair flats.

- Multiple inclusive FITS-coordinate ROIs form a union for reference measurements;
  overlap never duplicates pixels. A prior selection filters reference medians and
  normalization, not the pixels evaluated for defects.
- Preserve the actual legacy image-median convention, float stores and mean
  division. Robust residuals are mean absolute ADU (or -1 legacy fallback),
  proportional residuals are MSE in ADU squared. Fit state preserves fallback.
- Fit every pixel from its usable finite samples, return sample counts and a
  separate validity plane. Missing/degenerate coverage is not a good-pixel claim.
- Newly measured flags are only response-low=4 and response-high=8, including
  equality at the configured strict endpoints. New reasons and prior accumulated
  reasons remain distinct; recipe-level union/publication follows later.
- No implicit clipping, synthetic numerical default, input mutation or I/O.

`pixelmap_flags8_*_checked` supplies explicit reject-bit conversion to Eclipse
1=good selections and exact byte FITS I/O. The file contains BITPIX=8,
MASKENC=REASON8 and an explicitly matched registry tag (WENU_BPM_V1 in this
contract). The reader selects an explicit HDU, never the primary's BITPIX by
accident. Nonunity scaling, wrong type/rank/registry/encoding are rejected.
Every byte value 0..255 is preserved, including combined reasons. The writer
checks header/data/padding/flush and borrows a fresh seekable stream; exclusive
file creation, closing and atomic product publication remain caller duties.

These interfaces retain Eclipse's internal allocation policy and serial/global
state limitations. This increment does not close broader allocation-failure or
qfits header safety issues, and does not change legacy binary-mask semantics.

## Verification purpose and results

Inputs are generated active pixel planes and all 256 unsigned byte values; no
observational frames or installed production files are used. Actions compare the
new core with the unchanged legacy robust/proportional constructors, check an
independent known-response fixture, and use Astropy for FITS verification in both
directions. Success requires exact arithmetic/content equality where specified,
correct flags/coverage, unchanged inputs and explicit negative-case rejection.

Agent preparation: optimized C17, GCC 13.3, CMake 3.29.6. The two focused contracts
passed (0.50 s): native_bpm_response and the existing native_measurement_stats.
The response contract covers even image-median semantics, overlapping ROI union,
masked reference outliers, two-flat provisional slope coverage, missing/nonfinite
samples, strict endpoints, invalid/occupied outputs, degenerate normalization,
every byte value and selected-HDU/metadata/scaling errors. Linux additionally
checks write failure using /dev/full. Python runner/contract syntax and Git
whitespace checks passed. New source units compile without new warnings.

This is preparation evidence, not actual Mac or Chapman acceptance. The unchanged
bias/ASDF receipts remain historical evidence at their qualified revisions, not
qualification of this new source revision.

## Focused Mac gate and next increment

The existing guarded private runner now accepts `--bpm-response`. It exports the
exact revision without switching the clean main checkout, uses the selected
AppleClang/CMake/CTest/Make/ar/ranlib/SDK, builds only the response and existing
measurement probes, inventories precisely those two tests and verifies installed
files, checkout and exported source preservation. It performs no installation,
ASDF environment change, observational processing or unchanged six-test replay.

After the actual Mac gate, compose the typed BPM operation with the existing
layout loader, scan correction/trim, selected master bias and optional prior
reason/binary mask; then add checked product/ASDF publication and whole-command
completion using the bias template. Full linearity/common shutter fitting is a
later reviewed increment. Raw bias differences for RON remain before overscan
correction. Do not advertise a new BPM recipe CLI in this core-only increment.

The PDF may be rebuilt with pdflatex from its matching .tex file; it is a review
artifact, not a native build input. Keep both versions together when revised.
