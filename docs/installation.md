# Installation — quick start

Native M3 candidate, 30 October 2026: [explicit C execution paths](developer/m3-native-paths.md)
allow `mefpp` to select input/list/calibration/configuration and output/work/log
locations from an unrelated caller directory. Agent C90/C17 and scoped address/
undefined-behavior checks pass; actual Mac/Chapman qualification is pending.
Use a private review build; retain the current installation and configured engine.
The existing installation commands and Python dependency bounds are unchanged.

M3 candidate, 30 October 2026: the new optional `pycavi project inspect` command
provides [read-only legacy metadata inspection](developer/m3-project-inspection.md). Source invocation
and the package entry target pass agent and actual Mac/Chapman checks (15/15
on each target); this bounded increment is ready for owner review.
No installed package/script is changed by this delivery; a future reviewed wheel
provides the entry point. Existing setup commands/dependency bounds and native
installation/engine selection remain unchanged. No installation is requested now.

Last updated: 25 October 2026. The current native candidate is on
`fix/native-cmake-build` ([PR #81](https://github.com/fselman/wenu-imaging/pull/81));
it is not yet merged into main.

## Native mefpp

Prerequisites: a C compiler, CMake >=3.29, Make and `funpack` (CFITSIO tools).
Eclipse, qfits, configuration templates and compressed BPM resources are included.
No dependency packages are downloaded automatically. The frontend checks required
tools and explains missing prerequisites; macOS selects the active Xcode tools
and SDK, while Linux defaults to `cc`. Explicit overrides are optional.

From the repository root (or from `mefpp2`), the normal procedure is:

```sh
./configure --prefix="$HOME/.local/mefpp"
make
make install
```

Use a fresh private prefix; sudo is unnecessary. The default prefix, when omitted,
is `$HOME/.local/mefpp`. Configuration defaults to C90 and a serial Debug build;
`make install` ensures the build is complete before installing. The executable is
`PREFIX/bin/mefpp`; its PAFs and masks are in `PREFIX/config` and `PREFIX/static_cal`.
Existing edited/conflicting files are preserved by refusing the installation.
Installation does not change the engine selected by Pycavi or process observations.

`./configure --help` lists optional compiler/build-path settings. `make check`
runs developer tests and needs Python 3; Python is not required for the ordinary
native build/runtime. See [developer installation](developer/native-installation.md)
for qualification, staging, diagnostics and platform evidence.

**Status:** the normal C90 configure/make/install route, optional checks,
installed resources, repeat installation and staging passed on Intel macOS 13.7.8
at source 7c5238f8. Direct CMake C90/C17 acceptance is recorded separately.
chapman3, Apple Silicon and native Windows qualification remain pending.

## Pycavi

Use the separate [Python installation guide](developer/installation.md) with the
established Python 3.11 environment and reviewed dependency versions. Its wheel
does not install mefpp, SExtractor, SCAMP, SWarp, Astrometry.net or reference data.

A pip-versus-Conda/micromamba distribution is a deferred [roadmap TODO](developer/roadmap.md).
No mefpp package has been published through either route. Detailed tests, build
flags and acceptance histories stay under `docs/developer`.
