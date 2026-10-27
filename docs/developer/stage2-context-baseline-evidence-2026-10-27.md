# Inspected context cleanup baseline — 27 October 2026

Issue #99, within Stage 2 / #75; PR #100.
Actual Mac source: 3211d9982b925f691213ec31c7a419050b8cccfd, clean.
No production correction was applied to this baseline.

Uploaded archive SHA256:
364f1dbf54e251d98a6be29ee731b82289742ee48b66ef106d06bade7639dba8.
All 173 member sizes/hashes verified. The agent independently inspected all
48 case reports and original logs, the four build records and original
constructor/destructor source. All recorded commands exited zero, all native
context-result contracts passed, and no recorded address/undefined diagnostic
or unreachable-leak finding occurred. The memory gate nonetheless correctly
failed in 24 cases because qfits retained application-owned allocations.

| Case, in every mode/lane/instrument | Final live pointers | Requested bytes |
|---|---:|---:|
| Valid one call | 29 | 550 |
| Valid three calls | 87 | 1650 |
| Late missing MEF.SATMAX rejection | 29 | 550 |
| Early missing count, missing geometry, invalid count | 0 | 0 |

Within each three-call process, the snapshots are exactly 29/550, 58/1100,
87/1650. Thus repeated process exit is not the explanation for the measured
growth. Both C90/C17 and instrumented/uninstrumented lanes and OCAM/WFI agree.
The two context configurations have 32/8 detectors; the retained report includes
native result expectations and context fingerprints for later comparisons.

## Attribution and preservation

The source inventory finds 29 independently strdup-owned fields absent from
the destructor's free sites: 27 Phase 3 strings and master_flat_key/comment.
The [field/key/byte manifest](fixtures/mac-stage2-context-baseline-2026-10-27/omitted-owned-fields.json)
independently totals the original PAF values plus NUL terminators to exactly
550 bytes for either instrument, accounting for the measured count and size.
Preserve original PAF string bytes and legacy quoting; this is an ownership
repair, not a metadata-content correction.

The failed [run report](fixtures/mac-stage2-context-baseline-2026-10-27/run-provenance.json),
four build records and full transfer manifest are committed. The full archive
with original source, PAF variants and raw logs is retained as Library file
libfile_2d39969507dc819193c38ddfdaa958cf. Fernando retains the actual Mac run:
~/Software/build/wenu-imaging/mac-stage2-context-baseline-zhrgko0z/.
Do not delete, relocate or overwrite this failed-run evidence.

The actual-host report records unchanged sources, checkout, selected engine and
configuration; the collection command revalidated protected-file and input/log
hashes. The agent inspected the uploaded snapshot, not the live Mac filesystem.
No normal installation or astronomy processing ran.

The qualified control evidence explains why leaks reports zero unreachable
blocks: qfits' global table still holds registrations. This is no memory pass.
The proposed #99 repair adds only missing NULL-guarded member releases so partial
initialization remains safe, and reruns the same actual-call driver/PAF matrix
on the Mac. Corrected acceptance and unchanged deliverable verification on
Chapman3 remain pending; #99/#75 are open and broader Stage 2 is not complete.
