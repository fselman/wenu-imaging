# S2-05 supplied-bias Mac evidence inspection — 28 October 2026

Both full evidence sets were independently inspected. The diagnostic run passes
its declared suite; the original descriptor mismatch is confirmed but cannot be
attributed from that older observer. #116 remains open, as do full S2-05/#75.
No target advance, gate waiver, merge/deletion or installation change follows.

## Archive identity and retained records

Original transfer archive:
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-bias-transfer-lkvr01p0/mac-bpm-bias-both-runs.tar.gz`.
SHA256 `dbe6ba9429abd33e7fafe1619db79404b5343b455f67deae5bd8bd100a02082b`.
Persistent attachment `libfile_67921576ba2c8191b1c10ea6c6ae6eae`.
All **823 member file identities plus the transfer manifest** are verified;
membership is exact and every archived file matches the manifest hash.

Original failed run:
`~/Software/build/wenu-imaging/mac-stage2-bpm-bias-zutw0_xe/`, tested clean
`e7e8fbdcff5af70bdcb4ea8d5521efe4a030e62f`.
Diagnostic run:
`~/Software/build/wenu-imaging/mac-stage2-bpm-bias-w21bs79o/`, tested clean
`c49123908c9a401eee41cccf006b6cf2d1f75b78`.
Both remain preserved with their sources, builds, binaries, outputs and logs.

Full reports, eight build identities, the two implicated observer logs, transfer
manifest, verification script, results and inspection provenance are committed
under `fixtures/mac-stage2-bpm-bias-inspected-2026-10-28/`. The persistent archive
retains the complete transferred evidence. The verifier's original absolute
scratch/source paths are inspection provenance, not a user launch command.

## Independently verified scientific and build contracts

Across both runs, all **64 native roles / 32 pairs** reproduce every accepted
returned/saved mask pixel: 79 good / 2 bad, binary polarity, 9x9 geometry,
unsigned BITPIX=8, no scaling and unchanged 0.5–1.5 bounds/QC counts. There are
10,368 individual returned/saved mask pixel comparisons. Independent Astropy
readback and the retained output oracle agree with the accepted reference.

All canonical primary/extension cards, order/comments, first-frame metadata and
extension identity agree with accepted populated-metadata references. Raw output
hashes are verified; generated ORIGFILE values remain separately recorded. All
32 corresponding ordinary/observer canonical output dictionaries are identical
between the two runs. This is controlled-fixture equivalence, not independent
observational calibration quality or Phase 3 compliance.

All 192 staged frame checks establish exact float32 bias cancellation back to
accepted science pixels, unchanged overscan, raw populated headers and padding.
Bias pixels/type/layout and all declared input hashes match the retained fixture
manifest. All output hashes and actual archived executable hashes match reports.

All **94 command logs** match recorded hashes and exits are zero. Eight build
records and their compile-command inventories confirm declared C90/C17 modes,
ASan/UBSan versus separate uninstrumented leak lanes, allocator mode 2 and maximum
2,000,000 registrations. Private diagnostic CMake hashes match. Selected source
hashes match the exported files. The only selected-source differences between
runs are the test observer, qualification runner and added descriptor parser;
the ordinary driver, numerical sources and fixture bytes remain identical.
All six recorded preservation checks are true in both Mac run reports; this
inspection does not independently access the current Mac installation.

## Independently verified resource observations

All 32 observer context/mask contracts balance. All nine allocator boundaries
per observer agree with raw logs. Each run retains 20 RAM registrations / 158
bytes after driver return; the first public purge releases them. Both purges
and process-start have zero tracked RAM pointers/bytes, mappings/references and
swap bytes in all cases. No ASan/UBSan error is recorded. All **16 external leak
summaries** (eight per run) report zero unreachable blocks/bytes.

The original C90 instrumented retained/robust case alone has count 4 to 4 but
identity unequal at driver return and both purges. The original observer did
not retain individual identity fields, so its actual changed descriptor cannot
be recovered from these logs. No missing source/product or unexplained RAM
registration explains that separate descriptor finding.

The diagnostic run passes all **48 post-call descriptor boundaries** across 16
pairs. Raw per-fd details independently recompute all aggregate signatures and
match recorded JSON snapshots; no added, closed or changed entry occurs. In
the corresponding first case, fd 0 is the terminal, fds 1/2 share the log, and
fd 3 has socket type bits. The failed F_GETPATH for that socket is a path-lookup
observation, not evidence of closure/leak or proof that fd 3 caused the older
mismatch. No descriptor exclusion or relaxed gate was introduced.

## Current conclusion and next diagnostic boundary

The successful diagnostic suite is verified evidence. It does **not** identify
the original mismatch's cause, prove it harmless or close #116. Do not discard
the failed run, accept an implicit waiver or advance to Chapman3/S2-06 based
only on a later pass.

The next useful diagnostic would focus on the previously failing C90
instrumented retained/robust case using the already qualified binary and fresh
case directories, retaining raw descriptor identities on each attempt. Separate
process repetitions would investigate #116; they would not satisfy S2-09's
same-process lifetime gate. Do not repeat unrelated reductions or change the
allocator/scientific pipeline to investigate this observation. If it remains
unreproduced, present that limitation and the evidence for review rather than
inventing an attribution or weakening completion criteria.

All broader S2-05/#75, WFI/multiple extensions, applicable shared-helper/error/
repeat/cache/mmap/swap and target external diagnostic obligations remain open.
Mandatory review before Stage 2A/extraction and early Phase 3 requirements work
remain in force. No native execution occurred in this agent inspection.
