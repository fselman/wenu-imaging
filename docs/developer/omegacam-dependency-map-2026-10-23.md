# OmegaCAM notebook dependency map, 23 October 2026

## Scope and evidence

Fernando authorized this read-only requirements map after the bounded SCAMP
checks were merged. It describes the tracked notebook/library path at commit
`9ee7ff998a3d98e8dc6fbecf16e1e07ac55b8c30`. It changes no notebooks, scientific
library, engine selection, package versions or data. Source inspection identifies
requirements; it does not establish that those requirements work on a target.
Reported target evidence is in the [chapman3 inventory](chapman3-dependencies-2026-10-23.md).

Paths below are relative to `Pycavi2/pycavi/`. The notebook sequence has no
separate distributed `02` notebook: `01` constructs the partition tree and `03`
uses association/reduction classes. `0_wfi_select_cals.ipynb` and the packaged
`data/wfi_*_query_*.csv` files belong to deferred WFI work. The alternate
`09_pycavi_makeCatalogue_testing.ipynb` and `pycavi_astromatic.py` are present but
are not substitutes for the main notebook/PAPI path mapped here.

## Stage requirements and current coverage

| Stage / notebook | Library entry points and Python requirements | Engines, resources and services | Evidence and boundary |
|---|---|---|---|
| `00_pycavi_project_config` | `pycavi_tools.ProjectInfo`, `read_pycavi_config`; Tkinter/Tcl/Tk, NumPy, Matplotlib, Astropy through tools imports | Working-directory `config/`, writable project directories; `ProjectInfo` opens a native Tk window | Tcl import/version and configured pilot paths checked. A local Mac Firefox connection does not provide a remote Tk display; this GUI path is not headless-qualified. Existing explicit-path setup is a separate tested path. |
| `01_pycavi_partition_data` | `PartitionsTree`, `Instrument`, tools; NumPy, Astropy FITS, ephem | Raw FITS headers and project/instrument CFG; readable raw tree and writable partition/list/log directories | Nine manually selected pilot partitions / 60 inputs were checked. That is not a test of full raw-tree scanning and association through this notebook. |
| `03_pycavi_run` | `ExposuresPartition`, association functions, `mefpp_reduce_bpm/bias/dome/sky/science`, `mefpp_normalize_science`; NumPy, Astropy, ephem | mefpp executable plus install prefix `config/` and `static_cal/`; project PAF, input lists, MEF BPM and dependency links | Pilot native reduction and once-only normalization have recorded checks. Complete automatic association/orchestration is not qualified. Installed BPM copy is current behavior; BPM generation remains later audit work. |
| `04_pycavi_solve` | `run_py4_solve` → `run_solve_field`, `solvefield`, `create_wcs_frame`; NumPy, Astropy, multiprocessing, tools | Astrometry.net executable, native libraries and Python helpers, `astrometry.cfg`, index FITS files; per-exposure detector output directories | Local 0.98 with Python 3.11 passed helper/compiled checks and 32/32 detector solves in each of two exposures. Diagnostic calls do not qualify the pool runner, failure propagation, assembled MEFs or scientific accuracy. |
| `05_pycavi_scamp` | `scamp_lists`, extraction preparation, `run_sextractor_on_target`, `run_scamp_on_target`; Astropy, tools, PAPI `SExtractor`/`SCAMP` | SExtractor; generated `.sex/.param/.conv/.nnw`; FITS_LDAC and `.ahead`; SCAMP; VizieR Gaia DR2; native plotting backend for notebook `CHECKPLOT_DEV=PDF` | Extraction, offline single-detector linear fit and native live Gaia DR2 retrieval passed independently. Notebook uses `MOSAIC_TYPE=FIX_FOCALPLANE`; this and PDF output are not covered by the checks (`UNCHANGED`, plots disabled). |
| `06_pycavi_swarp` | `get_swarp_lists_dict`, `prepare_to_swarp`, `run_swarp`, `update_headers`; Astropy, tools, PAPI `SWarp` | SWarp, solved images, SCAMP `.head`, frame lists, output/weight files, writable `resamp/` and `swap/` | Synthetic constant-image resampling passed. Multi-exposure median/background processing, actual wrapper, weights and header propagation are not qualified by that fixture. |
| `07_pycavi_zpcal` | `ZPCalibration`, plotting/file-discovery helpers; NumPy, pandas, IPython, Matplotlib, SciPy, Astroquery, Astroplan, Astropy, Photutils, scikit-image | Coadd and its ancestor frames/list, instrument metadata, photometric catalogue/cache; current notebook chooses `query_calibrator="Gaia"` | Import of `pycavi_zpcal` passed. The Gaia DR3/GSPC query and subsequent calibration have not been exercised on chapman3. SkyMapper and SDSS are selectable alternatives, not current default equivalence claims. |
| `07b_pycavi_zpcal_qc` | `extract_calibration`, residual/illumination plots, save/read illumination data; NumPy, pandas, Matplotlib, SciPy, Astropy, Photutils plus zpcal import closure | Calibration products, photometric/reference CSV, residual and illumination CSV/plots; original-frame metadata | Import evidence only for this complete path; production QC results unqualified. This existing science-photometry QC is distinct from the deferred new calibration-product QC library. |
| `07c_pycavi_zpcal_qc_and_illum` | Above plus Chebyshev and kriging modules; SymPy, PyKrige, lmfit | Calibration residuals, model outputs and plots | Both model libraries are imported even if only one model branch is used. Limited regressions do not validate this notebook. |
| `08a_pycavi_illum_chebyshev` | Chebyshev fit/evaluation/export, zpcal plots, also imports kriging; SymPy, PyKrige, lmfit plus preceding scientific stack | Selected illumination CSV and model/output directories | Synthetic Chebyshev fitting/export and notebook plotting-call contracts have regression coverage. Full data fitting remains unqualified; do not infer PyKrige is dispensable because of the notebook title. |
| `08b_pycavi_illum_kriging` and `08c_pycavi_illum_read_kriging` | `kriging_interpolation`, uncertainty/model save/read helpers, zpcal helpers; PyKrige `UniversalKriging`, lmfit `Model`, SciPy and scientific stack; `08c` also imports Chebyshev | Residual data, sampled kriging model FITS and output plots | Imports pass; the earlier shared repeat-guard regression is not a test of full kriging fitting, uncertainty estimation or model persistence. |
| `09_pycavi_makeCatalogue` | SExtractor helpers; catalogue load/crossmatch/clean/correction/check plots; NumPy, pandas, Astropy, SciPy, Matplotlib, SymPy through catalogue imports, zpcal import closure | Coadds with photometric headers, SExtractor outputs; `gaia3_qry_<target>_raw.csv` from calibration; selected Chebyshev/kriging models; SkyMapper comparison in the final code cell | Limited one/two/three-filter catalogue and correction regressions pass. Gaia CSV reuse, complete science catalogue, online SkyMapper comparison and real photometric accuracy remain unqualified. |

