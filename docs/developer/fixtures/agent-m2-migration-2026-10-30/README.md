# Agent M2 migration evidence — 30 October 2026

Configuration-only Linux evidence; no FITS, reduction, installation or target-host
claim. Logs retain C90/C17 focused results, scoped ASan/UBSan results, actual
commands/tool paths and private report locations. C90/C17 compile records confirm
core C90/C17 and parser-specific C99. Sanitizer compilation used strict warnings
with `-Werror`; original common/Eclipse/qfits references remain uninstrumented.
LeakSanitizer was disabled; no whole-dependency OOM/thread-safety claim is made.

Initial failed attempts are retained: the new test fixture first used nonexistent
legacy CLI option spellings, then expected the bias kappa's stored value as float32
instead of its actual narrowed-to-float-then-stored-as-double representation.
Correcting the test spelling and independent binary64 expectation required no
numerical implementation change. All final checks passed. The final C90 migration
run also checks the generated examples against the public API and original bytes.
No failed evidence was overwritten.

See [the agent receipt](../../m2-migration-agent-results-2026-10-30.md).
Actual Mac and representative shared Chapman verification remains pending.
