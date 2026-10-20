# Previous Intel Mac installation and OmegaCAM workflow

Evidence collected with Fernando Selman on 20 October 2026. This supplements
the original source audit; it does not certify scientific correctness or change
processing code. Terminal results were supplied by Fernando from his Mac.
Log contents, notebook execution records and science FITS headers have not yet
been inspected. Paths and file modification times are evidence, not a complete
execution provenance record.

## Confirmed workflow and last recorded use

Fernando explained that notebook `00_pycavi_project_config.ipynb` selects the
raw-data location and destination for reduced products. Subsequent notebooks
create the project directory structure. The notebook command center, source
checkout, installed executables, raw files and output project are separate roles.

Raw data reside in `~/Pictures/OCAM/raw_files/CPPup_raw` and `m67_raw`.
For the historical run Fernando selected only CP Puppis and chose the output
name `CPPup`. He uses the name `Multi` when choosing multiple science targets;
neither is a mandatory pipeline directory name. The current configuration's
reference to absent `OCAM/Multi` does not establish a broken installation or
identify the configuration that produced CPPup.

The CPPup logs contain internal timestamps confirming processing on **6 February
2025**. Their timezone is not explicit. Selected recorded stages:

| Log time | Activity |
|---|---|
| 13:00:57 | Partition raw files, including CP Pup science exposures in `r_SDSS` |
| 13:04:19 and 13:05:52 | Invoke bias creation with `--bias bias.list --biassave` |
| 13:07:04 | Invoke dome-flat processing |
| 13:08:16 | Invoke sky/master-flat processing |
| 13:11:28 | Invoke science reduction |
| 13:14:05 through at least 13:15:51 | Python science normalization |
| Around 16:05 | Jupyter widget communication errors/warnings |

The commands explicitly name `/Users/fselman/opt/local/mefpp//bin/mefpp`.
This confirms the historical executable path, not that today's bytes are unchanged.
Normalization repeatedly records `NO light correction.` Do not infer that the
correction was applied from a present-day template setting of `True`.
Command invocation and subsequent normalization do not by themselves prove every
calibration stage succeeded or that the final products passed scientific QC.

The recursive OCAM scan completed without read errors at
`2026-10-20 17:28:51-03:00`, finding 3,881 regular files. Its newest non-hidden
file was `CPPup/logs/pymeffpp_partition_data.log`, modified at
`2025-02-06 16:05:46-03:00`; its final entries are widget communication messages.
The run log likewise ends in widget messages at 16:05:12, after reduction entries
around 13:15. Therefore the last recorded activity under OCAM is 6 February 2025,
with the exact end of scientific processing still to be reconstructed from later
stage logs. The only newer file reported was Finder `.DS_Store` metadata dated
20 October 2026, which is not a new reduction.

Other logs and catalogue/illumination outputs have modification dates on
6 February 2025. Astrometry, SCAMP, SWarp and photometric-calibration log contents
have not yet been inspected. Names such as `2017-03-13T01:57:49` refer to data
partition identifiers and must not be mistaken for processing dates.

Fernando intends a fresh rerun on 21 October 2026, with a new output destination
so the historical products remain available for comparison. This is an intention,
not a scheduled task or evidence of a completed rerun.

## Data and output layout

| Top-level directory | Files | Logical size, GiB | Interpretation |
|---|---:|---:|---|
| `raw_files` | 132 | 65.568 | Raw-data area reported by Fernando |
| `bpm` | 37 | 16.390 | Bad-pixel-mask area; individual contents unverified |
| `CPPup` | 3,712 | 49.497 | Existing project/calibration/science outputs |

Logical total is approximately 131.455 GiB; hard links, symlinks, sparse files
and allocated disk usage have not been characterized. Do not assume these are
the exact inputs or volume of the new Phase 3 production set.

Observed directory structure:

```text
OCAM/
  raw_files/CPPup_raw/
  raw_files/m67_raw/
  bpm/
  CPPup/
    calib/bias/
    calib/dome/
    calib/sky/
    logs/
    static_calib/bpm/
    science/CP_Pup/
      r_SDSS/
      Calibration_dir/
```

The displayed tree combines the three-level inventory and paths from the newest
files. It is not a complete directory listing. CP Pup and `r_SDSS` are observed
project/filter labels; their identities have not yet been checked against FITS
headers. The presence of `m67_raw` does not establish that M67 was processed.

There were 320 files of each suffix `.wcs`, `.corr`, `.rdls`, `.axy`, `.match`,
`.solved` and `.xyls`, consistent with Astrometry.net stage artifacts. Their
presence and equal counts do not prove 320 valid or independent successful solves.
Other counts included 346 `.log`, 336 `.txt`, and 9 `.list` files.
The scan grouped some FITS files by compound suffix, so the reported 647 `.fits`
entries are not a complete count of all FITS files.

