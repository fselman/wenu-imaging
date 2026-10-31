# M3 ESO header correction — paired qualification and actual-tree receipt

31 October 2026. PR #178 corrected source
`f7967fd1ee93f2a5a1a4faa227cadd460c054fa5`, tree
`2a47848d07ce083252abfb38e2d37a1d1b2464a9`.

**The bounded #180 correction passed 22/22 on both actual hosts and the
historical Chapman redisplay now retains readable metadata for all five science
exposures. The M3 closure recommendation is reinstated for owner review.**

## Paired actual-host qualification

| Host | Result | Retained export | Retained qualification |
|---|---|---|---|
| Intel Mac MC02VV0HPHTDG | 22/22 in 4.788 s | `/Users/fselman/Software/build/wenu-imaging/mac-m3-eso-header-export.O4lR11fO` | `/Users/fselman/Software/build/wenu-imaging/mac-m3-inspector-stages-z0v0c0io` |
| Representative shared Chapman4 | 22/22 in 2.405 s | `/home1/fselman/Software/build/wenu-imaging/chapman-m3-eso-header-export.WKXoY9Ns` | `/home1/fselman/Software/build/wenu-imaging/chapman-m3-inspector-stages-p_958lyq` |

Nested suite directories are `m3 project inspection p4urj159` (Mac) and
`m3 project inspection b4en8ch1` (Chapman). Full tests.log, run-provenance.json and
synthetic fixtures remain at those locations; exports retain exact source.tar
and source. Times identify runs, not benchmarks.

The guarded commands required actual host, selected clean-main repository/full
SHA/upstream/origins and exact fetched candidate revision. Checkout main remained
`3a61df627edfdbb1ef43cc3c956dff74bd28c066`; no branch switch or installation.
The same previously reviewed runner verified thirteen exact source objects,
selected imaging Python and prefix, niceness10, actual nested installed reduction
module and configured engine/configuration. Both returned successful before/after
protection assertions, including the runner's failure-safe preservation path.

The suite retains all prior 21 groups, adding malformed incidental ESO telemetry
and selected-card isolation controls. It verifies readable unrelated metadata,
retained diagnostics/incomplete coverage, no image-array inspection and unchanged
fixture bytes/modes/mtimes. Existing original/updated normalization/WCS client-body
comparisons also pass. The header correction does not modify those clients or C.

HIERARCH warnings remain visible, and Chapman's known LC_CTYPE startup warning
remains nonfatal without a global locale change. No native engine, solver,
observation reduction, package/tool installation or historical matrix occurred.

## Bounded historical real-tree redisplay

Inspected project:
`/home1/fselman/omegacam/testing/reduced/science/CN_Ori_055207p790_m052500p5/r_SDSS/2017-03-11T01:24:08`.
Full retained JSON:
`/home1/fselman/Software/build/wenu-imaging/chapman-m3-real-tree.uQvM4D3K/report.json`.

The owner-run command verified the four inspector/helper source blobs against
the exact qualified commit, used the legacy partition execution base and explicit
instrument config, requested recursive header-only JSON inspection and checked
clean checkout state. It retained the entire report instead of horizontally
clipped diagnostic excerpts. The returned summary preserves list order:

| Member | Raw file | Target | Filter | EXPTIME | HDUs read |
|---|---|---|---|---:|---:|
| 1 | OMEGA.2017-03-11T02:14:43.394.fits | CN Ori | r_SDSS | 80.0 s | 33 |
| 2 | OMEGA.2017-03-11T02:18:53.274.fits | CN Ori | r_SDSS | 80.0 s | 33 |
| 3 | OMEGA.2017-03-11T02:23:03.275.fits | CN Ori | r_SDSS | 80.0 s | 33 |
| 4 | OMEGA.2017-03-11T02:20:58.284.fits | CN Ori | r_SDSS | 80.0 s | 33 |
| 5 | OMEGA.2017-03-11T02:16:48.284.fits | CN Ori | r_SDSS | 80.0 s | 33 |

Returned diagnostics: **36 fits_warning and one reference_error**; no fits_error
or header_card_error in the returned diagnostic counts. Warnings are retained,
not suppressed or repaired. The first warning is attributed to the existing
master-bias file; its complete message remains in the saved JSON. HDU counts are
readable header coverage, not physical detector or pixel-data validation.

The separate unavailable reference is the science partition's
`OMEGACAM_MFF_r_SDSS_1x1.fits`, targeting
`/home1/fselman/omegacam/testing/reduced/calibs/sky/200253584/r_SDSS/2017-03-13T23:12:13/OMEGACAM_MFF_r_SDSS_1x1.fits`.
This reference remains visibly incomplete. It is not repaired, rebuilt, silently
reassociated or treated as proof that products do not exist at other locations.

## Evidence limits and disposition

This receipt inspects owner-returned terminal results. Full raw target files and
the real-tree JSON remain on Chapman/Mac; they have not been transferred or
independently reread by the agent. Do not claim a raw archive audit, actual input
pixel comparison, exact reproduction of the original malformed telemetry bytes,
full project completion or FITS/scientific/Phase 3 compliance. The actual display
does not bulk-hash or process observation arrays. The prior strict-reader failure,
representative before/after regression and earlier successful runs remain intact.

The actual legacy metadata failure is now corrected and target-qualified; #180
meets its bounded criteria. Retain #181 as the separate suffix-convention follow-up
(not the cause of this .fits case). The
[final M3 review](m3-final-closure-review-2026-10-31.md) uses this corrected receipt
alongside the original accepted native path evidence and prior inspector scope.
Recommend owner acceptance, then separately instructed integration/cleanup and
M4 detector/layout review. This receipt changes documentation only and requires
no test replay, installation or host synchronization.
