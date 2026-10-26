# Intel Mac shared-normalization CTest evidence

Actual host: MC02VV0HPHTDG, Darwin x86_64. Tested branch:
test/shared-flat-normalization, clean source commit
c5f2bac84e39918d0a82ac1e57769f6473be0828. Refs #94, PR #95.

Source run:
`/Users/fselman/Software/build/wenu-imaging/mac-normalization-ctest-tli85v3h`.
AppleClang 15.0.0.15000100 and CMake/CTest 3.29.3 built the native graph
in explicit C90 and C17 modes, Debug, with BUILD_TESTING=ON and
MEFPP_BUILD_RESOURCES=OFF. All nine CTest entries passed in each mode.
Four production-linked mef_build_cal dome/sky/order cases per mode checked
324 exact pixels each: 2592 across both modes. Recorded fixture hashes,
eight attempt log hashes, language flags, suite results and preservation
assertions were independently checked from this upload.

The 34 original evidence files are retained byte-for-byte in reports/.
manifest.json maps each copied file to its original path, byte size and SHA256.
reports/qualification-run-provenance.json is the outer qualification record;
the two run-provenance.json files describe evidence collection, not another test.

Corrected transfer bundle:
mac-normalization-ctest-evidence-fixed.tar.gz, 28055 bytes, SHA256
99d2722ba229ab7153616154dd773cdcef226bfd2dea313d314e0103e7a58b52.
Retained Mac collection:
`/Users/fselman/Software/build/wenu-imaging/mac-normalization-evidence-fixed-5_381zye`.

The first collection accidentally replaced reports/run-provenance.json with
collection metadata. Its archive checksum matched but that one manifest entry
failed; the other 33 matched. It was not accepted. The corrected collection
recopied all 34 original files after verifying their recorded hashes, giving
the outer qualification record its distinct name. No tests were rerun.
The corrected archive and every manifest entry verified before this commit.

Protected executable/configuration hashes and checkout preservation passed.
No installation or observational processing was performed. This is bounded
normalization/build integration acceptance, not scientific flat accuracy,
variance/covariance, nonzero-overscan accuracy, memory-safety or full-pipeline
qualification. Resource decompression and installation were not repeated.
Chapman3 CTest integration remains pending; #94 stays open. No merge, branch
cleanup, normal engine switch or deletion of retained runs is implied.
