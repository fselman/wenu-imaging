# Native failure-handling correction — 26 October 2026

Parent: 03861a5460370cb03f257f4119c972b2c35021a3 (fix/native-cmake-build).
Issues: #71 (status), #75 (context ownership), #76 (configuration), #85 (split),
#86 (Pycavi subprocess), #87 (PAF stale value). Status: implementation/source
verification and bounded actual-Mac acceptance passed; Chapman3 and the remaining
Stage 1 gates are pending. No merge,
replacement of working engines or full memory qualification is claimed.

## Actual Mac acceptance of the corrected source

Fernando reports the following at code commit
4ade8c52027c736a49b65da3bdb31f11b036693b on MC02VV0HPHTDG, macOS 13.7.8,
Xcode Apple Clang and SDK, CMake 3.29.3, imaging Python 3.11.14. These are
returned terminal reports; the agent has not read the Mac JSON files directly.

| Check | Reported result | Actual Mac evidence |
|---|---|---|
| Fresh frontend builds | 100 translation units with explicit mode flags, all five CTest entries passed in C90 and C17 | /Users/fselman/wenu-mac-failure-build-u021mf2l/build-check.json |
| Private installed runtimes | Exact complete manifest payload, matching Mach-O x86_64 binaries, ten installed failure-test methods passed per mode; payload preserved | Same directory, installation-check.json |
| Direct observational regression | Every pixel of all 32 detector arrays exact and finite in C90/C17; structure matches, raw headers differ only in generated primary ORIGFILE | /Users/fselman/Pictures/OCAM/mac-native-cppup-corrected-1y_n625f/comparison.json |
| Isolated Python wheel/install | No dependency download/upgrade; exact installed module identity/full imports and five wrapper regressions passed, original package preserved | /Users/fselman/wenu-mac-python-failure-test-trbc6ykz/installation-check.json |
| Corrected installed wrapper plus native engines | Production Instrument/ExposuresPartition/mefpp_reduce_science/copy_paf/check_mef_bpm/run_commands, explicit private engine per mode; all 32 detector arrays exact/finite and structure matched in C90/C17, raw-header difference only ORIGFILE; cwd restored | /Users/fselman/Pictures/OCAM/mac-corrected-wrapper-cppup-76_e3753/wrapper-comparison.json |

The expected ERROR log lines in the five wrapper regressions come from deliberately
failing subprocess fixtures, not failed tests. The observational wrapper runs
used the actual corrected installed modules and real retained raw/master/BPM/PAF
copies; they are distinct from the earlier helper-based wrapper regressions.
No Python normalization, new calibration construction, parameter tuning or
independent scientific validation occurred. Native/Python working selections
were not changed. Protected inputs/engines/packages and checkout were preserved.
Both direct and wrapper C90/C17 results compared against the historical native
reference, not a Python-normalized image.

These results supersede pending Mac build/installed/observational statuses in the
historical source-verification/handoff sections below for this correction only.
The remaining work is calibration-building fixtures and Chapman3 qualification,
plus the separately gated broader memory/platform/science work. No issue is closed
by this documentation alone. Machine-readable attributed summary:
[Mac correction acceptance](fixtures/mac-native-failure-acceptance-2026-10-26.json).

## Actual Mac evidence before the correction

Fernando's MC02VV0HPHTDG reports, not agent access/reruns:

| Run | Evidence directory under /Users/fselman/Pictures/OCAM | Result |
|---|---|---|
| C90 direct | mac-native-cppup-candidate-zueviard | All 32 detector pixels exact/finite; matching identity/shape/type; raw-header difference only primary ORIGFILE timestamp |
| C90 installed Pycavi wrapper | mac-pycavi-native-wrapper-4cvbdvez | Same acceptance, actual installed modules/source identity and explicit candidate command verified |
| C17 direct | mac-native-cppup-c17-hcnz4try | Same complete native pixel/raw-header comparison |
| C90/C17 negative suite | mac-native-failure-checks-f4legehm | Missing PAF SIGSEGV; missing split input and invalid satmax exit 0 despite errors; protected files unchanged |

Engines: C90 SHA256 7eefb5a6f1ae108fc9987420bbd9b85cc5c9092e8a4aef5b1db0c501dcc8f92c;
C17 e84f61b21ba4cb6e6e104237b91083049adf7d02e2a2c08edecd2d2543c7d798.
These are the uncorrected qualified private installs, not the new patch binaries.
Source C17 revision 41c8e6a544c1bc5122dc558e0c8cc7904214e1d0; its native C/header
identities matched the review checkout. Historical engine remained selected.
The observational fixture did not build calibrations or invoke Python normalization.
Identical pre-existing telemetry cards triggered Astropy formatting warnings;
direct raw-header comparisons confirmed no hidden telemetry-card differences.

