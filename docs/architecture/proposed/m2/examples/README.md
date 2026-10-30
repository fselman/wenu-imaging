# Complete native-domain examples

These OCAM/WFI examples were copied from the passing agent C90 native-domain
contract. They contain complete normalized effective settings and explicit units,
not new defaults or recommendations for a scientific reduction.

For each instrument:

- `entry.toml` composes the three files in `shared settings/`.
- `full.toml` contains the same complete native settings in one document.
- `local.toml` demonstrates explicitly declared numeric overrides verified
  against the real retained CLI configuration loader.

[OCAM entry](omegacam/entry.toml) / [WFI entry](wfi/entry.toml).
[OCAM local example](omegacam/local.toml) / [WFI local example](wfi/local.toml).

`conversion-evidence.json` retains the original source PAF text (including
identical duplicates/unconsumed keys), exact source hash/ref/path, and SHA256s of
these generated examples. The test starts with the actual PAF constructor's
full-precision dump, verifies it against the M1 baseline, renders typed TOML and
compares the native reader result exactly. No new scientific values are inferred
from the legacy text. Complete general migration/conflict handling remains M2.

Do not install these examples or switch the normal engine selection from this
review package. Actual Mac/representative Chapman qualification is pending.


The reusable [configuration migration API/CLI](../configuration-migration.md) now
produces [source-preserving migrated examples](../migration-examples/).
These earlier domain fixtures remain the accepted split/local-override references;
they are not installed defaults or automatically rewritten during migration.
