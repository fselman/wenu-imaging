# Candidate native CMake build

Native M3 path qualification, 30 October 2026: [paired Mac/Chapman checks](LINK)
passed both affected CTests at 113156b94fe68f7bf2848c93ecd7451551db2984,
including actual C execution from unrelated directories with separate inputs,
calibrations and destinations. Protected installed files/checkouts stayed unchanged.
PR #167 is ready for owner review; full M3 remains open. Current installation,
configured engine and Python dependency bounds remain unchanged.

30 October paired typed-domain receipt: Intel Mac and representative shared
Chapman4 private C90 builds and all three focused TOML tests passed 3/3 at
920dd13251287c07ca9d9e3355e1cb9afcd38370. Exact legacy settings, subset controls,
151 catalog templates, 11 document/lifetime profiles and 25 domain/unit rejection
cases passed. Protected installed files/checkouts stayed unchanged. See
[paired results](../docs/developer/m2-typed-domains-paired-results-2026-10-30.md). Ready for bounded owner review; full M2 remains open.
Preserve evidence/tools; no rebuild for this documentation receipt. Earlier
pending-target notes below are historical. Merge/cleanup requires owner instruction.


30 October third M2 increment after accepted/merged/cleaned PR #148 and clean
Mac/shared Chapman main 7e665da170e2e1af9f96a97e9f5bc2f6ebcfeef5: owner instructed
“Proceed” with [typed native domains and sources](../docs/architecture/proposed/m2/typed-domains-and-sources.md). Input version 3 maps
all 151 getter templates into versioned instrument/detector, processing and
product mappings with explicit units, plus an owned immutable settings/source
document. Versions 1/2 remain supported. C90/C17 owns catalog/composition/report
logic; C99 remains parser-specific. Opt-in only; no normal engine/installation or
numerical changes. Full WAD/domain/migration/persistence work remains pending.
Build the normal engine and config_paf_snapshot/config_toml_snapshot/
cli_capture_probe/config_domains_probe; select only the three native_config_toml
compatibility/subset/domain checks. Agent C90/C17 3/3 and scoped sanitizer
checks passed; actual Mac/shared Chapman checks are pending;
preserve selected tools/evidence and do not replay the historical matrix.
No automatic merge/cleanup.

30 October paired subset receipt: Intel Mac and representative Chapman4 private
C90 builds and both focused TOML tests passed 2/2 at
d622bbec7e9784ab9fa6211080cfd4955ff3a08d. Original exact-setting/41-case controls,
16 composition profiles from two directories and 32 rejection/recovery cases
passed. Protected files/checkouts stayed unchanged. See [paired results](../docs/developer/m2-toml-subsets-paired-results-2026-10-30.md).
Ready for bounded owner review; full M2 domain/unit/source/migration work remains
pending. This documentation update requires no repeated execution or installation.
Earlier target-pending notes below are historical. Merge/cleanup requires owner
instruction.


30 October next M2 increment after owner-accepted/merged PR #147 and clean
Mac/shared Chapman main 0550fb90215c636cc6b881eb67e221c24b5ed876: owner instructed
“Proceed” with [native subset composition](../docs/architecture/proposed/m2/native-subset-composition.md). Version 2 adds containing-file
includes and explicit per-file numeric overrides, retaining standalone version 1.
Core composition stays C90/C17, parser shim C99; opt-in probes only, no normal
engine/installation or numerical change. Full domain/unit/source/migration work
remains M2. Agent C90/C17 two-test and scoped sanitizer checks passed; actual
Mac/representative Chapman checks for this increment are pending. Build the normal
engine and config_paf_snapshot/config_toml_snapshot/cli_capture_probe; select only
native_config_toml and native_config_toml_subsets. Preserve prior evidence/tools;
no historical matrix replay or automatic merge/cleanup.

30 October paired M2 target receipt: Intel Mac and representative Chapman4 private
C90 builds (normal engine and both probes) and native_config_toml passed at
b0ea0897ff2b5257eaf3bae0029b14a11a8f7152: all 585 OCAM / 249 WFI /
249 edge settings and 41 rejection/recovery cases. Protected files/checkouts
stayed unchanged. See [paired results](../docs/developer/m2-native-toml-paired-results-2026-10-30.md). Ready for bounded owner review;
full M2 composition/override/unit/source/migration work remains pending. No test
replay or installation is needed for this documentation update. Earlier pending
target notes below are historical. Merge/cleanup requires owner instruction.


