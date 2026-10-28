# Integrated F1/F2 runner and input-lock review — 28 October 2026

PR #120 continues the accepted frozen v2.0/v2.1 campaign. Native launches remain
**0/19** and correction rounds **0/2**. Nothing is merged, installed or switched
in the user's normal engine selection. F3–F5 remain the existing pending rows.

The selected-input archive SHA256 is
`4fb753bbaa7f4e46555d6818c61508abb79ed28e42145ae51b9ab089ee70d0d5`;
its report SHA256 is
`e4572a8f99b4648722a89c6b4b4ffcc539243ef69faeee0dc71999f4a8d6d397`.
All 11 host-reported identities, five lists, unchanged WFI PAF, stat-preservation
records and eight-extension sample mappings are consistent with the committed
selection. Each detector has three distinct positive BPM lamp signal previews.
These small samples support the bounded regression; they are not full native
frame medians or scientific calibration acceptance. Raw pixels were not uploaded
or independently rehashed by the agent. The actual-host runner rechecks their
locked SHA256/stat identities before staging, and checks preservation afterward.
The compact inspection receipt is retained beside the preparation record.

## Next execution, fixed F1 then F2

`qualify_integrated_campaign_mac.py` creates one retained campaign report and an
exclusive `stage2-integrated-active-campaign.json` pointer under the approved build
root. A second invocation cannot silently start over or reset the budget. Preserve
this pointer even if a build or workload stops; subsequent work must continue the
same campaign with the declared global correction-round counter.

The runner exports the clean committed source and builds private Mac C17 ordinary,
ASan/UBSan and external-leaks binaries. It reuses the accepted allocator/tool
controls, retains complete build logs and binary identities, sets batch niceness
and thread guards, and protects the selected installed engine/configuration.
No dependency upgrades or installations occur. Production native files are unchanged.

For each dataset, the actual existing recipe builds bias, robust BPM, dome, sky,
combined flat and one science result in the same invocation, over all selected
extensions. The ordinary control runs first; ASan/UBSan and external leaks follow
only if prior results pass. F2 starts only after all F1 lanes pass. This command
allows at most six native launches and never automatically retries a finding.
Native executions have no guessed timeout; interruption is retained as a stopped
attempt, not interpreted as a numerical or memory pass.

F1 has independent exact arrays: zero bias, 79-good-pixel mirrored binary BPMs,
shared-normalized dome/sky/combined flats of 1 and 2, and science 1000 on both
9×9 extensions. All synthetic raw headers include ORIGFILE because the current
recipe modifies this existing card. This is fixture preparation, not a native fix.
F2 copies each of its eleven original raw files once into private read-only staging;
all three roles share those copies and have private output directories. Originals
are never hardlinked, chmodded or processed in place.

All six products must have their declared categories, primary/extension structure
and ordered detector names. F1 arrays must match exactly. F2 physical pixel hashes,
shapes, BITPIX and complete ordered canonical headers must match its ordinary
control exactly. Only generated product IDs are mapped to product-role tokens,
including exact references to those IDs; all other header cards remain exact.
Calibration/science extension headers are not required to contain ORIGFILE where
the actual recipe does not publish it; BPM extension identities are required.
The ordinary control supplies instrumentation equivalence, not scientific truth.

## Memory observations

The test-only observer wraps calls from the actual recipe into unchanged common
routines. It observes context construction/destruction, returned bias/dome/sky/
combined images, BPM masks and science cubes; all ownership counts and releases
must balance. Internal temporaries are observed by allocator snapshots and external
diagnostics rather than a replacement implementation. Snapshots surround each stage
and product release, context cleanup, driver return and two qfits cache purges.
Nonzero states while objects are owned are retained; zero is required at process
start and both final purge boundaries. The pre-purge state is not discarded.

Exact descriptor identities/limits are retained at the original four boundaries,
with the existing #116 gate unchanged. Native status and external-tool exit status
are checked separately. ASan/UBSan must have no findings and external leaks must
report zero. Any product, ownership, descriptor or memory finding stops dependent
cases and leaves logs/report/products intact for one bounded review and the global
maximum of two correction rounds. This runner cannot declare full Stage 2 accepted.

## Agent preparation checks, not native acceptance

Linux C17 and C90 syntax-only compilation of the observer passed. Both retain one
existing recipe format-security warning. Python compilation passed. Constructed
FITS controls passed: fixture counts/ORIGFILE, exact arrays/detector order, consistent
canonicalization of generated IDs and their references, detection of unrelated
metadata changes, and rejection of changed pixels/swapped detector names.
These controls call no native engine or Pycavi routines and consume zero launches.
See [preparation provenance](fixtures/agent-integrated-preparation-2026-10-28/run-provenance.json).
