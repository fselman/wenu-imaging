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
the existing named kernel, and runs through `nice -n 10` with BLAS/OpenMP thread
limits of one. Jupyter's existing authentication remains enabled; the launcher
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
