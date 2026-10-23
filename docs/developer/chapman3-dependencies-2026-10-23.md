# Chapman3 dependency qualification — 23 October 2026

## Scope and evidence

This records Fernando's terminal/notebook output from chapman3. The documenting
agent has no remote shell. Dependency acceptance remains open; a package import
or a functional pilot is not full workflow or scientific validation. Capture a
fresh machine-readable environment inventory before declaring the gate complete.
No workflow implementation changes are included in this documentation update.

Fresh capture reported on 23 October: `~/wenu-dependencies-mi_avvgc` contains
`python-inventory.json` (140 distributions), `pip-freeze.txt`, `pip-check.txt`,
`conda-explicit.txt`, `conda-history.txt`, `kernels.json`, saved engine configuration,
engine-check output and command statuses/stderr. All five capture commands
returned zero; pip check reported no broken requirements. Fernando supplied the
selected versions and Conda build summary below. Full 140-distribution inventory
and explicit URLs remain in the capture on chapman3, not copied into this repo.

The latest reported checkout is `~/Software/wenu-imaging`, origin
`https://github.com/fselman/wenu-imaging.git`, branch `fix/installed-packaging`,
clean at `470d57b23ce5ca3ca7e16c4520020ab5db3f20d6`. The installed scientific
library came from the earlier `dfcb3e715d8bbee5174e3a9cb5ad782a2cedc0ae`
wheel; later changes supplied tools/documentation. Version `pycavi==0.1.0` alone
does not distinguish these wheels. Refresh actual checkout and installed-library
identities before further installations or Git changes.

## Platform and runtime

| Item | Observed value |
|---|---|
| Host | chapman3.sc.eso.org |
| OS / libc | CentOS 7; glibc 2.17 |
| Kernel / architecture | 3.10.0-1160.71.1.el7.x86_64; x86_64 |
| CPU / memory | EPYC 7742; 64 cores, 128 threads; about 503 GiB RAM |
| Home storage | GFS2 under /home1; /home/fselman resolves there |
| Project Python | ~/.conda/envs/wenu-imaging/bin/python; 3.11.14, conda-forge |
| Base interpreter, preserved | ~/anaconda3/bin/python; 3.9.12 |
| System interpreter, preserved | /usr/bin/python3; 3.6.8 |
| Conda manager, preserved | 4.12.0 |
| Notebook execution | Server/kernel on chapman3; Firefox on Mac through SSH tunnel |
| Priority | Interactive server/kernel niceness 0; batch and descendants >=10 |
| Resource limits for pilots | One worker; OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1 |

Visible CPU affinity is not a scheduler allocation. Allocation policy and a
dedicated scratch location have not been established. Do not use 128 workers
merely because the machine exposes 128 logical CPUs.

## Python package baseline

Direct numerical checks establish NumPy 1.26.4 and SciPy 1.17.1 (conda-forge),
and Matplotlib 3.11.2, ContourPy 1.3.2 and Pillow 12.2.0 (pip binary wheels).
Python SSL, SQLite and Tcl checks passed: OpenSSL 3.6.5, SQLite 3.54.1,
Tcl 8.6.13. Tk import/Tcl success does not establish a working GUI display.

The fresh capture confirmed the following installed scientific selection. The
table is not a transitive lock and does not establish every package's provenance.

| Package | Recorded version |
|---|---|
| astropy | 6.1.7 |
| photutils | 1.13.0 |
| pandas | 2.3.2 |
| scikit-image | 0.20.0 |
| PyWavelets | 1.8.0 |
| IPython | 9.17.1 |
| astroquery | 0.4.11 |
| astroplan | 0.10.1 |
| PyKrige | 1.7.3 |
| lmfit | 1.3.4 |
| sympy | 1.14.0 |
| ephem | 4.2.1 |

Notebook 7.0.6, ipykernel 6.25.0, jupyter-server 2.21.1 and jupyter-client 8.10.0
are recorded. IPython is 9.17.1. Build/install tools are pip 26.2.2,
setuptools 84.2.1 and wheel 0.48.0. The selected versions satisfy the current
declared direct Python ranges and notebook extra; pip check confirms installed
distribution metadata consistency, not scientific behavior or optional branches.

The `wenu-imaging-chapman3` kernelspec binds the absolute project Python path;
the generic `python3` kernelspec uses relative `python` and should not substitute
for that verified named kernel. Preserve pip and Conda inventories separately:
pip freeze alone does not record native Conda builds or external engines.

Conda-forge records identify Python `3.11.14 hd63d673_3_cpython`, NumPy
`1.26.4 py311h64a7726_0`, SciPy `1.17.1 py311hbe70eeb_1`, and OpenBLAS
`0.3.34 pthreads_hf13c14d_2`. GCC/libstdc++/Fortran runtime packages are 16.2.0;
these are runtime libraries, not an installed replacement compiler. Other
Conda builds and their channels are retained in the capture.

Known provisioning differences:

- SciPy 1.17.1 was unavailable as a compatible pip wheel in the reported probe;
  its conda-forge build installed and passed a linear-algebra calculation.
