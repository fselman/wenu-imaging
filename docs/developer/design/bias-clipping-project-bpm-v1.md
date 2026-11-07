# Optional clipped RON and project BPM policy

Owner-authorized contract, 7 November 2026. This implements the reviewed median-centered iterative sigma clipping and shared processing-TOML BPM setting. Existing statistics, stack rejection and un-clipped RON are unchanged. All calculations remain native C17 and ADU.

The shared immutable processing snapshot owns BPM encoding, polarity, rejection bits and registry. A detector supplies only its BPM path, HDU and coordinates. Legacy `bpm_good_value` remains compatible only without a policy or when identical to an explicit binary project policy; conflicting settings fail before products are created. Internal Eclipse selection maps remain Boolean with 1 accepted. REASON8 ingestion uses existing exact-byte/registry helpers; original masks and defect reasons remain unchanged.

The processing TOML supports optional native keys (schema 1/2), or the corresponding `processing.bpm` / `processing.ron_clip` domain descriptors (schema 3). Groups must be complete; no inferred polarity, registry, thresholds or silent per-detector override. The existing composition/provenance machinery carries the policy; it is not a separate recipe parser or mutable process-global setting.

## Clipping

For each pixel in the requested inclusive region, exclude BPM failures first, then nonfinite operands/differences. Pair differences use the existing pixelvalue subtraction rounding, before any scan correction. Gather valid differences once into one double buffer. At each iteration compute their averaged-middle median and centered sample standard deviation about their retained mean. Keep values inclusively between median minus low-sigma times standard deviation and median plus high-sigma times standard deviation. Reject monotonically; compact the buffer in place. Stop at unchanged membership or the explicit limit. Recompute final statistics after every rejection, including the last iteration. No mask/image copies, file reads, allocation, or full sorting inside iterations. Existing Wirth selection supplies the median; typical work O(KN), O(N) scratch (Wirth's worst case is not guaranteed linear).

Final RON is retained sample standard deviation divided by sqrt(2), available only with at least two retained samples and convergence. A limit exit remains explicitly nonconverged. Record low/high rejection counts, retained count, iterations, convergence, thresholds and limit in both native ASDF and additive FITS QC cards. Existing raw RON/MAD remain separate. No truncation-bias correction is claimed.

## Input policies

`BPM.ENCODING="binary"` plus `BPM.BAD_WHEN="zero"` accepts legacy binary 1; `"nonzero"` accepts binary 0. This strict encoding continues to reject nonbinary pixels.

`BPM.ENCODING="reason8"`, `BPM.BAD_WHEN="nonzero"`, `BPM.REJECT_BITS=255`, `BPM.REGISTRY="WENU_BPM_V1"` accepts exactly byte zero. The existing REASON8 contract also allows an explicit subset of rejection bits: the predicate is `(flags & reject_bits)==0`. This differs deliberately from rejecting every nonzero byte when fewer than 255 bits are selected. A reason mask must carry matching MASKENC/MASKREG metadata; unlabeled external masks are not guessed.

For opt-in clipping supply all four keys: `QC.RON.CLIP.ENABLED=1`, `QC.RON.CLIP.LOW=5.0`, `QC.RON.CLIP.HIGH=5.0`, `QC.RON.CLIP.MAX_ITERATIONS=10`. Omit the group to preserve the old snapshot and path. Explicit enabled=0 records the settings without running clipping. Clipping requires an explicit RON pair.

## Qualification

Check exact legacy results with absent/disabled options, independent sorted-array clipping oracle, even medians, ties, zero scale, small samples, asymmetric cuts, BPM intersections, nonfinite exclusion, boundaries, bad options and iteration exhaustion. Compare equivalent binary polarities and reason bytes including 2/128/255 with immutable source masks and shared-policy conflict refusals. Check FITS/ASDF mapping and provenance independently. Measure time and scratch for detector-sized synthetic data. Actual Mac uses the existing selected source/build/cache/tools; no new configuration or dependency installation and no observational reduction is authorized by these synthetic gates.
