#!/bin/sh
# Shared configure/make frontend. Native build logic remains in CMake.
set -eu
fail() { echo "ERROR: $*" >&2; exit 1; }
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
source_dir=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
repository_dir=$(CDPATH= cd -- "$source_dir/.." && pwd -P)
entry_dir=$(pwd -P)
case "$entry_dir" in
    "$source_dir"|"$repository_dir") ;;
    *) fail "Run configure/make from the repository root or mefpp2 directory." ;;
esac
state_dir="$entry_dir/.mefpp-config"
action=${1:-help}
shift || true
help() {
    cat <<'EOF'
Usage: ./configure [options]
Then: make; make install. Optional developer checks: make check.

  --prefix=PATH          Private absolute runtime prefix (default: $HOME/.local/mefpp)
  --build-dir=PATH       Separate binary directory (default: ./build-native)
  --with-cc=FILE         C compiler executable (also honors CC)
  --with-funpack=FILE    BPM decompressor executable (also honors FUNPACK)
  --c-standard=90|17     Explicit language mode (default: 90)
  --enable-tests        Configure developer tests; requires Python 3
  --disable-tests       Omit developer tests (default)
  --with-python=FILE     Python used for developer tests
  --disable-resources   Code-only developer build; runtime install is rejected
  --source-revision=ID   Revision identity for exported sources
  --help                Print this help without changing configuration

CMake >=3.29 and a Make build tool are required. macOS defaults to active Xcode
compiler/archive tools and SDK; Linux defaults to cc. No packages are downloaded.
CMAKE, MAKE, CC, AR, RANLIB, LD, FUNPACK and PYTHON can select explicit tools.
Use a fresh binary directory when changing compiler, SDK or language mode.
make install preserves conflicting/edited files; no engine selection is changed.
EOF
}
# Read state as literal data: no generated shell code, eval or Make interpolation.
read_value() {
    test -f "$state_dir/$1" && test ! -L "$state_dir/$1" || fail "Invalid frontend state; rerun ./configure."
    IFS= read -r value < "$state_dir/$1" || fail "Incomplete frontend state; rerun ./configure."
}
resolve_tool() {
    resolved=$(command -v "$1" 2>/dev/null) || fail "$2 not found: $1. Install/select it before configuring."
    test -f "$resolved" && test -x "$resolved" || fail "$2 must name an executable file: $1"
    case "$resolved" in *';'*|*'
'*) fail "$2 path must not contain newlines or semicolons." ;; esac
    case "$resolved" in /*) ;; *) resolved="$entry_dir/$resolved" ;; esac
}
if test "$action" != configure; then
    case "$action" in help) help; exit 0 ;; build|install|check|clean) ;; *) fail "Unknown frontend action: $action" ;; esac
    test -d "$state_dir" && test ! -L "$state_dir" && test -f "$state_dir/ready" && test ! -e "$state_dir/configuring" ||
        fail "No successful configuration. Run ./configure first."
    read_value cmake; cmake_bin=$value
    read_value build_dir; build_dir=$value
    case "$action" in
        build) exec "$cmake_bin" --build "$build_dir" --parallel 1 ;;
        install) exec "$cmake_bin" --install "$build_dir" ;;
        clean) exec "$cmake_bin" --build "$build_dir" --target clean --parallel 1 ;;
        check)
            resolve_tool "$(dirname -- "$cmake_bin")/ctest" "CTest matching CMake"
            ctest_bin=$resolved
            "$cmake_bin" -S "$source_dir" -B "$build_dir" -DBUILD_TESTING=ON
            "$cmake_bin" --build "$build_dir" --parallel 1
            exec "$ctest_bin" --test-dir "$build_dir" --parallel 1 --output-on-failure --no-tests=error
            ;;
    esac
fi

prefix="${HOME}/.local/mefpp"
build_dir="$entry_dir/build-native"
compiler=${CC:-}
funpack=${FUNPACK:-funpack}
python=${PYTHON:-}
standard=90
tests=OFF
resources=ON
revision=""
for argument in "$@"; do
    case "$argument" in
        --help|-h) help; exit 0 ;;
        --prefix=*) prefix=${argument#*=} ;;
        --build-dir=*) build_dir=${argument#*=} ;;
        --with-cc=*) compiler=${argument#*=} ;;
        --with-funpack=*) funpack=${argument#*=} ;;
        --with-python=*) python=${argument#*=} ;;
        --c-standard=*) standard=${argument#*=} ;;
        --enable-tests) tests=ON ;;
        --disable-tests) tests=OFF ;;
        --disable-resources) resources=OFF ;;
        --source-revision=*) revision=${argument#*=} ;;
        *) fail "Unsupported configure option: $argument; use --help." ;;
    esac
done
case "$prefix" in /*) ;; *) fail "--prefix must be an absolute path." ;; esac
test "$prefix" != / || fail "Choose a private prefix, not /."
case "$standard" in 90|17) ;; *) fail "--c-standard must be 90 or 17." ;; esac
case "$build_dir" in /*) ;; *) build_dir="$entry_dir/$build_dir" ;; esac
# Normalize dot components before checking identity, even when parents do not exist.
remaining=$build_dir
normalized=""
while test -n "$remaining"; do
    case "$remaining" in
        */*) component=${remaining%%/*}; remaining=${remaining#*/} ;;
        *) component=$remaining; remaining="" ;;
    esac
    case "$component" in
        ""|.) ;;
        ..) normalized=${normalized%/*} ;;
        *) normalized="$normalized/$component" ;;
    esac
done
build_dir=${normalized:-/}
# Refuse an in-source binary directory before CMake can create its probe files.
if test -d "$build_dir"; then build_dir=$(CDPATH= cd -- "$build_dir" && pwd -P); fi
case "$build_dir" in "$source_dir"|"$repository_dir") fail "Use a separate binary directory, not the source directory." ;; esac
# Keep line-oriented state unambiguous and avoid CMake list separators in paths.
for item in "$prefix" "$build_dir"; do
    case "$item" in *';'*|*'
'*) fail "Paths must not contain newlines or semicolons." ;; esac
done
# A failed CMake reconfiguration must not leave an older build falsely selected.
test ! -L "$state_dir" || fail "Refusing linked frontend state: $state_dir"
if test -e "$state_dir"; then
    test -d "$state_dir" && test -f "$state_dir/format" && test "$(cat "$state_dir/format")" = 1 || fail "Preserving unexpected frontend state: $state_dir"
else
    mkdir "$state_dir"
    printf '%s\n' 1 > "$state_dir/format"
fi
for name in cmake build_dir ready configuring; do test ! -L "$state_dir/$name" || fail "Refusing linked frontend state file: $name"; done
rm -f "$state_dir/ready"
: > "$state_dir/configuring"

resolve_tool "${CMAKE:-cmake}" CMake
cmake_bin=$resolved
case "$(uname -s)" in
    Darwin)
        command -v xcrun >/dev/null 2>&1 || fail "Xcode command-line tools are required (xcrun missing)."
        if test -z "$compiler"; then compiler=$(xcrun --find clang) || fail "Cannot locate Xcode clang."; fi
        archiver=${AR:-$(xcrun --find ar)}
        ranlib=${RANLIB:-$(xcrun --find ranlib)}
        linker=${LD:-$(xcrun --find ld)}
        sdk=$(xcrun --show-sdk-path) || fail "Cannot locate the active macOS SDK."
        make_program=${MAKE:-/usr/bin/make}
        ;;
    Linux) compiler=${compiler:-cc}; make_program=${MAKE:-make}; archiver=${AR:-}; ranlib=${RANLIB:-}; linker=${LD:-}; sdk="" ;;
    *) fail "This candidate supports Darwin/Linux; native Windows qualification is pending." ;;
esac
resolve_tool "$compiler" "C compiler"; compiler=$resolved
resolve_tool "$make_program" "Make build tool"; make_program=$resolved
if test "$resources" = ON; then resolve_tool "$funpack" "funpack (CFITSIO tools, or --with-funpack=PATH)"; funpack=$resolved; fi
if test -n "$python"; then resolve_tool "$python" Python; python=$resolved; fi
if test -z "$revision"; then
    revision=$(git -C "$source_dir" rev-parse HEAD 2>/dev/null) || revision=unknown
fi
set -- -S "$source_dir" -B "$build_dir" -G "Unix Makefiles" \
    "-DCMAKE_C_COMPILER=$compiler" "-DCMAKE_MAKE_PROGRAM=$make_program" \
    "-DCMAKE_BUILD_TYPE=Debug" "-DCMAKE_INSTALL_PREFIX=$prefix" \
    "-DMEFPP_C_STANDARD=$standard" "-DBUILD_TESTING=$tests" \
    "-DMEFPP_BUILD_RESOURCES=$resources" "-DMEFPP_SOURCE_REVISION=$revision"
if test "$resources" = ON; then set -- "$@" "-DMEFPP_FUNPACK=$funpack"; fi
if test -n "$python"; then set -- "$@" "-DPython3_EXECUTABLE=$python"; fi
if test -n "$archiver"; then resolve_tool "$archiver" archiver; set -- "$@" "-DCMAKE_AR=$resolved"; fi
if test -n "$ranlib"; then resolve_tool "$ranlib" ranlib; set -- "$@" "-DCMAKE_RANLIB=$resolved"; fi
if test -n "$linker"; then resolve_tool "$linker" linker; set -- "$@" "-DCMAKE_LINKER=$resolved"; fi
if test -n "$sdk"; then set -- "$@" "-DCMAKE_OSX_SYSROOT=$sdk" "-DCMAKE_OSX_ARCHITECTURES=$(uname -m)"; fi
"$cmake_bin" "$@"
printf '%s\n' "$cmake_bin" > "$state_dir/cmake"
printf '%s\n' "$build_dir" > "$state_dir/build_dir"
rm -f "$state_dir/configuring"
: > "$state_dir/ready"
printf '\nConfigured: %s\nPrefix: %s\nNext: make; make install\nOptional developer tests: make check\n' "$build_dir" "$prefix"
