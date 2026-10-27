# Actual Mac acceptance evidence — 26 October 2026

Fernando supplied mac-acceptance-evidence.tar.gz (71587 bytes), SHA256
535200be7bdf69d9ed930390cff3dc532a16e7ba2d796388fe271b031df1b739.
The agent verified the archive identity, safe regular-file members, and all
32 source-file sizes/hashes in manifest.json. This directory preserves all
35 regular archive members byte-for-byte, including the collection provenance.
No observational images, executables or private configuration are included.
The files in reports/ use flattened names; manifest.json maps them to exact
original Mac paths and hashes.

## Reviewed results

- Robust BPM C90/C17: both run records and comparisons cross-link by verified
  SHA256. All 32 detectors reproduce the historical mask, with 34122 bad pixels.
  The 33 raw header changes per comparison are exclusively reviewed generated
  ORIGFILE replacements. The separate-master-bias argument was not supplied.
- Native science BPM toggle: four detector-1 runs, C90/C17 and original/two-pixel
  mask variant, have zero unequal output pixels and retained nonzero flagged
  samples. This characterizes missing direct exclusion with a fixed prebuilt
  flat; it does not test flat construction or full mask transformations.
- Installed SExtractor/SWarp: NONE retained the test signals; explicit binary
  MAP_WEIGHT excluded the flagged contribution while retaining controls.
  These diagnostic weights are not validated propagated physical variances.
- Shared normalization: the included Mac report records successful dome/sky
  C90/C17 fixtures. The driver and its complete fixtures are not in this bundle;
  the permanent-regression task remains open.
- SCAMP 2.10.0: build/test/selection records share the permanent executable hash.
  The agent independently compared all selected WCS coefficients from the two
  supplied native headers exactly. Both synthetic catalogues have 100 objects.
  The retained PDF matches its recorded SHA256. It rendered successfully for
  inspection, with a visible detection field, grid and axes; this is a rendering
  check, not independent astrometric or scientific validation.
- Relocation and final selection journals preserve old/new paths. Original
  absolute paths in historical records must not be interpreted as current paths.

## Provenance caveat and retention

The original native-mask root run-provenance.json retains a stale status_note
saying runs had not launched. Its final status is passed, processing_launched is
true, and the detailed native-mask-check.json plus four per-run records record
completed runs. Preserve the original bytes; use those completion records and
this explicit reconciliation. Do not silently edit historical evidence.

Some records are retrospective or retain unknown external-source Git identities.
A source revision, binary hash, and orchestration branch have different roles.
The imported records describe their actual source commits; this review branch
does not pretend to be the original tested branch.

Large raw inputs, calibration products, outputs, full logs, relocation contents
inventories and configuration backups remain at the retained Mac locations
identified by the records/journals. The agent verified archive-internal
identities, not current access to those external Mac files. Their independent
retention review still applies before deleting any run tree. This import does
not authorize deleting scientific data, active installations or directories.

This preserves the supplied bounded Mac evidence in Git. It does not establish
full Stage 1, memory safety, Chapman3 sentinel acceptance, WFI/platform support
or ESO Phase 3 compliance. #13/#75/#90/#91 and the declared remaining gates stay
open. Do not merge or delete branches without Fernando's instruction.
