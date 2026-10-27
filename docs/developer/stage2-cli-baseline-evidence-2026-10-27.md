# S2-03 failed Mac baseline — 27 October 2026

Actual source: test/stage2-cli-ownership at
753f106fb6ea85a7cee68ff6e4ffa92bda59bfdf (clean). The complete matrix ran:
224 case pairs / 448 native invocations. **Memory gate failed.**

| Lane | Case pairs | Passed | Findings |
|---|---:|---:|---:|
| C90/C17 ASan/UBSan, OCAM/WFI | 112 | 12 | 100 |
| C90/C17 uninstrumented leaks/accounting, OCAM/WFI | 112 | 112 | 0 |

Each of the 100 failing pairs has the same ASan global-buffer-overflow at
`src/unix/getopt.c:219`, in both ordinary and observer logs (200 logs). The
unbounded-to-string comparison uses the input option length in `memcmp` against
each registered name. A longer input such as `--version` reads beyond shorter
registered strings such as `help`. No separate UBSan diagnostic was recorded.
This is #103, distinct from the already corrected configuration-selection #76.
The affected cases stop before their intended ownership boundaries; their
absence of an observer completion marker is correctly a failure.

The 12 instrumented passes are help/license/no-arguments in both standards and
instruments. All 112 uninstrumented pairs have the expected ordinary native
status/diagnostic, observer constructor/destructor contract, zero initial/final
qfits accounting and zero unreachable blocks/bytes from `leaks`. These do not
override the invalid read demonstrated by the instrumented lane.

Apple Clang 15.0.0.15000100, CMake 3.29.3, x86_64 and the recorded Xcode SDK;
four Debug builds, qfits mode 2/max pointers 2000000. Instrumented flags are
`-O0 -g -fno-omit-frame-pointer -fsanitize=address,undefined
-fno-sanitize-recover=all`; the separate leaks lane omits sanitizer flags.
Full commands/environment and tool/source identities are in the retained report.

Original Mac directory:
`~/Software/build/wenu-imaging/mac-stage2-cli-baseline-6nw2zx0_/`.
Uploaded archive: `mac-stage2-cli-baseline-evidence.tar.gz`, SHA256
`96f4dc40ac0671f8ffd0166899ae266aba55a8e94071e1791bf32eb1bd1b29c1`.
Persistent attachment identity: `libfile_c44da74e0e60819188c880dfb7b3848c`.
All 890 file identities verified; all 448 original native logs inspected for
diagnostic classes, all passing ownership/accounting contracts checked, all
11 retained source hashes matched the prepared source, and four build records
inspected. The archive contains the 889 hashed files plus its transfer manifest.
Retain the original full run and archive; committed reports are an index, not
a replacement for the original logs.

The report confirms source/export/checkout and protected configuration/selected
engine hashes unchanged. No installation or observational processing occurred.
The bundled getopt source itself was not copied into the transfer archive;
its identity is reproducible from the exact tested Git commit and build source
inventory. A corrected runner must explicitly include it in its source manifest.

Next: a separate bounded #103 correction and fresh qualification retaining the
same 224 CLI/PAF case definitions, with parser matching regressions. S2-03, #75
and Chapman3 correction verification remain open. No numerical or allocator
policy change, normal installation switch or image reduction is required.
