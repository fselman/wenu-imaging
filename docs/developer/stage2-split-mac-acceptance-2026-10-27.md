# S2-04 Mac split/cache acceptance — 27 October 2026

Latest: [Chapman3 acceptance inspected; bounded S2-04 verified on both hosts](stage2-split-chapman3-acceptance-2026-10-27.md). Earlier target-pending statements below describe preparation history.

## Actual scope and result

Clean source `5322bb952e6958a93594692fcf1e96c58fbf800d` on branch
`test/stage2-split-ownership` passed 80 ordinary/observer pairs (160 native
invocations), OmegaCAM/WFI synthetic two-detector fixtures, C90/C17, instrumented
ASan/UBSan and separate external-leaks lanes. No production source, cleanup
policy, allocator setting, installation or observational processing changed.

Independent archive readback confirms all 160 staged input/sentinel/output
sets and exact FITS pixels, headers, scaling and padding. All products match
the prior repaired-observer reference. Context/native exit contracts pass in
all 80 observers. All 240 descriptor boundaries (CLI return and both purges)
preserve count/identity. Original logs show no ASan/UBSan findings and all
40 external leaks summaries report zero unreachable blocks/bytes.

The original after-cli measurements remain visible: 64 cases have five RAM
registrations, exactly the queried filename including NUL plus four integer
arrays for the cached headers. The other 16 missing/non-FITS cases have zero.
The existing public cache purge removes all registered resources; a second
purge remains clean in all 80 observers. All 160 post-purge allocator boundaries
have zero RAM registrations/bytes, mapped files/references and swap bytes.
Because the intervening operation releases cache entries only, this controlled
result attributes the observed return-state registrations to qfits cache
ownership in these fixtures. It does not require a production cleanup repair
or suppression of an unexplained allocation.

## Evidence and preservation

Original directory:
`~/Software/build/wenu-imaging/mac-stage2-split-cache-zgw1_npt/`.
Archive `mac-stage2-split-cache-evidence.tar.gz`, computed SHA256
`470d585cbc974ceb5542ad9235ca5bbbf0029100a95dbbc6877fcdbf384c04bc`.
Persistent attachment `libfile_38faed2424008191a8d4bd3556e2e81d`.
All 933 file identities verified, including the transfer manifest. Raw native
logs, all role directories, source identities, allocator and descriptor records
were inspected. Mac reference report SHA256:
`299895e850c473c21645e8ecc03f21ef785160a6896492cef00198bcd59b3f78`.
The preceding repaired-observer report also matches its recorded reference hash.
Sources/export/checkout, both references and protected selected engine/config
remain unchanged. Retain all three runs and full archives, including the first
failed observer and the baseline with visible return-state findings. Committed
reports/build identities/manifests live in
`fixtures/mac-stage2-split-cache-2026-10-27/`.

## Prepared target check and roadmap boundary

`qualify_split_chapman3.py` is prepared, not native-executed. Two uninstrumented
GCC C90/C17 builds run the same ten variants for each instrument: 40 pairs /
80 native invocations. It requires exact inspected Mac report hash and unchanged
Mac-qualified production sources, native observer, fixture helper, Mac runner,
accounting parser and private CMake observer wiring. Its separate target
orchestrator is recorded independently. Exact inputs/products/exits must match
the Mac reference; return-state cache bytes use the actual target pathname,
then both purges must reach zero resources with unchanged descriptor identities.
No system/normal installation is changed; every new directory gets provenance.

This is functional/qfits-bookkeeping target verification only. Compatible
Chapman3 external sanitizer/leak tools remain unavailable; no substitute runtime
or target external memory-tool acceptance is claimed. Agent preparation checked
Python syntax, source/wiring reference identities, fixture/reference coverage and
whitespace only; no agent native qualification ran.

Current stage remains **Stage 2 memory/ownership qualification, S2-04 split
I/O/publication ownership**. The bounded Mac gate and cache-attribution subcheck
pass; target verification is pending. This does not close broader #75, S2-05/06
calibration ownership, S2-07 additional recipes, S2-08 practical injection,
S2-09 repeated stages, S2-10 cache lifetimes/general mmap/swap or conditional
S2-11 wrapper checks. The early ESO Phase 3 audit and mandatory review before
Stage 2A/component extraction remain pending. PR #105 stays draft/unmerged;
no branch or run-directory cleanup is authorized.
