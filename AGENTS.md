# wenu-imaging

Intel Mac native acceptance, 25 October 2026: Fernando reports C90/C17 native
builds, three CTest entries per mode, exact OCAM/WFI BPM pixels, checksum metadata
accounting, real private installations/repeats/installed CLI and C17 DESTDIR passed
at source 41c8e6a544c1bc5122dc558e0c8cc7904214e1d0. See
[the acceptance record](docs/developer/native-mac-build-install-acceptance.md). Historical engine and configuration
remain selected/unchanged. Observational pixel equivalence, installed wrapper,
calibration/WFI fixtures, failure/memory and chapman3 gates remain pending.
Prepare immutable observational fixtures next; publication starts no reduction,
engine switch, merge or branch cleanup. Earlier pending statuses below are historical.

Stage 4 amendment, 25 October 2026: Fernando requires creation and propagation
of per-pixel frame variances for science and calibration products. Follow
[roadmap revision 1.3](docs/developer/mefpp-modernization-roadmap-v1.md): squared units, masks, gain/RON,
calibration/parameter uncertainties, shared-normalization correlations and
Pycavi/resampling/photometry handoffs, with independent recovery tests. This is
future Stage 4 scope; preserve the current Stage 1 build-only boundary.

Stage 1 candidate implementation, 25 October 2026: Fernando authorized the isolated
bundled-source CMake build after reviewing stage 0 and reporting actual-Mac
fixture settings. See [candidate status](docs/developer/native-cmake-candidate.md)
and mefpp2/README.cmake.md. qfits is now under mefpp2/qfits5 in this candidate;
retain all 18 qfits and 79 Eclipse archive sources. Numerical algorithms,
allocator policy, existing installations and data remain unchanged. Agent Linux
GCC 13.3/CMake 3.29.6 code-only C90/C17 builds and three CTest entries per mode
passed; this is not Mac/chapman3 qualification. Actual BPM decompression, complete
runtime install and observational pixel equivalence are pending on the Mac.
No engine switch, observation rerun, memory-clean claim, merge or branch deletion
is authorized by this implementation. Earlier audit-only holds below are historical
where superseded by this bounded authorization.

Stage 0 native build specification, 25 October 2026: read
[the specification](docs/developer/native-build-specification-v1.md) before
implementation. It defines the minimum static target graph, runtime payload,
fixtures and pending gates. Mac synthetic C90/C17 CMake/CTest probe passed;
real native builds, fixture manifests and chapman3 toolchain remain pending.
Initial candidate tools: CMake/CTest 3.29, Unix Makefiles, explicit Xcode tools.
No native source/build/install change is made by this documentation delivery.

Native roadmap revision 1.2, 25 October 2026: retain C89/C90 as the portable C
source baseline and explicitly qualify compilation and behavior in C17 mode.
C17 is a compatibility target, not a new source-feature baseline. Inventory
legacy/dependency extensions and isolate platform APIs; do not claim existing
strict compliance. Newer facilities need a reviewed exception. C23 checks are
optional. Mac compiler support is distinct from unperformed mefpp tests;
chapman3's inventoried GCC 4.8.5/Clang 3.4.2 cannot provide the C17 lane. Qualify
an isolated compatible compiler without implicitly replacing system tools or
upgrading glibc. This clarification authorizes documentation, not installation.

Roadmap v1 revision 1.1, 25 October 2026: extend data review to JWST, Roman,
Rubin, ELT and publicly documented future ESO archive plans, distinguishing
adopted standards from proposals/unknowns. Native Apple Silicon arm64 build/install
and functional acceptance is required; Rosetta is not acceptance. Extend the
parallel design assessment to optional threads within detectors and optional GPU
backends only after profiling/equivalence evidence, retaining a portable ANSI-C
CPU baseline, global resource limits and shared mosaic normalization. This is
planning authorization, not permission to add threading/GPU dependencies or run
new workloads. No accelerator backend or hardware purchase is selected.

Data-representation review added to native roadmap v1, 25 October 2026: insert
stage 2A immediately after memory qualification and before component contracts.
Review current accepted formats/metadata models and in-memory structures,
including FITS, HDF5, ASDF and Zarr, without preselecting a replacement. Preserve
FITS ingestion/interchange and originals; compare actual performance/fidelity
and ANSI-C/platform/dependency costs. Any new backend needs a separate reviewed
migration and renewed memory checks. See the version-1 native roadmap.

Current roadmap version 1, 25 October 2026: Fernando authorized documenting
[the native roadmap](docs/developer/mefpp-modernization-roadmap-v1.md) and
[current mefpp architecture](docs/developer/mefpp-current-architecture.md).
These supersede older sequencing descriptions for planning: clean build/install
Mac then chapman3, memory correctness, component extraction/new calibrations,
single detectors, parallel mosaics, native Windows qualification, CMOS last.
Windows portability is considered from the start. Preserve shared mosaic flat
normalization and distinguish acquisition gain/RON from processed effective values.
CMake/CTest and API names remain proposals; no implementation or install starts
from publication. Review/version the plan as evidence changes. Earlier dated
instructions below are historical where they conflict with this planning update.

