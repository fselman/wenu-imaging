# Large-file runtime installation and real OmegaCAM comparisons

Date: 1 November 2026 (America/Santiago).
Related: PR #200; issues #195, #201 and previously accepted #121.

## Result and attribution

Fernando returned successful installation and native real-data comparison receipts
from Intel Mac MC02VV0HPHTDG and representative Chapman4. Both actual checkouts
were clean main at a240829311ad958ac0d1ea205d74fd951d15001d.
The assistant inspected the returned console text; full on-host JSON reports,
logs and FITS products were not transferred for independent agent-side rereading.

PR #200 was already owner-accepted and merged, with branch cleanup completed.
#195 and #201 are closed. Earlier acceptance-pending notes describe historical
states. The owner inserted installation and real OmegaCAM comparison before M5;
this bounded work is now reported passing, awaiting owner acceptance.
M5 remains paused. Normal engine selections have not changed.

## Separate installations

Source: a240829311ad958ac0d1ea205d74fd951d15001d.
Each installation used a fresh pinned source export, the supported
configure/make/make install frontend, C90, CFLAGS=-O2, frontend Debug (-g),
tests disabled, selected project tools, niceness 10 and bounded numerical threads.
Builds were serial through the frontend. No dependency upgrade occurred.

| Host | Installed engine | SHA256 |
|---|---|---|
| Intel Mac | /Users/fselman/opt/mefpp-a240829-c90/bin/mefpp | fb22c57dd1cf735f0a1d574acb1c2cf8de3013e77c28bd62234288445eac3636 |
| Chapman4/shared home | /home1/fselman/opt/mefpp-a240829-c90/bin/mefpp | dab0da5312024894685a633cdcb5a8937feafec8149f45f30cd51b15b24e5276 |

Returned verification passed source/language/prefix identity, every manifest-listed
installed-file hash, installed-vs-built engine hash and no-argument CLI usage.
This did not repeat the historical installer, resource-pixel or C90/C17 matrices.

Retained installation directories:
- Mac: /Users/fselman/Software/build/wenu-imaging/mac-large-file-install-GzLXV55v
- Chapman: /home1/fselman/Software/build/wenu-imaging/chapman-large-file-install-SLEBL3NJ

Each retains source/, build/, logs, protected-before.json and run-provenance.json.
The source copies used for installation are source/mefpp2/.
Source changes replace the same paths in the current checkout; old versions
remain in Git history. The old and new installed executables coexist.

## Correct reference selection and retained initial failure

The first Mac run compared CP Pup against the retained 26 October output from
4ade8c52027c736a49b65da3bdb31f11b036693b. Every detector had 8,362,004 unequal
finite pixels, with changed overscan and frame QC headers. Native processing
returned zero. The comparison correctly failed; do not relabel it as passing.

The assistant initially selected a reference predating accepted overscan correction
#121. The historical trimmed-mean loop started at pix_low+1, omitting one retained
sample while retaining the full denominator. The corrected loop starts at pix_low.
Both source versions were inspected. A read-only calculation from actual raw scan
pixels, using the unchanged PAF rejection counts (10 low, 10 high), reproduced
both old and corrected SCAN MEDIAN header values in all 32 detectors at their
six-decimal printed precision. This is a scan-median diagnosis, not a standalone
proof of every pixel or arbitrary scientific correctness.

Failed comparison retained:
 /Users/fselman/Software/build/wenu-imaging/mac-large-file-cppup-6ov3a88h
Its run-provenance.json remains failed and retains pixel/header differences.
Protected files and checkout passed preservation.

The exact comparison was then made against the accepted pre-large-file native
source 5b2518312b962e4e7aeff72e08d370b5e1c6a81a, which already includes #121.
Fresh code-only reference builds used selected tools, C90, Debug/-g and -O2
to match the installed candidate's settings; no reference installation or tests.
Reference builds used at most two jobs. Retained prior builds were not modified.

## Real-data comparisons

