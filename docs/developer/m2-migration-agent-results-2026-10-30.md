# M2 configuration migration — agent receipt — 30 October 2026

Owner authorized finishing configuration migration after accepted PR #151 and
clean Mac/shared Chapman main `a09bec7e6bc0d3fa8d82245db59aaf3063ac0d94`.
The [migration contract](../architecture/proposed/m2/configuration-migration.md)
and [#152](https://github.com/fselman/wenu-imaging/issues/152) define the boundary.

The shared Python library/CLI now migrates source PAF settings through the original
C constructor and exact TOML round-trip, retains original PAF/CFG text/hashes and
duplicate/conflict evidence, freezes the actual parsed native source graph and
validates the WAD configuration attributes. Separate purpose/recipe/product
requirements remain intact. Ordinary mefpp/Pycavi and all installed selections
remain unchanged. This is implementation/agent qualification, not M2 owner closure.

## Actual checks

Agent Linux x86_64, GCC 13.3, Python 3.12.14, CMake 3.29.6:

| Lane | Actual work | Result |
|---|---|---|
| C90 core / C99 parser CMake | Ordinary executable and five configuration targets linked; domain/source lifecycle and migration CTests | 2/2 passed |
| C17 core / C99 parser CMake | Same targets and focused checks; final migration check includes resolved source edges | Passed |
| Strict C90/C99 ASan + UBSan | Changed config/document/composition/parser paths and real configuration bridge; migration and domain contracts | Both passed; `detect_leaks=0`, `halt_on_error=1` |
| Generated example verification | Public API output agrees with checked-in migrated TOML, native stored values and original source bytes | Passed |
| Markdown/source whitespace | `git diff --check` | Passed |

The native domain regression retains 11 typed/document/lifetime profiles, 151
catalog templates and 25 domain/unit rejection/recovery cases. Allocation-failure
checks cover the changed C90 metadata construction/clone/stream-error paths;
parser/private-shim allocations remain outside the callback. Sanitizer builds
instrument the new ownership/parsing code, not the historical PAF/Eclipse/qfits
libraries; no whole-dependency memory or concurrency claim follows.

The new migration contract checks all 585 OmegaCAM and 249 WFI stored settings
against both the retained M1 baseline and actual original PAF constructor, and
selected local overrides against the real legacy CLI loader. Two identical WFI
duplicate keys remain separate ledger occurrences. CLI/library records agree
from two caller directories. Both project authoring examples pass through the
native reference gate without inventing detector/asset identities.

Twenty-one rejection/recovery controls cover PAF conflicts/resolutions, unknown or
missing keys, numeric/count/size/NUL limits, frozen-record tampering, TOML units,
types/conflicts/cycles and CFG vocabulary/duplicates/inheritance. Additional CLI
failure controls leave output absent; existing outputs are refused. Source/caller
mutation, source deletion, saved-record recovery, CRLF preservation, C document
clone ownership, parent resolution of sibling conflict and symlink-target capture
pass. No FITS, scientific subroutine, numerical engine, observation or installation
was exercised. CFG destination labels preserve compatibility evidence, not new
association/execution behavior.

[Retained evidence](fixtures/agent-m2-migration-2026-10-30/README.md) includes the
initial fixture assertion failures and corrected results. Exact paths and command
records remain in the private work directories and committed reports.

## Target and closure gates

Actual selected-tool Intel Mac and representative shared Chapman C90 checks are
pending. Build the ordinary engine and `mef_config_read`, `config_domains_probe`,
`config_paf_snapshot`, `cli_capture_probe`; select only
`^native_config_(migration|toml_domains)$` in fresh private directories, preserving
installed-file baselines and checkout state. No replay of the historical matrix,
installation, host/tool requalification or reduction is needed.

After paired results, review M2's configuration deliverables against the original
milestone gate before proposing owner closure. General asset/FITS applicability,
executable task plans, ASDF project publication, normal engine dispatch and
numerical optional/multi-amplifier support remain in their original milestones.
No automatic merge or branch cleanup is authorized by this receipt.
