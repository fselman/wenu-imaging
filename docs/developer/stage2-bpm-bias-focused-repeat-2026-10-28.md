# Focused fresh-process diagnostic for #116 — 28 October 2026

Status: prepared, actual Mac execution pending. Continue the original S2-05
descriptor investigation after inspecting both full Mac runs. No scope/gate
departure, target advance or S2-09 acceptance.

## Purpose and fixed workload

Attempt to reproduce the original same-count descriptor mismatch in ten fresh
processes of only `c90-instrumented-retained-flag0`. Use the existing inspected
Mac C90 ASan/UBSan observer binary from
`~/Software/build/wenu-imaging/mac-stage2-bpm-bias-w21bs79o/`.
Binary SHA256 `b89332ba536ee53e51ef13273cab88f515f0e09b46b94a8c58a903310bed3820`;
reference report SHA256
`eb7b590cd4993ecfb72224e51da2093da179d3be7fdd8299099f5d26f8539df5`.

`repeat_bpm_bias_descriptor_case.py` does not build, install, patch native code,
change fixtures/algorithms or reprocess observations. It calls the same actual
production-linked observer once per fresh input/output directory. Native path
remains image_load -> mef_build_bpm -> load/overscan/trim/subtract bias -> robust
regression -> normalize/threshold/save, followed by caller mask/bias/context
release, descriptor observations and two public cache purges. No Pycavi routine
is invoked. The full 16-pair suite and external-leaks results remain retained;
this narrow instrumented diagnostic does not replace them.

## Section correspondence and contracts

- Guards: require the actual Intel Mac, `/Users/fselman/anaconda3`, clean checkout
  and niceness >=10. Limit core dumps, preserving all original runs.
- Reference/binary protection: compare both local and committed inspected report
  hashes, actual existing executable hash, all 35 qualified source/fixture hashes
  and selected installed engine/configuration hashes before workload. Record the
  current orchestration commit separately from the binary's native c4912390 source.
- Retained provenance: create a new
  `~/Software/build/wenu-imaging/mac-bpm-bias-descriptor-repeat-*` root and fresh
  attempt directories, with manifests before staging/processing. Never reuse
  either original run. Retain failed/interrupted attempts and command logs.
- Environment: remove the same inherited diagnostic/injection variables as the
  accepted runner; apply its exact ASan/UBSan settings, E_DEBUG/E_VERBOSE=0 and
  retain declared thread limits. Record actual parent niceness and lane settings.
- Staging/native processing: stage exact deterministic retained fixture inputs,
  verify their six hashes, run the qualified observer with proportional flag 0
  in ten independent processes. Each attempt has a separate log and outputs.
- Output/resource verification: require exact accepted masks/canonical metadata,
  actual native/borrowed-bias/context completion, native exit, no sanitizer error,
  all nine accounting boundaries, process-start/both-purge zero resources, both
  descriptor-limit observations and all original count/identity gates. Parse raw
  per-fd snapshots before reporting findings; retain exact changed entries even
  when another gate fails. Continue all ten attempts to retain attribution data.
- Preservation/final status: recheck sources, checkout, original binary/reference
  and protected installation/configuration. Report attempt and descriptor-change
  counts without calling nonreproduction a new qualification pass or closing #116.

## Preparation evidence

Five unittest methods cover balanced observations, nonzero exit, sanitizer
messages, missing/live resource observations, incomplete snapshots/owners and
same-count inode replacement with explicit attribution. Python syntax passes.
The new reader accepts all 16 retained diagnostic observer logs and rejects the
older implicated log's missing snapshots/failed original gates. The inspected
reference and actual archived binary hashes match both hard-coded pins; all 35
qualified source identities match the unchanged current checkout. These are
agent readback/control checks, not new native Mac execution. Logs, hashes and
preparation provenance are retained under
`fixtures/agent-stage2-bpm-focused-preparation-2026-10-28/`.

## Handoff and interpretation

After guarded synchronization, launch with existing Python, `nice -n 10`, thread
caps and `--reference` pointing to the preserved w21bs79o run-provenance.json.
No compiler/SDK/CMake selection or installation is needed. Inspect the new report
and raw logs; retain all ten case directories and both previous full runs.

If the mismatch recurs, use exact changed fields/targets to investigate the owner
before proposing a bounded correction. If it does not recur, report ten attempts
without reproduction and keep the original cause unresolved. Do not retry
indefinitely, whitelist descriptors or infer harmlessness. Separate-process
repetition does not qualify S2-09's same-process lifetime behavior. #116, full
S2-05/#75 and target/external-diagnostic obligations remain open; no S2-06 advance,
merge/deletion or Stage 2A/extraction follows automatically.
