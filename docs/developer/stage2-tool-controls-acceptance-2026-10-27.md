# Mac Stage 2 tool controls: inspected acceptance — 27 October 2026

Tracking #75; control PR #98, stacked on preparation PR #97.
This accepts diagnostic controls only, not application memory correctness.

## Source and actual runs

Earlier invalid-access controls:
main 7aeb454574ee35f924e5d3d024b273ebbb4dd153, clean;
~/Software/build/wenu-imaging/mac-memory-toolcheck-2tk86jc0/.
Actual source driver SHA256:
8665d5d2400251b39e6b9a4f0e001dcdd51e552e1ab6705b922299c6b9206b53.

New leak/accounting controls:
test/stage2-leak-controls db6af6a1888e6abbe65fd4ac177f1e890d3a952a, clean;
~/Software/build/wenu-imaging/mac-stage2-leak-controls-8o3il223/.
Both actual Mac runs use the selected Xcode Apple Clang/SDK in C90/C17.
Mode 2, 2000000 maximum pointer registrations and unchanged allocator source
hashes are recorded; new controls use XMEMORY_DEBUG=0 and no sanitizer.
The earlier controls use address/undefined instrumentation with leak detection
disabled. No installation or astronomy processing ran.

## Independent review

Uploaded archive SHA256:
6c7eca9250417ffd78ab2aae757b06f9d6e7cf228548d7b6948b5c3f3c58d63a.
All 58 member sizes/hashes verified against the transfer manifest.
The agent inspected original driver/source identities, all 34 recorded
command/log hashes, the earlier expected diagnostic classes and actual new
leaks/accounting output, including allocation-stack attribution for the
unreachable system control. No control was rerun for this evidence update.

Earlier C90/C17: 18 runtime cases total. Clean system/qfits cases return zero;
the deliberately invalid bounds/lifetime/duplicate-release controls and
signed-overflow control return the configured status 86 with the expected
diagnostic class. This qualifies the declared small-RAM invalid-access/UB
configuration, not mapped/swap coverage or leak detection.

New C90/C17: ten runtime cases total, with these outcomes in each mode:

| Control | leaks blocks / bytes | leaks exit | Final qfits live pointers / requested bytes |
|---|---|---|---|
| system-clean | 0 / 0 | 0 | 0 / 0 |
| system-unreachable | 1 / 8704 | 1 | 0 / 0 |
| system-rooted | 0 / 0 | 0 | 0 / 0 |
| qfits-clean | 0 / 0 | 0 | 0 / 0 |
| qfits-registered | 0 / 0 | 0 | 1 / 8192 |

The system control requests 8192 bytes; leaks reports an 8704-byte block and
attributes its allocation to allocate_unreachable in the actual driver.
Retain requested and tool-reported quantities separately; they are not
scientific pixel units or qfits byte-accounting disagreement.
Both qfits controls show one live 8192-byte allocation at the intermediate
snapshot; the released case returns to zero, while the retained case does not.

## Consequence for application qualification

Zero unreachable blocks does not mean zero abandoned registered allocations.
The installed leaks manual treats writable globals as reachability roots;
the qfits table demonstrably retains the registered-control pointer.
No suppression or exclusion was used to obtain these results.

Application checks must pair invalid-access diagnostics, leak reachability and
explicit allocator/lifetime accounting. Explain cache retention and per-call
growth rather than classifying every reachable allocation as harmless.
These controls do not qualify application cache purge, full/partial context
destruction, normal/error/repeated image stages or the entire #75 scope.

Stage 2 S2-01 is qualified for these Mac small-RAM controls only.
Mapped/swap paths and the required Chapman3 memory-tooling lane remain gaps.
Do not call either host generally memory-clean, close #75, or advance to
Stage 2A/extraction on the strength of these tool controls.

## Retention and next bounded check

[Leak-control report](fixtures/mac-stage2-tool-controls-2026-10-27/leak-run-provenance.json)
and [earlier diagnostic report](fixtures/mac-stage2-tool-controls-2026-10-27/diagnostic-run-provenance.json)
retain exact commands, flags, environment, source/tool/log hashes, cases and
protected-file checks. The original earlier probe and full 58-file transfer
manifest are committed beside them. The complete uploaded archive is retained
as Library file libfile_9fd25f69117881918e1ba17cdd768294, with the SHA256 above.
Fernando retains both original Mac run directories and the archive in the new
control run. No deletion/relocation of those directories or installations is
authorized.

Both reports record unchanged allocator sources, protected selected engine and
configuration, and checkout. Protected-file checks were revalidated on the Mac
when collecting this archive; the agent verified their returned recorded
identities, not live access to the Mac filesystem.

Next is S2-02: direct mef_bb_new_from_paf / mef_bb_del construction and destruction
for valid OCAM/WFI PAFs and early/late rejected configuration, with independently
recorded context-result expectations and before/after allocator state.
Prepare the actual-call driver on the Mac; preserve unexpected findings and
link distinct defects before bounded repairs. No production correction or new
application run is delivered by this acceptance record.