Current hold before native modifications, 25 October 2026: Fernando requires
an expanded architecture/modern-practice/Eclipse-usage audit first, then a full
roadmap for review before any implementation. See
[the architecture audit](docs/developer/native-architecture-audit-2026-10-25.md)
and #73. Do not proceed directly from installation audit #64/#72 to moving
qfits, fixing builds or extracting components. Bias/BPM/non-linearity/dome/sky/
master-flat/science components are design candidates, not approved changes.
Current work is audit evidence/diagrams only; preserve source and installations.

Current scope override, 25 October 2026: Fernando explicitly brings point 5
forward for a mefpp/qfits build and installation audit, Intel Mac first and
chapman3 second, with qfits to move under mefpp. See
[the native installation audit](docs/developer/native-installation-audit-2026-10-25.md)
and #64. First audit is read-only source review/disposable fixture probes;
native source migration and target build/install acceptance remain pending.
This overrides earlier native-work deferral only for the bounded installation
task. Preserve existing engines/data; no numerical changes, upgrades, new
runtime parallelism or scientific tuning. Follow the latest canonical scope.

Current Mac handoff, 25 October 2026: selected installed-library paths for one
CP Pup r_SDSS exposure (32 detectors) passed through notebooks 03–09, including
both model applications and twelve catalogue QC PNGs. See
[the Mac pilot](docs/developer/pilots/mac-cp-pup-2017-03-13/README.md).
This is not full notebook orchestration, multi-exposure/filter Mac acceptance or
scientific validation. #62 parameter investigation and scientific tuning wait
until the agreed later stage after all fields are reduced. Current work records
acceptance/roadmap only; preserve outputs, and do not start refactoring, reruns,
upgrades or merge/cleanup without the applicable instruction. Earlier dated
handoffs below are historical; follow the newest canonical instructions.

Test explanations, approved 25 October 2026: before every functional test or
result-verification test, explain its purpose, inputs, actions, the actual
Pycavi subroutines/methods and native tools exercised, and expected outputs and
pass criteria. Distinguish processing from read-only verification and functional
success from scientific validation. In testing scripts and command groups, add
short comments identifying each test section; the announced tests and script
comments must correspond in both directions. Report actual results and
limitations after execution. See the canonical developer instructions.

Defect tracking, approved 23 October 2026: create a GitHub issue for each
distinct defect found, checking for an existing ticket first. Record evidence,
scope and acceptance criteria; link the fix and verification in a correction
comment before closing it. Keep unresolved native causes and pending target
qualification open. See the canonical developer instructions.

Current integration handoff, 24 October 2026: Fernando authorized merge and
cleanup of qualified PRs #43/#45/#47/#50/#52, in that dependency order. Preserve
all qualified commits and verify the final main tree against this integrated
head, then remove only merged branches with ancestry/tip checks. Synchronize
chapman3 from its inspected clean checkout; no reinstall or reduction rerun.
Selected functional paths through notebook 09 and twelve QC PNGs passed.
Scientific/orchestration/export/Mac gaps and #51 remain open. This instruction
authorizes integration/cleanup only, not further processing or unrelated fixes.

Latest scope, 23 October 2026: finish and document chapman3 dependency
qualification before the Pycavi workflow audit. Aim to align Mac versions where
practical. Python future-proofing follows the agreed five points, not this gate.
See the controlling dated updates in the developer instructions and roadmap.

Read and follow [the developer agent instructions](docs/developer/agent-instructions.md)
before work in this workspace or its component directories. Also read the
[architecture](docs/developer/architecture.md) and [roadmap](docs/developer/roadmap.md).

The immediate goal is an OmegaCAM reduction set for ESO Phase 3 submission.
Multiprocessing is within one node; mefpp remains serial for this milestone.
Component implementation changes require authorization for the relevant stage.

Before user-facing terminal commands, follow the machine/repository guards in
the developer instructions. Fernando works on Mac/wenu and chapman3/wenu-imaging
in parallel. Batch reduction launches must use niceness >=10; the interactive
Jupyter server/kernel stays at niceness 0 (23 October clarification).
Before changing either user's cloned wenu-imaging checkout or its installation,
obtain current Git/environment evidence from that actual computer; an agent's
checkout is not evidence of the user's local state. See the canonical policy.

After every push or merge, automatically provide the applicable complete,
guarded synchronization/verification commands and any authorized cleanup steps.
Give one command group at a time and inspect the user's result before dependent
operations. Distinguish agent-workspace, GitHub, chapman3 and Mac status; never
claim that remote delivery synchronized a user's clone. Follow the canonical
[delivery handoff rules](docs/developer/agent-instructions.md#delivery-handoff-and-local-synchronization).

The original audit is historical evidence, not the current agent policy.

Scope clarification, 21 October 2026: package wenu-imaging and debug/improve
Pycavi first; do not upgrade Python libraries or external engines yet. Audit
single-detector support and all opportunities for single-node parallel work.
mefpp implementation follows the Pycavi milestone. See the dated scope update
in the developer instructions and roadmap.
