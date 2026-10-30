# Agent Eclipse dependency failure evidence — 30 October 2026

See [the receipt](../../eclipse-allocation-agent-results-2026-10-30.md).
Original four-unit reproductions, corrected C90/C17/ASan controls, exact
source identities and retained failed test/preparation logs are included.
`reproduce-baseline.py` records the exact original source commit and compiles
those units with the same test seams; it is an agent reproduction record with
absolute private paths, not a target-host runner. Source-origin comparison uses
original import c69c314a24e56311dfd0efeb5721c3549aa5cbd0 at repository root paths,
and e2460fb at current mefpp2 paths. False whole-function equality for the rejected
mean and overscan helper reflects earlier documented corrections, not newly
introduced allocation checks. Build-info is configure-time evidence with unknown
revision for dirty builds; tested-source-sha256.json identifies final tested code.
The initial whitespace fixture attempt and first invalid C17 preparation remain
failed evidence. No real OOM, target acceptance, LeakSanitizer or scientific claim.
