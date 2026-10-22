# Focused Python compatibility review — 22 October 2026

Fernando approved bringing this limited part of the Pycavi audit forward before
continuing chapman3 installation. This is a compatibility review, not the full
scientific library audit. The initial review changed no runtime software.
The subsequently approved environment installation and narrow notebook fix are
recorded below. Dependency declarations, scientific algorithms, native
installations and observational products remain unchanged.

## Source and evidence identity

- Reviewed local packaging commit `7608491`; the published packaging commit is
  `c406e3390d29f37b9e53380bf3f8763ac84f4713`.
- Both packaging commits identify tree `5920541fbea995d9bb636e39a7b7b51dfef6dfa4`.
- Root `pyproject.toml`, installed Python modules, notebook code cells, and the
  two existing regression test files were inspected.
- Fernando reports the historical development machines were his Mac, chapman,
  and Lientur Celedon's Linux laptop. Versions were probably selected from the
  existing installations, without a deliberate minimum-version study. Treat
  the inherited lower bounds as declarations, not measured compatibility limits.
- Chapman runtime evidence below comes from Fernando's terminal output, rather
  than execution from this review workspace. The reviewer has no remote shell.

## Findings

### Python version and package policy are different questions

All 26 Python files under `Pycavi2/pycavi` and all 136 code cells in its 15
distributed notebooks parse with Python 3.9's grammar, using Python 3.12's
`ast.parse(..., feature_version=(3, 9))`. This includes historical scripts and
the retained WFI notebook; parsing does not validate those workflows.

The new setup implementation uses `importlib.resources.files`, which exists in
Python 3.9. No source-language feature requiring Python 3.10 was identified in
this focused scan. A grammar check is not execution on Python 3.9 and does not
establish complete standard-library/API compatibility.

The installation boundary **does** have a definite dependency reason: the
retained `astropy>=6.1.1,<7` requirement selects an Astropy series whose minimum
Python is 3.10. The original metadata claimed Python >=3.9 while also requesting
that Astropy version. The packaging change aligned the Python declaration with
the retained dependency, rather than demonstrating that Pycavi algorithms need
Python 3.10. Restoring 3.9 would require qualifying a different dependency set;
changing only `requires-python` or bypassing the installer would not do that.

### The old scientific stack cannot execute every current path unchanged

`pycavi_catalogue.apply_kriggin_illumination_correction` constructs
`RegularGridInterpolator(..., method='cubic')`. SciPy added the spline methods
in version 1.9. The old chapman SciPy 1.7.3 therefore lacks an API used by this
current catalogue correction path. Importing the module can still succeed,
because the interpolator is constructed when the function runs.

The existing `test_kriging_uses_shared_repeat_guard` regression exercises that
path with temporary synthetic FITS files. This establishes a source/API reason
for **SciPy >=1.9 for this path**, not a validated minimum environment for the
whole application. It does not justify the stronger inherited SciPy >=1.12 bound.
Do not switch interpolation methods to make the test pass: that would change
the scientific implementation.

Older notebook orchestration may not have called this newer function. Its
historical success is compatible with this finding; no old run has been
reconstructed or declared invalid.

### The Pandas obstacle is a Linux wheel baseline, not a Python failure

The official Pandas 2.3.3 CPython 3.11 x86-64 wheel is tagged
`manylinux_2_24_x86_64.manylinux_2_28_x86_64`. Its lowest advertised glibc
baseline is 2.24, above chapman3's 2.17. This explains pip's rejection of that
binary on chapman3. Changing the interpreter alone does not change host glibc.

The reviewed source uses `pandas.read_csv`, `DataFrame`, column/index operations,
CSV output and Astropy table conversions. This scan found no feature that
specifically requires **Pandas 2.3.3**. That exact version came from the Mac
inventory; it is not even a package lower bound (the package requests >=2.1.4).
This is not proof that Pandas 1.2.5, 2.3.2 or any other complete alternative set
passes the scientific workflow. No version substitution is made by this review.

### Dependency inventory and remaining qualification

