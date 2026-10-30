# Agent project-authoring evidence — 30 October 2026

Base: ed949cab4f70381a1e187c7be691026c7fecf01c, new unmerged authoring-contract
files. Final agent command from the dedicated worktree:

```bash
TASK_SOURCE_REVISION=ed949cab4f70381a1e187c7be691026c7fecf01c nice -n 10 python -B docs/architecture/proposed/m2/project-contracts/check_contract.py --work-parent /workspace/scratch/555b377cf948
```

run-provenance.json records actual platform/Python, six examples, two caller
directories, 66 rejection diagnostics and input hashes. test.log transcribes the
successful tool output. source-sha256.json identifies checked source/catalog,
examples and retained native references; sha256.json identifies these artifacts.
Initial-fixture-assertion.txt preserves the earlier incorrect draft OCAM test
assumption and source-based correction. No native code/reference values changed.

No compiler/build, FITS, numerical, Pycavi, installation, target-host, WAD-runtime
or scientific check occurred. Actual Mac/representative shared Chapman Python
3.11 checks remain pending. Do not replay accepted native test matrices.
