# Chapman evidence receipt and Mac private trial

29 October 2026. Continuation of the [Chapman qualification](toml-asdf-chapman-qualification-2026-10-29.md). Private dependency testing only; production activation and refactoring remain outside this increment.

## Independently inspected Chapman evidence

Uploaded archive: `chapman4-asdf6-evidence.tar.gz`, 1,063,536 bytes, SHA256 `146182a5f21acaeb5436d2ffed4f89d81ecd662f6eb8cf75cf475bed9b6b9358`.

The agent verified safe regular-file membership, no duplicate/path-traversal entries, and all 23 manifest size/hash entries. D1 report identity is `d2292e08cc5c143559f49373a2f52d19a971459c6b62cfa6ba1fb400d0a1c4e6`. D2 parent/functional report linkage, all five command-log hashes and zero exit statuses, all six artifact hashes, three pinned helper identities, and four wheel hashes/metadata match. D1 before/after and D2 before/after production package snapshots agree exactly. These are retained metadata observations, not a fresh inspection of the remote production filesystem.

D2 records private ASDF imports, a valid installed dependency closure, TOML positive/error controls, offline custom-schema validation/round-trip, FITS reference controls and relocation. Network-attempt list is empty. Both pip-check logs report success; the offline install contains exactly the four planned additions. The agent did not reinstall or rerun the successful Chapman trial.

Independent standard-library FITS byte/header inspection confirmed the tiny MEF has PRIMARY/SCI/VAR/DQ, 4×4 SCI values 0–15, VAR=0.25, DQ first pixel=1 with the remainder zero (including FITS unsigned scaling), and a primary-image FITS containing the same signal. Detector IDs and units match the expected bindings. Canonical expected-WAD digest matches `4df8a3c69e541d2d4950e9ffdc86b2b57670a1364682611f6f7fc4e5207daf30`. This does not qualify a production WAD schema, variance propagation, numerical reductions or ASDF runtime behavior on the agent host.

Retained Chapman trial: `/home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC/D2-private-s6qsxbqf`.

## Mac preparation and acceptance gate

Actual owner preflight: MC02VV0HPHTDG / macOS 13.7.8 x86_64; clean main `b5bfd910614a786b95a598cb6295989c9f6602d6`; production Python 3.11.14 at `/Users/fselman/anaconda3/envs/wenu-imaging`. Exact archive was transferred to `/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/chapman4-asdf6-evidence.tar.gz` and hash-checked in the owner's terminal.

Prepared helpers:

- `probes/install_mac_asdf6.py`: guarded one-use private venv installation from the exact four retained wheels, no index/dependency resolution or production activation. Checks archive safety and every identity, current host/repository/base metadata, private target/pip layout, baseline/candidate pip checks, and production/checkout/transfer preservation. Retains logs and a report on trial failure; no automatic retry.
- Existing `probes/asdf6_functional_probe.py`, unchanged: same synthetic TOML/ASDF/FITS controls as Chapman. Mac-specific expected dependency closure is computed separately from Mac metadata; original Chapman D1 report is preserved.
- `probes/asdf6_interchange_probe.py`: reads the exact transferred Chapman ASDF with its local schema, checks semantic equality and all four FITS bindings/arrays, repeats after relocation with spaces, rejects the transferred invalid record, denies network attempts, and verifies original fixture/cwd preservation.

Mac zipp remains **4.1.1**; Chapman zipp is **4.1.2**. Both satisfy the existing importlib-metadata requirement. All other closure versions must match. NumPy 1.26.4 and Astropy 6.1.7 remain in their retained base; no asdf-astropy, GWCS, compression, HTTP extras or native TOML parser is added.

Test purpose/input/actions: the private Mac Python executes the unchanged dependency probe plus the new transferred-fixture reader; ASDF and Astropy FITS APIs operate only on 4×4 synthetic files. No Pycavi methods or native astronomy tools are exercised. Expected outputs are private environment, logs, generated/relocated synthetic fixtures, functional/interchange reports and parent provenance. Pass requires exact intended package/import identities, successful checks, no new pip issues, offline operation, unchanged recorded base/checkout/transfer, and status `Mac-passed-awaiting-reverse-interchange`.

Agent checks passed: syntax of both new helpers and wrong-host rejection before writes/installation. Runtime Mac execution remains pending. The helper is delivered by exact-commit/hash download into the existing transfer area, so no checkout synchronization is required for this trial; Mac remains on the accepted main. PR remains draft.

## Remaining before adoption

Inspect the returned Mac report/artifacts, then transfer the Mac-generated synthetic fixture to Chapman and read/validate it there in the retained private environment. Reading the Chapman-created file on both machines establishes only Chapman-to-Mac interchange, not the reverse direction. No production switch follows automatically. Other Chapman machines require their own equivalence/qualification evidence. Native TOML/C90 and full WAD schemas remain separate open gates.
