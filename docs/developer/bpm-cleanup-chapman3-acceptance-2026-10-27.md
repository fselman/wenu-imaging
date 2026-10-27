# BPM cleanup: Chapman3 target acceptance, 27 October 2026

Issue #90; PR #96. Actual target source:
7b570d3a00b932e887bfb95ae5156258dd384f18, clean fix/90-bpm-result-cleanup.
The production repair is the constructor-dependent third-result cleanup guard.
See [Mac reproduction and instrumented acceptance](bpm-cleanup-acceptance-2026-10-27.md).

## Results and independent review

All eight target cases passed: explicit C90/C17, robust/proportional, and
retained/known-response inputs. Each 9x9 returned mask equals the saved extension
pixel for pixel, has binary polarity, 79 good and 2 bad pixels, matching extension
identity and consistent saved counts. All 81 pixels in each controlled mask also
match the independent expected mask, with bad flat indices 0 and 40.
Every target input file hash and each mask-pixel digest matches the corresponding
Mac record exactly. This is bounded constructor/mask regression, not a general
scientific or calibration-quality validation.

The uploaded target archive SHA256 is
c790f9f563351880f7c34c7a821ffa9986d8dfc5a59533859841137acab84273.
The agent independently verified all 83 member sizes/hashes against the transfer
manifest, every recorded command/log hash and zero exit status, and read every
returned/saved mask and first input extension. Build reports establish GCC 10.2.1,
CMake 3.29.6, Linux, explicit C90/C17 and -O0 -g. All eight input sets and pixel
digests were independently compared with the separately uploaded Mac archive.

The committed C driver and fixture bytes are unchanged from Mac qualification.
Only disposable exported CMake target wiring differs by host. No production
source was edited on Chapman3. Its inspected checkout resolves to
/home1/fselman/Software/wenu-imaging; /home/fselman paths are recorded host aliases,
not evidence that a second checkout was tested.

## Diagnostic scope

No compatible GCC 10 address/undefined diagnostic runtime was found in the
inspected locations; compiler lookup returned bare library names. Existing
listed GCC 4.8 runtimes were not substituted. No runtime package was installed.
Chapman3 runs are uninstrumented functional target verification. The separate
Mac C90/C17 instrumented runs and unchanged C90 reproduction establish the
bounded invalid-access evidence. Leak detection was disabled on the Mac.
Neither host result closes the broader #75 memory/ownership qualification.

## Preservation and reproducibility

The [target run report](fixtures/chapman3-bpm-cleanup-2026-10-27/run-provenance.json)
contains all commands, exact tested source, tool/input/output hashes, cases and
preservation checks. C90/C17 build reports and the 83-file transfer manifest
are retained beside it. The complete archive, including all logs and original
output masks, is retained as Library file libfile_32b1b34f9bec8191ab5691cd18eaa8d6.

Retain the target run and archive on Chapman3:
~/Software/build/wenu-imaging/chapman3-bpm-cleanup-xx1e8_5z/
A hash-verified copy of chapman3-bpm-cleanup-evidence.tar.gz is also on the Mac
under ~/Software/build/wenu-imaging/mac-bpm-cleanup-corrected-dqxrrtzz/.
Fernando retains both host run directories. No deletion/relocation is authorized.

The selected historical executable and executable configuration hashes remained
unchanged. The committed fixtures and checkout remained unchanged. No installation,
engine selection switch or observational processing ran. Build-info /usr/local
is only the default unused CMake install prefix.

Reproduce on Chapman3 from a clean repair branch using:
nice -n 10 "$HOME/.conda/envs/wenu-imaging/bin/python" mefpp2/tests/qualify_bpm_chapman3.py
with --cmake "$HOME/opt/cmake-3.29.6/bin/cmake" and
--compiler /opt/rh/devtoolset-10/root/usr/bin/gcc.
The runner creates an independent recorded attempt and never executes in the
repository fixture directory.

The bounded #90 acceptance criteria are met: source contract repair, actual Mac
diagnostic reproduction, corrected instrumented Mac and unchanged-driver/fixture
Chapman3 C90/C17 mask verification, with evidence retained. Issue closure records
verified correction; PR integration is a separate action. No merge or branch
deletion has been authorized. Broader #13/#75, WFI observational, scientific,
installation and Phase 3 gates remain separate.
