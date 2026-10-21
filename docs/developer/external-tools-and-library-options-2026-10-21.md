# External astronomy tools and library integration options

Checked 21 October 2026, following Fernando's agreement with the portability
audit direction and request for a coherent, maintainable system that uses
libraries where they simplify integration. This supplements the
[Pycavi portability audit](pycavi-portability-audit-2026-10-21.md).
No external software was installed or upgraded and no backend was replaced.

## Installed versus current upstream releases

Installed versions below are from the Mac inventory and working pilot, not a
new inspection of the Mac. Latest releases were checked against the upstream
GitHub REST `releases/latest` endpoints, not only search snippets or a development
branch's version string. Distribution availability may differ from upstream.

| Program | Recorded Mac installation | Latest published upstream | Release date |
|---|---|---|---|
| SExtractor | 2.28.0, MacPorts `/opt/local/bin/source-extractor` | 2.29.0 | 30 September 2026 |
| SCAMP | 2.10.0, `/opt/local/scamp/bin/scamp` | 2.15.0 | 12 April 2026 |
| SWarp | 2.38.0, MacPorts `/opt/local/bin/swarp` | 2.41.5 | 13 February 2021 |
| Astrometry.net, including solve-field | 0.95, Homebrew revision `0.95_2` under `/usr/local/Cellar/astrometry-net/0.95_2/bin/` | 0.97 | 2 December 2024 |

Homebrew `_2` is a packaging revision, not upstream version 0.95.2. `solve-field`
belongs to Astrometry.net; it is not a separately versioned astronomical engine.
The older 0.93 source directory on the Mac is not the installed solver used in
the successful pilot. The binary `/usr/local/bin/sex` may be another installation;
its version and actual use must be resolved in preflight rather than assumed.

Release notes relevant to this work (not an exhaustive old-to-new comparison):

- SExtractor 2.29.0: updated internal FITS code, modern C declarations, format
  warning fixes and longer filename support.
- SCAMP 2.15.0: fixes a stability-type loop-index error and long-filename buffer
  overflow, plus modern compiler warnings. Earlier intervening releases also
  exist; do not infer numerical equivalence from the latest release notes alone.
- SWarp 2.41.5: GCC 10 compilation and large COMBINE_BUFSIZE fixes. Its old release
  date does not mean a local 2.38.0 executable is current.
- Astrometry.net 0.96 explicitly added NumPy 2 support; 0.97 includes minor fixes
  and changes CFITSIO helper build/install defaults. A Python upgrade must also
  check the solver's Python components, interpreter paths and linked libraries.

Retain these versions as the measured pilot baseline. Qualify selected new
versions in a separate prefix/environment, with exact paths, versions, build
options, libraries, configuration and index identities recorded. Do not upgrade
all four engines and every Python library in one untraceable production change.

## Library candidates

Candidate versions below were retrieved from PyPI release metadata on the audit
date. They are research observations, not newly accepted dependencies.

| Existing role | Candidate | Value and limitations |
|---|---|---|
| SExtractor detection, background, measurements | SEP 1.4.1, maintained at sep-developers/sep; existing Photutils for complementary measurements | SEP exposes SExtractor-derived C algorithms through NumPy-array functions. Best first experiment. It does not generate all existing catalogue columns/FITS-LDAC layouts automatically; Kron/AUTO conventions, Petrosian measurements, flags, masks and uncertainties need explicit qualification. |
| SWarp reprojection/coaddition | reproject 0.21.0 | Astropy-compatible reprojection and weighted mosaicking, output/temporary memmap support. Current stable reproject_and_coadd exposes mean, sum, first, last, min and max, not median. Background matching is constant additive adjustment per image, distinct from the pilot's SWarp mesh-background processing. It is not a drop-in replacement for median/LANCZOS3 SWarp. |
| SCAMP astrometric refinement | Astropy WCS fitting and tweakwcs 0.9.2 | Useful catalogue-based fitting/alignment building blocks. They do not establish equivalence to SCAMP's distortion/focal-plane and joint astrometric/photometric modelling. Characterize the exact current SCAMP use before selecting a subset to replace. |
| solve-field blind solving | astrometry 4.3.0, neuromorphicsystems/astrometry | Python bindings to Astrometry.net C functions. Takes star positions, not raw FITS images; image preprocessing/extraction moves to our library path. Still needs index files and native engine code. The package maintains a pinned, patched Astrometry.net snapshot; compare maintenance/version provenance as well as API convenience. |