| Dependency | Current declared range | Source use | Review conclusion |
|---|---|---|---|
| NumPy | >=1.26.3,<2 | Array operations, reductions, Chebyshev basis and least squares | No 1.26-specific feature identified; lower bound not qualified |
| SciPy | >=1.12,<2 | Optimization, distributions, interpolation, distances | Cubic regular-grid interpolation needs >=1.9; full minimum still unqualified |
| Astropy | >=6.1.1,<7 | FITS, tables, WCS, coordinates, units, statistics, modeling | Selected dependency requires Python >=3.10; necessity of this Astropy floor unqualified |
| Photutils | >=1.8,<2 | Sky apertures/annuli and aperture photometry | Old 1.1 import alone does not test current aperture calls/results |
| Matplotlib | >=3.8,<4 | Plotting and QC figures | No 3.8-specific feature identified in scan; old/current output equivalence unqualified |
| Pandas | >=2.1.4,<3 | CSV/dataframe operations and table conversions | No need for exact 2.3.3 found; older-version qualification pending |
| scikit-image | >=0.19 | `transform.resize(..., anti_aliasing=True)` | Old 0.19.2 imports; current numerical call/output still unqualified there |
| SymPy | >=1.12,<2 | Symbolic expressions and NumPy lambdify for exported Chebyshev models | Historical version not recorded; Chebyshev export/round-trip regressions pass in the old environment |
| ephem | >=4.1.2,<5 | Dates and surrounding new moons for association | Historical version and association equivalence pending |
| astroplan | >=0.10,<1 | Moon illumination | Historical version and numerical equivalence pending |
| astroquery | >=0.4.7,<1 | Gaia and SDSS catalogue access | Historical version pending; import/live service success are distinct |
| PyKrige | >=1.7.1,<2 | UniversalKriging and model evaluation | Historical version and model equivalence pending |
| lmfit | >=1.3.2,<2 | Model fitting | Historical version and fit equivalence pending |
| IPython | >=8 | Display helper | Historical version pending; notebook server and kernel versions are separate |

The inventory is focused source evidence, not exhaustive proof that no newer API
is used. Transitive package constraints, ABI compatibility, optional branches,
service behavior and scientific equivalence remain separate checks. Neither all
lower bounds nor their upper bounds have been systematically qualified here.

## Runtime evidence and its limits

| Environment | Evidence actually available |
|---|---|
| Old chapman Python 3.9.12 | NumPy 1.21.5, SciPy 1.7.3, Astropy 5.0.4, Photutils 1.1.0, Matplotlib 3.5.1, Pandas 1.2.5, scikit-image 0.19.2 import. `pycavi` is absent from its ordinary import path. With current sources explicitly added, 9 of 10 existing regressions pass; the cubic-interpolation test errors (details below). |
| New chapman Python 3.11.14 | Approved scientific dependencies installed. pip check passes, all nine initial installed packaging tests pass, all ten targeted regressions pass (including cubic interpolation). Nine runtime module imports pass. Named notebook kernel imports Pycavi and renders inline PNG; Mac Firefox connection confirms chapman3/interpreter/package identity. Full reduction remains pending. |
| Mac Python 3.11.14 | Reported installed-package tests and ten targeted regressions passed, with full scientific dependencies. This is not full pipeline validation. |
| This review workspace | Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. Grammar scan passes. Actual NumPy-only Chebyshev function definitions, extracted via AST, recover a known degree-five weighted fit at 1e-12 tolerance and rank 36. A synthetic cubic constant-grid interpolation passes. These narrow checks are not runs of the entire existing suite or evidence for Python 3.9. |

The workspace lacks Astropy, SymPy and several other runtime dependencies; the
complete existing regression suite was not run here during this review. No
package installation was performed to compensate. Do not substitute these
isolated checks for executing the existing tests on chapman3.

## Completed old-environment regression check on chapman3

Fernando ran the existing regression suite on 22 October 2026 using
`/home/fselman/anaconda3/bin/python`, Python 3.9.12, with the current checkout
added to the source path. Ten tests ran in 1.379 seconds: **9 passed, 1 errored**.
The failing test was `test_kriging_uses_shared_repeat_guard`, at
`pycavi_catalogue.py:315`; SciPy 1.7.3 raised
`ValueError: Method 'cubic' is not defined` during construction of
`RegularGridInterpolator`. This reproduces the source/API incompatibility.

The nine passing tests cover Chebyshev weighted fitting and model export,
catalogue correction signs/provenance/repeat guards, catalogue cleaning,
temporary catalogue preparation, selected notebook catalogue cells, and plotting
call signatures. Their success is evidence against treating all inherited
version minima as necessary for these particular tests. They do not exercise
the full photometric module, live catalogue queries, actual plotting functions
under the old stack, the native engines or complete reductions.