M2 opt-in configuration integration: `MEFPP_BUILD_CONFIG_PROBES=ON` additionally
builds `config_toml_snapshot`, `mefpp_config_toml` (core C90/C17) and a private
C99 parser/shim target from the pinned vendored source. Normal `mefpp` linking,
installation and defaults are unchanged. Build both `config_paf_snapshot` and
`config_toml_snapshot` and select `native_config_toml` for the focused text-only
check. Parser sources/license/provenance are included in opt-in source inventory.
See [scope, API and pending target acceptance](../docs/architecture/proposed/m2/native-compatibility-reader.md). No new package install,
resource download or repeat tool qualification is needed on the user hosts.

For the maintained installation procedure and platform status, read the
[native installation guide](../docs/developer/native-installation.md).
Keep this build reference and that guide consistent when installation changes.

Status: stage-1 candidate. The direct CMake Intel Mac build/install was qualified
at source 41c8e6a...; restored frontend Mac acceptance and chapman3 remain pending.
This builds the existing serial mefpp recipe, the complete 79-source Eclipse
archive and complete 18-source qfits archive. qfits lives in `mefpp2/qfits5`;
no historical installed native library or tracked binary is a build input.
Numerical algorithms and qfits allocator mode 2 / 2,000,000 entries are retained.

CMake >=3.29 is required; CTest/Python 3 are used for developer tests. Initial supported build hosts are Darwin
and Linux with the existing POSIX services. Windows is explicitly rejected until
its platform adapters are qualified. Apple Silicon has not yet been tested.
Choose C90 or C17 explicitly in separate binary directories. This does not claim
strict ISO conformance of the legacy dependency sources: POSIX interfaces and
existing warnings remain. Only the new small primitive test uses pedantic errors.

The normal interface is now ./configure --prefix=PRIVATE_PREFIX; make; make install,
from the repository root or mefpp2. The wrappers select tools/check prerequisites
and delegate to CMake; make check is optional developer qualification. Defaults
are C90/Debug, serial build and testing OFF. No packages are automatically downloaded.
Actual Mac frontend qualification is pending; see docs/developer/native-frontend.md.

Direct CMake configuration remains available. Example variables below
are deliberately placeholders, not a command to run on an unverified machine:

```
cmake -S <source>/mefpp2 -B <fresh-build> -G "Unix Makefiles" \
  -DCMAKE_C_COMPILER=<absolute-compiler> -DCMAKE_AR=<absolute-ar> \
  -DCMAKE_RANLIB=<absolute-ranlib> -DCMAKE_LINKER=<absolute-linker> \
  -DCMAKE_BUILD_TYPE=Debug -DMEFPP_C_STANDARD=90 \
  -DCMAKE_INSTALL_PREFIX=<fresh-private-prefix> \
  -DMEFPP_FUNPACK=<absolute-funpack> -DMEFPP_SOURCE_REVISION=<exact-commit>
cmake --build <fresh-build> --parallel 1 --verbose
ctest --test-dir <fresh-build> --parallel 1 --output-on-failure --no-tests=error
cmake --install <fresh-build>
```

On Mac explicitly select the active Xcode compiler/archive tools and SDK using
`xcrun`, rather than mixed MESA/Conda programs on PATH. Use a clean recorded
environment; changing compilers requires a fresh build directory. CMake links
through the compiler driver; recording CMAKE_LINKER alone does not prove which
subordinate linker the driver invokes. C17 requires a sufficiently recent compiler;
chapman3's system GCC 4.8.5 is not that qualification compiler.

The root and mefpp2 configure/Makefile entry points are supported thin frontends.
They record ignored local state in .mefpp-config and default binary output in
build-native. Failed configuration prevents using stale state. make install builds
first, then invokes the existing installer with DESTDIR preserved. make clean
cleans only the configured build. Internal legacy Makefiles, sysconf/e_setup and
independent qfits configure scripts remain historical unsupported entry points.

