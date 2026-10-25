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

## Next actual target gate

Sync the new source from Fernando's last inspected clean Mac revision
efd5df6eacf6355175500edfeac64a8a84a623ff. He explicitly did not run the separate
roadmap-only db33a643 update; include that ancestry in the single new sync.

Test the normal frontend on a fresh source export/private prefix on the actual
Mac, including default selection, make check, real distributed BPMs, repeat/staged
installation and unchanged historical engine/configuration. Preserve earlier
qualified private installs at source 41c8e6a... as comparison evidence. #84 stays
open until the frontend target gate passes. The previous direct-CMake Mac
[acceptance](native-mac-build-install-acceptance.md) is not automatically frontend
acceptance. Then resume the retained CP Pup preflight/regression and broader
Stage 1/chapman3 gates. No normal engine switch, observation run or merge starts
from this source delivery.
