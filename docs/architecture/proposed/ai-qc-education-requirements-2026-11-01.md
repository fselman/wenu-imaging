# AI-assisted processing, QC, and education — architecture requirements review

**Date:** 2026-11-01  
**Status:** Owner-approved architectural objectives; requirements review only. No implementation or detailed interface contract approved.  
**Scope:** wenu-imaging (Pycavi, mefpp, project services, QC, documentation).  
**Development constraint:** This review is **non-blocking**. Continue accepted M5–M11 work and existing verification gates without delay.

## Executive summary

Wenu-imaging should be an accessible scientific processing and educational environment, not solely an expert-oriented reduction pipeline. It must support installation, project setup, raw-frame QC, calibration and science processing, execution monitoring, quality assessment, instrument characterization, and optional ESO Phase 3 preparation. All operations must remain scientifically reproducible and available without an AI assistant or Internet connection when required local data and dependencies are installed.

**Design principle:** AI-ready, AI-optional, offline-capable, scientifically deterministic.

## Adopted objective: controlled-autonomy AI assistant (AR-AI.01)

The future assistant should help with installation and dependency diagnostics, project configuration, calibration association, execution supervision and recovery, QC interpretation, anomaly investigation, and Phase 3 preparation. Routine operations may be performed within explicitly granted permissions. **Significant scientific decisions and external submissions require explicit human authorization.** AI interpretations must be labeled and distinguished from measurements, deterministic QC rules, and recorded human decisions. No AI model, protocol (including MCP), or implementation is selected yet.

## Five target users and observability

1. Professional astrophysicist processing infrequently, without expertise in data processing or computation: scientific reliability and intelligible provenance.
2. PhD student urgently needing calibrated data: fast start, visible progress, actionable blockers, available outputs.
3. Operations astronomer: instrument health, detector-level trends, diagnosis and localization of anomalies.
4. QC operator with limited astronomy/physics/data expertise: understandable evidence, thresholds, documented decisions and escalation.
5. Amateur astronomer without technical background: rapid processing, clear previews and understandable quality.

All users must be able to visualize **quickly, accurately, and completely** what is happening. Use one authoritative scientific state with task-oriented, progressively detailed views, not five divergent scientific pipelines. Expose raw measurements, uncertainties, detector maps, trends, configuration, provenance, logs, and decisions. Guided, operational and scientific-inspection presentations are complementary, selectable modes.

## AR-QC.02 — Individual raw-frame QC at ingestion

Each ingested raw bias, dark, flat, or science exposure should receive a persistent individual QC profile before eligibility decisions and master-calibration construction. Preserve exposure and detector identity, metadata, integrity, statistics, image structure, anomalies, reference comparisons, and provenance. Support contextual inclusion, flagging, review, and logical exclusion from a particular processing group. **Never modify or delete original raw inputs**; record reasons, authorship, and reversibility. Distinguish anomalous behavior from scientific unsuitability and final acceptance. Individual raw-frame QC should precede master-calibration selection, not merely inspect the resulting master.

## AR-QC.01 — Historical instrument characterization

A future work package should retrieve and characterize large collections of historical **raw** OmegaCAM and WFI calibrations from the ESO archive, using existing masters and ESO QC records as complementary reference evidence. Construct versioned, configuration-aware baselines for bias, read noise, flat structure, detector defects, gain/linearity where appropriate data support it, and temporal changes. Preserve detector/amplifier, readout mode, filter, epoch and intervention metadata; do not pool incompatible populations. Compare observatory certification, independently measured historical baselines, and project-specific fitness-for-purpose separately. WFI and smaller observatories with minimal QC need provisional baselines and explicit confidence/coverage limits. Anomaly detection is not equivalent to rejection. Historical acquisition and model implementation are deferred, not prerequisites for M5.

## AR-EDU.01 — Educational scientific processing

Wenu-imaging should be an educational platform for non-experts as well as professionals. Every major operation should support practical (what happened/next action), scientific (why/meaning/limitations), and technical (algorithm/parameters/provenance) explanations. Use real data, diagnostic images and plots, with progressively disclosed detail and no concealment of uncertainty or anomalies. The core educational material and processing must work offline without an AI service.

## AR-EDU.02 — Example-driven Practical Guide

Provide an old-fashioned, readable **Practical Guide**, organized around complete runnable examples rather than a feature-by-feature manual. Each chapter should get a newcomer to a useful result quickly, with a real downloadable/example dataset, reproducible procedure, expected results and tolerances, what to inspect, typical problems, and contextual links to theory. Complement this with a Scientific Background resource and precise Technical Reference. Candidate examples: first calibrated image; raw-frame inspection; master bias; anomalous flat selection; WFI and OmegaCAM reductions; detector anomalies; science QC; optional Phase 3 preparation. Keep guide examples versioned and, where practical, regression-tested.

## Workflow and evidence requirements to assess

- Installation: structured platform/dependency diagnostics, validation and recovery guidance.
- Project setup: declarative validated configuration, instrument metadata, calibration associations, distinct reduction profile / processing recipe / product profile.
- Execution: machine-readable progress/events, persistent run state, resource usage, errors, retry/recovery, audit trail.
- QC: detector-level measurements, thresholds, comparisons, trends, visual diagnostics, human decisions and overrides.
- Products: science quality and provenance, independent Phase 3 conformance checks, manifests and human-approved external submission.
- Interfaces: CLI/Python and potential GUI/agent adapters over stable scientific operations; do not make numerical calculations depend on an LLM.

## Review deliverables and non-blocking policy

1. Inventory existing versus partial versus missing interfaces, with repository evidence and explicit uncertainties.
2. Trace requirements to current Pycavi/mefpp/WAD/QC architecture and M5–M11 boundaries; distinguish already approved contracts from exploratory proposals.
3. Identify low-cost preservation of metadata, status, diagnostics and stable identifiers when related code is already being touched; defer larger changes.
4. Produce a future implementation sequence only after review and owner approval.

**Not authorized by this document:** implementation, schema freeze, new mandatory M5 gate, changes to numerical behavior, installation, test replay, data retrieval, historical QC survey, AI/dashboard construction, Phase 3 submission, or merge into main.

## Related architecture

- [Architecture index](../README.md)
- [Current proposed implementation plan](implementation-plan.md)
- [WAD and processing projects](wad-processing-project.md)
- [Proposed Pycavi/mefpp architecture](pycavi-mefpp.md)
- [Current mefpp architecture review](../../developer/mefpp-architecture-review-2026-11-01.md)
