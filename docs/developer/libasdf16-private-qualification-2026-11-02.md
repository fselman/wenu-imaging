# Private libasdf / ASDF 1.6 qualification — 2 November 2026

Status: Mac shared QC passed 10/10 in 1.607 s at 0840f031; private native
provisioning failed before installation. Corrected retry prepared, not yet run.
Chapman remains pending. Refs #213/#214/#215.
Fernando authorized trying the C library and upgrading the file/core standard
to 1.6.0. This supersedes the earlier no-native-dependency-trial boundary only
for this private qualification. Existing installations and evidence remain.

## Versions and scope

- File/core standard: **1.6.0**, explicitly selected in the shared QC writer.
- Python serializer: **asdf 6.0.0**, reused from the qualified private Mac venv.
- Schema distribution: **asdf-standard package 1.5.0**, which includes core 1.6.0.
- Native candidate: **libasdf 0.3.0**, released 23 October 2026. Its package
  version is independent of ASDF standard 1.6.0.

No Python package replacement is needed just to select standard 1.6.0. Existing
1.5.0 files/evidence remain unchanged. The new candidate changes the opt-in writer
target; it does not silently rewrite old QC files or activate a production engine.

Upstream sources:

- https://github.com/asdf-format/libasdf/releases/tag/0.3.0
- https://github.com/conda-forge/libasdf-feedstock/blob/main/recipe/recipe.yaml
- https://www.asdf-format.org/en/latest/implementations/asdf-c.html
- https://www.asdf-format.org/projects/asdf-standard/en/1.1.1/generated/asdf-format.org/core/core-1.6.0.html

The release source tarball SHA256 is
`56d3d6ffc1c182a808e812da0f941537c1a0e98922eb78cbfbe3b0a896e10b6d`.
The trial uses the pinned Conda binary package with recorded build/dependency
identities, not a source archive build. It is a library qualification plus a
locally compiled C17 consumer. Upstream is still 0.x and not fully conformant;
complex/string/structured arrays and masks are outside this bounded trial.

## Mac gate

Run `Pycavi2/tests/qualify_shared_qc_mac.py --with-libasdf` using the installed
wenu-imaging Python for preservation guards. It launches tests with the retained
private ASDF Python at:

`/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python`

The runner requires actual Intel Mac MC02VV0HPHTDG, clean main at 47123eed,
upstream origin/main, exact fetched candidate and niceness >=10. It exports the
candidate privately and protects installed reduction module/configured engine/
configuration, source checkout and export. A failed attempt remains on disk.

First run the ten shared QC metadata contracts at standard 1.6.0. These verify
common schema, ADU/count restrictions, origins, unavailable values, separate
input/product records, immutable membership, naming conflicts and bounded links.
They do not select or validate numerical estimators.

Then `qualify_libasdf_mac.py` creates a fresh `libasdf-environment` under this
run using `libasdf=0.3.0` from conda-forge, plus pkgconf and dependencies.
It records solver plan, platform virtual packages, installed package list and
explicit package URLs. It uses a private package cache and never activates the
environment. Old Mac Conda's erroneous 10.16 detection is corrected only to the
actual 13.7.8 version independently measured with `sw_vers` under
`SYSTEM_VERSION_COMPAT=0`, using documented `CONDA_OVERRIDE_OSX`. The runner
verifies the resulting `__osx` before solving; it never claims a newer OS or
overrides glibc. An incompatible package solve/load is a failure, with no
automatic fallback or system changes. External plugins are disabled only for
these calls and the built-in classic solver is explicit. Modern `pkgconf`
provides linker metadata without the old pkg-config/zlib constraint.

One synthetic fixture is compiled with selected Xcode Clang, **C17 only**, and
explicit private library paths. Three interchange controls must pass:

1. C writes metadata, ADU label, null and a 2x3 float64 array; Python reads,
   validates structure and compares every value and shape exactly.
2. Python writes the same data at standard 1.6.0, uncompressed and zlib;
   C reads and compares metadata, null, shape and all values exactly.
3. Python writes shared-schema raw/product QC. C reads and re-emits the product;
   Python validates its semantic content digest and traverses both frozen input
   links. This tests the real shared schema, without a second C QC serializer.

All produced file headers must declare ASDF standard 1.6.0. Python functional
checks deny/record network calls; downloads occur only during private dependency
provisioning. This is not an assertion that arbitrary native code is network
sandboxed. No observation/FITS pixels are loaded. No mefpp rebuild, C90 duplicate,
native bias replay, scientific QC acceptance, throughput claim or production
serializer adoption is part of this gate.

Retain `qc-qualification.json`, `qc-contract-results.json`,
`libasdf-qualification.json`, `interchange-results.json`, logs, sources, package
manifest/cache, prefix, executable and synthetic ASDF files. Failure preserves
all files and cannot be reported as qualification passed.

## First Mac result and scoped retry

Owner-returned evidence at 0840f031:
`/Users/fselman/Software/build/wenu-imaging/mac-asdf16-qTH3ZFNB`.
All ten shared QC tests passed in 1.607 s. Native provisioning stopped at the
dry-run solve: missing base libarchive.19.dylib for the libmamba plugin,
incorrect `__osx=10.16`, and old pkg-config/zlib constraints. No libasdf install,
C compilation or interchange ran. Overall qualification failed; checkout,
installed files and exported source preservation all passed. Retain everything.

The corrected runner changes provisioning only. Use a fresh run with
`--reuse-qc-run /Users/fselman/Software/build/wenu-imaging/mac-asdf16-qTH3ZFNB`
and `--with-libasdf`. It checks the original report/revision/preservation and
all ten passed controls, then verifies the retained and new module, schema and
test sources are byte-identical to the pinned qualified versions. It records
the original report digests. It does not repeat the ten unchanged QC tests.
Only the three blocked C-library interchange controls remain to execute.
Correction #215 remains target-pending; the base Conda installation is not repaired.

## Chapman gate

Mac success does not prove CentOS 7/glibc 2.17 compatibility. Next obtain fresh
actual Chapman host/repository/Python/Conda/compiler evidence, then prepare the
same bounded native/Python interchange under its real virtual-package limits.
Use existing GCC 10.2.1 and private prefixes; no glibc override or active-package
upgrade. This is a new dependency platform gate, not a duplicated bias suite.
Chapman remains explicitly pending; this Mac runner refuses Linux execution.

After both gates, review whether to adopt a shared native ASDF writer for the
recipe template. Numerical bias QC definitions and native-to-project handoff
remain separate unfinished work. No merge/cleanup is authorized by qualification.
