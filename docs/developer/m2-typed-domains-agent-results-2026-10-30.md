# M2 typed domains and source documents — agent receipt — 30 October 2026

Owner instructed “Proceed” after accepted/merged/cleaned PR #148 and confirmed
clean Mac/shared Chapman main `7e665da170e2e1af9f96a97e9f5bc2f6ebcfeef5`.
The [typed-domain/source contract](../architecture/proposed/m2/typed-domains-and-sources.md)
implements the next bounded native configuration increment. It is not complete
M2 or normal engine activation.

## Actual agent checks

Linux x86_64 / GCC 13.3 / Python 3.12.14 / CMake 3.29.6:

| Lane | What actually ran | Result |
|---|---|---|
| C90 core/catalog/document, C99 parser/shim CMake | Normal engine and four text probes linked; three focused TOML CTests | 3/3 passed, 36.56 s |
| C17 core/catalog/document, C99 parser/shim CMake | Same targets and three CTests | 3/3 passed, 77.18 s |
| Strict C90/C99 -Werror ASan+UBSan | Domain/catalog/document/config/merge/source-serializer/probe plus unchanged parser; new domain contract against uninstrumented PAF/CLI references | Passed; detect_leaks=0, halt_on_error=1 |

Elapsed times are attempt provenance, not comparative benchmarks. Compile
commands confirm C90/C17 for catalog, mapping, composition and document owners;
C99 stays in the private parsed-tree shim and parser. The upstream parser
source/header/license hashes remain unchanged. Existing legacy warnings remain;
no warning-free or new warning-baseline audit is claimed.

## Functional/ownership evidence

The retained compatibility check passes all 585 OCAM / 249 WFI / 249 edge stored
settings and 41 rejection/recovery cases. The accepted composition check retains
16 profiles from two caller directories and 32 rejection/recovery cases.

The new check passes 11 typed/document/lifetime profiles and 25 domain/unit
rejection/recovery cases. Compiled/documented catalog coverage matches all 151
accepted getter templates and source C types. Explicit physical-unit controls
cover configured gain/RON, WCS defaults, pixels, ADU, counts and dimensionless
parameters. Actual PAF snapshots and retained CLI loader settings match exactly,
including stored float bits and the legacy narrowed-double behavior.

Complete/split/local OCAM/WFI configurations, version-1/2 source records and a
signed-zero/escaped UTF-8 fixture pass. Every normal load/clone profile injects
all new C90 allocation positions and checks occupied outputs, independence,
partial cleanup and source-stream errors. For the WFI complete document: 127
load-owner positions and 113 clone-owner positions passed. Parser/private-shim
allocations and the original temporary detector map are excluded from these
callbacks. ASan/UBSan cover the scoped instrumented units; LSan is disabled.

Freeze controls edit only a private synthetic file after loading; copied values
and source records survive that edit and original-document destruction. Metadata
covers winning file/key/line, domain/type/unit/role, configured authority,
version, declared/inferred units and inherited/explicit-override state. It does
not capture content hashes, complete competing-definition histories or an atomic
filesystem snapshot. Runtime source_hash_state is explicitly not-recorded.

[Retained reports, compile commands and input hashes](fixtures/agent-m2-typed-domains-2026-10-30/README.md)
identify the actual attempts. No native numerical recipe, FITS, Pycavi reduction,
installation, ASDF persistence or target host execution occurred here. The normal
engine was linked, not executed. No thread-safety, blanket OOM, safe-Python-host,
scientific or full WAD/M2 conformance claim follows.

## Examples and next step

[Complete typed OCAM/WFI examples](../architecture/proposed/m2/examples/README.md)
were copied byte-for-byte from a passing actual-PAF/native-domain check. The
conversion-evidence record retains original PAF text (duplicates and unconsumed
fields included), source ref/path/hash and generated-file hashes. This is bounded
reference conversion, not a complete public PAF/CFG migration tool.

Actual selected Python 3.11.14 / Intel Mac and one representative shared Chapman
C90 builds and the three focused checks remain pending. Use already selected
tools and fresh private exports; do not repeat dependency/tool qualification or
the historical matrix. Owner review precedes separately instructed merge/cleanup.
Other execution/domain/WAD/migration/history work remains in M2/M7 as specified;
reduction profile, ordered recipe and product profile remain separate. Other
numerical extraction stays M5/M6. Optional BPM, required M6a variances and
#133/#144/#75 limits remain unchanged.
