# Installation — quick start

Last updated: 25 October 2026. This page is for users; build diagnostics and
qualification records belong in [the developer guide](developer/native-installation.md).

**Current status:** native mefpp source build/private installation has passed on
Intel macOS 13.7.8. Linux/chapman3 is pending. The candidate is on
`fix/native-cmake-build` ([PR #81](https://github.com/fselman/wenu-imaging/pull/81)),
not yet main. There is no published mefpp Conda package or one-command installer.

## Native mefpp: current source-install route

1. Obtain the candidate source and install prerequisites: Xcode tools,
   CMake >=3.29, a Make build tool and `funpack`. Eclipse, qfits, PAF templates
   and compressed BPMs are already included in the source.
2. From the repository root, configure, build and install into a new private
   prefix. This basic user build omits developer tests and therefore needs no
   Python interpreter. It is not the full qualification procedure.
3. Use the printed `bin/mefpp` path when a reduction has been qualified. Installation
   alone does not change the engine selected by Pycavi.

The following block is for an Intel Mac. It checks the platform and keeps the
build outside the checkout. Other platforms must wait for their tested instructions.

```bash
(
set -eu
actual="$(uname -s):$(uname -m)"
test "$actual" = "Darwin:x86_64" || {
    echo "STOP: these instructions require an Intel Mac; detected $actual." >&2
    exit 1
}
test -f mefpp2/CMakeLists.txt || { echo "STOP: run from the candidate repository root." >&2; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: preserve and inspect local changes." >&2; exit 1; }
build="$(mktemp -d "$HOME/mefpp-build.XXXXXXXX")"
prefix="$HOME/.local/mefpp-candidate"
test ! -e "$prefix" && test ! -L "$prefix" || { echo "STOP: choose a fresh private prefix." >&2; exit 1; }
# Configure/build/install: bundled native sources and distributed resources, C90, serial.
cmake -S mefpp2 -B "$build" -G "Unix Makefiles" \
    -DCMAKE_MAKE_PROGRAM=/usr/bin/make -DCMAKE_BUILD_TYPE=Debug \
    "-DCMAKE_C_COMPILER=$(xcrun --find clang)" "-DCMAKE_AR=$(xcrun --find ar)" \
    "-DCMAKE_RANLIB=$(xcrun --find ranlib)" "-DCMAKE_LINKER=$(xcrun --find ld)" \
    "-DCMAKE_OSX_SYSROOT=$(xcrun --show-sdk-path)" -DCMAKE_OSX_ARCHITECTURES=x86_64 \
    -DMEFPP_C_STANDARD=90 -DBUILD_TESTING=OFF "-DMEFPP_FUNPACK=$(command -v funpack)" \
    "-DMEFPP_SOURCE_REVISION=$(git rev-parse HEAD)" "-DCMAKE_INSTALL_PREFIX=$prefix"
nice -n 10 cmake --build "$build" --parallel 1
nice -n 10 cmake --install "$build"
echo "Private executable: $prefix/bin/mefpp"
)
```

This basic source installation omits developer tests. For full acceptance use
the developer procedure; the recipe above is not a new target qualification run.

## Pycavi and the full application

Use [Python installation instructions](developer/installation.md) with the
established Python 3.11 environment and reviewed dependency versions. The Python
wheel does not install mefpp or the external astronomy engines. Full-application
installation also needs the selected SExtractor, SCAMP, SWarp, Astrometry.net and
reference data; these are separate from the native mefpp prerequisites.

## Simplifying this further

A packaged Mac/Linux installation is the next distribution design task. Proposed
deferred TODO: compare pip platform wheels with Conda/micromamba packages for
native mefpp and the application environment. No package manager is selected;
this work does not block the current native qualification. See the
[package-manager assessment](developer/native-distribution-options.md).

Keep this page short: prerequisites, install/use and links. Keep compiler probes,
long verification scripts, defect histories and acceptance ledgers under
`docs/developer`.
