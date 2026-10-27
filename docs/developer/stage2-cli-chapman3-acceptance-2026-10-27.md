# S2-03 Chapman3 correction verification — 27 October 2026

Actual target source: fix/103-getopt-name-bounds at
4594aec1f3945ee3d48aff3f0d51093ab8418e56, clean. **Bounded target
functional/qfits-accounting gate passed.** Together with the inspected
[Mac correction acceptance](stage2-cli-mac-acceptance-2026-10-27.md), this meets
the declared #103 correction gates. The baseline/correction PRs #102/#104 remain
unmerged. #75, remaining Stage 2 rows and compatible target external diagnostics
remain open; this is not full Stage 2 memory acceptance.

## Actual checks and agreement

GCC 10.2.1, CMake 3.29.6, Debug C90/C17, `-O0 -g -fno-omit-frame-pointer`,
qfits mode 2/max pointers 2000000. No sanitizer flags or external leak tool.
The existing qualified toolchain and installations were preserved.

All **112 CLI case pairs / 224 native invocations** passed. Each ordinary CLI
has its declared exit/diagnostic; each observer has the expected actual recipe
return, successful-construction/destruction counts, matching owner identity
and no live context owner at return. Raw qfits accounting boundaries are zero
registrations/bytes before entry and after return, before atexit cleanup.

All argument lists, PAF hashes, exits, ownership contracts and final accounting
match the accepted Mac functional reference. All thirteen Mac-qualified source,
driver and fixture hashes match, including the corrected parser, observer,
focused parser probe and shared case/PAF preparation. Target orchestration is
separate and retained with its own source hash. Diagnostic CMake target wiring
is byte-identical to the Mac-qualified wiring.

The actual bundled parser also passed thirteen focused matching/argument
contracts per standard, **26 checks total**. Both original parser logs have
all individual passes and zero-failure completion records. No native source,
PAF fixture, parser expectation or observer adaptation was made on Chapman3.

## Retained evidence

Original target directory:
`~/Software/build/wenu-imaging/chapman3-stage2-cli-71v4syfj/`.
Target archive: `chapman3-stage2-cli-evidence.tar.gz`, SHA256
`f9afb0343e3a27cbe08926a009c568fe56bd1841a39ddfc6d0064111588e5482`.
Persistent attachment: `libfile_a4f7f82567948191912a60b0f1338f98`.
Mac transfer destination requested in the handoff:
`~/Software/build/wenu-imaging/mac-stage2-cli-corrected-92e328bc/chapman3-stage2-cli-evidence.tar.gz`.
The uploaded archive matches the target-reported hash exactly.

All **459 file identities** verified: 458 hashed files plus the manifest.
All 224 original native logs/statuses/diagnostics, raw accounting boundaries,
112 staged-input/reference mappings, two parser logs, source identities,
diagnostic wiring and both build records independently inspected.
Committed run/build reports and the full transfer manifest index the retained
originals; do not remove or overwrite the target/Mac run directories or archives.

The target report confirms sources/export/checkout, selected installed
engine/configuration and accepted reference report unchanged. No installation,
normal engine switch, image reduction or Pycavi execution occurred. Preserve
the invalid-read baseline and the stopped assertion attempt as well.

## Roadmap boundary

The bounded S2-03 CLI/parser/early engine ownership suite now has Mac diagnostic
acceptance and unchanged Chapman3 functional/accounting verification. The next
increment after integration is **S2-04 split I/O/publication ownership**.
Other calibration/science ownership paths, practical injection, repeated stages,
cache purge/mapped/swap coverage and target compatible sanitizer/leak tooling
remain open under Stage 2/#75. The early ESO Phase 3 audit remains pending.
Mandatory review still precedes Stage 2A representation work or extraction.
No new workload, merge or branch/run cleanup is authorized by this record.
