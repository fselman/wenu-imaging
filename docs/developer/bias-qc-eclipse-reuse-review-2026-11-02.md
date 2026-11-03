# Bias QC decisions and Eclipse reuse review — 2 November 2026

Status: source review and owner scientific decisions; no new numerical code,
native test replay, processing, installation, merge or cleanup in this record.
Reviewed source is 07d27330555712ef6bf59a068a578b450e89b4a3.

## Owner-approved definitions

- Retain active-area level/scatter before overscan correction, after correction
  and trimming, and in the final master. Preserve detector/HDU/stage/region.
- Save mean and median; sample standard deviation about the mean with N-1;
  scaled MAD=1.4826*median(abs(x-median(x))); valid/excluded counts and mask
  context. No implicit clipping. Signal/scatter remain ADU.
- Master high-offset pixels: values above median+k*scaled-MAD, configurable
  k=5 initially. Save actual threshold, count and locations; no automatic mask
  or rejection. Bias high offsets do not establish excessive dark current.
- RON: subtract RAW bias frames first, with no overscan correction beforehand.
  This explicitly supersedes the assistant's proposed corrected-pair stage.
  Use the selected active region of D=B1-B2 and s(D)/sqrt(2), with the agreed
  sample standard deviation. Comparable independent input noise is the
  interpretation assumption. Statistical mean centering is not an overscan
  correction. No master-bias subtraction or gain conversion.

Pair choice, exact region/coordinate contract, invalid/masked samples,
insufficient samples, zero MAD and profile conventions remain to be reviewed.
These decisions do not silently replace the legacy stacking/rejection estimator.

## Mandatory implementation policy

Before any new implementation, first look for suitable existing Eclipse
subroutines. Do not add a duplicate when a suitable routine exists. Tell
Fernando beforehand about any new routine genuinely needed. Such routines must
be general-purpose within Eclipse, usable by other recipes, following current
Eclipse signatures, allocation/ownership, errors and documentation conventions.
Inspect the existing maths modules and reuse their scaffolding. Do not turn
image/statistics work into bias-only copies in the recipe or ASDF serializer.

## Source findings

Reviewed all49 C source files in src/math and src/iproc, plus relevant public
statistics headers. This is a source inventory, not runtime qualification of
every library routine or a complete safety audit.

| Requirement | Existing Eclipse routine | Finding |
|---|---|---|
| Raw pair difference | image_sub, image_arith.c | Produces a new image; inputs are not overwritten |
| Sample standard deviation | image_getstdev / image_getstdev_vig, image_stats.c | Uses N-1; suitable estimator for the requested full selected region |
| Array mean/scatter | double_avg / double_rms, math/dstats.c | Existing double-array scaffolding; double_rms is sample stdev about the mean despite its name |
| Image median | image_getmedian_checked, image_stats.c | Checked allocation path; preserves caller image through a copy |
| Array median | double_median, math/dstats.c; median_pixelvalue, math/median.c | Reusable primitives; mutation and even-sample convention must be respected |
| RON estimator | image_rect_readout_noise, detector.c | Already exists, but returns median of sampled small-window stdevs, not the requested full-region stdev |
| Absolute-value operations | image_abs / image_cst_op, image_arith.c | Existing reusable operations |
| Similar-looking robust statistic | image_median_stat, image_stats.c | Returns mean(abs(x-median(x))), NOT median absolute deviation |
| Pixel threshold maps | image_threshold2pixelmap, pixelmaps.c | Existing mapper; strict endpoint and pixelmap polarity need explicit adaptation |

image_rect_readout_noise normally generates100 sampled9x9 windows, returns the
median window stdev and optionally the stdev across those estimates. It takes
an already formed difference image and does not divide by sqrt(2). It must not
be substituted silently for the previously discussed full-region estimator.
The ring counterpart uses a different geometric sampling policy again.

image_median_stat's average absolute deviation is a legitimate existing
statistic but is not MAD, and multiplying that result by1.4826 would not implement
the agreed scaled-MAD definition. Do not change its meaning or existing callers.

The current overscan correction uses per-row rejected-mean scan estimates and
stores their median plus double_rms across rows. Those are correction-profile
diagnostics. Keep them distinct from raw overscan-pixel scatter and from RON.

## Proposed code scope, announced before implementation

RON needs composition of existing subtraction, region selection and sample-
standard-deviation routines, followed by division by sqrt(2). No new subtraction
or duplicate RON estimator is needed for that calculation.

No dedicated median-absolute-deviation routine was found in the49 reviewed
math/iproc sources. The only proposed new numerical facility is a general,
checked MAD helper in Eclipse, using existing median/array machinery and the
math/dstats.c and matching header scaffolding. An image wrapper should be added
only if needed by the integration, not as a second implementation. Its precise
signature, input preservation, allocation failures, nonfinite/masked sample and
even-sample behavior must be stated before coding. This helper is NOT implemented
or runtime-tested by this source review.

Prior Mac/Chapman gates remain valid for their qualified code and scope. New
affected numerical behavior will need independent known-answer checks and the
current Mac C17 gate after its bounded implementation is agreed.
