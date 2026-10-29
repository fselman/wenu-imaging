# TOML/ASDF dependency qualification — production Chapman gate

29 October 2026. Owner states that the older Chapman machines are the main production systems and explicitly requires qualification there for new TOML/ASDF packages. Development remains on the Intel Mac. This is a mandatory adoption gate, not optional post-Mac portability work.

Baseline: main b5bfd910614a786b95a598cb6295989c9f6602d6. M0/M0a review package is accepted/merged; actual ASDF schemas/runtime, parser selection and effective legacy-setting decisions remain open. Prior chapman3 evidence does not automatically qualify chapman4 or another dependency.

## Candidate review; no adoption or installation yet

| Candidate | Source requirement/evidence | Proposed disposition |
|---|---|---|
| Python 3.11 tomllib | Standard library, read-only TOML parser; no new distribution | First Python reader candidate; test on both actual interpreters. Writing/editing is a separate requirement. |
| Python asdf 6.0.0 | Python >=3.11, NumPy >=1.22; BSD-3-Clause; PyPI py3-none-any wheel | First core-ASDF qualification candidate, not a production pin. Resolve its full dependency closure against actual production package constraints. |
| Python asdf 5.4.0 | Python >=3.10, NumPy >=1.22; BSD-3-Clause; prior release | Consider only if a concrete 6.0 incompatibility justifies a fallback; do not run an automatic version matrix. |
| tomlc17 | Upstream describes C17 implementation with C99 compatibility, MIT, TOML 1.1 support | Candidate only. Not strict C90; no native parser adoption or language exception implied by GCC/Clang availability. |
| tomlc99 | Upstream marks the project obsolete in favor of tomlc17 | Not the default choice merely because its name sounds compatible with an older host. |
| asdf-astropy / GWCS | Extra types/transforms beyond the initial primitive WAD metadata | Defer unless a concrete selected model needs them; each adds its own dependencies and target gate. |
| libasdf native adapter | Separate optional C adapter direction | No adoption, installation or C-standard assumption in this increment. Python owns ASDF initially. |

ASDF 6.0 direct dependencies in the reviewed tagged pyproject are asdf-standard>=1.1.0, importlib-metadata>=4.11.4 on Python <=3.11, jmespath>=0.6.2, numpy>=1.22, packaging>=19, pyyaml>=6.0, semantic_version>=2.8, typing-extensions>=4.16 and attrs>=22.2.0. The package vendors its JSON Schema implementation; do not add an independent jsonschema requirement merely because a review checker might otherwise use it.

A pure-Python ASDF wheel does not qualify its transitive dependencies: PyYAML and any optional compiled/compression packages need appropriate artifacts or a separately qualified build path. Do not infer glibc from the Linux kernel version, compiler compatibility from Python's build banner, or complete environment compatibility from top-level minimum versions.

## Source identities reviewed

- ASDF 6.0.0 source: ab9944e6b35c5ab8fe05c2306ecc7e5a70d9c8d4; pyproject blob 74b4f07c295f607c373af4cb83365248720b2cc4.
- ASDF 5.4.0 source: 47ff5ea63e65dbaa91961632378094364af193db; pyproject blob 3f0c2547cfc5c46e58e438150a73b11db119c2d1.
- tomlc17 source snapshot: 4987cf895df61f702d19e3481f34b032ab29ed3a; README blob dbdfa3878c2fdad6d5a81728b34945c27fddce4e; MIT license blob 173779e2145a1cc338cabfdeb024d13490c96c02.
- PyPI ASDF 6.0.0 wheel SHA256: 152d49f9b2a2cd3ac0321b3ae6d2c30e2cb83d944ec00b8205aebf827fa38a7f. This is published identity evidence, not a claim the wheel was downloaded/verified or installed.
- PyPI ASDF 5.4.0 wheel SHA256: c4367681154f35550a6dda3563e251a6cda50e43d34e54dad27704fe7da1aeef.

Use exact release artifacts and record every resolved transitive version/hash for the actual trial. Do not substitute rolling stable docs, mutable main branches or an unconstrained pip upgrade for the trial identity.

## D0 — Fresh read-only production preflight

Collect actual host/OS/glibc/architecture, resolved checkout/origin/branch/HEAD/upstream/status, selected Python/prefix/pip and installed versions/locations of scientific and prospective dependency packages. Record available compiler/CMake paths separately from the selected qualified compiler.

Start with chapman4 and collect the corresponding Mac snapshot before candidate trials. Identify differences across the other Chapman production hosts before transferring acceptance; hardware/OS/runtime/compiler/filesystem differences may require an additional focused check.

The [read-only metadata probe](probes/dependency_metadata_preflight.py) can collect the Python portion after delivery. An equivalent inline block avoids needing a checkout update just to collect initial target evidence.

