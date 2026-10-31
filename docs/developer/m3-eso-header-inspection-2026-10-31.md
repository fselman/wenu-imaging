# M3 legacy ESO header inspection correction — 31 October 2026

31 October #180 [corrected paired and real-tree receipt](m3-eso-header-paired-results-2026-10-31.md): source
f7967fd1ee93f2a5a1a4faa227cadd460c054fa5 passed 22/22 on selected Intel Mac
(4.788 s) and representative Chapman4 (2.405 s), with installed files and clean
main preserved. Actual CN Ori redisplay now retains all five 80 s r_SDSS headers,
33 HDUs each, while retaining 36 warnings and one separate missing master-flat
reference. The original-scope M3 closure recommendation is reinstated for owner
acceptance; PR #178 is ready. No test replay/install/host sync for this receipt.
Separate owner merge/cleanup precedes M4 review; earlier held/pending notes are
historical. #181 remains a separate suffix-convention follow-up.

Refs #180 and #159, PR #178. Actual Chapman4 display at qualified source
`0d8f2978a4ef4c78c47f1526b48e03d77351c024` exposed a case missing from the
21-group synthetic suite. The earlier cumulative closure recommendation is
held pending this correction's actual-host qualification and repeated display.
Existing passing results remain valid at their stated revisions and scope.

## Actual observation and cause

The historical CN Ori r_SDSS partition display reported existing files with empty
target/filter/exposure/EXTNAME fields. Its diagnostics identify nonstandard ESO
telemetry cards, including raw `ESO DET TLM2 END` at Card 60 and master-bias Card
51. Source `headers` called `hdu.verify("exception")` before retaining any HDU
fields, so an incidental nonstandard card discarded otherwise readable metadata.

The owner supplied a pager excerpt, not full diagnostics or raw cards. The exact
offending card bytes/value are not established here. Representative deliberately
invalid ESO telemetry and selected EXPTIME cards reproduce the strict-reader
failure without claiming byte-identical real-card reproduction.

The missing master-flat link is a separate unavailable-reference observation.
Unavailable expected preprocessing/WCS locations also do not establish that
historical products are absent everywhere. Do not repair links, rewrite raw
headers or restart reduction based on this display.

## Bounded correction

- Use Astropy's non-fixing `verify("warn")` inspection mode, retaining warnings
  as diagnostics and incomplete coverage, instead of treating every nonstandard
  incidental card as a reason to discard the entire HDU.
- Read selected cards independently. If one selected value cannot be parsed,
  retain its keyword, available raw card and parse diagnostic, represent its
  value as unavailable, and continue with unrelated readable fields.
- Retain warning evidence in the finally path even if a later true structural
  error prevents further traversal. Structural/unreadable/truncated FITS and
  header/HDU/byte limits remain diagnosed; no blanket ignore/fix option is used.
- Keep read-only mode, no payload access, unchanged files and metadata authority.
  This is inspection, not FITS compliance, detector/scientific or product success
  validation. No native code, numerical client or project state changes.

## Verification and next gate

[Retained evidence](fixtures/agent-m3-eso-headers-2026-10-31/README.md): the added
regression fails before the correction (21/22; zero retained HDUs instead of
three). Corrected suite passes 22/22 in 3.246 s. Tests cover malformed incidental
telemetry and malformed selected EXPTIME independently, preservation of readable
target/detector/exposure fields as applicable, warning/error diagnostics,
incomplete coverage, exact bytes/modes/mtimes and traps on image-array reads.
All existing 21 groups, including original/updated normalization/WCS client-body
comparison, remain in the suite. Existing agent environment was reused.

The actual-host protection runner now requires exactly 22 groups. Qualify the
corrected source on selected Intel Mac, then representative Chapman4; no C build,
installation, native engine, solver, observations or historical matrix. Preserve
both earlier successful host runs and failed new regression evidence.

After paired qualification, repeat the bounded read-only historical Chapman
display with identifying path/HDU columns and retain full diagnostics rather
than a horizontally clipped pager excerpt. Confirm readable header fields are
retained; do not require missing calibration/products to appear or unknown
completion to become successful. Then revisit the M3 closure recommendation.
