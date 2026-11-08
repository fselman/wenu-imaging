# wenu-imaging

Astronomical image reduction with Pycavi (Python), mefpp (C) and bundled
qfits/Eclipse. The Python package and imports retain the name `pycavi`.

- [Install](docs/installation.md)
- [Prepare inputs](docs/data-preparation.md)
- [Run recipes and inspect products](docs/recipes.md)
- [Acceptance tests by recipe](docs/acceptance.md)
- [Architecture and scientific guides](docs/developer/README.md)
- [Issues and work summaries](https://github.com/fselman/wenu-imaging/issues)

Raw observations are read-only. Keep orchestration and products in separate
locations. Preserve accepted reference products when testing a modified version.

## Licensing

Retain existing component/source license notices, including PAPI notices. The
aggregate Pycavi license declaration remains unresolved: old metadata names an
absent `Pycavi2/LICENSE`. Resolve it before public release. Native components
carry their own licenses and are not part of the Python wheel.
