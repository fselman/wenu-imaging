# tomlc17 — bundled upstream source

This directory vendors the unmodified tomlc17 C parser maintained by CK Tan:
https://github.com/cktan/tomlc17

Pinned revision: `4987cf895df61f702d19e3481f34b032ab29ed3a`.
License: MIT; retain [LICENSE](LICENSE) and the source copyright notices.
[upstream.json](upstream.json) records exact original paths, SHA256 hashes and Git blob identities. No local patches are applied.

The owner approved vendoring on 29 October 2026 after private Mac/Chapman4 qualification. The two source files and license are byte-identical to both tested copies. A checkout includes the dependency source; building it will not require a separate tomlc17 installation or download.

## Integration boundary

M2 now provides an opt-in private static C99 target and parser-specific shim through the configuration probes. See [the compatibility-reader contract](../../docs/architecture/proposed/m2/native-compatibility-reader.md). Neither is linked into normal mefpp or installed; actual paired integration acceptance and full M2 composition remain pending. Existing numerical code and public native contracts retain the C90 baseline. tomlc17.h exposes C99 types and must stay out of C90-facing public headers. The private shim exception is explicit in that contract; core mapping and public internal headers retain C90. Production activation remains a later reviewed integration.

The parser supports TOML 1.1; the initial Wenu configuration language uses the TOML 1.0 subset shared with Python 3.11 tomllib, with explicit C-compatible integer/domain bounds. Adapter validation must enforce the selected contract. Enable UTF-8 checking explicitly: the upstream default is false. Set parser/allocator options once during initialization before any worker activity; this qualification does not establish concurrent parsing safety.

See [qualification evidence and limits](../../docs/developer/native-toml-qualification-2026-10-29.md): Intel Mac/Apple Clang 15 and Chapman4/GCC 10.2.1, strict-C90 caller boundary, bounded parser agreement and allocator-hook cleanup/failure controls. Other hosts, sanitizer/all-process memory coverage, full conformance and reduction correctness are separate qualifications.

## Updating

Keep upstream source unchanged and put Wenu-specific code outside this directory. To update, select an exact upstream revision, review source/API/license changes, verify identities, repeat the relevant bounded Mac/Chapman qualification, and update the three upstream files plus upstream.json together. Do not track upstream main automatically. Preserve prior qualified identities and evidence. Any local patch must be explicit, documented and separately tested; the current import has none.
