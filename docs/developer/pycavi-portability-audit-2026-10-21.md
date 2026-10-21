# Pycavi installation portability and library upgrade audit

Audit date: 21 October 2026. Source baseline:
`d17784d9603065f22773c2fbbd29a8d13e4a0d60`.

Scope: Python distribution, installed resources, notebook setup, Python/library
compatibility, external executable boundaries and macOS/Linux execution risks.
This is an audit and implementation proposal, not authorization to change
component code, scientific defaults or the working Mac environment. No component
source or notebook was changed. Native mefpp/qfits builds are separate work.

## Conclusion

The existing editable Python 3.11 Intel Mac pilot is valuable operational
evidence, but ordinary distribution is currently broken: built wheels and source
archives omit the notebooks, configuration and WFI data. A clean install also
omits runtime dependencies. Current-library installation requires API repairs,
not simply removing version ceilings. The calibration module fails to import
with Astropy 8.0.2 because it imports the removed `get_moon` function.

Keep the working Mac environment as the reference. Use a separate Python 3.12
upgrade environment first; expand Python/platform coverage only after scientific
comparisons. Do not upgrade the production environment in place.

## Evidence and reproducibility

Tests ran on a disposable Linux x86_64 worktree and virtual environments, using
CPython 3.12.14, glibc 2.39, setuptools 84.0.0 and wheel 0.48.0. No original
observational data, existing working installation or system package was changed.
These are Linux results, not native macOS or cluster certification.

Build from the monorepo root (outputs to a disposable directory):

```bash
python -m pip wheel --no-deps --no-build-isolation ./Pycavi2 -w /tmp/wenu-portability-wheels
```

The wheel built successfully as `pycavi-0.1.0-py3-none-any.whl`, but contained
zero files under each of `pycavi/config/`, `pycavi/notebooks/`, `pycavi/data/`.
A source archive built through `setuptools.build_meta.build_sdist` also contained
zero files under those three resource directories. Builds succeeded despite the
defect: build success alone is not installation acceptance.

Installed that wheel into an isolated environment, changed working directory to
`/tmp`, and ran `pycavi_setup`. Both resource groups raised `ModuleNotFoundError`;
the command printed errors and still exited successfully. The resource omission
is independent of optional scientific dependencies. Editable installs expose
source directories and can conceal this failure.

### Dependency environments actually tested

| Package | Existing metadata constraints, plus missing imports | Current-library diagnostic stack |
|---|---|---|
| Python | 3.12.14 | 3.12.14 |
| NumPy | 1.26.4 | 2.5.4 |
| SciPy | 1.17.1 | 1.18.1 |
| Astropy | 6.1.7 | 8.0.2 |
| Photutils | 1.13.0 | 3.1.1 |
| pandas | 2.3.3 | 3.0.6 |
| Matplotlib | 3.11.2 | 3.11.2 |
| scikit-image | 0.26.0 | 0.26.0 |
| IPython | 9.17.1 | 9.17.1 |
| Astroquery | 0.4.11 | 0.4.11 |
| Astroplan | 0.10.1 | 0.10.1 |
| PyKrige | 1.7.3 | 1.7.3 |
| lmfit | 1.3.4 | 1.3.4 |
| SymPy | 1.14.0 | 1.14.0 |
| ephem | 4.2.1 | 4.2.1 |

The current-library stack deliberately installed scientific dependencies first
and the wheel with `--no-deps` to characterize code beyond existing ceilings.
It is **not a dependency-consistent supported installation**: `uv pip check`
correctly reports Astropy, Photutils, pandas and NumPy constraint conflicts and
the omitted pathlib backport. Do not give that procedure as user installation
instructions. Current versions refer to what resolved on the audit date, not
permanent pins or a promise to track every newest release.

Clean installation using only declared requirements lacked IPython and
scikit-image. Calibration import stopped at missing `IPython`. After adding both
while resolving the Pycavi requirements together, calibration import passed and
`uv pip check` passed. Ten existing regression tests passed in this environment.

All ten existing tests also passed in the current-library stack, while importing
`pycavi.pycavi.pycavi_zpcal` failed on `get_moon`. The tests cover catalogue and
Chebyshev repairs, not the entire calibration/reduction path; some load functions
through AST or source paths. Installed-wheel smoke tests are needed separately.