Calibration-directory names include a coadd catalogue, illumination CSV,
Chebyshev coefficients, kriging FITS output, diagnostic PNGs and region files.
These suggest work through coaddition, photometric/illumination calibration and
catalogue generation. Scientific quality, stage completion and Phase 3 readiness
remain unverified.

## Machine and Python environment at rediscovery

- macOS 13.7.8, build 22H730; Intel `x86_64`.
- Python 3.11.7: `/Users/fselman/anaconda3/bin/python3`, in Anaconda `base`.
- Apple Clang 15.0.0; Xcode developer directory
  `/Applications/Xcode.app/Contents/Developer`.
- GNU GCC alternatives: Mesa SDK 13.3.0, MacPorts GCC 13.2.0
  (`13.2.0_4+stdlib_flag`), and a Homebrew GCC 14.1.0_2 path.
- `/usr/bin/gcc` reports Apple Clang, not GNU GCC.
- Bare `gcc` currently selects `/Applications/mesasdk/bin/gcc` before
  `/opt/local/bin/gcc`, which resolves to `/opt/local/bin/gcc-mp-13`.

Reported Python distributions on 20 October 2026, not necessarily the historical
versions used for the February 2025 processing:

| Distribution | Version | Distribution | Version |
|---|---|---|---|
| numpy | 1.26.3 | scipy | 1.12.0 |
| astropy | 7.1.0 | astroquery | 0.4.11 |
| photutils | 1.8.0 | scikit-image | 0.20.0 |
| ephem | 4.1.2 | astroplan | 0.10 |
| pykrige | 1.7.1 | lmfit | 1.3.2 |
| matplotlib | 3.8.0 | pandas | 2.1.4 |
| sympy | 1.12 | IPython | 8.20.0 |
| notebook | 7.0.6 | setuptools | 84.0.0 |
| wheel | 0.41.2 | | |

Current Astropy 7.1.0 is outside the audited Pycavi declaration `<7`.
No changes to the base environment were made as part of this investigation.

## Notebook command center setup

The imported Pycavi `pyproject.toml` declares the console entry point
`pycavi_setup = "pycavi.pycavi_setup:setup_pycavi"`. The README instructs the
user to create a command-center directory, change into it, run `pycavi_setup`,
then start `jupyter notebook` there. This directory is conceptually separate
from both the installed software and the configured raw/project data paths.
A candidate command center is `~/Software/testing`, containing 15 notebooks
and a `config/` directory. All inspected notebooks have empty execution counts
and no saved outputs, so they are not themselves a retained execution record.

The implementation in `Pycavi2/pycavi/pycavi_setup.py` defaults to destination
`.` and copies installed resource `.ipynb` files into it, plus `.cfg` and `.paf`
files into its `config/` subdirectory. It uses `shutil.copy`, which can overwrite
existing files with the same names without confirmation. Do not run setup in
the historical command center during discovery. The console entry point does
not parse a destination argument or provide a dry-run/help interface; a fresh
directory followed by a bare `pycavi_setup` is the documented command usage.
The Python function accepts a destination string if called directly.

Resource availability depends on the installed Python distribution; source
inspection alone does not verify successful copying from the current Mac
installation. The source contains 15 notebooks, including WFI and testing
notebooks, and the setup function copies every available `.ipynb` resource.
`pycavi_setastro` is a separate command for recording external executable paths.

## Python environments and local configuration

Conda 24.11.3 lists `base` and `wenu-3d`. Direct interpreter checks find no
registered Pycavi distribution in either environment; `pycavi` is also not
discoverable on the current base interpreter's ordinary search path.

- Base: Python 3.11.7, notebook 7.0.6, ipykernel 6.25.0, numpy 1.26.3,
  astropy 7.1.0.
- wenu-3d: Python 3.11.14, numpy 2.4.6; notebook, ipykernel and astropy
  were not found by package metadata lookup.
- The only kernel found in the searched common locations is `python3`, pointing
  to `/Users/fselman/anaconda3/bin/python`. Historical environment identity
  remains unproven; an earlier environment could have been changed or removed.
- Conda reports a libmamba plugin load error for missing `libarchive.19.dylib`,
  but still returns environment information. Its configured solver is `classic`.
  No environment repair or package installation has been performed.

The notebooks in `Software/testing` append their parent directory to `sys.path`
and import `pycavi.pycavi.pycavi_tools`. The corresponding lowercase filesystem
path `~/Software/pycavi/pycavi/pycavi/pycavi_tools.py` exists. This supports direct
source use without package installation, but that import has not been executed
in this investigation and filesystem name casing must not become a portability
assumption.

