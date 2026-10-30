# M2 project domains/readout contracts — agent results — 30 October 2026

Owner accepted/merged PR #149 and confirmed clean Mac/shared Chapman main
ed949cab4f70381a1e187c7be691026c7fecf01c, accepted remaining-domain work, added
optional overscan/amplifier-specific readout requirements, then instructed
“Proceed with the next step.” See [contract and examples](../architecture/proposed/m2/project-contracts/README.md)
and [chain-wide overscan policy](../architecture/proposed/overscan-readout-policy.md).

## Actual delivery and checks

A dependency-free Python authoring validator checks versioned project,
association, reduction profile, ordered recipe, execution, quality, product
profile, processing reference and readout domains. Six complete authoring
examples cover retained WFI/OmegaCAM geometry and synthetic no-overscan,
defined-but-disabled, alternative-selected and simultaneous-channel cases.
The returned immutable byte record retains normalized declarations, containing-
file roots, source text/hashes and catalog hash. Caller copies and edits/deletion
of project/native source files cannot redefine a loaded record. Execution-ready
is always false; reference resolution/compliance/WAD runtime validation are not
claimed. Native reference scalar validation remains the accepted C reader's job.

The final actual agent run passed:

- All six catalog/example reproducibility checks and CLI validation from two
  unrelated caller directories.
- Exact legacy per-chip overscan-side assertions and retained WFI/OmegaCAM native
  reference hashes from accepted conversion evidence.
- Frozen project/native source, caller-mutation and ordered-recipe controls.
- 66 strict type/version/identity/contradiction/recovery cases and two malformed
  CLI-input controls; no project-root creation or source changes.

[Evidence](fixtures/agent-m2-project-contracts-2026-10-30/README.md) records actual
Python/platform, code/input hashes, rejection diagnostics and successful output.
A draft independent OCAM assertion initially assumed one common overscan side;
it failed. The source-derived example was already correct. The checker now pins
both alternating groups of eight, and the initial finding is retained. No native
geometry/reference or algorithm was changed to pass a check.

The owner's subsequent clarification is included: reported amplifier names,
active-amplifier fields and scan geometry in headers may be unreliable. Optional
exact raw-card evidence is retained separately with asset/version/HDU/occurrence,
unverified trust and unresolved disposition. A synthetic contrary scan card is
preserved without replacing configured geometry. Six added rejection cases
prohibit automatic header authority, trusted/selected claims, truncated cards,
missing detector references and duplicated occurrences. No actual header parser,
conflict resolver or hardware verification is claimed.

## Hardware and execution boundary

The owner reports two amplifiers per WFI detector and an exceptional alternative
amplifier. The current bundled PAF actually configures opposite-side overscan for
legacy chips 5–7; this is not sufficient to assign a physical amplifier identity
or explain the discrepancy. OCAM also alternates configured sides. No exposure
headers or hardware documentation were supplied/opened. Actual physical mapping
and readout applicability remain unverified; examples mark hardware inventory
not established and physical IDs unknown. Synthetic examples demonstrate
contract expressiveness, not real CCD/CMOS numerical support.

Native schema-1/2/3 constructors still require retained per-detector geometry and
the global scan switch; native code, engine linkage, C90/C17/C99 boundaries,
installation, numerical routines and Pycavi are unchanged. No new native build,
compiler qualification, FITS/native/Pycavi execution, scientific/QC/Phase3 or
full-M2 acceptance occurred. Geometry-free/multi-active examples explicitly lack
a native fallback. Subsequent M4/M5/M6 adapters/services must implement the
optional/per-amplifier policy under actual layout/numerical checks.

## Next gates

Actual selected Python 3.11.14 authoring checks on Intel Mac and one representative
shared Chapman host are pending. They require fresh private output directories
but no native rebuild, dependency install or historical matrix replay. After both
pass, record the paired receipt and present the bounded result for owner review.
General migration/duplicates, native/CLI/library frozen-plan integration, full
WAD domains/runtime and persistence remain later work. Optional BPM, required
M6a variance/covariance and #133/#144/#75 remain unchanged. No merge/cleanup is
authorized without the owner's separate instruction.
