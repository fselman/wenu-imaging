# Chapman4 D1 receipt and D2 private ASDF trial

29 October 2026. Continuation of [production qualification](toml-asdf-chapman-qualification-2026-10-29.md) and [D0/D1 preparation](chapman4-toml-asdf-preflight-2026-10-29.md).

## Accepted returned D1 metadata evidence

User ran the exact D1 helper on chapman4 and inspected its retained report.

- Work directory: /home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC (home alias /home/fselman/...).
- Report SHA256: d2292e08cc5c143559f49373a2f52d19a971459c6b62cfa6ba1fb400d0a1c4e6.
- Status: D1-passed-awaiting-private-installation.
- Actual Python: /home/fselman/.conda/envs/wenu-imaging/bin/python; checkout clean main 0fa9eaf157359a93f2a9196f6fff05dc3e96e220.
- Four downloaded wheels exactly match pinned SHA256/version metadata: asdf6.0.0, asdf-standard1.5.0, jmespath1.1.0 and semantic-version2.10.0.
- Seven reused runtime dependencies: attrs26.1.0, typing-extensions4.16.0, PyYAML6.0.3, packaging26.3, NumPy1.26.4, importlib-metadata9.0.1 and zipp4.1.2.
- Applicable runtime requirements in this eleven-distribution closure are satisfied. Development/docs/test extras shown in metadata are not installed.
- Report states production package metadata and checkout unchanged; no installation/import/build/FITS read/reduction ran.

This accepts the returned report for preparing D2, not actual installed ASDF behavior or independent inspection of downloaded binary artifacts by the agent.

## Prepared D2 method

[Installer/coordinator](probes/install_chapman_asdf6.py) verifies the exact D1 report/helper, retained wheel identities and requirement file, production metadata snapshot and clean checkout before beginning. It uses a one-use D2-attempt.json pointer and a fresh D2-private-* directory below the retained D1 campaign. Failures and logs are retained; no automatic retry.

Create a private Python venv with system_site_packages=True and with_pip=False. The existing pip and scientific packages are a read-only base. The candidate is isolated for new package writes, not a standalone environment independent of the base. The coordinator verifies the private prefix/site-packages path before installation and explicitly targets that directory.

Install only the four retained hash-pinned wheels with --no-index, --no-deps, --no-compile and --require-hashes. There is no dependency upgrade, source build, optional extra or pip bootstrap. No candidate becomes selected in the normal conda environment or native executable configuration.

Compare full pip-check diagnostics before/after; preserve any pre-existing issues and fail if the candidate introduces additional issues. The functional child independently checks the exact D1 runtime closure and candidate import paths, so a successful baseline comparison alone cannot mask missing candidate requirements.

The private environment, synthetic artifacts and reports remain below the trial directory. Production distribution metadata/RECORD hashes, checkout and D1 report identity are checked again afterward. This is not a full hash of every production binary payload.

## Functional probe and expected checks

The [functional child](probes/asdf6_functional_probe.py) runs from the private environment outside the checkout. Network connection/DNS/send audit events are rejected during the child process, including import/schema use. This is an application-level offline check, not a claim of OS network isolation.

| Check | Tiny input / expected behavior |
|---|---|
| Installed imports | ASDF6.0.0 must load inside the private prefix; NumPy1.26.4 and Astropy6.1.7 remain in the retained base; all D1 dependency versions/requirements agree |
| TOML | Tables, arrays, a path with spaces and duplicate/malformed input rejection through stdlib tomllib |
| ASDF round-trip | Primitive WAD-like project revision, ordered membership, frozen older plan/calibration choice, configured gain and explicit unknown/false values survive exactly |
| Offline schema | Local test schema and ASDF format/core version1.5.0; valid record accepted, bad type/version rejected, invalid record rejected on file read |
| FITS references | Fresh 4x4 synthetic science/variance/quality planes in one MEF plus a primary-HDU image; explicit relative references resolve to expected detector, HDU name/index, units, shape and pixels |
| Failure/relocation | Missing file, wrong detector, contradictory HDU selector and wrong shape rejected; copied fixture resolves from a relocated document base |
| Preservation | Original synthetic file identities and cwd unchanged; record artifact hashes and semantic digest for later Mac interchange |

Signal, variance and mask arrays stay in FITS. References are ordinary application descriptor mappings. This does not qualify ASDF ExternalArrayReference, final WAD tags/converters, all instrument metadata, numerical variance propagation or detector reduction.

The custom schema is a minimal unpublished dependency probe. It is not adoption of a public WAD schema/namespace. Packaged project schema resources and migration/unsupported-version behavior remain M7 work.

## Expected outcome and stopping boundary

Success reports Chapman4-D2-passed-awaiting-Mac-and-interchange and retains run-provenance.json, functional-report.json, logs, the private environment and tiny artifacts. Do not activate the candidate or remove any trial on success.

Stop on the first install, dependency, import, schema, reference or preservation finding. Inspect the actual report/log before proposing a correction or retry. This is one bounded candidate trial; no scientific data, mefpp native launch or exhausted Stage2 matrix is involved.

Next after successful inspected Chapman4 results: corresponding actual Mac preflight/private trial and both-direction interchange of the retained tiny products. Only after those gates can a production adoption proposal be made; C TOML/C90 and other Chapman production hosts remain separately addressed.

## Preparation status

Agent syntax/AST checks and companion checksum consistency passed. ASDF6 API signatures for custom_schema, validate, open and config_context were checked against official docs and tagged source. The agent environment has no ASDF/Astropy runtime; no real functional probe or private installation has run there or on Chapman yet.

Actual D2 target execution remains pending. Sources: [AsdfFile](https://www.asdf-format.org/projects/asdf/en/stable/api/asdf.AsdfFile.html), [open](https://www.asdf-format.org/projects/asdf/en/stable/api/asdf.open.html), and [tagged ASDF6 source](https://github.com/asdf-format/asdf/blob/ab9944e6b35c5ab8fe05c2306ecc7e5a70d9c8d4/asdf/_asdf.py). This qualification does not change installed requirements, production algorithms or the native C standard.
