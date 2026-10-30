# M2 project domains and readout authoring contract

30 October final M2 cumulative review after owner-accepted/merged PR #157 and
clean Mac/shared Chapman main 09a7aee4d69f04f5aeef954ff87c39d6f870d2d3:
[recommend original-scope M2 closure](../../../../developer/m2-final-closure-review-2026-10-30.md). The #155 project/native
composition gap is resolved; the complete checklist and six paired receipts support
configuration completion. This is a recommendation pending owner milestone
acceptance, not M3 execution. Retain existing JSON outputs for now as explicitly
instructed; human configuration remains TOML, and M7 retains planned ASDF
persistence without a newly invented JSON-removal requirement. Follow the current
plan and good programming practices; discuss proposed departures before
implementation. Source/evidence/documentation review only; preserve selected
tools, installations and all evidence, with no historical test replay. Separate
owner instruction precedes merge/cleanup. Earlier status notes are historical.

30 October paired project/native composition receipt: selected-tool Intel Mac
and representative shared Chapman4 private C90 builds and both affected CTests
passed 2/2 at d0ab19e91b46e6fe6e21c541af99c21ed35029b4. Protected installed files
and clean review checkouts stayed unchanged. See [paired results](../../../../developer/m2-project-composition-paired-results-2026-10-30.md).
The #155 configuration integration correction is target-qualified and ready for
owner review in PR #157. Full M2 closure remains a cumulative review/owner decision;
no M3, ASDF publication, numerical processing, installation or automatic merge.
Preserve selected tools and all evidence; this receipt needs no test replay.
Earlier target-pending notes below are historical. Separate owner instruction
precedes merge/cleanup.

30 October owner accepted/merged PR #156 and instructed merge, clean, and
proceed. At baseline ea35197a7f074ac1c44289e7bcc94336f92d6681, the next original-M2
increment implements [project/native composition](../project-composition.md) for #155. Project
envelope 2 composes reusable complete domain-v1 declarations; complete version-1
projects remain supported. The shared CLI/library loader uses the qualified C
resolver for complete/split/local native references and validates readout against
resolved settings, retaining all source texts/hashes/edges and domain origins.
Project conflicts fail (empty project override allowlist); numeric overrides stay
native. Agent focused C90 checks passed 2/2, including 18 primary profiles and 24
composition rejection/recovery cases. Actual Mac/representative Chapman checks
are pending. Native C/catalogs, installed software, numerical algorithms and
milestone order are unchanged; no M3 execution or ASDF publication. See
[agent receipt](../../../../developer/m2-project-composition-agent-results-2026-10-30.md). #155/full M2 closure remain open pending target/owner
review. Preserve accepted evidence; no historical matrix/tool replay or automatic
merge/cleanup. The earlier closure review retains its original as-is baseline.

