# Agent native M4 layout evidence

Retained logs include initial/corrected optimized C90/C17 layout+bias, scoped
ASan/UBSan and the final affected-layout repeats. `run-provenance.json` records
tools/commands/private paths; `source-sha256.json` records the delivered native
boundary/probe sources. Per-run C probe logs and fixture/source identities are
copied from each actual harness run into `runs/`. No observational FITS are here.

Initial sources before the #185 FIFO guard remain at the private path recorded
in provenance, with their hashes. The first tests passed but did not cover FIFO;
this is a source finding, not a reproduced production hang. Logs are not replaced
by later successes. Full sparse/input fixtures and build outputs remain private.

Scope: actual C metadata/layout/loader and existing synthetic bias service only.
No actual Mac/Chapman, normal pipeline activation, normalization algorithm, no-scan
CMOS, physical detector, native Windows or performance acceptance is established.
Leak detection is disabled in the scoped sanitizer lane for legacy global caches.