## Implementation and ownership

- A preliminary getopt pass handles informational requests and selects default
  mefpp.paf or argument-bearing --pafname before construction. A second pass
  retains processing overrides; loader status separates error from informational
  success. Numeric satmax parsing retains the existing 0.0001..0.9999 limits.
- mef_bb_new_from_paf validates file/key/value reads before the original numeric
  conversions. It checks positive integer detector count, representable numeric
  values, bounded strings and context/string allocations. The legacy default
  constructor remains available. Failed construction destroys its partial state;
  a successfully returned context belongs to main. The engine borrows it.
- A small qfits_paf_query guard checks scanner results and rejects valueless
  fields instead of returning a preceding query's static value. Explicitly
  quoted empty strings retain their existing meaning. No replacement parser.
- main propagates parser/engine failure. Split checks its per-file status and
  returns failure for invalid geometry, truncated/mapping/read/header/write/
  close/publication failures. Valid input paths are retained; output basenames
  stay compatible. A private mkstemp file is renamed after a complete write;
  failed temporaries are removed. Completed earlier extensions remain if a later
  extension fails; overall status is nonzero. This is not a transaction across
  all extensions. Temporary-derived output permissions are private (0600).
- Pycavi run_commands uses communicate to drain pipes and actual native status,
  retaining 0-success/1-error and legacy text detection. Logs close on launch
  errors. The science wrapper restores cwd even when it raises. Tests execute
  actual function bodies; helper setup is not full orchestration acceptance.

The arithmetic/calibration/science loops, masks, PAF defaults, gain/exposure
normalization, scientific parameters and allocator policy are preserved.
Broader error cleanup/leak/allocator/format-string findings remain Stage 2 work;
this patch does not prove the engine memory-safe or all I/O paths qualified.

## Agent verification and test boundaries

Agent Linux GCC diagnostic builds compiled the actual 100-unit CMake source lists
(18 qfits, 79 Eclipse, common, recipe and primitive test) in explicit C90 and C17
modes. Headers were generated for this host ABI by a local diagnostic driver;
CMake/CTest was unavailable in this session. This is not configure/CTest or target
qualification. Existing warnings remain. The added CTest entry is pending target
execution; no resources or runtime payload were installed by the agent.

- Ten native test methods per mode with each distributed OmegaCAM/WFI PAF
  (40 method runs plus subcases): missing/malformed PAF, absent/valueless/invalid
  keys, informational/invalid CLI, satmax limits, missing split input, explicit
  PAF paths with spaces, valid synthetic split, publication failure, constrained
  child file-size/write failure and preservation/temporary cleanup.
- Both native primitive executables: actual Eclipse image arithmetic, qfits
  PAF missing/quoted-empty behavior, native FITS serialization and ctype/math
  integration. This is not WFI observational qualification.
- Five Python unittest methods execute production run_commands and science
  wrapper AST bodies with real subprocesses: silent nonzero, success/legacy
  diagnostics, verbose pipes, spawn failure, raised science failure/cwd recovery.
  Astropy/ephem import and real BPM/science data are not exercised by that helper.
- The original agent-built C90 binary reproduces all three negative outcomes
  (SIGSEGV/false success/false success). Valid synthetic split output files were
  byte-identical across the baseline, C90 and C17 implementations. These checks
  are distinct from the earlier actual-Mac CP Pup comparisons.
- The valueless-key regression with `MEF.SATMAX ` (trailing whitespace) fails
  before the qfits guard and passes afterward. A bare key directly followed by
  newline is treated as absent and was already rejected by checked construction.

Machine-readable summary: [agent verification](fixtures/agent-native-failure-verification.json).
The source tests are bounded regression evidence, not scientific validation.

## Target handoff and remaining gates

Obtain fresh actual-Mac Git/environment evidence before synchronizing the review
branch. Build/install in new private prefixes using the existing configure/make
interface and explicit qualified tools, C90/C17 separately. Run the nonempty CTest
suite (now includes native_failure_contract), installed negative cases and installed
Pycavi status tests. Use a fresh Python test install for the changed wrapper;
do not overwrite the working environment. Repeat complete CP Pup native/wrapper
pixel/raw-header comparisons against retained references. Record compiler/mode/
source/resource hashes. Then qualify Chapman3 with its compatible toolchain.

Calibration-building fixtures F2–F5, broader WFI/science/memory/platform gates and
Phase 3 remain open. Keep linked defects open until actual target verification;
do not infer full issue acceptance from source-only tests.
