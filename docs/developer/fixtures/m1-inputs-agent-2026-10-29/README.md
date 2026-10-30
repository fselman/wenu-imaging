# Agent file/list request evidence

Source/probe identities and all 35 command statuses/log hashes per lane are in
each run-provenance.json. Selected logs and exact compile commands/warnings are
retained here; full generated fixtures/logs remain in the recorded agent work
directories and are reproducible from input_request_contract.py. No real data,
native binaries, environments or packages are included.

Agent Ubuntu x86_64 GCC 13.3.0; C90/C17 strict adapter/probe syntax and 17 cases
from two unrelated directories pass. C90 ASan/UBSan passes with detect_leaks=0,
halt_on_error=1; no LeakSanitizer claim. Custom allocation counts exclude the
unchanged Eclipse parser allocator. Actual Mac/Chapman CMake checks are pending.

The manual probe link retains unused legacy units from the previously recorded
CLI probe build and uses GNU section collection only for agent preparation.
Do not use it as a Chapman workaround: actual target verification uses selected
CMake/CTest and the normal static dependency targets. Strict-core.log covers
new adapter/probe syntax; existing compile.log warnings remain distinct.
