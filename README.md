# wenu-imaging

wenu-imaging coordinates Pycavi (Python), mefpp and qfits for astronomical image
reduction. The Python distribution and imports retain the name **pycavi**.

Install the Python component from the **repository root**, using an isolated
reference environment:

```bash
python -m pip install .
```

For the notebook application and a kernel in that environment:

```bash
python -m pip install '.[notebooks]'
pycavi_setup /path/to/new-notebook-workspace
```

Existing notebook, configuration and reference-data files are preserved by
setup. `--overwrite` explicitly replaces them. Run `pycavi_setup --help` and
`pycavi_setastro --help` for the installed commands.

This installs Python modules, 15 notebooks, 12 configuration templates and four
historical WFI CSV tables with their readme. It does **not** compile/install
mefpp, qfits or the external astronomy engines, download astrometry indexes,
create calibrations or establish scientific validity. WFI resources are retained;
WFI implementation and dedicated validation are deferred.

See [installation and validation](docs/developer/installation.md) for external
software, reference constraints, Mac/Linux instructions and known blockers.
The [roadmap](docs/developer/roadmap.md) governs subsequent notebook thinning,
configuration-driven scripts, the Pycavi Python library audit, then the mefpp audit.
No scientific-library or external-engine upgrades are part of this packaging work.

## Licensing

Existing component and source-file license notices remain in place. The old
Python metadata referred to a `Pycavi2/LICENSE` file that is absent. This change
does not assign a new license to Pycavi; the maintainer must resolve the missing
aggregate license declaration before a public package release. In particular,
retain the existing PAPI source notices. Native components have their own license
files and are not incorporated into the Python wheel.