An intermediate diagnostic installation added supplementary packages without
reasserting Pycavi constraints. It upgraded NumPy to 2.5.4 beside Astropy 6.1.7,
which failed on missing `np.in1d`. Re-resolving the wheel and supplementary
requirements together restored NumPy 1.26.4 and passing tests. This was not a
failure of the final constrained resolution; it demonstrates why partial
upgrades and unchecked environments must not define the supported stack.

## Confirmed defects and source risks

| Priority | Finding and evidence | Minimal direction for an approved repair |
|---|---|---|
| Blocking distribution | Explicit packages list omits resource namespaces; MANIFEST.in points at root `config/*`, `data/*` rather than actual package paths. Wheel and sdist resource omission reproduced. | Include intended installed resources explicitly; inspect both archives and run setup outside the checkout. Decide whether the roughly 50 MB of WFI catalogue CSVs ship or become explicit external inputs. |
| Blocking clean use | `pycavi_zpcal.py` imports IPython and skimage, absent from dependency declarations. Notebook server/kernel also undeclared. | Declare direct runtime dependencies; provide a documented notebook extra for notebook/ipykernel. Separate truly optional functionality only after checking notebook imports. |
| Blocking modern calibration | `pycavi_zpcal.py:32` imports `astropy.coordinates.get_moon`, used for Moon QC around line 1430. Astropy 8.0.2 import failure reproduced; removal documented in Astropy changelog. | Use supported `get_body("moon", time, location)` API and compare Moon QC at fixed times/sites with the old implementation. Preserve ephemeris choices. |
| Incorrect Python support claim | Metadata advertises Python >=3.9, but Astropy >=6.1.1 requires >=3.10. Resolver failure reproduced for 3.9. | Declare a tested support interval rather than >=3.9,<4.0. |
| New Python installation blocked | NumPy <2 has no usable CPython 3.13 wheels in the allowed range. Binary NumPy resolution failure reproduced for 3.13. | Upgrade dependency compatibility before claiming 3.13+ support; do not make unsupported source compilation the normal install path. |
| mefpp interface | Setup stores an executable path; notebook 03 treats it as an installation prefix; reduction code appends `/bin/mefpp`, `/config`, `/static_cal`. Pilot needed a local workaround. | Distinguish executable and resource directories, validate both and preserve existing configuration through migration. |
| Cluster setup | Shared tools module imports Tk unconditionally; notebook 00 creates a Tk root and event loop. | Make GUI optional at import time and support explicit noninteractive project configuration. Tk availability and display availability are separate requirements. |
| Failure reporting | Actual `run_command('exit 9', logfile=<temporary file>)` returned 0, despite nonzero shell exit. It scans log text instead of enforcing return code. Source busy-waits before draining pipes. | Check return codes, propagate errors and drain output safely; test spaces in paths and failed child commands. Preserve argument values. |
| Process lifecycle | `run_solve_field` uses `starmap_async(...).wait()` without retrieving results; closes without explicit join. Notebook uses visible CPU count minus 2. | Retrieve worker exceptions, clean up/join reliably, bound workers by allocation and memory, account for external threads. Validate spawn/forkserver. mefpp remains serial. |
| Setup preservation | `pycavi_setup` copies onto existing notebooks/configuration and catches errors without a failure exit. | Preserve edited files by default; provide explicit overwrite/backup behavior and meaningful exit status. |
| Executable discovery | Recursively scans `/usr`, `/usr/local`, `/opt/local`, `/home`, `/Users`, uses unordered sets, does not validate execute permission/version, lacks `/opt/homebrew` as a root, and omits `sex` alias despite runtime support. | Prefer explicit overrides and PATH, bounded optional search, deterministic results and executable/version checks. PATH can already find Apple Silicon Homebrew when correctly configured. |
| SExtractor selection | Active high-level extraction helper calls `sextractor.run(image_name)` without passing configured executable; wrapper probes PATH names. SCAMP/SWarp helpers accept paths. | Honor configured selection consistently; report resolved path/version in preflight. |
| Source-tree assumptions | Notebooks alter sys.path; WFI notebook reads `../data/...csv` and contains personal raw paths. Setup does not copy data. Distributed pycavi.cfg contains personal OCAM/Multi paths. | Support installed resources and explicit project inputs from an unrelated directory; use unset example paths rather than personal defaults. |
| Legacy dependency | PyPI `pathlib` backport is installed despite using standard-library pathlib. | Remove backport requirement after confirming supported Python floor. |
| Build metadata | Referenced `Pycavi2/LICENSE` absent; TOML license table deprecated. Backend emitted warnings including a 2027-02-18 migration deadline. | Maintainer verifies appropriate license/attribution; use current metadata syntax without inventing licensing terms. |

