# Bias scalar QC inspection — 7 November 2026

Owner approved the bounded first view in design/bias-qc-inspection-v1.md. It is
prepared as tools/view-bias-qc.py with bias-qc-viewer.html and
bias-qc-inspection.js. It reads product ASDF once per generation and writes one
self-contained HTML file. All selection/plotting then uses that page's data.
It never reads referenced raw/FITS images or changes products. No native C or
libasdf recipe change, build, reconfiguration, installation or reduction.

The page lists product coverage and stored creation times, shared ordered
raw-input sequences, all scalar master/input QC, unavailable states and reasons,
full point definitions/source bindings, header/configuration provenance and
array names/counts. A product selector uses diamonds/highlighted table rows,
with the other products retained as circles. Definition groups separate units,
stages, methods and region/mask definitions. X is detector category, not time.
No representative observation epoch or JD policy is selected. These three
existing master files share raw exposures and must not be treated as independent
historical measurements. No persistent QC database/cache is introduced.

## Agent verification

- Three Python test groups pass: detached scalar/array projection and explicit
  unavailable/zero; exactly one read callback per enumerated file, bad-file
  visibility and shared-input grouping; source-change/nonfinite/duplicate/stem
  refusal. HTML escapes embedded closing-script strings.
- JS model tests pass definition/unit separation, missing versus zero, scope/
  detector filtering, pagination and constant-value plotting ranges.
- CLI help and outer/inline JS syntax pass; existing shared plot cursor-binding
  tests pass separately. These are metadata/model checks, not actual ASDF reads.
- Agent has no ASDF runtime. Local Playwright browser could not start (missing
  bundled shell; installed Chromium blocked on socket/ptrace operations).
  Cloud preview explicitly blocks local-file URLs; no alternate route was used.
  Actual browser painting, responsive layout and click-through acceptance remain
  pending. The saved optional tools/tests/test_bias_qc_browser.py harness records
  intended real-browser controls; its failed launch is not a passing result.

No actual Mac products were accessible to the agent. The next gate is a single
generation from the retained three product ASDF files using the existing private
ASDF interpreter and a new inspection directory under orchestration. Print each
loaded file/detector/row count, then open the resulting page in the owner's
browser. Every unavailable file must be reported; a partial collection returns
exit 2 while retaining a visibly incomplete page. Preserve failed evidence and
do not overwrite an existing view during retries.

## Invocation after source delivery

Use the qualified ASDF interpreter and the delivered viewer source, for example:

```bash
/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python -B \
  /Users/fselman/Developer/wenu-imaging/tools/view-bias-qc.py \
  --products /Users/fselman/Pictures/OCAM/test_recipes/reduced/cal/bias \
  --output /Users/fselman/Pictures/OCAM/test_recipes/orchestration/qc-bias-inspection/index.html
```

Create the chosen new output parent explicitly first. During branch review the
guarded delivery block exports only the four viewer/helper files to a new
orchestration inspection directory, preserving clean main and the selected
build. It also exports the canonical schema at its original repository-relative
path. The source root is inferred from the tool's location; maintain this layout.
Existing helper/schema bytes must match merged main. No checkout/build switch.

The HTML is offline and contains local file paths/configuration provenance;
choose deliberately before sharing it outside the project. Product selection
does not trigger another harvest. New products require a new explicit page
generation in a fresh output destination.
