# Candidate native CMake build

Status: first stage-1 candidate; Intel Mac and chapman3 qualification is pending.
This builds the existing serial mefpp recipe, the complete 79-source Eclipse
archive and complete 18-source qfits archive. qfits lives in `mefpp2/qfits5`;
no historical installed native library or tracked binary is a build input.
Numerical algorithms and qfits allocator mode 2 / 2,000,000 entries are retained.

CMake and CTest >=3.29 are required. Initial supported build hosts are Darwin
and Linux with the existing POSIX services. Windows is explicitly rejected until
its platform adapters are qualified. Apple Silicon has not yet been tested.
Choose C90 or C17 explicitly in separate binary directories. This does not claim
strict ISO conformance of the legacy dependency sources: POSIX interfaces and
existing warnings remain. Only the new small primitive test uses pedantic errors.

Configure from repository root or directly from `mefpp2`. Example variables below
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

The `mefpp2/configure` executable is now a small CMake compatibility launcher;
`--help` lists supported arguments. It propagates CMake failures. Old recursive
Makefiles, sysconf/e_setup binaries, and independent qfits configure scripts are
historical sources, not supported entry points for this candidate. They are
preserved for audit/history and may still contain obsolete sibling paths.
The compatibility launcher does not run those scripts. Prefer direct CMake for
complete control. Do not run the old top-level make/install procedure.

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

The installer preflights the whole payload. It rejects missing files, symlink
paths, conflicting parent types and different existing contents before copying.
An identical repeated install is allowed. Use a private absolute prefix and never
point this candidate at the historical installation. Unix DESTDIR is applied once;
the staging root is excluded from the recorded runtime prefix. Installation does
not select the engine in Pycavi, edit ~/.pycavi or ~/.eclipse-rc, run reductions,
or alter project calibrations. No uninstaller is supplied. Preflight is protection
against ordinary mistakes, not an atomic transaction against concurrent changes.

## Executed test sections and boundaries

- `native_primitives` calls image_new, image_getmean and image_del with three known
  pixels, qfits_paf_query with a tiny PAF, and qfits_pixdump_float / qfits_pixin_float
  for exact float pixel conversion. It does not validate full MEF/FITS headers.
- `native_cli_usage` executes mefpp without arguments and requires nonzero status
  plus its usage text. This does not establish truthful reduction-failure exits.
- `native_install_contract` runs the production install template with synthetic
  resources: complete/repeated install, DESTDIR, edited-file preservation, symlink
  rejection, missing-resource rejection and non-directory-parent rejection.
  It does not decompress or certify the distributed BPMs.

Each corresponding script section is commented. F1 is partial; F2–F7 and the
native-reduction failure parts of F8 in the build specification remain pending.
Known source issues #69, #71, #74–#76 remain open, including version strings,
ignored engine status, warning/lifecycle and PAF/argument-order behavior. This
build candidate must not be described as memory-clean or scientifically validated.

The recipe's seven C++-style line comments were converted to block comments for
explicit C90 mode (#80); executable tokens were preserved. All other active C
source changes select the generated configuration header by name.
