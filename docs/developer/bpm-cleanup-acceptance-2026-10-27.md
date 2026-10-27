# BPM constructor cleanup: Mac acceptance, 27 October 2026

Issue #90; repair PR #96. Tested source: b394a99bbfb57f45d1c982b578f39e003c329540,
clean fix/90-bpm-result-cleanup on MC02VV0HPHTDG (Darwin x86_64).
Only production change: guard the third result access in mef_build_bpm with
!bb->bpm_proportional_flag. The proportional producer allocates two pointers;
the robust producer allocates three. Producers, arithmetic, normalization,
0.5–1.5 thresholds, mask polarity and installations are unchanged.

## Evidence reviewed

The uploaded archive SHA256 is
63cd5411470e605fd47cfeaf268d719ba51441c3f8545787ac5bc434f143f6dd.
All 90 member sizes/hashes matched its transfer manifest. The agent independently
read the production source, reports, logs, FITS masks and inputs. The exported
production C unit matches the intended repair exactly. Every corrected command
exited zero; reviewed logs contain no address/undefined diagnostic failure.

The original main 7aeb454574ee35f924e5d3d024b273ebbb4dd153 C90 run reproduced
the invalid proportional cleanup access (diagnostic exit 86). Its passed status
means the expected failure was reproduced, not that the baseline was correct.

Corrected C90 and C17 Debug builds used AppleClang 15.0.0.15000100,
CMake 3.29.3, -O0 -g -fno-omit-frame-pointer, address/undefined instrumentation
and -fno-sanitize-recover=all. Leak detection was disabled; this does not
establish leak freedom or the broader Stage 2 memory gate.

All eight combinations passed: C90/C17, robust/proportional, retained/known-response.
Each returned and production-saved mask contains 81 matching pixels, 79 good and
2 bad, with matching source extension identity and saved counts. C90/C17 pixel
digests agree per constructor/fixture. The controlled fixture independently
requires rejection of flat indices 0 and 40: responses 0.25 and 2 among 79 unit
responses; illumination levels 100, 200, 400 and zero overscan. Mean response is
81.25/81. This checks threshold/polarity behavior without replacing the fitting
algorithm. All controlled expected pixels were independently rechecked from
the uploaded outputs.

## Retention and reproduction

Original baseline:
~/Software/build/wenu-imaging/mac-bpm-cleanup-baseline-n06whasu/
Corrected run:
~/Software/build/wenu-imaging/mac-bpm-cleanup-corrected-dqxrrtzz/
Keep both directories and the archive; no deletion or relocation is authorized.
Fernando retains the Mac runs. The complete uploaded archive is also retained as
Library file libfile_a9ebc6e273708191b747b5279a2b2fd7, with the SHA256 above.
It contains all original output masks, corrected logs, selected source,
build records and transfer manifest; no active installation is bundled.

[Committed reports](fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json)
record exact commands, all case/input/output hashes and protected-file identities.
The original selected engine and executable configuration were unchanged.
No install or observational processing ran. The build-info install_prefix
/usr/local is a CMake default, not evidence that an installation occurred.

The driver and two input sets under
mefpp2/tests/fixtures/bpm-cleanup/ are preserved byte-for-byte from the qualified
Mac attempt. manifest.json identifies every file. Run only staged copies in
fresh directories with run-provenance.json, never in the fixture directory.
The historical diagnostic marker still says proportional even for flag 0;
argv[1] controls the actual branch. Do not interpret that marker as the selector.

Reproduce the original Mac orchestration with:
python mefpp2/tests/qualify_bpm_cleanup.py <retained-baseline-directory>
That script is deliberately Mac-specific. Chapman3 must use the unchanged
committed C driver and fixture bytes with its own recorded compiler/build
orchestration; actual Chapman3 acceptance is pending.

Keep #90 open until its target evidence is linked. Broader #13/#75, installation,
WFI observational, scientific and Phase 3 gates are not completed by this result.
No merge, branch cleanup or normal engine switch is authorized.