30 October cumulative M2 review at accepted merged main
c0bbcc5866b49d64fad6498a029429b35ada9953: keep M2 open. Native configuration
resolution/equivalence, migration and provenance have accepted paired evidence,
but reusable project-domain composition is not connected to the frozen project
loader. The as-is loader still requires inline project domains and one complete
standalone native reference. [Closure review](../../../../developer/m2-closure-review-2026-10-30.md) records the original-gate
checklist, accepted chain and [remaining M2 integration #155](https://github.com/fselman/wenu-imaging/issues/155).
Do not infer full M2 closure from native test success or start M3. No source code,
new functional run, installation or numerical processing in this review; preserve
accepted tests/tools/evidence and implement no scope reduction. Owner review and
separate integration instruction remain required for this documentation branch.

30 October M2 migration implementation after accepted/merged PR #151 and clean
Mac/shared Chapman main a09bec7e6bc0d3fa8d82245db59aaf3063ac0d94: owner authorized
finishing configuration migration. The shared Python API/CLI and opt-in native
configuration bridge now migrate PAF values through the original constructor,
retain PAF/CFG text/hashes and duplicate/conflict records, preserve exact parsed
TOML source graphs/override contributions, and freeze WAD configuration attributes
for CLI/library requests. New examples match all 585 OCAM / 249 WFI stored values
and selected local CLI overrides exactly. CFG values remain explicit compatibility
evidence; no scientific associations/identities or executable plans are invented.
Agent C90/C17 focused checks and scoped ASan/UBSan pass. Actual selected-tool Intel
Mac and representative shared Chapman checks remain pending; full M2 closure needs
those results and owner review. Preserve original PAFs, installed tools/prefixes,
prior evidence and milestone order. No installation, numerical processing,
ordinary engine activation, ASDF publication, merge or cleanup is authorized by
this implementation. See [migration contract](../configuration-migration.md) and
[agent receipt](../../../../developer/m2-migration-agent-results-2026-10-30.md). Earlier remaining-migration notes are historical within
this implemented boundary.

30 October paired project/readout receipt: Intel Mac and representative shared
Chapman4 selected Python 3.11.14 authoring checks passed at
3769f5196f9be2c2581673f89c61ae2a472167d3: six examples from two caller directories,
66 rejection/recovery cases, immutable sources/recipe order and malformed CLI
controls. Protected installed files/checkouts stayed unchanged. See
[paired results](../../../../developer/m2-project-contracts-paired-results-2026-10-30.md). Ready for bounded owner review; full M2 remains open.
No numerical/hardware execution or header-trust qualification is claimed. Preserve
evidence/tools; no rerun for this documentation receipt. Earlier pending-target
notes below are historical. Merge/cleanup requires owner instruction.


30 October 2026. Owner authorized the next M2 increment after accepted/merged
PR #149 and clean Mac/shared Chapman main
`ed949cab4f70381a1e187c7be691026c7fecf01c`. The additional
[optional overscan/readout policy](../../overscan-readout-policy.md) is a required
forward contract, including CMOS omission and amplifier-specific geometry.

## Delivered boundary

This increment adds a closed, versioned **authoring validation** layer for the
remaining project/association/recipe/execution/quality/product-profile domains,
plus selected readout descriptions. It does not implement an association engine,
workflow executor, native dispatcher, scientific QC thresholds or ASDF persistence.
Existing native instrument/processing/product-mapping domains remain authoritative
for their numeric settings. Neither mefpp nor Pycavi loads these project files in
ordinary execution. This is a bounded M2 implementation, not M2 closure.

[catalog.json](catalog.json) is a small review notation, **not** a general JSON
Schema or ASDF metaschema. All tables are closed: unknown fields, wrong types,
missing fields, unsupported versions and scalar coercions fail. Project root
project_schema_version=1 is deliberately distinct from native schema_version=3.
Each domain has its own schema_version=1. Passing the authoring check is not a
native applicability, reference-availability, WAD-runtime or product-compliance gate.

| Domain | Implemented contract |
|---|---|
| project | Review identity/name, raw/calibration/output/work/log roots, each resolved relative to this containing file; no creation, discovery or cwd change |
| association | Explicit group/role bindings; selected requires asset ID and positive exact version; omitted forbids a selected identity. Input BPM may be explicitly omitted. No candidate selection or file lookup |
| reduction_profile | Separate identity and scientific/visual purpose; no implicit algorithm change |
| recipe | Separate identity and nonempty ordered steps with unique IDs and agreed native service names; declarations do not establish service implementation/availability |
| execution | Explicitly disabled serial declaration, one worker/thread, batch niceness 10–19; no launch, resource allocation or parallelism |
| quality | Record-only intent; estimators not qualified, no numeric cuts. Nonempty thresholds rejected pending a separate version/qualified contract |
| product_profile | Separate identity and legacy/ESO_Phase3 target; compliance not_validated and pre-M6a variance unavailable. No Phase 3 certification or variance-off mode for the M6a chain |
| processing | Explicit unavailable mode or reference to one complete standalone accepted native schema-3 file; no second defaults or include/override implementation |
| readout | Configured/synthetic authority, detector/channel identity status, active selection, per-channel optional overscan and signal regions. Physical amplifier inventory explicitly not established |

Association IDs and versions are declarations. This layer does not resolve group
membership, assets, calibration applicability or detector/FITS identity. Separate
profile IDs are required and never aliased to each other. The single-step
mef_sci_pp examples are illustrative ordered requests, not the full dataset recipe.

## Optional overscan and channels

The readout schema permits absent+subtract=false, defined+subtract=false and
defined+subtract=true. Defined requires a region; absent forbids it. Subtraction
requires an active channel and valid region. Regions use pixel and explicit
fits-1-based-inclusive endpoints; x endpoints are positive/ordered and y endpoints
are both present or both absent. Missing y means all rows of the selected channel,
not a guessed FITS height. Raw image bounds, binning, orientation, HDU applicability
and prescan/trim integration remain M4/M5/M6 qualification.

Channel names are local configuration labels, not hardware amplifier IDs. Known
physical identities must be explicitly declared with identity_status=verified;
unknown forbids an invented physical ID. A declared verified mapping requires
verified selected identities but is **not** independently verified by this tool.
The examples retain mapping_status=unverified and inventory_status=not_established.
Channels describe configured alternatives, not a complete hardware inventory.
Two simultaneously active channels require explicit disjoint signal regions;
active overscan may not overlap any active signal. The contract does not select
or implement a numerical correction model.

## Reported header evidence

readout.metadata_policy=explicit_review is mandatory. header_evidence may retain
exact 80-byte ASCII raw cards, source asset ID/version, HDU and card occurrence,
local detector reference and candidate field (amplifier_name, active_amplifier or
overscan_region). Every candidate stays trust=unverified and disposition=unresolved;
no raw-card parser or header-to-geometry overwrite occurs. Empty evidence means
not_supplied; nonempty means pending review in the immutable snapshot. The
alternative-selected synthetic example retains a contrary scan card without
changing selected geometry. It does not assert an actual instrument keyword.

Actual headers may be unreliable, and configured values are also assumptions.
Future M4 adapters must preserve both, compare candidates, expose discrepancies
and require explicit resolution before executing with an inconsistent mapping.
A declared verified identity is caller metadata, not proof of trustworthy headers.
This review checker cannot certify detector/readout facts from an authoring file.

## Complete authoring examples

| Example | What it demonstrates |
|---|---|
| [wfi.toml](examples/wfi.toml) | Eight legacy ordinal detectors; existing per-chip x strips and global subtraction flag preserved; physical IDs unknown |
| [omegacam.toml](examples/omegacam.toml) | Thirty-two legacy ordinal detectors; both configured overscan sides preserved; physical IDs unknown |
| [no-overscan.toml](examples/no-overscan.toml) | Synthetic single channel, no region and no subtraction; no native fallback |
| [defined-disabled.toml](examples/defined-disabled.toml) | Synthetic geometry retained with subtraction disabled |
| [alternative-selected.toml](examples/alternative-selected.toml) | Synthetic two-channel description with only alternative channel active, using its own opposite-side geometry |
| [dual-active.toml](examples/dual-active.toml) | Synthetic simultaneous two-channel selection with distinct scan/signal regions |

The WFI/OmegaCAM project identities, asset choices, roots and recipe are review
labels, not observed projects or real calibration associations. Only their native
reference bytes/values and scan geometry come from the accepted configuration
examples. WFI's checked-in strips are 2100..2142 on chips 1–4/8 and 5..48 on 5–7;
OmegaCAM uses the same two strips in alternating groups of eight. This does not
identify the physical alternative amplifier or establish a hardware explanation.
No exposure headers are supplied/opened in this increment.

WFI/OmegaCAM reference the complete [native examples](../examples/README.md), whose
original PAF text, hashes and exact stored-value comparisons are already accepted.
The project loader checks exact legacy ordinal coverage, one active channel per
detector, scan endpoints and agreement with the native global subtraction switch.
It requires retained geometry even if a legacy switch is disabled. Geometry-free
or multi-active requests are native_mode=unavailable: no fake native keys, zero
regions or silent fallback. Native scalar/type/unit validation still belongs to
the unchanged C reader, not a second Python numeric implementation.

## Frozen records and WAD crosswalk

validate_project.load returns FrozenProject owning serialized bytes. as_dict
returns an independent copy. It records the full normalized authoring tree,
resolved roots, exact project/native source text and SHA256, catalog SHA256,
explicit execution_ready=false, reference_validation=not_resolved,
product_compliance=not_validated and wad_validation=review-crosswalk-only.
Read errors and size limits fail, not repair or reread fallback. Source records
identify bytes actually read; multi-file reads are not an atomic filesystem
snapshot. Runtime native per-field source hashes/history remain separate work.
No published plan/run is created and no durable store is advanced.

| Existing M0a WAD review concept | Authoring mapping and limit |
|---|---|
| project.roots / profiles | Normalized roots and three separate profile/recipe identities; no project revision publication |
| association.selected | Explicit asset ID/version and omission; no availability/applicability assertion |
| configuration.settings / sources | Frozen authoring tree and exact input text/hashes; native values remain in referenced version-3 text |
| task.operation / depends_on | Ordered requested service names; no task DAG or scheduling constructed |
| image.detector_id / hdu | Physical IDs may be unknown; legacy ordinals remain ordinals, no HDU/asset mapping invented |
| image.corrections | Requested per-channel subtraction only; no applied state fabricated |
| image.variance / product provenance | Pre-M6a unavailable and compliance not_validated; M6a required variance policy unchanged |

## Focused check and next gates

Python 3.11+ standard library only; no dependency install. Run from any cwd:

```bash
python -B /absolute/checkout/docs/architecture/proposed/m2/project-contracts/check_contract.py --work-parent /existing/private/work
```

The checker reads the catalog/examples/native hash evidence, writes only fresh
private fixtures/reports under the supplied work parent, exercises six examples
from two unrelated directories, 66 rejection/recovery cases, malformed CLI input,
source-edit/deletion and caller-mutation lifetime controls. It checks actual WFI
and OCAM per-chip geometry and accepted native source hashes. No C build, native
execution, FITS, Pycavi routines, installation or scientific validation. Catalog
and example generators are reproducibility helpers, not migration tools.

See [agent results](../../../../developer/m2-project-contracts-agent-results-2026-10-30.md).
Actual selected Python 3.11 Intel Mac and representative shared Chapman authoring
checks remain pending; do not replay native matrices or requalify tools. The
accepted native implementation is unchanged. Remaining M2: general migration,
duplicate/conflict ledger integration, complete provenance/CLI-library plan
integration and runtime WAD validation. Numerical optional/multi-amplifier overscan
needs its explicit native request/adapter/service implementation and qualification
in the original milestone order. Owner review precedes separate merge/cleanup.
