# Agent typed-domain/document checks — 30 October 2026

Actual Linux x86_64 / GCC 13.3 / Python 3.12.14 / CMake 3.29.6 checks. C90 and
C17 CMake builds linked normal mefpp and four configuration/CLI probes, then the
three focused TOML CTests passed 3/3. These retain the original 41-case check,
16 composition profiles from two directories/32 rejection cases, and add 11
owned typed-document/lifetime profiles with 25 domain/unit rejection/recovery
cases. Catalog coverage matches all 151 getter templates and their source C
types; actual PAF/CLI effective values match exactly. Freeze mode edits only a
private test fixture after loading; immutable settings/source clones survive.

Strict C90/C99 -Werror ASan/UBSan compiled the catalog, document/config/merge,
source serializer, probe and unmodified parser. The new domain/document contract
passed against uninstrumented PAF and CLI references. ASAN_OPTIONS=detect_leaks=0;
UBSAN_OPTIONS=halt_on_error=1. No LSan/all-process allocation claim. Callback
controls cover new C90 owners; parser/shim and original temporary detector maps
remain excluded. Source hashes and full override histories are explicitly absent
from runtime metadata; winning-source records are not durable content identity.

Reports retain original private attempt paths, commands and source/probe hashes.
Compile excerpts confirm C90/C17 catalog/ownership/policy and C99 only in the
private parsed-tree shim and parser. The pinned upstream source/header/license
hashes remain unchanged. Original per-case artifacts remain in the private
attempts and are not all copied here. Actual Mac/Chapman checks are pending.
Existing legacy warnings remain; no scientific run, installation, full WAD/M2,
thread-safety, safe-Python-host or warning-baseline acceptance is implied.