All stages importing `pycavi_tools` also import Tkinter, NumPy, Matplotlib and
Astropy at module load. An unused notebook import can still be an installation
requirement in the current code. Import presence and actual algorithm use must
not be confused. Standard-library facilities such as `configparser`, `urllib`,
`multiprocessing`, `subprocess` and `tkinter` are not separate pip distributions.
Tkinter nevertheless requires a Python build with working Tcl/Tk support.

## Direct Python requirements

These are the 14 distribution requirements declared in root `pyproject.toml`,
mapped to actual imports. Versions are reported installed chapman3 versions,
not newly proven minima or a portable lock. The focused compatibility review
and scientific audit remain necessary to justify supported ranges.

| Distribution / import | Reported chapman3 version | Source consumer / role |
|---|---|---|
| NumPy / `numpy` | 1.26.4 | Tools, reduction, solving, photometry, catalogue and illumination arrays |
| SciPy / `scipy` | 1.17.1 | zpcal optimization/statistics; notebook interpolation; kriging and catalogue `RegularGridInterpolator(method='cubic')` |
| Astropy / `astropy` | 6.1.7 | FITS, WCS, coordinates, units, tables, time, statistics and aperture context throughout |
| Photutils / `photutils` | 1.13.0 | zpcal and QC aperture/annulus photometry |
| Matplotlib / `matplotlib` | 3.11.2 | Tools, zpcal, catalogue and kriging plotting |
| pandas / `pandas` | 2.3.2 | Reference CSV, calibration/residual tables, catalogue/model handling |
| scikit-image / `skimage` | 0.20.0 | zpcal `transform.resize` |
| IPython / `IPython` | 9.17.1 | zpcal `display`, notebook interaction |
| Astroquery / `astroquery` | 0.4.11 | zpcal Gaia and SDSS clients |
| Astroplan / `astroplan` | 0.10.1 | zpcal lunar illumination |
| PyKrige / `pykrige` | 1.7.3 | Universal kriging |
| lmfit / `lmfit` | 1.3.4 | Kriging model fitting |
| SymPy / `sympy` | 1.14.0 | Chebyshev symbolic expressions |
| ephem / `ephem` | 4.2.1 | Partition/reduction date and lunar calculations |

