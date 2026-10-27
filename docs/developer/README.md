# Developer documentation

Latest S2-05: [bounded BPM correction verified on Mac and Chapman3](stage2-bpm-chapman3-acceptance-2026-10-27.md); exact FITS products and ownership/accounting pass. PR stack awaits integration; full S2-05 and target external diagnostics remain open.

Latest S2-05: [corrected Mac BPM gate accepted; target runner prepared](stage2-bpm-mac-acceptance-2026-10-27.md). Exact products preserved, double-purge resources zero; target execution and broader S2 remain pending.

Latest S2-05: [ownership correction prepared for #109–#112](stage2-bpm-ownership-correction-2026-10-27.md); failed baseline retained, fresh actual Mac verification pending.

Latest S2-05: [failed Mac baseline inspected and attributed](stage2-bpm-baseline-evidence-2026-10-27.md), #109–#112; numerical checks pass, ownership repair awaits native qualification.

Next S2-05: [BPM ownership baseline prepared](stage2-bpm-ownership-2026-10-27.md), unchanged accepted driver/fixtures, Mac native execution pending.

[Full agreed S2 milestone and current status](stage2-memory-qualification-2026-10-27.md#declared-test-matrix): departures require prior agreement with Fernando and documentation before implementation.

Latest S2-04: [Mac and Chapman3 split/cache acceptance inspected](stage2-split-chapman3-acceptance-2026-10-27.md). All 80 Mac and 40 target pairs pass; PR #105 awaits review/integration. Broader Stage 2 and target external diagnostics remain open.

Latest S2-04: [Mac split/cache acceptance inspected; target runner prepared](stage2-split-mac-acceptance-2026-10-27.md). All 80 pairs pass with controlled cache attribution. Chapman3 verification and broader Stage 2 remain pending.

Latest S2-04: [repaired observer inspected; cache-attribution control prepared](stage2-split-observed-evidence-2026-10-27.md). All 80 functional pairs pass; the resource gate remains failed in 64 cases. Fresh control and target verification pending.

Latest S2-04: [inspected first baseline and descriptor-observer repair (#106)](stage2-split-baseline-evidence-2026-10-27.md); fresh actual-Mac observation remains pending.

Current Stage 2 increment: [S2-04 split ownership baseline](stage2-split-ownership-2026-10-27.md), prepared after S2-03 integration; actual Mac qualification pending.

Latest S2-03: [Mac and Chapman3 bounded correction acceptance](stage2-cli-chapman3-acceptance-2026-10-27.md); PRs #102/#104 await integration.

Latest S2-03: [Mac correction accepted; Chapman3 verification prepared](stage2-cli-mac-acceptance-2026-10-27.md).

Current S2-03 correction: [bounded getopt name matching (#103)](stage2-getopt-correction-2026-10-27.md), prepared for actual Mac verification; failed baseline remains retained.

Current Stage 2 increment: [S2-03 CLI ownership baseline](stage2-cli-ownership-2026-10-27.md), Mac baseline completed with parser defect #103; [inspected failed evidence](stage2-cli-baseline-evidence-2026-10-27.md) is retained after integration of #97/#98/#100/#101.

Current Stage 2 acceptance, 27 October 2026: [context cleanup #99 is verified](stage2-context-chapman3-acceptance-2026-10-27.md) on Mac C90/C17 (48 cases) and Chapman3 C90/C17 (24 functional/accounting cases). Tool controls, failed baseline and corrected evidence are retained. PR stack #97/#98/#100/#101 awaits integration. #75 and the remaining Stage 2 normal/error/repeat, cache, allocation-failure and mapped/swap gates stay open; Chapman3 sanitizer/leak-tool coverage is not claimed. Next after integration is S2-03 CLI/parser/engine failure ownership, not Stage 2A/extraction. Keep run directories, archives and installations preserved. This status supersedes earlier pending context-cleanup statements below.


Next: [Stage 2 memory/ownership matrix](stage2-memory-qualification-2026-10-27.md). #90 is resolved; broader #75 and leak qualification remain open.

BPM cleanup #90, 27 October 2026: [Mac instrumented acceptance](bpm-cleanup-acceptance-2026-10-27.md) and [Chapman3 target acceptance](bpm-cleanup-chapman3-acceptance-2026-10-27.md) are verified; PR #96 is merged. Broader memory/scientific gates remain open.

For ordinary installation, use the [short user guide](../installation.md).
This directory contains development policy, detailed procedures and evidence.
The latest dated policy/acceptance record controls; old audits remain historical.

## Current work and policy

- [Agent instructions](agent-instructions.md)
- [Overall roadmap](roadmap.md)
- [Native modernization roadmap](mefpp-modernization-roadmap-v1.md)
- [Current native candidate and remaining gates](native-cmake-candidate.md)

## Installation and portability

- [Native build/install/qualification guide](native-installation.md)
- [Configure/make frontend status and target gate](native-frontend.md)
- [Detailed Python installation and packaging](installation.md)
- [Intel Mac native build/install acceptance](native-mac-build-install-acceptance.md)
- [Mac/Linux package-manager assessment](native-distribution-options.md)
- [Pycavi portability audit](pycavi-portability-audit-2026-10-21.md)
- [External tools and library options](external-tools-and-library-options-2026-10-21.md)

## Architecture and native design

- [Overall architecture](architecture.md)
- [Current mefpp architecture](mefpp-current-architecture.md)
- [Native build specification](native-build-specification-v1.md)
- [Native architecture audit](native-architecture-audit-2026-10-25.md)
- [Native installation audit](native-installation-audit-2026-10-25.md)
- [Single-detector/parallel audit](detectors-and-parallel-work-audit-2026-10-21.md)
- [Thin notebooks and script interface review](pycavi-two-interface-review-2026-10-21.md)

## Workflow evidence and corrections

- [Mac CP Pup pilot](pilots/mac-cp-pup-2017-03-13/README.md)
- [chapman3 CN Ori pilot](pilots/chapman3-cn-ori-2017-03-11/README.md)
- [Chebyshev correction and pilot](chebyshev-repair-2026-10-21.md)
- [Catalogue execution correction](catalogue-repair-2026-10-21.md)
- [Gaia IDs](gaia-source-id-correction.md)
- [Catalogue integer IDs](catalogue-integer-correction.md)
- [Illumination null masks](illumination-null-mask-correction.md)
- [Kriging readback](kriging-readback-correction.md)
- [Kriging application](kriging-application-correction.md)

## Historical background

- [Original audit, 20 October 2026](audit-2026-10-20.md)
- [Previous Mac installation/workflow](mac-installation-history-2026-10-20.md)
- [Repository migration](migration.md)

This is the first navigation reorganization. Before moving dated files into
physical subdirectories, inventory and update their inbound links, AGENTS and
guide references together; preserve stable entry points. New developer documents
must be added to the appropriate topic, not appended as an undifferentiated list.

The immediate scientific goal remains OmegaCAM products for ESO Phase 3.
Functional acceptance, scientific validation and archive compliance are distinct.
Native mefpp remains serial; later threading/accelerators follow reviewed gates.

- [Native configuration/failure correction and 26 October evidence](native-failure-correction-2026-10-26.md).
