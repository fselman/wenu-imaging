# S2-05 supplied-bias descriptor diagnostic — 28 October 2026

Update: [both actual Mac runs independently inspected](stage2-bpm-bias-mac-inspection-2026-10-28.md).
The diagnostic run passes all 16 pairs; the original descriptor mismatch remains
unattributed and #116 stays open. Earlier pending-inspection/execution statements
are historical. No broader acceptance or target advance is authorized.

Tracking: #116 and broader #75, draft PR #115. Status: test-only diagnostic
prepared; actual Mac execution pending. No production correction or gate waiver.

## Retained actual-host finding

Fernando's Mac run at `e7e8fbdcff5af70bdcb4ea8d5521efe4a030e62f`,
`/Users/fselman/Software/build/wenu-imaging/mac-stage2-bpm-bias-zutw0_xe`,
completed 16 ordinary/observer pairs. Its summary reports zero functional
findings and one resource finding: `c90-instrumented-retained-flag0`.

The supplied case and ordinary/observer log text show correct accepted masks and
metadata, native/tool exit zero and balanced context/mask ownership. Twenty RAM
registrations / 158 bytes after driver return reach zero tracked RAM/mapping/swap
state after both purges. Descriptor count remains four, but the combined
fd/flags/device/inode/mode identity differs at driver return and after each purge.
All six reported source/export/protected/reference/checkout preservation checks
are true. These are the provided terminal/case/log observations, not an independent
inspection of the complete run archive or every one of its 32 native roles.

Preserve the entire original failed run, sources, builds, logs, outputs and
installations. The supplied text and its hash/location provenance are committed
under `fixtures/mac-stage2-bpm-bias-finding-2026-10-28/`.

The cause is unresolved. Same count does not establish unchanged descriptors;
the old aggregate signature cannot identify which descriptor/field changed.
No production leak, harmless sanitizer descriptor or observer defect is asserted
without attribution. Historical #106 concerned a separate descriptor-limit
enumeration problem and is not an explanation for this finding.

## Diagnostic scope and unchanged gate

Only the supplied-bias observer and its runner gain diagnostic detail. All
production .c/.h, numerical/header operations, ordinary driver, input fixture
bytes, thresholds, allocator, working installations and prior evidence remain
unchanged. This does not alter normal mefpp verbosity or clean up production code.

At the existing before/after-driver/after-purge/after-second-purge boundaries,
record each actual fd, FD flags, device, inode and mode. Record the existing
aggregate signature and count explicitly. Resolve targets with F_GETPATH on Mac
and readlink on Linux where available; unavailable socket/pipe targets remain
explicit. Target lookup opens no descriptors and grants no exclusions. Only
the scan directory descriptor is excluded, as before.

`descriptor_snapshots.py` requires four complete, nonduplicated snapshots,
recomputes the original unsigned-long signature from the raw identity fields,
and records exact added/removed/changed entries relative to the before state.
The runner records this attribution before enforcing descriptor gates. Existing
count/identity checks remain; per-descriptor equality is also required, without
allowlists, suppressions or relaxed memory/output conditions. A changed target
path alone is explanatory and does not replace identity-field comparisons.

## Test explanation and results

- Parser controls: synthetic balanced/unordered observations, same-count inode
  replacement, added/closed descriptors, missing/duplicate sets/details and
  inconsistent signatures. Five unittest methods pass. They test the diagnostic
  parser, not production mefpp or the actual Mac failure.
- Syntax: Python compilation and updated observer GCC C90/C17 syntax-only checks
  pass with private Linux platform declarations. No native linking/application
  execution, Mac compiler result or target qualification is claimed.
- Preservation: repository changes are confined to diagnostic tests, documentation
  and retained evidence. Existing fixtures, ordinary driver and production code
  are not modified. Logs, source identities and private platform declarations
  are retained under `fixtures/agent-stage2-bpm-descriptor-preparation-2026-10-28/`.

## Actual Mac handoff and remaining obligations

After fresh guarded synchronization, repeat the existing Mac runner at nice >=10
in a fresh retained directory. The scientific workload remains the same 16 pairs:
C90/C17 ASan/UBSan and separate leaks lanes, both fixture kinds and both
regression constructors. It still requires all 81 accepted mask pixels,
canonical headers, unchanged borrowed-bias pixels, balanced owners/descriptors,
zero tracked resources at both purges, no sanitizer diagnostics and zero external
leaks. New descriptor details are raw-log and JSON evidence, not acceptance by
themselves. Do not overwrite or reuse the original failed directory.

If the mismatch recurs, inspect the exact descriptor/field and owner before
proposing a correction. If it does not recur, the prior finding remains
unattributed; one later pass does not establish its cause or waive #116.
Inspect evidence before declaring acceptance or preparing Chapman3 verification.
Full S2-05/#75, #116, compatible target diagnostics and broader pending coverage
remain open. No S2-06 advance, departure, merge/deletion, normal installation
change or gate weakening is authorized. Mandatory review before Stage 2A/
extraction and early Phase 3 requirements work remain in force.
