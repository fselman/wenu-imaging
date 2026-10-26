# Chapman3 native installation and CN Ori acceptance — 26 October 2026

Evidence attribution: Fernando's returned Chapman3 terminal reports. The agent
did not access the target files directly. Tested native source:
805e6c63dea20e7f5e5ade816f6a6ddc90702d86. This documentation update changes no
production source or installation.

## Installation and failure behavior

Both explicit C90 and C17 builds previously passed the required M_PI/shmget
checks, 100-unit builds and all five CTest entries per mode, using existing
devtoolset-10 GCC 10.2.1 and qualified CMake/CTest 3.29.6 on CentOS 7/glibc 2.17.
Both complete runtime payloads were then installed with cmake --install --prefix
into fresh private prefixes under:
`/home/fselman/Software/build/wenu-imaging/chapman3-installed-xogkdst_`.

Each installed payload matched every manifest hash. Ten installed native
failure-contract methods passed per mode, including explicit/missing/invalid
PAF, CLI/satmax, required keys, split inputs and checked write/publication failure.
Payloads stayed unchanged. Record: `installation-check.json` in that directory.
Normal engine selection and the working Python installation were preserved.

## Direct native observational comparison

Fixture work:
`/home/fselman/Software/build/wenu-imaging/chapman3-cnori-native-r3uhi3ax`.

Independent copies of raw science, prebuilt master bias/master flat, BPM and
original PAF were staged for:
- NB_659: OMEGA.2017-03-11T01:48:00.279.fits, 480 s.
- r_SDSS: OMEGA.2017-03-11T02:14:43.394.fits, 80 s.

Each private engine ran each exposure serially at niceness 10 in separate run
directories, referencing only the staged input copies. All four exits were zero;
each output was 1,070,553,600 bytes. No Python normalization was called.
References were the retained pre-normalization backups, not subsequently
normalized pilot science files. Their hashes matched the backup manifest:
- NB_659: 5586babdb1efa1b0223e3e0068f19964afccbc51b9d355225a9fd17bdaf03b06.
- r_SDSS: 8cab5dbb44da99ee983ae892fe90115e0eec3aa09e703e8a2dc2453e787823d2.

All 32 detectors in all four comparisons matched in identity/order, shape
(4091, 2044), stored dtype and scaling. Every pixel was exactly equal and
finite; unequal count, nonfinite count, maximum absolute difference and RMS
were zero. All raw header differences were in the primary HDU, limited to
ORIGFILE and MJD-END. Generated ORIGFILE names carry the new processing time.

## MJD-END review and remaining #24 scope

Both candidate modes agree with the independent decimal calculation
MJD-OBS + EXPTIME/86400 at the eight-decimal-day output precision:
| Filter | Raw MJD-OBS | Candidate MJD-END | Error against independent arithmetic |
|---|---|---|---|
| NB_659 | 57823.075003233 | 57823.08055879 | +0.0001248 s |
| r_SDSS | 57823.093557795 | 57823.09448372 | -0.0000800 s |

Historical values 57823.07812500 and 57823.09375000 exactly match a binary32
simulation. These explain historical-to-candidate shifts of 210.279456 s and
63.393408 s; they are not processing timestamps. The candidate science recipe
already declares exptime/mjdobs/mjdend as double; this qualification makes no
new arithmetic change. This is a reviewed historical metadata difference.

Issue #24 stays open: mef_header_esophase3 in common/mefp_lib.c still declares
the corresponding variables as float. These science-only checks do not qualify
calibration-product timing or close the ticket's short/long exposure criteria.

Retained records in the fixture work directory:
- fixture-record.json: original/staged inputs and reference identities.
- native-run-record.json: four commands, outputs, engine hashes and statuses.
- native-output-comparison.json: complete detector and raw-card differences.
- mjd-end-review.json: decimal arithmetic, float simulation and source evidence.

All recorded original/staged inputs, references, candidate outputs and installed
payloads remained unchanged during the applicable checks.

## Permanent tools, workspace and relocation

Fernando requested builds beneath ~/Software/build/wenu-imaging/ and permanent
reusable tools beneath ~/opt/. CMake and CTest 3.29.6 are now verified at
`/home/fselman/opt/cmake-3.29.6/bin/{cmake,ctest}`. System CMake and PATH were
unchanged. Qualification records/downloads remain under
`~/Software/build/wenu-imaging/tools/wenu-cmake-3.29.6-check-h4i7yr9s/`;
permanent-tool-relocation.json records the final distribution move and hashes.

Thirty retired home runs and then the completed native retry were moved
reversibly, preserving evidence, under
`~/Software/build/wenu-imaging/archive/home-runs-20261026-p7gyr1zh/`.
relocation.json and final-home-relocation.json map old paths to new paths.
No ~/wenu-* entries remain. Archived CMake trees/virtual environments retain
historical absolute paths and must not be executed as current builds.
The original native retry now resides in that archive; its build-check.json,
logs and source exports remain evidence. The failed 579kejl8 attempt is there
too. No Git branch cleanup occurred.

## Next acceptance gate and limits

Next: export the pinned Python source, build/install its wheel without dependency
downloads into a fresh target under the workspace, verify installed imports and
run the five wrapper failure regressions. Then exercise the actual installed
Pycavi science wrapper with the corrected engines on isolated inputs and compare
the resulting pixels/headers. Do not replace the normal package or engine.

This accepts bounded Chapman3 native build/install/failure/direct-science behavior
with prebuilt calibrations. Installed corrected Pycavi on Chapman3, calibration
construction, broader ownership/memory, WFI observations, other platforms and
independent scientific/Phase 3 gates remain open. No merge, release, normal
selection switch or further production processing is implied.
