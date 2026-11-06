# Additive bias scalar QC headers — 6 November 2026

## Executive summary

The standalone native bias recipe now prepares additive FITS scalar diagnostics
from exactly the same archived measurements used by its final ASDF. Existing
legacy headers and numerical kernels are unchanged. Owner accepted
[the mapping](design/bias-qc-fits-asdf-mapping-v1.md) before implementation.
ASDF already held these measurements; no new measurement or application-schema
change is needed. The mapping registry is
`mefpp2/ins/mef/common/mef_bias_qc_fits.def`.

The coordinator uses the existing operation template in measurement-only mode,
archives QC, prepares the additive header and invokes the existing exclusive
publisher. Original non-recipe adapters retain their old publication behavior.
No published product is patched and no statistic is recalculated. Detector
arrays are released after native detector publication as before. Unknown code,
nonfinite measured value, collision or overlong card fails before publication.

Scalar cards include availability, unit, method, sample count and region/mask/
source context. Input identities, actual source HDUs, used/rejected memberships
and original RON indices stay distinct. Arrays stay in ASDF. FITS-only harvesting
is a later consumer, not claimed as implemented or a complete ASDF reconstruction.
New real diagnostics use 17 significant decimal digits and uppercase E; counts
remain integer. Legacy cards retain their existing six-decimal formatting.

## Evidence and limits

Actual owner-run existing-product checks: 864 exact legacy header comparisons
against retained all32 reference masters; 704 FITS/ASDF comparisons within legacy
rounding. These metadata checks do not establish real image pixel equivalence.

Agent native build uses actual qfits/Eclipse/bias kernels and UBSan. Four
BPM/MAD/RON profiles cover two detectors each, preserve input pixels and compare
copied values. Eight actual serialized header fixtures pass an independent
80-byte card parser for keyword uniqueness, numeric grammar and measured versus
unavailable semantics. Native controls cover NaN refusal, overlong identifiers,
DBL_MIN, DBL_MAX, the next double above one and signed zero. Strict C17 new-code
syntax and Python compilation pass. Existing optional-NULL diagnostics (#269)
remain unrelated and unchanged. No external ASDF library or Astropy is installed
in the agent; do not describe these checks as actual Mac integration qualification.

## Focused actual Mac gate

`mefpp2/tests/qualify_bias_scalar_qc_mac.py` runs from an exported exact candidate
revision under the established Astropy interpreter. It reuses the compiler/SDK,
qualified external prefix and one-detector reference adapter from the retained
memory-readback-build. It builds only the changed recipe and QC probe, checks
compiler warnings, runs four two-detector native profiles, parses eight dumped
headers with Astropy and runs the eight focused standalone recipe groups.

The recipe checker retains exact legacy-card and byte-identical pixel assertions
against the reference adapter. Only explicitly recognized additive keys are
excluded from the legacy comparison, then every addition is independently checked
against the final ASDF via `bias_qc_fits_contract.py`. That checker asserts complete
registry coverage, scalar values, states/reasons, units/methods, masks/regions/
sample counts, input source HDUs/memberships and RON identities. It uses separate
established FITS and ASDF interpreters. Invalid and occupied destination controls
remain in the same focused boundary gate. No old warning/scientific matrix rerun.

Only new synthetic evidence directories are created under the existing build
root. There are no real raw/product reads, installation, merge or evidence cleanup.
After this gate passes, review its actual results before a new real-data run.

## Qualification-controller correction (#272)

Owner inventory confirms the retained mefpp_m5 reference adapter exists in
warning-fix-build, while memory-readback-build contains only the recipe. All
three retained builds use the same valid libasdf prefix. The first preflight
failed without creating a qualification directory. Using warning-fix-build then
reached configure, which failed because the controller omitted the explicit
MEFPP_C_STANDARD=17 setting. No compilation or tests ran.

The controller now checks the reference C17 lane, passes it explicitly to the
fresh configuration, and distinguishes missing adapter from missing headers.
One mocked controller regression passes, asserting the actual generated configure
command retains C17, compiler, SDK and prefix. This is not actual Mac qualification.
Preserve the failed source/build/log. Export the corrected candidate separately
and retry under scalar-qc-qualification-c17; use warning-fix-build as reference.
