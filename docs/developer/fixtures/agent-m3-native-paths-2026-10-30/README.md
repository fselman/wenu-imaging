# Agent native-path evidence — 30 October 2026

Raw focused logs, compile configuration, source hashes and per-command provenance.
See [the result receipt](../../m3-native-paths-agent-results-2026-10-30.md).
The compile records say source_revision unknown because these private builds
used an uncommitted candidate; tested-source-sha256.json records the exact final
source/test files instead of inventing a commit identity. Source inventory in
build-info is configure-time evidence; the final test-only log/provenance
assertions were added afterward. No numerical C source changed between final
builds and qualified runs. Failed runs remain evidence, not accepted controls.
