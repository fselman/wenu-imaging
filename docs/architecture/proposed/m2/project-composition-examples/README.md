# Reusable project composition examples

Both project entries reuse `shared/profiles.toml`. Their instrument subsets retain
the accepted per-chip readout declarations and reference the accepted native
local-override examples, which in turn include reusable native subsets.

- [OmegaCAM](omegacam/project.toml)
- [WFI](wfi/project.toml)
- [Shared policy/profile declarations](shared/profiles.toml)

These are source-review templates, not real observation/association choices or
installed scientific defaults. Project envelope 2 composes complete domain-v1
blocks; numerical values and overrides remain native-reader responsibilities.
Use the integrated `freeze-project` API/CLI described in the
[contract](../project-composition.md). The earlier standalone authoring CLI keeps
its version-1 review-only boundary.
