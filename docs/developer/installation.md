# Developer installation: Python and native components

Native M3 path qualification, 30 October 2026: [paired Mac/Chapman checks](LINK)
passed both affected CTests at 113156b94fe68f7bf2848c93ecd7451551db2984,
including actual C execution from unrelated directories with separate inputs,
calibrations and destinations. Protected installed files/checkouts stayed unchanged.
PR #167 is ready for owner review; full M3 remains open. Current installation,
configured engine and Python dependency bounds remain unchanged.

M3 candidate, 30 October 2026: the new optional `pycavi project inspect` command
provides [read-only legacy metadata inspection](m3-project-inspection.md). Source invocation
and the package entry target pass agent and actual Mac/Chapman checks (15/15
on each target); this bounded increment is ready for owner review.
No installed package/script is changed by this delivery; a future reviewed wheel
provides the entry point. Existing setup commands/dependency bounds and native
installation/engine selection remain unchanged. No installation is requested now.

For ordinary users, start with the [quick installation guide](../installation.md).
This page retains detailed Python packaging and validation information.

## Maintained native installation guide, 25 October 2026

Use [the native mefpp installation guide](native-installation.md) for the bundled
CMake build, resources, private installation, verification, staging and rollback.
Intel Mac C90/C17 build/resource/private-install acceptance passed at source
41c8e6a544c1bc5122dc558e0c8cc7904214e1d0; see the
[acceptance record](native-mac-build-install-acceptance.md). Observational and
chapman3 qualification remain pending, and the historical engine stays selected.
Native installation does not install the Python wheel or other astronomy engines.

The sections below cover Python packaging and retain dated evidence. Their
historical platform-pending statements do not override newer pilot/acceptance
records or the maintained native guide. Update both guides with relevant changes.

## Current chapman3 evidence, 23 October 2026

The [chapman3 dependency inventory](chapman3-dependencies-2026-10-23.md)
updates the historical baseline and pending statements below. The isolated
Python 3.11 environment, installed-package tests, remote notebook connection,
selected native reductions and local Astrometry.net 0.98 detector tests now have
reported evidence. Dependency acceptance is still open. Full workflow auditing
and Python future-proofing are subsequent work, as clarified in roadmap.md.

Packaging implementation based on `2732d285fee41d266a5aace14ecb773ba357298c`.
This is the first roadmap item. It does not complete Mac/cluster acceptance,
notebook thinning, the scientific Pycavi library audit or the subsequent mefpp audit.
Any deviation from the roadmap requires discussion and Fernando's approval first.

## Scope and distribution identity

One canonical `pyproject.toml` and `MANIFEST.in` now live at the monorepo root.
Install from that root, not `Pycavi2`. The distribution name stays `pycavi`, the
imports stay `pycavi.*`, and the Python component source layout is unchanged.
The native CMake candidate nests qfits under `mefpp2/qfits5`; its build/install
is described in the maintained native guide. The Python source archive is not
a complete native wenu-imaging source release; obtain native code from Git.

Existing scientific dependency ranges are retained. IPython and scikit-image are
now declared because calibration imports them. The unnecessary pathlib backport
is removed. Python metadata narrows the prior unsupported >=3.9,<4 claim to
>=3.10,<3.13: Astropy 6.1 requires at least 3.10, and newer Python is not qualified.
This metadata is an installation boundary, not proof of validation on every
allowed interpreter/platform. Python 3.11 remains the operational reference.
The `notebooks` extra supplies Notebook and ipykernel; Tk remains an interpreter/
platform dependency, not a pip package. No working installation is upgraded.

The missing `Pycavi2/LICENSE` reference is removed from metadata. No replacement
license is invented; existing file notices are retained. The maintainer must
resolve the aggregate Python license before public package release.

## Preserve the reference first (Mac)

In the working wenu-imaging environment, these commands only report information:

```bash
python -c 'import sys, platform; print(sys.executable); print(sys.version); print(platform.platform())'
python -m pip list --format=freeze
python -m pip check
pycavi_setastro --help
```

Capture the exact Mac package versions and selected native engines before
constructing its installation constraints. `pip list --format=freeze` lists
versions without editable source URLs; it is an inventory, not automatically a
portable lock file. Conda packages, platform differences and direct dependencies
must be reviewed when preparing constraints. Do not resolve unconstrained newer
libraries into the working environment. There is not yet a verified Mac/Linux
lock file in this change.

