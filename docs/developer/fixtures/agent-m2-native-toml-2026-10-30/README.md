# Agent M2 native TOML checks — 30 October 2026

Final C90/C17 CTest reports, scoped ASan/UBSan direct-run report and exact compile
commands retained from the agent Linux x86_64 / GCC 13.3 environment. Reports
record original private attempt paths, actual commands, source/probe hashes,
counts and statuses. Per-case outputs/source-copy artifacts remain in those
private attempts; they are not all copied here. This is not actual Mac or
Chapman evidence. Python was 3.12.14 here, with actual selected 3.11.14 target
verification pending. The C90 normal engine also linked successfully without
parser targets; no recipe was executed. Legacy recipe warnings remain.

Every lane matched 585 OCAM, 249 WFI and 249 signed-zero/text-edge stored values,
including floating bits, and passed 41 rejection/same-process-recovery cases.
Every valid profile exercised 111 returned-snapshot allocation failures and
clone/ownership/output guards. ASan/UBSan instrumented the new reader, parser,
snapshot and probe only; the reference PAF probe was the uninstrumented C90
build. ASAN_OPTIONS=detect_leaks=0; UBSAN_OPTIONS=halt_on_error=1. No LSan or
whole-process allocator/thread-safety claim. Parser source/header/license
identities still match the pinned upstream.json. No source dependency changed.

Original attempts before the final root-key case/provenance additions also
passed (40 rejection cases); only final 41-case results are copied here.
No scientific input, installed engine/config, reduction, installation, replay
of the historical matrix or target-tool qualification was involved.
