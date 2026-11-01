# Large image I/O — paired target results and IO-6 review

Date: 31 October 2026 (America/Santiago).
Native implementation qualified: `c66b81582630941050d79aea2c81ba481300e39a`.
Approved [roadmap v1.0](large-file-image-io-roadmap-v1.md), frozen
[IO-0 plan](large-file-image-io-io0-plan.md), tracking #195 and PR #200.

**IO-5 is complete on the Intel Mac and representative Chapman4. Recommend owner
acceptance of this bounded large image I/O increment.** IO-6 owner acceptance,
merge/cleanup and source synchronization remain pending. No installation or M5
advance follows automatically. No additional tests are proposed for unchanged code.

## Actual target evidence

| Target | C90 four focused contracts | C17 same contracts | C90 large processed output |
|---|---|---|---|
| Intel Mac MC02VV0HPHTDG | 4/4, 35.48 s | 4/4, 34.52 s | Passed independent pixel/header/order/scaling/padding validation |
| Chapman4, shared Chapman installation | 4/4, 22.10 s | 4/4, 24.02 s | Same validation passed |

Four contracts: native_large_file_io, native_qfits_discovery, native_layout and
native_explicit_paths. The last retains ordinary tiny OmegaCAM/WFI exact output
comparisons. No unrelated BPM/configuration/full historical matrix was rerun.
No large C17 output was generated; the approved C90 large run occurred once per
target. Test durations are not throughput or matched performance measurements.

Mac retained run:
`/Users/fselman/Software/build/wenu-imaging/mac-large-image-io-tnDIpq`.
Large evidence:
`large-work/large-file-io-odofh97c`.

Chapman retained run:
`/home1/fselman/Software/build/wenu-imaging/chapman-large-image-io-244VAT`.
Large evidence:
`large-work/large-file-io-zys1c048`.

Each runner reports QUALIFICATION passed and all three preservation checks true:
installed_files, checkout and exported_source. Runs pin the exact source/runner,
selected tool invocation paths, guarded main 38b27f8 and private builds/outputs.
Original observations were not used. Main was neither checked out to the candidate
nor installed over. The owner's returned console receipts establish these target
results; full host archives were not independently transferred. No exact target
large-run duration or RSS figures were supplied or inferred.

## Capability established

Existing shared qfits discovery/header/pixel I/O reads supported ordinary-sized
planes at wide disk positions. Existing image_sub_local subtraction and normal
mef_hdrpix_dump output produce a fully materialized **4,362,324,480-byte MEF**
from the approved synthetic 65-detector input. The pinned runner independently
checks all **1,090,519,040 large-output pixels**, relevant headers, detector order,
scaling, HDU positions and padding. Known sparse input regions and metadata are
preserved without hashing gigabytes of holes. Small-output controls also pass.

The file-offset type is signed off_t, verified at least 64 bits; memory/transfer
lengths use checked size_t. Counts, image dimensions, pixel values and numerical
routines retain their types. The two widened loader span fields change struct
layout and require coherent rebuilding; old binaries must not be mixed with new
headers/libraries. Narrow segment APIs safely reject unrepresentable requested
results and do not partially change outputs.

No additional FITS parser, numerical-type migration, allocator policy change,
new per-pixel offset logic or full-plane copy was introduced. Fourteen approved
production/header/build files and three focused test/runner files implement the
scope. #201 corrects a full-plane conversion count used with a copied-window
buffer within IO-2. Agent scoped ASan/UBSan and actual target window controls pass.

## Stage disposition and limits

| Stage | Disposition |
|---|---|
| IO-0 | Approval, interfaces, fixtures, existing operation and resources frozen before C edits |
| IO-1 | Wide discovery and checked legacy behavior qualified |
| IO-2 | Header/pixel/map/copy/window/late-plane reads and M4 consumer qualified |
| IO-3 | Wide output/padding, checked byte products and changed write-status boundaries qualified |
| IO-4 | Agent C90/C17, independent large output and scoped sanitizer controls passed |
| IO-5 | Actual Mac and representative Chapman qualification passed |
| IO-6 | Ready for owner acceptance and explicit integration instruction |

The achieved result is usable large image I/O with ordinary detector planes,
not an exabyte-tested library. Retain the existing plane-byte/pixel-count,
HDU-count/header budgets, addressability and supported-format limits.
No arbitrary huge individual image, table payload, heap/random group,
standalone utility (#198/#199), general CMOS/scientific readiness or full
production-recipe acceptance is claimed. mef_split remains outside this migration.
The processing harness calls the existing operation and production I/O helpers;
it does not establish a complete observational reduction.

Scoped sanitizers were run in the agent, with leak detection disabled for the
documented legacy-cache limitation; target runs are functional qualification.
Resource limits were enforced by the pinned runner, but theoretical type range
is distinct from actual filesystem/disk/mapping support. General no-performance-
penalty obligations remain: no matched speedup, universally identical memory use
or full scientific throughput claim is made. No new benchmark campaign is needed
without a changed boundary, failure or evidence of a reproducible regression.

## Next action

Accept the IO-6 review, then explicitly instruct merge/cleanup to integrate PR
#200 and synchronize Mac/Chapman source. Keep #195 open through that acceptance
decision; #201 meets its bounded correction/target-verification criteria.
No installation is implied by source synchronization. After accepted integration,
resume M5 calibration subroutine decomposition. Preserve all original, failed,
corrected, target and large-output evidence.
