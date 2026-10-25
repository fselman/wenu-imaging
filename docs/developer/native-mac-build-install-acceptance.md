# Intel Mac native build/install acceptance — 25 October 2026

Status: bounded build/resource/private-install acceptance passed, reported by
Fernando on MC02VV0HPHTDG. This is not observational equivalence or complete
Stage 1 acceptance.

Qualified native source: 41c8e6a544c1bc5122dc558e0c8cc7904214e1d0,
draft PR #81, branch fix/native-cmake-build. The acceptance documentation commit
does not change the native source tree. Main and the selected historical engine
have not been updated.

## Actual target and records

Intel Mac macOS 13.7.8 x86_64; established wenu-imaging Python environment.
Explicit active Xcode clang/ar/ranlib/ld and SDK, Unix Makefiles, CMake/CTest
under /opt/local/bin, /usr/local/bin/funpack, serial build/test execution and
niceness >=10. Earlier tool inventory identified Apple Clang 15 / CMake 3.29.3;
the retained build records identify the actual selected tools and configuration.

Records: /Users/fselman/wenu-mac-c17-inline-qj56jko6.

- started.json, source.tar, configure/build/ctest logs for C90 and C17.
- output-check.json: successful corrected C17 build/test.
- resource-and-c90-check.json: corrected C90 build/test and both resource comparisons.
- bpm-header-comparison.json: complete ordered header-card comparison.
- installation-check.json: private installed-file hashes, manifest, repeated
  installation, architecture/CLI checks, staging and preservation.
- Dependency and installed-CLI logs for both language modes.

Evidence is Fernando's returned command output from his actual Mac, not an agent
rerun or independent access to that filesystem. The full local JSON records and
logs remain on the Mac; unreported binary hashes are not invented here.

## Passed scope

Both modes compiled 100 translation units: 18 qfits, 79 Eclipse, MEF/common,
recipe and test. Every compile command selected the requested C90/C17 mode.
Three nonempty CTest entries passed per mode:

1. native_primitives: image_new/image_getmean/image_del, qfits_paf_query,
   qfits_pixdump_float/qfits_pixin_float, C17 inline-keyword guard and ctype/math
   integration through toupper/fabs.
2. native_cli_usage: mefpp without arguments reports usage and nonzero status.
3. native_install_contract: seven synthetic cases for complete/repeated install,
   staging, external ancestor aliases, linked prefixes/internal paths,
   missing resources, conflicting parents and edited-file preservation.

Both distributed masks were decompressed, opened with Astropy and compared
pixel-by-pixel with their compressed sources. OCAM has 32 image HDUs; WFI has 8.
Shape, dtype and extension names match; all output pixels are finite and exact.

| Resource | Compressed SHA256 | C90 uncompressed SHA256 | C17 uncompressed SHA256 |
|---|---|---|---|
| OCAM_BPM_1x1 | 297dbd539f29a0c039e285178ae8668968fa0d3fa8d1bff4dea41fe7ee08f356 | ccbb5896730746198211683e64b972a01e7178c6889e2b630312cff163af8e6b | 040cfb98de27db1c335cbcb39579d6ab43925a2430d8d983c28e17ad3de447a1 |
| WFI_BPM_1x1 | 21bb2e8095a6b45143d5ede96eee2b75841c0bf507b54447bba8869b0f0c6269 | e954ebd2bb1718c2cc68f36a91965a8c6eba8619dc73247b197d8cde3f58846a | 0fe2aa63c28f7d942dcb240edc91f983fbd527f5ce830872417b1f410aca9435 |

Whole-file mask hashes differ between modes because funpack updates CHECKSUM/
DATASUM cards and timestamp comments at different execution times. The complete
comparison checked that all 64 OCAM and 16 WFI differing cards were these two
keywords, with unchanged DATASUM values. Actual FITS checksum/datasum verification
passed. This is exact pixel/resource-content equivalence, not byte-reproducible
decompression; retain each actual file hash in its installation provenance.

Real private prefixes:
- /Users/fselman/wenu-mac-c17-inline-qj56jko6/prefix-c90
- /Users/fselman/wenu-mac-c17-inline-qj56jko6/prefix-c17

Each contains the exact promised runtime files, matching the corresponding build
and installed manifest. Source revision/language mode, generated-header hashes,
permissions and installed-file hashes were verified. Repeated installation was
byte-identical. Installed binaries were Mach-O x86_64, with only system dynamic
dependencies, and no-argument usage worked outside source/build directories.
C17 DESTDIR staging passed, with its runtime prefix retained in provenance.

Historical engine, saved Pycavi configuration and checkout were unchanged;
neither private engine was selected for normal processing. No observational
processing, normalization, query or scientific validation was performed.

## Defects and boundaries

- #80: seven recipe line comments converted to C90-compatible block comments;
  executable-token preservation review and actual Mac C90/C17 compilation/tests passed.
- #82: normal /var ancestor alias was wrongly rejected. Ancestors outside the
  prefix are resolved; linked prefixes/internal payload links remain rejected.
  Seven cases and real repeated/staged installation passed.
- #83: legacy empty inline macro affected C17/system-header linkage. The fallback
  is now pre-C99 only. The regression detects the old header under agent C17;
  actual Mac C17 linking/tests now pass, with renewed C90 checks.

These bounded defects have verified corrections on draft #81; the draft is not
merged. Existing native algorithm, status/cleanup, warning and version issues
remain separate.

## Remaining gates and next step

Prepare the retained CP Pup native observational anchor for comparison of both
private candidates against the historical native output. Recheck input/master/
PAF/engine hashes and exact command settings before launching any reduction.
Keep native output separate from Python normalization. Compare all detector
pixels/metadata with the agreed policy; do not equate a zero exit with acceptance.

Installed Pycavi wrapper, calibration-building fixtures, WFI reduction coverage,
native failure propagation, memory qualification and chapman3/toolchain acceptance
remain pending. A WFI BPM resource check does not establish WFI reduction support.
No normal engine switch, merge/cleanup, parallel runtime or scientific tuning is
authorized by publication of this record.