## Ordinary Python installation (Mac and Linux)

Use a disposable environment created from an **existing reference Python 3.11**.
Do not change system Python, base Conda, raw inputs or existing products. Commands
below assume the reviewed constraints file has been prepared and paths have been
chosen; they are acceptance instructions, not evidence that Mac/cluster ran them.

```bash
python3.11 -m venv /path/to/new-wenu-env
/path/to/new-wenu-env/bin/python -m pip install --constraint /path/to/reference-constraints.txt /path/to/wenu-imaging
/path/to/new-wenu-env/bin/python -m pip check
```

For notebooks, install the same project with its optional application dependencies
in that same environment and with the same constraints:

```bash
/path/to/new-wenu-env/bin/python -m pip install --constraint /path/to/reference-constraints.txt '/path/to/wenu-imaging[notebooks]'
```

Activate that environment, move outside the checkout and populate a new workspace:

```bash
source /path/to/new-wenu-env/bin/activate
cd /path/to/work-area
pycavi_setup new-notebook-workspace
cd new-notebook-workspace
python -c 'import pycavi; print(pycavi.__file__)'
```

Setup copies 15 notebooks, 12 CFG/PAF templates, four historical WFI CSV tables
and their readme (32 files). They are loaded relative to the installed `pycavi`
package, not the source directory. Copies belong to the user. Existing files are
preserved by default; `pycavi_setup --overwrite DESTINATION` explicitly replaces
them, without a backup. Use it only for disposable workspaces or after backing
up edited files. Missing resources and copy failures return nonzero status.
New project templates leave personal directory values blank. Fill them using
notebook 00 or the current library configuration function before reduction.

Launch `python -m notebook` from the activated environment, and verify the
notebook kernel's `sys.executable` matches it before running cells. Kernel
registration and actual Tk/display operation must be checked on each target.

## External astronomy programs

The wheel does not install mefpp, qfits, SExtractor, SCAMP, SWarp, Astrometry.net,
funpack or astrometry indexes. Keep their existing versions for this stage.
Use `pycavi_setastro --help` for full options. For example, substitute actual
executable paths (the mefpp value is a binary, not its installation prefix):

```bash
pycavi_setastro --non-interactive \
  --mefpp /prefix/bin/mefpp \
  --sextractor /path/to/sex \
  --scamp /path/to/scamp \
  --swarp /path/to/swarp \
  --solve-field /path/to/solve-field
pycavi_setastro --check
```

Explicit overrides precede existing saved choices; otherwise saved choices are
preserved and missing choices are discovered in PATH order. SExtractor aliases
include `sex`, `sextractor` and `source-extractor`. Programs must be executable.
Without a terminal or with `--non-interactive`, selection does not prompt.
Filesystem scans happen only for explicitly requested `--search-root` paths;
never scan the entire shared home filesystem by default. Missing programs abort
without saving a partial configuration. Changes back up the existing CFG as
`.bak`, `.bak.1`, etc. Unchanged selections do not rewrite it.

The existing default `~/.pycavi/pycavi_astrosoft.cfg` and `[Paths]` keys are
preserved. A separate configuration can be selected without changing the normal
one, for example:

```bash
export PYCAVI_ASTROSOFT_CONFIG=/path/to/test-astrosoft.cfg
pycavi_setastro --non-interactive
pycavi_setastro --check
```

`load_executable_paths()` honors the same environment variable or an explicit
filename. `--config` selects a file for an individual setup/check command; use
the environment variable as well when the notebook must read that alternative.
The read-only check reports selected paths and native version/help output;
mefpp is checked for existence/execute permission only. These probes do not
establish engine compatibility or a successful reduction.

## Known workflow boundaries, retained for the next stages

- Notebook 03 passes the configured mefpp binary where reduction helpers expect
  a prefix containing `bin/mefpp`, `config` and `static_cal`. Keep the documented
  pilot prefix override until the shared notebook/library interface is repaired.
  The export of the executable path alone does not fix this resource boundary.
- Active source extraction can still ignore the saved SExtractor selection and
  rediscover through PATH. Keep the intended reference binary first in PATH.
  Consistent runtime selection belongs in the notebook/interface work.
