# F3 fixed failure-handling preparation — 28 October 2026

Fernando instructed "proceed" after the five fixed cases were displayed. The existing frozen F3 row authorizes at most ten launches, using the accepted tiny fixture under ASan/UBSan and separate external leaks. F1/F2 are accepted, preserved and not rerun. No production correction, further repair round, extra matrix or installation is included.

## Fixed cases and declared failure points

Run in this order, each instrumented then leaks, stopping at the first finding:

1. Missing calibration list: replace only the bias CLI argument with missing-bias.list; all fixture files remain available.
2. Corrupt selected frame: replace disposable bias0.fits with a fixed invalid byte string before locking the case input hashes.
3. Blocked output publication: reserve OCAM_MB_1x1.fits as a directory containing an immutable marker; require truthful failure and preserve that blocker.
4. Early context allocation: one declared NULL result in the disposable common-source bb = calloc(1, sizeof(mef_bb)) expression, before any context exists.
5. Intermediate cube allocation: one declared NULL result at cube_new's initial cube_t structure allocation, reached while building the bias input cube. No allocation sweep or random counter is used.

The two dormant allocation branches are inserted only into a disposable git archive. Checked-in common/cube sources and qfits remain unchanged. Each private original/replacement and before/after file hash is recorded before build. S2_F3_ALLOC selects precisely context or cube for that process; other cases use neither branch. A marker must occur exactly once for an allocation case and never for the other three. This tests explicit NULL-return handling, not exhaustive real allocator exhaustion/fallback semantics. An actual crash is a finding, never an expected successful failure test. No wrapper/backend change is introduced.

## Runner and pass criteria

qualify_integrated_failures_mac.py accepts only the known successful f5afd08 F2 parent, 6 planned + 6 retests = 12 actual launches and 2/2 general repair rounds. It verifies the active pointer, parent preservation flags, previous command hashes, selected installation/tool identities, clean qualified Mac checkout, immutable contracts and absence of production changes from f5afd08. A fresh F3-failures directory prevents repeat/overwrite. All work uses nice >=10 and one thread per numerical library.

Two private C17 builds retain qfits memory mode 2/2,000,000 pointers, ASan/UBSan symbols and the separate qualified leaks lane. They run the actual integrated recipe/observer. Every failure must return a positive nonzero native status through the observer, with balanced context/product owners, no sanitizer finding, zero final double-purge resources, stable exact descriptors and zero external leaks. The observer/tool itself must return zero after observing the clean native failure; a crash, missing return marker, sanitizer exit or tool error fails the case. Inputs/blocker, previous evidence, checkout and selected installation must remain unchanged. Early cases must not publish products; any blocked-output partial products are hashed and retained, never treated as accepted output.

On all ten passes: planned count 16/19, total actual count 22, retests unchanged at 6, repair rounds 2/2. F4, final Mac C90 and compact Chapman3 C17/C90 remain pending. On any finding: stop immediately, retain report/logs and require a bounded owner decision; no automatic repair or retry.

## Preparation evidence

Agent Python syntax, focused parser/injection positive and negative controls, real archived diagnostic-log parser controls with a simulated native error return, and private injected C90/C17 syntax pass. No native recipe is run on the agent. The parser unit controls mock low-level accounting/descriptor parsers only to isolate result policy; real archived-log controls use the actual parsers. Existing common-source format-security warnings remain. Actual Mac F3 execution is pending. Records: fixtures/agent-integrated-f3-preparation-2026-10-28/.
