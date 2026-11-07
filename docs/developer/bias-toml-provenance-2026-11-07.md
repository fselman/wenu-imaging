# Bias completion: short TOML call and selected provenance — 7 November 2026

## Actual Mac acceptance complete; merge authorized

7 November: owner authorized merge/branch cleanup after the selected Mac built
3cae0756 with pinned cache/tools and passed native header controls. Corrected
dab9b44 verifier reused the same executable/cache and retained tiny references:
five actual products (default all, explicit all, subset, single-extension raw,
primary-image raw), four refusals and independent FITS/ASDF checks passed.
Receipt: scalar-qc-qualification-c17/toml-provenance-reference-fix-dab9b44/qualification.json
under the selected retained build root. #280 is verified closed. Producer stamp
remains accurately 3cae0756; later changes are verification/documentation only.

Real CCD65/CCD66 subset completed as CMDP.2026-11-07T13:35:31.698Z.001 in
/Users/fselman/Pictures/OCAM/test_recipes/reduced/cal/bias. Comparison with
retained CMDP.2026-11-06T21:42:22.830Z.001 passed exact detector pixels and
2804 nonidentity QC cards per detector. All 13 product-specific cards are
independently correct for each own product: ASDF, PROD and SRC1 for BPM ACTIVE,
BPM GOOD, HOT DEGEN, HOT K, HOT N, HOT THR, MAST, REQ MAD, REQ PAIR, UMAS, VAR.
ASDF schemas, selected FITS card values/types/missing states, exact processing
TOML snapshot, complete FITS/ASDF scalar/context mapping, product/input QC and
ten original inputs/bindings passed. Normalize only exact own-product sources
when comparing records; preserve raw/calibration identities. #281 comparator
defect is verified closed. No raw read or product mutation during verification.

Actual orchestration now has bias-recipe.toml with absolute settings/BPM paths,
a shortened run-bias.sh using the qualified recipe, and preserved old launcher
run-bias.sh.before-toml. Legacy numerical bias.toml/bias.list remain in place.
The all-32 catalogue is retained; this real execution selected two detectors.
No new all-32 execution is claimed. No installation or new platform validation.

## Saved read-only comparator

Owner requested retaining the successful comparison as tools/compare-bias-products.py.
It accepts explicit product, reference, processing envelope and ASDF interpreter
paths, discovers output detector IDs and checks their catalogue bindings. The
reference may contain additional detectors. Both products must have expanded
bias-scalar/1 FITS cards and the same ordered raw inputs; this is equivalence
verification, not a comparison of independent historical measurements. It reads
product arrays and headers plus ASDF/configuration; never reads raw inputs or
writes files. Existing registry/schema are reused; FITS and ASDF keep their
separate qualified interpreters. Missing/duplicate cards, differing scientific
values and incorrect own-product links fail.

The original inline two-detector algorithm passed on Mac. Saved-tool outer and
independent reader syntax, CLI help, strict 13-key identity coverage and rejection
of a wrong self-source pass in the agent environment. The saved-tool invocation
itself has not yet run on Mac. No production native source changed to add it.

```bash
/Users/fselman/anaconda3/envs/wenu-imaging/bin/python -B \
  /Users/fselman/Developer/wenu-imaging/tools/compare-bias-products.py \
  --product /Users/fselman/Pictures/OCAM/test_recipes/reduced/cal/bias/CMDP.2026-11-07T13:35:31.698Z.001.fits \
  --reference /Users/fselman/Pictures/OCAM/test_recipes/reduced/cal/bias/CMDP.2026-11-06T21:42:22.830Z.001.fits \
  --config /Users/fselman/Pictures/OCAM/test_recipes/orchestration/bias-recipe.toml \
  --asdf-python /Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python
```

Earlier pending-target text below is historical and superseded by this result.

## Executive summary

Owner requested a bounded finish to bias: transfer a small TOML-selected set
of primary/detector FITS keywords into product ASDF, support single detectors,
and remove repeated detector CLI blocks. All configured catalogue detectors
are now the default, also explicit all; a subset is an explicit ID list.

Implementation is prepared. Agent checks pass eight actual native TOML
configuration groups, actual one/two-detector QC and selected-card capture,
four existing in-memory kernel/QC profiles, and strict C17 inspection of all
changed production units against retained libasdf headers. No native ASDF
runtime is available in the agent environment: full short-command FITS/ASDF
execution and primary-image/single-extension acceptance remain pending on Mac.
No native numerical estimators or QC values changed. No database/viewer work,
installation, observation replay or existing-product modification.

## Short call

From the existing orchestration directory, using the selected native executable:

    mefpp_bias_recipe cal bias --config bias-recipe.toml \
      --bias bias.list --output-dir ../reduced/cal/bias

All entries in the authoritative TOML detector catalogue are selected by default.
The same choice is explicit with:

    --detectors all

An explicit subset is, for example:

    --detectors 'ESO_CCD_#65,ESO_CCD_#66'

