# Developer guide: native mefpp build, installation and qualification

For ordinary users, start with the [quick installation guide](../installation.md).
The detailed toolchain, test and acceptance procedure below is for developers.

Maintained guide. Last updated: 25 October 2026.
Qualified native source: **41c8e6a544c1bc5122dc558e0c8cc7904214e1d0**.
Availability: draft [PR #81](https://github.com/fselman/wenu-imaging/pull/81),
branch `fix/native-cmake-build`; not yet merged into main.

This guide covers mefpp, its bundled Eclipse/qfits libraries and required runtime
resources. [Python installation](installation.md) covers the separate Pycavi wheel,
notebooks and external-engine selection. Installing the wheel does not build the
native engine; building the native engine does not install those Python components
or SExtractor, SCAMP, SWarp, Astrometry.net or their reference data.

## Normal interface restored (#84)

From the repository root or from mefpp2, the supported user interface is
./configure --prefix=PRIVATE_PREFIX, then make, then make install. Root and
component Makefiles are thin dispatchers; CMake remains the sole build graph and
installer. The ordinary path defaults to serial C90/Debug with testing OFF, so it
does not add a Python dependency to native compilation or runtime. No prerequisite
is downloaded automatically.

Mac configuration selects the active Xcode compiler/archive tools, SDK and
architecture; Linux defaults to cc and Make. Help lists CC/CMAKE/MAKE/AR/RANLIB/LD/
FUNPACK/PYTHON and explicit configure overrides. Toolchain changes need fresh
binary directories. Default binary output is build-native in the invocation
directory; .mefpp-config contains ignored local state. These are the only new
frontend configuration outputs in the checkout; host headers remain binary-tree
products. Source input hashes now include the component Makefile and frontend.

make install builds first and forwards Unix DESTDIR to the existing safe installer.
make clean cleans the configured build without deleting prefixes or source.
make check enables tests, builds and invokes the CTest beside the selected CMake.
It requires Python 3 and fails when tests are empty or unsuccessful. Failed
configuration blocks stale state; build/install failures remain nonzero. Root and
component invocations have independent state. Help changes no configuration.

The frontend contract test has nine cases covering defaults, both entry locations,
literal spaced paths, prerequisite/configure/build/install failures, optional tests,
source-directory rejection and simulated Xcode selection. It uses a recorded fake
backend; platform simulation is not actual Mac qualification. The current full
suite has four CTest entries: frontend contract (nine cases), install contract
(seven cases), native primitives and CLI usage.

Agent Linux GCC 13.3/CMake 3.29.6 real C90/C17 integration passed configure/make/
make check/make install, repeats, C17 DESTDIR and the direct CMake route. These
integration installs used synthetic empty-FITS decompressor fixtures, not actual
OCAM/WFI data, because the agent has no funpack. The actual Intel Mac normal C90 frontend/resource/installed-payload/check/repeat/
staging gate subsequently passed at source 7c5238f8. See
[the frontend acceptance](native-frontend.md) for exact evidence and remaining
platform/runtime gates.
The previous direct CMake Mac acceptance below remains evidence for its pinned
source; it does not qualify the restored frontend automatically.

## Qualification status

| Target | Current evidence | Remaining work |
|---|---|---|
| Fernando's Intel Mac, macOS 13.7.8 x86_64 | C90/C17 full native builds, CTest, exact BPM pixels/checksums, private installs/repeats, installed CLI/dependencies, C17 DESTDIR | Observational output comparison, installed wrapper and wider fixture coverage |
| chapman3, CentOS 7 x86_64, glibc 2.17 | System compiler/platform inventory only for this native candidate | Compatible CMake >=3.29 and isolated C17-capable compiler, then actual build/install/runtime checks |
| Other Linux / Ubuntu | Agent Linux GCC 13.3 code-only builds/tests; not target installation acceptance | Actual target resources, install and processing qualification |
| Apple Silicon | Required support target | Native arm64 build/install/runtime qualification; Rosetta is insufficient |
| Native Windows | Required support target; current CMake candidate rejects it explicitly | Platform adapters, native toolchain/install/runtime qualification |

See [actual Intel Mac acceptance](native-mac-build-install-acceptance.md) for
source identities, test boundaries, retained records and failures corrected in
#80/#82/#83. This guide assembles the verified procedure; it is not evidence that
an additional run of the block below occurred. A newer compiler, OS, SDK or source
revision needs recorded checks rather than an assumed pass.

## Before building

- Obtain the native sources from Git. The Pycavi Python source distribution is not
  a complete native source release. Preserve the working engine and configuration.
- Initial tools: CMake/CTest >=3.29, Unix Makefiles and a C compiler that supports
  the requested explicit C90 or C17 mode. The verified Mac used Xcode Apple Clang
  15, explicit Xcode ar/ranlib/ld and SDK; CMake/CTest inventory was 3.29.3.
- Required resources: three PAF templates and distributed OCAM/WFI compressed BPMs.
  The verified Mac uses `/usr/local/bin/funpack`. Record its identity; do not
  silently upgrade an engine or replace the masks with historical local copies.
- Testing uses Python 3, standard-library installer fixtures and, for independent
  BPM inspection below, NumPy/Astropy. The native executable does not depend on
  Python. On Fernando's Mac, use the existing wenu-imaging environment.
- Use a fresh source export, build directory per language/compiler and private
  prefix. Allow several GB for two builds, decompressed masks and installations.
  Do not install over `/Users/fselman/opt/local/mefpp` or use sudo.

No Xcode/MacPorts/Conda provisioning or compiler upgrade is implicit here. If a
prerequisite is absent, inventory it and qualify an isolated installation first.
On chapman3, GCC 4.8.5/Clang 3.4.2 cannot supply the C17 lane; do not replace system
tools or glibc. Its actual installation command sequence is pending qualification.

## Historical direct-CMake qualification procedure (pinned source)

This retained developer reproduction block targets the previously qualified source
41c8e6a544c1bc5122dc558e0c8cc7904214e1d0 and does not exercise the new frontend.
The following complete block is specifically for Fernando's verified Intel Mac.
It intentionally stops on another machine. It builds the pinned qualified source,
not whatever happens to be the checkout HEAD. Review any source update before
changing the pin. No Git checkout mutation, normal engine selection or observations
are part of the block. Existing acceptance directories are retained.

Tests and pass criteria:

- Complete C90/C17 compilation/linking, with explicit language flags.
- `native_primitives`: image_new/getmean/del, qfits_paf_query,
  qfits_pixdump_float/pixin_float, C17 inline-keyword protection and toupper/fabs.
- `native_cli_usage`: no-argument mefpp usage and expected nonzero exit.
- `native_install_contract`: seven synthetic installer cases, including repeat,
  DESTDIR, preserved edits, missing resources, parent conflicts and symlink rules.
- Astropy `fits.open`, NumPy array comparison and HDU checksum verification:
  complete distributed BPM geometry/dtype/names/pixels and checksum validity.
- Actual runtime installation: all nine payload files match source/build bytes,
  manifest records the pinned source/language/prefix, and installed CLI usage,
  x86_64 architecture and system-only dynamic dependencies are verified.
- Protected historical engine/configuration hashes and clean checkout are unchanged.

Each corresponding section is commented below. These are functional build/install
checks, not scientific validation or a memory-safety certification.

```bash
(
set -euo pipefail
stop() { echo "STOP: $*" >&2; exit 1; }

# Machine/checkout guard: require the intended Intel Mac and preserved local state.
actual="$(uname -s):$(hostname -s)"
test "$actual" = "Darwin:MC02VV0HPHTDG" ||
    stop "Expected Darwin:MC02VV0HPHTDG; detected $actual."
cd /Users/fselman/Developer/wenu-imaging
test "$(git rev-parse --show-toplevel)" = "$PWD" || stop "Unexpected checkout."
test "$(git remote get-url origin)" = "git@github.com:fselman/wenu-imaging.git" ||
    stop "Unexpected origin."
test -z "$(git status --porcelain)" || stop "Preserve and inspect local changes."
revision=41c8e6a544c1bc5122dc558e0c8cc7904214e1d0
git cat-file -e "$revision^{commit}" || stop "Qualified source commit is unavailable."

# Tool/environment guard: select the established environment and Xcode programs.
py="$HOME/anaconda3/envs/wenu-imaging/bin/python"
cmake=/opt/local/bin/cmake
ctest=/opt/local/bin/ctest
funpack=/usr/local/bin/funpack
clang="$(/usr/bin/xcrun --find clang)"
archiver="$(/usr/bin/xcrun --find ar)"
ranlib="$(/usr/bin/xcrun --find ranlib)"
linker="$(/usr/bin/xcrun --find ld)"
sdk="$(/usr/bin/xcrun --show-sdk-path)"
for tool in "$py" "$cmake" "$ctest" "$funpack" "$clang" "$archiver" "$ranlib" "$linker"; do
    test -x "$tool" || stop "Missing executable: $tool"
done
"$py" -c 'import sys; from pathlib import Path; assert Path(sys.prefix).resolve() == (Path.home()/"anaconda3/envs/wenu-imaging").resolve(); import numpy; import astropy'
unset CC CXX CFLAGS CXXFLAGS CPPFLAGS LDFLAGS CPATH C_INCLUDE_PATH
unset CPLUS_INCLUDE_PATH LIBRARY_PATH COMPILER_PATH GCC_EXEC_PREFIX SDKROOT
unset MACOSX_DEPLOYMENT_TARGET CMAKE_GENERATOR DESTDIR
export PATH=/usr/bin:/bin:/usr/sbin:/sbin:/opt/local/bin:/usr/local/bin

# Preservation/source isolation: hash working selections and export tracked sources.
work="$(mktemp -d "$HOME/wenu-native-install.XXXXXXXX")"
echo "Build/install records: $work"
engine="$HOME/opt/local/mefpp/bin/mefpp"
configuration="$HOME/.pycavi/pycavi_astrosoft.cfg"
/usr/bin/shasum -a 256 "$engine" "$configuration" > "$work/protected-before.sha256"
git rev-parse HEAD > "$work/checkout-before.txt"
git archive --format=tar --output="$work/source.tar" "$revision" mefpp2
mkdir "$work/source"
/usr/bin/tar -xf "$work/source.tar" -C "$work/source"
source_dir="$work/source/mefpp2"

runlog() {
    label=$1; shift
    echo "Starting: $label | log: $work/$label.log"
    if /usr/bin/nice -n 10 "$@" > "$work/$label.log" 2>&1; then
        echo "PASS: $label"
    else
        tail -n 60 "$work/$label.log"
        stop "$label failed; inspect the retained log."
    fi
}

# Verification helper: inspect build flags/BPMs and the actual installed payload.
cat > "$work/verify.py" <<'PY'
from pathlib import Path
import hashlib, json, os, subprocess, sys, tempfile
import numpy as np
from astropy.io import fits
phase, source, build, prefix, mode, revision = sys.argv[1:]
source, build, prefix = map(Path, (source, build, prefix))
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()
if phase == 'build':
    # Language/resource test: explicit mode and exact pixels with valid FITS checksums.
    commands = json.loads((build/'compile_commands.json').read_text())
    assert len(commands) == 100
    assert all('-std=c'+mode in row['command'] for row in commands)
    for name in ('OCAM_BPM_1x1', 'WFI_BPM_1x1'):
        with fits.open(source/'ins/mef/static_cal'/f'{name}.fits.fz', memmap=False) as left, \
             fits.open(build/'resources'/f'{name}.fits', memmap=False) as right:
            assert len(left) == len(right)
            count = 0
            for a, b in zip(left, right):
                if a.data is None:
                    assert b.data is None
                else:
                    assert a.name == b.name and a.data.shape == b.data.shape
                    assert a.data.dtype == b.data.dtype and a.data.size > 0
                    assert np.isfinite(b.data).all()
                    np.testing.assert_array_equal(a.data, b.data)
                    count += 1
                if 'CHECKSUM' in b.header: assert b.verify_checksum() == 1
                if 'DATASUM' in b.header: assert b.verify_datasum() == 1
            assert count > 0
else:
    # Installed-payload test: compare every promised file with source/build and manifest.
    originals = {'bin/mefpp': build/'mefpp',
                 'share/mefpp/source-sha256.txt': build/'source-sha256.txt',
                 'share/mefpp/licenses/mefpp-LICENSE': source/'LICENSE',
                 'share/mefpp/licenses/qfits-LICENSE': source/'qfits5/LICENSE'}
    originals.update({f'config/{n}.paf': source/'ins/mef/config'/f'{n}.paf'
                      for n in ('mefpp', 'omegacam', 'wfi')})
    originals.update({f'static_cal/{n}.fits': build/'resources'/f'{n}.fits'
                      for n in ('OCAM_BPM_1x1', 'WFI_BPM_1x1')})
    manifest_name = 'share/mefpp/build-manifest.json'
    manifest = json.loads((prefix/manifest_name).read_text())
    assert manifest['source_revision'] == revision and manifest['c_standard'] == mode
    assert manifest['install_prefix'] == str(prefix)
    assert set(manifest['installed_files']) == set(originals)
    assert not any(p.is_symlink() for p in prefix.rglob('*'))
    assert {str(p.relative_to(prefix)) for p in prefix.rglob('*') if p.is_file()} == set(originals)|{manifest_name}
    for name, original in originals.items():
        assert digest(prefix/name) == digest(original) == manifest['installed_files'][name]
    # Installed-executable test: check architecture/dependencies and usage outside the build.
    executable = prefix/'bin/mefpp'
    assert os.access(executable, os.X_OK)
    architecture = subprocess.check_output(['/usr/bin/file', '-b', str(executable)], text=True)
    assert 'Mach-O' in architecture and 'x86_64' in architecture
    dependencies = subprocess.check_output(['/usr/bin/otool', '-L', str(executable)], text=True)
    for line in dependencies.splitlines()[1:]:
        assert line.strip().split(' (', 1)[0].startswith(('/usr/lib/', '/System/Library/'))
    with tempfile.TemporaryDirectory(prefix='installed-cli-', dir=prefix.parent) as directory:
        usage = subprocess.run([str(executable)], cwd=directory, capture_output=True, text=True, timeout=15)
    assert usage.returncode != 0 and 'options' in (usage.stdout+usage.stderr).lower()
print('PASS:', phase, 'C'+mode)
PY

for standard in 90 17; do
    build="$work/build-c$standard"
    prefix="$work/prefix-c$standard"
    # Configuration/build: full bundled graph, serial execution and complete resources.
    runlog "configure-c$standard" "$cmake" -S "$source_dir" -B "$build" \
        -G "Unix Makefiles" -DCMAKE_MAKE_PROGRAM=/usr/bin/make \
        "-DCMAKE_C_COMPILER=$clang" "-DCMAKE_AR=$archiver" \
        "-DCMAKE_RANLIB=$ranlib" "-DCMAKE_LINKER=$linker" \
        "-DCMAKE_OSX_SYSROOT=$sdk" -DCMAKE_OSX_ARCHITECTURES=x86_64 \
        -DCMAKE_BUILD_TYPE=Debug "-DMEFPP_C_STANDARD=$standard" \
        -DBUILD_TESTING=ON -DMEFPP_BUILD_RESOURCES=ON \
        "-DPython3_EXECUTABLE=$py" "-DMEFPP_FUNPACK=$funpack" \
        "-DMEFPP_SOURCE_REVISION=$revision" "-DCMAKE_INSTALL_PREFIX=$prefix"
    runlog "build-c$standard" "$cmake" --build "$build" --parallel 1 --verbose
    # CTest: native primitives/header integration, CLI usage and seven installer cases.
    runlog "ctest-c$standard" "$ctest" --test-dir "$build" --parallel 1 \
        --output-on-failure --no-tests=error
    # Independent resources: require exact source pixels before real installation.
    runlog "resources-c$standard" "$py" "$work/verify.py" build \
        "$source_dir" "$build" "$prefix" "$standard" "$revision"
    # Private installation: install once, then verify all runtime files/provenance.
    test ! -e "$prefix" || stop "Prefix unexpectedly exists: $prefix"
    runlog "install-c$standard" "$cmake" --install "$build" --prefix "$prefix"
    runlog "payload-c$standard" "$py" "$work/verify.py" install \
        "$source_dir" "$build" "$prefix" "$standard" "$revision"
done

# Final preservation: verify historical engine/configuration and checkout unchanged.
/usr/bin/shasum -a 256 "$engine" "$configuration" > "$work/protected-after.sha256"
cmp "$work/protected-before.sha256" "$work/protected-after.sha256"
git rev-parse HEAD > "$work/checkout-after.txt"
cmp "$work/checkout-before.txt" "$work/checkout-after.txt"
test -z "$(git status --porcelain)" || stop "Checkout changed unexpectedly."
echo "PASS: private C90/C17 builds and installations. Records: $work"
echo "Historical engine remains selected; no observations processed."
)
```

## Installed layout and provenance

| Relative path | Purpose |
|---|---|
| bin/mefpp | New executable, statically linked to bundled Eclipse/qfits |
| config/mefpp.paf, omegacam.paf, wfi.paf | Distributed templates; project-edited PAFs are not overwritten |
| static_cal/OCAM_BPM_1x1.fits, WFI_BPM_1x1.fits | Uncompressed distributed masks |
| share/mefpp/licenses/* | Original component license texts |
| share/mefpp/source-sha256.txt | Native source-input inventory |
| share/mefpp/build-manifest.json | Source revision, language/tools/SDK/configuration and installed-file hashes |

Keep source/archive, compile_commands.json, CMake cache/generated headers, logs,
resource identities and installation manifest together. CMake links through the
compiler driver; setting CMAKE_LINKER is not an independent trace of the driver's
subordinate linker. Existing version-string inconsistencies remain tracked (#69).

BPM decompression is pixel-exact but not byte-reproducible: checksum-card timestamp
comments change at different execution times, affecting CHECKSUM and file hashes.
Record each actual file hash. Do not strip cards or rewrite metadata to make hashes
match. See the acceptance record for full header comparisons and checksum checks.

## Reinstallation, staging and rollback

The installer permits identical contents and rejects edited/conflicting files,
linked prefixes and links within the payload before copying. Existing ancestors
outside the prefix are resolved, allowing macOS /var. Preflight is not an atomic
transaction against concurrent filesystem changes. Use a fresh prefix for another
source/toolchain build; do not use installation as a way to overwrite user edits.

The actual Mac acceptance tested repeat installation of both builds and C17 Unix
DESTDIR staging. For an inspected build/prefix, repeat the same CMake install
invocation. For staging, supply DESTDIR only to that invocation; its result lives
under DESTDIR followed by the absolute runtime prefix. The manifest must retain
the runtime prefix, not the staging root. Do not stage over a real installation.

MEFPP_BUILD_RESOURCES=OFF is a code-only development option; a complete runtime
install from that build is deliberately rejected. The runtime requires both BPMs
and all PAFs. Optional legacy utilities/development archives are not installed.
The supported root/component configure and Makefile frontends delegate to CMake.
Historical internal recursive Makefiles under src/ins/qfits, sysconf/e_setup binaries
and independent qfits configure scripts are not supported entry points. Do not run
those old internal install rules.

No uninstaller is supplied. Before removing a disposable prefix, inspect its exact
path, manifest and any user changes; never recursively remove a historical/shared
installation. Keeping the old selected engine is the current rollback strategy.
A future switch must record and back up the saved selection, preserve all other
engine choices and verify the installed wrapper/resources. Reverting then restores
that recorded selection; it does not require deleting the candidate builds.

## Runtime handoff and remaining checks

Private installation does not change ~/.pycavi/pycavi_astrosoft.cfg or ~/.eclipse-rc.
Do not select these candidates for normal reduction merely because CTest passed.
First compare installed native outputs against the immutable CP Pup historical
anchor, keeping Python normalization separate, and qualify the installed Pycavi
wrapper. Calibration-building/WFI fixtures, failure propagation, memory and
chapman3 remain separate pending gates. A WFI mask is not a WFI reduction test.

## Maintenance rule

Update this guide in the same PR as any change to build/install entry points,
required tools/versions, platforms, resources/layout, configuration/selection,
upgrade/rollback or qualification status. Record the actual tested source commit,
platform, commands/results and limitations; label untested procedures as pending.
Keep the installation hub, root README, build reference and acceptance records
consistent. Preserve dated historical audits; do not rewrite old failures as passes.

## Failure-handling candidate, 26 October 2026

The focused failure/configuration correction adds the nonempty CTest entry
`native_failure_contract`; run it in both C90/C17 builds. Existing private Mac
engines and normal selection remain unchanged. Source regression checks passed;
rebuilt target build/install, installed-wrapper and observational acceptance remain
pending. See [the correction record](native-failure-correction-2026-10-26.md).
