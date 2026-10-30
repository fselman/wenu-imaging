# M2 project/readout authoring contracts — paired results — 30 October 2026

Intel Mac and representative Chapman4 selected-Python authoring checks passed
at implementation `3769f5196f9be2c2581673f89c61ae2a472167d3` (PR #150).
Protected installed files and clean review checkouts remained unchanged.
The bounded increment is ready for owner review; full M2 remains open.

## Evidence boundary

These are owner-returned terminal results inspected in Work chat, not an
independently transferred/hash-audited target archive. Logs, protected-file
baselines and detailed JSON reports remain in the private directories below.
Python 3.11.14 was explicitly checked on both hosts, with optimization disabled.
No native build, C90/C17/sanitizer, FITS/native/Pycavi processing, dependency
installation, hardware/readout applicability or scientific/QC acceptance occurred.
Accepted native matrices were not replayed and selected tools were not requalified.

## Actual checks

| Target | Private source/work directory | Detailed report subdirectory | Result |
|---|---|---|---|
| Intel Mac MC02VV0HPHTDG, macOS 13.7.8 | /Users/fselman/Software/build/wenu-imaging/mac-m2-project-contracts-opS6NPhF | m2 project contracts jl5ck92c | Passed |
| Chapman4 EL7 x86_64, shared home | /home/fselman/Software/build/wenu-imaging/chapman-m2-project-contracts-NOCCdfDa | m2 project contracts 7qqbzaeg | Passed |

Chapman /home paths resolve to /home1. Each detailed subdirectory contains
run-provenance.json; each parent contains tests.log, source-commit.txt,
protected.json and a fresh source export. Tests used niceness 10 and the already
selected Python, not the base environment.

Both hosts returned all four pass groups:

- Six authoring examples from two unrelated caller directories, retained native
  reference hashes and exact per-chip WFI/OmegaCAM geometry.
- Frozen project/native source records survive caller mutation, source edits
  and deletion; ordered recipe declarations remain in their original order.
- 66 rejection/same-process recovery controls for schema/types, identity,
  overscan states/geometry, native-reference contradictions and header authority.
- Malformed CLI input rejected; no project-root directories or source files changed.

The tests exercise validate_project.load/validate/native_consistency/check and
the authoring CLI. Sources are bounded private/exported TOML; destructive lifetime
controls edit/delete newly generated synthetic fixtures only. No ordinary
Pycavi or mefpp routine is called.

Mac protected the installed mefpp executable, pycavi_astrosoft.cfg and installed
pycavi_associate_reduction.py hashes. Chapman protected its configuration and
installed reduction-module hashes. Both confirmed unchanged clean review HEAD.

## Meaning and limits

The model represents absent overscan, retained-but-disabled geometry,
alternative selected channels and simultaneous channels with distinct regions.
Reported amplifier/overscan cards remain unverified evidence, separate from
configured geometry. Synthetic contrary evidence cannot overwrite selected
settings or imply verified hardware identity. No actual frame headers are
parsed here, and an author-supplied verified declaration is not an independent
hardware verification. WFI's exceptional physical amplifier mapping remains to
be checked against actual frames/documentation rather than inferred from strips.

This authoring validator does not activate processing. Existing native constructors
still require retained legacy geometry and one active channel/global flag;
geometry-free and simultaneous-channel examples explicitly lack native fallback.
M4/M5/M6 adapters/services must implement/qualify the accepted optional/readout
policy. Configuration itself remains an assumption, not proof headers are wrong.

See [contract/examples](../architecture/proposed/m2/project-contracts/README.md),
[overscan/header policy](../architecture/proposed/overscan-readout-policy.md) and
[agent results](m2-project-contracts-agent-results-2026-10-30.md). General migration,
complete duplicate/conflict histories, native/CLI/library frozen-plan integration,
full WAD runtime and persistence remain pending. Optional BPM / required M6a
variance/covariance and #133/#144/#75 are unchanged.

This receipt is documentation only; no rerun or rebuild is required. Preserve all
private evidence. Owner review precedes separately authorized merge/cleanup.
