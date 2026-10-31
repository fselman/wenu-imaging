# qfits-backed M4 paired qualification — 31 October 2026

Owner accepted the paired functional qualification of
`5e6bd83beafa744cd2a3be64b5405083c3ae634b` in PR #186. M4 consumes existing
qfits header/discovery machinery, with checked bounds and unchanged numerical
code/Eclipse loading. This acceptance does not merge the PR, close M4, accept
performance, or permanently adopt the current int-offset whole-file limit.

| Contract | Mac C90 | Mac C17 | Chapman4 C90 | Chapman4 C17 |
|---|---:|---:|---:|---:|
| qfits discovery | 2.49 s | 1.97 s | 0.74 s | 0.65 s |
| layout | 1.98 s | 1.85 s | 0.46 s | 0.55 s |
| bias | 2.78 s | 1.94 s | 0.60 s | 0.65 s |
| native paths | 28.03 s | 26.29 s | 19.42 s | 19.52 s |
| Total | 4/4, 35.28 s | 4/4, 32.06 s | 4/4, 21.22 s | 4/4, 21.38 s |

Both runs report QUALIFICATION passed and preservation of installed files,
checkout and exported source. Exact four-test inventories were checked. All
processing used synthetic fixtures/private executables; no original observation
was opened, installation performed or selected engine changed. These timings
identify attempts and are not matched performance measurements.

- Mac: `/Users/fselman/Software/build/wenu-imaging/mac-m4-qfits-reuse-KKXuAs2V`.
- Chapman4: `/home1/fselman/Software/build/wenu-imaging/chapman-m4-qfits-reuse-xqZWMTX1`.

These are owner-returned console receipts; full host logs/reports remain retained
there, not independently transferred archives. Agent before/corrected evidence
is linked in the [implementation record](m4-qfits-reader-adapter-2026-10-31.md).
#194 count bounds is closed after paired correction comments; #195 remains open
for the explicitly unresolved larger-file boundary, with overflow-safety controls
target-qualified. Earlier #185/#193 and agent setup #196 are separately closed.

Next is [performance-plan preparation and review](m4-performance-comparison-plan-2026-10-31.md),
reusing matched private optimized builds. No functional replay or tool discovery
is required to record this receipt. Larger files, actual map/shared-context
review and full milestone closure remain distinct from this bounded acceptance.
