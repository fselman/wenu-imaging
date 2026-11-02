# Private libasdf / ASDF 1.6 qualification — 2 November 2026

Status: Mac bounded qualification PASSED at
6395745dd3e55f90c63ae90f28238eae436c6468. All three C17/Python interchange
controls passed; ten unchanged shared QC controls reused. Retained prefix,
checkout, installed files and exported source preserved. External libasdf
selected; upstream nested-insertion limitation #219 remains open. Chapman
compatibility and production integration are not qualified. No merge/activation.
Earlier pending statements below are historical at their stated source.
Refs #213/#214/#215/#216/#217/#219.
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

Second retained attempt at c83c91df:
`/Users/fselman/Software/build/wenu-imaging/mac-asdf16-retry-9NFYFeVP`.
Original QC result/source identity was successfully reused. Conda 24.11.3's
returned platform data confirms actual `__osx=13.7.8` and classic solver, but
it still emits the libmamba startup entry-point diagnostic despite the requested
no-plugins setting. The runner incorrectly combined this stderr warning with
stdout JSON and failed parsing, before solve/install/compile/interchange.
All preservation checks passed. This is runner defect #216, not an ASDF failure.

The correction captures stdout and stderr in separate exclusive `.log` and
`.stderr.log` files, records each command's exit status and parses only stdout.
It retains warnings and still rejects nonzero process exits; it does not strip
arbitrary text until a JSON object is found. Two agent stdlib subprocess controls
pass: exact stdout JSON survives a stderr plugin warning, and a failing command
preserves both streams and remains a failure. No Conda/native execution was
needed for this logging regression. Corrected actual Mac native trial remains
pending. Keep both failed attempts and reuse only the original passed QC sub-gate.

## External library decision and third retained attempt

