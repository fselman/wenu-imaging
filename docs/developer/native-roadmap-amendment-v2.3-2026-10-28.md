# Approved amendment v2.3: BPM input provenance filenames

28 October 2026. Fernando explicitly instructed: "Let us do the mefp_lib.c correction and write as an issue the lack of CONTINUE capabilities in qfits, it should be fixed later."

This authorizes one caller-side metadata correction in mefp_lib.c::mef_build_bpm: pass get_basename(flist->name[i]) to the BPM FRAME### header insertion, consistent with bias/dome/sky. File loading continues to use the unchanged full path. Raw inputs, numerical calculations, expectations and thresholds are unchanged. No fits_h.c change, CONTINUE implementation or ASDF migration is included. General repair rounds remain 2/2; this separately approved correction does not reopen that budget.

The current Mac source 92421749d8350d9b6438d7b16014555a228f2c5f reportedly passes F1 ordinary, instrumented and external leaks. F2 ordinary exits -4 with two partial products. The 28 October 17:28:32 crash stack confirms __chk_fail_overflow -> __strcpy_chk -> keytuple2str, fits_h.c:1139. The exact val string was not captured. All F2 diagnostics and F3–F5 remain pending. Counters: 4 planned launches, 5 correction/exception retests, 9 actual launches; v2.2 is consumed.

Track the immediate correction as #126 and deferred qfits long-string/CONTINUE and unsafe formatting as #125. Caller correction does not make arbitrary long filenames or comments safe in qfits. Full input locations and hashes remain in existing manifests. No native runtime retry, new matrix, merge, deletion or installation is executed by this amendment. Prepare a guarded continuation of the stopped F2 as the next campaign handoff; do not replay accepted F1 merely for this metadata change or invoke the old F1-only resume guards with this new failure.

Agent C90/C17 syntax and twelve controls of the actual existing basename helper pass. The three selected BPM filename values fit their complete keyword/value cards (65 characters before comment). The helper preserves its input buffers. No engine runs on the agent; actual Mac F2 six-product/eight-extension and diagnostic acceptance remain pending. Evidence is in fixtures/agent-bpm-basename-correction-2026-10-28/.

Preserve all previous attempts, reports, archives, raw files, input locks, selected installations and the byte-identical frozen v2.0/v2.1/v2.2 files. The existing final C90 and compact Chapman3 C17/C90 checkpoints remain in place.
