# Shared mosaic normalization regression

Scope: #94, authorized by Fernando on 26 October 2026. This retains the
Mac-developed and Mac/Chapman3-qualified disposable fixture in regular CTest.
It changes no production numerical routine, calibration default or installation
selection. The focused test branch is stacked on acceptance documentation PR #93.

## Test contract

BUILD_TESTING adds shared_normalization_probe, linked to the actual
mefpp_common -> Eclipse -> qfits graph, plus four CTest entries:
native_shared_normalization_{dome,sky}_order{0,1}.
The previous five entries remain, so this configuration has nine entries.
The normal resource/install route is unchanged; make check includes the new
entries when built from this revision.

The unchanged C driver calls production mef_build_cal on four detectors and
three illumination levels. Each trimmed image is 9x9 with a doubled center
pixel and zero-valued overscan. Responses are [1,2,4,0.5] and [4,1,0.5,2].
Every returned pixel must equal its independent response/first-detector
expectation exactly. Thus one build checks 4 cases x 4 detectors x 81 pixels =
1296 pixels, and C90/C17 together check 2592.

This is not a PAF/CLI, nonzero-overscan accuracy, variance/covariance, independent
observational flat-quality, memory-safety or full pipeline test. Do not replace
the exact assertions with tolerances after a mismatch.

## Preserved origin

The fixture directory tests/fixtures/shared-normalization/ is imported
byte-for-byte from shared-normalization-mac-qualified.tar.gz, SHA256
16f0bba19bb09e2f3d8e8626b8f4c4d5d51c3b7d2aec9b29e9a84b8e8e2afa7a.
Its transfer-manifest.json verifies the driver, the original Mac report and
all eight FITS/list inputs. Driver SHA256:
65197f209c93326c331fa333520758ad49b0d44b497bbe2e3d19e021d54376ba.
The archive originated at source 2ace67a; imported historical reports preserve
their original absolute paths. The underlying native routines are unchanged
in the current integration baseline.

## Isolation and provenance

The standard-library Python launcher validates all transferred hashes, makes a
fresh per-attempt binary-tree working directory, copies the selected four input
files, invokes the production-linked driver, and checks that source/staged
inputs remain unchanged. Attempts retain native.log and run-provenance.json,
including failures and the executable hash. Tests can run concurrently without
sharing writable fixture files. No Astropy, NumPy, funpack or observational
input is needed to run these four cases.

For exports, pass both -DMEFPP_SOURCE_REVISION=<exact-SHA> and
-DMEFPP_SOURCE_BRANCH=<tested-branch> to CMake. Unknown source identities stay
explicitly null in the per-attempt records; the outer build record must capture
dirty state and any patches. The container record delegates individual results
to per-attempt records. Put all user builds under
~/Software/build/wenu-imaging/, preserve evidence before merge and retain the
qualified installations.

## Qualification status

Original disposable fixture: Fernando reported exact passes on Intel Mac and
Chapman3 in both language modes. This does not qualify the new CTest wrapper.

Agent Linux diagnostic: the unchanged driver compiled in explicit C90/C17 and
all eight cases passed through the new launcher, totaling 2592 exact pixels.
A corrupted FITS fixture was rejected before native execution. These checks
reused earlier native diagnostic objects/archives; no CMake executable was
available in the agent environment. They do not establish new CMake/CTest
integration or actual Mac/Chapman3 acceptance.

Intel Mac CTest integration is accepted at c5f2bac84e39918d0a82ac1e57769f6473be0828:
AppleClang 15.0.0.15000100, CMake 3.29.3, explicit C90/C17, nine tests passed
per mode and all 2592 normalization pixels matched exactly. The uploaded evidence
was independently checked against its 34-entry manifest, per-attempt log hashes,
recorded language flags and complete CTest logs. Protected selections and the
checkout stayed unchanged. No installation or observational processing ran.
See [preserved Mac evidence](fixtures/mac-normalization-ctest-2026-10-26/README.md).

Chapman3 verification of this CTest integration remains pending. Keep #94 open.
No new observations, normal installation switch, merge or cleanup is required.