`Software/testing/config/pycavi.cfg` points to `OCAM/raw_files/` and output
`OCAM/Multi/`. Its `mefpp.cfg` points to absent `/opt/local/eclipse/`.
The saved `~/.pycavi/pycavi_astrosoft.cfg` contains:

| Key | Saved path |
|---|---|
| mefpp | `/Users/fselman/opt/local/mefpp/bin/mefpp` |
| solve-field | `/usr/local/Cellar/astrometry-net/0.95_2/bin/solve-field` |
| sextractor | `/opt/local/bin/source-extractor` |
| scamp | `/opt/local/scamp/bin/scamp` |
| swarp | `/opt/local/bin/swarp` |

These existing settings were read, not changed. Fernando clarified that `torm`
means "to remove" and denotes a cleanup candidate; it has not been deleted.

## Installed software and saved sources

| Component | Installed location | Evidence and limits |
|---|---|---|
| mefpp selected by Pycavi and recorded in CPPup log | `~/opt/local/mefpp/bin/mefpp` | Intel Mach-O; separate home-prefix build with matching debug symbols |
| second mefpp installation | `/opt/local/mefpp/bin/mefpp` | Different Intel Mach-O build with matching debug symbols |
| qfits | `/opt/local/qfits5` | Headers and static archive present; separate archive also exists under `/opt/local/lib` |
| SCAMP | `/opt/local/scamp/bin/scamp` | Byte-identical to `~/Software/scamp-2.10.0/src/scamp` |
| SExtractor | `/opt/local/bin/source-extractor` | Present; MacPorts registry includes 2.28.0_0; runtime version not yet checked |
| alternate SExtractor name | `/usr/local/bin/sex` | On PATH; relationship/version not yet checked |
| SWarp | `/opt/local/bin/swarp` | Present; MacPorts registry includes 2.38.0_0; runtime version not yet checked |
| Astrometry.net | `/usr/local/Cellar/astrometry-net/0.95_2` | `solve-field` starts and prints revision 0.95 |
| funpack | `/Users/fselman/anaconda3/bin/funpack` | Found on PATH; version not collected |

mefpp, SCAMP and Astrometry.net commands were absent from the initial PATH lookup
despite being installed. This is an executable-discovery issue, not evidence
that reinstallation is needed. No persistent PATH changes have been made.

Saved source checkouts under `~/Software`:

| Directory | Reported HEAD | Tracked modifications |
|---|---|---|
| `Pycavi` | `b1c401d`, 8 February 2025 | None reported |
| `mefpp` | `0716b63`, 21 August 2024 | None reported |
| `mefpp_2024_08_10` | `54001ba`, 9 August 2024 | None reported |
| `qfits5` | `0b0fc5e`, 9 August 2024 | None reported |

The status commands excluded untracked files; these results do not establish
the absence of untracked build inputs. The Pycavi commit matches the imported
monorepo baseline, but its date is after the latest OCAM output timestamps, so
that commit cannot yet be assigned as the exact processing version.

`mefpp_2024_08_10/config.make` records `CC=gcc`, qfits at `/opt/local/qfits5`
and prefix `/opt/local/eclipse`; its executable differs from the installed one.
`qfits5/config.make` records prefix `/opt/local/qfits5` and `-g -Wa,-q -O3`.
These configurations do not themselves prove which installation was produced.
`~/Software/mefpp_dir/bin/mefpp` is a Linux ELF executable, not a native Mac
executable. `old_pycavi/mefpp_dir/bin/mefpp` is a different Intel Mac executable.

## Installed mefpp build provenance

The home-prefix and system-prefix executables are not the same underlying file
and have different hashes and UUIDs. Both link only to `libSystem.B.dylib` in
`otool -L`; this does not identify the statically incorporated qfits archive.

For `~/opt/local/mefpp/bin/mefpp`, executable and `.dSYM` UUIDs match:
`D84D0CD4-4C04-3A28-BF7C-C2BF7632F4E7`. Debug information records GNU C17
13.2.0, `-O3`, debug symbols, PIC flags, `-mtune=core2` and minimum macOS 13.0,
with build paths:

- `/Users/fselman/Software/testing/mefpp/ins/mef`.
- `/Users/fselman/Software/testing/mefpp/src`.
- `/Users/fselman/Software/testing/qfits5-5.0.1`.

These paths are historical build records; they no longer appear at those
locations in the supplied inventory. The version matches current MacPorts GCC
13.2.0, but does not establish the exact compiler executable path or source
commit. The source-directory name alone is not proof of qfits source identity.

For the separate system-prefix build:

`dwarfdump --uuid` reports the same UUID for the installed executable and its
adjacent `.dSYM`: `7206BB36-6454-3A6E-9F65-2B4EC60045E5`.
Its debug information records:

