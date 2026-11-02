# Chapman4 bias and ASDF 1.6 qualification — 2 November 2026

Status: first target attempt failed at Conda CLI parsing; corrected retry prepared,
not yet target-qualified. PR #209 / #214. The owner explicitly
requests bringing Chapman to the current branch and testing the new bias routine
and ASDF installation because subsequent development depends on them. This
authorizes one representative Chapman4 C17 gate, superseding earlier Mac-only
wording for this increment. No merge or production activation is authorized.

## Actual target evidence and reuse

Chapman4: CentOS 7 x86_64, glibc 2.17. Clean main was 493e4f6, then owner-returned
fast-forward to main 47123eed and checkout of feat/m5-bias-template-20261102 at
6d8c4592d1173fd7dd61d6efece0be243a993aab. Origin is the HTTPS fselman/wenu-imaging
repository. Physical checkout: /home1/fselman/Software/wenu-imaging.

Guard Python is /home/fselman/.conda/envs/wenu-imaging/bin/python (3.11.14).
Normal environment lacks ASDF. Reuse the earlier private qualified environment:
/home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC/D2-private-s6qsxbqf/environment.
Owner metadata inspection confirms asdf 6.0.0, asdf-standard 1.5.0, NumPy 1.26.4
and Astropy 6.1.7 there. Do not reinstall this unchanged Python closure.

Use selected tools from selected-tools.md: devtoolset-10 GCC 10.2.1, private
CMake/CTest 3.29.6, system make/ar/ranlib. Do not rediscover or requalify tools.
Reuse the selected funpack path from the accepted
chapman-large-file-install-SLEBL3NJ CMake cache; reject missing/ambiguous records.

## Single bounded gate

Launch Pycavi2/tests/qualify_m5_asdf_chapman.py with guard Python, niceness >=10,
an exact clean candidate revision and a fresh retained directory under
~/Software/build/wenu-imaging. Source is exported privately; no work runs inside
the checkout or on observational inputs. Build parallelism is two, tests serial.

1. **Dependency/platform gate first.** Conda classic solver with separate retained
   stdout/stderr verifies actual linux-64/__glibc=2.17. Plan, then install external
   libasdf=0.3.0 plus pkgconf>=2 into run/libasdf-environment. Record package list,
   explicit URLs and all command statuses. Never override glibc/OS/architecture,
   upgrade base Conda or automatically choose another library/source build.
   A failed solve stops before installation and all functional tests.
2. **Shared QC:** retained private Python runs the existing test_shared_qc.py
   ten schema/ADU/missing-value/identity/naming/sidecar/traversal contracts at
   standard 1.6.0. These run once on Chapman; prior Mac evidence stays retained.
3. **C/Python interchange:** selected GCC compiles the same standalone C17
   asdf16_interop.c with explicit prefix include/library/rpath. ldd must resolve
   the selected libasdf and show no missing libraries. The same Python test
   checks C-to-Python metadata/null/float64, Python-to-C uncompressed/zlib arrays,
   and shared-QC C re-emission with exact content/frozen links. No second QC
   serializer is invented. Keep the #219 direct-mapping workaround and leave
   its underlying external-library limitation open.
4. **Native bias:** existing qualify_bias_files_mac.py gains explicit Chapman
   and clean candidate-checkout modes, without changing Mac defaults or native
   arithmetic. Run native_operation_template, native_bias_files, native_layout,
   native_bias_service and native_explicit_paths in C17 only. Tiny synthetic
   OCAM/WFI PAF/TOML, selected detector/HDU, float/unsigned16 primary outputs,
   exact pixels/relevant headers and negative controls remain unchanged.
5. **Private normal-runtime installation:** enable resource build with recorded
   funpack, install the full existing normal mefpp payload under native/install,
   compare all manifest-listed hashes and installed-vs-built engine bytes, then
   run the existing installed CLI usage control. Normal production selection
   stays unchanged. The new bias adapter remains the opt-in mefpp_m5 build
   executable: this gate does not add it to the supported installed payload or
   connect its provisional native QC output to ASDF.

## Preservation and evidence

Guard configured reduction module/engine/config, clean candidate checkout,
production Python package metadata, retained Python ASDF prefix, exported
source and external library prefix after its new installation. Fingerprint
regular files and symlinks; do not create bytecode in retained environments.
All failures retain reports/logs/builds/prefixes; no automatic retry or cleanup.

Outer report: chapman-qualification.json. Child evidence includes package plan/
list/explicit URLs, qc/qc-contract-results.json, interchange-results.json, ldd,
compiler logs, native/qualification.json, five-test inventory/results and private
installed build manifest/hash checks. Inspect actual returned reports before
claiming success. No files are transferred to prove runtime by implication.

Two agent stdlib controls pass in 0.081 s: platform/glibc mismatch rejection and
wrong-host rejection before directory creation. Runner syntax passes. These
are guard checks, not native/Conda/ASDF target qualification.

## Acceptance boundary

Require all planned gates and preservation checks passed on Chapman4. This
establishes bounded bias behavior, private normal installation and ASDF 1.6
interchange under real CentOS 7 limits. It does not establish full ASDF
conformance, numerical QC/scientific acceptance, production engine/package
activation, observational processing, new adapter installation API, other
hosts, C90, memory/leak or performance certification. Follow-up scientific QC
definitions/native-to-ASDF handoff remain separate review work.

## First attempt and Conda CLI compatibility correction (#220)

Actual owner-returned run at 59cb940c62a7aadcf6fb04227126c6ac3458edc0:
`/home1/fselman/Software/build/wenu-imaging/chapman-m5-asdf16-wEY4w9AQ`.
The first conda-platform command returned an unrecognized --no-plugins error.
No solve, dependency install, QC/interchange/native contract or runtime install
ran. Checkout, installed files, production packages, retained Python environment
and exported source preservation all passed. The selected funpack guard and
source export had completed. Preserve this run in place.

The runner now records conda --version and reads global/create help before
selecting flags. --no-plugins is used only if advertised. --solver classic or
--experimental-solver classic is used only if advertised; classic-only legacy
Conda receives neither. Unknown modern CLI layouts and absent required create
options stop before solving. Child environment requests remain local; base
Conda, condarc and global environment are not repaired/upgraded. Real platform
and glibc checks, separate streams and all later functional gates are unchanged.

Five agent stdlib controls passed in 0.089 s: platform/glibc mismatch, wrong host
before writes, legacy flags, modern flags, and transitional solver/unknown modern
CLI handling. These use emulated help responses, not an installed target Conda;
runner syntax also passes. Actual corrected Chapman execution remains pending.
No previous functional gate passed on Chapman to reuse; retry starts in a fresh
retained directory without repeating Mac gates or the qualified Python install.
