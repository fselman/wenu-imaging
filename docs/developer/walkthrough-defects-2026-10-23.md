# OmegaCAM walkthrough defect register, 23 October 2026

Fernando requested individual GitHub tickets for defects, with a correction
comment and verification evidence before closure. GitHub is the live status
record; this table records the initial disposition, not a second tracker.

| Ticket | Defect | Initial disposition |
| --- | --- | --- |
| [#23](https://github.com/fselman/wenu-imaging/issues/23) | Native science detector headers inherit calibration timestamps | Open; native implementation deferred |
| [#24](https://github.com/fselman/wenu-imaging/issues/24) | Native MJD-END loses precision | Open; native implementation deferred |
| [#25](https://github.com/fselman/wenu-imaging/issues/25) | Pycavi science metadata lost at detector/coadd boundaries | Open; bounded correction approved, not yet implemented/qualified |
| [#26](https://github.com/fselman/wenu-imaging/issues/26) | Released SExtractor banner rejected | Corrected and verified on chapman3; closed with comment |
| [#27](https://github.com/fselman/wenu-imaging/issues/27) | Explicit SExtractor NTHREADS raises KeyError | Corrected and verified on chapman3; closed with comment |
| [#28](https://github.com/fselman/wenu-imaging/issues/28) | Missing PLplot plotting resources | Local environmental remedy verified on chapman3; closed with comment |
| [#29](https://github.com/fselman/wenu-imaging/issues/29) | Logging retains a closed redirected stream | Open; ownership/lifetime correction pending |
| [#30](https://github.com/fselman/wenu-imaging/issues/30) | SCAMP abort not propagated by Python wrapper | Open; related shared-command failures already recorded in #10/#12 |
| [#31](https://github.com/fselman/wenu-imaging/issues/31) | Second notebook 06 output says nobacksub although subtraction is enabled | Open; intended naming/background policy needs resolution |

The two SExtractor corrections are on PR #22, commit
`1927166644606567b374a23ff5437b248b9b7029`, installed and verified on chapman3.
Their closure does not mean PR #22 has merged. Six focused regressions, ten
installed-package checks and actual extraction of all ten exposures passed.
The plotting remedy uses batch-scoped `PLPLOT_LIB` with matching local data;
all ten SCAMP runs produced the expected XML and eight complete PDF frames.
No claim of support for other machines follows from those results.

The first r_SDSS notebook 06 coadd passed functional pixel/weight/WCS checks,
but has incorrect observation metadata. Keep it as diagnostic evidence at
`~/omegacam/testing/wenu-imaging-test/notebook06-r_SDSS-B128-20pm51ir`
on chapman3. Do not repeat normalization or all-detector solving merely to
repair metadata. The approved Python boundary correction must preserve pixels
and reuse solved WCS in fresh outputs. It must distinguish total integration
from effective exposure/noise semantics and must not enable SCAMP photometry.
Native defects #23/#24 stay open if only Python mitigation is completed.

The canonical policy is in [agent-instructions.md](agent-instructions.md#defect-tickets-approved-23-october-2026).