The original command with an expanded dependency inventory is retained below
for reproducibility; Fernando used its shorter variant that printed the
interpreter/Python version and executed the same tests. Do not request a repeat
of this suite without a new reason.

Use the explicit old interpreter, current checkout sources only for this
diagnostic, no bytecode writes, and temporary plotting state. Existing tests use
temporary synthetic inputs and do not run the reduction engines. A failed run is
useful evidence, including missing dependencies; do not install replacements yet.

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  "$HOME/anaconda3/bin/python" - <<'PY'
import importlib.metadata as metadata
import os
from pathlib import Path
import sys
import tempfile
import unittest

root = Path.home() / "Software/wenu-imaging"
assert (root / "Pycavi2/tests/test_catalogue_workflow.py").is_file(), root
sys.path.insert(0, str(root / "Pycavi2"))
print("Interpreter:", sys.executable, flush=True)
for name in ("numpy", "scipy", "astropy", "photutils", "matplotlib",
             "pandas", "scikit-image", "sympy", "ephem", "astroplan",
             "astroquery", "pykrige", "lmfit", "ipython", "notebook", "ipykernel"):
    try:
        print(name, metadata.version(name), flush=True)
    except metadata.PackageNotFoundError:
        print(name, "NOT INSTALLED", flush=True)

