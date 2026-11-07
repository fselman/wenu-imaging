# Common-parameter refinement — 7 November 2026

After acceptance/merge of clipped bias RON, owner authorized refining this existing viewer. It now defaults to Common QC with clipped RON first, and a master overview shows clipped/raw/MAD RON, master mean/median/RMS, high-offset counts and stored input membership counts for all product/detector rows. All stored parameters remain accessible with one selector. Older products explicitly show Not stored for clipped RON; stored unavailable values and zero remain distinct. Shared raw-sequence groups are prominently labeled; product selection highlights its rows and diamond markers without removing other products.

The refinement is based on accepted main af24c3699957d03a11f26c0bc47172b202ca0ede and retains the original PR #283. Owner previously reported that the first viewer worked, while requesting a smaller parameter set; no detailed first-generation browser receipt was supplied. No native recipe, numerical QC, build, configuration or reduced product is changed. No persistent QC store or representative JD is introduced.

Three Python projection/cache/error test groups and JS model/selector/overview tests pass, including seven master defaults, clipped priority, full-parameter fallback, no fabricated missing values, existing membership counts and shared-input groups. Definition keys and filtered collections are cached in memory. The real-browser harness has been updated for the new controls, but cannot run here: installed Chromium exits on denied socket/ptrace operations before loading the page. This is not a passing browser result; owner Mac generation and visual review are the next gate. No dependency installation or alternate browser access route was attempted.

Earlier three-product descriptions below describe the initial retained collection. A new generation enumerates all top-level product ASDF files, including the accepted full 32-detector clipped product CMDP.2026-11-07T21:05:44.919Z.001.asdf. It reads them once with the existing qualified ASDF environment and matching updated schema. Use a fresh orchestration inspection directory and preserve earlier pages, products and logs. The guarded `tools/qualify-bias-qc-viewer-mac.py` helper exports only the five matching viewer/helper/schema assets from the candidate, generates once with the existing private ASDF environment, records product identities and a receipt, and opens the new page. The main checkout stays at af24c36; no native mutable source/build changes are made.

---

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
