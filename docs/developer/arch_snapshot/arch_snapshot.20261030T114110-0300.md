# Architecture snapshot — wenu-imaging

Recorded: 2026-10-30T11:41:10-03:00 (America/Santiago).
Filename uses the ISO 8601 basic timestamp form.

Source baseline: `0160ed181cd1e609f5e82cfab7932763b228f698`.
This is the as-is merged repository, based on direct source and CMake inspection,
not the proposed target architecture. Blue boxes identify the new components.
The snapshot is historical; future changes should produce another dated file.

## Ordinary reduction path

The first diagram shows the ordinary reduction path built from this source.
Installed binaries have not been replaced during these increments.

```mermaid
flowchart TD
    subgraph PY["Pycavi2 — Python orchestration"]
        CFG["Project and instrument CFG"]
        PART["PartitionsTree and reduction wrappers"]
        ARENA["Partition directories, PAF, lists and links"]
        CFG --> PART
        PART --> ARENA
    end

    subgraph NATIVE["mefpp2 — ordinary serial executable"]
        CLI["mefpp.c: CLI and mef_bb configuration"]
        ENGINE["mef_engine: serial detector processing"]
        COMMON["mefp_lib.c: calibration, scan and output helpers"]
        KERNEL["NEW: shared bias-stacking kernel"]
        ECL["Embedded Eclipse"]
        QF["Bundled qfits5"]
        CLI --> ENGINE
        ENGINE --> COMMON
        COMMON -->|"bias stacking"| KERNEL
        KERNEL --> ECL
        COMMON --> ECL
        ECL --> QF
    end

    ARENA --> CLI
    DATA["Raw and calibration FITS"] --> ENGINE
    COMMON --> PRODUCTS["Calibration and preprocessed science FITS"]
    PRODUCTS --> POST["Pycavi normalization, WCS and later processing"]

    classDef added fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#111827;
    class KERNEL added;
```

## Implemented opt-in and authoring components

The remaining new components exist alongside that path. Arrows below show
implemented relationships, not future integration.

```mermaid
flowchart TD
    subgraph OPT["mefpp2/ins/mef/common — opt-in native components"]
        LEG["NEW M1: legacy PAF and CLI capture adapters"]
        INPUT["NEW M1: file/list request adapter"]
        CONFIG["NEW M1: immutable mef_config"]
        REQUEST["NEW M1: owned requests and calibration/BPM selections"]
        CONTEXT["NEW M1: context, result and error ownership"]
        BIAS["NEW M1: bounded mef_cal_bias service"]
        SHARED["Shared bias kernel from first diagram"]

        LEG --> CONFIG
        INPUT --> REQUEST
        CONFIG --> CONTEXT
        REQUEST --> CONTEXT
        CONTEXT --> BIAS
        BIAS --> SHARED

        TOML["Native TOML versions 1–3"]
        READER["NEW M2: parser, field catalog and subset composition"]
        DOCUMENT["NEW M2: owned settings and source records"]
        TOML --> READER
        READER --> DOCUMENT
        DOCUMENT -->|"contains"| CONFIG
    end

    subgraph AUTHOR["docs/architecture/proposed/m2/project-contracts — Python validation"]
        PROJECT["Project TOML, profiles and readout declarations"]
        VALIDATOR["NEW M2: closed authoring validator"]
        FROZEN["NEW M2: frozen declarations, source text and hashes"]
        PROJECT --> VALIDATOR
        VALIDATOR --> FROZEN
    end

    VALIDATOR -.->|"reads complete version-3 reference; no C call"| TOML

    classDef added fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#111827;
    class LEG,INPUT,CONFIG,REQUEST,CONTEXT,BIAS,READER,DOCUMENT,VALIDATOR,FROZEN added;
```

## Source locations and actual status

| Element | Actual location | Current status |
|---|---|---|
| Shared bias kernel | `mefpp2/ins/mef/common/mef_bias_kernel.c` | Used by both the ordinary bias builder and the new bias service |
| M1 configuration, requests and bias service | `mefpp2/ins/mef/common/mef_config.c`, `mef_runtime.c`, `mef_*request.c`, `mef_cal_bias.c` | Built through opt-in test targets |
| M2 native TOML reader | Same directory: `mef_config_toml.c`, `mef_toml_bundle.c`, `mef_config_domains.c` | Implemented and tested; ordinary `mefpp` does not load it |
| TOML parser | `third_party/tomlc17`, with private `mef_toml_bridge.c` | C99 parser boundary; surrounding native code stays C90/C17 |
| Project/readout validator | `docs/architecture/proposed/m2/project-contracts/validate_project.py` | Standalone Python validation; no reduction launch |
| Optional overscan and header rules | Project catalog/examples and `docs/architecture/proposed/overscan-readout-policy.md` | Configuration validation implemented; numerical adaptation remains ahead |

The build separation is explicit in
[CMakeLists.txt at the baseline](https://github.com/fselman/wenu-imaging/blob/0160ed181cd1e609f5e82cfab7932763b228f698/mefpp2/CMakeLists.txt):
`MEFPP_BUILD_CONFIG_PROBES` defaults to **OFF**. Bundled qfits is physically under
`mefpp2/qfits5`; the earlier sibling layout is historical.

The project validator currently preserves separate reduction purpose, ordered
recipe and product requirements, plus amplifier-specific overscan declarations
and unverified header evidence. Its snapshots explicitly say **execution is not
ready**. There is no operational ASDF project store, Python-to-native service
binding, or general numerical dispatcher connecting these new components to
ordinary reductions yet. The metadata-only `mef_execute` returns unsupported;
the concrete bounded bias service is called separately through `mef_cal_bias`.

## Inspection evidence and limits

Source anchors checked at the baseline:

- `Pycavi2/pycavi/pycavi/pycavi_associate_reduction.py`: PartitionsTree,
  reduction wrappers, PAF staging, subprocess launch and science normalization.
- `mefpp2/CMakeLists.txt`: normal executable/library graph and default-off
  opt-in native targets.
- `mefpp2/ins/mef/common/mefp_lib.c`: existing bias builder calls the shared
  `mef_bias_stack` kernel.
- `mefpp2/ins/mef/common/mef_cal_bias.c`: concrete bias service uses that same
  kernel with its explicit input/context contract.
- `mefpp2/ins/mef/common/mef_runtime.c`, `mef_config_toml.h` and
  `mef_input_request.h`: ownership, unsupported general dispatch and adapter limits.
- `docs/architecture/proposed/m2/project-contracts/validate_project.py`:
  Python-only frozen authoring records, explicit readiness/validation statuses.

This snapshot records source organization and implemented calls/build relations.
It is not a new processing run, deployment, hardware/readout validation, numerical
qualification or full M2 acceptance. Preserve the existing paired results and
private evidence; no native test replay is required to save this document.