All 26 distributed Python files parsed under Python 3.12, with invalid-regex
escape SyntaxWarnings in PAPI wrappers and the alternate astromatic module.
These warnings are future maintenance items, not current syntax failures.
No GitHub Actions workflows were present at this baseline.

## Scientific compatibility probes and their limits

A synthetic two-position aperture probe used a 101-by-101 float32 image:
background 10 plus a Gaussian of amplitude 1000, sigma 2.1 pixels, centre
(50.3,49.6). TAN WCS: CRPIX=(51,51), CRVAL=(123,-35) degrees,
CDELT=(-0.2,+0.2) arcsec/pixel. Positions were (50.3,49.6) and (4.2,4.5);
aperture radius 1 arcsec, annulus 1.2–1.8 arcsec; exact aperture integration,
centre annulus masks, sigma clipping at 3, background times aperture area.

| Probe | Constrained stack | Current-library stack |
|---|---|---|
| Central background-subtracted aperture sum | 25927.8779830314 | 25927.877982284983 |
| Edge aperture sum after the same procedure | 778.5326520564885 | 778.5326519485262 |
| Resize to 20-by-20, anti_aliasing=True, output sum | 5081.8603515625 | 5081.8603515625 |

Relative flux differences were approximately 2.9e-11 and 1.4e-10. No warnings
were emitted by this probe. Photutils output renamed xcenter/ycenter to
x_center/y_center; the currently used aperture_sum column remained available.
This tests selected library calls directly, not the full blocked calibration
module. The zero-filled off-image annulus behavior of the edge example is not a
scientific endorsement of edge photometry or a production quality threshold.

NumPy 2 changes scalar promotion and compiled-library ABI; the in-place gain,
exposure and illumination operations deserve explicit float32/float64, FITS
endianness/scaling and overflow comparisons. No broad NumPy incompatibility was
established just by source search. pandas 3 changes copy/view and string dtype
behavior. An AST scan found nested assignments to dictionaries/configuration but
did not establish a production chained-DataFrame-assignment defect; do not
mislabel dictionary assignments as pandas failures. Verify CSV/missing-ID types,
joins, nulls and catalogue schemas with real and synthetic fixtures.

Astroquery is imported eagerly and attempts to retrieve Gaia status messages;
the audit observed "Status messages could not be retrieved". Site registry,
IERS/ephemeris caches, catalogue service schemas and saved query identities need
an offline/cache policy for cluster nodes. A cache-dependent import success does
not establish disconnected operation. Existing query endpoints must be checked
against service documentation before changes, without changing photometric
reference release or transformations as a side effect.

## Platform plan and recommended support policy

| Target | Existing evidence | Next validation |
|---|---|---|
| macOS 13.7.8 Intel | User's Python 3.11.14 editable install ran CP Pup pilot with historical native tools and notebook workarounds | Fresh wheel install, setup/resources, GUI/kernel, external paths and pilot comparison in separate upgrade environment |
| Linux audit host | Python 3.12.14 builds, imports, dependency resolution and limited tests/probes above | Full Python pipeline with real external programs and trusted immutable data |
| Linux cluster | Single-node model known; distro, glibc, scheduler/modules and allocation limits unknown | Identify environment before selecting wheels/native builds; test headless setup, worker limits, failures and offline data |
| macOS Apple Silicon | No native execution evidence | Native arm64 interpreter and matching native external executables; no accidental Intel/Rosetta mixing |
| Ubuntu Linux | No dedicated Ubuntu execution evidence | Specify release/architecture, Tk/headless choices, external packages and real pipeline checks |

PyPI release metadata on the audit date listed CPython-3.12-compatible Intel Mac
wheels with deployment tags <=13 for NumPy 2.5.4, SciPy 1.18.1, Astropy 8.0.2,
Photutils 3.1.1, pandas 3.0.6 and scikit-image 0.26.0. Matching arm64 wheels also
exist. This is encouraging availability evidence, not proof that every transitive
dependency or external tool installs/runs on Fernando's Mac. Do not assume all
new wheels require macOS 14 simply because some optimized alternatives do.