- GNU C17 13.2.0, optimization `-O3`, debugging `-g`, tuning `-mtune=core2`,
  macOS minimum target `13.0.0`, with PIC flags on the recorded units.
- `/Users/fselman/Software/mefpp/ins/mef`.
- `/Users/fselman/Software/mefpp/src`.
- `/Users/fselman/Software/mefpp/qfits5`.

The version matches the current MacPorts GCC, supporting that compiler choice;
the debug records do not identify the compiler executable path or exact source
commit. The nested qfits build directory was not found in the source-directory
inventory. The installed source provenance therefore remains partly unresolved.

Recorded SHA256 values:

| File | SHA256 |
|---|---|
| `~/opt/local/mefpp/bin/mefpp` | `8bc2996bfc35719c60bdeb10219c3052ad87c89d444cd27512aeddf2cd266e9a` |
| `/opt/local/mefpp/bin/mefpp` | `3cec5808d1ff8ee34c3b9d502a925dce94b39e3ba057bc9e34f2892b5d7b5e5d` |
| `~/Software/mefpp_2024_08_10/src/bin/mefpp` | `136fe7c8e3d7c7f7ad7b2d31fce3d46d57558f7c782295cd3cbbdff90dce794d` |
| `~/Software/old_pycavi/mefpp_dir/bin/mefpp` | `f4608819b7c38ff8cc3f06e13d8b7255dbc1725f0cf8c92b0a3eb48f775588d0` |
| installed SCAMP and saved 2.10.0 build | `acd0575a9640c0601667febff6995c54d1306cb04aa1711da04424e6d93c7347` |
| `/opt/local/qfits5/lib/libqfits.a` | `1777537d567b3c79d2701de7ec5595d40121956523d0046beab2da4494bfb821` |
| `/opt/local/lib/libqfits.a` | `84201912b4306cfd49a39cb518f938724ea28e97aa946703c4a58333502460e6` |

Different executable hashes do not establish different source code. Debug paths,
compiler/linker settings and stripping can also change binary bytes. The installed
qfits archive linked into mefpp has not been conclusively identified.

## Astrometry.net and indexes

`/usr/local/opt/astrometry-net` resolves to `../Cellar/astrometry-net/0.95_2`.
This is separate from saved source `~/Software/astrometry_net/astrometry.net-0.93`.
The installed `solve-field --help` printed usage and revision information,
including a no-input-files message. This establishes startup, not a functional
solve or the availability of every helper/dependency.

Configuration at `/usr/local/Cellar/astrometry-net/0.95_2/etc/astrometry.cfg`:

```text
cpulimit 300
add_path /usr/local/Cellar/astrometry-net/0.95_2/data
autoindex
```

`inparallel` is commented out. This backend setting is distinct from Pycavi's
single-node multiprocessing of separate solves.
The data directory lists 144 index files: `index-5200-00` through `-47`,
`index-5201-00` through `-47`, and `index-5202-00` through `-47`, all `.fits`.
They occupy roughly 29 GiB and have displayed modification dates of 17 July 2024.
Integrity, actual catalogue provenance and suitability for the chosen OmegaCAM
scales/fields have not yet been checked. No new indexes were downloaded.

## New baseline experiments, kept separate from the old installation

Unchanged monorepo qfits at `db8b83eef64021d109952f15b0566a2876c7471b`
configured and built in disposable copies on Intel macOS:

- Mesa SDK GCC 13.3.0: `/tmp/wenu-qfits-_bz9om_z`.
- Explicit MacPorts GCC 13.2.0: `/tmp/wenu-qfits-macports-tkqbtlti`.

Both reported successful configure/make exits. The MacPorts build commands
explicitly used `/opt/local/bin/gcc-mp-13`. No installation result was supplied;
no FITS functional or numerical reduction check has been completed. Compiler
selection must be explicit to avoid accidentally using the first GCC on PATH.

## Next evidence to collect

1. Read existing project CFG/PAF, input lists and executable-selection settings;
   identify the exact historical command center and preserve original contents.
2. Read log headers and tails for internal dates, command lines, selected
   programs, calibrations, CPU/process settings, completion and errors.
3. Compare `Software/mefpp` commit `0716b63` and saved qfits with the imported
   source baselines; locate historical nested qfits inputs if available.
4. Inspect representative FITS headers read-only for instrument/filter, units,
   WCS, calibration/provenance and processing history. Agree reference products
   and tolerances before reruns.
5. Test external-program versions and one representative solve/reduction only
   with fresh output locations and immutable inputs.

Preserve `/opt/local/mefpp`, its `.dSYM`, old source trees and OCAM outputs.
No cleanup, overwrite, system installation, numerical algorithm change or
Phase 3 acceptance claim follows from this inventory.
