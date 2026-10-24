# Notebook 07 saturation units (#33)

The first r_SDSS ZPCalibration completed despite a disconnected terminal.
Fernando verified finite calibrated pixels, recorded linear scaling, sampled
WCS/timing preservation, and unchanged source/parent inputs. Records:
`~/omegacam/testing/wenu-imaging-test/notebook07-r_SDSS-tft0e40n`.
Its `runner-returned.json` and `output-check.json` exist. There were 981 clean
catalogue rows and 584 usable calibrators. DN2FLAM is
`2.10315823839273e-19`; maximum relative pixel-scaling error was
`7.790296462939863e-08`. MAGZP/PHOTZP are -21.374 in physical pixel units;
a negative zero point is not itself an error. Calibrated-image SHA256:
`f1d8a44239425b3c32b10ce3c51b06dab0b91e4affa6f13fd477e048cbed1bc4`.

However SATLEVEL remains `1759.4343046875001`, in original e-/s, while BUNIT
is `erg/s/cm**2/A`. The actual writer first scales an existing SATLEVEL (or
sets UNKNOWN when absent), then appends phase3_cards containing the unscaled
mean parent SATLEVEL. These overwrite the conversion. Native SATURATE also
remains in the pre-calibration units. This is a confirmed unit-handoff defect,
not a request for a different zero-point or saturation/noise model.

The correction applies saturation metadata after the inherited cards. It keeps
the parent-average SATLEVEL definition, multiplying by cumulative DN2FLAM;
it keeps native SWarp SATURATE, multiplying by this run's incremental pixel
factor. Unknown/nonfinite/nonpositive saturation is recorded as UNKNOWN, not
invented. MAGSATL retains the existing pixel-level expression and is explicitly
labelled a diagnostic, not a measured point-source saturation magnitude or
Phase 3 ABMAGSAT. Broader modelling and export remain #9.

The shared `calibrated_saturation_cards` helper also permits a fresh header-only
repair of the completed calibration: use the original parent-average SATLEVEL,
recorded cumulative DN2FLAM, and SATURATE from the preserved uncalibrated
coadd. No Gaia query, aperture measurement, fit or pixel rescaling is needed.
Never multiply the already calibrated image pixels again to repair headers.
Keep the old output and record source/output hashes and changed header cards.

Seven focused regressions cover the actual writer with native catalogue/plotting
operations excluded, first calibration with/without input SATLEVEL, subsequent
calibration, fallback input units, unknown values, invalid conversion factors, and fresh
header-only repair preserving exact pixel bytes/source hash/checksums.
The actual writer body is compiled from the installed/source module to avoid
initializing remote catalogue clients. These are focused tests, not full
constructor or independent scientific acceptance. Ten prior metadata tests pass.
Chapman3 installation and real-output header-repair verification remain pending;
keep #33 open until its correction comment includes those results.
