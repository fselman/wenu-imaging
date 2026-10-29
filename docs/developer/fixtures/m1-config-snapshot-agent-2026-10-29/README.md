# Agent configuration-snapshot checks

Ubuntu x86_64, GCC 13.3.0. See the M1 [scope and limitations](../../../architecture/proposed/m1/config-snapshot.md).

The C90 lane compiles the new snapshot and synthetic ownership tests with
`-pedantic-errors -Wall -Wextra -Werror` plus ASan/UBSan. LeakSanitizer is disabled
because this container cannot inspect `/proc`; the failed earlier attempt is
retained in the agent workspace, not described as a passing leak check.
The C17 lane uses the same strict warnings. Exact command lines, private work
paths, input hashes and successful subprocess exits are in each report.

Both lanes also invoke a separate, non-instrumented C90 real-PAF probe linked
from unchanged legacy source with unused sections discarded. Its link command,
source/binary identities and full compile warnings are retained here. Do not
infer a warning-free legacy build from the warning-free new snapshot units.
The synthetic tests check all mapped values against the reviewed baseline;
the PAF probe checks the actual constructor against the same expected values.

These files are receipts, not scripts to rerun old private paths. Use the current
`mefpp2/tests/config_snapshot_contract.py` and opt-in CMake probe in new work
directories. Intel Mac/Chapman and full CMake/CTest qualification remain pending.
No native recipe, FITS read, installation, processing or scientific acceptance.
