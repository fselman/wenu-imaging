# Pycavi checkout tools

## Portable synthetic dependency checks

`check_dependencies.py` runs the same bounded checks on Linux and macOS. It is
a checkout utility, not a wheel-installed command. It does not install packages,
change saved engine selections, consume observational data or validate the full
Pycavi workflow. Python with NumPy and Astropy is required for the checks.

Checks are `fits-compression` (exact integer FITS round trip and selected headers),
`sextractor` (five synthetic stars with distinct detections within two pixels),
and `swarp` (constant-image resampling, finite WCS and positive central weights).
These retain the manual chapman3 fixtures and tolerances, with unique source
matching additionally checked. Floating-point compression, science photometry,
coadd quality and real-sky astrometric accuracy are outside their claims.

`scamp` additionally tests a synthetic single-detector FITS_LDAC catalogue with
100 noiseless sources against a local known reference catalogue (`ASTREF_CATALOG
FILE`). Its initial RA reference is displaced by three arcseconds in coordinate
angle. Pattern matching, photometric calibration and check plots are disabled;
one thread performs a degree-one astrometric fit. The recovered sky positions
must have RMS below 0.2 arcsec and improve at least tenfold over the input WCS;
input catalogue hashes must remain unchanged. No observational data or online
reference service is used. This is a controlled engine/interface test, not a
Pycavi wrapper, mosaic, Gaia access, proper-motion or scientific-accuracy test.
Use `--scamp /actual/path/to/scamp`; generated `.head`, XML and logs are preserved.
Real Astrometry.net image solves are not yet included in this tool.
The fixture follows the official
[SCAMP input/output catalogue contract](https://scamp.readthedocs.io/en/latest/Using.html).
The embedded image header is serialized as exact space-padded 80-byte FITS
cards in complete 2880-byte blocks. Raw-byte regression coverage is required:
Astropy can reconstruct readable cards from NUL-padded table strings while
SCAMP 2.10.0's native reader cannot recognize their `END` keyword. The initial
fixture exposed this construction defect and crashed during header loading;
that run is not evidence against the installed engine's valid-input behavior.
SCAMP 2.10.0 can write UTF-8 accents in `.head` COMMENT text, which Astropy's
strict FITS text reader rejects. For this diagnostic's in-memory WCS only,
non-ASCII COMMENT/HISTORY lines are excluded and recorded verbatim as text/hex
in the result. Other non-ASCII cards fail explicitly. The native `.head` file
is never rewritten, and its hash is recorded and checked unchanged. This narrow
diagnostic reader does not repair Pycavi's production header-reading paths.

Select checks as positional arguments. Supply a new `--output` directory and,
where needed, `--fpack`, `--funpack`, `--sextractor`, `--swarp`, `--scamp` paths.
Defaults resolve fpack/funpack/sex/swarp/scamp on PATH. Nothing reads or changes Pycavi's
saved engine configuration. Explicit paths are preferred when comparing machines.
`--expect-host` checks the short hostname and `--expect-prefix` checks the Python
environment before writes or native jobs. `--dry-run` resolves selected paths and
checks guards without scientific imports, jobs, directory creation or priority
changes. It is not an engine qualification test.

### Opt-in live SCAMP retrieval

`scamp-live --allow-network --ref-server vizier.u-strasbg.fr` separately tests
SCAMP's own Gaia DR2 retrieval and parser. The hostname defaults to the existing
Pycavi wrapper's server; it is not a URL. This does not edit saved settings or
change the selected catalogue. Offline checks never select this check implicitly.

The fixture covers 51.2 arcsec near CN Ori (88.018586, -5.464047 degrees), with
a 0.05 arcmin position margin. SCAMP 2.10.0 retrieves references before the
optional fit; both astrometric and photometric solving and pattern matching are
disabled. A saved Gaia DR2 LDAC catalogue must contain finite, valid coordinates
within one arcminute of the field centre. Input hashes must remain unchanged.
The native response, commands and logs remain available in the output directory.
This qualifies live retrieval/parsing only, not a real-sky astrometric fit.

The request is bounded by this small sky area and the command's 120-second
timeout. SCAMP 2.10.0 hardcodes a large row ceiling in its VizieR request;
this native check does **not** impose the five-row cap used by the separate curl
connectivity probe. It supplies one server and performs no tool-level retries.
No network check has been qualified on Mac or Ubuntu yet. Unit tests simulate
the response and command contract; actual native retrieval on chapman3 remains
pending. The inspected implementation is
[SCAMP 2.10.0 makeit.c](https://github.com/astromatic/scamp/blob/2.10.0/src/makeit.c)
and [astrefcat.c](https://github.com/astromatic/scamp/blob/2.10.0/src/astrefcat.c).

Always launch as a separate process from a guarded terminal or with notebook
`subprocess.Popen`; never `%run`, `runpy` or call `main` inside the kernel. The
CLI lowers only itself and descendants to niceness >=10 and sets four numerical
thread-limit variables to one. It never changes its caller's priority. Runtime
host, OS and Python are printed before jobs. Supported targets are macOS and
Linux; other operating systems are not qualified. Do not use Python `-O`.

The output contains synthetic inputs, generated engine configs, native stdout/
stderr and `report.json`: executable paths/hashes, tool hash, Python distribution
versions, host, priority, command arguments/statuses and per-check measurements.
Existing output directories and symlinks are refused. Commands have 120-second
timeouts. Independent selected checks continue after one fails; CLI exit status
is nonzero if any check fails. Preserve failed directories; rerun in a new one.
Conda explicit builds and full installation provenance still need separate capture.

For chapman3 use the existing absolute project Python and engine paths. For Mac
or Ubuntu obtain the actual checkout/interpreter/engine locations first; do not
reuse chapman3's paths or assume those targets passed. Compare each platform's
JSON measurements and installed versions after executing there. The earlier
manual chapman3 results are evidence for those manual runs, not an execution of
this new tool. Follow machine guards in `docs/developer/agent-instructions.md`
when preparing runnable command blocks.

## Remote notebook launcher

`start_remote_notebook.py` is a checkout utility for the existing chapman3 pilot,
not a wheel-installed entry point or a general remote service manager. Run it
with `$HOME/.conda/envs/wenu-imaging/bin/python`. It refuses other hosts,
interpreters, missing workspaces and a registered `wenu-imaging-chapman3` kernel
whose absolute executable does not match the environment.

Options: `--dry-run` validates without starting the server; `--port` defaults to
8888; `--root` defaults to `$HOME/omegacam/workflows/wenu-imaging-test`.
No environments, kernels or workspace files are installed or repaired.

The server binds to 127.0.0.1, disables port fallback and browser launch, selects
the existing named kernel, and retains normal niceness 0 with BLAS/OpenMP thread limits of one.
It refuses to start from a terminal already running at a different niceness. Jupyter's existing authentication remains enabled; the launcher
does not set or disable credentials. Normal Jupyter runtime files are written
only when the server starts. A busy port causes startup failure; the launcher
does not kill an existing server. `--dry-run` does not test port availability.

The launcher prints a separate SSH local-forwarding command for the Mac. Use
the actual working SSH alias/jump-host configuration when required. Open the
localhost token URL printed by Jupyter in Mac Firefox. Keep the server and SSH
terminals open. Stop each with Ctrl-C; no X11 forwarding is needed. The server
and Python kernel run on chapman3, while Firefox runs locally on the Mac.

The implementation has local mocked tests for host/environment/kernel rejection,
safe launch options and a dry run that never executes the server. Actual
chapman3 startup and tunnel validation for this launcher remain pending.

## Batch commands from notebooks

`run_batch.py` starts a supplied command in its own process at niceness 10 (or
retains a higher inherited niceness). Its descendants inherit that priority;
it does not change the calling kernel. It checks the same chapman3 environment
and forces BLAS/OpenMP thread limits of one. `--dry-run` prints the command
without executing it or changing priority. Arguments after `--` are passed as
an argument vector; the helper does not use a shell. Exit status and terminal
signals belong to the executed command because the helper replaces itself.

From the notebook, use `subprocess.Popen` with an argument list consisting of
`sys.executable`, the absolute path to `Pycavi2/tools/run_batch.py`, `--`, and
then the script command and its arguments. Use `sys.executable` again for Python
scripts. Keep the returned process handle to inspect its status. A blocking
`subprocess.run` or `.wait()` inside a cell still occupies that kernel until the
batch finishes; `Popen` lets the cell return while the separate batch continues.
Capture verbose batch logs to a file rather than filling the notebook output.

This does not wrap direct Python calculations or existing notebook library
calls automatically. Until those workloads explicitly use the batch helper,
they run at kernel priority. Do not run the helper with `%run`/`runpy` inside
the kernel: it changes its own process priority and replaces its process.
The helper is only for a separately launched subprocess. No scientific library
or reduction notebook implementation is changed by these tools.
