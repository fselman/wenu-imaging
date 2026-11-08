# Bias human readability pass

Owner-approved scope, 8 November 2026, issue #292. The owner accepted the permanent policy in PR #291 and instructed applying it to the bias recipe and routines, with source comprehension review before acceptance.

Start from native producer b833aca7 and policy main 165d02d. Cover the recipe coordinator; bias service, admission/stack kernel and file adapter; recipe envelope parser and QC serializers; and only the shared row-scan correction routine reached by bias. Preserve the rest of the legacy implementation and dependency libraries. Use clear domain names, one statement per line, explicit braces, logical paragraphs, direct option handling in place of a flow-hiding macro, sparse scientific-stage landmarks and short intent/ownership comments. Retain existing function/ownership boundaries in this first pass unless a concrete extraction clearly improves reading. No gratuitous wrappers or new framework.

Preserve all numerical expressions and evaluation order, conversions, zero-spread refusal, strict endpoints, median modes, mask/finite populations, RON estimators, ownership/cleanup, error messages, command/configuration interfaces, FITS/ASDF schema/cards, filenames and publication order. This is a readability change, not permission to improve algorithms or silently fix unrelated findings. Keep formatting/naming work identifiable independently from any future scientific change.

Provide a reading map and source-file/routine/landmark references in the existing LaTeX mathematical guide and compiled PDF. Align historical guide wording with already accepted average/lower median and zero-spread behavior; do not create a new policy. Labels remain sparse, unique and independent of source/document numbering.

Qualification: token/evaluation-order comparison against the qualified source (allowing explicit renames, braces and macro expansion), strict C17 syntax/build checks, existing synthetic service/legacy exact pixel/QC and lifetime/failure contracts, affected configuration/QC/file checks where available, and a bounded selected-Mac recipe comparison using tiny synthetic inputs when needed. Preserve existing selected build/cache/tools and qualified binary; no fresh Mac export/reconfigure by default, observational replay or installation. Generated producer stamps must describe the actual built source. Human source comprehension remains a separate pending owner acceptance gate.

Linearity remains paused. No merge of the readability implementation is authorized by approval to prepare it.