Recommended initial lanes:

1. Preserve/reference the existing Python 3.11 environment and real pilot outputs;
   capture exact Python, package, native executable, configuration and model identities.
2. Qualify Python 3.12 with a selected coherent NumPy 2/Astropy/Photutils/pandas
   stack. Current Photutils 3.1.1 requires Python >=3.12, NumPy >=2, SciPy >=1.15
   and Astropy >=7: latest Photutils cannot simply be added to Python 3.11.
3. Add newer Python (e.g. 3.14) after wheel availability, Python start methods,
   imports and scientific comparisons pass. Python 3.14 changes the POSIX default
   away from fork; macOS already uses spawn. Current module-level worker design
   is useful, but does not eliminate lifecycle/failure tests.

Keep reasonable declared compatibility ranges, plus exact tested constraints per
Python/platform for reproducibility. Avoid both freezing every user forever to
the 2024 stack and claiming all future <4.0 Python/library releases work. Test
updates on a separate candidate lane before promoting constraints. Consider
notebook/test extras; do not split dependencies on paper while active notebooks
still import them unconditionally. Keep Python package/import names unchanged.

## Proposed implementation stages (approval pending)

### A. Repair distribution without upgrading the scientific stack

Fix wheel/sdist resources, missing direct dependencies, Python metadata and
pathlib backport; resolve license metadata with the maintainer. Make setup errors
visible and preserve existing orchestration files. Add installed-wheel smoke
coverage from outside the source tree, both console entry points and notebook
resource counts (15 notebooks, 12 config files at baseline). WFI data needs an
explicit location/delivery decision. A wheel built from the sdist must also work.

### B. Repair portability boundaries

Agree executable/resource configuration, honor configured program selection,
provide headless project setup, and repair command/worker error propagation.
Check paths containing spaces, missing programs/resources, unsuccessful children,
worker limits and restarts. Preserve serial mefpp. These changes require their
own focused implementation review and real external command checks.

### C. Qualify current libraries in a separate environment

Replace removed APIs with scientifically equivalent public APIs, then relax
ceilings only to tested combinations. Run library-call probes, real installed
module imports, all existing regressions, notebook cells in fresh kernels,
Moon/time/site comparisons, calibrated aperture/flux/error/CSV/FITS checks and
the CP Pup pipeline against agreed reference tolerances. Include WFI regression
evidence when shared code changes. Scientific differences must be explained,
not dismissed because tests/imports pass. Phase 3 export remains issue #9;
photometric and astrometric qualification remains linked to #7 and #8.

### D. Make support maintainable

Add CI for archive contents, installed wheel/sdist, resource setup, dependency
consistency, imports, limited offline numerical tests and deprecation reporting.
Maintain a compact Python/platform matrix rather than every possible combination.
Keep real data/native-program acceptance as an explicit additional stage. No
full macOS/Linux portability claim until the corresponding native runs pass.

## Primary references checked for this audit

- [Setuptools package data](https://setuptools.pypa.io/en/latest/userguide/datafiles.html)
- [Astropy changelog, get_moon removal](https://docs.astropy.org/en/stable/changelog.html)
- [Photutils 3.1.1 requirements](https://photutils.readthedocs.io/en/3.1.1/getting_started/install.html)
- [NumPy 2 migration guide](https://numpy.org/doc/2.0/numpy_2_0_migration_guide.html)
- [pandas Copy-on-Write](https://pandas.pydata.org/docs/user_guide/copy_on_write.html)
- [Python 3.14 multiprocessing](https://docs.python.org/3.14/library/multiprocessing.html)
- Release metadata/wheel lists: PyPI JSON endpoints for
  [NumPy](https://pypi.org/pypi/numpy/2.5.4/json),
  [SciPy](https://pypi.org/pypi/scipy/1.18.1/json),
  [Astropy](https://pypi.org/pypi/astropy/8.0.2/json),
  [Photutils](https://pypi.org/pypi/photutils/3.1.1/json),
  [pandas](https://pypi.org/pypi/pandas/3.0.6/json),
  [scikit-image](https://pypi.org/pypi/scikit-image/0.26.0/json).

Recheck release requirements and wheel availability at implementation time.
