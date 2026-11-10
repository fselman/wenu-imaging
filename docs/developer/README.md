# Developer documentation

- [Architecture](architecture.md): component boundaries and data contracts.
- [Recipe template](native-operation-recipe-template.md): common readable structure.
- [Acceptance by recipe](../acceptance.md): real-data product comparisons and test scope.
- [Scientific guides](#scientific-guides): equations, conventions and source mapping.
- [Current priorities](roadmap.md): short list, not a historical diary.
- [Agent instructions](../../AGENTS.md): one authoritative set of working rules.

## Scientific guides

Read only the guide for the operation being changed. LaTeX sources accompany PDFs.

- [Bias recipe](bias-recipe-mathematical-guide-v1.pdf) ([source](bias-recipe-mathematical-guide-v1.tex)).
- [Bias clipped RON](mathematics/mefpp/bias-clipped-ron.pdf) ([source](mathematics/mefpp/bias-clipped-ron.tex)).
- [Temporal median convention](mathematics/mefpp/bias-median-even-handling.pdf) ([source](mathematics/mefpp/bias-median-even-handling.tex)).
- [Detector characterization design](detector-characterization-design-2026-11-02.pdf) ([source](detector-characterization-design-2026-11-02.tex)).
- [Joint shutter/linearity interface](joint-shutter-linearity-interface-2026-11-03.pdf) ([source](joint-shutter-linearity-interface-2026-11-03.tex)).
- [Linearity preparation](linearity-preparation-guide-v1.pdf) ([source](linearity-preparation-guide-v1.tex)).
  Inspect completed recipe measurements with `tools/view-bpm-linearity-qc.py
  --manifest RUN/manifest.json --detectors detector.toml
  --processing processing.toml --run FRESH_REDUCED_VIEWER_DIRECTORY`.
  Run from orchestration. The offline page reuses the QC plots and shows saved BPM
  histograms; it opens no images or external TSV files and applies no correction.
  Geometry/processing must match the executed recipe fingerprints.
- [Saved linearity residuals](linearity-residual-asdf-guide-v2.pdf) ([source](linearity-residual-asdf-guide-v2.tex)).

The [design directory](design/) contains the reviewed scientific/structural contracts.
Some guides describe scoped or pending capabilities; consult the current issue
before implementing a scientific change. Manuals, papers and standards elsewhere
under docs are external reference material. Work summaries live in
[issues](https://github.com/fselman/wenu-imaging/issues), not dated report collections.
