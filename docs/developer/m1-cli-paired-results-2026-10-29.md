# M1 CLI compatibility — paired target receipt, 29 October 2026

## Executive summary

The owned legacy CLI capture and diagnostic bounds correction passed private C90
CMake builds and all three focused CTests on the Intel Mac and representative
Chapman4. Both targets passed all 51 CLI cases. This increment is ready for owner
review in PR #140; it is not complete M1 acceptance.

Tested source: `3423aadb15ef6c6b4a48183ae05d4eab8d65673f`.
Evidence below is the owner's returned terminal output, not an independently
transferred or hash-audited target archive. No tests were repeated for this receipt.

## Returned target results

| Target | Configuration snapshot | Runtime lifecycle | CLI capture | Total |
|---|---|---|---|---|
| Intel Mac MC02VV0HPHTDG | passed, 2.55 s | passed, 1.28 s | 51 cases passed, 5.58 s | 3/3; 9.43 s |
| Chapman4 shared production environment | passed, 0.79 s | passed, 0.71 s | 51 cases passed, 7.50 s | 3/3; 9.06 s |

The snapshot test reports 585 exact OmegaCAM values, 249 WFI values, 249 edge
values and both actual PAF constructor snapshots. Runtime controls pass for
OmegaCAM, WFI and synthetic overrides. CLI cases cover twelve retained forms,
defaults/full/repeated/partial/empty bindings, default/first/last/negative/excessive
display selectors for both instruments, fourteen rejected commands and five
informational exits. The test program calls the actual loader and owned capture;
it does not call the numerical engine. See [the implementation contract](../architecture/proposed/m1/cli-compatibility.md)
for allocation, lifetime and full-precision comparison controls.

Both use the selected absolute tools from [selected-tools.md](selected-tools.md),
fresh Git exports, Debug C90, resources OFF, config probes/testing ON, nice 10
and two build jobs. Mac uses Xcode Apple Clang 15 and MacPorts CMake/CTest;
Chapman uses devtoolset-10 GCC and the shared private CMake/CTest 3.29.6.
These identities reuse the existing qualification, not new version/hash probes.
Chapman3/4 are owner-confirmed copycat hosts with shared homes; no duplicate run
is required. The nonfatal SSH locale warning did not prevent any test.

## Retained evidence

Mac work directory:
`/Users/fselman/Software/build/wenu-imaging/mac-m1-cli-vLfbd4IH`

- `configure.log`, `build.log`, `tests.log`, `protected.sha256`
- `build/test-work/m1-config-krl403qu/run-provenance.json`
- `build/test-work/m1-runtime-0eckfepj/run-provenance.json`
- `build/test-work/m1-cli-o_ovby70/run-provenance.json`

Chapman requested work directory:
`/home/fselman/Software/build/wenu-imaging/chapman-m1-cli-cjwRxHdc`
(resolved CTest paths use `/home1/fselman`):

- `configure.log`, `build.log`, `tests.log`, `protected.sha256`
- `build/test-work/m1-config-h7wlvev7/run-provenance.json`
- `build/test-work/m1-runtime-p2oc3z1a/run-provenance.json`
- `build/test-work/m1-cli-lsdbg69r/run-provenance.json`

Mac returned OK for the installed mefpp, normal executable configuration and
installed reduction module. Chapman returned OK for its normal configuration and
installed reduction module. Both final guards report unchanged source revision
and clean review checkout. No installation, executable switch, FITS processing,
notebook execution, scientific/QC change or reduction ran.

## Diagnostic defect and limits

Issue [#139](https://github.com/fselman/wenu-imaging/issues/139) is corrected by
the narrow mef_bb_dump diagnostic bounds change in the tested source. The
original failed agent sanitizer trace remains retained alongside corrected agent
C90/C17 and C90 ASan/UBSan evidence. Actual target tests now separately confirm
the bounded display and capture cases. This is sufficient for bounded defect
verification; issue closure is distinct from merging the PR.

No target C17/sanitizer, LeakSanitizer, whole-engine memory, science or Phase 3
acceptance is claimed. Agent sanitizers used detect_leaks=0; explicit owner
accounting is separate. Known --ksize defect #133 remains unchanged. Normal -d
still prints and continues into processing; it is not a dump-only command.

Next: owner review of this increment, then authorized integration/cleanup.
Resolved-operation integration and one concrete operation through the common
pattern remain subsequent M1 work. Preserve all successful and failed evidence;
this documentation-only receipt requires no rebuild, installation or rerun.
