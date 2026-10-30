# Grouped native commands and callable C services

Owner decision, 29 October 2026: use one `mefpp` executable with grouped
subcommands, such as `mefpp cal bias`, rather than separate executables such as
`mefpp_cal_bias`. C service names retain the accepted `mef_cal_*` / `mef_sci_pp`
spellings. This records the interface direction; these commands are not yet
implemented or enabled by the M1 bias-service extraction.

| Planned native command | C processing service |
|---|---|
| `mefpp cal bias` | `mef_cal_bias` |
| `mefpp cal bpm` | `mef_cal_bpm` |
| `mefpp cal dark` | `mef_cal_dark` |
| `mefpp cal fringes` | `mef_cal_fringes` |
| `mefpp cal linearity` | `mef_cal_linearity` |
| `mefpp cal domeff` | `mef_cal_domeff` |
| `mefpp cal skyff` | `mef_cal_skyff` |
| `mefpp cal mff` | `mef_cal_mff` |
| `mefpp sci pp` | `mef_sci_pp` |

Each command is a thin adapter: parse arguments, load/validate the selected
configuration and explicitly selected inputs, construct the same typed request
and operation payload used by library callers, call the C service, then report
status and pass completed results to the writer/orchestrator. Numerical work,
calibration selection and QC definitions are not duplicated in command handlers.
Private helpers do not need individual commands. QC remains an explicit phase
inside applicable operations; a separate QC-processing command is not adopted
here. Inspection of existing QC records belongs to the M3 project inspector.

Help is hierarchical: `mefpp --help`, `mefpp cal --help`, and
`mefpp cal bias --help`. Informational commands must work without a project,
configuration file or image. Invalid subcommands/options fail explicitly and
must not fall back to interpreting a command name as a file or legacy request.
Shared configuration, logging, work/output location and status conventions stay
consistent across commands; exact option spelling remains adapter design work.

The legacy option-based invocation remains the compatibility path during
migration. Introduce grouped command dispatch without changing its recorded
defaults, flags, numerical behavior or existing help/version contract. M1
establishes callable services; M2 supplies typed TOML, M3 supplies general path
resolution and M4 establishes image-layout loading. M5/M6 connect the applicable
calibration/science commands as their services are extracted. M6b–M6d retain the
later linearity/dark/fringe numerical scope. This naming decision does not bring
those algorithms forward.

Native commands remain independently usable with TOML/FITS. Python owns the
planned ASDF project resolution boundary and may supply an exact resolved plan;
the numerical kernels do not parse ASDF or change cwd to discover files.
Optional mefppy calls the same services, with its stable public wrapper designed
later; internal Eclipse structs are not a permanent Python ABI. No separate
launcher aliases, install changes, automatic cascades or parallel execution are
introduced by this decision.
