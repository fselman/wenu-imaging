# Chapman3 shared-normalization CTest acceptance — 27 October 2026

Refs #94, PR #95. Actual source: clean test/shared-flat-normalization at
dbdb0a47947577a46f854591a14e527570731fc0. This documentation-only successor
of the Mac-qualified source has unchanged CMake/test/production inputs;
the native source inventory SHA256 is identical across these Mac and Linux builds:
6171af9eb1c5f55c38731325b46c74902ea0f5c6fd4778f417fa4a5eb76aafd9.

Host: Chapman3, Linux x86_64, previously inventoried glibc 2.17.
Actual build-info records GNU GCC 10.2.1 and matching devtoolset-10 tools,
private CMake/CTest 3.29.6, Debug, explicit C90 and C17, qfits memory mode 2,
BUILD_TESTING=ON and MEFPP_BUILD_RESOURCES=OFF.

Both native builds passed all nine CTests: 3.90 seconds (C90), 3.06 seconds (C17).
Four dome/sky and detector-order cases per mode called the production-linked
mef_build_cal path and checked every returned pixel exactly:
324 per case, 1296 per mode, 2592 total. This upload's archive checksum,
all 34 manifest entries, language flags, complete suite logs, per-attempt source
identities/results, eight native log hashes and preservation assertions verified.

Source run:
`/home/fselman/Software/build/wenu-imaging/chapman3-normalization-ctest-mex5jiwt`.
Retained collection:
`/home/fselman/Software/build/wenu-imaging/chapman3-normalization-evidence-hgo6d1zm`.
Transfer bundle: chapman3-normalization-ctest-evidence.tar.gz,
28642 bytes, SHA256
872e866ce1c49a3892476f0dc5655f604fd71a6e9ee4c4b46fa7307827d7c8c1.
Verified Mac copy:
`/Users/fselman/Software/build/wenu-imaging/chapman3-normalization-transfer-LNYam3yZ/chapman3-normalization-ctest-evidence.tar.gz`.

All 34 original reports are copied byte-for-byte in reports/. manifest.json
records their original paths, byte lengths and SHA256 hashes.
reports/qualification-run-provenance.json is the outer build/test record.
The root and reports/run-provenance.json records describe collection, not new tests.
Historical paths are retained; archived build trees are not portable installations.

Protected configuration/native executables and the checkout remained unchanged.
No installation, resource decompression, normal engine switch or observational
processing ran. This is bounded test/build and shared-normalization acceptance,
not memory-safety, independent flat quality, covariance/variance, nonzero-overscan
accuracy, BPM exclusion, other-platform or full-pipeline acceptance.

Together with the preserved Mac evidence this meets #94's target gate.
Review PR #93 then #95 before integration; no merge or cleanup is implied.
Retain source runs and installations. Proceed to the declared Stage 2
memory/ownership work only within its scope; review after Stage 2 remains mandatory.
