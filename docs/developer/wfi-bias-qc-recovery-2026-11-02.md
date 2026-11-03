# WFI first-detector QC recovery

Actual Mac d96608a attempt retained at
`/Users/fselman/Software/build/wenu-imaging/wfi-first-bias-retry-pKBFGzsm`.
Native exit status is zero and `WFI_MB_CHIP1.fits` was published. ASDF completion
failed because raw WFI timestamp basenames contain colons, forbidden by the local
QC reference policy. All four preservation controls passed. This is not yet
scientific acceptance or complete recipe acceptance.

The common sidecar naming function now escapes unsafe filename characters using
`~HH` hexadecimal bytes, escaping literal tilde too. A colon becomes `~3A`;
ordinary alphanumeric/dot/hyphen/underscore names retain their spelling. Percent
escapes are avoided because ASDF's path handling decodes them. Original FITS
names and locations remain in records. No decoding is performed by QC traversal.
Reference validation/root containment, digests and no-overwrite rules remain.

Preparation: all eleven shared metadata/ASDF controls passed, including timestamp
names, escape collisions, relocation and forbidden references. Mac confirmation
uses the retained ASDF environment before running QC-only recovery.

`Pycavi2/tools/resume_wfi_bias_qc.py` checks the retained failed-QC/successful-native
receipt and input hashes, writes twelve verified records to a fresh directory,
verifies FITS structure read-only and locks earlier artifacts before/after. It
never invokes the native recipe. Earlier failed receipts remain unchanged;
`qc-recovery.json` is a separate completion record. Native NULL-free diagnostic
messages are retained for follow-up; they did not prevent native exit zero.
Owner inspection of image HDU1 and QC remains required before other detectors.

## Mac recovery preflight corrections

Actual Mac common QC controls passed 11/11 in 1.666 seconds at
`wfi-bias-qc-recovery-8qns8FIH`. Its first recovery invocation supplied a nested
QC directory; the fresh-run guard requires a directory directly under the build
root. A corrected invocation retained `wfi-bias-qc-only-Pc8fZ9P5`, then stopped
before writing QC because installed-package discovery ran inside the private
ASDF Python. These are recovery orchestration errors, not native failures.

The corrected helper invokes installed-file discovery and identity checks with
the selected `/Users/fselman/anaconda3/envs/wenu-imaging/bin/python` in a read-only
subprocess. ASDF writing remains under the qualified private QC Python. Both
snapshots use the same owning interpreter and guard, before and after recovery.
Preparation checked interpreter identity and propagation of guard failures.
Neither failed preflight wrote QC or changed the native product. Reuse passed
Mac naming tests; no native replay, installation or dependency change needed.