SEP is not a shell wrapper around a hidden SExtractor executable: it provides
array-level algorithms. Its stated compatibility aim is not a guarantee that
every current SExtractor 2.29 feature or catalogue will be reproduced. Its project
documents the transition from older sep and temporary sep-pjw maintenance to
sep-developers/sep; use the current maintained distribution, not both names.

The Python astrometry binding can support a cleaner array workflow, but is not
the official solve-field command exposed unchanged. Its index convenience API
downloads missing files. Any evaluation must explicitly reuse staged index paths
and prove offline behavior; do not automatically fetch a large new index set on
the cluster. Existing 5200-series files remain separate scientific resources.
No binding installation, index compatibility test or maintenance audit was run
in this research step.

Photutils is already a Pycavi dependency. Reuse its existing aperture/QC role
where suitable rather than adding another package for an identical task. Adding
SEP plus custom reconstruction of every SExtractor output could be more work
than retaining SExtractor; assess total maintained code, not executable count.

## Recommended architecture direction

Keep one supported production backend per stage and one explicit configuration
and provenance path. First simplify the current integrations: resolve the
configured executable consistently, eliminate ambiguity between active PAPI
wrappers and alternate implementations, use reliable process handling, and record
all actual versions. This is proposed focused consolidation, not permission to
delete historical interfaces without checking callers.

Prefer libraries when they reduce our integration code and have suitable
coverage, wheels, maintenance and scientific behavior. A well-managed external
engine is acceptable when it is the simpler reliable implementation. Avoid
turning each stage into a permanent catalogue of interchangeable backends.

Near-term sequence:

1. Complete ordinary package/resource installation and environment validation.
2. Preserve the existing engines as the reference production path, and qualify
   updated releases separately from Python/library migration.
3. Run a bounded SEP extraction experiment on copies of the pilot inputs. Compare
   background/noise maps, segmentation/deblending, detections, centroids, AUTO and
   PETRO-related measurement requirements, flags and flux uncertainties. Verify
   downstream SCAMP/FITS-LDAC and final catalogue schema requirements. Promote
   only if the maintained code and scientific validation burden decrease.
4. Evaluate in-process astrometry against the same 320 solved CCDs and staged
   indexes, only after extraction is established. Compare solution success,
   distortion/WCS accuracy, failure recovery, runtime and peak memory.
5. Evaluate reproject and WCS-refinement alternatives afterward. A change from
   median to mean, background algorithm, interpolation kernel, distortion model
   or photometric matching is a scientific-method decision, not just plumbing.

The pilot output is 19987 by 19099 pixels, with ten 32-CCD exposures. Measure
memory/I/O and parallel resource use at that scale; a small demonstration mosaic
does not establish production suitability. Keep mefpp serial in this milestone.

## Decisions to settle before backend implementation

- Preserve existing AUTO/PETRO output semantics or explicitly redesign them?
- Is median combination scientifically required for the immediate products?
- Which current SCAMP distortion and photometric options must be retained?
- Which supported release combinations and platform package sources can be
  installed consistently on Intel Mac, arm64 Mac, Ubuntu and the cluster?
- Does a library actually remove locally maintained wrappers, or add another
  patched native dependency plus conversion code?

These questions should be answered through inspection and bounded experiments
before a production replacement is selected. Raw data, reference reductions,
calibration conventions and Phase 3 scientific validation remain preserved.

## Primary sources

- [SExtractor 2.29.0 release](https://github.com/astromatic/sextractor/releases/tag/2.29.0)
- [SCAMP 2.15.0 release](https://github.com/astromatic/scamp/releases/tag/v2.15.0)
- [SWarp 2.41.5 release](https://github.com/astromatic/swarp/releases/tag/2.41.5)
- [Astrometry.net releases, including 0.96 NumPy 2 support and 0.97](https://github.com/dstndstn/astrometry.net/releases)
- [SEP documentation and maintenance lineage](https://sep.readthedocs.io/en/stable/)
- [SEP aperture conventions](https://sep.readthedocs.io/en/stable/apertures.html)
- [reproject stable coaddition API](https://reproject.readthedocs.io/en/stable/api/reproject.mosaicking.reproject_and_coadd.html)
- [reproject background matching](https://reproject.readthedocs.io/en/stable/mosaicking.html)
- [tweakwcs](https://tweakwcs.readthedocs.io/en/stable/)
- [Python astrometry bindings](https://github.com/neuromorphicsystems/astrometry)
- [Astrometry.net index and engine documentation](https://astrometry.net/doc/readme.html)

Recheck releases and platform availability when implementation starts.
