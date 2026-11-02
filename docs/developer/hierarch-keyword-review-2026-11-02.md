# HIERARCH warning and qfits keyword dispatch — 2 November 2026

Owner asked why the bias completion fixture emits HIERARCH warnings and whether
this relates to earlier Eclipse keyword-dispatch difficulties. Investigation is
against completed bias source ce36197 and its bundled qfits/Eclipse path. No
native library or observation was changed.

## Warning origin

The fixture helper constructs Astropy cards with names such as `ESO DPR CATG`.
Astropy creates a HIERARCH card automatically for this non-basic keyword spelling
and emits VerifyWarning. Passing `HIERARCH ESO DPR CATG` explicitly produces the
same 80-byte card without the warning. The warning is from fixture construction,
not from Eclipse reporting a read/dispatch failure. It should not be globally
suppressed or treated as proof that all HIERARCH handling is safe.

The helper now explicitly prefixes its known ESO keywords. Comparing complete
old/new fixture FITS files, all17 are byte-identical. With warnings always enabled,
old construction emits136 notices (eight distinct keyword messages across17
files); explicit construction emits0 HIERARCH notices. The owner's default warning
filter printed the eight distinct messages. Native bias/ASDF code is unchanged,
so this fixture spelling change does not require replaying qualified numerical
contracts. This comparison used agent Astropy8.0.2; actual Mac warnings confirmed
the same implicit-HIERARCH behavior, but the isolated source probe was not run
on the Mac.

## Reproduced qfits interoperability pitfall

A tiny agent GCC13 C17 probe links the existing libqfits.a and uses only short
values and temporary headers. Full-name and dotted add/write/read/query/update/
copy controls succeed. Results:

| Spelling supplied to qfits | Result |
|---|---|
| `HIERARCH ESO DPR CATG` | Full HIERARCH name, reads/writes/updates correctly |
| `DPR.CATG` | Expands to that same full ESO name, reads/writes/updates correctly |
| `ESO DPR CATG` | No automatic HIERARCH prefix; memory lookup can succeed, but serialization truncates the key to `ESO DPR` and original-name lookup then fails |
| `ESO.DPR.CATG` | Expands to `HIERARCH ESO ESO DPR CATG`, a different key |

This is recorded in [#223](https://github.com/fselman/wenu-imaging/issues/223).
It is a real naming/round-trip limitation, but cannot be identified conclusively
as the particular historical incident the owner remembers.

Source trace:

- `qfits5/src/expkey.c:qfits_expand_keyword` uppercases a no-dot name without
  adding HIERARCH. For dotted shortFITS names it always prepends `HIERARCH ESO`.
- `qfits5/src/fits_h.c:keytuple_new` uses that expansion. Exact get/mod and disk
  query APIs also expand their argument.
- `fits_h.c:keytuple2str` selects HIERARCH formatting only if the stored key
  begins with HIERARCH; otherwise its standard format uses only eight key chars.
- `qfits_header_findmatch` performs raw prefix comparison without expansion.
  Its own documentation warns that dotted shortFITS prefixes are not supported;
  use the full `HIERARCH ESO ...` prefix for this API.

The probe demonstrates the dangerous distinction: adding the stripped Astropy
name and reading it back from the same in-memory object is insufficient evidence.
The output card becomes `ESO DPR = 'CALIB   ' ...`; disk round-trip must be tested.
Both exact in-memory and disk queries against valid Astropy-produced HIERARCH
cards succeed with the full name or correct dotted shorthand.

## Current scope and future callers

The reviewed bias/legacy configuration and native header-writing sites use full
HIERARCH names; no current bias failure was found. New callers must not pass
Astropy's stripped, space-separated key names directly into qfits. Use explicit
full names at that boundary; keep PAF setting names separate from FITS names.
Prefix dispatch must use full prefixes. No silent fallback, broad normalization
rewrite or unrelated native repair is included in this investigation.

Long string/CONTINUE/fixed-buffer safety remains separately deferred in #125.
The earlier actual Mac BPM provenance overflow #126 involved full pathname values,
not failure of the HIERARCH convention itself. Using correct keyword spelling
does not fix those value-length limits. #223 remains open for a reviewed native
normalization/rejection contract and target qualification before any library fix.
