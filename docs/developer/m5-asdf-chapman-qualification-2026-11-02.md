# Chapman4 bias and ASDF 1.6 qualification — 2 November 2026

Status: PASSED on actual Chapman4 at
4417d7d159d08afcff2fbb8518fc90c3f4c84e29. Owner-returned JSON, CTest log and ldd
output were reviewed. Three interchange controls, ten reused QC controls,
five C17 native contracts and complete private normal-runtime installation
passed, with all preservation checks. Earlier pending statements below are
historical at their stated source. No production activation or merge. PR #209 / #214. The owner explicitly
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

## Second attempt: provisioning/QC passed, optional Float16 header blocked

Owner-returned run at 449220c3351a0e95649dfcbdb66873ed66422fc1:
`/home1/fselman/Software/build/wenu-imaging/chapman-m5-asdf16-retry-ZES69RYi`.
Local Conda version/help/platform checks, dry-run solve, external libasdf install,
package inventory and explicit URLs passed. All ten shared QC controls passed.
Selected GCC10.2.1 failed compiling ndarray.h's optional _Float16-returning API.
All six preservation checks passed, including external prefix after installation.
No interchange/native bias/normal-runtime-install control ran. Keep both attempts.

Review of pinned 0.3.0 public headers shows ASDF_HAVE_FLOAT16 gates only an
optional _Float16 accessor declaration and its C _Generic dispatch association;
public structures and float64 APIs are unchanged. Test-only asdf_probe_compat.h
loads installed config first, then undefines that macro only when the explicit
WENU_ASDF_PROBE_OMIT_FLOAT16 flag is passed by the Chapman consumer build.
The library binary and installed headers are never edited. No substitute typedef,
array conversion, datatype size change or claim of direct Float16 ABI support.
Mac/default consumer retains the installed header's normal feature selection.

Agent GCC13 C17 -Wall/-Wextra/-Werror syntax checks against pinned public headers
pass with a synthetic generated config enabling Float16, both with and without
the shim flag. A standalone public-layout check in both modes agrees:
sizeof ndarray=112, sizeof datatype=56, offsets ndim/shape/datatype/byteorder
8/16/24/80 on this agent. This demonstrates unchanged public layout on the agent,
not GCC10 target/runtime acceptance. A synthetic evidence-reuse guard passes
in 0.004s and rejects changed QC source or failed prior preservation.

Retry in a fresh run with --reuse-run pointing to the second attempt. It verifies
exact original revision/status/platform/preservation, successful command statuses,
libasdf package/version/build, required headers/tools, unchanged module/schema/QC
test sources against Git and old export, and passed ten-control report identity.
It records original report/QC/package-list/explicit-URL hashes. Reuse installed
prefix and passed QC: no Conda solve/install/list or QC replay. Fingerprint the
reused prefix before/after, then compile/execute only the previously blocked
interchange and native bias/private-install gates. #221 remains open because this
is a scoped consumer workaround, not an upstream header repair.

## Final Chapman receipt — 2 November 2026

Qualified source: `4417d7d159d08afcff2fbb8518fc90c3f4c84e29`.
Retained run: `/home1/fselman/Software/build/wenu-imaging/chapman-m5-asdf16-resume-U4vTGDyf`.
Evidence attribution: owner-returned retained JSON, native CTest log and linked
library listing inspected in Work chat; no direct on-host access or independent
archive transfer is claimed. Outer and native reports both say passed.

| Native C17 contract | Actual result | Time (s) |
|---|---|---:|
| native_operation_template | passed | 0.00 |
| native_bias_files | passed | 6.69 |
| native_layout | passed | 2.74 |
| native_bias_service | passed | 2.35 |
| native_explicit_paths | passed | 28.37 |

CTest reports 5/5, zero failures, 40.20 s total real time. These retain the
existing synthetic native lifecycle/detector/HDU/PAF/TOML/pixel/header/error
contracts. They do not constitute scientific validation of real observations.

| ASDF surface | Actual result |
|---|---|
| C to Python | metadata/null/float64 shape and every value exact |
| Python to C | uncompressed/zlib float64 shape and every value exact |
| Shared QC through C | schema/content and frozen input links preserved |
| File/core standard | 1.6.0 |
| Python serializer/schema packages | asdf 6.0.0 / asdf-standard 1.5.0 |
| NumPy | 1.26.4 |
| C package | external libasdf 0.3.0 |
| Interchange network attempts | none |
| Platform | actual CentOS7/glibc2.17, selected GCC10.2.1 |

The resume reuses completed provisioning and ten QC controls from
`chapman-m5-asdf16-retry-ZES69RYi`, revision
`449220c3351a0e95649dfcbdb66873ed66422fc1`, after exact report/preservation,
package-build and QC source identity checks. No Conda or unchanged QC replay.
Recorded reused evidence SHA256s:

- Parent report: `1b12c699231e5e78dbeaa36b51ece5998c5a2e6f1c125f94d479dcad8c9cdc4d`
- QC contracts: `68ba89ad2e7ef40cc9ea3fd55e36229336b9c00cd2ab0fcccd5d52051ade50ae`
- Package list: `a61d41baf3d130c23cad5cd9dd11c27dd12271c95da02367a1e801c2deabaf2f`
- Explicit packages: `ee8e23c73347d5d7f5dae953cefc42df2f323a7f96717225e0d6258a8f62bc5b`

ldd resolves libasdf, libfyaml, zlib, bzip2, lz4, libstatgrab and libmd under the
retained external prefix in `chapman-m5-asdf16-retry-ZES69RYi/libasdf-environment`.
libc, libm, pthread and the loader are system /lib64. No missing library is listed.
The selected GCC10 consumer omits only the unused optional direct Float16 API;
that API is not qualified. Installed headers and library binary remain unchanged.

Private normal-runtime installation:
`/home1/fselman/Software/build/wenu-imaging/chapman-m5-asdf16-resume-U4vTGDyf/native/install`.
All nine manifest payload hashes, installed-vs-built engine bytes and installed
CLI control passed. This is not a change to the normal production selection.
The new bias adapter remains an opt-in private build executable at:
`native/build-c17/mefpp2/mefpp_m5` beneath that run. It is not added to the
normal installed payload or connected to a new scientific ASDF QC extractor.

Preservation: checkout, configured installed files, production package metadata,
retained Python environment, exported source and external prefix after install
all true. Child native installed-file/checkout/export preservation all true.
All earlier failed attempts and their diagnostic evidence remain retained.

The requested one-host C17 Chapman gate is complete. Keep #219 and #221 open for
underlying external-library limitations; the consumer workarounds are qualified,
not repairs. No further unchanged tests, C90/other-host matrices, source-library
builds, compiler/glibc upgrades or production activation follow this receipt.
Review numerical QC definitions/handoff separately; no merge/cleanup implied.
