# Installation

Use an isolated Python environment and a separate native installation prefix.
Installing a candidate does not select it for normal reductions.

## Python

From the repository root:

```sh
python -m pip install .
```

For notebooks:

```sh
python -m pip install '.[notebooks]'
pycavi_setup /path/to/new-notebook-workspace
```

Setup preserves existing files unless `--overwrite` is explicit. Use command
`--help` for options. The wheel does not install mefpp, Source-Extractor, SCAMP,
SWarp, astrometry.net or its indexes. Check their configured executable paths in
the target environment before reduction.

## Native build

Requirements include a C compiler, CMake 3.29 or newer, Make and CFITSIO `funpack`
for the bundled compressed resources. From the repository root, configure a new
candidate build and private prefix explicitly:

```sh
cmake -S . -B /path/to/new-build -DMEFPP_C_STANDARD=17 \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/path/to/private-prefix
cmake --build /path/to/new-build --parallel 2
cmake --install /path/to/new-build
```

These are new-install examples. During development, reuse the selected qualified
build, compiler, SDK, dependencies and cache rather than routinely reconfiguring.
The normal installed executable is `PREFIX/bin/mefpp`; resources are installed
under the prefix. Installation refuses conflicting existing resource files.

The standalone native bias recipe is a development target, built with
`MEFPP_BUILD_BIAS_ADAPTER=ON` and `MEFPP_BUILD_BIAS_RECIPE=ON`. It also requires an
exact 40-character `MEFPP_SOURCE_REVISION` and the selected qualified native ASDF
prefix (`MEFPP_ASDF_PREFIX`). This does not make it the normal installed engine.
Do not install or upgrade ASDF dependencies merely to follow these examples.

After installation run the [primary acceptance suite](acceptance.md) appropriate
to the supported recipes/instruments. An import or `--help` smoke check alone does
not establish product equivalence. Keep the old installation available until the
candidate's products are accepted.
