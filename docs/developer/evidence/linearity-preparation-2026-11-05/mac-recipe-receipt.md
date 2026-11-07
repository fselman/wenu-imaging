# Actual Mac linearity recipe / ASDF qualification

5 November 2026. Owner-returned terminal receipt; refs #235, #236.

Retained run:
`/Users/fselman/Software/build/wenu-imaging/mac-linearity-recipe-rSGbf1Mq`.

The owner reports `QUALIFICATION: passed` and all four preservation guards true:
checkout, installed_files, exported_source, private_qc_runtime.

Native C17 controls:

| Control | Result | Seconds |
|---|---|---:|
| native_linearity_files | passed | 43.43 |
| native_linearity_preparation_command | passed | 3.31 |
| native_sample_command | passed | 2.38 |

Total native wall time:49.14 seconds. The qualifier also completed retained-QC
version verification, six TOML controls, six recipe/ASDF controls and five
preparation-ASDF controls. Its pass checks require the declared Python counts.
No observations, real ROI publication, installation or physical fit ran.

The prescribed exact-source command pins d25b10650bcb5a0a3132cdee3f32e2867ee9f3ff;
the fetched branch reached62fce1f7175523ee7c188469c1b75bf2c16ed529 (only the
footprint executable mode differs). The terminal excerpt does not print the
saved source_revision field. Read qualification.json before real-data admission
and reuse its exact verified source/build; do not infer a source revision solely
from the fetch log and do not replay the qualification.

## Next authorized work

Admit all32 real dependencies using the qualified preparation_dependencies
service, explicit detector/processing TOMLs, preserved sample-ASDF index and
master catalogue. Freeze metadata identities and save the dependency plan in a
fresh retained directory. This step reads JSON/TOML/ASDF metadata only, with no
FITS opens, image hashing, native execution, master rebuilding or separate
singleton extraction. Review any admission failure before processing.

After complete admission, prepare a new corrected ROI ASDF archive using the
qualified recipe and preserved masters, followed by separate saved diagnostics
and plots for owner inspection. Noise/covariance stays unavailable; physical
modelling, installation, merge and cleanup remain outside this step.