Equivalent selection in TOML is bias.detectors = \"all\" (or omitted), or a
nonempty array of exact IDs. Unknown/duplicate IDs fail before output creation.
Catalogue order determines selected output order; configuration index, input
HDU, logical ID and output HDU remain independent. An input plane cannot be
bound to two selected logical detectors. All means all configured catalogue
entries, not blind discovery of every FITS extension, including tables.

The example config/recipes/omegacam-bias.example.toml contains all 32 retained
identity/HDU/configuration mappings and a small header selection. It references
the already-qualified numerical bias.toml; copy the example beside that file as
bias-recipe.toml, after checking the actual orchestration/input/BPM metadata.
The reference settings and the structural-BPM path are explicit project choices,
not instrument defaults for another dataset. Numerical settings stay in their
existing native reader; the new envelope does not reinterpret them. Settings/BPM
paths are relative to the envelope; CLI bias/output paths retain invocation
semantics. Legacy full CLI PAF/TOML invocations remain supported.

## Selected metadata

The provenance.primary and provenance.detector lists each allow at most 16
unique canonical keywords. HIERARCH prefixes are optional in these lists.
COMMENT/HISTORY/CONTINUE/END lists are refused because they are not unique scalar
keyword selections. No complete-header dump or recursive ancestry harvesting.

After final MEF assembly, the caller reads selected final-product cards using
the existing bounded qfits scanner (16 MiB aggregate header bound), then the
native ASDF writer serializes:

- qc.provenance.recipe_configuration: exact recipe path, format and frozen text;
- qc.provenance.fits_headers: keyword, role, actual product HDU, detector ID,
  source_file, status, value_type, typed value, original FITS literal, comment and
  original 80-byte card.

Primary selection is captured once; detector selection once per output detector,
including a one-extension product. Missing keys remain explicit with null data.
Undefined values remain distinct from missing keys; booleans and signed 64-bit
integers keep their types, real values stay finite doubles, strings unescape
FITS quote pairs, unsupported/continued syntax retains a fits_literal rather
than inventing a value. The captured source_file remains explicit provenance if
a later recovery preserves the record; it is not silently rewritten into a
claim that a different product's header was captured.

No JD calculation, time conversion or representative exposure epoch is chosen.
Existing FITS pixels and QC cards do not change. The application v2 schema gains
optional metadata fields only; old products/legacy invocations omit them and
remain valid with the extended canonical schema. Independent consumers using
a frozen older strict schema must use the matching updated canonical schema
when reading these new optional fields.

## One detector and primary images

The recipe accepts explicit raw HDU 0 and HDU 1 as well as mosaic extensions.
An optional expected_extname assertion is independent of logical ID. Single
detector input/output ordinal assumptions are not used. The old file publisher
API retains its behavior; the recipe's named-publication variant supplies an
output logical EXTNAME when needed, preserving existing identical cards.
Final products remain a primary header plus one or more detector extensions.

## Evidence and pending target gate

Agent evidence is retained under warning-checks/bias-toml-provenance. Eight
configuration groups pass under actual bundled TOML/C17/UBSan: default/explicit
all, catalogue order/subsets, primary/single-extension selectors, invalid or
duplicate IDs/types/bindings, header bounds, relative paths/BPM inheritance, and
legacy configuration behavior. Real existing bias calculations plus header
capture pass for one and two detectors; exact source cards, missing/undefined
states, quoted strings, D exponents, int64, booleans and malformed metadata are
checked. Four previous in-memory BPM/MAD/RON QC profiles pass with no xmem
diagnostics. Failed agent fixture/link attempts are retained; fixtures were
corrected to include required primary BITPIX/NAXIS/EXTEND. No production ASDF
writer mock is used: the agent-only in-memory probe omits recovery entry linkage;
writer inspection uses the real retained libasdf headers with external headers
marked as system headers, as in CMake.

Actual Mac gate: mefpp2/tests/qualify_bias_toml_mac.py first prints a read-only
preflight. After inspection, it updates only changed files in the selected
scalar-qc-c17-source, preserves old source/cache/binary, deliberately changes
only MEFPP_SOURCE_REVISION in the existing cache, builds existing recipe/QC
targets, and runs native header controls plus five tiny recipe products:
default all, explicit all, subset, one-extension raw, primary-image raw.
Independent Astropy/reference-pixel and retained ASDF6 schema/card/typed-value/
provenance/mapping checks run, plus four early selection/binding refusals.
No observations are opened. This target gate must pass before claiming
completed standalone ASDF behavior for the new feature.

## Mac contract correction (#280)

Candidate 3cae0756 built and passed native selected-header controls on the
selected Mac. The first actual short-command product passed detector pixel
comparisons, then the reused legacy primary-header verifier expected detector B
(RDNOISE 4.0) while the TOML correctly defaulted to first selected detector A
(RDNOISE 4.1). Parameterize the verifier reference index, preserving legacy
default B and explicitly checking A for default/all TOML tests. No production
code or numerical expectation is relaxed. A --reuse-fixture option reads and
freezes the failed attempt's tiny inputs/references and all previous evidence;
new products/logs go to a separate exclusive attempt. No adapter, rebuild or
configuration replay is needed. Full native ASDF acceptance remains pending.