| Actual host | Exposure | Filter | Result |
|---|---|---|---|
| Intel Mac | OMEGA.2017-03-13T02:35:52.825.fits (CP Pup, 20 s) | r_SDSS | 32/32 detectors exact and finite |
| Chapman4 | OMEGA.2017-03-11T01:48:00.279.fits (CN Ori, 480 s) | NB_659 | 32/32 detectors exact and finite |
| Chapman4 | OMEGA.2017-03-11T02:14:43.394.fits (CN Ori, 80 s) | r_SDSS | 32/32 detectors exact and finite |

Inputs were private byte-identical copies of the retained raw science, master
bias, master flat, BPM and original PAF. Calibration files were reused to isolate
engine behavior; they were not reconstructed. The recipe command was:
mefpp --bias OCAM_MB_1x1.fits --mff OCAM_MFF_<filter>_1x1.fits --science science.list.
Each science list named a private absolute input path; command cwd was recorded.

This exercises the native science recipe and its existing overscan/trimming,
bias/flat processing and MEF output. No Python reduction wrapper, normalization,
astrometry, extraction, mosaic or photometry stage was invoked.

Mac: the installed candidate ran once, initially producing the failed historical
comparison above; its existing product was reused for the corrected comparison.
The fresh pre-large-file reference ran once. No duplicate candidate reduction.
Chapman: each engine ran once per filter (four native reductions), serially,
retaining both products and separate console logs.

Each paired comparison checked all pixels in bounded row chunks, primary plus
32 detector HDUs, detector identity/order, shape, dtype and scaling, and complete
raw header cards. All three exposures have zero unequal/nonfinite pixels in every
detector; all raw headers match except generated primary ORIGFILE.
Output hashes and actual command/input identities are retained in host reports.
No output was rounded or transformed to manufacture equality.

Final comparison evidence:
- Mac: /Users/fselman/Software/build/wenu-imaging/mac-pre-large-file-reference-chz8gjme/run-provenance.json
- Chapman: /home1/fselman/Software/build/wenu-imaging/chapman-large-file-cnori-x4cbrcvv/run-provenance.json

The original Chapman fixture and input manifest remain:
 /home1/fselman/Software/build/wenu-imaging/chapman3-cnori-native-r3uhi3ax
fixture-record.json SHA256:
 da3526467f65095d154655e81b66868dfe0dc6ebd61902c0be48d2ff5a09ce93

## Preservation and rollback

Final receipts report protected files and checkouts unchanged. Original raw
observations were not modified; previous products/evidence remain.
Normal selections still point to:
- Mac: /Users/fselman/opt/local/mefpp/bin/mefpp
  SHA256 8bc2996bfc35719c60bdeb10219c3052ad87c89d444cd27512aeddf2cd266e9a
- Chapman: /home/fselman/opt/local/mefpp/bin/mefpp
  SHA256 06dde5281aa10a8bc874f55cd5838299deb3b59a815136df30d09c37d1d61265

Normal configuration identities remain:
- Mac ~/.pycavi/pycavi_astrosoft.cfg:
  3a0bca420a06827abd3073ac6cc0794ee7b89fe7a2d9f4cb4553db428996c70b
- Chapman ~/.pycavi/pycavi_astrosoft.cfg:
  9127dc7b2225799af763ba7f8a558f1fa9c358dfcd2059fdf69fc935555f0e52

A later engine-selection change must preserve all other configured programs and
record the original selection/configuration for rollback. No selection change,
engine replacement, run-directory cleanup or deletion is part of this receipt.

## Scope and next step

This establishes installed native equivalence across the large-file increment
for these three real exposures with retained calibrations. It is distinct from
the already accepted synthetic >4-GiB qualification in
[the paired I/O receipt](large-file-image-io-paired-results-2026-10-31.md).
The real exposures do not independently retest the >4-GiB offset boundary.

No speed/RSS benchmark, new sanitizer/leak claim, calibration reconstruction,
complete Pycavi workflow, scientific validation or Phase 3 compliance is established.
Native NULL-free warning messages observed in the Mac console remain recorded;
no diagnostic-free or new defect-cause claim follows from successful pixels.

Review this documentation and accept the intervening installation/comparison
work before resuming M5. Do not replay unchanged qualification matrices.
Merge/branch cleanup, changing normal engine selection and M5 implementation
remain separately instructed actions. Earlier source/date-specific pending
statements remain historical evidence.
