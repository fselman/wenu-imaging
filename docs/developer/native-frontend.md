# Configure/make frontend — candidate status

Date: 25 October 2026. Related: #84, #64–#67 and draft PR #81.
Fernando explicitly authorizes completing the normal installation interface
before resuming CP Pup processing. The former wrapper configured CMake while
the component Makefile still ran obsolete recursive rules; the root lacked an
entry point. This candidate closes that interface gap without a second build graph.

## User contract

From the repository root or mefpp2:

    ./configure --prefix=PRIVATE_PREFIX
    make
    make install

Defaults: C90, Debug, serial build, complete runtime resources, developer tests
disabled. Python is not a native build/runtime requirement; make check enables
developer tests and needs Python 3. Configuration checks installed prerequisites;
it does not download them. Mac selects active Xcode tools/SDK, Linux defaults to
cc/Make. Explicit tools/compiler/build directory remain configurable.

Root configure dispatches to component configure, which runs the shared POSIX
shell frontend in mefpp2/cmake/frontend.sh. Both Makefiles only dispatch build,
install/check/clean/help actions. CMake owns dependencies and installation.
make install builds first and forwards DESTDIR. Internal old recursive Makefiles
are not revived. Optional legacy utilities remain outside the default graph.

Ignored .mefpp-config records literal tool/build paths, not executable shell code.
No eval or generated Make interpolation is used for paths. A failed CMake/tool
configuration prevents reuse of stale state. Source-root binary directories,
including normalized dot-component aliases, are rejected before CMake probes.
make clean cleans build products and leaves installed prefixes/source unchanged.
Use fresh binary directories for changed compiler/SDK/language selections.

## Verification actually executed

Agent Linux x86_64, GCC 13.3 and CMake/CTest 3.29.6, niceness 10, serial:

- Nine frontend contract cases passed using a recorded fake backend. These cover
  clean help and unconfigured make; root workflow and DESTDIR forwarding;
  component entry/C17/literal spaced paths; failed-reconfigure stale-state guard;
  build/install failure propagation; missing tools; optional make check; simulated
  Xcode selection; source-root/dot-component protection.
- Real C90 root and C17 component configure/make/make check/make install passed.
  Both qualified 100 native translation units with developer tests enabled and
  four CTest entries: frontend contract (nine cases), install contract (seven),
  native primitives and CLI usage.
- Real integration private installs each had the expected ten payload/manifest
  files; repeated installs were byte-identical; C17 DESTDIR forwarding passed.
- Direct cmake --build / CTest still worked against both configured builds.
- Code-only installation was rejected even with previous resource outputs present,
  and made no incomplete prefix. Restoring complete configuration permitted repeat
  installation. make clean preserved native sources/private prefix; rebuild passed.
- Default configure/make/make install with developer tests disabled passed and
  did not discover a Python interpreter; 99 translation units were built.

The agent lacks funpack. Real integration above used an explicitly synthetic
decompressor producing empty valid FITS primary framing. This tests resource/build/
installer forwarding, not actual OCAM/WFI mask contents or scientific processing.
Mac-like default selection was simulated, not executed on a Mac. No observations
were processed and no user's installation/environment was touched.

[Machine-readable integration summary](fixtures/agent-native-frontend-verification.json)
records the scope. Full agent logs remain in its retained integration directory.
Do not call these actual Mac/chapman3 qualification.

## Actual Intel Mac default-frontend acceptance — 25 October 2026

Fernando reports successful execution on MC02VV0HPHTDG, macOS 13.7.8 x86_64,
at source 7c5238f848284033bcef416ec5970a8004550afd. This is actual target
evidence, distinct from the agent integration above.

Records: /Users/fselman/wenu-mac-simple-install.7en8H834.
Private executable: install/bin/mefpp under that directory.
SHA256: 7eefb5a6f1ae108fc9987420bbd9b85cc5c9092e8a4aef5b1db0c501dcc8f92c.
Reported compiler: active Xcode AppleClang at
/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang.

- Fresh full source export, ./configure with private prefix/source identity,
  make and make install passed using default C90/Debug selection.
- Optional make check enabled testing and passed all four CTest entries:
  frontend contract, install contract, native primitives and CLI usage.
- Installed file set/hashes, source/build/manifest agreement and generated-header
  identities passed. The installed binary was Mach-O x86_64, had system-only
  dynamic dependencies and provided expected no-argument CLI usage.
- All installed OCAM (32 HDUs) and WFI (8 HDUs) BPM pixels matched the compressed
  sources exactly, with expected geometry/dtype/names, finite values and valid
  FITS checksums/datasums.
- Repeated make install was byte-identical for the complete installed payload/
  manifest. Actual make install with DESTDIR staged identical bytes once under
  the staging root and retained the runtime prefix in provenance.
- Historical engine and saved configuration remained unchanged. No normal engine
  selection, observational processing, query or Python normalization occurred.

Retained configure.log, make.log, install.log and make-check.log document execution.
frontend-installation-check.json records payload/resource/CLI verification.
frontend-repeat-stage-check.json plus frontend-repeat-install.log and
frontend-staged-install.log record repeat/staging verification. Evidence is
Fernando's returned output; the agent did not independently access his Mac.

This closes the bounded normal-interface defect #84 on the unmerged candidate.
C17 frontend/component integration was tested on the agent, not separately
claimed on the Mac; earlier direct-CMake C17 Mac acceptance remains separate.
chapman3, Apple Silicon and Windows qualification remain pending.

## Next current roadmap gate

Resume the read-only CP Pup fixture/installed-candidate preflight, then prepare
the isolated native regression comparison. Preserve all earlier accepted builds
and the selected historical engine. Observational equivalence, installed Pycavi
wrapper, broader calibration/WFI fixtures, native failure/memory work and chapman3
remain open Stage 1/later gates. No additional installation test is required to
close this bounded Mac frontend gate. No reduction, engine switch, merge or
cleanup starts automatically from this acceptance record.