Runtime installation contains only bin/mefpp, three config/*.paf templates,
two uncompressed static_cal/*.fits masks, both original license texts and build
provenance under share/mefpp. No development archives/headers or legacy tools
are installed. The checked-in generated config.h files are ignored by this build:
active sources use distinct generated mefpp_platform_config.h and
qfits_platform_config.h in the binary tree. Host/type/byte-order/mmap and 64-bit
off_t checks run at configuration. They do not remove legacy internal integer
size limits or prove correctness for every very-large FITS file.

Resources are required by default. Explicit funpack produces build-tree masks;
its status, FITS primary-card framing and block alignment are checked before
publishing a product. Target acceptance must additionally open/check both actual
BPM products independently; framing is not full semantic FITS validation.
`MEFPP_BUILD_RESOURCES=OFF` permits code-only development builds but their runtime
installation fails visibly. Testing requires Python 3 (standard library only);
Python is not a dependency of the installed native executable.

The installer preflights the whole payload. It resolves existing ancestors outside the requested prefix (including macOS
/var), then rejects linked prefixes, symlinks within the payload, missing files,
conflicting parent types and different existing contents before copying.
An identical repeated install is allowed. Use a private absolute prefix and never
point this candidate at the historical installation. Unix DESTDIR is applied once;
the staging root is excluded from the recorded runtime prefix. Installation does
not select the engine in Pycavi, edit ~/.pycavi or ~/.eclipse-rc, run reductions,
or alter project calibrations. No uninstaller is supplied. Preflight is protection
against ordinary mistakes, not an atomic transaction against concurrent changes.

## Executed test sections and boundaries

- `native_frontend_contract` exercises nine public-interface cases using a recorded
  fake backend, including error propagation, paths, state and platform selection.
  Real build/install integration is separately identified; simulated Mac selection
  does not qualify the Mac.
- `native_primitives` calls image_new, image_getmean and image_del with three known
  pixels, qfits_paf_query with a tiny PAF, and qfits_pixdump_float / qfits_pixin_float
  for exact float pixel conversion. It also checks C17 retains the inline keyword
  and exercises toupper/fabs after Eclipse includes (#83). It does not validate
  full MEF/FITS headers.
- `native_cli_usage` executes mefpp without arguments and requires nonzero status
  plus its usage text. This does not establish truthful reduction-failure exits.
- `native_install_contract` runs the production install template with synthetic
  resources: complete/repeated install, DESTDIR, edited-file preservation, symlink
  rejection, missing-resource rejection, non-directory-parent rejection, support
  for an external ancestor alias and rejection of a linked prefix.
  It does not decompress or certify the distributed BPMs.

Each corresponding script section is commented. F1 is partial; F2–F7 and the
native-reduction failure parts of F8 in the build specification remain pending.
Known source issues #69, #71, #74–#76 remain open, including version strings,
ignored engine status, warning/lifecycle and PAF/argument-order behavior. This
build candidate must not be described as memory-clean or scientifically validated.

The recipe's seven C++-style line comments were converted to block comments for
explicit C90 mode (#80); executable tokens were preserved. Other compatibility changes select the generated
configuration header by name and restrict the inline fallback to pre-C99 modes
(#83). The frontend itself changes no numerical C source.

## Failure regression suite

The focused failure/configuration correction adds the nonempty CTest entry
`native_failure_contract`; run it in both C90/C17 builds. Existing private Mac
engines and normal selection remain unchanged. Source regression checks passed;
rebuilt target build/install, installed-wrapper and observational acceptance remain
pending. See [the correction record](../docs/developer/native-failure-correction-2026-10-26.md).


## Opt-in M2 configuration migration

`MEFPP_BUILD_CONFIG_PROBES=ON` also builds `mef_config_read`, a configuration-only
bridge for the shared Python migration API/CLI. It calls the original PAF
constructor or the existing TOML document reader, never `mef_engine`. It is not
installed and is not linked into the ordinary executable. Build resources can
remain disabled for these text checks. Keep C90 as the default, C17 as the
compatibility lane and C99 scoped to the parser/shim.

Build `mefpp mef_config_read config_domains_probe config_paf_snapshot cli_capture_probe`
and select `^native_config_(migration|toml_domains)$` for this increment. See the
[migration contract](../docs/architecture/proposed/m2/configuration-migration.md)
for source ownership, input/conflict rules and exact target gates. No existing
installation or normal processing selection changes.


The next M2 [project-composition increment](../docs/architecture/proposed/m2/project-composition.md)
changes the Python configuration service and adds `native_config_project_composition`.
For its private verification select `^native_config_(migration|project_composition)$`
after building the existing normal engine/configuration targets above. Native C,
parser and installation boundaries remain unchanged; actual target verification
is pending. No C17/sanitizer or historical matrix replay is required for this
Python integration change.