`requires-python` is `>=3.10,<3.13`; the selected interpreter is 3.11.14.
The `notebooks` extra declares Notebook `>=6,<8` and ipykernel `>=6,<7`.
Reported Notebook 7.0.6 / ipykernel 6.25.0 and the named chapman3 kernel worked
through the Mac SSH tunnel. Jupyter Server/Client and widgets/support packages,
ContourPy, Pillow, PyWavelets and numerical/native runtime libraries are
additional installed/transitive dependencies. Their exact resolution belongs
in the captured full inventory, not an invented second list of direct imports.
`pip check` passed; it checks metadata consistency, not service or scientific
compatibility. No package additions or removals are recommended from this map.

## External data and network distinctions

| Consumer | Requirement observed in source | Qualification / next boundary |
|---|---|---|
| SCAMP/PAPI and notebook 05 | Wrapper server `vizier.u-strasbg.fr`; notebook `GAIA-DR2` / `REDDEST` | Native small-field retrieval passed. Direct curl access to the advertised HTTPS route also passed; saved configuration was not migrated. |
| `ZPCalibration.get_gaia_dr3_gspc_df` | Astroquery `Gaia.launch_job_async`; join `gaiadr3.gaia_source` and `gaiadr3.synthetic_photometry_gspc`; SDSS or Johnson-Cousins synthetic bands; target-dependent CSV cache | Separate service/client/schema path from SCAMP Gaia DR2. No target execution evidence. Current query has no `TOP` cap and sets Gaia `ROW_LIMIT=-1`; a future dependency probe should be separately bounded, not run this production query merely as a connectivity test. |
| `ZPCalibration.get_skymapper_df` and `crossmatch_against_SkyMapper` | `urllib.request` CSV requests to the source's `http://skymapper.anu.edu.au/sm-cone/public/query`; raw/clean caches and expected columns | Untested calibration alternative and active final notebook-09 comparison. Catalogue comparison uses a one-degree request; do not launch it as an incidental requirement inspection. Existing cached data can mask connectivity failures. |
| `ZPCalibration.get_sdss_df` | `SDSS.query_sql(..., data_release=17)` through Astroquery, expected PSF magnitudes | Untested alternative. A successful Gaia query would not establish SDSS availability or footprint coverage. |
| `get_moon_from_frames` | Original-frame dates/pointing and observatory name; `EarthLocation.of_site`, `get_moon`, `AltAz`, Astroplan illumination | Site registry and Earth-orientation/cache behavior need target characterization. No blanket network/offline claim from imports; no site download or cache modification was run for this map. |
| Filter conversion functions in tools | SVO URLs appear as references beside hardcoded effective-width/pivot-wavelength tables | These source comments are not evidence of a runtime SVO query; do not add a live SVO requirement solely from a URL search. |

No service was queried while creating this map. Cached catalogue identity,
query, release, radius, columns, units and provenance must eventually be recorded
alongside calibration products; existing filenames alone do not prove these.

## Resources, filesystem and executable selection

- Project `config/pycavi.cfg`, `omegacam.cfg` and `omegacam.paf` are distinct from
  installed templates and the user executable file `~/.pycavi/pycavi_astrosoft.cfg`.
  `Instrument` reads project CFG; `copy_paf` prefers project PAF over native-prefix
  configuration, then copies to partition `mefpp.paf` when absent. Existing
  partition PAFs are not automatically refreshed by changing a template.
- Native mefpp depends on Eclipse/qfits linkage and its config/static calibration
  installation, not a Python import named qfits. `funpack` is explicitly used by
  `mefpp2/Makefile` during static-calibration installation. Its integer round trip
  passed separately. `fpack` is a useful qualified inverse, not an observed
  compulsory call in the mapped notebook path.