Preflight reads metadata; it does not install/import prospective scientific dependencies, fetch/pull, compile, hash raw data or reduce images. Existing system, user-local, conda and native installations remain unchanged. Chapman can stay on its last synchronized main while the preflight runs.

## D1 — Resolve and prepare a private candidate

Using the inspected target state, choose a new private environment/prefix, explicit package constraints and a bounded exact candidate set. Preserve NumPy/Astropy and other production scientific versions initially. If resolution requires changing them, stop that candidate path and report the actual conflict; do not silently upgrade or weaken constraints.

Resolve/download into a retained trial directory with artifact hashes and a reproducible closure/lock, including platform wheel compatibility. Review a source-build requirement before launching a new compiler/build/dependency path. Do not install into the working wenu-imaging conda environment, global user site or selected native prefix.

The first ASDF trial uses core features only; no HTTP/compression/extras/test-suite dependency set is installed by implication. Obtain schemas from packaged resources; reading test records must work offline.

## D2 — Bounded functional/dependency checks on Mac and Chapman

| Surface | Focused checks |
|---|---|
| Package installation | Import outside checkout; exact version/path/closure; dependency consistency against baseline; no import from source tree |
| TOML reader | Required TOML 1.0 shared subset, quoted strings/paths, arrays/tables, numeric/date types, malformed/duplicate keys; no writer claim from tomllib |
| ASDF project metadata | Round-trip nested primitive WAD-like records; stable exact IDs/membership, unknown/unavailable values, resolved-setting snapshots and schema/version identifiers |
| Schema adapter | Local packaged schema validation, malformed structure rejection, unavailable/unsupported schemas/tags handled explicitly; perform only after actual adapter/fixtures are prepared |
| FITS reference adapter | Tiny synthetic MEF and primary-HDU references with detector selectors, relocation/missing/mismatched references; application resolver semantics checked separately from ASDF serialization |
| Uncertainty/data contract | Preserve signal/variance/mask descriptors and explicit unavailable variance, units/correction state; no claim of numerical variance propagation |
| File/resource behavior | Context-manager cleanup, explicit destinations and names with spaces, no cwd dependence or accidental overwrite; no mutation of original fixtures |
| Cross-platform interchange | Mac writes/Chapman reads and reverse for the same tiny artifacts; compare semantic values and selectors, not incidental serialized timestamps/bytes |

D2 table is a qualification specification, not prepared/executed runtime tests. Freeze the exact small runner and expected outputs before actual trials; no full science baseline or Stage 2 diagnostic matrix is required just to select a dependency.

## D3 — Adoption decision

Adopt only with both actual-Mac and production-Chapman results plus exact dependency/artifact records. Classify other Chapman hosts as verified, equivalent with evidence, or still unqualified; do not claim cluster-wide support from one host.

C parser qualification also needs a bounded actual-target build/link/parser/lifecycle probe with explicit compiler and C standard. The current C90 boundary must be preserved or changed by a concrete reviewed exception; compiling a separate C99/C17 parser adapter does not make it C90.

If a candidate cannot be supported on Chapman, choose another supported candidate or keep the compatibility route with an explicit remaining gap. A Mac-only success cannot activate a production dependency.

Keep the candidate private until the integration/activation decision. Record rollback to the existing package/engine selection; do not delete trial evidence, raw inputs or accepted pilot products.

## Status and next step

Primary documentation and tagged metadata reviewed; no dependency resolution/download/install/build/runtime trial has run. Next: inspect returned D0 Chapman4 preflight and its actual scientific package versions before preparing D1. No production adoption is claimed.

Sources checked 29 October 2026:

- [Python 3.11 tomllib](https://docs.python.org/3.11/library/tomllib.html).
- [ASDF 6.0.0 PyPI artifacts](https://pypi.org/project/asdf/6.0.0/) and [tagged pyproject](https://github.com/asdf-format/asdf/blob/ab9944e6b35c5ab8fe05c2306ecc7e5a70d9c8d4/pyproject.toml).
- [ASDF 5.4.0 PyPI artifacts](https://pypi.org/project/asdf/5.4.0/) and [tagged pyproject](https://github.com/asdf-format/asdf/blob/47ff5ea63e65dbaa91961632378094364af193db/pyproject.toml).
- [tomlc17 README](https://github.com/cktan/tomlc17/blob/4987cf895df61f702d19e3481f34b032ab29ed3a/README.md) and [license](https://github.com/cktan/tomlc17/blob/4987cf895df61f702d19e3481f34b032ab29ed3a/LICENSE).
- [tomlc99 upstream notice](https://github.com/cktan/tomlc99).
