# Remote notebook launcher

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
