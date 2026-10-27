# Developer documentation

BPM cleanup #90, 27 October 2026: [Mac instrumented acceptance](bpm-cleanup-acceptance-2026-10-27.md) and [Chapman3 target acceptance](bpm-cleanup-chapman3-acceptance-2026-10-27.md) are verified; PR #96 awaits integration. Broader memory/scientific gates remain open.

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
