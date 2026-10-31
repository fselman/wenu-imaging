# M3 inspector stages: retained agent evidence

31 October 2026, Linux agent only; not actual Mac/Chapman acceptance.

- Initial: `/tmp/m3-inspector-stages-_e6c65b9`, 20/21; new oracle dtype defect #179.
- Corrected: `/tmp/m3-inspector-stages-5jk2ur7m`, 21/21, 3.128 s.
- Final: `/tmp/m3-inspector-stages-final-iugme394`, 21/21, 3.237 s; includes final category-conflict/default-view changes.

Full synthetic fixtures remain at those locations. Committed logs/commands and
receipts preserve all three attempts; source hashes identify the final tested
inspector/client boundary. The subsequent actual-host runner is standard-library
guard/orchestration code, syntax-reviewed separately, not part of these suite runs.
Existing private Python 3.12.14, NumPy 1.26.4, Astropy 6.1.7; niceness10 and one
numerical thread. No installation, native engine, solver or observation.

HIERARCH VerifyWarnings are from existing client behavior and deliberate conflicting
category fixture cards, not test failures. The client-body comparison writes tiny
private products, while the inspector-only controls trap image reads and preserve
bytes/modes/mtimes/cwd. AST body comparison is not installed-wheel/full-import or
solver-orchestration qualification. Original bodies are from accepted main 3a61df6.