- Notebook 00 uses Tk; general helper imports also require Tk. Headless *setup*
  and executable selection work without Tk, but unattended pipeline support is
  not established here. Packaging is not a new script runner.
- WFI CSVs are installed and copied under the workspace's `data` directory.
  The historical WFI notebook still has relative `../data`/personal path
  assumptions. WFI source is preserved; dedicated fixes and validation remain
  deferred. The CSVs are historical reference data, not an updated calibration DB.
- Existing subprocess/worker failure handling, BPM generation, photometric and
  Phase 3 issues are not repaired by packaging. All remain on their roadmap.
- Calibration import can attempt Gaia status retrieval; import success does not
  establish fully offline operation. Existing regex escape warnings remain.

## Recorded Linux cluster (reported by Fernando)

`chapman3.sc.eso.org`: CentOS 7, kernel 3.10.0-1160.71.1.el7.x86_64, glibc 2.17;
AMD EPYC 7742, 64 physical cores/128 threads, approximately 503 GiB RAM.
Home is shared GFS2 `/home1` (100 TB total, about 34 TB free when inspected);
`/tmp` is about 14 GB. No dedicated scratch path or scheduler allocation was
identified. Affinity includes 0-127; permission to use that capacity is unknown.

System Python is 3.6.8, user Anaconda base is Python 3.9.12/Conda 4.12.0.
Native tools: SExtractor 2.19.5, SCAMP 2.10.0, SWarp 2.38.0, Astrometry.net 0.85;
GCC 4.8.5, CMake 2.8.12.2; mefpp was not in PATH. Native dependency probes found
no missing shared libraries. This is characterization, not installation approval
or a successful pipeline test. Reference Python/environment provisioning and
compatible builds must be established without changing existing installations.
No OS, Python/library or engine upgrade is implemented by this patch.

## Reproduce packaging verification

In an isolated build environment with setuptools and wheel, build from the root:

```bash
python -m pip wheel --no-deps --no-build-isolation . --wheel-dir /tmp/wenu-wheels
python -c 'from setuptools.build_meta import build_sdist; build_sdist("/tmp/wenu-sdist")'
python -m pip wheel --no-deps --no-build-isolation /tmp/wenu-sdist/pycavi-0.1.0.tar.gz --wheel-dir /tmp/wenu-roundtrip
```

Install each wheel into a separate disposable interpreter, then run the installed
package tests from outside the checkout. The setup/discovery tests need only the
wheel (use `--no-deps` for this deliberately limited smoke test); that is not a
scientific runtime installation. Substitute actual paths:

```bash
cd /tmp
PYCAVI_SOURCE_ROOT=/path/to/wenu-imaging /path/to/test-env/bin/python /path/to/wenu-imaging/tests/test_installed_package.py
```

With scientific dependencies installed under the preserved reference constraints,
also check package consistency, installed module imports and existing regressions:

```bash
python -m pip check
MPLBACKEND=Agg python -m unittest discover -s /path/to/wenu-imaging/Pycavi2/tests -v
```

### Evidence for this patch

Ubuntu 24.04.3 x86_64/glibc 2.39, CPython 3.12.14, setuptools 84.0.0/wheel 0.48.0.
The test runtime uses the exact 72 dependency versions from the prior constrained
Linux audit environment (including NumPy 1.26.4, Astropy 6.1.7, Photutils 1.13.0,
SciPy 1.17.1, IPython 9.17.1, scikit-image 0.26.0); no existing environment was
updated. This is diagnostic Linux evidence, not the Mac reference lock.

- Root wheel and source archive build; source archive rebuilds to a wheel.
- Both installed wheels pass all nine packaging tests outside the checkout:
  resources match source bytes, setup/rerun/overwrite/failure behavior, missing
  resources, symlink refusal, paths with spaces, `sex` alias, headless selection,
  saved choices/backups, invalid selections and read-only engine checks.
- Sixteen installed scientific/PAPI modules import with constrained dependencies.
- Dependency consistency passes; ten existing regression tests pass.

Pending: native Intel Mac and CentOS 7/Python 3.11 wheel/runtime checks, actual
external engine and pilot reduction comparisons, approved portable constraints,
GUI/kernel checks and the license decision. No full portability, scientific
correctness, Phase 3 compliance or roadmap-stage completion is claimed.