Fernando's latest decision is to rely on external libasdf for now. Bundling
libasdf into mefpp (#218) is deferred; no upstream C sources or CMake integration
are added. Python asdf remains a distinct required Python dependency; this trial
does not update an installed production environment.

Third retained attempt at ad42ef7a:
`/Users/fselman/Software/build/wenu-imaging/mac-asdf16-streams-o8KPDcUm`.
Dependency solve, creation and package inventory passed. C compilation failed
with asdf.h not found. Owner inspection proves both headers exist and libasdf.pc
has correct paths; returned compiler argv omitted -I and -L. All preservation
checks passed. This is runner defect #217, not evidence of an ASDF API failure.

The corrected runner explicitly passes prefix/include, prefix/lib and runtime
rpath, and requests pkgconf retain system paths for transitive dependencies.
Use a fresh run with both:
- `--reuse-qc-run /Users/fselman/Software/build/wenu-imaging/mac-asdf16-qTH3ZFNB`
- `--reuse-libasdf-run /Users/fselman/Software/build/wenu-imaging/mac-asdf16-streams-o8KPDcUm`

The second option implies the native trial without provisioning. It checks the
old exact revision, passed preservation and successful provisioning command
statuses, package version/build and required files. It fingerprints regular files
and symlinks in the retained prefix before/after, records a manifest digest and
rejects changes. It never repeats Conda solve/create/list calls in reuse mode.
All new logs, executable and synthetic ASDF outputs go to the new run directory.
The original ten QC tests are reused only under their existing identity guards.

Three agent stdlib regression controls passed in 0.005 s: explicit compiler paths
with the actual omitted-path flags, accepted complete versus rejected incomplete
or mismatched retained metadata, and prefix mutation/symlink detection. These
checks do not compile or execute ASDF. Actual Mac C17/Python interchange remains
pending; no C90/bias replay, production activation, merge or cleanup.

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

## Fourth Mac attempt: runtime boundary

2 November external ASDF runtime receipt (#219): at 33f16555, actual Mac
mac-asdf16-external-dFpUmHsz compiled/linked/started the C17 probe successfully.
The first write stopped adding measurement/value after measurement/unit succeeded;
all ten unchanged QC controls were reused and outer preservation passed.
Do not call native interchange qualified. Pinned upstream source suggests a
nested-parent insertion defect, not yet isolated on target. Run the bounded
flat/nested/direct-mapping diagnostic before choosing a workaround or library
change. Keep external libasdf, all evidence and installed engines unchanged.
The diagnostic's Python syntax is checked; its C/API execution is target-pending.

Use `Pycavi2/tests/diagnose_libasdf_nested_mac.py` in a fresh private directory,
with installed guard Python and niceness >=10. It verifies the retained helper
against pinned 33f16555, the previous prefix preservation and exact prefix digest,
reuses the successful compiler command and runs each flat/nested/mapping case
in a separate process. It prints exact setter/getter status codes and readbacks,
retains stdout/stderr and checks library-prefix/checkout preservation. It creates
no ASDF output and performs no installation or scientific processing. Diagnostic
completion is not functional acceptance: inspect every case's numeric results.

## Actual nested-path diagnostic and consumer workaround

2 November #219 diagnostic receipt: actual Intel Mac mac-asdf-nested-Kll2GMfs
isolates libasdf 0.3.0 nested-sibling insertion failure (code5, missing readback).
Flat writes and direct mapping construction/attachment/get all return0 and
read back12.5. Prefix/checkout preservation passed. Use the verified mapping
API in the synthetic interchange consumer, preserving exact metadata/array/QC
checks. External library is unchanged; its limitation remains open. Agent GCC
C17 syntax check against pinned public headers passes (synthetic config only,
no linking/runtime claim). Reuse ten QC controls and installed external prefix;
full three-control Mac interchange remains pending. No production activation,
upstream patch/upgrade, C90/bias/Chapman replay, merge or cleanup.

At commit 6779f16b the separate diagnostic processes reported:

| API path | Setter status | Getter status | Readback |
|---|---|---|---|
| Flat unit/value | both 0 | 0 | 12.5 |
| Nested measurement/unit then measurement/value | 0 then 5 | -1 | unchanged sentinel -999 |
| Direct mapping unit/value/null then attach | all 0 | 0 | 12.5 |

All processes exit zero intentionally because they report each API result;
that does not make the failing nested case pass. Error 5 is named OOM by the
library, but these results do not establish actual system memory exhaustion.
Pinned source review identifies an existing-parent reappend in materialization
as the likely mechanism. The underlying upstream library is not repaired.

Only the synthetic C writer now creates the measurement mapping through
asdf_mapping_create/set_string0/set_double/set_null and attaches it once using
asdf_set_mapping. The attachment consumes the wrapper, so no second destroy is
performed. Metadata paths/values, ndarray and independent Python exact validation
remain unchanged. Keep #219 open for the external API limitation even if the
bounded workaround passes interchange.

Agent GCC C17 -Wall/-Wextra/-Werror syntax-only check passes against the pinned
0.3.0 public headers with a synthetic generated config header disabling optional
feature macros. This checks declarations/usage, not compilation/linking of the
library or Mac runtime behavior. Next retry uses the retained installed prefix
and original passed ten QC controls; no package install or repeated diagnostic.

## Final Mac qualification receipt — 2 November 2026

Owner returned and reviewed the retained JSON reports and linked-library list.
Qualified source: `6395745dd3e55f90c63ae90f28238eae436c6468`.
Run: `/Users/fselman/Software/build/wenu-imaging/mac-asdf16-mapping-DmvnvXZJ`.

| Control | Actual result |
|---|---|
| C to Python | Metadata, null, float64 shape and every array value exact |
| Python to C | Uncompressed and zlib float64 shape and every value exact |
| Shared QC through C | Schema/content digest and frozen links preserved |
| File/core standard | 1.6.0 |
| Python packages | asdf 6.0.0; asdf-standard 1.5.0; NumPy 1.26.4 |
| C library | external libasdf 0.3.0 |
| Retry dependency provisioning | false |
| Network attempts | none recorded |
| Retained external prefix | preserved |
| Checkout / installed files / exported source | all preserved |

The executable links `@rpath/libasdf.0.dylib`, `@rpath/libfyaml.0.dylib` and
system libSystem. The libasdf dylib compatibility/current versions reported by
otool are 2.0.0/2.1.0; these are Mach-O library version fields, not the package
version. The selected package remains libasdf 0.3.0 under
`mac-asdf16-streams-o8KPDcUm/libasdf-environment`.

Retained prefix manifest SHA256:
`7b35af3f85d0764a86650ad651b4068469628c6891a15393770514bb90faa251`.

Reused QC source/evidence: original revision
`0840f03187e56ac8113cc76d75edbf7aeaf5edfe`, run `mac-asdf16-qTH3ZFNB`.
Report SHA256:
`aaba6d900c90222582495be839f1268b9fcfdb15c63cbcec8bd59fe112bf9228`.
Contract SHA256:
`68ba89ad2e7ef40cc9ea3fd55e36229336b9c00cd2ab0fcccd5d52051ade50ae`.
Ten passed contracts were reused after byte-identical source and prior
preservation checks; no new full QC replay occurred.

The bounded Mac dependency, logging, compiler-path and consumer workaround
sequence is now qualified. Earlier failed runs and diagnostic remain retained.
No further unchanged Mac test, native bias replay, C90 matrix or Chapman run is
needed for this receipt. #219 remains open because the external library's nested
insertion behavior was avoided, not repaired. This does not qualify arbitrary
ASDF features, numerical QC estimators, observational processing, production
installation, or CentOS 7 compatibility. Native QC definitions and handoff remain
separate pending review. Owner acceptance/merge is separate; nothing is activated.
