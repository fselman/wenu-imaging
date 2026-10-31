# Bias dependency allocation failures — #144

Batch update: owner authorized [reachable format/buffer corrections](native-format-safety.md) in the same draft PR before one combined four-test Mac/Chapman handoff. This earlier receipt retains the original #144 snapshot, checks and evidence.

Owner authorized this correction after accepted/merged PR #170 and clean Mac
and representative Chapman main e2460fb72bdbe69f92c7da8994a81d21928569b5.
The bounded contract is failure propagation through the existing bias dependency
path, with unchanged normal pixels/QC. It is not a replacement of the historical
qfits allocator or a promise of graceful recovery from system-wide exhaustion.
See [agent checks](eclipse-allocation-agent-results-2026-10-30.md).
Actual selected-tool Mac/representative Chapman qualification remains pending.

## Origin and connected scope

The original three #144 functions alone were insufficient: their callers and
connected overscan, crop and QC allocations could still dereference NULL or turn
failure into a valid scalar. The complete connected correction is disclosed here.

| Area | Origin at accepted baseline | Correction |
|---|---|---|
| `image_new`, `image_copy` | Function bodies identical to original Eclipse/mefpp import | Reject missing structure/pixels, free incomplete image, propagate copy failure |
| `cube_avg_median` | Identical to original import | Check output and timeline, release incomplete output |
| `cube_reject_planes` | Identical to original import | Check replacement cube; preserve original cube/planes on failure |
| `image_getvig`, `pixel2double_array` | Identical to original import | Propagate crop/conversion allocation failure |
| `image_getmedian` | Identical to original import | Add checked status/output helper, preserving old scalar entry |
| Rejected line average | Original unchecked allocation retained; earlier #121 corrected the retained interval | Add checked status/output helper; retain accepted #121 arithmetic/order |
| Overscan scratch/QC path | Original unchecked scratch allocations; earlier #110 already fixed scan-double release | Check scratch/conversion/line-average failures; one cleanup path restores geometry |
| Cube overscan owner, #171 | Function body identical to original import | Return error without destroying borrowed cube; active native callers check status and clean their own cube |
| Shared bias kernel | Recent extraction calling inherited helpers | Propagate checked final median failure and release incomplete signal |
| New test setup, #172 | Introduced in this change, no production effect | Whitespace-free fixture directory; original failed run retained |

Original import: c69c314a24e56311dfd0efeb5721c3549aa5cbd0 (paths at repository
root); accepted baseline: e2460fb72bdbe69f92c7da8994a81d21928569b5 (mefpp2 paths).
Raw function-origin comparisons and original-site reproductions are retained.
The borrowed-cube problem is separately tracked as #171, rather than attributed
to the recent operation API. Earlier corrected defects remain historical.

## Production behavior

Incomplete images never escape `image_new`. Failed replacement cube allocation
leaves its original owner intact. The checked median/rejected-average helpers
return a status and write their scalar output only on success. Existing scalar
entries remain available, preserving normal results and their zero-on-error
fallback; the bias path uses checked entries so valid zero cannot hide failure.
The kernel always consumes its owned working cube, and transfers a signal only
on success. The bias service retains its NULL result/error status contract and
read-only borrowed inputs; allocation failure in dependencies can report
`MEF_ERR_COMPUTATION`, because legacy helpers do not distinguish every cause.
No new exhaustive memory-error classification is claimed.

Overscan releases scratch buffers and restores temporarily decremented geometry
on every exit. Its working frame may already have subtracted rows if a later
allocation fails; the service operates on owned copies and destroys that failed
attempt, so no partial public result or borrowed-input mutation is accepted.
Native calibration, BPM and science callers now honor cube-overscan failure.
An owned native working cube may be partly processed before failure and is then
destroyed. QC belonging to a failed pending service result is destroyed with it.

## Test boundary

With `MEFPP_BUILD_CONFIG_PROBES=ON`, build `eclipse_allocation_probe` and normal
`mefpp`; run `native_eclipse_allocation` and `native_explicit_paths`. The test-only
object library compiles actual dependency units with malloc/calloc NULL-return
seams before calling the real qfits allocator. Successful calls use real mode-2
qfits allocation/accounting. Normal libraries/executable have no injection
interface. The global allocator implementation, swap policy and numerical
algorithms are unchanged. No Python production API is changed.

For each OmegaCAM/WFI PAF, the suite retains all eight accepted exact legacy
pixel/FITS/QC profiles and existing operation-owner controls. Eight direct controls
cover two image allocations, three median-stack allocations, two replacement-cube
allocations and borrowed-cube failure ownership. Complete bias sweeps cover 73
reached dependency positions with all frames retained and 75 with an outlier
rejected, each failing once and persistently from that position (296 attempts per
instrument, 592 total). Every attempt must fire its seam, return a failed status
with NULL result, preserve raw/configuration inputs, balance service owners and
restore qfits bytes/cells/mappings/descriptor counters and pointer-identity checksum.
Five subsequent successes per profile in the same context require exact expected
pixels and balanced resources. These are reached-path controls, not every
possible Eclipse execution path or allocation size.

## Remaining limits and gates

- Actual Mac/representative Chapman focused checks remain pending; keep #144,
  #171 and test setup #172 open until their applicable correction evidence exists.
- Actual low-memory pressure and allocator-internal RAM/swap failure retain the
  existing qfits fatal policy. No disk filling or real memory exhaustion is used.
- This does not qualify every Eclipse operation, other native calibration path,
  persistent OS cleanup failure, reentrancy, concurrency or broad leak freedom.
- Container LeakSanitizer is unavailable; scoped ASan/UBSan has leak detection
  disabled. Resource accounting is a separate bounded assertion.
- Full M3/#159, long FITS strings #125, output-write handling #128, legacy
  format/buffer work #74 and unresolved descriptor event #116 remain separate.
  This is no claim that every open historical issue is an active defect or that
  the source tree has undergone a complete memory audit.

Preserve all original/corrected runs, evidence and selected tools. No installation,
configured-engine activation, observations, scientific tuning, milestone advance,
automatic merge or branch deletion is authorized by these checks.