with tempfile.TemporaryDirectory(prefix="wenu-compat-") as temporary:
    os.environ["MPLBACKEND"] = "Agg"
    os.environ["MPLCONFIGDIR"] = temporary
    suite = unittest.defaultTestLoader.discover(str(root / "Pycavi2/tests"))
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
PY
```

This source-path diagnostic does not install or certify the Python 3.9 package.
If missing dependencies prevent loading a test module, record that limitation
before drawing conclusions about the underlying numerical tests.

## Proposed decision after that evidence

### Complete candidate resolution, 22 October 2026

Fernando's next dry run succeeded with Pandas 2.3.2 and the narrowly scoped
`--no-binary=astroplan` exception to `--only-binary=:all:`. Astroplan 0.10.1 is
published on PyPI as a source archive only; its isolated build requirements and
metadata preparation succeeded. This is a package-format issue, not evidence
of interpreter incompatibility. Its wheel build and runtime still need testing.

Evidence file supplied by Fernando: `Pasted text(20261022-111128).txt`.
The complete plan ends in `Would install` without an error, and does not propose
replacing the installed NumPy 1.26.4, SciPy 1.17.1, Matplotlib 3.11.2,
ContourPy 1.3.2 or Pillow 12.2.0. Existing Pycavi remains installed.

The remaining direct pins resolve as Astropy 6.1.7, Photutils 1.13.0,
Pandas 2.3.2, scikit-image 0.20.0, IPython 9.17.1, astroquery 0.4.11,
astroplan 0.10.1, PyKrige 1.7.3, lmfit 1.3.4, SymPy 1.14.0 and ephem 4.2.1.
The selected compiled dependencies have compatible wheel tags; this remains
resolution evidence, not a runtime or full scientific validation result.

Differences in the numerical/imaging dependencies compared with the recorded
Mac environment are:

| Dependency | Mac | Chapman candidate | State |
|---|---|---|---|
| Pandas | 2.3.3 | 2.3.2 | Proposed, not installed |
| ContourPy | 1.3.3 | 1.3.2 | Already installed; PNG rendering passed |
| Pillow | 13.0.0 | 12.2.0 | Already installed; PNG rendering passed |
| PyWavelets | 1.9.0 | 1.8.0 | Proposed transitive dependency, not installed |

Some utility dependencies and platform-specific credential backends also differ.
Do not claim this is an exact Mac environment copy. No minimum requirement in
`pyproject.toml` needs changing to accept this candidate. Fernando explicitly
approved Pandas 2.3.2, PyWavelets 1.8.0 and installation of the reviewed stack on
22 October 2026 ("Proceed", after the complete resolution and differences were
presented). Installation and targeted tests then succeeded, as recorded below.
Next characterize remaining runtime imports and remote notebook prerequisites.
Keep the old base environment and existing native engines intact.

### Installation and regression result, 22 October 2026

Fernando supplied `Pasted text(20261022-111516).txt` showing successful
installation in the new isolated environment, including the approved Pandas
2.3.2 and PyWavelets 1.8.0. Astroplan 0.10.1 built as a pure-Python wheel
(`astroplan-0.10.1-py3-none-any.whl`, SHA256
`aa5b4994ff532c996db82897da2de0510d95732d01ee3b074f00570e045ddb18`).

- `python -m pip check`: no broken requirements.
- All nine installed-package tests: pass, 0.621 seconds.
- All ten existing numerical/catalogue/notebook-contract regressions: pass,
  0.534 seconds, including the cubic interpolation test that errored in the old
  environment.
- Records directory on chapman3: `/home/fselman/wenu-runtime-check.0XWSKR`.
  The executed command saves `before.txt`, `install-report.json`, `installed.txt`
  and `conda-explicit.txt` there. Those record files themselves have not been
  retrieved into the review workspace.

The source-path regression tests and installed-package tests cover different
contracts; neither establishes a complete installed scientific reduction.
Fernando then ran the installed-module import check outside the checkout with
`PYTHONPATH` empty and user-site packages disabled. All nine checked modules
loaded from the new environment's `site-packages/pycavi`: instrument, tools,
association/reduction, solve, astromatic_tools, Chebyshev, catalogue, kriging
and zpcal. `Failed imports: []`. The Gaia client printed an archive release
notice during zpcal import, but no import error occurred. Live service queries
and their compatibility remain unvalidated.

Notebook/kernel installation and remote browser access, scientific reference
comparisons and the rest of the library audit remain outstanding. No engine or
data changes were part of this installation. The next notebook dependency dry
run should constrain the already installed stack and request the Mac-tested
Notebook 7.0.6 and ipykernel 6.25.0 versions.

That constrained notebook dry run subsequently succeeded (Fernando's
`Pasted text(20261022-112434).txt`), proposing additions only. It retains
Notebook 7.0.6 and ipykernel 6.25.0, selects Jupyter Server 2.21.1,
JupyterLab 4.6.4, pyzmq 26.4.0, argon2-cffi-bindings 21.2.0 and Tornado 6.6.
Some notebook infrastructure builds differ from the Mac inventory. Existing
scientific packages are constrained to their installed versions.

Fernando then supplied `Pasted text(20261022-112723).txt`: Jupyter installation
completed and pip check passed. The named kernel `wenu-imaging-chapman3` was
registered within the environment at
`/home/fselman/.conda/envs/wenu-imaging/share/jupyter/kernels/wenu-imaging-chapman3`.
An actual nbclient-executed notebook cell verified the kernel prefix/interpreter,
imported Pycavi from installed site-packages and produced inline PNG output.
Result: `PASS: notebook kernel, Pycavi import, and inline PNG`.
Debugpy emitted frozen-module breakpoint warnings, without preventing this test.
Browser/server/tunnel access remains pending. Workspace materialization and
starting a loopback-only notebook server are the next steps, followed by the
Mac SSH tunnel and Firefox check.

The subsequent fresh notebook in Mac Firefox printed
`chapman3.sc.eso.org`,
`/home/fselman/.conda/envs/wenu-imaging/bin/python` and
`/home/fselman/.conda/envs/wenu-imaging/lib/python3.11/site-packages/pycavi/__init__.py`.
This confirms the remote browser/server/kernel connection and installed-package
identity. The setup/start commands selected the separate workspace
`/home/fselman/omegacam/workflows/wenu-imaging-test`; the workspace inventory has
not independently been retrieved. No reduction notebook has been executed.
Next register/check existing external executable paths and review project
configuration and known integration blockers before a scientific pilot.

External executable registration subsequently succeeded at
`/home/fselman/.pycavi/pycavi_astrosoft.cfg`. Fernando's `--check` output confirms
mefpp executable presence at `/home/fselman/opt/local/mefpp/bin/mefpp`
(no version probe), Astrometry.net 0.85 at
`/usr/local/astrometry/bin/solve-field`, SExtractor 2.19.5 at `/usr/bin/sex`,
SCAMP 2.10.0 at `/usr/bin/scamp`, and SWarp 2.38.0 at `/usr/bin/swarp`.
No reductions were executed by this check. The known executable-versus-prefix
mismatch in notebook 03 remains unresolved; recording the correct executable
path does not fix that interface. Notebook 00 also still invokes Tk widgets;
remote Firefox alone does not supply a desktop display for that dialog.

Fernando then configured the isolated project paths. Raw inputs remain
`/home/fselman/fits/`; the new project root is
`/home/fselman/omegacam/testing/wenu-imaging-test/`, with `static_calib/`,
`calib/`, `std/`, `science/` and `logs/` paths. Configuration backup reported:
`/home/fselman/omegacam/workflows/wenu-imaging-test/config/pycavi.cfg.backup-20261022-084823-253647`.

Source tracing confirms notebook 03 assigns the full saved mefpp executable to
`mefpp_dir`, but its reduction helpers append `/bin/mefpp`, `/config/...` and
`/static_cal/...`. With the registered path this would construct
`/home/fselman/opt/local/mefpp/bin/mefpp/bin/mefpp` and similarly invalid resource
paths. The proposed narrow correction is to adapt notebook 03 to pass the
existing installation prefix, derived from its known `bin/mefpp` layout, while
retaining the correctly saved executable path. Fernando approved that narrow
notebook correction and focused path-resolution check ("Agreed").

### Approved notebook prefix correction

Notebook 03 now uses
`mefpp_dir = os.path.dirname(os.path.dirname(executable_paths['mefpp']))`.
Its existing `os` import is retained. This one-line adapter is for the existing
`PREFIX/bin/mefpp`, `PREFIX/config` and `PREFIX/static_cal` layout; arbitrary
executable/resource layouts are not established. The saved executable path and
all reduction helpers, commands and scientific settings are unchanged. This
does not implement BPM construction or the larger notebook-thinning stage.

A new stdlib-only installed-package regression reads the installed notebook,
executes its actual prefix assignment with a temporary installation fixture,
checks the actual bias command and BPM path expressions, and exercises the
actual PAF fallback-copy function in a disposable output directory. It launches
no engine and does not validate scientific BPM content or reduction results.

The test failed with the old installed notebook at the prefix assertion, then
passed after the one-line correction. A fresh wheel was built from a clean
disposable source copy and installed without dependencies into a separate local
Python 3.12.14 test environment. All **10 installed-package tests** pass (0.522
seconds), outside the source checkout. An initial build attempt in the old
working directory encountered a stale build/dist-info collision; the disposable
clean-source build succeeded without packaging changes. The science regression
suite was not repeated locally, since scientific code/dependencies did not
change and several scientific dependencies are absent in this test environment.
Chapman3's working notebook copy and installed wheel still need this update;
no reduction has run as part of the correction.

Primary package-format reference:
[Astroplan 0.10.1 release files](https://pypi.org/project/astroplan/0.10.1/).

Preserve both environments. The current tests have now been compared with the
old stack; changing interpreter does not restore all current functionality.
The new Python 3.11 environment already works for numerical and plotting checks,
so continuing it with an explicitly qualified Linux package resolution remains
a candidate. A separately qualified Python 3.9 dependency set is another
candidate, not a decision already made. No newer package versions are requested
and no different scientific algorithms are proposed.

Any requirement changes or substitute exact versions must be reviewed with
Fernando before implementation. An old interpreter plus modern libraries is
different from reproducing the historical software checkout and environment.
The later full Pycavi audit, trusted science reference comparisons and native
mefpp audit remain outstanding.

## Remote notebook requirement retained

Restore the server and Python kernel on chapman3, with Firefox locally on the
Mac through SSH local forwarding. No X11 forwarding. Notebook/ipykernel presence,
kernel identity, inline plotting and the remote connection are now verified as
recorded above. Retain this connection procedure for subsequent sessions.

```bash
# Chapman3, selected environment and intended notebook workspace:
python -m notebook --no-browser --ip=127.0.0.1 --port=8888

# Separate Mac terminal, using the actual working SSH hostname/alias:
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 \
  -L 8888:127.0.0.1:8888 fselman@chapman3.sc.eso.org
```

Use the port actually selected by Jupyter (8888 in this example), retain token
authentication, and open its token URL at `http://127.0.0.1:8888` in Mac Firefox.
These are retained instructions, not actions performed by this review.

## Primary references inspected

- [Astropy 6.1.1 distribution metadata: Python >=3.10](https://pypi.org/project/astropy/6.1.1/).
- [Python 3.9 importlib resources documentation: files added in 3.9](https://docs.python.org/3.9/library/importlib.html#importlib.resources.files).
- [SciPy 1.9.3 RegularGridInterpolator documentation: spline methods added in 1.9](https://docs.scipy.org/doc/scipy-1.9.3/reference/generated/scipy.interpolate.RegularGridInterpolator.html).
- [Pandas 2.3.3 official release files, including CPython 3.11 Linux wheel tags](https://pypi.org/project/pandas/2.3.3/).
