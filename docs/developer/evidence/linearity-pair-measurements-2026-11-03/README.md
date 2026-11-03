# Raw pair measurement preparation evidence

GCC C17 agent preparation, 3 November 2026. Focused final tests: 2/2, 15.25 s.
This is synthetic preparation, not actual Mac or real-data scientific validation.
The 22-case FITS contract hashes all generated sources before/after; ordinary
sample behavior and its small legacy BPM caller control remain checked.

- agent-c17-tests.log: final affected two-test run.
- agent-c17-build.log: final new/affected probe build, no new warnings.
- agent-known-answer.log: known answers and 117 service/config failure positions.
- agent-first-fits-oracle-failure.log: retained first failure, wrong expected
  surviving-population count/variance in the added FITS test. Corrected expected
  RON is sqrt(2/3) ADU; the reason mask leaves three pixels, not two, in its first
  pair/ROI. No numerical service change was made for this oracle correction.

The measurement FITS reason-mask case exercises 251 persistent custom allocator
failure positions. This checks service/snapshot ownership, not a general claim
about real OOM or global qfits allocation behavior. Existing Eclipse dependency
allocation contracts are reused, not newly requalified here.