- PAPI SExtractor writes its parameter/filter/neural-network files from embedded
  defaults. These are writable work products, not evidence of a missing external
  `.nnw` package. Its setup searches `source-extractor`, `sextractor`, `sex` when
  no path is passed. `run_sextractor_on_target` constructs `SExtractor()` and
  does not forward a selected executable path. Thus the saved engine selection
  alone does not prove which executable this wrapper launches. Trace on the
  actual target during the later workflow audit; do not patch it in this map.
- Astrometry.net 0.98 needs the recorded Python helper installation, native
  shared libraries, config and 191 existing index files (9.579 GiB). An isolated
  binary or package list without those resources is insufficient for migration.
- Raw trees must remain readable and unchanged; project partitions need writes,
  directory traversal and symlink support. Calibration products must exist before
  dependent jobs. Solving needs temporary detector images; SWarp needs resampling,
  virtual-memory and output space. Disk/memory demand depends on real input and
  concurrency; the earlier visible 128 CPUs is not an allocation or safe worker
  count. Native/linker and filesystem behavior still need separate Mac evidence.
- Notebooks retain `os.getcwd()`-relative config and `sys.path` additions; library
  wrappers change working directories and create fixed-name temporary outputs.
  Installed import tests do not validate every notebook directory/concurrency
  assumption. Keep these as later workflow-audit findings, not dependency upgrades.
- Interactive server/kernel niceness stays zero. Heavy scripts/native children
  must be separately launched at niceness >=10 with explicit process/thread
  limits; merely opening a notebook does not lower direct computations.

## Remaining dependency acceptance work

1. Capture full installed Pycavi file identities and reconcile package origins
   against the wheel, 140-distribution inventory and Conda records. Preserve
   build/install records for local Astrometry.net 0.98 and native resources.
2. The current notebook-07 Gaia DR3/GSPC client/schema and lunar/site-data paths
   lack target checks. Define small independent probes before exercising them;
   do not silently invoke full-field production photometric calibration.
   SDSS is a conditional calibration alternative. SkyMapper is also a calibration
   alternative, but notebook 09 actively calls its comparison function in its
   final cell for every selected catalogue (empty selection means all). Thus a
   complete run of the tracked notebook needs that service too; omitting the
   comparison for acceptance needs an explicit scope decision, not an assumption.
3. SCAMP PDF plotting is explicitly selected by notebook 05 but remains untested.
   Agree a small plotting-capability check if this is required for acceptance.
   Existing UTF-8 `.head` commentary and reference `TDISPn` warnings are recorded;
   diagnostic readers are not fixes for production reader compatibility.
4. Capture the actual Mac imaging clone, interpreter and engines before changes;
   compare versions and run accepted portable checks there. Ubuntu remains a
   future qualification target, not current evidence. Do not transfer Linux
   Conda URLs as a Mac lockfile or alter either environment to force equality.
5. Present remaining limitations for Fernando's explicit dependency-baseline
   acceptance. Scientific calibration, full notebook orchestration, pool error
   handling, MEF assembly, Phase 3 compliance and the systematic library/mefpp
   audits remain subsequent work. A successful service check does not close them.

## Source anchors

- [Project metadata](../../pyproject.toml): declared direct/optional dependencies.
- [Notebooks](../../Pycavi2/pycavi/notebooks): code-cell imports, choices and calls.
- [Tools](../../Pycavi2/pycavi/pycavi/pycavi_tools.py) and
  [Instrument](../../Pycavi2/pycavi/pycavi/pycavi_instrument.py): config/Tk requirements.
- [Reduction](../../Pycavi2/pycavi/pycavi/pycavi_associate_reduction.py) and
  [solving](../../Pycavi2/pycavi/pycavi/pycavi_solve.py): native/resource boundaries.
- [Astromatic tools](../../Pycavi2/pycavi/pycavi/pycavi_astromatic_tools.py) and
  [PAPI](../../Pycavi2/pycavi/papi): actual executable/config generation path.
- [Photometric calibration](../../Pycavi2/pycavi/pycavi/pycavi_zpcal.py),
  [catalogue](../../Pycavi2/pycavi/pycavi/pycavi_catalogue.py),
  [Chebyshev](../../Pycavi2/pycavi/pycavi/pycavi_chebyshev.py) and
  [kriging](../../Pycavi2/pycavi/pycavi/pycavi_kriging.py): later-stage imports,
  API use, reference requests and model files.

Inspection used notebook code-cell extraction, Python AST imports and targeted
source reads. It did not import the production photometry module (which loads
Astroquery Gaia), execute a notebook, install software or launch a native job.
