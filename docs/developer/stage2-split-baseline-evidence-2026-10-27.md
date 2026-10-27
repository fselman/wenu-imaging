# S2-04 first Mac baseline and observer repair — 27 October 2026

Actual baseline source: test/stage2-split-ownership at
8e2c2ad061a30f9a91c649d07ee07bd254a43101, clean. All 80 pairs / 160 native
invocations completed. The runner correctly reported a failed overall gate;
the blanket functional-finding count needs the qualification below.

## Inspected results

All **80 ordinary CLI functional contracts passed**. Independent archive
readback of all **160 role directories** confirms exact expected pixels,
headers/padding, staged inputs/sentinels and partial-output behavior. Ordinary
and observer products and input hashes match for every pair. No ASan/UBSan
finding is present in the original logs. All 40 external `leaks` summaries
report zero unreachable blocks/bytes; missing observer completion still fails.

Every observer reaches the after-cli accounting boundary, but then lacks the
descriptor/native completion records. All 40 direct instrumented observers
exit 2. The external leaks launcher returns 0 despite incomplete native
observation; the completion-marker requirement prevents a false pass.
The observer result exception skips output validation, so its absent decoded
output list also triggers a pair mismatch. This is not evidence of actual
different or corrupt output pixels.

The first probe scans descriptor numbers only when RLIMIT_NOFILE is finite
and <=1048576. Unchanged `xmemory_init` raises the child's soft descriptor limit
to its hard maximum on first allocation. The post-call probe can reject that
initialized environment and returns before printing the native CLI result.
This diagnostic design defect is #106. The original log does not record the
limit/error branch; a revised observer must record before/after limits and
observation errors rather than infer actual limit values from this report.

**64 cases retain five RAM registrations**, no mapped files/references or swap
bytes. Their sizes exactly match the source-level cache candidate: the queried
filename including NUL plus four integer offset/size arrays, one element per
primary/extension header. Ordinary relative inputs give 60 bytes; the truncated
one-extension fixture gives 44 bytes; absolute-path cases include their full
pathname length. The remaining 16 missing/non-FITS cases have zero allocations.
Source and byte accounting support cache attribution, but controlled purge/repeat
evidence is still required before declaring these retained resources accepted.
Do not call them lost allocations or suppress them in the next run.

## Evidence retained

Original Mac directory:
`~/Software/build/wenu-imaging/mac-stage2-split-baseline-5u7ex8l7/`.
Archive: `mac-stage2-split-baseline-evidence.tar.gz`, SHA256
`5e61dc1803071984eedcbc74f95a92052dd1427f8f041357448911fa0703813a`.
Persistent attachment: `libfile_66f4a66a89208191ba2ba826835c9952`.
All **933 file identities** verified: 932 hashed files plus the manifest.
All native logs, staged and produced file sets, paired products, allocator
states/source hashes and external leak summaries inspected. Run/build reports
and full transfer manifest are committed; retain the original full run/archive.
Sources/export/checkout and protected selected engine/configuration are unchanged.
No installation or observational processing occurred.

## Test-only repair and next run

Keep all production sources, the ten case definitions and output oracles
unchanged. Replace descriptor-range scanning with enumeration of actual open
descriptors (`/dev/fd` on Mac; `/proc/self/fd` for later Linux verification).
Exclude only the enumeration's own temporary descriptor and close it before
returning; compare count and order-independent identity fingerprints. Report
explicit observation failures, actual soft/hard limits and the native CLI/context
result even if post-call resource observation fails. No limit or allocator policy
change is made to production, and no cache purge is added.

Fresh Mac C90/C17 instrumented and separate leaks/accounting qualification is
pending. The next run must complete all native/descriptor observations, retain
reference products and continue reporting any outstanding allocator state.
Expected cache candidates may still fail the overall resource gate; that is a
separate attribution obligation, not permission to relax the gate. #106/#75,
S2-04 target verification and the broader Stage 2 suite remain open.
