# Chapman4 dependency preflight and D1 preparation

29 October 2026. User-returned read-only evidence; no remote shell session or agent-host substitution. See [qualification gate](toml-asdf-chapman-qualification-2026-10-29.md).

## Actual target receipt

- Host: chapman4.sc.eso.org; Linux 3.10.0-1160.71.1.el7.x86_64; x86_64; **glibc 2.17** confirmed by os.confstr.
- Checkout: /home1/fselman/Software/wenu-imaging; clean main 0fa9eaf157359a93f2a9196f6fff05dc3e96e220; upstream refs/remotes/origin/main; origin HTTPS fselman/wenu-imaging.
- Python: /home/fselman/.conda/envs/wenu-imaging/bin/python, 3.11.14 conda-forge; prefix/base_prefix both /home/fselman/.conda/envs/wenu-imaging.
- tomllib: stdlib path under that prefix; one in-memory table/number parse passed. No broad TOML acceptance claim.
- PATH tools: gcc/g++/cmake/make in /usr/bin; clang absent; conda /home/fselman/anaconda3/bin/conda. No compiler/tool versions or builds qualified by these paths. Python's GCC14.3.0 build banner is not the selected C compiler.

| Distribution | Returned version/state |
|---|---|
| pycavi | 0.1.0 |
| numpy | 1.26.4 |
| astropy | 6.1.7 |
| PyYAML | 6.0.3 |
| packaging | 26.3 |
| attrs | 26.1.0 |
| typing-extensions | 4.16.0 |
| importlib-metadata | 9.0.1 |
| zipp | 4.1.2 |
| pip | 26.2.2 |
| setuptools | 84.2.1 |
| asdf / asdf-standard / asdf-astropy | Not installed |
| jmespath / semantic-version | Not installed |

Installed distributions above are reported under the production prefix site-packages. Probe inspected package metadata, not scientific imports or binary linkage.

## Exact D1 candidate

The [download/metadata runner](probes/prepare_chapman_asdf6.py) prepares only:

| Wheel | Version | Published SHA256 |
|---|---|---|
| asdf | 6.0.0 | 152d49f9b2a2cd3ac0321b3ae6d2c30e2cb83d944ec00b8205aebf827fa38a7f |
| asdf-standard | 1.5.0 | 487d192c5eb1335a62c07a88d82503e1fe57911c0876ee183cf572d385f97213 |
| jmespath | 1.1.0 | a5663118de4908c91729bea0acadca56526eb2698e83de10cd116ae0f4e97c64 |
| semantic-version | 2.10.0 | de78a3b8e0feda74cabc54aab2da702113e33ac9d9eb9d2389bcf1f58b7d9177 |

Pure-Python wheel identities were checked in the upstream PyPI listings on 29 October 2026: [ASDF](https://pypi.org/project/asdf/6.0.0/), [ASDF Standard](https://pypi.org/project/asdf-standard/1.5.0/), [JMESPath](https://pypi.org/project/jmespath/1.1.0/) and [semantic-version](https://pypi.org/project/semantic-version/2.10.0/). No optional extras, asdf-astropy, compiler package or scientific-library replacement is included.

## Runner behavior

1. Guard actual host, Python/prefix/glibc, clean original checkout and returned production versions; require candidate packages still absent.
2. Use a fresh private directory under ~/Software/build/wenu-imaging/chapman4-asdf6-download-*; retain failures/logs.
3. Download exact wheels with pip download, --only-binary, --no-deps and --require-hashes, no cache, no automatic retry or source build.
4. Inspect zip metadata without importing/installing candidate code; verify filenames, SHA256, package versions, pure-wheel tags and Python requirements.
5. Traverse applicable runtime requirements using downloaded metadata plus existing installed metadata. Fail on conflicts, missing dependencies or unexpected extra/URL requirements rather than upgrading a production dependency.
6. Record the candidate dependency closure, complete before/after installed-distribution metadata/RECORD hashes and checkout preservation in run-provenance.json. This checks package metadata identities, not a rehash of all installed binary payloads.
7. Stop at D1-passed-awaiting-private-installation. No venv, installation, ASDF import, FITS read, compiler/build or reduction is launched.

The reused production dependencies are part of the recorded base, not downloaded into a complete standalone wheelhouse. D1 therefore proves artifact/metadata compatibility only. A later private environment can reference that base read-only or reproduce it; its exact isolation/install method and D2 runner will be prepared after the D1 report is inspected.

## Preparation checks and limits

Agent: runner syntax; synthetic wheel acceptance, hash/identity rejection and compatible/conflicting dependency controls passed. No actual candidate package was downloaded or installed by these agent checks.

Actual Chapman4: D0 receipt above accepted for preparing D1; D1 execution, installed imports, offline schema/FITS-reference checks, Mac trial and cross-platform interchange remain pending. No production dependency is adopted, and native TOML/C90 questions remain open.

No clone update is needed to collect the D1 evidence. Owner can fetch the exact committed runner into the private trial directory and verify its separate SHA256 before executing it; both source checkouts and working installations stay unchanged.