- Pandas 2.3.3 from the Mac inventory had no compatible binary for this host;
  chapman3 selected 2.3.2. Do not assume the Mac can change without validation.
- Conda Matplotlib resolution encountered a transitive glibc requirement;
  the pip manylinux 2.17 wheel passed headless PNG rendering.
- Astroplan 0.10.1 was not supplied as a wheel in the binary-only probe.
  Capture installed metadata/Conda records to establish its final provenance;
  do not infer a binary artifact from successful imports.

## External engines and resources

| Dependency | Selected location / version | Evidence |
|---|---|---|
| mefpp | ~/opt/local/mefpp/bin/mefpp; run banner mefpp-2.0.0 | Bias, dome, sky/MFF and science pilots ran |
| qfits system | eso-qfits-6.2.0-1.el7.centos.x86_64 | RPM ownership and shared-library registration |
| qfits private | ~/opt/local/qfits5; static library | Located; exact native build provenance still open |
| SExtractor | /usr/bin/sex; 2.19.5 | Synthetic extraction passed; Pycavi catalogue workflow pending |
| SCAMP | /usr/bin/scamp; 2.10.0 | Executable/version check; functional catalogue fit pending |
| SWarp | /usr/bin/swarp; 2.38.0 | Synthetic resampling passed; science coadd/Pycavi integration pending |
| Astrometry.net | ~/opt/astrometry.net-0.98; 0.98 | Installed modules/helpers and two full detector pilots passed |
| Astrometry indexes | /usr/local/astrometry/data | 191 files, about 9.579 GiB; existing indexes reused |
| funpack / fpack | /usr/bin/funpack; /usr/bin/fpack | Synthetic integer-image lossless round trip passed; versions still to capture |

The old Astrometry.net 0.85 under `/usr/local/astrometry` is preserved. The saved
`~/.pycavi/pycavi_astrosoft.cfg` now selects the local 0.98 binary; the previous
configuration is `.bak`. Other executable selections remain unchanged.
Private/system qfits inventories do not by themselves establish which library
was linked into mefpp; the inspected mefpp ldd showed only libm and libc.

Existing mefpp resources include `config/omegacam.paf` and
`static_cal/OCAM_BPM_1x1.fits`. The latter has 32 named detector images and lacks
PCOUNT/GCOUNT cards in all extensions. Approved Pycavi preflight tolerates those
specific omissions in memory only; the installed mask was not rewritten.

## Local Astrometry.net 0.98 build and installation

- Source: `~/Software/astrometry.net-0.98`; prefix: `~/opt/astrometry.net-0.98`.
- Archive SHA256:
  `d3fe037c9de2e747a9c8d5cdb467f723f023eaacc2e3dc607ff1496dc0d2c7fc`.
- Evidence: `~/astrometry-0.98-build-check.ii9i8q15`, including download records,
  `build-settings-python-config.json`, build logs, preinstall smoke log,
  `install-local.log` and `install-python-local.log`.
- GCC/G++ 4.8.5; GNU Make 3.82. Core build uses
  `CC=/usr/bin/gcc -std=gnu99 -fgnu89-inline`, `CXX=/usr/bin/g++`.
  C99 syntax alone failed because of upstream inline-selection behavior.
- Python, PYTHON_SCRIPT: absolute project Python 3.11 path. Python helpers are
  bound to that interpreter, not whichever python3 is first on notebook PATH.
- Build-local `python-config-gcc48` wrapper supplies compatible include/compiler
  flags, avoiding Conda's unsupported `-fno-plt` and related modern build flags.
  It does not modify Conda's python-config or system compiler.
- Netpbm 10.79.00 runtime/development RPMs exist despite missing pkg-config
  registration. Explicit `NETPBM_INC=-I/usr/include/netpbm`,
  `NETPBM_LIB=-L/usr/lib64 -lnetpbm` were used.
- CFITSIO 3.37: `CFITS_INC=-D_REENTRANT -I/usr/include/cfitsio`,
  `CFITS_LIB=-lcfitsio`; `SYSTEM_GSL=yes` uses system GSL 2.6.
- `make all`, `make py`, `make install`, `make pyinstall` completed after the
  recorded flag corrections. Build used two jobs; install used one, nice 10.
- The new prefix's `etc/astrometry.cfg` uses `cpulimit 300`, existing index path
  and `autoindex`. Its generated original is `astrometry.cfg.installed-default`.
  No system configuration or index files were changed.
- Installed compiled util and spherical-matching modules load from the new
  prefix with Python 3.11/NumPy 1.26.4. FITS-table round trip, numerical matching
  and image2pnm/removelines/solve-field help checks passed. Inspected shared
  libraries resolved against the existing host libraries.

The earlier 0.85 helper path failed first on module discovery and then np.bool
under NumPy 1.26. A scoped Python 3.9 helper workaround solved CCD65, but the
selected 0.98 installation now passes these checks with Python 3.11 throughout.
No global PYTHONPATH or system interpreter replacement is required.

## Qualification evidence and boundaries

- The reusable compression, SExtractor and SWarp checks each passed on chapman3
  at niceness 10. Records: `~/wenu-dependency-tools.p11U9J/results`. This is
  actual target execution of the shared tool, superseding the earlier pending
  statement for those three checks on chapman3; Mac and Ubuntu remain pending.
- SCAMP 2.10.0 version/default-configuration probes returned zero and ldd showed
  no unresolved libraries. The compiled default reference host is
  `vizier.unistra.fr`, while installed Pycavi's PAPI wrapper sets
  `vizier.u-strasbg.fr`; notebook 05 requests Gaia DR2. No host or catalogue
  selection is changed by this finding. Live service/alias behavior is untested.
  Required input columns include windowed centroids/error ellipses and auto flux/
  flux error in FITS_LDAC; local-reference FILE mode is available. The portable
  synthetic SCAMP check is added for qualification, but its native execution
  on chapman3 is pending. Plotting/PDF support is not covered by a plot-free fit.

- `/usr/bin/swarp` returned zero for a synthetic 64x64 constant-image resample;
  central intensity was 100.0 (expected 100), celestial WCS was finite and central
  weights were positive. Records: `~/wenu-swarp-check-ovnmyd2y`. This does not
  establish science coadd quality or Pycavi integration. Fernando requested
  reusable cross-platform dependency checks; `Pycavi2/tools/check_dependencies.py`
  now holds the compression, extraction and resampling fixtures. Subsequent
  shared-tool execution on chapman3 is recorded above; other platforms are pending.

- `/usr/bin/sex` returned zero and detected exactly five synthetic Gaussian
  stars, all within 0.008 pixel of their injected positions, with finite catalogue
  values and positive measured fluxes. Records: `~/wenu-sextractor-check-u6suum_b`.
  This qualifies the tested executable/configuration path, not Pycavi catalogue
  orchestration or scientific photometric accuracy.

- `/usr/bin/fpack` and `/usr/bin/funpack` each returned zero in a synthetic
  64x64 int16 FITS round trip. All pixels and selected OBJECT/BUNIT headers were
  preserved. Records: `~/wenu-fits-compression-n9i1p8fi`. This does not qualify
  floating-point quantization or every compressed MEF layout.

- Installed wheel resources/setup/executable configuration: ten tests passed.
- Current regression suite after MEF BPM correction: 21 tests passed.
- Nine recorded runtime library imports passed; pip consistency was reported
  previously and should be refreshed for the final installed environment.
- Remote notebook kernel host, interpreter and niceness 0 verified; separate
  batch process niceness 10 and unchanged kernel priority verified.
- Isolated CN Ori pilot: nine partitions, 60 distinct raw inputs; detector order
  matches in the inspected inputs. This does not prove name-based native matching.
- Biases with historical references, NB dome and NB sky matched numerically.
  NB MFF differences were confined to the changed-BPM smoothing footprint.
  r_SDSS has functional checks without the missing historical master references.
- r_SDSS dome functional override: upper threshold 55000, minimum five frames;
  failed 45000 attempt preserved. Do not propagate the override globally.
- Ten pilot science files were normalized once, with independent verified
  backups and completion records. Do not normalize again.
- Astrometry tests called installed Pycavi `solvefield()` through diagnostic
  extraction/check wrappers, sequentially at nice 10. CCD65 and 32/32 detectors
  in each of one r_SDSS and one NB_659 exposure passed solution-marker, finite
  celestial WCS, exact pixel preservation and unchanged-source checks.
- Records: project `astrometry-pilot-r_SDSS-ccd65-098`,
  `astrometry-pilot-r_SDSS-32ccd-098`, `astrometry-pilot-NB_659-32ccd-098`,
  under `~/omegacam/testing/wenu-imaging-test`.
- Full notebook orchestration, worker error propagation and assembled solved
  MEFs are not qualified by these wrappers. Astrometric accuracy, photometry,
  calibration quality and Phase 3 compliance are not established by these tests.

## Remaining dependency acceptance gate

1. Fresh Python/Conda inventories, kernel registration, saved engine paths and
   pip check captured successfully in `~/wenu-dependencies-mi_avvgc`. Preserve
   these artifacts; installed Pycavi file identities and complete package-origin
   reconciliation remain to be added. Notebook extra versions are confirmed.
2. Map required packages, executables and data resources to the existing OmegaCAM
   notebook path without changing its implementation. Identify any untested
   branches, funpack needs, catalogue/reference services and filesystem needs.
3. Perform bounded dependency checks for remaining required native engines and
   resources. Agree their inputs/results before running science fits or coadds;
   executable presence alone is insufficient. Do not start a replacement workflow.
4. Capture the actual Mac imaging environment and compare versions. Prepare
   reviewed common direct-version constraints and platform-specific installation
   records after comparison. Do not copy Linux Conda artifact URLs onto Mac.
5. Record explicit unresolved requirements and Fernando's dependency acceptance
   before beginning the Pycavi workflow audit/refactoring sequence.

Python future-proofing follows the five agreed project points, separately planned.
No general upgrades, workflow replacements or calibration-QC-library work are
authorized by this inventory.
